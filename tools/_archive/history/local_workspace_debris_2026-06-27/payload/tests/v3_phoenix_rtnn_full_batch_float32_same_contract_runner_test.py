import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from scripts import v3_phoenix_rtnn_full_batch_float32_same_contract_runner as runner


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_full_batch_float32_same_contract_runner.py"


def fake_optix_payload(*, query_sec: float, summary: dict[str, object]) -> dict[str, object]:
    return {
        "ok": True,
        "result_mode": runner.RTDL_RESULT_MODE,
        "query_count": 262_144,
        "search_count": 262_144,
        "query_batch_size": 262_144,
        "batch_count": 1,
        "elapsed_median_sec": query_sec,
        "elapsed_runs_sec": [query_sec, query_sec * 1.01, query_sec * 0.99],
        "input_load_sec": 0.10,
        "input_pack_sec": 0.05,
        "execution_prepare_sec": 0.20,
        "point_column_source": "npz",
        "point_column_file": "points.csv.npz",
        "ranked_aggregate_summary": summary,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": runner.RTDL_RESULT_MODE,
            "precision": "float32",
        },
        "phoenix_v3_runner_wall_sec": query_sec + 0.40,
    }


def fake_cupy_payload(*, query_sec: float, summary: dict[str, object]) -> dict[str, object]:
    return {
        "ok": True,
        "mode": "cupy_cuda_core_grid_exact_ranked_summary_3d",
        "query_count": 262_144,
        "search_count": 262_144,
        "elapsed_sec": query_sec,
        "elapsed_runs_sec": [query_sec, query_sec * 1.01, query_sec * 0.99],
        "input_load_sec": 0.08,
        "grid_prepare_sec": 0.12,
        "point_column_source": "npz",
        "point_column_file": "points.csv.npz",
        "grid_cell_count": 125_000,
        "occupied_cell_count": 95_000,
        "summary": summary,
        "contract": {
            "family": "fixed_radius_neighbors_3d",
            "mode": "ranked-summary",
            "uniform_grid_cuda_core": True,
        },
        "phoenix_v3_runner_wall_sec": query_sec + 0.30,
    }


class V3PhoenixRtnnFullBatchFloat32SameContractRunnerTest(unittest.TestCase):
    def test_parse_routes_normalizes_aliases(self):
        self.assertEqual(runner.parse_routes("rtdl,cupy,cupy"), ("optix", "cupy_grid"))
        self.assertEqual(runner.parse_routes("cuda-optix,cuda-core"), ("optix", "cupy_grid"))
        with self.assertRaises(ValueError):
            runner.parse_routes("embree")

    def test_fake_material_speedup_is_pending_review_not_m7(self):
        args = SimpleNamespace(
            routes="optix,cupy_grid",
            point_count=262_144,
            distribution="uniform",
            seed=4502,
            radius=0.02,
            k_max=50,
            query_batch_size=None,
            repeat=5,
            require_rt_hardware=False,
            point_column_source="npz",
        )
        summary_row = {
            "row_count": 262_144,
            "bounded_neighbor_count": 1_234_567,
            "nearest_id_checksum": 987_654_321,
            "kth_id_checksum": 123_456_789,
            "sum_distance": 42_000.0,
        }
        summary = runner.build_summary(
            args=args,
            route_payloads={
                "optix": fake_optix_payload(query_sec=0.10, summary=summary_row),
                "cupy_grid": fake_cupy_payload(query_sec=0.80, summary=summary_row),
            },
            environment={"hardware_gate": {"status": "fail"}},
            run_errors={},
            point_manifest={"path": "points.csv", "point_count": 262_144},
        )
        self.assertEqual(
            summary["status"],
            "rtnn_full_batch_float32_same_contract_pod_evidence_pending_2ai_not_m7",
        )
        self.assertFalse(summary["m7_promotion_authorized"])
        self.assertTrue(summary["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(summary["failed_checks"], [])
        self.assertTrue(summary["checks"]["point_column_source_recorded"])
        self.assertEqual(summary["parameters"]["point_column_source"], "npz")
        self.assertGreater(
            summary["comparisons"]["rtdl_optix_over_cupy_grid_hot_speedup"],
            runner.MATERIAL_SPEEDUP_FLOOR,
        )

    def test_fake_signature_mismatch_is_not_pending_review(self):
        args = SimpleNamespace(
            routes="optix,cupy_grid",
            point_count=262_144,
            distribution="uniform",
            seed=4502,
            radius=0.02,
            k_max=50,
            query_batch_size=None,
            repeat=5,
            require_rt_hardware=False,
            point_column_source="npz",
        )
        optix_summary = {
            "row_count": 262_144,
            "bounded_neighbor_count": 1_234_567,
            "nearest_id_checksum": 987_654_321,
            "kth_id_checksum": 123_456_789,
            "sum_distance": 42_000.0,
        }
        reference_summary = {**optix_summary, "kth_id_checksum": 123_456_790}
        summary = runner.build_summary(
            args=args,
            route_payloads={
                "optix": fake_optix_payload(query_sec=0.10, summary=optix_summary),
                "cupy_grid": fake_cupy_payload(query_sec=0.80, summary=reference_summary),
            },
            environment={"hardware_gate": {"status": "fail"}},
            run_errors={},
            point_manifest={"path": "points.csv", "point_count": 262_144},
        )
        self.assertEqual(
            summary["status"],
            "rtnn_full_batch_float32_same_contract_evidence_collected_not_m7",
        )
        self.assertFalse(summary["m7_reopen_candidate_pending_2ai_review"])
        self.assertIn("same_contract_signature_match", summary["failed_checks"])
        self.assertNotIn("point_column_source_recorded", summary["failed_checks"])

    def test_dry_run_writes_plan_not_m7_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--point-count",
                    "64",
                    "--routes",
                    "optix,cupy_grid",
                    "--point-column-source",
                    "npz",
                    "--output-dir",
                    tmp,
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            summary_path = Path(tmp) / "summary.json"
            readme_path = Path(tmp) / "README.md"
            self.assertTrue(summary_path.exists())
            self.assertTrue(readme_path.exists())
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                summary["status"],
                "rtnn_full_batch_float32_same_contract_runner_plan_not_m7",
            )
            self.assertFalse(summary["m7_promotion_authorized"])
            self.assertFalse(summary["public_speedup_claim_authorized"])
            self.assertEqual(summary["parameters"]["point_column_source"], "npz")
            self.assertEqual(summary["point_manifest"]["point_column_source"], "npz")
            self.assertTrue(summary["point_manifest"]["column_source_path"].endswith(".npz"))
            self.assertIn("RTNN is only the", readme_path.read_text(encoding="utf-8"))

    def test_small_npz_point_column_source_is_materialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            args = SimpleNamespace(
                point_file=None,
                point_count=8,
                distribution="uniform",
                seed=4502,
                point_column_source="npz",
            )
            manifest = runner.ensure_point_file(args, out_dir=out_dir)
            npz_path = Path(manifest["column_source_path"])
            self.assertTrue(npz_path.exists())
            self.assertEqual(manifest["point_column_source"], "npz")
            self.assertEqual(manifest["column_source_manifest"]["point_count"], 8)
            self.assertEqual(manifest["column_source_manifest"]["format"], "rtnn_npz_xyz_columns_v1")

    def test_run_route_passes_column_source_manifest_to_real_routes(self):
        args = SimpleNamespace(
            point_count=16,
            radius=0.02,
            k_max=50,
            query_batch_size=None,
            repeat=1,
            point_column_source="npz",
            max_grid_cells=2_000_000,
        )
        point_file = Path("points.csv")
        point_manifest = {"column_source_path": "points.csv.npz"}
        captured: dict[str, object] = {}
        original_optix = runner.rtnn_runner.run_rtdl_batched_3d_neighbors
        original_cupy = runner.rtnn_runner.run_cupy_grid_3d_ranked_summary

        def fake_optix(ns):
            captured["optix"] = ns
            return fake_optix_payload(query_sec=0.1, summary={"row_count": 16})

        def fake_cupy(ns):
            captured["cupy_grid"] = ns
            return fake_cupy_payload(query_sec=0.2, summary={"row_count": 16})

        try:
            runner.rtnn_runner.run_rtdl_batched_3d_neighbors = fake_optix
            runner.rtnn_runner.run_cupy_grid_3d_ranked_summary = fake_cupy
            runner.run_route(
                args=args,
                route="optix",
                point_file=point_file,
                point_manifest=point_manifest,
            )
            runner.run_route(
                args=args,
                route="cupy_grid",
                point_file=point_file,
                point_manifest=point_manifest,
            )
        finally:
            runner.rtnn_runner.run_rtdl_batched_3d_neighbors = original_optix
            runner.rtnn_runner.run_cupy_grid_3d_ranked_summary = original_cupy

        self.assertEqual(captured["optix"].point_column_source, "npz")
        self.assertEqual(captured["optix"].point_column_file, "points.csv.npz")
        self.assertEqual(captured["cupy_grid"].point_column_source, "npz")
        self.assertEqual(captured["cupy_grid"].point_column_file, "points.csv.npz")


if __name__ == "__main__":
    unittest.main()
