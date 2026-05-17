import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2295_prepared_closed_shape_phase_telemetry_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2295_closed_shape_phase_probe_pod_2026-05-17.json"


class Goal2295PreparedClosedShapePhaseTelemetryTest(unittest.TestCase):
    def test_native_and_python_telemetry_accessors_exist(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_closed_shape_membership_get_last_phase_timings", prelude)
        self.assertIn("g_optix_last_closed_shape_candidate_write_s", workloads)
        self.assertIn("reset_closed_shape_membership_phase_timings(1u)", workloads)
        self.assertIn("reset_closed_shape_membership_phase_timings(2u)", workloads)
        self.assertIn("def get_last_closed_shape_membership_phase_timings()", runtime)
        self.assertIn("def last_phase_timings(self) -> dict[str, float | int | str] | None:", runtime)

    def test_pod_artifact_records_expected_phase_split(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["row_count"], 8686)
        self.assertEqual(data["count"], 8686)
        self.assertEqual(data["row_phase"]["raw_candidate_count"], 8793)
        self.assertEqual(data["count_phase"]["raw_candidate_count"], 8793)
        self.assertEqual(data["row_phase"]["emitted_count"], 8686)
        self.assertEqual(data["count_phase"]["emitted_count"], 8686)
        self.assertGreater(data["row_phase"]["candidate_write_pass"], data["row_phase"]["exact_refine"])
        self.assertGreater(data["count_phase"]["candidate_write_pass"], data["count_phase"]["exact_refine"])
        self.assertLess(data["count_phase"]["point_upload"], 0.005)

    def test_report_is_diagnostic_not_claim_expansion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("instrumentation, not an optimization", text)
        self.assertIn("candidate traversal/write is the largest measured native phase", text)
        self.assertIn("does not authorize", text)
        self.assertIn("RTDL beats RayJoin", text)
        self.assertIn("v2.0 release readiness", text)


if __name__ == "__main__":
    unittest.main()
