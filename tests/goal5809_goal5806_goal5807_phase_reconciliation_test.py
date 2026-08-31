from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from scripts import goal5809_reconcile_goal5806_goal5807_phases as reconcile


ROOT = Path(__file__).resolve().parents[1]


class Goal5809HistoricalPhaseReconciliationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = reconcile.build_reconciliation(
            reconcile.DEFAULT_GOAL5806_ARCHIVE,
            reconcile.DEFAULT_GOAL5807_ARCHIVE,
            reconcile.DEFAULT_GOAL5807_PILOT_SOURCE,
        )

    def test_uses_all_raw_workers_and_no_primary_evaluator(self) -> None:
        self.assertEqual(self.value["goal5806"]["raw_worker_count"], 128)
        self.assertEqual(self.value["goal5807"]["raw_worker_count"], 128)
        self.assertEqual(
            set(self.value["goal5806"]["raw_task_arm_counts"].values()),
            {32})
        self.assertEqual(
            set(self.value["goal5807"]["raw_task_arm_counts"].values()),
            {32})
        self.assertFalse(self.value["method"]["primary_evaluator_imported"])
        self.assertFalse(self.value["method"]["primary_evaluator_output_read"])
        self.assertFalse(self.value["method"]["published_result_read"])

    def test_absolute_medians_reconstruct_known_raw_values(self) -> None:
        rows5806 = {
            (row["task"], row["arm"]): row
            for row in self.value["goal5806"]["absolute_arm_medians"]
        }
        self.assertEqual(
            rows5806[("relation", "RTDL")]["absolute_median_ns"]["PREPARE"],
            622_455_540.5)
        self.assertEqual(
            rows5806[("triangle", "PYOPTIX")]["absolute_median_ns"]
            ["DEPLOYMENT_COLD"], 343_074_732.5)
        self.assertEqual(
            rows5806[("triangle", "RTDL")]["absolute_median_ns"]
            ["STEADY_E2E"], 79_655.0)

        rows5807 = {
            (row["task"], row["arm"]): row
            for row in self.value["goal5807"]["absolute_arm_medians"]
        }
        self.assertEqual(
            rows5807[("relation", "RTDL_PROVIDER_READY")]
            ["absolute_phase_median_ns"]["provider_bind"], 241_608_463.0)
        self.assertEqual(
            rows5807[("triangle", "RTDL_PROVIDER_READY")]
            ["absolute_phase_median_ns"]["app_prepare"], 249_546_756.5)
        self.assertEqual(
            rows5807[(
                "triangle", "PYOPTIX_RUNTIME_PROVIDER_PROGRAM_READY")]
            ["absolute_continuous_prefix_median_ns"]
            ["POST_RUNTIME_PRELOAD_TO_FIRST_EXACT_OUTPUT"], 451_062_290.0)

    def test_provider_bind_precedes_app_prepare_in_every_raw_row(self) -> None:
        invariants = self.value["goal5807"]["raw_invariants"]
        self.assertEqual(
            invariants[
                "provider_bind_ends_no_later_than_app_prepare_starts_count"],
            128)
        self.assertEqual(
            invariants["additive_app_boundary_exact_match_count"], 128)
        self.assertEqual(
            invariants["continuous_prefix_exact_match_count"], 128)
        self.assertFalse(
            self.value["reconciliation"]["same_named_prepare_boundary"])

    def test_archive_and_source_identities_are_exact(self) -> None:
        self.assertEqual(
            self.value["goal5807"]["archive"]["sha256"],
            "dc95d0295b2d4f525255a1543a4adff2dcd2f18c7aa755284921f55e98ec36ee")
        self.assertEqual(
            self.value["goal5807"]["pilot_source"]["sha256"],
            "0b225d3625801b7c2a065a428e148523dbe261d89971b957180281411c061389")
        unsigned = dict(self.value)
        observed = unsigned.pop("reconciliation_sha256")
        self.assertEqual(
            observed,
            hashlib.sha256(json.dumps(
                unsigned, allow_nan=False, separators=(",", ":"),
                sort_keys=True).encode("utf-8")).hexdigest())


if __name__ == "__main__":
    unittest.main()
