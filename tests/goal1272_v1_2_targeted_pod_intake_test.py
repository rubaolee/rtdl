from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal1272_v1_2_targeted_pod_intake import build_intake
from scripts.goal1272_v1_2_targeted_pod_intake import to_markdown


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _db_payload(sec: float) -> dict[str, object]:
    return {
        "results": [
            {
                "prepared_session_warm_query_sec": {"median_sec": sec},
                "db_review_observation": {
                    "row_materializing_operation_count": 0,
                },
                "reported_native_db_phase_totals_sec": {
                    "bitset_copyback_sec": 0.01,
                    "counter_status": "exported",
                    "emitted_count": 12,
                    "exact_filter_sec": 0.02,
                    "output_pack_sec": 0.03,
                    "raw_candidate_count": 34,
                    "traversal_sec": 0.04,
                },
            }
        ]
    }


class Goal1272V12TargetedPodIntakeTest(unittest.TestCase):
    def test_missing_artifacts_keep_intake_invalid_and_non_claim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = build_intake(Path(tmp))
        self.assertFalse(payload["valid"])
        self.assertEqual(payload["environment_status"], "env_probe_missing")
        self.assertEqual(payload["execution_status"], "environment_blocked")
        self.assertFalse(payload["public_wording_authorized"])
        self.assertGreater(len(payload["missing_artifacts"]), 0)

    def test_synthetic_complete_artifacts_classify_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "rtdl_pod_env.json", {"nvcc_exists": True, "optix_header_exists": True})
            _write(root / "make_build_optix.status.json", {"exit_code": 0, "status": "ok"})
            _write(root / "goal1267_status_summary.json", {"status_count": 20, "failed_count": 0, "failed_labels": []})
            _write(root / "goal1267_graph_ray_pack_metadata.json", {"artifact_count": 4})
            for copies in (30000, 60000):
                _write(root / f"graph_embree_visibility_{copies}.json", {"graph_phase_totals_sec": {"query_visibility_pair_rows_sec": 3.0}})
                _write(
                    root / f"graph_optix_visibility_{copies}.json",
                    {
                        "records": [
                            {
                                "label": "optix_visibility_anyhit",
                                "sec": 6.0,
                                "section_run_phases": {"query_anyhit_count_sec": 0.5},
                            }
                        ]
                    },
                )
                _write(
                    root / f"graph_optix_visibility_repeats_{copies}.json",
                    {
                        "app": "graph_analytics",
                        "sections": {
                            "visibility_edges": {
                                "visibility_query_repeats": 100,
                                "ray_pack_mode": "numpy_packed_rays",
                                "blocker_pack_mode": "numpy_packed_triangles",
                                "run_phases": {
                                    "scene_prepare_sec": 1.2,
                                    "ray_prepare_sec": 0.1,
                                    "query_anyhit_count_first_sec": 0.003,
                                    "query_anyhit_count_mean_sec": 0.002,
                                    "query_anyhit_count_min_sec": 0.001,
                                },
                            }
                        },
                    },
                )
            for copies in (100000, 300000):
                _write(root / f"db_embree_sales_risk_{copies}.json", _db_payload(2.0))
                _write(root / f"db_optix_sales_risk_{copies}.json", _db_payload(1.0))
            for copies in (40000, 80000, 160000):
                _write(root / f"polygon_pair_embree_{copies}.json", {"run_phases": {"rt_candidate_discovery_sec": 2.0}})
                _write(
                    root / f"polygon_pair_optix_{copies}.json",
                    {
                        "parity_vs_cpu": True,
                        "phases": {"optix_candidate_discovery_sec": 1.0},
                        "candidate_diagnostics": {
                            "candidate_count_matches_expected": False,
                            "candidate_count_delta_vs_expected": -2,
                            "positive_pair_count_matches_expected": True,
                            "expected_positive_pair_count": 4,
                            "optix_positive_pair_count": 4,
                        },
                    },
                )
            for copies in (4096, 8192):
                _write(root / f"polygon_jaccard_embree_{copies}.json", {"run_phases": {"rt_candidate_discovery_sec": 1.0}})
                _write(
                    root / f"polygon_jaccard_optix_{copies}_chunk_1024.json",
                    {
                        "parity_vs_cpu": True,
                        "chunk_copies": 1024,
                        "chunk_policy": {"policy": "public_safe", "public_safe": True},
                        "phases": {"optix_candidate_discovery_sec": 2.0},
                        "candidate_diagnostics": {"positive_pair_count_matches_expected": True},
                    },
                )
            payload = build_intake(root)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["environment_status"], "env_probe_ok")
        self.assertEqual(payload["build_status"], "build_ok")
        self.assertEqual(payload["execution_status"], "artifact_complete")
        self.assertEqual(payload["decisions"]["graph_analytics"], "optix_still_slower_with_reason")
        self.assertEqual(payload["decisions"]["graph_prepared_repeat"], "optix_improved")
        self.assertEqual(payload["decisions"]["database_analytics"], "optix_improved")
        self.assertEqual(payload["decisions"]["polygon_pair_overlap_area_rows"], "optix_improved")
        self.assertEqual(payload["decisions"]["polygon_set_jaccard"], "optix_still_slower_with_reason")
        self.assertEqual(payload["database_analytics"][0]["optix_native_counter_status"], "exported")
        self.assertTrue(payload["polygon_pair_overlap_area_rows"][0]["positive_pair_count_matches_expected"])
        self.assertFalse(payload["public_wording_authorized"])

    def test_markdown_preserves_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = to_markdown(build_intake(Path(tmp)))
        self.assertIn("Public wording authorized: `False`", text)
        self.assertIn("does not authorize public RTX speedup wording", text)
        self.assertIn("3-AI consensus", text)
        self.assertIn("separate reviewed packet", text)


if __name__ == "__main__":
    unittest.main()
