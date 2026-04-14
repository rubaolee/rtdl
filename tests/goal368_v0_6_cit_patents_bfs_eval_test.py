from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class Goal368CitPatentsBfsEvalTest(unittest.TestCase):
    def test_cit_patents_eval_script_runs_on_bounded_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "cit-Patents.txt"
            dataset_path.write_text("0 1\n0 2\n2 3\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal368_cit_patents_bfs_eval.py",
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
            self.assertIn('"oracle_match": true', result.stdout)
            self.assertIn('"vertex_count": 3774768', result.stdout)


if __name__ == "__main__":
    unittest.main()
