from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _execution_contract(backend: str = "reference"):
    hierarchy = rt.aggregate_hierarchy_3d(
        point_x=[0.0, 1.0, 2.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 1.0, 2.0],
        point_weight=[1.0, 2.0, 3.0],
        node_cx=[1.0, 0.0, 1.5],
        node_cy=[0.0, 0.0, 0.0],
        node_cz=[1.0, 0.0, 1.5],
        node_half_size=[2.0, 0.5, 0.5],
        node_weight=[6.0, 1.0, 5.0],
        member_offsets=[0, 0, 1, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 2, 2, 2],
        child_indices=[1, 2],
        source_leaf_node_index=[1, 2, 2],
        node_subtree_end_index=[3, 2, 3],
    )
    prepared = rt.prepare_aggregate_hierarchy_3d(hierarchy)
    spec = rt.aggregate_frontier_reduce_spec_3d(
        prepared,
        opening=rt.SizeDistanceOpening(max_ratio=0.5),
        reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
    )
    return rt.aggregate_frontier_reduce_execution_contract_3d(
        spec,
        backend=backend,
        max_output_rows=3,
    )


class Goal5069AggregateFrontierReduceExecutionContractTest(unittest.TestCase):
    def test_public_execution_contract_exports_are_available(self) -> None:
        for name in (
            "AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT",
            "AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS",
            "AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS",
            "AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS_REFERENCE",
            "AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA",
            "AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS",
            "AggregateFrontierReduceExecutionContract3D",
            "aggregate_frontier_reduce_execution_contract_3d",
            "aggregate_frontier_reduce_reference_3d",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__, name)

    def test_execution_contract_authorizes_only_reference_backend(self) -> None:
        for backend in rt.AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS:
            contract = _execution_contract(backend=backend)
            metadata = contract.to_metadata()
            expected_status = rt.AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS[backend]

            self.assertEqual(rt.AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT, metadata["contract_version"])
            self.assertEqual(backend, metadata["backend"])
            self.assertEqual(expected_status, metadata["backend_status"])
            self.assertEqual(backend in ("reference", "numba"), metadata["backend_execution_authorized"])
            self.assertEqual(backend == "reference", metadata["reference_execution_authorized"])
            self.assertEqual(backend == "numba", metadata["numba_execution_authorized"])
            self.assertFalse(metadata["native_backend_symbols_authorized"])
            self.assertEqual(tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA), metadata["output_schema"])
            self.assertIn("aggregate_count", metadata["reference_supported_reducers"])
            self.assertIn("aggregate_count", metadata["numba_supported_reducers"])
            self.assertIn("source_leaf_node_index", metadata["required_descriptor_columns"])
            self.assertIn("node_subtree_end_index", metadata["required_descriptor_columns"])
            self.assertEqual("fail_closed_before_result_materialization", metadata["overflow_policy"])

    def test_execution_contract_is_reflected_in_hierarchy_contract_description(self) -> None:
        contract = rt.describe_aggregate_hierarchy_3d_contract()

        self.assertEqual(
            rt.AGGREGATE_FRONTIER_REDUCE_3D_EXECUTION_CONTRACT,
            contract["execution_contract"],
        )
        self.assertEqual(tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_BACKENDS), contract["execution_backends"])
        self.assertEqual(dict(rt.AGGREGATE_FRONTIER_REDUCE_3D_BACKEND_STATUS), contract["execution_backend_status"])
        self.assertEqual(
            tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_REFERENCE_REDUCERS),
            contract["reference_supported_reducers"],
        )
        self.assertEqual(
            tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_NUMBA_REDUCERS),
            contract["numba_supported_reducers"],
        )
        self.assertEqual(tuple(rt.AGGREGATE_FRONTIER_REDUCE_3D_OUTPUT_SCHEMA), contract["execution_output_schema"])
        self.assertTrue(contract["reference_execution_authorized"])
        self.assertTrue(contract["numba_execution_authorized"])
        self.assertFalse(contract["native_backend_symbols_authorized"])

    def test_execution_contract_rejects_unsupported_backend_and_overflow_policy(self) -> None:
        contract = _execution_contract()
        spec = contract.spec
        with self.assertRaisesRegex(ValueError, "unsupported backend"):
            rt.aggregate_frontier_reduce_execution_contract_3d(spec, backend="author_payload")
        with self.assertRaisesRegex(ValueError, "unsupported overflow_policy"):
            rt.aggregate_frontier_reduce_execution_contract_3d(spec, overflow_policy="partial_rows_allowed")
        with self.assertRaisesRegex(ValueError, "max_output_rows"):
            rt.aggregate_frontier_reduce_execution_contract_3d(spec, max_output_rows=-1)

    def test_public_module_has_no_app_identity_or_backend_implementation_claim(self) -> None:
        source = (REPO_ROOT / "src" / "rtdsl" / "aggregate_hierarchy.py").read_text(encoding="utf-8")
        for forbidden in ("BarnesHut", "Treelogy", "RTBH", "author-optix-payload", "load_inline", "import torch"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
