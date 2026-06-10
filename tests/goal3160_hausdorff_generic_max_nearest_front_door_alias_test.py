import math
import unittest
from pathlib import Path

import rtdsl as rt
from examples.current.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff
from rtdsl.reference import Point


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT_SOURCE = REPO_ROOT / "src" / "rtdsl" / "__init__.py"
APP_SOURCE = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_distance_app.py"
)
REPORT = REPO_ROOT / "docs" / "reports" / "goal3160_hausdorff_generic_max_nearest_front_door_alias_2026-06-03.md"


class Goal3160HausdorffGenericMaxNearestFrontDoorAliasTest(unittest.TestCase):
    def test_generic_alias_is_exported_while_compatibility_adapter_remains(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        init_text = INIT_SOURCE.read_text(encoding="utf-8")

        self.assertIn("def directed_max_of_nearest_distance_2d_partner_columns", adapter)
        self.assertIn("directed_hausdorff_2d_partner_columns(", adapter)
        self.assertIn("compatibility_adapter_aliases", adapter)
        self.assertIn("generic_directed_max_of_nearest_distance_2d", adapter)
        self.assertIn("from .partner_adapters import directed_max_of_nearest_distance_2d_partner_columns", init_text)
        self.assertIn('"directed_max_of_nearest_distance_2d_partner_columns"', init_text)
        self.assertTrue(hasattr(rt, "directed_max_of_nearest_distance_2d_partner_columns"))
        self.assertTrue(hasattr(rt, "directed_hausdorff_2d_partner_columns"))

    def test_hausdorff_partner_exact_route_uses_generic_alias(self) -> None:
        app = APP_SOURCE.read_text(encoding="utf-8")
        helper_start = app.index("def _run_partner_exact_directed")
        helper_end = app.index("def _run_partner_numpy_exact_directed", helper_start)
        helper = app[helper_start:helper_end]

        self.assertIn("rt.directed_max_of_nearest_distance_2d_partner_columns", helper)
        self.assertNotIn("rt.directed_hausdorff_2d_partner_columns", helper)
        self.assertIn('"partner_reference_contract": directed_ab["partner_reference_contract"]', app)

    def test_generic_alias_executes_when_numba_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable generic-alias validation")

        source = (
            Point(id=10, x=0.0, y=0.0),
            Point(id=11, x=2.0, y=0.0),
        )
        target = (
            Point(id=20, x=0.0, y=1.0),
            Point(id=21, x=3.0, y=0.0),
        )
        source_columns = rt.point_rows_to_partner_columns(source, partner="numba")
        target_columns = rt.point_rows_to_partner_columns(target, partner="numba")

        payload = rt.directed_max_of_nearest_distance_2d_partner_columns(
            source_columns,
            target_columns,
            partner="numba",
            materialize_nearest_distances=False,
            return_metadata=True,
        )
        metadata = payload["metadata"]
        self.assertEqual(metadata["adapter"], "directed_max_of_nearest_distance_2d_partner_columns")
        self.assertEqual(metadata["partner_reference_contract"], "generic_directed_max_of_nearest_distance_2d")
        self.assertEqual(metadata["compatibility_adapter_aliases"], ("directed_hausdorff_2d_partner_columns",))
        self.assertEqual(metadata["semantic_aliases"], ("directed_hausdorff_2d",))
        self.assertEqual(metadata["source_id"], 10)
        self.assertEqual(metadata["target_id"], 20)
        self.assertTrue(math.isclose(metadata["distance"], 1.0, rel_tol=0.0, abs_tol=1e-12))
        self.assertFalse(metadata["nearest_distance_column_materialized"])
        self.assertFalse(metadata["host_score_row_materialization_used"])
        self.assertTrue(metadata["score_rows_generated_on_partner_device"])
        self.assertFalse(metadata["v2_8_release_authorized"])

    def test_app_partner_exact_reports_generic_contract_when_numba_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable app validation")

        payload = hausdorff.run_app("partner_exact", copies=2, partner="numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["partner_reference_contract"], "generic_directed_max_of_nearest_distance_2d")
        self.assertEqual(
            payload["directed_a_to_b"]["partner_reference_contract"],
            "generic_directed_max_of_nearest_distance_2d",
        )
        self.assertFalse(payload["claim_boundary"]["v2_8_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_report_records_non_authorizing_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "directed_max_of_nearest_distance_2d_partner_columns",
            "directed_hausdorff_2d_partner_columns",
            "compatibility alias",
            "does not change native code",
            "`v2_8_release_authorized: False`",
            "`app_specific_engine_logic_allowed: False`",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
