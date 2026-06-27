import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from examples.current.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact,
)
from scripts import v3_phoenix_aabb_prepare_reuse_pod_runner as runner


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_pod_runner.py"


def fake_payload(*, backend: str, scale: int, prepare: float, query: float, collect: float, wall: float):
    return {
        "candidate_discovery_backend": backend,
        "dataset": f"jittered_grid_{scale}",
        "discovery_warmup_count": 3,
        "discovery_repeat_count": 50,
        "aabb_candidate_pair_count": scale,
        "valid_count": scale,
        "matches_cpu_reference": True,
        "complete_candidate_coverage": True,
        "overflowed": False,
        "prepared_session_residency": {
            "query_reuse_observed_within_payload": True,
        },
        "prepared_execution_session_runner_used": backend in {"embree", "optix"},
        "productized_execution_path": (
            "prepared_execution_session_runner" if backend in {"embree", "optix"} else None
        ),
        "prepared_execution_session_runner_metadata": {
            "runtime_executed_count": 50,
            "cache_hit_count": 49,
        },
        "run_phases": {
            "prepare_aabb_index_2d_sec": prepare,
            "emit_aabb_intersection_pair_rows_2d_median_sec": query,
            "emit_aabb_intersection_pair_rows_2d_total_sec": query * 50,
            "collect_k_bounded_rows_sec": collect,
            "python_exact_refinement_sec": 0.01,
            "generic_aabb_broadphase_wall_sec": wall,
        },
        "phoenix_v3_aabb_prepare_reuse_runner": {
            "indexed_aabb_count": scale,
            "query_aabb_count": scale,
            "runner_wall_sec": wall + collect + 0.01,
        },
    }


class FakePreparedAabbIndex:
    def __init__(self) -> None:
        self.intersection_calls = 0
        self.last_row_capacity = None
        self.closed = False

    def intersection_rows(self, query_boxes, query_ids, *, row_capacity=None):
        self.intersection_calls += 1
        self.last_row_capacity = row_capacity
        return tuple((int(query_id), int(query_id) - 10_000) for query_id in query_ids)

    def prepared_query_cache_stats(self) -> dict[str, int]:
        return {
            "range_intersection_hits": max(0, self.intersection_calls - 1),
            "range_intersection_misses": 1,
            "range_intersection_entries": 1,
            "native_range_intersection_hits": max(0, self.intersection_calls - 1),
            "native_range_intersection_misses": 1,
            "native_range_intersection_entries": 1,
        }

    def close(self) -> None:
        self.closed = True


class V3PhoenixAabbPrepareReusePodRunnerTest(unittest.TestCase):
    def test_parse_backends_normalizes_aliases(self):
        self.assertEqual(runner.parse_backends("embree,optix,optix"), ("embree", "optix"))
        self.assertEqual(runner.parse_backends("cpu_python_reference,cuda-optix"), ("cpu", "optix"))
        with self.assertRaises(ValueError):
            runner.parse_backends("vulkan")

    def test_fake_material_wall_win_is_pending_review_not_m7(self):
        args = SimpleNamespace(
            dataset="jittered_grid",
            grid_count=32768,
            resolution=None,
            witness_capacity=None,
            discovery_row_capacity=None,
            warmup=3,
            repeat=50,
            backends="embree,optix",
            require_rt_hardware=False,
        )
        summary = runner.build_summary(
            args=args,
            backend_payloads={
                "embree": fake_payload(
                    backend="embree",
                    scale=32768,
                    prepare=0.20,
                    query=0.010,
                    collect=0.006,
                    wall=0.75,
                ),
                "optix": fake_payload(
                    backend="optix",
                    scale=32768,
                    prepare=0.05,
                    query=0.002,
                    collect=0.004,
                    wall=0.20,
                ),
            },
            environment={"hardware_gate": {"status": "fail"}},
            run_errors={},
        )
        self.assertEqual(summary["status"], "aabb_prepare_reuse_pod_evidence_pending_2ai_not_m7")
        self.assertFalse(summary["m7_promotion_authorized"])
        self.assertTrue(summary["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(summary["failed_checks"], [])
        self.assertGreater(
            summary["comparisons"]["optix_over_embree_cold_plus_collect_wall_speedup"],
            runner.MATERIAL_WALL_SPEEDUP_FLOOR,
        )

    def test_fake_hot_win_without_wall_win_is_not_pending_review(self):
        args = SimpleNamespace(
            dataset="jittered_grid",
            grid_count=32768,
            resolution=None,
            witness_capacity=None,
            discovery_row_capacity=None,
            warmup=3,
            repeat=50,
            backends="embree,optix",
            require_rt_hardware=False,
        )
        summary = runner.build_summary(
            args=args,
            backend_payloads={
                "embree": fake_payload(
                    backend="embree",
                    scale=32768,
                    prepare=0.05,
                    query=0.010,
                    collect=0.004,
                    wall=0.15,
                ),
                "optix": fake_payload(
                    backend="optix",
                    scale=32768,
                    prepare=0.20,
                    query=0.002,
                    collect=0.004,
                    wall=0.30,
                ),
            },
            environment={"hardware_gate": {"status": "fail"}},
            run_errors={},
        )
        self.assertEqual(summary["status"], "aabb_prepare_reuse_pod_evidence_collected_not_m7")
        self.assertFalse(summary["m7_reopen_candidate_pending_2ai_review"])
        self.assertIn("material_optix_wall_win_after_prepare_reuse", summary["failed_checks"])

    def test_cpu_local_smoke_writes_non_m7_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dataset",
                    "grid",
                    "--grid-count",
                    "3",
                    "--backends",
                    "cpu",
                    "--warmup",
                    "0",
                    "--repeat",
                    "1",
                    "--witness-capacity",
                    "3",
                    "--discovery-row-capacity",
                    "8",
                    "--allow-non-serious-local-smoke",
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
            self.assertEqual(summary["status"], "aabb_prepare_reuse_pod_evidence_collected_not_m7")
            self.assertFalse(summary["m7_promotion_authorized"])
            self.assertFalse(summary["checks"]["serious_fixture_scale"])
            self.assertIn("Contact Manifold is only the harness", readme_path.read_text(encoding="utf-8"))

    def test_contact_aabb_route_uses_productized_prepared_session_runner(self):
        prepared = FakePreparedAabbIndex()
        prepare_calls = {"count": 0}

        def fake_prepare(*args, **kwargs):
            prepare_calls["count"] += 1
            self.assertEqual(kwargs["backend"], "optix")
            return prepared

        with patch("rtdsl.aabb_index.prepare_aabb_index_2d", side_effect=fake_prepare):
            payload = contact.aabb_broadphase_collect_k_payload(
                dataset="grid",
                grid_count=3,
                witness_capacity=3,
                discovery_backend="optix",
                discovery_row_capacity=16,
                discovery_warmup_count=2,
                discovery_repeat_count=3,
            )

        runner_metadata = payload["prepared_execution_session_runner_metadata"]

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertTrue(payload["prepared_execution_session_runner_used"])
        self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(prepared.intersection_calls, 5)
        self.assertEqual(prepared.last_row_capacity, 16)
        self.assertTrue(prepared.closed)
        self.assertEqual(payload["run_phases"]["emit_aabb_intersection_pair_rows_2d_measured_count"], 3)
        self.assertEqual(runner_metadata["runtime_executed_count"], 3)
        self.assertEqual(runner_metadata["cache_hit_count"], 2)
        self.assertEqual(runner_metadata["row_contract"], "generic_prepared_aabb_index_query_2d_native_query_handle")
        self.assertEqual(runner_metadata["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertFalse(runner_metadata["release_authorized"])
        self.assertFalse(runner_metadata["public_speedup_claim_authorized"])
        self.assertFalse(runner_metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(
            runner_metadata["first_run"]["productized_execution_path"],
            "prepared_execution_session_runner",
        )
        self.assertFalse(runner_metadata["first_run"]["prepared_session"]["cache_hit"])
        self.assertTrue(runner_metadata["last_run"]["prepared_session"]["cache_hit"])


if __name__ == "__main__":
    unittest.main()
