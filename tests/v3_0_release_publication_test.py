from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import tomllib


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs" / "release_reports" / "v3_0_2"
DOCTOR = ROOT / "scripts" / "rtdl_source_tree_doctor.py"


def _load_doctor():
    spec = importlib.util.spec_from_file_location("rtdl_source_tree_doctor_release_test", DOCTOR)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class V30ReleasePublicationTest(unittest.TestCase):
    def test_version_markers_are_v3_0_2(self) -> None:
        self.assertEqual("v3.0.2", (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual("3.0.2", pyproject["project"]["version"])

    def test_release_packet_is_complete(self) -> None:
        for name in (
            "README.md",
            "release_statement.md",
            "support_matrix.md",
            "public_wording_boundaries.md",
            "publication.md",
            "tag_preparation.md",
            "final_closeout.md",
            "major_release_requirements_trace.md",
        ):
            self.assertTrue((RELEASE / name).exists(), name)

        readme = (RELEASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("RTDL v3.0.2 Release Package", readme)
        self.assertIn("Version marker: `v3.0.2`", readme)
        self.assertIn("Embedding, SDK packaging, generated bindings", readme)
        self.assertIn("not part of V3.0", readme)

    def test_current_docs_point_to_v3_0(self) -> None:
        docs = "\n".join(
            (ROOT / rel).read_text(encoding="utf-8")
            for rel in (
                "README.md",
                "docs/README.md",
                "docs/versioning.md",
                "docs/learn/current_claim_boundaries.md",
                "docs/current_main_support_matrix.md",
                "tutorials/current/README.md",
                "examples/current/README.md",
            )
        )
        self.assertIn("v3.0", docs)
        self.assertIn("docs/release_reports/v3_0_2/README.md", docs)
        self.assertNotIn("current v2.14", docs.lower())
        self.assertNotIn("current v2.10", docs.lower())

    def test_embedding_is_v4_scope_not_v3_release_scope(self) -> None:
        combined = "\n".join(
            (RELEASE / name).read_text(encoding="utf-8")
            for name in (
                "README.md",
                "release_statement.md",
                "support_matrix.md",
                "public_wording_boundaries.md",
                "publication.md",
                "final_closeout.md",
            )
        )
        self.assertIn("V4.0 scope", combined)
        self.assertIn("not V3.0 release scope", (ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md").read_text(encoding="utf-8"))
        self.assertNotIn("ships the current C ABI handoff surface", combined)
        self.assertNotIn("C ABI handoff surface", combined)

    def test_source_tree_doctor_keeps_c_abi_reviewer_only(self) -> None:
        doctor = _load_doctor()
        payload = doctor.gather_checks(run_smoke=False)
        checks = {row["name"]: row for row in payload["checks"]}
        self.assertEqual("v3.0.2", payload["version"])
        self.assertEqual("pass", checks["v3.0.2 release package"]["status"])
        self.assertNotIn("V4 preparatory C ABI surface", checks)
        self.assertNotIn("V4 preparatory C ABI docs", checks)
        self.assertEqual([], payload["required_failures"])

        reviewer_payload = doctor.gather_checks(run_smoke=False, include_v4_prep=True)
        reviewer_checks = {row["name"]: row for row in reviewer_payload["checks"]}
        self.assertFalse(reviewer_checks["V4 preparatory C ABI surface"]["required"])
        self.assertFalse(reviewer_checks["V4 preparatory C ABI docs"]["required"])
        self.assertEqual([], reviewer_payload["required_failures"])


if __name__ == "__main__":
    unittest.main()
