from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX = REPO_ROOT / "docs" / "current_main_support_matrix.md"


class Goal654CurrentMainSupportMatrixTest(unittest.TestCase):
    def test_current_main_matrix_exists_and_marks_release_boundary(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        self.assertIn("Current public release: `v0.9.6`.", text)
        self.assertIn("Current `main`: released `v0.9.6` surface plus", text)
        self.assertIn("released `v0.9.6` tag is the current public release boundary", text)
        self.assertIn("This page is not a speedup claim.", text)

    def test_current_main_matrix_lists_native_anyhit_backend_support(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "Embree any-hit uses `rtcOccluded1`",
            "OptiX any-hit uses `optixTerminateRay()`",
            "Vulkan any-hit uses Vulkan ray tracing shaders with `terminateRayEXT`",
            "HIPRT any-hit uses HIPRT traversal",
            "Apple RT 3D any-hit uses `MPSRayIntersector`",
            "Apple RT 2D any-hit extrudes triangles into MPS-traversed prisms",
            "visibility_rows(..., backend=...)",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_current_main_matrix_preserves_honesty_boundaries(self) -> None:
        text = MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "Apple RT any-hit is not programmable shader-level Apple any-hit.",
            "`reduce_rows` is a deterministic Python standard-library helper",
            "AMD GPU validation for HIPRT",
            "HIPRT CPU fallback",
            "RT-core speedup from the GTX 1070 Linux evidence",
            "Apple MPS ray-tracing-hardware traversal for DB or graph workloads",
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
