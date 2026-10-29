#!/usr/bin/env python3
"""Produce an evidence-limited HAL review queue from a static inventory."""
import argparse
import json
from pathlib import Path

PRIORITY = {
    "display": "P0", "audio": "P1", "camera": "P1",
    "connectivity": "P1", "sensors": "P1",
    "security": "P1", "media": "P1", "power": "P1", "other": "P2",
}
KEYWORDS = {
    "display": ("graphics", "composer", "display", "mapper", "allocator"),
    "audio": ("audio",),
    "camera": ("camera",),
    "connectivity": ("wifi", "bluetooth", "gnss", "radio"),
    "sensors": ("sensor",),
    "security": ("keymaster", "keymint", "gatekeeper", "soter", "drm"),
    "media": ("codec", "media", "vpp"),
    "power": ("power", "thermal", "health"),
}

def review(data):
    queue = []
    for group, entries in data.get("groups", {}).items():
        for hal in entries:
            name = hal.get("name", "")
            lower = name.lower()
            suggested = next((k for k, words in KEYWORDS.items() if any(w in lower for w in words)), None)
            queue.append({
                "name": name, "current_group": group,
                "suggested_group": suggested if group == "other" else None,
                "priority": PRIORITY.get(group, "P2"),
                "review": "Verify against actual ZUI 15 vendor VINTF, Android 16 framework matrices, and runtime logs",
                "status": "unverified",
            })
    queue.sort(key=lambda e: (e["priority"], e["current_group"], e["name"]))
    return {
        "scope": "review priorities only; no verified compatibility or boot claim",
        "total": len(queue),
        "unclassified": sum(e["current_group"] == "other" for e in queue),
        "queue": queue,
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, default=Path("reference-hal-review.json"))
    args = ap.parse_args()
    result = review(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("HAL declarations for review:", result["total"])
    print("Unclassified HAL declarations:", result["unclassified"])
    print("Priority is an engineering review order, not a measured failure risk")

if __name__ == "__main__":
    main()
