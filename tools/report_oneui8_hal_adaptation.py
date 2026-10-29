#!/usr/bin/env python3
"""Read-only donor/Lenovo HAL inventory for planning One UI 8 adaptation.

Compares names as a diagnostic only. It never certifies VINTF compatibility.
"""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def report(donor, manifest_xml):
    root = ET.fromstring(manifest_xml)
    if root.tag != "manifest" or root.get("type") != "device":
        raise ValueError("Expected a device VINTF manifest")
    vendor = {}
    for hal in root.findall("hal"):
        name = hal.findtext("name")
        if not name:
            continue
        vendor.setdefault(name, []).append({
            "format": hal.get("format", "hidl"),
            "versions": [v.text for v in hal.findall("version") if v.text],
            "interfaces": [
                {"name": i.findtext("name"), "instances": [v.text for v in i.findall("instance") if v.text]}
                for i in hal.findall("interface")
            ],
            "fqnames": [v.text for v in hal.findall("fqname") if v.text],
        })
    matrix = {}
    for key, entry in donor.get("files", {}).items():
        if not key.startswith("framework_matrix_level_"):
            continue
        if not entry.get("present"):
            continue
        summary = entry.get("vintf_summary", {})
        if summary.get("parse_error"):
            continue
        matrix[key] = sorted(set(summary.get("hal_names", [])))
    if not matrix:
        raise ValueError("Donor has no parsed framework matrix inventory")
    names = set(vendor)
    return {
        "device_target_level": root.get("target-level"),
        "vendor_hal_count": sum(map(len, vendor.values())),
        "vendor_hals": vendor,
        "donor_framework_matrices": {
            k: {
                "declared_hal_names": v,
                "names_also_in_vendor": sorted(set(v) & names),
                "names_absent_from_vendor": sorted(set(v) - names),
                "vendor_names_not_in_this_matrix": sorted(names - set(v)),
            } for k, v in sorted(matrix.items())
        },
        "vintf_compatible": None,
        "boot_verified": False,
        "warning": "HAL names are diagnostic only. FCM applicability, optional HALs, versions, instances, kernel and SELinux are NOT validated. Never use as flash approval."
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("donor_inventory", type=Path)
    p.add_argument("vendor_manifest", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    result = report(json.loads(a.donor_inventory.read_text()), a.vendor_manifest.read_text())
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("Vendor target level:", result["device_target_level"])
    print("Vendor HAL names:", len(result["vendor_hals"]))
    for k, v in result["donor_framework_matrices"].items():
        print(k, "overlap", len(v["names_also_in_vendor"]), "absent", len(v["names_absent_from_vendor"]))
    print("Compatibility remains unverified")

if __name__ == "__main__":
    main()
