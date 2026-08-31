import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_DOC_FILES = (
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "learn" / "README.md",
    ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md",
    ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md",
    ROOT / "docs" / "learn" / "prepared_execution_pattern.md",
    ROOT / "docs" / "learn" / "primitive_discovery_workflow.md",
    ROOT / "docs" / "tutorials" / "README.md",
    ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md",
)

ACTIVE_DOC_DIRS = (
    ROOT / "docs" / "tutorials",
    ROOT / "examples" / "v2_0" / "research_benchmarks",
)

STALE_CURRENT_TERMS = re.compile(r"\bv2\.(?:3|5|6|7|x)\b|\bv2_[67]\b|release package", re.IGNORECASE)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _active_markdown_files() -> tuple[Path, ...]:
    files = set(ACTIVE_DOC_FILES)
    for directory in ACTIVE_DOC_DIRS:
        files.update(directory.glob("*.md"))
        files.update(directory.glob("*/README.md"))
    return tuple(sorted(files))


class Goal3519V28LearnerDocsCleanupTest(unittest.TestCase):
    def test_active_docs_do_not_teach_old_versions(self):
        offenders = []
        for path in _active_markdown_files():
            text = path.read_text(encoding="utf-8")
            for match in STALE_CURRENT_TERMS.finditer(text):
                offenders.append(f"{path.relative_to(ROOT)}:{text.count(chr(10), 0, match.start()) + 1}:{match.group(0)}")

        self.assertEqual(offenders, [])

    def test_main_doors_are_v2_10_facing(self):
        checks = {
            ROOT / "docs" / "README.md": ("RTDL v2.10", "10-app benchmark"),
            ROOT / "docs" / "tutorials" / "README.md": ("RTDL v2.10 Tutorials", "Prepared Execution Pattern"),
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md": ("RTDL v2.10 Research Benchmarks", "primitive first"),
        }
        for path, required in checks.items():
            text = path.read_text(encoding="utf-8")
            for phrase in required:
                self.assertIn(phrase, text, f"{path.relative_to(ROOT)} missing {phrase!r}")

    def test_local_links_in_main_doors_resolve(self):
        docs = (
            ROOT / "docs" / "README.md",
            ROOT / "docs" / "learn" / "README.md",
            ROOT / "docs" / "tutorials" / "README.md",
            ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md",
        )
        missing = []
        for path in docs:
            text = path.read_text(encoding="utf-8")
            for raw_link in MARKDOWN_LINK.findall(text):
                if raw_link.startswith(("http://", "https://", "mailto:")):
                    continue
                target = raw_link.split("#", 1)[0]
                if not target:
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    missing.append(f"{path.relative_to(ROOT)} -> {raw_link}")

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
