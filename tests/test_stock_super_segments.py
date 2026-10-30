import importlib.util
import pathlib
import unittest

p=pathlib.Path(__file__).resolve().parents[1]/"tools"/"validate_stock_super_segments.py"
spec=importlib.util.spec_from_file_location("segment_validation",p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class SegmentValidationTests(unittest.TestCase):
    def test_contiguous_segments_still_do_not_authorize_reconstruction(self):
        report={"segmented_image_names":{"super":["super_1.img","super_2.img"]},
                "unresolved_references":{"super.img":["rawprogram0.xml"]},
                "super_entries":[{"num_partition_sectors":"2097152","sector_size":"4096"}]}
        r=mod.assess(report)
        self.assertTrue(r["numbered_segments_contiguous"])
        self.assertTrue(r["unresolved_super_img_reference"])
        self.assertEqual(r["nominal_super_bytes"],8589934592)
        self.assertFalse(r["reconstruction_authorized"])

    def test_missing_segment_detected(self):
        r=mod.assess({"segmented_image_names":{"super":["super_1.img","super_3.img"]},
                      "super_entries":[{"num_partition_sectors":"1","sector_size":"4096"}]})
        self.assertFalse(r["numbered_segments_contiguous"])

    def test_conflicting_geometry_detected(self):
        r=mod.assess({"segmented_image_names":{"super":["super_1.img"]},
                      "super_entries":[{"num_partition_sectors":"1","sector_size":"4096"},
                                       {"num_partition_sectors":"2","sector_size":"4096"}]})
        self.assertFalse(r["super_geometry_consistent"])

if __name__=="__main__":
    unittest.main()
