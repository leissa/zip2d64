# zip2d64

Convert C64 Zipcode 4-file disk sets (`1!name` … `4!name`) back into `.d64` images.

## Usage

```sh
python3 zip2d64.py '1!name'            # writes name.d64 next to the input files
python3 zip2d64.py '1!name' out.d64    # or choose the output file
```

Pass the `1!` file; `2!`–`4!` are picked up from the same directory.
No dependencies beyond Python 3.

## Format

Zipcode splits a 35-track disk into four files:

| File | Tracks |
|------|--------|
| `1!` | 1–8    |
| `2!` | 9–16   |
| `3!` | 17–25  |
| `4!` | 26–35  |

Each file starts with a 2-byte load address (`$03FE` for `1!`, followed by the
2-byte disk ID; `$0400` for the others), then a sequence of sector records:

```
track | (mode << 6), sector, payload
```

| Mode | Payload |
|------|---------|
| `00` | 256 raw bytes |
| `01` | 1 byte, repeated over the whole sector |
| `10` | `len, marker, data[len]`; inside `data`, `marker, count, value` expands to `count` × `value` |

Sectors are stored interleaved and written to their proper position in the
image. Trailing zero padding (common after XMODEM transfers) is ignored.
