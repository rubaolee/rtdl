from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"


class Goal5463GenericOptixAabbRefitRollbackFaultGateTest(unittest.TestCase):
    def test_post_amendment_microbenchmarks_match_without_regression(self) -> None:
        for count in (4096, 65536):
            payload = json.loads(
                (
                    DOCS
                    / f"goal5463_generic_optix_aabb_sparse_refit_linux_{count}.json"
                ).read_text(encoding="utf-8")
            )
            self.assertTrue(payload["matched"])
            self.assertGreater(
                payload["timing_diagnostic"]["same_host_microbenchmark_speedup"],
                5.0,
            )
            self.assertFalse(
                payload["claim_boundary"]["librts_paper_performance_claimed"]
            )

    def test_amendment_keeps_fault_hook_private_and_app_neutral(self) -> None:
        source = (
            ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
        ).read_text(encoding="utf-8")
        begin = source.index("static void require_prepared_aabb_index_2d_valid")
        end = source.index("struct GpuAabb3D", begin)
        window = source[begin:end].lower()
        self.assertIn("rtdl_optix_test_aabb_refit_fault", window)
        self.assertIn("primary_after_device_and_gas_update", window)
        self.assertIn("mutation_state_valid = false", window)
        for forbidden in ("librts", "rtspatial", "paper", "ray multicast"):
            self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
