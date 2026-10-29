import pathlib
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from inventory_firmware_zip import inventory

class FirmwareZipInventoryTests(unittest.TestCase):
    def test_partition_only_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = pathlib.Path(temp) / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("images/super.img", "placeholder")
                z.writestr("images/vbmeta.img", "placeholder")
            result = inventory(archive)
            self.assertEqual(len(result["entries"]), 2)
            self.assertTrue(any("Partition images" in x for x in result["blockers"]))

    def test_direct_vendor_files(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = pathlib.Path(temp) / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("vendor/build.prop", "ro.vendor.build.version.sdk=33")
                z.writestr("vendor/etc/vintf/manifest.xml", "<manifest/>")
            result = inventory(archive)
            self.assertEqual({x["type"] for x in result["entries"]},
                             {"vendor_properties", "vintf_manifest"})
            self.assertFalse(result["blockers"])

    def test_ota_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = pathlib.Path(temp) / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("payload.bin", "placeholder")
            result = inventory(archive)
            self.assertTrue(any("payload.bin" in x for x in result["blockers"]))

if __name__ == "__main__":
    unittest.main()
