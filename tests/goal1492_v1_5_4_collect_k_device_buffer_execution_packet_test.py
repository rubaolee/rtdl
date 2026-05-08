import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1492_v1_5_4_collect_k_device_buffer_execution_packet.py"


def load_packet_module():
    spec = importlib.util.spec_from_file_location("goal1492_packet", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1492V154CollectKDeviceBufferExecutionPacketTest(unittest.TestCase):
    def test_packet_has_expected_reference_rows_and_guardrails(self) -> None:
        module = load_packet_module()

        packet = module.validate_packet(module.build_packet())

        self.assertEqual(packet["first_target_primitive"], "COLLECT_K_BOUNDED")
        self.assertEqual(packet["expected_reference"]["valid_count"], 3)
        self.assertFalse(packet["expected_reference"]["overflowed"])
        self.assertEqual(
            tuple(tuple(row) for row in packet["expected_reference"]["candidate_id_rows"]),
            ((1, 10), (2, 20), (3, 30)),
        )
        self.assertFalse(packet["ready_to_run_on_current_pod"])
        self.assertFalse(packet["true_zero_copy_authorized"])
        self.assertFalse(packet["public_speedup_wording_authorized"])

    def test_packet_survives_json_roundtrip(self) -> None:
        module = load_packet_module()
        packet = module.build_packet()

        roundtripped = json.loads(json.dumps(packet))
        validated = module.validate_packet(roundtripped)

        self.assertEqual(validated["native_symbols"]["optix_target"], "rtdl_optix_collect_k_bounded_i64")

    def test_rejects_claim_expansion(self) -> None:
        module = load_packet_module()
        packet = module.build_packet()
        packet["release_action_authorized"] = True

        with self.assertRaisesRegex(ValueError, "release_action_authorized=False"):
            module.validate_packet(packet)

    def test_markdown_contains_fixture_and_boundary(self) -> None:
        module = load_packet_module()
        markdown = module.to_markdown(module.validate_packet(module.build_packet()))

        self.assertIn("COLLECT_K_BOUNDED", markdown)
        self.assertIn("Expected Reference", markdown)
        self.assertIn("does not run OptiX", markdown)


if __name__ == "__main__":
    unittest.main()
