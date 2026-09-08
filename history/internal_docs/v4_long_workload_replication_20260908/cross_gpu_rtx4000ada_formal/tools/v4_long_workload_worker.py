#!/usr/bin/env python3
"""Create-only worker for the frozen three-arm long-workload transaction."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import statistics
import subprocess
import sys
import time
import traceback
from collections.abc import Mapping
from pathlib import Path
from typing import Any


ARMS = ("old_v4", "new_v4", "pyoptix")
ENDPOINTS = ("complete", "prepared")
CONFIG_SCHEMA = "rtdl.v4_long_workload.formal_config.v1"
RESULT_SCHEMA = "rtdl.v4_long_workload.worker_result.v1"
JOURNAL_SCHEMA = "rtdl.v4_long_workload.worker_journal.v1"
CPU_AFFINITY_FIELDS = frozenset({"cpu_ids"})


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _append(path: Path, value: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, text=True,
        capture_output=True,
    ).stdout.strip()


def _load_base_worker(root: Path):
    path = root / "scripts/v4_paper_apps_pyoptix_worker.py"
    spec = importlib.util.spec_from_file_location(
        f"v4_long_workload_base_{os.getpid()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load base worker: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def _activate_root(root: Path, all_roots: tuple[Path, ...]) -> None:
    rejected = {str(item) for base in all_roots for item in (base, base / "src")}
    sys.path[:] = [item for item in sys.path if item not in rejected]
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))


def _selected_config(config: Mapping[str, Any], arm: str) -> dict[str, Any]:
    common = config.get("common")
    implementations = config.get("implementations")
    if not isinstance(common, Mapping) or not isinstance(implementations, Mapping):
        raise TypeError("formal config lacks common/implementations mappings")
    selected = implementations.get(arm)
    if not isinstance(selected, Mapping):
        raise KeyError(f"formal config lacks implementation arm: {arm}")
    result = dict(common)
    result.update(selected)
    required = (
        "source_root", "source_commit", "source_tree", "native_library_path",
        "native_library_sha256",
    )
    if any(not result.get(name) for name in required):
        raise ValueError(f"implementation arm is incomplete: {arm}")
    return result


def _bind_cpu_affinity(
    config: Mapping[str, Any], *, apply: bool,
) -> dict[str, Any] | None:
    """Apply or observe one registered, non-migrating worker CPU set."""

    contract = config.get("cpu_affinity")
    if contract is None:
        return None
    if not isinstance(contract, Mapping) or set(contract) != CPU_AFFINITY_FIELDS:
        raise ValueError("CPU-affinity contract fields differ")
    cpu_ids = contract.get("cpu_ids")
    if not isinstance(cpu_ids, list) or len(cpu_ids) != 1 \
            or type(cpu_ids[0]) is not int or cpu_ids[0] < 0:
        raise ValueError("CPU-affinity contract requires one logical CPU")
    setter = getattr(os, "sched_setaffinity", None)
    getter = getattr(os, "sched_getaffinity", None)
    if not callable(setter) or not callable(getter):
        raise RuntimeError("registered CPU affinity requires Linux sched affinity")
    if apply:
        setter(0, set(cpu_ids))
    observed = sorted(int(value) for value in getter(0))
    if observed != cpu_ids:
        raise RuntimeError(
            "CPU-affinity observation differs from registered contract: "
            f"expected={cpu_ids!r} observed={observed!r}"
        )
    return {"cpu_ids": observed}


def _load_input(base, unit: Mapping[str, Any], config: Mapping[str, Any]):
    app = str(unit["app"])
    operation = unit.get("operation")
    if app != "triangle_counting":
        return base._load_input(app, config, operation=operation)

    from experiments.v4_paper_apps_pyoptix import inputs

    dataset = str(unit["dataset"])
    expected = int(unit["expected_triangle_count"])
    cap = int(unit["max_relation_rows"])
    if cap <= 0:
        raise ValueError("triangle relation cap must be positive")
    data = inputs.load_triangle(
        config["source_root"], config["data_root"],
        dataset=dataset, expected_triangle_count=expected,
    )
    data["max_relation_rows"] = cap
    identity = {
        "edge_file_sha256": data["edge_file_sha256"],
        "dataset": dataset,
        "expected_triangle_count": expected,
        "paper_algorithm": data["paper_algorithm"],
        "max_relation_rows": cap,
    }
    return data, identity


def _run(
    *, base, unit: Mapping[str, Any], base_arm: str,
    selected_config: Mapping[str, Any], endpoint: str,
    repetitions: int, warmups: int, journal: Path,
) -> dict[str, Any]:
    if endpoint == "complete" and (repetitions != 1 or warmups != 0):
        raise ValueError("complete endpoint requires one repetition and no warmup")
    if endpoint == "prepared" and (repetitions <= 0 or warmups < 0):
        raise ValueError("prepared repetition counts are invalid")

    load_started = time.perf_counter_ns()
    data, input_identity = _load_input(base, unit, selected_config)
    load_ended = time.perf_counter_ns()
    complete_started = time.perf_counter_ns() if endpoint == "complete" else None
    prepare_started = time.perf_counter_ns()
    execute, close, method = base._prepare_case(
        str(unit["app"]), base_arm, selected_config, data)
    prepare_ended = time.perf_counter_ns()
    if endpoint == "prepared":
        _append(journal, {
            "schema": JOURNAL_SCHEMA, "event": "prepared",
            "prepare_ns": prepare_ended - prepare_started,
        })

    samples: list[int] = []
    digests: list[str] = []
    outputs: list[dict[str, Any]] = []
    close_started = close_ended = None
    try:
        for index in range(warmups):
            observed = execute()
            if observed.get("matched") is not True:
                raise RuntimeError("warmup output mismatch")
            _append(journal, {
                "schema": JOURNAL_SCHEMA, "event": "warmup_complete",
                "index": index, "output_sha256": str(observed["output_sha256"]),
            })
        for index in range(repetitions):
            started = time.perf_counter_ns()
            observed = execute()
            ended = time.perf_counter_ns()
            if ended <= started or observed.get("matched") is not True:
                raise RuntimeError("timed app execution failed")
            elapsed = ended - started
            digest = str(observed["output_sha256"])
            samples.append(elapsed)
            digests.append(digest)
            outputs.append({
                key: value for key, value in observed.items()
                if key not in {"output", "traversal_receipt", "lifecycle_receipt"}
            })
            if endpoint == "prepared":
                _append(journal, {
                    "schema": JOURNAL_SCHEMA, "event": "sample_complete",
                    "index": index, "elapsed_ns": elapsed,
                    "output_sha256": digest,
                })
        if len(set(digests)) != 1:
            raise RuntimeError("application output changed across repetitions")
    finally:
        close_started = time.perf_counter_ns()
        close()
        close_ended = time.perf_counter_ns()
        if endpoint == "prepared":
            _append(journal, {
                "schema": JOURNAL_SCHEMA, "event": "close_complete",
                "close_ns": close_ended - close_started,
            })
    complete_ended = time.perf_counter_ns() if endpoint == "complete" else None
    if endpoint == "complete":
        _append(journal, {
            "schema": JOURNAL_SCHEMA, "event": "complete_sample_complete",
            "elapsed_ns": complete_ended - complete_started,
            "output_sha256": digests[0],
        })
    primary = (
        [complete_ended - complete_started]
        if endpoint == "complete" else samples
    )
    return {
        "schema": RESULT_SCHEMA,
        "status": "PASS",
        "unit_id": unit["unit_id"],
        "app": unit["app"],
        "operation": unit.get("operation"),
        "endpoint": endpoint,
        "input_identity": input_identity,
        "method": method,
        "primary_samples_ns": primary,
        "primary_median_ns": int(statistics.median(primary)),
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
        "journal_io_included_in_primary_timer": False,
        "retry_count": 0,
        "discard_count": 0,
    }


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--endpoint", choices=ENDPOINTS, required=True)
    parser.add_argument("--repetitions", type=int, required=True)
    parser.add_argument("--warmups", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--journal", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = _args()
    if args.output.exists() or args.journal.exists():
        raise FileExistsError("worker output and journal are create-only")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.journal.parent.mkdir(parents=True, exist_ok=True)
    args.journal.touch(exist_ok=False)
    _append(args.journal, {
        "schema": JOURNAL_SCHEMA, "event": "worker_started",
        "pid": os.getpid(), "arm": args.arm, "unit_id": args.unit,
        "endpoint": args.endpoint,
    })
    started = time.perf_counter_ns()
    exit_code = 0
    config: dict[str, Any] | None = None
    selected: dict[str, Any] | None = None
    base = None
    base_path = None
    affinity_preflight = None
    affinity_postflight = None
    try:
        loaded = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict) or loaded.get("schema") != CONFIG_SCHEMA:
            raise ValueError("worker formal config schema differs")
        config = loaded
        units = config.get("units")
        if not isinstance(units, Mapping) or not isinstance(units.get(args.unit), Mapping):
            raise KeyError(f"formal config lacks unit: {args.unit}")
        unit = units[args.unit]
        if unit.get("unit_id") != args.unit:
            raise ValueError("formal unit identity differs")
        selected = _selected_config(config, args.arm)
        affinity_preflight = _bind_cpu_affinity(selected, apply=True)
        if affinity_preflight is not None:
            _append(args.journal, {
                "schema": JOURNAL_SCHEMA,
                "event": "cpu_affinity_preflight",
                "observation": affinity_preflight,
            })
        roots = tuple(
            Path(row["source_root"]).resolve(strict=True)
            for row in config["implementations"].values()
        )
        selected_root = Path(selected["source_root"]).resolve(strict=True)
        _activate_root(selected_root, roots)
        base, base_path = _load_base_worker(selected_root)
        base_arm = "pyoptix" if args.arm == "pyoptix" else "v4"
        result = _run(
            base=base, unit=unit, base_arm=base_arm,
            selected_config=selected, endpoint=args.endpoint,
            repetitions=args.repetitions, warmups=args.warmups,
            journal=args.journal,
        )
        affinity_postflight = _bind_cpu_affinity(selected, apply=False)
        if affinity_postflight is not None:
            _append(args.journal, {
                "schema": JOURNAL_SCHEMA,
                "event": "cpu_affinity_postflight",
                "observation": affinity_postflight,
            })
    except BaseException as error:  # noqa: BLE001 - retain all adverse rows
        exit_code = 1
        _append(args.journal, {
            "schema": JOURNAL_SCHEMA, "event": "worker_failure",
            "error_type": type(error).__name__, "error": str(error),
            "traceback": traceback.format_exc(),
        })
        result = {
            "schema": RESULT_SCHEMA, "status": "FAIL",
            "unit_id": args.unit, "arm": args.arm,
            "endpoint": args.endpoint, "error_type": type(error).__name__,
            "error": str(error), "traceback": traceback.format_exc(),
            "retry_count": 0, "discard_count": 0,
        }

    runtime_identity: Mapping[str, Any] = {"status": "FAILED_TO_BIND"}
    machine: Mapping[str, Any] = {"status": "FAILED_TO_BIND"}
    implementation_identity: Mapping[str, Any] = {"status": "FAILED_TO_BIND"}
    if base is not None and selected is not None:
        try:
            runtime_identity = base._runtime_identity(
                "pyoptix" if args.arm == "pyoptix" else "v4")
            base._validate_runtime_identity(
                "pyoptix" if args.arm == "pyoptix" else "v4",
                runtime_identity, selected,
            )
            machine = base._machine()
            base._validate_machine_identity(machine, selected)
            if selected.get("cpu_affinity") is not None:
                if affinity_preflight is None or affinity_postflight is None:
                    raise RuntimeError("CPU-affinity evidence is incomplete")
                machine = {
                    **dict(machine),
                    "cpu_affinity": {
                        "preflight": affinity_preflight,
                        "postflight": affinity_postflight,
                    },
                }
            root = Path(selected["source_root"]).resolve(strict=True)
            commit = _git(root, "rev-parse", "HEAD")
            tree = _git(root, "rev-parse", "HEAD^{tree}")
            dirty = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
            if commit != selected["source_commit"] or tree != selected["source_tree"] or dirty:
                raise RuntimeError("implementation source identity differs")
            native = Path(selected["native_library_path"]).resolve(strict=True)
            if _sha256(native) != selected["native_library_sha256"]:
                raise RuntimeError("implementation native identity differs")
            implementation_identity = {
                "source_root": str(root), "source_commit": commit,
                "source_tree": tree, "source_status_clean": True,
                "native_library_path": str(native),
                "native_library_sha256": _sha256(native),
                "base_worker_sha256": _sha256(base_path),
            }
        except BaseException as error:  # noqa: BLE001
            exit_code = 1
            result.update({
                "status": "FAIL",
                "identity_error_type": type(error).__name__,
                "identity_error": str(error),
                "identity_traceback": traceback.format_exc(),
            })
    result.update({
        "arm": args.arm,
        "process_id": os.getpid(),
        "worker_wall_ns": time.perf_counter_ns() - started,
        "machine": machine,
        "runtime_identity": runtime_identity,
        "implementation_identity": implementation_identity,
        "formal_config_sha256": _sha256(args.config.resolve(strict=True)),
        "formal_worker_sha256": _sha256(Path(__file__).resolve()),
        "journal_sha256": _sha256(args.journal),
    })
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({
        "status": result["status"], "unit": args.unit,
        "arm": args.arm, "endpoint": args.endpoint,
        "output": str(args.output),
    }, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
