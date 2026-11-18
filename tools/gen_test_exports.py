# Writes the Packed2 test exports in tests/, for checking the format in game:
#   packed2-test.txt       the 8 Soldier recording (tests/exports/8-soldiers.csv)
#   packed2-edge-test.txt  synthetic tracks that use every key form and the limits between them
#   python tools/gen_test_exports.py
# both are decoded back here and compared with their source, and the key forms each one uses are counted

import io
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_import as G

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, "..", "tests")
MAP = "Workshop Chamber"
SOLDIER = 17


# key forms written, counted through the encoder's helpers
forms = {}


def count(name):
    forms[name] = forms.get(name, 0) + 1


def counted_look(gap, st, pd):
    r = look(gap, st, pd)
    count({1: "facing 1 char", 2: "facing 2 chars", 3: "facing delta"}[len(r)])
    return r


def counted_step(gap, v, last, hp):
    r = step(gap, v, last, hp)
    count({1: "steps throttle only", 2: "steps buttons only"}.get(len(r), "steps full + health" if hp is not None else "steps full"))
    if len(r) == 1:
        count(f"steps throttle only, gap {'113' if gap == 113 else 'other'}")
    if len(r) == 2:
        count(f"steps buttons only, gap {'128' if gap == 128 else 'other'}")
    if len(r) > 2 and hp is None and (v[0], v[2]) == (last[0], last[2]) and gap == 129:
        count("steps full, buttons only at gap 129")
    if len(r) > 2 and hp is None and v[1] == last[1] and gap == 114:
        count("steps full, throttle only at gap 114")
    return r


look, step = G.look_key, G.step_key
G.look_key, G.step_key = counted_look, counted_step


def write(name, src, stamp, focus=0):
    forms.clear()
    end = max(T.start + T.n for T in src)
    enc = G.Encoder(0.0057, 0.01).encode(src, focus, len(src), 0, end)
    text, total = G.rules_text(enc, src, len(src), stamp, MAP)
    path = os.path.join(TESTS, name)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    _, chars, gap, trees, rules, worst_p, worst_a, step_err, worst_g, worst_gx = G.check(path, src, "")
    print(f"{name}: {len(src)} tracks, {total} frames, {chars - gap:,} data chars, {trees} trees, {rules} rule{G.plural(rules)}")
    print(f"  decoded back: worst position {worst_p * 100:.2f} cm, worst facing {worst_a:.3f} deg, steps frames wrong: {step_err}")
    for k in sorted(forms):
        print(f"  {forms[k]:6} {k}")


def soldiers():
    src = G.load_csv(os.path.join(TESTS, "exports", "8-soldiers.csv"))[0]
    for T in src:
        T.hero = SOLDIER
    return src


# ---- edge cases ----
def edge():
    rnd = random.Random(7)
    base = soldiers()[0]
    x0, y0, z0 = base.x[0], base.y[0], base.z[0]
    tracks = []

    # track 1: every curve form. circles, standing still past CURVE_GAP_MAX, a teleport, a fast line, a jump, jitter,
    # aim flicks, yaw wrapping past 180 twice, small and large pitch moves
    n = 4200
    T = G.Track(0, SOLDIER, 0, 0, n, [120, 2000])
    for s in range(n):
        if s < 500:
            a = s * 0.02
            x, y, z = x0 + 2 * math.cos(a) - 2, y0, z0 + 2 * math.sin(a)
        elif s < 1800:
            x, y, z = x0, y0, z0 + 2 * math.sin(10)
        elif s < 2400:
            k = s - 1800
            x, y, z = x0 + 2.5 + 0.12 * (k % 30 if k // 30 % 2 == 0 else 30 - k % 30), y0, z0     # 7.5 m/s back and forth
            if 2000 <= s < 2060:     # a jump
                tj = (s - 2000) / 62.5
                y = y0 + 6 * tj - 0.5 * 17.5 * tj * tj
        else:
            x, y, z = x0 + rnd.uniform(-0.3, 0.3), y0 + rnd.uniform(0, 0.02), z0 + rnd.uniform(-0.3, 0.3)
        T.x[s], T.y[s], T.z[s] = x, y, z

        if s < 500:
            yaw = s * 1.5 + 20 * math.sin(s * 0.05)          # passes 180 twice, steady and accelerating turns
            pitch = 30 * math.sin(s * 0.03)
        elif s < 1800:
            yaw, pitch = T.yaw[499], T.pitch[499]
        elif s == 1800:
            yaw, pitch = T.yaw[499] + 90, -60                # a flick
        elif s < 2400:
            yaw = T.yaw[s - 1] + rnd.uniform(-15, 15)         # large per-frame moves, delta keys
            pitch = max(-89, min(89, T.pitch[s - 1] + rnd.uniform(-3, 3)))
        else:
            yaw = T.yaw[s - 1] + rnd.choice([0, 0.05, -0.05, 0.31, -0.32, 0.08, -0.09, 2.55, -2.56, 20.4])
            pitch = max(-89, min(89, T.pitch[s - 1] + rnd.choice([0, 0.07, -0.08, 0.3, -0.3, 2.55, -2.56])))
        T.yaw[s], T.pitch[s] = G.wrap(yaw), pitch

        T.b[s] = 0 if 2000 <= s < 2060 else 8192     # on the ground but for the jump
        T.hp[s] = 200
        T.tx[s] = T.tz[s] = 0.0
    tracks.append(T)

    # track 2: every steps form and limit. each button bit alone, several at once, throttle levels and analog values,
    # health changes, gaps right at the 1-char and 2-char limits, an idle stretch past KEY_GAP_MAX
    n = 5200
    T = G.Track(1, SOLDIER, 1, 40, n, [])
    for s in range(n):
        T.x[s], T.y[s], T.z[s] = base.x[s % base.n], base.y[s % base.n], base.z[s % base.n]
        T.yaw[s], T.pitch[s] = base.yaw[s % base.n], base.pitch[s % base.n]
    events = []     # (frame, field, value)
    f = 0
    for bit in range(15):
        f += 5 + bit
        events.append((f, "b", 1 << bit))
        f += 3
        events.append((f, "b", 0))
    for gap in (128, 129, 127):
        f += gap
        events.append((f, "b", 3 | 64))
        f += 2
        events.append((f, "b", 0))
    for gap in (113, 114, 112, 1):
        f += gap
        events.append((f, "t", (1, -1)))
        f += 1
        events.append((f, "t", (0, 0)))
    for t in ((-1, 0), (0, 1), (1, 1), (-1, -1), (0.5, 0), (0.93, -0.27), (0.0002, 0), (-0.9998, 1), (0, 0)):
        f += 7
        events.append((f, "t", t))
    for hp in (180, 179.5, 0.25, 0, 200):
        f += 11
        events.append((f, "hp", hp))
    f += 9
    events.append((f, "b", 16384))                  # dead
    f += 30
    events.append((f, "b", 0))
    f += 2100                                       # idle past KEY_GAP_MAX
    events.append((f, "b", 1 + 2 + 4 + 8 + 16 + 32 + 64 + 128 + 256 + 512 + 1024 + 2048 + 4096 + 8192 + 16384))
    f += 1
    events.append((f, "t", (1, 1)))
    events.append((f, "b", 5))                      # buttons and throttle at once
    for k in range(200):
        f += rnd.randint(1, 6)
        r = rnd.random()
        events.append((f, "b", rnd.randrange(32768)) if r < 0.5 else (f, "t", (rnd.choice((-1, 0, 1)), rnd.choice((-1, 0, 1)))))
    assert f < n - 1, f
    b, t, hp = 0, (0, 0), 200
    ev = {}
    for e in events:
        ev.setdefault(e[0], []).append(e)
    for s in range(n):
        for _, field, value in ev.get(s, []):
            if field == "b":
                b = value
            elif field == "t":
                t = value
            else:
                hp = value
        T.b[s], T.tx[s], T.tz[s], T.hp[s] = b, t[0], t[1], hp
    tracks.append(T)

    # track 3: real data, starts later than the others
    S = soldiers()[3]
    S.t = 2; S.start = 100
    tracks.append(S)
    return tracks


def main():
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    write("packed2-test.txt", soldiers(), 5001)
    write("packed2-edge-test.txt", edge(), 5002)


if __name__ == "__main__":
    main()
