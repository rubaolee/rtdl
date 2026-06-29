from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class V4Goal4806RayJoinSection57PodSetupTest(unittest.TestCase):
    def test_setup_reports_missing_author_and_exact_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_json = root / "setup.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_pod_setup.py",
                    "--author-root",
                    str(root / "missing_author"),
                    "--dataset-root",
                    str(root / "missing_dataset"),
                    "--output-dir",
                    str(root / "out"),
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)
            file_payload = json.loads(output_json.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.rayjoin.section57_pod_setup.v1")
        self.assertEqual(file_payload["schema"], payload["schema"])
        self.assertFalse(payload["ready_for_section57_runbook"])
        self.assertIn("missing_author_source", payload["blockers"])
        self.assertIn("missing_author_binaries", payload["blockers"])
        self.assertIn("missing_exact_section57_cdb_inputs", payload["blockers"])
        self.assertIn("https://github.com/pwrliang/RayJoin", payload["author_repo"]["url"])
        self.assertIn("scripts/rayjoin_section57_pod_runbook.py", payload["next_command"])

    def test_setup_recognizes_fake_author_binaries_and_all_eight_input_paths(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            author = root / "RayJoin_fresh"
            bin_dir = author / "release" / "bin"
            bin_dir.mkdir(parents=True)
            (bin_dir / "query_exec").write_text("#!/bin/sh\n", encoding="utf-8")
            (bin_dir / "polyover_exec").write_text("#!/bin/sh\n", encoding="utf-8")
            dataset = root / "rayjoin_section57_cdb"
            for pair in paper_pairs():
                for relative in (pair.left_relative_path, pair.right_relative_path):
                    path = dataset / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_pod_setup.py",
                    "--author-root",
                    str(author),
                    "--dataset-root",
                    str(dataset),
                    "--output-dir",
                    str(root / "out"),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)

        self.assertTrue(payload["author"]["binaries_ready"])
        self.assertTrue(payload["dataset"]["all_overlay_pairs_ready"])
        self.assertEqual(payload["dataset"]["overlay_pairs_ready"], 8)
        self.assertNotIn("missing_author_source", payload["blockers"])
        self.assertNotIn("missing_author_binaries", payload["blockers"])
        self.assertNotIn("missing_exact_section57_cdb_inputs", payload["blockers"])
        self.assertIn(str(bin_dir / "query_exec"), payload["next_command"])
        self.assertIn(str(bin_dir / "polyover_exec"), payload["next_command"])
        self.assertFalse(payload["ready_for_section57_runbook"])
        self.assertIn("Setup readiness is not performance evidence", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
