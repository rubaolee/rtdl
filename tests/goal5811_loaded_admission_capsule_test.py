from __future__ import annotations

from dataclasses import replace
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from rtdsl import v4_rtdlexe as runtime


class LoadedAdmissionCapsuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _direct(self, marker: str = "trusted") -> runtime.LoadedRTDLExecutable:
        native_sha = hashlib.sha256(b"exact native").hexdigest()
        return runtime.LoadedRTDLExecutable(
            artifact_path=self.root / f"{marker}.rtdlexe",
            authority_path=self.root / f"{marker}.authority.json",
            authority_sha256="1" * 64,
            deployment_id=f"goal5811-{marker}",
            trust_root_sha256="2" * 64,
            trust_package_sha256="3" * 64,
            artifact_sha256="4" * 64,
            executable_identity_sha256="5" * 64,
            family=runtime._BOUNDED,
            composed_ptx=f"// {marker} exact PTX\n",
            product_projection={
                "target_toolchain": {
                    "native_library_sha256": native_sha,
                    "compute_capability": [8, 9],
                },
                "runtime": {
                    "native_abi": (
                        "rtdl.v4.prepared_bounded_relation_callback.v7"),
                    "capacity": 8,
                    "minimum_overlap_f32": 0.0,
                },
                "execution_schema": {
                    "native_producer_descriptor": {
                        "exact": "native-producer-v1",
                    },
                },
            },
        )

    def _loaded(self, marker: str = "trusted") \
            -> runtime.LoadedRTDLExecutable:
        return runtime._issue_loaded_runtime_session_capability(
            self._direct(marker))

    @staticmethod
    def _equivalent_distinct(value: object) -> object:
        if isinstance(value, Path):
            replacement = Path(str(value))
        elif isinstance(value, str):
            replacement = value.encode("utf-8").decode("utf-8")
        else:
            replacement = runtime._deep_freeze(runtime._plain(value))
        if replacement is value:
            raise AssertionError("test did not construct a distinct object")
        return replacement

    def test_revalidation_performs_no_canonicalization_digest_or_hash(self) \
            -> None:
        loaded = self._loaded()
        with mock.patch.object(
                runtime, "_canonical",
                side_effect=AssertionError("canonicalization on hot path")), \
                mock.patch.object(
                    runtime, "_digest",
                    side_effect=AssertionError("digest on hot path")), \
                mock.patch.object(
                    runtime, "_sha_bytes",
                    side_effect=AssertionError("hash on hot path")):
            for _ in range(1000):
                runtime._require_runtime_session_loaded_capability(
                    loaded, identity_path="test.loaded")

    def test_every_captured_field_replacement_is_rejected(self) -> None:
        for field_name in (
                "artifact_path", "authority_path", "authority_sha256",
                "deployment_id", "trust_root_sha256",
                "trust_package_sha256", "artifact_sha256",
                "executable_identity_sha256", "family", "composed_ptx",
                "product_projection"):
            with self.subTest(field_name=field_name):
                loaded = self._loaded(field_name)
                replacement = self._equivalent_distinct(
                    getattr(loaded, field_name))
                object.__setattr__(loaded, field_name, replacement)
                with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                    runtime._require_runtime_session_loaded_capability(
                        loaded, identity_path="test.loaded")
                self.assertEqual(
                    rejected.exception.code,
                    "RX056_LOADED_CAPABILITY_INVALID")

    def test_capsule_cannot_transfer_to_direct_or_replaced_object(self) -> None:
        trusted = self._loaded()
        forged = self._direct("forged")
        object.__setattr__(
            forged, "_token", runtime._LOADED_EXECUTABLE_CAPABILITY_TOKEN)
        object.__setattr__(
            forged, "_runtime_session_snapshot_seal",
            trusted._runtime_session_snapshot_seal)
        replaced = replace(
            trusted, composed_ptx="// replacement-selected PTX\n")

        for value in (forged, replaced):
            with self.subTest(kind=value.deployment_id):
                with self.assertRaises(runtime.RTDLExecutableError) as rejected:
                    runtime._require_runtime_session_loaded_capability(
                        value, identity_path="test.loaded")
                self.assertEqual(
                    rejected.exception.code,
                    "RX056_LOADED_CAPABILITY_INVALID")

    def test_capsule_payload_and_projection_are_immutable(self) -> None:
        loaded = self._loaded()
        capsule = loaded._runtime_session_snapshot_seal
        self.assertIsInstance(
            capsule, runtime._LoadedRuntimeSessionAdmissionCapsule)
        with self.assertRaises(AttributeError):
            object.__setattr__(capsule, "_payload", ())
        with self.assertRaises(TypeError):
            capsule[1] = self.root / "replacement.rtdlexe"
        with self.assertRaises(TypeError):
            loaded.product_projection["runtime"]["capacity"] = 999


if __name__ == "__main__":
    unittest.main()
