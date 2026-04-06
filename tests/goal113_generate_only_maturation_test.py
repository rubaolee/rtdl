import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal113GenerateOnlyMaturationTest(unittest.TestCase):
    def test_generate_handoff_bundle_writes_manifest_readme_and_program(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            bundle_dir = Path(tmpdir) / "handoff_bundle"
            payload = rt.generate_handoff_bundle(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_hitcount",
                    dataset="authored_segment_polygon_minimal",
                    backend="cpu_python_reference",
                    verify=True,
                    output_mode="rows",
                    artifact_shape="handoff_bundle",
                ),
                bundle_dir,
            )
            program = Path(payload["program"])
            manifest = Path(payload["manifest"])
            readme = Path(payload["readme"])
            self.assertTrue(program.exists())
            self.assertTrue(manifest.exists())
            self.assertTrue(readme.exists())
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["artifact_shape"], "handoff_bundle")
            self.assertIn("RTDL Generate-Only Handoff Bundle", readme.read_text(encoding="utf-8"))
            self.assertIn(program.name, readme.read_text(encoding="utf-8"))

    def test_generated_handoff_bundle_program_runs(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            bundle_dir = Path(tmpdir) / "handoff_bundle"
            payload = rt.generate_handoff_bundle(
                rt.GenerateOnlyRequest(
                    workload="segment_polygon_hitcount",
                    dataset="authored_segment_polygon_minimal",
                    backend="cpu_python_reference",
                    verify=True,
                    output_mode="summary",
                    artifact_shape="handoff_bundle",
                ),
                bundle_dir,
            )
            completed = subprocess.run(
                [sys.executable, payload["program"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["backend"], "cpu_python_reference")
            self.assertTrue(result["verified_against_cpu_python_reference"])
            self.assertEqual(result["row_count"], 2)

    def test_bundle_is_more_handoff_ready_than_single_file_mvp(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            tmp_root = Path(tmpdir)
            single_file = tmp_root / "generated.py"
            bundle_dir = tmp_root / "bundle"
            request = rt.GenerateOnlyRequest(
                workload="segment_polygon_hitcount",
                dataset="authored_segment_polygon_minimal",
                backend="cpu_python_reference",
                verify=True,
                output_mode="rows",
            )
            rt.generate_python_program(request, single_file)
            rt.generate_handoff_bundle(
                rt.GenerateOnlyRequest(**{**request.to_dict(), "artifact_shape": "handoff_bundle"}),
                bundle_dir,
            )
            self.assertTrue(single_file.exists())
            self.assertFalse((single_file.parent / "README.md").exists())
            self.assertTrue((bundle_dir / "README.md").exists())
            self.assertTrue((bundle_dir / "request.json").exists())


if __name__ == "__main__":
    unittest.main()
