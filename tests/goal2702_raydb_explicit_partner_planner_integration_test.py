from __future__ import annotations

import unittest

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb

import rtdsl as rt


class Goal2702RaydbExplicitPartnerPlannerIntegrationTest(unittest.TestCase):
    def test_raydb_reference_fallback_records_explicit_gather_and_partner_plan(self) -> None:
        fixture = raydb.make_fixture(copies=1)
        plan = raydb.make_plan("sum")
        result = raydb._run_paper_rt_device_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode="sum",
            copies=1,
            backend="cpu",
            backend_label="paper_rt_cpu_device_hit_stream_reference",
            allow_reference_fallback=True,
        )

        self.assertTrue(result["matches_cpu_reference"])
        metadata = result["metadata"]
        self.assertEqual(metadata["requested_gather_partner"], "python_reference")
        self.assertEqual(metadata["hit_stream_handoff"]["requested_gather_partner"], "python_reference")
        self.assertEqual(metadata["hit_stream_handoff"]["selected_gather_partner"], "python_reference")
        self.assertTrue(metadata["hit_stream_handoff"]["explicit_partner_choice"])

        partner_plans = metadata["v2_5_hit_stream_partner_plans"]
        self.assertEqual(len(partner_plans), 1)
        partner_plan = partner_plans[0]
        self.assertEqual(partner_plan["operation"], "segmented_sum_f64")
        self.assertEqual(partner_plan["selected_partner"], rt.V2_5_REFERENCE_PARTNER)
        self.assertFalse(partner_plan["fail_closed"])
        self.assertFalse(partner_plan["true_zero_copy_authorized"])
        self.assertFalse(partner_plan["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
