from __future__ import annotations

import unittest

from scripts.goal743_lsi_pip_large_cross_machine_perf import _case_specs
from scripts.goal743_lsi_pip_large_cross_machine_perf import run_case


class Goal743LsiPipLargeCrossMachinePerfTest(unittest.TestCase):
    def test_quick_large_harness_cases_match_deterministic_hashes(self) -> None:
        for spec in _case_specs("quick"):
            result = run_case(spec, repeats=1)
            self.assertGreater(result["expected_rows"], 0)
            self.assertTrue(result["parity"]["one_thread_dict"])
            self.assertTrue(result["parity"]["auto_dict"])
            self.assertTrue(result["parity"]["auto_prepared_raw"])


if __name__ == "__main__":
    unittest.main()
