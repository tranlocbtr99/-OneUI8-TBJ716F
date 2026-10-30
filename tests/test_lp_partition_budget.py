import importlib.util
import pathlib
import unittest

path=pathlib.Path(__file__).resolve().parents[1]/"tools"/"report_lp_partition_budget.py"
spec=importlib.util.spec_from_file_location("lp_budget",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class LpBudgetTests(unittest.TestCase):
    def test_extent_accounting(self):
        data={"tables_checksum_ok":True,"partitions":[
            {"name":"system_a","group_index":0,"extents":[{"sectors":20,"type":0}]},
            {"name":"vendor_a","group_index":0,"extents":[{"sectors":10,"type":0}]},
            {"name":"product_a","group_index":0,"extents":[{"sectors":4,"type":1}]}]}
        report=module.summarize(data,100000,20000)
        self.assertEqual(report["non_system_allocated_bytes"],7168)
        self.assertEqual(report["non_system_linear_physical_bytes"],5120)
        self.assertEqual(report["allocated_linear_physical_bytes"],15360)
        self.assertEqual(report["nominal_remaining_after_donor_and_other_bytes"],72832)
        self.assertEqual(report["status"],"evidence_only_not_flashable")

    def test_system_b_not_counted_as_non_system(self):
        data={"tables_checksum_ok":True,"partitions":[
            {"name":"system_a","extents":[{"sectors":10,"type":0}]},
            {"name":"system_b","extents":[{"sectors":10,"type":0}]},
            {"name":"vendor_a","extents":[{"sectors":4,"type":0}]}]}
        report=module.summarize(data,100000,20000)
        self.assertEqual(report["non_system_allocated_bytes"],2048)
        self.assertEqual(report["ab_slot_accounting"],"not_verified")

    def test_unverified_metadata_rejected(self):
        with self.assertRaisesRegex(ValueError,"verified"):
            module.summarize({"partitions":[]},100,10)

    def test_duplicate_partition_rejected(self):
        p={"name":"vendor_a","extents":[]}
        with self.assertRaisesRegex(ValueError,"duplicate"):
            module.summarize({"tables_checksum_ok":True,"partitions":[p,p]},100,10)

if __name__=="__main__":
    unittest.main()
