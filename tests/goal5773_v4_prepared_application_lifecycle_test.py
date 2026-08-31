from __future__ import annotations

import pickle
from pathlib import Path
import tempfile
import threading
import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from rtdsl import v4_multiround_spatial_optix_runtime as runtime


class _Symbol:
    def __init__(self, result=0):
        self.result = result
        self.calls = []

    def __call__(self, *args):
        self.calls.append(args)
        return self.result


class Goal5773PreparedApplicationLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        native = Path(self.temporary.name) / "librtdl_optix.so"
        native.write_bytes(b"exact-fake-native-for-lifecycle-contract")
        self.destroy = _Symbol()
        self.library = SimpleNamespace(
            _name=str(native),
            rtdl_optix_v4_prepare_multiround_spatial_callback_v1=_Symbol(),
            rtdl_optix_v4_execute_multiround_spatial_callback_v1=_Symbol(),
            rtdl_optix_v4_destroy_multiround_spatial_callback_v1=self.destroy,
        )
        self.owner = runtime.PreparedMultiRoundSpatialOwner(
            token=17,
            authority=SimpleNamespace(authority_nonce="authority-nonce"),
            search_points=np.asarray([[0.0, 1.0, 2.0]], dtype=np.float32),
            library=self.library,
            native_path=native,
            composed_ptx_sha256="a" * 64,
            initial_radius=0.5,
            prepare_seconds=0.125,
        )

    def tearDown(self):
        if not self.owner._closed:
            self.owner.close()
        self.temporary.cleanup()

    def test_receipt_binds_exact_owner_and_reports_prepare_separately(self):
        receipt = self.owner.lifecycle_receipt
        self.assertEqual(receipt["session_identity"], self.owner.session_identity)
        self.assertEqual(self.owner.prepare_seconds, 0.125)
        self.assertTrue(receipt["prepare_seconds_reported_separately"])
        self.assertFalse(receipt["cold_result_replaced"])
        self.assertTrue(receipt["process_bound"])
        self.assertTrue(receipt["thread_bound"])

    def test_owner_cannot_be_serialized(self):
        with self.assertRaisesRegex(RuntimeError, "cannot be serialized"):
            pickle.dumps(self.owner)

    def test_cross_thread_access_fails_closed(self):
        errors = []

        def access():
            try:
                _ = self.owner.session_identity
            except Exception as error:  # expected cross-thread rejection
                errors.append(str(error))

        thread = threading.Thread(target=access)
        thread.start()
        thread.join()
        self.assertEqual(errors, ["prepared spatial owner crossed thread boundary"])

    def test_reentrant_execution_fails_closed(self):
        self.owner._enter_execution()
        try:
            with self.assertRaisesRegex(RuntimeError, "already executing"):
                self.owner._enter_execution()
        finally:
            self.owner._leave_execution(completed=False)
        self.assertEqual(self.owner.execution_count, 0)

    def test_successful_execution_increments_once(self):
        sentinel = object()
        with mock.patch.object(
            runtime, "_execute_ranked_distance_window_unlocked",
            return_value=sentinel,
        ):
            result = runtime.execute_ranked_distance_window(
                self.owner, [[0.0, 0.0, 0.0]], SimpleNamespace())
        self.assertIs(result, sentinel)
        self.assertEqual(self.owner.execution_count, 1)

    def test_failed_execution_releases_guard_without_counting(self):
        with mock.patch.object(
            runtime, "_execute_radius_graph_components_unlocked",
            side_effect=ValueError("synthetic failure"),
        ):
            with self.assertRaisesRegex(ValueError, "synthetic failure"):
                runtime.execute_radius_graph_components(
                    self.owner, SimpleNamespace())
        self.assertEqual(self.owner.execution_count, 0)
        with self.assertRaisesRegex(RuntimeError, "is poisoned"):
            self.owner._enter_execution()

    def test_close_invalidates_owner_and_calls_exact_destroy(self):
        self.owner.close()
        self.assertEqual(len(self.destroy.calls), 1)
        self.assertEqual(self.owner._token, 0)
        with self.assertRaisesRegex(RuntimeError, "is closed"):
            _ = self.owner.session_identity

    def test_cumulative_native_telemetry_is_reconciled_per_call(self):
        first = runtime._telemetry(
            self.owner,
            (1, 2, 3, 101, 101, 2, 0, 0),
            (0.5, 1.0, 2.0),
        )
        self.assertEqual((first.gas_refit_count, first.launch_count), (2, 3))
        second = runtime._telemetry(
            self.owner,
            (1, 5, 6, 101, 101, 5, 0, 0),
            (0.5, 1.0, 2.0),
        )
        self.assertEqual((second.gas_refit_count, second.launch_count), (3, 3))
        self.assertEqual(self.owner._cumulative_launch_count, 6)

    def test_cumulative_telemetry_regression_fails_closed(self):
        runtime._telemetry(
            self.owner, (1, 0, 1, 101, 101, 0, 0, 0), (0.5,))
        with self.assertRaisesRegex(RuntimeError, "telemetry regressed"):
            runtime._telemetry(
                self.owner, (1, 0, 0, 101, 101, 0, 0, 0), (0.5,))

    def test_core_has_no_application_identity_dispatch(self):
        source = Path(runtime.__file__).read_text(encoding="utf-8").lower()
        for forbidden in (
            "rtnn", "rt-dbscan", "x-hd", "triangle-counting",
            "rayjoin", "raydb", "librts", "barneshut", "particle-tracking",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
