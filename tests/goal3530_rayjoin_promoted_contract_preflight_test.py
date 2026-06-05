from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3530_rayjoin_promoted_contract_preflight_2026-06-05.md"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
RELATION_CONTINUATIONS = ROOT / "src" / "rtdsl" / "geometry_relation_continuations.py"
OVERLAY_PAYLOAD = ROOT / "src" / "rtdsl" / "v2_8_overlay_area_prepared_payload.py"
OVERLAY_CONTRACT = ROOT / "src" / "rtdsl" / "v2_8_overlay_area_continuation_contract.py"


class Goal3530RayJoinPromotedContractPreflightTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = REPORT.read_text(encoding="utf-8")
        self.lowered = self.report.lower()
        self.normalized = " ".join(self.report.split())

    def test_report_covers_all_goal3527_rayjoin_contracts(self) -> None:
        required = (
            "Count/parity",
            "Relation columns",
            "Shape-pair payload",
            "Overlay-area continuation",
        )
        for phrase in required:
            self.assertIn(phrase, self.report)

    def test_statuses_distinguish_app_cli_methods_and_substrate(self) -> None:
        self.assertIn("runnable_app_cli", self.report)
        self.assertIn("runnable_app_method", self.report)
        self.assertIn("runnable_script_or_rtdsl_surface", self.report)
        self.assertIn("Needs a promoted runner", self.report)
        self.assertIn("do not fold into count/parity", self.lowered)

    def test_app_source_has_count_and_relation_column_surfaces(self) -> None:
        app = APP.read_text(encoding="utf-8")
        required = (
            "run_rayjoin_prepared_optix_workload",
            '"prepared_optix"',
            '"prepared_optix_compact_grouped_count"',
            '"prepared_optix_left_id_dense_count"',
            '"prepared_optix_shape_pair_active_count"',
            "active_relation_device_columns",
            "run_packed_left_active_relation_device_columns",
            "run_packed_left_active_relation_grouped_count_by_left",
        )
        for phrase in required:
            self.assertIn(phrase, app)

    def test_relation_and_overlay_substrate_surfaces_exist(self) -> None:
        relation = RELATION_CONTINUATIONS.read_text(encoding="utf-8")
        payload = OVERLAY_PAYLOAD.read_text(encoding="utf-8")
        contract = OVERLAY_CONTRACT.read_text(encoding="utf-8")
        for phrase in (
            "shape_pair_relation_active_shape_ordinals_cupy",
            "shape_pair_relation_witness_cupy",
            "shape_pair_relation_complexity_cupy",
            "shape_pair_relation_convex_overlay_area_cupy",
        ):
            self.assertIn(phrase, relation)
        for phrase in (
            "prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals",
            "evaluate_prepared_overlay_area_tile_task_cupy_inputs",
            "evaluate_prepared_overlay_area_tile_tasks_cupy",
        ):
            self.assertIn(phrase, payload)
        for phrase in (
            "v2_8_overlay_area_continuation_plan",
            "validate_v2_8_overlay_area_continuation_plan",
        ):
            self.assertIn(phrase, contract)

    def test_report_blocks_fake_performance_and_release_claims(self) -> None:
        self.assertIn("This is not a performance result", self.report)
        self.assertIn("does not authorize any public claim", self.report)
        self.assertIn("must not claim full RayJoin reproduction", self.report)
        self.assertIn("Do not add RayJoin-specific native engine shortcuts", self.normalized)
        self.assertIn("no hidden PyTorch path is allowed", self.report)

    def test_next_authoring_requirements_are_explicit(self) -> None:
        self.assertIn("Add a compact promoted RayJoin runner", self.report)
        self.assertIn("one row per contract", self.normalized)
        self.assertIn("sub-millisecond rows", self.report)
        self.assertIn("scale or repeat metadata", self.report)
        self.assertIn("authorized only after a runner or packet normalizes", self.normalized)


if __name__ == "__main__":
    unittest.main()
