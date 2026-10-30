import unittest

from threshold_bench import (
    count_branch,
    count_branchless,
    count_threshold,
    ripes_case,
    run_all,
    run_case,
)


class TestBench(unittest.TestCase):
    def test_all_workloads_correct(self):
        for row in run_all():
            self.assertTrue(row["correct"], row)

    def test_ripes_case_count(self):
        # 3 elements take the >= path (8 each), 5 do not (9 each): 6 + 24 + 45 + 2 = 77
        values, limit, ic_branch, ic_threshold = ripes_case()
        self.assertEqual(ic_branch, 77)
        self.assertEqual(ic_threshold, 6 + 7 * 8 + 2)

    def test_per_element_counts(self):
        self.assertEqual(count_branch([10], 5) - count_branch([], 5), 8)
        self.assertEqual(count_branch([1], 5) - count_branch([], 5), 9)
        self.assertEqual(count_branchless([0]) - count_branchless([]), 9)
        self.assertEqual(count_threshold([0]) - count_threshold([]), 7)

    def test_speedup_bounded_by_per_element_ratio(self):
        # threshold saves 1-2 instructions out of 8-9 per element, so speedup stays below 9/7
        for row in run_all(ratios=(1.0,)):
            self.assertGreater(row["speedup_branch"], 1.0)
            self.assertLessEqual(row["speedup_branchless"], 9 / 7 + 1e-9)

    def test_slower_clock_reduces_speedup(self):
        fast = run_case("pixel", 256, 1.0)["speedup_branch"]
        slow = run_case("pixel", 256, 1.2)["speedup_branch"]
        self.assertLess(slow, fast)


if __name__ == "__main__":
    unittest.main()
