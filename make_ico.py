"""Gera icon.ico com o mesmo design do favicon.svg. Apenas stdlib."""
import os, struct, zlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")

BG    = (30,  41,  59, 255)   # #1e293b
BLUE  = (59, 130, 246, 255)   # #3b82f6
GRAY  = (148,163, 184, 255)   # #94a3b8
WHITE = (241,245, 249, 255)   # #f1f5f9
LINE  = (203,213, 225, 255)   # #cbd5e1
GREEN = (74, 222, 128, 255)   # #4ade80
CLEAR = (0,   0,   0,   0)


def make_pixels(size):
    s = size / 32.0
    grid = [[BG] * size for _ in range(size)]

    def fill(x1, y1, x2, y2, col):
        for r in range(max(0, y1), min(size, y2)):
            for c in range(max(0, x1), min(size, x2)):
                grid[r][c] = col

    def circle(cx, cy, rad, col):
        for r in range(size):
            for c in range(size):
                if (c + 0.5 - cx) ** 2 + (r + 0.5 - cy) ** 2 <= rad ** 2:
                    grid[r][c] = col

    def sc(v):
        return round(v * s)

    fill(sc(10), sc(7),  sc(22), sc(13), GRAY)   # paper input
    fill(sc(7),  sc(12), sc(25), sc(23), BLUE)   # printer body
    fill(sc(10), sc(19), sc(22), sc(26), WHITE)  # paper output
    fill(sc(12), sc(21), sc(19), sc(23), LINE)   # output line 1
    fill(sc(12), sc(24), sc(17), sc(26), LINE)   # output line 2
    circle(22.5 * s, 16.5 * s, 2 * s, GREEN)    # status dot

    # Transparent corners to match SVG rx="7"
    rx = sc(7)
    for r in range(size):
        for c in range(size):
            dx, dy = min(c, size - 1 - c), min(r, size - 1 - r)
            if dx < rx and dy < rx and (rx - dx) ** 2 + (rx - dy) ** 2 > rx ** 2:
                grid[r][c] = CLEAR

    return grid


def png_bytes(pixels):
    n = len(pixels)
    raw = b"".join(b"\x00" + bytes(b for px in row for b in px) for row in pixels)

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


pngs = {sz: png_bytes(make_pixels(sz)) for sz in (48, 32, 16)}
count = len(pngs)
header = struct.pack("<HHH", 0, 1, count)
offset = 6 + 16 * count
dirs, data = b"", b""
for sz, png in pngs.items():
    w = sz if sz < 256 else 0
    dirs += struct.pack("<BBBBHHII", w, w, 0, 0, 1, 32, len(png), offset)
    offset += len(png)
    data += png

with open(OUT, "wb") as f:
    f.write(header + dirs + data)
print("OK", OUT)
