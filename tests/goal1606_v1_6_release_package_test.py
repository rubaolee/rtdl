from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "docs" / "release_reports" / "v1_6"
README = PACKAGE / "README.md"
RELEASE_STATEMENT = PACKAGE / "release_statement.md"
SUPPORT_MATRIX = PACKAGE / "support_matrix.md"
AUDIT_REPORT = PACKAGE / "audit_report.md"
TAG_PREPARATION = PACKAGE / "tag_preparation.md"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal1606V16ReleasePackageTest(unittest.TestCase):
    def assert_no_affirmative_claims(self, forbidden_list, text):
        import re

        safe_phrases = [
            "not ",
            "false",
            "reject",
            "block",
            "avoid",
            "unsupported",
            "cannot",
            "misconception",
            "do not",
            "does not",
            "never",
            "instead of",
            "disallowed",
            "must not claim",
            "not allowed",
            "no ",
            "unless",
        ]
        for forbidden in forbidden_list:
            for match in re.finditer(re.escape(forbidden), text, re.IGNORECASE):
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end].lower()
                if not any(safe in context for safe in safe_phrases):
                    self.fail(
                        "Forbidden affirmative claim found: "
                        f"'{match.group(0)}' (context: '{text[start:end]}')"
                    )

    def test_release_package_files_exist(self):
        for path in [
            README,
            RELEASE_STATEMENT,
            SUPPORT_MATRIX,
            AUDIT_REPORT,
            TAG_PREPARATION,
        ]:
            self.assertTrue(path.exists(), path)

    def test_release_statement_names_architecture_boundary(self):
        text = _flat(RELEASE_STATEMENT)
        for phrase in [
            "first Python+RTDL architecture milestone",
            "Python remains the app/control layer",
            "RTDL owns the supported RT-shaped primitive contract",
            "Embree and OptiX are the active v1.6 closure backends",
            "`ANY_HIT`, `COUNT_HITS`",
            "`REDUCE_FLOAT(MIN|MAX|SUM)`",
            "`REDUCE_INT(COUNT|SUM)`",
            "v1.6 is an architecture anchor, not a performance freeze",
        ]:
            self.assertIn(phrase, text)

    def test_support_matrix_keeps_pending_and_excluded_surfaces_blocked(self):
        text = _flat(SUPPORT_MATRIX)
        for phrase in [
            "`COLLECT_K_BOUNDED` | pending/experimental",
            "True zero-copy | excluded",
            "Partner tensor handoff | excluded",
            "Package install | excluded",
            "Whole-app speedup | excluded",
            "Broad RTX/GPU speedup | excluded",
            "App-free native internals | excluded",
            "Vulkan/HIPRT/Apple RT active targets | excluded",
            "`--backend optix` is not by itself a public NVIDIA RT-core speedup claim",
        ]:
            self.assertIn(phrase, text)

    def test_audit_report_records_validation_and_remaining_release_gates(self):
        text = _flat(AUDIT_REPORT)
        for phrase in [
            "Windows source-tree validation | pass",
            "Linux source-tree validation | pass",
            "Real NVIDIA OptiX validation | pass",
            "Final 3-AI release consensus | pass",
            "Explicit release/tag authorization | pass",
            "ae92aa8eabc969da856ea730c7b82e19345ca3a3",
            "`v1.6` tag has been published",
        ]:
            self.assertIn(phrase, text)

    def test_tag_preparation_requires_final_consensus_and_authorization(self):
        text = _flat(TAG_PREPARATION)
        for phrase in [
            "Candidate Tag",
            "v1.6",
            "Validation Commit",
            "Tag Target Commit",
            "reviewed release commit that contains",
            "Final 3-AI release consensus accepted",
            "Explicit release/tag authorization is confirmed",
            "git tag -a v1.6",
            "git push origin v1.6",
            "does not authorize moving `v1.6`",
        ]:
            self.assertIn(phrase, text)

    def test_package_avoids_blocked_claims(self):
        joined = "\n".join(
            _flat(path)
            for path in [README, RELEASE_STATEMENT, SUPPORT_MATRIX, AUDIT_REPORT, TAG_PREPARATION]
        )
        self.assert_no_affirmative_claims([
            "RTDL optimizes arbitrary user Python code",
            "RTDL provides whole-application speedup",
            "true zero-copy is supported",
            "`COLLECT_K_BOUNDED` is stable",
            "package-install support is supported",
            "native internals are fully app-agnostic",
            "every `--backend optix` run is a NVIDIA RT-core speedup",
        ], joined)


if __name__ == "__main__":
    unittest.main()
