from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.goal71_prepared_backend_positive_hit_county import persist_summary
from scripts.goal71_prepared_backend_positive_hit_county import render_markdown
from scripts.goal71_prepared_backend_positive_hit_county import select_prepare_fn
import rtdsl as rt


class Goal71PreparedBackendPositiveHitCountyTest(unittest.TestCase):
    def test_select_prepare_fn(self) -> None:
        self.assertIs(select_prepare_fn("embree"), rt.prepare_embree)
        self.assertIs(select_prepare_fn("vulkan"), rt.prepare_vulkan)
        self.assertIs(select_prepare_fn("optix"), rt.prepare_optix)

    def test_render_mentions_prepared_boundary_and_backend(self) -> None:
        text = render_markdown(
            {
                "backend": "embree",
                "host_label": "host",
                "db_name": "db",
                "prepare_kernel_sec": 1.0,
                "pack_points_sec": 2.0,
                "pack_polygons_sec": 3.0,
                "bind_sec": 4.0,
                "postgis": {
                    "plan": {"uses_index": True, "node_types": ["Index Scan"]},
                    "row_count": 5,
                    "sha256": "abc",
                },
                "runs": [
                    {
                        "backend_sec": 0.5,
                        "postgis_sec": 0.7,
                        "parity_vs_postgis": True,
                        "row_count": 5,
                        "sha256": "abc",
                    }
                ],
                "result": {
                    "beats_postgis_all_reruns": True,
                    "parity_preserved_all_reruns": True,
                },
            }
        )
        self.assertIn("execution-ready / prepacked", text)
        self.assertIn("Embree", text)

    def test_persist_summary_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            persist_summary(
                path,
                {
                    "backend": "vulkan",
                    "host_label": "host",
                    "db_name": "db",
                    "prepare_kernel_sec": 0.0,
                    "pack_points_sec": 0.0,
                    "pack_polygons_sec": 0.0,
                    "bind_sec": 0.0,
                    "postgis": {
                        "plan": {"uses_index": True, "node_types": []},
                        "row_count": 0,
                        "sha256": "x",
                    },
                    "runs": [],
                    "result": {
                        "beats_postgis_all_reruns": False,
                        "parity_preserved_all_reruns": False,
                    },
                },
            )
            self.assertTrue((path / "summary.json").exists())
            self.assertTrue((path / "summary.md").exists())


if __name__ == "__main__":
    unittest.main()
