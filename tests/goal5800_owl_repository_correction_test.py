from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "goal5800_build_owl_untimed_bundle.py"
RESULT = (
    ROOT / "history" / "internal_docs" /
    "goal5800_owl_repository_locator_correction_result_20260824.json"
)


class Goal5800OwlRepositoryCorrectionTest(unittest.TestCase):
    def test_future_builder_names_official_nvidia_repository(self) -> None:
        source = BUILDER.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn(
            'OWL_REPOSITORY = "https://github.com/NVIDIA/OWL"', source)
        self.assertNotIn(
            '"repository": "https://github.com/owl-project/owl"', source)

    def test_append_only_bridge_preserves_execution_and_scope(self) -> None:
        result = json.loads(RESULT.read_bytes())
        self.assertEqual(
            result["status"],
            "PASS__P1_REPOSITORY_LOCATOR_CORRECTED_APPEND_ONLY__EXECUTION_PRESERVED",
        )
        self.assertEqual(
            result["official_source_bridge"]["official_file_count"], 203)
        self.assertEqual(
            result["official_source_bridge"]
            ["undeclared_mismatch_count_excluding_overlay"], 0)
        self.assertTrue(
            result["fresh_untimed_reexecution"]
            ["raw_result_byte_identical_to_original"])
        self.assertEqual(
            result["fresh_untimed_reexecution"]
            ["registered_performance_timing_count"], 0)
        self.assertFalse(result["claim_boundary"]["performance_claimed"])
        self.assertFalse(
            result["claim_boundary"]["new_app_generalization_claimed"])


if __name__ == "__main__":
    unittest.main()
