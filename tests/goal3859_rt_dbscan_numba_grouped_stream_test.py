from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
FRONT_DOOR = ROOT / "src/rtdsl/v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs/reports/goal3859_rt_dbscan_numba_grouped_stream_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3859_rt_dbscan_numba_grouped_stream_a5000"
FOCUSED_SUMMARY = ARTIFACT_DIR / "summary.json"
NEW_NUMBA_PAYLOAD = ARTIFACT_DIR / "optix_rt_core_grouped_stream_numba_column_signature_3d.json"
OLD_NUMBA_PAYLOAD = ARTIFACT_DIR / "optix_rt_core_flags_numba_prepared_grid_column_signature_3d.json"
CUPY_PAYLOAD = ARTIFACT_DIR / "optix_rt_core_grouped_stream_cupy_column_signature_3d.json"
SCALE_SUMMARY = ARTIFACT_DIR / "scale_profile_summary.json"
FULL_SCALE_SUMMARY = ARTIFACT_DIR / "full_scale_summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3859RtDbscanNumbaGroupedStreamTest(unittest.TestCase):
    def test_front_door_supports_explicit_numba_grouped_stream_without_app_vocab(self) -> None:
        plan = rt.plan_v2_8_fixed_radius_graph_component_continuation(
            point_count=65536,
            radius=0.05,
            component_threshold=5,
            backend="optix",
            partner="numba",
            strategy="grouped_stream",
        )

        self.assertEqual(plan["status"], "accepted_preview")
        self.assertEqual(plan["user_selected_partner"], "numba")
        self.assertFalse(plan["fallback_selected"])
        self.assertFalse(plan["automatic_partner_selection_allowed"])
        self.assertFalse(plan["app_specific_engine_logic_allowed"])

        source = FRONT_DOOR.read_text(encoding="utf-8").lower()
        self.assertIn('("cupy", "numba")', source)
        self.assertNotIn("dbscan", source)
        self.assertNotIn("cluster", source)

    def test_rt_dbscan_app_exposes_numba_grouped_stream_modes(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("optix_rt_core_grouped_stream_numba_components_3d", source)
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", source)
        self.assertIn('grouped_stream_partner = "numba"', source)
        self.assertIn("prepare_v2_8_fixed_radius_graph_component_continuation_3d", source)
        self.assertIn('partner=grouped_stream_partner', source)
        self.assertNotIn('"native_dbscan_abi_added": true', source)

    def test_registry_promotes_numba_grouped_stream_current_rt_dbscan_row(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "rt_dbscan")

        self.assertEqual(row["row_id"], "rt_dbscan_optix_numba_scale_default_65536_no_validation")
        self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", row["command"])
        self.assertIn("Goal3859", row["evidence_refs"])
        self.assertTrue(row["requires_numba"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["broad_rt_core_claim_authorized"])
        self.assertFalse(row["automatic_partner_selection_authorized"])
        self.assertFalse(row["app_specific_native_engine_logic_allowed"])

    def test_focused_a5000_artifacts_match_and_improve_old_numba_route(self) -> None:
        summary = _load(FOCUSED_SUMMARY)
        old_payload = _load(OLD_NUMBA_PAYLOAD)
        cupy_payload = _load(CUPY_PAYLOAD)
        new_payload = _load(NEW_NUMBA_PAYLOAD)
        metadata = new_payload["metadata"]

        self.assertTrue(summary["all_match"])
        self.assertGreater(summary["new_vs_old_speedup"], 2.0)
        self.assertLess(summary["new_vs_cupy_ratio"], 1.10)
        self.assertLess(new_payload["elapsed_sec"], old_payload["elapsed_sec"] / 2.0)
        self.assertLess(new_payload["elapsed_sec"], cupy_payload["elapsed_sec"] * 1.10)

        self.assertEqual(metadata["partner"], "numba")
        self.assertEqual(
            metadata["path"],
            "optix_rt_grouped_stream_numba_radius_graph_column_signature_3d",
        )
        native_metadata = metadata["native_grouped_stream_metadata"]
        self.assertEqual(
            native_metadata["native_symbol"],
            "rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_device_outputs",
        )
        self.assertEqual(
            native_metadata["native_execution_path"],
            "prepared_rt_core_grouped_union_3d_all_items_self_query",
        )
        self.assertFalse(metadata["materializes_neighbor_rows"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_current_scale_profile_and_full_refresh_use_new_route(self) -> None:
        for path, expected_rows in ((SCALE_SUMMARY, 1), (FULL_SCALE_SUMMARY, 10)):
            summary = _load(path)
            self.assertTrue(summary["all_pass"])
            self.assertEqual(summary["json_pass_count"], expected_rows)
            self.assertFalse(summary["release_authorized"])
            self.assertFalse(summary["public_speedup_claim_authorized"])
            self.assertFalse(summary["broad_rt_core_claim_authorized"])

            row = next(row for row in summary["rows"] if row["app"] == "rt_dbscan")
            self.assertEqual(row["status"], "pass")
            self.assertIn("optix_rt_core_grouped_stream_numba_column_signature_3d", row["command"])
            self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])
            payload = _load(ROOT / row["stdout_path"])
            self.assertEqual(
                payload["metadata"]["path"],
                "optix_rt_grouped_stream_numba_radius_graph_column_signature_3d",
            )
            self.assertEqual(payload["metadata"]["partner"], "numba")
            self.assertLess(payload["elapsed_sec"], 0.2)

    def test_report_records_purpose_evidence_and_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3859",
            "RT-DBSCAN Numba Grouped-Stream Route",
            "2.449x faster",
            "1.017x as slow",
            "all_match: true",
            "does not add a DBSCAN-specific native engine path",
            "automatic partner selection",
            "true zero-copy claims",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
