from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import v4_paper_apps_pyoptix_controller as controller
from scripts import v4_paper_apps_pyoptix_make_config as make_config
from scripts import v4_paper_apps_pyoptix_recount as recount
from scripts import v4_paper_apps_pyoptix_worker as worker


class V4PaperAppsPyOptixHarnessTest(unittest.TestCase):
    def test_schedule_has_eight_balanced_fixed_orders(self) -> None:
        self.assertEqual(len(controller.BLOCK_ORDERS), 8)
        self.assertEqual(sum(order[0] == "v4" for order in controller.BLOCK_ORDERS), 4)
        self.assertEqual(
            sum(order[0] == "pyoptix" for order in controller.BLOCK_ORDERS), 4
        )
        self.assertEqual(len(controller.UNITS), 4)
        self.assertEqual(controller.ENDPOINTS, ("complete", "first_result", "prepared"))
        self.assertEqual(
            len(controller.UNITS)
            * len(controller.ENDPOINTS)
            * len(controller.BLOCK_ORDERS)
            * 2,
            192,
        )

    def test_worker_complete_boundary_excludes_load_and_includes_prepare_to_close(
        self,
    ) -> None:
        events: list[str] = []

        def load_input(app, config, *, operation):
            events.append("load")
            return {}, {"input_sha256": "0" * 64}

        def prepare_case(app, arm, config, data):
            events.append("prepare")

            def execute():
                events.append("execute")
                return {"matched": True, "output_sha256": "1" * 64}

            def close():
                events.append("close")

            return execute, close, {"path_class": "mock"}

        with (
            mock.patch.object(worker, "_load_input", load_input),
            mock.patch.object(worker, "_prepare_case", prepare_case),
        ):
            result = worker._run(
                app="particle_tracking",
                arm="v4",
                endpoint="complete",
                operation=None,
                config={},
                repetitions=1,
                warmups=0,
            )
        self.assertEqual(events, ["load", "prepare", "execute", "close"])
        self.assertTrue(result["complete_timer_includes_prepare_execute_close"])
        self.assertFalse(result["input_load_included_in_primary_timer"])
        self.assertEqual(result["retained_sample_count"], 1)
        self.assertGreaterEqual(
            result["primary_samples_ns"][0], result["execute_samples_ns"][0]
        )

    def test_worker_prepared_boundary_retains_every_execution(self) -> None:
        calls = 0

        def execute():
            nonlocal calls
            calls += 1
            return {"matched": True, "output_sha256": "2" * 64}

        with (
            mock.patch.object(
                worker, "_load_input", return_value=({}, {"input_sha256": "0" * 64})
            ),
            mock.patch.object(
                worker, "_prepare_case", return_value=(execute, lambda: None, {})
            ),
        ):
            result = worker._run(
                app="triangle_counting",
                arm="pyoptix",
                endpoint="prepared",
                operation=None,
                config={},
                repetitions=5,
                warmups=2,
            )
        self.assertEqual(calls, 7)
        self.assertEqual(result["retained_sample_count"], 5)
        self.assertEqual(len(result["execute_samples_ns"]), 5)
        self.assertFalse(result["complete_timer_includes_prepare_execute_close"])
        self.assertFalse(result["input_load_included_in_primary_timer"])

    def test_worker_rejects_endpoint_sample_drift(self) -> None:
        with self.assertRaises(ValueError):
            worker._run(
                app="librts",
                arm="v4",
                endpoint="first_result",
                operation="point_contains",
                config={},
                repetitions=2,
                warmups=0,
            )

    def test_config_accepts_multidigit_compute_capability(self) -> None:
        self.assertEqual(make_config._compute_capability("8.9"), (8, 9))
        self.assertEqual(make_config._compute_capability("12.0"), (12, 0))
        for value in ("89", "8", "8.x", "0.0", "12.10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_config._compute_capability(value)

    def test_runtime_identity_binding_fails_closed(self) -> None:
        observed = {
            "python_executable_sha256": "a" * 64,
            "python_version": "3.12.0",
            "package_versions": {"numpy": "2.4.4"},
            "pyoptix_loaded_extension_sha256": "b" * 64,
        }
        config = dict(observed)
        config.update(
            {
                "data_manifest_path": __file__,
                "data_manifest_sha256": worker._sha(__file__),
                "native_build_manifest_path": __file__,
                "native_build_manifest_sha256": worker._sha(__file__),
                "pyoptix_build_receipt_path": __file__,
                "pyoptix_build_receipt_sha256": worker._sha(__file__),
                "pyoptix_ptx_manifest_path": __file__,
                "pyoptix_ptx_manifest_sha256": worker._sha(__file__),
            }
        )
        worker._validate_runtime_identity("pyoptix", observed, config)
        bad = {**observed, "pyoptix_loaded_extension_sha256": "c" * 64}
        with self.assertRaises(RuntimeError):
            worker._validate_runtime_identity("pyoptix", bad, config)

    def test_prebuilt_pyoptix_ptx_is_hash_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "particle.ptx"
            path.write_bytes(b".version 8.0\n")
            config = {
                "pyoptix_prebuilt_ptx": {
                    "particle_tracking": {
                        "path": str(path),
                        "sha256": worker._sha(path),
                    }
                }
            }
            self.assertEqual(
                worker._prebuilt_ptx(config, "particle_tracking"),
                b".version 8.0\n",
            )
            path.write_bytes(b".version 9.0\n")
            with self.assertRaisesRegex(RuntimeError, "PTX differs"):
                worker._prebuilt_ptx(config, "particle_tracking")

    def test_formal_dry_run_binding_rejects_config_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "config.json"
            config.write_text("{}\n", encoding="utf-8")
            dry = {
                "schema": "rtdl.v4_paper_apps_pyoptix.dry_run.v1",
                "status": "PASS",
                "formal_worker_zero_reached": False,
                "config_sha256": "0" * 64,
            }
            with self.assertRaisesRegex(PermissionError, "formal config"):
                controller._validate_dry_run_authority(dry, config_path=config)

    def test_formal_dry_run_binding_reads_retained_worker_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.json"
            config.write_text("{}\n", encoding="utf-8")
            config_sha = controller._sha(config)
            records = []
            for app, operation, unit_id in controller.UNITS:
                arms = []
                for position, arm in enumerate(controller.ARMS):
                    path = root / f"{unit_id}__{arm}.json"
                    payload = {
                        "status": "PASS",
                        "output_sha256": unit_id,
                        "input_identity": {"unit_id": unit_id},
                        "retry_count": 0,
                        "discard_count": 0,
                        "process_id": 1000 + position,
                        "source_identity": {
                            "config_sha256": config_sha,
                            "worker_sha256": controller._sha(controller.WORKER),
                        },
                        "app": app,
                        "operation": operation,
                        "arm": arm,
                        "endpoint": "first_result",
                    }
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    arms.append(
                        {
                            "position": position,
                            "arm": arm,
                            "launch": {
                                "return_code": 0,
                                "command": [
                                    "python",
                                    "worker",
                                    "--config",
                                    str(config),
                                    "--app",
                                    app,
                                    "--arm",
                                    arm,
                                    "--endpoint",
                                    "first_result",
                                    "--repetitions",
                                    "1",
                                    "--warmups",
                                    "0",
                                    "--output",
                                    str(path),
                                ]
                                + (
                                    []
                                    if operation is None
                                    else ["--operation", operation]
                                ),
                            },
                            "worker": payload,
                        }
                    )
                records.append(
                    {
                        "unit_id": unit_id,
                        "app": app,
                        "operation": operation,
                        "valid": True,
                        "input_identity_parity": True,
                        "output_parity": True,
                        "workers": arms,
                    }
                )
            dry = {
                "schema": "rtdl.v4_paper_apps_pyoptix.dry_run.v1",
                "status": "PASS",
                "formal_worker_zero_reached": False,
                "unit_count": len(controller.UNITS),
                "records": records,
                "config_sha256": config_sha,
                "config_unchanged_during_dry_run": True,
                "worker_sha256": controller._sha(controller.WORKER),
                "worker_unchanged_during_dry_run": True,
                "retry_count": 0,
                "discard_count": 0,
            }
            registered = controller._validate_dry_run_authority(dry, config_path=config)
            self.assertEqual(
                registered,
                {
                    unit_id: {"unit_id": unit_id}
                    for _app, _operation, unit_id in controller.UNITS
                },
            )
            records[0]["workers"][0]["worker"] = {"status": "PASS"}
            with self.assertRaisesRegex(PermissionError, "retained bytes"):
                controller._validate_dry_run_authority(dry, config_path=config)

    def test_formal_dry_run_binding_rejects_input_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / "config.json"
            config.write_text("{}\n", encoding="utf-8")
            config_sha = controller._sha(config)
            records = []
            for app, operation, unit_id in controller.UNITS:
                arms = []
                for position, arm in enumerate(controller.ARMS):
                    path = root / f"{unit_id}__{arm}.json"
                    payload = {
                        "status": "PASS",
                        "output_sha256": unit_id,
                        "input_identity": {
                            "unit_id": unit_id,
                            "drift": position if unit_id == "particle_tracking" else 0,
                        },
                        "retry_count": 0,
                        "discard_count": 0,
                        "process_id": 1000 + position,
                        "source_identity": {
                            "config_sha256": config_sha,
                            "worker_sha256": controller._sha(controller.WORKER),
                        },
                        "app": app,
                        "operation": operation,
                        "arm": arm,
                        "endpoint": "first_result",
                    }
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    command = [
                        "python",
                        "worker",
                        "--config",
                        str(config),
                        "--app",
                        app,
                        "--arm",
                        arm,
                        "--endpoint",
                        "first_result",
                        "--repetitions",
                        "1",
                        "--warmups",
                        "0",
                        "--output",
                        str(path),
                    ]
                    if operation is not None:
                        command.extend(("--operation", operation))
                    arms.append(
                        {
                            "position": position,
                            "arm": arm,
                            "launch": {"return_code": 0, "command": command},
                            "worker": payload,
                        }
                    )
                records.append(
                    {
                        "unit_id": unit_id,
                        "app": app,
                        "operation": operation,
                        "valid": True,
                        "input_identity_parity": True,
                        "output_parity": True,
                        "workers": arms,
                    }
                )
            dry = {
                "schema": "rtdl.v4_paper_apps_pyoptix.dry_run.v1",
                "status": "PASS",
                "formal_worker_zero_reached": False,
                "unit_count": len(controller.UNITS),
                "records": records,
                "config_sha256": config_sha,
                "config_unchanged_during_dry_run": True,
                "worker_sha256": controller._sha(controller.WORKER),
                "worker_unchanged_during_dry_run": True,
                "retry_count": 0,
                "discard_count": 0,
            }
            with self.assertRaisesRegex(PermissionError, "input/output parity"):
                controller._validate_dry_run_authority(dry, config_path=config)

    def test_compact_traversal_projection_rejects_non_optix_receipt(self) -> None:
        receipt = {
            "schema": "rtdl.physical_execution.compact_traversal_receipt.v1",
            "receipt_sha256": "a" * 64,
            "physical_executor_classification": "optix_traversal_observed",
            "route_identity": "test-route",
            "expected_program_bundle": "test-bundle",
        }
        self.assertEqual(
            worker._traversal_projection(receipt)["receipt_sha256"], "a" * 64
        )
        receipt["physical_executor_classification"] = "host_fallback"
        with self.assertRaisesRegex(RuntimeError, "compact-auditable"):
            worker._traversal_projection(receipt)

    def test_worker_machine_identity_is_exactly_bound(self) -> None:
        observed = {
            "cuda_visible_devices": "0",
            "gpu": {
                "name": "NVIDIA Test",
                "uuid": "GPU-test",
                "compute_capability": "8.9",
                "driver": "580.1",
            },
        }
        worker._validate_machine_identity(observed, {"registered_machine": observed})
        changed = {
            **observed,
            "gpu": {**observed["gpu"], "uuid": "GPU-other"},
        }
        with self.assertRaisesRegex(RuntimeError, "machine differs"):
            worker._validate_machine_identity(changed, {"registered_machine": observed})

    def test_independent_recount_requires_the_complete_population(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "original"
            root.mkdir()
            config = root / "config.json"
            config.write_text("{}\n", encoding="utf-8")
            config_sha = recount._sha(config)
            machine = {
                "gpu": {
                    "name": "NVIDIA Test",
                    "uuid": "GPU-test",
                    "compute_capability": "8.9",
                    "driver": "580.1",
                },
                "cuda_visible_devices": "0",
            }
            source_commit = "a" * 40
            source_tree = "b" * 40
            worker_sha = "c" * 64
            prepared = {unit_id: 1 for _app, _operation, unit_id in recount.UNITS}
            registrations = []
            for app, operation, unit_id in recount.UNITS:
                for endpoint in recount.ENDPOINTS:
                    for block, order in enumerate(recount.BLOCK_ORDERS):
                        arm_rows = []
                        for position, arm in enumerate(order):
                            sample = 20 if arm == "v4" else 10
                            path = root / (
                                f"{unit_id}__{endpoint}__{block}__{arm}.json"
                            )
                            raw = {
                                "status": "PASS",
                                "app": app,
                                "operation": operation,
                                "arm": arm,
                                "endpoint": endpoint,
                                "retained_sample_count": 1,
                                "primary_samples_ns": [sample],
                                "execute_samples_ns": [sample],
                                "warmup_count": 0,
                                "retry_count": 0,
                                "discard_count": 0,
                                "process_id": 1000 + block * 2 + position,
                                "input_identity": {"unit_id": unit_id},
                                "output_sha256": unit_id,
                                "outputs": [
                                    {
                                        "matched": True,
                                        "output_sha256": unit_id,
                                        "compact_execution_evidence": {
                                            "kind": "unit-test",
                                        },
                                        "detailed_receipt_retention_count": 0,
                                        "public_output_materialized_inside_call": True,
                                    }
                                ],
                                "complete_timer_includes_prepare_execute_close": (
                                    endpoint == "complete"
                                ),
                                "input_load_included_in_primary_timer": False,
                                "machine": {
                                    **machine,
                                    "hostname": "test-host",
                                },
                                "source_identity": {
                                    "config_sha256": config_sha,
                                    "git_commit": source_commit,
                                    "git_tree": source_tree,
                                    "git_status_clean": True,
                                    "worker_sha256": worker_sha,
                                },
                            }
                            path.write_text(json.dumps(raw), encoding="utf-8")
                            command = [
                                "python",
                                "worker",
                                "--app",
                                app,
                                "--arm",
                                arm,
                                "--endpoint",
                                endpoint,
                                "--repetitions",
                                "1",
                                "--warmups",
                                "0",
                                "--output",
                                str(path),
                            ] + (
                                [] if operation is None else ["--operation", operation]
                            )
                            arm_rows.append(
                                {
                                    "position": position,
                                    "arm": arm,
                                    "launch": {
                                        "return_code": 0,
                                        "command": command,
                                    },
                                    "worker_output_relative": path.name,
                                    "worker": raw,
                                }
                            )
                        registrations.append(
                            {
                                "unit_id": unit_id,
                                "app": app,
                                "operation": operation,
                                "endpoint": endpoint,
                                "block": block,
                                "order": list(order),
                                "workers": arm_rows,
                                "pair": {
                                    "valid": True,
                                    "output_sha256": unit_id,
                                    "v4_median_ns": 20,
                                    "pyoptix_median_ns": 10,
                                    "v4_over_pyoptix": 2.0,
                                },
                            }
                        )
            evaluations = [
                {
                    "key": f"{unit_id}::{endpoint}",
                    "valid": True,
                    "valid_block_count": 8,
                    "registered_block_count": 8,
                    "median_v4_over_pyoptix": 2.0,
                    "min_v4_over_pyoptix": 2.0,
                    "max_v4_over_pyoptix": 2.0,
                }
                for _app, _operation, unit_id in recount.UNITS
                for endpoint in recount.ENDPOINTS
            ]
            evaluations.sort(key=lambda row: row["key"])
            formal = {
                "schema": "rtdl.v4_paper_apps_pyoptix.formal_transaction.v1",
                "status": "PASS",
                "source_commit": source_commit,
                "source_tree": source_tree,
                "worker_sha256": worker_sha,
                "config_sha256": config_sha,
                "source_unchanged_during_transaction": True,
                "config_unchanged_during_transaction": True,
                "registered_machine": machine,
                "registered_prepared_repetitions": prepared,
                "registered_prepared_warmups": 0,
                "registered_input_identities": {
                    unit_id: {"unit_id": unit_id}
                    for _app, _operation, unit_id in recount.UNITS
                },
                "formal_worker_zero_reached": True,
                "block_orders": [list(row) for row in recount.BLOCK_ORDERS],
                "registered_pair_count": len(registrations),
                "worker_process_count": len(registrations) * 2,
                "retry_count": 0,
                "discard_count": 0,
                "registrations": registrations,
                "evaluations": evaluations,
            }
            formal_path = root / "formal.json"
            formal_path.write_text(json.dumps(formal), encoding="utf-8")
            rebuilt = recount.recount(formal_path)
            self.assertEqual(rebuilt["worker_file_count"], 192)
            self.assertEqual(len(rebuilt["recomputed_pairs"]), 96)

            relocated = Path(temporary) / "relocated"
            shutil.copytree(root, relocated)
            relocated_recount = recount.recount(relocated / "formal.json")
            self.assertEqual(relocated_recount["worker_file_count"], 192)

            first_arm = formal["registrations"][0]["workers"][0]
            first_path = recount._retained_worker_path(
                root,
                first_arm["worker_output_relative"],
                first_arm["launch"]["command"],
            )
            original_worker = first_arm["worker"]
            drifted_worker = {
                **original_worker,
                "input_identity": {"unit_id": "post-dry-run-drift"},
            }
            first_arm["worker"] = drifted_worker
            first_path.write_text(json.dumps(drifted_worker), encoding="utf-8")
            drifted = root / "drifted.json"
            drifted.write_text(json.dumps(formal), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "worker contract"):
                recount.recount(drifted)
            first_arm["worker"] = original_worker
            first_path.write_text(json.dumps(original_worker), encoding="utf-8")

            duplicate_source = formal["registrations"][1]["workers"][0]
            original_command = duplicate_source["launch"]["command"]
            original_relative = duplicate_source["worker_output_relative"]
            duplicate_source["launch"]["command"] = first_arm["launch"]["command"]
            duplicate_source["worker_output_relative"] = first_arm[
                "worker_output_relative"
            ]
            duplicated = root / "duplicated.json"
            duplicated.write_text(json.dumps(formal), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "reuses a worker output path"):
                recount.recount(duplicated)
            duplicate_source["launch"]["command"] = original_command
            duplicate_source["worker_output_relative"] = original_relative

            formal["registrations"] = formal["registrations"][:-1]
            incomplete = root / "incomplete.json"
            incomplete.write_text(json.dumps(formal), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "population"):
                recount.recount(incomplete)


if __name__ == "__main__":
    unittest.main()
