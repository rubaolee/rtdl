import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1489_v1_5_4_optix_device_buffer_preflight.py"


def load_preflight_module():
    spec = importlib.util.spec_from_file_location("goal1489_preflight", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1489V154OptixDeviceBufferPreflightTest(unittest.TestCase):
    def test_dry_run_accepts_gate_without_hardware_requirements(self) -> None:
        module = load_preflight_module()

        payload = module.run_preflight(dry_run=True)

        self.assertTrue(payload["valid_for_optix_device_buffer_execution_work"])
        self.assertTrue(payload["checks"]["goal1488_boundary_gate_accepted"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("build_or_provide_librtdl_optix", payload["required_next_evidence"])
        self.assertIn("does not run backend execution", payload["claim_boundary"])

    def test_non_dry_run_reports_missing_optix_toolchain_or_library_as_blockers(self) -> None:
        module = load_preflight_module()

        payload = module.run_preflight(dry_run=False)

        self.assertTrue(payload["checks"]["goal1488_boundary_gate_accepted"])
        self.assertIsInstance(payload["blockers"], list)
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["release_action_authorized"])

    def test_markdown_lists_blockers_and_boundary(self) -> None:
        module = load_preflight_module()
        payload = module.run_preflight(dry_run=True)

        markdown = module.to_markdown(payload)

        self.assertIn("Goal 1489", markdown)
        self.assertIn("Claim Boundary", markdown)
        self.assertIn("does not authorize true", markdown)


if __name__ == "__main__":
    unittest.main()
