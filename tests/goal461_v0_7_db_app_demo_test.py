from __future__ import annotations

import unittest

from examples.rtdl_v0_7_db_app_demo import run_app


class Goal461DbAppDemoTest(unittest.TestCase):
    def test_cpu_reference_demo_outputs_app_ready_rows(self):
        payload = run_app("cpu_reference")
        self.assertEqual(payload["app"], "regional_order_dashboard")
        self.assertEqual(payload["backend"], "cpu_reference")
        self.assertEqual(payload["input_table"]["row_count"], 7)
        self.assertEqual(
            payload["results"]["promo_order_ids"],
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
