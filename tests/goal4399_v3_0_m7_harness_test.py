from __future__ import annotations

import unittest

import rtdsl as rt


class Goal4399V30M7HarnessTest(unittest.TestCase):
    def test_valid_harness_packet_requires_phase_complete_rows_and_no_public_claim(self) -> None:
        packet = rt.BenchmarkHarnessPacket(
            packet_id="m7_packet",
            rows=(
                _row("optix_row", "rtdl_optix", "optix"),
                _row("embree_row", "rtdl_embree", "embree"),
            ),
        )
        payload = packet.to_metadata()
        self.assertEqual(payload["harness_version"], rt.V3_BENCHMARK_HARNESS_VERSION)
        self.assertEqual(payload["status"], rt.V3_BENCHMARK_HARNESS_STATUS)
        self.assertFalse(payload["public_claim_authorized"])
        self.assertEqual(payload["claim_boundary"]["public_speedup_authorized"], False)

        summary = rt.validate_benchmark_harness_packet(packet)
        self.assertEqual(summary["row_count"], 2)
        self.assertFalse(summary["public_claim_authorized"])

    def test_comparison_group_requires_optix_and_embree_rows_together(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "Embree row"):
            rt.BenchmarkHarnessPacket(
                packet_id="m7_packet",
                rows=(_row("optix_row", "rtdl_optix", "optix"),),
            )

        with self.assertRaisesRegex(rt.GraphValidationError, "OptiX row"):
            rt.BenchmarkHarnessPacket(
                packet_id="m7_packet",
                rows=(_row("embree_row", "rtdl_embree", "embree"),),
            )

    def test_comparison_group_requires_same_contract_key(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "same_contract_key"):
            rt.BenchmarkHarnessPacket(
                packet_id="m7_packet",
                rows=(
                    _row("optix_row", "rtdl_optix", "optix", same_contract_key="contract_a"),
                    _row("embree_row", "rtdl_embree", "embree", same_contract_key="contract_b"),
                ),
            )

    def test_external_rows_require_code_version_and_timing_basis(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "external_code_version"):
            _row(
                "external_row",
                "external_system",
                "external",
                partner="external",
                external_code_version=None,
                external_timing_basis="cold_total_wall_time",
            )

        with self.assertRaisesRegex(rt.GraphValidationError, "external_timing_basis"):
            _row(
                "external_row",
                "external_system",
                "external",
                partner="external",
                external_code_version="external_commit",
                external_timing_basis=None,
            )

        row = _row(
            "external_row",
            "external_system",
            "external",
            partner="external",
            external_code_version="external_commit",
            external_timing_basis="cold_total_wall_time",
        )
        self.assertEqual(row.external_code_version, "external_commit")

    def test_harness_rejects_public_claim_boundary(self) -> None:
        with self.assertRaisesRegex(rt.GraphValidationError, "public_speedup_authorized"):
            rt.BenchmarkHarnessPacket(
                packet_id="m7_packet",
                rows=(
                    _row("optix_row", "rtdl_optix", "optix"),
                    _row("embree_row", "rtdl_embree", "embree"),
                ),
                claim_boundary=rt.ClaimBoundary(public_speedup_authorized=True),
            )


def _row(
    row_id: str,
    role: str,
    backend: str,
    *,
    partner: str = "none",
    same_contract_key: str = "candidate_contract_v1",
    external_code_version: str | None = None,
    external_timing_basis: str | None = None,
) -> rt.BenchmarkHarnessRow:
    return rt.BenchmarkHarnessRow(
        row_id=row_id,
        graph_id="generic_candidate_graph",
        comparison_group="candidate_group",
        comparison_role=role,
        backend=backend,
        partner=partner,
        dataset="synthetic_contract_fixture",
        scale="unit",
        hardware="metadata_only",
        timing_basis="phase_split" if role != "external_system" else "external_system_reported",
        same_contract_key=same_contract_key,
        instrumentation=_instrumentation(backend if backend != "external" else "cpu"),
        warmups=0,
        repeats=1,
        includes_build=True,
        includes_upload=True,
        includes_download=True,
        includes_validation=True,
        external_code_version=external_code_version,
        external_timing_basis=external_timing_basis,
    )


def _instrumentation(backend: str) -> rt.InstrumentationPacket:
    return rt.InstrumentationPacket(
        graph_id="generic_candidate_graph",
        backend=backend,
        hardware="metadata_only",
        phase_timings=(
            rt.PhaseTimingRecord("prepare", 0.0, backend, "metadata_only", setup_candidate=True),
            rt.PhaseTimingRecord("build", 0.0, backend, "metadata_only", setup_candidate=True),
            rt.PhaseTimingRecord("upload", 0.0, backend, "metadata_only", setup_candidate=True),
            rt.PhaseTimingRecord("query_prepare", 0.0, backend, "metadata_only", setup_candidate=True),
            rt.PhaseTimingRecord("rt_traversal", 0.0, backend, "metadata_only", steady_state_candidate=True),
            rt.PhaseTimingRecord("stream_handoff", 0.0, backend, "metadata_only", steady_state_candidate=True),
            rt.PhaseTimingRecord("continuation_or_reduction", 0.0, backend, "metadata_only", steady_state_candidate=True),
            rt.PhaseTimingRecord("download_or_materialization", 0.0, backend, "metadata_only"),
            rt.PhaseTimingRecord("validation", 0.0, backend, "metadata_only"),
            rt.PhaseTimingRecord("host_wrapper", 0.0, backend, "metadata_only"),
        ),
    )


if __name__ == "__main__":
    unittest.main()
