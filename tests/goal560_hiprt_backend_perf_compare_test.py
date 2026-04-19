from __future__ import annotations

import unittest

from scripts.goal560_hiprt_backend_perf_compare import run_perf_compare


class Goal560HiprtBackendPerfCompareTest(unittest.TestCase):
    def test_cpu_reference_backend_smoke_has_all_workloads_and_no_failures(self) -> None:
        payload = run_perf_compare(repeats=1, backends=("cpu_python_reference",))
        self.assertEqual(payload["summary"]["fail"], 0)
        self.assertEqual(len(payload["results"]), 18)
        for entry in payload["results"]:
            backend = entry["backends"]["cpu_python_reference"]
            self.assertEqual(backend["status"], "PASS")
            self.assertTrue(backend["parity_vs_cpu_reference"])

    def test_unknown_backend_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown backends"):
            run_perf_compare(repeats=1, backends=("bogus",))


if __name__ == "__main__":
    unittest.main()
