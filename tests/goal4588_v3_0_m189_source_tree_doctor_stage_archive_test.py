from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4588_v3_0_m189_source_tree_doctor_stage_archive_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4588_v3_0_m189_source_tree_doctor_stage_archive_2026-06-17.md"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4588V30M189SourceTreeDoctorStageArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4588_m189_v3_source_tree_doctor_stage_archive")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_stage_archive_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.source_tree_doctor_stage_archive.goal4588.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_surface_names_archive_target(self) -> None:
        surface = self.packet["doctor_surface"]
        self.assertEqual("pass", surface["status"])
        self.assertIn("package-c-api-stage", surface["detail"])
        self.assertIn("make package-c-api-stage", DOCTOR_DOC.read_text(encoding="utf-8"))

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4588 / V3 M189", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4588 source-tree doctor stage archive", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
