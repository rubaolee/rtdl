from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import rtdsl as rt
from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3823_current_benchmark_front_door_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3823_current_benchmark_front_door_registry_2026-06-07.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3823_current_benchmark_front_door_registry_a5000" / "summary.json"


class Goal3823CurrentBenchmarkFrontDoorRegistryTest(unittest.TestCase):
    def test_registry_covers_all_promoted_apps_without_claim_authorization(self) -> None:
        rows = rt.current_benchmark_front_doors()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["row_id"] for row in rows}), 10)
        validation = rt.validate_current_benchmark_front_doors()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

        for row in rows:
            self.assertFalse(row["release_authorized"], row["row_id"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["row_id"])
            self.assertFalse(row["paper_reproduction_claim_authorized"], row["row_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["row_id"])

    def test_repaired_and_hardened_commands_are_the_registered_front_doors(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_front_doors()}

        self.assertIn("directed_threshold_prepared", rows["hausdorff_xhd"]["command"])
        self.assertIn("--witness-capacity", rows["contact_manifold"]["command"])
        self.assertIn("prepared_optix_ranked_summary", rows["rtnn"]["command"])
        self.assertIn("--optix-graph-mode", rows["triangle_counting"]["command"])
        self.assertIn("native", rows["triangle_counting"]["command"])

        self.assertEqual(rows["rtnn"]["evidence_refs"], ("Goal3820",))
        self.assertIn("Goal3819", rows["triangle_counting"]["evidence_refs"])
        self.assertTrue(rows["rt_dbscan"]["requires_numba"])
        self.assertTrue(rows["barnes_hut"]["requires_numba"])

    def test_runner_dry_run_outputs_machine_readable_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "front_doors.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--dry-run",
                    "--output-json",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            self.assertIn("current_benchmark_front_doors.goal3823", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertIsNone(payload["all_pass"])
        self.assertEqual(payload["summary"]["app_count"], 10)
        self.assertEqual(payload["summary"]["row_count"], 10)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        row_ids = {row["row_id"] for row in payload["rows"]}
        self.assertIn("rtnn_prepared_optix_ranked_summary", row_ids)
        self.assertIn("triangle_counting_optix_native_summary", row_ids)

    def test_report_records_non_authorizing_runner_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3823",
            "single current command registry",
            "per-row progress",
            "prepared_optix_ranked_summary",
            "--optix-graph-mode native",
            "A5000 Pod Evidence",
            "all ten registered rows passed",
            "does not authorize release action",
            "not a long-run performance matrix",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifact_records_all_registered_rows_passed(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], rt.CURRENT_BENCHMARK_FRONT_DOOR_VERSION)
        self.assertTrue(payload["all_pass"])
        self.assertFalse(payload["dry_run"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertEqual(payload["validation"]["errors"], [])
        rows = payload["rows"]
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        self.assertIn(
            "rtnn_prepared_optix_ranked_summary",
            {row["row_id"] for row in rows},
        )
        self.assertIn(
            "triangle_counting_optix_native_summary",
            {row["row_id"] for row in rows},
        )


if __name__ == "__main__":
    unittest.main()
