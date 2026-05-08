from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN_MD = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_plan_2026-05-08.md"


class Goal1506V154OptixCollectKStageProfilePlanTest(unittest.TestCase):
    def test_plan_keeps_claim_boundary_conservative(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        self.assertIn("Local source review only", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("Claim flags all false", text)
        self.assertIn("does not change the experimental status", text)

    def test_plan_records_next_pod_stage_measurement_targets(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        for phrase in (
            "Tile sort time",
            "Merge kernel time by level",
            "Host synchronization and metadata download time",
            "Final device-to-device output copy time",
            "First-call PTX compile/module-load overhead",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_plan_records_current_tiled_topology_for_large_counts(self) -> None:
        text = PLAN_MD.read_text(encoding="utf-8")

        self.assertIn("For `131072` candidates", text)
        self.assertIn("`32` sort kernel launches", text)
        self.assertIn("`31` merge kernel launches", text)
        self.assertIn("`126` tiny device-to-host metadata fields", text)
        self.assertIn("For `65537` candidates", text)
        self.assertIn("`17` sort kernel launches", text)
        self.assertIn("`16` merge kernel launches", text)
        self.assertIn("`66` tiny device-to-host metadata fields", text)


if __name__ == "__main__":
    unittest.main()
