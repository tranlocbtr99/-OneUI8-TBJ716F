#!/usr/bin/env python3
"""Read-only One UI 8 ext4 system image inventory using debugfs (no root/mount).

Run only on a locally acquired, verified donor IMG. No proprietary image is shipped.
"""
import argparse
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

FILES = {
    "system_build_prop": "/system/build.prop",
    "product_build_prop": "/system/product/etc/build.prop",
    "framework_manifest": "/system/etc/vintf/manifest.xml",
    "framework_matrix": "/system/etc/vintf/compatibility_matrix.xml",
    "system_ext_manifest": "/system/system_ext/etc/vintf/manifest.xml",
    "audio_stage_policy": "/system/etc/stage_policy.conf",
    "samsung_audio_effects": "/system/etc/audio_effects_sec.xml",
    "init_rc": "/system/etc/init/hw/init.rc",
}
for level in range(1, 9):
    FILES[f"framework_matrix_level_{level}"] = f"/system/etc/vintf/compatibility_matrix.{level}.xml"
FILES["product_matrix"] = "/system/product/etc/vintf/compatibility_matrix.xml"
FILES["system_ext_matrix"] = "/system/system_ext/etc/vintf/compatibility_matrix.xml"
MAX_CAPTURE = 1024 * 1024

def summarize_vintf(xml):
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        return {"parse_error": str(exc)}
    hals = [name.text for hal in root.findall("hal") for name in hal.findall("name") if name.text]
    return {"root_tag": root.tag, "type": root.attrib.get("type"),
            "level": root.attrib.get("level"),
            "hal_count": len(hals), "hal_names": sorted(set(hals))}


def read_file(image, filename):
    # debugfs -R cat only reads the filesystem; no loop mount or image modification.
    cmd = ["debugfs", "-R", "cat " + filename, str(image)]
    result = subprocess.run(cmd, capture_output=True, timeout=45)
    data = result.stdout
    if result.returncode or len(data) > MAX_CAPTURE:
        return {"present": False, "reason": "not readable or too large"}
    if not data:
        return {"present": False, "reason": "empty or missing"}
    return {"present": True, "bytes": len(data), "data": data.decode("utf-8", "replace")}

def inventory(image):
    if not shutil.which("debugfs"):
        raise RuntimeError("Install e2fsprogs (debugfs) to inspect ext4 donor image")
    with image.open("rb") as stream:
        stream.seek(1080)
        if stream.read(2) != b"\x53\xef":
            raise ValueError("Image is not a raw ext4 filesystem; decompress or unsparse first")
    result = {"image_size_bytes": image.stat().st_size, "format": "raw_ext4", "files": {}}
    for name, path in FILES.items():
        info = read_file(image, path)
        entry = {"path": path, "present": info["present"]}
        if info["present"]:
            data = info["data"]
            if name.endswith("build_prop"):
                props = {}
                for line in data.splitlines():
                    if "=" in line and not line.lstrip().startswith("#"):
                        k, v = line.split("=", 1)
                        if k.startswith(("ro.build.", "ro.product.", "ro.vendor.", "persist.sys.usb.")):
                            props[k] = v
                entry["selected_properties"] = props
            elif name == "audio_stage_policy":
                entry["dolby_stage_tokens"] = len(re.findall(r"STAGE_EFFECT_DOLBY\w*", data))
            else:
                entry["bytes"] = info["bytes"]
                if "/vintf/" in path and path.endswith(".xml"):
                    entry["vintf_summary"] = summarize_vintf(data)
        else:
            entry["reason"] = info["reason"]
        result["files"][name] = entry
    result["warning"] = "Static metadata only; does not prove VINTF compatibility, runtime or boot"
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--output", type=Path, default=Path("oneui8-donor-inventory.json"))
    args = p.parse_args()
    result = inventory(args.image)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
