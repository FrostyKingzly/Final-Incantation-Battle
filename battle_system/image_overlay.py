from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import List, Sequence, Tuple

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PngError(ValueError):
    pass


def _paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter_scanlines(raw: bytes, width: int, height: int, channels: int) -> bytearray:
    stride = width * channels
    expected_len = height * (stride + 1)
    if len(raw) != expected_len:
        raise PngError("Unexpected decompressed image length")

    out = bytearray(height * stride)
    for row in range(height):
        scanline_start = row * (stride + 1)
        filter_type = raw[scanline_start]
        src = raw[scanline_start + 1 : scanline_start + 1 + stride]
        dst_start = row * stride

        for i in range(stride):
            x = src[i]
            left = out[dst_start + i - channels] if i >= channels else 0
            up = out[dst_start - stride + i] if row > 0 else 0
            up_left = out[dst_start - stride + i - channels] if row > 0 and i >= channels else 0

            if filter_type == 0:
                out[dst_start + i] = x
            elif filter_type == 1:
                out[dst_start + i] = (x + left) & 0xFF
            elif filter_type == 2:
                out[dst_start + i] = (x + up) & 0xFF
            elif filter_type == 3:
                out[dst_start + i] = (x + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                out[dst_start + i] = (x + _paeth_predictor(left, up, up_left)) & 0xFF
            else:
                raise PngError(f"Unsupported PNG filter: {filter_type}")

    return out


def read_png_rgb(path: Path) -> Tuple[int, int, bytearray]:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise PngError("Not a PNG file")

    pos = len(PNG_SIGNATURE)
    width = height = 0
    bit_depth = color_type = interlace = None
    idat_parts: List[bytes] = []

    while pos < len(data):
        chunk_len = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + chunk_len]
        pos += 12 + chunk_len

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _comp, _filt, interlace = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width == 0 or height == 0:
        raise PngError("PNG missing IHDR")
    if bit_depth != 8 or color_type != 2:
        raise PngError("Only 8-bit RGB PNG files are supported")
    if interlace != 0:
        raise PngError("Interlaced PNG files are not supported")

    raw = zlib.decompress(b"".join(idat_parts))
    rgb = _unfilter_scanlines(raw, width, height, channels=3)
    return width, height, rgb


def write_png_rgb(path: Path, width: int, height: int, rgb: Sequence[int]) -> None:
    stride = width * 3
    if len(rgb) != height * stride:
        raise PngError("RGB buffer size does not match dimensions")

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(rgb[start : start + stride])

    compressed = zlib.compress(bytes(raw), level=9)

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png_data = PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png_data)


def create_battle_overlay(
    background_path: Path,
    enemy_path: Path,
    output_path: Path,
    *,
    enemy_scale: float = 0.62,
    enemy_offset_x: int = 15,
    enemy_offset_y: int = 190,
    chroma_key_threshold: int = 20,
) -> Path:
    bg_w, bg_h, bg_rgb = read_png_rgb(background_path)
    en_w, en_h, en_rgb = read_png_rgb(enemy_path)

    out = bytearray(bg_rgb)
    scaled_w = max(1, int(en_w * enemy_scale))
    scaled_h = max(1, int(en_h * enemy_scale))

    for sy in range(scaled_h):
        src_y = int(sy / enemy_scale)
        if src_y >= en_h:
            src_y = en_h - 1
        dy = enemy_offset_y + sy
        if dy < 0 or dy >= bg_h:
            continue

        for sx in range(scaled_w):
            src_x = int(sx / enemy_scale)
            if src_x >= en_w:
                src_x = en_w - 1
            dx = enemy_offset_x + sx
            if dx < 0 or dx >= bg_w:
                continue

            src_idx = (src_y * en_w + src_x) * 3
            r = en_rgb[src_idx]
            g = en_rgb[src_idx + 1]
            b = en_rgb[src_idx + 2]

            if r < chroma_key_threshold and g < chroma_key_threshold and b < chroma_key_threshold:
                continue

            dst_idx = (dy * bg_w + dx) * 3
            out[dst_idx] = r
            out[dst_idx + 1] = g
            out[dst_idx + 2] = b

    write_png_rgb(output_path, bg_w, bg_h, out)
    return output_path
