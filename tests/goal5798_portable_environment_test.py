from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from experiments.goal5798_premeasurement.compatibility import (
    COMPATIBLE_STACKS,
    select_compatible_stack,
)
from experiments.goal5798_premeasurement.contract_runtime import (
    PORTABLE_ARMS,
    digest,
    validate_freeze,
    validate_host_binding,
)


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
FREEZE = ROOT / "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
RUNTIME = GOAL / "runtime_manifest_v13.json"


def load_freeze() -> dict[str, object]:
    return json.loads(FREEZE.read_text(encoding="utf-8"))


def binding(freeze: dict[str, object], *, driver: str, gpu: str, capability: str,
            vram: int) -> dict[str, object]:
    selected = select_compatible_stack(driver)
    value: dict[str, object] = {
        "schema": "rtdl.goal5798.physical_host_binding.v2",
        "hostname": "provided-linux-host",
        "gpu_model": gpu,
        "gpu_uuid": "GPU-00000000-0000-0000-0000-000000000000",
        "compute_capability": capability,
        "vram_bytes": vram,
        "driver_version": driver,
        "driver_branch": int(driver.split(".", 1)[0]),
        "kernel": "Linux 6.x",
        "os_release": "provided Linux",
        "wsl": False,
        "cuda_toolkit": "actual toolkit bound later",
        "nvrtc": "actual NVRTC bound later",
        "python": "3.12",
        "gxx": "actual compiler bound later",
        "optix_api_version": selected["optix_api_version"],
        "optix_header_commit": selected["optix_header_commit"],
        "pyoptix_commit": freeze["dependencies"]["pyoptix_commit"],
        "pyoptix_distribution_name": selected["pyoptix_distribution_name"],
        "pyoptix_distribution_version": selected["pyoptix_distribution_version"],
        "selected_stack": selected,
        "visible_gpu_ordinal": 0,
        "visible_gpu_count": 1,
        "stack_selection_inputs": ["driver_version"],
        "stack_selection_before_task_materialization": True,
        "source_manifest_sha256": freeze["source_manifest_sha256"],
        "other_compute_process_count": 0,
    }
    value["binding_sha256"] = digest(value)
    return value


def reseal(value: dict[str, object]) -> None:
    value.pop("binding_sha256", None)
    value["binding_sha256"] = digest(value)


class Goal5798PortableEnvironmentTest(unittest.TestCase):
    def test_freeze_removes_hardware_and_preferred_driver_filters(self) -> None:
        freeze = load_freeze()
        validate_freeze(freeze)
        host = freeze["designated_host"]
        self.assertIsNone(host["gpu_model_allowlist"])
        self.assertIsNone(host["gpu_model_denylist"])
        self.assertIsNone(host["fixed_compute_capability"])
        self.assertIsNone(host["fixed_vram_minimum"])
        self.assertIsNone(host["fixed_driver_branch"])
        self.assertFalse(freeze["stack_selection"]["result_dependent"])
        self.assertFalse(freeze["stack_selection"]["gpu_model_dependent"])

    def test_every_published_driver_boundary_selects_newest_compatible_stack(self) -> None:
        cases = {
            "595.71": "9.1.0",
            "590.0": "9.1.0",
            "589.99": "9.0.0",
            "580.126.09": "9.0.0",
            "570.0": "9.0.0",
            "569.99": "8.1.0",
            "555.0": "8.1.0",
            "554.99": "8.0.0",
            "535.0": "8.0.0",
            "534.99": "7.7.0",
            "530.41": "7.7.0",
            "530.40": "7.6.0",
            "522.25": "7.6.0",
        }
        for driver, api in cases.items():
            self.assertEqual(select_compatible_stack(driver)["optix_api_version"], api)
        with self.assertRaises(RuntimeError):
            select_compatible_stack("522.24")

    def test_model_capability_and_vram_do_not_change_admission(self) -> None:
        freeze = load_freeze()
        examples = (
            ("NVIDIA GeForce GTX 1070", "6.1", 2_000_000_000),
            ("NVIDIA RTX 2000 Ada Generation", "8.9", 4_000_000_000),
            ("UNSEEN FUTURE NVIDIA GPU NAME", "12.0", 1),
        )
        for gpu, capability, vram in examples:
            value = binding(
                freeze, driver="580.126.09", gpu=gpu,
                capability=capability, vram=vram)
            self.assertEqual(validate_host_binding(freeze, value), [])

    def test_only_driver_selects_stack_and_mismatch_rejects(self) -> None:
        freeze = load_freeze()
        valid = binding(
            freeze, driver="570.0", gpu="arbitrary NVIDIA GPU",
            capability="8.6", vram=123)
        self.assertEqual(validate_host_binding(freeze, valid), [])
        attacked = deepcopy(valid)
        attacked["selected_stack"] = select_compatible_stack("590.0")
        attacked["optix_api_version"] = "9.1.0"
        attacked["optix_header_commit"] = attacked["selected_stack"]["optix_header_commit"]
        reseal(attacked)
        self.assertIn(
            "STACK_NOT_DETERMINISTIC_MAXIMUM_COMPATIBLE",
            validate_host_binding(freeze, attacked))
        extra_input = deepcopy(valid)
        extra_input["stack_selection_inputs"] = ["driver_version", "gpu_model"]
        reseal(extra_input)
        self.assertIn("STACK_SELECTION_INPUTS_INVALID",
                      validate_host_binding(freeze, extra_input))

    def test_all_workers_plan_without_importing_cuda_or_authority(self) -> None:
        freeze = load_freeze()
        scripts = {
            "A_DIRECT_CUDA_OPTIX": None,
            "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API": "pyoptix_worker.py",
            "D_RTDL_PUBLIC": "rtdl_worker.py",
        }
        self.assertEqual(set(scripts), set(PORTABLE_ARMS))
        for arm, script in scripts.items():
            if script is None:
                continue
            worker = next(row["worker_id"] for row in freeze["performance_schedule"]
                          if row["arm"] == arm)
            result = subprocess.run([
                sys.executable, str(GOAL / script), "--freeze", str(FREEZE),
                "--runtime-manifest", str(RUNTIME), "--worker-id", worker,
                "--plan-only",
            ], cwd=ROOT, check=True, text=True, capture_output=True)
            value = json.loads(result.stdout)
            self.assertEqual(value["status"], "PLAN_ONLY__GPU_NOT_IMPORTED_OR_EXECUTED")

    def test_runner_uses_dynamic_stack_and_compute_target(self) -> None:
        runner = (ROOT / "scripts/goal5798_portable_prepare_and_run.sh").read_text(
            encoding="utf-8")
        self.assertIn('--driver "$driver_version"', runner)
        self.assertIn('OPTIX_CUDA_ARCH="$cuda_arch"', runner)
        self.assertIn('export CMAKE_ARGS="-DFETCHCONTENT_SOURCE_DIR_OPTIX_HEADERS=', runner)
        self.assertIn('export PYOPTIX_CMAKE_ARGS="$CMAKE_ARGS"', runner)
        self.assertIn("runtime_manifest_v13.json", runner)
        self.assertIn("GOAL5798_V12_EXTERNAL_PREEXECUTION_GATE", runner)
        self.assertIn("goal5798_verify_v12_external_gate.py", runner)
        self.assertIn('export PATH="$cuda_root/bin:$PATH"', runner)
        self.assertNotIn("RTX 4000 Ada", runner)
        self.assertNotIn("R590", runner)
        self.assertNotIn("sm_89", runner)
        self.assertNotIn('test "$driver_branch"', runner)
        controller = (GOAL / "controller.py").read_text(encoding="utf-8")
        self.assertIn('args.compute_capability = authority["host_binding"]', controller)
        rtdl = (GOAL / "rtdl_worker.py").read_text(encoding="utf-8")
        self.assertNotIn('requires compute capability 8.9', rtdl)
        self.assertIn("compute_capability=compute_capability", rtdl)

    def test_registry_is_complete_and_unique(self) -> None:
        self.assertEqual(len(COMPATIBLE_STACKS), 6)
        self.assertEqual(len({row["stack_id"] for row in COMPATIBLE_STACKS}), 6)
        self.assertEqual(len({row["optix_header_commit"] for row in COMPATIBLE_STACKS}), 6)


if __name__ == "__main__":
    unittest.main()
