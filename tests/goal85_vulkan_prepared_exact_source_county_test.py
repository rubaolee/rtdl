from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.goal85_vulkan_prepared_exact_source_county as goal85


class Goal85VulkanPreparedExactSourceCountyTest(unittest.TestCase):
    def test_render_markdown_mentions_exact_source_scope(self) -> None:
        summary = {
            "host_label": "lx1",
            "db_name": "rtdl_postgis",
            "prepare_kernel_sec": 0.01,
            "pack_points_sec": 0.02,
            "pack_polygons_sec": 0.03,
            "bind_sec": 0.04,
            "postgis": {
                "plan": {"uses_index": True, "node_types": ["Index Scan", "Nested Loop"]},
                "row_count": 39073,
                "sha256": "abc",
            },
            "runs": [
                {
                    "backend_sec": 1.23,
                    "postgis_sec": 3.45,
                    "parity_vs_postgis": True,
                    "row_count": 39073,
                    "sha256": "abc",
                }
            ],
            "result": {
                "beats_postgis_all_reruns": True,
                "parity_preserved_all_reruns": True,
            },
        }
        md = goal85.render_markdown(summary)
        self.assertIn("exact-source top4 county/zipcode CDB package", md)
        self.assertIn("beats PostGIS on all reruns", md)

    def test_persist_summary_writes_json_and_markdown(self) -> None:
        summary = {
            "host_label": "lx1",
            "db_name": "rtdl_postgis",
            "prepare_kernel_sec": 0.01,
            "pack_points_sec": 0.02,
            "pack_polygons_sec": 0.03,
            "bind_sec": 0.04,
            "postgis": {
                "plan": {"uses_index": True, "node_types": ["Index Scan"]},
                "row_count": 1,
                "sha256": "abc",
            },
            "runs": [],
            "result": {
                "beats_postgis_all_reruns": False,
                "parity_preserved_all_reruns": False,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            goal85.persist_summary(out, summary)
            self.assertTrue((out / "summary.json").exists())
            self.assertTrue((out / "summary.md").exists())

    def test_parse_args_accepts_required_paths(self) -> None:
        with patch(
            "sys.argv",
            [
                "goal85",
                "--county-cdb",
                "/tmp/county.cdb",
                "--zipcode-cdb",
                "/tmp/zipcode.cdb",
                "--output-dir",
                "/tmp/out",
            ],
        ):
            args = goal85.parse_args()
        self.assertEqual(args.county_cdb, "/tmp/county.cdb")
        self.assertEqual(args.zipcode_cdb, "/tmp/zipcode.cdb")


if __name__ == "__main__":
    unittest.main()
