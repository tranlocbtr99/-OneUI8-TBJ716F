#!/usr/bin/env python3
"""Read-only extraction of selected vendor evidence from a local ZIP archive.

Only extracts plain vendor/build.prop and VINTF XML entries. Does not parse
super.img, payload.bin, nested archives, or flash any partitions.
"""
import argparse
import hashlib
import json
import pathlib
import re
import zipfile

MAX_ENTRY = 2 * 1024 * 1024
MAX_TOTAL = 12 * 1024 * 1024
SAFE = re.compile(r"^[A-Za-z0-9_.+/@-]+$")
VENDOR_PROP = re.compile(r"(?:^|/)vendor/(?:etc/)?build\.prop$")
MANIFEST = re.compile(r"(?:^|/)vendor/etc/vintf/(?:manifest(?:_[\w-]+)?\.xml|manifest/[^/]+\.xml)$")

def extract(path, dest):
    dest.mkdir(parents=True, exist_ok=True)
    items, warnings, total = [], [], 0
    with zipfile.ZipFile(path) as archive:
        candidates = []
        seen = set()
        for info in archive.infolist():
            name = info.filename
            if info.is_dir() or not SAFE.fullmatch(name) or ".." in name.split("/"):
                continue
            kind = "vendor_build_prop" if VENDOR_PROP.search(name) else "vintf_manifest" if MANIFEST.search(name) else None
            if kind:
                if name in seen:
                    warnings.append(f"Skipped duplicate ZIP member: {name}")
                    continue
                seen.add(name)
                candidates.append((info, kind))
        for idx, (info, kind) in enumerate(candidates):
            if info.file_size > MAX_ENTRY or total + info.file_size > MAX_TOTAL:
                warnings.append(f"Skipped oversized entry: {info.filename}")
                continue
            # Read with a hard cap even if the ZIP metadata lies.
            with archive.open(info) as stream:
                data = stream.read(MAX_ENTRY + 1)
            if len(data) > MAX_ENTRY:
                warnings.append(f"Skipped oversized decompression: {info.filename}")
                continue
            total += len(data)
            suffix = ".prop" if kind == "vendor_build_prop" else ".xml"
            output = dest / f"evidence-{idx:03d}{suffix}"
            output.write_bytes(data)
            items.append({"archive_path": info.filename, "kind": kind, "output": str(output),
                          "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if not items:
        warnings.append("No directly accessible vendor/build.prop or VINTF manifest XML; archive may contain only partition images")
    return {"scope": "selected static ZIP evidence; NOT firmware verification or compatibility", "files": items, "warnings": warnings}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("archive", type=pathlib.Path)
    ap.add_argument("--output-dir", type=pathlib.Path, default=pathlib.Path("vendor-evidence"))
    args = ap.parse_args()
    if not args.archive.is_file():
        ap.error("ZIP archive not found")
    result = extract(args.archive, args.output_dir)
    report = args.output_dir / "evidence-index.json"
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
