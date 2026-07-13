from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP_DIR / "results"
sys.path.insert(0, str(APP_DIR))
SCRIPT = APP_DIR / "extract_verified_ae_archive.py"
SPEC = importlib.util.spec_from_file_location("librts_goal5475_extract", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_tar(path: Path, entries: list[tuple[str, bytes | None, str]]) -> None:
    with tarfile.open(path, mode="w:gz") as archive:
        for name, payload, kind in entries:
            info = tarfile.TarInfo(name)
            if kind == "dir":
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = (
                    payload.decode("utf-8") if payload is not None else "target"
                )
                archive.addfile(info)
            else:
                assert payload is not None
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))


class Goal5475LibrtsSafeArchiveExtractionTest(unittest.TestCase):
    def test_goal5479_real_archive_inventory_is_safe_and_not_yet_extracted(self):
        import json

        payload = json.loads(
            (RESULTS / "librts_goal5479_archive_inventory.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            payload["status"], "exact_ae_archive_inventory_complete__not_extracted"
        )
        self.assertTrue(payload["inventory"]["safe"])
        self.assertEqual(payload["inventory"]["member_count"], 1694)
        self.assertEqual(payload["inventory"]["file_count"], 1370)
        self.assertEqual(payload["inventory"]["symlink_count"], 3)
        self.assertEqual(payload["inventory"]["unpacked_file_bytes"], 88229246574)
        self.assertTrue(payload["claim_boundary"]["inventory_completed"])
        self.assertFalse(payload["claim_boundary"]["archive_extracted"])

    def test_safe_inventory_and_atomic_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "safe.tar.gz"
            destination = root / "out"
            destination.mkdir()
            _write_tar(
                archive,
                [
                    ("bundle", None, "dir"),
                    ("bundle/data/a.txt", b"alpha", "file"),
                    ("bundle/data/b.txt", b"beta", "file"),
                ],
            )
            inventory = MODULE.inspect_archive_members(archive)
            self.assertEqual(inventory["file_count"], 2)
            self.assertEqual(inventory["unpacked_file_bytes"], 9)
            result = MODULE.extract_archive_atomically(archive, destination, inventory)
            final = Path(result["final_path"])
            self.assertEqual((final / "bundle/data/a.txt").read_text(), "alpha")
            self.assertFalse((destination / ".PPoPPAE-v2.extracting").exists())

    def test_resume_staging_skips_complete_and_rewrites_partial_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "safe.tar.gz"
            destination = root / "out"
            staging = destination / ".PPoPPAE-v2.extracting"
            (staging / "bundle/data").mkdir(parents=True)
            (staging / "bundle/data/a.txt").write_bytes(b"alpha")
            (staging / "bundle/data/b.txt").write_bytes(b"be")
            _write_tar(
                archive,
                [
                    ("bundle", None, "dir"),
                    ("bundle/data/a.txt", b"alpha", "file"),
                    ("bundle/data/b.txt", b"beta", "file"),
                ],
            )
            inventory = MODULE.inspect_archive_members(archive)
            result = MODULE.extract_archive_atomically(
                archive, destination, inventory, resume_staging=True
            )
            final = Path(result["final_path"])
            self.assertEqual((final / "bundle/data/a.txt").read_bytes(), b"alpha")
            self.assertEqual((final / "bundle/data/b.txt").read_bytes(), b"beta")
            self.assertEqual(result["resumed_complete_file_count"], 1)
            self.assertEqual(result["rewritten_partial_file_count"], 1)

    def test_parent_path_and_backslash_escape_are_rejected(self):
        for malicious_name in ("../escape.txt", "bundle/../../escape.txt", "..\\escape.txt"):
            with self.subTest(name=malicious_name), tempfile.TemporaryDirectory() as temporary:
                archive = Path(temporary) / "bad.tar.gz"
                _write_tar(archive, [(malicious_name, b"bad", "file")])
                with self.assertRaises(ValueError):
                    MODULE.inspect_archive_members(archive)

    def test_safe_relative_symlink_is_inventoried(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "safe-link.tar.gz"
            _write_tar(
                archive,
                [
                    ("bundle/target", b"value", "file"),
                    ("bundle/link", b"target", "symlink"),
                ],
            )
            inventory = MODULE.inspect_archive_members(archive)
            self.assertEqual(inventory["symlink_count"], 1)
            self.assertTrue(inventory["escaping_symlinks_rejected"])

    def test_escaping_symlinks_and_duplicate_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            symlink_archive = root / "symlink.tar.gz"
            duplicate_archive = root / "duplicate.tar.gz"
            _write_tar(symlink_archive, [("bundle/link", b"../../escape", "symlink")])
            _write_tar(
                duplicate_archive,
                [("bundle/a", b"one", "file"), ("bundle/a", b"two", "file")],
            )
            with self.assertRaises(ValueError):
                MODULE.inspect_archive_members(symlink_archive)
            with self.assertRaises(ValueError):
                MODULE.inspect_archive_members(duplicate_archive)

    def test_verified_archive_contract_remains_size_and_md5_bound(self):
        content = b"tiny-archive-placeholder"
        expected = hashlib.md5(content, usedforsecurity=False).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "archive.tar.gz"
            path.write_bytes(content)
            verified = MODULE.verify_archive(
                path,
                expected_size_bytes=len(content),
                expected_md5=expected,
            )
            self.assertTrue(verified["verified"])
            with self.assertRaises(ValueError):
                MODULE.verify_archive(
                    path,
                    expected_size_bytes=len(content),
                    expected_md5="0" * 32,
                )

    def test_verified_inventory_evidence_reuse_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / MODULE.ARCHIVE_NAME
            archive.write_bytes(b"x")
            evidence = root / "inventory.json"
            evidence.write_text(
                __import__("json").dumps(
                    {
                        "status": "exact_ae_archive_inventory_complete__not_extracted",
                        "verification": {
                            "verified": True,
                            "path": str(archive),
                            "size_bytes": MODULE.ARCHIVE_SIZE_BYTES,
                            "md5": MODULE.ARCHIVE_MD5,
                        },
                        "inventory": {
                            "safe": True,
                            "member_count": 1,
                            "file_count": 1,
                            "directory_count": 0,
                            "symlink_count": 0,
                            "unpacked_file_bytes": 1,
                            "top_level_entries": ["bundle"],
                        },
                        "claim_boundary": {
                            "archive_verified": True,
                            "inventory_completed": True,
                        },
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "absent or has changed size"):
                MODULE.load_verified_inventory_evidence(evidence, archive)

            original_size = MODULE.ARCHIVE_SIZE_BYTES
            try:
                MODULE.ARCHIVE_SIZE_BYTES = 1
                payload = __import__("json").loads(evidence.read_text(encoding="utf-8"))
                payload["verification"]["size_bytes"] = 1
                evidence.write_text(__import__("json").dumps(payload), encoding="utf-8")
                verification, inventory = MODULE.load_verified_inventory_evidence(
                    evidence, archive
                )
            finally:
                MODULE.ARCHIVE_SIZE_BYTES = original_size
            self.assertTrue(verification["verified"])
            self.assertTrue(inventory["safe"])


if __name__ == "__main__":
    unittest.main()
