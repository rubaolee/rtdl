from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4547_v3_0_m148_source_tree_doctor_v3_matrix_hint_2026-06-17.md"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4547V30M148SourceTreeDoctorV3MatrixHintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4547_m148_source_tree_doctor_v3_matrix_hint")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_v3_matrix_checks_all_pass(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.source_tree_doctor_v3_matrix_hint.goal4547.v1",
            self.packet["version"],
        )
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_payload_contains_v3_matrix_hint_and_smoke(self) -> None:
        payload = self.packet["doctor_payload"]
        checks = {row["name"]: row for row in payload["checks"]}
        self.assertEqual("pass", checks["V3 current test matrix"]["status"])
        self.assertIn("--group v3_current", checks["V3 current test matrix"]["detail"])
        self.assertEqual("pass", checks["hello-world smoke"]["status"])
        self.assertEqual([], payload["required_failures"])

    def test_docs_and_evidence_index_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        doc = DOCTOR_DOC.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4547 / V3 M148", report)
        self.assertIn("scripts/run_test_matrix.py --group v3_current", doc)
        self.assertIn("Goal4547 source-tree doctor V3 matrix hint", index)

    def test_claim_boundary_remains_blocked(self) -> None:
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
