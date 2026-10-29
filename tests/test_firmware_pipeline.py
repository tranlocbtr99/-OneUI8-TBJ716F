"""End-to-end offline test of ZIP inventory, format hints, extraction and identity."""
import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
from inventory_firmware_zip import inventory
from probe_partition_formats import inspect
from extract_vendor_evidence import extract
from check_firmware_identity import assess

class FirmwarePipelineTests(unittest.TestCase):
    def test_reference_pipeline(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            archive = root / "fixture.zip"
            sparse = b"\x3a\xff\x26\xed" + struct.pack("<HHHHIIII", 1, 0, 28, 12, 4096, 2, 1, 0)
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("images/super.img", sparse)
                z.writestr("vendor/build.prop", "ro.product.vendor.model=TB-J716F\nro.vendor.build.version.sdk=33\n")
                z.writestr("vendor/etc/vintf/manifest.xml", "<manifest version='1.0' type='device'/>")
            self.assertEqual(len(inventory(archive)["entries"]), 3)
            self.assertEqual(inspect(archive)["images"][0]["format_hint"], "android_sparse_v1")
            evidence = extract(archive, root / "evidence")
            props = [x["output"] for x in evidence["files"] if x["kind"] == "vendor_build_prop"]
            self.assertEqual(assess(props)["identity_status"], "target_identifier_present")
            self.assertEqual(len(evidence["files"]), 2)

    def test_image_only_is_unknown_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            archive = root / "fixture.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("images/super.img", b"not-a-real-image")
            self.assertEqual(extract(archive, root / "evidence")["files"], [])
            self.assertEqual(inspect(archive)["images"][0]["format_hint"], "unknown")

if __name__ == "__main__":
    unittest.main()
