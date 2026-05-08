from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1512_v1_5_4_collect_k_pod_intake_failure_taxonomy_2026-05-08.md"


class Goal1512CollectKPodIntakeFailureTaxonomyTest(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.exists())

    def test_report_has_immediate_commands(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "git clone https://github.com/rubaolee/rtdl.git rtdl_pod_check",
            "nvidia-smi",
            "nvcc --version",
            "git checkout v8.0.0",
            "OPTIX_PREFIX=/root/vendor/optix-sdk bash scripts/goal1506_v1_5_4_run_optix_collect_k_stage_profile_pod.sh",
        ]:
            self.assertIn(phrase, text)

    def test_report_classifies_failures_without_speculation(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Environment missing NVIDIA driver",
            "CUDA missing but driver present",
            "OptiX headers missing",
            "Driver/SDK mismatch",
            "Shared memory insufficient",
            "Native path fallback",
            "Topology mismatch",
            "Parity failure",
            "Missing profile records",
            "High total time with clean gates",
        ]:
            self.assertIn(phrase, text)

    def test_report_has_accepted_evidence_gates(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "Goal1508 preflight says all requested counts are profile candidates",
            "Counts include `4097`, `65537`, and `131072`",
            "Parity passes",
            "Profile JSONL contains expected records",
            "row_width2_bounded_multi_tile_sort_merge",
            "Claim flags remain false",
        ]:
            self.assertIn(phrase, text)

    def test_report_keeps_claim_boundary_conservative(self):
        text = REPORT.read_text(encoding="utf-8")
        for phrase in [
            "does not authorize public speedup",
            "broad RTX wording",
            "whole-app claims",
            "true zero-copy wording",
            "does not add new measurements",
            "Do not treat fallback smoke as accepted evidence",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
