from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5793_x1_canonical.py"


def load_module():
    spec = importlib.util.spec_from_file_location("goal5793_x1_canonical", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load canonical helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5793X1CanonicalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_ascii_known_answer_and_no_trailing_newline(self):
        value = {"z": 1, "a": [True, None, "x"]}
        got = self.mod.canonical_json_bytes(value)
        self.assertEqual(got, b'{"a":[true,null,"x"],"z":1}')
        self.assertFalse(got.endswith(b"\n"))
        self.assertEqual(
            self.mod.sha256_bytes(got),
            hashlib.sha256(b'{"a":[true,null,"x"],"z":1}').hexdigest(),
        )

    def test_non_ascii_is_utf8_not_ascii_escape(self):
        got = self.mod.canonical_json_bytes({"label": "语义"})
        self.assertIn("语义".encode("utf-8"), got)
        self.assertNotIn(b"\\u", got)

    def test_nan_and_infinity_rejected(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                self.mod.canonical_json_bytes({"value": value})

    def test_domain_version_and_projection_change_digest(self):
        value = [{"path": "a", "sha256": "0" * 64}]
        base = self.mod.canonical_digest(
            value, domain="rtdl.goal5793.x1.rows", version=1, projection="full"
        )
        changed = [
            self.mod.canonical_digest(
                value, domain="rtdl.goal5793.x1.other", version=1, projection="full"
            ),
            self.mod.canonical_digest(
                value, domain="rtdl.goal5793.x1.rows", version=2, projection="full"
            ),
            self.mod.canonical_digest(
                value, domain="rtdl.goal5793.x1.rows", version=1, projection="identity"
            ),
        ]
        self.assertTrue(all(row["sha256"] != base["sha256"] for row in changed))

    def test_projection_is_explicit_and_order_preserved(self):
        rows = [{"path": "b", "bytes": 2}, {"path": "a", "bytes": 1}]
        got = self.mod.project_rows(rows, lambda row: {"path": row["path"]})
        self.assertEqual(got, [{"path": "b"}, {"path": "a"}])
        self.assertNotEqual(
            self.mod.canonical_digest(
                got, domain="rtdl.goal5793.x1.rows", version=1, projection="path"
            )["sha256"],
            self.mod.canonical_digest(
                list(reversed(got)),
                domain="rtdl.goal5793.x1.rows",
                version=1,
                projection="path",
            )["sha256"],
        )

    def test_bool_is_not_plain_integer_version(self):
        with self.assertRaises(ValueError):
            self.mod.canonical_digest({}, domain="d", version=True, projection="p")

    def test_seal_removes_only_named_field(self):
        document = {"schema": "x", "seal": "ignored", "other": "retained"}
        got = self.mod.seal_document(
            document, seal_field="seal", domain="rtdl.goal5793.x1.test", version=1
        )
        changed = dict(document, other="changed")
        self.assertNotEqual(
            got,
            self.mod.seal_document(
                changed, seal_field="seal", domain="rtdl.goal5793.x1.test", version=1
            ),
        )


if __name__ == "__main__":
    unittest.main()
