from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import goal914_rtx_targeted_graph_jaccard_rerun as goal914


class Goal914RtxTargetedGraphJaccardRerunTest(unittest.TestCase):
    def test_dry_run_plans_graph_and_jaccard_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "plan.json"
            payload = goal914.run_driver(
                mode="dry-run",
                copies=20000,
                graph_chunk_copies=0,
                jaccard_chunk_copies=(100, 50, 20),
                output_json=output_json,
            )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual([result["label"] for result in payload["results"]], [
            "graph_visibility_edges_gate",
            "jaccard_chunk_100",
            "jaccard_chunk_50",
            "jaccard_chunk_20",
        ])
        graph_command = payload["results"][0]["command"]
        self.assertIn("scripts/goal889_graph_visibility_optix_gate.py", graph_command)
        self.assertIn("--strict", graph_command)
        self.assertEqual(graph_command[graph_command.index("--chunk-copies") + 1], "0")
        jaccard_command = payload["results"][1]["command"]
        self.assertIn("scripts/goal877_polygon_overlap_optix_phase_profiler.py", jaccard_command)
        self.assertIn("--chunk-copies", jaccard_command)
        self.assertIn("100", jaccard_command)

    def test_rejects_empty_jaccard_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "jaccard_chunk_copies"):
                goal914.run_driver(
                    mode="dry-run",
                    copies=1,
                    graph_chunk_copies=1,
                    jaccard_chunk_copies=(),
                    output_json=Path(tmp) / "plan.json",
                )


if __name__ == "__main__":
    unittest.main()
