from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

import numpy as np

from rtdsl import optix_runtime
from rtdsl import physical_execution_provenance as provenance
from rtdsl import v4_multiround_spatial_optix_runtime as multiround


class _Symbol:
    def __init__(self, mode: str = "plain") -> None:
        self.mode = mode
        self.calls = 0
        self.argtypes = None
        self.restype = None

    def __call__(self, *args):
        self.calls += 1
        if self.mode == "finish":
            snapshot = args[2]._obj
            snapshot.nonce_hi = int(args[0])
            snapshot.nonce_lo = int(args[1])
            snapshot.attempted_launch_count = 1
            snapshot.successful_launch_count = 1
            snapshot.complete_context_launch_count = 1
            snapshot.context_bind_count = 1
            snapshot.raygen_invocation_count = 1
            snapshot.first_program_bundle_id = 11
            snapshot.last_program_bundle_id = 11
            snapshot.first_traversable = 17
            snapshot.last_traversable = 17
        return 0


def _audit_library(path: Path):
    return SimpleNamespace(
        _rtdl_library_path=str(path),
        rtdl_optix_traversal_audit_begin=_Symbol(),
        rtdl_optix_traversal_audit_finish=_Symbol("finish"),
        rtdl_optix_traversal_audit_abort=_Symbol(),
    )


class Goal5775LoadedProviderIdentityTest(unittest.TestCase):
    def test_audit_hashes_external_handle_once_but_receipts_stay_fresh(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "librtdl_optix.so"
            original = b"loaded-provider-v1"
            path.write_bytes(original)
            library = _audit_library(path)
            expected = hashlib.sha256(original).hexdigest()
            real_sha = provenance._sha256
            with mock.patch.object(
                provenance, "_sha256", wraps=real_sha
            ) as sha_call:
                first = provenance.OptixTraversalAuditSession.open(
                    library=library, nonce=(1, 2)
                ).finish(
                    semantic_digest="1" * 64,
                    output_digest="2" * 64,
                    route_identity="test:first",
                )
                path.write_bytes(b"path-mutated-after-handle-load")
                second = provenance.OptixTraversalAuditSession.open(
                    library=library, nonce=(3, 4)
                ).finish(
                    semantic_digest="3" * 64,
                    output_digest="4" * 64,
                    route_identity="test:second",
                )
            self.assertEqual(sha_call.call_count, 1)
            self.assertEqual(first["provider_library_sha256"], expected)
            self.assertEqual(second["provider_library_sha256"], expected)
            self.assertNotEqual(first["nonce"], second["nonce"])
            self.assertNotEqual(first["receipt_sha256"], second["receipt_sha256"])

    def test_malformed_cached_digest_fails_before_native_begin(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "librtdl_optix.so"
            path.write_bytes(b"provider")
            library = _audit_library(path)
            library._rtdl_loaded_library_path = str(path.resolve())
            library._rtdl_loaded_library_sha256 = "not-a-sha"
            with self.assertRaisesRegex(RuntimeError, "SHA-256 is malformed"):
                provenance.OptixTraversalAuditSession.open(library=library)
            self.assertEqual(library.rtdl_optix_traversal_audit_begin.calls, 0)

    def test_cached_identity_cannot_cross_library_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "one.so"
            second = Path(temporary) / "two.so"
            first.write_bytes(b"one")
            second.write_bytes(b"two")
            library = _audit_library(second)
            library._rtdl_loaded_library_path = str(first.resolve())
            library._rtdl_loaded_library_sha256 = hashlib.sha256(b"one").hexdigest()
            with self.assertRaisesRegex(RuntimeError, "different library path"):
                provenance.OptixTraversalAuditSession.open(library=library)

    def test_public_handle_attributes_cannot_mutate_registered_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "librtdl_optix.so"
            payload = b"loaded-provider"
            path.write_bytes(payload)
            library = _audit_library(path)
            expected = provenance._register_loaded_provider_identity(
                library, path, hashlib.sha256(payload).hexdigest()
            )
            library._rtdl_loaded_library_sha256 = "f" * 64
            session = provenance.OptixTraversalAuditSession.open(
                library=library, nonce=(9, 10)
            )
            receipt = session.finish(
                semantic_digest="5" * 64,
                output_digest="6" * 64,
                route_identity="test:immutable-private-identity",
            )
            self.assertEqual(receipt["provider_library_sha256"], expected)

    def test_rtdl_loader_freezes_digest_on_handle(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "librtdl_optix.so"
            payload = b"provider-loaded-by-rtdl"
            path.write_bytes(payload)
            library = SimpleNamespace()
            optix_runtime._load_optix_library.cache_clear()
            try:
                with mock.patch.object(
                    optix_runtime, "_ensure_cuda_driver_initialized"
                ), mock.patch.object(
                    optix_runtime, "_find_optix_library", return_value=path
                ), mock.patch.object(
                    optix_runtime.ctypes, "CDLL", return_value=library
                ), mock.patch.object(optix_runtime, "_register_argtypes"):
                    loaded = optix_runtime._load_optix_library()
                self.assertIs(loaded, library)
                self.assertEqual(
                    loaded._rtdl_loaded_library_sha256,
                    hashlib.sha256(payload).hexdigest(),
                )
                self.assertEqual(
                    Path(loaded._rtdl_loaded_library_path), path.resolve()
                )
            finally:
                optix_runtime._load_optix_library.cache_clear()

    def test_multiround_owner_reuses_preverified_sha_without_provider_file(self):
        expected = "a" * 64
        owner = multiround.PreparedMultiRoundSpatialOwner(
            token=7,
            authority=SimpleNamespace(authority_nonce="authority"),
            search_points=np.asarray([[0.0, 0.0, 0.0]], dtype=np.float32),
            library=SimpleNamespace(),
            native_path=Path("provider-does-not-need-to-be-reread.so"),
            composed_ptx_sha256="b" * 64,
            initial_radius=1.0,
            prepare_seconds=0.5,
            native_sha256=expected,
        )
        try:
            self.assertEqual(
                owner.lifecycle_receipt["native_library_sha256"], expected
            )
            self.assertEqual(owner._native_sha256, expected)
        finally:
            owner._closed = True


if __name__ == "__main__":
    unittest.main()
