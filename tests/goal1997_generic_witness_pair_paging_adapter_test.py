from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
GOAL1856 = ROOT / "scripts" / "goal1856_segment_polygon_v2_partner_perf.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1997_generic_witness_pair_paging_adapter_2026-05-14.md"


class Goal1997GenericWitnessPairPagingAdapterTest(unittest.TestCase):
    def test_generic_witness_pair_paging_adapter_is_public(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def ray_primitive_witness_pair_page_optix_prepared_partner_columns", adapters)
        self.assertIn("partner_page_columns(", adapters)
        self.assertIn('"witness_ray_ids"', adapters)
        self.assertIn('"witness_primitive_ids"', adapters)
        self.assertIn("not_performed_generic_witness_page_only", adapters)
        self.assertIn("generic_ray_primitive_witness_pairs", adapters)
        self.assertIn(
            "from .partner_adapters import ray_primitive_witness_pair_page_optix_prepared_partner_columns",
            init_text,
        )
        self.assertIn('"ray_primitive_witness_pair_page_optix_prepared_partner_columns"', init_text)

    def test_all_witness_contract_rejects_float64_ray_columns(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        perf = GOAL1856.read_text(encoding="utf-8")

        self.assertIn("bounded all-witness ray column", runtime)
        self.assertIn("must use dtype float32", runtime)
        self.assertIn('"ox": runtime["tensor"]([segment.x0 for segment in segments], runtime["float32"])', perf)
        self.assertNotIn('"ox": runtime["tensor"]([segment.x0 for segment in segments], runtime["float64"])', perf)

    def test_report_and_preflight_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("generic witness-pair page", report)
        self.assertIn("does not add polygon, segment, robot, GIS, or graph semantics", report)
        self.assertIn("not by itself a performance claim", report)
        self.assertIn("tests.goal1997_generic_witness_pair_paging_adapter_test", preflight)


if __name__ == "__main__":
    unittest.main()
