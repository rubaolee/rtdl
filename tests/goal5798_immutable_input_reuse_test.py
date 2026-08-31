from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5798ImmutableInputReuseTest(unittest.TestCase):
    def test_old_native_abis_remain_conservative_and_successors_are_explicit(self):
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2", api)
        self.assertIn(
            "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3", api)
        self.assertGreaterEqual(api.count("reuse_cached_sources != 0u"), 1)
        self.assertGreaterEqual(api.count("false,"), 2)

    def test_native_reuse_requires_an_exact_uploaded_predecessor(self):
        core = (ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        self.assertIn("uploaded_query_count", core)
        self.assertIn(
            "query_count != prepared->uploaded_query_count", core)
        self.assertIn(
            "prepared->cached_sources.size() != source_count", core)
        self.assertIn(
            "source-cache reuse is invalid", core)
        self.assertIn(
            "query reuse lacks an exact uploaded predecessor", core)

    def test_python_identity_cache_is_retired_before_state_transition(self):
        relation = (
            ROOT / "src/rtdsl/v4_bounded_relation_prepared_runtime.py"
        ).read_text(encoding="utf-8")
        triangle = (
            ROOT / "src/rtdsl/v4_triangle_reduction_prepared_runtime.py"
        ).read_text(encoding="utf-8")
        self.assertIn("and self._cached_source_native is not None", relation)
        self.assertIn("self._cached_source_object = None", relation)
        self.assertIn("next_cached_query_inputs = None", triangle)
        self.assertIn("self._cached_queries = None", triangle)
        self.assertIn("if not cache_hit:", relation)
        self.assertIn("if not cache_hit:", triangle)

    def test_formal_oracle_preserves_exactness_without_reboxing_python_ints(self):
        worker = (
            ROOT / "experiments/goal5798_premeasurement/rtdl_worker.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'expected_relation_rows = (\n        tuple(tuple(value)', worker)
        self.assertIn(
            'expected_per_ray = (\n        tuple(task_value["expected_per_ray"])',
            worker)
        self.assertIn(
            'per_ray = tuple(result.details["per_ray_u64"])', worker)
        self.assertNotIn(
            '[int(value) for value in result.details["per_ray_u64"]]', worker)
        self.assertNotIn(
            'output = [list(value) for value in result.output]', worker)

    def test_pyoptix_baseline_uses_bulk_numpy_materialization(self):
        worker = (
            ROOT / "experiments/goal5798_premeasurement/pyoptix_worker.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'rows = sorted(set(map(tuple, raw.tolist())))', worker)
        self.assertIn(
            'per_ray = cp.asnumpy(self.d_per_ray).tolist()', worker)
        self.assertNotIn(
            'sorted({(int(row[0]), int(row[1])) for row in raw})', worker)
        self.assertNotIn(
            '[int(value) for value in cp.asnumpy(self.d_per_ray)]', worker)


if __name__ == "__main__":
    unittest.main()
