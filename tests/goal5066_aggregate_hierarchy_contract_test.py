from __future__ import annotations

from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_SOURCE = REPO_ROOT / "src" / "rtdsl" / "aggregate_hierarchy.py"

sys.path.insert(0, str(REPO_ROOT / "src"))

import rtdsl as rt


def _tiny_hierarchy() -> rt.AggregateHierarchy3D:
    return rt.aggregate_hierarchy_3d(
        point_x=[0.0, 1.0, 2.0],
        point_y=[0.0, 0.0, 0.0],
        point_z=[0.0, 1.0, 2.0],
        point_weight=[1.0, 2.0, 3.0],
        node_cx=[1.0, 1.0],
        node_cy=[0.0, 0.0],
        node_cz=[1.0, 1.0],
        node_half_size=[2.0, 1.0],
        node_weight=[6.0, 6.0],
        member_offsets=[0, 0, 3],
        member_indices=[0, 1, 2],
        child_offsets=[0, 1, 1],
        child_indices=[1],
        node_next_index=[-1, -1],
        node_resume_index=[-1, -1],
    )


class Goal5066AggregateHierarchyContractTest(unittest.TestCase):
    def test_public_symbols_are_exported_without_app_identity_names(self) -> None:
        expected = (
            "AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION",
            "AGGREGATE_HIERARCHY_3D_API_MATURITY",
            "SizeDistanceOpening",
            "ContinuationPayloadOpening",
            "AggregateHierarchy3D",
            "PreparedAggregateHierarchy3D",
            "AggregateFrontierReduceSpec3D",
            "aggregate_hierarchy_3d",
            "prepare_aggregate_hierarchy_3d",
            "aggregate_frontier_reduce_spec_3d",
            "describe_aggregate_hierarchy_3d_contract",
            "validate_aggregate_hierarchy_3d_contract",
        )
        for name in expected:
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__, name)

        public_payload = "\n".join(rt.__all__) + "\n" + "\n".join(dir(rt))
        for forbidden in ("Author", "Treelogy", "RTBH", "BarnesHut", "author-optix-payload"):
            self.assertNotIn(forbidden, public_payload)

        module_text = MODULE_SOURCE.read_text(encoding="utf-8")
        for forbidden in ("Treelogy", "RTBH", "BarnesHut", "author-optix-payload"):
            self.assertNotIn(forbidden, module_text)

    def test_contract_authorizes_only_reference_execution_and_no_speedup_claims(self) -> None:
        contract = rt.validate_aggregate_hierarchy_3d_contract()

        self.assertEqual(rt.AGGREGATE_HIERARCHY_3D_CONTRACT_VERSION, contract["contract_version"])
        self.assertEqual("reference_and_optional_numba_cpu_executor_no_native_backend", contract["api_maturity"])
        self.assertTrue(contract["reference_execution_authorized"])
        self.assertFalse(contract["native_backend_symbols_authorized"])
        self.assertFalse(contract["app_specific_schema_allowed"])
        self.assertFalse(contract["paper_reproduction_claim_authorized"])
        self.assertFalse(contract["whole_program_speedup_claim_authorized"])
        self.assertIn("size_distance_opening", contract["opening_policies"])
        self.assertIn("continuation_payload_opening", contract["opening_policies"])
        self.assertIn("aggregate_count", contract["supported_reducers"])

    def test_valid_hierarchy_prepare_and_reduce_spec_metadata(self) -> None:
        hierarchy = _tiny_hierarchy()
        prepared = rt.prepare_aggregate_hierarchy_3d(hierarchy)
        spec = rt.aggregate_frontier_reduce_spec_3d(
            prepared,
            opening=rt.SizeDistanceOpening(max_ratio=0.5),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )

        hierarchy_meta = hierarchy.to_metadata()
        self.assertEqual(3, hierarchy_meta["point_count"])
        self.assertEqual(2, hierarchy_meta["node_count"])
        self.assertEqual(("node_next_index", "node_resume_index"), hierarchy_meta["continuation_columns"])
        self.assertFalse(hierarchy_meta["backend_execution_authorized"])

        prepared_meta = prepared.to_metadata()
        self.assertEqual("contract_only", prepared_meta["backend"])
        self.assertFalse(prepared_meta["device_resident_candidate"])
        self.assertTrue(prepared_meta["materializes_host_rows_for_bridge"])

        spec_meta = spec.to_metadata()
        self.assertEqual("aggregate_frontier_reduce_3d", spec_meta["spec"])
        self.assertEqual("aggregate_count", spec_meta["reducer"])
        self.assertEqual("size_distance_opening", spec_meta["opening"]["policy"])
        self.assertFalse(spec_meta["backend_execution_authorized"])
        self.assertFalse(spec_meta["app_specific_reducer_allowed"])

    def test_reducer_contract_accepts_non_force_aggregate_count(self) -> None:
        hierarchy = _tiny_hierarchy()
        prepared = rt.prepare_aggregate_hierarchy_3d(hierarchy)
        spec = rt.aggregate_frontier_reduce_spec_3d(
            prepared,
            opening=rt.SizeDistanceOpening(max_ratio=1.0),
            reducer=rt.AGGREGATE_HIERARCHY_3D_REDUCER_AGGREGATE_COUNT,
        )

        self.assertEqual("aggregate_count", spec.reducer)
        with self.assertRaisesRegex(ValueError, "unsupported reducer"):
            rt.aggregate_frontier_reduce_spec_3d(
                prepared,
                opening=rt.SizeDistanceOpening(max_ratio=1.0),
                reducer="inverse_square_force_field_app",
            )

    def test_continuation_payload_opening_is_generic_and_requires_ratio(self) -> None:
        opening = rt.ContinuationPayloadOpening(max_ratio=0.5)
        metadata = opening.to_metadata()

        self.assertEqual(rt.AGGREGATE_HIERARCHY_3D_OPENING_CONTINUATION_PAYLOAD, metadata["policy"])
        self.assertEqual(("node_next_index", "node_rope_index"), metadata["requires_continuation_columns"])
        self.assertFalse(metadata["app_specific_policy_allowed"])
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            rt.ContinuationPayloadOpening(max_ratio=0.0)

    def test_invalid_offsets_and_indices_fail_closed(self) -> None:
        kwargs = dict(
            point_x=[0.0],
            point_y=[0.0],
            point_z=[0.0],
            point_weight=[1.0],
            node_cx=[0.0],
            node_cy=[0.0],
            node_cz=[0.0],
            node_half_size=[1.0],
            node_weight=[1.0],
            member_offsets=[0, 1],
            member_indices=[0],
            child_offsets=[0, 0],
            child_indices=[],
        )
        with self.assertRaisesRegex(ValueError, "must start at zero"):
            rt.aggregate_hierarchy_3d(**{**kwargs, "member_offsets": [1, 1]})
        with self.assertRaisesRegex(ValueError, "monotonic"):
            rt.aggregate_hierarchy_3d(**{**kwargs, "member_offsets": [0, -1]})
        with self.assertRaisesRegex(ValueError, "outside"):
            rt.aggregate_hierarchy_3d(**{**kwargs, "member_indices": [2]})
        with self.assertRaisesRegex(ValueError, "outside"):
            rt.aggregate_hierarchy_3d(**{**kwargs, "child_offsets": [0, 1], "child_indices": [1]})

    def test_invalid_continuation_and_opening_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "finite and positive"):
            rt.SizeDistanceOpening(max_ratio=0.0)
        with self.assertRaisesRegex(ValueError, "node_next_index values"):
            rt.aggregate_hierarchy_3d(
                point_x=[0.0],
                point_y=[0.0],
                point_z=[0.0],
                point_weight=[1.0],
                node_cx=[0.0],
                node_cy=[0.0],
                node_cz=[0.0],
                node_half_size=[1.0],
                node_weight=[1.0],
                member_offsets=[0, 1],
                member_indices=[0],
                child_offsets=[0, 0],
                child_indices=[],
                node_next_index=[1],
            )


if __name__ == "__main__":
    unittest.main()
