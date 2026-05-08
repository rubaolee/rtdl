import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1496_v1_5_4_collect_k_device_pointer_stub_gate.py"


def load_gate_module():
    spec = importlib.util.spec_from_file_location("goal1496_stub_gate", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1496V154CollectKDevicePointerStubGateTest(unittest.TestCase):
    def test_device_pointer_stub_is_present_and_fail_closed(self) -> None:
        module = load_gate_module()

        gate = module.validate_gate(module.build_gate())

        self.assertTrue(gate["signature_present"])
        self.assertTrue(gate["implementation_present"])
        self.assertTrue(gate["fail_closed_stub_present"])
        self.assertFalse(gate["accepted_for_goal1493_device_buffer_execution"])
        self.assertFalse(gate["native_symbol_implemented"])

    def test_rejects_treating_stub_as_accepted_execution(self) -> None:
        module = load_gate_module()
        gate = module.build_gate()
        gate["accepted_for_goal1493_device_buffer_execution"] = True

        with self.assertRaisesRegex(ValueError, "must not be accepted"):
            module.validate_gate(gate)

    def test_rejects_claim_expansion(self) -> None:
        module = load_gate_module()
        gate = module.build_gate()
        gate["claim_flags"]["public_speedup_wording_authorized"] = True

        with self.assertRaisesRegex(ValueError, "public_speedup_wording_authorized=False"):
            module.validate_gate(gate)

    def test_markdown_preserves_boundary(self) -> None:
        module = load_gate_module()
        markdown = module.to_markdown(module.validate_gate(module.build_gate()))

        self.assertIn("Fail-closed stub present", markdown)
        self.assertIn("does not implement device execution", markdown)
        self.assertIn("does not prove true zero-copy", markdown)


if __name__ == "__main__":
    unittest.main()
