from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from goal5776_verify_source_file_manifest import MANIFEST_MEMBER, verify
from goal5776_build_pre_pod_bundle import (
    REQUIRED_LEGACY_SCRIPT_DEPENDENCIES,
    ROOT,
    _overlays,
)


class Goal5776SourceFileManifestTest(unittest.TestCase):
    def _root(self, directory: str) -> tuple[Path, Path]:
        root = Path(directory) / "source"
        (root / "src").mkdir(parents=True)
        (root / "src/module.py").write_bytes(b"answer = 42\n")
        manifest = root / MANIFEST_MEMBER
        manifest.parent.mkdir(parents=True)
        data = (root / "src/module.py").read_bytes()
        manifest.write_text(json.dumps({
            "schema": "rtdl.goal5776.source_file_manifest.v1",
            "file_count": 1,
            "files": [{
                "path": "src/module.py", "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }],
        }, sort_keys=True) + "\n", encoding="utf-8")
        return root, manifest

    def test_exact_source_membership_and_bytes_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root(directory)
            self.assertEqual(verify(root, manifest)["status"], "PASS")

    def test_extra_or_mutated_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root(directory)
            (root / "extra.py").write_bytes(b"extra")
            with self.assertRaisesRegex(RuntimeError, "membership"):
                verify(root, manifest)
            (root / "extra.py").unlink()
            (root / "src/module.py").write_bytes(b"answer = 43\n")
            with self.assertRaisesRegex(RuntimeError, "byte mismatch"):
                verify(root, manifest)

    def test_portable_overlay_carries_every_goal5776_helper_and_legacy_reader(self):
        overlays = set(_overlays())
        expected = {
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / "scripts").glob("goal5776*")
            if path.is_file()
        }
        expected.update(REQUIRED_LEGACY_SCRIPT_DEPENDENCIES)
        self.assertTrue(expected)
        self.assertEqual(expected - overlays, set())


if __name__ == "__main__":
    unittest.main()
