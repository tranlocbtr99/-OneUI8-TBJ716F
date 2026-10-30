#!/usr/bin/env python3
"""Fail-closed validation of QFIL super segment references in metadata artifact."""
import argparse
import json
import re
from pathlib import Path

def assess(report):
    segments=report.get("segmented_image_names",{}).get("super",[])
    missing=report.get("unresolved_references",{})
    super_entries=report.get("super_entries",[])
    numbered=[]
    for s in segments:
        m=re.fullmatch(r"super_([1-9][0-9]*)\.img",s)
        if not m:
            raise ValueError("Unexpected super segment filename: "+str(s))
        numbered.append(int(m.group(1)))
    contiguous=bool(numbered) and sorted(numbered)==list(range(1,len(numbered)+1))
    unresolved_super=any("super.img"==k for k in missing)
    size_values=set()
    for e in super_entries:
        try:
            size_values.add(int(e["num_partition_sectors"])*int(e["sector_size"]))
        except (TypeError,ValueError,KeyError) as ex:
            raise ValueError("Invalid super geometry") from ex
    geometry_consistent=len(size_values)==1 and next(iter(size_values))>0
    return {
        "segments":segments,
        "numbered_segments_contiguous":contiguous,
        "unresolved_super_img_reference":unresolved_super,
        "super_geometry_consistent":geometry_consistent,
        "nominal_super_bytes":next(iter(size_values)) if geometry_consistent else None,
        "reconstruction_authorized":False,
        "reason":"Segment naming and XML reference do not establish chunk encoding, ordering, concatenation semantics or LP validity. Inspect real image headers and original packaging first."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("audit_json",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=assess(json.loads(a.audit_json.read_text(encoding="utf-8")))
    a.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    main()
