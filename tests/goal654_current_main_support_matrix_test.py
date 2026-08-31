from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX = REPO_ROOT / "docs" / "current_main_support_matrix.md"


class Goal654CurrentMainSupportMatrixTest(unittest.TestCase):
    def test_current_main_matrix_exists_and_marks_release_boundary(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        self.assertIn("Current released version is `v2.3`.", text)
        self.assertIn("Active pre-release docs target: v2.6", text)
        self.assertIn("Active release engines: Embree for CPU RT, OptiX for NVIDIA RT.", text)
        self.assertIn("Engine ABI rule: native backends stay app-agnostic.", text)
        self.assertIn("Performance rule: a backend flag is not a speedup claim.", text)

    def test_current_main_matrix_lists_native_anyhit_backend_support(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "Any-hit rows",
            "Hit counts",
            "Closest hit",
            "Fixed-radius rows",
            "Segment/polygon witnesses",
            "Partner tensor/custom continuation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_current_main_matrix_preserves_honesty_boundaries(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "broad speedup across all workloads",
            "package-install support",
            "AMD GPU performance",
            "Apple RT performance for the current release target",
            "true zero-copy unless the exact measured path proves device-resident handoff",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_public_entry_points_link_current_main_matrix(self) -> None:
        for path in (
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs" / "README.md",
            REPO_ROOT / "docs" / "current_architecture.md",
            REPO_ROOT / "docs" / "backend_maturity.md",
        ):
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn(
                    "current_main_support_matrix.md",
                    path.read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
