from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
COLUMNAR_PARTNER = ROOT / "src" / "rtdsl" / "columnar_partner.py"
NUMBA_CONTINUATION = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
DEVICE_ORDERING = ROOT / "src" / "rtdsl" / "device_ordering.py"


class Goal5046DeviceGroupByPublicReadinessDecisionTest(unittest.TestCase):
    def test_device_group_by_is_not_public(self) -> None:
        self.assertFalse(hasattr(rt, "device_group_by"))
        self.assertNotIn("device_group_by", rt.__all__)

    def test_columnar_partner_still_records_host_row_values_blocker(self) -> None:
        text = COLUMNAR_PARTNER.read_text(encoding="utf-8")
        self.assertIn("Current OptiX compatibility payload stores host scalar row_values.", text)
        self.assertIn(
            "Current OptiX exact filtering and grouped count/sum reductions read host row_values.",
            text,
        )
        self.assertIn('"native_execution_allowed": False', text)

    def test_existing_numba_grouped_assets_are_not_a_public_group_by_contract(self) -> None:
        text = NUMBA_CONTINUATION.read_text(encoding="utf-8")
        self.assertIn("def run_numba_segmented_count_i64", text)
        self.assertIn("def run_numba_segmented_sum_f64", text)
        self.assertIn("host_prefix_sum_used", text)
        self.assertIn("host_present_group_compaction_used", text)
        self.assertIn("promoted_performance_path", text)
        self.assertIn("False", text[text.index('"promoted_performance_path"') : text.index('"rt_traversal_contract_version"')])

    def test_device_order_by_explicitly_does_not_authorize_group_by(self) -> None:
        contract = rt.describe_device_order_by_contract()
        self.assertFalse(contract["supports_public_device_group_by"])
        self.assertFalse(contract["device_group_by_public_claim_authorized"])
        validation = rt.validate_device_order_by_contract(contract)
        self.assertEqual("accept", validation["status"])

        source = DEVICE_ORDERING.read_text(encoding="utf-8")
        self.assertIn('"supports_public_device_group_by": False', source)
        self.assertIn('"device_group_by_public_claim_authorized": False', source)


if __name__ == "__main__":
    unittest.main()
