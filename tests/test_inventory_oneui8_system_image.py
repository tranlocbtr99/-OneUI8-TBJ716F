import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools"))
import inventory_oneui8_system_image as inv

class ImageInventoryTests(unittest.TestCase):
    def test_reject_non_ext4(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "image.img"
            p.write_bytes(b"not ext4" + bytes(4096))
            with patch.object(inv.shutil, "which", return_value="/usr/bin/debugfs"):
                with self.assertRaises(ValueError):
                    inv.inventory(p)

    def test_missing_debugfs(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "image.img"
            p.write_bytes(bytes(4096))
            with patch.object(inv.shutil, "which", return_value=None):
                with self.assertRaises(RuntimeError):
                    inv.inventory(p)

    def test_parse_build_properties_and_dolby_tokens(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "image.img"
            data = bytearray(4096)
            data[1080:1082] = b"\x53\xef"
            p.write_bytes(data)
            def fake_read(image, filename):
                if filename.endswith("build.prop"):
                    return {"present": True, "bytes": 43,
                            "data": "ro.build.version.release=16\nsecret.key=no\n"}
                if filename.endswith("stage_policy.conf"):
                    return {"present": True, "bytes": 20, "data": "STAGE_EFFECT_DOLBY_A"}
                return {"present": False, "reason": "not found"}
            with patch.object(inv.shutil, "which", return_value="/usr/bin/debugfs"), patch.object(inv, "read_file", side_effect=fake_read):
                result = inv.inventory(p)
            self.assertEqual(result["files"]["system_build_prop"]["selected_properties"]["ro.build.version.release"], "16")
            self.assertNotIn("secret.key", result["files"]["system_build_prop"]["selected_properties"])
            self.assertEqual(result["files"]["audio_stage_policy"]["dolby_stage_tokens"], 1)

if __name__ == "__main__":
    unittest.main()
