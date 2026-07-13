from __future__ import annotations

from itertools import product
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _contact_manifold_broadphase_schedule() -> dict[str, object]:
    import rtdsl as rt

    obstacle_ids = tuple(range(1000, 1008))
    moving_shape_ids = (2000, 2001, 2002)
    plan = rt.partitioned_traversal_fanout_plan(
        primitive_ids=obstacle_ids,
        ray_ids=moving_shape_ids,
        partition_count=4,
    )
    columns = plan["columns"]
    scheduled_pairs = {
        (ray_id, primitive_id)
        for ray_id, partition_id in zip(
            columns["fanout_ray_ids"], columns["fanout_partition_ids"]
        )
        for primitive_id, primitive_partition_id in zip(
            columns["primitive_ids"], columns["primitive_partition_ids"]
        )
        if partition_id == primitive_partition_id
    }
    return {
        "plan": plan,
        "scheduled_pairs": scheduled_pairs,
        "expected_pairs": set(product(moving_shape_ids, obstacle_ids)),
    }


class Goal5469PartitionedTraversalFanoutContractTest(unittest.TestCase):
    def test_reference_plan_has_complete_exact_pair_coverage(self) -> None:
        payload = _contact_manifold_broadphase_schedule()
        plan = payload["plan"]
        self.assertEqual(payload["scheduled_pairs"], payload["expected_pairs"])
        self.assertEqual(plan["columns"]["partition_loads"], (2, 2, 2, 2))
        self.assertEqual(plan["metadata"]["max_primitives_per_partition"], 2)
        self.assertEqual(plan["metadata"]["fanout_ray_count"], 12)
        self.assertEqual(plan["metadata"]["cartesian_pair_count"], 24)
        self.assertEqual(plan["metadata"]["partitioned_pair_count"], 24)
        self.assertTrue(plan["metadata"]["complete_pair_coverage_by_construction"])
        self.assertFalse(plan["metadata"]["runtime_speedup_claimed"])

    def test_cost_model_is_explicit_and_selects_from_power_of_two_candidates(self) -> None:
        import rtdsl as rt

        selectivity = rt.estimate_partitioned_traversal_selectivity(
            sampled_hit_count=64,
            sampled_ray_count=8,
            sampled_primitive_count=64,
        )
        self.assertEqual(selectivity, 0.125)
        result = rt.select_partitioned_traversal_fanout(
            ray_count=64,
            primitive_count=1024,
            selectivity=0.25,
            intersection_cost_weight=0.9,
            candidate_partition_counts=(1, 2, 4, 8, 16, 32, 64),
        )
        self.assertEqual(result["selected_partition_count"], 32)
        self.assertEqual(result["metadata"]["app_semantics"], "none")
        self.assertFalse(result["metadata"]["runtime_speedup_claimed"])

    def test_contract_fails_closed_on_ambiguous_or_invalid_inputs(self) -> None:
        import rtdsl as rt

        with self.assertRaisesRegex(ValueError, "unique ids"):
            rt.partitioned_traversal_fanout_plan(
                primitive_ids=(1, 1), ray_ids=(2,), partition_count=2
            )
        with self.assertRaisesRegex(ValueError, "power of two"):
            rt.partitioned_traversal_fanout_plan(
                primitive_ids=(1,), ray_ids=(2,), partition_count=3
            )
        with self.assertRaisesRegex(ValueError, "within"):
            rt.select_partitioned_traversal_fanout(
                ray_count=1,
                primitive_count=1,
                selectivity=1.1,
                intersection_cost_weight=0.5,
            )

    def test_non_librts_consumer_and_core_are_app_neutral(self) -> None:
        test_source = Path(__file__).read_text(encoding="utf-8").lower()
        start = test_source.index("def _contact_manifold_broadphase_schedule")
        end = test_source.index("class goal5469")
        consumer = test_source[start:end]
        self.assertIn("contact_manifold", consumer)
        self.assertIn("partitioned_traversal_fanout_plan", consumer)
        for forbidden in ("librts", "rtspatial", "paper", "ray multicast"):
            self.assertNotIn(forbidden, consumer)

        core_source = (ROOT / "src" / "rtdsl" / "partitioned_traversal.py").read_text(
            encoding="utf-8"
        ).lower()
        for forbidden in ("librts", "rtspatial", "paper", "author", "ray multicast"):
            self.assertNotIn(forbidden, core_source)


if __name__ == "__main__":
    unittest.main()
