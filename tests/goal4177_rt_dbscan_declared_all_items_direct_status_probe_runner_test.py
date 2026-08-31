from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal4177_rt_dbscan_declared_all_items_direct_status_probe.py"


class Goal4177RtDbscanDeclaredAllItemsDirectStatusProbeRunnerTest(unittest.TestCase):
    def test_runner_measures_current_measured_and_declared_routes(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("RT_DBSCAN_GROUPED_STREAM_NUMBA_APP_MODE", source)
        self.assertIn("RT_DBSCAN_PREDICATE_DIRECT_STATUS_ALL_TRUE_APP_MODE", source)
        self.assertIn("RT_DBSCAN_DECLARED_ALL_TRUE_DIRECT_STATUS_APP_MODE", source)
        self.assertIn('"current_grouped_stream_numba"', source)
        self.assertIn('"measured_alltrue_predicate_direct_status"', source)
        self.assertIn('"declared_all_items_direct_status"', source)
        self.assertIn("--point-count", source)
        self.assertIn("2_097_152", source)
        self.assertIn("--partition-cell-factor", source)

    def test_runner_prints_progress_for_long_pod_runs(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for marker in (
            "GOAL4177_PROBE_START",
            "GOAL4177_ROUTE_START",
            "GOAL4177_ROUTE_DONE",
            "GOAL4177_PROBE_DONE",
        ):
            self.assertIn(marker, source)
        self.assertGreaterEqual(source.count("flush=True"), 4)
        self.assertIn('"warmup_policy": "per_route_small_input_warmup_before_large_measurement"', source)
        self.assertIn('"warmup_rows": warmup_rows', source)
        self.assertIn('label=f"warmup_{label}"', source)
        self.assertIn("for label, mode in route_specs", source)

    def test_runner_records_refactor_boundaries_and_claim_blocks(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        for fragment in (
            "declared_route_uses_generic_all_items_direct_status_signature",
            "declared_route_materializes_predicate_columns",
            "declared_route_executes_rt_count_threshold",
            "Internal large-scale route evidence only",
            '"release_authorized": False',
            '"paper_speedup_claim_authorized": False',
            '"public_speedup_claim_authorized": False',
            '"rt_core_speedup_claim_authorized": False',
            '"whole_app_speedup_claim_authorized": False',
            '"true_zero_copy_claim_authorized": False',
            '"native_abi_added": False',
        ):
            self.assertIn(fragment, source)

    def test_runner_preserves_signature_comparison(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn('reference = rows[0]["signature"]', source)
        self.assertIn('"same_signature_as_current"', source)
        self.assertIn('"speedup_vs_current_elapsed"', source)
        self.assertIn('"declared_speedup_vs_current_elapsed"', source)


if __name__ == "__main__":
    unittest.main()
