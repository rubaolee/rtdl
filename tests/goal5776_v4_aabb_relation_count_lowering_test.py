import os
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from rtdsl.aabb_index import OptixAabbIndex2D
from rtdsl.v4_aabb_relation_count_lowering import (
    AabbCountAlgebra,
    PreparedVerifiedAabbRelationCountV4,
)


ROOT = Path(__file__).resolve().parents[1]
LOWERING = ROOT / "src/rtdsl/v4_aabb_relation_count_lowering.py"
APP = ROOT / "Paper-reproduction-apps/librts-paper/v4_whole_app.py"


class Goal5776AabbRelationCountLoweringTest(unittest.TestCase):
    def test_lowering_is_closed_app_neutral_and_true_optix(self):
        source = LOWERING.read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("librts", "parks", "paper app"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("compile_callback()", source)
        self.assertIn("verify_typed_physical_schema", source)
        self.assertIn("AabbCountAlgebra", source)
        self.assertIn("prepare_aabb_index_2d_columns", source)
        self.assertIn("def bind_queries", source)
        self.assertIn("def bind_query_columns", source)
        self.assertIn("count_prepared_queries", source)
        self.assertIn("OptixTraversalAuditSession", source)
        self.assertIn("arbitrary_user_reducer_allowed\": False", source)

    def test_app_has_no_cartesian_capacity_for_real_scale_count(self):
        source = APP.read_text(encoding="utf-8")
        self.assertIn("prepare_v4_real_scale_count", source)
        body = source[source.index("def prepare_v4_real_scale_count"):]
        self.assertNotIn("len(indexed_columns) *", body)

    def test_prepared_query_reuse_remains_app_neutral(self):
        source = LOWERING.read_text(encoding="utf-8")
        bind_body = source[source.index("def bind_queries"):source.index("def _guard")]
        self.assertIn("prepare_optix_aabb_point_queries_2d", bind_body)
        self.assertIn("prepare_optix_aabb_box_queries_2d", bind_body)
        for forbidden in ("librts", "parks", "paper"):
            self.assertNotIn(forbidden, bind_body.lower())

    def test_generic_index_checks_prepared_query_layout(self):
        class FakePrepared:
            def count_prepared_queries(self, queries, *, operation):
                self.call = (queries, operation)
                return 7

        native = FakePrepared()
        owner = OptixAabbIndex2D(
            boxes=(object(), object()), prepared=native, row_ids=(0, 1)
        )
        queries = SimpleNamespace(count=3, operation="point_contains")
        result = owner.count_prepared_queries(
            queries, operation="point_contains"
        )
        self.assertEqual(result["counts"], {"point_contains": 7})
        self.assertEqual(result["query_counts"]["point_queries"], 3)
        self.assertEqual(native.call, (queries, "point_contains"))
        with self.assertRaisesRegex(ValueError, "layout"):
            owner.count_prepared_queries(queries, operation="range_contains")

    def test_verified_owner_binds_one_matching_query_batch(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._prepared_queries = None
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.POINT_CONTAINS
        )
        prepared = SimpleNamespace(count=2, operation="point_contains")
        with mock.patch(
            "rtdsl.v4_aabb_relation_count_lowering.prepare_optix_aabb_point_queries_2d",
            return_value=prepared,
        ) as prepare:
            owner.bind_queries(point_queries=((0.0, 0.0), (1.0, 1.0)))
        prepare.assert_called_once()
        self.assertIs(owner._prepared_queries, prepared)
        with self.assertRaisesRegex(RuntimeError, "already bound"):
            owner.bind_queries(point_queries=((2.0, 2.0),))

    def test_verified_owner_binds_typed_columns_without_python_rows(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._prepared_queries = None
        owner._prepared_query_layout = None
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.RANGE_CONTAINS
        )
        prepared = SimpleNamespace(count=3, operation="range_contains")
        columns = {
            "min_x": np.asarray([0.0, 1.0, 2.0], dtype=np.float32),
            "min_y": np.asarray([0.0, 1.0, 2.0], dtype=np.float32),
            "max_x": np.asarray([0.5, 1.5, 2.5], dtype=np.float32),
            "max_y": np.asarray([0.5, 1.5, 2.5], dtype=np.float32),
        }
        with mock.patch(
            "rtdsl.v4_aabb_relation_count_lowering."
            "prepare_optix_aabb_box_query_columns_f32_2d",
            return_value=prepared,
        ) as prepare:
            owner.bind_query_columns(box_columns=columns)
        prepare.assert_called_once_with(
            min_x=columns["min_x"], min_y=columns["min_y"],
            max_x=columns["max_x"], max_y=columns["max_y"],
            enable_range_intersects=False,
        )
        self.assertIs(owner._prepared_queries, prepared)
        self.assertEqual(owner._prepared_query_layout, "typed_f32_columns")

    def test_typed_column_binding_rejects_algebra_mismatch(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._prepared_queries = None
        owner._prepared_query_layout = None
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.POINT_CONTAINS
        )
        with self.assertRaisesRegex(ValueError, "box query columns require"):
            owner.bind_query_columns(box_columns={})

    def test_typed_column_binding_rejects_extra_columns(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._prepared_queries = None
        owner._prepared_query_layout = None
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.POINT_CONTAINS
        )
        with self.assertRaisesRegex(ValueError, "exactly x and y"):
            owner.bind_query_columns(
                point_columns={"x": [0.0], "y": [0.0], "app_id": [1]}
            )

    def test_dynamic_query_validation_accepts_array_containers(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._prepared_queries = None
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.POINT_CONTAINS
        )
        with self.assertRaisesRegex(ValueError, "rejects box queries"):
            owner.execute_count(box_queries=np.asarray([[0.0, 0.0, 1.0, 1.0]]))

    def test_execute_uses_bound_compact_aabb_traversal_receipt(self):
        owner = object.__new__(PreparedVerifiedAabbRelationCountV4)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._authority = SimpleNamespace(
            algebra=AabbCountAlgebra.POINT_CONTAINS,
            authority_nonce="authority",
        )
        owner._prepared_queries = SimpleNamespace(count=3)
        owner._prepared = SimpleNamespace(
            count_prepared_queries=mock.Mock(return_value={
                "counts": {"point_contains": 7},
                "rt_core_accelerated": True,
            })
        )
        owner._library = object()
        owner._native_sha256 = "a" * 64
        owner._execution_count = 0
        receipt = object()
        audit = SimpleNamespace(
            finish_validated_compact=mock.Mock(return_value=receipt),
            abort=mock.Mock(),
        )
        with mock.patch(
            "rtdsl.v4_aabb_relation_count_lowering.OptixTraversalAuditSession.open",
            return_value=audit,
        ), mock.patch(
            "rtdsl.v4_aabb_relation_count_lowering."
            "validate_bound_compact_traversal_receipt",
            return_value=receipt,
        ) as validate:
            result = owner.execute_count()
        self.assertEqual(result["count"], 7)
        self.assertIs(result["traversal_receipt"], receipt)
        finish = audit.finish_validated_compact.call_args.kwargs
        self.assertEqual(finish["expected_program_bundle"], "aabb_index_count_2d")
        self.assertEqual(finish["expected_raygen_invocation_count"], 3)
        self.assertEqual(
            finish["output_digest"], validate.call_args.kwargs["output_digest"]
        )
        self.assertEqual(
            validate.call_args.kwargs["provider_library_sha256"], "a" * 64
        )
        self.assertEqual(owner._execution_count, 1)


if __name__ == "__main__":
    unittest.main()
