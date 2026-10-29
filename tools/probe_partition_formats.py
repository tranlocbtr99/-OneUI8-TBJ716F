#!/usr/bin/env python3
"""Inspect partition-image magic inside ZIP entries without extracting images."""
import argparse
import json
from pathlib import Path
import struct
import zipfile

from inventory_firmware_zip import inventory

SPARSE_MAGIC = b"\x3a\xff\x26\xed"
EROFS_MAGIC = b"\xe2\xe1\xf5\xe0"
LP_METADATA_MAGIC = b"\x30\x50\x4c\x41"

def identify(prefix):
    if prefix[:4] == SPARSE_MAGIC:
        if len(prefix) < 28:
            return "android_sparse_truncated"
        major, minor, file_header, chunk_header, block_size, blocks, chunks, checksum = struct.unpack_from("<HHHHIIII", prefix, 4)
        if major != 1 or file_header < 28 or chunk_header < 12 or block_size == 0:
            return "android_sparse_invalid_header"
        return "android_sparse_v1"
    if prefix[:4] == LP_METADATA_MAGIC:
        return "android_dynamic_partition_metadata_candidate"
    if prefix[1024:1028] == EROFS_MAGIC:
        return "erofs_candidate"
    if prefix[1080:1082] == b"\x53\xef":
        return "ext4_candidate"
    return "unknown"

def inspect(archive):
    index = inventory(archive)
    results = []
    with zipfile.ZipFile(archive) as z:
        for entry in index["entries"]:
            if entry["type"] != "partition_image":
                continue
            with z.open(entry["path"]) as stream:
                prefix = stream.read(4096)
            results.append({"path": entry["path"], "format_hint": identify(prefix),
                            "size_bytes": entry["uncompressed_bytes"]})
    return {"scope": "first 4096 decompressed bytes per image; format hints only, not validated images",
            "images": results, "limitations": ["No extraction or dynamic partition unpacking",
            "No bootability, integrity, vendor compatibility or hardware conclusions"]}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path("image-format-hints.json"))
    args = p.parse_args()
    result = inspect(args.archive)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
