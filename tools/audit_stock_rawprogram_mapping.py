#!/usr/bin/env python3
"""Read-only audit of Qualcomm rawprogram XML and available firmware image names."""
import argparse
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

def audit(root):
    root = pathlib.Path(root)
    xmls = sorted(root.rglob("rawprogram*.xml"))
    if not xmls:
        return {"status": "insufficient_evidence", "reason": "No rawprogram XML found", "entries": []}
    entries = []
    for xml in xmls:
        try:
            tree = ET.parse(xml)
        except ET.ParseError as exc:
            entries.append({"xml": str(xml.relative_to(root)), "error": str(exc)})
            continue
        for node in tree.iter():
            if node.tag.lower() != "program":
                continue
            a = node.attrib
            label = a.get("label", "")
            filename = a.get("filename", "")
            if not (label.startswith(("super", "boot", "dtbo", "vbmeta", "vendor", "odm")) or "super" in filename.lower()):
                continue
            matches = sorted(str(p.relative_to(root)) for p in root.rglob(pathlib.Path(filename).name)) if filename else []
            entries.append({
                "xml": str(xml.relative_to(root)),
                "label": label,
                "filename": filename,
                "physical_partition_number": a.get("physical_partition_number"),
                "start_sector": a.get("start_sector"),
                "num_partition_sectors": a.get("num_partition_sectors"),
                "sector_size_in_bytes": a.get("SECTOR_SIZE_IN_BYTES"),
                "matching_local_files": matches[:20],
                "image_present": bool(matches),
            })
    referenced = {pathlib.Path(e["filename"]).name for e in entries if e.get("filename")}
    super_parts = sorted(str(p.relative_to(root)) for p in root.rglob("super*.img") if p.name not in referenced)
    missing = [e for e in entries if e.get("filename") and not e["image_present"]]
    return {
        "status": "needs_review" if missing or super_parts else "inventory_only",
        "xml_count": len(xmls),
        "entries": entries,
        "missing_referenced_images": len(missing),
        "unreferenced_super_images": super_parts,
        "warning": "Inventory only: no LP metadata, VINTF compatibility, or flash safety proven.",
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("firmware_dir", help="Extracted stock firmware directory; read-only")
    p.add_argument("--output", help="Optional JSON output file")
    args = p.parse_args()
    result = audit(args.firmware_dir)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        pathlib.Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0 if result["status"] != "insufficient_evidence" else 2

if __name__ == "__main__":
    sys.exit(main())
