from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class Goal372CitPatentsTriangleCountProbeTest(unittest.TestCase):
    def test_cit_patents_triangle_probe_runs_on_bounded_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "cit-Patents.txt"
            dataset_path.write_text("0 1\n1 2\n2 0\n2 2\n1 0\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal372_cit_patents_triangle_count_probe.py",
                    "--dataset",
                    str(dataset_path),
                    "--max-edges",
                    "10",
                    "--repeats",
                    "1",
                ],
                cwd=Path(__file__).resolve().parents[1],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn('"dataset": "graphalytics_cit_patents"', result.stdout)
            self.assertIn('"goal": "goal372"', result.stdout)
            self.assertIn('"graph_transform": "simple_undirected"', result.stdout)
            self.assertIn('"oracle_match": true', result.stdout)
            self.assertIn('"workload": "triangle_count"', result.stdout)

    def test_cit_patents_triangle_probe_reports_max_canonical_edges(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "cit-Patents.txt"
            dataset_path.write_text("0 1\n1 2\n2 0\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal372_cit_patents_triangle_count_probe.py",
                    "--dataset",
                    str(dataset_path),
                    "--max-edges",
                    "50000",
                    "--repeats",
                    "1",
                ],
                cwd=Path(__file__).resolve().parents[1],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn('"max_canonical_edges_loaded": 50000', result.stdout)


if __name__ == "__main__":
    unittest.main()
