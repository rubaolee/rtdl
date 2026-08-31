from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-barneshut-paper"
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Goal5067RtBarnesHutAggregateHierarchyAdapterTest(unittest.TestCase):
    def test_adapter_contract_is_app_owned_and_backend_free(self) -> None:
        adapter = _load_module("rtbh_aggregate_hierarchy_adapter_contract", APP_DIR / "aggregate_hierarchy_adapter.py")
        contract = adapter.describe_adapter_contract()

        self.assertEqual(
            "rt_barneshut_prepared_arrays_to_generic_aggregate_hierarchy_3d_v1",
            contract["adapter_contract"],
        )
        self.assertEqual(rt.AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION, contract["output_contract"])
        self.assertFalse(contract["backend_execution_authorized"])
        self.assertIn("source_leaf_node_index", contract["generic_descriptor_fields_promoted"])
        self.assertIn("node_subtree_end_index", contract["generic_descriptor_fields_promoted"])
        self.assertEqual("available_via_public_generic_rtdl_api", contract["app_owned_numba_parity_mode"])
        self.assertEqual("available_via_public_generic_rtdl_api", contract["app_owned_force_output_bridge"])
        self.assertIn("no_cuda", contract["claim_boundary"])

    def test_synthetic_author_prepared_arrays_map_to_generic_hierarchy(self) -> None:
        adapter = _load_module("rtbh_aggregate_hierarchy_adapter_synthetic", APP_DIR / "aggregate_hierarchy_adapter.py")
        author_reference = _load_module("rtbh_author_contract_reference_for_goal5067", APP_DIR / "author_contract_reference.py")
        diag = _load_module(
            "goal2547_rt_barneshut_prepared_reader_for_goal5067",
            ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
        )

        bodies = author_reference.make_synthetic_bodies(64)
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "prepared.json"
            author_reference.write_prepared_arrays(prepared_path, bodies)
            prepared = diag.read_prepared_arrays_3d(prepared_path)

        packet = adapter.prepared_arrays_to_aggregate_hierarchy(prepared)
        hierarchy = packet["hierarchy"]
        prepared_hierarchy = packet["prepared_hierarchy"]
        reduce_spec = packet["reduce_spec"]
        metadata = packet["metadata"]

        self.assertIsInstance(hierarchy, rt.AggregateHierarchy3D)
        self.assertIsInstance(prepared_hierarchy, rt.PreparedAggregateHierarchy3D)
        self.assertIsInstance(reduce_spec, rt.AggregateFrontierReduceSpec3D)
        self.assertEqual(len(prepared["point_x"]), hierarchy.point_count)
        self.assertEqual(len(prepared["node_cx"]), hierarchy.node_count)
        self.assertEqual(tuple(prepared["member_offsets"]), hierarchy.member_offsets)
        self.assertEqual(tuple(prepared["child_offsets"]), hierarchy.child_offsets)
        self.assertEqual("size_distance_opening", reduce_spec.opening.to_metadata()["policy"])
        self.assertEqual(0.5, reduce_spec.opening.max_ratio)
        self.assertEqual(rt.AGGREGATE_HIERARCHY_3D_REDUCER_INVERSE_SQUARE_SCALAR_SUM, reduce_spec.reducer)
        self.assertFalse(metadata["backend_execution_authorized"])
        self.assertFalse(metadata["paper_reproduction_claim_authorized"])
        self.assertIn("source_leaf_node_index", metadata["generic_descriptor_fields_promoted"])
        self.assertIn("node_subtree_end_index", metadata["generic_descriptor_fields_promoted"])
        self.assertIn("source_leaf_node_index", hierarchy.to_metadata()["descriptor_columns"])
        self.assertIn("node_subtree_end_index", hierarchy.to_metadata()["descriptor_columns"])

    def test_author_binary_continuation_columns_map_to_generic_names(self) -> None:
        adapter = _load_module("rtbh_aggregate_hierarchy_adapter_author_binary", APP_DIR / "aggregate_hierarchy_adapter.py")
        payload = {
            "schema": "generic_aggregate_frontier_inverse_square_scalar_sum_3d_prepared_arrays_v1",
            "contract_source": "rt_barneshut_author_binary_prepared_state_v1",
            "points": [
                {"id": 0, "mass": 10.0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 1, "mass": 20.0, "x": 1.0, "y": 0.0, "z": 0.0},
            ],
            "nodes": [
                {
                    "id": 1,
                    "cx": 0.5,
                    "cy": 0.0,
                    "cz": 0.0,
                    "half_size": 4.0,
                    "mass": 30.0,
                    "member_ids": [],
                    "child_ids": [2],
                    "dfs_index": 0,
                    "resume_index": None,
                    "is_leaf": False,
                    "author_device": {"next_prim_id": 1, "auto_rope_prim_id": 0},
                },
                {
                    "id": 2,
                    "cx": 0.5,
                    "cy": 0.0,
                    "cz": 0.0,
                    "half_size": 2.0,
                    "mass": 30.0,
                    "member_ids": [0, 1],
                    "child_ids": [],
                    "dfs_index": 1,
                    "resume_index": None,
                    "is_leaf": True,
                    "author_device": {"next_prim_id": 2, "auto_rope_prim_id": -887151303},
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "author_binary_prepared.json"
            prepared_path.write_text(json.dumps(payload), encoding="utf-8")
            packet = adapter.read_prepared_arrays_as_aggregate_hierarchy(prepared_path)

        hierarchy = packet["hierarchy"]
        reduce_spec = packet["reduce_spec"]
        self.assertEqual((1, -1), hierarchy.node_next_index)
        self.assertEqual((-1, -1), hierarchy.node_rope_index)
        self.assertEqual((-1, -1), hierarchy.node_resume_index)
        self.assertEqual("continuation_payload_opening", reduce_spec.opening.to_metadata()["policy"])
        self.assertEqual("rt_barneshut_author_binary_prepared_state_v1", packet["source_contract"])

    def test_adapter_does_not_use_torch_cuda_or_native_execution(self) -> None:
        source = (APP_DIR / "aggregate_hierarchy_adapter.py").read_text(encoding="utf-8")
        for forbidden in ("import torch", "load_inline", "ctypes", "rtdl_optix"):
            self.assertNotIn(forbidden, source)
        self.assertIn("app_owned_fields_not_promoted_to_core", source)

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba is required for app-owned parity mode")
    def test_app_owned_numba_parity_mode_uses_public_generic_executors(self) -> None:
        adapter = _load_module("rtbh_aggregate_hierarchy_adapter_numba_parity", APP_DIR / "aggregate_hierarchy_adapter.py")
        author_reference = _load_module("rtbh_author_contract_reference_for_goal5074", APP_DIR / "author_contract_reference.py")
        diag = _load_module(
            "goal2547_rt_barneshut_prepared_reader_for_goal5074",
            ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
        )

        bodies = author_reference.make_synthetic_bodies(64)
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "prepared.json"
            author_reference.write_prepared_arrays(prepared_path, bodies)
            prepared = diag.read_prepared_arrays_3d(prepared_path)

        result = adapter.run_generic_aggregate_frontier_numba_parity(prepared)

        self.assertEqual("generic_aggregate_frontier_numba_parity", result["mode"])
        self.assertEqual("reference", result["reference_backend"])
        self.assertEqual("numba", result["candidate_backend"])
        self.assertTrue(result["comparison"]["match"])
        self.assertEqual(0, result["comparison"]["mismatch_count"])
        self.assertEqual(len(prepared["point_x"]), result["comparison"]["source_count"])
        self.assertIn("uses_public_generic_rtdl_aggregate_hierarchy_api", result["claim_boundary"])
        self.assertIn("not_author_binary_comparator", result["claim_boundary"])
        self.assertIn("not_performance_claim", result["claim_boundary"])

    @unittest.skipUnless(rt.aggregate_frontier_reduce_numba_available(), "Numba is required for force bridge mode")
    def test_app_owned_force_output_bridge_matches_author_contract_reference(self) -> None:
        adapter = _load_module("rtbh_aggregate_hierarchy_adapter_force_bridge", APP_DIR / "aggregate_hierarchy_adapter.py")
        author_reference = _load_module("rtbh_author_contract_reference_for_goal5075", APP_DIR / "author_contract_reference.py")
        diag = _load_module(
            "goal2547_rt_barneshut_prepared_reader_for_goal5075",
            ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
        )

        bodies = author_reference.make_synthetic_bodies(64)
        expected = {
            int(row["source_id"]): float(row["scalar_force"])
            for row in author_reference.compute_author_contract_forces(bodies)["force_rows"]
        }
        with tempfile.TemporaryDirectory() as tmp:
            prepared_path = Path(tmp) / "prepared.json"
            force_output = Path(tmp) / "generic_numba_forces.txt"
            author_reference.write_prepared_arrays(prepared_path, bodies)
            prepared = diag.read_prepared_arrays_3d(prepared_path)
            result = adapter.run_generic_aggregate_frontier_numba_force_bridge(
                prepared,
                force_output=force_output,
            )

            observed = {}
            for line in force_output.read_text(encoding="utf-8").splitlines():
                source_id, scalar_force = line.split()
                observed[int(source_id)] = float(scalar_force)

        self.assertEqual("generic_aggregate_frontier_numba_force_bridge", result["mode"])
        self.assertEqual("numba", result["candidate_backend"])
        self.assertTrue(result["comparison_to_reference_executor_force_rows"]["match"])
        self.assertEqual(0, result["comparison_to_reference_executor_force_rows"]["mismatch_count"])
        self.assertEqual(set(expected), set(observed))
        for source_id, expected_value in expected.items():
            self.assertAlmostEqual(expected_value, observed[source_id], places=6)
        self.assertIn("maps_generic_scalar_reducer_to_app_scalar_force_rows", result["claim_boundary"])
        self.assertIn("not_author_binary_comparator", result["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
