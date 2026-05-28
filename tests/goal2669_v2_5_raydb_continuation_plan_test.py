import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.raydb_style import (
    rtdl_raydb_style_benchmark_app as app,
)


class Goal2669V25RaydbContinuationPlanTest(unittest.TestCase):
    def test_count_and_sum_map_to_generic_triton_numba_continuations(self):
        count_plan = app.describe_raydb_v2_5_partner_continuation("count")
        sum_plan = app.describe_raydb_v2_5_partner_continuation("sum")

        self.assertEqual(count_plan["contract_version"], rt.V2_5_PARTNER_CONTINUATION_VERSION)
        self.assertEqual(count_plan["status"], app.RAYDB_V2_5_CONTINUATION_STATUS_DESCRIPTOR_ONLY)
        self.assertEqual(count_plan["operations"], ("segmented_count_i64",))
        self.assertEqual(sum_plan["operations"], ("segmented_sum_f64",))
        for plan in (count_plan, sum_plan):
            self.assertEqual(plan["preferred_partner"], "triton")
            self.assertEqual(plan["fallback_partner"], "numba")
            self.assertTrue(plan["post_rt_continuation_only"])
            self.assertFalse(plan["replaces_rt_traversal"])
            self.assertFalse(plan["promoted_performance_path"])
            self.assertFalse(plan["rt_core_speedup_claim_authorized"])
            self.assertFalse(plan["raw_kernel_required"])
            self.assertTrue(plan["descriptor_only"])
            self.assertEqual(plan["blocked_reason"], None)
            self.assertEqual(plan["triton_descriptors"][0]["status"], "preview_not_promoted")
            self.assertEqual(plan["numba_descriptors"][0]["status"], "preview_not_promoted")

    def test_all_raydb_modes_have_generic_v2_5_continuation_semantics(self):
        avg_plan = app.describe_raydb_v2_5_partner_continuation("avg_as_sum_count")
        min_plan = app.describe_raydb_v2_5_partner_continuation("min")
        max_plan = app.describe_raydb_v2_5_partner_continuation("max")

        self.assertEqual(avg_plan["operations"], ("segmented_sum_f64", "segmented_count_i64"))
        self.assertEqual(avg_plan["status"], app.RAYDB_V2_5_CONTINUATION_STATUS_DESCRIPTOR_ONLY)
        self.assertEqual(min_plan["operations"], ("segmented_min_f64",))
        self.assertEqual(max_plan["operations"], ("segmented_max_f64",))
        for plan in (min_plan, max_plan):
            self.assertEqual(plan["status"], app.RAYDB_V2_5_CONTINUATION_STATUS_DESCRIPTOR_ONLY)
            self.assertEqual(plan["blocked_reason"], None)
            self.assertEqual(plan["triton_descriptors"][0]["status"], "preview_not_promoted")
            self.assertEqual(plan["numba_descriptors"][0]["status"], "partner_descriptor_only")
            self.assertFalse(plan["promoted_performance_path"])

    def test_native_metadata_carries_v2_5_plan_when_backend_is_available(self):
        try:
            payload = app.run_result_mode("count", backend=app.PAPER_RT_EMBREE_BACKEND)
        except (FileNotFoundError, RuntimeError) as exc:
            self.assertRegex(str(exc), "Embree|librtdl_embree|does not export")
            return

        plan = payload["metadata"]["v2_5_partner_continuation"]
        self.assertEqual(plan["operations"], ("segmented_count_i64",))
        self.assertFalse(plan["replaces_rt_traversal"])
        self.assertFalse(plan["promoted_performance_path"])


if __name__ == "__main__":
    unittest.main()
