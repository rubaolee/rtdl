from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt


class Goal1283V14RuntimeContractValidationTest(unittest.TestCase):
    def test_graph_attach_validates_contract_before_attaching(self) -> None:
        with mock.patch(
            "rtdsl.primitive_contract_schema.validate_primitive_contract",
            side_effect=ValueError("schema blocked"),
        ):
            with self.assertRaisesRegex(ValueError, "schema blocked"):
                rt.attach_visibility_edges_primitive_contract(
                    {"app": "graph"},
                    backend="optix",
                    output_mode="summary",
                    prepared_summary=True,
                )

    def test_sales_risk_attach_validates_contract_before_attaching(self) -> None:
        with mock.patch(
            "rtdsl.primitive_contract_schema.validate_primitive_contract",
            side_effect=ValueError("schema blocked"),
        ):
            with self.assertRaisesRegex(ValueError, "schema blocked"):
                rt.attach_sales_risk_primitive_contract(
                    {"run_phases": {}, "session": {"chunked_compact_summary": True}},
                    backend="embree",
                    output_mode="compact_summary",
                )

    def test_polygon_pair_attach_validates_contract_before_attaching(self) -> None:
        with mock.patch(
            "rtdsl.primitive_contract_schema.validate_primitive_contract",
            side_effect=ValueError("schema blocked"),
        ):
            with self.assertRaisesRegex(ValueError, "schema blocked"):
                rt.attach_polygon_pair_primitive_contract(
                    {"candidate_row_count": 2},
                    backend="optix",
                    output_mode="summary",
                )

    def test_polygon_jaccard_attach_validates_contract_before_attaching(self) -> None:
        with mock.patch(
            "rtdsl.primitive_contract_schema.validate_primitive_contract",
            side_effect=ValueError("schema blocked"),
        ):
            with self.assertRaisesRegex(ValueError, "schema blocked"):
                rt.attach_polygon_jaccard_diagnostic_contract(
                    {"candidate_row_count": 2},
                    backend="optix",
                    output_mode="summary",
                )


if __name__ == "__main__":
    unittest.main()
