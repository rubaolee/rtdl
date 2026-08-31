from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py"


def _load_app():
    spec = importlib.util.spec_from_file_location("goal5776_xhd_app", APP)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5776XhdRealScaleInputTest(unittest.TestCase):
    def _packet(self, root: Path) -> None:
        values = {
            "sources_f32.npy": np.asarray([[0, 0, 0], [2, 0, 0]], dtype=np.float32),
            "targets_f32.npy": np.asarray([[0.5, 0, 0], [1, 0, 0]], dtype=np.float32),
            "expected_query_u32.npy": np.asarray([0, 1], dtype=np.uint32),
            "expected_candidate_u32.npy": np.asarray([0, 1], dtype=np.uint32),
            "expected_rank_u32.npy": np.asarray([1, 1], dtype=np.uint32),
            "expected_distance_sq_f32.npy": np.asarray([0.25, 1.0], dtype=np.float32),
        }
        members = {}
        for name, value in values.items():
            path = root / name
            np.save(path, value, allow_pickle=False)
            members[name] = {
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
                "dtype": str(value.dtype),
                "shape": list(value.shape),
            }
        (root / "MANIFEST.json").write_text(json.dumps({
            "schema": "rtdl.goal5776.xhd_real_scale_input.v1",
            "contract": {
                "initial_radius": 0.01,
                "maximum_distance": 0.32,
                "maximum_rounds": 6,
            },
            "members": members,
        }), encoding="utf-8")

    def test_loader_reconstructs_exact_witness_and_multiround_contract(self) -> None:
        app = _load_app()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._packet(root)
            packet = app.load_real_scale_v4_input(root)
        self.assertEqual(packet["sources"].shape, (2, 3))
        self.assertEqual(packet["targets"].shape, (2, 3))
        self.assertEqual(packet["expected"]["source_id"], 1)
        self.assertEqual(packet["expected"]["item_id"], 1)
        self.assertEqual(packet["expected"]["value"], 1.0)
        self.assertEqual(packet["initial_radius"], 0.01)
        self.assertEqual(packet["maximum_distance"], 0.32)
        self.assertEqual(packet["maximum_rounds"], 6)
        self.assertTrue(packet["route_independent_expected"])

    def test_loader_fails_closed_on_tail_mutation(self) -> None:
        app = _load_app()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._packet(root)
            path = root / "targets_f32.npy"
            payload = bytearray(path.read_bytes())
            payload[-1] ^= 1
            path.write_bytes(payload)
            with self.assertRaisesRegex(RuntimeError, "member mismatch"):
                app.load_real_scale_v4_input(root)


if __name__ == "__main__":
    unittest.main()
