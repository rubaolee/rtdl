from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2867_v2_5_app_facing_front_door_bypass_audit_2026-05-31.md"

RAW_TRITON_CALL = re.compile(r"\brun_triton_[A-Za-z0-9_]+\s*\(")
ALLOWED_LOW_LEVEL_CONFORMANCE = {
    ROOT / "scripts" / "goal2665_v2_5_triton_grouped_continuation_pod_runner.py",
}
SCAN_DIRS = (
    ROOT / "examples",
    ROOT / "scripts",
    ROOT / "src" / "rtdsl" / "app_adapters",
    ROOT / "src" / "rtdsl" / "adapters",
)


class Goal2867V25AppFacingFrontDoorBypassAuditTest(unittest.TestCase):
    def test_app_facing_code_does_not_call_raw_triton_helpers(self) -> None:
        violations: list[str] = []
        low_level_hits: list[str] = []
        for scan_dir in SCAN_DIRS:
            for path in scan_dir.rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                if not RAW_TRITON_CALL.search(text):
                    continue
                relative = path.relative_to(ROOT).as_posix()
                if path in ALLOWED_LOW_LEVEL_CONFORMANCE:
                    low_level_hits.append(relative)
                    continue
                violations.append(relative)

        self.assertEqual([], violations)
        self.assertEqual(
            ["scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py"],
            low_level_hits,
        )

    def test_report_records_single_low_level_exception_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2867",
            "zero app-facing bypasses",
            "scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py",
            "low-level conformance runner",
            "not a release authorization",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
