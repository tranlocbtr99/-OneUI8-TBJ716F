#!/usr/bin/env python3
"""Create a reversible, non-flashable One UI 8 TB-J716F adaptation overlay.

This is a staging overlay, not a bootable ROM or a compatibility claim.
It never touches boot, vendor, odm, vbmeta, or device firmware.
"""
import argparse
import hashlib
import json
from pathlib import Path

TARGET = "TB-J716F"
FILES = {
    "system/etc/oneui8-tbj716f/port-metadata.json": None,
    "system/etc/oneui8-tbj716f/README.txt": (
        "One UI 8 TB-J716F staging overlay.\n"
        "Preserve Lenovo stock vendor, odm, boot, vendor_boot, dtbo, and vbmeta.\n"
        "Do not flash this overlay. No hardware compatibility is established.\n"
        "Validate full VINTF, SELinux, kernel, partition sizes and rollback first.\n"
    ),
}

def create(out: Path):
    if out.exists() and any(out.iterdir()):
        raise ValueError("Output directory must be empty")
    out.mkdir(parents=True, exist_ok=True)
    metadata = {
        "target_device": TARGET,
        "donor": "Nekover2/OneUI8-Tablet-GSI",
        "donor_android_api": 36,
        "stage": "offline-staging-only",
        "verified_boot": False,
        "vintf_compatible": None,
        "flashable": False,
        "protected_partitions": [
            "boot", "vendor_boot", "vendor", "odm", "dtbo", "vbmeta", "vbmeta_system"
        ],
        "policy": "No device-specific HAL, SELinux or property overrides without evidence"
    }
    for relative, value in FILES.items():
        dest = out / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if value is None:
            value = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
        dest.write_text(value, encoding="utf-8")
    hashes = {}
    for relative in FILES:
        hashes[relative] = hashlib.sha256((out / relative).read_bytes()).hexdigest()
    manifest = {"files": hashes, "flashable": False, "target": TARGET}
    (out / "overlay-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(create(args.output), indent=2))

if __name__ == "__main__":
    main()
