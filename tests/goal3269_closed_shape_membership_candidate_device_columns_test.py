from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
TYPED = ROOT / "src" / "rtdsl" / "v2_8_geometry_relation_typed_stream.py"
REPORT = ROOT / "docs" / "reports" / "goal3269_closed_shape_membership_candidate_device_columns_2026-06-03.md"


class Goal3269ClosedShapeMembershipCandidateDeviceColumnsTest(unittest.TestCase):
    def test_native_surface_exports_generic_point_shape_candidate_columns(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        symbol = "rtdl_optix_prepared_point_closed_shape_membership_candidate_device_columns_2d"
        release = "rtdl_optix_release_point_closed_shape_membership_candidate_device_columns_2d"
        for text in (prelude, api):
            self.assertIn("RtdlNativeDevicePairColumns", text)
            self.assertIn(symbol, text)
            self.assertIn(release, text)
            self.assertNotIn("rayjoin", text.lower())

    def test_candidate_pipeline_writes_device_columns_directly(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("g_pip_candidate_device_columns", core)
        self.assertIn("ensure_pip_candidate_device_columns_pipeline", workloads)
        self.assertIn("point_closed_shape_candidate_device_columns_kernel.cu", workloads)
        self.assertIn("params.point_ids_out[slot] = (unsigned long long)params.point_ids[pidx]", workloads)
        self.assertIn("params.shape_ids_out[slot] = (unsigned long long)params.polygons[prim].id", workloads)
        self.assertIn("NativeClosedShapeMembershipCandidateDeviceColumnsOwner", workloads)

        start = workloads.index("static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix")
        end = workloads.index("static void release_point_closed_shape_membership_candidate_device_columns_2d_optix", start)
        body = workloads[start:end]
        self.assertNotIn("RtdlPointClosedShapeMembershipRow", body)
        self.assertNotIn("download(chunk_rows", body)
        self.assertNotIn("exact_point_in_polygon", body)
        self.assertNotIn("rayjoin", body.lower())

    def test_python_runtime_exposes_raii_output_and_point_shape_metadata(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("OPTIX_CLOSED_SHAPE_MEMBERSHIP_CANDIDATE_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn("def candidate_device_columns(", runtime)
        self.assertIn("release_symbol_name=OPTIX_RELEASE_CLOSED_SHAPE_MEMBERSHIP_CANDIDATE_DEVICE_COLUMNS_SYMBOL", runtime)
        self.assertIn('field_names=("point_id", "shape_id")', runtime)
        self.assertIn("true_zero_copy_authorized", runtime)
        self.assertNotIn("rayjoin", runtime[runtime.index("class PreparedOptixPointClosedShapeMembership2D"):runtime.index("def prepare_point_closed_shape_membership_2d_optix")].lower())

    def test_typed_metadata_declares_point_shape_candidate_columns(self) -> None:
        typed = TYPED.read_text(encoding="utf-8")

        self.assertIn("point_closed_shape_membership_2d_candidate_device_columns", typed)
        self.assertIn("point_closed_shape_membership_2d_candidate", typed)
        self.assertIn('"point_id"', typed)
        self.assertIn('"shape_id"', typed)
        self.assertIn('field_names: tuple[str, str] = ("left_id", "right_id")', typed)
        self.assertIn('"true_zero_copy_claim_authorized": False', typed)

    def test_report_records_boundary_and_next_step(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "device-resident point/shape candidate ID columns",
            "not exact host-refined membership rows",
            "does not authorize a release claim",
            "does not authorize a true zero-copy claim",
            "next step is a generic device-side continuation",
            "RayJoin-specific native logic added: false",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
