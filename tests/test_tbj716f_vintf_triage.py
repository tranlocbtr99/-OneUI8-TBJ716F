import tempfile
import unittest
from pathlib import Path
from tools.report_tbj716f_vintf_missing_hals import parse_hals

class VintfParsingTests(unittest.TestCase):
    def test_framework_and_vendor_roots(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matrix.xml"
            p.write_text('<compatibility-matrix><hal format="aidl"><name>android.hardware.foo</name><interface><name>IFoo</name><instance>default</instance></interface></hal></compatibility-matrix>')
            items = parse_hals([p], "compatibility-matrix")
            self.assertEqual(items[0]["instances"], ["IFoo/default"])
            with self.assertRaises(ValueError):
                parse_hals([p], "manifest")

if __name__ == "__main__":
    unittest.main()
