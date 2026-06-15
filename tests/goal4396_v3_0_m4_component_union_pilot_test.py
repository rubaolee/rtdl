from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4396V30M4ComponentUnionPilotTest(unittest.TestCase):
    def test_two_pilot_graphs_reuse_same_generic_continuation(self) -> None:
        graphs = rt.m4_component_union_pilot_graphs()
        self.assertEqual(len(graphs), 2)
        operations = [
            node.operation
            for graph in graphs
            for node in graph.nodes
            if isinstance(node, rt.ContinuationNode)
        ]
        self.assertEqual(operations, [rt.M4_COMPONENT_UNION_OPERATION, rt.M4_COMPONENT_UNION_OPERATION])
        self.assertEqual(set(graph.graph_id for graph in graphs), {"fixed_radius_component_pilot", "generic_edge_component_pilot"})

    def test_pilot_graphs_are_no_execution_prepared_graphs(self) -> None:
        for graph in rt.m4_component_union_pilot_graphs():
            payload = graph.to_metadata()
            self.assertFalse(payload["executes"])
            self.assertFalse(payload["native_execution_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertEqual(payload["claim_boundary"]["app_specific_native_engine_authorized"], False)
            self.assertIn("component_ids", payload["value_table"])

    def test_pilot_graphs_do_not_use_partner_nodes_or_auto_selection(self) -> None:
        for graph in rt.m4_component_union_pilot_graphs():
            node_types = [node.to_metadata()["node_type"] for node in graph.nodes]
            self.assertNotIn("PartnerNode", node_types)
            self.assertFalse(graph.partner_policy.auto_selection_allowed)
            self.assertFalse(graph.partner_policy.explicit_partner_required)

    def test_pilot_graphs_share_component_edge_contract(self) -> None:
        for graph in rt.m4_component_union_pilot_graphs():
            primitive_nodes = [node for node in graph.nodes if isinstance(node, rt.PrimitiveNode)]
            self.assertEqual(len(primitive_nodes), 1)
            primitive = primitive_nodes[0]
            self.assertEqual(primitive.same_contract_key, "component_edge_contract_v1")
            self.assertEqual(primitive.backend_contract.contract_id, "component_edge_contract_v1")
            self.assertEqual(primitive.backend_contract.output_contract, ("component_ids",))

    def test_local_reuse_summary_requires_pod_evidence_for_completion(self) -> None:
        summary = rt.validate_m4_component_union_reuse()
        self.assertEqual(summary["status"], rt.M4_LOCAL_PREP_STATUS)
        self.assertEqual(summary["graph_count"], 2)
        self.assertEqual(summary["shared_continuation_operation"], rt.M4_COMPONENT_UNION_OPERATION)
        self.assertFalse(summary["partner_nodes_present"])
        self.assertTrue(summary["pod_evidence_required"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
