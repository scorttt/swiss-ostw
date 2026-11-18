# Converts an Overdub export in an older format (1.0.3 and older, or the first packed format) to the current one (Packed2),
# the same steps as converter/main.del, to check what the converter logs in game:
#   python tools/convert_export.py old.txt new.txt [--check ingame.txt]
# --check compares the stream of an export the converter logged in game with this one's, char for char.

import argparse
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_import as G
from gen_import import TABLE, IDX, TREE_CHARS, HEALTH_FLAG, SHORT_KEYS, ABS_KEYS, CURVE_GAP_MAX, STEP_FULL, look_key, step_key

NOT_OLD = "not an export from an older Overdub version"


def stream_of(path):
    ent = G.read_entries(G.read_text(path))
    return "".join(t for e in range(len(ent)) for t in ent[e])


class Converter:
    def __init__(self, old):
        self.v = [IDX[c] for c in old]
        self.cur = 0
        self.out = []
        self.heroes = []; self.frames = 0; self.end = 0
        self.old = True         # the track's format: Old, else Packed
        self.pd = [0, 0]        # the last facing key's deltas written
        self.last = (-1, -1, -1)    # the last steps key written: throttle x, buttons, throttle z

    def at(self, cnt, w):
        r = []
        for _ in range(cnt):
            r.append(self.v[self.cur] if w == 1 else self.v[self.cur] * 4096 + self.v[self.cur + 1])
            self.cur += w
        return r

    def put(self, values, w):
        for n in values:
            if n < 0 or n > (4095 if w == 1 else 4096 * 4096 - 1):
                raise ValueError(f"value {n} out of range for width {w}")
            self.out += [TABLE[n]] if w == 1 else [TABLE[n // 4096], TABLE[n % 4096]]

    def copy(self, cnt, w):
        r = self.at(cnt, w)
        self.put(r, w)
        return r

    def look(self, gap, st):
        self.put(look_key(gap, st, self.pd), 1)
        self.pd = st[:2]

    # an Old curve key: absolute keeps its values, a delta key is split over keys of at most CURVE_GAP_MAX frames
    def key(self, c, g, absolute, vals):
        if absolute:
            self.put([g + ABS_KEYS], 1)
            self.put(vals, 2)
            self.pd = [0, 0]
            return
        d = [vals[0] - 2048, vals[1] - 2048, vals[2] - 2048 if c == 0 else 0]
        total = [0, 0, 0]; done = 0
        while done < g:
            gap = min(g - done, CURVE_GAP_MAX)
            done += gap
            st = [(2 * d[i] * done + g) // (2 * g) - total[i] for i in range(3)]
            total = [total[i] + st[i] for i in range(3)]
            z = st[2] + 512; x = st[0] + 512
            if c == 1:
                self.look(gap, st)
            elif gap <= 8 and 0 <= z < 1024 and 0 <= x < 1024:
                self.put([(gap - 1) * 256 + z // 4, z % 4 * 1024 + x, st[1] + 2048], 1)
            else:
                self.put([gap + SHORT_KEYS, st[0] + 2048, st[1] + 2048, st[2] + 2048], 1)

    def curve(self, c, n):
        f = -1
        while f < n - 1:
            g = self.at(1, 1)[0]
            if f < 0:
                if g not in (2048, ABS_KEYS):
                    raise ValueError(NOT_OLD)
                self.old = g == 2048
            if self.old:
                if f >= 0 and g % 2048 == 0:
                    raise ValueError(NOT_OLD)
                if g > 2048 + CURVE_GAP_MAX:
                    raise ValueError("an absolute key is too far after the last one")
                vals = self.at(3 - c, 2 if g >= 2048 else 1)
                self.key(c, g % 2048, g >= 2048, vals)
                gap = g % 2048
            else:
                vals = self.at(2 - c if g < SHORT_KEYS else 3 - c, 2 if g >= ABS_KEYS else 1)
                gap = g // (256 if c == 0 else 1024) + 1 if g < SHORT_KEYS else (g - SHORT_KEYS) % 1024
                if f >= 0 and gap == 0:
                    raise ValueError(NOT_OLD)
                if c == 1 and g < ABS_KEYS:
                    self.look(gap, [vals[0] - 2048, g % 1024 - 512] if g < SHORT_KEYS else [vals[0] - 2048, vals[1] - 2048])
                else:
                    self.put([g], 1)
                    self.put(vals, 2 if g >= ABS_KEYS else 1)
                    self.pd = [0, 0]
            f = max(f, 0) + gap
        if f != n - 1:
            raise ValueError(NOT_OLD)

    def steps(self, n):
        f = -1
        while f < n - 1:
            g = self.at(1, 1)[0]
            if (g != 0) if f < 0 else (g == 0):
                raise ValueError(NOT_OLD)
            b = self.at(1, 2)[0]; hp = None
            if b >= HEALTH_FLAG:
                hp = self.at(1, 2)[0]; b -= HEALTH_FLAG
            tx, tz = self.at(2, 1)
            for x, w in step_key(g, (tx, b, tz), self.last, hp):
                self.put([x], w)
            self.last = (tx, b, tz)
            f = max(f, 0) + g
        if f != n - 1:
            raise ValueError(NOT_OLD)

    def convert(self):
        count = self.copy(2, 1)[1]
        self.copy(2, 2)
        # the first track's first steps key is full, a Packed2 export has it at STEP_FULL or more
        steps0 = self.v[len(self.v) - count * 4 + 2] * 4096 + self.v[len(self.v) - count * 4 + 3]
        if self.v[steps0] >= STEP_FULL:
            raise ValueError("already in the newest format")
        directory = []
        for _ in range(count):
            hdr = self.copy(3, 1)
            start, n = self.copy(2, 2)
            self.heroes.append(hdr[1]); self.frames += n; self.end = max(self.end, start + n)
            self.copy(self.copy(1, 1)[0], 2)
            self.curve(0, n)
            directory.append(len(self.out))
            self.curve(1, n)
            directory.append(len(self.out))
            self.steps(n)
        if self.cur > len(self.v) - count * 4:
            raise ValueError(NOT_OLD)
        # the filler goes in pieces of 128 from the table's start, like the game (String Slice returns at most 128)
        pad = (TREE_CHARS - (len(self.out) + len(directory) * 2) % TREE_CHARS) % TREE_CHARS
        while pad > 0:
            self.out += TABLE[:min(pad, 128)]
            pad -= 128
        self.put(directory, 2)
        return "".join(self.out), count


def main():
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Converts an Overdub export in an older format to the current one")
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--check", default="", help="an export the converter logged in game, compared char for char")
    a = p.parse_args()

    txt = G.read_text(a.old)
    stamp = int(G.first(r'rule\("\[IMPORT (\d+)\]', txt) or 0)
    map_name = G.first(r'importMap = Custom String\("([^"]*)"\)', txt)
    old = stream_of(a.old)
    cv = Converter(old)
    new, count = cv.convert()

    class T:    # what rules_text reads of a track
        pass
    src = []
    for k in range(count):
        t = T(); t.n = cv.frames if k == 0 else 0; t.start = cv.end - t.n if k == 0 else 0
        src.append(t)
    text, _ = G.rules_text(new, src, count, stamp, map_name)
    with open(a.new, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print(f"{count} tracks: {len(old):,} chars -> {len(new):,} ({len(new) / len(old) - 1:+.1%}), {len(old) // TREE_CHARS} -> {len(new) // TREE_CHARS} trees -> {a.new}")

    if a.check:
        game = stream_of(a.check)
        if game == new:
            print(f"{a.check}: the same {len(game):,} chars")
        else:
            k = next((i for i in range(min(len(game), len(new))) if game[i] != new[i]), min(len(game), len(new)))
            print(f"{a.check}: differs at char {k:,} of {len(new):,} (in game {len(game):,} chars)")


if __name__ == "__main__":
    main()
