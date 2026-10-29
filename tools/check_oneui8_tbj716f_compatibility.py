#!/usr/bin/env python3
"""Conservative offline compatibility gate for One UI 8 on TB-J716F.

Input JSON is an evidence manifest, NOT an instruction to flash.
Unknown fields never silently pass.
"""
import argparse
import json
from pathlib import Path

TARGET = "TB-J716F"
DONOR_API = 36
DONOR_ABI = "arm64-v8a"

def assess(e):
    checks = []
    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})
    model = e.get("model")
    add("device_identity", "pass" if model == TARGET else ("unknown" if not model else "fail"),
        f"Expected exact model {TARGET}; got {model!r}")
    abis = e.get("supported_abis")
    add("arm64_userspace", "unknown" if abis is None else
        ("pass" if isinstance(abis, list) and DONOR_ABI in abis else "fail"),
        "One UI 8 donor requires arm64-v8a")
    vendor_api = e.get("vendor_api_level")
    add("vendor_api_level", "unknown" if vendor_api is None else
        ("pass" if type(vendor_api) is int and vendor_api >= 0 and e.get("vendor_runtime_verified") is True else
         "review" if type(vendor_api) is int and vendor_api >= 0 else "fail"),
        f"Donor Android API {DONOR_API}; vendor API {vendor_api!r}. Vendor API alone never proves Android 16 compatibility; requires tested VINTF/runtime evidence.")
    manifest = e.get("vintf_compatible")
    add("vintf", "unknown" if manifest is None else ("pass" if manifest is True else "fail"),
        "Requires actual donor framework compatibility matrix versus device vendor manifest")
    size = e.get("system_partition_capacity_bytes")
    required = e.get("donor_image_bytes", 6845104128)
    if type(required) is not int or required <= 0:
        raise ValueError("donor_image_bytes must be a positive integer")
    add("partition_capacity", "unknown" if size is None else
        ("pass" if type(size) is int and size >= required else "fail"),
        f"Total allocatable logical system capacity {size!r}; donor image {required!r} bytes; free space inside filesystem is not sufficient evidence")
    recovery = e.get("verified_recovery_path")
    add("recovery", "pass" if recovery is True else ("fail" if recovery is False else "unknown"),
        "A tested rollback route is mandatory before on-device trials")
    statuses = {c["status"] for c in checks}
    return {"target": TARGET, "donor_android_api": DONOR_API, "checks": checks,
            "ready_for_device_trial": statuses == {"pass"},
            "note": "Passing static checks is necessary but never proves boot compatibility"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path, default=Path("oneui8-compatibility-report.json"))
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        parser.error("Evidence must be a JSON object")
    result = assess(evidence)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ready_for_device_trial"] else 2)

if __name__ == "__main__":
    main()
