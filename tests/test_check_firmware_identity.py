import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from check_firmware_identity import assess

class FirmwareIdentityTests(unittest.TestCase):
    def check(self, contents):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "build.prop"
            path.write_text(contents, encoding="utf-8")
            return assess([path])

    def test_target(self):
        result = self.check("ro.product.vendor.model=TB-J716F\nro.vendor.build.version.sdk=33\n")
        self.assertEqual(result["identity_status"], "target_identifier_present")
        self.assertEqual(result["api_properties"]["ro.vendor.build.version.sdk"], "33")

    def test_other_model(self):
        result = self.check("ro.product.vendor.model=TB-J706F\n")
        self.assertEqual(result["identity_status"], "possible_other_device")

    def test_missing_identity(self):
        result = self.check("ro.vendor.build.version.sdk=33\n")
        self.assertEqual(result["identity_status"], "identity_unverified")

if __name__ == "__main__":
    unittest.main()
