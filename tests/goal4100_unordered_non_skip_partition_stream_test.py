from __future__ import annotations

import pathlib
import unittest
from typing import Any

import rtdsl as rt


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4100_unordered_non_skip_partition_stream_2026-06-09.md"
BUILD_BASELINE = ROOT / "docs" / "reports" / "goal4096_partition_summary_build_after_device_key_decode_pod.json"
BUILD = ROOT / "docs" / "reports" / "goal4100_unordered_non_skip_build_pod.json"
REUSE_BASELINE = ROOT / "docs" / "reports" / "goal4096_partition_reuse_after_device_key_decode_pod.json"
REUSE = ROOT / "docs" / "reports" / "goal4100_unordered_non_skip_reuse_pod.json"
PHASE_BASELINE = ROOT / "docs" / "reports" / "goal4096_device_partition_key_decode_phase_breakdown_pod.json"
PHASE = ROOT / "docs" / "reports" / "goal4100_unordered_non_skip_phase_pod.json"


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _rows_by_profile(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["profile"]): row for row in doc["rows"]}


def _build_median(row: dict[str, Any]) -> float:
    return float(row["partition_summary_build_sec"]["median_sec"])


def _phase_median(row: dict[str, Any], field: str) -> float:
    return float(row["phase_summary"][field]["median_sec"])


class Goal4100UnorderedNonSkipPartitionStreamTest(unittest.TestCase):
    def test_unordered_non_skip_mode_is_explicit_and_labeled(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        for text in (source, app):
            self.assertIn("device_count_then_emit_non_skip_unordered", text)
        self.assertIn("sort_pairs=pair_enumeration != \"device_count_then_emit_non_skip_unordered\"", source)
        self.assertIn("device_atomic_append_unordered", source)
        self.assertIn("pair_order", source)

    def test_unordered_non_skip_preserves_component_signature_when_cupy_available(self) -> None:
        try:
            import cupy  # noqa: F401
        except Exception:
            self.skipTest("CuPy is not available in this local environment")

        points = [
            (0.00, 0.00, 0.00),
            (0.01, 0.00, 0.00),
            (0.02, 0.00, 0.00),
            (1.00, 1.00, 1.00),
            (1.01, 1.00, 1.00),
            (4.00, 4.00, 4.00),
        ]
        sorted_result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip",
            validate_summary_same_contract=False,
            validate_against_component_labels=False,
        )
        unordered_result = rt.build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d(
            points,
            radius=0.05,
            cell_factor=0.5,
            pair_enumeration="device_count_then_emit_non_skip_unordered",
            validate_summary_same_contract=False,
            validate_against_component_labels=True,
        )
        self.assertEqual(unordered_result["metadata"]["status"], "accept")
        self.assertTrue(unordered_result["metadata"]["same_contract_against_component_labels"])
        self.assertEqual(
            tuple(unordered_result["columns"]["component_size_signature"]),
            tuple(sorted_result["columns"]["component_size_signature"]),
        )
        self.assertEqual(
            unordered_result["metadata"]["partition_summary_pair_order"],
            "device_atomic_append_unordered",
        )

    def test_pod_artifacts_are_commit_pinned_and_boundary_blocked(self) -> None:
        for path in (BUILD, REUSE, PHASE):
            doc = _load_json(path)
            self.assertEqual(doc["source_commit"][:8], "9e11c058")
            self.assertFalse(doc["release_authorized"])
            self.assertFalse(doc["public_speedup_claim_authorized"])
            self.assertFalse(doc["rt_core_speedup_claim_authorized"])
            self.assertFalse(doc["whole_app_speedup_claim_authorized"])
            self.assertFalse(doc["native_abi_added"])
            self.assertEqual(doc["pair_enumeration"], "device_count_then_emit_non_skip_unordered")

    def test_unordered_build_is_faster_than_goal4096_sorted_non_skip(self) -> None:
        baseline = _rows_by_profile(_load_json(BUILD_BASELINE))
        candidate = _rows_by_profile(_load_json(BUILD))

        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            self.assertLess(_build_median(candidate[profile]), _build_median(baseline[profile]))

        self.assertGreater(_build_median(baseline["clustered3d"]) / _build_median(candidate["clustered3d"]), 1.15)
        self.assertGreater(_build_median(baseline["road3d"]) / _build_median(candidate["road3d"]), 1.15)
        self.assertGreater(_build_median(baseline["ngsim_dense"]) / _build_median(candidate["ngsim_dense"]), 1.10)

    def test_unordered_phase_improves_emit_path_but_not_underlying_two_pass_shape(self) -> None:
        baseline = _rows_by_profile(_load_json(PHASE_BASELINE))
        candidate = _rows_by_profile(_load_json(PHASE))

        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            self.assertLess(
                _phase_median(candidate[profile], "pair_status_emit_sec"),
                _phase_median(baseline[profile], "pair_status_emit_sec"),
            )
            self.assertGreater(_phase_median(candidate[profile], "pair_status_count_probe_sec"), 0.0)

        self.assertGreater(
            _phase_median(baseline["clustered3d"], "pair_status_emit_sec")
            / _phase_median(candidate["clustered3d"], "pair_status_emit_sec"),
            2.0,
        )
        self.assertGreater(
            _phase_median(baseline["road3d"], "pair_status_emit_sec")
            / _phase_median(candidate["road3d"], "pair_status_emit_sec"),
            1.8,
        )
        self.assertGreater(
            _phase_median(baseline["ngsim_dense"], "pair_status_emit_sec")
            / _phase_median(candidate["ngsim_dense"], "pair_status_emit_sec"),
            1.2,
        )

    def test_prepared_reuse_improves_prepare_but_remains_unpromoted(self) -> None:
        baseline = _rows_by_profile(_load_json(REUSE_BASELINE))
        candidate = _rows_by_profile(_load_json(REUSE))

        for profile in ("clustered3d", "road3d"):
            self.assertLess(float(candidate[profile]["prepare_sec"]), float(baseline[profile]["prepare_sec"]))
            self.assertFalse(candidate[profile]["prepared_metadata"]["default_route_promoted"])
            self.assertFalse(candidate[profile]["prepared_metadata"]["partition_convergence_hybrid_promoted"])
            self.assertEqual(candidate[profile]["prepared_metadata"]["partition_summary_digest"]["pair_order"], "device_atomic_append_unordered")
            self.assertLess(float(candidate[profile]["amortized"]["speedup_vs_current_reference_for_n_runs"]), 1.0)

        self.assertIsNone(candidate["road3d"]["amortized"]["break_even_runs_reference"])
        self.assertGreater(float(candidate["clustered3d"]["amortized"]["break_even_runs_reference"]), 6.0)

    def test_report_records_evidence_and_non_promotion_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "device_atomic_append_unordered",
            "1.170x",
            "2.319x",
            "0.851x",
            "does not promote",
            "does not authorize release",
            "avoid the double pass",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
