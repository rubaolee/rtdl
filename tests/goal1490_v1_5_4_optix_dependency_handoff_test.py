import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "goal1490_v1_5_4_optix_dependency_handoff.py"
POD_PREFLIGHT = ROOT / "docs" / "reports" / "goal1489_v1_5_4_optix_device_buffer_preflight_pod_2026-05-07.json"


def load_handoff_module():
    spec = importlib.util.spec_from_file_location("goal1490_handoff", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal1490V154OptixDependencyHandoffTest(unittest.TestCase):
    def test_builds_handoff_from_pod_preflight_blockers(self) -> None:
        module = load_handoff_module()

        payload = module.validate_handoff(module.build_handoff(module.load_preflight(POD_PREFLIGHT)))

        self.assertTrue(payload["optix_dependency_blocked"])
        self.assertIn("CUDA Driver API allocation probes", payload["accepted_current_pod_uses"])
        self.assertIn("end_to_end_rtdl_optix_device_buffer_execution", payload["blocked_current_pod_uses"])
        self.assertEqual(len(payload["acceptable_resolution_paths"]), 3)
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])

    def test_rejects_unblocked_preflight(self) -> None:
        module = load_handoff_module()
        preflight = {
            "valid_for_optix_device_buffer_execution_work": True,
            "blockers": [],
        }

        with self.assertRaisesRegex(ValueError, "blocked OptiX dependencies"):
            module.validate_handoff(module.build_handoff(preflight))

    def test_markdown_contains_commands_and_boundary(self) -> None:
        module = load_handoff_module()
        payload = module.validate_handoff(module.build_handoff(module.load_preflight(POD_PREFLIGHT)))

        markdown = module.to_markdown(payload)

        self.assertIn("make build-optix", markdown)
        self.assertIn("RTDL_OPTIX_LIB", markdown)
        self.assertIn("Claim Boundary", markdown)
        self.assertIn("does not install OptiX", markdown)


if __name__ == "__main__":
    unittest.main()
