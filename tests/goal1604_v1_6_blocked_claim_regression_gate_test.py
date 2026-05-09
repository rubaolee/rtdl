from pathlib import Path
import unittest

from src.rtdsl.v1_6_python_rtdl_readiness import (
    V1_6_PYTHON_RTDL_PENDING_PRIMITIVES,
    V1_6_PYTHON_RTDL_STABLE_PRIMITIVES,
    validate_v1_6_python_rtdl_readiness_gate,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1604_v1_6_blocked_claim_regression_gate_2026-05-09.md"
CURRENT_ARCHITECTURE = ROOT / "docs" / "current_architecture.md"
GOAL1603_REPORT = ROOT / "docs" / "reports" / "goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md"

CLAIM_SURFACE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "current_architecture.md",
    ROOT / "docs" / "capability_boundaries.md",
    ROOT / "docs" / "performance_model.md",
    ROOT / "docs" / "current_main_support_matrix.md",
    ROOT / "docs" / "reports" / "goal1599_v1_6_python_rtdl_historical_milestone_readiness_2026-05-09.md",
    ROOT / "docs" / "reports" / "goal1600_v1_6_python_rtdl_readiness_gate_2026-05-09.md",
    ROOT / "docs" / "reports" / "goal1601_v1_6_release_surface_proposal_2026-05-09.md",
    ROOT / "docs" / "reports" / "goal1602_v1_6_public_docs_overclaim_audit_2026-05-09.md",
    ROOT / "docs" / "reports" / "goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md",
)
SOURCE_TREE_USAGE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "tutorials" / "README.md",
    ROOT / "docs" / "release_reports" / "v1_5" / "README.md",
    ROOT / "docs" / "release_reports" / "v1_5" / "support_matrix.md",
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class Goal1604V16BlockedClaimRegressionGateTest(unittest.TestCase):
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
            "unless",
        ]
        for forbidden in forbidden_list:
            for match in re.finditer(re.escape(forbidden), text, re.IGNORECASE):
                start = max(0, match.start() - 120)
                end = min(len(text), match.end() + 120)
                context = text[start:end].lower()
                if not any(safe in context for safe in safe_phrases):
                    self.fail(
                        "Forbidden affirmative claim found: "
                        f"'{match.group(0)}' (context: '{text[start:end]}')"
                    )

    def test_readiness_gate_keeps_unsupported_claim_flags_blocked(self):
        gate = validate_v1_6_python_rtdl_readiness_gate(repo_root=ROOT)
        for flag in [
            "stable_collect_k_bounded_promotion_authorized",
            "public_speedup_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rtx_or_gpu_acceleration_claim_authorized",
            "true_zero_copy_wording_authorized",
            "partner_tensor_handoff_authorized",
            "package_install_support_authorized",
        ]:
            self.assertIs(gate[flag], False)

    def test_collect_k_remains_pending_not_stable(self):
        self.assertIn("COLLECT_K_BOUNDED", V1_6_PYTHON_RTDL_PENDING_PRIMITIVES)
        self.assertNotIn("COLLECT_K_BOUNDED", V1_6_PYTHON_RTDL_STABLE_PRIMITIVES)

    def test_claim_surface_docs_avoid_forbidden_broad_claims(self):
        joined = "\n".join(_flat(path) for path in CLAIM_SURFACE_DOCS)
        self.assert_no_affirmative_claims([
            "RTDL optimizes arbitrary user Python code",
            "RTDL accelerates arbitrary Python",
            "RTDL provides whole-application speedup",
            "whole-app speedup is authorized",
            "all `--backend optix` runs are NVIDIA RT-core speedups",
            "`--backend optix` automatically means NVIDIA RT-core speedup",
            "true zero-copy is supported",
            "true zero-copy is authorized",
            "`COLLECT_K_BOUNDED` is stable",
            "COLLECT_K_BOUNDED is now stable",
            "partner tensor handoff is supported",
            "partner tensor handoff is authorized",
            "RTDL native internals are fully app-agnostic",
            "all native exports are app-name-free",
        ], joined)

    def test_source_tree_docs_do_not_claim_package_install_support(self):
        joined = "\n".join(_flat(path) for path in SOURCE_TREE_USAGE_DOCS)
        self.assert_no_affirmative_claims([
            # Editable installs are blocked until packaging metadata exists and is validated.
            "pip install -e .",
            "pip install rtdl",
            "python -m pip install rtdl",
            "package-install support is authorized",
        ], joined)
        self.assertIn("PYTHONPATH=src:.", joined)

    def test_architecture_docs_preserve_track_split(self):
        text = _flat(CURRENT_ARCHITECTURE)
        self.assertIn("v1.6 is the current release line and the first Python+RTDL architecture milestone", text)
        self.assertIn("v1.6 is an architecture anchor, not a performance freeze", text)
        self.assertIn("v1.7-v2.0 are the staged Python+partner+RTDL mechanism track", text)
        self.assertNotIn("v1.6-v2.0 are the staged partner-mechanism track", text)

    def test_native_internals_full_app_agnostic_claim_stays_blocked(self):
        text = _flat(GOAL1603_REPORT)
        self.assertIn("does block any claim that native internals are fully app-agnostic", text)
        self.assertIn("Excluded/internal surface: app-shaped compatibility and proof exports", text)

    def test_report_records_gate_scope_without_publishing_v1_6(self):
        text = _flat(REPORT)
        for phrase in [
            "does not publish `v1.6`",
            "does not authorize release/tag action",
            "arbitrary user Python code",
            "whole-application speedup",
            "true zero-copy",
            "`COLLECT_K_BOUNDED` is stable",
            "Package-install usage",
            "real NVIDIA OptiX evidence",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
