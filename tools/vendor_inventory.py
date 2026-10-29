#!/usr/bin/env python3
"""Read-only, offline Android vendor compatibility inventory. No flashing."""
import argparse
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

KEYS = (
    "ro.product.vendor.device", "ro.product.vendor.model",
    "ro.vendor.build.version.sdk", "ro.vndk.version",
    "ro.vendor.api_level", "ro.board.api_level",
    "ro.product.first_api_level", "ro.vendor.build.fingerprint",
    "ro.boot.dynamic_partitions", "ro.boot.slot_suffix",
    "ro.build.version.sdk", "ro.build.version.release",
)
HAL_TAGS = {"hal", "name", "version", "interface", "instance", "fqname"}

def props(path):
    found = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        found[key.strip()] = value.strip()
    return found

def hal_inventory(path):
    root = ET.parse(path).getroot()
    entries = []
    for hal in root.findall(".//hal"):
        name = hal.findtext("name", default="").strip()
        versions = sorted({(e.text or "").strip() for e in hal.findall("version") if e.text})
        interfaces = []
        for interface in hal.findall("interface"):
            iname = interface.findtext("name", default="").strip()
            instances = [(e.text or "").strip() for e in interface.findall("instance") if e.text]
            interfaces.append({"name": iname, "instances": sorted(instances)})
        fqnames = sorted({(e.text or "").strip() for e in hal.findall("fqname") if e.text})
        entries.append({"name": name, "versions": versions, "interfaces": interfaces, "fqnames": fqnames})
    return {"file": path.name, "root": root.tag, "type": root.attrib.get("type"), "target_level": root.attrib.get("target-level"), "hals": entries}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor-build-prop", type=pathlib.Path)
    ap.add_argument("--system-build-prop", type=pathlib.Path)
    ap.add_argument("--manifest", type=pathlib.Path, action="append", default=[])
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("vendor-compatibility.json"))
    args = ap.parse_args()
    if not (args.vendor_build_prop or args.system_build_prop or args.manifest):
        ap.error("Supply at least one local properties or VINTF manifest file")
    result = {"scope": "offline inventory; not a VINTF compatibility verdict", "properties": {}, "manifests": [], "warnings": []}
    for label, path in (("vendor", args.vendor_build_prop), ("system", args.system_build_prop)):
        if path:
            if not path.is_file():
                ap.error(f"Missing {label} property file: {path}")
            p = props(path)
            result["properties"][label] = {k: p[k] for k in KEYS if k in p}
            if label == "vendor" and "ro.vendor.build.version.sdk" not in p:
                result["warnings"].append("Vendor SDK not present in supplied property file")
    for path in args.manifest:
        if not path.is_file():
            ap.error(f"Missing manifest: {path}")
        try:
            result["manifests"].append(hal_inventory(path))
        except ET.ParseError as e:
            ap.error(f"Invalid XML {path}: {e}")
    if not args.manifest:
        result["warnings"].append("No VINTF manifest supplied; HAL inventory unavailable")
    result["warnings"].append("VINTF compatibility requires framework matrix and actual device/vendor context")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
