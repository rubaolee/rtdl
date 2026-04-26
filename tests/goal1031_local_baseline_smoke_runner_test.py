from __future__ import annotations

import unittest


class Goal1031LocalBaselineSmokeRunnerTest(unittest.TestCase):
    def test_smoke_scaling_rewrites_copies_only_in_smoke_mode(self) -> None:
        module = __import__("scripts.goal1031_local_baseline_smoke_runner", fromlist=["_scaled_command"])
        command = ["python3", "examples/app.py", "--copies", "20000", "--backend", "cpu"]
        self.assertEqual(
            module._scaled_command(command, mode="smoke"),
            ["python3", "examples/app.py", "--copies", "50", "--backend", "cpu"],
        )
        self.assertEqual(module._scaled_command(command, mode="full"), command)

    def test_json_summary_extracts_claim_neutral_fields(self) -> None:
        module = __import__("scripts.goal1031_local_baseline_smoke_runner", fromlist=["_json_summary"])
        summary = module._json_summary(
            '{"app":"x","backend":"embree","copies":50,"matches_oracle":true,'
            '"native_continuation_active":true,"outlier_count":10,"rows":[1,2,3]}'
        )
        self.assertEqual(summary["json_parse_status"], "ok")
        self.assertEqual(summary["app"], "x")
        self.assertEqual(summary["backend"], "embree")
        self.assertEqual(summary["copies"], 50)
        self.assertTrue(summary["matches_oracle"])
        self.assertTrue(summary["native_continuation_active"])
        self.assertEqual(summary["outlier_count"], 10)
        self.assertNotIn("rows", summary)

    def test_scipy_missing_is_optional_dependency_gap(self) -> None:
        module = __import__("scripts.goal1031_local_baseline_smoke_runner", fromlist=["_command_status"])
        self.assertEqual(
            module._command_status(
                ["python3", "examples/app.py", "--backend", "scipy"],
                1,
                "RuntimeError: SciPy is not installed; install scipy",
            ),
            "optional_dependency_unavailable",
        )
        self.assertEqual(
            module._command_status(["python3", "examples/app.py", "--backend", "cpu"], 1, "boom"),
            "failed",
        )

    def test_manifest_has_four_ready_entries(self) -> None:
        module = __import__("scripts.goal1031_local_baseline_smoke_runner", fromlist=["build_manifest"])
        manifest = module.build_manifest()
        ready = [entry for entry in manifest["entries"] if entry["local_status"] == "baseline_ready"]
        self.assertEqual(len(ready), 2)

    def test_build_report_selects_ready_entries_by_default(self) -> None:
        module = __import__("scripts.goal1031_local_baseline_smoke_runner", fromlist=["build_report", "run_entry"])
        original = module.run_entry
        try:
            module.run_entry = lambda entry, *, mode, timeout_sec: {
                "app": entry["app"],
                "rtx_path": entry["rtx_path"],
                "local_status": entry["local_status"],
                "mode": mode,
                "status": "ok",
                "failed_command_count": 0,
                "optional_dependency_unavailable_count": 0,
                "commands": [],
            }
            default_payload = module.build_report(mode="smoke", timeout_sec=1.0)
            self.assertEqual(default_payload["entry_count"], 2)
            partial_payload = module.build_report(mode="smoke", timeout_sec=1.0, include_partial=True)
            self.assertEqual(partial_payload["entry_count"], 17)
        finally:
            module.run_entry = original


if __name__ == "__main__":
    unittest.main()
