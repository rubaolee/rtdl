from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4604_v3_0_m205_toolchain_support_matrix_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4604_v3_0_m205_toolchain_support_matrix_2026-06-17.md"
TOOLCHAIN_DOC = ROOT / "docs/history/v4_preparatory_embedding/v3_0_toolchain_support_matrix.md"
LEARN_README = ROOT / "docs/history/v4_preparatory_embedding/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4604V30M205ToolchainSupportMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4604_m205_v3_toolchain_support_matrix")
        cls.packet = cls.module.build_packet(ROOT, run_live_probe=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_toolchain_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.toolchain_support_matrix.goal4604.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_pod_probe_captures_current_v3_toolchain(self) -> None:
        probe = self.checked_in["live_probe"]
        self.assertTrue(probe["commands"]["nvidia_smi"]["ok"])
        self.assertTrue(probe["packages"]["cupy"]["ok"])
        self.assertTrue(probe["packages"]["numba"]["ok"])
        self.assertTrue(probe["cupy_runtime"]["ok"])
        self.assertTrue(probe["libraries"]["rtdl_optix"])
        self.assertTrue(probe["libraries"]["rtdl_embree"])
        self.assertTrue(probe["libraries"]["rtdl_c_api"])
        self.assertTrue(probe["libraries"]["c_api_stage_archive"])
        self.assertIn("nvcc", probe["commands"])

    def test_docs_and_index_are_wired(self) -> None:
        doc = TOOLCHAIN_DOC.read_text(encoding="utf-8")
        self.assertIn("observed on this pod", doc)
        self.assertIn("not a release support guarantee", doc)
        self.assertIn("V3.0 Toolchain Support Matrix", LEARN_README.read_text(encoding="utf-8"))
        self.assertIn("Goal4604 / V3 M205", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4604 toolchain support matrix", INDEX.read_text(encoding="utf-8"))

    def test_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertTrue(self.checked_in["claim_boundary"]["pod_toolchain_observation_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "pod_toolchain_observation_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
