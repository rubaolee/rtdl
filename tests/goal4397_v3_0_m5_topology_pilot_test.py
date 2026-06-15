from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4397V30M5TopologyPilotTest(unittest.TestCase):
    def test_two_topology_pilot_graphs_share_contract_and_compaction(self) -> None:
        graphs = rt.m5_topology_pilot_graphs()
        self.assertEqual(len(graphs), 2)
        self.assertEqual(
            {graph.graph_id for graph in graphs},
            {"point_location_topology_pilot", "edge_intersection_topology_pilot"},
        )
        for graph in graphs:
            primitive_nodes = [node for node in graph.nodes if isinstance(node, rt.PrimitiveNode)]
            continuation_nodes = [node for node in graph.nodes if isinstance(node, rt.ContinuationNode)]
            self.assertEqual(len(primitive_nodes), 1)
            self.assertEqual(len(continuation_nodes), 1)
            self.assertEqual(primitive_nodes[0].same_contract_key, rt.M5_TOPOLOGY_CONTRACT_KEY)
            self.assertEqual(continuation_nodes[0].operation, rt.M5_TOPOLOGY_COMPACTION_OPERATION)

    def test_topology_pilot_graphs_are_no_execution_and_no_partner(self) -> None:
        for graph in rt.m5_topology_pilot_graphs():
            payload = graph.to_metadata()
            self.assertFalse(payload["executes"])
            self.assertFalse(payload["native_execution_authorized"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertEqual(payload["claim_boundary"]["raw_optix_callback_user_api_authorized"], False)
            self.assertFalse(any(node.to_metadata()["node_type"] == "PartnerNode" for node in graph.nodes))

    def test_topology_outputs_are_generic_streams_and_summaries(self) -> None:
        for graph in rt.m5_topology_pilot_graphs():
            value_table = graph.value_table
            self.assertEqual(value_table["topology_face_ids"].kind, "topology_stream")
            self.assertEqual(value_table["topology_event_mask"].kind, "status")
            self.assertEqual(value_table["selected_face_ids"].kind, "summary")
            self.assertEqual(value_table["topology_face_ids"].overflow_policy, "fail_closed")
            self.assertEqual(value_table["selected_face_ids"].producer, "topology_compaction")

    def test_topology_summary_requires_author_and_pod_evidence(self) -> None:
        summary = rt.validate_m5_topology_pilots()
        self.assertEqual(summary["status"], rt.M5_LOCAL_PREP_STATUS)
        self.assertEqual(summary["graph_count"], 2)
        self.assertEqual(summary["shared_topology_contract"], rt.M5_TOPOLOGY_CONTRACT_KEY)
        self.assertEqual(summary["shared_continuation_operation"], rt.M5_TOPOLOGY_COMPACTION_OPERATION)
        self.assertTrue(summary["author_code_comparison_required"])
        self.assertTrue(summary["pod_evidence_required"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
