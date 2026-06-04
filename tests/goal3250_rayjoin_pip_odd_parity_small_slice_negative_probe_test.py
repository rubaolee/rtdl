from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3250_rayjoin_pip_odd_parity_small_slice_negative_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3250_rayjoin_pip_odd_parity_small_slice_probe_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3250_rayjoin_pip_odd_parity_small_slice_probe_pod_2026-06-03.stdout"
SCRIPT = ROOT / "scripts" / "goal3250_rayjoin_pip_odd_parity_small_slice_probe.py"


class Goal3250RayJoinPipOddParitySmallSliceNegativeProbeTest(unittest.TestCase):
    def test_report_records_negative_conclusion_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin PIP Odd-Parity Small-Slice Negative Probe",
            "0.920307 ms",
            "2.948057 ms",
            "misses `1307`",
            "remains rejected",
            "stronger generic membership/count primitive",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_claim_bounded_and_negative(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3250)
        self.assertEqual(data["repo_state"]["commit"], "76bfa25ca2a03fc68791c7ba2cb6e89f5b67cb99")
        self.assertEqual(data["repo_state"]["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

        self.assertEqual(data["inputs"]["point_count"], 512)
        self.assertEqual(data["inputs"]["polygon_count"], 481)
        self.assertEqual(data["inputs"]["boundary_segment_count"], 25330)

        self.assertEqual(data["closed_shape_reference"]["count_values"], [1430, 1430, 1430, 1430, 1430])
        self.assertEqual(data["odd_parity_route"]["row_count_values"], [123, 123, 123, 123, 123])
        self.assertFalse(data["odd_parity_route"]["sets_match_all"])
        self.assertEqual(data["odd_parity_route"]["missing_counts"], [1307, 1307, 1307, 1307, 1307])
        self.assertEqual(data["odd_parity_route"]["extra_counts"], [0, 0, 0, 0, 0])
        self.assertGreater(data["ratios"]["odd_parity_over_closed_count_median"], 3.0)

    def test_stdout_has_progress_lines(self) -> None:
        text = STDOUT.read_text(encoding="utf-8")

        self.assertIn("[goal3250] loaded points=512 polygons=481 boundary_segments=25330", text)
        self.assertIn("[goal3250] closed count repeat 5/5", text)
        self.assertIn("[goal3250] odd-parity repeat 5/5", text)
        self.assertIn("match=False missing=1307 extra=0", text)

    def test_probe_script_remains_generic_and_reports_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_ray_segment_group_count_2d_optix", text)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_QUERY_HALF_EXTENT", text)
        self.assertIn("\"rayjoin_paper_reproduction_claim_authorized\": False", text)
        self.assertNotIn("rtdl_optix_run_pip", text)


if __name__ == "__main__":
    unittest.main()
