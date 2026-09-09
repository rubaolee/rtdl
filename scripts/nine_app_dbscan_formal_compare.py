#!/usr/bin/env python3
"""Auditable complete-output RTDL versus public-PyOptiX DBSCAN protocol."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import dataclasses
import datetime as dt
from enum import Enum
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import random
import shutil
import statistics
import subprocess
import sys
import threading
import time
import uuid


SCHEMA = "rtdl.nine_app.dbscan.formal_compare.v1"
CONFIG_SCHEMA = f"{SCHEMA}.config"
PREREG_SCHEMA = f"{SCHEMA}.preregistration"
ORDERS = (
    ("A", "C"), ("C", "A"), ("A", "C"), ("C", "A"),
    ("C", "A"), ("A", "C"), ("C", "A"), ("A", "C"),
)
PRIMARY_ENDPOINT = "public_full_return_plus_same_external_oracle_ns"
LIFECYCLE_ENDPOINT = (
    "prepare_plus_first_public_return_plus_close_plus_same_external_oracle_ns")
SOURCE_PATHS = (
    "scripts/nine_app_dbscan_formal_compare.py",
    "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py",
    "Paper-reproduction-apps/rt-dbscan-paper/rtdl3_action_migration.py",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "experiments/v4_paper_apps_pyoptix/dbscan_adapter.py",
    "experiments/v4_paper_apps_pyoptix/dbscan_owner.py",
    "experiments/v4_paper_apps_pyoptix/dbscan_device.cu",
    "experiments/v4_paper_apps_pyoptix/dbscan_continuation.cu",
    "scripts/build_dbscan_public_pyoptix_ptx.py",
)


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, object]:
    value = Path(path).resolve(strict=True)
    return {
        "path": str(value),
        "sha256": sha256(value),
        "bytes": value.stat().st_size,
    }


def checked_binding(value: object) -> Path:
    if not isinstance(value, dict) or set(value) != {"path", "sha256", "bytes"}:
        raise ValueError("exact path/sha256/bytes binding required")
    path = Path(value["path"]).resolve(strict=True)
    if binding(path) != value:
        raise ValueError(f"bound file changed: {path}")
    return path


def read_json(path: str | Path) -> dict[str, object]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def json_value(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float cannot enter evidence")
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return json_value(value.value)
    if dataclasses.is_dataclass(value):
        return json_value(dataclasses.asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(item) for item in value]
    try:
        import numpy as np
        if isinstance(value, np.ndarray):
            return json_value(value.tolist())
        if isinstance(value, np.generic):
            return json_value(value.item())
    except ImportError:
        pass
    if hasattr(value, "to_metadata"):
        return json_value(value.to_metadata())
    raise TypeError(f"unsupported evidence value: {type(value)!r}")


def write_new(path: str | Path, value: object) -> dict[str, object]:
    path = Path(path)
    raw = (json.dumps(
        json_value(value), sort_keys=True, indent=2, allow_nan=False,
    ) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return binding(path)


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, text=True,
        capture_output=True,
    ).stdout.strip()


def gpu_inventory(gpu_uuid: str) -> dict[str, str]:
    result = subprocess.run([
        "nvidia-smi", "-i", gpu_uuid,
        "--query-gpu=uuid,name,driver_version",
        "--format=csv,noheader",
    ], check=True, text=True, capture_output=True)
    fields = [field.strip() for field in result.stdout.strip().split(",")]
    if len(fields) != 3 or fields[0] != gpu_uuid:
        raise RuntimeError("selected GPU inventory mismatch")
    return {"uuid": fields[0], "name": fields[1], "driver": fields[2]}


def validate_config(path: str | Path, *, require_runtime: bool) -> dict[str, object]:
    config = read_json(path)
    if config.get("schema") != CONFIG_SCHEMA:
        raise ValueError("unexpected DBSCAN comparison config schema")
    root = Path(config["source_root"]).resolve(strict=True)
    if git(root, "rev-parse", "HEAD") != config["source_commit"] \
            or git(root, "rev-parse", "HEAD^{tree}") != config["source_tree"]:
        raise ValueError("source commit/tree differs from frozen config")
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("tracked source must remain clean")
    source_files = config.get("source_files")
    if not isinstance(source_files, list) or len(source_files) != len(SOURCE_PATHS):
        raise ValueError("exact source closure is required")
    for relative, row in zip(SOURCE_PATHS, source_files, strict=True):
        if checked_binding(row) != (root / relative).resolve(strict=True):
            raise ValueError(f"source closure order/path mismatch: {relative}")
    data_manifest = checked_binding(config["data_manifest"])
    if data_manifest != Path(config["data_root"]).resolve(strict=True) / "MANIFEST.json":
        raise ValueError("DBSCAN data manifest/root mismatch")
    native = checked_binding(config["native_library"])
    native_build_path = checked_binding(config["native_build"])
    native_build = read_json(native_build_path)
    if native_build.get("status") != \
            "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED" \
            or native_build.get("git_commit") != config["source_commit"] \
            or native_build.get("native_sha256") != sha256(native):
        raise ValueError("native build/source/library binding mismatch")
    pyoptix_build_path = checked_binding(config["pyoptix_build"])
    pyoptix_build = read_json(pyoptix_build_path)
    if pyoptix_build.get("status") != "PASS__TWO_CANONICAL_PTX_ARTIFACTS_BUILT" \
            or pyoptix_build.get("source_commit") != config["source_commit"] \
            or pyoptix_build.get("source_tree") != config["source_tree"]:
        raise ValueError("public-PyOptiX build/source binding mismatch")
    for name in ("device", "continuation"):
        artifact = checked_binding(config[f"pyoptix_{name}_ptx"])
        if pyoptix_build["outputs"][name]["sha256"] != sha256(artifact):
            raise ValueError(f"public-PyOptiX {name} PTX mismatch")
    if config.get("gpu_exclusive_attestation") != \
            "no concurrent GPU workload scheduled for this transaction":
        raise ValueError("explicit exclusive-GPU scheduling attestation required")
    if require_runtime:
        if os.environ.get("CUDA_VISIBLE_DEVICES") != config["gpu_uuid"]:
            raise ValueError("CUDA_VISIBLE_DEVICES differs from frozen GPU UUID")
        if Path(sys.executable).absolute() != Path(config["python_invocation_path"]):
            raise ValueError("worker interpreter invocation path differs")
        if platform.python_version() != config["versions"]["python"]:
            raise ValueError("Python version differs")
        for package in ("numpy", "numba", "cupy-cuda12x", "pyoptix"):
            if importlib.metadata.version(package) != config["versions"][package]:
                raise ValueError(f"{package} version differs")
        if Path(os.environ.get("CUDA_HOME", "")).resolve() != \
                Path(config["cuda_home"]).resolve():
            raise ValueError("CUDA_HOME differs from frozen NVVM toolkit")
        ld_paths = os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep)
        if not ld_paths or Path(ld_paths[0]).resolve() != \
                Path(config["nvrtc_library_dir"]).resolve():
            raise ValueError("frozen NVRTC library is not first in loader order")
        from cuda.bindings import nvrtc
        status, major, minor = nvrtc.nvrtcVersion()
        if status.value or f"{major}.{minor}" != config["versions"]["nvrtc"]:
            raise ValueError("runtime NVRTC version differs")
        if gpu_inventory(config["gpu_uuid"]) != config["gpu"]:
            raise ValueError("runtime GPU identity differs")
    return config


def command_config(args: argparse.Namespace) -> int:
    root = args.source_root.resolve(strict=True)
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("config creation requires clean tracked source")
    data_manifest = args.data_root.resolve(strict=True) / "MANIFEST.json"
    native_build = read_json(args.native_build)
    pyoptix_build = read_json(args.pyoptix_build)
    config = {
        "schema": CONFIG_SCHEMA,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_root": str(root),
        "source_commit": git(root, "rev-parse", "HEAD"),
        "source_tree": git(root, "rev-parse", "HEAD^{tree}"),
        "source_files": [binding(root / path) for path in SOURCE_PATHS],
        "data_root": str(args.data_root.resolve(strict=True)),
        "data_manifest": binding(data_manifest),
        "native_library": binding(args.native),
        "native_build": binding(args.native_build),
        "pyoptix_build": binding(args.pyoptix_build),
        "pyoptix_device_ptx": binding(args.device_ptx),
        "pyoptix_continuation_ptx": binding(args.continuation_ptx),
        "gpu_uuid": args.gpu_uuid,
        "gpu": gpu_inventory(args.gpu_uuid),
        "compute_capability": [8, 9],
        "optix_sdk": "8.0.0",
        "optix_include": str(args.optix_include.resolve(strict=True)),
        "cuda_include": str(args.cuda_include.resolve(strict=True)),
        "cuda_home": str(args.cuda_home.resolve(strict=True)),
        "nvrtc_library_dir": str(args.nvrtc_library_dir.resolve(strict=True)),
        "cuda_library_dir": str(args.cuda_library_dir.resolve(strict=True)),
        "pyoptix_library_dir": str(
            args.pyoptix_library_dir.resolve(strict=True)),
        "python_invocation_path": str(args.python.absolute()),
        "python_resolved_path": str(args.python.resolve(strict=True)),
        "versions": {
            "python": platform.python_version(),
            **{package: importlib.metadata.version(package) for package in (
                "numpy", "numba", "cupy-cuda12x", "pyoptix",
            )},
            "nvrtc": pyoptix_build["toolchain"]["nvrtc_version"],
        },
        "gpu_exclusive_attestation": (
            "no concurrent GPU workload scheduled for this transaction"),
        "minimum_free_bytes": 1 << 30,
        "primary_endpoint": PRIMARY_ENDPOINT,
        "lifecycle_endpoint": LIFECYCLE_ENDPOINT,
        "endpoint_contents": {
            "prepared_primary": {
                "exact_neighbor_count_traversal": "excluded_after_one_symmetric_warmup; immutable counts/core reused by both arms",
                "core_component_union": "included",
                "boundary_assignment": "included",
                "canonical_label_materialization": "included",
                "all_three_host_output_columns": "included",
                "same_external_full_output_oracle": "included",
                "setup_and_gas_build": "excluded_and_reported_separately",
            },
            "lifecycle_secondary": {
                "exact_neighbor_count_traversal": "included",
                "core_component_union": "included",
                "boundary_assignment": "included",
                "canonical_label_materialization": "included",
                "all_three_host_output_columns": "included",
                "same_external_full_output_oracle": "included",
                "setup_gas_build_and_close": "included",
            },
        },
        "engineering_targets": {
            "median_rtdl_over_pyoptix_at_most": 1.20,
            "every_block_rtdl_over_pyoptix_at_most": 1.35,
            "targets_are_not_sample_filters": True,
        },
        "build_cross_checks": {
            "native_commit": native_build.get("git_commit"),
            "pyoptix_commit": pyoptix_build.get("source_commit"),
        },
    }
    write_new(args.output, config)
    validate_config(args.output, require_runtime=False)
    print(args.output.resolve())
    return 0


class MemorySampler:
    def __init__(self, gpu_uuid: str) -> None:
        import pynvml
        self._nvml = pynvml
        pynvml.nvmlInit()
        self._handle = pynvml.nvmlDeviceGetHandleByUUID(gpu_uuid)
        self._stop = threading.Event()
        self.baseline_bytes = self._used()
        self.peak_bytes = self.baseline_bytes
        self._thread = threading.Thread(target=self._sample, daemon=True)

    def _used(self) -> int:
        return int(self._nvml.nvmlDeviceGetMemoryInfo(self._handle).used)

    def _sample(self) -> None:
        while not self._stop.wait(0.005):
            self.peak_bytes = max(self.peak_bytes, self._used())

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> dict[str, int]:
        self._stop.set()
        self._thread.join()
        self.peak_bytes = max(self.peak_bytes, self._used())
        self._nvml.nvmlShutdown()
        return {
            "baseline_used_bytes": self.baseline_bytes,
            "peak_used_bytes": self.peak_bytes,
            "peak_delta_bytes": max(0, self.peak_bytes - self.baseline_bytes),
            "sampling_period_ms": 5,
        }


def load_v4_app(root: Path):
    path = root / "Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py"
    name = "formal_compare_rtdbscan_v4"
    if name in sys.modules:
        return sys.modules[name]
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def prepare_arm(config: dict[str, object], arm: str, data: dict[str, object]):
    if arm == "C":
        from experiments.v4_paper_apps_pyoptix.dbscan_adapter import prepare_owner
        return prepare_owner(
            data,
            device_ptx_path=config["pyoptix_device_ptx"]["path"],
            continuation_ptx_path=config["pyoptix_continuation_ptx"]["path"],
        )
    root = Path(config["source_root"])
    app = load_v4_app(root)
    app_data = app.load_real_scale_v4_input(config["data_root"])
    if app_data["expected"] != data["expected"] \
            or app_data["input_sha256"] != data["manifest_sha256"]:
        raise RuntimeError("A and C input/oracle projections differ")
    from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile
    import numba
    import numpy as np
    target = ReferenceTargetProfile(
        provider="optix",
        optix_sdk=config["optix_sdk"],
        compute_capability="8.9",
        native_sha256=config["native_library"]["sha256"],
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    return app.prepare_v4(
        target=target,
        compute_capability=tuple(config["compute_capability"]),
        optix_include=config["optix_include"],
        cuda_include=config["cuda_include"],
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__,
        native_library_path=config["native_library"]["path"],
        points=data["points"],
        initial_radius=data["epsilon"],
        frozen_expected=data["expected"],
        frozen_input_sha256=data["manifest_sha256"],
        frozen_epsilon=data["epsilon"],
        frozen_min_points=data["min_points"],
        maximum_event_capacity=len(data["points"]) ** 2,
    )


def execute_arm(owner: object, arm: str, data: dict[str, object]) -> dict[str, object]:
    if arm == "A":
        return owner.execute(
            epsilon=data["epsilon"], min_points=data["min_points"])
    return owner.execute()


def verify_result(
    config: dict[str, object], arm: str, raw: dict[str, object],
    expected: dict[str, tuple[object, ...]],
) -> dict[str, object]:
    from experiments.v4_paper_apps_pyoptix.dbscan_adapter import compare_output
    comparison = compare_output(raw["output"], expected)
    if arm == "A":
        snapshot = raw["traversal_receipt"]["native_snapshot"]
        receipt_ok = (
            raw.get("matched") is True
            and raw.get("native_library_sha256") ==
                config["native_library"]["sha256"]
            and raw["traversal_receipt"]["physical_executor_classification"] ==
                "optix_traversal_observed"
            and int(snapshot["successful_launch_count"]) > 0
            and int(snapshot["failed_launch_count"]) == 0
            and int(snapshot["incomplete_context_launch_count"]) == 0
            and int(snapshot["pending_context_at_finish"]) == 0
        )
        identity = raw.get("native_library_sha256")
        launches = int(snapshot["successful_launch_count"])
    else:
        receipt_ok = (
            raw.get("device_status") == 0
            and raw.get("device_ptx_sha256") ==
                config["pyoptix_device_ptx"]["sha256"]
            and raw.get("continuation_ptx_sha256") ==
                config["pyoptix_continuation_ptx"]["sha256"]
            and int(raw.get("successful_optix_launches", 0)) > 0
        )
        identity = raw.get("device_ptx_sha256")
        launches = int(raw.get("successful_optix_launches", 0))
    comparison.update(
        implementation_receipt_ok=receipt_ok,
        implementation_identity=identity,
        successful_optix_launches=launches,
    )
    comparison["matched"] = bool(comparison["matched"] and receipt_ok)
    return comparison


def retain_call(
    directory: Path,
    *,
    raw: dict[str, object],
    comparison: dict[str, object],
    timing: dict[str, int],
    phase: str,
    ordinal: int,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=False)
    output = write_new(directory / "output.json", raw["output"])
    implementation = write_new(directory / "implementation.json", raw)
    sample = {
        "phase": phase,
        "ordinal": ordinal,
        "status": "FULL_OUTPUT_ORACLE_PASS" if comparison["matched"] else
            "OUTPUT_OR_RECEIPT_MISMATCH",
        "comparison": comparison,
        "timing": timing,
        "output": output,
        "implementation": implementation,
        "retention_inside_timing": False,
    }
    sample_binding = write_new(directory / "SAMPLE.json", sample)
    return {"sample": sample_binding, "status": sample["status"]}


def command_worker(args: argparse.Namespace) -> int:
    config = validate_config(args.config, require_runtime=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if shutil.disk_usage(output).free < config["minimum_free_bytes"]:
        raise RuntimeError("worker output reserve is below one GiB")
    from experiments.v4_paper_apps_pyoptix.dbscan_adapter import load_input
    data = load_input(config["data_root"])
    # Module import and argument-parser startup are outside both arms' public
    # prepare/execute endpoints. Runtime/library initialization remains inside.
    if args.arm == "A":
        load_v4_app(Path(config["source_root"]))
    report: dict[str, object] = {
        "schema": f"{SCHEMA}.worker",
        "status": "INCOMPLETE",
        "process_token": str(uuid.uuid4()),
        "pid": os.getpid(),
        "arm": args.arm,
        "endpoint": args.endpoint,
        "warmups": args.warmups,
        "calls_requested": args.calls,
        "config": binding(args.config),
        "input_manifest_sha256": data["manifest_sha256"],
        "calls": [],
        "formal_performance_claim_allowed": False,
    }
    sampler = MemorySampler(config["gpu_uuid"])
    sampler.start()
    owner = None
    return_code = 2
    try:
        if args.endpoint == "prepared":
            started = time.perf_counter_ns()
            owner = prepare_arm(config, args.arm, data)
            report["prepare_ns"] = time.perf_counter_ns() - started
            for ordinal in range(args.warmups + args.calls):
                phase = "warmup" if ordinal < args.warmups else "timed"
                start = time.perf_counter_ns()
                raw = execute_arm(owner, args.arm, data)
                returned = time.perf_counter_ns()
                comparison = verify_result(
                    config, args.arm, raw, data["expected"])
                compared = time.perf_counter_ns()
                timing = {
                    "public_full_return_ns": returned - start,
                    "same_external_oracle_ns": compared - returned,
                    PRIMARY_ENDPOINT: compared - start,
                }
                row = retain_call(
                    output / f"call-{ordinal:04d}", raw=raw,
                    comparison=comparison, timing=timing, phase=phase,
                    ordinal=ordinal)
                report["calls"].append(row)
                if row["status"] != "FULL_OUTPUT_ORACLE_PASS":
                    report["status"] = "RETAINED_CALL_FAILURE"
                    break
            else:
                report["status"] = "ALL_REQUESTED_CALLS_RETAINED"
                return_code = 0
        else:
            if args.warmups != 0 or args.calls != 1:
                raise ValueError("lifecycle worker requires zero warmups and one call")
            start = time.perf_counter_ns()
            owner = prepare_arm(config, args.arm, data)
            raw = execute_arm(owner, args.arm, data)
            owner.close()
            owner = None
            returned = time.perf_counter_ns()
            comparison = verify_result(
                config, args.arm, raw, data["expected"])
            compared = time.perf_counter_ns()
            timing = {
                "prepare_first_public_return_and_close_ns": returned - start,
                "same_external_oracle_ns": compared - returned,
                LIFECYCLE_ENDPOINT: compared - start,
            }
            row = retain_call(
                output / "call-0000", raw=raw, comparison=comparison,
                timing=timing, phase="timed", ordinal=0)
            report["calls"].append(row)
            report["status"] = (
                "ALL_REQUESTED_CALLS_RETAINED"
                if row["status"] == "FULL_OUTPUT_ORACLE_PASS"
                else "RETAINED_CALL_FAILURE")
            return_code = 0 if report["status"] == \
                "ALL_REQUESTED_CALLS_RETAINED" else 2
    except BaseException as error:
        report.update(
            status="STRUCTURED_WORKER_FAILURE",
            error_type=type(error).__name__,
            error=str(error),
        )
    finally:
        if owner is not None:
            try:
                owner.close()
            except BaseException as error:
                report.update(
                    prior_status=report["status"],
                    status="OWNER_CLOSE_FAILURE",
                    close_error_type=type(error).__name__,
                    close_error=str(error),
                )
                return_code = 2
        report["gpu_memory"] = sampler.stop()
        report["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        report["not_executed_call_count"] = (
            args.warmups + args.calls - len(report["calls"]))
        write_new(output / "WORKER.json", report)
    return return_code


def worker_environment(config: dict[str, object]) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        CUDA_VISIBLE_DEVICES=config["gpu_uuid"],
        CUDA_HOME=config["cuda_home"],
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPATH=os.pathsep.join((
            str(Path(config["source_root"]) / "src"),
            config["source_root"],
        )),
    )
    old_ld = environment.get("LD_LIBRARY_PATH", "")
    environment["LD_LIBRARY_PATH"] = os.pathsep.join(filter(None, (
        config["nvrtc_library_dir"],
        config["pyoptix_library_dir"],
        config["cuda_library_dir"],
        old_ld,
    )))
    return environment


def run_worker(
    config_path: Path,
    output: Path,
    *,
    arm: str,
    endpoint: str,
    warmups: int,
    calls: int,
) -> dict[str, object]:
    config = validate_config(config_path, require_runtime=False)
    output.mkdir(parents=True, exist_ok=False)
    command = [
        config["python_invocation_path"], str(Path(__file__).resolve()),
        "worker", "--config", str(config_path.resolve()), "--output",
        str((output / "raw").resolve()), "--arm", arm, "--endpoint", endpoint,
        "--warmups", str(warmups), "--calls", str(calls),
    ]
    intent = {
        "command": command,
        "arm": arm,
        "endpoint": endpoint,
        "warmups": warmups,
        "calls": calls,
    }
    write_new(output / "INTENT.json", intent)
    started = time.perf_counter_ns()
    timed_out = False
    return_code = None
    with (output / "stdout.log").open("xb") as stdout, \
            (output / "stderr.log").open("xb") as stderr:
        try:
            result = subprocess.run(
                command,
                cwd=config["source_root"],
                env=worker_environment(config),
                stdout=stdout,
                stderr=stderr,
                timeout=3600,
                check=False,
            )
            return_code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    launch = {
        **intent,
        "return_code": return_code,
        "timed_out": timed_out,
        "controller_wall_ns": time.perf_counter_ns() - started,
        "stdout": binding(output / "stdout.log"),
        "stderr": binding(output / "stderr.log"),
        "worker": binding(output / "raw/WORKER.json")
            if (output / "raw/WORKER.json").is_file() else None,
    }
    write_new(output / "LAUNCH.json", launch)
    return launch


def command_controller(args: argparse.Namespace) -> int:
    config = validate_config(args.config, require_runtime=False)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.mode == "check":
        schedule = [("A", "prepared", 0, 1), ("C", "prepared", 0, 1)]
    elif args.mode == "calibrate":
        schedule = [("C", "prepared", 1, 3)]
    elif args.mode == "lifecycle":
        schedule = [("A", "lifecycle", 0, 1), ("C", "lifecycle", 0, 1)]
    else:
        prereg = read_json(args.preregistration)
        if prereg.get("schema") != PREREG_SCHEMA \
                or prereg.get("status") != \
                    "FROZEN_BEFORE_FIRST_MEASUREMENT_WORKER" \
                or prereg.get("config") != binding(args.config) \
                or prereg.get("orders") != [list(row) for row in ORDERS] \
                or prereg.get("warmups_per_worker") != 1 \
                or prereg.get("primary_endpoint") != PRIMARY_ENDPOINT \
                or prereg.get("retries") != 0 \
                or prereg.get("discarded_samples") != 0:
            raise ValueError("measurement preregistration differs")
        if dt.datetime.fromisoformat(prereg["frozen_utc"]) >= \
                dt.datetime.now(dt.timezone.utc):
            raise ValueError("preregistration must predate measurement")
        for name in ("correctness_check", "c_only_calibration", "lifecycle_check"):
            checked_binding(prereg[name])
        calls = int(prereg["calls_per_worker"])
        if calls < 1:
            raise ValueError("preregistered call count must be positive")
        schedule = [
            (arm, "prepared", 1, calls)
            for order in ORDERS for arm in order
        ]
    report: dict[str, object] = {
        "schema": f"{SCHEMA}.controller",
        "status": "INCOMPLETE",
        "mode": args.mode,
        "config": binding(args.config),
        "preregistration": binding(args.preregistration)
            if args.preregistration else None,
        "schedule": schedule,
        "launches": [],
        "retry_count": 0,
        "discard_count": 0,
        "source_commit": config["source_commit"],
    }
    return_code = 2
    for ordinal, (arm, endpoint, warmups, calls) in enumerate(schedule):
        launch = run_worker(
            args.config,
            output / f"worker-{ordinal:02d}-{arm}",
            arm=arm,
            endpoint=endpoint,
            warmups=warmups,
            calls=calls,
        )
        report["launches"].append(launch)
        if launch["return_code"] != 0 or launch["worker"] is None \
                or read_json(launch["worker"]["path"])["status"] != \
                    "ALL_REQUESTED_CALLS_RETAINED":
            report["status"] = "FAILED_TRANSACTION__NO_RETRY"
            break
    else:
        report["status"] = "ALL_SCHEDULED_WORKERS_RETAINED__RECOUNT_REQUIRED"
        return_code = 0
    report["finished_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    report["unexecuted_schedule"] = schedule[len(report["launches"]):]
    write_new(output / "RUN.json", report)
    print(output / "RUN.json")
    return return_code


def samples_from_run(
    run_path: str | Path,
    *,
    config_path: str | Path,
    expected: dict[str, tuple[object, ...]],
) -> list[dict[str, object]]:
    run = read_json(run_path)
    if run.get("status") != "ALL_SCHEDULED_WORKERS_RETAINED__RECOUNT_REQUIRED":
        raise ValueError("controller transaction did not retain every worker")
    if run.get("config") != binding(config_path):
        raise ValueError("controller transaction config binding differs")
    from experiments.v4_paper_apps_pyoptix.dbscan_adapter import compare_output
    samples = []
    for worker_index, launch in enumerate(run["launches"]):
        worker = read_json(checked_binding(launch["worker"]))
        if worker.get("status") != "ALL_REQUESTED_CALLS_RETAINED":
            raise ValueError("worker did not retain all calls")
        for row in worker["calls"]:
            sample = read_json(checked_binding(row["sample"]))
            if sample.get("status") != "FULL_OUTPUT_ORACLE_PASS":
                raise ValueError("retained call failed output/receipt gate")
            output = read_json(checked_binding(sample["output"]))
            checked_binding(sample["implementation"])
            replay = compare_output(output, expected)
            if not replay["matched"]:
                raise ValueError("independent recount rejects retained full output")
            timing = sample.get("timing")
            if not isinstance(timing, dict) or any(
                    type(value) is not int or value <= 0
                    for value in timing.values()):
                raise ValueError("retained timing must contain positive integers")
            sample["independent_recount"] = replay
            sample.update(
                arm=worker["arm"],
                worker_index=worker_index,
                endpoint=worker["endpoint"],
                worker_prepare_ns=worker.get("prepare_ns"),
                worker_gpu_memory=worker["gpu_memory"],
            )
            samples.append(sample)
    return samples


def command_freeze(args: argparse.Namespace) -> int:
    config = validate_config(args.config, require_runtime=False)
    from experiments.v4_paper_apps_pyoptix.dbscan_adapter import load_input
    expected = load_input(read_json(args.config)["data_root"])["expected"]
    check_samples = samples_from_run(
        args.check_run, config_path=args.config, expected=expected)
    calibration = [row for row in samples_from_run(
        args.calibration_run, config_path=args.config, expected=expected)
                   if row["phase"] == "timed"]
    lifecycle = samples_from_run(
        args.lifecycle_run, config_path=args.config, expected=expected)
    if {row["arm"] for row in check_samples} != {"A", "C"} \
            or {row["arm"] for row in lifecycle} != {"A", "C"} \
            or not calibration or {row["arm"] for row in calibration} != {"C"}:
        raise ValueError("check/calibration/lifecycle predecessor coverage differs")
    if any(row["comparison"]["successful_optix_launches"] != 3
           for row in check_samples + lifecycle):
        raise ValueError("first complete DBSCAN executions require three RT traversals")
    if any(row["comparison"]["successful_optix_launches"] != 2
           for row in calibration):
        raise ValueError("post-warmup prepared DBSCAN executions require two RT traversals")
    median_c_ns = statistics.median(
        row["timing"][PRIMARY_ENDPOINT] for row in calibration)
    # At least 32 same-owner calls make both arms approximately second-scale;
    # process medians, not calls, are the final statistical units.
    calls = max(32, math.ceil(1_000_000_000 / median_c_ns))
    prereg = {
        "schema": PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_FIRST_MEASUREMENT_WORKER",
        "frozen_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "config": binding(args.config),
        "correctness_check": binding(args.check_run),
        "c_only_calibration": binding(args.calibration_run),
        "lifecycle_check": binding(args.lifecycle_run),
        "orders": [list(row) for row in ORDERS],
        "warmups_per_worker": 1,
        "calls_per_worker": calls,
        "calibration_c_median_ns": median_c_ns,
        "retries": 0,
        "discarded_samples": 0,
        "primary_endpoint": PRIMARY_ENDPOINT,
        "endpoint_contents": config["endpoint_contents"],
        "statistical_unit": "fresh_process_worker_median_paired_by_block",
        "engineering_targets": {
            "median_rtdl_over_pyoptix_at_most": 1.20,
            "every_block_rtdl_over_pyoptix_at_most": 1.35,
            "targets_are_not_sample_filters": True,
        },
    }
    write_new(args.output, prereg)
    print(args.output.resolve())
    return 0


def bootstrap_median_interval(values: list[float]) -> list[float]:
    generator = random.Random(0xDB5CA7)
    estimates = []
    for _ in range(100_000):
        estimates.append(statistics.median(
            generator.choice(values) for _ in values))
    estimates.sort()
    return [
        estimates[int(0.025 * len(estimates))],
        estimates[int(0.975 * len(estimates)) - 1],
    ]


def command_recount(args: argparse.Namespace) -> int:
    config = validate_config(args.config, require_runtime=False)
    prereg = read_json(args.preregistration)
    run = read_json(args.measurement_run)
    if prereg.get("schema") != PREREG_SCHEMA \
            or prereg.get("config") != binding(args.config) \
            or run.get("config") != binding(args.config) \
            or run.get("preregistration") != binding(args.preregistration):
        raise ValueError("measurement/config/preregistration binding differs")
    from experiments.v4_paper_apps_pyoptix.dbscan_adapter import load_input
    expected = load_input(config["data_root"])["expected"]
    lifecycle_samples = samples_from_run(
        prereg["lifecycle_check"]["path"],
        config_path=args.config,
        expected=expected,
    )
    samples = [row for row in samples_from_run(
        args.measurement_run, config_path=args.config, expected=expected)
               if row["phase"] == "timed"]
    calls = prereg["calls_per_worker"]
    if len(samples) != 16 * calls:
        raise ValueError("formal sample count differs from preregistration")
    if any(row["comparison"]["successful_optix_launches"] != 2
           for row in samples):
        raise ValueError(
            "prepared timed calls must use the same two-traversal cached-count contract")
    workers: list[dict[str, object]] = []
    for worker_index in range(16):
        rows = [row for row in samples if row["worker_index"] == worker_index]
        if len(rows) != calls or len({row["arm"] for row in rows}) != 1:
            raise ValueError("worker sample cardinality/arm differs")
        values = [row["timing"][PRIMARY_ENDPOINT] for row in rows]
        workers.append({
            "worker_index": worker_index,
            "block": worker_index // 2,
            "position": worker_index % 2,
            "arm": rows[0]["arm"],
            "median_ns": statistics.median(values),
            "minimum_ns": min(values),
            "maximum_ns": max(values),
            "all_primary_ns": values,
            "prepare_ns": rows[0]["worker_prepare_ns"],
            "gpu_memory": rows[0]["worker_gpu_memory"],
        })
    block_rows = []
    for block, expected_order in enumerate(ORDERS):
        pair = workers[2 * block:2 * block + 2]
        if tuple(row["arm"] for row in pair) != expected_order:
            raise ValueError("measured block order differs from preregistration")
        by_arm = {row["arm"]: row for row in pair}
        ratio = by_arm["A"]["median_ns"] / by_arm["C"]["median_ns"]
        block_rows.append({
            "block": block,
            "order": list(expected_order),
            "a_rtdl_median_ns": by_arm["A"]["median_ns"],
            "c_public_pyoptix_median_ns": by_arm["C"]["median_ns"],
            "rtdl_over_pyoptix": ratio,
            "pyoptix_over_rtdl_speedup": 1.0 / ratio,
        })
    ratios = [row["rtdl_over_pyoptix"] for row in block_rows]
    median_ratio = statistics.median(ratios)
    result = {
        "schema": f"{SCHEMA}.recount",
        "status": "PASS__ALL_RETAINED_OUTPUTS_AND_SAMPLES_RECOUNTED",
        "config": binding(args.config),
        "preregistration": binding(args.preregistration),
        "measurement_run": binding(args.measurement_run),
        "source_commit": config["source_commit"],
        "primary_endpoint": PRIMARY_ENDPOINT,
        "endpoint_contents": config["endpoint_contents"],
        "calls_per_worker": calls,
        "fresh_process_worker_count": 16,
        "paired_block_count": 8,
        "lifecycle_secondary": {
            row["arm"]: {
                "timing": row["timing"],
                "gpu_memory": row["worker_gpu_memory"],
                "successful_optix_launches": row["comparison"][
                    "successful_optix_launches"],
            }
            for row in lifecycle_samples
        },
        "workers": workers,
        "blocks": block_rows,
        "median_rtdl_over_pyoptix": median_ratio,
        "median_pyoptix_over_rtdl_speedup": 1.0 / median_ratio,
        "median_ratio_95pct_block_bootstrap_interval":
            bootstrap_median_interval(ratios),
        "maximum_block_rtdl_over_pyoptix": max(ratios),
        "engineering_target_evaluation": {
            "median_at_most_1_20": median_ratio <= 1.20,
            "every_block_at_most_1_35": max(ratios) <= 1.35,
            "result_retained_regardless_of_targets": True,
        },
        "claim_boundary": {
            "paper_dataset_claimed": False,
            "public_pyoptix_is_application_specialized": True,
            "rtdl_is_generic_engine_path": True,
            "external_review_completed": False,
            "paper_claim_authorized": False,
        },
    }
    write_new(args.output, result)
    print(json.dumps({
        "status": result["status"],
        "median_rtdl_over_pyoptix": median_ratio,
        "median_pyoptix_over_rtdl_speedup": 1.0 / median_ratio,
        "maximum_block_rtdl_over_pyoptix": max(ratios),
    }, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    config = commands.add_parser("config")
    config.add_argument("--source-root", required=True, type=Path)
    config.add_argument("--data-root", required=True, type=Path)
    config.add_argument("--native", required=True, type=Path)
    config.add_argument("--native-build", required=True, type=Path)
    config.add_argument("--pyoptix-build", required=True, type=Path)
    config.add_argument("--device-ptx", required=True, type=Path)
    config.add_argument("--continuation-ptx", required=True, type=Path)
    config.add_argument("--gpu-uuid", required=True)
    config.add_argument("--optix-include", required=True, type=Path)
    config.add_argument("--cuda-include", required=True, type=Path)
    config.add_argument("--cuda-home", required=True, type=Path)
    config.add_argument("--nvrtc-library-dir", required=True, type=Path)
    config.add_argument("--cuda-library-dir", required=True, type=Path)
    config.add_argument("--pyoptix-library-dir", required=True, type=Path)
    config.add_argument("--python", required=True, type=Path)
    config.add_argument("--output", required=True, type=Path)
    worker = commands.add_parser("worker")
    worker.add_argument("--config", required=True, type=Path)
    worker.add_argument("--output", required=True, type=Path)
    worker.add_argument("--arm", required=True, choices=("A", "C"))
    worker.add_argument("--endpoint", required=True,
                        choices=("prepared", "lifecycle"))
    worker.add_argument("--warmups", required=True, type=int)
    worker.add_argument("--calls", required=True, type=int)
    for mode in ("check", "calibrate", "lifecycle", "measure"):
        command = commands.add_parser(mode)
        command.set_defaults(mode=mode)
        command.add_argument("--config", required=True, type=Path)
        command.add_argument("--output", required=True, type=Path)
        if mode == "measure":
            command.add_argument("--preregistration", required=True, type=Path)
    freeze = commands.add_parser("freeze")
    freeze.add_argument("--config", required=True, type=Path)
    freeze.add_argument("--check-run", required=True, type=Path)
    freeze.add_argument("--calibration-run", required=True, type=Path)
    freeze.add_argument("--lifecycle-run", required=True, type=Path)
    freeze.add_argument("--output", required=True, type=Path)
    recount = commands.add_parser("recount")
    recount.add_argument("--config", required=True, type=Path)
    recount.add_argument("--preregistration", required=True, type=Path)
    recount.add_argument("--measurement-run", required=True, type=Path)
    recount.add_argument("--output", required=True, type=Path)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "config":
        return command_config(args)
    if args.command == "worker":
        if args.warmups < 0 or args.calls < 1:
            raise ValueError("worker warmups/calls must be nonnegative/positive")
        return command_worker(args)
    if args.command in {"check", "calibrate", "lifecycle", "measure"}:
        return command_controller(args)
    if args.command == "freeze":
        return command_freeze(args)
    if args.command == "recount":
        return command_recount(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
