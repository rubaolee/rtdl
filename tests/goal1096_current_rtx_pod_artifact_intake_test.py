from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _artifact(
    *,
    scenario: str,
    skip_validation: bool,
    matches_oracle: bool | None,
    median_sec: float = 0.2,
    extra_result: dict | None = None,
    coordinate_mapping: str | None = None,
) -> dict:
    result = {
        "matches_oracle": matches_oracle,
        **(extra_result or {}),
    }
    scenario_payload = {
        "scenario": scenario,
        "mode": "optix",
        "result": result,
        "timings_sec": {"optix_query_sec": {"median_sec": median_sec}},
    }
    if coordinate_mapping is not None:
        scenario_payload["coordinate_mapping"] = coordinate_mapping
    return {
        "schema_version": "goal887_prepared_decision_phase_contract_v1",
        "parameters": {"skip_validation": skip_validation},
        "scenario": scenario_payload,
    }


class Goal1096CurrentRtxPodArtifactIntakeTest(unittest.TestCase):
    def test_missing_artifacts_require_cloud(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            payload = module.build_intake(Path(tmpdir))

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "needs_cloud_artifacts")
        self.assertEqual(payload["expected_artifact_count"], 3)
        self.assertEqual(payload["missing_artifact_count"], 3)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_all_current_artifacts_pass_but_do_not_authorize_claims(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root
                / "goal1084_facility_recentered_rtx_pod_packet"
                / "facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                _artifact(
                    scenario="facility_service_coverage_recentered",
                    skip_validation=False,
                    matches_oracle=True,
                    coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                ),
            )
            _write_json(
                root / "goal1093_barnes_hut_20m_contract" / "barnes_hut_depth8_4096_validation.json",
                _artifact(
                    scenario="barnes_hut_node_coverage",
                    skip_validation=False,
                    matches_oracle=True,
                    extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                ),
            )
            _write_json(
                root / "goal1093_barnes_hut_20m_contract" / "barnes_hut_depth8_20m_timing.json",
                _artifact(
                    scenario="barnes_hut_node_coverage",
                    skip_validation=True,
                    matches_oracle=None,
                    extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                    median_sec=0.4,
                ),
            )
            payload = module.build_intake(root)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "ready_for_2ai_review_not_public_claim")
        self.assertEqual(payload["missing_artifact_count"], 0)
        self.assertEqual(payload["public_speedup_claim_authorized_count"], 0)

    def test_facility_bad_oracle_blocks(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root
                / "goal1084_facility_recentered_rtx_pod_packet"
                / "facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                _artifact(
                    scenario="facility_service_coverage_recentered",
                    skip_validation=False,
                    matches_oracle=False,
                    coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                ),
            )
            payload = module.build_intake(root)

        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_barnes_timing_floor_not_met_is_not_claim_ready(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_json(
                root
                / "goal1084_facility_recentered_rtx_pod_packet"
                / "facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                _artifact(
                    scenario="facility_service_coverage_recentered",
                    skip_validation=False,
                    matches_oracle=True,
                    coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                ),
            )
            _write_json(
                root / "goal1093_barnes_hut_20m_contract" / "barnes_hut_depth8_4096_validation.json",
                _artifact(
                    scenario="barnes_hut_node_coverage",
                    skip_validation=False,
                    matches_oracle=True,
                    extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                ),
            )
            _write_json(
                root / "goal1093_barnes_hut_20m_contract" / "barnes_hut_depth8_20m_timing.json",
                _artifact(
                    scenario="barnes_hut_node_coverage",
                    skip_validation=True,
                    matches_oracle=None,
                    extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                    median_sec=0.01,
                ),
            )
            payload = module.build_intake(root)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["overall_status"], "timing_floor_not_met")
        self.assertEqual(payload["timing_below_floor_count"], 1)

    def test_common_blocking_paths_are_covered(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        cases = [
            (
                "skip_validation_mismatch",
                "goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                _artifact(
                    scenario="facility_service_coverage_recentered",
                    skip_validation=True,
                    matches_oracle=True,
                    coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                ),
            ),
            (
                "wrong_schema",
                "goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                {
                    **_artifact(
                        scenario="facility_service_coverage_recentered",
                        skip_validation=False,
                        matches_oracle=True,
                        coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                    ),
                    "schema_version": "wrong",
                },
            ),
            (
                "non_optix_mode",
                "goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                {
                    **_artifact(
                        scenario="facility_service_coverage_recentered",
                        skip_validation=False,
                        matches_oracle=True,
                        coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                    ),
                    "scenario": {
                        **_artifact(
                            scenario="facility_service_coverage_recentered",
                            skip_validation=False,
                            matches_oracle=True,
                            coordinate_mapping="copy_local_recentered_queries_canonical_depots",
                        )["scenario"],
                        "mode": "dry-run",
                    },
                },
            ),
            (
                "facility_missing_coordinate_mapping",
                "goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json",
                _artifact(scenario="facility_service_coverage_recentered", skip_validation=False, matches_oracle=True),
            ),
            (
                "barnes_wrong_contract",
                "goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json",
                _artifact(
                    scenario="barnes_hut_node_coverage",
                    skip_validation=False,
                    matches_oracle=True,
                    extra_result={"barnes_tree_depth": 7, "hit_threshold": 4, "node_count": 65536},
                ),
            ),
            (
                "barnes_timing_missing_median",
                "goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json",
                {
                    **_artifact(
                        scenario="barnes_hut_node_coverage",
                        skip_validation=True,
                        matches_oracle=None,
                        extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                    ),
                    "scenario": {
                        **_artifact(
                            scenario="barnes_hut_node_coverage",
                            skip_validation=True,
                            matches_oracle=None,
                            extra_result={"barnes_tree_depth": 8, "hit_threshold": 4, "node_count": 65536},
                        )["scenario"],
                        "timings_sec": {"optix_query_sec": {"min_sec": 0.2}},
                    },
                },
            ),
        ]

        for name, relative_path, artifact in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                _write_json(root / relative_path, artifact)
                payload = module.build_intake(root)

            self.assertFalse(payload["valid"])
            self.assertEqual(payload["overall_status"], "blocked")
            self.assertEqual(payload["blocked_count"], 1)

    def test_malformed_json_blocks(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["build_intake"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = (
                root
                / "goal1084_facility_recentered_rtx_pod_packet"
                / "facility_recentered_coverage_threshold_2_5m_optix_validation.json"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{", encoding="utf-8")
            payload = module.build_intake(root)

        self.assertFalse(payload["valid"])
        self.assertEqual(payload["overall_status"], "blocked")
        self.assertEqual(payload["blocked_count"], 1)

    def test_unknown_app_blocks_review_row(self) -> None:
        module = __import__("scripts.goal1096_current_rtx_pod_artifact_intake", fromlist=["_review_row"])
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            row = {
                "app": "unknown_app",
                "path_name": "unknown",
                "phase": "unknown",
                "output_json": "unknown_dir/unknown.json",
                "requires_validation": True,
                "contains_skip_validation": False,
                "timing_floor_sec": None,
            }
            _write_json(
                root / "unknown_dir" / "unknown.json",
                _artifact(scenario="facility_service_coverage_recentered", skip_validation=False, matches_oracle=True),
            )
            reviewed = module._review_row(row, root)

        self.assertEqual(reviewed["review_status"], "blocked")
        self.assertIn("unexpected app", reviewed["reason"])

    def test_cli_writes_intake_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "intake.json"
            output_md = Path(tmpdir) / "intake.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1096_current_rtx_pod_artifact_intake.py",
                    "--artifact-root",
                    tmpdir,
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertIn("needs_cloud_artifacts", completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["expected_artifact_count"], 3)
            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("Goal1096 Current RTX Pod Artifact Intake", markdown)
            self.assertIn("does not authorize public RTX speedup claims", markdown)


if __name__ == "__main__":
    unittest.main()
