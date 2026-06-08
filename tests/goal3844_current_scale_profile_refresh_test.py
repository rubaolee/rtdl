from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3844_current_scale_profile_refresh_2026-06-08.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3844_current_scale_profiles_refresh_a5000"
    / "summary.json"
)
OUTPUT_DIR = ARTIFACT.parent / "outputs"


class Goal3844CurrentScaleProfileRefreshTest(unittest.TestCase):
    def test_a5000_packet_keeps_all_promoted_scale_profiles_green(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["version"],
            "rtdl.v2_10.current_benchmark_scale_profiles.goal3828.v1",
        )
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["file_backed_stdout_probe"])
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertEqual(payload["validation"]["errors"], [])

        rows = payload["rows"]
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        for row in rows:
            self.assertEqual(row["status"], "pass", row["row_id"])
            self.assertTrue(
                row["semantic_stdout_check"]["stdout_json_parseable"],
                row["row_id"],
            )
            self.assertEqual(
                row["semantic_stdout_check"]["claim_flag_violations"],
                [],
                row["row_id"],
            )
            self.assertGreater(row["stdout_bytes"], 0, row["row_id"])
            self.assertEqual(row["stderr_bytes"], 0, row["row_id"])
            self.assertLess(row["elapsed_sec"], row["timeout_sec"], row["row_id"])

    def test_top_level_claim_boundary_remains_non_authorizing(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(payload[key])
        boundary = payload["claim_boundary"]
        self.assertIn("does not authorize release action", boundary)
        self.assertIn("automatic partner selection", boundary)
        self.assertIn("app-specific native-engine logic", boundary)

    def test_numba_reference_rows_are_present_and_scoped(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_id = {row["row_id"]: row for row in payload["rows"]}

        rt_dbscan = by_id["rt_dbscan_optix_numba_scale_default_65536_no_validation"]
        rt_dbscan_stdout = json.loads(
            (ROOT / rt_dbscan["stdout_path"]).read_text(encoding="utf-8")
        )
        metadata = rt_dbscan_stdout["metadata"]
        self.assertEqual(metadata["partner"], "numba")
        self.assertTrue(metadata["optix_backend_used"])
        self.assertFalse(metadata["raw_cuda_kernel_required"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])

        barnes = by_id["barnes_hut_numba_scale_default_8192"]
        barnes_stdout = json.loads((ROOT / barnes["stdout_path"]).read_text(encoding="utf-8"))
        self.assertEqual(barnes_stdout["output_mode"], "force_summary")
        self.assertIn("numba", barnes["row_id"])

    def test_report_records_scope_and_result_table(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3844",
            "NVIDIA RTX A5000",
            "ad4bea28960f",
            "All ten promoted benchmark apps passed",
            "rt_dbscan_optix_numba_scale_default_65536_no_validation",
            "barnes_hut_numba_scale_default_8192",
            "not a new public speedup table",
            "does not authorize",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
