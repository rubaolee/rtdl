import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1763_v1_8_public_docs_and_learner_path_readiness_2026-05-12.md"


class Goal1763V18PublicDocsAndLearnerPathReadinessTest(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_front_page_teaches_current_design_split(self) -> None:
        text = self._read("README.md")
        self.assertIn("current released version is `v2.0`", text)
        self.assertIn("Python app layer", text)
        self.assertIn("RTDL engine layer", text)
        self.assertIn("native engine must stay app-agnostic", text)
        self.assertIn("input -> traverse -> refine -> emit", text)
        self.assertIn("RTDL is an embedded Python DSL", text)
        self.assertIn("not a fixed box of apps", text)
        self.assertIn("That list is a teaching catalog, not the capacity of", text)
        self.assertNotIn("## What RTDL Contains", text)

    def test_docs_index_tutorial_and_examples_teach_generic_engine_boundary(self) -> None:
        joined = "\n".join(
            (
                self._read("docs/README.md"),
                self._read("docs/quick_tutorial.md"),
                self._read("examples/README.md"),
            )
        )
        for phrase in (
            "Python writes the application",
            "RTDL expresses the RT-shaped kernel",
            "Native backends execute generic engine contracts",
            "Python App, Generic Engine",
            "runtime engine selection",
            "native runtime symbols stay\ngeneric",
        ):
            self.assertIn(phrase, joined)

    def test_current_docs_no_longer_claim_missing_final_docs_or_consensus(self) -> None:
        joined = "\n".join(
            (
                self._read("docs/current_architecture.md"),
                self._read("docs/current_main_support_matrix.md"),
                self._read("docs/public_documentation_map.md"),
            )
        )
        for stale in (
            "final documentation alignment",
            "final v1.8 consensus",
            "v1.8 still requires its own release decision",
            "its own release packet, packaging/install boundary choice",
        ):
            self.assertNotIn(stale, joined)
        self.assertIn("RTDL v2.0 is the current source-tree", joined)
        self.assertIn("current released version is `v2.0`", joined)

    def test_docs_keep_public_overclaims_blocked(self) -> None:
        joined = "\n".join(
            (
                self._read("README.md"),
                self._read("docs/README.md"),
                self._read("docs/public_documentation_map.md"),
                self._read("docs/capability_boundaries.md"),
                self._read("docs/performance_model.md"),
            )
        )
        for phrase in (
            "package-install",
            "broad speedup",
            "whole-application",
            "Python+partner+RTDL",
            "true zero-copy",
            "--backend optix",
        ):
            self.assertIn(phrase, joined)

    def test_report_records_user_requested_doc_surfaces(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for path in (
            "README.md",
            "docs/README.md",
            "docs/quick_tutorial.md",
            "examples/README.md",
            "docs/public_documentation_map.md",
            "docs/current_architecture.md",
        ):
            self.assertIn(path, text)
        self.assertIn("v1_8_public_docs_and_learner_path_ready_pending_release_authorization", text)


if __name__ == "__main__":
    unittest.main()
