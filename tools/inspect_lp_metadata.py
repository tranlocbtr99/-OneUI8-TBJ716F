#!/usr/bin/env python3
"""Validate Android liblp primary metadata and enumerate logical partitions (read-only)."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

GEOMETRY_MAGIC = 0x616c4467
HEADER_MAGIC = 0x414C5030

def sha_ok(blob, start, length):
    b = bytearray(blob)
    expected = bytes(b[start:start+length])
    b[start:start+length] = bytes(length)
    return hashlib.sha256(b).digest() == expected

def inspect(path):
    with open(path, "rb") as f:
        f.seek(4096)
        geom = f.read(4096)
        if struct.unpack_from("<I", geom)[0] != GEOMETRY_MAGIC or not sha_ok(geom[:52], 8, 32):
            raise ValueError("Invalid LP geometry")
        max_size, slots, block_size = struct.unpack_from("<III", geom, 40)
        if not (128 <= max_size <= 4*1024*1024 and 1 <= slots <= 8 and block_size >= 512):
            raise ValueError("Unreasonable geometry parameters")
        f.seek(12288)
        header = f.read(256)
        magic, major, minor, header_size = struct.unpack_from("<IHHI", header)
        if magic != HEADER_MAGIC or not (128 <= header_size <= 256):
            raise ValueError(f"Invalid metadata header: {magic:#x}")
        if not sha_ok(header[:header_size], 12, 32):
            raise ValueError("Metadata header checksum mismatch")
        tables_size = struct.unpack_from("<I", header, 44)[0]
        if tables_size > max_size - header_size:
            raise ValueError("Tables exceed geometry metadata_max_size")
        f.seek(12288+header_size)
        tables = f.read(tables_size)
        if len(tables) != tables_size or hashlib.sha256(tables).digest() != header[48:80]:
            raise ValueError("Metadata tables checksum mismatch")
        descriptors = []
        for i in range(4):
            offset, count, size = struct.unpack_from("<III", header, 80+i*12)
            if offset + count*size > tables_size:
                raise ValueError("Table descriptor outside bounds")
            descriptors.append((offset,count,size))
        po, pc, ps = descriptors[0]
        eo, ec, es = descriptors[1]
        if ps < 52 or es < 24:
            raise ValueError("Unexpected partition/extent entry size")
        partitions = []
        for i in range(pc):
            item = tables[po+i*ps:po+(i+1)*ps]
            name = item[:36].split(bytes(1))[0].decode("ascii", errors="replace")
            attributes, first, count, group = struct.unpack_from("<IIII", item, 36)
            if first+count > ec:
                raise ValueError("Partition extents out of range")
            extents = []
            for j in range(first,first+count):
                x = tables[eo+j*es:eo+(j+1)*es]
                num_sectors, target_type, target_data, target_source = struct.unpack_from("<QIQI", x)
                extents.append({"sectors": num_sectors, "type": target_type,
                                "target_data": target_data, "target_source": target_source})
            partitions.append({"name": name, "attributes": attributes,
                               "group_index": group, "extents": extents})
        return {"version": f"{major}.{minor}", "metadata_max_size": max_size,
                "metadata_slot_count": slots, "logical_block_size": block_size,
                "tables_checksum_ok": True, "partitions": partitions}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("image", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    data = inspect(a.image)
    a.output.write_text(json.dumps(data, indent=2)+chr(10))
    print("Partitions:", ", ".join(p["name"] for p in data["partitions"]))
    print("Metadata tables SHA-256 verified; partitions:", len(data["partitions"]))
    if not any(p["name"].startswith("vendor") for p in data["partitions"]):
        raise SystemExit("No vendor logical partition found")
