from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3392_exact_membership_bridge_live_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3392_exact_membership_bridge_live_probe_2026-06-04.md"
SCRIPT = ROOT / "scripts" / "goal3392_exact_membership_bridge_live_probe.py"


class Goal3392ExactMembershipBridgeLiveProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.script = SCRIPT.read_text(encoding="utf-8")

    def test_live_probe_materializes_exact_rows_as_partner_columns(self):
        payload = self.payload
        self.assertEqual(payload["schema"], "rtdl.goal3392.exact_membership_bridge_live_probe.v1")
        self.assertEqual(payload["goal"], 3392)
        self.assertEqual(payload["count"], 4096)
        self.assertEqual(payload["point_count"], 4096)
        self.assertEqual(payload["shape_count"], 3762)
        self.assertEqual(payload["exact_row_count"], 11316)
        self.assertEqual(payload["bridge_row_count"], 11316)
        self.assertTrue(payload["pairs_match_exact_rows"])
        self.assertEqual(payload["missing_exact_pair_count"], 0)
        self.assertEqual(payload["extra_pair_count"], 0)
        self.assertIn("prepared.run(points)", self.script)
        self.assertIn("materialize_closed_shape_membership_rows_as_cupy_columns", self.script)

    def test_bridge_metadata_is_explicitly_bounded(self):
        metadata = self.payload["bridge_metadata"]
        self.assertEqual(metadata["source_protocol"], "host_refined_optix_exact_rows")
        self.assertEqual(metadata["output_residency"], "partner_device_after_host_refine_upload")
        self.assertTrue(metadata["host_refined_rows_materialized"])
        self.assertFalse(metadata["native_exact_device_row_stream_produced"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        for key, value in self.payload["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertIn("not the final performance primitive", self.report)
        self.assertIn("native exact closed-shape relation stream", self.report)


if __name__ == "__main__":
    unittest.main()
