from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/rtdl_feature_guide.md",
    "docs/current_architecture.md",
    "docs/capability_boundaries.md",
    "docs/release_facing_examples.md",
    "docs/application_catalog.md",
    "docs/app_engine_support_matrix.md",
    "docs/tutorials/README.md",
    "docs/tutorials/v0_8_app_building.md",
    "docs/tutorials/feature_quickstart_cookbook.md",
    "examples/README.md",
)


class Goal512PublicDocSmokeAuditTest(unittest.TestCase):
    def test_public_docs_do_not_call_v08_released_or_in_progress(self) -> None:
        for rel_path in PUBLIC_DOCS:
            with self.subTest(path=rel_path):
                text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
                self.assertNotIn("released `v0.8`", text)
                self.assertNotIn("released v0.8", text)
                self.assertNotIn("in-progress `v0.8`", text)

    def test_core_public_docs_preserve_v08_evidence_boundaries(self) -> None:
        combined = "\n".join((REPO_ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_DOCS)

        self.assertIn("accepted `v0.8` app-building", combined)
        self.assertIn("Goal507 Hausdorff Linux Performance Report", combined)
        self.assertIn("Goal509 Robot/Barnes-Hut Linux Performance Report", combined)
        self.assertIn("Vulkan is not exposed", combined)
        self.assertIn("per-edge hit-count", combined)
        self.assertIn("full N-body", combined)
        self.assertIn("GTX 1070", combined)
        self.assertIn("RT-core hardware speedup", combined)

    def test_public_markdown_links_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for rel_path in PUBLIC_DOCS:
            doc_path = REPO_ROOT / rel_path
            text = doc_path.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                with self.subTest(path=rel_path, target=target):
                    if target.startswith(("http://", "https://", "mailto:")):
                        continue
                    if target.startswith("#"):
                        continue
                    clean_target = target.split("#", 1)[0]
                    if not clean_target:
                        continue
                    resolved = (doc_path.parent / clean_target).resolve()
                    self.assertTrue(resolved.exists(), f"{rel_path} has missing link target {target}")


if __name__ == "__main__":
    unittest.main()
