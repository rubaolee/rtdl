from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4002_direct_side_effect_app_probe_pod"
REPORT = ROOT / "docs" / "reports" / "goal4002_grouped_union_direct_side_effect_app_probe_2026-06-08.md"


class Goal4002GroupedUnionDirectSideEffectAppProbeTest(unittest.TestCase):
    def _payload(self, profile: str, mode: str) -> dict[str, object]:
        return json.loads((ARTIFACT_DIR / f"{profile}_{mode}.json").read_text(encoding="utf-8"))

    def test_direct_mode_preserves_column_signatures(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            default = self._payload(profile, "default")
            direct = self._payload(profile, "direct")
            self.assertEqual(default["signature"], direct["signature"])
            self.assertEqual(default["point_count"], 65536)
            self.assertEqual(direct["point_count"], 65536)
            self.assertFalse(default["metadata"]["automatic_hidden_dispatcher"])
            self.assertFalse(direct["metadata"]["automatic_hidden_dispatcher"])
            self.assertFalse(default["metadata"]["automatic_partner_selection_allowed"])
            self.assertFalse(direct["metadata"]["automatic_partner_selection_allowed"])

    def test_direct_mode_is_not_reliable_default_improvement(self) -> None:
        ratios = {}
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            default = self._payload(profile, "default")
            direct = self._payload(profile, "direct")
            ratios[profile] = float(direct["elapsed_sec"]) / float(default["elapsed_sec"])
            self.assertTrue(direct["metadata"]["grouped_union_direct_side_effect_enabled"])
            self.assertFalse(default["metadata"]["grouped_union_direct_side_effect_enabled"])
        self.assertLess(ratios["clustered3d"], 1.0)
        self.assertGreater(ratios["road3d"], 0.99)
        self.assertGreater(ratios["ngsim_dense"], 1.0)

    def test_claim_boundaries_remain_closed(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            for mode in ("default", "direct"):
                payload = self._payload(profile, mode)
                metadata = payload["metadata"]
                self.assertFalse(metadata["release_authorized"])
                self.assertFalse(metadata["public_speedup_claim_authorized"])
                self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
                self.assertFalse(metadata["true_zero_copy_claim_authorized"])
                self.assertFalse(metadata["app_specific_engine_logic_allowed"])

    def test_report_records_rejection_as_default(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`reject-as-default`",
            "Keep it available as an explicit user-selected option",
            "Signature match",
            "Do not promote",
            "generic partition/convergence hybrid",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
