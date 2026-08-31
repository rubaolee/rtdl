from __future__ import annotations

import ctypes
from dataclasses import FrozenInstanceError
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from rtdsl import physical_execution_provenance as provenance


_PROGRAM = "v4_builtin_triangle_checked_reduction_composed"
_SEMANTIC = "1" * 64
_OUTPUT = "2" * 64


class _Symbol:
    def __init__(self, callback=None):
        self.callback = callback
        self.argtypes = None
        self.restype = None
        self.calls = 0

    def __call__(self, *args):
        self.calls += 1
        if self.callback is None:
            return 0
        return self.callback(*args)


def _library(snapshot_overrides=None):
    overrides = dict(snapshot_overrides or {})

    def finish(nonce_hi, nonce_lo, pointer, _error, _capacity):
        snapshot = ctypes.cast(
            pointer,
            ctypes.POINTER(provenance._NativeTraversalAuditSnapshot),
        ).contents
        values = {
            "nonce_hi": int(nonce_hi),
            "nonce_lo": int(nonce_lo),
            "attempted_launch_count": 1,
            "successful_launch_count": 1,
            "failed_launch_count": 0,
            "complete_context_launch_count": 1,
            "incomplete_context_launch_count": 0,
            "context_bind_count": 1,
            "raygen_invocation_count": 32,
            "first_program_bundle_id": provenance.physical_program_bundle_id(
                _PROGRAM
            ),
            "last_program_bundle_id": provenance.physical_program_bundle_id(
                _PROGRAM
            ),
            "first_traversable": 17,
            "last_traversable": 17,
            "pending_context_at_finish": 0,
            "session_error": 0,
        }
        values.update(overrides)
        for name, value in values.items():
            setattr(snapshot, name, value)
        return 0

    return SimpleNamespace(
        rtdl_optix_traversal_audit_begin=_Symbol(),
        rtdl_optix_traversal_audit_finish=_Symbol(finish),
        rtdl_optix_traversal_audit_abort=_Symbol(),
    )


class DeferredTraversalEvidenceTest(unittest.TestCase):
    def _open(self, root: Path, library, nonce=(11, 29)):
        provider = root / "librtdl_optix.so"
        if not provider.exists():
            provider.write_bytes(b"goal5790-deferred-traversal-provider")
        return provenance.OptixTraversalAuditSession.open(
            library=library,
            library_path=provider,
            nonce=nonce,
        )

    def test_capture_is_immutable_and_performs_no_receipt_hash_or_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = self._open(root, _library())
            with mock.patch.object(
                provenance,
                "_stable_digest",
                side_effect=AssertionError("receipt digest entered capture"),
            ), mock.patch.object(
                provenance.json,
                "dumps",
                side_effect=AssertionError("receipt JSON entered capture"),
            ):
                captured = session.capture(
                    expected_program_bundles=(_PROGRAM,)
                )

            self.assertEqual(
                captured.physical_executor_classification,
                "optix_traversal_observed",
            )
            self.assertTrue(
                captured.expected_program_observed_at_receipt_edge
            )
            self.assertIsInstance(captured.native_snapshot_items, tuple)
            self.assertTrue(all(
                isinstance(item, tuple)
                for item in captured.native_snapshot_items
            ))
            with self.assertRaises(FrozenInstanceError):
                captured.nonce_hi = 99
            with self.assertRaisesRegex(RuntimeError, "not active"):
                session.capture(expected_program_bundles=(_PROGRAM,))

            receipt = captured.build_receipt(
                semantic_digest=_SEMANTIC,
                output_digest=_OUTPUT,
                route_identity="goal5790:test",
            )
            self.assertEqual(
                receipt["physical_executor_classification"],
                "optix_traversal_observed",
            )
            self.assertEqual(
                receipt["receipt_sha256"],
                provenance._stable_digest({
                    key: value
                    for key, value in receipt.items()
                    if key != "receipt_sha256"
                }),
            )

    def test_legacy_finish_matches_capture_then_build_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            library = _library()
            captured = self._open(root, library).capture(
                expected_program_bundles=(_PROGRAM,)
            )
            deferred = captured.build_receipt(
                semantic_digest=_SEMANTIC,
                output_digest=_OUTPUT,
                route_identity="goal5790:test",
            )
            legacy = self._open(root, library).finish(
                semantic_digest=_SEMANTIC,
                output_digest=_OUTPUT,
                route_identity="goal5790:test",
                expected_program_bundles=(_PROGRAM,),
            )
            self.assertEqual(legacy, deferred)

    def test_capture_classifies_invalid_native_and_program_edge_states(self):
        cases = (
            ({"session_error": 1}, "invalid_traversal_audit_session"),
            ({"pending_context_at_finish": 1},
             "invalid_traversal_audit_session"),
            ({"complete_context_launch_count": 0},
             "optix_launch_observed_without_bound_traversable_context"),
            ({"incomplete_context_launch_count": 1},
             "optix_traversal_observed_with_unbound_launches"),
            ({"first_program_bundle_id": 71,
              "last_program_bundle_id": 71},
             "optix_traversal_observed_but_expected_program_not_bound"),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, (overrides, expected) in enumerate(cases):
                with self.subTest(expected=expected):
                    captured = self._open(
                        root, _library(overrides), nonce=(101, index + 1)
                    ).capture(expected_program_bundles=(_PROGRAM,))
                    self.assertEqual(
                        captured.physical_executor_classification, expected
                    )

    def test_capture_rejects_wrong_native_nonce_and_closes_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = self._open(
                root, _library({"nonce_lo": 999}), nonce=(7, 8)
            )
            with self.assertRaisesRegex(RuntimeError, "wrong nonce"):
                session.capture(expected_program_bundles=(_PROGRAM,))
            with self.assertRaisesRegex(RuntimeError, "not active"):
                session.capture(expected_program_bundles=(_PROGRAM,))

    def test_build_receipt_validates_bindings_after_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            captured = self._open(
                Path(directory), _library()
            ).capture(expected_program_bundles=(_PROGRAM,))
        with self.assertRaisesRegex(ValueError, "semantic_digest"):
            captured.build_receipt(
                semantic_digest="bad",
                output_digest=_OUTPUT,
                route_identity="goal5790:test",
            )
        with self.assertRaisesRegex(ValueError, "route_identity"):
            captured.build_receipt(
                semantic_digest=_SEMANTIC,
                output_digest=_OUTPUT,
                route_identity="",
            )


if __name__ == "__main__":
    unittest.main()
