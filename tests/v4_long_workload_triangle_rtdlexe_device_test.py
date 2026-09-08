from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock

from rtdsl.v4_rtdlexe import LoadedRTDLExecutable
from rtdsl import v4_rtdlexe as rtdlexe
from rtdsl import v4_triangle_reduction_device_runtime as runtime
from rtdsl.v4_triangle_reduction import ReducerAlgebra


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("ascii")).hexdigest()


class _Loaded:
    family = "builtin_triangle_reduction_v1"
    family_executable_identity_sha256 = _sha("family-executable")
    executable_identity_sha256 = _sha("executable")
    composed_ptx = "// verified triangle AOT PTX\n"

    def __init__(self, native_sha: str, *, mode: str = "weighted_hit_count"):
        callback = _sha("callback")
        effect = _sha("effect")
        schema = _sha("schema")
        target = _sha("target")
        abi = _sha("abi")
        contract = _sha("contract")
        declaration_contract = _sha("declaration-contract")
        composed = hashlib.sha256(self.composed_ptx.encode()).hexdigest()
        self.product_projection = {
            "family": self.family,
            "runtime": {"triangle_mode": mode},
            "provider_key": {
                "callback_ir_sha256": callback,
                "callback_abi_sha256": abi,
                "callback_abi_projection": {
                    "callback_effect_digest": effect,
                },
            },
            "target_toolchain": {
                "target_sha256": target,
                "native_library_sha256": native_sha,
            },
            "executable_identity": {
                "physical_schema_sha256": schema,
                "target_sha256": target,
                "abi_sha256": abi,
                "contract_sha256": contract,
                "native_library_sha256": native_sha,
                "composed_ptx_sha256": composed,
            },
            "protocol_contract_sha256": declaration_contract,
            "composed_ptx_sha256": composed,
        }
        self.descriptor_calls = []

    def _validate_native_provider_descriptor(self, library, *, identity_path):
        self.descriptor_calls.append((library, identity_path))


class TriangleRTDLExecutableDeviceTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.native = Path(self.temporary.name) / "librtdl_optix.so"
        self.native.write_bytes(b"exact native bytes")
        self.native_sha = hashlib.sha256(self.native.read_bytes()).hexdigest()
        self.library = object()
        self.symbols = (object(), object(), object(), None, None, None, None, None)

    def tearDown(self):
        self.temporary.cleanup()

    def _prepare(self, loaded):
        with mock.patch.object(
            rtdlexe, "_require_runtime_session_loaded_capability"
        ), mock.patch.object(runtime, "_configure", return_value=self.symbols):
            return runtime.VerifiedTriangleDeviceColumnCountExecutor._from_loaded_rtdlexe(
                loaded,
                library=self.library,
                native_library_path=self.native,
            )

    def test_weighted_family_artifact_builds_identity_bound_device_owner(self):
        loaded = _Loaded(self.native_sha)
        owner = self._prepare(loaded)
        projection = loaded.product_projection
        self.assertEqual(
            owner._reducer_algebra(), ReducerAlgebra.CHECKED_U64_PRODUCT_SUM)
        self.assertEqual(
            owner.callback_ir_sha256,
            projection["provider_key"]["callback_ir_sha256"],
        )
        self.assertEqual(owner.abi_sha256, projection["provider_key"]["callback_abi_sha256"])
        self.assertEqual(
            owner.contract_sha256,
            projection["executable_identity"]["contract_sha256"],
        )
        self.assertEqual(owner.target_identity_sha256,
                         projection["target_toolchain"]["target_sha256"])
        self.assertEqual(owner.composed_program_sha256,
                         projection["composed_ptx_sha256"])
        self.assertEqual(owner.native_library_sha256, self.native_sha)
        self.assertEqual(
            loaded.descriptor_calls,
            [(self.library, "triangle_device_columns.native_producer_descriptor")],
        )

    def test_all_hit_mode_is_not_silently_promoted_to_weighted(self):
        owner = self._prepare(_Loaded(self.native_sha, mode="all_hit_count"))
        self.assertEqual(owner._reducer_algebra(), ReducerAlgebra.CHECKED_U64_SUM)

    def test_forged_public_loaded_value_is_rejected_before_native_load(self):
        forged = LoadedRTDLExecutable(
            artifact_path=Path("artifact.rtdlexe"),
            authority_path=Path("authority.json"),
            authority_sha256=_sha("authority"),
            deployment_id="test-slot",
            trust_root_sha256=_sha("root"),
            trust_package_sha256=_sha("package"),
            artifact_sha256=_sha("artifact"),
            executable_identity_sha256=_sha("executable"),
            family="builtin_triangle_reduction_v1",
            composed_ptx="// forged",
            product_projection={},
            family_executable_identity_sha256=_sha("family"),
        )
        with self.assertRaisesRegex(Exception, "RX056_LOADED_CAPABILITY_INVALID"):
            runtime.VerifiedTriangleDeviceColumnCountExecutor._from_loaded_rtdlexe(
                forged, library=self.library, native_library_path=self.native)

    def test_legacy_artifact_and_wrong_family_fail_closed(self):
        legacy = _Loaded(self.native_sha)
        legacy.family_executable_identity_sha256 = None
        with self.assertRaisesRegex(ValueError, "family-bound"):
            self._prepare(legacy)
        wrong = _Loaded(self.native_sha)
        wrong.family = "custom_aabb_bounded_relation_v1"
        with self.assertRaisesRegex(ValueError, "triangle family"):
            self._prepare(wrong)

    def test_projection_or_native_identity_drift_fails_closed(self):
        drift = _Loaded(self.native_sha)
        drift.product_projection["executable_identity"]["abi_sha256"] = _sha("other")
        with self.assertRaisesRegex(RuntimeError, "identity chain drift"):
            self._prepare(drift)

        wrong_native = _Loaded(_sha("wrong-native"))
        with self.assertRaisesRegex(RuntimeError, "native bytes"):
            self._prepare(wrong_native)

    def test_loaded_public_method_rechecks_capability(self):
        forged = LoadedRTDLExecutable(
            artifact_path=Path("artifact.rtdlexe"),
            authority_path=Path("authority.json"),
            authority_sha256=_sha("authority"),
            deployment_id="test-slot",
            trust_root_sha256=_sha("root"),
            trust_package_sha256=_sha("package"),
            artifact_sha256=_sha("artifact"),
            executable_identity_sha256=_sha("executable"),
            family="builtin_triangle_reduction_v1",
            composed_ptx="// forged",
            product_projection={},
            family_executable_identity_sha256=_sha("family"),
        )
        with self.assertRaisesRegex(Exception, "RX056_LOADED_CAPABILITY_INVALID"):
            forged.prepare_triangle_device_columns(native_library_path=self.native)

    def test_loaded_public_method_transfers_explicit_provider_ownership(self):
        loaded = _Loaded(self.native_sha)
        provider = SimpleNamespace(
            _binding_library=self.library,
            native_library_path=self.native,
            closed=False,
        )

        def close_provider():
            provider.closed = True

        provider.close = mock.Mock(side_effect=close_provider)
        executor = SimpleNamespace()
        loaded.bind_provider = mock.Mock(return_value=provider)
        with mock.patch.object(
            rtdlexe, "_require_runtime_session_loaded_capability"
        ), mock.patch.object(
            runtime.VerifiedTriangleDeviceColumnCountExecutor,
            "_from_loaded_rtdlexe", return_value=executor,
        ) as construct:
            observed = LoadedRTDLExecutable.prepare_triangle_device_columns(
                loaded, native_library_path=self.native)
        self.assertIs(observed, executor)
        self.assertIs(executor._rtdlexe_provider, provider)
        loaded.bind_provider.assert_called_once_with(self.native)
        construct.assert_called_once_with(
            loaded,
            library=self.library,
            native_library_path=self.native,
        )
        provider.close.assert_not_called()

        owner = runtime.VerifiedTriangleDeviceColumnCountExecutor.__new__(
            runtime.VerifiedTriangleDeviceColumnCountExecutor)
        owner._closed = False
        owner._program_token = 0
        owner._rtdlexe_provider = provider
        owner.close()
        self.assertTrue(provider.closed)
        provider.close.assert_called_once_with()

    def test_loaded_public_method_closes_provider_after_constructor_failure(self):
        loaded = _Loaded(self.native_sha)
        provider = SimpleNamespace(
            _binding_library=self.library,
            native_library_path=self.native,
            closed=False,
            close=mock.Mock(),
        )
        loaded.bind_provider = mock.Mock(return_value=provider)
        with mock.patch.object(
            rtdlexe, "_require_runtime_session_loaded_capability"
        ), mock.patch.object(
            runtime.VerifiedTriangleDeviceColumnCountExecutor,
            "_from_loaded_rtdlexe", side_effect=RuntimeError("prepare failed"),
        ), self.assertRaisesRegex(RuntimeError, "prepare failed"):
            LoadedRTDLExecutable.prepare_triangle_device_columns(
                loaded, native_library_path=self.native)
        provider.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
