import importlib.util
import pathlib
import tempfile
import unittest
import zipfile

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "tools" / "audit_stock_inventory_artifact.py"
spec = importlib.util.spec_from_file_location("audit_stock_inventory_artifact", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class StockInventoryTests(unittest.TestCase):
    def test_segmented_images_are_not_mistaken_for_super_img(self):
        with tempfile.TemporaryDirectory() as d:
            archive = pathlib.Path(d) / "inventory.zip"
            xml = ('<?xml version="1.0"?><data>'
                   '<program label="super" filename="super.img" start_sector="10" '
                   'num_partition_sectors="20" SECTOR_SIZE_IN_BYTES="4096"/>'
                   '<program label="boot_a" filename="boot.img"/>'
                   '</data>')
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("archive-contents.txt", "super_10.img\nsuper_2.img\nboot.img\n")
                z.writestr("rawprogram0.xml", xml)
            result = module.analyze(archive)
            self.assertEqual(result["xml_count"], 1)
            self.assertEqual(result["total_references"], 2)
            self.assertEqual(result["unresolved_references"], {"super.img": ["rawprogram0.xml"]})
            self.assertEqual(result["segmented_image_names"]["super"], ["super_2.img", "super_10.img"])
            self.assertEqual(result["assessment"], "metadata_only_no_image_bytes; no sparse header or LP metadata verified")

    def test_missing_inventory_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            archive = pathlib.Path(d) / "empty.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("rawprogram0.xml", "<data/>")
            with self.assertRaisesRegex(ValueError, "Missing archive-contents"):
                module.analyze(archive)

if __name__ == "__main__":
    unittest.main()
