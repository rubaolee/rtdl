from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json_example(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal686AppCatalogCleanupTest(unittest.TestCase):
    def test_db_app_accepts_public_cpu_python_reference_alias(self) -> None:
        payload = run_json_example(
            "examples/rtdl_v0_7_db_app_demo.py",
            "--backend",
            "cpu_python_reference",
        )

        self.assertEqual(payload["app"], "regional_order_dashboard")
        self.assertEqual(payload["requested_backend"], "cpu_python_reference")
        self.assertEqual(payload["backend"], "cpu_reference")
        self.assertIn("promo_order_ids", payload["results"])

    def test_public_app_catalog_names_spatial_join_apps(self) -> None:
        catalog = (REPO_ROOT / "docs" / "application_catalog.md").read_text(encoding="utf-8")

        required = (
            "Service coverage gaps",
            "Event hotspot screening",
            "Facility KNN assignment",
            "Road hazard screening",
            "Segment/polygon hit count",
            "Segment/polygon any-hit rows",
            "Polygon-pair overlap rows",
            "Polygon-set Jaccard",
            "PostGIS is an external baseline",
            "not a full GIS engine",
        )
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, catalog)

    def test_public_docs_link_application_catalog(self) -> None:
        docs = (
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs" / "README.md",
            REPO_ROOT / "docs" / "release_facing_examples.md",
            REPO_ROOT / "examples" / "README.md",
        )
        for path in docs:
            with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                text = path.read_text(encoding="utf-8")
                self.assertIn("application_catalog.md", text)

    def test_spatial_join_app_clis_emit_json(self) -> None:
        cases = (
            ("examples/rtdl_service_coverage_gaps.py", "service_coverage_gaps"),
            ("examples/rtdl_event_hotspot_screening.py", "event_hotspot_screening"),
            ("examples/rtdl_facility_knn_assignment.py", "facility_knn_assignment"),
            ("examples/rtdl_road_hazard_screening.py", "road_hazard_screening"),
        )
        for script, app_name in cases:
            with self.subTest(script=script):
                payload = run_json_example(script, "--backend", "cpu_python_reference")
                self.assertEqual(payload["app"], app_name)

    def test_unified_database_graph_and_apple_apps_emit_json(self) -> None:
        cases = (
            (
                ("examples/rtdl_database_analytics_app.py", "--backend", "cpu_python_reference"),
                "database_analytics",
                ("regional_dashboard", "sales_risk"),
            ),
            (
                ("examples/rtdl_graph_analytics_app.py", "--backend", "cpu_python_reference"),
                "graph_analytics",
                ("bfs", "triangle_count"),
            ),
            (
                ("examples/rtdl_apple_rt_demo_app.py",),
                "apple_rt_demo",
                ("closest_hit", "visibility_count"),
            ),
        )
        for args, app_name, sections in cases:
            with self.subTest(app=app_name):
                payload = run_json_example(*args)
                self.assertEqual(payload["app"], app_name)
                for section in sections:
                    self.assertIn(section, payload["sections"])


if __name__ == "__main__":
    unittest.main()
