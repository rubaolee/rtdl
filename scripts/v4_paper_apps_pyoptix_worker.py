#!/usr/bin/env python3
"""Create-only worker for one V4 paper-app / PyOptiX comparison arm.

The module imports only the standard library before ``main``.  Complete-stage
timing therefore begins before application, NumPy, RTDL, CuPy, or PyOptiX
imports.  Every terminal failure is written to the requested result path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

APPS = ("particle_tracking", "triangle_counting", "librts")
ARMS = ("v4", "pyoptix")
ENDPOINTS = ("complete", "first_result", "prepared")


def _sha(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()


def _traversal_projection(receipt: object) -> dict[str, Any]:
    if not isinstance(receipt, Mapping):
        raise RuntimeError(  # noqa: TRY004 - malformed public runtime output
            "V4 public output lacks a traversal receipt"
        )
    classification = receipt.get("physical_executor_classification")
    receipt_sha256 = receipt.get("receipt_sha256")
    if (
        classification != "optix_traversal_observed"
        or not isinstance(receipt_sha256, str)
        or len(receipt_sha256) != 64
    ):
        raise RuntimeError("V4 public traversal receipt is not compact-auditable")
    return {
        "schema": receipt.get("schema"),
        "receipt_sha256": receipt_sha256,
        "physical_executor_classification": classification,
        "route_identity": receipt.get("route_identity"),
        "expected_program_bundle": receipt.get("expected_program_bundle"),
    }


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _machine() -> dict[str, object]:
    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not visible or "," in visible:
        raise RuntimeError("worker requires exactly one CUDA_VISIBLE_DEVICES selector")
    command = [
        "nvidia-smi",
        "-i",
        visible,
        "--query-gpu=name,uuid,compute_cap,driver_version",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as error:
        return {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "gpu": {"nvidia_smi_error": str(error)},
        }
    if completed.returncode:
        gpu = {"nvidia_smi_error": completed.stderr.strip()}
    else:
        rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
        if len(rows) != 1:
            raise RuntimeError(f"worker requires exactly one visible GPU: {rows!r}")
        fields = [field.strip() for field in rows[0].split(",")]
        if len(fields) != 4:
            raise RuntimeError(f"unexpected nvidia-smi row: {rows[0]!r}")
        gpu = dict(zip(("name", "uuid", "compute_capability", "driver"), fields))
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": str(Path(sys.executable).resolve()),
        "gpu": gpu,
        "cuda_visible_devices": visible,
    }


def _source_identity(config: Mapping[str, Any], config_path: Path) -> dict[str, Any]:
    source_root = Path(config["source_root"]).resolve(strict=True)

    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=source_root,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()

    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    dirty = git("status", "--porcelain=v1", "--untracked-files=all")
    if (
        commit != config.get("source_commit")
        or tree != config.get("source_tree")
        or dirty
    ):
        raise RuntimeError(
            "worker source identity differs from clean registered config"
        )
    return {
        "git_commit": commit,
        "git_tree": tree,
        "git_status_clean": True,
        "worker_sha256": _sha(Path(__file__).resolve()),
        "config_sha256": _sha(config_path),
    }


def _rtdl_runtime(config: Mapping[str, Any]) -> dict[str, Any]:
    import numba
    import numpy as np

    from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

    native = Path(config["native_library_path"]).resolve(strict=True)
    native_sha256 = _sha(native)
    if native_sha256 != config.get("native_library_sha256"):
        raise RuntimeError("RTDL native library differs from registered config")
    cc = tuple(int(value) for value in config["compute_capability"])
    if len(cc) != 2:
        raise ValueError("compute_capability must contain major/minor")
    os.environ["RTDL_OPTIX_LIB"] = str(native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(native)
    return {
        "target": ReferenceTargetProfile(
            provider="optix",
            optix_sdk=str(config.get("optix_sdk", "9.0.0")),
            compute_capability=f"{cc[0]}.{cc[1]}",
            native_sha256=native_sha256,
            supports_custom_aabb=True,
            supports_builtin_triangle=True,
        ),
        "compute_capability": cc,
        "optix_include": Path(config["optix_include"]).resolve(strict=True),
        "cuda_include": Path(config["cuda_include"]).resolve(strict=True),
        "expected_python_version": platform.python_version(),
        "expected_numba_version": numba.__version__,
        "expected_numpy_version": np.__version__,
        "native_library_path": native,
    }


def _runtime_identity(arm: str) -> dict[str, Any]:
    package_names = (
        "cuda-bindings",
        "cuda-python",
        "cupy-cuda12x",
        "numba",
        "numpy",
        "pyoptix",
    )
    packages = {}
    for name in package_names:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    value: dict[str, Any] = {
        "python_executable": str(Path(sys.executable).resolve(strict=True)),
        "python_executable_sha256": _sha(Path(sys.executable).resolve(strict=True)),
        "python_version": platform.python_version(),
        "package_versions": packages,
    }
    if arm == "pyoptix":
        extension = sys.modules.get("optix._optix")
        extension_path = getattr(extension, "__file__", None)
        if not extension_path:
            raise RuntimeError("PyOptiX arm did not load optix._optix")
        resolved = Path(extension_path).resolve(strict=True)
        value["pyoptix_loaded_extension_path"] = str(resolved)
        value["pyoptix_loaded_extension_sha256"] = _sha(resolved)
    return value


def _validate_runtime_identity(
    arm: str, observed: Mapping[str, Any], config: Mapping[str, Any]
) -> None:
    for name in ("python_executable_sha256", "python_version", "package_versions"):
        if observed.get(name) != config.get(name):
            raise RuntimeError(f"worker runtime identity differs: {name}")
    if arm == "pyoptix" and observed.get(
        "pyoptix_loaded_extension_sha256"
    ) != config.get("pyoptix_loaded_extension_sha256"):
        raise RuntimeError("loaded PyOptiX extension differs from build receipt")
    for path_name, hash_name in (
        ("data_manifest_path", "data_manifest_sha256"),
        ("native_build_manifest_path", "native_build_manifest_sha256"),
        ("pyoptix_build_receipt_path", "pyoptix_build_receipt_sha256"),
        ("pyoptix_ptx_manifest_path", "pyoptix_ptx_manifest_sha256"),
    ):
        path = Path(str(config[path_name])).resolve(strict=True)
        if _sha(path) != config.get(hash_name):
            raise RuntimeError(f"registered external evidence differs: {path_name}")


def _prebuilt_ptx(config: Mapping[str, Any], app: str) -> bytes:
    programs = config.get("pyoptix_prebuilt_ptx")
    if not isinstance(programs, Mapping) or app not in programs:
        raise RuntimeError(f"config lacks prebuilt PyOptiX PTX: {app}")
    row = programs[app]
    if not isinstance(row, Mapping):
        raise TypeError(f"prebuilt PyOptiX PTX row is malformed: {app}")
    path = Path(str(row.get("path"))).resolve(strict=True)
    ptx = path.read_bytes()
    if _sha(path) != row.get("sha256") or b".version" not in ptx[:4096]:
        raise RuntimeError(f"prebuilt PyOptiX PTX differs: {app}")
    return ptx


def _validate_machine_identity(
    observed: Mapping[str, Any], config: Mapping[str, Any]
) -> None:
    registered = config.get("registered_machine")
    if not isinstance(registered, Mapping):
        raise TypeError("worker config lacks a registered machine")
    if observed.get("cuda_visible_devices") != registered.get(
        "cuda_visible_devices"
    ) or observed.get("gpu") != registered.get("gpu"):
        raise RuntimeError("worker machine differs from registered config")


def _load_input(
    app: str, config: Mapping[str, Any], *, operation: str | None
) -> tuple[dict[str, Any], dict[str, Any]]:
    from experiments.v4_paper_apps_pyoptix import inputs

    source_root = Path(config["source_root"]).resolve(strict=True)
    data_root = Path(config["data_root"]).resolve(strict=True)
    if app == "particle_tracking":
        data = inputs.load_particle(data_root)
        identity = {"input_sha256": data["input_sha256"]}
    elif app == "triangle_counting":
        data = inputs.load_triangle(source_root, data_root)
        identity = {
            "edge_file_sha256": data["edge_file_sha256"],
            "dataset": data["dataset"],
            "expected_triangle_count": data["expected_triangle_count"],
            "paper_algorithm": data["paper_algorithm"],
        }
    elif app == "librts":
        if operation is None:
            raise ValueError("LibRTS worker requires --operation")
        data = inputs.load_librts(data_root, operation=operation)
        identity = {
            "cache_npz_sha256": data["cache_npz_sha256"],
            "cache_json_sha256": data["cache_json_sha256"],
            "query_sha256": data["query_sha256"],
            "expected_count": data["expected_count"],
            "operation": operation,
        }
    else:
        raise ValueError(f"unsupported first-batch app: {app}")
    return data, identity


def _particle_case(
    arm: str, config: Mapping[str, Any], data: Mapping[str, Any]
) -> tuple[Callable[[], dict[str, Any]], Callable[[], None], dict[str, Any]]:
    source_root = Path(config["source_root"]).resolve(strict=True)
    adapter = __import__(
        "experiments.v4_paper_apps_pyoptix.particle_adapter",
        fromlist=["particle_adapter"],
    )
    if arm == "v4":
        app = _load_module(
            source_root
            / "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py",
            "v4_pyoptix_worker_particle_app",
        )
        owner = app.prepare_v4(**_rtdl_runtime(config), prepared_input=data)

        def execute() -> dict[str, Any]:
            observed = adapter.observe_v4_particle_result(
                owner.execute(), data["expected"]
            )
            observed["compact_execution_evidence"] = _traversal_projection(
                observed["traversal_receipt"]
            )
            observed["detailed_receipt_retention_count"] = 0
            return observed

        metadata = {
            "path_class": "v4_public_paper_app_prepared_owner",
            "device_source_shared_with_pyoptix": False,
            "device_semantics_matched_with_pyoptix": True,
            "private_checker_off_path": False,
            "rtdlexe_lifecycle_used": False,
            "restricted_callback_compile_in_complete": True,
        }
    else:
        ptx = _prebuilt_ptx(config, "particle_tracking")
        owner = adapter.prepare_pyoptix_particle(data, prebuilt_ptx=ptx)

        def execute() -> dict[str, Any]:
            observed = adapter.execute_pyoptix_particle(owner, data)
            observed["compact_execution_evidence"] = {
                "kind": "public_pyoptix_device_status_and_operation_counts",
                "control": list(observed["control"]),
                "operation_counts": observed["operation_counts"],
            }
            observed["detailed_receipt_retention_count"] = 0
            return observed

        metadata = {
            "path_class": "public_pyoptix_semantically_matched_particle_program",
            "device_source_shared_with_v4": False,
            "device_semantics_matched_with_v4": True,
            "private_rtdl_native_called": False,
            "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        }
    return execute, owner.close, metadata


def _triangle_case(
    arm: str, config: Mapping[str, Any], data: Mapping[str, Any]
) -> tuple[Callable[[], dict[str, Any]], Callable[[], None], dict[str, Any]]:
    source_root = Path(config["source_root"]).resolve(strict=True)
    if arm == "v4":
        app = _load_module(
            source_root
            / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
            "v4_pyoptix_worker_triangle_app",
        )
        owner = app.prepare_v4_segmented(
            "RT-2A1",
            **_rtdl_runtime(config),
            edge_file=str(data["edge_file"]),
            expected_triangle_count=int(data["expected_triangle_count"]),
            max_relation_rows=int(data["max_relation_rows"]),
            prepared_graph_contract=data["graph_contract"],
        )

        def execute() -> dict[str, Any]:
            result = owner.execute()
            value = int(result["output"]["triangle_count"])
            if result.get("matched") is not True or value != int(
                data["expected_triangle_count"]
            ):
                raise RuntimeError("triangle V4 full-app output mismatch")
            receipts = result.get("traversal_receipts")
            if not isinstance(receipts, list) or not receipts:
                raise RuntimeError("triangle V4 output lacks traversal receipts")
            compact = [_traversal_projection(receipt) for receipt in receipts]
            return {
                "output_sha256": _digest({"triangle_count": value}),
                "triangle_count": value,
                "segment_count": int(result["segment_count"]),
                "matched": True,
                "public_output_materialized_inside_call": True,
                "compact_execution_evidence": {
                    "kind": "rtdl_segmented_traversal_receipt_projection",
                    "segment_receipts": compact,
                },
                "detailed_receipt_retention_count": 0,
            }

        metadata = {
            "path_class": "v4_standard_callback_general_leaf_device_columns",
            "private_checker_off_path": False,
            "standard_count_fast_control_used": False,
            "device_columns_preserved": True,
            "post_traversal_reduction": "cupy_checked_u64_weighted_sum_device",
        }
    else:
        owner_module = __import__(
            "experiments.v4_paper_apps_pyoptix.triangle_owner",
            fromlist=["triangle_owner"],
        )
        owner = owner_module.PublicPyOptixTriangleCountingOwner.prepare(
            prebuilt_ptx=_prebuilt_ptx(config, "triangle_counting"),
        )

        def execute() -> dict[str, Any]:
            result = owner.execute_graph(
                graph_contract=data["graph_contract"],
                segment_iterator=data["segment_iterator"],
                max_relation_rows=int(data["max_relation_rows"]),
            )
            value = int(result["output"]["triangle_count"])
            statuses = [int(row["device_status"]) for row in result["segments"]]
            if any(statuses):
                raise RuntimeError("triangle PyOptiX segment status failed")
            return {
                "output_sha256": _digest({"triangle_count": value}),
                "triangle_count": value,
                "segment_count": int(result["segment_count"]),
                "matched": bool(result["matched"]),
                "public_output_materialized_inside_call": True,
                "compact_execution_evidence": {
                    "kind": "public_pyoptix_segment_device_status",
                    "segment_statuses": statuses,
                },
                "detailed_receipt_retention_count": 0,
            }

        metadata = {
            "path_class": "public_pyoptix_rt_2a1_device_weighted_reduction",
            "private_rtdl_native_called": False,
            "ptx_sha256": hashlib.sha256(owner.ptx).hexdigest(),
        }
    return execute, owner.close, metadata


def _librts_case(
    arm: str, config: Mapping[str, Any], data: Mapping[str, Any]
) -> tuple[Callable[[], dict[str, Any]], Callable[[], None], dict[str, Any]]:
    source_root = Path(config["source_root"]).resolve(strict=True)
    operation = str(data["operation"])
    if arm == "v4":
        app = _load_module(
            source_root / "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
            "v4_pyoptix_worker_librts_app",
        )
        owner = app.prepare_v4_real_scale_count(
            target=_rtdl_runtime(config)["target"],
            indexed_columns=data["indexed"],
            operation=operation,
            native_library_path=config["native_library_path"],
        )
        kwargs = (
            {"point_queries": data["queries"]}
            if operation == "point_contains"
            else {"box_queries": data["queries"]}
        )
        owner.bind_queries(**kwargs)

        def execute() -> dict[str, Any]:
            result = owner.execute_count()
            value = int(result["count"])
            if value != int(data["expected_count"]):
                raise RuntimeError("LibRTS V4 full-app output mismatch")
            if not isinstance(result.get("traversal_receipt"), Mapping):
                raise RuntimeError(  # noqa: TRY004 - malformed runtime output
                    "LibRTS V4 output lacks traversal receipt"
                )
            compact = _traversal_projection(result["traversal_receipt"])
            return {
                "output_sha256": _digest({"count": value}),
                "count": value,
                "operation": operation,
                "matched": True,
                "public_output_materialized_inside_call": True,
                "compact_execution_evidence": compact,
                "detailed_receipt_retention_count": 0,
            }

        metadata = {
            "path_class": "v4_fixed_aabb_count_specialization",
            "private_checker_off_path": False,
        }
    else:
        owner_module = __import__(
            "experiments.v4_paper_apps_pyoptix.librts_owner",
            fromlist=["librts_owner"],
        )
        owner = owner_module.PublicPyOptixLibRTSCountOwner.prepare(
            data["indexed"],
            prebuilt_ptx=_prebuilt_ptx(config, "librts"),
        )
        owner.bind_queries(operation=operation, queries=data["queries"])

        def execute() -> dict[str, Any]:
            result = owner.execute_count(
                operation=operation,
                expected_count=int(data["expected_count"]),
            )
            if result.device_status:
                raise RuntimeError("LibRTS PyOptiX device status failed")
            return {
                "output_sha256": _digest({"count": result.checked_u64}),
                "count": result.checked_u64,
                "operation": operation,
                "matched": True,
                "public_output_materialized_inside_call": True,
                "compact_execution_evidence": {
                    "kind": "public_pyoptix_device_status",
                    "device_status": int(result.device_status),
                },
                "detailed_receipt_retention_count": 0,
            }

        metadata = {
            "path_class": "public_pyoptix_custom_aabb_device_count",
            "private_rtdl_native_called": False,
            "prepared_query_columns": True,
            "ptx_sha256": hashlib.sha256(owner.ptx).hexdigest(),
        }
    return execute, owner.close, metadata


def _prepare_case(
    app: str, arm: str, config: Mapping[str, Any], data: Mapping[str, Any]
) -> tuple[Callable[[], dict[str, Any]], Callable[[], None], dict[str, Any]]:
    if app == "particle_tracking":
        return _particle_case(arm, config, data)
    if app == "triangle_counting":
        return _triangle_case(arm, config, data)
    if app == "librts":
        return _librts_case(arm, config, data)
    raise ValueError(app)


def _run(
    *,
    app: str,
    arm: str,
    endpoint: str,
    operation: str | None,
    config: Mapping[str, Any],
    repetitions: int,
    warmups: int,
) -> dict[str, Any]:
    if endpoint == "complete" and (repetitions != 1 or warmups != 0):
        raise ValueError("complete endpoint requires one repetition and no warmup")
    if endpoint == "first_result" and (repetitions != 1 or warmups != 0):
        raise ValueError("first_result requires one repetition and no warmup")
    if repetitions <= 0 or warmups < 0:
        raise ValueError("worker repetition counts differ")

    load_started = time.perf_counter_ns()
    data, input_identity = _load_input(app, config, operation=operation)
    load_ended = time.perf_counter_ns()
    complete_started = time.perf_counter_ns() if endpoint == "complete" else None
    prepare_started = time.perf_counter_ns()
    execute, close, method = _prepare_case(app, arm, config, data)
    prepare_ended = time.perf_counter_ns()

    samples: list[int] = []
    digests: list[str] = []
    outputs: list[dict[str, Any]] = []
    try:
        for _ in range(warmups):
            warm = execute()
            if warm.get("matched") is not True:
                raise RuntimeError("warmup output mismatch")
        for _ in range(repetitions):
            started = time.perf_counter_ns()
            output = execute()
            ended = time.perf_counter_ns()
            if ended <= started or output.get("matched") is not True:
                raise RuntimeError("timed app execution failed")
            samples.append(ended - started)
            digests.append(str(output["output_sha256"]))
            outputs.append(
                {
                    key: value
                    for key, value in output.items()
                    if key not in {"output", "traversal_receipt", "lifecycle_receipt"}
                }
            )
        if len(set(digests)) != 1:
            raise RuntimeError("application output changed across repetitions")
    finally:
        close_started = time.perf_counter_ns()
        close()
        close_ended = time.perf_counter_ns()
    complete_ended = time.perf_counter_ns() if endpoint == "complete" else None
    primary = (
        [int(complete_ended - complete_started)]
        if complete_started is not None and complete_ended is not None
        else samples
    )
    return {
        "schema": "rtdl.v4_paper_apps_pyoptix.worker_result.v1",
        "status": "PASS",
        "app": app,
        "operation": operation,
        "arm": arm,
        "endpoint": endpoint,
        "input_identity": input_identity,
        "method": method,
        "primary_samples_ns": primary,
        "execute_samples_ns": samples,
        "warmup_count": warmups,
        "retained_sample_count": len(primary),
        "output_sha256": digests[0],
        "outputs": outputs,
        "phase_ns": {
            "load": load_ended - load_started,
            "prepare": prepare_ended - prepare_started,
            "close": close_ended - close_started,
        },
        "complete_timer_includes_prepare_execute_close": endpoint == "complete",
        "input_load_included_in_primary_timer": False,
        "retry_count": 0,
        "discard_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--app", choices=APPS, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--endpoint", choices=ENDPOINTS, required=True)
    parser.add_argument("--operation", choices=("point_contains", "range_contains"))
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--warmups", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    started = time.perf_counter_ns()
    exit_code = 0
    config: dict[str, Any] | None = None
    try:
        loaded_config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(loaded_config, dict):
            raise TypeError("worker config root must be an object")
        if loaded_config.get("schema") != "rtdl.v4_paper_apps_pyoptix.config.v1":
            raise ValueError("worker config schema differs")
        config = loaded_config
        result = _run(
            app=args.app,
            arm=args.arm,
            endpoint=args.endpoint,
            operation=args.operation,
            config=config,
            repetitions=args.repetitions,
            warmups=args.warmups,
        )
    # A formal worker must persist even KeyboardInterrupt/SystemExit as adverse rows.
    except BaseException as error:  # noqa: BLE001
        exit_code = 1
        result = {
            "schema": "rtdl.v4_paper_apps_pyoptix.worker_result.v1",
            "status": "FAIL",
            "app": args.app,
            "operation": args.operation,
            "arm": args.arm,
            "endpoint": args.endpoint,
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
            "retry_count": 0,
            "discard_count": 0,
        }
    if config is None:
        runtime_identity = {"status": "FAILED_TO_BIND"}
        source_identity = {"status": "FAILED_TO_BIND"}
    else:
        try:
            runtime_identity = _runtime_identity(args.arm)
            _validate_runtime_identity(args.arm, runtime_identity, config)
        except BaseException as error:  # noqa: BLE001 - retain identity failure
            exit_code = 1
            result = {
                **result,
                "status": "FAIL",
                "runtime_identity_error_type": type(error).__name__,
                "runtime_identity_error": str(error),
                "runtime_identity_traceback": traceback.format_exc(),
            }
            runtime_identity = {"status": "FAILED_TO_BIND"}
        try:
            source_identity = _source_identity(config, args.config.resolve(strict=True))
        except BaseException as error:  # noqa: BLE001 - retain custody failure
            exit_code = 1
            result = {
                **result,
                "status": "FAIL",
                "source_identity_error_type": type(error).__name__,
                "source_identity_error": str(error),
                "source_identity_traceback": traceback.format_exc(),
            }
            source_identity = {"status": "FAILED_TO_BIND"}
    machine: dict[str, object] = {}
    try:
        machine = _machine()
        _validate_machine_identity(machine, config or {})
    except BaseException as error:  # noqa: BLE001 - retain machine-binding failure
        exit_code = 1
        result = {
            **result,
            "status": "FAIL",
            "machine_identity_error_type": type(error).__name__,
            "machine_identity_error": str(error),
            "machine_identity_traceback": traceback.format_exc(),
        }
        if not machine:
            machine = {"status": "FAILED_TO_BIND"}
    result["worker_wall_ns"] = time.perf_counter_ns() - started
    result["process_id"] = os.getpid()
    result["machine"] = machine
    result["runtime_identity"] = runtime_identity
    result["source_identity"] = source_identity
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "app": args.app,
                "arm": args.arm,
                "endpoint": args.endpoint,
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
