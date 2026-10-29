import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import verify_oneui8_donor as donor

class DonorPreflightTests(unittest.TestCase):
    def test_unknown_size_rejected_without_hashing(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "donor.img"
            path.write_bytes(b"not a donor")
            result = donor.inspect(path)
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(result["candidate_type"], "unknown")

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "donor.img"
            path.write_bytes(b"fake")
            with patch.object(donor, "RAW_SIZE", 4):
                result = donor.inspect(path)
            self.assertEqual(result["status"], "rejected")
            self.assertEqual(result["hash_algorithm"], "md5")

    def test_unexpected_large_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp) / "donor.img"
            path.write_bytes(b"x")
            with patch.object(donor, "MAX_BYTES", 0):
                with self.assertRaises(ValueError):
                    donor.inspect(path)

if __name__ == "__main__":
    unittest.main()
