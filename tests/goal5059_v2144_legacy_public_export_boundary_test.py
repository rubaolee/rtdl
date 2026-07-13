from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
GOAL5050 = ROOT / "history" / "internal_docs" / "goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md"
GOAL5051 = ROOT / "history" / "internal_docs" / "goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md"
GOAL5059 = ROOT / "history" / "internal_docs" / "goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md"
PREFLIGHT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"


LEGACY_RAYJOIN_PUBLIC_EXPORTS = (
    "PreparedEmbreeRayjoinCdbPointLocation2D",
    "PreparedOptixRayjoinCdbPointLocation2D",
    "PreparedOptixRayjoinCdbPointLocationPoints2D",
    "RAYJOIN_PAPER_TARGETS",
    "RayJoinBoundedPlan",
    "RayJoinFeatureServiceLayer",
    "RayJoinPlan",
    "RayJoinPublicAsset",
    "chains_to_rayjoin_cdb_segments",
    "download_rayjoin_sample",
    "lower_to_rayjoin",
    "pack_rayjoin_cdb_segments",
    "prepare_rayjoin_cdb_point_location_2d_embree",
    "prepare_rayjoin_cdb_point_location_2d_optix",
    "rayjoin_bounded_plans",
    "rayjoin_feature_service_layers",
    "rayjoin_public_assets",
)


class Goal5059V2144LegacyPublicExportBoundaryTest(unittest.TestCase):
    def test_rayjoin_named_helpers_are_real_legacy_public_exports(self) -> None:
        dynamic = tuple(sorted(name for name in rt.__all__ if "rayjoin" in name.lower()))
        self.assertEqual(tuple(sorted(LEGACY_RAYJOIN_PUBLIC_EXPORTS)), dynamic)
        for name in LEGACY_RAYJOIN_PUBLIC_EXPORTS:
            self.assertIn(name, rt.__all__)
            self.assertTrue(hasattr(rt, name), name)

    def test_boundary_reports_disclose_legacy_public_exports(self) -> None:
        for path in (GOAL5050, GOAL5051, GOAL5059):
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            self.assertIn("legacy public exports", lowered, path.name)
            self.assertIn("compatibility debt", lowered, path.name)
            self.assertIn("not new v2.14.4 public generic api", lowered, path.name)
            for name in LEGACY_RAYJOIN_PUBLIC_EXPORTS:
                self.assertIn(name, text, path.name)

    def test_preflight_enforces_disclosure_and_review_debt(self) -> None:
        text = PREFLIGHT.read_text(encoding="utf-8")
        self.assertIn("goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md", text)
        self.assertIn("5059", text)
        self.assertIn("legacy_rayjoin_public_exports_disclosed", text)
        self.assertIn("EXPECTED_RAYJOIN_PUBLIC_EXPORTS", text)
        self.assertIn("_rayjoin_exports_from_init_all", text)
        for name in LEGACY_RAYJOIN_PUBLIC_EXPORTS:
            self.assertIn(name, text)


if __name__ == "__main__":
    unittest.main()
