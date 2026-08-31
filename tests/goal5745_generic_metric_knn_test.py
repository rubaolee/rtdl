from __future__ import annotations

from pathlib import Path
import inspect
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.metric_knn import (  # noqa: E402
    MetricKnn3DKind,
    MetricKnn3DSpec,
    MetricKnnError,
    cpu_aabb_candidate_provider_3d,
    compile_metric_knn_3d,
    execute_metric_knn_physical_3d,
)


def _oracle(data: np.ndarray, queries: np.ndarray, *, metric: MetricKnn3DKind, k: int):
    data64 = np.asarray(data, dtype=np.float32).astype(np.float64)
    query64 = np.asarray(queries, dtype=np.float32).astype(np.float64)
    if metric is MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM:
        data64 = data64 / np.linalg.norm(data64, axis=1)[:, None]
        query64 = query64 / np.linalg.norm(query64, axis=1)[:, None]
    output = []
    for query in query64:
        rows = []
        for item_id, item in enumerate(data64):
            if metric is MetricKnn3DKind.EUCLIDEAN_FILTER_REFINE:
                distance = float(np.linalg.norm(query - item))
            elif metric is MetricKnn3DKind.L_INFINITY_FILTER_REFINE:
                distance = float(np.max(np.abs(query - item)))
            else:
                distance = float(1.0 - np.dot(query, item))
            rows.append((distance, item_id))
        output.append([item_id for _, item_id in sorted(rows)[:k]])
    return np.asarray(output, dtype=np.uint32)


class Goal5745GenericMetricKnnTest(unittest.TestCase):
    def test_compiled_production_frontdoor_has_no_opaque_provider_callback(self) -> None:
        from rtdsl.metric_knn import CompiledMetricKnn3D

        parameters = inspect.signature(CompiledMetricKnn3D.execute).parameters
        self.assertNotIn("candidate_provider", parameters)
        app_source = (
            ROOT / "Paper-reproduction-apps/arkade-paper/rtdl3_whole_app.py"
        ).read_text(encoding="utf-8")
        production = app_source[
            app_source.index("def run_v3(") : app_source.index(
                "def run_v3_reference_for_functional_validation("
            )
        ]
        self.assertNotIn("candidate_provider", production)

    def setUp(self) -> None:
        self.data = np.asarray(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 1.0, 0.0],
                [-1.0, 0.0, 0.0],
                [0.25, 0.25, 0.25],
            ],
            dtype=np.float32,
        )
        self.queries = np.asarray(
            [[0.9, 0.1, 0.0], [0.2, 0.3, 0.4]], dtype=np.float32
        )

    def _run(self, metric: MetricKnn3DKind):
        spec = MetricKnn3DSpec(
            metric=metric,
            data_count=len(self.data),
            query_count=len(self.queries),
            k=3,
            initial_geometric_radius=0.05,
            maximum_rounds=12,
            maximum_candidate_rows=len(self.data) * len(self.queries),
        )
        return execute_metric_knn_physical_3d(
            spec,
            self.data,
            self.queries,
            candidate_provider=cpu_aabb_candidate_provider_3d,
        )

    def test_linf_filter_refine_matches_independent_oracle(self) -> None:
        result = self._run(MetricKnn3DKind.L_INFINITY_FILTER_REFINE)
        np.testing.assert_array_equal(
            result["ordered_item_ids"],
            _oracle(
                self.data,
                self.queries,
                metric=MetricKnn3DKind.L_INFINITY_FILTER_REFINE,
                k=3,
            ),
        )
        self.assertFalse(result["metadata"]["opaque_callback_used"])
        self.assertGreater(result["metadata"]["completed_round_count"], 1)

    def test_cosine_monotone_transform_matches_independent_oracle(self) -> None:
        result = self._run(MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM)
        np.testing.assert_array_equal(
            result["ordered_item_ids"],
            _oracle(
                self.data,
                self.queries,
                metric=MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM,
                k=3,
            ),
        )
        self.assertEqual(
            result["metadata"]["metric"], "cosine_monotone_transform"
        )

    def test_zero_vector_fails_before_candidate_provider(self) -> None:
        called = False

        def provider(**_kwargs):
            nonlocal called
            called = True
            return {}

        spec = MetricKnn3DSpec(
            metric=MetricKnn3DKind.COSINE_MONOTONE_TRANSFORM,
            data_count=2,
            query_count=1,
            k=1,
            initial_geometric_radius=0.1,
            maximum_rounds=4,
            maximum_candidate_rows=2,
        )
        with self.assertRaisesRegex(ValueError, "zero or invalid vector"):
            execute_metric_knn_physical_3d(
                spec,
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[1.0, 0.0, 0.0]],
                candidate_provider=provider,
            )
        self.assertFalse(called)

    def test_incomplete_or_duplicate_candidate_provider_fails_closed(self) -> None:
        spec = MetricKnn3DSpec(
            metric=MetricKnn3DKind.L_INFINITY_FILTER_REFINE,
            data_count=2,
            query_count=1,
            k=1,
            initial_geometric_radius=1.0,
            maximum_rounds=1,
            maximum_candidate_rows=2,
        )
        with self.assertRaisesRegex(MetricKnnError, "complete coverage"):
            execute_metric_knn_physical_3d(
                spec,
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[0.0, 0.0, 0.0]],
                candidate_provider=lambda **_kwargs: {
                    "candidate_id_rows": (),
                    "complete_candidate_coverage": False,
                },
            )
        with self.assertRaisesRegex(MetricKnnError, "duplicate"):
            execute_metric_knn_physical_3d(
                spec,
                [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
                [[0.0, 0.0, 0.0]],
                candidate_provider=lambda **_kwargs: {
                    "candidate_id_rows": ((0, 0), (0, 0)),
                    "complete_candidate_coverage": True,
                    "overflowed": False,
                },
            )

    def test_core_contains_no_application_or_publication_dispatch(self) -> None:
        source = (ROOT / "src/rtdsl/metric_knn.py").read_text(encoding="utf-8").lower()
        for forbidden in ("ark" + "ade", "gow" + "alla", "x-" + "hd", "paper" + "_app"):
            self.assertNotIn(forbidden, source)

    def test_all_metric_semantics_resolve_to_one_canonical_provider_each(self) -> None:
        provider_ids = []
        for metric in MetricKnn3DKind:
            spec = MetricKnn3DSpec(
                metric=metric,
                data_count=6,
                query_count=2,
                k=3,
                initial_geometric_radius=0.05,
                maximum_rounds=12,
                maximum_candidate_rows=12,
            )
            program = compile_metric_knn_3d(
                spec,
                target_identity={"machine_class": "static_test"},
                memory_limit_bytes=1 << 30,
            )
            self.assertEqual(program.canonical_resolution["status"], "RESOLVED")
            self.assertFalse(program.canonical_resolution["candidate_executed"])
            self.assertTrue(
                program.canonical_resolution[
                    "behavioral_traversal_receipt_still_required"
                ]
            )
            provider_ids.append(
                program.canonical_resolution["provider_candidate_stable_id"]
            )
        self.assertEqual(len(set(provider_ids)), len(MetricKnn3DKind))


if __name__ == "__main__":
    unittest.main()
