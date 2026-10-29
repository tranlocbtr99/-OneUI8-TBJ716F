#!/usr/bin/env python3
"""Run an isolated ARM64 QEMU boot experiment with explicitly supplied boot assets.

Does NOT claim to emulate Lenovo TB-J716F hardware. Never touches real devices.
The One UI system image alone is insufficient to boot Android.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kernel",type=Path,required=True,help="ARM64 Linux Image built for QEMU virt")
    p.add_argument("--initrd",type=Path,required=True,help="Android-compatible ramdisk for the supplied kernel")
    p.add_argument("--system",type=Path,required=True,help="Read-only raw ext4 system image")
    p.add_argument("--vendor",type=Path,required=True,help="QEMU-compatible raw vendor image (NOT Lenovo stock vendor)")
    p.add_argument("--seconds",type=int,default=180)
    p.add_argument("--log",type=Path,required=True)
    p.add_argument("--result",type=Path,required=True)
    a=p.parse_args()
    if not 15<=a.seconds<=900: p.error("seconds must be between 15 and 900")
    if not shutil.which("qemu-system-aarch64"):p.error("qemu-system-aarch64 not installed")
    for name in ("kernel","initrd","system","vendor"):
        f=getattr(a,name)
        if not f.is_file() or f.stat().st_size==0:p.error(f"Missing/nonempty {name}: {f}")
    cmd=["qemu-system-aarch64","-machine","virt","-cpu","cortex-a72","-smp","4",
         "-m","4096","-nographic","-no-reboot","-monitor","none",
         "-kernel",str(a.kernel),"-initrd",str(a.initrd),
         "-append","console=ttyAMA0 androidboot.hardware=virt printk.devkmsg=on",
         "-drive",f"file={a.system},if=none,format=raw,readonly=on,id=system",
         "-device","virtio-blk-pci,drive=system",
         "-drive",f"file={a.vendor},if=none,format=raw,readonly=on,id=vendor",
         "-device","virtio-blk-pci,drive=vendor"]
    a.log.parent.mkdir(parents=True,exist_ok=True)
    a.result.parent.mkdir(parents=True,exist_ok=True)
    timed_out=False
    with a.log.open("wb") as out:
        try:
            proc=subprocess.run(cmd,stdout=out,stderr=subprocess.STDOUT,timeout=a.seconds,check=False)
            code=proc.returncode
        except subprocess.TimeoutExpired:
            timed_out=True
            code=None
    log=a.log.read_bytes()[-1048576:].decode("utf-8","replace")
    # A boot requires a guest-side positive signal; timeout/console activity is NOT success.
    # Serial text alone is untrusted evidence; it may be printed by init scripts.
    # Never treat a generic marker as a verified Android userspace boot.
    markers=["sys.boot_completed=1","BOOT_COMPLETED=1"]
    serial_boot_marker_observed=any(x in log for x in markers)
    guest_reported_boot=False
    result={"qemu_exit_code":code,"timed_out":timed_out,
            "guest_reported_boot":guest_reported_boot,
            "serial_boot_marker_observed":serial_boot_marker_observed,
            "boot_verification_method":"not_available_without_guest_adb_or_authenticated_agent",
            "device_compatibility_verified":False,"flashable":False,
            "note":"QEMU virt differs from TB-J716F; generic serial boot markers are not sufficient hardware validation.",
            "log":str(a.log)}
    a.result.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
