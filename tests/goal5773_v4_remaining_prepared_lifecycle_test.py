from __future__ import annotations

import os
import pickle
from pathlib import Path
import threading
import unittest

from rtdsl import v4_bounded_relation_prepared_runtime as bounded
from rtdsl import v4_triangle_prepared_runtime as builtin_triangle
from rtdsl import v4_triangle_reduction_prepared_runtime as triangle_reduction
from rtdsl import v4_grouped_event_reduction as grouped


class _Destroy:
    def __init__(self):
        self.tokens = []

    def __call__(self, token, _error, _capacity):
        self.tokens.append(int(getattr(token, "value", token)))
        return 0


class Goal5773RemainingPreparedLifecycleTest(unittest.TestCase):
    RUNTIME_OWNERS = (
        (builtin_triangle.PreparedBuiltinTriangleOwner,
         "prepared built-in triangle owner"),
        (bounded.PreparedBoundedRelationOwner,
         "prepared bounded relation owner"),
        (triangle_reduction.PreparedTriangleReductionOwner,
         "prepared triangle owner"),
    )

    def _bare_owner(self, owner_type):
        owner = object.__new__(owner_type)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._token = 17
        owner._destroy = _Destroy()
        return owner

    def test_all_native_owners_fail_closed_on_serialization_thread_and_reentry(self):
        for owner_type, label in self.RUNTIME_OWNERS:
            with self.subTest(owner=owner_type.__name__):
                owner = self._bare_owner(owner_type)
                with self.assertRaisesRegex(RuntimeError, "cannot be serialized"):
                    pickle.dumps(owner)
                errors = []

                def cross_thread():
                    try:
                        owner._check()
                    except Exception as error:
                        errors.append(str(error))

                thread = threading.Thread(target=cross_thread)
                thread.start(); thread.join()
                self.assertEqual(errors, [f"{label} crossed thread boundary"])
                owner._active.acquire()
                try:
                    with self.assertRaisesRegex(RuntimeError, "during execution"):
                        owner.close()
                finally:
                    owner._active.release()
                owner.close()
                self.assertEqual(owner._destroy.tokens, [17])
                with self.assertRaisesRegex(RuntimeError, "is closed"):
                    owner._check()

    def test_grouped_owner_has_the_same_ownership_guards(self):
        owner = object.__new__(grouped.PreparedGroupedEventReductionOwner)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        with self.assertRaisesRegex(RuntimeError, "cannot be serialized"):
            pickle.dumps(owner)
        owner._active.acquire()
        try:
            with self.assertRaisesRegex(RuntimeError, "during execution"):
                owner.close()
        finally:
            owner._active.release()
        owner.close()
        with self.assertRaisesRegex(RuntimeError, "is closed"):
            owner._check()

    def test_generic_native_abis_and_owners_are_present(self):
        root = Path(__file__).resolve().parents[1]
        api = (root / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8")
        core = (root / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text(
            encoding="utf-8")
        for stem in (
            "triangle_reduction_callback",
            "builtin_triangle_callback",
            "bounded_relation_callback",
        ):
            for operation in ("prepare", "execute_prepared", "destroy_prepared"):
                self.assertIn(f"rtdl_optix_v4_{operation}_{stem}_v1", api)
        for owner in (
            "V4PreparedTriangleReduction",
            "V4PreparedBuiltinTriangle",
            "V4PreparedBoundedRelation",
        ):
            self.assertIn(owner, core)

    def test_core_lifecycle_modules_have_no_application_dispatch(self):
        for module in (
            builtin_triangle, bounded, triangle_reduction, grouped,
        ):
            source = Path(module.__file__).read_text(encoding="utf-8").lower()
            if module is grouped:
                self.assertFalse(
                    grouped.product_source_has_forbidden_identity_dispatch(source))
                continue
            for forbidden in (
                "rtnn", "rt-dbscan", "x-hd", "triangle-counting",
                "rayjoin", "raydb", "librts", "barneshut", "particle-tracking",
            ):
                self.assertNotIn(forbidden, source, (module.__name__, forbidden))


if __name__ == "__main__":
    unittest.main()
