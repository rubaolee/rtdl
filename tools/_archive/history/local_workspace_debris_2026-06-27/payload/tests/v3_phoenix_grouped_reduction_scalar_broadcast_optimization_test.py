import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.json"
)
PACKET_MD = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md"
)
REPEAT100_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_grouped_reduction_scalar_broadcast_repeat100_20260620"
)


class V3PhoenixGroupedReductionScalarBroadcastOptimizationTest(unittest.TestCase):
    def payload(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_records_generic_optimization_not_release(self):
        payload = self.payload()
        self.assertEqual(
            payload["status"],
            "grouped_reduction_scalar_broadcast_optimization_pod_evidence_not_release",
        )
        self.assertEqual(payload["optimization"], "ray_3d_scalar_field_broadcast_for_constant_direction_and_tmax")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertTrue(payload["claim_boundary"]["generic_packer_optimization"])
        self.assertFalse(payload["claim_boundary"]["app_specific_native_engine_logic_allowed"])
        self.assertIn("external_review_blocked_phoenix_v3_grouped_reduction_scalar_broadcast_optimization", payload["external_review_blockage"])

    def test_repeat100_artifacts_are_present_and_correctness_gated(self):
        self.assertEqual((REPEAT100_DIR / "repeat100_scalar_broadcast.status").read_text(encoding="utf-8").strip(), "ok")
        for name in ["grouped_sum_scalar_broadcast_repeat100_262144.json", "grouped_sum_scalar_broadcast_repeat100_524288.json"]:
            raw = json.loads((REPEAT100_DIR / name).read_text(encoding="utf-8"))
            self.assertEqual(raw["status"], "ok")
            self.assertTrue(raw["comparison"]["all_match_cpu_reference"])
            self.assertFalse(raw["claim_boundary"]["public_speedup_claim_authorized"])
            rows = {row["backend"]: row for row in raw["rows"]}
            self.assertEqual(rows["embree"]["repeat"], 100)
            self.assertEqual(rows["optix"]["repeat"], 100)

    def test_optimized_numbers_replace_previous_current_values_without_overclaim(self):
        rows = {row["generated_rows"]: row for row in self.payload()["rows"]}
        self.assertGreater(rows[262144]["actual_repeat100_cold_plus_loop_speedup"], 27.5)
        self.assertGreater(rows[524288]["actual_repeat100_cold_plus_loop_speedup"], 2.9)
        self.assertLess(rows[524288]["actual_repeat100_cold_plus_loop_speedup"], 3.0)
        self.assertLess(rows[524288]["optix_workload_build_sec"], 100.0)
        before_after = self.payload()["comparison_to_clean_pre_optimization"]
        self.assertGreater(
            before_after["row_524288_embree_workload_build_before_sec"],
            before_after["row_524288_embree_workload_build_after_sec"] * 2.0,
        )
        self.assertGreater(
            before_after["row_524288_optix_workload_build_before_sec"],
            before_after["row_524288_optix_workload_build_after_sec"] * 1.8,
        )

    def test_markdown_keeps_claim_boundary_visible(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        self.assertIn("generic scalar-broadcast", text)
        self.assertIn("ray-packer", text)
        self.assertIn("27.917x", text)
        self.assertIn("2.983x", text)
        self.assertIn("Do not claim grouped_sum is released", text)
        self.assertIn("Do not hide the 524,288-row cold prepare cost", text)


if __name__ == "__main__":
    unittest.main()
