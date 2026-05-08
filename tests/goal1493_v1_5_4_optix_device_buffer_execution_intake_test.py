import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1493_v1_5_4_optix_device_buffer_execution_intake.py"
PACKET_PATH = ROOT / "docs" / "reports" / "goal1492_v1_5_4_collect_k_device_buffer_execution_packet_2026-05-08.json"


def load_intake_module():
    spec = importlib.util.spec_from_file_location("goal1493_intake", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def accepted_execution_fixture(packet):
    return {
        "goal": "Goal1493",
        "source_packet_goal": packet["goal"],
        "primitive": packet["first_target_primitive"],
        "backend": "optix",
        "native_symbol": "rtdl_optix_collect_k_bounded_i64_device",
        "measured_on_real_nvidia": True,
        "goal1489_preflight_green": True,
        "git_commit": "future-optix-ready-commit",
        "row_width": packet["row_width"],
        "capacity": packet["capacity"],
        "candidate_rows": packet["candidate_rows"],
        "result": {
            "valid_count": packet["expected_reference"]["valid_count"],
            "overflowed": packet["expected_reference"]["overflowed"],
            "candidate_id_rows": packet["expected_reference"]["candidate_id_rows"],
        },
        "parity": {
            "same_candidate_rows": True,
            "same_valid_count": True,
            "same_overflowed_flag": True,
        },
        "transfer_accounting": {
            "host_to_device_transfers_before_backend_execution": 1,
            "device_to_host_transfers_after_backend_execution": 1,
            "internal_device_transfers_if_any": 0,
            "allocation_only_transfers_distinguished_from_content_transfers": True,
        },
        "true_zero_copy_authorized": False,
        "public_speedup_wording_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "stable_public_primitive_authorized": False,
        "partner_tensor_handoff_authorized": False,
        "release_action_authorized": False,
    }


class Goal1493V154OptixDeviceBufferExecutionIntakeTest(unittest.TestCase):
    def test_pending_intake_keeps_current_pod_blockers_and_claim_flags(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)

        intake = module.pending_intake(packet)

        self.assertEqual(intake["status"], "goal1493_pending_measured_optix_execution")
        self.assertIn("goal1489_current_pod_missing_optix_headers", intake["blocked_by"])
        self.assertEqual(intake["required_symbol"], "rtdl_optix_collect_k_bounded_i64_device")
        self.assertEqual(
            intake["legacy_packet_symbol_rejected_for_device_execution"],
            "rtdl_optix_collect_k_bounded_i64",
        )
        self.assertFalse(intake["true_zero_copy_authorized"])
        self.assertFalse(intake["public_speedup_wording_authorized"])

    def test_accepts_strict_matching_future_execution_fixture(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)
        execution = accepted_execution_fixture(packet)

        intake = module.validate_execution_intake(packet, execution)

        self.assertEqual(intake["status"], "goal1493_measured_optix_execution_intake_accepted")
        self.assertIn("transfer-accounting evidence only", intake["claim_boundary"])

    def test_rejects_wrong_rows(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)
        execution = accepted_execution_fixture(packet)
        execution["result"]["candidate_id_rows"] = [(1, 10), (3, 30)]

        with self.assertRaisesRegex(ValueError, "candidate row parity failed"):
            module.validate_execution_intake(packet, execution)

    def test_rejects_legacy_host_pointer_symbol(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)
        execution = accepted_execution_fixture(packet)
        execution["native_symbol"] = "rtdl_optix_collect_k_bounded_i64"

        with self.assertRaisesRegex(ValueError, "legacy host-pointer symbol"):
            module.validate_execution_intake(packet, execution)

    def test_rejects_claim_expansion(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)
        execution = accepted_execution_fixture(packet)
        execution["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            module.validate_execution_intake(packet, execution)

    def test_rejects_missing_transfer_accounting(self) -> None:
        module = load_intake_module()
        packet = module.load_json(PACKET_PATH)
        execution = accepted_execution_fixture(packet)
        del execution["transfer_accounting"]["device_to_host_transfers_after_backend_execution"]

        with self.assertRaisesRegex(ValueError, "transfer accounting"):
            module.validate_execution_intake(packet, execution)


if __name__ == "__main__":
    unittest.main()
