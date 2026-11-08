# Generates the 4096-char encoding table (v3) used for exporting recordings.
# Only visible symbols/punctuation: control chars and U+2028/2029 break the inspector copy/paste,
# and "{}\<> are excluded for workshop/OSTW string safety. Skips chars that Unicode NFC/NFD normalization changes 
# (e.g. U+037E -> ';', U+2ADC -> 2 chars): they become duplicates or split when text is normalized and decode to 
# the wrong value. Ends at U+A493 (Yi radicals). Output: OSTW string expression, 32 pieces of 128 chars joined with +.

import hashlib
import io
import sys
import unicodedata

OK_CATEGORIES = {"So", "Sm", "Sc", "Sk", "Po", "Pd", "Ps", "Pe", "Pi", "Pf", "Pc"}
BANNED = '"{}\\<>'
# chars added to Unicode after the table was made. the table can't change, every export depends on it, but unicodedata
# follows the Python version. a newer Python can add more, char_table() then fails instead of shifting the table
NEWER_CHARS = "\u1b4e\u1b4f\u1b7f\u20c1\u2427\u2428\u2429\u2b96\u2ffc\u2ffd\u2ffe\u2fff\u31e4\u31e5\u31ef"
TABLE_SHA256 = "dade0e4a6c675df5c29f3be40fbf806d52401439257ebbeddfd827c2af74a48c"     # of the table in export/export.del


def char_table():
    chars = []
    for cp in range(0x21, 0x10000):
        c = chr(cp)
        if c in BANNED or c in NEWER_CHARS or unicodedata.category(c) not in OK_CATEGORIES:
            continue
        if unicodedata.normalize("NFC", c) != c or unicodedata.normalize("NFD", c) != c:
            continue
        chars.append(c)
        if len(chars) == 4096:
            break
    table = "".join(chars)
    if hashlib.sha256(table.encode()).hexdigest() != TABLE_SHA256:
        raise ValueError(f"char table isn't the one in export.del, Unicode {unicodedata.unidata_version} may have added chars to NEWER_CHARS")
    return table


if __name__ == "__main__":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    table = char_table()
    print(" +\n".join(f'"{table[i * 128:(i + 1) * 128]}"' for i in range(32)))
