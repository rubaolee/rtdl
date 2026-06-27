from __future__ import annotations

import json
import unittest
from pathlib import Path

from rtdsl.v4_goal4749_final_rt_core_protocol import APP_ORDER
from rtdsl.v4_goal4749_final_rt_core_protocol import VERSION_ORDER
from rtdsl.v4_goal4749_final_rt_core_protocol import build_protocol
from rtdsl.v4_goal4749_final_rt_core_protocol import validate_protocol


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "future" / "v4" / "evidence" / "v4_goal4749_final_rt_core_protocol_2026-06-26.json"
REPORT = ROOT / "future" / "v4" / "v4_goal4749_final_rt_core_protocol_2026-06-26.md"


def _walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)


class V4Goal4749FinalRtCoreProtocolTest(unittest.TestCase):
    def test_protocol_validator_passes(self) -> None:
        protocol = build_protocol()
        validation = validate_protocol(protocol)

        self.assertEqual("passed", validation["status"], validation["errors"])
        self.assertEqual(0, validation["error_count"])

    def test_protocol_has_all_ten_apps_and_three_versions(self) -> None:
        protocol = build_protocol()
        rows = protocol["rows"]
        by_app = {row["app"]: row for row in rows}

        self.assertEqual(list(APP_ORDER), protocol["app_order"])
        self.assertEqual(10, len(rows))
        self.assertEqual(set(APP_ORDER), set(by_app))
        for app, row in by_app.items():
            with self.subTest(app=app):
                self.assertEqual(set(VERSION_ORDER), set(row["versions"]))
                self.assertTrue(row["same_semantics_required"])
                self.assertTrue(row["rt_core_primary_required"])
                self.assertEqual("control_only_not_primary_denominator", row["embree_role"])

    def test_global_rules_match_user_boundary(self) -> None:
        rules = build_protocol()["global_rules"]

        self.assertTrue(rules["nvidia_rt_core_primary_required"])
        self.assertFalse(rules["embree_primary_denominator_authorized"])
        self.assertTrue(rules["embree_control_reference_authorized"])
        self.assertTrue(rules["no_na_rows_authorized"])
        self.assertTrue(rules["same_semantics_required"])
        self.assertTrue(rules["correctness_parity_required_before_speed_credit"])
        self.assertTrue(rules["v4_is_v2_v3_superset_release_line"])
        self.assertFalse(rules["partner_migration_counts_as_v4_speed_win"])
        self.assertFalse(rules["pod_authorized_by_goal4749"])

    def test_no_na_style_values_are_present(self) -> None:
        for text in _walk_strings(build_protocol()):
            with self.subTest(text=text[:80]):
                self.assertNotIn(text.strip().lower(), {"n/a", "na", "not applicable"})

    def test_no_version_uses_embree_as_primary_backend(self) -> None:
        for row in build_protocol()["rows"]:
            for version, route in row["versions"].items():
                with self.subTest(app=row["app"], version=version):
                    self.assertEqual("optix_rt_core", route["backend"])
                    self.assertTrue(route["primary_denominator_allowed"])

    def test_v4_superset_rows_are_not_hidden_missing_routes(self) -> None:
        protocol = build_protocol()
        runnable = "runnable_protocol_template"

        for row in protocol["rows"]:
            v4 = row["versions"]["v4_0"]
            with self.subTest(app=row["app"]):
                self.assertIn("must expose or inherit", row["v4_superset_obligation"])
                self.assertEqual(runnable, v4["route_status"])
                self.assertEqual("", v4["blocker"])

    def test_hausdorff_primary_row_is_threshold_not_embree_or_mixed_exact(self) -> None:
        rows = {row["app"]: row for row in build_protocol()["rows"]}
        hausdorff = rows["hausdorff_xhd"]

        self.assertIn("threshold-decision", hausdorff["semantic_contract"])
        self.assertIn("threshold-decision", hausdorff["scale_policy"])
        self.assertIn("directed_threshold_prepared", hausdorff["versions"]["v2_14"]["command_hint"])
        self.assertTrue(
            any("exact nearest-witness row may be reported separately" in note for note in hausdorff["supplemental_notes"])
        )

    def test_written_artifacts_match_validator(self) -> None:
        self.assertTrue(EVIDENCE.exists(), "run scripts/v4_goal4749_final_rt_core_protocol.py first")
        self.assertTrue(REPORT.exists(), "run scripts/v4_goal4749_final_rt_core_protocol.py first")

        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual("passed", payload["validation"]["status"], payload["validation"]["errors"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4750 builds the unified dry-run/POD runner", report)
        self.assertIn("Primary performance denominators must be NVIDIA OptiX/RT-core routes", report)


if __name__ == "__main__":
    unittest.main()
