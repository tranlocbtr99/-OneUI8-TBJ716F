import importlib.util
import pathlib
import struct
import tempfile
import unittest
import zipfile

source=pathlib.Path(__file__).resolve().parents[1]/"tools"/"inspect_stock_super_chunk_headers.py"
spec=importlib.util.spec_from_file_location("chunk_headers",source)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ChunkHeaderTests(unittest.TestCase):
    def archive(self, entries):
        tmp=tempfile.TemporaryDirectory()
        path=pathlib.Path(tmp.name)/"firmware.zip"
        with zipfile.ZipFile(path,"w") as z:
            for name,blob in entries.items():
                z.writestr(name,blob)
        self.addCleanup(tmp.cleanup)
        return path

    def test_sparse_header(self):
        sparse=struct.pack("<IHHHHIIII",0xed26ff3a,1,0,28,12,4096,16,1,0)
        result=mod.inspect_zip(self.archive({"images/super_1.img":sparse}))
        self.assertTrue(result["indices_contiguous"])
        self.assertEqual(result["segments"][0]["format"],"android_sparse")
        self.assertEqual(result["segments"][0]["sparse_header"]["declared_output_bytes"],65536)
        self.assertTrue(result["segments"][0]["sparse_header"]["header_plausible"])
        self.assertFalse(result["image_reconstruction_authorized"])

    def test_missing_segment(self):
        result=mod.inspect_zip(self.archive({"super_1.img":b"RAW","super_3.img":b"RAW"}))
        self.assertFalse(result["indices_contiguous"])

    def test_truncated_sparse_header_rejected(self):
        with self.assertRaisesRegex(ValueError,"Truncated"):
            mod.inspect_zip(self.archive({"super_1.img":struct.pack("<I",0xed26ff3a)}))

    def test_unrelated_files_ignored(self):
        result=mod.inspect_zip(self.archive({"vendor_1.img":b"hello","super.img":b"hello"}))
        self.assertEqual(result["segments"],[])

if __name__=="__main__":
    unittest.main()
