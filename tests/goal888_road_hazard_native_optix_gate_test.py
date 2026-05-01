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

        payload = {
            "output_mode": "summary",
            "priority_segment_count": 1,
            "summary_materializes_rows": False,
            "run_phases": {"native_threshold_count_sec": 0.01},
            "native_continuation_active": True,
            "native_continuation_backend": "optix_native_hitcount_gated",
        }
        with mock.patch.object(goal888, "_run_cpu", return_value=payload):
            with mock.patch.object(goal888, "_run_optix_native", return_value=payload):
                result = goal888.run_gate(copies=1, output_mode="summary", strict=True)
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["records"][1]["parity_vs_cpu_python_reference"])
        self.assertFalse(result["records"][1]["summary_materializes_rows"])
        self.assertEqual(result["records"][1]["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertIn("native_threshold_count_sec", result["records"][1]["run_phases"])

    def test_summary_digest_ignores_materialized_priority_ids(self) -> None:
        from scripts import goal888_road_hazard_native_optix_gate as goal888

        cpu = {
            "output_mode": "summary",
            "row_count": 3,
            "priority_segments": [1, 3],
            "priority_segment_count": 2,
            "summary_materializes_rows": True,
        }
        native = {
            "output_mode": "summary",
            "row_count": 0,
            "priority_segments": [],
            "priority_segment_count": 2,
            "summary_materializes_rows": False,
        }

        self.assertEqual(
            goal888._canonical(cpu)["priority_segment_count"],
            goal888._canonical(native)["priority_segment_count"],
        )

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
            self.assertIn("run_phases", payload["records"][0])
            self.assertIn("summary_materializes_rows", payload["records"][0])

    def test_payload_metadata_preserves_summary_no_row_materialization_boundary(self) -> None:
        from scripts import goal888_road_hazard_native_optix_gate as goal888

        metadata = goal888._payload_metadata(
            {
                "output_mode": "summary",
                "row_count": 0,
                "priority_segment_count": 8,
                "summary_materializes_rows": False,
                "native_continuation_active": True,
                "native_continuation_backend": "optix_native_hitcount_gated",
                "run_phases": {"native_threshold_count_sec": 0.25},
            }
        )

        self.assertEqual(metadata["row_count"], 0)
        self.assertEqual(metadata["priority_segment_count"], 8)
        self.assertFalse(metadata["summary_materializes_rows"])
        self.assertTrue(metadata["native_continuation_active"])
        self.assertEqual(metadata["native_continuation_backend"], "optix_native_hitcount_gated")
        self.assertEqual(metadata["run_phases"]["native_threshold_count_sec"], 0.25)


if __name__ == "__main__":
    unittest.main()
