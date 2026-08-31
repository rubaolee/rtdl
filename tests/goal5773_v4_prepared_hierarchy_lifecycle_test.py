from __future__ import annotations

import pickle
from pathlib import Path
import threading
import unittest
from types import SimpleNamespace
from unittest import mock

from rtdsl import v4_hierarchy_frontier as hierarchy
from goal5764_m6_hierarchy_fixtures import hierarchy_coverage_fixture


class _Native:
    def __init__(self, plan):
        self._library = object()
        self.calls = []
        self.closed = False

    def execute(self, *, softening=0.0, canonical_output_binding=False):
        if not canonical_output_binding:
            raise AssertionError("V4 prepared hierarchy must request provider binding")
        self.calls.append(float(softening))
        return {"rows": (), "metadata": {}, "partial_result_returned": False}

    def close(self):
        self.closed = True


class _Audit:
    def finish(self, **kwargs):
        return {"audit": kwargs}

    def abort(self):
        raise AssertionError("unexpected audit abort")


class Goal5773PreparedHierarchyLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.compiled = SimpleNamespace(
            plan_sha256="a" * 64,
            spec_sha256="b" * 64,
            schema=SimpleNamespace(maximum_output_rows=3),
        )
        self.spec = object()
        plan = SimpleNamespace(
            selected_template=hierarchy.AGGREGATE_HIERARCHY_OPTIX_TEMPLATE)
        patches = (
            mock.patch.object(hierarchy, "_verify_compiled"),
            mock.patch.object(
                hierarchy,
                "_prepared_static_authority_payload",
                return_value=("test-static-authority",),
            ),
            mock.patch.object(
                hierarchy,
                "compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d",
                return_value=plan,
            ),
            mock.patch.object(
                hierarchy, "PreparedNativeAggregateHierarchy3D", _Native),
        )
        self.patchers = patches
        for patcher in patches:
            patcher.start()
        self.owner = hierarchy.PreparedHierarchyFrontierOwner(
            self.compiled, self.spec)

    def tearDown(self):
        if not self.owner._closed:
            self.owner.close()
        for patcher in reversed(self.patchers):
            patcher.stop()

    def test_receipt_binds_owner_and_reports_prepare_separately(self):
        receipt = self.owner.lifecycle_receipt
        self.assertEqual(receipt["plan_sha256"], "a" * 64)
        self.assertTrue(receipt["process_bound"])
        self.assertTrue(receipt["thread_bound"])
        self.assertTrue(receipt["nonserializable"])
        self.assertTrue(receipt["prepare_seconds_reported_separately"])
        self.assertFalse(receipt["cold_result_replaced"])

    def test_owner_cannot_be_serialized(self):
        with self.assertRaisesRegex(RuntimeError, "cannot be serialized"):
            pickle.dumps(self.owner)

    def test_cross_thread_access_fails_closed(self):
        errors = []

        def access():
            try:
                _ = self.owner.lifecycle_receipt
            except Exception as error:
                errors.append(str(error))

        thread = threading.Thread(target=access)
        thread.start()
        thread.join()
        self.assertEqual(
            errors, ["prepared hierarchy owner crossed thread boundary"])

    def test_reentrant_execute_fails_closed(self):
        self.owner._active.acquire()
        try:
            with self.assertRaisesRegex(RuntimeError, "already executing"):
                self.owner.execute()
        finally:
            self.owner._active.release()

    def test_two_calls_reuse_one_native_owner(self):
        sentinel = object()
        with mock.patch.object(
            hierarchy.OptixTraversalAuditSession, "open", return_value=_Audit()
        ), mock.patch.object(
            hierarchy, "_bind_canonical_packed_hierarchy_endpoint",
            return_value=SimpleNamespace(output_sha256="c" * 64),
        ), mock.patch.object(
            hierarchy, "_accept_hierarchy_endpoint", return_value=sentinel
        ):
            self.assertIs(self.owner.execute(softening=0.0), sentinel)
            self.assertIs(self.owner.execute(softening=0.125), sentinel)
        self.assertEqual(self.owner._native.calls, [0.0, 0.125])
        self.assertEqual(self.owner.lifecycle_receipt["execution_count"], 2)

    def test_close_invalidates_owner(self):
        native = self.owner._native
        self.owner.close()
        self.assertTrue(native.closed)
        with self.assertRaisesRegex(RuntimeError, "is closed"):
            _ = self.owner.lifecycle_receipt

    def test_core_has_no_application_dispatch(self):
        source = Path(hierarchy.__file__).read_text(encoding="utf-8").lower()
        for forbidden in (
            "rtnn", "rt-dbscan", "x-hd", "triangle-counting",
            "rayjoin", "raydb", "librts", "barneshut", "particle-tracking",
        ):
            self.assertNotIn(forbidden, source)

    def test_prepared_oracles_are_outside_registered_timer(self):
        root = Path(__file__).resolve().parents[1]
        files = (
            root / "Paper-reproduction-apps/rtnn-paper/v4_whole_app.py",
            root / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
            root / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py",
            root / "Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py",
        )
        for path in files:
            source = path.read_text(encoding="utf-8")
            prepared = source[source.index("class Prepared"):]
            elapsed = prepared.index("elapsed = time.perf_counter() - started")
            oracle_markers = [
                marker for marker in (
                    "expected = self.app._expected_for_points",
                    "expected_full = self.app._expected_from_points",
                    "expected = _expected_for",
                    "_reference_rows(",
                ) if marker in prepared
            ]
            self.assertEqual(len(oracle_markers), 1, path)
            self.assertGreater(prepared.index(oracle_markers[0]), elapsed, path)


class Goal5775PreparedHierarchyStaticAuthorityTest(unittest.TestCase):
    def _owner(self):
        spec, _coverage = hierarchy_coverage_fixture()
        raw = spec.prepared_hierarchy.hierarchy
        schema = hierarchy.HierarchyFrontierSchema(
            producer_contract_sha256="d" * 64,
            hierarchy_sha256=hierarchy.hierarchy_content_sha256(spec),
            reducer=hierarchy.HierarchyReducer.AGGREGATE_COUNT,
            maximum_output_rows=raw.point_count,
            maximum_visits_per_source=raw.node_count * 2 + 1,
        )
        compiled = hierarchy.compile_hierarchy_frontier(spec, schema)
        plan = SimpleNamespace(
            selected_template=hierarchy.AGGREGATE_HIERARCHY_OPTIX_TEMPLATE)
        with mock.patch.object(
            hierarchy, "PreparedNativeAggregateHierarchy3D", _Native
        ), mock.patch.object(
            hierarchy,
            "compile_aggregate_frontier_reduce_candidate_for_functional_validation_3d",
            return_value=plan,
        ):
            owner = hierarchy.PreparedHierarchyFrontierOwner(compiled, spec)
        return owner, compiled, spec

    def test_compiled_plan_replacement_fails_closed_without_rehash(self):
        owner, compiled, _spec = self._owner()
        original = compiled.plan_sha256
        try:
            object.__setattr__(compiled, "plan_sha256", "e" * 64)
            with self.assertRaisesRegex(
                hierarchy.HierarchyFrontierError, "prepared_static_authority"
            ):
                owner._check_static_authority()
        finally:
            object.__setattr__(compiled, "plan_sha256", original)
            owner.close()

    def test_hierarchy_column_replacement_fails_closed_without_content_hash(self):
        owner, _compiled, spec = self._owner()
        raw = spec.prepared_hierarchy.hierarchy
        original = raw.point_x
        try:
            object.__setattr__(raw, "point_x", tuple(list(original)))
            with self.assertRaisesRegex(
                hierarchy.HierarchyFrontierError, "prepared_static_authority"
            ):
                owner._check_static_authority()
        finally:
            object.__setattr__(raw, "point_x", original)
            owner.close()


if __name__ == "__main__":
    unittest.main()
