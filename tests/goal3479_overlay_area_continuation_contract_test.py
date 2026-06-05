from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "rtdsl" / "v2_8_overlay_area_continuation_contract.py"
REPORT = ROOT / "docs" / "reports" / "goal3479_overlay_area_continuation_contract_2026-06-05.md"


class Goal3479OverlayAreaContinuationContractTest(unittest.TestCase):
    def test_contract_module_defines_scalar_first_targets(self) -> None:
        validation = rt.validate_v2_8_overlay_area_continuation_plan()
        plans = rt.v2_8_overlay_area_continuation_plan()

        self.assertEqual(validation["status"], "accept", validation)
        self.assertEqual(plans[0]["target"], "scalar_exact_area")
        self.assertEqual(plans[0]["priority"], "P0")
        self.assertEqual(plans[1]["target"], "streamed_overlay_geometry")
        self.assertEqual(plans[1]["priority"], "P1")
        self.assertIn("Goal3474", plans[0]["evidence_refs"])
        self.assertIn("Goal3477", plans[1]["evidence_refs"])

    def test_selector_routes_output_modes(self) -> None:
        scalar = rt.select_v2_8_overlay_area_continuation_target(output_mode="area")
        geometry = rt.select_v2_8_overlay_area_continuation_target(output_mode="geometry")

        self.assertEqual(scalar["target"], "scalar_exact_area")
        self.assertEqual(geometry["target"], "streamed_overlay_geometry")
        with self.assertRaisesRegex(ValueError, "unsupported overlay continuation output_mode"):
            rt.select_v2_8_overlay_area_continuation_target(output_mode="app_magic")

    def test_contract_blocks_claims_and_app_specific_engine_logic(self) -> None:
        for plan in rt.v2_8_overlay_area_continuation_plan():
            for field in (
                "app_specific_engine_logic_allowed",
                "automatic_partner_selection_allowed",
                "release_authorized",
                "public_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
                "full_overlay_completion_claim_authorized",
            ):
                with self.subTest(target=plan["target"], field=field):
                    self.assertFalse(plan[field])
            self.assertIn("app-specific native-engine behavior", plan["claim_boundary"])

    def test_module_and_report_record_oracle_numbers(self) -> None:
        module_text = MODULE.read_text(encoding="utf-8")
        report_text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "26.08321766231042",
            "1,086 thresholded positive rows",
            "609 positive MultiPolygon rows",
            "42,314 output vertices",
            "scalar exact-area continuation",
            "streamed component/vertex contract",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, module_text + report_text)


if __name__ == "__main__":
    unittest.main()
