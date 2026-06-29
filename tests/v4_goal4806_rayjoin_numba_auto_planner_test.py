from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class V4Goal4806RayJoinNumbaAutoPlannerTest(unittest.TestCase):
    def test_v4_python_api_exposes_semantic_rayjoin_numba_entry(self) -> None:
        from rtdsl import v4 as rtdl_v4

        payload = rtdl_v4.paper.rayjoin.section57_polygon_overlay(
            dataset_root="missing_section57_inputs",
            partner="numba",
            select="fastest_valid",
            pairs="county_zipcode",
            check_runtime=False,
        )

        self.assertEqual(
            payload["schema"],
            "rtdl.v4.rayjoin.section57_numba_auto_primitive_planner.v1",
        )
        self.assertEqual(payload["user_semantics"]["workload"], "rayjoin_section57_polygon_overlay")
        self.assertEqual(payload["user_semantics"]["partner"], "numba")
        self.assertFalse(payload["user_semantics"]["primitive_names_required_from_user"])
        self.assertEqual(payload["columns"], ("author_code", "v2_14_exact_suite", "v4_numba_selected_plan"))
        self.assertEqual(payload["claim_classification"], "blocked_missing_inputs")

    def test_candidate_scoreboard_requires_measured_selection_not_static_route(self) -> None:
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        payload = section57_polygon_overlay(
            dataset_root="missing_section57_inputs",
            pairs="county_zipcode",
            check_runtime=False,
        )
        scoreboard = payload["candidate_scoreboard"]

        plan_ids = {candidate["plan_id"] for candidate in scoreboard}
        self.assertGreaterEqual(len(scoreboard), 3)
        self.assertIn("v4_numba_post_traversal_lsi_stream_digest", plan_ids)
        self.assertIsNone(payload["selected_plan"])
        self.assertTrue(payload["selection_policy"]["measured_candidate_required"])
        self.assertFalse(payload["selection_policy"]["hardcoded_default_allowed"])
        self.assertTrue(all(candidate["selection_role"] == "v4_numba_selected_plan" for candidate in scoreboard))

    def test_numba_partner_boundary_is_jit_device_resident_and_not_optix_callback(self) -> None:
        from rtdsl.rayjoin_numba_auto_planner import numba_section57_partner_contract
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        contract = numba_section57_partner_contract()
        self.assertTrue(contract["numba_cuda_jit_required"])
        self.assertTrue(contract["device_resident_input_required"])
        self.assertFalse(contract["host_materialization_in_hot_path_allowed"])
        self.assertFalse(contract["optix_traversal_callback_injection"])

        payload = section57_polygon_overlay(
            dataset_root="missing_section57_inputs",
            pairs="county_zipcode",
            check_runtime=False,
        )
        for candidate in payload["candidate_scoreboard"]:
            stages = candidate["stages"]
            self.assertTrue(any(stage["numba_cuda_jit_required"] for stage in stages))
            self.assertTrue(all(not stage["optix_traversal_callback_injection"] for stage in stages))
            self.assertTrue(
                any(stage["execution_boundary"].startswith("post_traversal") for stage in stages)
            )

    def test_author_v214_v4_columns_are_explicit_and_missing_author_is_blocking(self) -> None:
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        payload = section57_polygon_overlay(
            dataset_root="missing_section57_inputs",
            pairs="county_zipcode",
            check_runtime=False,
        )
        row = payload["rows"][0]

        self.assertEqual(row["baselines"]["author_code"]["status"], "blocked_missing_author_baseline")
        self.assertTrue(row["baselines"]["author_code"]["required_for_full_paper_reproduction_claim"])
        self.assertEqual(row["baselines"]["v2_14_exact_suite"]["status"], "blocked_missing_inputs")
        self.assertTrue(row["correctness_gate"]["topology_geometry_hash_required"])
        self.assertFalse(row["correctness_gate"]["row_count_only_sufficient"])

    def test_exact_inputs_and_numba_still_block_without_section57_device_columns(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pair = paper_pairs()[0]
            left = root / pair.left_relative_path
            right = root / pair.right_relative_path
            left.parent.mkdir(parents=True, exist_ok=True)
            right.parent.mkdir(parents=True, exist_ok=True)
            left.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            right.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")

            with mock.patch("rtdsl.rayjoin_numba_auto_planner.numba_partner_available", return_value=True):
                blocked = section57_polygon_overlay(
                    dataset_root=root,
                    pairs="county_zipcode",
                    check_runtime=True,
                    section57_device_columns_ready=False,
                )
                ready = section57_polygon_overlay(
                    dataset_root=root,
                    pairs="county_zipcode",
                    check_runtime=True,
                    section57_device_columns_ready=True,
                )

        blocked_statuses = {candidate["status"] for candidate in blocked["candidate_scoreboard"]}
        ready_statuses = {candidate["status"] for candidate in ready["candidate_scoreboard"]}
        self.assertEqual(blocked_statuses, {"blocked_missing_section57_device_columns"})
        self.assertEqual(ready_statuses, {"ready_for_measurement"})
        self.assertIn("section57_device_columns_requirement", blocked["runtime_probe"])
        self.assertFalse(blocked["runtime_probe"]["section57_device_columns_ready"])

    def test_measured_candidate_import_selects_fastest_valid_plan(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs
        from rtdsl.rayjoin_numba_auto_planner import RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pair = paper_pairs()[0]
            left = root / pair.left_relative_path
            right = root / pair.right_relative_path
            left.parent.mkdir(parents=True, exist_ok=True)
            right.parent.mkdir(parents=True, exist_ok=True)
            left.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            right.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            query_exec = root / "RayJoin" / "query_exec"
            polyover_exec = root / "RayJoin" / "polyover_exec"
            query_exec.parent.mkdir(parents=True, exist_ok=True)
            query_exec.write_text("", encoding="utf-8")
            polyover_exec.write_text("", encoding="utf-8")
            measurements = root / "measurements.json"
            measurements.write_text(
                json.dumps(
                    {
                        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
                        "rows": [
                            {
                                "pair_id": "county_zipcode",
                                "plan_id": "v4_numba_post_traversal_mask_compact",
                                "correctness_status": "pass",
                                "measured_total_sec": 0.22,
                                "steady_state_sec": 0.20,
                                "compile_jit_sec": 0.02,
                                "v4_vs_v2_14_speedup": 1.10,
                                "measurement_source": "pod_runtime",
                                "topology_geometry_hash_match": True,
                                "device_column_route": True,
                                "host_materialization_in_hot_path": False,
                            },
                            {
                                "pair_id": "county_zipcode",
                                "plan_id": "v4_numba_post_traversal_segmented_counts",
                                "correctness_status": "pass",
                                "measured_total_sec": 0.10,
                                "steady_state_sec": 0.09,
                                "compile_jit_sec": 0.01,
                                "v4_vs_v2_14_speedup": 1.45,
                                "measurement_source": "pod_runtime",
                                "topology_geometry_hash_match": True,
                                "device_column_route": True,
                                "host_materialization_in_hot_path": False,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch("rtdsl.rayjoin_numba_auto_planner.numba_partner_available", return_value=True):
                payload = section57_polygon_overlay(
                    dataset_root=root,
                    pairs="county_zipcode",
                    query_exec=query_exec,
                    polyover_exec=polyover_exec,
                    check_runtime=True,
                    section57_device_columns_ready=True,
                    measured_candidates_path=measurements,
                )

        self.assertEqual(payload["measurement_import"]["accepted_count"], 2)
        self.assertEqual(payload["measurement_import"]["rejected_count"], 0)
        self.assertEqual(payload["selected_plan"]["plan_id"], "v4_numba_post_traversal_segmented_counts")
        self.assertEqual(payload["selected_plan"]["correctness_status"], "pass")
        self.assertEqual(payload["selected_plan"]["measurement_source"], "pod_runtime")
        self.assertEqual(payload["claim_classification"], "high_performance")

    def test_measured_candidate_import_rejects_unsafe_rows(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs
        from rtdsl.rayjoin_numba_auto_planner import RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pair = paper_pairs()[0]
            left = root / pair.left_relative_path
            right = root / pair.right_relative_path
            left.parent.mkdir(parents=True, exist_ok=True)
            right.parent.mkdir(parents=True, exist_ok=True)
            left.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            right.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            query_exec = root / "RayJoin" / "query_exec"
            polyover_exec = root / "RayJoin" / "polyover_exec"
            query_exec.parent.mkdir(parents=True, exist_ok=True)
            query_exec.write_text("", encoding="utf-8")
            polyover_exec.write_text("", encoding="utf-8")
            measurements = root / "measurements.json"
            measurements.write_text(
                json.dumps(
                    {
                        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
                        "rows": [
                            {
                                "pair_id": "county_zipcode",
                                "plan_id": "v4_numba_post_traversal_mask_compact",
                                "correctness_status": "pass",
                                "measured_total_sec": 0.10,
                                "measurement_source": "pod_runtime",
                                "topology_geometry_hash_match": True,
                                "device_column_route": True,
                                "host_materialization_in_hot_path": True,
                            },
                            {
                                "pair_id": "wrong_pair",
                                "plan_id": "v4_numba_post_traversal_segmented_counts",
                                "correctness_status": "pass",
                                "measured_total_sec": 0.08,
                                "measurement_source": "pod_runtime",
                                "topology_geometry_hash_match": True,
                                "device_column_route": True,
                                "host_materialization_in_hot_path": False,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch("rtdsl.rayjoin_numba_auto_planner.numba_partner_available", return_value=True):
                payload = section57_polygon_overlay(
                    dataset_root=root,
                    pairs="county_zipcode",
                    query_exec=query_exec,
                    polyover_exec=polyover_exec,
                    check_runtime=True,
                    section57_device_columns_ready=True,
                    measured_candidates_path=measurements,
                )

        self.assertIsNone(payload["selected_plan"])
        self.assertEqual(payload["measurement_import"]["accepted_count"], 0)
        reasons = {row["reason"] for row in payload["measurement_import"]["rejections"]}
        self.assertIn("host_materialization_in_hot_path_not_rejected", reasons)
        self.assertIn("candidate_not_found_for_pair_and_plan", reasons)
        self.assertEqual(payload["claim_classification"], "not_release_ready")

    def test_measured_candidate_without_app_speedup_is_not_labeled_regression(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs
        from rtdsl.rayjoin_numba_auto_planner import RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA
        from rtdsl.rayjoin_numba_auto_planner import section57_polygon_overlay

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pair = paper_pairs()[0]
            left = root / pair.left_relative_path
            right = root / pair.right_relative_path
            left.parent.mkdir(parents=True, exist_ok=True)
            right.parent.mkdir(parents=True, exist_ok=True)
            left.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            right.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")
            query_exec = root / "RayJoin" / "query_exec"
            polyover_exec = root / "RayJoin" / "polyover_exec"
            query_exec.parent.mkdir(parents=True, exist_ok=True)
            query_exec.write_text("", encoding="utf-8")
            polyover_exec.write_text("", encoding="utf-8")
            measurements = root / "measurements.json"
            measurements.write_text(
                json.dumps(
                    {
                        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
                        "rows": [
                            {
                                "pair_id": "county_zipcode",
                                "plan_id": "v4_numba_post_traversal_segmented_counts",
                                "correctness_status": "pass",
                                "measured_total_sec": 0.10,
                                "measurement_source": "pod_runtime",
                                "topology_geometry_hash_match": True,
                                "device_column_route": True,
                                "host_materialization_in_hot_path": False,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch("rtdsl.rayjoin_numba_auto_planner.numba_partner_available", return_value=True):
                payload = section57_polygon_overlay(
                    dataset_root=root,
                    pairs="county_zipcode",
                    query_exec=query_exec,
                    polyover_exec=polyover_exec,
                    check_runtime=True,
                    section57_device_columns_ready=True,
                    measured_candidates_path=measurements,
                )

        self.assertEqual(payload["selected_plan"]["plan_id"], "v4_numba_post_traversal_segmented_counts")
        self.assertEqual(payload["claim_classification"], "candidate_stage_measured_no_app_speedup_claim")

    def test_cli_writes_numba_auto_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "section57_auto"
            output_json = output_dir / "evidence.json"
            output_md = output_dir / "evidence.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "examples/paper_reproduction/rayjoin.py",
                    "--section57-auto-numba",
                    "--dataset-root",
                    str(root / "missing_inputs"),
                    "--pairs",
                    "county_zipcode",
                    "--skip-runtime-probe",
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                    "--json",
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                check=True,
            )
            stdout_payload = json.loads(completed.stdout)
            file_payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")

        self.assertEqual(stdout_payload["schema"], file_payload["schema"])
        self.assertEqual(file_payload["claim_classification"], "blocked_missing_inputs")
        self.assertIn("V4+Numba Auto-Primitive Planner", markdown)
        self.assertIn("blocked_missing_author_baseline", markdown)


if __name__ == "__main__":
    unittest.main()
