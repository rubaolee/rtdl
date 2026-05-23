import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2514_partner_resident_compact_grouped_output_2026-05-22.md"
POD_SCRIPT = ROOT / "scripts/goal2514_partner_resident_compact_output_pod.py"
POD_ARTIFACT = ROOT / "docs/reports/goal2514_partner_resident_compact_output_pod_2026-05-22.json"
OPTIX_WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"


class Goal2514PartnerResidentCompactGroupedOutputTest(unittest.TestCase):
    def test_native_source_defines_device_compaction_kernels(self) -> None:
        source = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("device_column_grouped_i64_compact_count_kernel", source)
        self.assertIn("device_column_grouped_i64_compact_sum_kernel", source)
        self.assertIn("compact_count_fn", source)
        self.assertIn("compact_sum_fn", source)

    def test_native_source_downloads_compact_rows_not_capacity_arrays(self) -> None:
        source = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("download(count_rows.data(), d_rows.ptr, compact_row_count)", source)
        self.assertIn("download(sum_rows.data(), d_rows.ptr, compact_row_count)", source)
        self.assertNotIn("download(group_counts.data()", source)
        self.assertNotIn("download(group_sums.data()", source)

    def test_report_records_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("compact grouped rows", text)
        self.assertIn("not full capacity-sized count/sum arrays", text)
        self.assertIn("true zero-copy claim", text)
        self.assertIn("5 tests OK", text)

    def test_pod_runner_records_compact_output_evidence(self) -> None:
        text = POD_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("compact_output_source_check", text)
        self.assertIn("count_rows_downloaded", text)
        self.assertIn("sum_rows_downloaded", text)

    def test_pod_artifact_records_compact_output_evidence(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertIs(payload["compact_output_source_check"], True)
        self.assertEqual(payload["group_capacity"], 3)
        self.assertEqual(payload["count_rows_downloaded"], 3)
        self.assertEqual(payload["sum_rows_downloaded"], 3)
        self.assertIs(payload["all_match_cpu_reference"], True)


if __name__ == "__main__":
    unittest.main()
