from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
REPORT = ROOT / "docs" / "reports" / "goal2238_closed_shape_membership_primitive_2026-05-17.md"


class Goal2238ClosedShapeMembershipPrimitiveTest(unittest.TestCase):
    def test_future_version_todo_captures_deferred_design_ideas(self) -> None:
        text = TODO.read_text(encoding="utf-8")
        self.assertIn("Future-Version To-Do List", text)
        self.assertIn("Generic Closed-Shape Membership / Predicate Primitive", text)
        self.assertIn("Device-Resident Grouped Count / Parity Reduction", text)
        self.assertIn("not a v2.0 release authorization", text)

    def test_native_abi_uses_closed_shape_membership_vocabulary(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        self.assertIn("struct RtdlClosedShapeRef", prelude)
        self.assertIn("struct RtdlPointClosedShapeMembershipRow", prelude)
        self.assertIn("uint32_t point_id, shape_id, membership", prelude)
        self.assertIn("rtdl_optix_run_point_closed_shape_membership_2d", prelude)
        self.assertIn("rtdl_optix_run_point_closed_shape_membership_2d", api)
        self.assertIn("run_point_closed_shape_membership_2d_optix", api)

    def test_workload_wraps_existing_optimized_path_but_exports_generic_rows(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("run_point_closed_shape_membership_2d_optix")
        end = workloads.index("static void validate_polygon_ref_span_for_collection", start)
        body = workloads[start:end]
        self.assertIn("reinterpret_cast<const RtdlPolygonRef*>(shapes)", body)
        self.assertIn("run_pip_optix(", body)
        self.assertIn("RtdlPointClosedShapeMembershipRow", body)
        self.assertIn("raw_rows[i].point_id", body)
        self.assertIn("raw_rows[i].polygon_id", body)
        self.assertIn("raw_rows[i].contains", body)

    def test_python_wrapper_exposes_generic_dict_rows(self) -> None:
        runtime = PY_RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        self.assertIn("class _RtdlClosedShapeRef", runtime)
        self.assertIn("class _RtdlPointClosedShapeMembershipRow", runtime)
        self.assertIn("def closed_shape_membership_2d_optix", runtime)
        self.assertIn('"rtdl_optix_run_point_closed_shape_membership_2d"', runtime)
        self.assertIn('field_names=("point_id", "shape_id", "membership")', runtime)
        self.assertIn('"closed_shape_membership_2d_optix"', init)

    def test_new_public_symbol_name_is_not_app_named(self) -> None:
        symbol = "rtdl_optix_run_point_closed_shape_membership_2d"
        forbidden = re.compile(r"(rayjoin|county|spatial|pip|polygon|map)", re.IGNORECASE)
        self.assertIsNone(forbidden.search(symbol))

    def test_report_keeps_release_and_perf_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2238", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)
        self.assertIn("not a v2.0 release claim", text)
        self.assertIn("not a full RayJoin reproduction claim", text)


if __name__ == "__main__":
    unittest.main()
