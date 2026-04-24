import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal888_road_hazard_native_optix_gate.py"


class Goal888RoadHazardNativeOptixGateTest(unittest.TestCase):
    def test_non_strict_records_missing_optix_without_failing(self) -> None:
        from scripts import goal888_road_hazard_native_optix_gate as goal888

        cpu = {"row_count": 1, "priority_segments": [1], "priority_segment_count": 1}
        with mock.patch.object(goal888, "_run_cpu", return_value=cpu):
            with mock.patch.object(goal888, "_run_optix_native", side_effect=RuntimeError("no optix")):
                payload = goal888.run_gate(copies=1, output_mode="summary", strict=False)
        self.assertEqual(payload["status"], "non_strict_recorded_gaps")
        self.assertFalse(payload["strict_pass"])
        self.assertIn("optix_native did not run", payload["strict_failures"])

    def test_strict_passes_when_native_matches_cpu_digest(self) -> None:
        from scripts import goal888_road_hazard_native_optix_gate as goal888

        payload = {"row_count": 1, "priority_segments": [1], "priority_segment_count": 1}
        with mock.patch.object(goal888, "_run_cpu", return_value=payload):
            with mock.patch.object(goal888, "_run_optix_native", return_value=payload):
                result = goal888.run_gate(copies=1, output_mode="summary", strict=True)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["records"][1]["parity_vs_cpu_python_reference"])

    def test_cli_writes_non_strict_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output = Path(tmpdir) / "road.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--copies",
                    "1",
                    "--output-mode",
                    "summary",
                    "--output-json",
                    str(output.relative_to(ROOT)),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            summary = json.loads(completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(summary["output_json"], str(output.relative_to(ROOT)))
            self.assertIn(payload["status"], {"pass", "non_strict_recorded_gaps"})
            self.assertIn("cloud_claim_contract", payload)


if __name__ == "__main__":
    unittest.main()
