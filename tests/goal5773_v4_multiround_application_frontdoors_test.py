from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class _Owner:
    def __init__(self):
        self.count = 0
        self.closed = False

    @property
    def lifecycle_receipt(self):
        return {
            "schema": "rtdl.v4.prepared_application_lifecycle.v1",
            "execution_count": self.count,
            "prepare_seconds_reported_separately": True,
            "cold_result_replaced": False,
        }

    def close(self):
        if self.closed:
            raise RuntimeError("closed")
        self.closed = True


class Goal5773MultiRoundApplicationFrontdoorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rtnn = _load(
            "goal5773_rtnn_v4",
            "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py")
        cls.dbscan = _load(
            "goal5773_dbscan_v4",
            "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py")
        cls.xhd = _load(
            "goal5773_xhd_v4",
            "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py")

    def test_cold_and_prepared_frontdoors_coexist(self):
        for module in (self.rtnn, self.dbscan, self.xhd):
            self.assertTrue(callable(module.run_v4_complete))
            self.assertTrue(callable(module.prepare_v4))
            source = Path(module.__file__).read_text(encoding="utf-8")
            self.assertIn("prepare_is_free\": False", source)
            self.assertIn("cold_result_replaced\": False", source)

    def test_rtnn_reuses_owner_across_distinct_query_batches(self):
        owner = _Owner()
        search = np.asarray([[0, 0, 0], [1, 0, 0]], dtype=np.float32)
        app = SimpleNamespace(
            _expected_for_points=lambda _s, q, **_kwargs:
                tuple((index, 0, 1, float(index)) for index in range(len(q))))
        prepared = self.rtnn.PreparedRtnnV4(owner, search, app, 2.5)

        def execute(_owner, queries, _request):
            owner.count += 1
            value = tuple(
                (index, 0, 1, float(index)) for index in range(len(queries)))
            return SimpleNamespace(
                value=value, traversal_receipt={"physical_executor_classification":
                                                 "optix_traversal_observed"},
                native_library_sha256="a" * 64)

        with mock.patch.object(self.rtnn, "execute_ranked_distance_window", execute):
            first = prepared.execute([[0, 0, 0]])
            second = prepared.execute([[1, 0, 0], [0, 0, 0]])
        self.assertTrue(first["matched"] and second["matched"])
        self.assertNotEqual(first["input_sha256"], second["input_sha256"])
        self.assertEqual(owner.count, 2)
        self.assertEqual(first["reported_total_prepare_seconds"], 2.5)

    def test_dbscan_reuses_owner_across_distinct_parameters(self):
        owner = _Owner()
        points = np.asarray([[0, 0, 0], [1, 0, 0]], dtype=np.float32)

        def expected(_points, *, epsilon, min_points):
            marker = int(round(epsilon * 100)) + min_points
            return {
                "canonical_component_labels": (marker, marker),
                "core_flags": (True, False),
            }

        app = SimpleNamespace(_expected_from_points=expected)
        prepared = self.dbscan.PreparedRtDbscanV4(owner, points, app, 3.0)

        def execute(_owner, request):
            owner.count += 1
            value = expected(
                points, epsilon=request.epsilon, min_points=request.min_points)
            return SimpleNamespace(
                value=value, traversal_receipt={"physical_executor_classification":
                                                 "optix_traversal_observed"},
                native_library_sha256="b" * 64)

        with mock.patch.object(self.dbscan, "execute_radius_graph_components", execute):
            first = prepared.execute(epsilon=0.25, min_points=3)
            second = prepared.execute(epsilon=0.5, min_points=4)
        self.assertTrue(first["matched"] and second["matched"])
        self.assertNotEqual(first["input_sha256"], second["input_sha256"])
        self.assertEqual(owner.count, 2)

    def test_xhd_reuses_owner_across_distinct_source_sets(self):
        owner = _Owner()
        targets = np.asarray([[0, 0, 0], [2, 0, 0]], dtype=np.float32)
        prepared = self.xhd.PreparedXhdV4(owner, targets, 4.0, 32.0)

        def execute(_owner, sources, _request):
            owner.count += 1
            rows = []
            for query_id, source in enumerate(sources):
                candidates = []
                for item_id, target in enumerate(targets):
                    delta = np.subtract(source, target, dtype=np.float32)
                    d2 = float(np.sum(np.multiply(delta, delta, dtype=np.float32),
                                      dtype=np.float32))
                    candidates.append((d2, item_id))
                d2, item_id = min(candidates)
                rows.append((query_id, item_id, 1, d2))
            return SimpleNamespace(
                value=tuple(rows), traversal_receipt={
                    "physical_executor_classification": "optix_traversal_observed"},
                native_library_sha256="c" * 64)

        with mock.patch.object(self.xhd, "execute_ranked_distance_window", execute):
            first = prepared.execute([[0, 0, 0]])
            second = prepared.execute([[1, 0, 0], [2, 0, 0]])
        self.assertTrue(first["matched"] and second["matched"])
        self.assertNotEqual(first["input_sha256"], second["input_sha256"])
        self.assertEqual(owner.count, 2)


if __name__ == "__main__":
    unittest.main()
