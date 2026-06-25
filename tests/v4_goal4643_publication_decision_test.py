from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4 import V4_AUTHORIZED_RELEASE_LABEL
from rtdsl.v4_goal4643_publication_decision import V4_GOAL4643_DECISION
from rtdsl.v4_goal4643_publication_decision import validate_v4_goal4643_publication_decision


class V4Goal4643PublicationDecisionTest(unittest.TestCase):
    def test_publication_decision_authorizes_only_bounded_v4_0_0_release(self) -> None:
        decision = validate_v4_goal4643_publication_decision(ROOT)

        self.assertEqual(V4_GOAL4643_DECISION, decision["decision"])
        self.assertEqual("v4.0.0", decision["version"])
        self.assertEqual("4.0.0", decision["pyproject_version"])
        self.assertTrue(decision["release_authorized"])
        self.assertTrue(decision["formal_release_authorized"])
        self.assertEqual(
            V4_AUTHORIZED_RELEASE_LABEL,
            decision["authorized_release_label"],
        )
        self.assertEqual(8, decision["measured_surfaces_count"])
        self.assertEqual(0, decision["candidate_surfaces_count"])
        self.assertEqual((), decision["release_blockers"])

    def test_publication_decision_keeps_forbidden_claims_locked(self) -> None:
        decision = validate_v4_goal4643_publication_decision(ROOT)

        for claim in (
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "app-specific native kernels",
            "Barnes-Hut covered by V4.0",
            "Spatial RayJoin covered by V4.0",
            "LibRTS paper reproduction",
        ):
            self.assertIn(claim, decision["forbidden_claims"])

        for flag in (
            "broad_v4_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "all_benchmark_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "tier3_callback_claim_authorized",
            "raw_optix_callback_claim_authorized",
            "cupy_performance_claim_authorized",
            "c_abi_or_embedding_claim_authorized",
            "non_python_host_claim_authorized",
            "app_specific_native_kernel_authorized",
        ):
            self.assertFalse(decision[flag])

    def test_public_quickstart_reports_formal_release_without_overclaim(self) -> None:
        proc = subprocess.run(
            [sys.executable, "examples/v4/v4_frontdoor_quickstart.py"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["formal_release_authorized"])
        self.assertEqual(
            V4_AUTHORIZED_RELEASE_LABEL,
            payload["authorized_release_label"],
        )
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
