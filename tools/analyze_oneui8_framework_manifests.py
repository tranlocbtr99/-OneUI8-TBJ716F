#!/usr/bin/env python3
"""Inventory Samsung framework VINTF HALs without claiming compatibility."""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def summarize(root):
    if root.tag!="manifest":
        raise ValueError("Expected VINTF manifest")
    return [{"name":h.findtext("name"),"format":h.get("format","hidl"),
             "versions":[x.text for x in h.findall("version") if x.text],
             "fqnames":[x.text for x in h.findall("fqname") if x.text],
             "interfaces":[{"name":i.findtext("name"),
                            "instances":[x.text for x in i.findall("instance") if x.text]}
                           for i in h.findall("interface")]}
            for h in root.findall("hal") if h.findtext("name")]

def analyze(tree):
    out={}
    for label,rel in (("system","system/etc/vintf/manifest.xml"),
                      ("system_ext","system_ext/etc/vintf/manifest.xml"),
                      ("lenovo_vendor","vendor/etc/vintf/manifest.xml")):
        p=tree/rel
        out[label]={"present":p.is_file(),"hals":summarize(ET.parse(p).getroot()) if p.is_file() else []}
    framework={h["name"] for key in ("system","system_ext") for h in out[key]["hals"]}
    vendor={h["name"] for h in out["lenovo_vendor"]["hals"]}
    return {"sources":out,"framework_names":sorted(framework),
            "vendor_names":sorted(vendor),
            "names_shared":sorted(framework & vendor),
            "framework_names_not_in_base_vendor":sorted(framework-vendor),
            "vintf_compatible":None,"boot_verified":False,
            "warning":"Manifest declarations are not necessarily device HAL requirements. This is NOT a checkvintf result."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("tree",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.tree)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("Framework HAL names:",len(result["framework_names"]))
    print("Lenovo vendor HAL names:",len(result["vendor_names"]))
    print("Shared names:",len(result["names_shared"]))
if __name__=="__main__":
    main()
