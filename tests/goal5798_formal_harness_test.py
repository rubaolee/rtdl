from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
sys.path.insert(0, str(GOAL))

from contract_runtime import MEMORY_MODE, digest, load_freeze
from formal_contract_runtime import validate_final_worker_receipt
from worker_common import create_json, finish_receipt, load_runtime_manifest


FREEZE = ROOT / "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
RUNTIME = GOAL / "runtime_manifest_v13.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(value, indent=2, sort_keys=True).encode() + b"\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Goal5798FormalHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = load_freeze(FREEZE)
        cls.runtime = load_runtime_manifest(RUNTIME)

    def test_runtime_manifest_rehashes_all_317_files(self):
        self.assertEqual(self.runtime["file_count"], 317)

    def test_create_only_json_is_atomically_published(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "barrier.json"
            payload = {"rows": list(range(10000)), "status": "COMPLETE"}
            create_json(output, payload)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), payload)
            self.assertEqual(list(output.parent.glob(".*.tmp.*")), [])
            with self.assertRaises(FileExistsError):
                create_json(output, payload)
        source = (GOAL / "worker_common.py").read_text(encoding="utf-8")
        self.assertIn("os.link(temporary, path)", source)
        self.assertEqual(self.runtime["base_freeze_sha256"], self.freeze["freeze_sha256"])
        paths = {row["path"] for row in self.runtime["files"]}
        for required in (
            "experiments/goal5798_premeasurement/controller.py",
            "experiments/goal5798_premeasurement/direct_measurement.cpp",
            "experiments/goal5798_premeasurement/pyoptix_worker.py",
            "experiments/goal5798_premeasurement/rtdl_worker.py",
            "experiments/goal5798_premeasurement/worker_common.py",
        ):
            self.assertIn(required, paths)

    def test_plan_only_workers_do_not_require_gpu_dependencies(self):
        cases = (
            ("pyoptix_worker.py", "P001__B00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__COLD_FRESH_PROCESS__B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API"),
            ("rtdl_worker.py", "P002__B00__CUSTOM_AABB_CLOSED_RELATION_COUNT_V1__COLD_FRESH_PROCESS__D_RTDL_PUBLIC"),
        )
        for script, worker_id in cases:
            process = subprocess.run([
                sys.executable, str(GOAL / script), "--freeze", str(FREEZE),
                "--runtime-manifest", str(RUNTIME), "--worker-id", worker_id,
                "--plan-only",
            ], cwd=ROOT, check=True, text=True, capture_output=True)
            value = json.loads(process.stdout)
            self.assertEqual(value["status"], "PLAN_ONLY__GPU_NOT_IMPORTED_OR_EXECUTED")

    def test_common_receipt_enforces_frozen_mode_denominators(self):
        authority = {
            "authority_sha256": "a" * 64,
            "host_binding_sha256": "b" * 64,
        }
        for mode, count, eligible in (
            ("COLD_FRESH_PROCESS", 1, True),
            ("PREPARED_EXECUTION", 64, True),
            (MEMORY_MODE, 1, False),
        ):
            row = next(value for value in (
                self.freeze["performance_schedule"] + self.freeze["memory_schedule"])
                if value["arm"] == "D_RTDL_PUBLIC" and value["mode"] == mode)
            receipt = finish_receipt(
                freeze=self.freeze, row=row, runtime_manifest=self.runtime,
                authority=authority,
                phases_ns={"common_preparation_total": 1},
                execute_durations_ns=list(range(1, count + 1)),
                correctness={"oracle_exact": True, "raw_output_sha256": "c" * 64},
                implementation={"arm": row["arm"]})
            self.assertIs(receipt["timing_eligible"], eligible)
            self.assertEqual(len(receipt["durations_ns"]["complete_execute_ns"]), count)
        row = next(value for value in self.freeze["performance_schedule"]
                   if value["mode"] == "PREPARED_EXECUTION" and value["arm"] == "D_RTDL_PUBLIC")
        with self.assertRaisesRegex(ValueError, "64 timed executes"):
            finish_receipt(
                freeze=self.freeze, row=row, runtime_manifest=self.runtime,
                authority=authority, phases_ns={}, execute_durations_ns=[1] * 63,
                correctness={"oracle_exact": True, "raw_output_sha256": "c" * 64},
                implementation={})

    def test_hardened_final_receipt_validator_closes_every_frozen_required_leaf(self):
        row = next(value for value in self.freeze["performance_schedule"]
                   if value["mode"] == "COLD_FRESH_PROCESS" and value["arm"] == "D_RTDL_PUBLIC")
        payload = finish_receipt(
            freeze=self.freeze, row=row, runtime_manifest=self.runtime,
            authority={"authority_sha256": "a" * 64, "host_binding_sha256": "b" * 64},
            phases_ns={
                "deterministic_input_materialization": 1,
                "protocol_validation_and_codegen": 1,
                "device_compile": None,
                "module_program_pipeline_sbt": None,
                "gas_and_static_prepare": 2,
                "common_preparation_total": 3,
                "close": 1,
            }, execute_durations_ns=[7],
            correctness={"oracle_exact": True, "raw_output_sha256": "c" * 64},
            implementation={"arm": row["arm"]})
        payload.pop("receipt_sha256")
        payload["schema"] = "rtdl.goal5798.formal_worker_receipt.v1"
        payload["worker_payload_receipt_file_sha256"] = "d" * 64
        payload["durations_ns"]["controller_process_wall_ns"] = 99
        payload["primary_sample_ns"] = 99
        payload["receipt_sha256"] = digest(payload)
        self.assertEqual(validate_final_worker_receipt(self.freeze, payload), [])
        attacks = {
            "missing_raw_output": lambda value: value.pop("raw_output_sha256"),
            "wrong_phase_set": lambda value: value["durations_ns"].pop("close_ns"),
            "wrong_execute_denominator": lambda value: value["durations_ns"].update(
                complete_execute_ns=[1, 2]),
            "timed_memory_contamination": lambda value: value.update(memory={}),
            "wrong_primary": lambda value: value.update(primary_sample_ns=98),
            "wrong_warmup_count": lambda value: value.update(warmup_execute_count=8),
        }
        for name, mutate in attacks.items():
            attacked = json.loads(json.dumps(payload))
            mutate(attacked)
            attacked.pop("receipt_sha256", None)
            attacked["receipt_sha256"] = digest(attacked)
            self.assertTrue(validate_final_worker_receipt(self.freeze, attacked), name)

    def test_formal_direct_source_uses_matched_bounded_budget_and_prepared_owners(self):
        source = (GOAL / "direct_measurement.cpp").read_text(encoding="utf-8")
        self.assertIn("kRelationRawCapacity = 8194", source)
        self.assertIn("struct PreparedRelation", source)
        self.assertIn("struct PreparedTriangle", source)
        self.assertIn("for (int index = 0; index < kWarmups", source)
        self.assertIn("for (int index = 0; index < kTimed", source)
        self.assertNotIn("2 * indexed.size() * sources.size()", source)

    def test_controller_orders_all_memory_workers_before_worker_zero(self):
        source = (GOAL / "controller.py").read_text(encoding="utf-8")
        self.assertIn('schedule = freeze["memory_schedule"] + freeze["performance_schedule"]', source)
        self.assertIn("TERMINAL_FAILURE__NO_RETRY_OR_REPLACEMENT", source)
        self.assertIn("revalidate_current_host", source)
        self.assertIn("foreign GPU compute process before worker", source)

    def test_independent_recount_reconstructs_full_318_worker_denominator(self):
        schedule = self.freeze["memory_schedule"] + self.freeze["performance_schedule"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seals = []
            for index, row in enumerate(schedule):
                directory = root / f"{index:03d}_{row['worker_id']}"
                if row["mode"] == "PREPARED_EXECUTION":
                    arm_offset = {"A_DIRECT_CUDA_OPTIX": 30,
                                  "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API": 20,
                                  "D_RTDL_PUBLIC": 10}[row["arm"]]
                    values = [arm_offset + value for value in range(64)]
                    ordered = sorted(values)
                    primary = (ordered[31] + ordered[32]) // 2
                elif row["mode"] == "COLD_FRESH_PROCESS":
                    primary = {"A_DIRECT_CUDA_OPTIX": 300,
                               "B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API": 200,
                               "D_RTDL_PUBLIC": 100}[row["arm"]]
                    values = [1]
                else:
                    primary = None
                    values = [1]
                memory = None if row["mode"] != MEMORY_MODE else {
                    "host_peak_rss_bytes": 1000 + row["row_sample_index"],
                    "gpu_process_sampled_peak_bytes": 2000 + row["row_sample_index"],
                    "gpu_process_steady_prepared_bytes": 1500 + row["row_sample_index"],
                }
                payload_path = directory / "worker_receipt.json"
                write_json(payload_path, {"schema": "synthetic.worker.payload.v1"})
                receipt = {
                    "schema": "rtdl.goal5798.formal_worker_receipt.v1",
                    "worker_id": row["worker_id"], "arm": row["arm"],
                    "task": row["task"], "mode": row["mode"],
                    "row_sample_index": row["row_sample_index"],
                    "source_manifest_sha256": self.freeze["source_manifest_sha256"],
                    "workload_authority_sha256": self.freeze["workload_authority"]["authority_sha256"],
                    "host_binding_sha256": "1" * 64,
                    "timing_eligible": row["mode"] != MEMORY_MODE,
                    "durations_ns": {
                        "input_materialization_ns": 1,
                        "protocol_validation_and_codegen_ns": None,
                        "device_compile_ns": 1,
                        "module_program_pipeline_sbt_ns": 1,
                        "gas_and_static_prepare_ns": 1,
                        "common_preparation_total_ns": 3,
                        "complete_execute_ns": values,
                        "close_ns": 1,
                        "controller_process_wall_ns": primary if primary is not None else 500,
                    },
                    "correctness": {"oracle_exact": True, "raw_output_sha256": "2" * 64},
                    "raw_output_sha256": "2" * 64,
                    "worker_payload_receipt_file_sha256": sha(payload_path),
                    "memory": memory,
                }
                receipt["receipt_sha256"] = digest(receipt)
                receipt_path = directory / "final_receipt.json"
                write_json(receipt_path, receipt)
                record = {
                    "schema": "rtdl.goal5798.controller_worker_record.v1",
                    "sequence_index": index, "worker_id": row["worker_id"],
                    "arm": row["arm"], "task": row["task"], "mode": row["mode"],
                    "row_sample_index": row["row_sample_index"],
                    "process_wall_ns": primary if primary is not None else 500,
                    "registered_primary_sample_ns": primary,
                    "timing_eligible": row["mode"] != MEMORY_MODE,
                    "memory": memory,
                    "worker_payload_receipt_sha256": sha(payload_path),
                    "final_receipt_sha256": sha(receipt_path),
                    "correctness_oracle_exact": True,
                }
                record["record_sha256"] = digest(record)
                write_json(directory / "controller_record.json", record)
                seals.append(record["record_sha256"])
            result = {
                "schema": "rtdl.goal5798.formal_controller_result.v1", "status": "PASS",
                "worker_count": len(schedule), "record_sha256s": seals,
                "retry_count": 0, "resume_count": 0,
                "replacement_count": 0, "dropped_row_count": 0,
            }
            result["result_sha256"] = digest(result)
            write_json(root / "controller_result.json", result)
            output = root / "recount.json"
            subprocess.run([
                sys.executable, str(ROOT / "scripts/goal5798_independent_recount.py"),
                "--freeze", str(FREEZE), "--result-root", str(root),
                "--output", str(output),
            ], cwd=ROOT, check=True, text=True, capture_output=True)
            recount = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(recount["worker_count"], 318)
            self.assertEqual(recount["correct_worker_count"], 318)
            self.assertEqual(len(recount["comparison_rows"]), 8)
            self.assertEqual(len(recount["memory_rows"]), 6)


if __name__ == "__main__":
    unittest.main()
