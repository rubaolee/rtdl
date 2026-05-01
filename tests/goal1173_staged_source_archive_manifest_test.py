import unittest

from scripts.goal1173_staged_source_archive_manifest import build_manifest


class Goal1173StagedSourceArchiveManifestTest(unittest.TestCase):
    def test_manifest_has_source_roots_and_digest(self):
        payload = build_manifest()

        self.assertTrue(payload["valid"])
        self.assertGreater(payload["file_count"], 0)
        self.assertEqual(len(payload["aggregate_sha256"]), 64)
        self.assertIn("src", payload["include_dirs"])
        self.assertIn("examples", payload["include_dirs"])
        self.assertIn("scripts", payload["include_dirs"])
        self.assertIn("tests", payload["include_dirs"])

    def test_manifest_excludes_build_outputs(self):
        payload = build_manifest()
        paths = [row["path"] for row in payload["files"]]

        self.assertFalse(any(path.startswith("build/") for path in paths))
        self.assertFalse(any(path.endswith(".so") for path in paths))
        self.assertFalse(any("/__pycache__/" in path for path in paths))


if __name__ == "__main__":
    unittest.main()
