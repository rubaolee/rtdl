"""Adversarial tests for Goal5798's non-executing design freeze."""

from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from experiments.goal5798_premeasurement.contract_runtime import (
    digest,
    validate_freeze,
    validate_future_worker_receipt,
    validate_host_binding,
)
from experiments.goal5798_premeasurement.workload import workload_authority


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "history/internal_docs/goal5798_s0_premeasurement_design_freeze_v4_20260823.json"
WORKLOAD = ROOT / "history/internal_docs/goal5798_s0_matched_workload_authority_20260823.json"
GENERATOR = ROOT / "experiments/goal5798_premeasurement/workload.py"


def load_freeze() -> dict[str, object]:
    return json.loads(FREEZE.read_text(encoding="utf-8"))


def reseal(value: dict[str, object]) -> None:
    value.pop("freeze_sha256", None)
    value["freeze_sha256"] = digest(value)


def verify_pin(pin: dict[str, object]) -> None:
    path = ROOT / pin["path"]
    assert path.stat().st_size == pin["bytes"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"]


def binding(freeze: dict[str, object]) -> dict[str, object]:
    value: dict[str, object] = {
        "schema": "rtdl.goal5798.host_binding.v1",
        "hostname": "future-rtdl-rtx4000ada",
        "gpu_model": "NVIDIA RTX 4000 Ada Generation",
        "gpu_uuid": "GPU-00000000-0000-0000-0000-000000000000",
        "compute_capability": "8.9",
        "vram_bytes": 21474836480,
        "driver_version": "590.00.00",
        "driver_branch": 590,
        "kernel": "Linux future 6.x x86_64",
        "os_release": "Ubuntu 24.04",
        "wsl": False,
        "cuda_toolkit": "UNBOUND_EXACT_FUTURE_RECEIPT",
        "nvrtc": "UNBOUND_EXACT_FUTURE_RECEIPT",
        "python": "3.12.x",
        "gxx": "13.x",
        "optix_api_version": "9.1.0",
        "optix_header_commit": freeze["dependencies"]["optix_header_commit"],
        "pyoptix_commit": freeze["dependencies"]["pyoptix_commit"],
        "source_manifest_sha256": freeze["source_manifest_sha256"],
        "other_compute_process_count": 0,
    }
    value["binding_sha256"] = digest(value)
    return value


class Goal5798PremeasurementFreezeTest(unittest.TestCase):
    def test_append_only_preaction_and_freeze_chain_rehashes(self) -> None:
        freeze = load_freeze()
        for key in (
            "preaction", "preaction_amendment_a1", "preaction_amendment_a2",
            "preaction_amendment_a3", "supersedes_pre_amendment_freeze",
        ):
            verify_pin(freeze[key])

    def test_workload_authority_rebuilds_and_imports_no_gpu_route(self) -> None:
        self.assertEqual(
            workload_authority(), json.loads(WORKLOAD.read_text(encoding="utf-8")))
        tree = ast.parse(GENERATOR.read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        self.assertTrue(imports <= {
            "__future__", "argparse", "hashlib", "json", "pathlib", "struct"})

    def test_frozen_contract_and_all_authorizations_false(self) -> None:
        freeze = load_freeze()
        validate_freeze(freeze)
        self.assertTrue(all(value is False for value in freeze["authorization"].values()))
        self.assertEqual(freeze["registered_performance_timing_count"], 0)
        self.assertEqual(freeze["gpu_execution_count"], 0)
        self.assertFalse(freeze["implementation_status"]["worker_zero_ready"])

    def test_schedule_drop_duplicate_and_position_bias_reject(self) -> None:
        for mutation in ("drop", "duplicate", "position"):
            freeze = load_freeze()
            schedule = freeze["performance_schedule"]
            if mutation == "drop":
                schedule.pop()
            elif mutation == "duplicate":
                schedule[1]["worker_id"] = schedule[0]["worker_id"]
            else:
                target = next(row for row in schedule if row["arm_position"] == 1)
                target["arm_position"] = 0
            reseal(freeze)
            with self.assertRaises(ValueError, msg=mutation):
                validate_freeze(freeze)

    def test_authorization_threshold_and_memory_timing_mutations_reject(self) -> None:
        attacks = []
        authorization = load_freeze()
        authorization["authorization"]["goal5798_worker_zero"] = True
        attacks.append(authorization)
        threshold = load_freeze()
        threshold["statistics"]["success_ratio_threshold"] = 1.0
        attacks.append(threshold)
        memory = load_freeze()
        memory["memory_schedule"][0]["timing_eligible"] = True
        attacks.append(memory)
        for attacked in attacks:
            reseal(attacked)
            with self.assertRaises(ValueError):
                validate_freeze(attacked)

    def test_host_and_baseline_substitutions_reject(self) -> None:
        freeze = load_freeze()
        valid = binding(freeze)
        self.assertEqual(validate_host_binding(freeze, valid), [])
        self.assertEqual(freeze["designated_host"]["vram_bytes_minimum"], 20_000_000_000)
        nominal = deepcopy(valid)
        nominal["vram_bytes"] = 20_000_000_000
        nominal.pop("binding_sha256")
        nominal["binding_sha256"] = digest(nominal)
        self.assertEqual(validate_host_binding(freeze, nominal), [])
        attacks = {
            "GTX1070": ("gpu_model", "NVIDIA GeForce GTX 1070"),
            "RTX2000Ada": ("gpu_model", "NVIDIA RTX 2000 Ada Generation"),
            "R570": ("driver_branch", 570),
            "WSL": ("wsl", True),
            "other_process": ("other_compute_process_count", 1),
            "source_swap": ("source_manifest_sha256", "0" * 64),
            "vram_below_nominal": ("vram_bytes", 19_999_999_999),
        }
        for name, (key, value) in attacks.items():
            attacked = deepcopy(valid)
            attacked[key] = value
            attacked.pop("binding_sha256")
            attacked["binding_sha256"] = digest(attacked)
            self.assertTrue(validate_host_binding(freeze, attacked), name)
        self.assertEqual(validate_host_binding(freeze, None), ["HOST_BINDING_ABSENT"])

    def test_future_receipt_must_match_schedule_source_workload_and_oracle(self) -> None:
        freeze = load_freeze()
        planned = freeze["performance_schedule"][0]
        receipt = {
            "worker_id": planned["worker_id"],
            "arm": planned["arm"],
            "task": planned["task"],
            "mode": planned["mode"],
            "row_sample_index": planned["row_sample_index"],
            "source_manifest_sha256": freeze["source_manifest_sha256"],
            "workload_authority_sha256": freeze["workload_authority"][
                "authority_sha256"],
            "correctness": {"oracle_exact": True},
            "timing_eligible": True,
            "durations_ns": {"controller_process_wall_ns": 1},
        }
        self.assertEqual(validate_future_worker_receipt(freeze, receipt), [])
        for key, value in (
            ("arm", "D_RTDL_PUBLIC" if receipt["arm"] != "D_RTDL_PUBLIC" else
             "A_DIRECT_CUDA_OPTIX"),
            ("source_manifest_sha256", "0" * 64),
            ("workload_authority_sha256", "0" * 64),
            ("correctness", {"oracle_exact": False}),
        ):
            attacked = deepcopy(receipt)
            attacked[key] = value
            self.assertTrue(validate_future_worker_receipt(freeze, attacked), key)

    def test_statistics_and_claim_ceiling_have_no_success_threshold(self) -> None:
        freeze = load_freeze()
        self.assertIsNone(freeze["statistics"]["success_ratio_threshold"])
        self.assertFalse(freeze["claim_ceiling"]["universal_performance"])
        self.assertFalse(freeze["claim_ceiling"]["new_application_generalization"])
        self.assertFalse(freeze["claim_ceiling"]["usability_or_productivity"])
        self.assertFalse(freeze["claim_ceiling"]["owl_performance"])
        self.assertEqual(
            freeze["matched_resource_budget"]["relation_raw_event_capacity"], 8194)
        self.assertIs(
            freeze["matched_resource_budget"]["identical_for_A_B_D"], True)
        metrics = freeze["measurement_modes"]["MEMORY_SEPARATE_NON_TIMED"][
            "primary_metrics"]
        self.assertIn("gpu_process_sampled_peak_bytes", metrics)
        self.assertNotIn("gpu_process_peak_bytes", metrics)


if __name__ == "__main__":
    unittest.main()
