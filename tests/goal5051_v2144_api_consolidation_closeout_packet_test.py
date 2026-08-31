from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "history" / "internal_docs" / "goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md"


class Goal5051V2144ApiConsolidationCloseoutPacketTest(unittest.TestCase):
    def test_packet_names_public_surface_and_goal_chain(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        for phrase in (
            "DeviceColumnBuffer",
            "PreparedGeometrySession",
            "device_order_by",
            "NumbaPartnerContinuation",
            "Goal5043",
            "Goal5044",
            "Goal5045",
            "Goal5046",
            "Goal5047",
            "Goal5048",
            "Goal5049",
            "Goal5050",
        ):
            self.assertIn(phrase, text)

    def test_packet_preserves_performance_boundary(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("v2.14.4 does not change the v2.14.3 performance headline", text)
        self.assertIn("0.328842s", text)
        self.assertIn("0.187042s", text)
        self.assertIn("1.76x slower", text)
        for forbidden in (
            "v2.14.4 makes RayJoin faster",
            "v2.14.4 reaches author parity",
            "v2.14.4 proves true zero-copy",
            "v2.14.4 replaces RT traversal with Numba",
        ):
            self.assertIn(forbidden, text)

    def test_packet_keeps_group_by_and_legacy_debts_honest(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        self.assertIn("`device_group_by` is not public in v2.14.4", text)
        self.assertIn("export-hygiene debt", text)
        self.assertIn("RayJoin-named native symbols", text)
        self.assertIn("All core/internal symbols are RayJoin-free.", text)
        self.assertIn("Public API names are generic", text)
        self.assertIn("legacy public exports", text)
        self.assertIn("compatibility debt", text)
        self.assertIn("not new v2.14.4 public generic API", text)
        for name in (
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
        ):
            self.assertIn(name, text)

    def test_packet_records_review_and_pod_debts(self) -> None:
        text = PACKET.read_text(encoding="utf-8")
        for phrase in (
            "Goal5048 external review",
            "Goal5049 external review",
            "Goal5050 external review",
            "Goal5051 external review",
            "POD CUDA smoke for public NumbaPartnerContinuation wrapper",
            "POD runtime check for RayJoin app path after device_order_by public migration",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
