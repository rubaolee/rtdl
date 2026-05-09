from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FRONT_DOOR_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "current_architecture.md",
    ROOT / "docs" / "performance_model.md",
)
CURRENT_USER_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "current_architecture.md",
    ROOT / "docs" / "capability_boundaries.md",
    ROOT / "docs" / "rtdl_feature_guide.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "tutorials" / "README.md",
    ROOT / "docs" / "app_example_quickstart.md",
    ROOT / "docs" / "application_catalog.md",
    ROOT / "docs" / "technical_app_notes" / "README.md",
    ROOT / "docs" / "technical_app_notes" / "app_implementation_matrix.md",
    ROOT / "docs" / "technical_app_notes" / "app_primitive_classification.md",
    ROOT / "docs" / "performance_model.md",
    ROOT / "docs" / "current_main_support_matrix.md",
    ROOT / "docs" / "features" / "engine_support_matrix.md",
)
CURRENT_ARCHITECTURE = ROOT / "docs" / "current_architecture.md"
REPORT = ROOT / "docs" / "reports" / "goal1602_v1_6_public_docs_overclaim_audit_2026-05-09.md"


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal1602V16PublicDocsOverclaimAuditTest(unittest.TestCase):
    def test_current_architecture_uses_accepted_v1_6_roadmap(self):
        text = _text(CURRENT_ARCHITECTURE)
        self.assertIn("v1.6 is the planned first Python+RTDL architecture closure milestone", text)
        self.assertIn("not a performance freeze", text)
        self.assertIn("v1.7-v2.0 are the staged Python+partner+RTDL mechanism track", text)
        self.assertNotIn("v1.6-v2.0 are the staged partner-mechanism track", text)

    def test_front_door_docs_do_not_publish_v1_6(self):
        joined = "\n".join(_text(path) for path in CURRENT_USER_DOCS)
        for forbidden in [
            "v1.6 is released",
            "v1.6 is now available",
            "v1.6 is stable",
            "v1.6 ships",
            "v1.6 has shipped",
            "current released version is `v1.6`",
            "v1.6 release tag action is authorized",
            "publish `v1.6` now",
            "v1.6 public release is authorized",
            "v1.6 release is authorized",
        ]:
            self.assertNotIn(forbidden, joined)

    def test_current_user_docs_do_not_authorize_blocked_claims(self):
        joined = "\n".join(_text(path) for path in CURRENT_USER_DOCS)
        for forbidden in [
            "COLLECT_K_BOUNDED is stable",
            "stable COLLECT_K_BOUNDED primitive",
            "zero-copy is authorized",
            "true zero-copy is authorized",
            "whole-app speedup is authorized",
            "public speedup is authorized",
            "every `--backend optix` run is a NVIDIA RT-core speedup",
            "pip install -e .",
        ]:
            self.assertNotIn(forbidden, joined)

    def test_front_door_docs_preserve_optix_and_speedup_boundaries(self):
        joined = "\n".join(_text(path) for path in FRONT_DOOR_DOCS)
        self.assertIn("`--backend optix` is not by itself", joined)
        self.assertIn("public NVIDIA RT-core speedup claim", joined)
        self.assertIn("not a whole-app speedup release", joined)
        self.assertIn("public speedup claim", joined)

    def test_front_door_docs_preserve_collect_and_zero_copy_boundaries(self):
        joined = "\n".join(_text(path) for path in FRONT_DOOR_DOCS)
        self.assertIn("`COLLECT_K_BOUNDED` remains experimental", joined)
        self.assertIn("no zero-copy wording", joined)
        self.assertIn("zero-copy or low-copy interop with GPU compute tools", joined)
        self.assertIn("Until that architecture exists", joined)

    def test_report_records_fixed_drift_and_non_authorization(self):
        text = _text(REPORT)
        for phrase in [
            "roadmap drift was found and fixed",
            "v1.6 is the planned first Python+RTDL architecture closure milestone",
            "v1.7-v2.0 are the staged Python+partner+RTDL mechanism track",
            "does not publish `v1.6`",
            "does not authorize release/tag action",
            "does not promote `COLLECT_K_BOUNDED`",
            "does not authorize true zero-copy or partner claims",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
