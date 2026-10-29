#!/usr/bin/env python3
"""Read-only ZIP firmware contents inventory; never extracts partition images."""
import argparse
import json
import pathlib
import re
import zipfile

IMAGE = re.compile(r"(?:^|/)(?:super|vendor|vendor_a|vendor_b|vendor_boot|boot|init_boot|dtbo|vbmeta|system|product|odm|system_ext)(?:\.img|\.new\.dat(?:\.br)?|\.transfer\.list)$", re.I)
PAYLOAD = re.compile(r"(?:^|/)payload\.bin$", re.I)
PROP = re.compile(r"(?:^|/)vendor/(?:etc/)?build\.prop$", re.I)
VINTF = re.compile(r"(?:^|/)vendor/etc/vintf/(?:manifest[^/]*\.xml|manifest/[^/]+\.xml)$", re.I)

def inventory(archive):
    entries = []
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename
            kind = ("payload" if PAYLOAD.search(name) else
                    "partition_image" if IMAGE.search(name) else
                    "vendor_properties" if PROP.search(name) else
                    "vintf_manifest" if VINTF.search(name) else "other")
            if kind != "other":
                entries.append({"path": name, "type": kind, "uncompressed_bytes": info.file_size,
                                "compressed_bytes": info.compress_size})
    types = {e["type"] for e in entries}
    blockers = []
    if "payload" in types:
        blockers.append("payload.bin requires a separate OTA payload parser; not supported here")
    if "partition_image" in types:
        blockers.append("Partition images may require sparse/super unpacking and ext4/EROFS readers; not supported here")
    if not ({"vendor_properties", "vintf_manifest"} & types):
        blockers.append("No directly accessible vendor properties or VINTF XML in the ZIP")
    return {"scope": "ZIP central directory only; no image parsing, integrity authentication or compatibility verdict",
            "entries": sorted(entries, key=lambda x: x["path"]), "blockers": blockers}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("firmware-zip-index.json"))
    args = parser.parse_args()
    result = inventory(args.archive)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
