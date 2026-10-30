#!/usr/bin/env python3
"""Read-only LP extent accounting from inspect_lp_metadata.py JSON."""
import argparse
import json
from pathlib import Path

SECTOR_BYTES = 512

def summarize(data, super_bytes, donor_bytes):
    if type(super_bytes) is not int or super_bytes <= 0 or type(donor_bytes) is not int or donor_bytes <= 0:
        raise ValueError("positive integer sizes required")
    partitions = data.get("partitions")
    if not isinstance(partitions, list) or not data.get("tables_checksum_ok"):
        raise ValueError("verified LP partition metadata required")
    entries = []
    for p in partitions:
        name = p.get("name")
        if not isinstance(name, str) or not name:
            raise ValueError("invalid partition name")
        extents = p.get("extents")
        if not isinstance(extents, list):
            raise ValueError("missing extents")
        sectors = 0
        physical_sectors = 0
        for e in extents:
            n = e.get("sectors")
            if type(n) is not int or n < 0 or e.get("type") not in (0, 1):
                raise ValueError("unsupported extent")
            sectors += n
            if e["type"] == 0:
                physical_sectors += n
        entries.append({"name": name, "allocated_bytes": sectors * SECTOR_BYTES,
                        "physical_linear_bytes": physical_sectors * SECTOR_BYTES,
                        "group_index": p.get("group_index")})
    by_name = {e["name"]: e for e in entries}
    if len(by_name) != len(entries):
        raise ValueError("duplicate partition names")
    system_candidates = [e for e in entries if e["name"] in ("system_a", "system")]
    other = [e for e in entries if e["name"] not in ("system_a", "system")]
    total = sum(e["allocated_bytes"] for e in entries)
    physical_total = sum(e["physical_linear_bytes"] for e in entries)
    return {"super_bytes": super_bytes, "donor_image_bytes": donor_bytes,
            "partitions": entries, "allocated_all_logical_bytes": total,
            "allocated_linear_physical_bytes": physical_total,
            "non_system_allocated_bytes": sum(e["allocated_bytes"] for e in other),
            "nominal_remaining_after_donor_and_other_bytes": super_bytes - donor_bytes - sum(e["allocated_bytes"] for e in other),
            "non_system_linear_physical_bytes": sum(e["physical_linear_bytes"] for e in other),
            "system_partition_candidates": system_candidates,
            "status": "evidence_only_not_flashable",
            "warning": "Nominal estimate includes zero-filled extents and may double-count A/B slots. Physical linear extents are reported separately. Metadata groups, slot sharing, sparse used blocks and actual usable capacity must be verified before repartition."}

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("lp_json",type=Path)
    p.add_argument("--super-bytes",type=int,default=8589934592)
    p.add_argument("--donor-bytes",type=int,default=6845104128)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=summarize(json.loads(a.lp_json.read_text()),a.super_bytes,a.donor_bytes)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("LP partitions:",len(result["partitions"]))
    print("Nominal remaining bytes:",result["nominal_remaining_after_donor_and_other_bytes"])
