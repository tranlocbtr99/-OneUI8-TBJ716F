#!/usr/bin/env python3
"""Conservative dynamic-partition size budget; never authorizes flashing."""
import argparse
import json

SUPER_BYTES = 2097152 * 4096
DONOR_BYTES = 6845104128

def assess(super_bytes, donor_bytes, other_bytes=None, metadata_reserve_bytes=0):
    for key, value in {"super_bytes":super_bytes, "donor_bytes":donor_bytes,
                       "metadata_reserve_bytes":metadata_reserve_bytes}.items():
        if type(value) is not int or value < 0:
            raise ValueError(key + " must be a nonnegative integer")
    if other_bytes is not None and (type(other_bytes) is not int or other_bytes < 0):
        raise ValueError("other_bytes must be a nonnegative integer")
    remaining = super_bytes - donor_bytes - metadata_reserve_bytes
    return {
        "super_bytes": super_bytes,
        "donor_image_bytes": donor_bytes,
        "other_partition_bytes": other_bytes,
        "metadata_reserve_bytes": metadata_reserve_bytes,
        "remaining_before_other_partitions_bytes": remaining,
        "fits_known_budget": None if other_bytes is None else remaining >= other_bytes,
        "status": "insufficient_evidence" if other_bytes is None else ("capacity_only_pass" if remaining >= other_bytes else "capacity_fail"),
        "note": "Sparse/ext4 image size is not the final logical partition allocation. Actual LP metadata, group quotas, A/B allocation, partition sizes and VINTF must be inspected. Capacity-only pass never authorizes flashing."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--super-bytes", type=int, default=SUPER_BYTES)
    p.add_argument("--donor-bytes", type=int, default=DONOR_BYTES)
    p.add_argument("--other-partition-bytes", type=int)
    p.add_argument("--metadata-reserve-bytes", type=int, default=0)
    p.add_argument("--output")
    args=p.parse_args()
    report=assess(args.super_bytes,args.donor_bytes,args.other_partition_bytes,args.metadata_reserve_bytes)
    result=json.dumps(report,indent=2)+"\n"
    if args.output:
        with open(args.output,"w",encoding="utf-8") as f:f.write(result)
    else:
        print(result)
    if report["status"]=="capacity_fail":
        raise SystemExit(2)

if __name__=="__main__":
    main()
