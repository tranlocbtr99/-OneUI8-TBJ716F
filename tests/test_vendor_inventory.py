import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "vendor_inventory.py"

class VendorInventoryTest(unittest.TestCase):
    def test_props_and_vintf(self):
        with tempfile.TemporaryDirectory() as td:
            d = pathlib.Path(td)
            (d / "vendor.prop").write_text("ro.vendor.build.version.sdk=33\nro.vndk.version=33\n")
            (d / "manifest.xml").write_text('<manifest version="1.0" type="device" target-level="7"><hal format="hidl"><name>android.hardware.audio</name><version>7.0</version><interface><name>IDevicesFactory</name><instance>default</instance></interface></hal></manifest>')
            out = d / "out.json"
            subprocess.run([sys.executable, str(TOOL), "--vendor-build-prop", str(d / "vendor.prop"), "--manifest", str(d / "manifest.xml"), "--output", str(out)], check=True, capture_output=True)
            obj = json.loads(out.read_text())
            self.assertEqual(obj["properties"]["vendor"]["ro.vendor.build.version.sdk"], "33")
            self.assertEqual(obj["manifests"][0]["hals"][0]["name"], "android.hardware.audio")
            self.assertEqual(obj["manifests"][0]["target_level"], "7")

    def test_missing_input_rejected(self):
        result = subprocess.run([sys.executable, str(TOOL)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)

if __name__ == "__main__":
    unittest.main()
