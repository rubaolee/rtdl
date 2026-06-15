from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4394V30M2ExecutionGraphSkeletonTest(unittest.TestCase):
    def test_valid_no_execution_prepared_graph_metadata(self) -> None:
        graph = _minimal_prepared_graph()
        payload = graph.to_metadata()

        self.assertEqual(payload["ir_version"], rt.V3_EXECUTION_GRAPH_IR_VERSION)
        self.assertEqual(payload["status"], rt.V3_EXECUTION_GRAPH_STATUS)
        self.assertFalse(payload["executes"])
        self.assertFalse(payload["native_execution_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertEqual(payload["state"], "validated")
        self.assertIn("candidate_ids", payload["value_table"])
        self.assertEqual(payload["claim_boundary"]["public_speedup_authorized"], False)

    def test_claim_boundary_rejects_any_authorized_flag(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "public_speedup_authorized"):
            rt.ClaimBoundary(public_speedup_authorized=True)

    def test_partner_policy_requires_explicit_best_partner_and_numba_reference(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "best_partner"):
            rt.PartnerPolicy(
                explicit_partner_required=True,
                benchmark_requires_dual_partner_rows=True,
                numba_reference_required=True,
                partner_timing_separated=True,
            )

        with self.assertRaisesRegex(rt.GraphValidationError, "Numba reference"):
            rt.PartnerPolicy(
                explicit_partner_required=True,
                best_partner="cupy",
                benchmark_requires_dual_partner_rows=True,
                partner_timing_separated=True,
            )

        policy = rt.PartnerPolicy(
            explicit_partner_required=True,
            best_partner="cupy",
            benchmark_requires_dual_partner_rows=True,
            numba_reference_required=True,
            partner_timing_separated=True,
        )
        self.assertEqual(policy.to_metadata()["best_partner"], "cupy")

    def test_device_resident_values_require_stream_binding(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "stream binding"):
            rt.GraphValue(
                name="device_scores",
                kind="summary",
                dtype="float64",
                shape=("n",),
                storage="cuda",
                residency="device_resident",
                lifetime="native_owned",
            )

        value = rt.GraphValue(
            name="device_scores",
            kind="summary",
            dtype="float64",
            shape=("n",),
            storage="cuda",
            residency="device_resident",
            lifetime="native_owned",
            stream_binding=rt.StreamBinding(
                stream_id="main_stream",
                ordering="same_stream",
                evidence=("cuda_event_pair",),
            ),
        )
        self.assertEqual(value.stream_binding.ordering, "same_stream")

    def test_public_names_reject_app_specific_tokens(self) -> None:
        for name in ("RayJoinGraph", "rt_dbscan_plan", "barnes_hut_force_node", "robot_collision_api"):
            with self.assertRaises(rt.GraphValidationError, msg=name):
                rt.validate_v3_public_name(name)

        rt.validate_v3_public_name("PrimitiveNode")
        rt.validate_v3_public_name("closed_shape_boundary_event")

    def test_graph_rejects_missing_value_references_and_duplicate_producers(self) -> None:
        graph = _minimal_prepared_graph()
        valid_value_names = set(graph.value_table.keys())
        self.assertEqual(valid_value_names, {"source_geometry", "query_geometry", "candidate_ids"})

        bad_node = _primitive_node(outputs=("missing_output",))
        with self.assertRaisesRegex(rt.GraphValidationError, "not a graph value"):
            rt.prepare_graph(
                graph_id="missing_output_graph",
                values=graph.values,
                nodes=(bad_node,),
                phase_markers=_required_phases(),
                target_backends=("optix",),
            )

        duplicate_node = _primitive_node(node_id="candidate_producer_two")
        with self.assertRaisesRegex(rt.GraphValidationError, "exactly one producing node"):
            rt.prepare_graph(
                graph_id="duplicate_output_graph",
                values=graph.values,
                nodes=(*graph.nodes, duplicate_node),
                phase_markers=_required_phases(),
                target_backends=("optix",),
            )

    def test_partner_node_requires_graph_level_partner_policy(self) -> None:
        stream = rt.StreamBinding(
            stream_id="main_stream",
            ordering="same_stream",
            evidence=("cuda_event_pair",),
        )
        values = (
            rt.GraphValue(
                name="candidate_ids",
                kind="candidate_stream",
                dtype="int64",
                shape=("n",),
                storage="cuda",
                residency="device_resident",
                lifetime="native_owned",
                stream_binding=stream,
            ),
            rt.GraphValue(
                name="summary_counts",
                kind="partner_output",
                dtype="int64",
                shape=("groups",),
                storage="cuda",
                residency="device_resident",
                lifetime="partner_owned",
                stream_binding=stream,
                producer="partner_count",
            ),
        )
        partner = rt.PartnerNode(
            node_id="partner_count",
            partner="cupy",
            operation="segmented_count_i64",
            inputs=("candidate_ids",),
            outputs=("summary_counts",),
            stream_binding=stream,
            phase="continuation_or_reduction",
        )

        with self.assertRaisesRegex(rt.GraphValidationError, "explicit partner policy"):
            rt.prepare_graph(
                graph_id="partner_policy_missing",
                values=values,
                nodes=(partner,),
                phase_markers=_required_phases(),
                target_backends=("optix",),
            )

        graph = rt.prepare_graph(
            graph_id="partner_policy_present",
            values=values,
            nodes=(partner,),
            phase_markers=_required_phases(),
            target_backends=("optix",),
            partner_policy=rt.PartnerPolicy(
                explicit_partner_required=True,
                best_partner="cupy",
                benchmark_requires_dual_partner_rows=True,
                numba_reference_required=True,
                partner_timing_separated=True,
            ),
        )
        self.assertEqual(graph.partner_policy.best_partner, "cupy")

    def test_backend_plan_and_execution_report_do_not_authorize_execution_claims(self) -> None:
        plan = rt.BackendPlan(
            backend="optix",
            graph_id="generic_candidate_graph",
            same_contract_key="candidate_contract_v1",
            lowered_nodes=("candidate_producer",),
            prepared_handles=("candidate_scene",),
            phase_markers=_required_phases(),
        )
        payload = plan.to_metadata()
        self.assertFalse(payload["executes"])
        self.assertEqual(payload["claim_boundary"]["true_zero_copy_authorized"], False)

        report = rt.V3ExecutionReport(
            graph_id="generic_candidate_graph",
            backend="optix",
            partner="none",
            hardware="local_test_metadata_only",
            dataset="synthetic_contract_fixture",
            scale="unit",
            data_start_residency="host_resident",
            warmups=0,
            repeats=1,
            timing_statistic="metadata_only",
            phase_timings={"rt_traversal": 0.0, "validation": 0.0},
            correctness_contract="candidate_contract_v1",
            same_contract_key="candidate_contract_v1",
        )
        self.assertEqual(report.to_metadata()["claim_boundary"]["rt_core_speedup_authorized"], False)


def _minimal_prepared_graph() -> rt.PreparedGraph:
    values = (
        rt.GraphValue(
            name="source_geometry",
            kind="geometry",
            dtype="struct:source",
            shape=("n",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("candidate_producer",),
        ),
        rt.GraphValue(
            name="query_geometry",
            kind="geometry",
            dtype="struct:query",
            shape=("m",),
            storage="host",
            residency="host_resident",
            lifetime="caller_retained",
            consumers=("candidate_producer",),
        ),
        rt.GraphValue(
            name="candidate_ids",
            kind="candidate_stream",
            dtype="int64",
            shape=("k",),
            storage="host",
            residency="host_resident",
            lifetime="session_retained",
            producer="candidate_producer",
            capacity="candidate_capacity",
            overflow_policy="fail_closed",
            materialization_policy="already_materialized",
        ),
    )
    return rt.prepare_graph(
        graph_id="generic_candidate_graph",
        values=values,
        nodes=(_primitive_node(),),
        phase_markers=_required_phases(),
        target_backends=("optix", "embree"),
    )


def _primitive_node(
    *,
    node_id: str = "candidate_producer",
    outputs: tuple[str, ...] = ("candidate_ids",),
) -> rt.PrimitiveNode:
    return rt.PrimitiveNode(
        node_id=node_id,
        primitive_id="primitive.aabb_query_2d",
        inputs=("source_geometry", "query_geometry"),
        outputs=outputs,
        backend_contract=rt.BackendContract(
            contract_id="candidate_contract_v1",
            allowed_backends=("optix", "embree"),
            input_contract=("source_geometry", "query_geometry"),
            output_contract=("candidate_ids",),
            precision_policy="float32",
            determinism_policy="stable_id_order",
        ),
        phase="rt_traversal",
        lowering_hints=rt.LoweringHints(),
        capacity_policy=rt.CapacityPolicy(
            capacity_value="candidate_capacity",
            overflow_policy="fail_closed",
            complete_candidate_coverage_required=True,
        ),
        same_contract_key="candidate_contract_v1",
    )


def _required_phases() -> tuple[rt.PhaseMarker, ...]:
    return (
        rt.PhaseMarker("prepare", "prepare graph metadata", setup_candidate=True),
        rt.PhaseMarker("build", "build backend structures", setup_candidate=True),
        rt.PhaseMarker("upload", "upload inputs", setup_candidate=True),
        rt.PhaseMarker("query_prepare", "prepare query state", setup_candidate=True),
        rt.PhaseMarker("rt_traversal", "run RT traversal", steady_state_candidate=True),
        rt.PhaseMarker("stream_handoff", "handoff streams", steady_state_candidate=True),
        rt.PhaseMarker("continuation_or_reduction", "run continuation", steady_state_candidate=True),
        rt.PhaseMarker("download_or_materialization", "materialize explicit outputs"),
        rt.PhaseMarker("validation", "validate same-contract results"),
        rt.PhaseMarker("host_wrapper", "host wrapper timing"),
    )


if __name__ == "__main__":
    unittest.main()
