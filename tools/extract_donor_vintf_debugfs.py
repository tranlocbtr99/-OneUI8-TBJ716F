#!/usr/bin/env python3
"""Read VINTF XML from a verified ext4 donor using read-only debugfs."""
import argparse
import json
import re
import subprocess
from pathlib import Path

PARTITIONS = ("system", "system_ext", "product", "vendor", "odm")
def debugfs(image, command):
    return subprocess.run(["debugfs", "-R", command, str(image)], capture_output=True, text=True)
def walk(image, directory, depth=0):
    if depth > 4:
        return []
    result = debugfs(image, f"ls -p {directory}")
    if result.returncode:
        return []
    found = []
    for line in result.stdout.splitlines():
        # debugfs -p entries: /inode/type/mode/uid/gid/name/size/
        parts = line.split("/")
        if len(parts) < 7:
            continue
        kind, name = parts[2], parts[5]
        if name in (".", "..") or not name:
            continue
        full = directory.rstrip("/") + "/" + name
        if kind == "040000":
            found.extend(walk(image, full, depth+1))
        elif kind == "100000" and name.endswith(".xml"):
            found.append(full)
    return found

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    extracted = []
    for partition in PARTITIONS:
        for prefix in (f"/{partition}/etc/vintf", f"/etc/vintf" if partition == "system" else "/__missing__"):
            for source in walk(a.image, prefix):
                target = a.output / partition / source.removeprefix(f"/{partition}/")
                target.parent.mkdir(parents=True, exist_ok=True)
                result = debugfs(a.image, f"dump {source} {target}")
                if result.returncode or not target.is_file() or not target.stat().st_size:
                    target.unlink(missing_ok=True)
                    continue
                extracted.append({"source": source, "output": str(target), "bytes": target.stat().st_size})
    report = {"donor": "One UI 8 pinned Tab S9 GSI", "files": extracted, "count": len(extracted),
              "complete_vintf": False, "flashable": False}
    (a.output/"report.json").write_text(json.dumps(report, indent=2)+"\n")
    if not extracted:
        raise SystemExit("No VINTF XML extracted: inspect ext4 root layout before proceeding")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
