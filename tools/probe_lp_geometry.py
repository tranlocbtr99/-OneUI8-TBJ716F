#!/usr/bin/env python3
"""Read-only Android LP geometry probe (not a substitute for lpdump)."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

MAGIC = 0x616c4467
GEOMETRY_SIZE = 4096

def probe(path):
    results = []
    with open(path, "rb") as f:
        for offset in (4096, 8192):
            f.seek(offset)
            block = f.read(GEOMETRY_SIZE)
            if len(block) != GEOMETRY_SIZE:
                results.append({"offset": offset, "valid": False, "reason": "short read"})
                continue
            magic, size = struct.unpack_from("<II", block)
            valid = magic == MAGIC and 52 <= size <= GEOMETRY_SIZE
            checksum_ok = False
            if valid:
                copy = bytearray(block[:size])
                stored = bytes(copy[8:40])
                copy[8:40] = b"\\x00" * 32
                checksum_ok = hashlib.sha256(copy).digest() == stored
            results.append({"offset": offset, "magic": hex(magic),
                            "geometry_size": size, "valid": valid and checksum_ok,
                            "checksum_ok": checksum_ok})
    return {"geometry": results, "has_valid_geometry": any(x["valid"] for x in results),
            "warning": "Geometry probe only; does not validate LP partition tables or extent mappings."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("image", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = probe(args.image)
    args.output.write_text(json.dumps(result, indent=2)+"\\n")
    print(json.dumps(result, indent=2))
    if not result["has_valid_geometry"]:
        raise SystemExit("No verified LP geometry at standard offsets; investigate reconstruction/base offset.")
