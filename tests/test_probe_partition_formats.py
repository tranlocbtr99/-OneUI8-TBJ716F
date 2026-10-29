import pathlib
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from probe_partition_formats import identify, inspect

class PartitionProbeTests(unittest.TestCase):
    def test_android_sparse(self):
        header = b"\x3a\xff\x26\xed" + struct.pack("<HHHHIIII", 1, 0, 28, 12, 4096, 2, 1, 0)
        self.assertEqual(identify(header), "android_sparse_v1")

    def test_ext4_hint(self):
        data = bytearray(4096)
        data[1080:1082] = b"\x53\xef"
        self.assertEqual(identify(data), "ext4_candidate")

    def test_zip_probe(self):
        with tempfile.TemporaryDirectory() as d:
            archive = pathlib.Path(d) / "firmware.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("images/super.img", b"\x3a\xff\x26\xed" + struct.pack("<HHHHIIII", 1, 0, 28, 12, 4096, 2, 1, 0))
            report = inspect(archive)
            self.assertEqual(report["images"][0]["format_hint"], "android_sparse_v1")

if __name__ == "__main__":
    unittest.main()
