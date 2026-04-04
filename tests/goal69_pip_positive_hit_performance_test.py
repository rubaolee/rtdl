from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.goal69_pip_positive_hit_performance import point_in_counties_positive_hits
from scripts.goal69_pip_positive_hit_performance import render_markdown
from scripts.goal69_pip_positive_hit_performance import persist_summary
import rtdsl as rt


class Goal69PipPositiveHitPerformanceTest(unittest.TestCase):
    def test_kernel_emits_positive_hit_predicate_mode(self) -> None:
        compiled = rt.compile_kernel(point_in_counties_positive_hits)
        self.assertEqual(compiled.refine_op.predicate.options["result_mode"], "positive_hits")
        self.assertEqual(compiled.emit_op.fields, ("point_id", "polygon_id", "contains"))

    def test_render_markdown_mentions_positive_hit_scope(self) -> None:
        text = render_markdown(
            {
                "host_label": "host",
                "db_name": "db",
                "county_zipcode": {
                    "load_sec": 1.0,
                    "compared_backends": ["cpu"],
                    "postgis_mode": "indexed",
                    "pip": {
                        "postgis": {"row_count": 3},
                        "postgis_sec": 0.2,
                        "plan": {"uses_index": True, "node_types": ["Index Scan"]},
                        "cpu": {"sec": 0.5, "parity_vs_postgis": True, "row_count": 3},
                    },
                },
            }
        )
        self.assertIn("positive-hit", text)
        self.assertIn("County/Zipcode", text)

    def test_persist_summary_writes_goal69_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            persist_summary(
                path,
                {
                    "host_label": "host",
                    "db_name": "db",
                    "county_zipcode": {
                        "load_sec": 0.0,
                        "compared_backends": [],
                        "postgis_mode": "indexed",
                        "pip": {
                            "postgis": {"row_count": 0},
                            "postgis_sec": 0.0,
                            "plan": {"uses_index": True, "node_types": []},
                        },
                    },
                },
            )
            self.assertTrue((path / "goal69_summary.json").exists())
            self.assertTrue((path / "goal69_summary.md").exists())


if __name__ == "__main__":
    unittest.main()
