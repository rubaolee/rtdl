from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _baseline_contract() -> dict[str, object]:
    return {
        "status": "required_before_public_speedup_claim",
        "minimum_repeated_runs": 3,
        "requires_correctness_parity": True,
        "requires_phase_separation": True,
        "forbidden_comparison": "do not compare scalar/prepared sub-paths against whole-app baselines",
        "comparable_metric_scope": "same result semantics",
        "required_baselines": ["cpu_oracle_same_semantics"],
        "required_phases": ["native_query"],
        "claim_limit": "bounded sub-path only",
    }


class Goal762RtxCloudArtifactReportTest(unittest.TestCase):
    def test_dry_run_summary_is_ok_without_benchmark_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "dry_run_summary.json"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal761_rtx_cloud_run_all.py",
                    "--dry-run",
                    "--only",
                    "robot_collision_screening",
                    "--output-json",
                    str(summary),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze", "to_markdown"])
            payload = module.analyze(summary)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["entry_count"], 1)
            self.assertEqual(payload["rows"][0]["artifact_status"], "dry_run_not_expected")
            markdown = module.to_markdown(payload)
            self.assertIn("does not authorize RTX speedup claims", markdown)

    def test_missing_artifact_after_ok_runner_needs_attention(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            summary.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "dry_run": False,
                        "results": [
                            {
                                "app": "robot_collision_screening",
                                "path_name": "prepared_pose_flags",
                                "claim_scope": "prepared OptiX ray/triangle any-hit pose-flag summary",
                                "non_claim": "not continuous collision detection",
                                "baseline_review_contract": _baseline_contract(),
                                "result": {
                                    "status": "ok",
                                    "returncode": 0,
                                    "command": [
                                        "python3",
                                        "script.py",
                                        "--output-json",
                                        "docs/reports/does_not_exist_goal762.json",
                                    ],
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            payload = module.analyze(summary)
            self.assertEqual(payload["status"], "needs_attention")
            self.assertEqual(payload["rows"][0]["artifact_status"], "missing")

    def test_fixed_radius_scalar_summary_fields_are_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_scalar_summary_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "app": "outlier_detection",
                                "schema_version": "goal825_tier1_phase_contract_v1",
                                "cloud_claim_contract": {
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not row-output",
                                    "required_phase_groups": [
                                        "prepared_optix_warm_query_sec",
                                        "prepared_optix_postprocess_sec",
                                    ],
                                },
                                "result_mode": "threshold_count",
                                "prepared_optix_warm_query_sec": {
                                    "min_sec": 0.1,
                                    "median_sec": 0.2,
                                    "max_sec": 0.3,
                                },
                                "prepared_optix_postprocess_sec": {
                                    "min_sec": 0.0,
                                    "median_sec": 0.0,
                                    "max_sec": 0.0,
                                },
                                "prepared_output": {
                                    "threshold_reached_count": 6,
                                    "outlier_count": 2,
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "outlier_detection",
                                    "path_name": "prepared_fixed_radius_density_summary",
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not a whole-app RTX speedup claim",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_scalar_summary_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["artifact_status"], "ok")
            self.assertEqual(row["result_mode"], "threshold_count")
            self.assertEqual(row["threshold_reached_count"], 6)
            self.assertEqual(row["warm_query_median_sec"], 0.2)
            self.assertEqual(row["postprocess_median_sec"], 0.0)
            self.assertEqual(row["cloud_contract_status"], "ok")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_db_compact_summary_phase_fields_are_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_db_compact_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "schema_version": "goal825_tier1_phase_contract_v1",
                        "results": [
                            {
                                "backend": "optix",
                                "schema_version": "goal825_tier1_phase_contract_v1",
                                "one_shot_total_sec": 2.0,
                                "prepared_session_prepare_total_sec": 0.5,
                                "prepared_session_warm_query_sec": {
                                    "min_sec": 0.1,
                                    "median_sec": 0.2,
                                    "max_sec": 0.3,
                                },
                                "prepared_session_close_sec": 0.01,
                                "speedup_one_shot_over_warm_query_median": 10.0,
                                "cloud_claim_contract": {
                                    "claim_scope": "prepared DB compact-summary sessions only",
                                    "non_claim": "not SQL",
                                    "required_phase_groups": [
                                        "one_shot_total_sec",
                                        "prepared_session_prepare_total_sec",
                                        "prepared_session_warm_query_sec",
                                        "reported_prepare_phases_sec",
                                        "reported_run_phases_sec",
                                        "reported_native_db_phases_sec",
                                    ],
                                },
                                "phase_contract": {},
                                "reported_prepare_phases_sec": {"unified_session": {"prepare_session_sec": 0.5}},
                                "reported_run_phases_sec": {
                                    "regional_dashboard": {
                                        "query_conjunctive_scan_count_sec": 0.02,
                                        "query_grouped_count_summary_sec": 0.03,
                                        "python_summary_postprocess_sec": 0.004,
                                    },
                                    "sales_risk": {
                                        "query_conjunctive_scan_count_sec": 0.01,
                                        "query_grouped_sum_summary_sec": 0.04,
                                        "python_summary_postprocess_sec": 0.006,
                                    },
                                },
                                "reported_run_phase_modes": {
                                    "sales_risk": {"scan": "count_summary"},
                                },
                                "reported_native_db_phases_sec": {
                                    "sales_risk": {"grouped_sum_summary": {"traversal_sec": 0.01}},
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "database_analytics",
                                    "path_name": "prepared_db_session_sales_risk",
                                    "claim_scope": "prepared OptiX DB session behavior",
                                    "non_claim": "not SQL",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_db_compact_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["artifact_status"], "ok")
            self.assertEqual(row["cloud_contract_status"], "ok")
            self.assertEqual(row["prepare_sec"], 0.5)
            self.assertEqual(row["warm_query_median_sec"], 0.2)
            self.assertAlmostEqual(row["db_query_total_sec"], 0.1)
            self.assertAlmostEqual(row["postprocess_median_sec"], 0.01)
            self.assertEqual(row["db_native_phase_groups"], ["sales_risk"])
            self.assertEqual(row["db_run_phase_modes"]["sales_risk"]["scan"], "count_summary")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_ok_runner_with_missing_contract_needs_attention(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_missing_contract_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "results": [
                            {
                                "app": "outlier_detection",
                                "prepared_optix_warm_query_sec": {
                                    "min_sec": 0.1,
                                    "median_sec": 0.2,
                                    "max_sec": 0.3,
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "outlier_detection",
                                    "path_name": "prepared_fixed_radius_density_summary",
                                    "claim_scope": "prepared fixed-radius threshold summary traversal only",
                                    "non_claim": "not a whole-app RTX speedup claim",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_missing_contract_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            self.assertEqual(payload["status"], "needs_attention")
            self.assertEqual(payload["rows"][0]["cloud_contract_status"], "missing")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_tier2_service_contract_artifact_is_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_service_contract_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "schema_version": "goal826_tier2_phase_contract_v1",
                        "cloud_claim_contract": {
                            "claim_scope": "prepared OptiX fixed-radius threshold traversal for coverage-gap compact summaries",
                            "non_claim": "not nearest-clinic row output",
                            "required_phase_groups": [
                                "input_build",
                                "optix_prepare",
                                "optix_query",
                                "python_postprocess",
                            ],
                        },
                        "scenario": {
                            "scenario": "service_coverage_gaps",
                            "mode": "optix",
                            "timings_sec": {
                                "input_build": 0.1,
                                "optix_prepare": 0.2,
                                "optix_query": 0.3,
                                "python_postprocess": 0.4,
                            },
                            "result": {
                                "native_summary_row_count": 8,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "service_coverage_gaps",
                                    "path_name": "prepared_gap_summary",
                                    "claim_scope": "prepared OptiX fixed-radius threshold traversal",
                                    "non_claim": "not whole app",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_service_contract_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["artifact_status"], "ok")
            self.assertEqual(row["schema_version"], "goal826_tier2_phase_contract_v1")
            self.assertEqual(row["cloud_contract_status"], "ok")
            self.assertEqual(row["baseline_review_contract_status"], "ok")
            self.assertEqual(row["warm_query_median_sec"], 0.3)
            self.assertEqual(row["native_summary_row_count"], 8)
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_prepared_decision_deferred_artifact_is_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_prepared_decision_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "schema_version": "goal887_prepared_decision_phase_contract_v1",
                        "cloud_claim_contract": {
                            "claim_scope": "prepared OptiX fixed-radius threshold traversal",
                            "non_claim": "not exact Hausdorff",
                            "required_phase_groups": [
                                "input_build_sec",
                                "point_pack_sec",
                                "optix_prepare_sec",
                                "optix_query_sec",
                                "python_postprocess_sec",
                                "validation_sec",
                                "optix_close_sec",
                            ],
                        },
                        "scenario": {
                            "scenario": "hausdorff_threshold",
                            "mode": "optix",
                            "timings_sec": {
                                "input_build_sec": 0.1,
                                "point_pack_sec": 0.2,
                                "optix_prepare_sec": 0.3,
                                "optix_query_sec": {"min_sec": 0.4, "median_sec": 0.5, "max_sec": 0.6},
                                "python_postprocess_sec": {"min_sec": 0.01, "median_sec": 0.02, "max_sec": 0.03},
                                "validation_sec": {"min_sec": 0.0, "median_sec": 0.0, "max_sec": 0.0},
                                "optix_close_sec": 0.04,
                            },
                            "result": {"threshold_reached_count": 9, "matches_oracle": True},
                        },
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "hausdorff_distance",
                                    "path_name": "directed_threshold_prepared",
                                    "claim_scope": "prepared OptiX fixed-radius threshold traversal",
                                    "non_claim": "not exact distance",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": ["python3", "script.py", "--output-json", "docs/reports/goal762_test_prepared_decision_tmp.json"],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["artifact_status"], "ok")
            self.assertEqual(row["warm_query_median_sec"], 0.5)
            self.assertEqual(row["postprocess_median_sec"], 0.02)
            self.assertEqual(row["threshold_reached_count"], 9)
            self.assertTrue(row["matches_oracle"])
            self.assertEqual(row["cloud_contract_status"], "ok")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_graph_visibility_gate_artifact_is_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_graph_visibility_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "output_mode": "summary",
                        "strict_pass": True,
                        "strict_failures": [],
                        "cloud_claim_contract": {
                            "claim_scope": "OptiX ray/triangle any-hit traversal for graph visibility-edge filtering",
                            "non_claim": "not BFS",
                            "required_phase_groups": [
                                "cpu_python_reference",
                                "optix_visibility_anyhit",
                                "strict_pass",
                                "strict_failures",
                            ],
                        },
                        "records": [
                            {"label": "cpu_python_reference", "status": "ok", "sec": 0.1},
                            {
                                "label": "optix_visibility_anyhit",
                                "status": "ok",
                                "sec": 0.2,
                                "parity_vs_cpu_python_reference": True,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "graph_analytics",
                                    "path_name": "graph_visibility_edges_gate",
                                    "claim_scope": "OptiX ray/triangle any-hit traversal",
                                    "non_claim": "not BFS",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": ["python3", "script.py", "--output-json", "docs/reports/goal762_test_graph_visibility_tmp.json"],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(row["warm_query_median_sec"], 0.2)
            self.assertTrue(row["strict_pass"])
            self.assertTrue(row["optix_native_parity"])
            self.assertEqual(row["cloud_contract_status"], "ok")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_graph_visibility_gate_analytic_artifact_is_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        artifact_path = ROOT / "docs" / "reports" / "goal762_test_graph_visibility_analytic_tmp.json"
        try:
            artifact_path.write_text(
                json.dumps(
                    {
                        "output_mode": "summary",
                        "validation_mode": "analytic_summary",
                        "chunk_copies": 100,
                        "strict_pass": True,
                        "strict_failures": [],
                        "cloud_claim_contract": {
                            "claim_scope": "OptiX ray/triangle any-hit traversal for graph visibility-edge filtering",
                            "non_claim": "not BFS",
                            "required_phase_groups": [
                                "analytic_expected_visibility_edges",
                                "analytic_expected_bfs",
                                "analytic_expected_triangle_count",
                                "optix_visibility_anyhit",
                                "optix_native_graph_ray_bfs",
                                "optix_native_graph_ray_triangle_count",
                                "strict_pass",
                                "strict_failures",
                            ],
                        },
                        "records": [
                            {"label": "analytic_expected_visibility_edges", "status": "ok", "sec": 0.0},
                            {
                                "label": "optix_visibility_anyhit",
                                "status": "ok",
                                "sec": 0.2,
                                "parity_vs_analytic_expected": True,
                            },
                            {"label": "analytic_expected_bfs", "status": "ok", "sec": 0.0},
                            {
                                "label": "optix_native_graph_ray_bfs",
                                "status": "ok",
                                "sec": 0.3,
                                "parity_vs_analytic_expected": True,
                            },
                            {"label": "analytic_expected_triangle_count", "status": "ok", "sec": 0.0},
                            {
                                "label": "optix_native_graph_ray_triangle_count",
                                "status": "ok",
                                "sec": 0.4,
                                "parity_vs_analytic_expected": True,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "graph_analytics",
                                    "path_name": "graph_visibility_edges_gate",
                                    "claim_scope": "OptiX ray/triangle any-hit traversal",
                                    "non_claim": "not BFS",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": [
                                            "python3",
                                            "script.py",
                                            "--output-json",
                                            "docs/reports/goal762_test_graph_visibility_analytic_tmp.json",
                                        ],
                                    },
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            row = payload["rows"][0]
            self.assertEqual(row["validation_mode"], "analytic_summary")
            self.assertEqual(row["chunk_copies"], 100)
            self.assertTrue(row["analytic_reference_present"])
            self.assertTrue(row["optix_native_parity"])
            self.assertEqual(row["cloud_contract_status"], "ok")
        finally:
            artifact_path.unlink(missing_ok=True)

    def test_segment_pair_rows_and_polygon_overlap_artifacts_are_extracted(self) -> None:
        module = __import__("scripts.goal762_rtx_cloud_artifact_report", fromlist=["analyze"])
        pair_rows_path = ROOT / "docs" / "reports" / "goal762_test_pair_rows_tmp.json"
        polygon_path = ROOT / "docs" / "reports" / "goal762_test_polygon_overlap_tmp.json"
        try:
            pair_rows_path.write_text(
                json.dumps(
                    {
                        "output_capacity": 1024,
                        "strict_pass": True,
                        "strict_failures": [],
                        "cloud_claim_contract": {
                            "claim_scope": "native bounded pair rows",
                            "non_claim": "not unbounded rows",
                            "required_phase_groups": [
                                "records",
                                "row_digest",
                                "emitted_count",
                                "copied_count",
                                "overflowed",
                                "strict_pass",
                                "strict_failures",
                            ],
                        },
                        "records": [
                            {"label": "cpu_python_reference", "status": "ok", "sec": 0.1},
                            {
                                "label": "optix_native_bounded",
                                "status": "ok",
                                "sec": 0.2,
                                "row_digest": {"row_count": 2, "sha256": "abc"},
                                "emitted_count": 2,
                                "copied_count": 2,
                                "overflowed": 0,
                                "parity_vs_cpu_python_reference": True,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            polygon_path.write_text(
                json.dumps(
                    {
                        "mode": "optix",
                        "parity_vs_cpu": True,
                        "cloud_claim_contract": {
                            "claim_scope": "OptiX native-assisted LSI/PIP candidate discovery",
                            "non_claim": "not full area kernel",
                            "required_phase_groups": [
                                "input_build_sec",
                                "cpu_reference_sec",
                                "optix_candidate_discovery_sec",
                                "cpu_exact_refinement_sec",
                                "parity_vs_cpu",
                                "rt_core_candidate_discovery_active",
                            ],
                        },
                        "phases": {
                            "input_build_sec": 0.1,
                            "cpu_reference_sec": 0.2,
                            "optix_candidate_discovery_sec": 0.3,
                            "cpu_exact_refinement_sec": 0.4,
                        },
                        "optix_metadata": {"rt_core_candidate_discovery_active": True},
                    }
                ),
                encoding="utf-8",
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary = Path(tmpdir) / "summary.json"
                summary.write_text(
                    json.dumps(
                        {
                            "status": "ok",
                            "dry_run": False,
                            "results": [
                                {
                                    "app": "segment_polygon_anyhit_rows",
                                    "path_name": "segment_polygon_anyhit_rows_native_bounded_gate",
                                    "claim_scope": "native bounded rows",
                                    "non_claim": "not default",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": ["python3", "script.py", "--output-json", "docs/reports/goal762_test_pair_rows_tmp.json"],
                                    },
                                },
                                {
                                    "app": "polygon_pair_overlap_area_rows",
                                    "path_name": "polygon_pair_overlap_optix_native_assisted_phase_gate",
                                    "claim_scope": "candidate discovery",
                                    "non_claim": "not full area",
                                    "baseline_review_contract": _baseline_contract(),
                                    "result": {
                                        "status": "ok",
                                        "returncode": 0,
                                        "command": ["python3", "script.py", "--output-json", "docs/reports/goal762_test_polygon_overlap_tmp.json"],
                                    },
                                },
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                payload = module.analyze(summary)
            self.assertEqual(payload["status"], "ok")
            pair_row = payload["rows"][0]
            polygon_row = payload["rows"][1]
            self.assertEqual(pair_row["emitted_count"], 2)
            self.assertEqual(pair_row["overflowed"], 0)
            self.assertEqual(pair_row["cloud_contract_status"], "ok")
            self.assertEqual(polygon_row["warm_query_median_sec"], 0.3)
            self.assertEqual(polygon_row["postprocess_median_sec"], 0.4)
            self.assertTrue(polygon_row["rt_core_candidate_discovery_active"])
            self.assertEqual(polygon_row["cloud_contract_status"], "ok")
        finally:
            pair_rows_path.unlink(missing_ok=True)
            polygon_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
