import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_database_analytics_app as db_app


ROOT = Path(__file__).resolve().parents[1]


class Goal815DbRtCoreClaimGateTest(unittest.TestCase):
    def test_db_metadata_is_goal941_ready_for_bounded_compact_summary(self) -> None:
        self.assertEqual(
            rt.optix_app_performance_support("database_analytics").performance_class,
            "python_interface_dominated",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("database_analytics").status,
            "ready_for_rtx_claim_review",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("database_analytics").current_status,
            "rt_core_ready",
        )

    def test_require_rt_core_rejects_non_optix_backend(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            db_app.run_app("embree", output_mode="compact_summary", require_rt_core=True)

    def test_require_rt_core_rejects_row_materializing_modes_before_optix_dispatch(self) -> None:
        for output_mode in ("full", "summary"):
            with self.subTest(output_mode=output_mode):
                with self.assertRaisesRegex(RuntimeError, "requires --output-mode compact_summary"):
                    db_app.run_app("optix", output_mode=output_mode, require_rt_core=True)

    def test_cpu_compact_summary_records_no_rt_core_acceleration(self) -> None:
        payload = db_app.run_app(
            "cpu_python_reference",
            scenario="sales_risk",
            output_mode="compact_summary",
        )
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("partial prepared compact-summary DB traversal", payload["rt_core_claim_scope"])

    def test_prepared_session_rechecks_required_output_mode(self) -> None:
        session = object.__new__(db_app.PreparedDatabaseAnalyticsSession)
        session._closed = False
        session.requested_backend = "optix"
        session.require_rt_core = True
        with self.assertRaisesRegex(RuntimeError, "requires --output-mode compact_summary"):
            session.run(output_mode="summary")

    def test_cli_require_rt_core_rejects_summary_before_optix_library_needed(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_database_analytics_app.py",
                "--backend",
                "optix",
                "--output-mode",
                "summary",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --output-mode compact_summary", result.stderr)


if __name__ == "__main__":
    unittest.main()
