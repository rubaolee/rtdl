from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Paper-reproduction-apps" / "librts-paper" / "run_goal5502_librts_author_validity_gate.py"
SPEC = importlib.util.spec_from_file_location("goal5502_gate", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def case(author: bool, rtdl: bool) -> dict[str, object]:
    return {
        "case_id": "synthetic",
        "author": {"result_count": 1},
        "rtdl_count": 1,
        "cpu_oracle": {"float32_overlap_count": 1},
        "diagnostic_matches": {
            "author_equals_cpu_float32": author,
            "rtdl_equals_cpu_float32": rtdl,
        },
    }


class Goal5502AuthorValidityGateTest(unittest.TestCase):
    def test_four_way_classification_is_explicit(self) -> None:
        self.assertEqual(
            MODULE.classify_case(case(True, True))["classification"],
            "author_and_rtdl_match_selected_generic_contract",
        )
        self.assertEqual(
            MODULE.classify_case(case(True, False))["decision"],
            "fix_rtdl_before_author_reproduction_claim",
        )
        self.assertEqual(
            MODULE.classify_case(case(False, True))["decision"],
            "preserve_generic_rtdl_do_not_copy_author_divergence",
        )
        self.assertEqual(
            MODULE.classify_case(case(False, False))["decision"],
            "collect_pair_rows_or_contract_evidence",
        )

    def test_gate_does_not_call_author_wrong_from_count_difference(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("author_wrong_is_not_inferred_from_count_difference", text)
        self.assertIn("author_specific_rtdl_core_behavior_authorized", text)
        self.assertNotIn("author_is_wrong = True", text)


if __name__ == "__main__":
    unittest.main()
