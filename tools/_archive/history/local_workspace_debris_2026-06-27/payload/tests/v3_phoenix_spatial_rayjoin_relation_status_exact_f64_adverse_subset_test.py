import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.json"
)
PACKET_MD = (
    ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_adverse_subset_2026-06-21.md"
)
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_rayjoin_relation_status_exact_f64_adverse_subset.py"
EVIDENCE = (
    ROOT
    / "docs/rebuild/v3/evidence/phoenix_v3_spatial_relation_status_exact_f64_adverse_subset_20260621"
    / "br_county_subset_relation_status_exact_f64_r20_s5.json"
)


class V3PhoenixSpatialRelationStatusExactF64AdverseSubsetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_closes_only_adverse_subset_parity(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "spatial_rayjoin_relation_status_exact_f64_adverse_subset_parity_pass_not_m7",
        )
        self.assertTrue(packet["adverse_subset_parity_closes_blocker"])
        self.assertEqual(packet["dataset"], "tests/fixtures/rayjoin/br_county_subset.cdb")
        self.assertEqual(packet["count_mode"], "relation_status_corrected_executor_validated")
        self.assertEqual(packet["row_count"], 6)
        self.assertTrue(packet["row_count_consistent"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["true_zero_copy_claim_authorized"])

    def test_checks_cover_m3_residency_and_no_row_stream(self) -> None:
        checks = self.packet["checks"]
        self.assertEqual(self.packet["failed_checks"], [])
        self.assertTrue(all(checks.values()))
        self.assertTrue(checks["all_samples_query_stream_resident"])
        self.assertTrue(checks["all_samples_prepared_handle_generic"])
        self.assertTrue(checks["all_samples_native_scalar_count"])
        self.assertTrue(checks["all_samples_no_row_stream_materialized"])
        self.assertTrue(checks["first_sample_validation_authority_recorded"])
        self.assertEqual(self.packet["summary"]["query_stream_residency"], (
            "device_resident_prepared_point_probe_columns_with_reusable_relation_status_corrected_executor"
        ))

    def test_evidence_is_preserved_and_not_toy_promoted(self) -> None:
        self.assertTrue(EVIDENCE.exists())
        evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.assertEqual(evidence["sample_repeat"], 5)
        self.assertEqual(evidence["query_repeat"], 20)
        self.assertEqual(evidence["summary"]["row_count"], 6)
        self.assertEqual(evidence["m7_qualified_release_rows_added"], 0)
        self.assertFalse(evidence["public_speedup_claim_authorized"])
        self.assertFalse(evidence["release_authorized"])
        self.assertIn(
            "This packet closes the adverse-subset parity blocker only.",
            self.markdown,
        )
        self.assertIn("does not authorize M7", self.markdown)

    def test_script_rebuilds_checked_in_packet(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
