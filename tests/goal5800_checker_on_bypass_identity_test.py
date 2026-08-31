from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5800_verify_checker_on_bypass_identity.py"
SPEC = importlib.util.spec_from_file_location("goal5800_identity", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def receipt(mode: str) -> dict[str, object]:
    marker = "a" * 64
    return {
        "schema": "rtdl.checker_on_bypass_execution_receipt.v1",
        "checker_mode": mode,
        "checker_decision": "ACCEPT" if mode == "ON" else "NOT_RUN",
        "structural_identity": {
            "artifacts": {
                "device_source_sha256": marker,
                "ptx_sha256": marker,
                "module_compile_options_sha256": marker,
                "program_group_manifest_sha256": marker,
                "pipeline_manifest_sha256": marker,
                "sbt_bytes_sha256": marker,
                "gas_input_sha256": marker,
                "gas_build_options_sha256": marker,
                "launch_params_bytes_sha256": marker,
            },
            "actions": {
                "launch_dimensions": [4, 1, 1],
                "launch_count": 1,
                "synchronization_count": 1,
                "output_copy_api": "bulk_tolist",
                "status_read_before_output": True,
                "oracle_sha256": marker,
            },
            "observations": {
                "status_bytes_sha256": marker,
                "output_bytes_sha256": marker,
                "oracle_pass": True,
            },
        },
    }


class Goal5800CheckerOnBypassIdentityTest(unittest.TestCase):
    def test_accepts_exact_structural_identity(self) -> None:
        result = MODULE.verify(receipt("ON"), receipt("BYPASS"))
        self.assertTrue(result["status"].startswith("PASS__"))
        self.assertEqual(result["registered_performance_timing_count"], 0)

    def test_rejects_artifact_mismatch(self) -> None:
        bypass = receipt("BYPASS")
        bypass["structural_identity"]["artifacts"]["ptx_sha256"] = "b" * 64
        with self.assertRaisesRegex(RuntimeError, "artifacts.ptx_sha256"):
            MODULE.verify(receipt("ON"), bypass)

    def test_rejects_missing_field_and_extra_field(self) -> None:
        missing = receipt("BYPASS")
        del missing["structural_identity"]["actions"]["launch_dimensions"]
        with self.assertRaisesRegex(RuntimeError, "actions keys"):
            MODULE.verify(receipt("ON"), missing)
        extra = receipt("BYPASS")
        extra["unsealed_note"] = "not allowed"
        with self.assertRaisesRegex(RuntimeError, "top-level"):
            MODULE.verify(receipt("ON"), extra)

    def test_rejects_output_and_action_mismatches(self) -> None:
        for section, key, value in (
            ("actions", "launch_count", 2),
            ("actions", "synchronization_count", 2),
            ("observations", "output_bytes_sha256", "c" * 64),
        ):
            with self.subTest(section=section, key=key):
                bypass = receipt("BYPASS")
                bypass["structural_identity"][section][key] = value
                if key == "launch_count":
                    bypass["structural_identity"]["actions"][
                        "synchronization_count"] = value
                with self.assertRaisesRegex(RuntimeError, "structural mismatch"):
                    MODULE.verify(receipt("ON"), bypass)


if __name__ == "__main__":
    unittest.main()
