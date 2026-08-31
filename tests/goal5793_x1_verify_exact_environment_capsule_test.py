from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/goal5793_x1_verify_exact_environment_capsule.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5793_x1_verify_environment_capsule", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifyExactEnvironmentCapsuleTest(unittest.TestCase):
    def test_raw_posix_name_validation(self):
        module = load_module()
        self.assertTrue(module._safe_name("a/b"))
        for name in ("", "/a", "a/", "a//b", "a/./b", "a/../b", "a\\b"):
            self.assertFalse(module._safe_name(name))

    def test_payload_set_digest_binds_order(self):
        module = load_module()
        rows = [
            {"path": "a", "bytes": 1, "sha256": "0" * 64},
            {"path": "b", "bytes": 2, "sha256": "1" * 64},
        ]
        self.assertNotEqual(module._payload_set_digest(rows), module._payload_set_digest(list(reversed(rows))))


if __name__ == "__main__":
    unittest.main()
