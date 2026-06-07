from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py"


class Goal3688RayJoinNativePipSafeMixedCompositeTest(unittest.TestCase):
    def test_runner_uses_native_pip_executor_and_safe_existing_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("prepare_relation_status_corrected_scalar_count_executor", source)
        self.assertIn("prepared_native_relation_status_corrected_scalar_count_executor", source)
        self.assertIn("_run_exact_lsi_prepared_optix", source)
        self.assertIn("run_rtdl_optix(", source)
        self.assertIn('"rtdl_optix_native_scalar_count_executor"', source)
        self.assertIn('"rtdl_optix_exact_refined_count"', source)
        self.assertIn('"rtdl_optix_active_count"', source)

    def test_runner_is_candidate_non_authorizing_packet(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("not promote a default route", source)
        self.assertIn("_claim_boundary()", source)
        self.assertIn("native_pip_safe_mixed_speedup_vs_all_cupy", source)
        self.assertIn("all_counts_match", source)
        self.assertIn("count mismatch", source)
        self.assertIn("goal3688_scoped_source_dirty", source)
        self.assertIn("SCOPED_SOURCE_PATHS", source)


if __name__ == "__main__":
    unittest.main()
