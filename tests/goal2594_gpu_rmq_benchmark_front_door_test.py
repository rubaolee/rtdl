from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
import sys
import struct

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.gpu_rmq import rtdl_gpu_rmq_benchmark_app as app
from rtdsl.reference import ray_triangle_closest_hit_cpu


class Goal2594GpuRmqBenchmarkFrontDoorTest(unittest.TestCase):
    def test_exact_cpu_rmq_uses_leftmost_minimum(self) -> None:
        values = (5.0, 2.0, 7.0, 2.0, 9.0)
        rows = app.exact_rmq_cpu(values, ((0, 4), (2, 4), (3, 3)))
        self.assertEqual(
            rows,
            (
                {"query_id": 0, "left": 0, "right": 4, "index": 1, "value": 2.0},
                {"query_id": 1, "left": 2, "right": 4, "index": 3, "value": 2.0},
                {"query_id": 2, "left": 3, "right": 3, "index": 3, "value": 2.0},
            ),
        )

    def test_local_hierarchical_matches_cpu_reference(self) -> None:
        fixture = app.make_fixture(
            dataset="repeated",
            value_count=257,
            query_count=73,
            seed=123,
            max_width=64,
        )
        expected = app.exact_rmq_cpu(fixture.values, fixture.queries)
        actual, table = app.hierarchical_rmq_local(fixture.values, fixture.queries, block_size=16)
        self.assertTrue(app._rows_match(expected, actual))
        self.assertGreaterEqual(table.metadata()["sparse_levels"], 1)

    def test_compare_local_payload_records_parity(self) -> None:
        payload = app.run_app(
            "compare_local",
            dataset="sawtooth",
            value_count=512,
            query_count=101,
            seed=44,
            max_width=80,
            block_size=32,
        )
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["fixture"]["value_count"], 512)
        self.assertEqual(payload["claim_boundary"]["full_gpu_rmq_reproduction"], False)
        self.assertEqual(payload["claim_boundary"]["native_engine_customization"], False)

    def test_scope_payload_marks_candidate_not_speedup_claim(self) -> None:
        payload = app.run_app("scope")
        self.assertEqual(payload["status"], "research_learner_app_not_benchmark")
        self.assertIn("GPU-RMQ", payload["paper_reference"]["title"])
        self.assertIn("paper_rt_lowering_reference", payload["current_local_modes"])
        self.assertIn("paper_rt_prepared_reuse", payload["current_local_modes"])
        self.assertIn("paper_hybrid_rtdl_partner", payload["current_local_modes"])
        self.assertTrue(payload["claim_boundary"]["paper_rt_lowering_path"])
        self.assertTrue(payload["claim_boundary"]["optix_generic_closest_hit_source_wired"])
        self.assertTrue(payload["claim_boundary"]["optix_generic_closest_hit_ready"])
        self.assertTrue(payload["claim_boundary"]["cupy_partner_path"])
        self.assertFalse(payload["claim_boundary"]["benchmark_app"])
        self.assertTrue(payload["claim_boundary"]["demoted_from_benchmark_candidate"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertIn("hybrid", payload["why_benchmark"])
        self.assertIn("cupy_author_style_hierarchical", payload["current_local_modes"])

    def test_paper_rt_lowering_matches_cpu_reference_with_ties(self) -> None:
        fixture = app.RMQFixture(
            dataset="hand_tie_case",
            values=(5.0, 2.0, 7.0, 2.0, 9.0, 1.0, 1.0, 4.0, 0.0, 0.0),
            queries=((0, 4), (5, 9), (6, 9), (1, 8)),
            seed=0,
        )
        expected = app.exact_rmq_cpu(fixture.values, fixture.queries)
        actual, scene = app.paper_rt_lowered_rmq(fixture.values, fixture.queries, block_size=4)
        self.assertTrue(app._rows_match(expected, actual))
        self.assertGreater(scene.metadata()["tie_break_epsilon"], 0.0)

    def test_paper_rt_scheduler_keeps_rmq_logic_app_side(self) -> None:
        fixture = app.RMQFixture(
            dataset="hand_schedule_case",
            values=(5.0, 2.0, 7.0, 2.0, 9.0, 1.0, 1.5, 4.0),
            queries=((0, 2), (1, 6), (4, 7)),
            seed=0,
        )
        scene = app.build_paper_rt_rmq_scene(fixture.values, block_size=4)
        scheduled = app._schedule_paper_rt_rmq_phases(fixture.queries, scene)
        self.assertEqual(scheduled.query_count, len(fixture.queries))
        self.assertGreater(scheduled.total_ray_count, len(fixture.queries))
        self.assertEqual({phase.phase for phase in scheduled.phases}, {"same_block", "left_partial", "right_partial"})
        self.assertEqual(scheduled.full_phase.phase, "full_blocks")

    def test_paper_rt_partial_block_rays_cover_block_size_one(self) -> None:
        scene = app.build_paper_rt_rmq_scene((0.0, 0.0, 0.0, 0.0), block_size=1)
        rays = (
            app._paper_rt_ray(0, scene, *app._left_partial_ray_yz(1, scene)),
            app._paper_rt_ray(1, scene, *app._right_partial_ray_yz(2, scene)),
        )
        rows = ray_triangle_closest_hit_cpu(rays, scene.element_triangles)
        self.assertEqual(tuple((row["ray_id"], row["triangle_id"]) for row in rows), ((0, 1), (1, 2)))
        self.assertAlmostEqual(rows[0]["t"], 1.1)
        self.assertAlmostEqual(rows[1]["t"], 1.2)

    def test_prepared_phase_bulk_pack_preserves_y_and_z_coordinates(self) -> None:
        try:
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest("numpy is optional for local source-tree tests")

        class FakePreparedScene:
            packed_ray = None

            def ray_closest_hit_rows(self, rays):
                self.packed_ray = rays.records[0]
                return ({"ray_id": 7, "triangle_id": 0, "t": 1.0},)

        scene = app.build_paper_rt_rmq_scene((1.0, 2.0, 3.0, 4.0), block_size=2)
        phase = app.RtdlRtRmqRayPhase("same_block", (7,), (1.25,), (2.5,))
        fake_scene = FakePreparedScene()
        rows = app._closest_rows_by_prepared_phase(phase, scene, fake_scene)
        self.assertEqual(rows[7]["triangle_id"], 0)
        self.assertAlmostEqual(fake_scene.packed_ray.oy, 1.25)
        self.assertAlmostEqual(fake_scene.packed_ray.oz, 2.5)

    def test_paper_rt_lowering_payload_records_generic_rt_boundary(self) -> None:
        payload = app.run_app(
            "paper_rt_lowering_reference",
            dataset="repeated",
            value_count=128,
            query_count=41,
            seed=55,
            max_width=64,
            block_size=8,
            sample=False,
        )
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["mode"], "paper_rt_lowering_reference")
        self.assertIn("ray_triangle_closest_hit", payload["contract"])
        self.assertIn("app-side Python", payload["rt_design_boundary"])
        self.assertIn("pod-validated generic ray_triangle_closest_hit OptiX path", payload["optix_status"])

    def test_command_plan_names_future_pod_work(self) -> None:
        payload = app.run_app("command_plan")
        self.assertIn("future_pod_tasks", payload)
        self.assertIn("CuPy", " ".join(payload["future_pod_tasks"]))
        self.assertIn("generic ray_triangle_closest_hit", " ".join(payload["future_pod_tasks"]))
        self.assertIn("must not contain GPU-RMQ-specific app logic", payload["native_engine_rule"])

    def test_prepared_reuse_uses_generic_grouped_argmin_boundary(self) -> None:
        source = (ROOT / "examples" / "v2_0" / "research_benchmarks" / "gpu_rmq" / "rtdl_gpu_rmq_benchmark_app.py").read_text()
        self.assertIn("ray_closest_hit_grouped_argmin", source)
        self.assertIn("_query_prepared_batch_grouped_argmin", source)
        self.assertIn("runtime_grouped_argmin_used", source)
        self.assertIn("prepared_ray_batch_grouped_argmin", source)
        self.assertIn("prepared_grouped_argmin_inputs", source)
        self.assertIn("prepare_closest_hit_grouped_argmin_inputs", source)
        self.assertIn("prepare_optix_grouped_candidate_argmin", source)
        self.assertIn("generic_grouped_candidate_argmin", source)
        self.assertIn("two_scene_ray_closest_hit_prepared_grouped_argmin", source)
        self.assertIn("native_two_source_grouped_merge", source)
        self.assertIn("combined_scene", source)
        self.assertIn("combined_prepared_grouped_argmin", source)
        self.assertIn("native_combined_scene_grouped_argmin", source)
        self.assertIn("_PAPER_RT_GROUPED_ARGMIN_QUERY_THRESHOLD = 1", source)
        self.assertIn("runtime_grouped_argmin", source)
        self.assertIn("prepare_query_batch", source)
        self.assertIn("query_prepared_batch_arrays", source)
        self.assertIn("native_engine_customization\": False", source)

    def test_combined_scene_preserves_block_selector_precision(self) -> None:
        scene = app.build_paper_rt_rmq_scene(tuple(float(i % 17) for i in range(2048)), block_size=512)
        first_element = scene.element_triangles[0]
        first_combined_element = scene.combined_triangles[0]
        first_block = scene.block_triangles[0]
        first_combined_block = scene.combined_triangles[scene.value_count]
        self.assertEqual(first_combined_element.id, first_element.id)
        self.assertEqual(first_combined_block.id, scene.combined_block_triangle_id_offset)
        self.assertAlmostEqual(first_combined_element.y0, first_element.y0)
        self.assertAlmostEqual(first_combined_element.z0, first_element.z0 + scene.combined_element_z_offset)
        self.assertAlmostEqual(first_combined_block.y0, first_block.y0)
        self.assertAlmostEqual(first_combined_block.z0, first_block.z0)

    def test_cupy_modes_are_declared_but_optional(self) -> None:
        try:
            payload = app.run_app(
                "cupy_hierarchical",
                dataset="random",
                value_count=32,
                query_count=8,
                seed=7,
                max_width=8,
                block_size=4,
            )
        except RuntimeError as exc:
            self.assertIn("CuPy/CUDA is required", str(exc))
        else:
            self.assertEqual(payload["backend"], "cupy")
            self.assertTrue(payload["verification"]["matches_cpu_reference"])

    def test_author_code_plan_records_repo_and_generated_input_boundary(self) -> None:
        payload = app.run_app("author_code_plan")
        self.assertEqual(payload["author_code"]["repo"], "https://github.com/lakreis/GPU-RMQ")
        self.assertFalse(payload["claim_boundary"]["author_static_datasets_available"])
        self.assertIn(16, payload["author_algorithms"])
        self.assertIn(-6, payload["paper_workloads"]["range_distributions"])

    def test_author_saved_input_binary_reader_matches_cpu_oracle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            array_path = root / "array.bin"
            query_path = root / "queries.bin"
            array_path.write_bytes(struct.pack("<5f", 5.0, 2.0, 7.0, 2.0, 9.0))
            query_path.write_bytes(struct.pack("<6I", 0, 4, 2, 4, 3, 3))
            fixture = app.make_author_saved_input_fixture(
                array_bin=array_path,
                queries_bin=query_path,
                seed=7,
                value_count=5,
                query_count=3,
                index_width=32,
            )
            self.assertEqual(fixture.dataset, "author_saved_input")
            self.assertEqual(app.exact_rmq_cpu(fixture.values, fixture.queries)[0]["index"], 1)

    def test_author_time_csv_parser_normalizes_numeric_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "author.csv"
            csv_path.write_text(
                "dev,alg,nt,reps,n,bs,nb,q,lr,GPU_BSIZE,CG_GROUP_SIZE,CG_MEM_ALIGNMENT,timestamp,scan_threshold,XXX_CG_SIZE_LOG,XXX_CG_AMOUNT_LOG,t,q/s,ns/q,construction,outbuffer,tempbuffer,freeGPUMemCorrect,freeGPUMem,checkResult\n"
                "NVIDIA RTX 4090,[GPU] XXX,1,3,1048576,1,0,65536,-3,1024,0,0,2026-05-24T00:00:00Z,64,3,2,0.001,1000.0,12.5,0.5,1.0,2.0,1,100.0,5\n",
                encoding="utf-8",
            )
            payload = app.author_time_csv_payload(csv_path)
            self.assertEqual(payload["row_count"], 1)
            self.assertEqual(payload["rows"][0]["n"], 1048576)
            self.assertEqual(payload["rows"][0]["ns/q"], 12.5)
            self.assertEqual(payload["rows"][0]["checkResult"], 5)

    def test_author_time_csv_parser_handles_mixed_author_schemas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "author_mixed.csv"
            csv_path.write_text(
                "dev,alg,nt,reps,n,bs,nb,q,lr,GPU_BSIZE,CG_GROUP_SIZE,CG_MEM_ALIGNMENT,timestamp,t,q/s,ns/q,construction,outbuffer,tempbuffer,freeGPUMemCorrect,freeGPUMem,checkResult\n"
                "NVIDIA RTX,[GPU] BASE,16,7,65536,1,0,8192,-3,1024,0,0,2026-05-25T00:00:00Z,0.003292,17416701.49,57.416153,0,0,0,1,23503.4,5\n"
                "NVIDIA RTX,[GPU] XXX,16,7,65536,1,0,8192,-3,1024,0,0,2026-05-25T00:00:01Z,64,3,2,0.000138,415704946.66,2.405552,3.430927,0.008448,0,1,23503.4,5\n",
                encoding="utf-8",
            )
            payload = app.author_time_csv_payload(csv_path)
            self.assertEqual(payload["row_count"], 2)
            self.assertEqual(payload["rows"][0]["alg"], "[GPU] BASE")
            self.assertEqual(payload["rows"][0]["t"], 0.003292)
            self.assertEqual(payload["rows"][1]["alg"], "[GPU] XXX")
            self.assertEqual(payload["rows"][1]["scan_threshold"], 64)
            self.assertEqual(payload["rows"][1]["t"], 0.000138)

    def test_author_style_workload_mode_matches_cpu_reference(self) -> None:
        payload = app.run_app(
            "author_style_compare_local",
            value_count=1024,
            query_count=128,
            seed=2604,
            author_lr=-6,
            block_size=32,
            sample=False,
        )
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["author_style"]["lr"], -6)
        self.assertIn("not bit-identical", payload["author_style"]["semantic_match"])

    def test_paper_hybrid_hierarchy_matches_cpu_reference_without_rt_top(self) -> None:
        payload = app.run_app(
            "paper_hybrid_rtdl_partner",
            dataset="repeated",
            value_count=256,
            query_count=64,
            seed=2609,
            max_width=128,
            reduction_factor=32,
            scan_threshold=1024,
            sample=False,
            reuse_repeats=2,
        )
        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["mode"], "paper_hybrid_rtdl_partner")
        self.assertFalse(payload["execution_metadata"]["rt"]["rt_used"])
        self.assertIn("multi-level reduction hierarchy", payload["contract"])
        self.assertFalse(payload["execution_metadata"]["native_engine_customization"])

    def test_paper_hybrid_top_rt_interval_matches_author_style_formula(self) -> None:
        hierarchy = app.build_paper_hybrid_hierarchy(
            tuple(float(i % 11) for i in range(4096)),
            reduction_factor=32,
            scan_threshold=64,
        )
        self.assertGreater(hierarchy.top_level, 0)
        span = hierarchy.top_group_span
        self.assertEqual(
            app._paper_hybrid_top_rt_query(5, span * 3 + 7, hierarchy),
            (1, 2),
        )


if __name__ == "__main__":
    unittest.main()
