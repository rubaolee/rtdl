from __future__ import annotations

import unittest

from examples.rtdl_v0_7_db_kernel_app_demo import run_app


class Goal462DbKernelAppDemoTest(unittest.TestCase):
    def test_cpu_python_reference_kernel_demo_outputs_expected_rows(self):
        payload = run_app("cpu_python_reference")
        self.assertEqual(payload["app"], "regional_order_dashboard_kernel_form")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertEqual(
            payload["results"]["one_predicate_discounted_ids"],
            [{"row_id": 3}, {"row_id": 4}, {"row_id": 5}, {"row_id": 7}],
        )
        self.assertEqual(
            payload["results"]["two_predicate_campaign_window_ids"],
            [{"row_id": 3}, {"row_id": 4}, {"row_id": 5}, {"row_id": 6}, {"row_id": 7}],
        )
        self.assertEqual(
            payload["results"]["three_predicate_promo_order_ids"],
            [{"row_id": 3}, {"row_id": 4}, {"row_id": 5}, {"row_id": 7}],
        )
        self.assertEqual(
            payload["results"]["open_order_count_by_region"],
            [
                {"count": 2, "region": "east"},
                {"count": 1, "region": "south"},
                {"count": 2, "region": "west"},
            ],
        )
        self.assertEqual(
            payload["results"]["web_revenue_by_region"],
            [
                {"region": "east", "sum": 180},
                {"region": "west", "sum": 240},
            ],
        )


if __name__ == "__main__":
    unittest.main()
