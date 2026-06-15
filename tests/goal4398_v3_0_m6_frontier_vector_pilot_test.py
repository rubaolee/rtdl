from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4398V30M6FrontierVectorPilotTest(unittest.TestCase):
    def test_two_frontier_pilot_graphs_share_vector_sum_continuation(self) -> None:
        graphs = rt.m6_frontier_vector_pilot_graphs()
        self.assertEqual(len(graphs), 2)
        self.assertEqual(
            {graph.graph_id for graph in graphs},
            {"aggregate_frontier_vector_pilot", "generic_frontier_vector_pilot"},
        )
        for graph in graphs:
            continuation_nodes = [node for node in graph.nodes if isinstance(node, rt.ContinuationNode)]
            self.assertEqual(len(continuation_nodes), 1)
            self.assertEqual(continuation_nodes[0].operation, rt.M6_VECTOR_SUM_OPERATION)

    def test_frontier_pilot_graphs_are_no_execution_and_no_partner(self) -> None:
        for graph in rt.m6_frontier_vector_pilot_graphs():
            payload = graph.to_metadata()
            self.assertFalse(payload["executes"])
            self.assertFalse(payload["native_execution_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertFalse(any(node.to_metadata()["node_type"] == "PartnerNode" for node in graph.nodes))

    def test_frontier_pilot_graphs_share_contract_and_outputs(self) -> None:
        for graph in rt.m6_frontier_vector_pilot_graphs():
            primitive_nodes = [node for node in graph.nodes if isinstance(node, rt.PrimitiveNode)]
            self.assertEqual(len(primitive_nodes), 1)
            primitive = primitive_nodes[0]
            self.assertEqual(primitive.same_contract_key, rt.M6_FRONTIER_CONTRACT_KEY)
            self.assertEqual(primitive.backend_contract.contract_id, rt.M6_FRONTIER_CONTRACT_KEY)
            self.assertIn("frontier_group_ids", graph.value_table)
            self.assertIn("vector_sum_x", graph.value_table)
            self.assertIn("vector_sum_y", graph.value_table)
            self.assertEqual(graph.value_table["vector_sum_x"].producer, "frontier_vector_sum")

    def test_frontier_summary_requires_pod_evidence(self) -> None:
        summary = rt.validate_m6_frontier_vector_pilots()
        self.assertEqual(summary["status"], rt.M6_LOCAL_PREP_STATUS)
        self.assertEqual(summary["graph_count"], 2)
        self.assertEqual(summary["shared_frontier_contract"], rt.M6_FRONTIER_CONTRACT_KEY)
        self.assertEqual(summary["shared_continuation_operation"], rt.M6_VECTOR_SUM_OPERATION)
        self.assertFalse(summary["partner_nodes_present"])
        self.assertTrue(summary["pod_evidence_required"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
