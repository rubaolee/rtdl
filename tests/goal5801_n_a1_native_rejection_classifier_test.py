from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load(
    "goal5801_n_a1_runner",
    ROOT / "experiments/goal5801_n_a1_typed_payload/typed_payload_native_controls.py")
VERIFIER = load(
    "goal5801_n_a1_verifier",
    ROOT / "scripts/goal5801_n_a1_independent_verify.py")


def row(*, failing_phase: str, message: str, nvrtc: str = "PASS",
        context: str = "PASS", complete_build: bool = False):
    phases = {
        "nvrtc": {"verdict": nvrtc},
        "context": {"verdict": context},
    }
    for phase in ("module", "program_groups", "pipeline_link"):
        if complete_build or phase != failing_phase:
            phases[phase] = {
                "verdict": "PASS",
                "num_payload_types": 1,
                "payload_semantics_u32_each": 195,
            }
        else:
            phases[phase] = {
                "verdict": "REJECT_OR_ERROR",
                "exception": {
                    "message": message,
                    "repr": f"RuntimeError({message!r})",
                    "traceback": "typed_payload_native_controls.py contains payload in path",
                },
            }
            break
    if complete_build:
        phases["launch"] = {
            "verdict": "REJECT_OR_ERROR",
            "exception": {"message": message, "repr": repr(message)},
        }
    return {
        "id": "role_effect_closure",
        "phases": phases,
        "terminal_phase": "launch" if complete_build else failing_phase,
        "optix_validation_messages": [],
    }


class NativeRejectionClassifierTest(unittest.TestCase):
    def assertBoth(self, value, expected):
        self.assertIs(RUNNER.native_payload_specific_rejection(value), expected)
        self.assertIs(VERIFIER.native_payload_specific_rejection(value), expected)

    def test_generic_program_group_failure_is_not_collision(self):
        self.assertBoth(row(
            failing_phase="program_groups",
            message="OPTIX_ERROR_INVALID_VALUE: generic program group defect"), False)

    def test_nvrtc_failure_is_not_collision(self):
        value = row(failing_phase="module", message="payload type mismatch",
                    nvrtc="REJECT_OR_ERROR")
        self.assertBoth(value, False)

    def test_context_failure_is_not_collision(self):
        value = row(failing_phase="module", message="payload type mismatch",
                    context="REJECT_OR_ERROR")
        self.assertBoth(value, False)

    def test_launch_failure_is_not_static_collision(self):
        self.assertBoth(row(
            failing_phase="launch", message="payload type mismatch at launch",
            complete_build=True), False)

    def test_payload_specific_module_failure_is_collision(self):
        self.assertBoth(row(
            failing_phase="module",
            message="Payload semantics forbid any-hit payload value write"), True)

    def test_payload_specific_program_group_failure_is_collision(self):
        self.assertBoth(row(
            failing_phase="program_groups",
            message="OPTIX_ERROR_PAYLOAD_TYPE_MISMATCH"), True)

    def test_payload_specific_pipeline_failure_is_collision(self):
        self.assertBoth(row(
            failing_phase="pipeline_link",
            message="payload type resolution failed"), True)

    def test_success_metadata_keys_cannot_create_false_positive(self):
        value = row(
            failing_phase="program_groups",
            message="OPTIX_ERROR_INVALID_VALUE without relevant diagnostic")
        value["phases"]["module"]["payload_semantics"] = "present"
        self.assertBoth(value, False)

    def test_identity_control_uses_one_canonical_nvrtc_source_name(self):
        self.assertEqual(RUNNER.NATIVE_NEGATIVE_IDENTITY_CONTROL_CASES, {
            "nearby_valid_triangle",
            "native_negative_missing_anyhit_rights",
        })
        self.assertEqual(
            RUNNER.NATIVE_NEGATIVE_IDENTITY_CONTROL_SOURCE_NAME,
            "goal5801_n_a1_valid_a_identity_control.cu")


if __name__ == "__main__":
    unittest.main()
