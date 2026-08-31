from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts import goal5793_x1_build_environment_source_bundle as builder


ROOT = Path(__file__).resolve().parents[1]


class EnvironmentSourceBundleTest(unittest.TestCase):
    def test_bundle_is_deterministic_and_exact(self) -> None:
        first, first_summary = builder.build_bundle(ROOT)
        second, second_summary = builder.build_bundle(ROOT)
        self.assertEqual(first, second)
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first_summary["file_count"], 326)
        self.assertEqual(first_summary["bundle_sha256"], hashlib.sha256(first).hexdigest())
        authority = json.loads(builder.SOURCE_AUTHORITY.read_text(encoding="utf-8"))
        expected = authority["declared_product_native_source_zero_drift_authority"]["rows"]
        with tarfile.open(fileobj=io.BytesIO(first), mode="r:gz") as archive:
            members = archive.getmembers()
            self.assertEqual([member.name for member in members], [row["path"] for row in expected])
            for member, row in zip(members, expected, strict=True):
                self.assertTrue(member.isfile())
                self.assertEqual((member.mode, member.uid, member.gid, member.mtime), (0o444, 0, 0, 0))
                self.assertEqual((member.uname, member.gname), ("", ""))
                payload = archive.extractfile(member).read()
                self.assertEqual(len(payload), row["size_bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_create_only_cli_guard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle.tar.gz"
            output.write_bytes(b"occupied")
            with self.assertRaises(builder.BundleError) as raised:
                old = __import__("sys").argv
                try:
                    __import__("sys").argv = ["builder", "--output", str(output)]
                    builder.main()
                finally:
                    __import__("sys").argv = old
            self.assertEqual(str(raised.exception), "create_only_output_exists")


if __name__ == "__main__":
    unittest.main()
