#!/usr/bin/env python3
"""Report firmware identity from extracted Android properties; never certify compatibility."""
import argparse
import json
from pathlib import Path

MODEL_KEYS = ("ro.product.vendor.model", "ro.product.model", "ro.product.device",
              "ro.product.vendor.device", "ro.build.product")
SDK_KEYS = ("ro.vendor.build.version.sdk", "ro.build.version.sdk",
            "ro.vendor.api_level", "ro.product.first_api_level")

def parse_props(path):
    props = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = value.strip()
    return props

def assess(paths):
    props = {}
    for path in paths:
        props.update(parse_props(path))
    models = {key: props[key] for key in MODEL_KEYS if props.get(key)}
    versions = {key: props[key] for key in SDK_KEYS if props.get(key)}
    models_joined = " ".join(models.values()).lower().replace("_", "-")
    # Device aliases vary; an unrecognized identifier is not proof of a mismatch.
    target_mentioned = "tb-j716f" in models_joined or "j716f" in models_joined
    other_tb = any("tb-" in v.lower() and "j716f" not in v.lower() for v in models.values())
    verdict = ("target_identifier_present" if target_mentioned else
               "possible_other_device" if other_tb else "identity_unverified")
    return {"target": "Lenovo TB-J716F", "identity_status": verdict,
            "model_properties": models, "api_properties": versions,
            "caution": "Properties can be spoofed or incomplete. This is NOT a firmware authenticity, Android 16, or One UI 8 compatibility check."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("properties", type=Path, nargs="+")
    p.add_argument("--output", type=Path, default=Path("firmware-identity.json"))
    args = p.parse_args()
    result = assess(args.properties)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
