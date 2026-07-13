import json
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5382_status_machine_stream_design.py"
)


class Goal5382StatusMachineStreamDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        namespace = runpy.run_path(str(SCRIPT))
        cls.packet = namespace["build_packet"]()

    def test_prior_evidence_records_goal5381_mismatch(self):
        prior = self.packet["prior_evidence"]
        bridge = prior["goal5381_current_bridge_probe"]
        self.assertEqual(prior["goal5374_author_oracle"]["offloading_size"], 27133990)
        self.assertEqual(bridge["bridge_offload_row_count"], 2188225)
        self.assertFalse(bridge["row_count_parity"])
        self.assertAlmostEqual(bridge["row_ratio_rtdl_div_author"], 2188225 / 27133990)

    def test_required_native_stream_is_app_neutral(self):
        stream = self.packet["required_native_stream"]
        self.assertEqual(stream["contract"], "generic_active_query_status_stream_v1")
        self.assertEqual(stream["app_semantics"], "none")
        joined = json.dumps(
            {
                "contract": stream["contract"],
                "columns": stream["minimum_columns"],
                "status_codes": stream["status_codes"],
                "telemetry": stream["required_telemetry"],
            },
            sort_keys=True,
        ).lower()
        for forbidden in ("xhd", "x-hd", "hausdorff", "hd_exec", "dragon", "asian"):
            self.assertNotIn(forbidden, joined)

    def test_design_rejects_bridge_optimization_as_semantic_fix(self):
        rejected = {row["direction"]: row["reason"] for row in self.packet["design_decision"]["rejected_directions"]}
        self.assertIn("vectorize_cpu_active_query_bridge_first", rejected)
        self.assertIn("wrong row denominator", rejected["vectorize_cpu_active_query_bridge_first"])
        self.assertFalse(self.packet["design_decision"]["explicit_lb_support_claimed"])
        self.assertFalse(self.packet["design_decision"]["row_count_parity_claimed"])

    def test_emission_point_preserves_raw_status_denominator(self):
        emission = self.packet["required_native_stream"]["required_emission_point"]
        self.assertIn("before", emission)
        self.assertIn("drops", emission)
        self.assertIn("collapses", emission)
        self.assertIn("offload denominator", emission)

    def test_implementation_plan_requires_pod_row_parity_gate(self):
        first = self.packet["implementation_plan"][0]
        self.assertEqual(first["goal"], "Goal5383")
        self.assertTrue(first["pod_required"])
        acceptance = "\n".join(first["acceptance"])
        self.assertIn("Goal5374 author oracle", acceptance)
        self.assertIn("no explicit -lb claim unless row_count_parity is true", acceptance)

    def test_forbidden_claims_keep_full_reproduction_closed(self):
        forbidden = set(self.packet["forbidden_claims"])
        self.assertIn("explicit -lb support", forbidden)
        self.assertIn("Figure 11 memory parity", forbidden)
        self.assertIn("full X-HD paper reproduction", forbidden)
        self.assertIn("X-HD-specific native RTDL primitive", forbidden)


if __name__ == "__main__":
    unittest.main()
