#!/usr/bin/env python3
"""Extract additional VINTF XML from verified donor ext4 without mounting.

Exports only known VINTF files. No proprietary images are redistributed.
"""
import argparse
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

PATHS={
 "system_manifest":"/system/etc/vintf/manifest.xml",
 "system_matrix":"/system/etc/vintf/compatibility_matrix.xml",
 "product_manifest":"/system/product/etc/vintf/manifest.xml",
 "product_matrix":"/system/product/etc/vintf/compatibility_matrix.xml",
 "system_ext_manifest":"/system/system_ext/etc/vintf/manifest.xml",
 "system_ext_matrix":"/system/system_ext/etc/vintf/compatibility_matrix.xml",
}
def extract(image,out):
    out.mkdir(parents=True,exist_ok=True)
    result={}
    for key,source in PATHS.items():
        p=subprocess.run(["debugfs","-R","cat "+source,str(image)],capture_output=True,timeout=45)
        if p.returncode or not p.stdout:
            result[key]={"present":False}
            continue
        if len(p.stdout)>1024*1024:
            raise ValueError("VINTF XML exceeds 1 MiB: "+source)
        root=ET.fromstring(p.stdout)
        if root.tag not in ("manifest","compatibility-matrix"):
            raise ValueError("Unexpected VINTF XML root: "+source)
        target=out/(key+".xml")
        target.write_bytes(p.stdout)
        result[key]={"present":True,"path":source,"bytes":len(p.stdout)}
    (out/"inventory.json").write_text(json.dumps({"files":result,"complete":False,
      "warning":"Only known paths; missing fragments, device runtime properties and kernel evidence."},indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("image",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(extract(a.image,a.output),indent=2))
if __name__=="__main__":
    main()
