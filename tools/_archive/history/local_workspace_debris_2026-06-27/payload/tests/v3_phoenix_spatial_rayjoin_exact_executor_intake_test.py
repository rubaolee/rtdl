import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_exact_executor_intake.py"
INTAKE_JSON = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.json"
INTAKE_MD = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_spatial_rayjoin_exact_executor_intake_2026-06-21.md"


class V3PhoenixSpatialRayjoinExactExecutorIntakeTest(unittest.TestCase):
    def load(self):
        return json.loads(INTAKE_JSON.read_text(encoding="utf-8"))

    def test_intake_is_not_release_or_m7(self):
        payload = self.load()
        self.assertEqual(payload["status"], "spatial_rayjoin_exact_executor_intake_not_m7")
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["v4_embedding_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)

    def test_exact_executor_packet_and_bottleneck_are_preserved(self):
        payload = self.load()
        exact = payload["exact_executor_packet"]
        self.assertEqual(exact["count_mode"], "exact_prepared_points_executor")
        self.assertEqual(exact["row_count"], 47262)
        self.assertEqual(exact["sample_repeat"], 5)
        self.assertEqual(exact["query_repeat"], 50)
        self.assertEqual(exact["warmup"], 5)
        self.assertEqual(exact["failed_checks"], [])
        self.assertEqual(
            exact["query_stream_residency"],
            "device_resident_prepared_point_probe_columns_with_reusable_exact_executor",
        )

        m3 = payload["m3_bottleneck"]
        self.assertGreater(m3["topology_continuation_over_rt_traversal"], 10.0)
        self.assertGreater(m3["topology_continuation_fraction_of_prepared_query"], 0.9)
        self.assertLess(m3["rt_traversal_fraction_of_prepared_query"], 0.05)
        self.assertEqual(m3["device_transfer_or_residency_sec_median"], 0.0)
        self.assertIn("exact topology continuation/refinement", m3["reading"])

    def test_rejected_fast_probe_and_author_gap_are_not_publishable(self):
        payload = self.load()
        rejected = payload["rejected_device_filtered_probe"]
        self.assertEqual(rejected["status"], "rejected_exact_count_mismatch")
        self.assertEqual(rejected["device_filtered_count"], 47570)
        self.assertEqual(rejected["exact_count"], 47262)
        self.assertFalse(rejected["publishable_fast_route"])

        author = payload["prior_author_gap"]
        self.assertIn("not_direct_public_county", author["scope"])
        self.assertFalse(author["direct_current_packet_comparison_authorized"])
        self.assertGreater(author["rayjoin_rt_speedup_vs_rtdl_optix_native_traversal"], 1.0)

    def test_markdown_keeps_forbidden_shortcuts_and_decision_audit(self):
        text = INTAKE_MD.read_text(encoding="utf-8")
        for phrase in (
            "Spatial RayJoin is the evidence harness, not the product boundary.",
            "Topology continuation / RT traversal",
            "Do not treat the public-county exact-executor packet as RayJoin-author comparison evidence.",
            "Do not publish the rejected device-filtered route.",
            "Do not call prepared point-column residency true zero-copy.",
            "m7_promotion_authorized: false",
            "Goal-Level Decision Self-Audit",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_intake_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "intake.json"
            md_out = Path(tmp) / "intake.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertEqual(md_out.read_text(encoding="utf-8"), INTAKE_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
