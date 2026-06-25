from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_goal4642_final_authorization_packet import validate_v4_goal4642_final_authorization_packet
from rtdsl.v4_release_decision import v4_goal4632_release_decision


PUBLIC_FRONT_DOOR_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "future" / "v4" / "tier2_operator_catalog.md",
    ROOT / "future" / "v4" / "v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md",
)


class V4Goal4644PostReleaseGuardrailsTest(unittest.TestCase):
    def test_machine_forbidden_claims_cover_deferred_and_reproduction_overclaims(self) -> None:
        release_decision = v4_goal4632_release_decision()
        packet = validate_v4_goal4642_final_authorization_packet(ROOT)

        required_forbidden = {
            "Barnes-Hut covered by V4.0",
            "Spatial RayJoin covered by V4.0",
            "LibRTS paper reproduction",
        }
        self.assertTrue(required_forbidden.issubset(set(release_decision["forbidden_claims"])))
        self.assertTrue(required_forbidden.issubset(set(packet["forbidden_claims"])))

    def test_candidate_surfaces_are_not_counted_as_measured(self) -> None:
        decision = v4_goal4632_release_decision()

        self.assertEqual(8, decision["measured_surfaces_count"])
        self.assertEqual(0, decision["candidate_surfaces_count"])
        self.assertEqual(0, decision["coverage_summary"]["by_status"]["candidate_not_measured_release_coverage"])
        self.assertEqual(2, decision["coverage_summary"]["by_status"]["deferred_or_uncovered_v4_0"])

    def test_public_docs_keep_release_caveats_and_no_stale_goal4640_4641_gate(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("formal high-performance generic RT-core operator", readme)
        self.assertNotIn("gated on public-doc\ncleanup, clean-tree reproducibility", readme)

        required_caveats = (
            "whole-application speedup",
            "public true-zero-copy",
            "Tier-3",
            "CuPy",
        )
        for path in PUBLIC_FRONT_DOOR_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                for caveat in required_caveats:
                    self.assertIn(caveat, text)

    def test_deferred_families_remain_out_of_v4_0_claims(self) -> None:
        packet = (ROOT / "future" / "v4" / "v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("spatial_rayjoin", packet)
        self.assertIn("barnes_hut", packet)
        self.assertIn("deferred/excluded", packet)
        self.assertIn("must not be used in V4.0 coverage or speedup claims", packet)


if __name__ == "__main__":
    unittest.main()
