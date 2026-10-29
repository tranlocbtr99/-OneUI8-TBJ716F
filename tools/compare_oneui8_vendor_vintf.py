#!/usr/bin/env python3
"""Compare One UI 8 framework VINTF HAL names with a TB-J716F vendor manifest.

This is a preliminary name-only gap analysis, NOT a full VINTF compatibility check.
Version ranges, optionality, instances, transport, kernel requirements and SELinux
are not evaluated. Missing names are investigation leads, not proof of incompatibility.
"""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

def vendor_hals(xml_text):
    root = ET.fromstring(xml_text)
    if root.tag != "manifest" or root.get("type") != "device":
        raise ValueError("Expected a VINTF device manifest")
    return {node.text.strip() for hal in root.findall("hal")
            for node in hal.findall("name") if node.text and node.text.strip()}

def compare(inventory, manifest_text):
    vendor = vendor_hals(manifest_text)
    found = {}
    matrix_count = 0
    for key, entry in inventory.get("files", {}).items():
        if not ("matrix" in key and entry.get("present")):
            continue
        summary = entry.get("vintf_summary", {})
        if summary.get("parse_error") or summary.get("root_tag") != "compatibility-matrix":
            continue
        matrix_count += 1
        for name in summary.get("hal_names", []):
            found.setdefault(name, []).append(key)
    required = set(found)
    return {
        "status": "preliminary" if matrix_count else "insufficient_framework_matrix_evidence",
        "framework_matrices_parsed": matrix_count,
        "vendor_hal_names": len(vendor),
        "framework_hal_names": len(required),
        "name_matches": sorted(required & vendor),
        "names_not_declared_in_vendor_manifest": [
            {"hal": name, "framework_sources": sorted(found[name])}
            for name in sorted(required - vendor)
        ],
        "warning": "Name-only comparison; optional HALs and version/instance requirements are not checked. Do not use as flashing approval.",
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("donor_inventory", type=Path)
    p.add_argument("vendor_manifest_xml", type=Path)
    p.add_argument("--output", type=Path, default=Path("oneui8-tbj716f-vintf-gaps.json"))
    args = p.parse_args()
    result = compare(json.loads(args.donor_inventory.read_text(encoding="utf-8")),
                     args.vendor_manifest_xml.read_text(encoding="utf-8"))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "preliminary":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
