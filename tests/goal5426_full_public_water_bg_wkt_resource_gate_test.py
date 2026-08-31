import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5426_full_public_water_bg_wkt_resource_gate.json"
)
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_goal5426_full_public_water_bg_wkt_resource_gate.py"
)


class Goal5426FullPublicWaterBgWktResourceGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_resource_gate_reuses_existing_goal5311_artifacts(self) -> None:
        payload = self.summary
        self.assertEqual(
            payload["schema"],
            "rtdl.paper_reproduction.xhd.goal5426.full_public_water_bg_wkt_resource_gate.v1",
        )
        self.assertTrue(payload["matched"])
        self.assertEqual(
            payload["status"],
            "resource_gate_complete__existing_goal5311_artifacts_reused__regeneration_not_safe_on_current_tmp",
        )
        decision = payload["resource_decision"]
        self.assertFalse(decision["generation_safety_gate_passed"])
        self.assertTrue(decision["existing_artifact_reuse_gate_passed"])
        self.assertEqual(
            decision["selected_action"],
            "reuse_existing_goal5311_full_public_wkt_candidate__no_regeneration",
        )

    def test_remote_probe_records_disk_and_symlink_manifest(self) -> None:
        remote = self.summary["remote_probe"]["parsed"]
        self.assertLess(remote["tmp_free_gib"], remote["recommended_free_gib"])
        self.assertTrue(remote["write_permission_passed"])
        self.assertEqual(remote["output_dir"], "/tmp/xhd_goal5426/full_public_water_bg")
        self.assertTrue(remote["manifest_path"].endswith("/manifest.json"))
        self.assertTrue(remote["all_files_exist"])
        self.assertTrue(remote["all_sizes_match"])
        self.assertTrue(remote["all_hashes_match"])

    def test_wkt_hashes_and_sizes_match_goal5310_manifest(self) -> None:
        remote_files = self.summary["remote_probe"]["parsed"]["files"]
        expected = self.summary["expected_artifacts"]
        for key in ("waterbodies", "blockgroups"):
            self.assertTrue(remote_files[key]["exists"])
            self.assertTrue(remote_files[key]["size_matches"])
            self.assertTrue(remote_files[key]["sha256_matches"])
            self.assertEqual(remote_files[key]["actual_bytes"], expected[key]["expected_bytes"])
            self.assertEqual(remote_files[key]["actual_sha256"], expected[key]["expected_sha256"])
            self.assertTrue(remote_files[key]["symlink_created"])
            self.assertEqual(remote_files[key]["symlink_target"], remote_files[key]["source_path"])

    def test_goal5311_author_ingestion_prior_evidence_is_visible(self) -> None:
        prior = self.summary["prior_evidence"]
        self.assertTrue(prior["goal5311_author_ingestion_passed"])
        self.assertFalse(prior["goal5311_paper_value_matched"])
        self.assertAlmostEqual(prior["goal5311_hd_result"], 0.8970130085945129, places=12)
        self.assertTrue(prior["goal5314_paper_config_matches_paper_log"])
        self.assertAlmostEqual(
            prior["goal5314_paper_config_author_hd_result"],
            0.8964367508888245,
            places=12,
        )
        self.assertTrue(prior["goal5314_rtdl_matches_author_float32_with_declared_tolerance"])
        self.assertAlmostEqual(
            prior["goal5314_rtdl_exact_witness_hd_result_float64"],
            0.8964380566690101,
            places=12,
        )

    def test_claim_boundary_blocks_execution_and_figure_claims(self) -> None:
        boundary = self.summary["claim_boundary"]
        self.assertTrue(boundary["resource_gate_claimed"])
        self.assertFalse(boundary["full_public_wkt_generated_by_goal5426"])
        self.assertTrue(boundary["existing_goal5311_wkt_reused"])
        self.assertFalse(boundary["author_rtdl_correctness_claimed"])
        self.assertFalse(boundary["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundary["figure5_reproduction_claimed"])
        self.assertFalse(boundary["full_xhd_paper_reproduction_claimed"])
        self.assertFalse(boundary["performance_ratio_claimed"])
        self.assertFalse(boundary["route_micro_optimization_goal_authorized"])
        self.assertFalse(boundary["explicit_lb_reopened"])

    def test_stop_loss_gate_and_script_use_wrapper(self) -> None:
        gate = self.summary["stop_loss_gate"]
        self.assertTrue(gate["gate_generic_capability_produced"])
        self.assertIn("no app-artifact parity", gate["gate_non_app_consumer"])
        self.assertFalse(gate["gate_requires_app_specific_logic"])
        self.assertTrue(gate["gate_downstream_consumer_reachable"])

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("current_pod_ssh.py", source)
        self.assertNotIn("ssh root@", source)
        self.assertNotIn("hd_exec", source)
        self.assertNotIn("directed_max_of_nearest_distance", source)

    def test_next_goal_uses_goal5314_paper_config_not_goal5311_default_denominator(self) -> None:
        self.assertEqual(
            self.summary["next_recommended_goal"],
            "Goal5427_refresh_or_consolidate_existing_full_public_water_bg_rtdl_against_goal5314_paper_config",
        )


if __name__ == "__main__":
    unittest.main()
