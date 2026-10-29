import unittest
from tools.classify_oneui8_matrix_hals import classify

VENDOR='''<manifest version="1.0" type="device" target-level="5"><hal format="hidl"><name>android.hardware.audio</name><version>6.0</version></hal></manifest>'''
MATRIX='''<compatibility-matrix version="1.0" type="framework" level="5">
<hal format="hidl" optional="false"><name>android.hardware.audio</name><version>6.0</version></hal>
<hal format="aidl" optional="true"><name>android.hardware.nfc</name><version>1</version></hal>
<hal format="aidl" optional="false"><name>android.hardware.camera.provider</name><version>1</version></hal>
</compatibility-matrix>'''

class TestClassification(unittest.TestCase):
    def test_required_and_optional(self):
        r=classify(MATRIX,VENDOR)
        self.assertEqual(r["framework_level"],"5")
        self.assertEqual(r["vendor_target_level"],"5")
        self.assertEqual(r["required_entries_absent_by_name"],["android.hardware.camera.provider"])
        self.assertEqual(r["optional_entries_absent_by_name"],["android.hardware.nfc"])
        self.assertIsNone(r["compatible"])
    def test_wrong_matrix_type(self):
        with self.assertRaises(ValueError):
            classify(MATRIX.replace('type="framework"','type="device"'),VENDOR)

if __name__=="__main__":
    unittest.main()
