from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3187_segment_pair_candidate_chunked_append_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3187_pod_segment_pair_candidate_chunked_append_2026-06-03.json"


class Goal3187SegmentPairCandidateChunkedAppendTest(unittest.TestCase):
    def test_device_column_launcher_uses_chunked_append(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        start = workloads.index("static void run_prepared_segment_pair_candidate_device_columns_optix")
        end = workloads.index("static void release_segment_pair_candidate_device_columns_optix", start)
        body = workloads[start:end]

        self.assertIn("max_left_per_launch64", body)
        self.assertIn("for (size_t left_offset = 0; left_offset < left_count; left_offset += max_left_per_launch)", body)
        self.assertIn("chunk_left_count", body)
        self.assertIn("d_left.ptr + static_cast<CUdeviceptr>(sizeof(GpuSegment) * left_offset)", body)
        self.assertIn("upload(d_row_count.ptr, &zero64, 1)", body)
        self.assertIn("upload(d_candidate_events.ptr, &zero64, 1)", body)
        self.assertIn("lp.row_count = reinterpret_cast<unsigned long long*>(d_row_count.ptr)", body)
        self.assertIn("lp.candidate_event_count = reinterpret_cast<unsigned long long*>(d_candidate_events.ptr)", body)
        self.assertNotIn("currently require a single uint32 launch", body)

    def test_capacity_remains_fail_closed(self) -> None:
        body = WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("max_rows exceeds uint32 output capacity", body)
        self.assertIn("if (overflow != 0u || attempted_rows > static_cast<unsigned long long>(max_rows))", body)
        self.assertIn("columns_out->overflow = 1u", body)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "chunked append",
            "same native-owned device columns",
            "capacity remains uint32-bounded and fail-closed",
            "does not prove a >4B-pair live pod case",
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_refactor_evidence_boundary(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["commit"], "2822f71a")
        self.assertEqual(artifact["focused_tests"]["status"], "ok")
        self.assertEqual(artifact["focused_tests"]["tests_run"], 20)
        self.assertTrue(artifact["evidence_boundary"]["chunked_loop_compiled"])
        self.assertTrue(artifact["evidence_boundary"]["same_small_live_smoke_still_passes_after_chunked_refactor"])
        self.assertFalse(artifact["evidence_boundary"]["greater_than_uint32_pair_space_live_case_proven"])

        smoke = artifact["live_smoke"]
        self.assertEqual(smoke["candidate_row_count"], 64)
        self.assertFalse(smoke["overflow"])
        self.assertTrue(smoke["device_resident"])

        for value in artifact["claim_boundary"].values():
            self.assertIs(value, False)


if __name__ == "__main__":
    unittest.main()
