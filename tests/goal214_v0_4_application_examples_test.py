import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_event_hotspot_screening
from examples import rtdl_facility_knn_assignment
from examples import rtdl_service_coverage_gaps


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


class Goal214V04ApplicationExamplesTest(unittest.TestCase):
    def test_service_coverage_in_process(self) -> None:
        payload = rtdl_service_coverage_gaps.run_case("cpu_python_reference", copies=2)
        self.assertEqual(payload["app"], "service_coverage_gaps")
        self.assertGreater(len(payload["uncovered_household_ids"]), 0)

    def test_event_hotspot_in_process(self) -> None:
        payload = rtdl_event_hotspot_screening.run_case("cpu_python_reference", copies=2)
        self.assertEqual(payload["app"], "event_hotspot_screening")
        self.assertGreater(len(payload["hotspots"]), 0)

    def test_facility_assignment_in_process(self) -> None:
        payload = rtdl_facility_knn_assignment.run_case("cpu_python_reference", copies=2)
        self.assertEqual(payload["app"], "facility_knn_assignment")
        self.assertEqual(set(payload["primary_depot_by_customer"]), set(payload["choices_by_customer"]))

    def test_service_coverage_cli(self) -> None:
        completed = subprocess.run(
            [PYTHON, "examples/rtdl_service_coverage_gaps.py", "--backend", "cpu_python_reference", "--copies", "2"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        self.assertEqual(json.loads(completed.stdout)["app"], "service_coverage_gaps")

    def test_event_hotspot_cli(self) -> None:
        completed = subprocess.run(
            [PYTHON, "examples/rtdl_event_hotspot_screening.py", "--backend", "cpu_python_reference", "--copies", "2"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        self.assertEqual(json.loads(completed.stdout)["app"], "event_hotspot_screening")

    def test_facility_assignment_cli(self) -> None:
        completed = subprocess.run(
            [PYTHON, "examples/rtdl_facility_knn_assignment.py", "--backend", "cpu_python_reference", "--copies", "2"],
            check=True,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        self.assertEqual(json.loads(completed.stdout)["app"], "facility_knn_assignment")

    def test_sql_scripts_exist_and_reference_expected_primitives(self) -> None:
        service_sql = (REPO_ROOT / "docs/sql/v0_4_service_coverage_gaps_postgis.sql").read_text(encoding="utf-8")
        hotspot_sql = (REPO_ROOT / "docs/sql/v0_4_event_hotspot_screening_postgis.sql").read_text(encoding="utf-8")
        facility_sql = (REPO_ROOT / "docs/sql/v0_4_facility_knn_assignment_postgis.sql").read_text(encoding="utf-8")
        self.assertIn("ST_DWithin", service_sql)
        self.assertIn("WHERE q.id <> s.id", hotspot_sql)
        self.assertIn("CROSS JOIN LATERAL", facility_sql)
        self.assertIn("<->", facility_sql)

    def test_application_doc_links_all_three_apps(self) -> None:
        doc = (REPO_ROOT / "docs/v0_4_application_examples.md").read_text(encoding="utf-8")
        self.assertIn("rtdl_service_coverage_gaps.py", doc)
        self.assertIn("rtdl_event_hotspot_screening.py", doc)
        self.assertIn("rtdl_facility_knn_assignment.py", doc)


if __name__ == "__main__":
    unittest.main()
