import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3239_rayjoin_upstream_build_and_same_slice_smoke_2026-06-03.json"
CANONICAL_BOUNDARY_KEYS = {
    "public_speedup_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
    "release_authorized",
    "rt_core_speedup_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "true_zero_copy_claim_authorized",
}


class Goal3239RayJoinUpstreamBuildAndSameSliceSmokeTest(unittest.TestCase):
    def test_report_records_bounded_rayjoin_build_and_smoke(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RayJoin builds on the pod after two local CUDA 12.8 compatibility shims",
            "nvtx3/nvToolsExt.h",
            "Double2Hash",
            "269 intersections",
            "268 intersections",
            "count not printed",
            "cudaErrorInvalidDevice",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_preserves_claim_boundary_and_partial_status(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "partial_pass")
        self.assertEqual(data["rayjoin"]["commit"], "02bf6220d6d20b04af77ee20364eced75cc029c9")
        self.assertTrue(data["rayjoin"]["executables"]["query_exec"])
        self.assertTrue(data["rayjoin"]["executables"]["polyover_exec"])
        self.assertTrue(data["rayjoin"]["build_status"].startswith("pass_after_local"))
        self.assertEqual(set(data["claim_boundary"]), CANONICAL_BOUNDARY_KEYS)
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_same_slice_statuses_are_explicit(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {(row["case"], row["rayjoin_mode"]): row for row in data["same_slice_smokes"]}
        for row in rows.values():
            self.assertEqual(set(row["claim_boundary"]), CANONICAL_BOUNDARY_KEYS)
            self.assertTrue(all(value is False for value in row["claim_boundary"].values()))
        self.assertEqual(rows[("lsi_county256_soil256_count512", "rt")]["rayjoin_intersections"], 269)
        self.assertEqual(rows[("lsi_county256_soil256_count512", "rt")]["rtdl_goal3232_rows"], 269)
        self.assertEqual(rows[("lsi_county256_soil256_count512", "grid")]["rayjoin_intersections"], 268)
        self.assertEqual(rows[("pip_county512", "rt")]["status"], "pass_checker_map0")
        self.assertFalse(rows[("pip_county512", "rt")]["positive_row_count_available"])
        self.assertEqual(rows[("overlay_county128_soil128", "rt")]["status"], "blocked_runtime_failure")
        self.assertIn("cudaErrorInvalidDevice", rows[("overlay_county128_soil128", "rt")]["failure"])
        self.assertEqual(rows[("overlay_county128_soil128", "grid")]["status"], "pass_no_check")


if __name__ == "__main__":
    unittest.main()
