from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.goal5848_strong_baseline import contracts
from scripts import goal5848_build_transaction_authority as authority
from tests.goal5848_instrumentation_fixture import (
    write_instrumentation_fixture,
)
from tests.goal5848_strong_baseline_contract_test import (
    Goal5848StrongBaselineContractTest,
)


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _sealed(value: dict[str, object], field: str) -> dict[str, object]:
    result = copy.deepcopy(value)
    result[field] = contracts.digest(result)
    return result


class Goal5848TransactionAuthorityTest(unittest.TestCase):
    def _fixture(self, root: Path):
        root = root.resolve(strict=True)
        source_commit = "a" * 40
        predecessor_commit = "b" * 40
        source_tree = "c" * 40
        predecessor_tree = "d" * 40
        pyoptix_commit = "e" * 40
        pyoptix_tree = "f" * 40
        source_root = root / "source"
        predecessor_root = root / "predecessor"
        pyoptix_root = root / "pyoptix"
        for repository in (source_root, predecessor_root, pyoptix_root):
            repository.mkdir()
        python = root / "bin" / "python3"
        python.parent.mkdir()
        python.write_text("synthetic-python\n")
        artifacts = {}
        for label in contracts.PREREGISTRATION_ARTIFACT_ARGUMENTS:
            path = root / "artifacts" / label
            path.parent.mkdir(exist_ok=True)
            path.write_text(label)
            artifacts[label] = authority._file_identity(path)
        prereg = {
            "schema": contracts.PREREGISTRATION_SCHEMA,
            "status": "FROZEN__BEFORE_FORMAL_WORKER_ZERO",
            "source_commit": source_commit,
            "source_tree": source_tree,
            "predecessor_commit": predecessor_commit,
            "predecessor_tree": predecessor_tree,
            "pyoptix_commit": pyoptix_commit,
            "pyoptix_tree": pyoptix_tree,
            "optix_disk_cache_policy": "disabled_for_all_primary_arms",
            "source_identity": {
                "path": str(source_root),
                "commit": source_commit,
                "tree": source_tree,
                "status": "",
                "clean": True,
            },
            "predecessor_identity": {
                "path": str(predecessor_root),
                "commit": predecessor_commit,
                "tree": predecessor_tree,
                "status": "",
                "clean": True,
            },
            "pyoptix_identity": {
                "path": str(pyoptix_root),
                "commit": pyoptix_commit,
                "tree": pyoptix_tree,
                "status": "",
                "clean": True,
            },
            "python": authority._file_identity(python),
            "python_version": "3.12.14",
            "expected_optix_sdk": "9.0.0",
            "tasks": list(contracts.TASKS),
            "task_contracts": contracts.TASK_CONTRACTS,
            "primary_arms": list(contracts.PRIMARY_ARMS),
            "all_arms": list(contracts.ARMS),
            "blocks": contracts.BLOCKS,
            "steady_warmups": contracts.STEADY_WARMUPS,
            "steady_repetitions": contracts.STEADY_REPETITIONS,
            "schedule": list(contracts.build_schedule()),
            "schedule_sha256": contracts.digest(list(contracts.build_schedule())),
            "thresholds_ppm": {
                "implementation_entry_median": (
                    contracts.IMPLEMENTATION_ENTRY_RATIO_LIMIT_PPM
                ),
                "implementation_entry_worst_block": (
                    contracts.IMPLEMENTATION_ENTRY_BLOCK_RATIO_LIMIT_PPM
                ),
                "post_import_diagnostic_reference_median": (
                    contracts.POST_IMPORT_RATIO_LIMIT_PPM
                ),
                "post_import_diagnostic_reference_worst_block": (
                    contracts.POST_IMPORT_BLOCK_RATIO_LIMIT_PPM
                ),
                "public_direct_median": (
                    contracts.PUBLIC_DIRECT_RATIO_LIMIT_PPM
                ),
                "successor_predecessor_median": (
                    contracts.SUCCESSOR_PREDECESSOR_RATIO_LIMIT_PPM
                ),
                "strong_competence_median": (
                    contracts.STRONG_COMPETENCE_RATIO_LIMIT_PPM
                ),
                "instrumentation_overhead": (
                    contracts.INSTRUMENTATION_OVERHEAD_LIMIT_PPM
                ),
            },
            "partition_reconciliation": {
                "absolute_tolerance_ns": (
                    contracts.PARTITION_ABSOLUTE_TOLERANCE_NS
                ),
                "relative_tolerance_ppm": (
                    contracts.PARTITION_RELATIVE_TOLERANCE_PPM
                ),
            },
            "instrumentation_protocol": contracts.instrumentation_protocol(),
            "aot_cache_protocol": contracts.aot_cache_protocol(),
            "endpoint": (
                "implementation_entry_to_first_exact_public_result__"
                "post_import_retained_as_state_mismatch_diagnostic"
            ),
            "estimator": "median_of_eight_within_block_integer_ratios",
            "failure_policy": {
                "formal_worker_retry": False,
                "formal_worker_discard": False,
                "prior_rows_authorized_for_pooling": False,
                "repair_requires_new_preregistration": True,
            },
            "artifacts": artifacts,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "claim_boundary": {
                "single_generation_only": True,
                "external_review_complete": False,
                "public_or_manuscript_claim_authorized": False,
            },
            "retry_count": 0,
            "discard_count": 0,
        }
        prereg = _sealed(prereg, "preregistration_sha256")
        prereg_path = root / "prereg.json"
        _write(prereg_path, prereg)
        hardware = {
            "gpu_name": "Synthetic RTX",
            "gpu_uuid": "GPU-synthetic",
            "driver_version": "580.0",
            "memory_mib": 16384,
            "compute_capability": "8.9",
        }
        witness = _sealed({
            "schema": "rtdl.goal5848.timer_free_witness_authority.v1",
            "status": "PASS__ALL_EIGHT_PRIMARY_ARM_TASK_WITNESSES",
            "hardware": hardware,
        }, "authority_sha256")
        witness_path = root / "witness.json"
        _write(witness_path, witness)
        competence = _sealed({
            "schema": "rtdl.goal5848.baseline_competence.v1",
            "status": "PASS__STRONG_PYOPTIX_COMPETENT_FOR_BOTH_TASKS",
            "hardware": hardware,
        }, "authority_sha256")
        competence_path = root / "competence.json"
        _write(competence_path, competence)
        instrumentation_path, instrumentation = write_instrumentation_fixture(
            root,
            source_commit=source_commit,
            predecessor_commit=predecessor_commit,
            preregistration_sha256=prereg["preregistration_sha256"],
            hardware=hardware,
            python_path=python,
            candidate_manifest=Path(
                str(artifacts["candidate_manifest"]["path"])
            ),
        )
        preflight = {
            "schema": contracts.PREFLIGHT_SCHEMA,
            "status": contracts.PREFLIGHT_PASS_STATUS,
            "source_commit": source_commit,
            "predecessor_commit": predecessor_commit,
            "preregistration_file_sha256": hashlib.sha256(
                prereg_path.read_bytes()
            ).hexdigest(),
            "preregistration_sha256": prereg["preregistration_sha256"],
            "timer_free_witness_path": str(witness_path),
            "timer_free_witness_file_sha256": hashlib.sha256(
                witness_path.read_bytes()
            ).hexdigest(),
            "timer_free_witness_sha256": witness["authority_sha256"],
            "baseline_competence_path": str(competence_path),
            "baseline_competence_file_sha256": hashlib.sha256(
                competence_path.read_bytes()
            ).hexdigest(),
            "baseline_competence_sha256": competence["authority_sha256"],
            "instrumentation_overhead_path": str(instrumentation_path),
            "instrumentation_overhead_file_sha256": hashlib.sha256(
                instrumentation_path.read_bytes()
            ).hexdigest(),
            "instrumentation_overhead_sha256": instrumentation[
                "authority_sha256"
            ],
            "hardware": hardware,
        }
        preflight = _sealed(preflight, "preflight_sha256")
        preflight_path = root / "preflight.json"
        _write(preflight_path, preflight)
        transaction_root = root / "transaction"
        workers = transaction_root / "workers"
        processes = transaction_root / "processes"
        support = transaction_root / "direct_support"
        workers.mkdir(parents=True)
        processes.mkdir()
        support.mkdir()
        receipts = []
        for row in contracts.build_schedule():
            post_import = 110 if row["arm"] == contracts.RTDL_ARM else 100
            steady = {
                contracts.RTDL_ARM: 110,
                contracts.IDIOMATIC_PYOPTIX_ARM: 100,
                contracts.STRONG_PYOPTIX_ARM: 100,
                contracts.DIRECT_OPTIX_ARM: 100,
                contracts.PREDECESSOR_RTDL_ARM: 110,
            }[row["arm"]]
            receipt = Goal5848StrongBaselineContractTest._receipt(
                row, post_import_ns=post_import, steady_ns=steady
            )
            receipt["source"]["tree"] = (
                predecessor_tree
                if row["arm"] == contracts.PREDECESSOR_RTDL_ARM
                else source_tree
            )
            if row["arm"] == contracts.DIRECT_OPTIX_ARM:
                support_value = _sealed({
                    "schema": "rtdl.goal5802.formal_runtime_preflight.v1",
                    "registered_performance_timing_count": 0,
                    "formal_worker_count": 0,
                }, "preflight_sha256")
                support_path = support / f"{row['worker_id']}.preflight.json"
                _write(support_path, support_value)
                evidence = receipt["measurements"]["evidence"]
                evidence["compatibility_preflight_file_sha256"] = (
                    hashlib.sha256(support_path.read_bytes()).hexdigest()
                )
                evidence["compatibility_preflight_sha256"] = support_value[
                    "preflight_sha256"
                ]
            receipt["result_sha256"] = contracts.digest({
                key: item
                for key, item in receipt.items()
                if key != "result_sha256"
            })
            worker_id = str(row["worker_id"])
            worker_path = workers / f"{worker_id}.json"
            _write(worker_path, receipt)
            stdout = json.dumps(receipt, sort_keys=True) + "\n"
            process = {
                "schema": "rtdl.goal5848.formal_process.v2",
                "worker_id": worker_id,
                "command": authority._expected_process_command(
                    row,
                    preregistration=prereg,
                    artifacts=artifacts,
                    preregistration_path=prereg_path,
                    transaction_root=transaction_root,
                ),
                "execution_context": authority._expected_execution_context(
                    prereg
                ),
                "exit_code": 0,
                "wall_ns": 1,
                "stdout_utf8": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                "stderr_utf8": "",
                "stderr_sha256": hashlib.sha256(b"").hexdigest(),
            }
            process = _sealed(process, "process_sha256")
            _write(processes / f"{worker_id}.json", process)
            receipts.append(receipt)
        recount = contracts.evaluate_complete_transaction(
            receipts,
            expected_source_commit=source_commit,
            expected_predecessor_commit=predecessor_commit,
        )
        transaction = {
            "schema": "rtdl.goal5848.formal_transaction.v2",
            "status": (
                "PASS__GOAL5848_LIFECYCLE_CORRECTED_SINGLE_GENERATION_"
                "FORMAL_TRANSACTION"
            ),
            "expected_source_commit": source_commit,
            "expected_predecessor_commit": predecessor_commit,
            "preregistration_file_sha256": hashlib.sha256(
                prereg_path.read_bytes()
            ).hexdigest(),
            "preflight_file_sha256": hashlib.sha256(
                preflight_path.read_bytes()
            ).hexdigest(),
            "worker_count": 80,
            "process_count": 80,
            "retry_count": 0,
            "discard_count": 0,
            "recount": recount,
        }
        transaction = _sealed(transaction, "transaction_sha256")
        _write(transaction_root / "transaction.json", transaction)
        return (
            transaction_root,
            prereg_path,
            preflight_path,
            source_commit,
            predecessor_commit,
        )

    def test_authority_rejects_duplicate_keys_and_nonfinite_json(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = {
                "duplicate": ('{"worker_id":"a","worker_id":"b"}', "duplicate"),
                "nonfinite": ('{"wall_ns":NaN}', "non-finite"),
            }
            for name, (payload, message) in cases.items():
                with self.subTest(name=name):
                    path = root / f"{name}.json"
                    path.write_text(payload)
                    with self.assertRaisesRegex(ValueError, message):
                        authority._read(path, name)

    def test_complete_archive_recounts_and_mutation_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            source_commit = fixture[3]
            predecessor_commit = fixture[4]
            git_rows = [
                {"commit": source_commit, "tree": "c" * 40, "status": ""},
                {
                    "commit": predecessor_commit,
                    "tree": "d" * 40,
                    "status": "",
                },
                {"commit": "e" * 40, "tree": "f" * 40, "status": ""},
            ]
            with mock.patch.object(
                authority, "_git_identity", side_effect=git_rows
            ), mock.patch.object(
                authority,
                "_validate_device_artifacts_independently",
                return_value={
                    "path": "/tmp/device.json",
                    "bytes": 1,
                    "sha256": "e" * 64,
                },
            ), mock.patch.object(
                authority,
                "load_aot_cache_authority",
                return_value={"authority_sha256": "f" * 64},
            ):
                result = authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=source_commit,
                    expected_predecessor_commit=predecessor_commit,
                )
            self.assertEqual(result["worker_count"], 80)
            self.assertEqual(result["direct_support_count"], 16)
            self.assertEqual(
                result["instrumentation_overhead"]["sha256"],
                hashlib.sha256(
                    (
                        Path(temporary)
                        / "instrumentation"
                        / "authority.json"
                    ).read_bytes()
                ).hexdigest(),
            )
            worker = next((fixture[0] / "workers").iterdir())
            value = json.loads(worker.read_text())
            value["measurements"]["steady_complete_execution"][
                "samples_ns"
            ][0] += 1
            value["result_sha256"] = contracts.digest({
                key: item
                for key, item in value.items()
                if key != "result_sha256"
            })
            _write(worker, value)
            with (
                self.assertRaisesRegex(RuntimeError, "process differs"),
                mock.patch.object(
                    authority,
                    "_validate_device_artifacts_independently",
                    return_value={
                        "path": "/tmp/device.json",
                        "bytes": 1,
                        "sha256": "e" * 64,
                    },
                ),
            ):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=source_commit,
                    expected_predecessor_commit=predecessor_commit,
                )

    def test_coherently_resealed_instrumentation_limit_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = self._fixture(root)
            instrumentation_path = root / "instrumentation" / "authority.json"
            instrumentation = json.loads(instrumentation_path.read_text())
            instrumentation["tasks"][contracts.RELATION_TASK][
                "limit_ppm"
            ] += 1
            instrumentation = _sealed({
                key: value
                for key, value in instrumentation.items()
                if key != "authority_sha256"
            }, "authority_sha256")
            _write(instrumentation_path, instrumentation)

            preflight_path = fixture[2]
            preflight = json.loads(preflight_path.read_text())
            preflight["instrumentation_overhead_file_sha256"] = (
                hashlib.sha256(instrumentation_path.read_bytes()).hexdigest()
            )
            preflight["instrumentation_overhead_sha256"] = instrumentation[
                "authority_sha256"
            ]
            preflight = _sealed({
                key: value
                for key, value in preflight.items()
                if key != "preflight_sha256"
            }, "preflight_sha256")
            _write(preflight_path, preflight)

            with self.assertRaisesRegex(RuntimeError, "recount differs"):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=preflight_path,
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )

    def test_instrumentation_process_command_mutation_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = self._fixture(root)
            process_path = min(
                (root / "instrumentation" / "processes").glob("*.json")
            )
            process = json.loads(process_path.read_text())
            process["command"].extend(["--substituted", "true"])
            process = _sealed({
                key: value
                for key, value in process.items()
                if key != "process_sha256"
            }, "process_sha256")
            _write(process_path, process)

            with self.assertRaisesRegex(
                RuntimeError, "instrumentation process differs"
            ):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )

    def test_coherently_resealed_process_command_substitution_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            process_path = min((fixture[0] / "processes").iterdir())
            process = json.loads(process_path.read_text())
            process["command"].extend(["--substituted", "true"])
            process = _sealed({
                key: value
                for key, value in process.items()
                if key != "process_sha256"
            }, "process_sha256")
            _write(process_path, process)

            with self.assertRaisesRegex(RuntimeError, "process differs"):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )

    def test_coherently_resealed_process_context_substitution_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            process_path = min((fixture[0] / "processes").iterdir())
            process = json.loads(process_path.read_text())
            process["execution_context"]["environment"]["PYTHONPATH"] = (
                "/tmp/substituted"
            )
            process = _sealed({
                key: value
                for key, value in process.items()
                if key != "process_sha256"
            }, "process_sha256")
            _write(process_path, process)

            with self.assertRaisesRegex(RuntimeError, "process differs"):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )

    def test_coherently_resealed_worker_python_substitution_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            worker_path = min((fixture[0] / "workers").iterdir())
            worker = json.loads(worker_path.read_text())
            worker["python"] = "9.9.9"
            worker = _sealed({
                key: value
                for key, value in worker.items()
                if key != "result_sha256"
            }, "result_sha256")
            _write(worker_path, worker)

            process_path = fixture[0] / "processes" / worker_path.name
            process = json.loads(process_path.read_text())
            stdout = json.dumps(worker, sort_keys=True) + "\n"
            process["stdout_utf8"] = stdout
            process["stdout_sha256"] = hashlib.sha256(
                stdout.encode("utf-8")
            ).hexdigest()
            process = _sealed({
                key: value
                for key, value in process.items()
                if key != "process_sha256"
            }, "process_sha256")
            _write(process_path, process)

            with self.assertRaisesRegex(RuntimeError, "source/runtime differs"):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=fixture[1],
                    preflight_path=fixture[2],
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )

    def test_coherently_resealed_preregistration_threshold_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self._fixture(Path(temporary))
            prereg_path = fixture[1]
            prereg = json.loads(prereg_path.read_text())
            prereg["thresholds_ppm"]["implementation_entry_median"] += 1
            prereg = _sealed({
                key: value
                for key, value in prereg.items()
                if key != "preregistration_sha256"
            }, "preregistration_sha256")
            _write(prereg_path, prereg)

            preflight_path = fixture[2]
            preflight = json.loads(preflight_path.read_text())
            preflight["preregistration_file_sha256"] = hashlib.sha256(
                prereg_path.read_bytes()
            ).hexdigest()
            preflight["preregistration_sha256"] = prereg[
                "preregistration_sha256"
            ]
            preflight = _sealed({
                key: value
                for key, value in preflight.items()
                if key != "preflight_sha256"
            }, "preflight_sha256")
            _write(preflight_path, preflight)

            with self.assertRaisesRegex(RuntimeError, "preregistration differs"):
                authority.build_authority(
                    transaction_root=fixture[0],
                    preregistration_path=prereg_path,
                    preflight_path=preflight_path,
                    expected_source_commit=fixture[3],
                    expected_predecessor_commit=fixture[4],
                )


if __name__ == "__main__":
    unittest.main()
