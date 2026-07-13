from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper" / "scripts"))

import run_authorofficial_warm_loop_matrix as warm_loop


class Goal5104AuthorWarmLoopRunnerTest(unittest.TestCase):
    def test_json_lines_reads_all_payloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "author.jsonl"
            path.write_text(
                "noise\n"
                + json.dumps({"repeat_index": 0, "core_count": 1})
                + "\n"
                + json.dumps({"repeat_index": 1, "core_count": 1})
                + "\n",
                encoding="utf-8",
            )
            rows = warm_loop._json_lines(path)
        self.assertEqual([row["repeat_index"] for row in rows], [0, 1])

    def test_author_repeat_metrics_use_inner_loop_without_build(self):
        payloads = [
            {
                "core_points_time_sec": 0.01,
                "cluster_formation_time_sec": 0.02,
                "build_time_sec": 0.5,
                "total_time_sec": 0.53,
            },
            {
                "core_points_time_sec": 0.011,
                "cluster_formation_time_sec": 0.021,
                "build_time_sec": 0.5,
                "total_time_sec": 0.532,
            },
            {
                "core_points_time_sec": 0.012,
                "cluster_formation_time_sec": 0.022,
                "build_time_sec": 0.5,
                "total_time_sec": 0.534,
            },
        ]
        metrics = warm_loop._author_repeat_metrics(payloads)
        self.assertEqual(metrics["author_inner_loop_sec"], [0.03, 0.032, 0.034])
        self.assertEqual(metrics["author_inner_loop_steady_median_sec"], 0.033)
        self.assertEqual(metrics["author_reported_total_steady_median_sec"], 0.533)


if __name__ == "__main__":
    unittest.main()
