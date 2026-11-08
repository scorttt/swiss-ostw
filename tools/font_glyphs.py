import os, struct, sys, unicodedata

FONT = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\BlizzardGlobal.ttf")


def code_points(path=FONT):
    data = open(path, "rb").read()
    num_tables = struct.unpack(">H", data[4:6])[0]
    cmap = None
    for i in range(num_tables):
        tag, _, offset, _ = struct.unpack(">4sIII", data[12 + 16 * i:28 + 16 * i])
        if tag == b"cmap":
            cmap = offset
    if cmap is None:
        raise SystemExit("no cmap table")

    cps = set()
    n = struct.unpack(">H", data[cmap + 2:cmap + 4])[0]
    for i in range(n):
        _, _, sub = struct.unpack(">HHI", data[cmap + 4 + 8 * i:cmap + 12 + 8 * i])
        at = cmap + sub
        fmt = struct.unpack(">H", data[at:at + 2])[0]
        if fmt == 4:
            segs = struct.unpack(">H", data[at + 6:at + 8])[0] // 2
            ends = struct.unpack(f">{segs}H", data[at + 14:at + 14 + 2 * segs])
            p = at + 16 + 2 * segs
            starts = struct.unpack(f">{segs}H", data[p:p + 2 * segs])
            p += 2 * segs
            deltas = struct.unpack(f">{segs}h", data[p:p + 2 * segs])
            p += 2 * segs
            ro_at = p
            ros = struct.unpack(f">{segs}H", data[p:p + 2 * segs])
            for s in range(segs):
                for c in range(starts[s], ends[s] + 1):
                    if c == 0xFFFF:
                        continue
                    if ros[s] == 0:
                        gid = (c + deltas[s]) & 0xFFFF
                    else:
                        g_at = ro_at + 2 * s + ros[s] + 2 * (c - starts[s])
                        gid = struct.unpack(">H", data[g_at:g_at + 2])[0]
                        if gid:
                            gid = (gid + deltas[s]) & 0xFFFF
                    if gid:
                        cps.add(c)
        elif fmt == 12:
            groups = struct.unpack(">I", data[at + 12:at + 16])[0]
            for g in range(groups):
                lo, hi, gid = struct.unpack(">III", data[at + 16 + 12 * g:at + 28 + 12 * g])
                for c in range(lo, hi + 1):
                    if gid + (c - lo):
                        cps.add(c)
    return cps


def ranges(cps):
    out, run = [], None
    for c in sorted(cps):
        if run and c == run[1] + 1:
            run[1] = c
        else:
            if run:
                out.append(tuple(run))
            run = [c, c]
    if run:
        out.append(tuple(run))
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cps = code_points()
    if len(sys.argv) > 1 and sys.argv[1] == "--blocks":
        print(f"{len(cps)} code points")
        for lo, hi in ranges(cps):
            print(f"U+{lo:04X}-U+{hi:04X} ({hi - lo + 1})  {chr(lo)}..{chr(hi)}")
    else:
        for ch in "".join(sys.argv[1:]):
            name = unicodedata.name(ch, "?")
            print(f"{'in font ' if ord(ch) in cps else 'MISSING '} {ch}  U+{ord(ch):04X} {name}")
