from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2331_rayjoin_query_exec_export_patch_plan_2026-05-18.md"
PATCH = ROOT / "docs" / "research" / "rayjoin_query_exec_export_patch.diff"


class Goal2331RayJoinQueryExecExportPatchPlanTest(unittest.TestCase):
    def test_report_explains_why_rayjoin_export_is_needed(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("patch-drafted-build-not-validated", text)
        self.assertIn("not the same", text)
        self.assertIn("RayJoin's generator", text)
        self.assertIn("RayJoin-authored stream", text)
        self.assertIn("does not authorize", text)

    def test_patch_adds_export_flag_and_stream_schema(self) -> None:
        text = PATCH.read_text(encoding="utf-8")
        self.assertIn("export_query_stream", text)
        self.assertIn("rtdl.rayjoin.same_query_stream.v1", text)
        self.assertIn("rayjoin_query_exec_export_patch", text)
        self.assertIn("same_contract_with_rayjoin_query_exec", text)
        self.assertIn("GenerateLSIQueries", text)
        self.assertIn("GeneratePIPQueries", text)


if __name__ == "__main__":
    unittest.main()
