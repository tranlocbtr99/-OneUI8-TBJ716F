#!/usr/bin/env python3
"""Read-only Android boot preflight: parse adb-collected device properties.

No flashing, unlocking, rebooting, or partition writes.
"""
import argparse
import json
from pathlib import Path

KEYS={
"ro.product.device","ro.product.model","ro.build.product",
"ro.boot.slot_suffix","ro.boot.dynamic_partitions",
"ro.boot.flash.locked","ro.boot.verifiedbootstate",
"ro.build.version.sdk","ro.vendor.build.version.sdk",
"ro.boot.bootdevice","ro.boot.hardware",
}
def parse_props(raw):
    props={}
    for line in raw.splitlines():
        line=line.strip()
        if line.startswith("[") and "]: [" in line and line.endswith("]"):
            key,value=line[1:-1].split("]: [",1)
            props[key]=value
    return props
def report(props):
    target=any("J716F" in props.get(k,"").upper().replace("-","") for k in ("ro.product.device","ro.product.model","ro.build.product"))
    slot=props.get("ro.boot.slot_suffix")
    dynamic=props.get("ro.boot.dynamic_partitions")
    unlocked=props.get("ro.boot.flash.locked")=="0"
    return {"device_identity_matches":target,"slot_suffix":slot,
      "dynamic_partitions_property":dynamic,
      "bootloader_unlocked_property":unlocked,
      "observed":{k:props.get(k) for k in sorted(KEYS)},
      "safe_to_flash":False,
      "reason":"Device identity alone does not establish GSI compatibility, partition capacity, rollback or recovery readiness.",
      "next_evidence":["fastboot getvar all (redact serial/IMEI)","adb shell ls -l /dev/block/by-name",
                       "adb shell getprop ro.boot.slot_suffix",
                       "adb shell getprop ro.boot.dynamic_partitions",
                       "stock backup and recovery procedure"]}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("getprop_txt",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=report(parse_props(a.getprop_txt.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
