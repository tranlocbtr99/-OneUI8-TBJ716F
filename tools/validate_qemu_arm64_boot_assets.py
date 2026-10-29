#!/usr/bin/env python3
"""Fail closed on malformed QEMU ARM64 boot assets. Does not establish Android compatibility."""
import argparse
import json
import struct
from pathlib import Path

p = argparse.ArgumentParser()
for name in ("kernel", "initrd", "system", "vendor"):
    p.add_argument("--" + name, type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
result = {"checks": {}, "android_boot_verified": False, "oneui_boot_verified": False, "flashable": False}
errors = []
for name in ("kernel", "initrd", "system", "vendor"):
    path = getattr(a, name)
    if not path.is_file() or path.stat().st_size < 4096:
        errors.append(f"{name}: missing or too small")
        continue
    result["checks"][name] = {"bytes": path.stat().st_size}
with a.kernel.open("rb") as f:
    header = f.read(64)
if header[56:60] != b"ARM\x64":
    errors.append("kernel: no ARM64 Image magic at 0x38; QEMU may reject this format")
with a.initrd.open("rb") as f:
    prefix = f.read(8)
if not (prefix.startswith(b"\x1f\x8b") or prefix.startswith(b"070701") or prefix.startswith(b"070702") or prefix.startswith(b"\xfd7zXZ")):
    errors.append("initrd: not a recognized gzip/cpio/xz initramfs header")
for name in ("system", "vendor"):
    with getattr(a, name).open("rb") as f:
        f.seek(1024 + 56)
        magic = f.read(2)
    if magic != b"\x53\xef":
        errors.append(f"{name}: no ext4 superblock magic; sparse or dynamic images need conversion")
result["errors"] = errors
result["preflight_passed"] = not errors
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if errors:
    raise SystemExit(1)
