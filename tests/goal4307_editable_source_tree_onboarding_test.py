from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
DOCTOR = ROOT / "scripts" / "rtdl_source_tree_doctor.py"
DOCTOR_DOC = ROOT / "docs" / "learn" / "source_tree_doctor.md"
TUTORIAL = ROOT / "tutorials" / "current" / "01_source_tree_first_run.md"
TUTORIAL_INDEX = ROOT / "tutorials" / "current" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal4307_editable_source_tree_onboarding_2026-06-11.md"


class Goal4307EditableSourceTreeOnboardingTest(unittest.TestCase):
    def test_pyproject_is_source_tree_editable_metadata_not_release_packaging(self) -> None:
        data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
        self.assertEqual(data["project"]["name"], "rtdl-source-tree")
        self.assertEqual(data["project"]["version"], "2.12.0")
        self.assertEqual(data["tool"]["setuptools"]["packages"]["find"]["where"], ["src"])
        self.assertEqual(data["tool"]["setuptools"]["packages"]["find"]["include"], ["rtdsl*"])
        self.assertIn("numpy>=1.26", data["project"]["dependencies"])

    def test_doctor_reports_optional_editable_metadata(self) -> None:
        source = DOCTOR.read_text(encoding="utf-8")
        self.assertIn("optional editable source-tree metadata", source)
        self.assertIn("pyproject.toml", source)
        namespace: dict[str, object] = {"__name__": "goal4307_doctor_import", "__file__": str(DOCTOR)}
        exec(compile(source, str(DOCTOR), "exec"), namespace)
        payload = namespace["gather_checks"]()
        editable = [item for item in payload["checks"] if item["name"] == "optional editable source-tree metadata"]
        self.assertEqual(len(editable), 1)
        self.assertEqual(editable[0]["status"], "pass")
        self.assertFalse(editable[0]["required"])

    def test_public_docs_keep_editable_install_boundary_clear(self) -> None:
        for path in (README, DOCTOR_DOC, TUTORIAL, TUTORIAL_INDEX):
            text = path.read_text(encoding="utf-8")
            self.assertIn("python -m pip install -e .", text)
        boundary_text = README.read_text(encoding="utf-8") + DOCTOR_DOC.read_text(encoding="utf-8")
        for phrase in (
            "not a PyPI",
            "distribution-package",
            "package-install support claim",
        ):
            self.assertIn(phrase, boundary_text)

    def test_report_documents_onboarding_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal4307",
            "editable source-tree",
            "rtdl-source-tree",
            "not a package-install claim",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
