from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.goal77_runtime_cache_measurement import persist_summary
from scripts.goal77_runtime_cache_measurement import render_markdown
from scripts.goal77_runtime_cache_measurement import select_clear_cache_fn
from scripts.goal77_runtime_cache_measurement import select_run_fn
import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime
from rtdsl import vulkan_runtime


class Goal77RuntimeCacheMeasurementTest(unittest.TestCase):
    def test_select_run_fn(self) -> None:
        self.assertIs(select_run_fn("embree"), rt.run_embree)
        self.assertIs(select_run_fn("optix"), rt.run_optix)
        self.assertIs(select_run_fn("vulkan"), rt.run_vulkan)

    def test_select_clear_cache_fn(self) -> None:
        self.assertIs(select_clear_cache_fn("embree"), embree_runtime.clear_embree_prepared_cache)
        self.assertIs(select_clear_cache_fn("optix"), optix_runtime.clear_optix_prepared_cache)
        self.assertIs(select_clear_cache_fn("vulkan"), vulkan_runtime.clear_vulkan_prepared_cache)

    def test_render_mentions_runtime_cache_boundary(self) -> None:
        text = render_markdown(
            {
                "backend": "optix",
                "host_label": "host",
                "db_name": "db",
                "postgis": {
                    "plan": {"uses_index": True, "node_types": ["Index Scan"]},
                    "row_count": 5,
                    "sha256": "abc",
                },
                "runs": [
                    {
                        "backend_sec": 2.0,
                        "postgis_sec": 3.0,
                        "parity_vs_postgis": True,
                        "row_count": 5,
                        "sha256": "abc",
                    },
                    {
                        "backend_sec": 1.0,
                        "postgis_sec": 3.0,
                        "parity_vs_postgis": True,
                        "row_count": 5,
                        "sha256": "abc",
                    },
                ],
                "result": {
                    "first_run_sec": 2.0,
                    "best_repeated_run_sec": 1.0,
                    "repeated_run_improved": True,
                    "parity_preserved_all_reruns": True,
                },
            }
        )
        self.assertIn("runtime-owned normalization", text)
        self.assertIn("best repeated run", text)

    def test_persist_summary_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            persist_summary(
                path,
                {
                    "backend": "embree",
                    "host_label": "host",
                    "db_name": "db",
                    "postgis": {
                        "plan": {"uses_index": True, "node_types": []},
                        "row_count": 0,
                        "sha256": "x",
                    },
                    "runs": [],
                    "result": {
                        "first_run_sec": 0.0,
                        "best_repeated_run_sec": 0.0,
                        "repeated_run_improved": False,
                        "parity_preserved_all_reruns": False,
                    },
                },
            )
            self.assertTrue((path / "summary.json").exists())
            self.assertTrue((path / "summary.md").exists())


if __name__ == "__main__":
    unittest.main()
