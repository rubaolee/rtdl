from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_goal4670_rt_dbscan_second_win_diagnostics.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("v4_goal4670_rt_dbscan_second_win_diagnostics", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Goal4670 diagnostics script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V4Goal4670RtDbscanDiagnosticsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_baseline_preserves_goal4669_non_release_numbers(self) -> None:
        baseline = self.module.BASELINE
        self.assertEqual(baseline["source"], "Goal4669 serious same-hardware app-level rerun")
        self.assertAlmostEqual(baseline["v4_vs_v2_14_hot_speedup"], 1.086127902760864)
        self.assertAlmostEqual(baseline["v4_vs_v3_0_2_hot_speedup"], 1.083118498208389)
        self.assertEqual(baseline["formal_speedup_bar"], 1.20)

    def test_only_default_numba_signature_can_count_as_true_v4_runtime_candidate(self) -> None:
        classifications = {row["id"]: row["classification"] for row in self.module.VARIANTS}
        self.assertEqual(
            classifications["v4_default_numba_signature"],
            "candidate_true_v4_runtime_route",
        )
        self.assertEqual(
            classifications["v4_direct_side_effect_no_culling_probe"],
            "generic_native_toggle_probe_not_pre_promoted",
        )
        self.assertEqual(
            classifications["v4_cupy_column_signature_historical_route"],
            "historical_partner_route_not_new_v4_win",
        )
        self.assertEqual(
            classifications["v4_declared_all_items_direct_status"],
            "external_proof_required_historical_route_not_rt_core_win",
        )

    def test_claim_boundary_blocks_release_wording(self) -> None:
        for key, value in self.module.CLAIM_BOUNDARY.items():
            self.assertFalse(value, key)

    def test_fast_non_candidate_row_is_not_second_true_v4_win(self) -> None:
        variant = next(
            row for row in self.module.VARIANTS if row["id"] == "v4_declared_all_items_direct_status"
        )
        payload = {
            "app": "rt_dbscan_benchmark",
            "dataset": "clustered3d",
            "point_count": 262144,
            "elapsed_sec": 0.5,
            "matches_reference": None,
            "metadata": {
                "partner": "cupy",
                "rt_core_accelerated": False,
                "uses_generic_all_items_direct_status_signature": True,
            },
        }
        row = self.module._summarize_payload(payload, variant=variant)
        self.assertGreater(row["v4_variant_vs_goal4669_v2_14_hot_speedup"], 1.20)
        self.assertGreater(row["v4_variant_vs_goal4669_v3_0_2_hot_speedup"], 1.20)
        self.assertFalse(row["passes_formal_second_win_bar"])
        self.assertTrue(row["would_be_fast_but_not_true_v4_win"])


if __name__ == "__main__":
    unittest.main()
