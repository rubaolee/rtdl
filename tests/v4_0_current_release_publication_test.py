from __future__ import annotations

from pathlib import Path
import unittest

from scripts import run_test_matrix
from scripts.rtdl_source_tree_doctor import gather_checks
from scripts.v4_0_current_front_door_claim_boundary_scan import scan as scan_v4_front_door_claims
from scripts.v4_0_release_promotion_gate import build_payload as build_promotion_payload


ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "docs" / "release_reports" / "v4_0_0"


class V40CurrentReleasePublicationTest(unittest.TestCase):
    def test_version_markers_identify_v4_0_0_source_tree_release(self) -> None:
        self.assertEqual("v4.0.0", (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "rtdl-source-tree"', pyproject)
        self.assertIn('version = "4.0.0"', pyproject)

    def test_release_package_and_front_door_docs_point_to_v4_first(self) -> None:
        for name in (
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "public_wording_boundaries.md",
            "publication.md",
            "final_closeout.md",
            "major_release_requirements_trace.md",
        ):
            self.assertTrue((RELEASE_DIR / name).exists(), name)

        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        release_index = (ROOT / "docs" / "release_reports" / "README.md").read_text(encoding="utf-8")

        for text in (root_readme, docs_index, release_index):
            self.assertIn("V4.0.0", text)
            self.assertIn("v4_0_0/README.md", text)

        self.assertIn("current V4.0.0 source-tree RTDL surface", root_readme)
        self.assertIn("RTDL V4.0.0 is the active source-tree", docs_index)
        self.assertIn("RTDL V4.0.0 Release Package", release_index)

    def test_release_package_keeps_forbidden_claims_blocked(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in RELEASE_DIR.glob("*.md"))
        compact = " ".join(combined.split())

        for token in (
            "fixed_radius_count_threshold_2d",
            "source-tree release",
            "CuPy",
            "Numba",
            "PyTorch",
            "caller-owned",
            "not a PyPI package",
            "public true-zero-copy",
            "public speedup",
            "RT-core speedup",
            "full PyTorch",
            "non-Python host",
        ):
            self.assertIn(token, compact)

        for forbidden_positive in (
            "RTDL is faster",
            "stable V4 SDK",
            "true zero-copy is authorized",
            "async is authorized",
            "PyPI package is released",
        ):
            self.assertNotIn(forbidden_positive, compact)

    def test_claim_scan_authorizes_only_bounded_v4_front_door(self) -> None:
        payload = scan_v4_front_door_claims(ROOT)

        self.assertEqual("pass", payload["status"])
        self.assertFalse(payload["findings"])
        self.assertEqual("v4.0.0", payload["front_door"]["current_version"])
        self.assertTrue(payload["front_door"]["pyproject_version_is_4_0_0"])
        self.assertTrue(payload["front_door"]["v4_0_0_release_package_exists"])

        claims = payload["claim_boundaries"]
        self.assertTrue(claims["v4_current_release_claim_authorized"])
        self.assertTrue(claims["v4_release_package_claim_authorized"])
        self.assertTrue(claims["fixed_radius_m1_python_gpu_operator_claim_authorized"])
        for key in (
            "stable_v4_sdk_claim_authorized",
            "package_install_claim_authorized",
            "public_true_zero_copy_claim_authorized",
            "async_claim_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "pytorch_route_claim_authorized",
            "full_dlpack_route_claim_authorized",
        ):
            self.assertFalse(claims[key], key)

    def test_source_tree_doctor_defaults_to_v4_current_gate(self) -> None:
        payload = gather_checks()
        self.assertEqual("v4.0.0", payload["version"])
        self.assertTrue(payload["ok"])
        checks = {row["name"]: row for row in payload["checks"]}
        self.assertIn("V4 current test matrix", checks)
        self.assertEqual("pass", checks["V4 current test matrix"]["status"])
        self.assertIn("V4.0.0 release package", checks)

    def test_v4_current_matrix_includes_publication_guard(self) -> None:
        modules = run_test_matrix.group_modules("v4_current")
        self.assertIn("tests.v4_0_current_release_publication_test", modules)
        self.assertIn("tests.v4_0_user_tutorials_test", modules)

    def test_release_promotion_gate_passes_with_bounded_claims(self) -> None:
        payload = build_promotion_payload()

        self.assertEqual("pass", payload["status"])
        self.assertTrue(payload["ok"])
        self.assertEqual("v4.0.0", payload["version"])
        self.assertEqual("4.0.0", payload["pyproject_version"])
        self.assertFalse(payload["failures"])
        self.assertTrue(payload["release_reading"]["v4_0_0_current_source_tree_release_authorized"])
        self.assertFalse(payload["release_reading"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["release_reading"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
