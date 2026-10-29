#!/usr/bin/env python3
"""Reconstruct a QFIL super partition into a local file; never flash hardware."""
import argparse
import json
import struct
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SPARSE_MAGIC = 0xED26FF3A

def reconstruct(archive, output, report):
    with zipfile.ZipFile(archive) as z:
        root = ET.fromstring(z.read("rawprogram_unsparse0.xml"))
        segments = []
        for node in root.iter("program"):
            a = node.attrib
            if a.get("label") != "super" or not a.get("filename"):
                continue
            filename = a["filename"]
            if filename not in z.namelist():
                raise ValueError("Missing segment: " + filename)
            start = int(a["start_sector"])
            sectors = int(a["num_partition_sectors"])
            sector_size = int(a["SECTOR_SIZE_IN_BYTES"])
            if min(start, sectors, sector_size) < 1:
                raise ValueError("Invalid sector metadata")
            segments.append((start, sectors, sector_size, filename))
        if not segments:
            raise ValueError("No super segments")
        if len({s[2] for s in segments}) != 1:
            raise ValueError("Mixed sector sizes")
        segments.sort()
        base = segments[0][0]
        previous_end = base
        records = []
        with open(output, "wb") as dst:
            for start, sectors, size, filename in segments:
                if start < previous_end:
                    raise ValueError("Overlapping super segments")
                previous_end = start + sectors
                expected = sectors * size
                info = z.getinfo(filename)
                with z.open(info) as src:
                    head = src.read(4)
                    if len(head) == 4 and struct.unpack("<I", head)[0] == SPARSE_MAGIC:
                        raise ValueError("Android sparse segment needs simg2img conversion: " + filename)
                    if info.file_size != expected:
                        raise ValueError(f"Size mismatch {filename}: {info.file_size} != {expected}")
                    dst.seek((start - base) * size)
                    dst.write(head)
                    while True:
                        data = src.read(4 * 1024 * 1024)
                        if not data:
                            break
                        dst.write(data)
                records.append({"file": filename, "offset": (start-base)*size, "size": expected})
            dst.truncate((previous_end-base)*segments[0][2])
    report.write_text(json.dumps({"base_sector": base, "segments": records,
      "warning": "Local reconstruction only. No device flashing or verified boot compatibility."}, indent=2)+"\\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    reconstruct(a.archive, a.output, a.report)

if __name__ == "__main__":
    main()
