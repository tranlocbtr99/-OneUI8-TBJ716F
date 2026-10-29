#!/usr/bin/env python3
"""Summarize a device-tree VINTF inventory without claiming runtime compatibility."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

GROUPS = {
    "display": ("graphics", "composer", "mapper", "allocator", "display", "light"),
    "audio": ("audio", "sound", "vibrator"),
    "camera": ("camera",),
    "connectivity": ("wifi", "bluetooth", "radio", "gnss", "nfc", "ethernet"),
    "sensors": ("sensor",),
    "security": ("keymaster", "keymint", "gatekeeper", "soter", "biometric", "fingerprint", "face", "drm", "secure_element"),
    "media": ("media", "codec", "vpp", "cas"),
    "power": ("power", "thermal", "health", "battery"),
}

def summarize(data):
    groups = defaultdict(list)
    for manifest in data.get("manifests", []):
        for hal in manifest.get("hals", []):
            name = hal.get("name", "")
            lower = name.lower()
            group = next((group for group, needles in GROUPS.items() if any(word in lower for word in needles)), "other")
            entry = {
                "name": name,
                "versions": hal.get("versions", []),
                "fqnames": hal.get("fqnames", []),
                "interfaces": hal.get("interfaces", []),
                "manifest": manifest.get("file"),
            }
            if entry not in groups[group]:
                groups[group].append(entry)
    for entries in groups.values():
        entries.sort(key=lambda e: (e["name"], e["manifest"] or ""))
    return {
        "scope": "static community device-tree HAL inventory; not Android 16 or One UI compatibility proof",
        "manifest_count": len(data.get("manifests", [])),
        "hal_count": sum(len(entries) for entries in groups.values()),
        "groups": dict(sorted(groups.items())),
        "limitations": [
            "Declarations may not reflect the actual ZUI 15 vendor partition",
            "No framework compatibility matrix or runtime service validation",
            "No SELinux, kernel ABI, partition sizing, or hardware testing",
        ],
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, default=Path("reference-hal-groups.json"))
    args = ap.parse_args()
    result = summarize(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Manifest files:", result["manifest_count"])
    print("Unique HAL declarations:", result["hal_count"])
    for group, entries in result["groups"].items():
        print(f"{group}: {len(entries)}")

if __name__ == "__main__":
    main()
