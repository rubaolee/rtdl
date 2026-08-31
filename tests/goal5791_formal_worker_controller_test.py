from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.goal5791_formal_contract import digest, schedule
from scripts import goal5791_formal_controller as controller
from scripts import goal5791_formal_worker as worker


SHA = "a" * 64


class _Clock:
    def __init__(self) -> None:
        self.value = 0

    def __call__(self) -> int:
        self.value += 1_000_000_000
        return self.value


def _target_probe_runner(command, **kwargs):
    if command != [
        "/usr/bin/nvidia-smi",
        "--query-gpu=uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ]:
        raise AssertionError(f"unexpected target probe command: {command}")
    if (
        "CUPY_CACHE_DIR" in kwargs["env"]
        or "NUMBA_CACHE_DIR" in kwargs["env"]
        or len(kwargs["env"]) != 14
    ):
        raise AssertionError("target probe environment is not exact 14-key")
    return mock.Mock(
        stdout="GPU-goal5791-controller-test, test-driver, 8.9\n",
        returncode=0,
    )


def _formal_controller_environment(source_root: Path) -> dict[str, str]:
    values = {
        name: "frozen" for name in worker.FORMAL_WORKER_ENVIRONMENT_KEYS
    }
    values.update({
        "PYTHONPATH": os.pathsep.join((
            str(source_root / "src"), str(source_root),
            str(source_root / "scripts"),
        )),
        "PATH": os.pathsep.join((str(source_root / "venv" / "bin"),
                                  "/usr/bin", "/bin")),
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "LC_ALL": "C.UTF-8",
        "LD_PRELOAD": "",
    })
    return values


def _process_state_observer(phase: str) -> dict[str, object]:
    return controller._observe_no_gpu_product_process_state(
        phase=phase,
        module_names={"argparse", "json", "os", "sys"},
        proc_self_maps_bytes=(
            b"1000-2000 r-xp 00000000 00:00 0 /usr/bin/python3\n"),
    )


def _freeze_control_files(root: Path) -> None:
    for name in ("runtime.json", "pre.json", "formal.json"):
        os.chmod(root / name, stat.S_IREAD)


def _authority(repository_root: Path, output_root: Path):
    target = {
        "binding_sha256": "b" * 64,
        "hashes": {"formal_identity_sha256": "c" * 64},
        "versions": {
            "gpu_uuid": "GPU-goal5791-controller-test",
            "driver_version": "test-driver",
            "compute_capability": "8.9",
        },
    }
    records = {}
    for role in controller.AUTHORITY_ROLES:
        name = "data.json" if role == "data_authority" else f"{role}.json"
        path = repository_root / name
        path.write_text(json.dumps({"role": role}) + "\n")
        records[role] = {
            "path": name,
            "sha256": worker.file_sha256(path),
            "bytes": path.stat().st_size,
        }
    pre = {
        "authority_sha256": "d" * 64,
        "dataset_input_sha256": {
            name: chr(ord("e") + index) * 64
            for index, name in enumerate(worker.DATASET_IDS)
        },
        "oracle_authority_sha256": {
            name: chr(ord("h") + index) * 64
            for index, name in enumerate(worker.DATASET_IDS)
        },
        "authority_records": records,
    }
    materialization_root = (
        repository_root.parent
        if repository_root.name == "source" else repository_root
    ).resolve()
    formal_output_root = output_root.resolve()
    formal_staging_root = formal_output_root.with_name(
        f".{formal_output_root.name}.goal5791_incomplete")
    formal = {
        "authority_sha256": "m" * 64,
        "execution_target": {
            "target_materialization_root": str(materialization_root),
            "create_only_formal_output_root": str(formal_output_root),
            "controller_incomplete_staging_root": str(formal_staging_root),
            "target_materialization_root_observed_existing_and_bound_at_authority_creation": True,
            "formal_output_root_observed_absent_at_authority_creation": True,
            "controller_incomplete_staging_root_observed_absent_at_authority_creation": True,
            "preexisting_or_shared_formal_output_root_allowed": False,
            "pod_endpoint": {},
        },
        "resource_confirmation": {
            "owner_confirmed_uninterrupted_window_hours": 7.0,
            "confirmed_free_disk_bytes": 25_000_000_000,
            "confirmed_before_formal_worker_zero": True,
            "formal_output_parent_resolved_path": str(
                formal_output_root.parent),
            "formal_output_parent_free_bytes_observed_at_authority_creation": (
                30_000_000_000),
            "minimum_required_free_disk_bytes": 20_000_000_000,
        },
    }
    pre_path = repository_root / "pre.json"
    formal_path = repository_root / "formal.json"
    pre_path.write_text(json.dumps(pre) + "\n")
    formal_path.write_text(json.dumps(formal) + "\n")
    return worker.WorkerAuthorityContext(
        preexecution=pre,
        formal=formal,
        preexecution_file_sha256=worker.file_sha256(pre_path),
        formal_authority_file_sha256=worker.file_sha256(formal_path),
        target_binding=target,
        repository_root=repository_root,
    )


def _data_authority(authority) -> dict[str, object]:
    return {
        "authority_sha256": "p" * 64,
        "datasets": {
            name: {
                "sha256": authority.preexecution[
                    "dataset_input_sha256"][name],
                "bytes": 8,
                "expected_triangle_count": 7,
                "oracle_authority_sha256": authority.preexecution[
                    "oracle_authority_sha256"][name],
            }
            for name in worker.DATASET_IDS
        },
    }


def _runtime(root: Path, authority) -> dict[str, object]:
    formal_environment = {
        name: "frozen" for name in worker.FORMAL_WORKER_ENVIRONMENT_KEYS
    }
    formal_environment["LD_PRELOAD"] = ""
    formal_environment["PYTHONHASHSEED"] = "0"
    formal_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    formal_environment["PYTHONNOUSERSITE"] = "1"
    formal_environment["LC_ALL"] = "C.UTF-8"
    target_path = root / "target.json"
    if not target_path.exists():
        target_path.write_text("{}\n")
    runtime_path = root / "runtime.json"
    runtime_path.write_text("{}\n")
    authority.formal["runtime_file_sha256"] = worker.file_sha256(runtime_path)
    authority.formal["runtime_sha256"] = "q" * 64
    formal_sources = {
        name: "u" * 64 for name in worker.FORMAL_SOURCE_PATHS
    }
    return {
        "runtime_sha256": "q" * 64,
        "runtime_budget_authority_sha256": "l" * 64,
        "target_materialization_authority_file_sha256": worker.file_sha256(
            target_path),
        "formal_conservative_budget_seconds": 10_000.0,
        "worker_timeout_seconds": 30.0,
        "python_executable": sys.executable,
        "llvmlite_version": "0.47.0",
        "execution_source_root": str(root),
        "execution_source_manifest_path": str(root / "source_manifest.json"),
        "execution_source_manifest_file_sha256": "v" * 64,
        "formal_identity_record": {"formal_sources": formal_sources},
        "target_materialization_authority_path": str(root / "target.json"),
        "formal_worker_environment": formal_environment,
        "neutral_prewarm": {"input_sha256": SHA},
        "datasets": {
            name: {
                "edge_path": str(root / f"{name}.edge"),
                "input_sha256": authority.preexecution[
                    "dataset_input_sha256"][name],
                "size_bytes": 8,
                "expected_triangle_count": 7,
                "oracle_authority_sha256": authority.preexecution[
                    "oracle_authority_sha256"][name],
            }
            for name in worker.DATASET_IDS
        },
    }


def _admission(runtime, authority, data) -> dict[str, object]:
    rows = {}
    for name in worker.DATASET_IDS:
        path = Path(runtime["datasets"][name]["edge_path"])
        mode = path.stat().st_mode if path.exists() else stat.S_IFREG | 0o444
        rows[name] = {
            "resolved_path": str(path.resolve()),
            "sha256": data["datasets"][name]["sha256"],
            "bytes": 8,
            "st_dev": 1,
            "st_ino": 2,
            "st_mtime_ns": 3,
            "st_mode": mode,
            "read_only": True,
            "full_rehash_complete": True,
        }
    return {"admission_sha256": "s" * 64, "datasets": rows}


def _source_admission(runtime, authority) -> dict[str, object]:
    source_root = Path(runtime["execution_source_root"]).resolve()
    loaded_sources = {
        name: {
            "resolved_path": str(source_root / Path(*name.split("/"))),
            "file_sha256": runtime["formal_identity_record"][
                "formal_sources"][name],
        }
        for name in controller.CONTROLLER_BOOTSTRAP_SOURCE_PATHS
    }
    return {
        "admission_sha256": "t" * 64,
        "runtime_file_sha256": authority.formal["runtime_file_sha256"],
        "runtime_sha256": runtime["runtime_sha256"],
        "controller_bootstrap_observation": {
            "schema": controller.CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA,
            "controller_environment_sha256": digest(
                runtime["formal_worker_environment"]),
            "controller_environment_exact_frozen_14_keys_verified": True,
            "controller_environment_key_count": 14,
            "controller_cupy_cache_dir_absent": True,
            "preimport_stdlib_bootstrap_verified": True,
            "loaded_harness_sources": loaded_sources,
            "loaded_harness_paths_and_hashes_match_formal_identity_record": True,
            "cuda_context_or_product_import_used": False,
            "completed_after_transaction_marker_before_worker_zero": True,
        },
        "execution_source_root": str(Path(runtime["execution_source_root"]).resolve()),
        "execution_source_manifest_file_sha256": "v" * 64,
        "execution_source_tree_sha256": "w" * 64,
        "manifest_payload_count": 1,
        "manifest_payload_bytes": 1,
        "full_manifest_rehash_complete": True,
        "all_manifest_payloads_read_only": True,
        "manifest_file_read_only": True,
        "exact_regular_file_set_verified": True,
        "exact_implied_directory_set_verified": True,
        "unmanifested_path_count": 0,
        "missing_manifest_payload_count": 0,
        "symlink_or_special_path_count": 0,
        "all_source_paths_without_write_bits": True,
        "regular_file_count": 2,
        "source_directory_count_including_root": 4,
        "source_path_count": 6,
    }


class _FakeBackend:
    log: list[str] = []
    cache: Path | None = None
    lifecycle = ""
    fail_execute = False

    def __init__(self, *, worker_spec, **_kwargs) -> None:
        type(self).lifecycle = str(worker_spec["lifecycle"])

    def load(self) -> None:
        self.log.append("loading")

    def prepare(self) -> None:
        self.log.append("preparation")

    def prewarm(self) -> None:
        self.log.append("prewarm")
        (self.cache / "off_then_on.cache").write_text("prepared")

    def execute(self) -> None:
        self.log.append("execute")
        if self.fail_execute:
            raise RuntimeError("terminal mock failure")
        (self.cache / "selected.cache").write_text("compiled in execute")

    def close(self) -> None:
        self.log.append("close")

    def seal(self) -> dict[str, object]:
        self.log.append("seal")
        prewarm = (
            {
                "performed": True,
                "order": [worker.FUSION_OFF, worker.FUSION_ON],
                "input_sha256": SHA,
                "rows": [
                    {
                        "variant": variant,
                        "token_pre_admitted_in_preparation": True,
                        "token_consumed_once": True,
                        "launch_completed": True,
                        "synchronized": True,
                        "device_pool_freed": True,
                        "output_exact": True,
                        "formal_evidence_created": False,
                    }
                    for variant in (worker.FUSION_OFF, worker.FUSION_ON)
                ],
            }
            if self.lifecycle == worker.PREPARED
            else {"performed": False, "order": [], "rows": []}
        )
        input_receipt = {
            "schema": "rtdl.goal5791.worker_input_file_receipt.v1",
            "dataset_id": "com_dblp",
            "resolved_path": "mock",
            "bytes": 8,
            "st_dev": 1,
            "st_ino": 2,
            "st_mtime_ns": 3,
            "st_mode": stat.S_IFREG | 0o444,
            "read_only": True,
            "observed_before_loader_read": True,
            "pre_and_post_loader_fstat_equal": True,
            "proc_self_fd_used": False,
        }
        input_receipt["receipt_sha256"] = digest(input_receipt)
        return {
            "output_scalar_u64": 7,
            "output_sha256": digest(7),
            "oracle_output_scalar_u64": 7,
            "oracle_output_sha256": digest(7),
            "segment_evidence": [{"mock": True}],
            "segment_count": 1,
            "prewarm_receipt": prewarm,
            "input_file_receipt": input_receipt,
        }

    def abort(self) -> None:
        self.log.append("abort")


class Goal5791FormalWorkerControllerTest(unittest.TestCase):
    def _run_mock_worker(self, *, worker_index: int, fail: bool = False):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        output_root = root / "formal"
        authority = _authority(root, output_root)
        data = _data_authority(authority)
        runtime = _runtime(root, authority)
        for name in worker.DATASET_IDS:
            Path(runtime["datasets"][name]["edge_path"]).write_bytes(b"12345678")
        admission = _admission(runtime, authority, data)
        source_admission = _source_admission(runtime, authority)
        cache = root / f"worker_{worker_index:04d}"
        cache.mkdir()
        (cache / "cupy").mkdir()
        (cache / "numba").mkdir()
        output_parent = root / "workers"
        output_parent.mkdir()
        output = output_parent / f"worker_{worker_index:04d}.json"
        _FakeBackend.log = []
        _FakeBackend.cache = cache / "cupy"
        _FakeBackend.fail_execute = fail
        patches = (
            mock.patch.object(worker, "_load_authority_context", return_value=authority),
            mock.patch.object(
                worker, "_load_data_authority", return_value=(data, root / "data.json")),
            mock.patch.object(worker, "_validate_runtime", return_value=runtime),
            mock.patch.object(worker, "_load_data_admission", return_value=admission),
            mock.patch.object(
                worker, "_load_source_admission", return_value=source_admission),
            mock.patch.object(
                worker, "_rehash_execution_source_manifest",
                return_value={name: source_admission[name] for name in (
                    "execution_source_root",
                    "execution_source_manifest_file_sha256",
                    "execution_source_tree_sha256", "manifest_payload_count",
                    "manifest_payload_bytes", "full_manifest_rehash_complete",
                    "all_manifest_payloads_read_only", "manifest_file_read_only",
                    "exact_regular_file_set_verified",
                    "exact_implied_directory_set_verified",
                    "unmanifested_path_count",
                    "missing_manifest_payload_count",
                    "symlink_or_special_path_count",
                    "all_source_paths_without_write_bits",
                    "regular_file_count",
                    "source_directory_count_including_root",
                    "source_path_count",
                )},
            ),
        )
        exact_environment = dict(runtime["formal_worker_environment"])
        exact_environment["CUPY_CACHE_DIR"] = str(cache / "cupy")
        exact_environment["NUMBA_CACHE_DIR"] = str(cache / "numba")
        with patches[0], patches[1], patches[2], patches[3], patches[4], \
                patches[5], mock.patch.dict(
            os.environ, exact_environment, clear=True
        ):
            if fail:
                with self.assertRaisesRegex(RuntimeError, "terminal mock failure"):
                    worker.run_worker(
                        repository_root=root,
                        runtime_path=root / "runtime.json",
                        preexecution_path=root / "pre.json",
                        formal_authority_path=root / "formal.json",
                        data_admission_path=root / "admission.json",
                        source_admission_path=root / "source_admission.json",
                        cache_dir=cache,
                        worker_index=worker_index,
                        output=output,
                        backend_factory=_FakeBackend,
                        clock_ns=_Clock(),
                    )
            else:
                worker.run_worker(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    data_admission_path=root / "admission.json",
                    source_admission_path=root / "source_admission.json",
                    cache_dir=cache,
                    worker_index=worker_index,
                    output=output,
                    backend_factory=_FakeBackend,
                    clock_ns=_Clock(),
                )
        return output

    def test_cold_and_prepared_phase_token_cache_and_seal_boundaries(self) -> None:
        for index, expected_log in (
            (0, ["loading", "preparation", "execute", "close", "seal"]),
            (6, ["loading", "preparation", "prewarm", "execute", "close", "seal"]),
        ):
            with self.subTest(worker_index=index):
                output = self._run_mock_worker(worker_index=index)
                value = json.loads(output.read_text())
                self.assertEqual(_FakeBackend.log, expected_log)
                self.assertEqual(value["status"], "COMPLETE")
                self.assertEqual(
                    list(value["phase_seconds"]),
                    ["close", "execute", "loading", "preparation", "prewarm"],
                )
                self.assertEqual(
                    [row["phase"] for row in value["phase_sequence"]],
                    ["loading", "preparation", "prewarm", "execute", "close"],
                )
                for left, right in zip(
                    value["phase_sequence"], value["phase_sequence"][1:]
                ):
                    self.assertLessEqual(left["ended_ns"], right["started_ns"])
                self.assertTrue(value[
                    "registered_endpoint_is_one_continuous_interval"])
                self.assertTrue(value[
                    "constant_time_pre_admitted_token_binding_only_inside_execute"])
                self.assertFalse(value["deep_verification_inside_execute"])
                self.assertFalse(value[
                    "evidence_hashing_or_serialization_inside_registered_timer"])
                unsigned = dict(value)
                claimed = unsigned.pop("worker_sha256")
                self.assertEqual(claimed, digest(unsigned))
                if index == 0:
                    continuous_cold_seconds = (
                        value["phase_sequence"][-1]["ended_ns"]
                        - value["phase_sequence"][0]["started_ns"]
                    ) / 1_000_000_000.0
                    raw_phase_sum = sum(value["phase_seconds"].values())
                    self.assertEqual(
                        value["registered_complete_endpoint_seconds"],
                        continuous_cold_seconds,
                    )
                    # The sentinel clock leaves one-second gaps between each
                    # timed phase, so this proves the endpoint is not the old
                    # gap-dropping sum of phase durations.
                    self.assertGreater(continuous_cold_seconds, raw_phase_sum)
                    self.assertTrue(value[
                        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check"])
                    self.assertEqual(value["phase_seconds"]["prewarm"], 0.0)
                    self.assertTrue(value["cache_receipt"][
                        "selected_recipe_first_compile_inside_execute"])
                    self.assertFalse(value["prewarm_receipt"]["performed"])
                else:
                    self.assertEqual(
                        value["registered_complete_endpoint_seconds"],
                        value["phase_seconds"]["execute"],
                    )
                    self.assertFalse(value[
                        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check"])
                    self.assertGreater(value["phase_seconds"]["prewarm"], 0.0)
                    self.assertEqual(
                        value["prewarm_receipt"]["order"],
                        [worker.FUSION_OFF, worker.FUSION_ON],
                    )
                    self.assertTrue(value["cache_receipt"][
                        "measurement_started_after_both_prewarms"])
                    self.assertTrue(value["cache_receipt"][
                        "prepared_same_worker_cache_contains_both_variant_recipes"])
                self.assertFalse(value["cache_receipt"][
                    "shared_between_workers_or_measured_arms"])
                self.assertNotIn(
                    "shared_between_workers_or_variants",
                    value["cache_receipt"],
                )
                # Exact call order makes evidence sealing observably later than
                # close, whose ended_ns is the cold endpoint's terminal stamp.
                self.assertEqual(_FakeBackend.log[-2:], ["close", "seal"])
                self.assertTrue(value[
                    "evidence_seal_started_after_registered_endpoint"])

    def test_failed_worker_and_authority_attack_create_no_output(self) -> None:
        failed = self._run_mock_worker(worker_index=0, fail=True)
        self.assertFalse(failed.exists())
        self.assertIn("abort", _FakeBackend.log)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cache = root / "worker_0000"
            cache.mkdir()
            (cache / "cupy").mkdir()
            (cache / "numba").mkdir()
            workers = root / "workers"
            workers.mkdir()
            os.environ["CUPY_CACHE_DIR"] = str(cache / "cupy")
            os.environ["NUMBA_CACHE_DIR"] = str(cache / "numba")
            with mock.patch.object(
                worker,
                "_load_authority_context",
                side_effect=worker.Goal5791WorkerError("resigned authority drift"),
            ):
                with self.assertRaisesRegex(Exception, "authority drift"):
                    worker.run_worker(
                        repository_root=root,
                        runtime_path=root / "runtime.json",
                        preexecution_path=root / "pre.json",
                        formal_authority_path=root / "formal.json",
                        data_admission_path=root / "admission.json",
                        source_admission_path=root / "source_admission.json",
                        cache_dir=cache,
                        worker_index=0,
                        output=workers / "worker_0000.json",
                    )
            self.assertFalse((workers / "worker_0000.json").exists())
            os.environ.pop("CUPY_CACHE_DIR", None)
            os.environ.pop("NUMBA_CACHE_DIR", None)

    def test_live_worker_environment_is_an_exact_allowlist(self) -> None:
        self.assertEqual(len(worker.FORMAL_WORKER_ENVIRONMENT_KEYS), 14)
        self.assertEqual(
            worker.FORMAL_WORKER_DYNAMIC_ENVIRONMENT_KEYS,
            ("CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = _authority(root, root / "formal")
            runtime = _runtime(root, authority)
            cache = root / "worker_0000"
            cache.mkdir()
            (cache / "cupy").mkdir()
            (cache / "numba").mkdir()
            expected = dict(runtime["formal_worker_environment"])
            expected["CUPY_CACHE_DIR"] = str((cache / "cupy").resolve())
            expected["NUMBA_CACHE_DIR"] = str((cache / "numba").resolve())
            self.assertEqual(len(expected), 16)
            worker._validate_formal_worker_environment(
                runtime["formal_worker_environment"],
                native=Path("frozen").resolve(),
            )
            with mock.patch.dict(os.environ, expected, clear=True):
                worker._validate_live_worker_environment(
                    runtime, cache_dir=cache.resolve())
            poisoned = dict(expected)
            poisoned["CUDA_VISIBLE_DEVICES"] = "7"
            with mock.patch.dict(os.environ, poisoned, clear=True):
                with self.assertRaisesRegex(Exception, "exact allowlist"):
                    worker._validate_live_worker_environment(
                        runtime, cache_dir=cache.resolve())
            empty_other = dict(runtime["formal_worker_environment"])
            empty_other["CUDA_HOME"] = ""
            with self.assertRaisesRegex(Exception, "malformed"):
                worker._validate_formal_worker_environment(
                    empty_other, native=Path("frozen").resolve())
            nonempty_preload = dict(runtime["formal_worker_environment"])
            nonempty_preload["LD_PRELOAD"] = "foreign.so"
            with self.assertRaisesRegex(Exception, "policy drifted"):
                worker._validate_formal_worker_environment(
                    nonempty_preload, native=Path("frozen").resolve())
            missing_locale = dict(runtime["formal_worker_environment"])
            del missing_locale["LC_ALL"]
            with self.assertRaisesRegex(Exception, "malformed"):
                worker._validate_formal_worker_environment(
                    missing_locale, native=Path("frozen").resolve())
            injected_locale = dict(expected)
            injected_locale["LC_CTYPE"] = "C.UTF-8"
            with mock.patch.dict(os.environ, injected_locale, clear=True):
                with self.assertRaisesRegex(Exception, "exact allowlist"):
                    worker._validate_live_worker_environment(
                        runtime, cache_dir=cache.resolve())

            # A real fresh cache-selecting Python subprocess must place its
            # payload only in the private, source-external NUMBA_CACHE_DIR.
            # Stage-A separately exercises the real target Numba stack.  Run
            # two schedule-shaped roots sequentially to reproduce the exact
            # worker-0 -> worker-1 mutation boundary caught on the POD.
            module_root = root / "sealed_source"
            module_root.mkdir()
            module = module_root / "numba_cache_probe.py"
            module.write_text(
                "import os\n"
                "from pathlib import Path\n"
                "def increment(value):\n"
                "    root = Path(os.environ['NUMBA_CACHE_DIR'])\n"
                "    root.joinpath('probe.cache').write_text('external')\n"
                "    return value + 1\n",
                encoding="utf-8",
            )
            source_before = {
                path.relative_to(module_root).as_posix(): path.read_bytes()
                for path in module_root.rglob("*") if path.is_file()
            }
            for index in range(2):
                process_root = root / f"subprocess_worker_{index:04d}"
                cupy = process_root / "cupy"
                numba = process_root / "numba"
                cupy.mkdir(parents=True)
                numba.mkdir()
                child_environment = dict(os.environ)
                child_environment.update({
                    "PYTHONPATH": str(module_root),
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "CUPY_CACHE_DIR": str(cupy),
                    "NUMBA_CACHE_DIR": str(numba),
                })
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "import numba_cache_probe as p; print(p.increment(41))",
                    ],
                    env=child_environment,
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                self.assertEqual(completed.stdout.strip(), "42")
                self.assertTrue(any(path.is_file() for path in numba.rglob("*")))
            source_after = {
                path.relative_to(module_root).as_posix(): path.read_bytes()
                for path in module_root.rglob("*") if path.is_file()
            }
            self.assertEqual(source_after, source_before)
            self.assertFalse((module_root / "__pycache__").exists())

    def test_production_execute_has_no_digest_or_deep_plan_verification(self) -> None:
        source = Path(worker.__file__).read_text(encoding="utf-8")
        begin = source.index("    def execute(self) -> None:", source.index(
            "class _ProductionBackend"))
        end = source.index("    def close(self) -> None:", begin)
        body = source[begin:end]
        self.assertIn("execute_segment_unsealed", body)
        self.assertIn("fusion_execution_token=token", body)
        self.assertNotIn("digest(", body)
        self.assertNotIn("verify_fusion_ablation_plan", body)
        self.assertNotIn("operation_contract", body)

    def test_segment_plan_input_binds_source_bytes_not_only_descriptor(self) -> None:
        descriptor = {
            "schema": "rtdl.goal5791.rt2a1_segment_descriptor.v1",
            "segment_id": 0,
        }
        left = worker._ProductionBackend._segment_plan_input_binding(
            descriptor=descriptor,
            source_input_sha256="a" * 64,
            formal_input=True,
        )
        right = worker._ProductionBackend._segment_plan_input_binding(
            descriptor=descriptor,
            source_input_sha256="b" * 64,
            formal_input=True,
        )
        neutral = worker._ProductionBackend._segment_plan_input_binding(
            descriptor=descriptor,
            source_input_sha256="a" * 64,
            formal_input=False,
        )
        self.assertNotEqual(digest(left), digest(right))
        self.assertNotEqual(digest(left), digest(neutral))
        self.assertEqual(left["segment_descriptor_sha256"], digest(descriptor))
        self.assertTrue(left["formal_input"])
        with self.assertRaisesRegex(Exception, "exact boolean"):
            worker._ProductionBackend._segment_plan_input_binding(
                descriptor=descriptor,
                source_input_sha256="a" * 64,
                formal_input=1,
            )

    def test_production_preparation_admits_descriptor_and_input_separately(self) -> None:
        descriptor = {
            "schema": "rtdl.goal5791.rt2a1_segment_descriptor.v1",
            "segment_id": 0,
            "primitive_count": 2,
            "query_count": 3,
        }

        class Plan:
            def __init__(self, input_sha256: str) -> None:
                self.input_sha256 = input_sha256

        class Token:
            state = "fresh"

            def __init__(self, plan_input_sha256: str) -> None:
                self.plan_input_sha256 = plan_input_sha256

        class Executor:
            def __init__(self) -> None:
                self.calls: list[dict[str, object]] = []

            def admit_fusion_execution_token(self, plan, **kwargs):
                self.calls.append({"plan": plan, **kwargs})
                return Token(str(kwargs["plan_input_binding_sha256"]))

        runtime = {
            "datasets": {"com_dblp": {"input_sha256": "a" * 64}},
            "neutral_prewarm": {
                "input_sha256": "b" * 64,
                "expected_triangle_count": 4,
            },
            "max_relation_rows": 1_000_000,
        }
        authority = mock.Mock(formal_authority_file_sha256="c" * 64)
        backend = worker._ProductionBackend(
            runtime=runtime,
            authority=authority,
            worker_spec={
                "dataset_id": "com_dblp",
                "lifecycle": worker.PREPARED,
                "variant": worker.FUSION_ON,
                "worker_index": 6,
            },
            data_admission={},
        )
        backend.graph = object()
        backend.prewarm_graph = object()
        executor = Executor()

        def build_plan(_descriptor, _variant, *, formal_input, **_kwargs):
            binding = backend._segment_plan_input_binding(
                descriptor=_descriptor,
                source_input_sha256=(
                    "a" * 64 if formal_input else "b" * 64),
                formal_input=formal_input,
            )
            return Plan(digest(binding)), binding

        with mock.patch.object(
            backend, "_validate_product_target_authority"
        ), mock.patch.object(
            backend, "_compile_executor", return_value=executor
        ), mock.patch.object(
            backend, "_validate_executor_identity"
        ), mock.patch.object(
            backend, "_build_plan", side_effect=build_plan
        ), mock.patch(
            "scripts.goal5791_segment_descriptors.iter_rt2a1_segment_descriptors",
            side_effect=(iter([descriptor]), iter([descriptor])),
        ):
            backend.prepare()

        self.assertEqual(len(executor.calls), 3)
        self.assertEqual(
            executor.calls[0]["segment_descriptor_sha256"], digest(descriptor))
        self.assertEqual(
            executor.calls[0]["plan_input_binding_sha256"],
            executor.calls[0]["plan"].input_sha256,
        )
        self.assertNotEqual(
            executor.calls[0]["plan_input_binding_sha256"],
            executor.calls[1]["plan_input_binding_sha256"],
        )
        self.assertEqual(
            executor.calls[1]["plan_input_binding_sha256"],
            executor.calls[2]["plan_input_binding_sha256"],
        )

    def test_data_admission_rehashes_all_three_and_rejects_writable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = _authority(root, root / "formal")
            runtime = _runtime(root, authority)
            data = _data_authority(authority)
            for index, name in enumerate(worker.DATASET_IDS):
                payload = bytes([index + 1]) * 8
                path = Path(runtime["datasets"][name]["edge_path"])
                path.write_bytes(payload)
                os.chmod(path, stat.S_IREAD)
                observed = worker.file_sha256(path)
                runtime["datasets"][name]["input_sha256"] = observed
                data["datasets"][name]["sha256"] = observed
            result = controller.build_data_admission(
                runtime=runtime, authority=authority, data_authority=data)
            self.assertEqual(set(result["datasets"]), set(worker.DATASET_IDS))
            unsigned = dict(result)
            claimed = unsigned.pop("admission_sha256")
            self.assertEqual(claimed, digest(unsigned))
            path = Path(runtime["datasets"]["com_dblp"]["edge_path"])
            os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
            with self.assertRaisesRegex(Exception, "frozen authority"):
                controller.build_data_admission(
                    runtime=runtime, authority=authority, data_authority=data)

    def test_full_source_manifest_rehash_and_writable_attack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            payload = source / "scripts" / "payload.py"
            payload.parent.mkdir(parents=True)
            payload.write_text("VALUE = 1\n")
            row = {
                "path": "scripts/payload.py",
                "size_bytes": payload.stat().st_size,
                "sha256": worker.file_sha256(payload),
            }
            manifest_path = source.joinpath(
                *worker.PurePosixPath(worker.SOURCE_MANIFEST_RELATIVE_PATH).parts)
            manifest_path.parent.mkdir(parents=True)
            manifest = {
                "schema": "rtdl.goal5791.portable_source_manifest.v1",
                "goal": 5791,
                "status": "PORTABLE_SOURCE_FROZEN__HOME_REQUALIFICATION_REQUIRED",
                "base_source_archive_sha256": SHA,
                "base_source_manifest_sha256": SHA,
                "base_source_tree_sha256": SHA,
                "base_source_file_count_excluding_manifest": 1,
                "old_source_manifest_removed": "old.json",
                "product_delta_paths": [],
                "product_delta": {},
                "nonproduct_overlay_count_including_builder": 0,
                "deep_blob_audit": {},
                "manifest_is_non_self_referential": True,
                "file_count_excluding_this_manifest": 1,
                "source_tree_sha256": digest([row]),
                "home_or_target_execution_count": 0,
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "files": [row],
            }
            manifest_path.write_text(json.dumps(manifest))
            runtime_path = root / "runtime.json"
            runtime_path.write_text("{}\n")
            runtime = {
                "execution_source_root": str(source),
                "execution_source_manifest_path": str(manifest_path),
                "execution_source_manifest_file_sha256": worker.file_sha256(
                    manifest_path),
                "runtime_sha256": SHA,
            }

            def freeze_source() -> None:
                for path in sorted(source.rglob("*"), reverse=True):
                    os.chmod(
                        path,
                        stat.S_IREAD | (stat.S_IEXEC if path.is_dir() else 0),
                    )
                os.chmod(source, stat.S_IREAD | stat.S_IEXEC)

            freeze_source()
            admission = controller.build_source_admission(
                runtime_path=runtime_path,
                runtime=runtime,
                controller_bootstrap_observation={"test_observation": True},
            )
            self.assertTrue(admission["full_manifest_rehash_complete"])
            self.assertTrue(admission["exact_regular_file_set_verified"])
            self.assertTrue(admission["exact_implied_directory_set_verified"])
            self.assertTrue(admission["all_source_paths_without_write_bits"])
            self.assertEqual(admission["unmanifested_path_count"], 0)
            self.assertEqual(admission["missing_manifest_payload_count"], 0)
            self.assertEqual(admission["symlink_or_special_path_count"], 0)
            self.assertEqual(admission["regular_file_count"], 2)
            self.assertEqual(
                admission["source_directory_count_including_root"], 4)
            self.assertEqual(admission["source_path_count"], 6)
            unsigned = dict(admission)
            self.assertEqual(unsigned.pop("admission_sha256"), digest(unsigned))

            os.chmod(payload, stat.S_IREAD | stat.S_IWRITE)
            with self.assertRaisesRegex(Exception, "remains writable"):
                worker._rehash_execution_source_manifest(runtime)
            freeze_source()

            # A same-length post-admission source replacement is detected by
            # every worker's independent full-manifest rehash.
            os.chmod(payload, stat.S_IREAD | stat.S_IWRITE)
            payload.write_text("VALUE = 2\n")
            freeze_source()
            with self.assertRaisesRegex(Exception, "bytes/mode drifted"):
                worker._rehash_execution_source_manifest(runtime)
            os.chmod(payload, stat.S_IREAD | stat.S_IWRITE)
            payload.write_text("VALUE = 1\n")
            freeze_source()

            # Neither Python cache materialization nor any other extra path
            # may appear beneath the sealed execution source.
            os.chmod(source, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            pycache = source / "__pycache__"
            pycache.mkdir()
            extra = pycache / "payload.cpython-test.pyc"
            extra.write_bytes(b"unmanifested")
            freeze_source()
            with self.assertRaisesRegex(Exception, "exact path set drifted"):
                worker._rehash_execution_source_manifest(runtime)
            os.chmod(pycache, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            os.chmod(extra, stat.S_IREAD | stat.S_IWRITE)
            extra.unlink()
            pycache.rmdir()
            freeze_source()

            os.chmod(payload.parent, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
            os.chmod(payload, stat.S_IREAD | stat.S_IWRITE)
            payload.unlink()
            freeze_source()
            with self.assertRaisesRegex(Exception, "exact path set drifted"):
                worker._rehash_execution_source_manifest(runtime)

    def test_controller_preimport_and_runtime_bootstrap_reject_poisoned_loads(
        self,
    ) -> None:
        source_root = Path(controller.__file__).resolve().parents[1]
        environment = _formal_controller_environment(source_root)
        controller_text = Path(controller.__file__).read_text(encoding="utf-8")
        self.assertLess(
            controller_text.index("_EARLY_CONTROLLER_BOOTSTRAP ="),
            controller_text.index(
                "from scripts import goal5791_formal_contract"),
        )
        with mock.patch.dict(os.environ, environment, clear=True):
            early = controller._early_stdlib_controller_bootstrap()
        formal_sources = {
            name: worker.file_sha256(
                source_root / Path(*name.split("/")))
            for name in worker.FORMAL_SOURCE_PATHS
        }
        runtime = {
            "formal_worker_environment": environment,
            "formal_identity_record": {"formal_sources": formal_sources},
        }
        control_temp = tempfile.TemporaryDirectory()
        self.addCleanup(control_temp.cleanup)
        control_root = Path(control_temp.name).resolve()
        for name in ("runtime.json", "pre.json", "formal.json"):
            (control_root / name).write_text("{}\n")
            os.chmod(control_root / name, stat.S_IREAD)
        (_control_paths, control_observations) = (
            controller._validate_immutable_control_files(
                runtime_path=control_root / "runtime.json",
                preexecution_path=control_root / "pre.json",
                formal_authority_path=control_root / "formal.json",
            )
        )
        with mock.patch.dict(
            os.environ, environment, clear=True,
        ), mock.patch.object(
            controller, "_EARLY_CONTROLLER_BOOTSTRAP", early,
        ):
            observation = controller.validate_controller_bootstrap(
                repository_root=source_root,
                runtime=runtime,
                immutable_control_file_observations=control_observations,
                process_state_observer=_process_state_observer,
            )
        self.assertTrue(observation["preimport_stdlib_bootstrap_verified"])
        self.assertEqual(
            observation["controller_environment_sha256"],
            digest(environment),
        )
        self.assertEqual(
            set(observation["loaded_harness_sources"]),
            set(controller.CONTROLLER_BOOTSTRAP_SOURCE_PATHS),
        )
        self.assertEqual(
            observation["immutable_control_file_observations"],
            control_observations,
        )
        self.assertEqual(
            observation["no_gpu_product_process_state_observation"]["phase"],
            "after_shared_import_before_target_probe",
        )

        poisoned = dict(environment)
        poisoned["PYTHONPATH"] += os.pathsep + str(source_root / "poison")
        with mock.patch.dict(os.environ, poisoned, clear=True):
            with self.assertRaisesRegex(Exception, "stdlib bootstrap rejected"):
                controller._early_stdlib_controller_bootstrap()
        for injected in ("LC_CTYPE", "CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"):
            poisoned = dict(environment)
            poisoned[injected] = "poison"
            with self.subTest(injected=injected), mock.patch.dict(
                os.environ, poisoned, clear=True,
            ):
                with self.assertRaisesRegex(
                    Exception, "stdlib bootstrap rejected",
                ):
                    controller._early_stdlib_controller_bootstrap()
        missing = dict(environment)
        missing.pop("LC_ALL")
        with mock.patch.dict(os.environ, missing, clear=True):
            with self.assertRaisesRegex(Exception, "stdlib bootstrap rejected"):
                controller._early_stdlib_controller_bootstrap()

        wrong_hash_runtime = json.loads(json.dumps(runtime))
        wrong_hash_runtime["formal_identity_record"]["formal_sources"][
            "scripts/goal5791_formal_worker.py"] = "0" * 64
        with mock.patch.dict(
            os.environ, environment, clear=True,
        ), mock.patch.object(
            controller, "_EARLY_CONTROLLER_BOOTSTRAP", early,
        ):
            with self.assertRaisesRegex(Exception, "module path/hash drifted"):
                controller.validate_controller_bootstrap(
                    repository_root=source_root,
                    runtime=wrong_hash_runtime,
                    immutable_control_file_observations=control_observations,
                    process_state_observer=_process_state_observer,
                )
        with mock.patch.dict(
            os.environ, environment, clear=True,
        ), mock.patch.object(
            controller, "_EARLY_CONTROLLER_BOOTSTRAP", early,
        ), mock.patch.object(
            controller._formal_worker_module, "__file__",
            str(source_root / "scripts" / "goal5791_formal_evaluate.py"),
        ):
            with self.assertRaisesRegex(Exception, "module path/hash drifted"):
                controller.validate_controller_bootstrap(
                    repository_root=source_root,
                    runtime=runtime,
                    immutable_control_file_observations=control_observations,
                    process_state_observer=_process_state_observer,
                )
        with self.assertRaisesRegex(Exception, "forbidden CUDA/product module"):
            controller._observe_no_gpu_product_process_state(
                phase="before_nvidia_smi",
                module_names={"sys", "cupy.cuda.runtime"},
                proc_self_maps_bytes=b"1000-2000 r-xp /usr/bin/python3\n",
            )
        with self.assertRaisesRegex(Exception, "forbidden CUDA/OptiX"):
            controller._observe_no_gpu_product_process_state(
                phase="before_nvidia_smi",
                module_names={"sys"},
                proc_self_maps_bytes=(
                    b"7f00-7f01 r-xp /usr/lib/libcuda.so.1\n"),
            )
        for mapped_dso in (
            "/usr/lib/libnvrtc-builtins.so.12.8",
            "/usr/lib/libnvidia-rtcore.so.580",
        ):
            with self.subTest(mapped_dso=mapped_dso):
                with self.assertRaisesRegex(Exception, "forbidden CUDA/OptiX"):
                    controller._observe_no_gpu_product_process_state(
                        phase="before_nvidia_smi",
                        module_names={"sys"},
                        proc_self_maps_bytes=(
                            f"7f00-7f01 r-xp {mapped_dso}\n".encode()),
                    )

    def test_target_runtime_admission_exact_probe_and_identity_attacks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            output = root.parent / f"{root.name}_goal5791_formal"
            authority = _authority(root, output)
            runtime = _runtime(root, authority)
            environment = runtime["formal_worker_environment"]
            with mock.patch.object(
                controller, "_observe_no_gpu_product_process_state",
                wraps=controller._observe_no_gpu_product_process_state,
            ) as gpu_state_gate:
                admission = controller.build_target_runtime_admission(
                    authority=authority,
                    runtime=runtime,
                    environment=environment,
                    probe_runner=_target_probe_runner,
                    process_state_observer=_process_state_observer,
                )
            self.assertEqual(gpu_state_gate.call_count, 2)
            unsigned = dict(admission)
            self.assertEqual(
                unsigned.pop("admission_sha256"), digest(unsigned))
            self.assertEqual(admission["visible_gpu_row_count"], 1)
            self.assertFalse(admission["cuda_context_or_product_import_used"])
            self.assertEqual(
                admission["controlled_environment_sha256"],
                digest(environment),
            )

            def wrong_gpu(_command, **_kwargs):
                return mock.Mock(
                    stdout="GPU-wrong, test-driver, 8.9\n", returncode=0)

            with self.assertRaisesRegex(Exception, "live target identity"):
                controller.build_target_runtime_admission(
                    authority=authority,
                    runtime=runtime,
                    environment=environment,
                    probe_runner=wrong_gpu,
                    process_state_observer=_process_state_observer,
                )

            def two_gpus(_command, **_kwargs):
                return mock.Mock(
                    stdout=(
                        "GPU-goal5791-controller-test, test-driver, 8.9\n"
                        "GPU-second, test-driver, 8.9\n"
                    ),
                    returncode=0,
                )

            with self.assertRaisesRegex(Exception, "exactly one visible GPU"):
                controller.build_target_runtime_admission(
                    authority=authority,
                    runtime=runtime,
                    environment=environment,
                    probe_runner=two_gpus,
                    process_state_observer=_process_state_observer,
                )
            polluted = dict(environment)
            polluted["CUPY_CACHE_DIR"] = str(root / "cache")
            with self.assertRaisesRegex(Exception, "frozen 14-key env"):
                controller.build_target_runtime_admission(
                    authority=authority,
                    runtime=runtime,
                    environment=polluted,
                    probe_runner=_target_probe_runner,
                    process_state_observer=_process_state_observer,
                )

    def test_controller_exact_96_fresh_processes_no_retry_and_raw_copies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            materialization = workspace / "goal5791_target_materialization"
            root = materialization / "source"
            root.mkdir(parents=True)
            output = workspace / "goal5791_formal_result"
            authority = _authority(root, output)
            data = _data_authority(authority)
            runtime = _runtime(root, authority)
            source_admission = _source_admission(runtime, authority)
            scripts = root / "scripts"
            scripts.mkdir()
            for name in (
                "goal5791_formal_worker.py", "goal5791_formal_evaluate.py",
                "goal5791_formal_independent_recount.py",
            ):
                (scripts / name).write_text("# frozen mock\n")
            for name in (
                "goal5791_formal_worker.py", "goal5791_formal_evaluate.py",
                "goal5791_formal_independent_recount.py",
            ):
                runtime["formal_identity_record"]["formal_sources"][
                    f"scripts/{name}"
                ] = worker.file_sha256(scripts / name)
            (root / "target.json").write_text("{}\n")
            for name in worker.DATASET_IDS:
                path = Path(runtime["datasets"][name]["edge_path"])
                path.write_bytes(b"12345678")
                os.chmod(path, stat.S_IREAD)
                observed = worker.file_sha256(path)
                runtime["datasets"][name]["input_sha256"] = observed
                data["datasets"][name]["sha256"] = observed
            for name in ("runtime.json",):
                (root / name).write_text("{}\n")
            # Real-shaped Stage-A state: the materialization/source tree
            # preexists and has no write bit, while the two formal siblings
            # remain absent until the controller transaction starts.
            for path in sorted(root.rglob("*"), reverse=True):
                os.chmod(
                    path,
                    stat.S_IREAD | (stat.S_IEXEC if path.is_dir() else 0),
                )
            os.chmod(root, stat.S_IREAD | stat.S_IEXEC)
            self.assertTrue(root.is_dir())
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(
                f".{output.name}.goal5791_incomplete").exists())
            self.assertTrue(all(
                (path.stat().st_mode & 0o222) == 0
                for path in [root, *root.rglob("*")]
            ))
            calls: list[tuple[str, str | None]] = []
            worker_seals: list[str] = []

            def child_runner(command, *, environment, timeout_seconds, label):
                del timeout_seconds
                calls.append((label, environment.get("CUPY_CACHE_DIR")))
                output_path = Path(command[command.index("--output") + 1])
                if "worker" in label:
                    index = int(command[command.index("--worker-index") + 1])
                    spec = schedule()[index]
                    Path(environment["CUPY_CACHE_DIR"]).joinpath(
                        "non_authoritative_recipe.cache"
                    ).write_text("mock compiled recipe")
                    endpoint_ns = (
                        2_000_000_000
                        if spec["variant"] == controller.FUSION_OFF
                        else 1_000_000_000
                    )
                    phase_sequence = [
                        {
                            "phase": phase,
                            "started_ns": 0,
                            "ended_ns": 0,
                            "seconds": 0.0,
                        }
                        for phase in (
                            "loading", "preparation", "prewarm", "execute", "close"
                        )
                    ]
                    if spec["lifecycle"] == "cold":
                        phase_sequence[-1]["ended_ns"] = endpoint_ns
                    else:
                        phase_sequence[3]["ended_ns"] = endpoint_ns
                    payload = {
                        "schema": worker.WORKER_SCHEMA,
                        "goal": 5791,
                        "status": "COMPLETE",
                        "formal_worker": True,
                        "worker_index": index,
                        "row_index": spec["row_index"],
                        "row_id": spec["row_id"],
                        "dataset_id": spec["dataset_id"],
                        "lifecycle": spec["lifecycle"],
                        "pair_index": spec["pair_index"],
                        "order_ordinal": spec["order_ordinal"],
                        "variant": spec["variant"],
                        "paper_algorithm": spec["paper_algorithm"],
                        "mechanism_id": spec["mechanism_id"],
                        "formal_contract_sha256": controller.contract_sha256(),
                        "schedule_sha256": controller.schedule_sha256(),
                        "runtime_file_sha256": (
                            authority.formal["runtime_file_sha256"]),
                        "source_admission_sha256": (
                            source_admission["admission_sha256"]),
                        "llvmlite_version": runtime["llvmlite_version"],
                        "segment_count": 1,
                        "phase_sequence": phase_sequence,
                        "parent_pid": 10_000 + index,
                        "retry_resume_replacement_row_drop_relabel_used": False,
                    }
                    payload["worker_sha256"] = digest(payload)
                    worker_seals.append(payload["worker_sha256"])
                    output_path.write_text(json.dumps(payload))
                else:
                    rows = []
                    for expected_row in controller.statistical_rows():
                        rows.append({
                            "row_index": expected_row["row_index"],
                            "row_id_internal_schedule_id": expected_row["row_id"],
                            "row_id": controller.result_row_id(
                                expected_row["dataset_id"],
                                expected_row["lifecycle"],
                            ),
                            "dataset_id": expected_row["dataset_id"],
                            "lifecycle_internal_schedule_id": expected_row[
                                "lifecycle"
                            ],
                            "lifecycle": controller.result_lifecycle_label(
                                expected_row["lifecycle"]
                            ),
                            "trace_cost_diagnostic_authority_file_sha256": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "cpu_only_diagnostic_authority_file_sha256"
                                ]
                            ),
                            "trace_cost_diagnostic_authority_sha256": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "cpu_only_diagnostic_authority_sha256"
                                ]
                            ),
                            "per_event_record_cost_bound_ns": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "per_event_record_cost_bound_ns"
                                ]
                            ),
                            "extra_trace_event_count_per_segment": 5,
                            "five_extra_event_differential_bound_per_segment_ns": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "five_extra_event_differential_bound_per_segment_ns"
                                ]
                            ),
                            "exact_row_segment_count": 1,
                            "row_total_trace_differential_bound_ns": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "five_extra_event_differential_bound_per_segment_ns"
                                ]
                            ),
                            "row_total_trace_differential_bound_seconds": 0.00006101,
                            "absolute_median_seconds_difference": 1.0,
                            "trace_differential_fraction_of_absolute_median_seconds_difference": 0.00006101,
                            "trace_small_relative_max_fraction": 0.01,
                            "classification": (
                                "ci_crosses_one__not_a_demonstrated_win"
                            ),
                            "trace_cost_bound_small_relative_to_observed_difference": True,
                            "demonstrated_clear_win": False,
                            "mechanism_performance_statement_eligible": False,
                            "mechanism_performance_statement_classification": (
                                "not_a_statistical_clear_win"
                            ),
                            "diagnostic_may_change_row_statistic_ci_threshold_or_verdict": False,
                            "statistical_classification_unchanged_by_trace_diagnostic": True,
                            "estimand_includes_evidence_overhead": True,
                            "pure_device_kernel_timing_claimed": False,
                        })
                    primary = output_path.name == "EVALUATION.json"
                    payload = {
                        "schema": (
                            "rtdl.goal5791.formal_primary_evaluation.v1"
                            if primary else
                            "rtdl.goal5791.formal_independent_recount.v1"
                        ),
                        "goal": 5791,
                        "status": (
                            "PASS__COMPLETE_FAIL_CLOSED_FORMAL_EVALUATION"
                            if primary else
                            "PASS__COMPLETE_INDEPENDENT_RAW_RECOUNT"
                        ),
                        "formal_contract_sha256": controller.contract_sha256(),
                        "schedule_sha256": controller.schedule_sha256(),
                        "preexecution_authority_file_sha256": (
                            authority.preexecution_file_sha256),
                        "target_materialization_binding_sha256": (
                            authority.target_binding["binding_sha256"]),
                        "target_materialization_authority_file_sha256": (
                            runtime["target_materialization_authority_file_sha256"]),
                        "formal_authority_file_sha256": (
                            authority.formal_authority_file_sha256),
                        "runtime_sha256": runtime["runtime_sha256"],
                        "runtime_file_sha256": (
                            authority.formal["runtime_file_sha256"]),
                        "data_admission_sha256": json.loads(
                            (output_path.parent / "DATA_ADMISSION.json").read_text()
                        )["admission_sha256"],
                        "raw_authority_manifest_sha256": json.loads(
                            (output_path.parent / "AUTHORITY_MANIFEST.json").read_text()
                        )["manifest_sha256"],
                        "source_admission_sha256": (
                            source_admission["admission_sha256"]),
                        "target_runtime_admission_sha256": json.loads(
                            (output_path.parent / "TARGET_RUNTIME_ADMISSION.json").read_text()
                        )["admission_sha256"],
                        "target_runtime_admission_file_sha256": worker.file_sha256(
                            output_path.parent / "TARGET_RUNTIME_ADMISSION.json"),
                        "resource_admission_sha256": json.loads(
                            (output_path.parent / "RESOURCE_ADMISSION.json").read_text()
                        )["admission_sha256"],
                        "resource_admission_file_sha256": worker.file_sha256(
                            output_path.parent / "RESOURCE_ADMISSION.json"),
                        "raw_worker_set_sha256": digest(worker_seals),
                        "worker_count": 96,
                        "unique_parent_pid_count": 96,
                        "unique_worker_cache_count": 96,
                        "exact_output_worker_count": 96,
                        "behavioral_true_optix_worker_count": 96,
                        "independent_row_count": 6,
                        "rows": rows,
                        "result_lifecycle_labels": {
                            lifecycle: controller.result_lifecycle_label(lifecycle)
                            for lifecycle in controller.LIFECYCLES
                        },
                        "trace_cost_diagnostic_authority": {
                            "file_sha256": controller.TRACE_INSTRUMENTATION_CONTRACT[
                                "cpu_only_diagnostic_authority_file_sha256"
                            ],
                            "diagnostic_sha256": controller.TRACE_INSTRUMENTATION_CONTRACT[
                                "cpu_only_diagnostic_authority_sha256"
                            ],
                            "per_event_record_cost_bound_ns": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "per_event_record_cost_bound_ns"
                                ]
                            ),
                            "five_extra_event_differential_bound_per_segment_ns": (
                                controller.TRACE_INSTRUMENTATION_CONTRACT[
                                    "five_extra_event_differential_bound_per_segment_ns"
                                ]
                            ),
                            "required_before_stage_b_worker_zero": True,
                        },
                        "independent_recount_external_review_status": (
                            controller.INDEPENDENT_RECOUNT_REVIEW_STATUS
                        ),
                        "every_figure_caption_must_state_includes_evidence_overhead": True,
                        "ci_clear_win_count": 0,
                        **controller._paper_outcome_summary(rows),
                        "ci_clear_loss_count": 0,
                        "ci_crossing_count": 6,
                        "all_six_rows_retained": True,
                        "cross_dataset_lifecycle_or_row_compensation_used": False,
                        "operation_delta_exact_all_workers": True,
                        "same_source_target_and_optix_producer_all_workers": True,
                        "operating_system_page_cache_controlled_or_dropped": False,
                        "operating_system_page_cache_scope": controller.CACHE_POLICY[
                            "operating_system_page_cache_scope"],
                        "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": True,
                        "cold_process_warm_system_definition": (
                            controller.CACHE_POLICY["cold_definition"]),
                        "cold_process_warm_system_excludes": (
                            controller.CACHE_POLICY["cold_claim_excludes"]),
                        "cuda_driver_jit_cache_controlled_or_isolated": False,
                        "optix_disk_cache_controlled_or_isolated": False,
                        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": True,
                        "same_host_root_race_excluded": False,
                        "cache_receipts_preserved": True,
                        "cache_payloads_non_authoritative": True,
                        "cache_payloads_must_be_removed_before_final_cohort_publication": True,
                        "failed_terminal_staging_may_preserve_cache_payloads": True,
                        "successful_cohort_empty_cache_directory_shells_preserved_for_offline_recount": True,
                        "successful_cohort_empty_cache_directory_shell_count": 96,
                        "empty_cache_directory_shells_are_authoritative_evidence": False,
                        "retry_resume_replacement_row_drop_relabel_used": False,
                    }
                    if not primary:
                        evaluation_path = output_path.parent / "EVALUATION.json"
                        evaluation = json.loads(evaluation_path.read_text())
                        payload.update({
                            "raw_root_mode": "analysis_stage",
                            "primary_evaluation_file_sha256": (
                                worker.file_sha256(evaluation_path)),
                            "primary_evaluation_sha256": evaluation[
                                "evaluation_sha256"],
                            "primary_evaluation_authority_pins_verified": True,
                        })
                    seal = "evaluation_sha256" if primary else "recount_sha256"
                    payload[seal] = digest(payload)
                    output_path.write_text(json.dumps(payload))

            with mock.patch.object(
                controller, "_load_authority_context", return_value=authority
            ), mock.patch.object(
                controller, "_load_data_authority", return_value=(data, root / "data.json")
            ), mock.patch.object(
                controller, "_validate_runtime", return_value=runtime
            ), mock.patch.object(
                controller, "validate_controller_bootstrap",
                return_value={"mock_bootstrap": True},
            ), mock.patch.object(
                controller, "build_source_admission",
                return_value=source_admission,
            ), mock.patch.object(
                controller.shutil, "disk_usage",
                return_value=mock.Mock(free=30_000_000_000),
            ):
                controller.run_controller(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    output_root=output,
                    child_runner=child_runner,
                    target_probe_runner=_target_probe_runner,
                    process_state_observer=_process_state_observer,
                    clock_ns=_Clock(),
                )
            self.assertTrue(output.is_dir())
            self.assertEqual(len(calls), 98)
            worker_calls = calls[:96]
            self.assertEqual(len({cache for _label, cache in worker_calls}), 96)
            self.assertTrue(all(cache is not None for _label, cache in worker_calls))
            self.assertTrue((output / "TARGET_MATERIALIZATION_AUTHORITY.json").is_file())
            self.assertTrue((output / "DATA_ADMISSION.json").is_file())
            self.assertTrue((output / "SOURCE_ADMISSION.json").is_file())
            self.assertTrue(
                (output / "TARGET_RUNTIME_ADMISSION.json").is_file())
            self.assertTrue((output / "RESOURCE_ADMISSION.json").is_file())
            authority_manifest = json.loads(
                (output / "AUTHORITY_MANIFEST.json").read_text())
            self.assertEqual(
                set(authority_manifest["authorities"]),
                set(controller.AUTHORITY_ROLES),
            )
            for role, record in authority_manifest["authorities"].items():
                copied = output / Path(*record["path"].split("/"))
                self.assertTrue(copied.is_file())
                self.assertEqual(worker.file_sha256(copied), record["file_sha256"])
                self.assertEqual(copied.stat().st_size, record["bytes"])
            self.assertEqual(
                (output / "DATA_AUTHORITY.json").read_bytes(),
                (output / "AUTHORITIES" / "data_authority.json").read_bytes(),
            )
            cohort = json.loads((output / "COHORT_MANIFEST.json").read_text())
            result = json.loads((output / "RESULT.json").read_text())
            resource_admission = json.loads(
                (output / "RESOURCE_ADMISSION.json").read_text())
            target_runtime_admission = json.loads(
                (output / "TARGET_RUNTIME_ADMISSION.json").read_text())
            self.assertEqual(result["formal_worker_count"], 96)
            self.assertEqual(result["fresh_parent_pid_count"], 96)
            self.assertEqual(result["launch_attempt_count"], 96)
            self.assertEqual(
                result["resource_admission_sha256"],
                resource_admission["admission_sha256"],
            )
            self.assertEqual(
                result["resource_admission_file_sha256"],
                worker.file_sha256(output / "RESOURCE_ADMISSION.json"),
            )
            self.assertEqual(
                result["target_runtime_admission_sha256"],
                target_runtime_admission["admission_sha256"],
            )
            self.assertEqual(
                result["target_runtime_admission_file_sha256"],
                worker.file_sha256(
                    output / "TARGET_RUNTIME_ADMISSION.json"),
            )
            self.assertEqual(
                resource_admission[
                    "controller_observed_free_disk_bytes_before_worker_zero"],
                30_000_000_000,
            )
            cache_root = output / "worker_caches"
            self.assertTrue(cache_root.is_dir())
            cache_shells = list(cache_root.iterdir())
            self.assertEqual(len(cache_shells), 96)
            self.assertEqual(
                {path.name for path in cache_shells},
                {f"worker_{index:04d}" for index in range(96)},
            )
            self.assertTrue(all(
                path.is_dir() and not path.is_symlink()
                and not any(path.iterdir())
                for path in cache_shells
            ))
            self.assertFalse(result["worker_cache_payloads_preserved"])
            self.assertTrue(result[
                "worker_cache_payloads_removed_after_validation"])
            self.assertTrue(result["cache_receipts_preserved"])
            self.assertFalse(result[
                "cache_payloads_are_authoritative_evidence"])
            self.assertTrue(result[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"])
            self.assertTrue(result[
                "failed_terminal_staging_may_preserve_cache_payloads"])
            self.assertTrue(result[
                "worker_cache_empty_directory_shells_preserved"])
            self.assertEqual(result[
                "worker_cache_empty_directory_shell_count"], 96)
            self.assertFalse(result[
                "worker_cache_empty_directory_shells_are_authoritative_evidence"])
            self.assertTrue(result[
                "worker_cache_empty_directory_shells_all_empty"])
            for published in (cohort, result):
                self.assertTrue(published[
                    "worker_cache_empty_directory_shells_preserved"])
                self.assertEqual(published[
                    "worker_cache_empty_directory_shell_count"], 96)
                self.assertFalse(published[
                    "worker_cache_empty_directory_shells_are_authoritative_evidence"])
                self.assertTrue(published[
                    "worker_cache_empty_directory_shells_all_empty"])
            self.assertEqual(
                result["raw_authority_manifest_sha256"],
                authority_manifest["manifest_sha256"],
            )
            self.assertFalse(result["retry_resume_replacement_row_drop_relabel_used"])

    def test_stage_a_root_split_capacity_and_preworker_marker_are_fail_closed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            materialization = workspace / "goal5791_target_materialization"
            root = materialization / "source"
            root.mkdir(parents=True)
            output = workspace / "goal5791_formal_result"
            staging = workspace / ".goal5791_formal_result.goal5791_incomplete"
            authority = _authority(root, output)
            data = _data_authority(authority)
            runtime = _runtime(root, authority)
            calls = 0

            layout = controller._validate_execution_layout(
                repository_root=root,
                runtime_path=root / "runtime.json",
                preexecution_path=root / "pre.json",
                formal_authority_path=root / "formal.json",
                runtime=runtime,
                authority=authority,
                requested_output_root=output,
            )
            with mock.patch.object(
                controller.shutil, "disk_usage",
                return_value=mock.Mock(free=24_999_999_999),
            ):
                with self.assertRaisesRegex(Exception, "capacity is insufficient"):
                    controller.build_resource_admission(
                        authority=authority,
                        materialization_root=layout[0],
                        formal_output_root=layout[1],
                        formal_staging_root=layout[2],
                        formal_output_parent=layout[3],
                    )
            self.assertFalse(staging.exists())
            os.chmod(root / "runtime.json", stat.S_IREAD)
            os.chmod(root / "pre.json", stat.S_IREAD)
            self.assertNotEqual(
                (root / "formal.json").stat().st_mode & 0o222, 0)
            with self.assertRaisesRegex(
                Exception, "formal_authority.*canonical read-only",
            ):
                controller.run_controller(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    output_root=output,
                )
            self.assertFalse(staging.exists())
            self.assertFalse(output.exists())
            os.chmod(root / "formal.json", stat.S_IREAD)

            def fail_data_admission(**_kwargs):
                nonlocal calls
                calls += 1
                raise controller.Goal5791ControllerError(
                    "preworker data rehash failed")

            with mock.patch.object(
                controller, "_load_authority_context", return_value=authority
            ), mock.patch.object(
                controller, "_load_data_authority",
                return_value=(data, root / "data.json"),
            ), mock.patch.object(
                controller, "_validate_runtime", return_value=runtime
            ), mock.patch.object(
                controller, "validate_controller_bootstrap",
                return_value={"mock_bootstrap": True},
            ), mock.patch.object(
                controller, "build_data_admission",
                side_effect=fail_data_admission,
            ), mock.patch.object(
                controller.shutil, "disk_usage",
                return_value=mock.Mock(free=30_000_000_000),
            ):
                with self.assertRaisesRegex(Exception, "data rehash failed"):
                    controller.run_controller(
                        repository_root=root,
                        runtime_path=root / "runtime.json",
                        preexecution_path=root / "pre.json",
                        formal_authority_path=root / "formal.json",
                        output_root=output,
                        target_probe_runner=_target_probe_runner,
                        process_state_observer=_process_state_observer,
                    )
            self.assertEqual(calls, 1)
            self.assertFalse(output.exists())
            self.assertTrue(staging.is_dir())
            resource_path = staging / "RESOURCE_ADMISSION.json"
            self.assertTrue(resource_path.is_file())
            resource = json.loads(resource_path.read_text())
            unsigned = dict(resource)
            self.assertEqual(
                unsigned.pop("admission_sha256"), digest(unsigned))
            self.assertEqual(
                resource["target_materialization_root"], str(materialization))
            self.assertEqual(
                resource["create_only_formal_output_root"], str(output))
            self.assertEqual(
                resource["controller_incomplete_staging_root"], str(staging))

            # The marker is acquired before the data admission.  A second use
            # of the same Stage-B authority is terminal before any admission.
            with self.assertRaises(FileExistsError):
                controller.run_controller(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    output_root=output,
                )
            self.assertEqual(calls, 1)

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            materialization = workspace / "goal5791_target_materialization"
            root = materialization / "source"
            root.mkdir(parents=True)
            output = workspace / "goal5791_formal_result"
            authority = _authority(root, output)
            runtime = _runtime(root, authority)
            output.mkdir()
            with self.assertRaisesRegex(
                Exception, "layout drifted",
            ):
                controller._validate_execution_layout(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    runtime=runtime,
                    authority=authority,
                    requested_output_root=output,
                )

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            materialization = workspace / "goal5791_target_materialization"
            root = materialization / "source"
            root.mkdir(parents=True)
            output = materialization / "goal5791_formal_result"
            authority = _authority(root, output)
            runtime = _runtime(root, authority)
            with self.assertRaisesRegex(
                Exception, "layout drifted",
            ):
                controller._validate_execution_layout(
                    repository_root=root,
                    runtime_path=root / "runtime.json",
                    preexecution_path=root / "pre.json",
                    formal_authority_path=root / "formal.json",
                    runtime=runtime,
                    authority=authority,
                    requested_output_root=output,
                )

    def test_marker_precedes_bootstrap_target_and_resource_failures(self) -> None:
        for phase in ("bootstrap", "target", "resource"):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as temporary:
                workspace = Path(temporary).resolve()
                materialization = workspace / "goal5791_target_materialization"
                root = materialization / "source"
                root.mkdir(parents=True)
                output = workspace / "goal5791_formal_result"
                staging = workspace / (
                    ".goal5791_formal_result.goal5791_incomplete")
                authority = _authority(root, output)
                data = _data_authority(authority)
                runtime = _runtime(root, authority)
                _freeze_control_files(root)
                bootstrap = (
                    mock.Mock(side_effect=controller.Goal5791ControllerError(
                        "bootstrap gate failed"))
                    if phase == "bootstrap"
                    else mock.Mock(return_value={"mock_bootstrap": True})
                )

                def wrong_target(_command, **_kwargs):
                    return mock.Mock(
                        stdout="GPU-wrong, test-driver, 8.9\n",
                        returncode=0,
                    )

                probe = wrong_target if phase == "target" \
                    else _target_probe_runner
                free = 19_999_999_999 if phase == "resource" \
                    else 30_000_000_000
                data_gate = mock.Mock(side_effect=AssertionError(
                    "data admission must not begin after earlier failure"))
                with mock.patch.object(
                    controller, "_load_authority_context",
                    return_value=authority,
                ), mock.patch.object(
                    controller, "_load_data_authority",
                    return_value=(data, root / "data.json"),
                ), mock.patch.object(
                    controller, "_validate_runtime", return_value=runtime,
                ), mock.patch.object(
                    controller, "validate_controller_bootstrap", bootstrap,
                ), mock.patch.object(
                    controller, "build_data_admission", data_gate,
                ), mock.patch.object(
                    controller.shutil, "disk_usage",
                    return_value=mock.Mock(free=free),
                ):
                    with self.assertRaises(Exception):
                        controller.run_controller(
                            repository_root=root,
                            runtime_path=root / "runtime.json",
                            preexecution_path=root / "pre.json",
                            formal_authority_path=root / "formal.json",
                            output_root=output,
                            target_probe_runner=probe,
                            process_state_observer=_process_state_observer,
                        )
                self.assertTrue(staging.is_dir())
                self.assertFalse(output.exists())
                self.assertEqual(data_gate.call_count, 0)
                self.assertEqual(
                    (staging / "TARGET_RUNTIME_ADMISSION.json").is_file(),
                    phase == "resource",
                )
                self.assertFalse(
                    (staging / "RESOURCE_ADMISSION.json").exists())
                with self.assertRaises(FileExistsError):
                    controller.run_controller(
                        repository_root=root,
                        runtime_path=root / "runtime.json",
                        preexecution_path=root / "pre.json",
                        formal_authority_path=root / "formal.json",
                        output_root=output,
                    )

    def test_controller_child_failure_is_terminal_without_retry_or_final_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary).resolve()
            materialization = workspace / "goal5791_target_materialization"
            root = materialization / "source"
            root.mkdir(parents=True)
            output = workspace / "goal5791_formal_result"
            authority = _authority(root, output)
            data = _data_authority(authority)
            runtime = _runtime(root, authority)
            source_admission = _source_admission(runtime, authority)
            scripts = root / "scripts"
            scripts.mkdir()
            for name in (
                "goal5791_formal_worker.py", "goal5791_formal_evaluate.py",
                "goal5791_formal_independent_recount.py",
            ):
                (scripts / name).write_text("# frozen mock\n")
            runtime["formal_identity_record"]["formal_sources"][
                "scripts/goal5791_formal_worker.py"
            ] = worker.file_sha256(scripts / "goal5791_formal_worker.py")
            (root / "target.json").write_text("{}\n")
            for name in worker.DATASET_IDS:
                path = Path(runtime["datasets"][name]["edge_path"])
                path.write_bytes(b"12345678")
                os.chmod(path, stat.S_IREAD)
                observed = worker.file_sha256(path)
                runtime["datasets"][name]["input_sha256"] = observed
                data["datasets"][name]["sha256"] = observed
            for name in ("runtime.json",):
                (root / name).write_text("{}\n")
            _freeze_control_files(root)
            attempted: list[int] = []

            def failing_runner(command, **_kwargs):
                index = int(command[command.index("--worker-index") + 1])
                attempted.append(index)
                if index == 3:
                    raise controller.Goal5791ControllerError(
                        "worker 3 failed terminally; retry is forbidden")
                spec = schedule()[index]
                payload = {
                    "schema": worker.WORKER_SCHEMA,
                    "goal": 5791,
                    "status": "COMPLETE",
                    "formal_worker": True,
                    **{name: spec[name] for name in (
                        "worker_index", "row_index", "row_id", "dataset_id",
                        "lifecycle", "pair_index", "order_ordinal", "variant",
                        "paper_algorithm", "mechanism_id",
                    )},
                    "formal_contract_sha256": controller.contract_sha256(),
                    "schedule_sha256": controller.schedule_sha256(),
                    "runtime_file_sha256": (
                        authority.formal["runtime_file_sha256"]),
                    "source_admission_sha256": (
                        source_admission["admission_sha256"]),
                    "llvmlite_version": runtime["llvmlite_version"],
                    "parent_pid": 20_000 + index,
                    "retry_resume_replacement_row_drop_relabel_used": False,
                }
                payload["worker_sha256"] = digest(payload)
                path = Path(command[command.index("--output") + 1])
                path.write_text(json.dumps(payload))

            with mock.patch.object(
                controller, "_load_authority_context", return_value=authority
            ), mock.patch.object(
                controller, "_load_data_authority", return_value=(data, root / "data.json")
            ), mock.patch.object(
                controller, "_validate_runtime", return_value=runtime
            ), mock.patch.object(
                controller, "validate_controller_bootstrap",
                return_value={"mock_bootstrap": True},
            ), mock.patch.object(
                controller, "build_source_admission",
                return_value=source_admission,
            ), mock.patch.object(
                controller.shutil, "disk_usage",
                return_value=mock.Mock(free=30_000_000_000),
            ):
                with self.assertRaisesRegex(Exception, "retry is forbidden"):
                    controller.run_controller(
                        repository_root=root,
                        runtime_path=root / "runtime.json",
                        preexecution_path=root / "pre.json",
                        formal_authority_path=root / "formal.json",
                        output_root=output,
                        child_runner=failing_runner,
                        target_probe_runner=_target_probe_runner,
                        process_state_observer=_process_state_observer,
                        clock_ns=_Clock(),
                    )
            self.assertEqual(attempted, [0, 1, 2, 3])
            self.assertFalse(output.exists())
            self.assertTrue(
                (workspace / ".goal5791_formal_result.goal5791_incomplete").is_dir())
            self.assertTrue(
                (workspace / ".goal5791_formal_result.goal5791_incomplete"
                 / "worker_caches").is_dir())


if __name__ == "__main__":
    unittest.main()
