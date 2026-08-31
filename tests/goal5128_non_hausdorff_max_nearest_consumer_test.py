from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class Goal5128FacilityServiceRadiusConsumerTest(unittest.TestCase):
    def test_facility_service_radius_uses_generic_pipeline_without_hd_wrapper(self) -> None:
        import rtdsl as rt

        demand_columns = {
            "ids": [100, 101, 102],
            "x": [0.0, 2.0, 6.0],
            "y": [0.0, 0.0, 0.0],
        }
        facility_columns = {
            "ids": [200, 201],
            "x": [0.0, 4.0],
            "y": [0.0, 0.0],
        }

        candidates = rt.pairwise_l2_distance_candidate_rows_numpy_columns(
            demand_columns,
            facility_columns,
            coordinate_fields=("x", "y"),
            return_metadata=True,
        )
        nearest = rt.nearest_witness_numpy_columns(
            candidates["candidate_rows"],
            candidates["source_ids"],
            return_metadata=True,
        )
        worst_served = rt.max_nearest_distance_witness_numpy_columns(
            nearest["columns"],
            group_ids=nearest["per_group_argmin"]["group_ids"],
            return_metadata=True,
        )

        self.assertEqual(candidates["metadata"]["contract"], "generic_pairwise_l2_distance_candidate_rows")
        self.assertEqual(nearest["metadata"]["contract"], "generic_nearest_witness_columns")
        self.assertEqual(worst_served["metadata"]["contract"], "generic_max_nearest_distance_with_witness")
        self.assertEqual(candidates["metadata"]["app_semantics"], "none")
        self.assertEqual(nearest["metadata"]["app_semantics"], "none")
        self.assertEqual(worst_served["metadata"]["app_semantics"], "none")

        self.assertEqual(nearest["columns"]["source_ids"].tolist(), [100, 101, 102])
        self.assertEqual(nearest["columns"]["nearest_item_ids"].tolist(), [200, 200, 201])
        self.assertEqual(nearest["columns"]["nearest_distances"].tolist(), [0.0, 2.0, 2.0])

        # Tie-break is stable and deterministic: demand point 101 appears before 102.
        self.assertEqual(worst_served["source_id"], 101)
        self.assertEqual(worst_served["item_id"], 200)
        self.assertAlmostEqual(worst_served["value"], 2.0, delta=1e-12)

    def test_non_hd_consumer_test_does_not_call_hd_wrapper(self) -> None:
        source = Path(__file__).read_text(encoding="utf-8").lower()
        start = source.index("def test_facility_service_radius_uses_generic_pipeline_without_hd_wrapper")
        end = source.index("def test_non_hd_consumer_test_does_not_call_hd_wrapper")
        consumer_window = source[start:end]
        self.assertIn("facility_service_radius", consumer_window)
        self.assertIn("pairwise_l2_distance_candidate_rows_numpy_columns", consumer_window)
        self.assertIn("nearest_witness_numpy_columns", consumer_window)
        self.assertIn("max_nearest_distance_witness_numpy_columns", consumer_window)
        self.assertNotIn("directed_haus" + "dorff", consumer_window)
        self.assertNotIn("xhd", consumer_window)
        self.assertNotIn("x-hd", consumer_window)
        self.assertNotIn("paper", consumer_window)
        self.assertNotIn("hd_exec", consumer_window)


if __name__ == "__main__":
    unittest.main()
