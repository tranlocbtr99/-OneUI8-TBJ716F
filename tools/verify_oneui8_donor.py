#!/usr/bin/env python3
"""Preflight a local One UI 8 donor image without modifying or flashing it."""
import argparse
import hashlib
import json
from pathlib import Path

DONOR_ZST = "OneUI8-GSI-arm64-A16-MysticTech-TabS9-nonsamsung-fix-20260813.img.zst"
DONOR_SHA256 = "b9155186e0bf0ef88ef30181395c7be85f854edfe7bddccf6029a8941b8274b1"
DONOR_SIZE = 2683294844
RAW_SIZE = 6845104128
RAW_MD5 = "6946aa3fdcafa3475c1809b640f0df5c"
MAX_BYTES = 8 * 1024**3

def inspect(path):
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError("Refusing to hash an unexpectedly large donor image")
    if size == DONOR_SIZE:
        expected_hash, algorithm, expected_size = DONOR_SHA256, "sha256", DONOR_SIZE
        candidate_type = "compressed_zst"
    elif size == RAW_SIZE:
        expected_hash, algorithm, expected_size = RAW_MD5, "md5", RAW_SIZE
        candidate_type = "raw_img"
    else:
        return {"status": "rejected", "reason": "Unexpected size for documented patched donor",
                "size_bytes": size, "candidate_type": "unknown"}
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    actual = h.hexdigest()
    return {"status": "verified_against_upstream_manifest" if actual == expected_hash else "rejected",
            "candidate_type": candidate_type, "size_bytes": size, "hash_algorithm": algorithm,
            "actual_hash": actual, "expected_hash": expected_hash,
            "scope": "Upstream published checksum only; no device boot, authenticity or license validation"}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--output", type=Path, default=Path("donor-preflight.json"))
    args = p.parse_args()
    result = inspect(args.image)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] == "rejected":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
