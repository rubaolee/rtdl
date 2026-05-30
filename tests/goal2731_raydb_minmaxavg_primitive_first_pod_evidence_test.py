import json
import unittest
from pathlib import Path

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2731_raydb_minmaxavg_primitive_first_pod_evidence_2026-05-30.md"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2731_pod_artifacts"
    / "goal2731_raydb_primitive_first_minmaxavg_gap_pod_69_30_85_171_2026-05-30.json"
)


class Goal2731RaydbMinMaxAvgPrimitiveFirstPodEvidenceTest(unittest.TestCase):
    def test_artifact_closes_min_max_avg_measurement_gap(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["all_correct"])
        self.assertTrue(payload["no_public_speedup_claim"])
        self.assertEqual(
            payload["backends"],
            [
                raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND,
                raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND,
            ],
        )
        self.assertEqual(payload["row_counts"], [250000, 1000000])
        self.assertEqual(payload["modes"], ["min", "max", "avg_as_sum_count"])
        self.assertIn("NVIDIA RTX A5000", payload["nvidia_smi"])

    def test_fused_primitive_beats_hit_stream_for_every_remaining_scalar_mode(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        by_key = {
            (case["row_count"], case["mode"], case["backend"]): case
            for case in payload["cases"]
        }

        for row_count in (250000, 1000000):
            for mode in ("min", "max", "avg_as_sum_count"):
                grouped = by_key[(row_count, mode, raydb.PAPER_RT_OPTIX_PREPARED_GROUPED_REDUCTION_BACKEND)]
                hit_stream = by_key[
                    (row_count, mode, raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_PREPARED_BACKEND)
                ]
                slowdown = hit_stream["median_wall_sec"] / grouped["median_wall_sec"]
                with self.subTest(row_count=row_count, mode=mode):
                    self.assertTrue(grouped["matches_cpu_reference"])
                    self.assertTrue(hit_stream["matches_cpu_reference"])
                    self.assertTrue(grouped["prepared_steady_state"])
                    self.assertTrue(hit_stream["prepared_steady_state"])
                    self.assertTrue(grouped["prepared_primitive_payload_reused"])
                    self.assertTrue(grouped["prepared_ray_batch_reused"])
                    self.assertFalse(grouped["native_device_column_path_used"])
                    self.assertTrue(hit_stream["native_device_column_path_used"])
                    self.assertGreater(slowdown, 100.0)

    def test_report_records_remaining_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RayDB Min/Max/Avg Primitive-First Pod Evidence", text)
        self.assertIn("Claude's Goal2729 review", text)
        self.assertIn("185.4x slower", text)
        self.assertIn("123.8x slower", text)
        self.assertIn("true-zero-copy remains unauthorized", text)
        self.assertIn("one RTX A5000", text)


if __name__ == "__main__":
    unittest.main()
