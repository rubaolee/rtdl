from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class Goal359WikiTalkTriangleCountEvalTest(unittest.TestCase):
    def test_wiki_talk_triangle_count_eval_script_runs_on_bounded_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "wiki-Talk.txt"
            dataset_path.write_text("0 1\n1 2\n2 0\n2 2\n1 0\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal359_wiki_talk_triangle_count_eval.py",
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

            self.assertIn('"dataset": "snap_wiki_talk"', result.stdout)
            self.assertIn('"graph_transform": "simple_undirected"', result.stdout)
            self.assertIn('"oracle_match": true', result.stdout)


if __name__ == "__main__":
    unittest.main()
