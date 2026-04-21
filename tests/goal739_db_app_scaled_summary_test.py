import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_database_analytics_app
from examples import rtdl_sales_risk_screening
from examples import rtdl_v0_7_db_app_demo


class Goal739DbAppScaledSummaryTest(unittest.TestCase):
    def test_regional_scaled_summary_multiplies_reference_counts(self) -> None:
        payload = rtdl_v0_7_db_app_demo.run_app("cpu_reference", copies=3, output_mode="summary")
        self.assertEqual(payload["input_table"]["row_count"], 21)
        self.assertEqual(payload["results"], {})
        self.assertEqual(payload["summary"]["promo_order_count"], 12)
        self.assertEqual(payload["summary"]["open_order_count_by_region"], {"east": 6, "south": 3, "west": 6})
        self.assertEqual(payload["summary"]["web_revenue_by_region"], {"east": 540, "west": 720})

    def test_sales_risk_scaled_summary_omits_full_rows(self) -> None:
        payload = rtdl_sales_risk_screening.run_case("cpu_python_reference", copies=3, output_mode="summary")
        self.assertEqual(payload["row_counts"], {"scan": 12, "grouped_count": 3, "grouped_sum": 3})
        self.assertEqual(payload["rows"], {})
        self.assertEqual(payload["summary"]["risky_order_count_by_region"], {"central": 3, "east": 3, "west": 6})
        self.assertEqual(payload["summary"]["highest_risk_region"], "west")

    def test_unified_db_app_keeps_default_full_behavior(self) -> None:
        payload = rtdl_database_analytics_app.run_app("cpu_python_reference")
        self.assertEqual(payload["copies"], 1)
        self.assertEqual(payload["output_mode"], "full")
        self.assertIn("promo_order_ids", payload["sections"]["regional_dashboard"]["results"])
        self.assertIn("scan", payload["sections"]["sales_risk"]["rows"])

    def test_embree_scaled_summary_matches_cpu_reference_when_available(self) -> None:
        try:
            embree = rtdl_database_analytics_app.run_app("embree", copies=2, output_mode="summary")
        except Exception as exc:
            self.skipTest(f"Embree unavailable: {exc}")
        cpu = rtdl_database_analytics_app.run_app("cpu_python_reference", copies=2, output_mode="summary")
        self.assertEqual(
            embree["sections"]["regional_dashboard"]["summary"],
            cpu["sections"]["regional_dashboard"]["summary"],
        )
        self.assertEqual(
            embree["sections"]["sales_risk"]["summary"],
            cpu["sections"]["sales_risk"]["summary"],
        )


if __name__ == "__main__":
    unittest.main()
