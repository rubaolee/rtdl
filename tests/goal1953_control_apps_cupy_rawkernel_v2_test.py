from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal1953_control_apps_cupy_rawkernel_v2_decision_2026-05-13.md"


class Goal1953ControlAppsCuPyRawKernelV2Test(unittest.TestCase):
    def test_example_defines_four_control_app_rawkernel_sources(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        for app in (
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertIn(app, text)
        self.assertIn("cp.RawKernel", text)
        self.assertIn("DB_RAWKERNEL_SOURCE", text)
        self.assertIn("GRAPH_RAWKERNEL_SOURCE", text)
        self.assertIn("POLYGON_PAIR_RAWKERNEL_SOURCE", text)
        self.assertIn("fairness_note", text)
        self.assertIn("not absolutely fair", text)

    def test_graph_rawkernel_uses_closed_form_summary_without_global_atomic_contention(self) -> None:
        import examples.rtdl_control_apps_cupy_rawkernel as rawkernel_apps

        self.assertNotIn("atomicAdd", rawkernel_apps.GRAPH_RAWKERNEL_SOURCE)
        self.assertIn("out[0] = 2 * copies", rawkernel_apps.GRAPH_RAWKERNEL_SOURCE)
        self.assertIn("out[6] = 3 * copies", rawkernel_apps.GRAPH_RAWKERNEL_SOURCE)

    def test_cpu_fallback_all_apps_match_v1_8_oracles(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--app",
                "all",
                "--copies",
                "2",
                "--partner",
                "cpu_fallback",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["goal"], "Goal1953")
        self.assertFalse(payload["claim_boundary"]["counts_as_v2_app_version"])
        self.assertTrue(payload["claim_boundary"]["cpu_fallback_is_correctness_only"])
        self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
        self.assertEqual(len(payload["results"]), 4)
        for result in payload["results"]:
            self.assertTrue(result["matches_v1_8_python_rtdl_oracle"], result["app"])
            self.assertIn("Python+CuPy RawKernel+RTDL", result["fairness_note"])

    def test_report_documents_user_decision_and_pod_requirement(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("User Decision", text)
        self.assertIn("not an absolutely", text)
        self.assertIn("fair comparison", text)
        self.assertIn("--partner cupy", text)
        self.assertIn("--candidate-backend optix", text)
        self.assertIn("pod timing", text)
        self.assertIn("any claim that RTDL accelerates arbitrary RawKernel code", text)


if __name__ == "__main__":
    unittest.main()
