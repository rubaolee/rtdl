from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4155_predicate_aware_direct_status_implementation_plan_2026-06-09.md"


class Goal4155PredicateAwareDirectStatusImplementationPlanTest(unittest.TestCase):
    def test_plan_is_generic_and_same_contract_gated(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "implementation-plan-ready",
            "Generic Contract",
            "caller-supplied vertex predicate flags",
            "deterministic neighbor-root policy",
            "No native ABI may contain",
            "Timings must be same-contract only",
            "does not authorize implementation promotion",
        ):
            self.assertIn(fragment, report)

        for forbidden_native_term in ("`dbscan`", "`cluster`", "`core`", "`border`", "`noise`"):
            self.assertIn(forbidden_native_term, report)


if __name__ == "__main__":
    unittest.main()
