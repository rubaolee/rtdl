from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ROOT_WRAPPER = ROOT / "src" / "native" / "rtdl_oracle.cpp"
OLD_CHUNK = ROOT / "src" / "native" / "oracle" / "rtdl_oracle_polygon.cpp"
NEW_CHUNK = ROOT / "src" / "native" / "oracle" / "rtdl_oracle_geometry_cells.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1674_oracle_root_wrapper_quarantine_2026-05-10.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"


LEAKAGE_RE = re.compile(
    r"\brtdl_[A-Za-z0-9_]*(db|pip|bfs|robot|pose|polygon|knn|hausdorff|jaccard)[A-Za-z0-9_]*\b",
    re.IGNORECASE,
)


class Goal1674OracleRootWrapperQuarantineTest(unittest.TestCase):
    def test_root_wrapper_uses_neutral_geometry_cells_chunk(self) -> None:
        text = ROOT_WRAPPER.read_text(encoding="utf-8")
        self.assertNotIn("rtdl_oracle_polygon.cpp", text)
        self.assertIn("rtdl_oracle_geometry_cells.cpp", text)
        self.assertFalse(OLD_CHUNK.exists())
        self.assertTrue(NEW_CHUNK.exists())

    def test_strict_symbol_scan_no_longer_finds_root_wrapper_symbol(self) -> None:
        hits: set[str] = set()
        for path in (ROOT / "src" / "native").rglob("*"):
            if path.suffix.lower() not in {".cpp", ".h", ".cu", ".mm"}:
                continue
            for match in LEAKAGE_RE.finditer(path.read_text(encoding="utf-8-sig")):
                hits.add(match.group(0))
        self.assertNotIn("rtdl_oracle_polygon", hits)

    def test_reports_record_scope_boundary(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        goal1672_text = GOAL1672.read_text(encoding="utf-8")
        for phrase in (
            "filename/include quarantine only",
            "does not remove polygon or\nJaccard app semantics",
            "does not\nauthorize any app-agnostic native-engine claim",
            "No pod validation was run",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("Goal1674 removed the single `legacy_oracle_wrapper` item", goal1672_text)


if __name__ == "__main__":
    unittest.main()
