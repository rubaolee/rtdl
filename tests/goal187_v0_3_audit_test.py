from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
VIDEO_URL = "https://youtu.be/d3yJB7AmCLM"


class Goal187V03AuditTest(unittest.TestCase):
    def test_live_front_surface_docs_use_new_public_video_url(self) -> None:
        targets = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs/README.md",
            REPO_ROOT / "docs/current_milestone_qa.md",
        ]
        for path in targets:
            text = path.read_text(encoding="utf-8")
            self.assertIn(VIDEO_URL, text, msg=str(path))

    def test_live_docs_point_to_hidden_star_primary_demo(self) -> None:
        docs = {
            REPO_ROOT / "README.md": "examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py",
            REPO_ROOT / "docs/README.md": "examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py",
            REPO_ROOT / "docs/current_milestone_qa.md": "rtdl_hidden_star_stable_ball_demo.py",
        }
        for path, needle in docs.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn(needle, text, msg=str(path))

    def test_hidden_star_cli_system_smoke(self) -> None:
        output_dir = REPO_ROOT / "build/goal187_v0_3_audit_test/hidden_star_cli"
        if output_dir.exists():
            for child in output_dir.iterdir():
                child.unlink()
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            PYTHON,
            str(REPO_ROOT / "examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py"),
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "none",
            "--width",
            "20",
            "--height",
            "20",
            "--latitude-bands",
            "6",
            "--longitude-bands",
            "12",
            "--frames",
            "2",
            "--jobs",
            "1",
            "--shadow-mode",
            "rtdl_light_to_surface",
            "--output-dir",
            str(output_dir),
        ]
        subprocess.run(cmd, check=True, cwd=REPO_ROOT, capture_output=True, text=True)
        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["backend"], "cpu_python_reference")
        self.assertEqual(summary["frame_count"], 2)
        self.assertEqual(summary["light_count"], 1)
        self.assertEqual(summary["shadow_mode"], "rtdl_light_to_surface")
        self.assertGreater(summary["total_shadow_query_seconds"], 0.0)
        self.assertTrue(any(int(frame["shadow_rays"]) > 0 for frame in summary["frames"]))

    def test_orbit_cli_system_smoke(self) -> None:
        output_dir = REPO_ROOT / "build/goal187_v0_3_audit_test/orbit_cli"
        if output_dir.exists():
            for child in output_dir.iterdir():
                child.unlink()
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            PYTHON,
            str(REPO_ROOT / "examples/visual_demo/rtdl_orbiting_star_ball_demo.py"),
            "--backend",
            "cpu_python_reference",
            "--compare-backend",
            "cpu_python_reference",
            "--width",
            "20",
            "--height",
            "20",
            "--latitude-bands",
            "6",
            "--longitude-bands",
            "12",
            "--frames",
            "2",
            "--jobs",
            "1",
            "--show-light-source",
            "--temporal-blend-alpha",
            "0.10",
            "--phase-mode",
            "uniform",
            "--output-dir",
            str(output_dir),
        ]
        subprocess.run(cmd, check=True, cwd=REPO_ROOT, capture_output=True, text=True)
        summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["backend"], "cpu_python_reference")
        self.assertEqual(summary["frame_count"], 2)
        self.assertEqual(summary["light_count"], 2)
        self.assertEqual(summary["phase_mode"], "uniform")
        self.assertTrue(summary["frames"][0]["compare_backend"]["matches"])
        self.assertGreaterEqual(summary["frames"][0]["shadow_rays"], summary["frames"][0]["hit_pixels"] * 2)


if __name__ == "__main__":
    unittest.main()
