from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal3050PartnerChoiceDocsTest(unittest.TestCase):
    def _read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_partner_choice_guide_exists_and_preserves_boundaries(self) -> None:
        text = self._read("docs/learn/partner_choice_for_custom_logic.md")

        required_phrases = [
            "Use the RTDL primitive first",
            "Choose the partner explicitly",
            "CuPy",
            "Numba",
            "custom logic",
            "not a release tag",
            "RTDL does not accelerate arbitrary Numba or CuPy programs",
            "Numba is not automatically faster than CuPy",
        ]
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_benchmark_matrix_covers_promoted_apps_and_partner_roles(self) -> None:
        text = self._read("docs/learn/benchmark_partner_reference_matrix.md")

        required_rows = [
            "Hausdorff / X-HD style",
            "Spatial RayJoin",
            "RT-DBSCAN",
            "RTNN",
            "RayDB-style unfused grouped continuation",
            "RayDB fused count/sum",
            "Triangle candidate-row compaction",
            "Triangle scalar answer",
            "Barnes-Hut",
            "Robot collision",
            "Contact manifold",
            "LibRTS-style spatial index",
        ]
        for row in required_rows:
            self.assertIn(row, text)

        required_headers = [
            "Recommended custom partner when needed",
            "CuPy role",
            "Numba role",
            "Current best path summary",
            "Evidence boundary",
        ]
        for header in required_headers:
            self.assertIn(header, text)

        self.assertIn("Users choose partners explicitly", text)
        self.assertIn("Partner-Needed Continuations", text)
        self.assertIn("Primitive-First Paths", text)
        self.assertIn("current_benchmark_adequacy", text)
        self.assertIn("measured prepared-repeat component continuation", text)
        self.assertNotIn("native scalar triangle-count primitive", text)
        self.assertNotIn("native triangle-count primitive", text)

    def test_learner_and_benchmark_doors_link_guidance(self) -> None:
        learner = self._read("docs/learn/README.md")
        benchmarks = self._read("examples/benchmark_apps/README.md")
        frontpage = self._read("README.md")

        self.assertIn("partner_choice_for_custom_logic.md", learner)
        self.assertIn("benchmark_partner_reference_matrix.md", learner)
        self.assertIn("partner_choice_for_custom_logic.md", benchmarks)
        self.assertIn("benchmark_partner_reference_matrix.md", benchmarks)
        self.assertIn("docs/learn/partner_choice_for_custom_logic.md", frontpage)


if __name__ == "__main__":
    unittest.main()
