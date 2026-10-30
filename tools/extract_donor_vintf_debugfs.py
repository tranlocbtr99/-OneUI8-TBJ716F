#!/usr/bin/env python3
"""Read VINTF XML from a verified ext4 donor using read-only debugfs."""
import argparse
import json
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
        if kind in ("2", "040000"):
            found.extend(walk(image, full, depth+1))
        elif kind in ("1", "100000") and name.endswith(".xml"):
            found.append(full)
    return found

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("output", type=Path)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    extracted = []
    diagnostics = {}
    for candidate in ("/", "/system", "/system/etc", "/system/etc/vintf", "/etc/vintf"):
        result = debugfs(a.image, f"ls -p {candidate}")
        diagnostics[candidate] = {"returncode": result.returncode, "stdout": result.stdout[:5000], "stderr": result.stderr[:1000]}
    (a.output/"layout-diagnostics.json").write_text(json.dumps(diagnostics, indent=2)+"\n")
    for partition in PARTITIONS:
        for prefix in (f"/{partition}/etc/vintf", f"/etc/vintf" if partition == "system" else "/__missing__"):
            for source in walk(a.image, prefix):
                rel = source.removeprefix(f"/{partition}/") if source.startswith(f"/{partition}/") else source.lstrip("/")
                target = a.output / partition / rel
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
        raise SystemExit("No VINTF XML extracted; see layout-diagnostics.json for actual ext4 paths")
    print(json.dumps(report, indent=2))
if __name__ == "__main__":
    main()
