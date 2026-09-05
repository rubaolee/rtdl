from __future__ import annotations

from dataclasses import dataclass
import gc
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from rtdsl.v4_bounded_relation_optix_compiler import (
    VerifiedBoundedRelationExecutable,
    _LIVE_EXECUTABLES,
    _register_live_executable,
    compile_verified_bounded_relation_executable,
    consume_verified_bounded_relation_executable,
    _compiler_source_identity,
)
from rtdsl.v4_executable_cache import (
    V4ExecutableCacheError,
    V4ExecutableCachePolicy,
    load_executable_cache_entry,
    materialize_executable_cache_manifest,
    store_executable_cache_entry,
)
from rtdsl.v4_callback_lifecycle import (
    ProtocolLifecycleError,
    V4Target,
    V4Toolchain,
    _NativeLibraryWarmup,
    _warm_exact_native_runtime,
)
from rtdsl.v4_family_route_adapters import _module_sha256


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


class Goal5846ExecutableCacheTest(unittest.TestCase):
    def test_compiler_source_identity_is_not_stale_cached(self):
        first = _sha("first")
        second = _sha("second")
        with patch(
            "rtdsl.v4_bounded_relation_optix_compiler._file_sha256",
            side_effect=[first] * 7 + [second] * 7,
        ) as digest_file:
            observed_first = _compiler_source_identity()
            observed_second = _compiler_source_identity()
        self.assertEqual(set(observed_first.values()), {first})
        self.assertEqual(set(observed_second.values()), {second})
        self.assertEqual(digest_file.call_count, 14)

    def test_content_addressed_round_trip_and_key_miss(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = V4ExecutableCachePolicy(Path(directory) / "cache")
            key = {"schema": "test.key.v1", "target": [8, 9]}
            payload = {"schema": "test.payload.v1", "ptx": ".version 8.0\n"}
            first = store_executable_cache_entry(policy, key, payload)
            second = store_executable_cache_entry(policy, key, payload)
            self.assertEqual(first, second)
            self.assertEqual(load_executable_cache_entry(policy, key), payload)
            self.assertIsNone(load_executable_cache_entry(
                policy, {"schema": "test.key.v1", "target": [8, 6]}
            ))

    def test_existing_different_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = V4ExecutableCachePolicy(Path(directory) / "cache")
            key = {"schema": "test.key.v1"}
            store_executable_cache_entry(policy, key, {"value": 1})
            with self.assertRaisesRegex(
                V4ExecutableCacheError, "refusing to replace"
            ):
                store_executable_cache_entry(policy, key, {"value": 2})

    def test_concurrent_identical_publication_never_replaces(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = V4ExecutableCachePolicy(Path(directory) / "cache")
            key = {"schema": "test.key.v1"}
            payload = {"value": 1}

            def win_race(source, destination):
                Path(destination).write_bytes(Path(source).read_bytes())
                raise FileExistsError(destination)

            with patch(
                "rtdsl.v4_executable_cache.os.link",
                side_effect=win_race,
            ):
                destination = store_executable_cache_entry(
                    policy, key, payload
                )
            self.assertTrue(destination.is_file())
            self.assertEqual(
                load_executable_cache_entry(policy, key), payload
            )

    def test_sealed_manifest_is_read_only_and_byte_exact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "cache"
            key = {"schema": "test.key.v1"}
            payload = {"value": 1}
            store_executable_cache_entry(
                V4ExecutableCachePolicy(root), key, payload
            )
            manifest = Path(directory) / "manifest.json"
            materialize_executable_cache_manifest(root, manifest)
            sealed = V4ExecutableCachePolicy(
                root,
                manifest,
                hashlib.sha256(manifest.read_bytes()).hexdigest(),
            )
            self.assertEqual(load_executable_cache_entry(sealed, key), payload)
            with self.assertRaisesRegex(V4ExecutableCacheError, "read-only"):
                store_executable_cache_entry(sealed, key, payload)
            artifact = next(root.glob("*/artifact.json"))
            document = json.loads(artifact.read_text(encoding="ascii"))
            document["payload"]["value"] = 2
            artifact.write_text(json.dumps(document), encoding="ascii")
            with self.assertRaisesRegex(
                V4ExecutableCacheError, "entry bytes differ"
            ):
                load_executable_cache_entry(sealed, key)

    def test_symlink_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            real = base / "real"
            real.mkdir()
            link = base / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(V4ExecutableCacheError, "symlink"):
                load_executable_cache_entry(
                    V4ExecutableCachePolicy(link), {"schema": "test.key.v1"}
                )

    def test_dangling_entry_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = V4ExecutableCachePolicy(Path(directory) / "cache")
            key = {"schema": "test.key.v1"}
            load_executable_cache_entry(policy, key)
            key_sha = hashlib.sha256(
                json.dumps(
                    key,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii")
            ).hexdigest()
            entry = policy.root / key_sha
            entry.mkdir()
            (entry / "artifact.json").symlink_to(entry / "absent.json")
            with self.assertRaisesRegex(V4ExecutableCacheError, "unsafe"):
                load_executable_cache_entry(policy, key)

    def test_provider_module_identity_is_rehashed_after_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "provider.py"
            path.write_bytes(b"first")
            with patch(
                "rtdsl.v4_family_route_adapters._MODULE_PATH", path
            ):
                first = _module_sha256()
                path.write_bytes(b"second")
                second = _module_sha256()
        self.assertNotEqual(first, second)

    def test_manifest_authority_must_be_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "required together"):
                V4ExecutableCachePolicy(
                    Path(directory), Path(directory) / "manifest.json"
                )

    def test_compiler_cache_hit_skips_all_code_generation(self):
        @dataclass(frozen=True)
        class Target:
            compute_capability: str

        @dataclass(frozen=True)
        class Physical:
            target: Target

        @dataclass(frozen=True)
        class Fresh:
            physical: Physical

        fresh = Fresh(Physical(Target("8.9")))
        cached = object()
        policy = V4ExecutableCachePolicy(Path("/tmp/rtdl-goal5846-test-cache"))
        with patch(
            "rtdsl.v4_bounded_relation_optix_compiler._fresh",
            return_value=fresh,
        ), patch(
            "rtdsl.v4_bounded_relation_optix_compiler._cache_key",
            return_value={"schema": "test.key.v1"},
        ), patch(
            "rtdsl.v4_bounded_relation_optix_compiler.load_executable_cache_entry",
            return_value={"schema": "cached"},
        ), patch(
            "rtdsl.v4_bounded_relation_optix_compiler._load_cached_executable",
            return_value=(cached, "cached-log"),
        ) as loader, patch(
            "rtdsl.v4_bounded_relation_optix_compiler._register_live_executable"
        ) as register, patch(
            "rtdsl.v4_bounded_relation_optix_compiler."
            "generate_bounded_relation_numba_leaf"
        ) as forbidden:
            observed = compile_verified_bounded_relation_executable(
                object(), object(), object(),
                any_hit_proof_authority=object(),
                compute_capability=(8, 9),
                optix_include="/opt/optix/include",
                cuda_include="/usr/local/cuda/include",
                expected_python_version="3.12.0",
                expected_numba_version="0.65.1",
                expected_numpy_version="2.4.4",
                executable_cache=policy,
            )
        self.assertEqual(observed, (cached, "cached-log"))
        loader.assert_called_once()
        register.assert_called_once()
        forbidden.assert_not_called()


class Goal5846NativeWarmupTest(unittest.TestCase):
    def test_native_source_exports_app_free_runtime_warmup(self):
        root = Path(__file__).resolve().parents[1]
        api = (root / "src/native/optix/rtdl_optix_api.cpp").read_text(
            encoding="utf-8-sig"
        )
        core = (root / "src/native/optix/rtdl_optix_core.cpp").read_text(
            encoding="utf-8"
        )
        self.assertIn("rtdl_optix_v4_warm_runtime_v1", api)
        self.assertIn("ScopedRtdlCudaContext context_guard", api)
        constructor = core.split("ScopedRtdlCudaContext() {", 1)[1].split(
            "~ScopedRtdlCudaContext", 1
        )[0]
        self.assertLess(
            constructor.index("std::call_once(g_optix_init_flag"),
            constructor.index("CU_CHECK(cuCtxGetCurrent(&prior_))"),
        )

    def test_narrow_native_warmup_abi_is_required(self):
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL039_NATIVE_WARMUP_ABI_MISSING"
        ):
            _warm_exact_native_runtime(SimpleNamespace())

    def test_native_warmup_error_fails_closed(self):
        def fail(error, _capacity):
            error.value = b"context creation failed"
            return 1

        warm = Mock(side_effect=fail)
        library = SimpleNamespace(rtdl_optix_v4_warm_runtime_v1=warm)
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL040_NATIVE_WARMUP_FAILED"
        ):
            _warm_exact_native_runtime(library)
        self.assertEqual(warm.call_count, 1)

    def test_background_warmup_loads_and_initializes_once(self):
        library = object()
        cuda = object()
        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
            return_value=library,
        ) as loader, patch(
            "rtdsl.v4_callback_lifecycle._warm_exact_native_runtime",
        ) as warm, patch(
            "rtdsl.v4_callback_lifecycle._initialize_v4_cuda_driver",
            return_value=cuda,
        ) as driver:
            operation = _NativeLibraryWarmup(object())
            self.assertIs(operation.finish(), library)
        loader.assert_called_once()
        driver.assert_called_once()
        warm.assert_called_once_with(library)

    def test_background_warmup_propagates_failure(self):
        failure = ProtocolLifecycleError("TEST", "warmup", "failed")
        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
            side_effect=failure,
        ), patch(
            "rtdsl.v4_callback_lifecycle._initialize_v4_cuda_driver",
            return_value=object(),
        ):
            operation = _NativeLibraryWarmup(object())
            with self.assertRaisesRegex(ProtocolLifecycleError, "TEST@warmup"):
                operation.finish()

    def test_background_driver_failure_is_not_hidden(self):
        failure = ProtocolLifecycleError("CUDA", "driver", "failed")
        with patch(
            "rtdsl.v4_callback_lifecycle._load_exact_native_library",
            return_value=object(),
        ), patch(
            "rtdsl.v4_callback_lifecycle._initialize_v4_cuda_driver",
            side_effect=failure,
        ):
            operation = _NativeLibraryWarmup(object())
            with self.assertRaisesRegex(ProtocolLifecycleError, "CUDA@driver"):
                operation.finish()

    def test_toolchain_prewarm_is_target_bound_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            native = root / "native.so"
            native.write_bytes(b"native")
            optix = root / "optix"
            cuda = root / "cuda"
            optix.mkdir()
            cuda.mkdir()
            target = V4Target.from_native(
                native, optix_sdk="9.0.0", compute_capability="8.9"
            )
            toolchain = V4Toolchain(
                compute_capability=(8, 9),
                optix_include=optix,
                cuda_include=cuda,
                expected_python_version="3.12.0",
                expected_numba_version="0.65.1",
                expected_numpy_version="2.4.4",
            )
            created = []

            def fake_init(instance, bound_target):
                instance._target = bound_target
                created.append(instance)

            with patch.object(
                _NativeLibraryWarmup, "__init__", fake_init
            ):
                warmed = toolchain.begin_native_initialization(target)
            fake = created[0]
            self.assertTrue(warmed.overlap_native_initialization)
            self.assertIs(warmed._native_library_warmup, fake)
            self.assertIs(warmed.begin_native_initialization(target), warmed)


@dataclass(frozen=True)
class _Callback:
    ir_sha256: str
    effect_digest: str


@dataclass(frozen=True)
class _Schema:
    schema_sha256: str


@dataclass(frozen=True)
class _Target:
    target_sha256: str


@dataclass(frozen=True)
class _Physical:
    callback: _Callback
    schema: _Schema
    target: _Target


@dataclass(frozen=True)
class _Authority:
    physical: _Physical
    schema: _Schema
    authority_nonce: str


@dataclass(frozen=True)
class _Contract:
    contract_sha256: str
    mode: str


@dataclass(frozen=True)
class _Abi:
    abi_sha256: str


@dataclass(frozen=True)
class _Proof:
    proof_sha256: str


@dataclass(frozen=True)
class _Wrapper:
    source: str


@dataclass(frozen=True)
class _Composed:
    ptx: str


@dataclass(frozen=True)
class _Generated:
    generated_source_sha256: str
    generated_source: str


@dataclass(frozen=True)
class _Compiled:
    ptx_sha256: str
    ptx: str


class Goal5846LiveExecutableSealTest(unittest.TestCase):
    def setUp(self):
        callback = _Callback(_sha("callback"), _sha("effect"))
        self.authority = _Authority(
            _Physical(callback, _Schema(_sha("physical")), _Target(_sha("target"))),
            _Schema(_sha("relation")),
            "nonce",
        )
        self.contract = _Contract(_sha("contract"), "bounded")
        self.abi = _Abi(_sha("abi"))
        self.proof = _Proof(_sha("proof"))
        source = "generated"
        leaf_ptx = ".version 8.0\n"
        wrapper_ptx = ".version 8.0\n// wrapper\n"
        composed_ptx = wrapper_ptx + leaf_ptx
        self.executable = VerifiedBoundedRelationExecutable(
            schema="test.executable.v1",
            authority_sha256=_sha("authority"),
            contract_sha256=self.contract.contract_sha256,
            abi_sha256=self.abi.abi_sha256,
            wrapper=_Wrapper("wrapper-source"),
            wrapper_ptx=wrapper_ptx,
            wrapper_ptx_sha256=_sha("wrapper-ptx"),
            generated_leaves=(_Generated(
                hashlib.sha256(source.encode()).hexdigest(), source
            ),),
            compiled_leaves=(_Compiled(
                hashlib.sha256(leaf_ptx.encode()).hexdigest(), leaf_ptx
            ),),
            inline_cuda_source_sha256=_sha("inline"),
            inline_cuda_leaf_sha256=(("role", _sha("leaf")),),
            composed=_Composed(composed_ptx),
            compiler_options=("--std=c++14",),
            nvrtc_log_sha256=_sha("log"),
            executable_sha256=_sha("executable"),
        )

    def tearDown(self):
        _LIVE_EXECUTABLES.pop(id(self.executable), None)

    def consume(self):
        return consume_verified_bounded_relation_executable(
            self.executable,
            self.authority,
            self.contract,
            self.abi,
            any_hit_proof_authority=self.proof,
        )

    def test_live_executable_consumes_exactly_once(self):
        _register_live_executable(
            self.executable, self.authority, self.contract, self.abi, self.proof
        )
        self.assertEqual(self.consume(), self.executable.composed.ptx)
        with self.assertRaisesRegex(RuntimeError, "forged, serialized, or consumed"):
            self.consume()

    def test_equal_rederived_authority_is_accepted(self):
        _register_live_executable(
            self.executable, self.authority, self.contract, self.abi, self.proof
        )
        rederived = _Authority(
            self.authority.physical,
            self.authority.schema,
            self.authority.authority_nonce,
        )
        observed = consume_verified_bounded_relation_executable(
            self.executable,
            rederived,
            self.contract,
            self.abi,
            any_hit_proof_authority=self.proof,
        )
        self.assertEqual(observed, self.executable.composed.ptx)

    def test_unhashed_contract_field_mutation_is_rejected(self):
        _register_live_executable(
            self.executable, self.authority, self.contract, self.abi, self.proof
        )
        object.__setattr__(self.contract, "mode", "mutated")
        with self.assertRaisesRegex(RuntimeError, "binding drift"):
            self.consume()
        with self.assertRaisesRegex(RuntimeError, "forged, serialized, or consumed"):
            self.consume()

    def test_dead_live_executable_registration_is_removed(self):
        executable = VerifiedBoundedRelationExecutable(**{
            name: getattr(self.executable, name)
            for name in VerifiedBoundedRelationExecutable.__dataclass_fields__
        })
        identity = id(executable)
        _register_live_executable(
            executable, self.authority, self.contract, self.abi, self.proof
        )
        self.assertIn(identity, _LIVE_EXECUTABLES)
        del executable
        gc.collect()
        self.assertNotIn(identity, _LIVE_EXECUTABLES)


if __name__ == "__main__":
    unittest.main()
