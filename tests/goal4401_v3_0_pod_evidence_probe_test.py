from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import REQUIRED_PHASE_NAMES


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "v3_0_pod_evidence_probe.py"


def _load_probe_module():
    spec = importlib.util.spec_from_file_location("v3_0_pod_evidence_probe", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load V3 pod evidence probe module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal4401V30PodEvidenceProbeTest(unittest.TestCase):
    def test_optix_probe_packet_is_ready_but_public_claims_remain_locked(self) -> None:
        probe = _load_probe_module()
        packet = probe.build_optix_probe_packet(
            hardware_label="rtx_test_gpu",
            cuda_seconds=0.001,
            validation_seconds=0.002,
            device_pointer=123456,
            measured_region_explicit_transfers=0,
        )
        payload = packet.to_metadata()

        self.assertEqual(payload["status"], rt.V3_INSTRUMENTATION_STATUS)
        self.assertTrue(payload["claim_readiness"]["same_stream_ready"])
        self.assertTrue(payload["claim_readiness"]["device_resident_ready"])
        self.assertTrue(payload["claim_readiness"]["true_zero_copy_ready"])
        self.assertTrue(payload["claim_readiness"]["phase_complete"])
        self.assertFalse(payload["claim_readiness"]["public_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_authorized"])

    def test_optix_probe_does_not_claim_zero_copy_when_transfer_counter_is_absent(self) -> None:
        probe = _load_probe_module()
        packet = probe.build_optix_probe_packet(
            hardware_label="rtx_test_gpu",
            cuda_seconds=0.001,
            validation_seconds=0.002,
            device_pointer=123456,
            measured_region_explicit_transfers=None,
        )

        self.assertTrue(packet.same_stream_ready)
        self.assertTrue(packet.device_resident_ready)
        self.assertFalse(packet.true_zero_copy_ready)

    def test_embree_probe_packet_is_phase_complete_without_gpu_claims(self) -> None:
        probe = _load_probe_module()
        packet = probe.build_embree_probe_packet(
            hardware_label="cpu_test_host",
            load_seconds=0.003,
            version="4.3.0",
        )

        self.assertTrue(packet.phase_complete)
        self.assertFalse(packet.same_stream_ready)
        self.assertFalse(packet.device_resident_ready)
        self.assertFalse(packet.claim_readiness["public_claim_authorized"])

    def test_phase_timings_cover_the_v3_required_phase_set(self) -> None:
        probe = _load_probe_module()
        timings = probe._phase_timings(
            backend="optix",
            default_source="metadata_only",
            seconds_by_phase={phase: 0.0 for phase in REQUIRED_PHASE_NAMES},
            evidence_by_phase={},
        )

        self.assertEqual(tuple(record.phase for record in timings), REQUIRED_PHASE_NAMES)


if __name__ == "__main__":
    unittest.main()
