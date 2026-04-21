from __future__ import annotations

import unittest

from scripts.goal742_lsi_pip_root_perf import _case_specs
from scripts.goal742_lsi_pip_root_perf import run_case


class Goal742LsiPipRootPerfTest(unittest.TestCase):
    def test_quick_cases_preserve_parity(self) -> None:
        for spec in _case_specs("quick"):
            payload = run_case(spec, repeats=1)
            self.assertGreater(payload["row_count"], 0)
            self.assertTrue(payload["parity"]["one_thread"])
            self.assertTrue(payload["parity"]["auto_thread"])
            self.assertTrue(payload["parity"]["prepared_raw"])


if __name__ == "__main__":
    unittest.main()
