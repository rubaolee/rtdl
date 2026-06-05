from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3505_overlay_area_payload_worker_sweep_2026-06-05.md"
WORKERS = (2, 4, 8, 12, 16)


def _artifact(worker_count: int) -> dict[str, object]:
    path = (
        ROOT
        / "docs"
        / "reports"
        / f"goal3505_overlay_area_payload_worker_sweep_w{worker_count}_pod_2026-06-05.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3505OverlayAreaPayloadWorkerSweepTest(unittest.TestCase):
    def test_worker_sweep_artifacts_are_consistent(self) -> None:
        rows = []
        for worker_count in WORKERS:
            data = _artifact(worker_count)
            timing = data["timing_sec"]
            self.assertEqual(data["schema"], "rtdl.goal3504.overlay_area_parallel_payload_prepare.v1")
            self.assertEqual(data["payload_workers"], worker_count)
            self.assertTrue(data["parallel_payload_prepare"])
            self.assertEqual(data["relation_row_count"], 4543)
            self.assertEqual(data["candidate_relation_row_count"], 2274)
            self.assertEqual(data["supported_relation_row_count"], 2149)
            self.assertEqual(data["component_pair_row_count"], 4524)
            self.assertEqual(data["tile_task_count"], 11617)
            self.assertEqual(data["planned_triangle_pair_count"], 4070240)
            self.assertTrue(data["positive_row_count_match"])
            self.assertLess(data["total_area_abs_error"], 1.0e-8)
            self.assertLess(data["max_relation_abs_error"], 2.0e-9)
            self.assertLess(timing["cupy_tile_task_executor_best_repeat"], 0.02)
            for field, value in data["claim_boundary"].items():
                with self.subTest(worker_count=worker_count, field=field):
                    self.assertFalse(value)
            rows.append((worker_count, float(timing["geometry_plus_payload_prepare"])))

        best_worker, best_sec = min(rows, key=lambda item: item[1])
        self.assertEqual(best_worker, 8)
        self.assertLess(best_sec, 1.5)
        self.assertGreater(dict(rows)[12], best_sec)
        self.assertGreater(dict(rows)[16], best_sec)

    def test_report_documents_sweep_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Best measured worker count on this pod: **8 workers**",
            "12 and 16 workers regress",
            "authorize a global default",
            "does not authorize release or public",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
