import unittest
from unittest.mock import patch

from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_STATUS
from rtdsl.prepared_execution import PREPARED_EXECUTION_SESSION_RUNNER_VERSION
from rtdsl.prepared_execution import PreparedExecutionSessionTask
from rtdsl.prepared_execution import audit_prepared_execution_continuation_metadata
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata
from rtdsl.prepared_execution import make_prepared_input_fingerprint
from rtdsl.prepared_execution import run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session
from rtdsl.prepared_execution import run_aabb_index_query_2d_count_prepared_session
from rtdsl.prepared_execution import run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session
from rtdsl.prepared_execution import run_aabb_index_query_2d_range_intersection_prepared_session
from rtdsl.prepared_execution import run_fixed_radius_count_threshold_3d_self_query_prepared_session
from rtdsl.prepared_execution import run_fixed_radius_ranked_summary_3d_prepared_session
from rtdsl.prepared_execution import run_fixed_radius_threshold_reached_count_2d_prepared_session
from rtdsl.prepared_execution import run_grouped_vector_sum_2d_prepared_session
from rtdsl.prepared_execution import run_point_location_topology_stream_prepared_session
from rtdsl.prepared_execution import run_prepared_execution_session
from rtdsl.prepared_execution import run_ray_triangle_weighted_summary_device_output_stream_prepared_session
from rtdsl.prepared_execution import run_radius_graph_component_union_3d_prepared_session
from rtdsl.prepared_execution import run_radius_graph_component_signature_3d_prepared_session
from rtdsl.prepared_execution import run_repeated_prepared_execution_session
from rtdsl.prepared_session_residency import ExplicitPreparedSessionCache


class _PreparedPrimitive:
    def __init__(self, factor: int) -> None:
        self.factor = factor
        self.calls = 0

    def run(self, value: int) -> int:
        self.calls += 1
        return value * self.factor


class _FakePreparedFixedRadiusSelfQuery:
    def __init__(self, search_count: int) -> None:
        self.search_count = int(search_count)
        self.self_query_calls = 0

    def write_device_count_threshold_self_columns(
        self,
        *,
        radius: float,
        threshold: int,
        query_ids_out,
        neighbor_counts_out,
        threshold_flags_out,
    ):
        self.self_query_calls += 1
        for index in range(self.search_count):
            query_ids_out[index] = index
            neighbor_counts_out[index] = int(threshold) + index
            threshold_flags_out[index] = 1
        return {
            "metadata": {
                "direct_device_handoff_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_accelerated": True,
                "host_query_point_repack_avoided": True,
                "host_query_point_upload_avoided": True,
            }
        }


class _FakePreparedAabbNativeQueryHandle:
    def __init__(self) -> None:
        self.intersection_calls = 0
        self.last_row_capacity = None

    def intersection_rows(self, query_boxes, query_ids, *, row_capacity=None):
        self.intersection_calls += 1
        self.last_row_capacity = row_capacity
        return tuple((int(query_id), 100 + index) for index, query_id in enumerate(query_ids))

    def prepared_query_cache_stats(self) -> dict[str, int]:
        return {
            "range_intersection_hits": max(0, self.intersection_calls - 1),
            "range_intersection_misses": 1,
            "native_range_intersection_hits": max(0, self.intersection_calls - 1),
            "native_range_intersection_misses": 1,
        }


class _FakePreparedAabbNativeCountHandle:
    def __init__(self) -> None:
        self.count_calls = 0
        self.last_operation = None
        self.last_point_query_count = None
        self.last_box_query_count = None

    def count(self, *, point_queries=(), box_queries=(), operation: str):
        self.count_calls += 1
        self.last_operation = operation
        self.last_point_query_count = len(tuple(point_queries))
        self.last_box_query_count = len(tuple(box_queries))
        return {
            "primitive": "AABB_INDEX_QUERY_2D",
            "contract": "generic_prepared_aabb_index_query_2d",
            "backend": "optix",
            "prepared": True,
            "operation": operation,
            "counts": {
                "point_contains": 3,
                "range_contains": 5,
                "range_intersects": 7,
            },
            "candidate_checks": None,
            "query_counts": {
                "point_queries": self.last_point_query_count,
                "box_queries": self.last_box_query_count,
            },
            "run_phases": {"query_aabb_index_2d_sec": 0.001},
        }

    def prepared_query_cache_stats(self) -> dict[str, int]:
        return {
            "count_point_query_hits": max(0, self.count_calls - 1),
            "count_point_query_misses": 1,
            "count_box_query_hits": max(0, self.count_calls - 1),
            "count_box_query_misses": 1,
        }


class _FakeOptixPreparedQuerySetSession:
    def __init__(self) -> None:
        self.index = self
        self.point_queries = object()
        self.box_queries = object()
        self.count_set_calls = 0
        self.count_single_calls = 0
        self.closed = False

    def count_prepared_query_set(self, *, point_queries=None, box_queries=None):
        self.count_set_calls += 1
        if point_queries is not self.point_queries:
            raise AssertionError("point query handle was not reused")
        if box_queries is not self.box_queries:
            raise AssertionError("box query handle was not reused")
        return {
            "point_contains": 11,
            "range_contains": 13,
            "range_intersects": 17,
        }

    def count_prepared_queries(self, queries, *, operation: str | None = None):
        self.count_single_calls += 1
        if operation == "point_contains" and queries is not self.point_queries:
            raise AssertionError("point query handle was not reused")
        if operation != "point_contains" and queries is not self.box_queries:
            raise AssertionError("box query handle was not reused")
        return 19

    def close(self) -> None:
        self.closed = True


class _FakePreparedRadiusGraphComponentSignature:
    def __init__(self) -> None:
        self.signature_calls = 0

    def component_signature(self, *, min_neighbors: int):
        self.signature_calls += 1
        return {
            "columns": {
                "component_size_signature": (2, 1),
                "neighbor_counts": (int(min_neighbors), int(min_neighbors) + 1, 0),
            },
            "metadata": {
                "adapter": "fake_radius_graph_component_signature",
                "continuation_contract": "grouped_stream_component_size_signature_3d",
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "external_host_buffer_exposure_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
                "point_ids_materialized_for_signature": False,
                "core_flags_materialized_for_signature": False,
                "app_specific_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
            },
        }


class _FakePreparedRadiusGraphComponentUnion:
    def __init__(self) -> None:
        self.union_calls = 0

    def component_union(self, *, min_neighbors: int):
        self.union_calls += 1
        return {
            "columns": {
                "point_ids": (0, 1, 2),
                "component_labels": (0, 0, 2),
                "is_core": (1, 1, 0),
                "neighbor_counts": (int(min_neighbors), int(min_neighbors) + 1, 0),
            },
            "metadata": {
                "adapter": "fake_radius_graph_component_union",
                "partner": "numba",
                "partner_reference_contract": (
                    "generic_prepared_optix_numba_grouped_stream_component_labels_3d"
                ),
                "native_engine_row_contract": (
                    "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces"
                ),
                "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query_blocked_ranges",
                "component_union_policy": (
                    "monotonic_atomic_min_from_rt_hit_stream_without_neighbor_index_materialization"
                ),
                "component_label_policy": "positive_root_index_labels_noise_minus_one",
                "boundary_assignment_policy": "single_pass_candidate_root_rebased",
                "boundary_assignment_canonical_policy": "single_pass_candidate_root_rebased",
                "grouped_stream_continuation_pass_count": 2,
                "grouped_union_query_block_size": 128,
                "grouped_union_query_block_count": 2,
                "native_grouped_stream_metadata": {
                    "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query_blocked_ranges",
                    "native_elapsed_sec": 0.002,
                    "boundary_assignment_pass_count": 1,
                },
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "materializes_neighbor_rows": False,
                "materializes_directed_adjacency_stream": False,
                "materializes_bounded_directed_adjacency_chunks": False,
                "external_host_buffer_exposure_authorized": False,
                "v4_embedding_or_external_zero_copy_authorized": False,
                "app_specific_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
            },
        }


class _FakePreparedPointLocationTopologyStream:
    def __init__(self) -> None:
        self.calls = 0

    def run_relation_status_count(self) -> dict[str, object]:
        self.calls += 1
        return {
            "row_count": 7,
            "summary": {
                "output_contract": "point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
                "positive_hit_row_count": 7,
            },
            "phases_sec": {
                "static_shape_pack_sec": 0.001,
                "prepare_static_scene_sec": 0.002,
                "query_pack_sec": 0.003,
                "prepare_query_points_sec": 0.004,
                "prepared_query_sec": 0.010,
            },
            "native_phase_timings": {
                "mode": "relation_status_corrected_scalar_count_executor_run",
                "point_upload": 0.0,
                "candidate_count_pass": 0.001,
                "candidate_write_pass": 0.0,
                "candidate_download": 0.0,
                "exact_refine": 0.0,
                "row_stream_materialized": False,
                "boundary_candidate_row_stream_materialized": False,
                "native_exact_device_scalar_count_produced": True,
            },
            "topology_stream_m3_phase_table": {
                "contract": "topology_stream_m3_phase_table_v1",
                "full_m3_phase_table_complete": True,
            },
            "topology_stream_prepared_handle": {
                "contract": "topology_stream_prepared_handle_v1",
                "query_stream_prepared": True,
                "query_stream_residency": (
                    "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor"
                ),
            },
            "metadata": {
                "app_specific_native_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_authorized": False,
            },
        }


class _FakePreparedAggregateTreeFusedVectorSum:
    def __init__(self) -> None:
        self.calls = 0

    def sum(self) -> dict[str, object]:
        self.calls += 1
        return {
            "columns": {
                "source_ids": (0, 1),
                "vector_x": (1.0, -1.0),
                "vector_y": (0.5, -0.5),
                "visited_counts": (3, 4),
                "aggregate_counts": (2, 2),
                "exact_counts": (1, 1),
            },
            "metadata": {
                "contract": "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
                "partner": "numba_cuda",
                "source_count": 2,
                "target_count": 2,
                "tree_node_count": 3,
                "prepared_lookup_columns_resident": True,
                "source_columns_reused": True,
                "target_columns_reused": True,
                "aggregate_tree_columns_resident": True,
                "output_columns_reused": True,
                "setup_seconds_excluded_from_hot_path": True,
                "frontier_rows_emitted": False,
                "frontier_rows_materialized_on_host": False,
                "contribution_rows_materialized_on_host": False,
                "count_columns_copied_to_host_for_metadata": True,
                "native_engine_app_specific": False,
                "automatic_partner_selection_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


class _FakePreparedGroupedVectorSum2D:
    def __init__(self) -> None:
        self.calls = 0

    def sum(self) -> dict[str, object]:
        self.calls += 1
        return {
            "columns": {
                "group_ids": (0, 1),
                "sum_x": (3.0, 7.0),
                "sum_y": (4.0, 8.0),
            },
            "metadata": {
                "adapter": "run_grouped_vector_sum_2d_partner_columns_session",
                "partner": "numba",
                "partner_reference_contract": "generic_grouped_vector_sum_f64x2",
                "input_contract": "caller_supplied_presegmented_grouped_vector_rows_2d",
                "group_count": 2,
                "row_count": 4,
                "v2_5_numba_offset_program_count": 1,
                "v2_5_numba_threads_per_block": 256,
                "v2_5_numba_groups_per_block": 8,
                "v2_5_numba_threads_per_group": 32,
                "v2_5_numba_launch_parallelism_axis": "group_count_warp_per_group_row_parallel",
                "v2_5_numba_rows_per_group_mean": 2.0,
                "v2_5_numba_kernel_strategy": "warp_per_group_tiled",
                "v2_5_numba_tiled_row_parallel_reduction_used": True,
                "v2_5_numba_thread_per_group_serial_loop_used": False,
                "output_columns_reused": True,
                "per_run_neutral_handoff_validation_used": False,
                "native_engine_row_contract": "not_called_partner_continuation_only",
                "direct_device_handoff_authorized": False,
                "app_specific_engine_logic_allowed": False,
                "automatic_partner_selection_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


class _FakePreparedRayTriangleWeightedSummaryDeviceOutput:
    def __init__(self) -> None:
        self.calls = 0

    def run_weighted_summary_device_output_stream(self) -> dict[str, object]:
        self.calls += 1
        return {
            "metadata": {
                "contract": "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1",
                "partner": "cupy",
                "primitive_count": 320000,
                "ray_count": 80000,
                "weighted_hit_sum": 320000,
                "prepared_scene_reused": True,
                "prepared_ray_batch_reused": True,
                "ray_weights_device_resident": True,
                "device_output_stream_validated": True,
                "caller_owned_device_output_scalar": True,
                "output_scalar_device_resident_until_finalize": True,
                "host_scalar_materialized_during_hot_path": False,
                "hot_path_host_materialization": False,
                "m113_graph_capture_claim_authorized": False,
                "automatic_partner_selection_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "whole_app_speedup_claim_authorized": False,
                "public_speedup_claim_authorized": False,
                "broad_v3_faster_than_v2_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
            },
        }


class _FakePreparedFixedRadiusRankedSummary3D:
    def __init__(self) -> None:
        self.calls = 0

    def aggregate(self) -> dict[str, object]:
        self.calls += 1
        return {
            "query_count": 3,
            "bounded_neighbor_count": 11,
            "nearest_id_checksum": 17,
            "kth_id_checksum": 23,
            "sum_distance": 3.25,
            "precision": "float32",
            "query_resident": True,
        }


class _FakePreparedFixedRadiusRankedSummary3DWithoutResidency:
    def __init__(self) -> None:
        self.calls = 0

    def aggregate(self) -> dict[str, object]:
        self.calls += 1
        return {
            "query_count": 3,
            "bounded_neighbor_count": 11,
            "nearest_id_checksum": 17,
            "kth_id_checksum": 23,
            "sum_distance": 3.25,
            "precision": "float32",
        }


class _FakePreparedFixedRadiusThreshold2D:
    def __init__(self, *, residency: bool = True, rows_materialized: bool = False) -> None:
        self.calls = 0
        self.residency = bool(residency)
        self.rows_materialized = bool(rows_materialized)

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int) -> dict[str, object]:
        self.calls += 1
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "backend": "optix",
            "prepared": True,
            "scene_reusable": True,
            "radius": float(radius),
            "threshold": int(threshold),
            "threshold_reached_count": len(tuple(query_points)),
            "result_layout": "aggregate_threshold_reached_count",
            "native_scalar_count_used": not self.rows_materialized,
            "threshold_summary_rows_materialized_on_host": self.rows_materialized,
            "hot_path_host_materialization": self.rows_materialized,
            "prepared_search_structure_resident_between_rtdl_phases": self.residency,
            "query_points_device_resident_between_rtdl_phases": False,
            "internal_device_residency_between_rtdl_phases": self.residency,
            "internal_residency_scope": (
                "prepared_search_structure_only_query_points_not_device_resident"
                if self.residency
                else "not_reported_by_backend"
            ),
            "run_phases": {
                "scene_prepare_sec": 0.001,
                "scene_prepare_sec_this_batch": 0.0,
                "query_fixed_radius_threshold_reached_count_sec": 0.002,
            },
        }


class V3PhoenixPreparedExecutionSessionRunnerTest(unittest.TestCase):
    def assertContinuationCoreReady(
        self,
        metadata: dict[str, object],
        *,
        expected_contract: str,
        expected_set_a: bool = True,
        expected_set_b: bool = False,
    ) -> None:
        audit = audit_prepared_execution_continuation_metadata(metadata)
        self.assertEqual(audit["status"], "accept_step4_continuation_core_ready")
        self.assertTrue(audit["step4_continuation_core_ready"])
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["continuation_contract"], expected_contract)
        self.assertIs(audit["set_a_probe_candidate"], expected_set_a)
        self.assertIs(audit["set_b_control_candidate"], expected_set_b)
        self.assertEqual(audit["missing_step4_fields"], ())
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])
        self.assertFalse(audit["all_app_rerun_authorized"])

    def assertContinuationCoreBlocked(
        self,
        metadata: dict[str, object],
        *,
        missing_step3: tuple[str, ...],
        missing_step4: tuple[str, ...],
        expected_set_a: bool,
        expected_set_b: bool,
    ) -> None:
        step3_audit = audit_prepared_execution_session_metadata(metadata)
        step4_audit = audit_prepared_execution_continuation_metadata(metadata)

        self.assertEqual(step3_audit["status"], "incomplete_step3_audit")
        self.assertFalse(step3_audit["step3_residency_default_ready"])
        self.assertIs(step3_audit["set_a_probe_candidate"], expected_set_a)
        self.assertIs(step3_audit["set_b_control_candidate"], expected_set_b)
        for field in missing_step3:
            self.assertIn(field, step3_audit["missing_step3_fields"])
        self.assertEqual(step4_audit["status"], "incomplete_step4_continuation_audit")
        self.assertFalse(step4_audit["step4_continuation_core_ready"])
        self.assertFalse(step4_audit["all_app_rerun_authorized"])
        self.assertFalse(step4_audit["release_authorized"])
        self.assertIs(step4_audit["set_a_probe_candidate"], expected_set_a)
        self.assertIs(step4_audit["set_b_control_candidate"], expected_set_b)
        for field in missing_step4:
            self.assertIn(field, step4_audit["missing_step4_fields"])

    def test_prepared_input_fingerprint_hashes_full_large_sequence(self):
        first = make_prepared_input_fingerprint(["x" * 4096 + "a"])
        second = make_prepared_input_fingerprint(["x" * 4096 + "b"])

        self.assertEqual(first["fingerprint_shape"], "sequence_full_repr_stream_hash")
        self.assertEqual(first["count"], 1)
        self.assertEqual(first["digest_algorithm"], "sha256")
        self.assertNotIn("repr", first)
        self.assertNotEqual(first["digest"], second["digest"])

    def test_non_topology_stream_set_a_bypasses_topology_bridge_gate(self):
        metadata = {
            "productized_execution_path": "prepared_execution_session_runner",
            "set_a_probe_candidate": True,
            "primitive_family": "fixed_radius_ranked_summary_3d",
            "runtime_executed": True,
            "runtime_trunk_executes_end_to_end": True,
            "internal_device_residency_between_rtdl_phases": True,
            "hot_path_host_materialization": False,
            "measured_repeat_seconds": (0.001, 0.001),
            "output_finalize_sec": 0.0,
            "prepared_execution_report": {"status": "present"},
            "prepared_execution_report_validation": {"status": "accept"},
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        }

        audit = audit_prepared_execution_session_metadata(metadata)

        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertFalse(audit["topology_stream_set_a_candidate"])
        self.assertTrue(audit["topology_stream_m3_bridge_ready"])
        self.assertNotIn(
            "complete_non_authorizing_topology_stream_m3_bridge",
            audit["missing_step3_fields"],
        )

    def test_runner_executes_explicit_prepared_session_and_records_boundaries(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _PreparedPrimitive:
            prepare_calls["count"] += 1
            return _PreparedPrimitive(3)

        task = PreparedExecutionSessionTask(
            workflow_name="phoenix_m1_fixed_radius_session_smoke",
            primitive="fixed_radius_count_threshold_self_query",
            backend="optix",
            partner="cupy",
            input_fingerprints={"points": "abc123"},
            parameters={"radius": 0.02, "threshold": 8},
            device="cuda:0",
            cache=cache,
            prepare_session=prepare,
            warmup_count=2,
            run_prepared=lambda prepared: prepared.run(7),
            validate_output=lambda output: {"matches_oracle": output == 21},
            notes=("generic runner smoke; no app-specific engine logic",),
        )

        result = run_prepared_execution_session(task)
        metadata = result.to_metadata()

        self.assertEqual(result.output, 21)
        self.assertFalse(result.cache_hit)
        self.assertTrue(result.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(metadata["schema"], PREPARED_EXECUTION_SESSION_RUNNER_VERSION)
        self.assertEqual(metadata["status"], PREPARED_EXECUTION_SESSION_RUNNER_STATUS)
        self.assertEqual(metadata["explicit_backend"], "optix")
        self.assertEqual(metadata["explicit_partner"], "cupy")
        self.assertTrue(metadata["explicit_partner_choice_required"])
        self.assertTrue(metadata["validation_passed"])
        self.assertEqual(metadata["prepared_execution_report_validation"]["status"], "accept")
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertFalse(
            metadata["prepared_execution_report"]["automatic_partner_selection_allowed"]
        )
        self.assertFalse(metadata["prepared_session"]["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["prepared_session"]["public_speedup_claim_authorized"])
        self.assertIn("miss", [row["event"] for row in metadata["prepared_session"]["cache_event_log"]])
        self.assertIn("put", [row["event"] for row in metadata["prepared_session"]["cache_event_log"]])
        audit = result.runtime_audit()
        self.assertEqual(audit["status"], "incomplete_step3_audit")
        self.assertTrue(audit["productized_runner_used"])
        self.assertTrue(audit["runtime_executed"])
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertFalse(audit["step3_residency_default_ready"])
        self.assertIn("runtime_trunk_executes_end_to_end", audit["missing_step3_fields"])
        self.assertIn("internal_device_residency_between_rtdl_phases", audit["missing_step3_fields"])
        self.assertIn("hot_path_host_materialization", audit["missing_step3_fields"])

    def test_runner_reuses_explicit_cache_on_second_run(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _PreparedPrimitive:
            prepare_calls["count"] += 1
            return _PreparedPrimitive(5)

        task = PreparedExecutionSessionTask(
            workflow_name="phoenix_m1_cache_reuse_smoke",
            primitive="aabb_index_query_2d_native_query_handle",
            backend="optix",
            partner="none",
            input_fingerprints={"boxes": "box-sha", "queries": "query-sha"},
            parameters={"k": 16},
            cache=cache,
            prepare_session=prepare,
            run_prepared=lambda prepared: prepared.run(4),
        )

        first = run_prepared_execution_session(task)
        second = run_prepared_execution_session(task)

        self.assertEqual(first.output, 20)
        self.assertEqual(second.output, 20)
        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertIn(
            "hit",
            [row["event"] for row in second.to_metadata()["prepared_session"]["cache_event_log"]],
        )
        cache_load_phase = [
            phase
            for phase in second.to_metadata()["prepared_execution_report"]["phase_timings"]
            if phase["phase"] == "cache_load"
        ][0]
        self.assertGreaterEqual(cache_load_phase["seconds"], 0.0)

    def test_repeated_runner_executes_measured_repeats_inside_one_session_call(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _PreparedPrimitive:
            prepare_calls["count"] += 1
            return _PreparedPrimitive(2)

        task = PreparedExecutionSessionTask(
            workflow_name="phoenix_repeated_prepared_session_smoke",
            primitive="fixed_radius_count_threshold_self_query",
            backend="optix",
            partner="cupy",
            input_fingerprints={"points": "abc123"},
            parameters={"radius": 0.02, "threshold": 8},
            device="cuda:0",
            cache=cache,
            prepare_session=prepare,
            warmup_count=1,
            run_prepared=lambda prepared: prepared.run(11),
            validate_output=lambda output: {"matches_oracle": output == 22},
        )

        result = run_repeated_prepared_execution_session(
            task,
            measured_repeat_count=4,
            validate_each_repeat=True,
        )
        metadata = result.to_metadata()
        executor_phase = [
            phase
            for phase in metadata["prepared_execution_report"]["phase_timings"]
            if phase["phase"] == "executor"
        ][0]

        self.assertEqual(result.output, 22)
        self.assertFalse(result.cache_hit)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(result.prepared_value.calls, 5)
        self.assertTrue(metadata["runtime_executed"])
        self.assertTrue(metadata["repeated_prepared_session_execution"])
        self.assertEqual(metadata["measured_repeat_count"], 4)
        self.assertEqual(len(metadata["measured_repeat_seconds"]), 4)
        self.assertEqual(len(executor_phase["repeat_seconds"]), 4)
        self.assertEqual(executor_phase["role"], "median_of_repeated_explicit_prepared_operations")
        self.assertTrue(metadata["single_cache_lookup_for_measured_repeats"])
        self.assertTrue(metadata["single_report_after_measured_repeats"])
        self.assertTrue(metadata["per_iteration_task_reconstruction_avoided"])
        self.assertTrue(metadata["per_iteration_fingerprint_recompute_avoided"])
        self.assertTrue(metadata["validate_each_repeat"])
        self.assertFalse(metadata["repeat_outputs_retained"])
        self.assertTrue(metadata["validation_passed"])
        self.assertEqual(metadata["prepared_execution_report_validation"]["status"], "accept")
        self.assertEqual(
            [row["event"] for row in metadata["prepared_session"]["cache_event_log"]],
            ["miss", "put"],
        )
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])

    def test_repeated_runner_rejects_zero_measured_repeat_count(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        task = PreparedExecutionSessionTask(
            workflow_name="phoenix_repeated_prepared_session_bad_repeat",
            primitive="fixed_radius_count_threshold_self_query",
            backend="optix",
            partner="cupy",
            input_fingerprints={"points": "abc123"},
            cache=cache,
            prepare_session=lambda: _PreparedPrimitive(2),
            run_prepared=lambda prepared: prepared.run(11),
        )

        with self.assertRaisesRegex(ValueError, "measured_repeat_count must be positive"):
            run_repeated_prepared_execution_session(task, measured_repeat_count=0)

    def test_runner_records_native_prepare_timing_separately_from_outer_wrapper(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        class _PreparedWithNativePrepare(_PreparedPrimitive):
            scene_prepare_sec = 0.0125

        task = PreparedExecutionSessionTask(
            workflow_name="phoenix_native_prepare_metric_smoke",
            primitive="fixed_radius_count_threshold_self_query",
            backend="optix",
            partner="cupy",
            input_fingerprints={"points": "abc123"},
            parameters={"radius": 0.02, "threshold": 8},
            device="cuda:0",
            cache=cache,
            prepare_session=lambda: _PreparedWithNativePrepare(2),
            run_prepared=lambda prepared: prepared.run(11),
        )

        result = run_repeated_prepared_execution_session(task, measured_repeat_count=1)
        metadata = result.to_metadata()

        self.assertEqual(metadata["native_prepare_sec"], 0.0125)
        self.assertEqual(
            metadata["native_prepare_seconds_source"],
            "prepared_value.scene_prepare_sec",
        )
        self.assertEqual(metadata["legacy_aligned_prepare_sec"], 0.0125)
        self.assertTrue(metadata["legacy_aligned_prepare_metric_available"])
        self.assertGreaterEqual(metadata["outer_prepare_or_cache_sec"], 0.0)
        self.assertGreaterEqual(metadata["outer_prepare_sec"], 0.0)
        self.assertEqual(metadata["outer_cache_load_sec"], 0.0)

    def test_point_location_topology_stream_helper_routes_generic_family_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedPointLocationTopologyStream:
            prepare_calls["count"] += 1
            return _FakePreparedPointLocationTopologyStream()

        result = run_point_location_topology_stream_prepared_session(
            query_stream_fingerprint={"kind": "fixture_points", "count": 100},
            static_scene_fingerprint={"kind": "fixture_shapes", "count": 12},
            output_contract="point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
            query_count=100,
            shape_count=12,
            backend="optix",
            partner="none",
            cache=cache,
            prepare_session=prepare,
            run_topology_stream=lambda prepared: prepared.run_relation_status_count(),
            validate_output=lambda output: {"matches_oracle": output["row_count"] == 7},
            warmup_count=1,
            measured_repeat_count=3,
        )
        metadata = result.to_metadata()
        audit = result.runtime_audit()

        self.assertEqual(result.output["row_count"], 7)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(result.prepared_value.calls, 4)
        self.assertTrue(metadata["runtime_executed"])
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertEqual(metadata["primitive_family"], "point_location_topology_stream")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "step2_runtime_trunk_generalization_probe")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "point_location_topology_stream_relation_status_scalar_count",
        )
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertEqual(metadata["native_phase_host_download_seconds"], 0.0)
        self.assertEqual(
            metadata["query_stream_residency"],
            "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor",
        )
        self.assertEqual(
            metadata["topology_stream_prepared_handle_contract"],
            "topology_stream_prepared_handle_v1",
        )
        self.assertEqual(metadata["topology_stream_m3_phase_table_contract"], "topology_stream_m3_phase_table_v1")
        self.assertEqual(
            metadata["prepared_execution_to_topology_stream_m3_bridge_contract"],
            "prepared_execution_to_topology_stream_m3_bridge_v1",
        )
        self.assertEqual(
            metadata["prepared_execution_to_topology_stream_m3_bridge_status"],
            "complete_non_authorizing_m3_bridge",
        )
        self.assertTrue(metadata["prepared_execution_to_topology_stream_m3_bridge_required"])
        self.assertTrue(metadata["topology_stream_m3_phase_table_complete"])
        self.assertEqual(metadata["topology_stream_m3_missing_phases_for_public_row"], ())
        self.assertEqual(
            metadata["topology_stream_m3_phase_table"]["contract"],
            "topology_stream_m3_phase_table_v1",
        )
        self.assertEqual(
            metadata["topology_stream_prepared_handle"]["generic_capability"],
            "point_location_topology_stream",
        )
        self.assertFalse(metadata["topology_stream_m3_bridge_public_row_authorized"])
        self.assertFalse(metadata["topology_stream_m3_bridge_m7_promotion_authorized"])
        self.assertAlmostEqual(
            metadata["topology_stream_m3_phase_seconds"]["static_scene_prepare_sec"],
            0.003,
        )
        self.assertAlmostEqual(
            metadata["topology_stream_m3_phase_seconds"]["query_stream_prepare_sec"],
            0.007,
        )
        self.assertAlmostEqual(metadata["topology_stream_m3_phase_seconds"]["rt_traversal_sec"], 0.001)
        self.assertAlmostEqual(
            metadata["topology_stream_m3_phase_seconds"]["host_return_or_scalar_materialization_sec"],
            0.0,
        )
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertIs(metadata["true_zero_copy_claim_authorized"], False)
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertTrue(metadata["focused_material_gain_required_before_all_app"])
        self.assertEqual(metadata["measured_repeat_count"], 3)
        self.assertTrue(metadata["validation_passed"])
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertTrue(audit["topology_stream_set_a_candidate"])
        self.assertTrue(audit["topology_stream_m3_bridge_contract_ok"])
        self.assertTrue(audit["topology_stream_m3_bridge_complete"])
        self.assertTrue(audit["topology_stream_m3_bridge_non_authorizing"])
        self.assertTrue(audit["topology_stream_m3_bridge_ready"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="point_to_shape_positive_hit_count_relation_status_corrected_executor_validated",
        )

        negative_cases = (
            (
                "partial_phase_table",
                {
                    "topology_stream_m3_phase_table_complete": False,
                    "topology_stream_m3_missing_phases_for_public_row": (
                        "topology_continuation_sec",
                    ),
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": False,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bad_bridge_contract",
                {
                    "prepared_execution_to_topology_stream_m3_bridge_contract": "bad_contract",
                },
                {
                    "topology_stream_m3_bridge_contract_ok": False,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bad_bridge_status",
                {
                    "prepared_execution_to_topology_stream_m3_bridge_status": (
                        "partial_non_authorizing_m3_bridge"
                    ),
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": False,
                    "topology_stream_m3_bridge_non_authorizing": True,
                },
            ),
            (
                "bridge_public_row_authorized",
                {
                    "topology_stream_m3_bridge_public_row_authorized": True,
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": False,
                },
            ),
            (
                "bridge_m7_authorized",
                {
                    "topology_stream_m3_bridge_m7_promotion_authorized": True,
                },
                {
                    "topology_stream_m3_bridge_contract_ok": True,
                    "topology_stream_m3_bridge_complete": True,
                    "topology_stream_m3_bridge_non_authorizing": False,
                },
            ),
        )
        for label, changes, expected_audit_fields in negative_cases:
            with self.subTest(label=label):
                broken_metadata = dict(metadata)
                broken_metadata.update(changes)
                broken_audit = audit_prepared_execution_session_metadata(broken_metadata)
                for field, expected_value in expected_audit_fields.items():
                    self.assertIs(broken_audit[field], expected_value)
                self.assertEqual(broken_audit["status"], "incomplete_step3_audit")
                self.assertFalse(broken_audit["topology_stream_m3_bridge_ready"])
                self.assertIn(
                    "complete_non_authorizing_topology_stream_m3_bridge",
                    broken_audit["missing_step3_fields"],
                )

    def test_point_location_topology_stream_helper_rejects_invalid_contract_shape(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "output_contract is required"):
            run_point_location_topology_stream_prepared_session(
                query_stream_fingerprint="points",
                static_scene_fingerprint="shapes",
                output_contract="",
                query_count=1,
                partner="none",
                cache=cache,
                prepare_session=lambda: _FakePreparedPointLocationTopologyStream(),
                run_topology_stream=lambda prepared: prepared.run_relation_status_count(),
            )

        with self.assertRaisesRegex(ValueError, "query_count must be positive"):
            run_point_location_topology_stream_prepared_session(
                query_stream_fingerprint="points",
                static_scene_fingerprint="shapes",
                output_contract="point_to_shape_positive_hit_count",
                query_count=0,
                partner="none",
                cache=cache,
                prepare_session=lambda: _FakePreparedPointLocationTopologyStream(),
                run_topology_stream=lambda prepared: prepared.run_relation_status_count(),
            )

    def test_runner_rejects_app_shaped_primitive_names(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        task = PreparedExecutionSessionTask(
            workflow_name="bad_app_shaped_runner",
            primitive="rt_dbscan_component_union",
            backend="optix",
            partner="cupy",
            input_fingerprints={"points": "abc123"},
            cache=cache,
            prepare_session=lambda: _PreparedPrimitive(1),
            run_prepared=lambda prepared: prepared.run(1),
        )

        with self.assertRaisesRegex(ValueError, "app-shaped term"):
            run_prepared_execution_session(task)

    def test_runner_rejects_automatic_partner(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "explicit partner"):
            PreparedExecutionSessionTask(
                workflow_name="bad_auto_partner",
                primitive="fixed_radius_count_threshold_self_query",
                backend="optix",
                partner="automatic",
                input_fingerprints={"points": "abc123"},
                cache=cache,
                prepare_session=lambda: _PreparedPrimitive(1),
                run_prepared=lambda prepared: prepared.run(1),
            )

    def test_fixed_radius_self_query_helper_routes_real_generic_primitive_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}
        sync_calls = {"count": 0}

        def prepare() -> _FakePreparedFixedRadiusSelfQuery:
            prepare_calls["count"] += 1
            return _FakePreparedFixedRadiusSelfQuery(search_count=3)

        def fake_runtime(partner: str):
            self.assertEqual(partner, "fake")
            return {
                "name": "fake",
                "sync": lambda: sync_calls.__setitem__("count", sync_calls["count"] + 1),
            }

        output_columns = {
            "query_ids": [0, 0, 0],
            "neighbor_counts": [0, 0, 0],
            "threshold_flags": [0, 0, 0],
        }

        with patch("rtdsl.partner_adapters._partner_module", side_effect=fake_runtime):
            first = run_fixed_radius_count_threshold_3d_self_query_prepared_session(
                search_points=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)],
                radius=1.25,
                threshold=4,
                partner="fake",
                cache=cache,
                output_columns=output_columns,
                prepare_session=prepare,
                validate_output=lambda output: {
                    "adapter_ok": output["metadata"]["adapter"]
                    == "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
                    "device_columns_ok": output["metadata"]["app_count_host_materialization"] is False,
                },
                device="cuda:contract",
            )
            second = run_fixed_radius_count_threshold_3d_self_query_prepared_session(
                search_points=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (2.0, 0.0, 0.0)],
                radius=1.25,
                threshold=4,
                partner="fake",
                cache=cache,
                output_columns=output_columns,
                prepare_session=prepare,
                device="cuda:contract",
            )

        first_meta = first.to_metadata()
        output_meta = first.output["metadata"]

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertTrue(first.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(sync_calls["count"], 2)
        self.assertEqual(first.prepared_value.self_query_calls, 2)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["schema"], PREPARED_EXECUTION_SESSION_RUNNER_VERSION)
        self.assertEqual(first_meta["status"], PREPARED_EXECUTION_SESSION_RUNNER_STATUS)
        self.assertEqual(first_meta["workflow_name"], "fixed_radius_count_threshold_3d_self_query_prepared_session")
        self.assertEqual(first_meta["primitive"], "fixed_radius_count_threshold_self_query")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "fake")
        self.assertTrue(first_meta["set_a_probe_candidate"])
        self.assertNotIn("set_b_control_candidate", first_meta)
        self.assertEqual(first_meta["primitive_family"], "fixed_radius_count_threshold_self_query")
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertContinuationCoreBlocked(
            first_meta,
            missing_step3=(
                "runtime_trunk_executes_end_to_end",
                "internal_device_residency_between_rtdl_phases",
                "hot_path_host_materialization",
            ),
            missing_step4=(
                "step3_residency_default_ready",
                "runtime_trunk_family",
                "continuation_contract",
                "row_contract",
                "focused_material_gain_required_before_all_app",
            ),
            expected_set_a=True,
            expected_set_b=False,
        )
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(
            output_meta["adapter"],
            "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
        )
        self.assertEqual(output_meta["partner"], "fake")
        self.assertEqual(output_meta["input_contract"], "prepared_native_self_query_device_search_scene")
        self.assertEqual(
            output_meta["native_engine_row_contract"],
            "generic_prepared_fixed_radius_count_threshold_3d_self_device_columns",
        )
        self.assertTrue(output_meta["self_query_prepared_search_buffer_reused"])
        self.assertTrue(output_meta["host_query_point_repack_avoided"])
        self.assertTrue(output_meta["host_query_point_upload_avoided"])
        self.assertFalse(output_meta["true_zero_copy_authorized"])
        self.assertFalse(output_meta["rt_core_speedup_claim_authorized"])
        self.assertFalse(output_meta["whole_app_speedup_claim_authorized"])
        self.assertEqual(output_columns["query_ids"], [0, 1, 2])
        self.assertEqual(output_columns["neighbor_counts"], [4, 5, 6])
        self.assertEqual(output_columns["threshold_flags"], [1, 1, 1])

    def test_fixed_radius_self_query_helper_rejects_invalid_parameters(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "radius must be positive"):
            run_fixed_radius_count_threshold_3d_self_query_prepared_session(
                search_points=[(0.0, 0.0, 0.0)],
                radius=0.0,
                threshold=1,
                partner="fake",
                cache=cache,
                prepare_session=lambda: _FakePreparedFixedRadiusSelfQuery(search_count=1),
            )

        with self.assertRaisesRegex(ValueError, "threshold must be non-negative"):
            run_fixed_radius_count_threshold_3d_self_query_prepared_session(
                search_points=[(0.0, 0.0, 0.0)],
                radius=1.0,
                threshold=-1,
                partner="fake",
                cache=cache,
                prepare_session=lambda: _FakePreparedFixedRadiusSelfQuery(search_count=1),
            )

    def test_fixed_radius_threshold_summary_2d_helper_routes_generic_family_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepared = _FakePreparedFixedRadiusThreshold2D(residency=True)

        result = run_fixed_radius_threshold_reached_count_2d_prepared_session(
            search_points=[(0.0, 0.0), (1.0, 0.0)],
            query_points=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
            radius=0.4,
            threshold=1,
            backend="optix",
            partner="none",
            cache=cache,
            max_radius=0.4,
            search_fingerprint={"kind": "fixture_search", "count": 2},
            query_fingerprint={"kind": "fixture_query", "count": 3},
            prepare_session=lambda: prepared,
            warmup_count=1,
            measured_repeat_count=5,
            require_repeat5_material_probe=True,
            retain_repeat_outputs=True,
        )
        metadata = result.to_metadata()

        self.assertTrue(result.runtime_executed)
        self.assertEqual(prepared.calls, 6)
        self.assertEqual(len(result.output), 5)
        self.assertEqual(metadata["workflow_name"], "fixed_radius_threshold_reached_count_2d_prepared_session")
        self.assertEqual(metadata["primitive"], "fixed_radius_threshold_reached_count_2d")
        self.assertEqual(metadata["primitive_family"], "fixed_radius_threshold_reached_count_2d")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "step2_runtime_trunk_third_family_generalization_probe")
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertEqual(metadata["search_count"], 2)
        self.assertEqual(metadata["query_count"], 3)
        self.assertEqual(metadata["output_threshold_reached_count"], 3)
        self.assertTrue(metadata["native_scalar_count_used"])
        self.assertFalse(metadata["threshold_summary_rows_materialized_on_host"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertTrue(metadata["prepared_search_structure_resident_between_rtdl_phases"])
        self.assertFalse(metadata["query_points_device_resident_between_rtdl_phases"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertEqual(
            metadata["internal_residency_scope"],
            "prepared_search_structure_only_query_points_not_device_resident",
        )
        self.assertTrue(metadata["material_probe_repeat_requirement_met"])
        self.assertTrue(metadata["repeat5_material_probe_candidate"])
        self.assertTrue(metadata["legacy_app_front_door_parity_required"])
        self.assertTrue(metadata["same_contract_embree_baseline_required"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertTrue(metadata["large_input_fingerprint_hot_path_avoided"])
        audit = audit_prepared_execution_session_metadata(metadata)
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="threshold_reached_count_scalar_2d",
        )

    def test_fixed_radius_threshold_summary_2d_helper_blocks_material_flag_without_runtime_residency(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepared = _FakePreparedFixedRadiusThreshold2D(residency=False)

        result = run_fixed_radius_threshold_reached_count_2d_prepared_session(
            search_points=[(0.0, 0.0), (1.0, 0.0)],
            query_points=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
            radius=0.4,
            threshold=1,
            backend="optix",
            partner="none",
            cache=cache,
            prepare_session=lambda: prepared,
            measured_repeat_count=5,
            require_repeat5_material_probe=True,
        )
        metadata = result.to_metadata()

        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["repeat5_material_probe_candidate"])

    def test_fixed_radius_threshold_summary_2d_helper_blocks_end_to_end_when_rows_materialize(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepared = _FakePreparedFixedRadiusThreshold2D(residency=True, rows_materialized=True)

        result = run_fixed_radius_threshold_reached_count_2d_prepared_session(
            search_points=[(0.0, 0.0), (1.0, 0.0)],
            query_points=[(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)],
            radius=0.4,
            threshold=1,
            backend="optix",
            partner="none",
            cache=cache,
            prepare_session=lambda: prepared,
            measured_repeat_count=5,
            require_repeat5_material_probe=True,
        )
        metadata = result.to_metadata()

        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["threshold_summary_rows_materialized_on_host"])
        self.assertTrue(metadata["hot_path_host_materialization"])
        self.assertFalse(metadata["repeat5_material_probe_candidate"])

    def test_fixed_radius_threshold_summary_2d_helper_rejects_invalid_material_probe_repeat(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "repeat5 material-probe"):
            run_fixed_radius_threshold_reached_count_2d_prepared_session(
                search_points=[(0.0, 0.0)],
                query_points=[(0.0, 0.0)],
                radius=0.4,
                threshold=1,
                backend="optix",
                partner="none",
                cache=cache,
                prepare_session=lambda: _FakePreparedFixedRadiusThreshold2D(),
                measured_repeat_count=1,
                require_repeat5_material_probe=True,
            )

    def test_fixed_radius_ranked_summary_helper_routes_generic_family_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedFixedRadiusRankedSummary3D:
            prepare_calls["count"] += 1
            return _FakePreparedFixedRadiusRankedSummary3D()

        result = run_fixed_radius_ranked_summary_3d_prepared_session(
            search_points=[
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "x": 1.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 2.0, "y": 0.0, "z": 0.0},
            ],
            query_points=[
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "x": 1.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 2.0, "y": 0.0, "z": 0.0},
            ],
            radius=0.02,
            k_max=50,
            backend="optix",
            partner="none",
            cache=cache,
            search_fingerprint={"kind": "fixture_search", "count": 3},
            query_fingerprint={"kind": "fixture_query", "count": 3},
            prepared_query_points=True,
            precision="float32",
            prepare_session=prepare,
            run_ranked_summary=lambda prepared: prepared.aggregate(),
            validate_output=lambda output: {
                "query_count_ok": output["query_count"] == 3,
                "integer_signatures_ok": all(
                    key in output
                    for key in (
                        "bounded_neighbor_count",
                        "nearest_id_checksum",
                        "kth_id_checksum",
                    )
                ),
                "distance_summary_ok": output["sum_distance"] > 0.0,
            },
            warmup_count=1,
            measured_repeat_count=50,
            require_repeat50_material_probe=True,
        )
        metadata = result.to_metadata()
        audit = result.runtime_audit()

        self.assertFalse(result.cache_hit)
        self.assertTrue(result.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(result.prepared_value.calls, 51)
        self.assertTrue(metadata["validation_passed"])
        self.assertEqual(metadata["workflow_name"], "fixed_radius_ranked_summary_3d_prepared_session")
        self.assertEqual(metadata["primitive"], "fixed_radius_ranked_summary_3d")
        self.assertEqual(metadata["explicit_backend"], "optix")
        self.assertEqual(metadata["explicit_partner"], "none")
        self.assertTrue(metadata["set_a_probe_candidate"])
        self.assertEqual(metadata["primitive_family"], "fixed_radius_ranked_summary_3d")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "step2_runtime_trunk_generalization_probe")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "fixed_radius_ranked_summary_3d_prepared_query_aggregate",
        )
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["integer_signatures_present"])
        self.assertTrue(metadata["distance_summary_present"])
        self.assertTrue(metadata["output_query_count_matches_requested"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertTrue(metadata["repeat50_material_probe_candidate"])
        self.assertTrue(metadata["material_probe_repeat_requirement_met"])
        self.assertTrue(metadata["hot_cold_runner_wall_must_travel_together"])
        self.assertTrue(metadata["baseline_asymmetry_must_be_disclosed"])
        self.assertFalse(metadata["ranked_summary_rows_materialized_on_host"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertTrue(metadata["large_input_fingerprint_hot_path_avoided"])
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="fixed_radius_ranked_summary_aggregate_3d",
        )

    def test_fixed_radius_ranked_summary_helper_rejects_material_probe_without_repeat50(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "repeat50 material-probe"):
            run_fixed_radius_ranked_summary_3d_prepared_session(
                search_points=[{"id": 0, "x": 0.0, "y": 0.0, "z": 0.0}],
                query_points=[{"id": 0, "x": 0.0, "y": 0.0, "z": 0.0}],
                radius=0.02,
                k_max=50,
                backend="optix",
                partner="none",
                cache=cache,
                prepare_session=lambda: _FakePreparedFixedRadiusRankedSummary3D(),
                run_ranked_summary=lambda prepared: prepared.aggregate(),
                measured_repeat_count=1,
                require_repeat50_material_probe=True,
            )

        with self.assertRaisesRegex(ValueError, "backend must be 'embree' or 'optix'"):
            run_fixed_radius_ranked_summary_3d_prepared_session(
                search_points=[{"id": 0, "x": 0.0, "y": 0.0, "z": 0.0}],
                query_points=[{"id": 0, "x": 0.0, "y": 0.0, "z": 0.0}],
                radius=0.02,
                k_max=50,
                backend="cpu",
                partner="none",
                cache=cache,
                prepare_session=lambda: _FakePreparedFixedRadiusRankedSummary3D(),
                run_ranked_summary=lambda prepared: prepared.aggregate(),
            )

    def test_fixed_radius_ranked_summary_helper_requires_runtime_residency_evidence(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        result = run_fixed_radius_ranked_summary_3d_prepared_session(
            search_points=[
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "x": 1.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 2.0, "y": 0.0, "z": 0.0},
            ],
            query_points=[
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "x": 1.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 2.0, "y": 0.0, "z": 0.0},
            ],
            radius=0.02,
            k_max=50,
            backend="optix",
            partner="none",
            cache=cache,
            search_fingerprint={"kind": "fixture_search", "count": 3},
            query_fingerprint={"kind": "fixture_query", "count": 3},
            prepared_query_points=True,
            precision="float32",
            prepare_session=lambda: _FakePreparedFixedRadiusRankedSummary3DWithoutResidency(),
            run_ranked_summary=lambda prepared: prepared.aggregate(),
            measured_repeat_count=50,
            require_repeat50_material_probe=True,
        )
        metadata = result.to_metadata()

        self.assertTrue(metadata["runtime_executed"])
        self.assertTrue(metadata["integer_signatures_present"])
        self.assertTrue(metadata["distance_summary_present"])
        self.assertFalse(metadata["prepared_queries_resident"])
        self.assertFalse(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["repeat50_material_probe_candidate"])
        self.assertTrue(metadata["material_probe_repeat_requirement_met"])

    def test_aabb_native_query_handle_helper_routes_second_set_a_family_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedAabbNativeQueryHandle:
            prepare_calls["count"] += 1
            return _FakePreparedAabbNativeQueryHandle()

        first = run_aabb_index_query_2d_range_intersection_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0), (2.0, 2.0, 3.0, 3.0)],
            query_boxes=[(0.5, 0.5, 1.5, 1.5), (2.5, 2.5, 3.5, 3.5)],
            indexed_ids=[100, 101],
            query_ids=[7, 9],
            backend="optix",
            partner="none",
            cache=cache,
            row_capacity=8,
            prepare_session=prepare,
            validate_output=lambda output: {
                "contract_ok": output["contract"]
                == "generic_prepared_aabb_index_query_2d_native_query_handle",
                "rows_ok": output["candidate_id_rows"] == ((7, 100), (9, 101)),
                "no_app_logic": output["metadata"]["app_specific_native_engine_logic_allowed"] is False,
            },
            device="cuda:contract",
            warmup_count=1,
        )
        second = run_aabb_index_query_2d_range_intersection_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0), (2.0, 2.0, 3.0, 3.0)],
            query_boxes=[(0.5, 0.5, 1.5, 1.5), (2.5, 2.5, 3.5, 3.5)],
            indexed_ids=[100, 101],
            query_ids=[7, 9],
            backend="optix",
            partner="none",
            cache=cache,
            row_capacity=8,
            prepare_session=prepare,
            device="cuda:contract",
        )

        first_meta = first.to_metadata()
        output_meta = first.output["metadata"]

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertTrue(first.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(first.prepared_value.intersection_calls, 3)
        self.assertEqual(first.prepared_value.last_row_capacity, 8)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["schema"], PREPARED_EXECUTION_SESSION_RUNNER_VERSION)
        self.assertEqual(first_meta["status"], PREPARED_EXECUTION_SESSION_RUNNER_STATUS)
        self.assertEqual(first_meta["workflow_name"], "aabb_index_query_2d_range_intersection_prepared_session")
        self.assertEqual(first_meta["primitive"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "none")
        self.assertFalse(first_meta["set_a_probe_candidate"])
        self.assertTrue(first_meta["set_b_control_candidate"])
        self.assertEqual(first_meta["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(
            first_meta["row_contract"],
            "generic_prepared_aabb_index_query_2d_native_query_handle",
        )
        self.assertContinuationCoreBlocked(
            first_meta,
            missing_step3=(
                "runtime_trunk_executes_end_to_end",
                "internal_device_residency_between_rtdl_phases",
                "hot_path_host_materialization",
            ),
            missing_step4=(
                "step3_residency_default_ready",
                "runtime_trunk_family",
                "continuation_contract",
                "focused_material_gain_required_before_all_app",
            ),
            expected_set_a=False,
            expected_set_b=True,
        )
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(first.output["candidate_id_rows"], ((7, 100), (9, 101)))
        self.assertEqual(first.output["valid_count"], 2)
        self.assertEqual(
            first.output["contract"],
            "generic_prepared_aabb_index_query_2d_native_query_handle",
        )
        self.assertEqual(
            output_meta["adapter"],
            "aabb_index_query_2d_range_intersection_prepared_session",
        )
        self.assertEqual(output_meta["input_contract"], "prepared_native_aabb_index_2d_with_query_boxes")
        self.assertEqual(
            output_meta["native_engine_row_contract"],
            "generic_prepared_aabb_index_query_2d_native_query_handle",
        )
        self.assertTrue(output_meta["native_query_handle_reuse"])
        self.assertFalse(output_meta["app_specific_native_engine_logic_allowed"])
        self.assertFalse(output_meta["automatic_partner_selection_authorized"])
        self.assertFalse(output_meta["true_zero_copy_authorized"])
        self.assertFalse(output_meta["rt_core_speedup_claim_authorized"])
        self.assertFalse(output_meta["whole_app_speedup_claim_authorized"])

    def test_aabb_native_query_handle_helper_rejects_invalid_parameters(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "backend 'embree' or 'optix'"):
            run_aabb_index_query_2d_range_intersection_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                query_boxes=[(0.5, 0.5, 1.5, 1.5)],
                backend="cpu",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeQueryHandle,
            )

    def test_aabb_count_helper_routes_librts_style_count_contract_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedAabbNativeCountHandle:
            prepare_calls["count"] += 1
            return _FakePreparedAabbNativeCountHandle()

        first = run_aabb_index_query_2d_count_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0), (2.0, 2.0, 3.0, 3.0)],
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            indexed_ids=[100, 101],
            operation="all",
            backend="optix",
            partner="none",
            cache=cache,
            prepare_session=prepare,
            validate_output=lambda output: {
                "contract_ok": output["contract"] == "generic_prepared_aabb_index_query_2d_count",
                "counts_ok": output["counts"]
                == {"point_contains": 3, "range_contains": 5, "range_intersects": 7},
                "no_app_logic": output["metadata"]["app_specific_native_engine_logic_allowed"] is False,
            },
            device="cuda:contract",
            warmup_count=1,
            measured_repeat_count=3,
        )
        second = run_aabb_index_query_2d_count_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0), (2.0, 2.0, 3.0, 3.0)],
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            indexed_ids=[100, 101],
            operation="all",
            backend="optix",
            partner="none",
            cache=cache,
            prepare_session=prepare,
            device="cuda:contract",
        )

        first_meta = first.to_metadata()
        output_meta = first.output["metadata"]

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertTrue(first.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(first.prepared_value.count_calls, 5)
        self.assertEqual(first.prepared_value.last_operation, "all")
        self.assertEqual(first.prepared_value.last_point_query_count, 1)
        self.assertEqual(first.prepared_value.last_box_query_count, 1)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["schema"], PREPARED_EXECUTION_SESSION_RUNNER_VERSION)
        self.assertEqual(first_meta["workflow_name"], "aabb_index_query_2d_count_prepared_session")
        self.assertEqual(first_meta["primitive"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "none")
        self.assertFalse(first_meta["set_a_probe_candidate"])
        self.assertTrue(first_meta["set_b_control_candidate"])
        self.assertEqual(first_meta["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(first_meta["row_contract"], "generic_prepared_aabb_index_query_2d_count")
        self.assertEqual(first_meta["count_contract"], "generic_prepared_aabb_index_query_2d_count")
        self.assertTrue(first_meta["repeated_prepared_session_execution"])
        self.assertEqual(first_meta["measured_repeat_count"], 3)
        self.assertContinuationCoreBlocked(
            first_meta,
            missing_step3=(
                "runtime_trunk_executes_end_to_end",
                "internal_device_residency_between_rtdl_phases",
                "hot_path_host_materialization",
            ),
            missing_step4=(
                "step3_residency_default_ready",
                "runtime_trunk_family",
                "continuation_contract",
                "focused_material_gain_required_before_all_app",
            ),
            expected_set_a=False,
            expected_set_b=True,
        )
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(
            first.output["counts"],
            {"point_contains": 3, "range_contains": 5, "range_intersects": 7},
        )
        self.assertEqual(
            first.output["contract"],
            "generic_prepared_aabb_index_query_2d_count",
        )
        self.assertEqual(output_meta["adapter"], "aabb_index_query_2d_count_prepared_session")
        self.assertEqual(
            output_meta["input_contract"],
            "prepared_native_aabb_index_2d_with_point_and_box_queries",
        )
        self.assertEqual(
            output_meta["native_engine_count_contract"],
            "generic_prepared_aabb_index_query_2d_count",
        )
        self.assertTrue(output_meta["native_query_handle_reuse"])
        self.assertFalse(output_meta["app_specific_native_engine_logic_allowed"])
        self.assertFalse(output_meta["automatic_partner_selection_authorized"])
        self.assertFalse(output_meta["true_zero_copy_authorized"])
        self.assertFalse(output_meta["rt_core_speedup_claim_authorized"])
        self.assertFalse(output_meta["whole_app_speedup_claim_authorized"])

    def test_aabb_count_helper_rejects_invalid_parameters(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "backend 'embree' or 'optix'"):
            run_aabb_index_query_2d_count_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                point_queries=[(0.5, 0.5)],
                box_queries=[(0.25, 0.25, 0.75, 0.75)],
                backend="cpu",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeCountHandle,
            )
        with self.assertRaisesRegex(ValueError, "point_contains count requires point_queries"):
            run_aabb_index_query_2d_count_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                box_queries=[(0.25, 0.25, 0.75, 0.75)],
                operation="point_contains",
                backend="embree",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeCountHandle,
            )
        with self.assertRaisesRegex(ValueError, "range count requires box_queries"):
            run_aabb_index_query_2d_count_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                point_queries=[(0.5, 0.5)],
                operation="range_intersects",
                backend="embree",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeCountHandle,
            )

    def test_optix_prepared_query_set_count_helper_preserves_fast_path_shape(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakeOptixPreparedQuerySetSession:
            prepare_calls["count"] += 1
            return _FakeOptixPreparedQuerySetSession()

        first = run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            operation="all",
            partner="none",
            cache=cache,
            prepare_session=prepare,
            validate_output=lambda output: {
                "contract_ok": output["contract"]
                == "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
                "counts_ok": output["counts"]
                == {"point_contains": 11, "range_contains": 13, "range_intersects": 17},
                "native_call_ok": output["prepared_query_set_native_call"]
                == "count_prepared_query_set",
            },
            device="cuda:contract",
            warmup_count=1,
            measured_repeat_count=3,
        )
        second = run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session(
            indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            operation="all",
            partner="none",
            cache=cache,
            prepare_session=prepare,
            device="cuda:contract",
        )

        first_meta = first.to_metadata()
        output_meta = first.output["metadata"]

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(first.prepared_value.count_set_calls, 5)
        self.assertEqual(first.prepared_value.count_single_calls, 0)
        self.assertTrue(first.runtime_executed)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["workflow_name"], "aabb_index_query_2d_optix_prepared_query_set_count_prepared_session")
        self.assertEqual(first_meta["primitive"], "aabb_index_query_2d_native_query_handle")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "none")
        self.assertEqual(first_meta["primitive_family"], "aabb_index_query_2d_native_query_handle")
        self.assertFalse(first_meta["set_a_probe_candidate"])
        self.assertTrue(first_meta["set_b_control_candidate"])
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(
            first_meta["count_contract"],
            "generic_prepared_aabb_index_query_2d_optix_prepared_query_set_count",
        )
        self.assertEqual(first_meta["prepared_query_mode"], "optix_prepared_query_set")
        self.assertTrue(first_meta["repeated_prepared_session_execution"])
        self.assertEqual(first_meta["measured_repeat_count"], 3)
        self.assertContinuationCoreBlocked(
            first_meta,
            missing_step3=(
                "runtime_trunk_executes_end_to_end",
                "internal_device_residency_between_rtdl_phases",
                "hot_path_host_materialization",
            ),
            missing_step4=(
                "step3_residency_default_ready",
                "runtime_trunk_family",
                "continuation_contract",
                "focused_material_gain_required_before_all_app",
            ),
            expected_set_a=False,
            expected_set_b=True,
        )
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(
            first.output["counts"],
            {"point_contains": 11, "range_contains": 13, "range_intersects": 17},
        )
        self.assertEqual(output_meta["adapter"], "aabb_index_query_2d_optix_prepared_query_set_count_prepared_session")
        self.assertTrue(output_meta["prepared_query_set_reuse"])
        self.assertFalse(output_meta["app_specific_native_engine_logic_allowed"])
        self.assertFalse(output_meta["automatic_partner_selection_authorized"])
        self.assertFalse(output_meta["true_zero_copy_authorized"])
        cache.clear()
        self.assertTrue(first.prepared_value.closed)

    def test_optix_prepared_query_set_count_helper_rejects_invalid_parameters(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "point_contains count requires point_queries"):
            run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                operation="point_contains",
                partner="none",
                cache=cache,
                prepare_session=_FakeOptixPreparedQuerySetSession,
            )
        with self.assertRaisesRegex(ValueError, "range count requires box_queries"):
            run_aabb_index_query_2d_optix_prepared_query_set_count_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                point_queries=[(0.5, 0.5)],
                operation="range_contains",
                partner="none",
                cache=cache,
                prepare_session=_FakeOptixPreparedQuerySetSession,
            )

    def test_radius_graph_component_signature_helper_routes_component_union_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedRadiusGraphComponentSignature:
            prepare_calls["count"] += 1
            return _FakePreparedRadiusGraphComponentSignature()

        def run_signature(prepared: _FakePreparedRadiusGraphComponentSignature):
            return prepared.component_signature(min_neighbors=4)

        point_rows = (
            (0.0, 0.0, 0.0),
            (0.1, 0.0, 0.0),
            (10.0, 0.0, 0.0),
        )
        point_rows_fingerprint = make_prepared_input_fingerprint(point_rows)
        first = run_radius_graph_component_signature_3d_prepared_session(
            point_rows=point_rows,
            point_rows_fingerprint=point_rows_fingerprint,
            radius=0.25,
            min_neighbors=4,
            partner="numba",
            cache=cache,
            grouped_union_query_block_size=128,
            prepare_session=prepare,
            run_component_signature=run_signature,
            validate_output=lambda output: {
                "contract_ok": output["metadata"]["continuation_contract"]
                == "grouped_stream_component_size_signature_3d",
                "signature_ok": output["columns"]["component_size_signature"] == (2, 1),
                "not_app_specific": output["metadata"]["app_specific_engine_logic_allowed"] is False,
            },
            device="cuda:contract",
            warmup_count=1,
        )
        second = run_radius_graph_component_signature_3d_prepared_session(
            point_rows=point_rows,
            point_rows_fingerprint=point_rows_fingerprint,
            radius=0.25,
            min_neighbors=4,
            partner="numba",
            cache=cache,
            grouped_union_query_block_size=128,
            prepare_session=prepare,
            run_component_signature=run_signature,
            device="cuda:contract",
        )

        first_meta = first.to_metadata()
        first_audit = first.runtime_audit()
        output_meta = first.output["metadata"]

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertTrue(first.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(first.prepared_value.signature_calls, 3)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["schema"], PREPARED_EXECUTION_SESSION_RUNNER_VERSION)
        self.assertEqual(first_meta["status"], PREPARED_EXECUTION_SESSION_RUNNER_STATUS)
        self.assertEqual(first_meta["workflow_name"], "radius_graph_component_signature_3d_prepared_session")
        self.assertEqual(first_meta["primitive"], "fixed_radius_graph_component_signature_3d")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "numba")
        self.assertTrue(first_meta["set_a_probe_candidate"])
        self.assertEqual(first_meta["primitive_family"], "fixed_radius_graph_component_signature")
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(first_meta["continuation_contract"], "grouped_stream_component_size_signature_3d")
        self.assertEqual(first_meta["row_contract"], "generic_fixed_radius_graph_component_signature_3d")
        self.assertEqual(first_meta["phoenix_v3_redesign_step"], "step1_runtime_trunk_probe")
        self.assertEqual(
            first_meta["runtime_trunk_family"],
            "fixed_radius_self_query_to_grouped_stream_component_signature_3d",
        )
        self.assertTrue(first_meta["runtime_trunk_probe_candidate"])
        self.assertTrue(first_meta["runtime_trunk_executes_end_to_end"])
        self.assertTrue(first_meta["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(first_meta["hot_path_host_materialization"])
        self.assertFalse(first_meta["external_device_buffer_interop_authorized"])
        self.assertFalse(first_meta["v4_embedding_or_external_zero_copy_authorized"])
        self.assertTrue(first_meta["focused_material_gain_required_before_all_app"])
        self.assertEqual(first_meta["input_fingerprint_source"], "caller_supplied")
        self.assertTrue(first_meta["large_input_fingerprint_hot_path_avoided"])
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(first_audit["status"], "accept_step3_ready")
        self.assertTrue(first_audit["step3_residency_default_ready"])
        self.assertEqual(first_audit["missing_step3_fields"], ())
        self.assertTrue(first_audit["phase_accounting_accept"])
        self.assertTrue(first_audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(first_audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(first_audit["hot_path_host_materialization"])
        self.assertFalse(first_audit["release_authorized"])
        self.assertContinuationCoreReady(
            first_meta,
            expected_contract="grouped_stream_component_size_signature_3d",
        )
        self.assertFalse(first_audit["public_speedup_claim_authorized"])
        self.assertEqual(output_meta["adapter"], "fake_radius_graph_component_signature")
        self.assertTrue(output_meta["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(output_meta["external_host_buffer_exposure_authorized"])
        self.assertFalse(output_meta["v4_embedding_or_external_zero_copy_authorized"])
        self.assertFalse(output_meta["point_ids_materialized_for_signature"])
        self.assertFalse(output_meta["core_flags_materialized_for_signature"])
        self.assertFalse(output_meta["app_specific_engine_logic_allowed"])
        self.assertFalse(output_meta["automatic_partner_selection_authorized"])
        self.assertFalse(output_meta["true_zero_copy_authorized"])
        self.assertFalse(output_meta["rt_core_speedup_claim_authorized"])
        self.assertFalse(output_meta["whole_app_speedup_claim_authorized"])

    def test_radius_graph_component_union_helper_splits_union_from_signature_accounting(self):
        cache = ExplicitPreparedSessionCache(max_entries=2)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedRadiusGraphComponentUnion:
            prepare_calls["count"] += 1
            return _FakePreparedRadiusGraphComponentUnion()

        def run_union(prepared: _FakePreparedRadiusGraphComponentUnion):
            return prepared.component_union(min_neighbors=4)

        point_rows = (
            (0.0, 0.0, 0.0),
            (0.1, 0.0, 0.0),
            (10.0, 0.0, 0.0),
        )
        point_rows_fingerprint = make_prepared_input_fingerprint(point_rows)
        first = run_radius_graph_component_union_3d_prepared_session(
            point_rows=point_rows,
            point_rows_fingerprint=point_rows_fingerprint,
            radius=0.25,
            min_neighbors=4,
            partner="numba",
            cache=cache,
            grouped_union_query_block_size=128,
            prepare_session=prepare,
            run_component_union=run_union,
            validate_output=lambda output: {
                "contract_ok": output["metadata"]["partner_reference_contract"]
                == "generic_prepared_optix_numba_grouped_stream_component_labels_3d",
                "label_ok": output["columns"]["component_labels"] == (0, 0, 2),
                "union_policy_visible": bool(output["metadata"]["component_union_policy"]),
            },
            device="cuda:contract",
            warmup_count=1,
        )
        second = run_radius_graph_component_union_3d_prepared_session(
            point_rows=point_rows,
            point_rows_fingerprint=point_rows_fingerprint,
            radius=0.25,
            min_neighbors=4,
            partner="numba",
            cache=cache,
            grouped_union_query_block_size=128,
            prepare_session=prepare,
            run_component_union=run_union,
            device="cuda:contract",
        )

        first_meta = first.to_metadata()
        first_audit = first.runtime_audit()

        self.assertFalse(first.cache_hit)
        self.assertTrue(second.cache_hit)
        self.assertTrue(first.runtime_executed)
        self.assertEqual(prepare_calls["count"], 1)
        self.assertEqual(first.prepared_value.union_calls, 3)
        self.assertTrue(first_meta["validation_passed"])
        self.assertEqual(first_meta["workflow_name"], "radius_graph_component_union_3d_prepared_session")
        self.assertEqual(first_meta["primitive"], "fixed_radius_graph_component_union_3d")
        self.assertEqual(first_meta["explicit_backend"], "optix")
        self.assertEqual(first_meta["explicit_partner"], "numba")
        self.assertTrue(first_meta["set_a_probe_candidate"])
        self.assertFalse(first_meta["set_b_control_candidate"])
        self.assertEqual(first_meta["primitive_family"], "fixed_radius_graph_component_union")
        self.assertEqual(first_meta["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(
            first_meta["continuation_contract"],
            "generic_prepared_optix_numba_grouped_stream_component_labels_3d",
        )
        self.assertEqual(first_meta["row_contract"], "generic_fixed_radius_graph_component_union_3d")
        self.assertEqual(first_meta["phoenix_v3_redesign_step"], "m37_component_union_core_node_split")
        self.assertEqual(
            first_meta["runtime_trunk_family"],
            "fixed_radius_self_query_to_grouped_stream_component_union_3d",
        )
        self.assertTrue(first_meta["runtime_trunk_executes_end_to_end"])
        self.assertTrue(first_meta["component_union_phase_accounting_visible"])
        self.assertEqual(first_meta["component_union_pass_count"], 2)
        self.assertEqual(first_meta["component_union_native_elapsed_sec"], 0.002)
        self.assertEqual(first_meta["boundary_assignment_pass_count"], 1)
        self.assertTrue(first_meta["component_label_pass_accounted"])
        self.assertTrue(first_meta["component_label_columns_present"])
        self.assertTrue(first_meta["component_signature_accounting_split"])
        self.assertFalse(first_meta["component_signature_pass_executed"])
        self.assertIsNone(first_meta["component_signature_policy"])
        self.assertTrue(first_meta["output_contract_matches_requested"])
        self.assertTrue(first_meta["output_partner_matches_requested"])
        self.assertTrue(first_meta["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(first_meta["hot_path_host_materialization"])
        self.assertFalse(first_meta["external_device_buffer_interop_authorized"])
        self.assertFalse(first_meta["v4_embedding_or_external_zero_copy_authorized"])
        self.assertTrue(first_meta["focused_material_gain_required_before_all_app"])
        self.assertFalse(first_meta["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(first_meta["release_authorized"])
        self.assertFalse(first_meta["public_speedup_claim_authorized"])
        self.assertFalse(first_meta["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(first_meta["true_zero_copy_claim_authorized"])
        self.assertFalse(first_meta["automatic_partner_selection_authorized"])
        self.assertEqual(first_audit["status"], "accept_step3_ready")
        self.assertTrue(first_audit["step3_residency_default_ready"])
        self.assertEqual(first_audit["missing_step3_fields"], ())
        self.assertContinuationCoreReady(
            first_meta,
            expected_contract="generic_prepared_optix_numba_grouped_stream_component_labels_3d",
        )

    def test_radius_graph_component_union_helper_rejects_signature_output_as_trunk_success(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        def signature_output(_prepared):
            return {
                "columns": {},
                "metadata": {
                    "adapter": "fake_signature_not_union",
                    "partner": "numba",
                    "partner_reference_contract": (
                        "generic_prepared_optix_numba_grouped_stream_component_labels_3d"
                    ),
                    "component_union_policy": "monotonic_atomic_min",
                    "component_label_policy": "positive_root_index_labels_noise_minus_one",
                    "component_signature_policy": "direct_root_count_from_parent_workspace",
                    "grouped_stream_continuation_pass_count": 1,
                    "native_grouped_stream_metadata": {
                        "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query",
                        "native_elapsed_sec": 0.001,
                    },
                    "internal_device_residency_between_rtdl_phases": True,
                    "hot_path_host_materialization": False,
                },
            }

        result = run_radius_graph_component_union_3d_prepared_session(
            point_rows=((0.0, 0.0, 0.0),),
            radius=0.25,
            min_neighbors=1,
            partner="numba",
            cache=cache,
            prepare_session=_FakePreparedRadiusGraphComponentUnion,
            run_component_union=signature_output,
        )
        metadata = result.to_metadata()
        step3_audit = result.runtime_audit()

        self.assertTrue(metadata["runtime_executed"])
        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["component_union_phase_accounting_visible"])
        self.assertFalse(metadata["component_label_pass_accounted"])
        self.assertFalse(metadata["component_label_columns_present"])
        self.assertTrue(metadata["component_signature_pass_executed"])
        self.assertEqual(step3_audit["status"], "incomplete_step3_audit")
        self.assertFalse(step3_audit["step3_residency_default_ready"])
        self.assertFalse(step3_audit["runtime_trunk_executes_end_to_end"])

    def test_radius_graph_component_signature_helper_rejects_invalid_parameters(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        with self.assertRaisesRegex(ValueError, "radius must be positive"):
            run_radius_graph_component_signature_3d_prepared_session(
                point_rows=[(0.0, 0.0, 0.0)],
                radius=0.0,
                min_neighbors=1,
                partner="numba",
                cache=cache,
                prepare_session=_FakePreparedRadiusGraphComponentSignature,
                run_component_signature=lambda prepared: prepared.component_signature(min_neighbors=1),
            )

        with self.assertRaisesRegex(ValueError, "min_neighbors must be non-negative"):
            run_radius_graph_component_signature_3d_prepared_session(
                point_rows=[(0.0, 0.0, 0.0)],
                radius=1.0,
                min_neighbors=-1,
                partner="numba",
                cache=cache,
                prepare_session=_FakePreparedRadiusGraphComponentSignature,
                run_component_signature=lambda prepared: prepared.component_signature(min_neighbors=1),
            )

        with self.assertRaisesRegex(ValueError, "requires point_rows"):
            run_radius_graph_component_signature_3d_prepared_session(
                point_rows=[],
                radius=1.0,
                min_neighbors=1,
                partner="numba",
                cache=cache,
                prepare_session=_FakePreparedRadiusGraphComponentSignature,
                run_component_signature=lambda prepared: prepared.component_signature(min_neighbors=1),
            )

        with self.assertRaisesRegex(ValueError, "row_capacity"):
            run_aabb_index_query_2d_range_intersection_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                query_boxes=[(0.5, 0.5, 1.5, 1.5)],
                backend="optix",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeQueryHandle,
            )

        with self.assertRaisesRegex(ValueError, "query_ids length"):
            run_aabb_index_query_2d_range_intersection_prepared_session(
                indexed_boxes=[(0.0, 0.0, 1.0, 1.0)],
                query_boxes=[(0.5, 0.5, 1.5, 1.5)],
                query_ids=[1, 2],
                backend="embree",
                partner="none",
                cache=cache,
                prepare_session=_FakePreparedAabbNativeQueryHandle,
            )

    def test_aggregate_tree_fused_vector_sum_helper_executes_generic_runtime_trunk(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedAggregateTreeFusedVectorSum:
            prepare_calls["count"] += 1
            return _FakePreparedAggregateTreeFusedVectorSum()

        result = run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
            source_fingerprint={"kind": "points", "count": 2, "digest": "src"},
            target_fingerprint={"kind": "points", "count": 2, "digest": "dst"},
            aggregate_tree_fingerprint={"kind": "tree", "count": 3, "digest": "tree"},
            source_count=2,
            target_count=2,
            tree_node_count=3,
            theta=0.5,
            softening=0.01,
            partner="numba_cuda",
            cache=cache,
            prepare_session=prepare,
            run_vector_sum=lambda prepared: prepared.sum(),
            device="cuda:contract",
            warmup_count=1,
            measured_repeat_count=3,
            retain_repeat_outputs=True,
            scorecard_binding={
                "id": "set_a_barnes_hut_app_geomean_0_844x",
                "set": "A",
                "app": "barnes_hut",
                "metric": "set_a_app_geomean_v3_vs_v2_14",
                "current_value": 0.844,
                "target": "move_toward_or_above_parity",
                "source": "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md",
                "route_kind": "trunk_fix_candidate",
                "role": "aggregate_tree_fused_vector_sum_front_door_probe",
            },
            win_source="partner_continuation",
        )
        metadata = result.to_metadata()
        audit = result.runtime_audit()

        self.assertEqual(prepare_calls["count"], 1)
        self.assertTrue(result.runtime_executed)
        self.assertFalse(result.cache_hit)
        self.assertEqual(result.prepared_value.calls, 4)
        self.assertEqual(metadata["workflow_name"], "aggregate_tree_fused_weighted_vector_sum_2d_prepared_session")
        self.assertEqual(metadata["primitive"], "aggregate_tree_fused_weighted_vector_sum_2d")
        self.assertEqual(metadata["explicit_backend"], "partner")
        self.assertEqual(metadata["explicit_partner"], "numba_cuda")
        self.assertEqual(metadata["primitive_family"], "aggregate_tree_fused_weighted_vector_sum_2d")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(
            metadata["continuation_contract"],
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
        )
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "step1_replacement_runtime_trunk_probe")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "aggregate_tree_fused_weighted_vector_sum_2d_explicit_partner",
        )
        self.assertEqual(metadata["win_source"], "partner_continuation")
        self.assertTrue(metadata["win_source_classification_required"])
        self.assertIn("partner_continuation", metadata["win_source_allowed_values"])
        self.assertTrue(metadata["scorecard_blocker_bound"])
        self.assertTrue(metadata["scorecard_controlling_row_binding_required_before_release_path"])
        self.assertEqual(metadata["scorecard_blocker_set"], "A")
        self.assertEqual(metadata["scorecard_blocker_app"], "barnes_hut")
        self.assertEqual(metadata["scorecard_blocker_metric"], "set_a_app_geomean_v3_vs_v2_14")
        self.assertEqual(metadata["scorecard_blocker_current_value"], 0.844)
        self.assertEqual(metadata["scorecard_blocker_target"], "move_toward_or_above_parity")
        self.assertEqual(metadata["scorecard_blocker_route_kind"], "trunk_fix_candidate")
        self.assertEqual(metadata["m72_target_blocker"], "set_a_barnes_hut_app_geomean_0_844x")
        self.assertTrue(metadata["m72_target_blocker_review_required_before_pod"])
        self.assertTrue(metadata["release_path_candidate"])
        self.assertIn("not the M43 CuPy grouped-reduction kernel", metadata["m43_reuse_scope"])
        self.assertTrue(metadata["runtime_trunk_probe_candidate"])
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["output_contract_matches_requested"])
        self.assertTrue(metadata["output_partner_matches_requested"])
        self.assertTrue(metadata["output_counts_match_requested"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["frontier_rows_materialized_on_host"])
        self.assertFalse(metadata["contribution_rows_materialized_on_host"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertTrue(metadata["focused_material_gain_required_before_all_app"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertEqual(len(result.output), 3)
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="generic_aggregate_tree_fused_weighted_vector_sum_2d_numba_cuda_v1",
        )
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])

    def test_aggregate_tree_fused_vector_sum_helper_without_blocker_binding_is_not_release_path_candidate(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        result = run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
            source_fingerprint={"kind": "points", "count": 2, "digest": "src"},
            target_fingerprint={"kind": "points", "count": 2, "digest": "dst"},
            aggregate_tree_fingerprint={"kind": "tree", "count": 3, "digest": "tree"},
            source_count=2,
            target_count=2,
            tree_node_count=3,
            theta=0.5,
            softening=0.01,
            partner="numba_cuda",
            cache=cache,
            prepare_session=_FakePreparedAggregateTreeFusedVectorSum,
            run_vector_sum=lambda prepared: prepared.sum(),
        )
        metadata = result.to_metadata()

        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["scorecard_blocker_bound"])
        self.assertEqual(metadata["scorecard_binding"], {})
        self.assertFalse(metadata["release_path_candidate"])
        self.assertIsNone(metadata["m72_target_blocker"])
        self.assertFalse(metadata["m72_target_blocker_review_required_before_pod"])

    def test_aggregate_tree_fused_vector_sum_helper_requires_valid_win_source_and_binding(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        kwargs = {
            "source_fingerprint": "source",
            "target_fingerprint": "target",
            "aggregate_tree_fingerprint": "tree",
            "source_count": 2,
            "target_count": 2,
            "tree_node_count": 3,
            "theta": 0.5,
            "softening": 0.01,
            "partner": "numba_cuda",
            "cache": cache,
            "prepare_session": _FakePreparedAggregateTreeFusedVectorSum,
            "run_vector_sum": lambda prepared: prepared.sum(),
        }

        with self.assertRaisesRegex(ValueError, "win_source must be one of"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "win_source": "rt_core"}
            )
        with self.assertRaisesRegex(ValueError, "scorecard_binding missing required fields"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "scorecard_binding": {"app": "barnes_hut"}}
            )
        with self.assertRaisesRegex(ValueError, "route_kind"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{
                    **kwargs,
                    "scorecard_binding": {
                        "set": "A",
                        "id": "set_a_barnes_hut_app_geomean_0_844x",
                        "app": "barnes_hut",
                        "metric": "set_a_app_geomean_v3_vs_v2_14",
                        "current_value": 0.844,
                        "source": "docs/rebuild/v3/phoenix_v3_set_a_set_b_scorecard_gate_2026-06-22.md",
                        "route_kind": "pretty_local_win",
                    },
                }
            )

    def test_grouped_vector_sum_helper_executes_generic_reduction_core_node(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepare_calls = {"count": 0}

        def prepare() -> _FakePreparedGroupedVectorSum2D:
            prepare_calls["count"] += 1
            return _FakePreparedGroupedVectorSum2D()

        result = run_grouped_vector_sum_2d_prepared_session(
            vector_columns_fingerprint={
                "kind": "presegmented_columns",
                "digest": "vectors",
            },
            row_offsets_fingerprint={
                "kind": "row_offsets",
                "digest": "offsets",
            },
            row_count=4,
            group_count=2,
            partner="numba",
            cache=cache,
            prepare_session=prepare,
            run_grouped_vector_sum=lambda prepared: prepared.sum(),
            validate_output=lambda output: {
                "contract_ok": output["metadata"]["partner_reference_contract"]
                == "generic_grouped_vector_sum_f64x2",
                "sum_ok": output["columns"]["sum_x"] == (3.0, 7.0),
                "not_app_specific": output["metadata"]["app_specific_engine_logic_allowed"] is False,
            },
            device="cuda:contract",
            warmup_count=1,
            measured_repeat_count=3,
            retain_repeat_outputs=True,
        )
        metadata = result.to_metadata()
        audit = result.runtime_audit()

        self.assertEqual(prepare_calls["count"], 1)
        self.assertTrue(result.runtime_executed)
        self.assertFalse(result.cache_hit)
        self.assertEqual(result.prepared_value.calls, 4)
        self.assertEqual(metadata["workflow_name"], "grouped_vector_sum_2d_prepared_session")
        self.assertEqual(metadata["primitive"], "grouped_vector_sum_2d")
        self.assertEqual(metadata["explicit_backend"], "partner")
        self.assertEqual(metadata["explicit_partner"], "numba")
        self.assertTrue(metadata["set_a_probe_candidate"])
        self.assertFalse(metadata["set_b_control_candidate"])
        self.assertEqual(metadata["primitive_family"], "grouped_vector_sum_2d")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["continuation_contract"], "generic_grouped_vector_sum_f64x2")
        self.assertEqual(metadata["row_contract"], "generic_presegmented_grouped_vector_sum_2d")
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "m36_grouped_reduction_core_node")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "grouped_vector_sum_2d_partner_columns_session",
        )
        self.assertTrue(metadata["runtime_trunk_probe_candidate"])
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertEqual(metadata["row_count"], 4)
        self.assertEqual(metadata["group_count"], 2)
        self.assertTrue(metadata["output_contract_matches_requested"])
        self.assertTrue(metadata["output_partner_matches_requested"])
        self.assertEqual(metadata["adapter_row_count"], 4)
        self.assertEqual(metadata["adapter_group_count"], 2)
        self.assertTrue(metadata["adapter_counts_present"])
        self.assertTrue(metadata["output_counts_match_requested"])
        self.assertEqual(metadata["v2_5_numba_offset_program_count"], 1)
        self.assertEqual(metadata["v2_5_numba_threads_per_block"], 256)
        self.assertEqual(metadata["v2_5_numba_groups_per_block"], 8)
        self.assertEqual(metadata["v2_5_numba_threads_per_group"], 32)
        self.assertEqual(
            metadata["v2_5_numba_launch_parallelism_axis"],
            "group_count_warp_per_group_row_parallel",
        )
        self.assertEqual(metadata["v2_5_numba_rows_per_group_mean"], 2.0)
        self.assertEqual(metadata["v2_5_numba_kernel_strategy"], "warp_per_group_tiled")
        self.assertTrue(metadata["v2_5_numba_tiled_row_parallel_reduction_used"])
        self.assertFalse(metadata["v2_5_numba_thread_per_group_serial_loop_used"])
        self.assertEqual(
            metadata["grouped_reduction_launch_shape"],
            {
                "partner": "numba",
                "parallelism_axis": "group_count_warp_per_group_row_parallel",
                "kernel_strategy": "warp_per_group_tiled",
                "program_count": 1,
                "threads_per_block": 256,
                "groups_per_block": 8,
                "threads_per_group": 32,
                "row_count": 4,
                "group_count": 2,
                "rows_per_group_mean": 2.0,
                "tiled_row_parallel_reduction_used": True,
                "thread_per_group_serial_loop_used": False,
            },
        )
        self.assertTrue(metadata["output_columns_reused"])
        self.assertFalse(metadata["per_run_neutral_handoff_validation_used"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertEqual(
            metadata["native_engine_row_contract"],
            "not_called_partner_continuation_only",
        )
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertTrue(metadata["focused_material_gain_required_before_all_app"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertEqual(len(result.output), 3)
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertFalse(audit["release_authorized"])
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="generic_grouped_vector_sum_f64x2",
        )

    def test_grouped_vector_sum_helper_rejects_invalid_inputs(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        kwargs = {
            "vector_columns_fingerprint": "columns",
            "row_offsets_fingerprint": "offsets",
            "row_count": 4,
            "group_count": 2,
            "partner": "numba",
            "cache": cache,
            "prepare_session": _FakePreparedGroupedVectorSum2D,
            "run_grouped_vector_sum": lambda prepared: prepared.sum(),
        }

        with self.assertRaisesRegex(ValueError, "partner='numba'"):
            run_grouped_vector_sum_2d_prepared_session(
                **{**kwargs, "partner": "auto"}
            )
        with self.assertRaisesRegex(ValueError, "row_count must be positive"):
            run_grouped_vector_sum_2d_prepared_session(
                **{**kwargs, "row_count": 0}
            )
        with self.assertRaisesRegex(ValueError, "group_count must be positive"):
            run_grouped_vector_sum_2d_prepared_session(
                **{**kwargs, "group_count": 0}
            )

    def test_grouped_vector_sum_helper_rejects_weak_output_metadata_as_trunk_success(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        def weak_output(_prepared):
            return {
                "columns": {},
                "metadata": {
                    "partner": "numba",
                    "partner_reference_contract": "generic_grouped_vector_sum_f64x2",
                    "group_count": 2,
                    "row_count": 4,
                    "output_columns_reused": False,
                    "per_run_neutral_handoff_validation_used": True,
                    "host_rows_materialized": True,
                },
            }

        result = run_grouped_vector_sum_2d_prepared_session(
            vector_columns_fingerprint="columns",
            row_offsets_fingerprint="offsets",
            row_count=4,
            group_count=2,
            partner="numba",
            cache=cache,
            prepare_session=_FakePreparedGroupedVectorSum2D,
            run_grouped_vector_sum=weak_output,
        )
        metadata = result.to_metadata()
        step3_audit = result.runtime_audit()

        self.assertTrue(metadata["runtime_executed"])
        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertTrue(metadata["hot_path_host_materialization"])
        self.assertFalse(step3_audit["step3_residency_default_ready"])
        self.assertFalse(step3_audit["runtime_trunk_executes_end_to_end"])
        self.assertFalse(step3_audit["internal_device_residency_between_rtdl_phases"])
        self.assertTrue(step3_audit["hot_path_host_materialization"])

    def test_aggregate_tree_fused_vector_sum_helper_rejects_invalid_inputs(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        kwargs = {
            "source_fingerprint": "source",
            "target_fingerprint": "target",
            "aggregate_tree_fingerprint": "tree",
            "source_count": 2,
            "target_count": 2,
            "tree_node_count": 3,
            "theta": 0.5,
            "softening": 0.0,
            "partner": "numba_cuda",
            "cache": cache,
            "prepare_session": _FakePreparedAggregateTreeFusedVectorSum,
            "run_vector_sum": lambda prepared: prepared.sum(),
        }

        with self.assertRaisesRegex(ValueError, "partner='numba_cuda'"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "partner": "numba"}
            )
        with self.assertRaisesRegex(ValueError, "source_count must be positive"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "source_count": 0}
            )
        with self.assertRaisesRegex(ValueError, "theta must be positive"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "theta": 0.0}
            )
        with self.assertRaisesRegex(ValueError, "softening must be non-negative"):
            run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
                **{**kwargs, "softening": -0.1}
            )

    def test_aggregate_tree_fused_vector_sum_helper_rejects_weak_output_metadata_as_trunk_success(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        def weak_output(_prepared):
            return {
                "columns": {},
                "metadata": {
                    "prepared_lookup_columns_resident": True,
                    "source_columns_reused": True,
                    "target_columns_reused": True,
                    "aggregate_tree_columns_resident": True,
                    "output_columns_reused": True,
                    "frontier_rows_emitted": False,
                    "frontier_rows_materialized_on_host": False,
                    "contribution_rows_materialized_on_host": False,
                },
            }

        result = run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session(
            source_fingerprint="source",
            target_fingerprint="target",
            aggregate_tree_fingerprint="tree",
            source_count=2,
            target_count=2,
            tree_node_count=3,
            theta=0.5,
            softening=0.0,
            partner="numba_cuda",
            cache=cache,
            prepare_session=_FakePreparedAggregateTreeFusedVectorSum,
            run_vector_sum=weak_output,
        )
        metadata = result.to_metadata()

        self.assertTrue(metadata["runtime_executed"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["output_contract_matches_requested"])
        self.assertFalse(metadata["output_partner_matches_requested"])
        self.assertFalse(metadata["output_counts_match_requested"])

    def test_ray_triangle_weighted_summary_helper_routes_triangle_candidate_through_runner(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        prepared = _FakePreparedRayTriangleWeightedSummaryDeviceOutput()

        result = run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
            triangle_fingerprint={
                "contract": "synthetic_weighted_any_hit",
                "scale": "k4_80000",
            },
            ray_batch_fingerprint={
                "ray_layout": "prepared_segment_replay",
                "ray_count": 80000,
            },
            weight_fingerprint={
                "weight_layout": "device_resident_uint64",
                "ray_count": 80000,
            },
            primitive_count=320000,
            ray_count=80000,
            expected_weighted_hit_sum=320000,
            partner="cupy",
            cache=cache,
            prepare_session=lambda: prepared,
            device="cuda:contract",
            warmup_count=1,
            measured_repeat_count=5,
            require_repeat5_material_probe=True,
            retain_repeat_outputs=True,
        )
        metadata = result.to_metadata()
        audit = result.runtime_audit()

        self.assertTrue(result.runtime_executed)
        self.assertFalse(result.cache_hit)
        self.assertEqual(prepared.calls, 6)
        self.assertEqual(metadata["workflow_name"], "ray_triangle_weighted_summary_device_output_stream_prepared_session")
        self.assertEqual(metadata["primitive"], "ray_triangle_weighted_summary_device_output_stream")
        self.assertEqual(metadata["explicit_backend"], "optix")
        self.assertEqual(metadata["explicit_partner"], "cupy")
        self.assertEqual(metadata["primitive_family"], "ray_triangle_weighted_summary_device_output_stream")
        self.assertEqual(metadata["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(metadata["phoenix_v3_redesign_step"], "m16_triangle_candidate_local_runner_wiring")
        self.assertEqual(
            metadata["runtime_trunk_family"],
            "ray_triangle_weighted_summary_device_output_stream",
        )
        self.assertTrue(metadata["runtime_trunk_probe_candidate"])
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])
        self.assertTrue(metadata["output_contract_matches_requested"])
        self.assertTrue(metadata["output_partner_matches_requested"])
        self.assertTrue(metadata["output_counts_match_requested"])
        self.assertTrue(metadata["weighted_hit_sum_matches_expected"])
        self.assertTrue(metadata["device_output_stream_validated"])
        self.assertTrue(metadata["prepared_scene_reused"])
        self.assertTrue(metadata["prepared_ray_batch_reused"])
        self.assertTrue(metadata["ray_weights_device_resident"])
        self.assertTrue(metadata["output_scalar_device_resident_until_finalize"])
        self.assertTrue(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertFalse(metadata["m113_graph_capture_claim_authorized"])
        self.assertFalse(metadata["m113_cuda_graph_capture_validated"])
        self.assertTrue(metadata["m113_graph_capture_still_blocked_for_triangle"])
        self.assertTrue(metadata["material_probe_repeat_requirement_met"])
        self.assertTrue(metadata["repeat5_material_probe_candidate"])
        self.assertTrue(metadata["same_contract_embree_baseline_required"])
        self.assertTrue(metadata["old_triangle_row_does_not_count_as_current_third_probe"])
        self.assertFalse(metadata["external_device_buffer_interop_authorized"])
        self.assertFalse(metadata["v4_embedding_or_external_zero_copy_authorized"])
        self.assertFalse(metadata["full_all_app_rerun_authorized_by_this_packet"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertFalse(metadata["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["automatic_partner_selection_allowed"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertEqual(len(result.output), 5)
        self.assertEqual(audit["status"], "accept_step3_ready")
        self.assertTrue(audit["step3_residency_default_ready"])
        self.assertEqual(audit["missing_step3_fields"], ())
        self.assertTrue(audit["phase_accounting_accept"])
        self.assertTrue(audit["runtime_trunk_executes_end_to_end"])
        self.assertTrue(audit["internal_device_residency_between_rtdl_phases"])
        self.assertFalse(audit["hot_path_host_materialization"])
        self.assertFalse(audit["release_authorized"])
        self.assertFalse(audit["public_speedup_claim_authorized"])
        self.assertContinuationCoreReady(
            metadata,
            expected_contract="generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1",
        )

    def test_ray_triangle_weighted_summary_helper_can_finalize_scalar_after_measured_repeats(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        class Prepared:
            def __init__(self) -> None:
                self.launch_calls = 0
                self.finalize_calls = 0

            def launch(self) -> dict[str, object]:
                self.launch_calls += 1
                return {
                    "metadata": {
                        "contract": "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1",
                        "partner": "cupy",
                        "primitive_count": 4,
                        "ray_count": 5,
                        "prepared_scene_reused": True,
                        "prepared_ray_batch_reused": True,
                        "ray_weights_device_resident": True,
                        "device_output_stream_validated": True,
                        "caller_owned_device_output_scalar": True,
                        "output_scalar_device_resident_until_finalize": True,
                        "host_scalar_materialized_during_hot_path": False,
                        "hot_path_host_materialization": False,
                        "m113_graph_capture_claim_authorized": False,
                    },
                }

            def finalize(self, measured_output: dict[str, object]) -> dict[str, object]:
                self.finalize_calls += 1
                output = dict(measured_output)
                metadata = dict(output["metadata"])
                metadata["weighted_hit_sum"] = 7
                metadata["host_scalar_materialized_during_finalize"] = True
                output["weighted_hit_sum"] = 7
                output["metadata"] = metadata
                return output

        prepared = Prepared()
        result = run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
            triangle_fingerprint="triangles",
            ray_batch_fingerprint="rays",
            weight_fingerprint="weights",
            primitive_count=4,
            ray_count=5,
            expected_weighted_hit_sum=7,
            partner="cupy",
            cache=cache,
            prepare_session=lambda: prepared,
            run_weighted_summary=lambda item: item.launch(),
            finalize_weighted_summary=lambda item, measured_output: item.finalize(measured_output),
            warmup_count=1,
            measured_repeat_count=5,
            require_repeat5_material_probe=True,
        )
        metadata = result.to_metadata()

        self.assertEqual(prepared.launch_calls, 6)
        self.assertEqual(prepared.finalize_calls, 1)
        self.assertEqual(result.output["weighted_hit_sum"], 7)
        self.assertTrue(metadata["measured_output_finalized_once"])
        self.assertTrue(metadata["per_repeat_output_finalization_avoided"])
        self.assertTrue(metadata["weighted_hit_sum_matches_expected"])
        self.assertFalse(metadata["hot_path_host_materialization"])
        self.assertTrue(metadata["runtime_trunk_executes_end_to_end"])

    def test_ray_triangle_weighted_summary_helper_rejects_weak_output_as_trunk_success(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)

        result = run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
            triangle_fingerprint="triangles",
            ray_batch_fingerprint="rays",
            weight_fingerprint="weights",
            primitive_count=2,
            ray_count=3,
            expected_weighted_hit_sum=1,
            partner="cupy",
            cache=cache,
            prepare_session=_FakePreparedRayTriangleWeightedSummaryDeviceOutput,
            run_weighted_summary=lambda _prepared: {
                "metadata": {
                    "contract": "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1",
                    "partner": "cupy",
                    "primitive_count": 2,
                    "ray_count": 3,
                    "weighted_hit_sum": 1,
                    "prepared_scene_reused": True,
                    "prepared_ray_batch_reused": True,
                    "ray_weights_device_resident": True,
                    "device_output_stream_validated": False,
                    "caller_owned_device_output_scalar": False,
                    "hot_path_host_materialization": True,
                }
            },
        )
        metadata = result.to_metadata()

        self.assertTrue(metadata["runtime_executed"])
        self.assertFalse(metadata["runtime_trunk_executes_end_to_end"])
        self.assertFalse(metadata["device_output_stream_validated"])
        self.assertFalse(metadata["internal_device_residency_between_rtdl_phases"])
        self.assertTrue(metadata["hot_path_host_materialization"])

    def test_ray_triangle_weighted_summary_helper_rejects_invalid_inputs(self):
        cache = ExplicitPreparedSessionCache(max_entries=1)
        kwargs = {
            "triangle_fingerprint": "triangles",
            "ray_batch_fingerprint": "rays",
            "weight_fingerprint": "weights",
            "primitive_count": 1,
            "ray_count": 1,
            "expected_weighted_hit_sum": 1,
            "partner": "cupy",
            "cache": cache,
            "prepare_session": _FakePreparedRayTriangleWeightedSummaryDeviceOutput,
        }

        with self.assertRaisesRegex(ValueError, "backend='optix'"):
            run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                **{**kwargs, "backend": "embree"}
            )
        with self.assertRaisesRegex(ValueError, "explicit partner"):
            run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                **{**kwargs, "partner": "none"}
            )
        with self.assertRaisesRegex(ValueError, "app-agnostic"):
            run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                **{**kwargs, "output_contract": "triangle_counting_rt_graph_contract"}
            )
        with self.assertRaisesRegex(ValueError, "measured_repeat_count"):
            run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                **{**kwargs, "measured_repeat_count": 0}
            )
        with self.assertRaisesRegex(ValueError, "repeat5"):
            run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                **{**kwargs, "require_repeat5_material_probe": True}
            )


if __name__ == "__main__":
    unittest.main()
