#!/usr/bin/env python3
"""Validate internal consistency of HAL evidence; does not assert VINTF compatibility."""
import argparse
import json
from pathlib import Path

def audit(reports):
    items=[]
    for path in sorted(reports.glob("compatibility_matrix.*.json")):
        data=json.loads(path.read_text())
        entries=data.get("hal_entries",[])
        explicit=sum(x.get("optionality_status") in ("explicit_required","explicit_optional") for x in entries)
        unknown=sum(x.get("optionality_status")=="unspecified" for x in entries)
        if explicit+unknown!=len(entries):
            raise ValueError(f"Unclassified HAL entries in {path}")
        items.append({"file":path.name,"level":data.get("framework_level"),"entries":len(entries),"explicit":explicit,"unspecified":unknown})
    if not items:
        raise ValueError("No matrix classification reports found; cannot audit")
    return {"matrices":items,"compatibility_verified":False,"boot_verified":False,
            "note":"Per-file HAL metadata only; full Android libvintf check and physical boot test are still required."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("directory",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.directory)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    main()
