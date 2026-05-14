from __future__ import annotations

import pathlib
import json
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
PERF = ROOT / "scripts" / "goal1955_rawkernel_control_app_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal1969_cupy_extent_polygon_candidate_backend_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1969_pod_cupy_extent_polygon_control_perf.json"


class Goal1969CuPyExtentPolygonCandidateBackendTest(unittest.TestCase):
    def test_example_exposes_cupy_extent_candidate_backend(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")
        perf = PERF.read_text(encoding="utf-8")

        self.assertIn("def _positive_candidate_pairs_cupy_extent", text)
        self.assertIn('candidate_backend == "cupy_extent"', text)
        self.assertIn("cp.nonzero", text)
        self.assertIn("width > 0", text)
        self.assertIn("height > 0", text)
        self.assertIn('"cupy_extent"', text)
        self.assertIn('"cupy_extent"', perf)

    def test_cpu_fallback_still_matches_oracle_after_backend_extension(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--app",
                "polygon_set_jaccard",
                "--copies",
                "2",
                "--partner",
                "cpu_fallback",
                "--candidate-backend",
                "cpu_all_pairs",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertTrue(payload["matches_v1_8_python_rtdl_oracle"])

    def test_report_states_boundary_and_next_pod_test(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("--candidate-backend cupy_extent", text)
        self.assertIn("does not add app semantics to the native engine", text)
        self.assertIn("does not replace", text)
        self.assertIn("OptiX RT-core candidate path", text)
        self.assertIn("Correct", text)
        self.assertIn("0.280x", text)
        self.assertIn("0.296x", text)

    def test_pod_artifact_records_polygon_speedups_and_correctness(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in payload["results"]}

        self.assertEqual(payload["candidate_backend"], "cupy_extent")
        self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
        self.assertLess(rows["polygon_pair_overlap_area_rows"]["v2_vs_v1_8_ratio"], 1.0)
        self.assertLess(rows["polygon_set_jaccard"]["v2_vs_v1_8_ratio"], 1.0)
        for row in rows.values():
            self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])


if __name__ == "__main__":
    unittest.main()
