#!/usr/bin/env python3
"""Prepare a VINTF filesystem tree for official checkvintf testing.

No vendor files are invented. Fail if required inputs are unavailable.
"""
import argparse
import json
import shutil
from pathlib import Path

def stage(donor_dir, stock_dir, output_dir):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("Output directory must be empty")
    matrix_dir=donor_dir/"raw-matrices"
    matrices=sorted(matrix_dir.glob("compatibility_matrix.*.xml"))
    vendor=stock_dir/"vendor-vintf"/"manifest.xml"
    if not matrices or not vendor.is_file():
        raise FileNotFoundError("Raw framework matrices and stock vendor manifest are required")
    dst=output_dir/"system"/"etc"/"vintf"
    dst.mkdir(parents=True,exist_ok=True)
    for p in matrices:
        shutil.copyfile(p,dst/p.name)
    target=output_dir/"vendor"/"etc"/"vintf"/"manifest.xml"
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(vendor,target)
    report={"matrices":[p.name for p in matrices],"vendor_manifest":str(vendor),
            "complete_vintf_tree":False,"checkvintf_passed":None,"flashable":False,
            "limitations":["Only extracted framework matrices and base vendor manifest are present",
                           "Missing system/product/system_ext matrices and manifest fragments, kernel metadata and runtime properties",
                           "Do not interpret checkvintf outcome on this partial tree as device compatibility"]}
    (output_dir/"STAGING-STATUS.json").write_text(json.dumps(report,indent=2)+"\n")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("donor",type=Path)
    p.add_argument("stock",type=Path)
    p.add_argument("output",type=Path)
    a=p.parse_args()
    print(json.dumps(stage(a.donor,a.stock,a.output),indent=2))
if __name__=="__main__":
    main()
