from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl import action_api  # noqa: E402


def _fast_runner(*, mutate=None):
    def run(command, **kwargs):
        request = json.loads(kwargs["input"])
        response = {
            "schema": action_api._FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_RESPONSE,
            "nonce": request["nonce"],
            "required_backends": ["optix"],
            "action_api_sha256": request["action_api_sha256"],
            "probe_child_sha256": request["probe_child_sha256"],
            "provider_library_sha256": request["provider_library_sha256"],
            "provider_version": [8, 0, 0],
            "target_profile": {
                "optix_available": True,
                "numba_available": False,
                "embree_available": False,
                "cpu_reference_available": request["cpu_reference_available"],
                "optix_max_inline_state_bytes": request[
                    "optix_max_inline_state_bytes"
                ],
                "numba_max_device_state_bytes": request[
                    "numba_max_device_state_bytes"
                ],
                "embree_max_host_state_bytes": request[
                    "embree_max_host_state_bytes"
                ],
                "max_output_bytes": request["max_output_bytes"],
                "profile_source": "runtime_capability_probe",
                "device_memory_limit_bytes": 8 << 30,
                "production_selection_policy": "compiler_owned_default",
            },
            "probe_process_pid": os.getpid() + 1,
            "parent_process_pid": os.getpid(),
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
            "nvidia_visible_devices": os.environ.get("NVIDIA_VISIBLE_DEVICES"),
        }
        if mutate is not None:
            mutate(response)
        response["response_sha256"] = action_api._canonical_sha256(response)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps(response, sort_keys=True),
            stderr="",
        )

    return run


class Goal5740FastForkCleanOptixTargetProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.native = Path(self.temporary.name) / "librtdl_optix.so"
        self.native.write_bytes(b"goal5740-fake-native")
        self.environment = patch.dict(
            os.environ,
            {"RTDL_OPTIX_LIB": str(self.native)},
            clear=False,
        )
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def probe(self, *, mutate=None):
        return action_api._detect_optix_target_profile_fork_clean_fast(
            cpu_reference_available=True,
            optix_max_inline_state_bytes=None,
            numba_max_device_state_bytes=None,
            embree_max_host_state_bytes=None,
            max_output_bytes=8,
            _runner=_fast_runner(mutate=mutate),
        )

    def test_valid_receipt_reconstructs_the_same_target_contract(self) -> None:
        target = self.probe()
        self.assertTrue(target.optix_available)
        self.assertFalse(target.numba_available)
        self.assertFalse(target.embree_available)
        self.assertEqual(8 << 30, target.device_memory_limit_bytes)
        self.assertEqual(8, target.max_output_bytes)
        self.assertEqual(
            "fork_clean_runtime_capability_probe", target.profile_source
        )

    def test_child_is_executed_by_path_without_importing_rtdsl(self) -> None:
        observed = {}

        def runner(command, **kwargs):
            observed["command"] = command
            return _fast_runner()(command, **kwargs)

        action_api._detect_optix_target_profile_fork_clean_fast(
            cpu_reference_available=True,
            optix_max_inline_state_bytes=None,
            numba_max_device_state_bytes=None,
            embree_max_host_state_bytes=None,
            max_output_bytes=None,
            _runner=runner,
        )
        command = observed["command"]
        self.assertEqual(2, len(command))
        self.assertEqual(Path(sys.executable), Path(command[0]))
        self.assertEqual(
            "_fork_clean_optix_target_probe_child.py", Path(command[1]).name
        )
        source = Path(command[1]).read_text(encoding="utf-8")
        self.assertNotIn("from rtdsl", source)
        self.assertNotIn("import rtdsl", source)
        self.assertNotIn("import numba", source)
        self.assertNotIn("import cupy", source)
        self.assertNotIn("optix_runtime", source)

    def test_source_native_nonce_parent_and_visibility_are_bound(self) -> None:
        mutations = (
            lambda response: response.__setitem__("nonce", "0" * 64),
            lambda response: response.__setitem__("probe_child_sha256", "0" * 64),
            lambda response: response.__setitem__(
                "provider_library_sha256", "0" * 64
            ),
            lambda response: response.__setitem__(
                "parent_process_pid", os.getpid() + 7
            ),
            lambda response: response.__setitem__(
                "cuda_visible_devices", "wrong-device"
            ),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_INVALID"):
                    self.probe(mutate=mutate)

    def test_false_optix_and_invalid_memory_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "TARGET_INVALID"):
            self.probe(
                mutate=lambda response: response["target_profile"].__setitem__(
                    "optix_available", False
                )
            )
        with self.assertRaisesRegex(ValueError, "TARGET_INVALID"):
            self.probe(
                mutate=lambda response: response["target_profile"].__setitem__(
                    "device_memory_limit_bytes", 0
                )
            )

    def test_limit_rebinding_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "LIMIT_BINDING_INVALID"):
            self.probe(
                mutate=lambda response: response["target_profile"].__setitem__(
                    "max_output_bytes", 16
                )
            )

    def test_production_optix_only_route_selects_fast_child(self) -> None:
        sentinel = object()
        with patch.object(
            action_api,
            "_detect_optix_target_profile_fork_clean_fast",
            return_value=sentinel,
        ) as fast:
            actual = action_api._detect_action_target_profile_for_required_backends_fork_clean(
                required_backends=("optix",),
                cpu_reference_available=True,
            )
        self.assertIs(sentinel, actual)
        fast.assert_called_once()

    def test_certified_nearest_does_not_use_fast_optix_only_probe(self) -> None:
        with patch.object(
            action_api,
            "_detect_optix_target_profile_fork_clean_fast",
            side_effect=AssertionError("fast path must not handle certified-nearest"),
        ):
            with self.assertRaisesRegex(ValueError, "RESPONSE_NOT_JSON"):
                action_api._detect_action_target_profile_for_required_backends_fork_clean(
                    required_backends=("optix",),
                    certified_nearest=True,
                    _runner=lambda command, **kwargs: subprocess.CompletedProcess(
                        command, 0, stdout="not-json", stderr=""
                    ),
                )

    def test_child_rejects_invalid_provider_bytes_before_any_claim(self) -> None:
        child = SRC / "rtdsl" / "_fork_clean_optix_target_probe_child.py"
        request = {
            "schema": action_api._FAST_FORK_CLEAN_OPTIX_TARGET_PROBE_REQUEST,
            "nonce": "a" * 64,
            "required_backends": ["optix"],
            "certified_nearest": False,
            "cpu_reference_available": True,
            "optix_max_inline_state_bytes": None,
            "numba_max_device_state_bytes": None,
            "embree_max_host_state_bytes": None,
            "max_output_bytes": None,
            "action_api_sha256": action_api._sha256_file(
                Path(action_api.__file__).resolve(strict=True)
            ),
            "probe_child_sha256": action_api._sha256_file(child),
            "provider_library_path": str(self.native.resolve(strict=True)),
            "provider_library_sha256": action_api._sha256_file(self.native),
        }
        completed = subprocess.run(
            [sys.executable, str(child)],
            input=json.dumps(request),
            text=True,
            capture_output=True,
            env=os.environ.copy(),
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("", completed.stdout)

    def test_default_registry_delta_is_only_action_api_reauthentication(self) -> None:
        path = SRC / "rtdsl" / "default_physical_selection.py"
        source = path.read_bytes()
        predecessor = (
            b'    "src/rtdsl/action_api.py": '
            b'"2e3908fcc27b506b2f473f5cf00cfe2c56a6d38a39537cb5c225c9cc80887eb2",'
        )
        candidate = (
            b'    "src/rtdsl/action_api.py": '
            b'"bb494a820a6b3d084919ab631ba4b240b632355dd0875b69ecc3ebf606cc31df",'
        )
        self.assertEqual(1, source.count(candidate))
        self.assertEqual(0, source.count(predecessor))
        reconstructed = source.replace(candidate, predecessor)
        self.assertEqual(
            "7d335b8d507c7439ae8c1797fdf6438176f4d9cd8958f41fedb7376b0b62415d",
            hashlib.sha256(reconstructed).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
