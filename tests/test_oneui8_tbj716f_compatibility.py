import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from check_oneui8_tbj716f_compatibility import assess

class OneUI8CompatibilityTests(unittest.TestCase):
    def test_missing_evidence_is_not_ready(self):
        result = assess({})
        self.assertFalse(result["ready_for_device_trial"])
        self.assertTrue(all(x["status"] == "unknown" for x in result["checks"]))

    def test_other_lenovo_device_rejected(self):
        result = assess({"model": "TB710FU"})
        self.assertEqual(result["checks"][0]["status"], "fail")

    def test_old_vendor_requires_review(self):
        result = assess({"model": "TB-J716F", "vendor_api_level": 32})
        self.assertEqual(result["checks"][2]["status"], "review")
        self.assertFalse(result["ready_for_device_trial"])

    def test_capacity_shortfall_rejected(self):
        result = assess({"system_partition_capacity_bytes": 2_000_000_000})
        self.assertEqual(result["checks"][4]["status"], "fail")

    def test_all_static_evidence_passes_but_no_boot_claim(self):
        result = assess({"model": "TB-J716F", "supported_abis": ["arm64-v8a"],
                         "vendor_api_level": 34, "vendor_runtime_verified": True, "vintf_compatible": True,
                         "system_partition_free_bytes": 7_000_000_000,
                         "verified_recovery_path": True})
        self.assertTrue(result["ready_for_device_trial"])
        self.assertIn("never proves boot", result["note"])

if __name__ == "__main__":
    unittest.main()
