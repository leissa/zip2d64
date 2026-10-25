#!/usr/bin/env python3
"""Convert a 4-file Zipcode set (1!name .. 4!name) into a .d64 image.

usage: zip2d64.py <path/to/1!name> [out.d64]
"""
import sys
from pathlib import Path

def spt(track):
    return 21 if track <= 17 else 19 if track <= 24 else 18 if track <= 30 else 17

def offset(track, sector):
    return (sum(spt(t) for t in range(1, track)) + sector) * 256

def unpack(data, img, first):
    pos = 4 if first else 2          # load addr (+ 2-byte disk ID in file 1)
    while pos + 1 < len(data):
        tb, sector = data[pos], data[pos + 1]
        if tb == 0:                  # zero padding after the last record
            break
        pos += 2
        track, mode = tb & 0x3f, tb >> 6
        if mode == 0:                # raw sector
            buf = data[pos:pos + 256]
            pos += 256
        elif mode == 1:              # sector filled with one byte
            buf = bytes([data[pos]]) * 256
            pos += 1
        elif mode == 2:              # run-length encoded
            length, rep = data[pos], data[pos + 1]
            pos += 2
            end = pos + length
            out = bytearray()
            while pos < end:
                c = data[pos]
                pos += 1
                if c == rep:
                    out += bytes([data[pos + 1]]) * data[pos]
                    pos += 2
                else:
                    out.append(c)
            buf = bytes(out)
        else:
            sys.exit(f"bad record type at offset {pos - 2}")
        if len(buf) != 256 or not 1 <= track <= 35 or sector >= spt(track):
            sys.exit(f"corrupt record T{track} S{sector}")
        o = offset(track, sector)
        img[o:o + 256] = buf

def main():
    first = Path(sys.argv[1])
    name = first.name.split("!", 1)[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else first.with_name(name + ".d64")
    img = bytearray(174848)
    for i in range(1, 5):
        unpack((first.parent / f"{i}!{name}").read_bytes(), img, i == 1)
    out.write_bytes(img)
    print(f"wrote {out}")

if __name__ == "__main__":
    main()
