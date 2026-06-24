import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"


class V3PublicDocsRebuildSurfaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs_index = (DOCS / "README.md").read_text(encoding="utf-8")
        cls.status = (DOCS / "current_v3_status.md").read_text(encoding="utf-8")
        cls.public_map = (DOCS / "public_documentation_map.md").read_text(encoding="utf-8")
        cls.boundaries = (DOCS / "learn" / "performance_wording.md").read_text(encoding="utf-8")
        cls.combined = "\n".join((cls.docs_index, cls.status, cls.public_map, cls.boundaries))

    def test_public_docs_are_clean_current_v3_surface(self) -> None:
        self.assertIn("current V3.0.0 documentation surface", self.docs_index)
        self.assertIn("Current V3.0.0 Status", self.status)
        self.assertIn("Public Documentation Map", self.public_map)
        self.assertIn("Performance Wording Guide", self.boundaries)
        self.assertNotIn("docs/rebuild", self.combined)
        self.assertNotIn("docs/reviews", self.combined)
        self.assertNotIn("release-candidate", self.combined)
        self.assertNotIn("history/", self.combined)
        self.assertNotIn("archive", self.combined.lower())
        self.assertNotIn("handoff", self.combined.lower())
        self.assertNotIn("release_authorized", self.combined)

    def test_claim_boundaries_are_explicit(self) -> None:
        self.assertIn("Performance Wording Guide", self.boundaries)
        self.assertIn("Use Exact Wording", self.boundaries)
        self.assertIn("Prefer Scoped Sentences", self.boundaries)

    def test_public_map_prefers_user_path(self) -> None:
        self.assertLess(
            self.public_map.index("[Project README](../README.md)"),
            self.public_map.index("[Performance Wording](learn/performance_wording.md)"),
        )
        self.assertIn("[Performance Wording](learn/performance_wording.md)", self.public_map)

    def test_getting_started_examples_run_with_clean_default_output(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{REPO_ROOT / 'src'}{os.pathsep}{REPO_ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
        examples = (
            "rtdl_hello_world.py",
            "rtdl_hello_world_backends.py",
            "rtdl_primitive_discovery_workflow.py",
            "rtdl_feature_quickstart_cookbook.py",
            "rtdl_prepared_measurement_demo.py",
        )
        forbidden = (
            "claim_boundary",
            "release_authorized",
            "public_speedup_claim_authorized",
            "history/",
            "docs/rebuild",
            "docs/reviews",
            "V4",
            "V2",
            "v3_rebuild",
        )

        for script in examples:
            with self.subTest(script=script):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(REPO_ROOT / "examples" / "current" / "getting_started" / script),
                    ],
                    cwd=REPO_ROOT,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                self.assertTrue(completed.stdout.strip(), script)
                combined = completed.stdout + completed.stderr
                for needle in forbidden:
                    self.assertNotIn(needle, combined, script)


if __name__ == "__main__":
    unittest.main()
