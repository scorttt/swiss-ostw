import argparse
import io
import math
import os
import re
import sys

from gen_char_table import char_table

IMPORT_ARRAY = 15                       # trees per rule
TREE_CHARS = 1628; TREE_STRINGS = 13    # 4 outer strings of 119 chars, 9 inner of 128
HEALTH_FLAG = 32768
POS_STEP = 0.001; ANG_STEP = 0.01
POS_STEP_Y = 1 / 4096; GROUND_TOL = 0.0002     # height steps on the absolute grid, tight position on frames on the ground
DELTA_LIM = 2000; KEY_GAP_MAX = 2047; OPEN = 100000.0
ENC_MAX = 4096 * 4096 - 1
FIELDS = ("x", "y", "z", "yaw", "pitch", "hp", "b", "tx", "tz")

TABLE = char_table()
IDX = {c: i for i, c in enumerate(TABLE)}


def near(x):
    frac, whole = math.modf(x)
    return int(whole + math.copysign(1, frac)) if abs(frac) >= 0.5 else int(whole)


def wrap(a):
    return a - near(a / 360) * 360


def quant(v):
    return min(max(near((v + 2048) * 4096), 0), ENC_MAX)


def plural(n):
    return "" if n == 1 else "s"


def first(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else ""


def read_text(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return f.read()


def csv_num(x):
    return format(x, ".15g").replace("e", "E")


def write_rows(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("".join(r + os.linesep for r in rows))


class Track:
    def __init__(self, t, hero, team, start, n, flags):
        self.t = t; self.hero = hero; self.team = team; self.start = start; self.n = n; self.flags = flags
        self.x = [0.0] * n; self.y = [0.0] * n; self.z = [0.0] * n
        self.yaw = [0.0] * n; self.pitch = [0.0] * n; self.hp = [0.0] * n
        self.b = [0] * n; self.tx = [0.0] * n; self.tz = [0.0] * n


# ---- the import's reading, like import.del. an export's text into importData entries, each a list of trees ----
def strings_of(rule):
    # flat strings or trees, either way the strings in written order are the stream
    text = re.sub(r'importMap = Custom String\("[^"]*"\)', "", rule, flags=re.I)
    return [m.group(1).replace("{0}{1}{2}", "") for m in re.finditer(r'Custom String\("([^"]*)"', text)]


def read_entries(txt):
    ent = {}
    # in an Inspector log every rule head after the first is mid-line, so the rules are split anywhere
    for r in re.split(r'(?=rule\(")', txt):
        if not r.startswith('rule("'):
            continue
        e = int(first(r"importData, (\d+), Array", r))
        # the trees are TREE_STRINGS strings each
        s = strings_of(r)
        if len(s) % TREE_STRINGS != 0:
            raise ValueError(f"entry {e} has {len(s)} strings, not whole trees")
        ent[e] = ["".join(s[i:i + TREE_STRINGS]) for i in range(0, len(s), TREE_STRINGS)]
    for e in range(len(ent) - 1):
        if len(ent[e]) != IMPORT_ARRAY:
            raise ValueError(f"entry {e} has {len(ent[e])} trees")
    for trees in ent.values():
        for t in trees:
            if len(t) != TREE_CHARS:
                raise ValueError(f"a tree has {len(t)} chars")
    return ent


# reading cursors cur (0 position, 1 facing, 2 steps, 3 header), the keys before (a) and after (b) each frame of a channel
class Reader:
    def __init__(self, ent):
        self.ent = ent
        self.cur = [0, 0, 0, 0]
        self.fa = [0, 0, 0]; self.fb = [0, 0, 0]
        self.va = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        self.vb = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        self.hp_a = 0.0; self.hp_b = 0.0

    def char(self, k):
        return IDX[self.ent[k // (IMPORT_ARRAY * TREE_CHARS)][k // TREE_CHARS % IMPORT_ARRAY][k % TREE_CHARS]]

    def at(self, c, cnt, w):
        r = []
        for _ in range(cnt):
            i = self.cur[c]
            r.append(self.char(i) if w == 1 else self.char(i) * 4096 + self.char(i + 1))
            self.cur[c] = i + w
        return r

    def key(self, c):
        g = self.at(c, 1, 1)[0]
        absolute = g >= 2048
        self.fb[c] = self.fa[c] + g % 2048
        va = self.va[c]
        if c == 0:
            v = self.at(0, 3, 2 if absolute else 1)
            if absolute:
                self.vb[0] = [x / 4096 - 2048 for x in v]
            else:
                self.vb[0] = [va[i] + (v[i] - 2048) * (POS_STEP, POS_STEP_Y, POS_STEP)[i] for i in range(3)]
        elif c == 1:
            v = self.at(1, 2, 2 if absolute else 1)
            if absolute:
                self.vb[1] = [va[0] + wrap(v[0] / ENC_MAX * 360 - 180 - va[0]), v[1] / ENC_MAX * 180 - 90, 0.0]
            else:
                self.vb[1] = [va[0] + (v[0] - 2048) * ANG_STEP, va[1] + (v[1] - 2048) * ANG_STEP, 0.0]
        else:
            b = self.at(2, 1, 2)[0]
            if b >= HEALTH_FLAG:
                self.hp_b = self.at(2, 1, 2)[0] / 1024
                b -= HEALTH_FLAG
            t = self.at(2, 2, 1)
            self.vb[2] = [t[0] / 2047.5 - 1, b, t[1] / 2047.5 - 1]

    # the directory is read once, then the header and first keys of each track
    def read_directory(self, chars):
        h = self.at(3, 2, 1)
        trim = self.at(3, 2, 2)
        self.cur[2] = chars - h[1] * 4
        return h, trim, self.at(2, h[1] * 2, 2)

    def begin_track(self, k, directory):
        hdr = self.at(3, 3, 1)
        se = self.at(3, 2, 2)
        fc = self.at(3, 1, 1)[0]
        if fc > 0:
            self.at(3, fc, 2)
        self.cur[0] = self.cur[3]; self.cur[1] = directory[k * 2]; self.cur[2] = directory[k * 2 + 1]
        self.fa = [0, 0, 0]
        self.va = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
        for c in range(3):
            self.key(c)
        return hdr, se, fc

    def advance(self, s, n):
        for c in range(3):
            if s == self.fb[c]:
                self.fa[c] = s
                self.va[c] = self.vb[c]
                if c == 2:
                    self.hp_a = self.hp_b
                if s < n - 1:
                    self.key(c)

    def fraction(self, c, s):
        return 0 if self.fb[c] == self.fa[c] else (s - self.fa[c]) / (self.fb[c] - self.fa[c])

    def lerp(self, c, i, u):
        return self.va[c][i] + (self.vb[c][i] - self.va[c][i]) * u


# ---- read: decode an export alone, one line of stats per track ----
def read_export(path, dump):
    txt = read_text(path)
    stamp = first(r"\[IMPORT (\d+)\]", txt)
    map_name = first(r'importMap = Custom String\("([^"]*)"\)', txt)
    ent = read_entries(txt)
    r = Reader(ent)
    h, trim, directory = r.read_directory(sum(len(t) for t in ent.values()) * TREE_CHARS)
    dcount = h[1]
    print(f"[IMPORT {stamp}] {map_name}, {dcount} track{plural(dcount)}, focused track {h[0] + 1}, trim {trim[0]} to {trim[1]}, {len(ent)} rule{plural(len(ent))}")
    rows = ["track,frame,buttons,x,y,z,yaw,pitch,health,throttle x,throttle z"] if dump else []
    for k in range(dcount):
        hdr, se, fc = r.begin_track(k, directory)
        n = se[1]
        changes = primary = jumps = ground = deaths = 0
        move = 0.0; move_max = 0.0
        last_b = -1; px = 0.0; pz = 0.0
        for s in range(n):
            r.advance(s, n)
            u = r.fraction(0, s)
            x = r.lerp(0, 0, u); y = r.lerp(0, 1, u); z = r.lerp(0, 2, u)
            u = r.fraction(1, s)
            yaw = wrap(r.lerp(1, 0, u)); pitch = r.lerp(1, 1, u)
            b = int(r.va[2][1])

            # a bot's SetBotButtons runs when the held buttons (below the ability bits) change
            if s > 0 and b % 1024 != last_b % 1024:
                changes += 1
            if b & 1:
                primary += 1
            if b & 64 and (s == 0 or not last_b & 64):
                jumps += 1
            if b & 8192:
                ground += 1
            if b & 16384 and (s == 0 or not last_b & 16384):
                deaths += 1
            if s > 0:
                d = math.sqrt((x - px) * (x - px) + (z - pz) * (z - pz))
                move += d
                move_max = max(move_max, d)
            last_b = b; px = x; pz = z
            if dump:
                rows.append(",".join(csv_num(v) for v in (k + 1, s, b, x, y, z, yaw, pitch, r.hp_a, r.va[2][0], r.va[2][2])))
        r.cur[3] = r.cur[2]
        secs = n / 62.5
        print(f"track {hdr[0] + 1}: hero #{hdr[1]}, {'enemy' if hdr[2] == 1 else 'ally'}, frames {se[0]} to {se[0] + n} ({secs:,.2f} s), {fc} flag{plural(fc)}"
              f" | buttons change {changes / max(secs, 0.001):,.1f}/s, primary held {primary / max(n, 1) * 100:,.0f}%, {jumps} jumps, on the ground {ground / max(n, 1) * 100:,.0f}%, {deaths} deaths"
              f" | horizontal speed {move / max(n - 1, 1) * 62.5:,.2f} m/s average ({move / max(n - 1, 1):,.3f} m per frame), {move_max * 62.5:,.2f} m/s fastest frame")
    if dump:
        write_rows(dump, rows)
        print(f"frames written to {dump}")


# ---- source: old per-frame format ----
def load_source(path):
    txt = read_text(path)
    stamp = int(first(r'rule\("\[IMPORT (\d+)\][^"]*"\)', txt) or 0)
    map_name = first(r'importMap = Custom String\("([^"]*)"\)', txt)
    entries = {}
    for r in re.split(r"(?m)^(?=rule\()", txt):
        if r.startswith("rule"):
            entries[int(first(r"importData, (\d+), Array", r))] = strings_of(r)
    data = "".join("".join(entries[e]) for e in range(len(entries)))
    p = 0

    def v(w):
        nonlocal p
        value = IDX[data[p]] if w == 1 else IDX[data[p]] * 4096 + IDX[data[p + 1]]
        p += w
        return value

    focus = v(1); count = v(1); trim_s = v(2); trim_e = v(2)
    src = []
    for _ in range(count):
        t = v(1); hero = v(1); team = v(1); start = v(2); n = v(2)
        fc = v(1)
        T = Track(t, hero, team, start, n, [v(2) for _ in range(fc)])
        hp = 0
        for s in range(n):
            b = v(2)
            if b >= HEALTH_FLAG:
                hp = v(2) / 1024
                b -= HEALTH_FLAG
            T.b[s] = b; T.hp[s] = hp
            T.x[s] = v(2) / 4096 - 2048; T.y[s] = v(2) / 4096 - 2048; T.z[s] = v(2) / 4096 - 2048
            T.yaw[s] = v(2) / ENC_MAX * 360 - 180; T.pitch[s] = v(2) / ENC_MAX * 180 - 90
            T.tx[s] = v(1) / 2047.5 - 1; T.tz[s] = v(1) / 2047.5 - 1
        src.append(T)
    return src, stamp, map_name, focus, count, trim_s, trim_e


# ---- optional tiling: each new track runs through the source tracks back to back from a different one ----
def tile(src, tracks, frames):
    tiled = []
    for k in range(tracks):
        T = Track(k, src[0].hero, 0, 0, frames, [])
        j = k % len(src); s0 = 0
        for s in range(frames):
            if s0 >= src[j].n:
                j = (j + 1) % len(src); s0 = 0
            for f in FIELDS:
                getattr(T, f)[s] = getattr(src[j], f)[s0]
            s0 += 1
        tiled.append(T)
    return tiled


# ---- encode, the same steps as export.del ----
class Encoder:
    def __init__(self, pos_tol, ang_tol):
        self.pos_tol = pos_tol; self.ang_tol = ang_tol
        self.ground_tol_xz = min(0.001, pos_tol)
        self.chars = []

    def put(self, values, w):
        for x in values:
            n = near(x)
            if n < 0 or n > (4095 if w == 1 else ENC_MAX):
                raise ValueError(f"value {n} out of range for width {w}")
            if w == 1:
                self.chars.append(TABLE[n])
            else:
                self.chars += [TABLE[n // 4096], TABLE[n % 4096]]

    def curve(self, T, c):
        n = T.n
        q = (POS_STEP, POS_STEP_Y, POS_STEP) if c == 0 else (ANG_STEP, ANG_STEP, ANG_STEP)
        kf = -1
        kv = [0.0, 0.0, 0.0]

        # tolerance per axis of frame s, height tight on frames recorded on the ground
        def tol_at(s):
            if c != 0:
                return self.ang_tol, self.ang_tol, 0.0
            if T.b[s] & 8192:
                return self.ground_tol_xz, GROUND_TOL, self.ground_tol_xz
            return self.pos_tol, self.pos_tol, self.pos_tol

        def read(s):
            return [T.x[s], T.y[s], T.z[s]] if c == 0 else [kv[0] + wrap(T.yaw[s] - kv[0]), T.pitch[s], 0.0]

        def max_abs(a):
            return max(abs(a[0]), abs(a[1]), abs(a[2]))

        def in_steps(v):
            return [(v[i] - kv[i]) / q[i] for i in range(3)]

        def key(f, v):
            nonlocal kf, kv
            st = [near(x) for x in in_steps(v)]
            absolute = kf < 0 or max_abs(st) > 2047
            self.put([f - max(kf, 0) + (2048 if absolute else 0)], 1)
            if not absolute:
                self.put([x + 2048 for x in st[:3 - c]], 1)
                kv = [kv[i] + st[i] * q[i] for i in range(3)]
            elif c == 0:
                a = [quant(v[0]), quant(v[1]), quant(v[2])]
                self.put(a, 2)
                kv = [x / 4096 - 2048 for x in a]
            else:
                a = [near((wrap(v[0]) + 180) / 360 * ENC_MAX), near((v[1] + 90) / 180 * ENC_MAX)]
                self.put(a, 2)
                kv = [kv[0] + wrap(a[0] / ENC_MAX * 360 - 180 - kv[0]), a[1] / ENC_MAX * 180 - 90, 0.0]
            kf = f

        key(0, read(0))
        lo = [-OPEN, -OPEN, -OPEN]; hi = [OPEN, OPEN, OPEN]
        for s in range(1, n):
            v = read(s)
            tol = tol_at(s)
            d = s - kf
            cut = max_abs(in_steps(v)) > DELTA_LIM or d > KEY_GAP_MAX
            nlo = [max(lo[i], (v[i] - tol[i] - kv[i]) / d) for i in range(3)]
            nhi = [min(hi[i], (v[i] + tol[i] - kv[i]) / d) for i in range(3)]
            if cut or nlo[0] > nhi[0] or nlo[1] > nhi[1] or nlo[2] > nhi[2]:
                if s - 1 > kf:
                    g = s - 1 - kf
                    key(s - 1, [kv[i] + (lo[i] + hi[i]) / 2 * g for i in range(3)])
                    v = read(s)
                if max_abs(in_steps(v)) > DELTA_LIM:
                    key(s, v)
                    lo = [-OPEN, -OPEN, -OPEN]; hi = [OPEN, OPEN, OPEN]
                else:
                    lo = [v[i] - tol[i] - kv[i] for i in range(3)]
                    hi = [v[i] + tol[i] - kv[i] for i in range(3)]
            else:
                lo = nlo; hi = nhi
        if n - 1 > kf:
            g = n - 1 - kf
            key(n - 1, [kv[i] + (lo[i] + hi[i]) / 2 * g for i in range(3)])

    def steps(self, T):
        kf = 0; last = None; last_hp = -1
        for s in range(T.n):
            tx = near((T.tx[s] + 1) * 2047.5); tz = near((T.tz[s] + 1) * 2047.5); b = T.b[s]; hp = T.hp[s]
            v = (tx, b, tz)
            if v != last or hp != last_hp or s == T.n - 1 or s - kf >= KEY_GAP_MAX:
                self.put([s - kf], 1)
                if hp != last_hp:
                    self.put([b + HEALTH_FLAG, min(near(hp * 1024), ENC_MAX)], 2)
                else:
                    self.put([b], 2)
                self.put([tx, tz], 1)
                kf = s; last = v; last_hp = hp

    def encode(self, src, focus, count, trim_s, trim_e):
        self.put([focus, count], 1)
        self.put([trim_s, trim_e], 2)
        directory = []
        for T in src:
            self.put([T.t, T.hero, T.team], 1)
            self.put([T.start, T.n], 2)
            self.put([len(T.flags)], 1)
            self.put(T.flags, 2)
            self.curve(T, 0)
            directory.append(len(self.chars))
            self.curve(T, 1)
            directory.append(len(self.chars))
            self.steps(T)
        # the last tree is filled up so the directory ends it
        self.chars += TABLE[:(TREE_CHARS - (len(self.chars) + len(directory) * 2) % TREE_CHARS) % TREE_CHARS]
        self.put(directory, 2)
        return "".join(self.chars)


# ---- rules: IMPORT_ARRAY trees per rule. a tree's strings are filled in the order it reads them, which is also the order
# they're written in: outer text (119 chars, then its 3 slots) first ----
def tree(t):
    mids = []
    for m in range(3):
        o = 119 + m * 503   # an outer string of 119 and its 3 inner ones of 128
        leaves = [f'Custom String("{t[o + 119 + i * 128:o + 247 + i * 128]}")' for i in range(3)]
        mids.append('Custom String("' + t[o:o + 119] + '{0}{1}{2}", ' + ", ".join(leaves) + ")")
    return 'Custom String("' + t[:119] + '{0}{1}{2}", ' + ", ".join(mids) + ")"


def rules_text(enc, src, count, stamp, map_name):
    trees = [enc[i:i + TREE_CHARS] for i in range(0, len(enc), TREE_CHARS)]
    parts = math.ceil(len(trees) / IMPORT_ARRAY)
    total = sum(T.n for T in src)
    long = max(T.start + T.n for T in src) * 0.016
    title = f"[IMPORT {stamp}] {count} track{plural(count)}, {math.floor(long / 60)}:{long % 60:05.2f} long, {total} frames, {map_name}"
    lines = []
    for e in range(parts):
        name = title if e == 0 else f"[IMPORT {stamp}] part {e + 1}"
        lines += [f'rule("{name}")', "{", "    event { Ongoing - Global; }",
                  f"    conditions {{ Global.importStamp <= {stamp}; }}", "    actions", "    {",
                  f"        If(Global.importStamp < {stamp});", "            Global.importData = Empty Array;",
                  "            Global.importParts = 0;", f"            Global.importStamp = {stamp};", "        End;",
                  f"        Set Global Variable At Index(importData, {e}, Array("]
        lines.append(",\n".join("            " + tree(t) for t in trees[e * IMPORT_ARRAY:(e + 1) * IMPORT_ARRAY]))
        lines.append("        ));")
        if e == parts - 1:
            lines += [f'        Global.importMap = Custom String("{map_name}");', f"        Global.importParts = {parts};"]
        lines += ["    }", "}", ""]
    return "".join(line + os.linesep for line in lines), total


# ---- decode the written file like import.del and compare with the source ----
def check(path, orig, dump):
    ent = read_entries(read_text(path))
    trees = sum(len(ent[e]) for e in range(len(ent)))
    chars = trees * TREE_CHARS
    r = Reader(ent)
    h, _, directory = r.read_directory(chars)
    dcount = h[1]
    worst_p = worst_a = worst_g = worst_gx = 0
    step_err = 0
    rows = []
    decoded = []    # the decoded tracks, the next export's source
    for k in range(dcount):
        hdr, se, _ = r.begin_track(k, directory)
        n = se[1]
        T = orig[k]
        if hdr[0] != T.t or n != T.n:
            raise ValueError(f"track {k} header mismatch")
        D = Track(T.t, T.hero, T.team, T.start, n, T.flags)
        for s in range(n):
            r.advance(s, n)
            u = r.fraction(0, s)
            x = r.lerp(0, 0, u); y = r.lerp(0, 1, u); z = r.lerp(0, 2, u)
            D.x[s] = x; D.y[s] = y; D.z[s] = z
            D.b[s] = int(r.va[2][1]); D.tx[s] = r.va[2][0]; D.tz[s] = r.va[2][2]; D.hp[s] = r.hp_a
            if dump:
                rows.append(",".join(csv_num(v) for v in (k, s, T.b[s], x, y, z, T.x[s], T.y[s], T.z[s])))
            if T.b[s] & 8192:
                worst_g = max(worst_g, abs(y - T.y[s]))
                worst_gx = max(worst_gx, math.sqrt(math.pow(x - T.x[s], 2) + math.pow(z - T.z[s], 2)))
            dx = x - T.x[s]; dy = y - T.y[s]; dz = z - T.z[s]
            pe = math.sqrt(dx * dx + dy * dy + dz * dz)
            u = r.fraction(1, s)
            ya = wrap(r.lerp(1, 0, u))
            pa = r.lerp(1, 1, u)
            D.yaw[s] = ya; D.pitch[s] = pa
            ae = max(abs(wrap(ya - T.yaw[s])), abs(pa - T.pitch[s]))
            worst_p = max(worst_p, pe); worst_a = max(worst_a, ae)
            if (r.va[2][1] != T.b[s] or abs(r.va[2][0] - T.tx[s]) > 0.0003 or abs(r.va[2][2] - T.tz[s]) > 0.0003
                    or abs(r.hp_a - T.hp[s]) > 0.001):
                step_err += 1
        r.cur[3] = r.cur[2]
        decoded.append(D)
    # the padding that fills the last tree is between them
    gap = chars - dcount * 4 - r.cur[2]
    if gap < 0 or gap >= TREE_CHARS:
        raise ValueError(f"steps of the last track end at {r.cur[2]}, the directory starts at {chars - dcount * 4}")
    if dump:
        write_rows(dump, rows)
    return decoded, chars, gap, trees, len(ent), worst_p, worst_a, step_err, worst_g, worst_gx


def main():
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Builds Swiss imports in the keyframe export format, or reads one")
    parser.add_argument("--source", default="")
    parser.add_argument("--out", default="")
    parser.add_argument("--read", default="", help="decode this export alone and print its tracks, no --source or --out needed")
    parser.add_argument("--tracks", type=int, default=0, help="0 keeps the source's tracks as they are")
    parser.add_argument("--frames", type=int, default=7500)
    parser.add_argument("--stamp", type=int, default=0, help="0 keeps the source's stamp")
    # tolerances, the import doesn't depend on them. export.del uses 0.0057 m and 0.01 degrees. near the delta steps
    # (0.001 m, 0.01 degrees) nearly every frame gets a key, as a near-lossless reference
    parser.add_argument("--pos-tol", type=float, default=0.0057)
    parser.add_argument("--ang-tol", type=float, default=0.01)
    parser.add_argument("--dump", default="", help="csv of every decoded frame next to the source: track, frame, buttons, x y z, source x y z (with --read: every decoded value)")
    parser.add_argument("--generations", type=int, default=1)
    parser.add_argument("--check", default="", help="decode this export (e.g. one made in game) against the source instead of the one written")
    args = parser.parse_args()

    if args.read:
        read_export(args.read, args.dump)
        return
    if not args.source or not args.out:
        parser.error("give --source and --out to write an export, or --read to decode one")

    src, stamp, map_name, focus, count, trim_s, trim_e = load_source(args.source)
    if args.tracks > 0:
        src = tile(src, args.tracks, args.frames)
        count = args.tracks; focus = 0; trim_s = 0; trim_e = args.frames
    if args.stamp != 0:
        stamp = args.stamp
    orig = src

    for gen in range(1, args.generations + 1):
        enc = Encoder(args.pos_tol, args.ang_tol).encode(src, focus, count, trim_s, trim_e)
        text, total = rules_text(enc, src, count, stamp, map_name)
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            f.write(text)

        written = args.check or args.out
        src, chars, gap, trees, rules, worst_p, worst_a, step_err, worst_g, worst_gx = check(written, orig, args.dump)
        secs = total / 62.5
        # in game a tree costs 53 elements (4 outer strings of 2, 9 inner of 5), a rule ~20
        # data chars leave out the padding of the last tree, the rate to compare codecs by
        print(f"{total} frames in {count} tracks ({secs:,.1f} s): {chars - gap} data chars = {(chars - gap) / secs:,.0f} chars/s, {trees} trees, ~{trees * 53 + rules * 20:,} elements, {rules} rules -> {written}")
        print(f"export {gen}, decoded back: worst position {worst_p * 100:,.2f} cm, on the ground: height {worst_g * 1000:,.2f} mm, horizontal {worst_gx * 1000:,.2f} mm, worst facing {worst_a:,.3f} deg, steps frames wrong: {step_err}")


if __name__ == "__main__":
    main()
