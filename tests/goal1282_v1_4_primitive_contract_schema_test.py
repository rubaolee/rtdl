from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_graph_analytics_app as graph_app
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app
from examples import rtdl_sales_risk_screening as sales_app
import rtdsl as rt


def _candidate_pairs(*_args, **_kwargs):
    return {(1, 10), (2, 11)}


class _FakeInner:
    transfer = "columnar"


class _FakeDbDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 12

    def compact_summary_batch(self, requests):
        return {
            "risky_scan_count": 4,
            "risky_order_count_by_region": {"east": 1, "west": 2, "central": 1},
            "risky_revenue_by_region": {"east": 310, "west": 430, "central": 260},
        }

    def close(self) -> None:
        pass


class Goal1282V14PrimitiveContractSchemaTest(unittest.TestCase):
    def test_schema_accepts_current_target_contracts(self) -> None:
        graph = graph_app.run_app("cpu_python_reference", "visibility_edges", output_mode="summary")
        with mock.patch.object(sales_app, "_prepare_dataset", return_value=_FakeDbDataset()):
            with sales_app.prepare_session("optix", copies=2) as session:
                sales = session.run(output_mode="compact_summary")
        with mock.patch.object(pair_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            pair = pair_app.run_case("optix", output_mode="summary")
        with mock.patch.object(jaccard_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            jaccard = jaccard_app.run_case("optix", output_mode="summary")

        contracts = (
            graph["sections"]["visibility_edges"]["primitive_contract"],
            sales["primitive_contract"],
            pair["primitive_contract"],
            jaccard["primitive_contract"],
        )
        for contract in contracts:
            with self.subTest(app_row=contract["app_row"]):
                self.assertEqual(rt.primitive_contract_schema_errors(contract), ())
                rt.validate_primitive_contract(contract)

    def test_schema_rejects_missing_required_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing required primitive_contract field"):
            rt.validate_primitive_contract({"app_row": "x"})

    def test_schema_rejects_inactive_backend_with_active_role(self) -> None:
        contract = rt.sales_risk_primitive_contract(
            backend="vulkan",
            output_mode="compact_summary",
            materialization_free=True,
        )
        contract["backend_contract_role"] = "nvidia_rt_target"

        errors = rt.primitive_contract_schema_errors(contract)
        self.assertIn("inactive backend must use compatibility_or_inactive role", errors)

    def test_schema_keeps_jaccard_non_promoting(self) -> None:
        contract = rt.polygon_jaccard_diagnostic_contract(
            backend="optix",
            output_mode="summary",
            candidate_row_count=2,
        )
        contract["public_wording_allowed"] = True

        errors = rt.primitive_contract_schema_errors(contract)
        self.assertIn("Jaccard public_wording_allowed must be false", errors)


if __name__ == "__main__":
    unittest.main()
