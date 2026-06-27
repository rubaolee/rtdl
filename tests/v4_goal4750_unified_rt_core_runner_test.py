from __future__ import annotations

import json
import unittest
from pathlib import Path

from rtdsl.v4_goal4750_unified_rt_core_runner import RUN_READY
from rtdsl.v4_goal4750_unified_rt_core_runner import build_dry_run
from rtdsl.v4_goal4750_unified_rt_core_runner import validate_dry_run


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4750_unified_rt_core_runner_dry_run_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4750_unified_rt_core_runner_dry_run_2026-06-26.md"


class V4Goal4750UnifiedRtCoreRunnerTest(unittest.TestCase):
    def test_dry_run_validator_passes(self) -> None:
        payload = build_dry_run()
        validation = validate_dry_run(payload)

        self.assertEqual("passed", validation["status"], validation["errors"])
        self.assertEqual(0, validation["error_count"])

    def test_dry_run_expands_all_thirty_rows(self) -> None:
        payload = build_dry_run()
        rows = payload["rows"]

        self.assertEqual(30, payload["row_count"])
        self.assertEqual(30, len(rows))
        self.assertEqual(30, payload["ready_for_command_binding_count"])
        self.assertEqual(0, payload["blocked_until_repair_count"])

    def test_pod_facts_use_recorded_current_key(self) -> None:
        pod = build_dry_run()["pod"]

        self.assertEqual("194.68.245.170", pod["host"])
        self.assertEqual(22089, pod["port"])
        self.assertEqual("~/.ssh/id_ed25519_rtdl_codex_current_pod", pod["ssh_key"])
        self.assertEqual("NVIDIA RTX A5000", pod["gpu"])

    def test_old_tags_set_both_optix_env_vars_to_v4compat_library(self) -> None:
        for row in build_dry_run()["rows"]:
            if row["version"] not in {"v2_14", "v3_0_2"}:
                continue
            with self.subTest(app=row["app"], version=row["version"]):
                env = row["env_contract"]
                self.assertTrue(env["RTDL_OPTIX_LIB"].endswith("librtdl_optix.v4compat.so"))
                self.assertEqual(env["RTDL_OPTIX_LIB"], env["RTDL_OPTIX_LIBRARY"])

    def test_no_embree_primary_or_hidden_missing_values(self) -> None:
        for row in build_dry_run()["rows"]:
            with self.subTest(app=row["app"], version=row["version"]):
                self.assertEqual("optix_rt_core", row["backend"])
                self.assertFalse(row["embree_primary_denominator_authorized"])
                self.assertNotEqual("n/a", row["command_binding_status"].lower())

    def test_all_rows_are_bound_and_ready(self) -> None:
        rows = build_dry_run()["rows"]
        ready = [row for row in rows if row["run_state"] == RUN_READY]

        self.assertEqual(30, len(ready))
        for row in ready:
            with self.subTest(app=row["app"], version=row["version"]):
                self.assertEqual("command_template_bound_for_goal4753_pod", row["command_binding_status"])
                self.assertTrue(row["command"])
                self.assertTrue(row["stdout_json"].endswith(f"{row['version']}_{row['app']}.json"))

    def test_inherited_compatibility_apps_are_runnable_not_speed_claims(self) -> None:
        rows = {
            (row["app"], row["version"]): row
            for row in build_dry_run()["rows"]
        }
        for app in ("robot_collision", "contact_manifold", "spatial_rayjoin"):
            row = rows[(app, "v4_0")]
            with self.subTest(app=app):
                self.assertEqual(RUN_READY, row["run_state"])
                self.assertEqual("runnable_protocol_template", row["route_status"])
                self.assertTrue(row["correctness_required_before_speed_credit"])

    def test_spatial_rows_use_generated_shape_pair_dataset_not_default_overlay_only(self) -> None:
        for row in build_dry_run(profile="serious")["rows"]:
            if row["app"] != "spatial_rayjoin":
                continue
            with self.subTest(version=row["version"]):
                command = row["command"]
                self.assertIn("--dataset", command)
                dataset_index = command.index("--dataset") + 1
                self.assertIn("spatial_shape_pair_serious_left_grid64.cdb", command[dataset_index])
                self.assertIn("spatial_shape_pair_serious_right_grid64.cdb", command[dataset_index])

    def test_written_artifacts_exist_and_validate(self) -> None:
        self.assertTrue(EVIDENCE.exists(), "run scripts/v4_goal4750_unified_rt_core_runner.py first")
        self.assertTrue(REPORT.exists(), "run scripts/v4_goal4750_unified_rt_core_runner.py first")

        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual("passed", payload["validation"]["status"], payload["validation"]["errors"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("rows: `30`", report)
        self.assertIn("key: `~/.ssh/id_ed25519_rtdl_codex_current_pod`", report)


if __name__ == "__main__":
    unittest.main()
