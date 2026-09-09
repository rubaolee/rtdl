"""Exclusive-output public-source control runner. CPU preflight is not GPU evidence."""
from __future__ import annotations
import argparse
from collections.abc import Mapping
import dataclasses
from enum import Enum
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import traceback

import numpy as np
import oracle
import program


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(value):
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_float": repr(value)}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return normalize(value.item())
    if dataclasses.is_dataclass(value):
        return {f.name: normalize(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, Mapping):
        return {str(k): normalize(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, frozenset, set)):
        return [normalize(v) for v in value]
    raise TypeError(f"cannot retain {type(value).__name__}")


def write(path, value):
    with Path(path).open("x", encoding="utf-8") as f:
        json.dump(normalize(value), f, sort_keys=True, indent=2, allow_nan=False)
        f.write("\n")


def textfile(path, value):
    with Path(path).open("x", encoding="utf-8") as f:
        f.write(value)


def source_inventory():
    import rtdsl
    package = Path(rtdsl.__file__).resolve().parent
    paths = list(Path(__file__).resolve().parent.glob("*.py"))
    paths += list(package.rglob("*.py"))
    return {str(p): digest(p) for p in sorted(paths)}


def save_array(path, value):
    with Path(path).open("xb") as f:
        np.save(f, value, allow_pickle=False)


def retain_compile(out, verified, compiled):
    write(out / "verified_callback.json", verified.callback)
    write(out / "program_identity.json", compiled.identity)
    write(out / "physical_plan.json", compiled.physical_plan)
    # Read-only inspection of generated artifacts; all execution uses public APIs.
    write(out / "derived_abi.json", compiled._abi)
    write(out / "declared_physical_bindings.json", compiled._declared_physical_bindings)
    textfile(out / "expected_wrapper.cu", compiled._expected_wrapper.source)


def execute_cell(out, cell, config, cpu_only):
    from rtdsl import v4
    out.mkdir(parents=False, exist_ok=False)
    before = source_inventory()
    write(out / "SOURCE_BEFORE.json", before)
    write(out / "STARTED.json", {"pid": os.getpid(), "cell": cell,
                                  "cpu_only": cpu_only, "python": sys.version,
                                  "platform": platform.platform(), "config": config})
    owner = None
    errors = []
    result = {}
    try:
        if cpu_only:
            native = out / "IDENTITY_ONLY_NOT_A_NATIVE_LIBRARY"
            native.write_bytes(b"CPU wrapper generation only; never load or materialize\n")
            sdk, cc = "9.0.0", (8, 9)
        else:
            native = Path(config["native"]).resolve(strict=True)
            if digest(native) != config["native_sha256"]:
                raise ValueError("native hash differs from registered configuration")
            sdk = config["optix_sdk"]
            cc = tuple(int(v) for v in config["compute_capability"].split("."))
            for path, expected_hash in config["header_sha256"].items():
                if digest(path) != expected_hash:
                    raise ValueError("registered actual header changed: " + path)
            if not config["header_sha256"]:
                raise ValueError("actual target header hashes required")
            if config.get("frozen_python_sources") != before:
                raise ValueError("GPU source set differs from preregistered exact Python sources")
        target = v4.V4Target.from_native(native, optix_sdk=sdk,
                                        compute_capability=cc)
        write(out / "TARGET.json", target)
        if cell == "stale_plan":
            p2 = v4.verify_builtin_triangle_callback_source(program.source(2), program.manifest())
            p3 = v4.verify_builtin_triangle_callback_source(program.source(3), program.manifest())
            plan = program.physical_plan(p2, "normal")
            textfile(out / "P2.py.txt", program.source(2))
            textfile(out / "P3.py.txt", program.source(3))
            if p2.callback.ir_sha256 == p3.callback.ir_sha256:
                raise AssertionError("source variants have identical IR")
            if p2.callback.effect_digest != p3.callback.effect_digest:
                raise AssertionError("source variants changed the effect class")
            try:
                p3.compile(physical_plan=plan, target=target)
            except v4.PhysicalSchemaError as error:
                if error.code != "callback_binding":
                    raise
                result = {"status": "EXPECTED_STALE_PLAN_REJECTION", "code": error.code,
                          "error": str(error), "p2_ir": p2.callback.ir_sha256,
                          "p3_ir": p3.callback.ir_sha256,
                          "same_effect_digest": p2.callback.effect_digest,
                          "materialize_called": False, "gpu_execute_called": False}
            else:
                raise AssertionError("stale plan accepted")
        else:
            power_text, binding = cell.split("-")
            power = int(power_text[1:])
            arrays, _ = oracle.input_arrays()
            write(out / "GEOMETRY_CHECK.json", oracle.independently_check_geometry())
            for name, array in arrays.items():
                save_array(out / (name + ".npy"), array)
            for reverse in (False, True):
                save_array(out / f"expected-{int(reverse)}.npy",
                           oracle.expected_rows(power, binding, reversed_order=reverse))
            source = program.source(power)
            textfile(out / "AUTHORED_SOURCE.py.txt", source)
            write(out / "MANIFEST.json", program.manifest())
            verified = v4.verify_builtin_triangle_callback_source(source, program.manifest())
            compiled = verified.compile(physical_plan=program.physical_plan(verified, binding),
                                        target=target)
            retain_compile(out, verified, compiled)
            if cpu_only:
                result = {"status": "CPU_ADMISSION_AND_WRAPPER_ONLY", "gpu_execute_called": False,
                          "source_sha256": verified.source_sha256,
                          "ir_sha256": verified.callback.ir_sha256,
                          "effect_digest": verified.callback.effect_digest,
                          "plan_sha256": compiled.physical_plan.plan_sha256,
                          "wrapper_sha256": compiled._expected_wrapper.source_sha256}
            else:
                toolchain = v4.V4Toolchain(
                    compute_capability=cc,
                    optix_include=Path(config["optix_include"]),
                    cuda_include=Path(config["cuda_include"]),
                    expected_python_version=config["python_version"],
                    expected_numba_version=config["numba_version"],
                    expected_numpy_version=config["numpy_version"])
                materialized = compiled.materialize(toolchain=toolchain)
                write(out / "materialized_identity.json", materialized.identity)
                write(out / "protocol_decision.json", materialized.protocol_contract_decision)
                write(out / "compiler_log_digest.json", materialized.compiler_log_sha256)
                executable = materialized._executable
                write(out / "generated_executable.json", executable)
                textfile(out / "composed.ptx", executable.composed.ptx)
                textfile(out / "wrapper.ptx", executable.wrapper_ptx)
                for leaf in executable.generated_leaves:
                    textfile(out / ("leaf-" + leaf.role.value + ".py"), leaf.generated_source)
                for leaf in executable.compiled_leaves:
                    textfile(out / ("leaf-" + leaf.role + ".ptx"), leaf.ptx)
                static = v4.BuiltinTriangleCallbackStaticInput(
                    vertices=arrays["vertices"], triangles=arrays["triangles"],
                    first_primitive_values=arrays["first_values"],
                    second_primitive_values=arrays["second_values"])
                owner = materialized.prepare(static)
                outputs = []
                for reverse in (False, True):
                    queries = np.ascontiguousarray(arrays["queries"][::-1] if reverse
                                                   else arrays["queries"])
                    batch = v4.BuiltinTriangleCallbackBatch(queries=queries)
                    observed = owner.execute(batch)
                    # Save before future calls/close even for an erroneous borrowed-view runtime.
                    actual = np.asarray(observed.output)
                    save_array(out / f"actual-{int(reverse)}.npy", actual)
                    write(out / f"receipt-{int(reverse)}.json", observed)
                    expected = oracle.expected_rows(power, binding, reversed_order=reverse)
                    matched = (actual.dtype == np.dtype("<u4") and actual.shape == (64, 3)
                               and np.array_equal(actual, expected))
                    write(out / f"comparison-{int(reverse)}.json", {"matched": bool(matched),
                          "actual_file_sha256": digest(out / f"actual-{int(reverse)}.npy"),
                          "expected_file_sha256": digest(out / f"expected-{int(reverse)}.npy")})
                    if not matched:
                        raise AssertionError("complete output differs from independent oracle")
                    outputs.append({"reverse": reverse, "rows": len(actual)})
                result = {"status": "GPU_PUBLIC_SOURCE_CELL_MATCHED", "outputs": outputs,
                          "materialized_identity": materialized.identity,
                          "performance_result": False}
    except BaseException as error:
        errors.append({"phase": "work", "type": type(error).__name__, "text": str(error),
                       "traceback": traceback.format_exc()})
    finally:
        if owner is not None:
            try:
                owner.close()
            except BaseException as error:
                errors.append({"phase": "close", "type": type(error).__name__,
                               "text": str(error), "traceback": traceback.format_exc()})
        try:
            after = source_inventory()
            write(out / "SOURCE_AFTER.json", after)
            if before != after:
                errors.append({"phase": "identity", "text": "source changed during cell"})
        except BaseException as error:
            errors.append({"phase": "source_identity_after", "type": type(error).__name__,
                           "text": str(error), "traceback": traceback.format_exc()})
        if not cpu_only and "native_sha256" in config:
            try:
                if digest(config["native"]) != config["native_sha256"]:
                    errors.append({"phase": "identity", "text": "native changed during cell"})
            except BaseException as error:
                errors.append({"phase": "native_identity_after", "type": type(error).__name__,
                               "text": str(error), "traceback": traceback.format_exc()})
        write(out / "RESULT.json", {"cell": cell, "result": result, "errors": errors,
                                     "passed_at_declared_scope": not errors,
                                     "gpu_evidence": not cpu_only and not errors and cell != "stale_plan"})
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("cpu-preflight", "gpu"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--cell", choices=("stale_plan", "P2-normal", "P2-swapped", "P3-normal", "P3-swapped"))
    args = parser.parse_args()
    if args.mode == "gpu" and args.config is None:
        parser.error("actual registered --config is required for GPU mode")
    config = {} if args.config is None else json.loads(args.config.read_text())
    if args.cell:
        return execute_cell(args.out.resolve(), args.cell, config, args.mode == "cpu-preflight")
    args.out.mkdir(parents=True, exist_ok=False)
    parent_sources = source_inventory()
    write(args.out / "REQUEST.json", {"argv": sys.argv, "config": config,
          "config_sha256": None if args.config is None else digest(args.config),
          "source": parent_sources, "mode": args.mode, "performance_result": False})
    cells = ["stale_plan", "P2-normal", "P2-swapped", "P3-normal", "P3-swapped"]
    attempted = []
    for cell in cells:
        command = [sys.executable, str(Path(__file__).resolve()), "--mode", args.mode,
                   "--cell", cell, "--out", str((args.out / cell).resolve())]
        if args.config is not None:
            command.extend(("--config", str(args.config.resolve())))
        with (args.out / (cell + ".stdout.log")).open("xb") as stdout, \
             (args.out / (cell + ".stderr.log")).open("xb") as stderr:
            process = subprocess.run(command, stdout=stdout, stderr=stderr, check=False)
        attempted.append({"cell": cell, "returncode": process.returncode})
        write(args.out / (cell + ".exit.json"), attempted[-1])
        if process.returncode:
            break
    all_pass = len(attempted) == len(cells) and all(v["returncode"] == 0 for v in attempted)
    consistency_errors = []
    for attempt in attempted:
        cell_dir = args.out / attempt["cell"]
        for snapshot in ("SOURCE_BEFORE.json", "SOURCE_AFTER.json"):
            if not (cell_dir / snapshot).is_file():
                consistency_errors.append(attempt["cell"] + ":missing:" + snapshot)
            elif json.loads((cell_dir / snapshot).read_text()) != parent_sources:
                consistency_errors.append(attempt["cell"] + ":changed:" + snapshot)
        if (cell_dir / "STARTED.json").is_file():
            if json.loads((cell_dir / "STARTED.json").read_text())["config"] != config:
                consistency_errors.append(attempt["cell"] + ":config changed")
    if source_inventory() != parent_sources:
        consistency_errors.append("parent sources changed")
    all_pass = all_pass and not consistency_errors
    write(args.out / "MATRIX.json", {"mode": args.mode, "attempted": attempted,
          "not_attempted": cells[len(attempted):], "passed_at_declared_scope": all_pass,
          "consistency_errors": consistency_errors,
          "gpu_matrix_passed": args.mode == "gpu" and all_pass,
          "performance_result": False})
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
