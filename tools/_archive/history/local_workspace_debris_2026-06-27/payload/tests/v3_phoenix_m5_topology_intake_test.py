import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


class V3PhoenixM5TopologyIntakeTest(unittest.TestCase):
    def make_artifact_dir(self) -> tempfile.TemporaryDirectory:
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        write_json(
            root / "optix_hardware_gate.json",
            {
                "status": "pass",
                "checks": {"rt_hardware_name_present": True},
            },
        )
        write_json(root / "gpu_env_gate.json", {"status": "pass"})
        write_json(
            root / "m5_local_graph_gate.json",
            {"status": "m5_local_topology_graphs_ready_pod_and_author_evidence_pending"},
        )
        (root / "rayjoin_query_exec_status.txt").write_text("missing\n", encoding="utf-8")
        write_json(
            root / "m5_pip_point_location_parity_filtered_100k" / "summary.json",
            {
                "schema": "rtdl.goal4373.rayjoin_cdb_point_location_compare.v1",
                "protocol": {
                    "point_count": 100000,
                    "parity_filter_requested": True,
                    "optix_repeats": 1000,
                    "embree_repeats": 1000,
                    "row_materialization_in_timed_path": False,
                },
                "parity_filter": {
                    "status": "pass",
                    "accepted_count": 100000,
                    "rejected_count": 1,
                },
                "correctness_sample": {
                    "sample_count": 100000,
                    "mismatch_count_first_10_materialized": 0,
                },
                "rayjoin_rt": None,
                "rtdl": {
                    "optix": {
                        "counts_stable": True,
                        "positive_face_count": 7,
                        "native_traversal_median_sec": 0.001,
                    },
                    "embree": {
                        "counts_stable": True,
                        "positive_face_count": 7,
                        "native_traversal_median_sec": 0.01,
                    },
                },
                "comparison": {
                    "rtdl_optix_speedup_vs_rtdl_embree": 10.0,
                    "rtdl_optix_native_traversal_speedup_vs_rtdl_embree": 10.0,
                },
            },
        )
        row_claim_boundary = {
            "full_polygon_overlay_claim_authorized": False,
            "rayjoin_section57_full_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        }
        write_json(
            root / "m5_overlay_active_count_same_contract.json",
            {
                "status": "ok",
                "claim_boundary": row_claim_boundary,
                "comparison": {
                    "same_output_contract": True,
                    "active_counts_match": True,
                    "all_row_materialization_avoided": True,
                    "active_count": 3,
                    "embree_over_optix_timed_median": 5.0,
                },
                "rows": [
                    {
                        "backend": "embree",
                        "output_contract": "overlay_active_pair_dependency_count",
                        "native_traversal_median_sec": 0.01,
                    },
                    {
                        "backend": "optix",
                        "output_contract": "overlay_active_pair_dependency_count",
                        "native_traversal_median_sec": 0.002,
                    },
                ],
            },
        )
        return tmp

    def test_missing_query_exec_is_top_level_blocker_not_failure(self):
        with self.make_artifact_dir() as tmp:
            md_out = Path(tmp) / "summary.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "v3_phoenix_m5_topology_intake.py"),
                    "--artifact-dir",
                    tmp,
                    "--md-out",
                    str(md_out),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["overall_status"], "partial_internal_evidence_author_code_blocked")
            self.assertEqual(payload["status_label"], "internal-author-blocked")
            self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
            self.assertEqual(payload["m5_author_code_comparison_status"], "blocked_query_exec_missing")
            self.assertEqual(payload["overlay_author_comparison_status"], "not_applicable_internal_same_contract_only")
            self.assertFalse(payload["release_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
            self.assertIn("BLOCKED (query_exec missing)", payload["headline"])
            self.assertIn("BLOCKED (query_exec missing)", md_out.read_text(encoding="utf-8"))

    def test_present_query_exec_completes_author_comparison_but_not_release(self):
        with self.make_artifact_dir() as tmp:
            root = Path(tmp)
            (root / "rayjoin_query_exec_status.txt").write_text("present\n", encoding="utf-8")
            summary_path = root / "m5_pip_point_location_parity_filtered_100k" / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["rayjoin_rt"] = {"query_ms": 0.5}
            write_json(summary_path, summary)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "v3_phoenix_m5_topology_intake.py"),
                    "--artifact-dir",
                    tmp,
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["overall_status"], "internal_evidence_with_author_code")
            self.assertEqual(payload["status_label"], "internal-author-complete")
            self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
            self.assertEqual(payload["m5_author_code_comparison_status"], "complete")
            self.assertEqual(payload["query_exec_status"], "present")
            self.assertFalse(payload["release_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
