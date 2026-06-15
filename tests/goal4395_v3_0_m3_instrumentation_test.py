from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4395V30M3InstrumentationTest(unittest.TestCase):
    def test_valid_instrumentation_packet_reports_readiness_without_claim_authority(self) -> None:
        packet = _instrumentation_packet()
        payload = packet.to_metadata()

        self.assertEqual(payload["instrumentation_version"], rt.V3_INSTRUMENTATION_VERSION)
        self.assertEqual(payload["status"], rt.V3_INSTRUMENTATION_STATUS)
        self.assertTrue(payload["claim_readiness"]["same_stream_ready"])
        self.assertTrue(payload["claim_readiness"]["device_resident_ready"])
        self.assertTrue(payload["claim_readiness"]["true_zero_copy_ready"])
        self.assertTrue(payload["claim_readiness"]["phase_complete"])
        self.assertFalse(payload["claim_readiness"]["public_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_authorized"])

    def test_phase_timings_must_cover_required_graph_phases(self) -> None:
        phases = tuple(record for record in _phase_timings() if record.phase != "validation")
        with self.assertRaisesRegex(rt.GraphValidationError, "missing phases"):
            rt.InstrumentationPacket(
                graph_id="generic_candidate_graph",
                backend="optix",
                hardware="metadata_only",
                phase_timings=phases,
            )

    def test_phase_timings_reject_negative_seconds_and_unknown_evidence_ids(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "non-negative"):
            rt.PhaseTimingRecord(
                phase="rt_traversal",
                seconds=-0.1,
                backend="optix",
                timing_source="cuda_event",
            )

        bad_phases = tuple(
            rt.PhaseTimingRecord(
                phase=record.phase,
                seconds=record.seconds,
                backend=record.backend,
                timing_source=record.timing_source,
                evidence_ids=("missing_evidence",) if record.phase == "rt_traversal" else (),
            )
            for record in _phase_timings()
        )
        with self.assertRaisesRegex(rt.GraphValidationError, "unknown evidence ids"):
            rt.InstrumentationPacket(
                graph_id="generic_candidate_graph",
                backend="optix",
                hardware="metadata_only",
                phase_timings=bad_phases,
                evidence_records=(),
            )

    def test_same_stream_requires_cuda_or_nsight_evidence(self) -> None:
        packet = rt.InstrumentationPacket(
            graph_id="generic_candidate_graph",
            backend="optix",
            hardware="metadata_only",
            phase_timings=_phase_timings(),
            evidence_records=(
                rt.EvidenceRecord(
                    evidence_id="host_timer_record",
                    kind="host_timer",
                    backend="optix",
                    phase="host_wrapper",
                    source="unit_test",
                    hardware="metadata_only",
                ),
            ),
        )
        self.assertFalse(packet.same_stream_ready)

        ready = _instrumentation_packet()
        self.assertTrue(ready.same_stream_ready)

    def test_residency_evidence_distinguishes_device_ready_from_zero_copy_ready(self) -> None:
        evidence = rt.ResidencyEvidence(
            value_name="candidate_ids",
            storage="cuda",
            residency="device_resident",
            lifetime="native_owned",
            stream_ordering="same_stream",
            data_ptr_observed=True,
            transfer_counter_observed=False,
            host_materialized=False,
            evidence_ids=("pointer_record",),
        )
        self.assertTrue(evidence.device_resident_ready)
        self.assertFalse(evidence.true_zero_copy_ready)

        zero_copy = rt.ResidencyEvidence(
            value_name="candidate_ids",
            storage="cuda",
            residency="device_resident",
            lifetime="native_owned",
            stream_ordering="same_stream",
            data_ptr_observed=True,
            transfer_counter_observed=True,
            host_materialized=False,
            hidden_copy_observed=False,
            evidence_ids=("pointer_record", "transfer_record"),
        )
        self.assertTrue(zero_copy.true_zero_copy_ready)

    def test_residency_evidence_rejects_unknown_references_and_host_materialized_claims(self) -> None:
        not_ready = rt.ResidencyEvidence(
            value_name="candidate_ids",
            storage="cuda",
            residency="device_resident",
            lifetime="native_owned",
            stream_ordering="same_stream",
            data_ptr_observed=True,
            transfer_counter_observed=True,
            host_materialized=True,
            evidence_ids=("pointer_record",),
        )
        self.assertFalse(not_ready.device_resident_ready)
        self.assertFalse(not_ready.true_zero_copy_ready)

        with self.assertRaisesRegex(rt.GraphValidationError, "unknown evidence ids"):
            rt.InstrumentationPacket(
                graph_id="generic_candidate_graph",
                backend="optix",
                hardware="metadata_only",
                phase_timings=_phase_timings(),
                residency_evidence=(not_ready,),
            )

    def test_claim_boundary_still_rejects_public_promotion(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "true_zero_copy_authorized"):
            rt.InstrumentationPacket(
                graph_id="generic_candidate_graph",
                backend="optix",
                hardware="metadata_only",
                phase_timings=_phase_timings(),
                claim_boundary=rt.ClaimBoundary(true_zero_copy_authorized=True),
            )

    def test_embree_phase_timing_evidence_is_supported_without_gpu_claims(self) -> None:
        evidence = rt.EvidenceRecord(
            evidence_id="embree_traversal_timer",
            kind="embree_phase_timer",
            backend="embree",
            phase="rt_traversal",
            source="unit_test",
            hardware="local_cpu",
        )
        packet = rt.InstrumentationPacket(
            graph_id="generic_candidate_graph",
            backend="embree",
            hardware="local_cpu",
            phase_timings=_phase_timings(backend="embree", timing_source="embree_timer"),
            evidence_records=(evidence,),
        )
        self.assertTrue(packet.phase_complete)
        self.assertFalse(packet.same_stream_ready)
        self.assertFalse(packet.claim_readiness["public_claim_authorized"])


def _instrumentation_packet() -> rt.InstrumentationPacket:
    evidence = (
        rt.EvidenceRecord(
            evidence_id="cuda_event_record",
            kind="cuda_event_pair",
            backend="optix",
            phase="stream_handoff",
            source="unit_test",
            hardware="metadata_only",
        ),
        rt.EvidenceRecord(
            evidence_id="pointer_record",
            kind="pointer_identity",
            backend="optix",
            phase="stream_handoff",
            source="unit_test",
            hardware="metadata_only",
        ),
        rt.EvidenceRecord(
            evidence_id="transfer_record",
            kind="transfer_counter",
            backend="optix",
            phase="download_or_materialization",
            source="unit_test",
            hardware="metadata_only",
        ),
    )
    residency = (
        rt.ResidencyEvidence(
            value_name="candidate_ids",
            storage="cuda",
            residency="device_resident",
            lifetime="native_owned",
            stream_ordering="same_stream",
            data_ptr_observed=True,
            transfer_counter_observed=True,
            host_materialized=False,
            hidden_copy_observed=False,
            evidence_ids=("pointer_record", "transfer_record"),
        ),
    )
    return rt.InstrumentationPacket(
        graph_id="generic_candidate_graph",
        backend="optix",
        hardware="metadata_only",
        phase_timings=_phase_timings(),
        evidence_records=evidence,
        residency_evidence=residency,
    )


def _phase_timings(
    *,
    backend: str = "optix",
    timing_source: str = "metadata_only",
) -> tuple[rt.PhaseTimingRecord, ...]:
    return (
        rt.PhaseTimingRecord("prepare", 0.0, backend, timing_source, setup_candidate=True),
        rt.PhaseTimingRecord("build", 0.0, backend, timing_source, setup_candidate=True),
        rt.PhaseTimingRecord("upload", 0.0, backend, timing_source, setup_candidate=True),
        rt.PhaseTimingRecord("query_prepare", 0.0, backend, timing_source, setup_candidate=True),
        rt.PhaseTimingRecord("rt_traversal", 0.0, backend, timing_source, steady_state_candidate=True),
        rt.PhaseTimingRecord("stream_handoff", 0.0, backend, timing_source, steady_state_candidate=True),
        rt.PhaseTimingRecord("continuation_or_reduction", 0.0, backend, timing_source, steady_state_candidate=True),
        rt.PhaseTimingRecord("download_or_materialization", 0.0, backend, timing_source, materialization_candidate=True),
        rt.PhaseTimingRecord("validation", 0.0, backend, timing_source),
        rt.PhaseTimingRecord("host_wrapper", 0.0, backend, timing_source),
    )


if __name__ == "__main__":
    unittest.main()
