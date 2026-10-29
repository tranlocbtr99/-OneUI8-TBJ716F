#!/usr/bin/env python3
"""Report exact framework-matrix HAL requirements absent from Lenovo vendor manifests.

Static triage only; NOT a substitute for official checkvintf.
"""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_hals(paths):
    result = []
    for path in paths:
        root = ET.parse(path).getroot()
        for hal in root.findall("hal"):
            name = hal.findtext("name")
            if not name:
                continue
            instances = []
            for interface in hal.findall("interface"):
                iname = interface.findtext("name")
                for instance in interface.findall("instance"):
                    instances.append(f"{iname}/{instance.text}")
                for pattern in interface.findall("regex-instance"):
                    instances.append(f"{iname}/regex:{pattern.text}")
            instances.extend(x.text for x in hal.findall("fqname") if x.text)
            result.append({
                "name": name,
                "format": hal.get("format", "hidl"),
                "versions": sorted(x.text for x in hal.findall("version") if x.text),
                "instances": sorted(instances),
                "optional": hal.get("optional") == "true",
                "source": str(path),
            })
    return result

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--framework-matrices", type=Path, required=True)
    ap.add_argument("--vendor-manifests", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    matrices = sorted(a.framework_matrices.rglob("*.xml"))
    vendors = sorted(a.vendor_manifests.rglob("*.xml"))
    if not matrices or not vendors:
        ap.error("Both directories must contain extracted XML files")
    required = parse_hals(matrices)
    declared = parse_hals(vendors)
    vendor_names = {(x["name"], x["format"]) for x in declared}
    missing = [x for x in required if not x["optional"] and (x["name"], x["format"]) not in vendor_names]
    shared = [x for x in required if (x["name"], x["format"]) in vendor_names]
    report = {
        "device": "TB-J716F",
        "framework_matrix_files": [str(p) for p in matrices],
        "vendor_manifest_files": [str(p) for p in vendors],
        "required_hal_entries": len(required),
        "vendor_hal_entries": len(declared),
        "required_hal_names_absent": missing,
        "shared_name_entries_requiring_version_instance_check": shared,
        "complete_vintf_compatible": None,
        "flashable": False,
        "limitations": [
            "Only detects absent HAL names/formats, not versions, instances, regex matching, kernel or sepolicy compatibility.",
            "Optional HALs are not treated as required.",
            "Use official checkvintf with complete partition manifests, matrices, kernel and properties before changing ROM.",
        ],
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Missing required HAL names/formats: {len(missing)}; shared entries needing official checkvintf: {len(shared)}")
    if missing:
        for item in missing:
            print(item["name"], item["format"], item["source"])
if __name__ == "__main__":
    main()
