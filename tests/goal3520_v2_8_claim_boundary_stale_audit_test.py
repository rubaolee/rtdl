import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_MARKDOWN_DIRS = (
    ROOT / "docs" / "learn",
    ROOT / "docs" / "tutorials",
    ROOT / "examples" / "v2_0" / "research_benchmarks",
)

ALLOWED_VERSIONED_PYTHON_FILES = {
    Path("examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py"),
    Path("examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py"),
    Path("examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"),
    Path("examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"),
    Path("examples/v2_0/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py"),
}

STALE_VERSION_RE = re.compile(r"\bv2\.(?:3|5|6|7|x)\b|\bv2_[567]\b|release package", re.IGNORECASE)
VERSIONED_CODE_RE = re.compile(r"\bv2\.(?:5|6|x)\b|\bv2_[56]\b", re.IGNORECASE)
FORBIDDEN_POSITIVE_CLAIMS = (
    "v2.8 release authorized",
    "public speedup claim authorized",
    "true zero-copy authorized",
    "rtdl beats rayjoin is authorized",
    "full rayjoin reproduction is authorized",
    "automatic partner selection is enabled",
    "pip install -e .",
)


def _active_markdown_files() -> tuple[Path, ...]:
    files = {ROOT / "README.md", ROOT / "docs" / "README.md"}
    for directory in ACTIVE_MARKDOWN_DIRS:
        files.update(directory.rglob("*.md"))
    return tuple(sorted(files))


class Goal3520V28ClaimBoundaryStaleAuditTest(unittest.TestCase):
    def test_active_markdown_keeps_old_versions_outside_history(self):
        offenders = []
        for path in _active_markdown_files():
            text = path.read_text(encoding="utf-8")
            for match in STALE_VERSION_RE.finditer(text):
                rel = path.relative_to(ROOT)
                if rel == Path("README.md") and "History And Audit Trail" in text[: match.start()]:
                    continue
                offenders.append(f"{rel}:{text.count(chr(10), 0, match.start()) + 1}:{match.group(0)}")

        self.assertEqual(offenders, [])

    def test_positive_overclaim_phrases_are_absent(self):
        offenders = []
        for path in _active_markdown_files():
            lower = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_POSITIVE_CLAIMS:
                if phrase in lower:
                    offenders.append(f"{path.relative_to(ROOT)}:{phrase}")

        self.assertEqual(offenders, [])

    def test_python_claim_boundaries_do_not_literal_authorize_claims(self):
        critical_true_literal = re.compile(
            r"['\"](?:"
            r"release_authorized|v2_8_release_authorized|"
            r"public_speedup_claim_authorized|performance_claim_authorized|"
            r"rt_core_speedup_claim_authorized|true_zero_copy_claim_authorized|"
            r"true_zero_copy_authorized|paper_reproduction_claim_authorized|"
            r"paper_speedup_claim_authorized|paper_scale_perf_claim_authorized|"
            r"rtdl_beats_rayjoin_claim_authorized|whole_app_speedup_claim_authorized|"
            r"full_rayjoin_reproduction|automatic_hidden_dispatcher"
            r")['\"]\s*:\s*True\b"
        )
        offenders = []
        for path in (ROOT / "examples" / "v2_0" / "research_benchmarks").glob("**/*.py"):
            text = path.read_text(encoding="utf-8")
            for match in critical_true_literal.finditer(text):
                offenders.append(
                    f"{path.relative_to(ROOT)}:{text.count(chr(10), 0, match.start()) + 1}:{match.group(0)}"
                )

        self.assertEqual(offenders, [])

    def test_versioned_python_residuals_are_quarantined(self):
        offenders = []
        for path in (ROOT / "examples" / "v2_0" / "research_benchmarks").glob("**/*.py"):
            text = path.read_text(encoding="utf-8")
            if not VERSIONED_CODE_RE.search(text):
                continue
            rel = path.relative_to(ROOT)
            if rel not in ALLOWED_VERSIONED_PYTHON_FILES:
                offenders.append(str(rel))

        self.assertEqual(offenders, [])

    def test_future_work_records_legacy_helper_names(self):
        text = (ROOT / "docs" / "research" / "future_version_to_do_list.md").read_text(encoding="utf-8")

        self.assertIn("Legacy Versioned Helper Names", text)
        self.assertIn("v2_6", text)
        self.assertIn("compatibility/protocol names", text)


if __name__ == "__main__":
    unittest.main()
