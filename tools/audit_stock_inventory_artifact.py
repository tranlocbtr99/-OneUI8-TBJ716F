#!/usr/bin/env python3
"""Read-only audit of metadata-only stock inventory artifacts."""
import argparse
import collections
import json
import pathlib
import zipfile
import xml.etree.ElementTree as ET

def analyze(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if "archive-contents.txt" not in names:
            raise ValueError("Missing archive-contents.txt")
        inventory = {pathlib.PurePosixPath(x.strip()).name for x in z.read("archive-contents.txt").decode().splitlines() if x.strip()}
        refs = []
        xmls = sorted(n for n in names if pathlib.PurePosixPath(n).name.startswith("rawprogram") and n.endswith(".xml"))
        for name in xmls:
            root = ET.fromstring(z.read(name))
            for node in root.iter():
                if node.tag.lower() != "program":
                    continue
                filename = pathlib.PurePosixPath(node.attrib.get("filename", "")).name
                if not filename:
                    continue
                refs.append({"xml": name, "label": node.attrib.get("label", ""), "filename": filename, "listed": filename in inventory,
                             "start_sector": node.attrib.get("start_sector"), "num_partition_sectors": node.attrib.get("num_partition_sectors"),
                             "sector_size": node.attrib.get("SECTOR_SIZE_IN_BYTES")})
        missing = collections.defaultdict(list)
        for r in refs:
            if not r["listed"]:
                missing[r["filename"]].append(r["xml"])
        segmented = {prefix: sorted((n for n in inventory if n.startswith(prefix + "_") and n.endswith(".img")),
                                    key=lambda n: int(n[len(prefix)+1:-4]) if n[len(prefix)+1:-4].isdigit() else 999999)
                     for prefix in ("super", "metadata", "userdata")}
        return {"xml_count": len(xmls), "total_references": len(refs), "unresolved_references": dict(missing),
                "segmented_image_names": segmented, "super_entries": [r for r in refs if r["label"] == "super"],
                "assessment": "metadata_only_no_image_bytes; no sparse header or LP metadata verified"}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("artifact_zip")
    p.add_argument("--output")
    args = p.parse_args()
    result = json.dumps(analyze(args.artifact_zip), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)
