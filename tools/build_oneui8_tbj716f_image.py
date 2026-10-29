#!/usr/bin/env python3
"""Patch a COPY of the pinned One UI ext4 donor with a narrowly scoped overlay.

Output is an engineering image, NOT approved for flashing.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

PREFIX="system/etc/oneui8-tbj716f/"
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
    return h.hexdigest()
def md5_file(path):
    h=hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(8*1024*1024),b""):h.update(block)
    return h.hexdigest()
def run(*args):
    p=subprocess.run(args,capture_output=True,text=True)
    if p.returncode:raise RuntimeError("command failed: "+" ".join(map(str,args))+"\n"+p.stderr[-1500:])
    return p
def build(donor,overlay,output,report):
    if output.exists():raise ValueError("Output already exists")
    manifest=json.loads((overlay/"overlay-manifest.json").read_text())
    files=manifest["files"]
    if not files or manifest.get("flashable") is not False:raise ValueError("Invalid staging manifest")
    if set(files)!={PREFIX+"port-metadata.json",PREFIX+"README.txt"}:raise ValueError("Unexpected overlay file list")
    if not donor.is_file():raise ValueError("Donor image missing")
    if donor.stat().st_size!=6845104128:raise ValueError("Unexpected donor image size")
    if md5_file(donor)!="6946aa3fdcafa3475c1809b640f0df5c":raise ValueError("Donor MD5 mismatch")
    for name,expected in files.items():
        p=overlay/name
        if not p.is_file() or p.is_symlink() or digest(p)!=expected:raise ValueError("Overlay integrity failure: "+name)
    metadata=json.loads((overlay/(PREFIX+"port-metadata.json")).read_text())
    if metadata.get("target_device")!="TB-J716F" or metadata.get("flashable") is not False:raise ValueError("Incorrect target")
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        shutil.copyfile(donor,output)
        pre=subprocess.run(["e2fsck","-fn",str(output)],capture_output=True,text=True)
        if pre.returncode not in (0,1):raise RuntimeError("Donor filesystem check failed: "+pre.stdout[-1200:])
        for folder in ("/system/etc/oneui8-tbj716f",):
            p=subprocess.run(["debugfs","-w","-R","mkdir "+folder,str(output)],capture_output=True,text=True)
            if "File exists" not in p.stderr and p.returncode:raise RuntimeError(p.stderr)
        for name in sorted(files):
            source=overlay/name
            dest="/"+name
            run("debugfs","-w","-R",f"write {source} {dest}",str(output))
            verify=subprocess.run(["debugfs","-R","cat "+dest,str(output)],capture_output=True)
            if verify.returncode or verify.stdout!=source.read_bytes():raise RuntimeError("Readback mismatch "+name)
        # e2fsck exit 0 (clean) or 1 (correctable issues repaired); never repair here
        check=subprocess.run(["e2fsck","-fn",str(output)],capture_output=True,text=True)
        if check.returncode not in (0,1):raise RuntimeError("Post-patch filesystem check failed: "+check.stdout[-1200:])
        result={"donor_md5":"6946aa3fdcafa3475c1809b640f0df5c",
                "output_sha256":digest(output),"output_bytes":output.stat().st_size,
                "patched_files":sorted(files),"flashable":False,"boot_verified":False,
                "vintf_compatible":None,"fsck_exit":check.returncode}
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
    except BaseException:
        output.unlink(missing_ok=True)
        raise
def main():
    p=argparse.ArgumentParser()
    p.add_argument("donor",type=Path)
    p.add_argument("overlay",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    build(a.donor,a.overlay,a.output,a.report)
if __name__=="__main__":main()
