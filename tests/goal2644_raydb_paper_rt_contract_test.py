from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
RAYDB_APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"
README = ROOT / "examples/v2_0/research_benchmarks/raydb_style/README.md"
REPORT = ROOT / "docs/reports/goal2644_raydb_paper_rt_core_rewrite_2026-05-27.md"
OPTIX_API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
EMBREE_API = ROOT / "src/native/embree/rtdl_embree_api.cpp"
EMBREE_PRELUDE = ROOT / "src/native/embree/rtdl_embree_prelude.h"
EMBREE_SCENE = ROOT / "src/native/embree/rtdl_embree_scene.cpp"
EMBREE_RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"


class Goal2644RaydbPaperRtContractTest(unittest.TestCase):
    def test_paper_rt_cpu_reference_matches_columnar_oracle_for_all_modes(self) -> None:
        suite = app.run_suite(backend=app.PAPER_RT_CPU_REFERENCE_BACKEND)
        self.assertTrue(suite["all_match_cpu_reference"])
        self.assertEqual(set(suite["modes"]), set(app.PAPER_RT_RESULT_MODES))
        for payload in suite["modes"].values():
            metadata = payload["metadata"]
            self.assertEqual(metadata["contract"], "raydb_paper_triangle_scan_grouped_aggregate_cpu_reference")
            self.assertEqual(metadata["paper_reproduction"], "paper_shaped_rt_contract_reference")
            self.assertTrue(metadata["hit_id_set_matches_predicate"])
            self.assertEqual(metadata["deduplicated_primitive_hit_count"], 4)
            self.assertEqual(metadata["expected_predicate_row_count"], 4)
            self.assertFalse(metadata["rt_core_accelerated"])
            self.assertFalse(metadata["rt_core_claim_authorized"])

    def test_paper_rt_reference_uses_triangle_ray_dedup_shape(self) -> None:
        payload = app.run_result_mode("sum", backend=app.PAPER_RT_CPU_REFERENCE_BACKEND)
        metadata = payload["metadata"]
        shape = metadata["reference_execution_shape"]
        self.assertIn("Triangle3D", shape["row_encoding"])
        self.assertEqual(shape["ray_direction"], "+Z")
        self.assertIn("Sx/2", shape["ray_spacing"])
        self.assertIn("deduplicate primitive ids", shape["deduplication"])
        self.assertEqual(metadata["triangle_count"], payload["row_count"])
        self.assertGreater(metadata["ray_count"], metadata["triangle_count"])
        self.assertEqual(metadata["raydb_reference_repo"], app.RAYDB_REFERENCE_REPO)
        self.assertEqual(metadata["raydb_reference_commit"], app.RAYDB_REFERENCE_COMMIT)
        self.assertEqual(metadata["generic_primitive_used"], "RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D")
        self.assertEqual(metadata["generic_primitive_reduction"], "sum")

    def test_paper_rt_packed_workload_preserves_shape_without_python_triangles(self) -> None:
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("numpy is required for packed RayDB host-buffer workload")
        fixture = app.make_fixture(copies=3)
        plan = app.make_plan("sum")
        object_workload = app._make_paper_rt_encoded_workload(fixture, plan, "sum")
        packed_workload = app._make_paper_rt_encoded_packed_workload(fixture, plan, "sum")
        table_descriptor = app.prepare_paper_rt_encoded_table_descriptor(fixture, plan)
        descriptor_workload = app._make_paper_rt_encoded_packed_workload(
            fixture,
            plan,
            "sum",
            table_descriptor=table_descriptor,
        )

        self.assertTrue(packed_workload["packed_host_buffers"])
        self.assertTrue(descriptor_workload["prepared_table_descriptor_used"])
        self.assertEqual(
            descriptor_workload["table_descriptor_contract"],
            "RAYDB_APP_PREPARED_ENCODED_TABLE_DESCRIPTOR_V1",
        )
        self.assertEqual(packed_workload["triangles"].count, len(object_workload["triangles"]))
        self.assertEqual(packed_workload["rays"].count, len(object_workload["rays"]))
        self.assertEqual(descriptor_workload["triangles"].count, packed_workload["triangles"].count)
        self.assertEqual(descriptor_workload["rays"].count, packed_workload["rays"].count)
        self.assertEqual(len(packed_workload["primitive_group_ids"]), len(object_workload["primitive_records"]))
        self.assertEqual(len(packed_workload["primitive_values"]), len(object_workload["primitive_records"]))
        self.assertEqual(len(descriptor_workload["primitive_group_ids"]), len(packed_workload["primitive_group_ids"]))
        self.assertEqual(len(descriptor_workload["primitive_values"]), len(packed_workload["primitive_values"]))
        self.assertEqual(packed_workload["query_scan_values"], object_workload["query_scan_values"])
        self.assertEqual(descriptor_workload["query_scan_values"], packed_workload["query_scan_values"])
        self.assertEqual(packed_workload["group_tuples"], object_workload["group_tuples"])
        self.assertEqual(descriptor_workload["group_tuples"], packed_workload["group_tuples"])

    def test_generated_fixture_is_not_the_ray_starved_repeated_shape(self) -> None:
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("numpy is required for generated RayDB fixture")
        fixture = app.make_generated_fixture(row_count=1024, group_count=16, revenue_mod=16)
        count_workload = app._make_paper_rt_encoded_packed_workload(fixture, app.make_plan("count"), "count")
        sum_workload = app._make_paper_rt_encoded_packed_workload(fixture, app.make_plan("sum"), "sum")
        payload = app.run_result_mode(
            "sum",
            backend=app.PAPER_RT_CPU_REFERENCE_BACKEND,
            fixture_kind="generated",
            generated_rows=1024,
            generated_groups=16,
            generated_revenue_mod=16,
        )

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["metadata"]["fixture"], "generated_deterministic")
        self.assertEqual(count_workload["triangles"].count, 1024)
        self.assertGreater(len(count_workload["query_scan_values"]), 1)
        self.assertGreater(sum_workload["rays"].count, count_workload["rays"].count)

    def test_generic_grouped_reduction_primitive_is_exported_and_app_agnostic(self) -> None:
        self.assertIn("run_generic_ray_triangle_primitive_grouped_i64_reduction_3d", rt.__all__)
        self.assertIn("prepare_generic_ray_triangle_primitive_grouped_i64_reduction_3d", rt.__all__)
        self.assertIn("OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL", rt.__all__)
        self.assertIn("OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL", rt.__all__)
        self.assertIn("OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL", rt.__all__)
        self.assertIn("OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL", rt.__all__)
        self.assertEqual(
            rt.OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction",
        )
        self.assertEqual(
            rt.OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "rtdl_optix_static_triangle_scene_3d_ray_prepared_primitive_grouped_i64_reduction",
        )
        self.assertEqual(
            rt.OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
            "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction",
        )
        generic_source = (ROOT / "src/rtdsl/generic_primitives.py").read_text(encoding="utf-8").lower()
        for forbidden in ("raydb-i0", "sql-like", "ssb query", "table scan"):
            self.assertNotIn(forbidden, generic_source)
        node = rt.find_primitive_hierarchy_node("reduction.ray_triangle_primitive_grouped_i64")
        self.assertEqual(node.layer, "reduction")
        self.assertEqual(node.status, "candidate_behavior")

    def test_optix_paper_backend_is_exposed_for_pod_validation(self) -> None:
        self.assertIn(app.PAPER_RT_OPTIX_BACKEND, app.BACKENDS)
        try:
            payload = app.run_result_mode("sum", backend=app.PAPER_RT_OPTIX_BACKEND)
        except (FileNotFoundError, RuntimeError) as exc:
            self.assertRegex(str(exc), "CUDA driver|librtdl_optix|does not export")
            return
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertTrue(payload["metadata"]["rt_core_accelerated"])
        self.assertEqual(
            payload["metadata"]["native_symbol"],
            rt.OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL,
        )

    def test_embree_paper_backend_uses_same_generic_contract(self) -> None:
        self.assertIn(app.PAPER_RT_EMBREE_BACKEND, app.BACKENDS)
        try:
            payload = app.run_result_mode("sum", backend=app.PAPER_RT_EMBREE_BACKEND)
        except (FileNotFoundError, RuntimeError) as exc:
            self.assertRegex(str(exc), "Embree|librtdl_embree|does not export")
            return
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertFalse(payload["metadata"]["rt_core_accelerated"])
        self.assertTrue(payload["metadata"]["embree_same_contract_baseline"])
        self.assertEqual(
            payload["metadata"]["native_symbol"],
            "rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction",
        )

    def test_native_sources_define_generic_symbol_shape(self) -> None:
        symbol = rt.OPTIX_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL
        prepared_symbol = rt.OPTIX_PREPARED_RAY_TRIANGLE_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL
        prepared_ray_symbol = rt.OPTIX_RAY_BATCH_PREPARED_PRIMITIVE_GROUPED_I64_REDUCTION_3D_SYMBOL
        device_ray_batch_symbol = rt.OPTIX_RAY_BATCH_3D_CREATE_DEVICE_RAYS_SYMBOL
        payload_symbol = rt.OPTIX_PRIMITIVE_GROUPED_I64_PAYLOAD_3D_CREATE_SYMBOL
        for path in (OPTIX_API, OPTIX_PRELUDE, OPTIX_RUNTIME):
            self.assertIn(symbol, path.read_text(encoding="utf-8"))
            self.assertIn(prepared_symbol, path.read_text(encoding="utf-8"))
            self.assertIn(prepared_ray_symbol, path.read_text(encoding="utf-8"))
            self.assertIn(device_ray_batch_symbol, path.read_text(encoding="utf-8"))
            self.assertIn(payload_symbol, path.read_text(encoding="utf-8"))
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("RayPrimitiveGroupedI64Reduction3DLaunchParams", workloads)
        self.assertIn("PreparedPrimitiveGroupedI64Payload3D", workloads)
        self.assertIn("PreparedRayBatch3D", workloads)
        self.assertIn("pack_ray3d_device_columns_to_buffer", workloads)
        self.assertIn("optixGetPrimitiveIndex", workloads)
        self.assertIn("primitive_flags", workloads)
        self.assertIn("RTDL_GROUPED_OP_SUM_COUNT", workloads)
        embree_symbol = "rtdl_embree_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction"
        for path in (EMBREE_API, EMBREE_PRELUDE, EMBREE_RUNTIME):
            self.assertIn(embree_symbol, path.read_text(encoding="utf-8"))
        self.assertIn("kRayPrimitiveGroupedI64Reduction3D", EMBREE_SCENE.read_text(encoding="utf-8"))

    def test_legacy_optix_columnar_payload_is_not_marked_rt_core_accelerated(self) -> None:
        source = RAYDB_APP.read_text(encoding="utf-8")
        self.assertIn("columnar_grouped_aggregate_optix_columnar_payload", source)
        self.assertIn("contract=\"columnar_grouped_aggregate_optix_columnar_payload\"", source)
        self.assertIn("rt_core_accelerated=False", source)

    def test_docs_record_reference_boundary_and_next_native_primitive(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for text in (readme, report):
            self.assertIn("paper_rt_cpu_reference", text)
            self.assertIn(app.GENERIC_RAY_TRIANGLE_GROUPED_REDUCTION_3D_SYMBOL, text)
            self.assertIn("RayDB-i0", text)
            self.assertIn("no RayDB-specific native", text)


if __name__ == "__main__":
    unittest.main()
