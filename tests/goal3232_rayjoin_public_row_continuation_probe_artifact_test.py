from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3232_rayjoin_public_row_continuation_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3232_rayjoin_public_row_continuation_probe_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3232_rayjoin_public_row_continuation_probe_2026-06-03.stdout"

CANONICAL_KEYS = {
    "public_speedup_claim_authorized",
    "rt_core_speedup_claim_authorized",
    "true_zero_copy_claim_authorized",
    "rayjoin_paper_reproduction_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "release_authorized",
}


class Goal3232RayJoinPublicRowContinuationProbeArtifactTest(unittest.TestCase):
    def _assert_boundary(self, boundary: dict[str, object]) -> None:
        self.assertEqual(set(boundary), CANONICAL_KEYS)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_pod_artifact_records_public_row_continuation(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3232)
        self.assertEqual(data["schema"], "rtdl.goal3232.rayjoin_public_row_continuation_probe.v1")
        self.assertEqual(data["commit"], "275e9f78de6e06cf0905fd90df19c8344f32a970")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["hardware"]["nvidia_smi"], "NVIDIA A40, 570.211.01")
        self.assertIn("CUDA Version", data["hardware"]["cuda_driver_query"])
        self.assertIn("release 12.8", data["hardware"]["nvcc_version"])
        self.assertEqual(data["hardware"]["rtdl_optix_library"], "/root/rtdl_goal3151/build/librtdl_optix.so")

        rows = {row["case"]: row for row in data["rows"]}
        self.assertEqual(
            set(rows),
            {
                "pip_county512",
                "lsi_county256_soil256_count512",
                "overlay_county128_soil128",
                "overlay_county256_soil256",
            },
        )

        expected = {
            "pip_county512": ("pip", 1430, None),
            "lsi_county256_soil256_count512": ("lsi", 269, None),
            "overlay_county128_soil128": ("overlay_seed", 14036, 1),
            "overlay_county256_soil256": ("overlay_seed", 56876, 9),
        }
        for case, (workload, row_count, active_count) in expected.items():
            with self.subTest(case=case):
                row = rows[case]
                measurement = row["measurements"]["prepared_optix_rows"][0]
                self.assertEqual(row["workload"], workload)
                self.assertEqual(row["cpu_row_count"], row_count)
                self.assertEqual(measurement["row_count"], row_count)
                self.assertEqual(measurement["symmetric_difference_count"], 0)
                self.assertTrue(measurement["row_set_matches_cpu"])
                self.assertIn("unattributed_prepared_total_minus_named_phases_sec", measurement)
                self.assertTrue(row["all_repeats_match_cpu_rows"])
                self.assertEqual(row["cpu_active_overlay_rows"], active_count)
                if workload == "lsi":
                    self.assertEqual(measurement["max_lsi_coordinate_delta"], 0)
                self.assertNotIn("positive_assignments", row["cpu_summary"])
                self.assertNotIn("active_seed_pairs", row["cpu_summary"])

    def test_artifact_preserves_canonical_false_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self._assert_boundary(data["claim_boundary"])
        for row in data["rows"]:
            self._assert_boundary(row["claim_boundary"])
            for measurement in row["measurements"]["prepared_optix_rows"]:
                self._assert_boundary(measurement["claim_boundary"])

    def test_report_and_stdout_are_consistent_and_bounded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        stdout = STDOUT.read_text(encoding="utf-8")

        for phrase in (
            "symmetric difference `0`",
            "max_lsi_coordinate_delta",
            "56,876 row-continuation records",
            "not a public speedup claim",
            "membership",
            "unattributed_prepared_total_minus_named_phases_sec",
            "does not authorize release",
            "true zero-copy claims",
            "RayJoin paper-reproduction claims",
        ):
            self.assertIn(phrase, report)
        for phrase in (
            "repeat pip_county512/prepared_rows 1/1",
            "repeat lsi_county256_soil256_count512/prepared_rows 1/1",
            "repeat overlay_county128_soil128/prepared_rows 1/1",
            "repeat overlay_county256_soil256/prepared_rows 1/1",
            "symdiff=0",
        ):
            self.assertIn(phrase, stdout)


if __name__ == "__main__":
    unittest.main()
