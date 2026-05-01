import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.goal1175_staged_source_archive_builder import build_archive, verify_archive


class Goal1175StagedSourceArchiveBuilderTest(unittest.TestCase):
    def test_build_archive_records_sha_and_manifest_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            payload = build_archive(archive)

        self.assertTrue(payload["valid"])
        self.assertEqual(len(payload["archive_sha256"]), 64)
        self.assertGreater(payload["archive_bytes"], 0)
        self.assertGreater(payload["manifest_file_count"], 0)
        self.assertEqual(len(payload["manifest_aggregate_sha256"]), 64)

    def test_archive_contains_staged_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            build_archive(archive)
            with tarfile.open(archive, "r:gz") as handle:
                names = handle.getnames()

        self.assertTrue(any(name.startswith("rtdl_staged_source/src/") for name in names))
        self.assertTrue(any(name.startswith("rtdl_staged_source/scripts/") for name in names))

    def test_verify_archive_accepts_matching_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "source.tar.gz"
            payload = build_archive(archive)
            verification = verify_archive(archive, payload["archive_sha256"])

        self.assertTrue(verification["valid"])


if __name__ == "__main__":
    unittest.main()
