from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
FRONT_DOOR = ROOT / "src" / "rtdsl" / "v2_8_fixed_radius_graph_component_front_door.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "rt_dbscan"
    / "rtdl_rt_dbscan_benchmark_app.py"
)
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
NATIVE_OPTIX = ROOT / "src" / "native" / "optix"
REPORT = ROOT / "docs" / "reports" / "goal4156_predicate_direct_status_candidate_surface_2026-06-09.md"


class Goal4156PredicateDirectStatusCandidateSurfaceTest(unittest.TestCase):
    def test_candidate_surface_is_explicit_and_exported(self) -> None:
        front_door = FRONT_DOOR.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")

        for fragment in (
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d",
            "predicate_true_partition_root_count_plus_lowest_predicate_neighbor_candidate",
            "lowest_predicate_true_point_id_within_radius",
            "predicate_direct_status_promoted",
        ):
            self.assertIn(fragment, front_door)
            if fragment.startswith(("prepare_v2_8", "run_v2_8")):
                self.assertIn(fragment, init)

        self.assertIn("optix_rt_core_flags_cupy_predicate_direct_status_column_signature_3d", app)
        self.assertIn('"predicate_direct_status_candidate": True', app)
        self.assertIn('"predicate_direct_status_promoted": False', app)
        self.assertIn('"automatic_convergence_mode_selection_authorized": False', app)

    def test_no_native_app_specific_abi_added(self) -> None:
        native_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in NATIVE_OPTIX.rglob("*")
            if path.is_file()
        )
        for forbidden in ("dbscan", "cluster", "core", "border", "noise"):
            self.assertNotIn(f"rtdl_optix_{forbidden}", native_text.lower())

    def test_report_keeps_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "implementation-candidate-exposed",
            "not a default route",
            "No native ABI was added",
            "does not authorize route",
            "Timings are useful only after same-contract parity is proven",
        ):
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
