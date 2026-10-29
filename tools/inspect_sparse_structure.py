#!/usr/bin/env python3
"""Read-only structural inspection of Android sparse images embedded in ZIP archives."""
import argparse
import json
from pathlib import Path
import struct
import zipfile

MAGIC = 0xED26FF3A
CHUNKS = {0xCAC1: "raw", 0xCAC2: "fill", 0xCAC3: "dont_care", 0xCAC4: "crc32"}
MAX_CHUNKS = 1000000

def inspect_sparse(stream, file_size):
    header = stream.read(28)
    if len(header) != 28:
        return {"valid": False, "reason": "truncated header"}
    magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, total_blks, total_chunks, checksum = struct.unpack("<IHHHHIIII", header)
    if magic != MAGIC or major != 1 or file_hdr_sz < 28 or chunk_hdr_sz < 12 or blk_sz == 0 or total_chunks > MAX_CHUNKS:
        return {"valid": False, "reason": "unsupported or invalid sparse header"}
    if file_hdr_sz > 4096 or chunk_hdr_sz > 4096:
        return {"valid": False, "reason": "unreasonably large header"}
    if file_hdr_sz > 28:
        stream.read(file_hdr_sz - 28)
    chunks = {}
    expanded = 0
    for i in range(total_chunks):
        data = stream.read(chunk_hdr_sz)
        if len(data) != chunk_hdr_sz:
            return {"valid": False, "reason": f"truncated chunk header {i}"}
        kind, reserved, blocks, total_sz = struct.unpack_from("<HHII", data)
        payload = total_sz - chunk_hdr_sz
        expected = {0xCAC1: blocks * blk_sz, 0xCAC2: 4, 0xCAC3: 0, 0xCAC4: 4}.get(kind)
        if expected is None or payload != expected:
            return {"valid": False, "reason": f"invalid chunk type/size at {i}"}
        expanded += blocks
        if expanded > total_blks:
            return {"valid": False, "reason": "chunk blocks exceed header total"}
        chunks[CHUNKS[kind]] = chunks.get(CHUNKS[kind], 0) + 1
        # Skip payload by reading in bounded pieces; no extracted image is written.
        remaining = payload
        while remaining:
            buf = stream.read(min(1024 * 1024, remaining))
            if not buf:
                return {"valid": False, "reason": f"truncated chunk payload {i}"}
            remaining -= len(buf)
    return {"valid": expanded == total_blks, "chunk_types": chunks, "expanded_bytes": expanded * blk_sz,
            "total_chunks": total_chunks, "note": "Sparse structure only; no checksum or filesystem validation"}

def inspect_zip(archive):
    from inventory_firmware_zip import inventory
    index = inventory(archive)
    result = []
    with zipfile.ZipFile(archive) as z:
        for entry in index["entries"]:
            if entry["type"] != "partition_image" or not entry["path"].lower().endswith(".img"):
                continue
            with z.open(entry["path"]) as stream:
                magic = stream.read(4)
                if magic != struct.pack("<I", MAGIC):
                    continue
                # Re-open to include header in parser.
            with z.open(entry["path"]) as stream:
                result.append({"path": entry["path"], **inspect_sparse(stream, entry["uncompressed_bytes"])})
    return {"scope": "read-only sparse structure; not integrity/compatibility validation", "sparse_images": result}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path("sparse-structure.json"))
    args = p.parse_args()
    result = inspect_zip(args.archive)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
