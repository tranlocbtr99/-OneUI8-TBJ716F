#!/usr/bin/env python3
"""Classify donor FCM HAL declarations by optionality, without boot claims.

Reads raw compatibility matrix XML (not the lossy name-only inventory).
"""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def classify(matrix_xml, vendor_xml):
    matrix=ET.fromstring(matrix_xml)
    vendor=ET.fromstring(vendor_xml)
    if matrix.tag!="compatibility-matrix" or matrix.get("type")!="framework":
        raise ValueError("Expected framework compatibility matrix")
    if vendor.tag!="manifest" or vendor.get("type")!="device":
        raise ValueError("Expected device manifest")
    provided={h.findtext("name") for h in vendor.findall("hal")}
    entries=[]
    for h in matrix.findall("hal"):
        name=h.findtext("name")
        if not name:
            continue
        optional=h.get("optional")
        entries.append({
            "name":name,
            "format":h.get("format"),
            "optional_attribute":optional,
            "required_by_this_entry":optional=="false",
            "declared_in_base_vendor_manifest":name in provided,
            "versions":[x.text for x in h.findall("version") if x.text],
            "interfaces":[{"name":i.findtext("name"),"instances":[x.text for x in i.findall("instance") if x.text],
                           "regex_instances":[x.text for x in i.findall("regex-instance") if x.text]} for i in h.findall("interface")]
        })
    return {
        "framework_level":matrix.get("level"),
        "vendor_target_level":vendor.get("target-level"),
        "hal_entries":entries,
        "required_entries_absent_by_name":[x["name"] for x in entries if x["required_by_this_entry"] and not x["declared_in_base_vendor_manifest"]],
        "optional_entries_absent_by_name":[x["name"] for x in entries if x["optional_attribute"]=="true" and not x["declared_in_base_vendor_manifest"]],
        "unknown_optionality_entries":[x["name"] for x in entries if x["optional_attribute"] not in ("true","false")],
        "compatible":None,
        "warning":"This is per-file diagnostics, NOT libvintf aggregation. Name-only presence does not verify versions/instances; absence may be satisfied by manifest fragments or other partitions. Never use to approve flashing."
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("matrix",type=Path)
    p.add_argument("vendor",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=classify(a.matrix.read_text(),a.vendor.read_text())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("Matrix FCM:",result["framework_level"],"HAL entries:",len(result["hal_entries"]))
    print("Required absent by name:",len(result["required_entries_absent_by_name"]))
    print("Optional absent by name:",len(result["optional_entries_absent_by_name"]))
    print("Unknown optionality:",len(result["unknown_optionality_entries"]))
if __name__=="__main__":
    main()
