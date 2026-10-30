import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "check_tbj716f_super_budget.py"
spec = importlib.util.spec_from_file_location("super_budget", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class BudgetTests(unittest.TestCase):
    def test_known_stock_and_donor_remain_unverified(self):
        report = mod.assess(mod.SUPER_BYTES, mod.DONOR_BYTES)
        self.assertEqual(report["remaining_before_other_partitions_bytes"], 1744820480)
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertIsNone(report["fits_known_budget"])

    def test_oversized_other_partitions_fail(self):
        report = mod.assess(100, 70, 31)
        self.assertEqual(report["status"], "capacity_fail")
        self.assertFalse(report["fits_known_budget"])

    def test_capacity_pass_is_not_boot_approval(self):
        report = mod.assess(100, 70, 20, 5)
        self.assertEqual(report["status"], "capacity_only_pass")
        self.assertTrue(report["fits_known_budget"])

    def test_reject_invalid_input(self):
        with self.assertRaises(ValueError):
            mod.assess(100, -1)
        with self.assertRaises(ValueError):
            mod.assess(100, 10, -5)

if __name__ == "__main__":
    unittest.main()
