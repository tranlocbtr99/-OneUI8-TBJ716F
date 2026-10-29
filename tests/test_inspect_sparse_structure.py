import io
import pathlib
import struct
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
from inspect_sparse_structure import inspect_sparse

def header(blocks=2, chunks=1):
    return struct.pack("<IHHHHIIII", 0xED26FF3A, 1, 0, 28, 12, 4096, blocks, chunks, 0)

class SparseStructureTests(unittest.TestCase):
    def test_valid_dont_care(self):
        data = header() + struct.pack("<HHII", 0xCAC3, 0, 2, 12)
        result = inspect_sparse(io.BytesIO(data), len(data))
        self.assertTrue(result["valid"])
        self.assertEqual(result["expanded_bytes"], 8192)

    def test_invalid_chunk_size(self):
        data = header() + struct.pack("<HHII", 0xCAC3, 0, 2, 13)
        self.assertFalse(inspect_sparse(io.BytesIO(data), len(data))["valid"])

    def test_truncated_payload(self):
        data = header(blocks=1) + struct.pack("<HHII", 0xCAC1, 0, 1, 4108) + b"x" * 10
        self.assertFalse(inspect_sparse(io.BytesIO(data), len(data))["valid"])

if __name__ == "__main__":
    unittest.main()
