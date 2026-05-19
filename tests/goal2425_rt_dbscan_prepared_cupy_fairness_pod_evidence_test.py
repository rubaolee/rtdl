from __future__ import annotations

import json
import pathlib
import statistics
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    plan_rt_dbscan_execution,
)


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence"
REPORT = ROOT / "docs" / "reports" / "goal2425_rt_dbscan_prepared_cupy_fairness_pod_evidence_2026-05-19.md"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"

FRESH_CUPY = "partner_cupy_grid_components_3d"
PREPARED_CUPY = "partner_cupy_prepared_grid_components_3d"
PREPARED_RT = "optix_rt_core_flags_cupy_prepared_grid_components_3d"


def _load(dataset: str, point_count: int) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / f"{dataset}_{point_count}_repeat3.json").read_text(encoding="utf-8"))


def _tail_median(payload: dict[str, object], mode: str) -> float:
    values = [float(row["app_elapsed_sec"]) for row in payload["rows"] if row["mode"] == mode]
    if len(values) >= 2:
        values = values[1:]
    return statistics.median(values)


class Goal2425RtDbscanPreparedCupyFairnessPodEvidenceTest(unittest.TestCase):
    def test_all_pod_artifacts_preserve_signature_parity(self) -> None:
        artifacts = sorted(ARTIFACT_DIR.glob("*_repeat3.json"))
        self.assertGreaterEqual(len(artifacts), 14)
        for artifact in artifacts:
            with self.subTest(artifact=artifact.name):
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                self.assertEqual(payload["modes"], [FRESH_CUPY, PREPARED_CUPY, PREPARED_RT])
                self.assertTrue(payload["signatures_match"])

    def test_fairness_matrix_selects_shape_and_scale_winners(self) -> None:
        for point_count in (65536, 131072, 262144, 524288):
            with self.subTest(dataset="clustered3d", point_count=point_count):
                payload = _load("clustered3d", point_count)
                self.assertLess(_tail_median(payload, PREPARED_RT), _tail_median(payload, PREPARED_CUPY))

        for point_count in (32768, 65536, 131072, 262144):
            with self.subTest(dataset="road3d", point_count=point_count):
                payload = _load("road3d", point_count)
                self.assertLess(_tail_median(payload, PREPARED_CUPY), _tail_median(payload, PREPARED_RT))

        payload = _load("road3d", 524288)
        self.assertLess(_tail_median(payload, PREPARED_RT), _tail_median(payload, PREPARED_CUPY))

        for point_count in (32768, 65536, 131072, 262144):
            with self.subTest(dataset="ngsim_dense", point_count=point_count):
                payload = _load("ngsim_dense", point_count)
                self.assertLess(_tail_median(payload, PREPARED_CUPY), _tail_median(payload, PREPARED_RT))

    def test_explicit_plan_uses_goal2425_thresholds(self) -> None:
        self.assertEqual(plan_rt_dbscan_execution("tiny", 9)["selected_mode"], "cpu_reference")
        self.assertEqual(plan_rt_dbscan_execution("clustered3d", 32768)["selected_mode"], PREPARED_CUPY)
        self.assertEqual(plan_rt_dbscan_execution("clustered3d", 65536)["selected_mode"], PREPARED_RT)
        self.assertEqual(plan_rt_dbscan_execution("road3d", 262144)["selected_mode"], PREPARED_CUPY)
        self.assertEqual(plan_rt_dbscan_execution("road3d", 524288)["selected_mode"], PREPARED_RT)
        self.assertEqual(plan_rt_dbscan_execution("ngsim_dense", 262144)["selected_mode"], PREPARED_CUPY)

    def test_docs_record_correction_without_broad_claim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("corrects earlier Goal2418/Goal2420 wording", report)
        self.assertIn("not uniformly best", report)
        self.assertIn("must not claim broad DBSCAN acceleration", report)
        self.assertIn("explicit_benchmark_plan_from_goal2425_prepared_fairness_evidence", app)
        self.assertIn("Goal2425 prepared-baseline fairness pass", readme)


if __name__ == "__main__":
    unittest.main()
