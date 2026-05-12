import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1742_v1_8_release_candidate_evidence_packet_2026-05-12.md"


class Goal1742V18ReleaseCandidateEvidencePacketTest(unittest.TestCase):
    def test_packet_declares_review_ready_not_release_authorized(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1_8_release_candidate_packet_ready_for_external_review", text)
        self.assertIn("does not authorize a tag", text)
        self.assertIn("not a final v1.8 release decision", text)
        self.assertIn("not a version bump", text)
        self.assertIn("not a package-install claim", text)

    def test_packet_separates_v1_8_from_v2_0_partner_track(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("v1.8 finishes Python+RTDL productization", text)
        self.assertIn("v2.0 remains the Python+partner+RTDL milestone", text)
        self.assertIn("Protocol first. PyTorch reference first. CuPy conformance alongside it.", text)
        self.assertIn("not a shipped partner-readiness claim", text)

    def test_packet_records_source_tree_boundary_and_packaging_gap(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("source-tree release boundary", text)
        self.assertIn("no `pyproject.toml`", text)
        self.assertIn("no `setup.py`", text)
        self.assertIn("no `setup.cfg`", text)
        self.assertFalse((ROOT / "pyproject.toml").exists())
        self.assertFalse((ROOT / "setup.py").exists())
        self.assertFalse((ROOT / "setup.cfg").exists())

    def test_packet_blocks_overclaims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "v1.8 ships Python+partner+RTDL",
            "universal PyTorch/CuPy support",
            "general true zero-copy support",
            "accelerates arbitrary PyTorch/CuPy programs",
            "accelerates whole applications",
            "Selecting `--backend optix` proves a public speedup",
            "recovered v1.0 Embree app-level rows are public same-contract speedup evidence",
        ):
            self.assertIn(phrase, text)

    def test_packet_records_same_contract_perf_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goals1746/1747 recovered all 14 v1.0 Embree app-level baseline artifacts", text)
        self.assertIn("Goal1748 classified recovered Embree timing comparability", text)
        self.assertIn("Goal1750 summarized same-contract performance evidence", text)
        self.assertIn("OptiX has 15 artifact-pair rows with 12 primary same-contract ratios", text)
        self.assertIn("Embree has one strict same-contract database row", text)

    def test_packet_records_goal1758_multi_backend_native_cleanup(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal1758 migrated the remaining older Apple RT / HIPRT / Oracle / Vulkan", text)
        self.assertIn("segment_pair_intersection", text)
        self.assertIn("shape_pair_relation_flags", text)
        self.assertIn("triangle_cycle_candidates", text)
        self.assertIn("full backend hardware validation for HIPRT, Vulkan, Apple RT, and OptiX remains separate", text)

    def test_packet_requires_external_review_and_user_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Get independent Claude and Gemini review", text)
        self.assertIn("Create a final v1.8 decision/consensus note", text)
        self.assertIn("Bump `VERSION` and tag only if the user explicitly authorizes", text)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), "v1.8")


if __name__ == "__main__":
    unittest.main()
