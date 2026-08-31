from __future__ import annotations

import gzip
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/goal5793_x1_build_exact_environment_capsule.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5793_x1_environment_capsule", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExactEnvironmentCapsuleTest(unittest.TestCase):
    def test_unsafe_names_rejected(self):
        module = load_module()
        for value in ("", "/abs", "../escape", "a\\b", "a/./b"):
            with self.assertRaises(module.CapsuleError):
                module._safe_name(value)

    def test_payload_set_digest_is_order_sensitive(self):
        module = load_module()
        rows = [{"path": "a", "bytes": 1, "sha256": "0" * 64, "source_path": "x"},
                {"path": "b", "bytes": 1, "sha256": "1" * 64, "source_path": "y"}]
        self.assertNotEqual(module._payload_set_digest(rows), module._payload_set_digest(list(reversed(rows))))

    def test_tar_helpers_emit_canonical_metadata(self):
        module = load_module()
        raw = io.BytesIO()
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.USTAR_FORMAT) as archive:
                module._add_bytes(archive, "x", b"payload")
        with tarfile.open(fileobj=io.BytesIO(raw.getvalue()), mode="r:gz") as archive:
            member = archive.getmembers()[0]
            self.assertEqual((member.mode, member.uid, member.gid, member.mtime), (0o444, 0, 0, 0))
            self.assertEqual((member.uname, member.gname), ("", ""))


if __name__ == "__main__":
    unittest.main()
