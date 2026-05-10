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


def _text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal1602PublicDocsOverclaimAuditTest(unittest.TestCase):
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
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, joined)

    def test_front_door_docs_preserve_optix_and_speedup_boundaries(self):
        joined = "\n".join(_text(path) for path in FRONT_DOOR_DOCS)
        self.assertIn("`--backend optix`", joined)
        self.assertIn("not", joined)
        self.assertIn("speedup", joined)
        self.assertIn("whole-app", joined)

    def test_entry_docs_keep_history_out_of_beginner_flow(self):
        joined = "\n".join(
            _text(path)
            for path in (
                ROOT / "README.md",
                ROOT / "docs" / "README.md",
                ROOT / "docs" / "public_documentation_map.md",
                ROOT / "docs" / "quick_tutorial.md",
                ROOT / "docs" / "tutorials" / "README.md",
            )
        )
        for forbidden in [
            "roadmap drift",
            "does not publish `v1.6`",
            "does not authorize release/tag action",
            "v1.7-v2.0",
            "v1.0 remains",
            "Goal748",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, joined)

    def test_history_index_preserves_where_audit_material_lives(self):
        history = _text(ROOT / "docs" / "history" / "README.md")
        for phrase in (
            "release history",
            "goal and audit trails",
            "review and consensus records",
            "Current Documentation Rule",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, history)


if __name__ == "__main__":
    unittest.main()
