#!/usr/bin/env python3
"""Prepare an isolated Cuttlefish image directory for One UI 8 experiments.

Requires a complete, same-build ARM64 Cuttlefish image directory. Does not
modify original images, disable AVB, or claim boot compatibility.
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

REQUIRED=("boot.img","vendor_boot.img","vendor.img","vbmeta.img","super.img")
def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cuttlefish-images",type=Path,required=True)
    p.add_argument("--oneui-system",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    src=a.cuttlefish_images.resolve()
    system=a.oneui_system.resolve()
    out=a.output.resolve()
    if not src.is_dir():p.error("Missing Cuttlefish images directory")
    if not system.is_file():p.error("Missing One UI system image")
    if out.exists():p.error("Output must not exist")
    if out==src or src in out.parents or out in src.parents:p.error("Output must be separate from source")
    if system.stat().st_size!=6845104128:p.error("Unexpected One UI image size")
    expected="cf3a6fdb29e5f42c36ec8dc2687380b89c38e8dfd5e9b570741f0b62b60b3c77"
    if sha256(system)!=expected:p.error("One UI system checksum mismatch")
    missing=[x for x in REQUIRED if not (src/x).is_file()]
    if missing:p.error("Incomplete Cuttlefish image set: "+", ".join(missing))
    out.mkdir(parents=True)
    try:
        # Copy all regular image metadata and images. Refuse symlinks to prevent
        # unintentionally modifying files outside the isolated directory.
        for f in src.iterdir():
            if f.is_symlink():raise ValueError("Symlink in Cuttlefish input: "+f.name)
            if f.is_file():shutil.copy2(f,out/f.name)
        # Stage separately; Cuttlefish dynamic super and AVB must be handled
        # explicitly, so never silently replace system or super partitions.
        staged=out/"oneui8-candidate-system.img"
        shutil.copyfile(system,staged)
        report={"status":"staged_not_bootable","oneui_sha256":sha256(staged),
                "cuttlefish_images":sorted(x.name for x in out.iterdir() if x.is_file()),
                "system_partition_replaced":False,"avb_modified":False,
                "super_modified":False,"flashable":False,
                "blockers":["Cuttlefish super partition layout and capacity",
                            "AVB chain and verified boot strategy",
                            "Framework/vendor VINTF compatibility",
                            "Cuttlefish guest boot validation"]}
        (out/"ONEUI8-STAGING.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps(report,indent=2))
    except BaseException:
        shutil.rmtree(out)
        raise
if __name__=="__main__":main()
