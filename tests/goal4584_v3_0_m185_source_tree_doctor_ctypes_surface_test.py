from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4584_v3_0_m185_source_tree_doctor_ctypes_surface_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4584_v3_0_m185_source_tree_doctor_ctypes_surface_2026-06-17.md"
DOCTOR = ROOT / "scripts/rtdl_source_tree_doctor.py"
DOCTOR_DOC = ROOT / "docs/learn/source_tree_doctor.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4584V30M185SourceTreeDoctorCtypesSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4584_m185_v3_source_tree_doctor_ctypes_surface")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_doctor_ctypes_surface_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.source_tree_doctor_ctypes_surface.goal4584.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_doctor_requires_current_embedding_examples(self) -> None:
        doctor = DOCTOR.read_text(encoding="utf-8")
        detail = self.packet["doctor_surface"]["detail"]
        self.assertIn("stage-c-api", detail)
        self.assertIn("Python ctypes examples", detail)
        self.assertIn("c_api_direct_link_client.c", doctor)
        self.assertIn("python_ctypes_client.py", doctor)
        self.assertIn("python_ctypes_aabb2_query_client.py", doctor)

    def test_report_docs_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4584 / V3 M185", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Python `ctypes` lifecycle", DOCTOR_DOC.read_text(encoding="utf-8"))
        self.assertIn("Goal4584 source-tree doctor ctypes surface", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
