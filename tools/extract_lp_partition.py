#!/usr/bin/env python3
"""Read-only extraction of a linear liblp logical partition from reconstructed super."""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_lp_metadata import inspect

SECTOR = 512
CHUNK = 4 * 1024 * 1024

def extract(super_path, partition_name, output, report):
    meta = inspect(super_path)
    parts = [p for p in meta["partitions"] if p["name"] == partition_name]
    if len(parts) != 1:
        raise ValueError("Expected exactly one partition named " + partition_name)
    part = parts[0]
    if not part["extents"]:
        raise ValueError("Partition has no extents")
    source_size = super_path.stat().st_size
    total = 0
    sha = hashlib.sha256()
    with super_path.open("rb") as src, output.open("wb") as dst:
        for ext in part["extents"]:
            length = ext["sectors"] * SECTOR
            if length <= 0:
                raise ValueError("Invalid extent length")
            if ext["type"] == 0:
                if ext["target_source"] != 0:
                    raise ValueError("Unexpected block device index; refusing extraction")
                offset = ext["target_data"] * SECTOR
                if offset < 0 or offset + length > source_size:
                    raise ValueError("Extent outside reconstructed super")
                src.seek(offset)
                remaining = length
                while remaining:
                    data = src.read(min(CHUNK, remaining))
                    if not data:
                        raise ValueError("Short read")
                    dst.write(data)
                    sha.update(data)
                    remaining -= len(data)
            elif ext["type"] == 1:
                zero = bytes(CHUNK)
                remaining = length
                while remaining:
                    data = zero[:min(CHUNK, remaining)]
                    dst.write(data)
                    sha.update(data)
                    remaining -= len(data)
            else:
                raise ValueError("Unsupported extent type " + str(ext["type"]))
            total += length
    result = {"partition": partition_name, "bytes": total, "sha256": sha.hexdigest(),
              "extents": len(part["extents"]), "filesystem_validated": False}
    report.write_text(json.dumps(result, indent=2) + chr(10))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("super_image", type=Path)
    p.add_argument("--partition", default="vendor_a")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args()
    extract(args.super_image, args.partition, args.output, args.report)
