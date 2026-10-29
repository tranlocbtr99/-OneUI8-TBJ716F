#!/usr/bin/env python3
"""Read-only Qualcomm rawprogram XML inspection; never executes flash instructions."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

def inspect(archive):
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        reports = []
        for name in sorted(n for n in names if Path(n).name.startswith("rawprogram") and n.endswith(".xml") and "WIPE" not in n and "BLANK" not in n):
            root = ET.fromstring(z.read(name))
            items = []
            for node in root.iter("program"):
                a = node.attrib
                filename = a.get("filename", "")
                if not filename:
                    continue
                items.append({
                    "filename": filename,
                    "partition_label": a.get("label", ""),
                    "start_sector": a.get("start_sector", ""),
                    "num_partition_sectors": a.get("num_partition_sectors", ""),
                    "sector_size_in_bytes": a.get("SECTOR_SIZE_IN_BYTES", ""),
                    "file_in_zip": filename in names,
                })
            reports.append({"xml": name, "programs": items,
                "super_entries": [i for i in items if "super" in i["filename"].lower() or "super" in i["partition_label"].lower()]})
        return {"rawprogram_files": reports,
                "warning": "Metadata-only. No writes, no flashing. Segment offsets and completeness must be validated before assembly."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, default=Path("rawprogram-super-map.json"))
    a = p.parse_args()
    result = inspect(a.archive)
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps([{"xml": r["xml"], "super_entries": r["super_entries"]} for r in result["rawprogram_files"]], indent=2))

if __name__ == "__main__":
    main()
