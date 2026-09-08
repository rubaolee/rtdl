from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest import mock

from scripts import v4_long_workload_replication_controller as controller
from scripts import v4_long_workload_replication_freeze as freeze
from scripts import v4_long_workload_replication_make_config as make_config
from scripts import v4_long_workload_replication_recount as recount


def _config():
    implementation = {
        "source_root": "/source",
        "source_commit": "a" * 40,
        "source_tree": "b" * 40,
        "native_library_path": "/native.so",
        "native_library_sha256": "c" * 64,
    }
    return {
        "schema": controller.CONFIG_SCHEMA,
        "common": {
            "prepared_warmups": 1,
            "retry_allowed": False,
            "discard_allowed": False,
            "worker_timeout_seconds": 900,
            "cpu_affinity": {"cpu_ids": [8]},
            "registered_machine": {
                "cuda_visible_devices": "0",
                "gpu": {
                    "name": "GPU",
                    "uuid": "GPU-LOCKED",
                    "driver": "driver",
                    "compute_capability": "8.6",
                },
            },
            "python_version": "3.12.3",
            "python_executable": "/venv/bin/python",
        },
        "implementations": {
            "new_v4": implementation,
            "pyoptix": implementation,
        },
        "units": {
            controller.UNIT_ID: {
                "unit_id": controller.UNIT_ID,
                **controller.EXPECTED_UNIT,
            },
        },
    }


def _observed_rows(*, ratio=1.05, mismatch_block=None):
    rows = controller.build_schedule(_config(), mode="formal")
    for row in rows:
        arm = row["arm"]
        sample = 105 if arm == "new_v4" else int(105 / ratio)
        output = "different" if (
            mismatch_block == row["block"] and arm == "pyoptix"
        ) else "same"
        row.update({
            "launch": {"return_code": 0, "timeout": False},
            "worker": {
                "status": "PASS",
                "unit_id": controller.UNIT_ID,
                "arm": arm,
                "endpoint": controller.ENDPOINT,
                "formal_config_sha256": "config",
                "retained_sample_count": 3,
                "warmup_count": 1,
                "retry_count": 0,
                "discard_count": 0,
                "input_identity": {"input": "fixed"},
                "output_sha256": output,
                "primary_samples_ns": [sample, sample, sample],
            },
        })
    return rows


class V4LongWorkloadReplicationHarnessTest(unittest.TestCase):
    def test_config_builder_derives_exact_two_arm_contract(self):
        base = {
            "schema": make_config.BASE_SCHEMA,
            "source_root": "/source",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "native_library_path": "/native.so",
            "native_library_sha256": "c" * 64,
            "native_build_manifest_path": "/native.json",
            "native_build_manifest_sha256": "d" * 64,
            "prepared_repetitions": {"old": 4},
            "prepared_warmups": 1,
            "performance_threshold_present": False,
            "registered_before_performance_observation": True,
            "retry_allowed": False,
            "discard_allowed": False,
            "registered_machine": {"gpu": {"uuid": "GPU-new"}},
        }
        fragment = {
            "expected_native_sha256": "c" * 64,
            "artifact_path": "/triangle.rtdlexe",
        }
        rtdlexe = {
            "schema": make_config.RTDLEXE_SCHEMA,
            "status": (
                "PASS__SIGNED_PUBLIC_LOAD_AND_DEVICE_PROGRAM_PREPARE_VERIFIED"
            ),
            "source": {"commit": "a" * 40, "tree": "b" * 40},
            "target": {"native_sha256": "c" * 64},
            "formal_config_fragment": fragment,
        }
        observed = make_config.derive_config(
            base, rtdlexe, cpu_id=8, worker_timeout_seconds=900)
        self.assertEqual(observed["schema"], controller.CONFIG_SCHEMA)
        self.assertEqual(
            set(observed["implementations"]), {"new_v4", "pyoptix"})
        self.assertNotIn("triangle_rtdlexe", observed["implementations"]["pyoptix"])
        self.assertEqual(
            observed["implementations"]["new_v4"]["triangle_rtdlexe"],
            fragment,
        )
        self.assertEqual(observed["common"]["cpu_affinity"], {"cpu_ids": [8]})
        self.assertNotIn("source_root", observed["common"])
        self.assertNotIn("prepared_repetitions", observed["common"])
        controller.validate_config(observed)

    def test_config_builder_rejects_rtdlexe_identity_drift(self):
        base = {
            "schema": make_config.BASE_SCHEMA,
            "source_root": "/source",
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "native_library_path": "/native.so",
            "native_library_sha256": "c" * 64,
            "native_build_manifest_path": "/native.json",
            "native_build_manifest_sha256": "d" * 64,
            "registered_before_performance_observation": True,
            "retry_allowed": False,
            "discard_allowed": False,
        }
        rtdlexe = {
            "schema": make_config.RTDLEXE_SCHEMA,
            "status": (
                "PASS__SIGNED_PUBLIC_LOAD_AND_DEVICE_PROGRAM_PREPARE_VERIFIED"
            ),
            "source": {"commit": "e" * 40, "tree": "b" * 40},
            "target": {"native_sha256": "c" * 64},
            "formal_config_fragment": {"expected_native_sha256": "c" * 64},
        }
        with self.assertRaises(ValueError):
            make_config.derive_config(
                base, rtdlexe, cpu_id=8, worker_timeout_seconds=900)

    def test_formal_schedule_is_exactly_sixteen_balanced_workers(self):
        rows = controller.build_schedule(_config(), mode="formal")
        self.assertEqual(len(rows), 16)
        self.assertEqual({row["unit_id"] for row in rows}, {controller.UNIT_ID})
        self.assertEqual({row["endpoint"] for row in rows}, {"prepared"})
        self.assertTrue(all(
            row["repetitions"] == 3 and row["warmups"] == 1
            for row in rows
        ))
        self.assertEqual(
            sum(order[0] == "new_v4" for order in controller.BLOCK_ORDERS), 4)
        self.assertEqual(
            sum(order[0] == "pyoptix" for order in controller.BLOCK_ORDERS), 4)
        self.assertEqual(rows, recount.expected_rows(_config()))

    def test_dry_run_has_one_worker_per_arm_without_warmup(self):
        rows = controller.build_schedule(_config(), mode="dry-run")
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["arm"] for row in rows], list(controller.ARMS))
        self.assertTrue(all(
            row["repetitions"] == 1 and row["warmups"] == 0
            and row["block"] is None
            for row in rows
        ))

    def test_config_rejects_workload_or_selection_changes(self):
        config = _config()
        controller.validate_config(config)
        config["units"][controller.UNIT_ID]["max_relation_rows"] = 8_000_000
        with self.assertRaises(ValueError):
            controller.validate_config(config)
        config = _config()
        config["common"]["cpu_affinity"]["cpu_ids"] = [8, 9]
        with self.assertRaises(ValueError):
            controller.validate_config(config)
        config = _config()
        config["common"]["retry_allowed"] = True
        with self.assertRaises(ValueError):
            controller.validate_config(config)

    def test_evaluation_retains_complete_adverse_result(self):
        result = controller.evaluate(
            _observed_rows(ratio=1.40), config_sha256="config", formal=True)
        self.assertTrue(result["method_complete"])
        self.assertEqual(result["valid_block_count"], 8)
        self.assertFalse(result["engineering_target_met"])
        self.assertGreater(result["median_new_v4_over_pyoptix"], 1.35)

    def test_evaluation_passes_only_complete_equal_output_population(self):
        result = controller.evaluate(
            _observed_rows(ratio=1.05), config_sha256="config", formal=True)
        self.assertTrue(result["method_complete"])
        self.assertTrue(result["engineering_target_met"])
        result = controller.evaluate(
            _observed_rows(ratio=1.05, mismatch_block=3),
            config_sha256="config",
            formal=True,
        )
        self.assertFalse(result["method_complete"])
        self.assertFalse(result["engineering_target_met"])
        self.assertEqual(result["cells"][3]["reason"], "input_or_output_parity")

    def test_recount_machine_validation_is_fail_closed(self):
        common = _config()["common"]
        machine = {
            **common["registered_machine"],
            "hostname": "pod",
            "platform": "Linux",
            "python": common["python_version"],
            "python_executable": common["python_executable"],
            "cpu_affinity": {
                "preflight": {"cpu_ids": [8]},
                "postflight": {"cpu_ids": [8]},
            },
        }
        recount.validate_machine(machine, common, ordinal=0)
        machine["cpu_affinity"]["postflight"] = {"cpu_ids": [9]}
        with self.assertRaises(RuntimeError):
            recount.validate_machine(machine, common, ordinal=0)

    def test_recount_source_has_no_project_import(self):
        source = Path(recount.__file__).read_text(encoding="utf-8")
        self.assertNotIn("from scripts", source)
        self.assertNotIn("import rtdsl", source)
        self.assertNotIn("from rtdsl", source)

    def test_recount_rejects_raw_paths_outside_exact_evidence_member(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            safe = root / "workers/safe.json"
            safe.parent.mkdir()
            safe.write_text("{}\n", encoding="utf-8")
            self.assertEqual(
                recount._resolve_evidence_member(
                    root, "workers/safe.json", expected="workers/safe.json",
                    ordinal=0, name="output",
                ),
                safe,
            )
            outside = root.parent / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            self.addCleanup(outside.unlink)
            with self.assertRaises(RuntimeError):
                recount._resolve_evidence_member(
                    root, "../outside.json", expected="../outside.json",
                    ordinal=0, name="output",
                )

    def test_replication_scope_is_bound_to_registered_gpu(self):
        different = _config()["common"]["registered_machine"]
        self.assertTrue(controller.replication_scope_matches(
            "cross_gpu_reproducibility", different))
        self.assertFalse(controller.replication_scope_matches(
            "same_host_temporal", different))
        original = {
            "cuda_visible_devices": "0",
            "gpu": dict(controller.PRIOR_REGISTERED_GPU),
        }
        self.assertTrue(controller.replication_scope_matches(
            "same_host_temporal", original))
        self.assertFalse(controller.replication_scope_matches(
            "cross_gpu_reproducibility", original))
        self.assertEqual(
            controller.replication_scope_matches(
                "cross_gpu_reproducibility", different),
            recount.replication_scope_matches(
                "cross_gpu_reproducibility", different),
        )

    def test_freeze_binds_dry_run_config_tools_and_schedule(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            dry_path = root / "dry.json"
            prereg_path = root / "prereg.json"
            config_path.write_text(
                json.dumps(_config(), indent=2) + "\n", encoding="utf-8")
            rows = controller.build_schedule(_config(), mode="dry-run")
            for row in rows:
                row.update({
                    "launch": {"return_code": 0, "timeout": False},
                    "worker": {
                        "status": "PASS",
                        "unit_id": controller.UNIT_ID,
                        "arm": row["arm"],
                        "endpoint": controller.ENDPOINT,
                        "formal_config_sha256": controller.sha256(config_path),
                        "retained_sample_count": 1,
                        "warmup_count": 0,
                        "retry_count": 0,
                        "discard_count": 0,
                        "input_identity": {"input": "fixed"},
                        "output_sha256": "same",
                        "primary_samples_ns": [100],
                    },
                })
            evaluation = controller.evaluate(
                rows,
                config_sha256=controller.sha256(config_path),
                formal=False,
            )
            dry = {
                "schema": controller.SUMMARY_SCHEMA,
                "mode": "dry-run",
                "status": "COMPLETE__DRY_RUN_PARITY_PASS",
                "formal_worker_zero_reached": False,
                "config_sha256": controller.sha256(config_path),
                "controller_sha256": controller.sha256(Path(controller.__file__)),
                "worker_sha256": controller.sha256(controller.WORKER),
                "worker_count": 2,
                "retry_count": 0,
                "discard_count": 0,
                "rows": rows,
                **evaluation,
            }
            dry_path.write_text(json.dumps(dry, indent=2) + "\n", encoding="utf-8")
            arguments = [
                "freeze", "--config", str(config_path),
                "--dry-run-summary", str(dry_path),
                "--output", str(prereg_path),
                "--transaction-id", "replication-test",
                "--replication-scope", "cross_gpu_reproducibility",
            ]
            with mock.patch.object(sys, "argv", arguments):
                self.assertEqual(freeze.main(), 0)
            prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
            self.assertEqual(prereg["formal_worker_count"], 16)
            self.assertFalse(prereg["formal_result_precommitted"])
            self.assertFalse(
                prereg["prior_transaction"]["pooled_into_this_replication"])
            controller._validate_formal_authority(
                config_path=config_path,
                config=_config(),
                prereg_path=prereg_path,
                dry_path=dry_path,
            )
            changed = _config()
            changed["common"]["worker_timeout_seconds"] = 901
            config_path.write_text(
                json.dumps(changed, indent=2) + "\n", encoding="utf-8")
            with self.assertRaises(PermissionError):
                controller._validate_formal_authority(
                    config_path=config_path,
                    config=changed,
                    prereg_path=prereg_path,
                    dry_path=dry_path,
                )

    def test_project_import_free_recount_reconstructs_all_raw_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config_path = root / "config.json"
            dry_path = root / "dry.json"
            prereg_path = root / "prereg.json"
            formal_root = root / "formal"
            recount_path = root / "recount.json"
            config = _config()
            config_path.write_text(
                json.dumps(config, indent=2) + "\n", encoding="utf-8")

            dry_rows = controller.build_schedule(config, mode="dry-run")
            for ordinal, row in enumerate(dry_rows):
                row.update({
                    "launch": {"return_code": 0, "timeout": False},
                    "worker": {
                        "status": "PASS",
                        "unit_id": controller.UNIT_ID,
                        "arm": row["arm"],
                        "endpoint": controller.ENDPOINT,
                        "formal_config_sha256": controller.sha256(config_path),
                        "retained_sample_count": 1,
                        "warmup_count": 0,
                        "retry_count": 0,
                        "discard_count": 0,
                        "input_identity": {"input": "fixed"},
                        "output_sha256": "same",
                        "primary_samples_ns": [100 + ordinal],
                    },
                })
            dry_evaluation = controller.evaluate(
                dry_rows,
                config_sha256=controller.sha256(config_path),
                formal=False,
            )
            dry = {
                "schema": controller.SUMMARY_SCHEMA,
                "mode": "dry-run",
                "status": "COMPLETE__DRY_RUN_PARITY_PASS",
                "formal_worker_zero_reached": False,
                "config_sha256": controller.sha256(config_path),
                "controller_sha256": controller.sha256(Path(controller.__file__)),
                "worker_sha256": controller.sha256(controller.WORKER),
                "worker_count": 2,
                "retry_count": 0,
                "discard_count": 0,
                "rows": dry_rows,
                **dry_evaluation,
            }
            dry_path.write_text(json.dumps(dry, indent=2) + "\n", encoding="utf-8")
            with mock.patch.object(sys, "argv", [
                "freeze", "--config", str(config_path),
                "--dry-run-summary", str(dry_path),
                "--output", str(prereg_path),
                "--transaction-id", "recount-test",
                "--replication-scope", "cross_gpu_reproducibility",
            ]):
                self.assertEqual(freeze.main(), 0)

            formal_root.mkdir()
            schedule = controller.schedule_payload(
                config_path, config, mode="formal")
            schedule_path = formal_root / "SCHEDULE.json"
            schedule_path.write_text(
                json.dumps(schedule, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            progress_rows = [{
                "event": "schedule_frozen",
                "worker_count": 16,
                "schedule_sha256": controller.sha256(schedule_path),
                "formal_worker_zero_reached": False,
            }]
            observed_rows = []
            for row in schedule["rows"]:
                ordinal = row["ordinal"]
                stem = (
                    f"w{ordinal:03d}__{controller.UNIT_ID}__"
                    f"{controller.ENDPOINT}__b{row['block']}__"
                    f"p{row['position']}__{row['arm']}"
                )
                paths = {
                    "stdout": formal_root / "stdout" / f"{stem}.bin",
                    "stderr": formal_root / "stderr" / f"{stem}.bin",
                    "output": formal_root / "workers" / f"{stem}.json",
                    "journal": formal_root / "journals" / f"{stem}.jsonl",
                }
                for path in paths.values():
                    path.parent.mkdir(parents=True, exist_ok=True)
                paths["stdout"].write_bytes(b"")
                paths["stderr"].write_bytes(b"")
                sample = 105 if row["arm"] == "new_v4" else 100
                journal_rows = [
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "worker_started", "pid": 10_000 + ordinal,
                     "arm": row["arm"], "unit_id": controller.UNIT_ID,
                     "endpoint": controller.ENDPOINT},
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "cpu_affinity_preflight",
                     "observation": {"cpu_ids": [8]}},
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "prepared", "prepare_ns": 2},
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "warmup_complete", "index": 0,
                     "output_sha256": "same"},
                    *[
                        {"schema": recount.JOURNAL_SCHEMA,
                         "event": "sample_complete", "index": index,
                         "elapsed_ns": sample, "output_sha256": "same"}
                        for index in range(3)
                    ],
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "close_complete", "close_ns": 3},
                    {"schema": recount.JOURNAL_SCHEMA,
                     "event": "cpu_affinity_postflight",
                     "observation": {"cpu_ids": [8]}},
                ]
                paths["journal"].write_text(
                    "".join(json.dumps(value, sort_keys=True) + "\n"
                            for value in journal_rows),
                    encoding="utf-8",
                )
                registered = config["implementations"][row["arm"]]
                worker = {
                    "status": "PASS",
                    "unit_id": controller.UNIT_ID,
                    "arm": row["arm"],
                    "endpoint": controller.ENDPOINT,
                    "formal_config_sha256": controller.sha256(config_path),
                    "formal_worker_sha256": controller.sha256(controller.WORKER),
                    "journal_sha256": controller.sha256(paths["journal"]),
                    "retry_count": 0,
                    "discard_count": 0,
                    "retained_sample_count": 3,
                    "warmup_count": 1,
                    "primary_samples_ns": [sample, sample, sample],
                    "primary_median_ns": sample,
                    "execute_samples_ns": [sample, sample, sample],
                    "input_identity": {"input": "fixed"},
                    "output_sha256": "same",
                    "outputs": [
                        {"matched": True, "output_sha256": "same"}
                        for _ in range(3)
                    ],
                    "phase_ns": {"load": 1, "prepare": 2, "close": 3},
                    "complete_timer_includes_prepare_execute_close": False,
                    "input_load_included_in_primary_timer": False,
                    "journal_io_included_in_primary_timer": False,
                    "process_id": 10_000 + ordinal,
                    "machine": {
                        **config["common"]["registered_machine"],
                        "hostname": "pod",
                        "platform": "Linux",
                        "python": config["common"]["python_version"],
                        "python_executable": config["common"]["python_executable"],
                        "cpu_affinity": {
                            "preflight": {"cpu_ids": [8]},
                            "postflight": {"cpu_ids": [8]},
                        },
                    },
                    "implementation_identity": {
                        **registered,
                        "source_status_clean": True,
                    },
                }
                paths["output"].write_text(
                    json.dumps(worker, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                launch = {
                    "return_code": 0,
                    "timeout": False,
                    "launch_error": None,
                }
                for name, path in paths.items():
                    launch[f"{name}_relative"] = path.relative_to(
                        formal_root).as_posix()
                    launch[f"{name}_sha256"] = controller.sha256(path)
                observed_rows.append({**row, "launch": launch, "worker": worker})
                progress_rows.append({
                    "event": "worker_complete",
                    "ordinal": ordinal,
                    "unit_id": controller.UNIT_ID,
                    "arm": row["arm"],
                    "endpoint": controller.ENDPOINT,
                    "return_code": 0,
                    "timeout": False,
                    "output_sha256": launch["output_sha256"],
                    "journal_sha256": launch["journal_sha256"],
                })
            progress_path = formal_root / "CONTROLLER_PROGRESS.jsonl"
            progress_path.write_text(
                "".join(json.dumps(value, sort_keys=True) + "\n"
                        for value in progress_rows),
                encoding="utf-8",
            )
            evaluation = controller.evaluate(
                observed_rows,
                config_sha256=controller.sha256(config_path),
                formal=True,
            )
            summary = {
                "schema": controller.SUMMARY_SCHEMA,
                "mode": "formal",
                "status": "COMPLETE__REPLICATION_TARGET_MET",
                "formal_worker_zero_reached": True,
                "config_sha256": controller.sha256(config_path),
                "controller_sha256": controller.sha256(Path(controller.__file__)),
                "worker_sha256": controller.sha256(controller.WORKER),
                "schedule_file_sha256": controller.sha256(schedule_path),
                "progress_file_sha256": controller.sha256(progress_path),
                "worker_count": 16,
                "retry_count": 0,
                "discard_count": 0,
                "rows": observed_rows,
                **evaluation,
            }
            (formal_root / "SUMMARY.json").write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(sys, "argv", [
                "recount", "--config", str(config_path),
                "--preregistration", str(prereg_path),
                "--dry-run-summary", str(dry_path),
                "--formal-root", str(formal_root),
                "--controller", str(Path(controller.__file__)),
                "--worker", str(controller.WORKER),
                "--output", str(recount_path),
            ]):
                self.assertEqual(recount.main(), 0)
            result = json.loads(recount_path.read_text(encoding="utf-8"))
            self.assertEqual(result["formal_worker_count"], 16)
            self.assertEqual(result["formal_cell_count"], 8)
            self.assertEqual(result["status"], "PASS__METHOD_AND_TARGET")
            self.assertFalse(result["prior_transaction_pooled"])


if __name__ == "__main__":
    unittest.main()
