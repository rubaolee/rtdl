from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
REPORT = ROOT / "docs" / "reports" / "goal4062_prepared_partition_convergence_summary_preview_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4062_prepared_partition_summary_timing_pod.json"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4062PreparedPartitionSummaryRuntimeTest(unittest.TestCase):
    def _points(self):
        return (
            (0.0, 0.0, 0.0),
            (0.2, 0.0, 0.0),
            (1.2, 0.0, 0.0),
            (1.5, 0.0, 0.0),
            (4.0, 0.0, 0.0),
        )

    def test_prepared_summary_reuses_columns_for_labels_and_signature(self) -> None:
        prepared = rt.prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d(
            self._points(),
            radius=1.0,
            cell_factor=0.5,
            validate_summary_same_contract=True,
        )

        handle_metadata = prepared.to_metadata()
        self.assertTrue(handle_metadata["prepared_partition_summary_handle"])
        self.assertEqual(handle_metadata["prepared_partition_summary_partner"], "cupy")
        self.assertEqual(handle_metadata["prepare_validation"]["status"], "accept")
        self.assertFalse(handle_metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(handle_metadata["release_authorized"])
        self.assertFalse(handle_metadata["automatic_partner_selection_allowed"])

        labels = rt.run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d(
            prepared,
            validate_against_all_pairs=True,
        )
        signature = rt.run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d(
            prepared,
            validate_against_component_labels=True,
        )

        label_values = tuple(int(value) for value in labels["columns"]["component_labels"])
        expected_signature = tuple(sorted(label_values.count(label) for label in set(label_values)))
        self.assertEqual(signature["columns"]["component_size_signature"], expected_signature)
        self.assertEqual(labels["metadata"]["status"], "accept")
        self.assertEqual(signature["metadata"]["status"], "accept")
        self.assertTrue(labels["metadata"]["partition_summary_reused"])
        self.assertTrue(signature["metadata"]["partition_summary_reused"])
        self.assertTrue(labels["metadata"]["prepared_partition_summary_reused"])
        self.assertTrue(signature["metadata"]["prepared_partition_summary_reused"])
        self.assertEqual(labels["metadata"]["prepared_partition_summary_run_index"], 1)
        self.assertEqual(signature["metadata"]["prepared_partition_summary_run_index"], 1)
        self.assertEqual(prepared.component_label_runs, 1)
        self.assertEqual(prepared.component_signature_runs, 1)

        prepared.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.run_component_signature()


class Goal4062PreparedPartitionSummarySourceTest(unittest.TestCase):
    def test_public_surface_and_metadata_boundary_are_present(self) -> None:
        for name in (
            "V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D",
            "prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_component_labels_cupy_prepared_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d",
        ):
            self.assertTrue(hasattr(rt, name), name)

        description = rt.describe_v2_8_fixed_radius_graph_component_front_door()
        status = description["candidate_strategy_runtime_status"]["partition_convergence_hybrid"]
        self.assertTrue(status["prepared_front_door_runtime_executable"])
        self.assertEqual(status["prepared_front_door_runtime_status"], "explicit_cupy_preview_not_promoted")
        self.assertIn("Goal4062", status["latest_preview_evidence_goals"])
        self.assertFalse(status["default_route_promoted"])
        self.assertFalse(status["partition_convergence_hybrid_promoted"])

    def test_source_and_report_keep_app_agnostic_non_promotion_boundary(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("class V28PreparedFixedRadiusPartitionConvergenceSummaryCupyPreview3D")
        end = source.index("def build_v2_8_fixed_radius_partition_convergence_summary_numba_preview_3d")
        prepared_section = source[start:end].lower()
        self.assertNotIn("dbscan", prepared_section)
        self.assertNotIn("cluster", prepared_section)

        text = source + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "prepared_partition_summary_handle",
            "explicit_cupy_preview_not_promoted",
            "component_size_signature",
            "partition_summary_reused",
            "no promoted default route",
            "does not add a native ABI",
            "does not choose partners automatically",
            "does not authorize public speedup",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


class Goal4062PreparedPartitionSummaryPodArtifactTest(unittest.TestCase):
    def test_pod_artifact_records_replay_speedup_without_claim_leakage(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4062")
        self.assertEqual(payload["schema"], "rtdl.goal4062.prepared_partition_summary_timing.v1")
        self.assertEqual(payload["source_commit"], "ddcc0680")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["partition_convergence_hybrid_promoted"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 6)
        for row in payload["rows"]:
            self.assertTrue(row["component_signature_match"])
            self.assertGreater(row["prepared_replay_speedup_min"], 3.0)
            self.assertGreater(row["prepared_three_run_amortized_speedup_median"], 1.5)
            self.assertTrue(row["prepared_signature_metadata"]["prepared_partition_summary_reused"])
            self.assertEqual(
                row["prepared_signature_metadata"]["prepared_partition_summary_handle_status"],
                "explicit_cupy_preview_not_promoted",
            )
            self.assertFalse(row["prepared_handle_metadata"]["release_authorized"])
            self.assertFalse(row["prepared_handle_metadata"]["automatic_partner_selection_allowed"])


if __name__ == "__main__":
    unittest.main()
