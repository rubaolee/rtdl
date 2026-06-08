from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3870_current_scale_after_barnes_reuse_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal3870_current_scale_after_barnes_reuse_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3870CurrentScaleAfterBarnesReuseTest(unittest.TestCase):
    def test_a5000_packet_keeps_all_current_scale_rows_green(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        payload = _load(SUMMARY)

        self.assertEqual(payload["version"], "rtdl.v2_10.current_benchmark_scale_profiles.goal3828.v1")
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])

        rows = {row["app"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut",
            "librts_spatial_index",
            "rtnn",
            "triangle_counting",
        })
        for row in rows.values():
            self.assertEqual(row["status"], "pass")
            self.assertTrue(row["semantic_stdout_check"]["stdout_json_parseable"])
            self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

    def test_barnes_hut_row_records_resident_output_reuse_without_whole_app_claim(self) -> None:
        payload = _load(SUMMARY)
        barnes_row = next(row for row in payload["rows"] if row["app"] == "barnes_hut")
        barnes_payload = _load(ROOT / barnes_row["stdout_path"])
        metadata = barnes_payload["partner_metadata"]

        self.assertEqual(barnes_row["row_id"], "barnes_hut_numba_scale_default_8192")
        self.assertLess(barnes_row["elapsed_sec"], 3.0)
        self.assertTrue(metadata["output_columns_reused"])
        self.assertTrue(metadata["prepared_force_output_columns_reused"])
        self.assertFalse(metadata["raw_cuda_kernel_required"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])
        self.assertLess(metadata["prepared_force_repeat_protocol"]["median_force_kernel_sec"], 0.01)

    def test_rayjoin_nested_payload_is_source_clean_and_representative(self) -> None:
        payload = _load(SUMMARY)
        rayjoin_row = next(row for row in payload["rows"] if row["app"] == "spatial_rayjoin")
        rayjoin_payload = _load(ROOT / rayjoin_row["stdout_path"])

        self.assertEqual(rayjoin_payload["git_status_short"], "")
        self.assertTrue(rayjoin_payload["representative_scale_profile"])
        self.assertTrue(rayjoin_payload["all_counts_match"])
        self.assertFalse(rayjoin_payload["cupy_required_for_reference_route"])
        self.assertFalse(rayjoin_payload["raw_cuda_kernel_required_for_reference_route"])
        self.assertFalse(rayjoin_payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertEqual(
            rayjoin_payload["recommended_route_summary"]["pip_one_shot"],
            "numba_cuda_jit_scalar_count_no_rawkernel",
        )
        self.assertEqual(
            rayjoin_payload["recommended_route_summary"]["pip_repeated_requests"],
            "rtdl_optix_prepared_batch_executor",
        )

    def test_report_explains_goal3870_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3870",
            "all_pass: true",
            "json_pass_count: 10",
            "resident force-output reuse",
            "not a whole-app cold-process speedup claim",
            "not a RayJoin paper reproduction",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
