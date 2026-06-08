from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3902_current_scale_with_payload_timing_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
REPORT = ROOT / "docs" / "reports" / "goal3902_current_scale_with_payload_timing_2026-06-08.md"


def _local_stdout_path(row: dict[str, object]) -> Path:
    remote_or_local = str(row["stdout_path"])
    return ARTIFACT_DIR / "outputs" / PurePosixPath(remote_or_local).name


class Goal3902CurrentScaleWithPayloadTimingA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_full_scale_packet_passes_with_clean_runtime_provenance(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.summary["rows"]), 10)
        env = self.summary["runtime_environment"]
        self.assertEqual(env["source_commit_short"], "1a3aaa86")
        self.assertTrue(env["working_tree_clean"])
        self.assertEqual(env["git_status_short"], [])
        self.assertIn("NVIDIA RTX A5000", env["nvidia_smi"])

        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(row["status"], "pass")
                self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

    def test_payload_timing_summary_is_present_for_every_parseable_payload(self) -> None:
        expected_counts = {
            "hausdorff_xhd_scale_default_optix_threshold": 14,
            "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default": 19,
            "rt_dbscan_optix_numba_scale_default_65536_no_validation": 14,
            "robot_collision_optix_scale_default_1024_no_probe_reference": 0,
            "contact_manifold_optix_scale_default_grid64": 2,
            "raydb_style_optix_count_scale_default_262k": 7,
            "barnes_hut_numba_scale_default_8192": 2,
            "librts_spatial_index_optix_scale_default_32768": 6,
            "rtnn_prepared_optix_scale_default_65536": 10,
            "triangle_counting_optix_rt_graph_2a1_scale_default_2048": 4,
        }
        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                timing = row["semantic_stdout_check"]["payload_timing_summary"]
                self.assertTrue(timing["payload_json_object"])
                self.assertEqual(timing["timing_scalar_count"], expected_counts[row["row_id"]])
                self.assertIsInstance(timing["timing_scalars_sample"], list)

    def test_rayjoin_hot_path_scope_is_explicitly_not_wrapper_wall_time(self) -> None:
        row = next(row for row in self.summary["rows"] if row["app"] == "spatial_rayjoin")
        timing = row["semantic_stdout_check"]["payload_timing_summary"]
        self.assertEqual(
            timing["representative_hot_path_metric_scope"],
            "per_contract_hot_medians_not_wrapper_wall_time",
        )
        self.assertTrue(timing["scale_runner_elapsed_sec_is_not_hot_path_metric"])
        self.assertGreater(timing["top_level_wrapper_elapsed_sec"], 8.0)

        payload = json.loads(_local_stdout_path(row).read_text(encoding="utf-8"))
        hot = payload["representative_hot_path_summary"]
        self.assertTrue(hot["all_contract_counts_match"])
        self.assertLess(hot["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(hot["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(hot["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 8.0)

    def test_rt_dbscan_signature_timing_is_machine_readable(self) -> None:
        row = next(row for row in self.summary["rows"] if row["app"] == "rt_dbscan")
        timing = row["semantic_stdout_check"]["payload_timing_summary"]
        paths = {item["path"] for item in timing["timing_scalars_sample"]}
        self.assertAlmostEqual(timing["top_level_elapsed_sec"], 0.07936993055045605)
        self.assertIn("$.metadata.benchmark_timing_breakdown.host_observed_sec.column_signature_sec", paths)

        payload = json.loads(_local_stdout_path(row).read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        self.assertEqual(metadata["column_signature_strategy"], "numba_segmented_count_all_core_labels")
        self.assertTrue(metadata["column_signature_uses_numba_segmented_count"])
        self.assertFalse(metadata["column_signature_materializes_point_ids"])
        self.assertFalse(metadata["column_signature_materializes_core_flags"])
        host_observed = metadata["benchmark_timing_breakdown"]["host_observed_sec"]
        self.assertLess(host_observed["column_signature_sec"], 0.01)

    def test_report_preserves_internal_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3902",
            "not a public performance comparison",
            "does not authorize release action",
            "process elapsed is pod-budget evidence",
            "payload hot timing is the engineering signal",
            "per_contract_hot_medians_not_wrapper_wall_time",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
