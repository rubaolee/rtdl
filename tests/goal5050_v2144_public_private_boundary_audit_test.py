from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "history" / "internal_docs" / "goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal5050V2144PublicPrivateBoundaryAuditTest(unittest.TestCase):
    def test_public_v2144_surfaces_are_present_and_claim_bounded(self) -> None:
        for name in (
            "DeviceColumnBuffer",
            "PreparedGeometrySession",
            "device_order_by",
            "numba_partner_continuation",
        ):
            self.assertTrue(hasattr(rt, name), name)
            self.assertIn(name, rt.__all__)

        numba_contract = rt.describe_numba_partner_continuation_contract()
        order_contract = rt.describe_device_order_by_contract()
        buffer_contract = rt.describe_device_column_buffer_contract()
        session_contract = rt.describe_prepared_geometry_session_contract()

        self.assertFalse(numba_contract["public_speedup_claim_authorized"])
        self.assertFalse(numba_contract["true_zero_copy_claim_authorized"])
        self.assertFalse(numba_contract["app_specific_semantics_allowed"])
        self.assertFalse(numba_contract["replaces_rt_traversal"])
        self.assertFalse(order_contract["device_group_by_public_claim_authorized"])
        self.assertFalse(buffer_contract["true_zero_copy_claim_authorized"])
        self.assertFalse(session_contract["app_specific_native_engine_logic_allowed"])

    def test_legacy_grouped_exports_are_documented_but_not_new_public_contract(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        legacy_operations = (
            rt.NUMBA_SEGMENTED_COUNT_I64_OPERATION,
            rt.NUMBA_SEGMENTED_SUM_F64_OPERATION,
            rt.NUMBA_GROUPED_VECTOR_SUM_F64X2_OPERATION,
            rt.NUMBA_GROUPED_ARGMIN_F64_OPERATION,
            rt.NUMBA_GROUPED_ARGMAX_F64_OPERATION,
            rt.NUMBA_GROUPED_TOPK_F64_OPERATION,
        )
        public_ops = set(rt.NUMBA_PARTNER_CONTINUATION_PUBLIC_OPERATIONS)

        for operation in legacy_operations:
            self.assertNotIn(operation, public_ops)

        self.assertFalse(hasattr(rt, "device_group_by"))
        self.assertNotIn("device_group_by", rt.__all__)
        self.assertIn("legacy export-hygiene debt", report)
        self.assertIn("defer_removal_for_compatibility__document_as_legacy_low_level_exports", report)
        self.assertIn("device_group_by` remains absent", report)

    def test_rayjoin_named_lower_level_symbols_are_disclosed_as_debt(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        optix_runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        optix_core = OPTIX_CORE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_prepare_rayjoin_cdb_point_location_2d", optix_runtime)
        self.assertIn('_PLANAR_MAP_LSI_LEGACY_NATIVE_ALIAS = "rayjoin_lsi"', optix_runtime)
        self.assertIn("__raygen__rayjoin_cdb_point_location", optix_core)

        self.assertIn("RayJoin-named lower-level implementation symbols remain", report)
        self.assertIn("defer_native_symbol_rename__risk_too_high_for_v2_14_4", report)
        self.assertIn("Forbidden wording", report)
        self.assertIn("All core/internal symbols are RayJoin-free.", report)

    def test_rayjoin_named_python_exports_are_disclosed_as_legacy_public_exports(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for name in (
            "PreparedEmbreeRayjoinCdbPointLocation2D",
            "PreparedOptixRayjoinCdbPointLocation2D",
            "PreparedOptixRayjoinCdbPointLocationPoints2D",
            "RAYJOIN_PAPER_TARGETS",
            "RayJoinBoundedPlan",
            "RayJoinFeatureServiceLayer",
            "RayJoinPlan",
            "RayJoinPublicAsset",
            "chains_to_rayjoin_cdb_segments",
            "download_rayjoin_sample",
            "lower_to_rayjoin",
            "pack_rayjoin_cdb_segments",
            "prepare_rayjoin_cdb_point_location_2d_embree",
            "prepare_rayjoin_cdb_point_location_2d_optix",
            "rayjoin_bounded_plans",
            "rayjoin_feature_service_layers",
            "rayjoin_public_assets",
        ):
            self.assertIn(name, rt.__all__)
            self.assertIn(name, report)
        self.assertIn("legacy public exports", report)
        self.assertIn("compatibility debt", report)
        self.assertIn("paper-app support exports", report)
        self.assertIn("not new v2.14.4 public generic API", report)

    def test_report_keeps_non_authorization_boundary_visible(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "device_group_by_public_ready",
            "all_internal_symbols_rayjoin_free",
            "public_speedup_claim",
            "author_parity_claim",
            "true_zero_copy_claim",
            "RayJoin_core_primitive",
            "POD_runtime_success_for_skipped_smokes",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
