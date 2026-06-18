from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4596_v3_0_m197_source_tree_doctor_prefix_stage_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4596_v3_0_m197_source_tree_doctor_prefix_stage_2026-06-17.md"
DOCTOR = ROOT / "scripts/rtdl_source_tree_doctor.py"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4596V30M197SourceTreeDoctorPrefixStageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4596_m197_v3_source_tree_doctor_prefix_stage")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_prefix_stage_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.source_tree_doctor_prefix_stage.goal4596.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_surface_names_prefix_stage_target(self) -> None:
        surface = self.packet["doctor_surface"]
        doctor = DOCTOR.read_text(encoding="utf-8")
        doc = DOCTOR_DOC.read_text(encoding="utf-8")
        self.assertEqual("pass", surface["status"])
        self.assertIn("stage-c-api-prefix", surface["detail"])
        self.assertIn("stage-c-api-prefix:", doctor)
        self.assertIn("make stage-c-api-prefix", doc)
        self.assertIn("It does not build", doc)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4596 / V3 M197", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4596 source-tree doctor prefix stage", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
