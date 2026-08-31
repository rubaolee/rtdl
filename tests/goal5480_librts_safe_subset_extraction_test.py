from __future__ import annotations

import importlib.util
import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_subset", APP / "extract_verified_ae_subset.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5480LibrtsSafeSubsetExtractionTest(unittest.TestCase):
    def test_selected_regular_files_are_atomically_extracted_with_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "bundle.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                for name, content in (
                    ("bundle/a.wkt", b"POINT (1 2)\n"),
                    ("bundle/b.wkt", b"POINT (3 4)\n"),
                    ("bundle/unselected.bin", b"unused"),
                ):
                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    archive.addfile(info, io.BytesIO(content))
            destination = root / "selected"
            result = MODULE.extract_selected_members_atomically(
                archive_path,
                destination,
                ("bundle/a.wkt", "bundle/b.wkt"),
            )
            self.assertEqual(result["selected_member_count"], 2)
            self.assertEqual((destination / "bundle/a.wkt").read_bytes(), b"POINT (1 2)\n")
            self.assertFalse((destination / "bundle/unselected.bin").exists())
            self.assertTrue(result["atomic_directory_promotion"])

    def test_missing_selected_member_fails_closed_and_removes_staging(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "bundle.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                content = b"value"
                info = tarfile.TarInfo("bundle/a")
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
            destination = root / "selected"
            with self.assertRaises(FileNotFoundError):
                MODULE.extract_selected_members_atomically(
                    archive_path, destination, ("bundle/missing",)
                )
            self.assertFalse(destination.exists())
            self.assertFalse((root / ".selected.extracting").exists())


if __name__ == "__main__":
    unittest.main()
