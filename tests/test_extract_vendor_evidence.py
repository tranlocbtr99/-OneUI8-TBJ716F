import pathlib
import tempfile
import unittest
import zipfile
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from extract_vendor_evidence import extract

class ZipEvidenceTests(unittest.TestCase):
    def test_extract_vendor_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            archive = root / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("images/vendor/build.prop", "ro.vendor.build.version.sdk=33\n")
                z.writestr("images/vendor/etc/vintf/manifest.xml", "<manifest/>")
                z.writestr("../escape/vendor/build.prop", "bad")
                z.writestr("images/system/build.prop", "not vendor")
            result = extract(archive, root / "out")
            self.assertEqual(len(result["files"]), 2)
            self.assertEqual({f["kind"] for f in result["files"]},
                             {"vendor_build_prop", "vintf_manifest"})
            self.assertFalse((root / "escape").exists())

    def test_duplicate_vendor_entry_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            archive = root / 'duplicate.zip'
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                with zipfile.ZipFile(archive, 'w') as z:
                    z.writestr('vendor/build.prop', 'ro.product.model=TB-J716F')
                    z.writestr('vendor/build.prop', 'ro.product.model=TB-J706F')
            result = extract(archive, root / 'out')
            self.assertEqual(len(result['files']), 1)
            self.assertTrue(any('duplicate' in warning for warning in result['warnings']))

    def test_partition_image_only_reports_limitation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            archive = root / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("super.img", "placeholder")
            result = extract(archive, root / "out")
            self.assertEqual(result["files"], [])
            self.assertTrue(result["warnings"])

if __name__ == "__main__":
    unittest.main()
