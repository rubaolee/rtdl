from __future__ import annotations

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from examples.current.research_benchmarks.contact_manifold import (  # noqa: E402
    rtdl3_effect_action_consumer as contact,
)
from rtdsl import action_api  # noqa: E402
from rtdsl.action_api import (  # noqa: E402
    ActionProducerKind,
    _detect_action_target_profile_for_required_backends_fork_clean,
    bind_action_producer,
    compile_bound_action_for_target,
)
from rtdsl.action_ray_triangle_scalar_summary import (  # noqa: E402
    detect_ray_triangle_scalar_summary_target,
)


def _fake_runner(*, mutate=None):
    def run(command, **kwargs):
        request = json.loads(kwargs["input"])
        target = {
            "optix_available": True,
            "numba_available": False,
            "embree_available": False,
            "cpu_reference_available": True,
            "optix_max_inline_state_bytes": None,
            "numba_max_device_state_bytes": None,
            "embree_max_host_state_bytes": None,
            "max_output_bytes": None,
            "profile_source": "runtime_capability_probe",
            "device_memory_limit_bytes": 8 << 30,
            "production_selection_policy": "compiler_owned_default",
        }
        response = {
            "schema": action_api._FORK_CLEAN_TARGET_PROBE_RESPONSE,
            "nonce": request["nonce"],
            "required_backends": request["required_backends"],
            "action_api_sha256": request["action_api_sha256"],
            "provider_library_sha256": request["provider_library_sha256"],
            "target_profile": target,
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


class Goal5738ForkCleanActionTargetProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.native = Path(self.temporary.name) / "librtdl_optix.so"
        self.native.write_bytes(b"goal5738-fake-native")
        self.environment = patch.dict(
            os.environ,
            {"RTDL_OPTIX_LIB": str(self.native)},
            clear=False,
        )
        self.environment.start()

    def tearDown(self) -> None:
        self.environment.stop()
        self.temporary.cleanup()

    def probe(self, *, runner=None):
        return _detect_action_target_profile_for_required_backends_fork_clean(
            required_backends=("optix",),
            cpu_reference_available=True,
            _runner=runner or _fake_runner(),
        )

    def test_valid_receipt_returns_explicit_fork_clean_profile(self) -> None:
        target = self.probe()
        self.assertTrue(target.optix_available)
        self.assertEqual(8 << 30, target.device_memory_limit_bytes)
        self.assertEqual(
            "fork_clean_runtime_capability_probe", target.profile_source
        )
        self.assertEqual("compiler_owned_default", target.production_selection_policy)

    def test_parent_never_calls_ordinary_cuda_initializing_probe(self) -> None:
        with patch.object(
            action_api,
            "_detect_action_target_profile_for_required_backends",
            side_effect=AssertionError("parent attempted dynamic CUDA probe"),
        ):
            target = self.probe()
        self.assertTrue(target.optix_available)

    def test_disposable_child_response_binds_source_native_and_dynamic_facts(self) -> None:
        request = {
            "schema": action_api._FORK_CLEAN_TARGET_PROBE_REQUEST,
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
            "provider_library_path": str(self.native.resolve(strict=True)),
            "provider_library_sha256": action_api._sha256_file(self.native),
        }
        target = action_api.ActionTargetProfile(
            optix_available=True,
            cpu_reference_available=True,
            profile_source="runtime_capability_probe",
            device_memory_limit_bytes=8 << 30,
            production_selection_policy="compiler_owned_default",
        )
        with patch.object(
            action_api,
            "_detect_action_target_profile_for_required_backends",
            return_value=target,
        ) as dynamic_probe:
            response = action_api._fork_clean_action_target_probe_response(request)
        dynamic_probe.assert_called_once()
        claimed = response.pop("response_sha256")
        self.assertEqual(claimed, action_api._canonical_sha256(response))
        self.assertEqual(request["action_api_sha256"], response["action_api_sha256"])
        self.assertEqual(
            request["provider_library_sha256"],
            response["provider_library_sha256"],
        )

        malformed = dict(request)
        malformed["certified_nearest"] = "false"
        with self.assertRaisesRegex(ValueError, "BOOLEAN_FACT_INVALID"):
            action_api._fork_clean_action_target_probe_response(malformed)

    def test_replayed_or_wrong_nonce_fails_closed(self) -> None:
        def wrong_nonce(response):
            response["nonce"] = "0" * 64

        with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_INVALID"):
            self.probe(runner=_fake_runner(mutate=wrong_nonce))

    def test_wrong_native_identity_fails_closed(self) -> None:
        def wrong_native(response):
            response["provider_library_sha256"] = "0" * 64

        with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_INVALID"):
            self.probe(runner=_fake_runner(mutate=wrong_native))

    def test_wrong_parent_or_gpu_visibility_fails_closed(self) -> None:
        def wrong_parent(response):
            response["parent_process_pid"] = os.getpid() + 17

        with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_INVALID"):
            self.probe(runner=_fake_runner(mutate=wrong_parent))

        def wrong_visibility(response):
            response["cuda_visible_devices"] = "unexpected-device"

        with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_INVALID"):
            self.probe(runner=_fake_runner(mutate=wrong_visibility))

    def test_unavailable_required_backend_fails_closed(self) -> None:
        def unavailable(response):
            response["target_profile"]["optix_available"] = False

        with self.assertRaisesRegex(ValueError, "REQUIRED_BACKEND_UNAVAILABLE"):
            self.probe(runner=_fake_runner(mutate=unavailable))

    def test_nonpaper_contact_action_consumes_same_target_profile(self) -> None:
        target = self.probe()
        planned = compile_bound_action_for_target(
            bind_action_producer(
                contact.compile_contact_action(),
                ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D,
            ),
            target,
            extents={},
            parameters={"row_capacity": 2},
        )
        self.assertEqual("optix", planned.plan.selected_backend)

    def test_triangle_public_frontdoor_requires_explicit_fork_clean_mode(self) -> None:
        sentinel = object()
        with patch(
            "rtdsl.action_ray_triangle_scalar_summary."
            "_detect_action_target_profile_for_required_backends",
            return_value=sentinel,
        ) as ordinary:
            self.assertIs(sentinel, detect_ray_triangle_scalar_summary_target())
        ordinary.assert_called_once()
        with patch(
            "rtdsl.action_ray_triangle_scalar_summary."
            "_detect_action_target_profile_for_required_backends_fork_clean",
            return_value=sentinel,
        ) as fork_clean:
            self.assertIs(
                sentinel,
                detect_ray_triangle_scalar_summary_target(fork_clean=True),
            )
        fork_clean.assert_called_once()


if __name__ == "__main__":
    unittest.main()
