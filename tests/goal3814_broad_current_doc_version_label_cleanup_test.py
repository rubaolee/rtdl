from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3814_broad_current_doc_version_label_cleanup_2026-06-07.md"
SCAN_ROOTS = (
    ROOT / "docs" / "learn",
    ROOT / "docs" / "tutorials",
    ROOT / "examples" / "v2_0" / "getting_started",
    ROOT / "examples" / "v2_0" / "research_benchmarks",
)
STALE_CURRENT_PATTERN = re.compile(
    r"current v2\.8|RTDL v2\.8|v2\.8-facing|current v2\.9|RTDL v2\.9|"
    r"v2_8_benchmark_matrix\(\)|summarize_v2_8_benchmark_matrix\(\)|"
    r"future candidate|not promoted for this row|Numba is a candidate",
    re.IGNORECASE,
)


def _scan_files() -> tuple[Path, ...]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        files.extend(root.rglob("*.md"))
        files.extend(root.rglob("*.py"))
    return tuple(sorted(set(files)))


class Goal3814BroadCurrentDocVersionLabelCleanupTest(unittest.TestCase):
    def test_no_stale_current_facing_version_labels_in_broad_learner_surface(self) -> None:
        offenders: list[str] = []
        for path in _scan_files():
            text = path.read_text(encoding="utf-8")
            for match in STALE_CURRENT_PATTERN.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{path.relative_to(ROOT)}:{line}:{match.group(0)}")
        self.assertEqual(offenders, [])

    def test_historical_method_names_remain_available(self) -> None:
        hausdorff = (
            ROOT
            / "examples"
            / "v2_0"
            / "research_benchmarks"
            / "hausdorff_xhd"
            / "rtdl_hausdorff_v2_function.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"rtdl_v2_user_cuda"', hausdorff)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3814",
            "preserving the historical method key",
            "Historical method names, artifact keys, and report links remain unchanged",
            "No native engine code changed",
            "No release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
