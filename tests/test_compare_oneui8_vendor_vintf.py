import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from compare_oneui8_vendor_vintf import compare, vendor_hals

VENDOR = '<manifest version="1.0" type="device"><hal><name>android.hardware.audio</name></hal></manifest>'

class VintfGapTests(unittest.TestCase):
    def test_name_matches_and_gaps(self):
        donor = {"files": {"framework_matrix_level_6": {
            "present": True, "vintf_summary": {"root_tag": "compatibility-matrix",
            "hal_names": ["android.hardware.audio", "android.hardware.camera"]}}}}
        result = compare(donor, VENDOR)
        self.assertEqual(result["name_matches"], ["android.hardware.audio"])
        self.assertEqual(result["names_not_declared_in_vendor_manifest"][0]["hal"],
                         "android.hardware.camera")
        self.assertEqual(result["status"], "preliminary")

    def test_no_matrix_is_not_pass(self):
        self.assertEqual(compare({"files": {}}, VENDOR)["status"],
                         "insufficient_framework_matrix_evidence")

    def test_invalid_vendor_type_rejected(self):
        with self.assertRaises(ValueError):
            vendor_hals('<manifest type="framework"/>')

    def test_malformed_vendor_xml_rejected(self):
        with self.assertRaises(Exception):
            vendor_hals("<manifest")

if __name__ == "__main__":
    unittest.main()
