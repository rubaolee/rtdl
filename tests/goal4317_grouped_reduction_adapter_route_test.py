from __future__ import annotations

import unittest
from pathlib import Path

import rtdsl as rt
from rtdsl.adapters import reductions


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SEGMENTED_STREAM = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"
REDUCTIONS = ROOT / "src" / "rtdsl" / "adapters" / "reductions.py"
REPORT = ROOT / "docs" / "reports" / "goal4317_grouped_reduction_adapter_route_2026-06-11.md"


class Goal4317GroupedReductionAdapterRouteTest(unittest.TestCase):
    def test_public_reduction_exports_route_through_generic_adapter_module(self) -> None:
        init_source = INIT.read_text(encoding="utf-8")

        for name in (
            "partner_group_any_by_key",
            "partner_group_count_by_key",
            "partner_group_count_unique_pairs_by_key",
            "partner_group_max_by_key",
            "partner_group_min_by_key",
            "partner_group_sum_by_key",
            "partner_group_vector_sum_2d_by_key",
            "partner_metric_table_reduce_batch",
            "partner_metric_table_reduce_by_key",
            "partner_metric_table_reduce_repeated_pattern",
            "partner_unique_pair_keys",
            "global_argmax_u32_f64_partner_columns",
            "grouped_argmax_f64_partner_columns",
            "grouped_argmin_f64_partner_columns",
            "grouped_topk_f64_partner_columns",
            "grouped_vector_sum_2d_partner_columns",
            "prepare_grouped_vector_sum_2d_partner_columns_session",
            "run_grouped_vector_sum_2d_partner_columns_session",
            "measured_grouped_vector_sum_2d_partner_selection",
            "group_argmin_then_global_argmax_partner_columns",
        ):
            self.assertIn(f"from .adapters.reductions import {name}", init_source)
            self.assertNotIn(f"from .partner_adapters import {name}", init_source)
            self.assertIs(getattr(rt, name), getattr(reductions, name))
            self.assertIn(name, reductions.__all__)

    def test_segmented_stream_adapter_uses_reduction_adapter_route(self) -> None:
        source = SEGMENTED_STREAM.read_text(encoding="utf-8")

        self.assertIn("from .adapters.reductions import grouped_vector_sum_2d_partner_columns", source)
        self.assertIn("from .adapters.reductions import grouped_argmin_f64_partner_columns", source)
        self.assertIn("from .adapters.reductions import grouped_argmax_f64_partner_columns", source)
        self.assertIn("from .adapters.reductions import grouped_topk_f64_partner_columns", source)
        self.assertNotIn("from .partner_adapters import grouped_vector_sum_2d_partner_columns", source)
        self.assertNotIn("from .partner_adapters import grouped_argmin_f64_partner_columns", source)
        self.assertNotIn("from .partner_adapters import grouped_argmax_f64_partner_columns", source)
        self.assertNotIn("from .partner_adapters import grouped_topk_f64_partner_columns", source)

    def test_reductions_module_declares_canonical_route_boundary(self) -> None:
        source = REDUCTIONS.read_text(encoding="utf-8")

        self.assertIn("Canonical grouped/summary reduction adapter front doors", source)
        self.assertIn("partner_adapters", source)
        self.assertIn("split incrementally", source)

    def test_report_documents_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4317",
            "grouped/summary reduction adapter route",
            "does not move implementation bodies",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
