#!/usr/bin/env python3
"""Inspect stock super chunk headers directly inside firmware ZIP, without extraction."""
import argparse
import hashlib
import json
import re
import struct
import zipfile
from pathlib import Path

SPARSE_MAGIC=0xED26FF3A
LP_GEOMETRY_MAGIC=0x616c4467

def inspect_zip(path, prefix="super", limit=4096):
    if not (64 <= limit <= 65536):
        raise ValueError("header limit outside safe range")
    found=[]
    seen_indices=set()
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            name=Path(info.filename).name
            match=re.fullmatch(re.escape(prefix)+r"_([1-9][0-9]*)\.img",name,re.I)
            if not match:
                continue
            index=int(match.group(1))
            if index in seen_indices:
                raise ValueError("Duplicate super segment index: "+str(index))
            seen_indices.add(index)
            with z.open(info) as stream:
                header=stream.read(min(info.file_size,limit))
            magic=struct.unpack_from("<I",header)[0] if len(header)>=4 else None
            sparse=magic==SPARSE_MAGIC
            sparse_info=None
            if sparse:
                if len(header)<28:
                    raise ValueError("Truncated Android sparse header: "+info.filename)
                major,minor,file_hdr,chunk_hdr,block,total_blocks,total_chunks,checksum=struct.unpack_from("<HHHHIIII",header,4)
                plausible=(major==1 and file_hdr>=28 and chunk_hdr>=12 and block>=512 and
                           block<=1048576 and block&(block-1)==0 and total_blocks>0 and
                           total_chunks>0 and file_hdr<=info.file_size)
                sparse_info={"major":major,"minor":minor,"file_header_size":file_hdr,
                             "chunk_header_size":chunk_hdr,"block_size":block,
                             "total_blocks":total_blocks,"total_chunks":total_chunks,
                             "declared_output_bytes":block*total_blocks,
                             "header_plausible":plausible}
            found.append({"archive_path":info.filename,"segment_index":index,
                          "zip_member_bytes":info.file_size,"first_bytes_sha256":hashlib.sha256(header).hexdigest(),
                          "first_32_hex":header[:32].hex(),"format":"android_sparse" if sparse else "unknown_or_raw",
                          "sparse_header":sparse_info})
    if not found:
        raise ValueError("No numbered super_*.img segments found in firmware ZIP")
    found.sort(key=lambda x:x["segment_index"])
    ids=[x["segment_index"] for x in found]
    return {"archive":str(path),"segments":found,"indices_contiguous":bool(ids) and ids==list(range(1,len(ids)+1)),
            "all_sparse_headers_plausible":bool(found) and all(s["format"]=="android_sparse" and s["sparse_header"]["header_plausible"] for s in found),
            "image_reconstruction_authorized":False,
            "warning":"Header identification alone cannot prove concatenation, complete chunk encoding or LP validity. No image bytes modified or flashed."}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("archive",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=inspect_zip(a.archive)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("super segments:",len(result["segments"]))
    for e in result["segments"]:
        print(e["archive_path"],e["format"],e["zip_member_bytes"])
if __name__=="__main__":
    main()
