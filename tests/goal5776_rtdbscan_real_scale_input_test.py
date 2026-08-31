from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PREP = ROOT / "scripts/goal5776_prepare_rtdbscan_input.py"
APP = ROOT / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"
GROUPED = ROOT / "src/rtdsl/v4_radius_graph_grouped_lowering.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Goal5776RtDbscanRealScaleInputTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prep = _load("goal5776_prepare_rtdbscan_test", PREP)
        cls.app = _load("goal5776_rtdbscan_v4_test", APP)

    def test_v4_app_explicitly_zero_lifts_nx2_input(self):
        points = np.asarray(((1.0, 2.0), (-3.0, 4.5)), dtype=np.float32)
        actual = self.app._canonicalize_spatial_points_3d(points)
        np.testing.assert_array_equal(
            actual,
            np.asarray(((1.0, 2.0, 0.0), (-3.0, 4.5, 0.0)),
                       dtype=np.float32),
        )
        self.assertTrue(actual.flags.c_contiguous)
        with self.assertRaisesRegex(ValueError, r"\[N,2\].*\[N,3\]"):
            self.app._canonicalize_spatial_points_3d(
                np.asarray(((1.0,), (2.0,)), dtype=np.float32))

    def test_oracle_is_route_independent_and_reaches_semantic_bound(self):
        text = PREP.read_text(encoding="utf-8")
        self.assertNotIn("rtdl3_action_migration", text)
        self.assertNotIn("v4_whole_app", text)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "packet"
            manifest = self.prep.prepare(
                output, seed=self.prep.DEFAULT_SEED)
            self.assertEqual(manifest["contract"]["point_count"], 4096)
            self.assertEqual(manifest["oracle"]["component_sizes"],
                             [1024, 1024, 1024, 1024])
            self.assertEqual(manifest["oracle"]["core_count"], 4095)
            self.assertGreater(manifest["oracle"]["directed_edge_count"],
                               2_000_000)
            self.assertTrue(manifest["oracle"]["route_independent"])

    def test_application_loader_rehashes_every_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "packet"
            self.prep.prepare(output, seed=self.prep.DEFAULT_SEED)
            loaded = self.app.load_real_scale_v4_input(output)
            self.assertEqual(loaded["points"].shape, (4096, 3))
            self.assertEqual(len(loaded["expected"]["core_flags"]), 4096)
            self.assertTrue(loaded["route_independent_expected"])
            path = output / "core_flags_u8.npy"
            path.write_bytes(path.read_bytes() + b"corrupt")
            with self.assertRaisesRegex(RuntimeError, "member mismatch"):
                self.app.load_real_scale_v4_input(output)

    def test_partition_contract_keeps_false_false_edges_out(self):
        # Two core components and one boundary point touching both.  The
        # boundary point deterministically selects the lower component root.
        adjacency = np.eye(9, dtype=np.bool_)
        adjacency[:4, :4] = True
        adjacency[4:8, 4:8] = True
        adjacency[3, 8] = adjacency[8, 3] = True
        adjacency[5, 8] = adjacency[8, 5] = True
        core, labels = self.prep.predicate_aware_partition(
            adjacency, min_points=4)
        self.assertEqual(core.tolist(), [True] * 8 + [False])
        self.assertEqual(labels.tolist(), [0, 0, 0, 0, 1, 1, 1, 1, 0])

    def test_real_scale_capacity_is_bound_before_launch(self):
        smoke = (ROOT / "scripts" /
                 "goal5776_home_rtdbscan_real_scale_smoke.py").read_text()
        self.assertIn(
            'maximum_event_capacity=int(len(data["points"])) ** 2',
            smoke)
        app = APP.read_text()
        self.assertIn("capacity=maximum_event_capacity", app)

    def test_optimized_lowering_is_callback_bound_and_app_neutral(self):
        text = GROUPED.read_text()
        lowered = text.lower()
        for forbidden in ("rt-dbscan", "rtdbscan", "paper-reproduction"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("consume_verified_multiround_spatial_executable", text)
        self.assertIn("callback.ir_sha256 != canonical.ir_sha256", text)
        self.assertIn("prepared_optix_grouped_union_numba_v1", text)
        app = APP.read_text()
        self.assertIn("prepare_verified_radius_graph_grouped_v4", app)


if __name__ == "__main__":
    unittest.main()
