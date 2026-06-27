import unittest
from unittest.mock import patch

from examples.current.research_benchmarks.librts_spatial_index import (
    rtdl_librts_spatial_index_benchmark_app as librts,
)


class _FakePreparedAabbCount:
    def __init__(self) -> None:
        self.count_calls = 0
        self.closed = False

    def count(self, *, point_queries=(), box_queries=(), operation: str):
        self.count_calls += 1
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": "embree",
            "prepared": True,
            "operation": operation,
            "counts": {
                "point_contains": 1,
                "range_contains": 1,
                "range_intersects": 1,
            },
            "candidate_checks": None,
            "query_counts": {
                "point_queries": len(tuple(point_queries)),
                "box_queries": len(tuple(box_queries)),
            },
            "index": {"indexed_boxes": 1, "native_index": "fake_embree_aabb"},
            "run_phases": {"query_aabb_index_2d_sec": 0.001},
        }

    def prepared_query_cache_stats(self) -> dict[str, int]:
        return {
            "count_point_query_hits": max(0, self.count_calls - 1),
            "count_point_query_misses": 1,
            "count_box_query_hits": max(0, self.count_calls - 1),
            "count_box_query_misses": 1,
        }

    def close(self) -> None:
        self.closed = True


class _FakeRunnerResult:
    def __init__(self, *, retained: bool = True) -> None:
        output = {
            "counts": {
                "point_contains": 1,
                "range_contains": 1,
                "range_intersects": 1,
            }
        }
        self.output = (output, output, output) if retained else output
        self.retained = retained

    def to_metadata(self) -> dict[str, object]:
        seconds = (0.003, 0.001, 0.002) if self.retained else (0.002,)
        return {
            "runtime_executed": True,
            "prepared_session": {"cache_hit": False},
            "measured_repeat_count": len(seconds),
            "measured_repeat_seconds": seconds,
            "repeated_prepared_session_execution": self.retained,
            "single_cache_lookup_for_measured_repeats": True,
            "single_report_after_measured_repeats": True,
            "row_contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            "count_contract": "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
            "primitive_family": "aabb_index_query_2d_native_query_handle",
            "prepared_query_mode": "optix_prepared_query_set",
            "set_a_probe_candidate": False,
            "set_b_control_candidate": True,
            "prepared_execution_report": {
                "phase_timings": [
                    {"phase": "prepare", "seconds": 0.25},
                    {"phase": "executor", "seconds": 0.001},
                ]
            },
        }


class V3PhoenixLibRtsAabbCountRunnerTest(unittest.TestCase):
    def test_embree_aabb_count_route_uses_productized_runner(self) -> None:
        prepared = _FakePreparedAabbCount()
        prepare_calls = {"count": 0}

        def fake_prepare(*args, **kwargs):
            prepare_calls["count"] += 1
            self.assertEqual(kwargs["backend"], "embree")
            return prepared

        fixture = librts.LibRTSFixture(
            dataset="runner_contract",
            boxes=(librts.Box2D(0.0, 0.0, 1.0, 1.0),),
            point_queries=(librts.Point2D(0.5, 0.5),),
            box_queries=(librts.Box2D(0.25, 0.25, 0.75, 0.75),),
            seed=7,
            paper_equivalent_dataset=False,
        )

        with patch("rtdsl.aabb_index.prepare_aabb_index_2d", side_effect=fake_prepare):
            payload = librts.run_embree_aabb_counts(
                fixture,
                "all",
                query_repeat=3,
                warmup=1,
                validate_reference=True,
            )

        metadata = payload["prepared_execution_session_runner_metadata"]
        last_run = metadata["last_run"]

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertTrue(payload["prepared_execution_session_runner_used"])
        self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
        self.assertFalse(payload["set_a_probe_candidate"])
        self.assertTrue(payload["set_b_control_candidate"])
        self.assertEqual(payload["primitive_contract"], "generic_prepared_aabb_index_query_2d_count")
        self.assertEqual(payload["counts"], {"point_contains": 1, "range_contains": 1, "range_intersects": 1})
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(prepared.count_calls, 4)
        self.assertTrue(prepared.closed)
        self.assertEqual(payload["repeat_protocol"]["measured_run_count"], 3)
        self.assertEqual(metadata["runtime_executed_count"], 1)
        self.assertEqual(metadata["cache_hit_count"], 0)
        self.assertEqual(metadata["measured_repeat_count"], 3)
        self.assertTrue(metadata["repeated_execution"])
        self.assertTrue(metadata["single_cache_lookup_for_measured_repeats"])
        self.assertTrue(metadata["single_report_after_measured_repeats"])
        self.assertEqual(metadata["count_contract"], "generic_prepared_aabb_index_query_2d_count")
        self.assertEqual(metadata["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertFalse(metadata["set_a_probe_candidate"])
        self.assertTrue(metadata["set_b_control_candidate"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(last_run["release_authorized"])
        self.assertFalse(last_run["public_speedup_claim_authorized"])
        self.assertFalse(last_run["broad_v3_faster_than_v2_claim_authorized"])

    def test_optix_aabb_count_route_uses_productized_prepared_query_set_runner(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_runner(**kwargs):
            calls.append(dict(kwargs))
            return _FakeRunnerResult()

        fixture = librts.LibRTSFixture(
            dataset="runner_contract",
            boxes=(librts.Box2D(0.0, 0.0, 1.0, 1.0),),
            point_queries=(librts.Point2D(0.5, 0.5),),
            box_queries=(librts.Box2D(0.25, 0.25, 0.75, 0.75),),
            seed=7,
            paper_equivalent_dataset=False,
        )

        with patch(
            "rtdsl.run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session",
            side_effect=fake_runner,
        ):
            payload = librts.run_optix_aabb_counts(
                fixture,
                "all",
                query_repeat=3,
                warmup=1,
                validate_reference=False,
            )

        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call["operation"], "all")
        self.assertEqual(call["partner"], "none")
        self.assertEqual(call["device"], "cuda:0")
        self.assertEqual(call["warmup_count"], 1)
        self.assertEqual(call["measured_repeat_count"], 3)
        self.assertTrue(call["retain_repeat_outputs"])

        metadata = payload["prepared_execution_session_runner_metadata"]
        self.assertIsNone(payload["matches_cpu_reference"])
        self.assertTrue(payload["prepared_execution_session_runner_used"])
        self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
        self.assertFalse(payload["set_a_probe_candidate"])
        self.assertTrue(payload["set_b_control_candidate"])
        self.assertEqual(
            payload["primitive_contract"],
            "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
        )
        self.assertEqual(payload["counts"], {"point_contains": 1, "range_contains": 1, "range_intersects": 1})
        self.assertEqual(payload["run_phases"]["scene_prepare_sec"], 0.25)
        self.assertEqual(payload["run_phases"]["query_median_sec"], 0.002)
        self.assertEqual(payload["run_phases"]["query_total_sec"], 0.006)
        self.assertEqual(payload["repeat_protocol"]["measured_run_count"], 3)
        self.assertTrue(payload["multi_operation_native_used"])
        self.assertTrue(payload["prepared_queries"])
        self.assertEqual(metadata["runtime_executed_count"], 1)
        self.assertEqual(metadata["cache_hit_count"], 0)
        self.assertEqual(metadata["measured_repeat_count"], 3)
        self.assertTrue(metadata["repeated_execution"])
        self.assertEqual(
            metadata["count_contract"],
            "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
        )
        self.assertEqual(metadata["prepared_query_mode"], "optix_prepared_query_set")
        self.assertFalse(metadata["set_a_probe_candidate"])
        self.assertTrue(metadata["set_b_control_candidate"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])

    def test_optix_aabb_count_single_repeat_avoids_retaining_runner_outputs(self) -> None:
        calls: list[dict[str, object]] = []

        def fake_runner(**kwargs):
            calls.append(dict(kwargs))
            return _FakeRunnerResult(retained=False)

        fixture = librts.LibRTSFixture(
            dataset="runner_contract",
            boxes=(librts.Box2D(0.0, 0.0, 1.0, 1.0),),
            point_queries=(librts.Point2D(0.5, 0.5),),
            box_queries=(librts.Box2D(0.25, 0.25, 0.75, 0.75),),
            seed=7,
            paper_equivalent_dataset=False,
        )

        with patch(
            "rtdsl.run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session",
            side_effect=fake_runner,
        ):
            payload = librts.run_optix_aabb_counts(
                fixture,
                "all",
                query_repeat=1,
                warmup=0,
                validate_reference=False,
            )

        self.assertEqual(len(calls), 1)
        self.assertFalse(calls[0]["retain_repeat_outputs"])
        self.assertEqual(payload["counts"], {"point_contains": 1, "range_contains": 1, "range_intersects": 1})
        self.assertEqual(payload["repeat_protocol"]["measured_run_count"], 1)
        self.assertEqual(payload["run_phases"]["query_median_sec"], 0.002)
        self.assertTrue(payload["prepared_execution_session_runner_used"])
        self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
        self.assertFalse(payload["set_a_probe_candidate"])
        self.assertTrue(payload["set_b_control_candidate"])


if __name__ == "__main__":
    unittest.main()
