from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_json(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal692OptixAppCorrectnessTransparencyTest(unittest.TestCase):
    def test_db_app_exposes_python_interface_dominated_optix_classification(self) -> None:
        payload = run_json("examples/rtdl_database_analytics_app.py", "--backend", "cpu_python_reference")
        self.assertEqual(payload["optix_performance"]["class"], "python_interface_dominated")
        self.assertIn("not SQL", payload["honesty_boundary"])

    def test_segment_polygon_apps_expose_host_indexed_optix_classification(self) -> None:
        cases = (
            ("examples/rtdl_road_hazard_screening.py", ("--backend", "cpu_python_reference")),
            ("examples/rtdl_segment_polygon_hitcount.py", ("--backend", "cpu_python_reference")),
            ("examples/rtdl_segment_polygon_anyhit_rows.py", ("--backend", "cpu_python_reference")),
        )
        for script, extra_args in cases:
            with self.subTest(script=script):
                payload = run_json(script, *extra_args)
                self.assertEqual(payload["optix_performance"]["class"], "host_indexed_fallback")
                self.assertIn("RT-core performance", payload["boundary"])

    def test_segment_polygon_anyhit_summary_modes_preserve_counts(self) -> None:
        rows_payload = run_json(
            "examples/rtdl_segment_polygon_anyhit_rows.py",
            "--backend",
            "cpu_python_reference",
            "--output-mode",
            "rows",
        )
        flags_payload = run_json(
            "examples/rtdl_segment_polygon_anyhit_rows.py",
            "--backend",
            "cpu_python_reference",
            "--output-mode",
            "segment_flags",
        )
        counts_payload = run_json(
            "examples/rtdl_segment_polygon_anyhit_rows.py",
            "--backend",
            "cpu_python_reference",
            "--output-mode",
            "segment_counts",
        )

        expected_counts: dict[int, int] = {}
        for row in rows_payload["rows"]:
            segment_id = int(row["segment_id"])
            expected_counts[segment_id] = expected_counts.get(segment_id, 0) + 1

        actual_counts = {int(row["segment_id"]): int(row["hit_count"]) for row in counts_payload["segment_counts"]}
        actual_flags = {int(row["segment_id"]): int(row["any_hit"]) for row in flags_payload["segment_flags"]}

        for segment_id, hit_count in actual_counts.items():
            self.assertEqual(hit_count, expected_counts.get(segment_id, 0))
            self.assertEqual(actual_flags[segment_id], int(hit_count > 0))
        self.assertNotIn("rows", flags_payload)
        self.assertNotIn("rows", counts_payload)

    def test_db_cpu_runtime_matches_cpu_python_reference_for_public_app_shape(self) -> None:
        reference = run_json("examples/rtdl_database_analytics_app.py", "--backend", "cpu_python_reference")
        native_cpu = run_json("examples/rtdl_database_analytics_app.py", "--backend", "cpu")
        self.assertEqual(
            reference["sections"]["regional_dashboard"]["results"],
            native_cpu["sections"]["regional_dashboard"]["results"],
        )
        self.assertEqual(
            reference["sections"]["sales_risk"]["summary"],
            native_cpu["sections"]["sales_risk"]["summary"],
        )
        self.assertEqual(
            reference["sections"]["sales_risk"]["rows"],
            native_cpu["sections"]["sales_risk"]["rows"],
        )

    def test_segment_polygon_cpu_runtime_matches_cpu_python_reference_for_summary_modes(self) -> None:
        for output_mode in ("rows", "segment_flags", "segment_counts"):
            with self.subTest(output_mode=output_mode):
                reference = run_json(
                    "examples/rtdl_segment_polygon_anyhit_rows.py",
                    "--backend",
                    "cpu_python_reference",
                    "--output-mode",
                    output_mode,
                )
                native_cpu = run_json(
                    "examples/rtdl_segment_polygon_anyhit_rows.py",
                    "--backend",
                    "cpu",
                    "--output-mode",
                    output_mode,
                )
                self.assertEqual(reference, native_cpu | {"backend": "cpu_python_reference"})


if __name__ == "__main__":
    unittest.main()
