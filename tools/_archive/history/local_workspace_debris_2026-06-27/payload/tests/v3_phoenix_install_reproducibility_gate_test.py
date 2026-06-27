import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_install_reproducibility_gate.py"
INSTALLER = ROOT / "scripts" / "v3_install_gpu_pod_env.sh"
STRATEGY = ROOT / "docs" / "rebuild" / "v3" / "v3_install_reproducibility_strategy_2026-06-21.md"
CANDIDATE = ROOT / "docs" / "rebuild" / "v3" / "v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md"
SCOPED_WORDING = (
    ROOT / "docs" / "rebuild" / "v3" / "v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md"
)


class V3PhoenixInstallReproducibilityGateTest(unittest.TestCase):
    def test_gate_classifies_installer_as_staged_pod_gate_only(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["tool"], "v3_phoenix_install_reproducibility_gate")
        self.assertEqual(payload["status"], "staged_pod_gate_present_general_release_installer_not_ready")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["package_install_claim_authorized"])
        self.assertTrue(payload["staged_gpu_pod_gate_available"])
        self.assertTrue(payload["source_tree_pod_gated_candidate_present"])
        self.assertTrue(payload["source_tree_pod_gated_candidate_reviewed"])
        self.assertTrue(payload["source_tree_pod_gated_scoped_release_wording_reviewed"])
        self.assertTrue(payload["source_tree_pod_gated_thirteen_row_scope_extension_reviewed"])
        self.assertFalse(payload["aggregate_13_row_installer_scope_review_required"])
        self.assertEqual(payload["release_scope"], "source_tree_pod_gated_thirteen_row")
        self.assertFalse(payload["general_release_installer_ready"])
        self.assertTrue(payload["installer_closes_release_blocker"])
        self.assertEqual(payload["installer_closes_release_blocker_scope"], "source_tree_pod_gated_thirteen_row")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["source_tree_candidate_reviewed_not_release"])
        self.assertTrue(payload["checks"]["claude_candidate_review_approves_with_amendments_not_release"])
        self.assertTrue(payload["checks"]["codex_candidate_consensus_reviewed_not_release"])
        self.assertTrue(payload["checks"]["scoped_wording_candidate_reviewed_not_release"])
        self.assertTrue(payload["checks"]["scoped_wording_claude_review_accepts_with_amendments_not_release"])
        self.assertTrue(payload["checks"]["scoped_wording_codex_consensus_closes_installer_scope_not_release"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_candidate_reviewed_not_release"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_claude_accepts_with_amendments_not_release"])
        self.assertTrue(payload["checks"]["thirteen_row_scope_extension_codex_consensus_reviewed_not_release"])
        self.assertEqual(payload["evidence"]["accept_flag"], "--accept-experimental-pod-gate")
        self.assertEqual(payload["evidence"]["gpu_env_gate_dry_run"]["status"], "dry_run")
        self.assertTrue(payload["evidence"]["install_scope"]["source_tree_pod_gated_candidate_present"])
        self.assertTrue(payload["evidence"]["install_scope"]["source_tree_pod_gated_candidate_reviewed"])
        self.assertTrue(payload["evidence"]["install_scope"]["source_tree_pod_gated_scoped_release_wording_reviewed"])
        self.assertTrue(
            payload["evidence"]["install_scope"]["source_tree_pod_gated_thirteen_row_scope_extension_reviewed"]
        )
        self.assertFalse(payload["evidence"]["install_scope"]["aggregate_13_row_installer_scope_review_required"])
        self.assertEqual(payload["evidence"]["install_scope"]["release_scope"], "source_tree_pod_gated_thirteen_row")

    def test_installer_keeps_experimental_accept_flag_and_no_repair_label(self):
        text = INSTALLER.read_text(encoding="utf-8")
        self.assertIn("--accept-experimental-pod-gate", text)
        self.assertIn("staged Python GPU package set", text)
        self.assertIn("not a general release installer", text)
        self.assertIn("python3 scripts/v3_gpu_python_env_gate.py --pretty", text)
        self.assertNotIn("Repair Pass", text)

    def test_strategy_doc_records_current_non_release_status(self):
        text = STRATEGY.read_text(encoding="utf-8")
        for phrase in (
            "staged_pod_gate_present_general_release_installer_not_ready",
            "staged_gpu_pod_gate_available: true",
            "general_release_installer_ready: false",
            "package_install_claim_authorized: false",
            "installer_closes_release_blocker: true",
            "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
            "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
            "aggregate_13_row_installer_scope_review_required: false",
            "--accept-experimental-pod-gate",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, text)

    def test_source_tree_pod_gated_candidate_is_reviewed_not_release(self):
        text = CANDIDATE.read_text(encoding="utf-8")
        for phrase in (
            "source_tree_pod_gated_candidate_reviewed_not_release",
            "not a general release installer",
            "not package-install wording",
            "not release authorization",
            "NUMBA_CUDA_PREFIX",
            "numba_cuda_jit: pass",
            "Candidate-Level Non-Closure",
            "source_tree_pod_gated_candidate_present: true",
            "source_tree_pod_gated_candidate_reviewed: true",
            "release_scope: source_tree_pod_gated_twelve_row",
            "installer_closes_release_blocker: true",
            "installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row",
            "general_release_installer_ready: false",
            "accepted source-tree/pod-gated release scope",
        ):
            self.assertIn(phrase, text)

    def test_scoped_release_wording_is_reviewed_not_release(self):
        text = SCOPED_WORDING.read_text(encoding="utf-8")
        for phrase in (
            "source_tree_pod_gated_scoped_release_wording_reviewed_not_release",
            "release_scope: source_tree_pod_gated_twelve_row",
            "installer_closes_release_blocker: true",
            "installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row",
            "release_authorized: false",
            "general_release_installer_ready: false",
            "package_install_claim_authorized: false",
            "This is not a general package installer.",
            "This does not by itself authorize V3 release.",
        ):
            self.assertIn(phrase, text)

    def test_gate_records_user_required_decision_audit(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        audit = json.loads(completed.stdout)["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("No.", audit["was_i_foolish"])
        self.assertIn("silently broadening", audit["foolish_actions"])
        self.assertIn("aggregate 13-row release-readiness review", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()
