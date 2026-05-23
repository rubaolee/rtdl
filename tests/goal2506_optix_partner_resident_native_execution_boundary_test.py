from pathlib import Path
import unittest

import rtdsl as rt

from tests.goal2505_partner_resident_columnar_descriptor_contract_test import _record_set


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2506_optix_partner_resident_columnar_native_execution_boundary_2026-05-22.md"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
OPTIX_PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"


class Goal2506OptixPartnerResidentNativeExecutionBoundaryTest(unittest.TestCase):
    def test_native_execution_requirements_are_exported_and_fail_closed(self) -> None:
        self.assertEqual(
            rt.PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_TARGET,
            "optix_partner_resident_columnar_payload_native_execution",
        )
        self.assertEqual(
            rt.PARTNER_RESIDENT_COLUMNAR_NATIVE_EXECUTION_STATUS,
            "blocked_pending_optix_device_column_abi",
        )
        self.assertEqual(
            rt.PARTNER_RESIDENT_COLUMNAR_REQUIRED_OPTIX_SYMBOL,
            "rtdl_optix_columnar_payload_create_from_device_columns",
        )
        requirements = rt.partner_resident_columnar_native_execution_requirements()
        self.assertEqual(requirements["backend"], "optix")
        self.assertEqual(requirements["status"], "blocked_pending_optix_device_column_abi")
        self.assertIn(
            "rtdl_optix_columnar_payload_create_from_device_columns",
            requirements["required_native_symbols"],
        )
        self.assertIn("device-side grouped reduction with host result materialization only at the boundary", requirements["first_executable_slice"])
        self.assertIn("true zero-copy public claim", requirements["excluded_scope"])

    def test_descriptor_native_plan_does_not_authorize_execution(self) -> None:
        descriptor = rt.prepare_partner_resident_columnar_record_set(_record_set(), backend="optix")
        plan = rt.plan_partner_resident_columnar_native_execution(descriptor)
        self.assertEqual(plan["target"], "optix_partner_resident_columnar_payload_native_execution")
        self.assertEqual(plan["backend"], "optix")
        self.assertFalse(plan["native_execution_allowed"])
        self.assertEqual(plan["descriptor_field_names"], ("row_id", "region_id", "revenue"))
        self.assertIn("host RtdlDbScalar row_values", " ".join(plan["blocked_reasons"]))

    def test_current_optix_db_path_is_host_row_value_centered(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        self.assertIn("std::vector<RtdlDbScalar> row_values", workloads)
        self.assertIn("db_copy_dataset_columnar_payload", workloads)
        self.assertIn("run_db_grouped_count_optix", workloads)
        self.assertIn("run_db_grouped_sum_optix", workloads)
        self.assertIn("struct RtdlPayloadField", prelude)
        self.assertIn("const int64_t* int_values", prelude)

    def test_report_records_boundary_and_native_abi_requirements(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2506", text)
        self.assertIn("blocked_pending_optix_device_column_abi", text)
        self.assertIn("rtdl_optix_columnar_payload_create_from_device_columns", text)
        self.assertIn("do not fall back to hidden device-to-host table staging", text)
        self.assertIn("device-side exact predicate evaluation", text)
        self.assertIn("device-side grouped reduction", text)


if __name__ == "__main__":
    unittest.main()
