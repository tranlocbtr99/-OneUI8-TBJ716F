#!/usr/bin/env python3
"""Assess whether a One UI system image can fit a Cuttlefish super partition.

Read-only gate; never edits super.img or AVB metadata.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

def assess(text,system_size):
    # lpdump format varies across Android releases; refuse uncertain parsing.
    entries=[]
    for line in text.splitlines():
        m=re.search(r"^\s*Name:\s*(\S+)",line)
        if m: entries.append({"name":m.group(1),"size":None})
        m=re.search(r"^\s*Size:\s*(\d+)\s*$",line)
        if m and entries and entries[-1]["size"] is None:
            entries[-1]["size"]=int(m.group(1))
    systems=[e for e in entries if e["name"] in ("system","system_a","system_b")]
    return {"candidate_bytes":system_size,"system_entries":systems,
            "capacity_verified":False,
            "replacement_safe":False,
            "reason":"Per-partition sizes do not establish free super group capacity, snapshot/COW constraints, or AVB correctness.",
            "next_required":"Use lpdump group maxima and partition extent allocation, then rebuild a disposable super image with matching AVB policy."}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--super",type=Path,required=True)
    p.add_argument("--system",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if not a.super.is_file() or not a.system.is_file():p.error("Missing images")
    if a.super.stat().st_size==0 or a.system.stat().st_size==0:p.error("Empty image")
    proc=subprocess.run(["lpdump",str(a.super)],capture_output=True,text=True)
    if proc.returncode:p.error("lpdump failed: "+proc.stderr[-500:])
    result=assess(proc.stdout,a.system.stat().st_size)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
