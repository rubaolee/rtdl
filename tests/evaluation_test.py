import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.evaluation_report import generate_gap_analysis
from rtdsl.evaluation_report import generate_markdown_summary


class EmbreeEvaluationTest(unittest.TestCase):
    def test_evaluation_matrix_covers_all_baseline_workloads(self) -> None:
        workloads = {entry.workload for entry in rt.EMBREE_EVALUATION_MATRIX}
        self.assertEqual(workloads, set(rt.BASELINE_WORKLOAD_ORDER))

    def test_generate_embree_evaluation_artifacts(self) -> None:
        output_dir = Path("build/test_embree_evaluation")
        artifacts = rt.generate_embree_evaluation_artifacts(
            workloads=("lsi", "ray_tri_hitcount"),
            iterations=1,
            warmup=1,
            output_dir=output_dir,
        )
        self.assertTrue(artifacts["json"].exists())
        self.assertTrue(artifacts["markdown"].exists())
        self.assertTrue(artifacts["csv"].exists())
        self.assertTrue(artifacts["latency_svg"].exists())
        self.assertTrue(artifacts["speedup_svg"].exists())
        self.assertTrue(artifacts["scaling_svg"].exists())
        self.assertTrue(artifacts["pdf"].exists())
        self.assertTrue(artifacts["gap_analysis"].exists())

        payload = json.loads(artifacts["json"].read_text(encoding="utf-8"))
        self.assertEqual(payload["suite"], "rtdl_embree_evaluation")
        self.assertEqual({record["workload"] for record in payload["records"]}, {"lsi", "ray_tri_hitcount"})
        self.assertTrue(all(record["parity"] for record in payload["records"]))
        self.assertTrue(artifacts["pdf"].read_bytes().startswith(b"%PDF-1.4"))
        self.assertIn("RTDL Embree Evaluation Summary", artifacts["markdown"].read_text(encoding="utf-8"))

    def test_summary_and_gap_analysis_text(self) -> None:
        payload = {
            "generated_at": "2026-03-30T12:00:00",
            "iterations": 1,
            "warmup": 1,
            "host": {"platform": "test"},
            "records": [
                {
                    "case_id": "lsi_authored_minimal",
                    "workload": "lsi",
                    "dataset": "authored_lsi_minimal",
                    "category": "authored",
                    "parity": True,
                    "cpu": {"mean_sec": 0.1},
                    "embree": {"mean_sec": 0.05},
                    "speedup_vs_cpu": 2.0,
                    "scale_hint": 2,
                }
            ],
        }
        summary = generate_markdown_summary(payload)
        gap = generate_gap_analysis(payload, (Path("a.svg"), Path("b.svg"), Path("c.svg")))
        self.assertIn("RTDL Embree Evaluation Summary", summary)
        self.assertIn("Embree Gap Analysis", gap)
