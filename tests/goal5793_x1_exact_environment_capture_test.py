from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/goal5793_x1_capture_exact_environment.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5793_x1_exact_environment", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExactEnvironmentCaptureTest(unittest.TestCase):
    def test_gnu_build_id_note(self):
        module = load_module()
        digest = bytes.fromhex("c4678ea80066e7d71c2db6b8ea2943fadb0fc134")
        note = struct.pack("<III", 4, len(digest), 3) + b"GNU\0" + digest
        self.assertEqual(module._parse_gnu_build_id_note(note), digest.hex())

    def test_gnu_build_id_rejects_duplicate(self):
        module = load_module()
        digest = bytes.fromhex("c4678ea80066e7d71c2db6b8ea2943fadb0fc134")
        one = struct.pack("<III", 4, len(digest), 3) + b"GNU\0" + digest
        with self.assertRaisesRegex(module.CaptureError, "not_unique"):
            module._parse_gnu_build_id_note(one + one)

    def test_plain_source_seal_detects_drift(self):
        module = load_module()
        value = {"schema": "x", "source_authority_sha256": ""}
        body = dict(value)
        body.pop("source_authority_sha256")
        value["source_authority_sha256"] = hashlib.sha256(module.canonical_json_bytes(body)).hexdigest()
        module._verify_plain_seal(value, "source_authority_sha256")
        value["schema"] = "y"
        with self.assertRaisesRegex(module.CaptureError, "mismatch"):
            module._verify_plain_seal(value, "source_authority_sha256")

    def test_tree_rejects_symlink(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = root / "target"
            target.write_bytes(b"x")
            link = root / "link"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlink unavailable")
            with self.assertRaisesRegex(module.CaptureError, "symlink_forbidden"):
                module._tree_rows(root, "fixture")


if __name__ == "__main__":
    unittest.main()
