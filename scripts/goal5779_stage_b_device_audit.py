#!/usr/bin/env python3
"""Execute the frozen Goal5779 same-plan callback code-quality audit.

The experiment substitutes exactly one generated callback leaf with an
independently hand-authored direct-OptiX control.  Wrapper, all other leaves,
GAS, ray layout, native provider, fixtures and output contract are identical.
It is a code-generation isolation experiment, not an application-endpoint
V2/V4 result and not a claim that the control is copied prior V2 source bytes.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import subprocess
import tempfile

import numpy as np

from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4_bounded_relation_optix_runtime import _Status as BoxStatus
from rtdsl.v4_bounded_relation_prepared_runtime import _configure as box_configure
from rtdsl.v4_multiround_spatial_optix_runtime import (
    _Status as SpatialStatus,
    _configure as spatial_configure,
)
from rtdsl.v4_triangle_reduction_optix_runtime import _Status as TriangleStatus
from rtdsl.v4_triangle_reduction_prepared_runtime import _configure as triangle_configure
from scripts import goal5779_stage_a_freeze as stage_a
from scripts.goal5779_handwritten_leaf_controls import compile_handwritten_control


SCHEMA = "rtdl.goal5779.generated_vs_handwritten.device_audit.v1"
CAPACITY = 1 << 20


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _digest(value: object) -> str:
    return _sha_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))


def _ptr(array: np.ndarray, ctype):
    return np.ascontiguousarray(array).ctypes.data_as(ctypes.POINTER(ctype))


def _raise(status: int, error, label: str) -> None:
    if status:
        raise RuntimeError(
            error.value.decode("utf-8", errors="replace")
            or f"{label} failed with status {status}")


def _status_rows(storage) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(getattr(row, name)) for name, _ in row._fields_)
                 for row in storage)


def _reset(storage) -> None:
    ctypes.memset(ctypes.addressof(storage), 0, ctypes.sizeof(storage))


def _cuda_event_seconds(call) -> float:
    # Import and initialize CuPy only after Stage-A compiler identity has been
    # rebuilt.  Initializing a CUDA context before Numba leaf compilation can
    # perturb target selection in this toolchain.
    import cupy as cp
    start = cp.cuda.Event()
    stop = cp.cuda.Event()
    start.record()
    call()
    stop.record()
    stop.synchronize()
    value = float(cp.cuda.get_elapsed_time(start, stop)) / 1000.0
    if not np.isfinite(value) or value <= 0.0:
        raise RuntimeError(f"invalid CUDA event duration {value!r}")
    return value


class _Variant:
    def __init__(self, *, family: str, label: str, token: int, execute, destroy,
                 invoke, output, validate, library, program_bundle: str):
        self.family = family
        self.label = label
        self.token = token
        self.execute = execute
        self.destroy = destroy
        self.invoke = invoke
        self.output = output
        self.validate = validate
        self.library = library
        self.program_bundle = program_bundle

    def functional(self) -> dict[str, object]:
        audit = OptixTraversalAuditSession.open(library=self.library)
        try:
            self.invoke()
            details = self.validate()
            output_sha = _digest(self.output())
            receipt = audit.finish(
                semantic_digest=_digest({
                    "goal": 5779, "family": self.family,
                    "variant": self.label,
                }),
                output_digest=output_sha,
                route_identity=f"goal5779:{self.family}:{self.label}",
                expected_program_bundles=(self.program_bundle,),
            )
        except Exception:
            audit.abort()
            raise
        if receipt["physical_executor_classification"] != "optix_traversal_observed":
            raise RuntimeError(f"{self.family}/{self.label} lacked bound traversal")
        return {"output_sha256": output_sha, "validation": details,
                "traversal_receipt": receipt}

    def timed(self) -> float:
        return _cuda_event_seconds(self.invoke)

    def close(self) -> None:
        error = ctypes.create_string_buffer(16384)
        _raise(int(self.destroy(self.token, error, len(error))), error,
               f"{self.family}/{self.label} destroy")


def _prepare_triangle(library, ptx: str, arrays, label: str) -> _Variant:
    prepare, execute, destroy = triangle_configure(library)
    vertices = np.ascontiguousarray(arrays["vertices"], dtype=np.float32)
    triangles = np.ascontiguousarray(arrays["triangles"], dtype=np.uint32)
    origins = np.ascontiguousarray(arrays["origins"], dtype=np.float32)
    directions = np.ascontiguousarray(arrays["directions"], dtype=np.float32)
    tmax = np.ascontiguousarray(arrays["tmax"], dtype=np.float32)
    token = ctypes.c_uint64(); error = ctypes.create_string_buffer(16384)
    null_u64 = ctypes.POINTER(ctypes.c_uint64)()
    null_i64 = ctypes.POINTER(ctypes.c_int64)()
    null_u32 = ctypes.POINTER(ctypes.c_uint32)()
    _raise(int(prepare(
        ptx.encode(), _ptr(vertices, ctypes.c_float), len(vertices),
        _ptr(triangles, ctypes.c_uint32), len(triangles),
        null_u64, null_i64, null_u32, 1,
        ctypes.byref(token), error, len(error))), error, "triangle prepare")
    if not token.value:
        raise RuntimeError("triangle prepare returned zero token")
    count = len(origins)
    per_ray = (ctypes.c_uint64 * count)()
    event_count = ctypes.c_uint64()
    event_query = (ctypes.c_uint32 * 1)()
    event_primitive = (ctypes.c_uint32 * 1)()
    event_stable = (ctypes.c_uint64 * 1)()
    event_signed = (ctypes.c_int64 * 1)()
    event_include = (ctypes.c_uint32 * 1)()
    statuses = (TriangleStatus * count)()
    counters = (ctypes.c_uint64 * 7)()

    def invoke():
        event_count.value = 0; _reset(per_ray); _reset(statuses); _reset(counters)
        error.value = b""
        _raise(int(execute(
            token.value, _ptr(origins, ctypes.c_float),
            _ptr(directions, ctypes.c_float), _ptr(tmax, ctypes.c_float), count,
            per_ray, ctypes.byref(event_count), event_query, event_primitive,
            event_stable, event_signed, event_include, statuses, counters,
            error, len(error))), error, "triangle execute")

    def output():
        return tuple(int(item) for item in per_ray)

    def validate():
        status = _status_rows(statuses)
        counts = tuple(int(item) for item in counters)
        if any(row[0] or row[1] for row in status):
            raise RuntimeError("triangle callback status failed")
        if counts[1] != count or counts[5] != count or counts[6] != count \
                or counts[3] <= 0 or event_count.value != 0:
            raise RuntimeError(f"triangle lifecycle drift: {counts!r}")
        return {"role_counters": counts, "event_count": int(event_count.value),
                "launch_status_sha256": _digest(status)}

    return _Variant(
        family=stage_a.ROW_ORDER[0], label=label, token=int(token.value),
        execute=execute, destroy=destroy, invoke=invoke, output=output,
        validate=validate, library=library,
        program_bundle="v4_builtin_triangle_checked_reduction_composed")


def _prepare_box(library, ptx: str, arrays, label: str) -> _Variant:
    prepare, execute, destroy = box_configure(library)
    indexed = np.ascontiguousarray(arrays["indexed"], dtype=np.float32)
    source = np.ascontiguousarray(arrays["source"], dtype=np.float32)
    ids = np.ascontiguousarray(arrays["ids"], dtype=np.uint32)
    token = ctypes.c_uint64(); error = ctypes.create_string_buffer(16384)
    _raise(int(prepare(
        ptx.encode(), _ptr(indexed, ctypes.c_float), _ptr(ids, ctypes.c_uint32),
        len(indexed), ctypes.c_float(0.0), CAPACITY,
        ctypes.byref(token), error, len(error))), error, "box prepare")
    if not token.value:
        raise RuntimeError("box prepare returned zero token")
    raw_count = ctypes.c_uint64(); overflow = ctypes.c_uint32()
    rows = (ctypes.c_uint32 * (CAPACITY * 2))()
    statuses = (BoxStatus * (len(source) + len(indexed)))()
    counters = (ctypes.c_uint64 * 7)()

    def invoke():
        raw_count.value = 0; overflow.value = 0; _reset(statuses); _reset(counters)
        error.value = b""
        _raise(int(execute(
            token.value, _ptr(source, ctypes.c_float), _ptr(ids, ctypes.c_uint32),
            len(source), ctypes.byref(raw_count), ctypes.byref(overflow), rows,
            statuses, counters, error, len(error))), error, "box execute")

    def output():
        stored = min(int(raw_count.value), CAPACITY)
        # Frozen relation semantics use KEYED_IDENTICAL_DEDUP.  The native
        # callback may emit the same accepted pair from multiple exact ray
        # constructions; compare the canonical semantic set, not raw events.
        return tuple(sorted({(int(rows[i * 2]), int(rows[i * 2 + 1]))
                             for i in range(stored)}))

    def validate():
        status = _status_rows(statuses)
        counts = tuple(int(item) for item in counters)
        launches = len(source) + len(indexed)
        if overflow.value or any(row[0] or row[1] for row in status):
            raise RuntimeError("box callback status/overflow failed")
        if counts[1] != launches or counts[6] != launches \
                or counts[4] + counts[5] != launches:
            raise RuntimeError(f"box lifecycle drift: {counts!r}")
        expected = tuple((int(i), int(i)) for i in ids)
        if output() != expected:
            raise RuntimeError("box independent exact-row oracle mismatch")
        return {"role_counters": counts, "raw_count": int(raw_count.value),
                "launch_status_sha256": _digest(status),
                "independent_oracle_exact": True}

    return _Variant(
        family=stage_a.ROW_ORDER[1], label=label, token=int(token.value),
        execute=execute, destroy=destroy, invoke=invoke, output=output,
        validate=validate, library=library,
        program_bundle="v4_custom_aabb_bounded_relation_composed")


def _prepare_spatial(library, ptx: str, arrays, label: str) -> _Variant:
    prepare, execute, destroy = spatial_configure(library)
    points = np.ascontiguousarray(arrays["points"], dtype=np.float32)
    queries = np.ascontiguousarray(arrays["queries"], dtype=np.float32)
    ids = np.arange(len(points), dtype=np.uint32)
    query_ids = np.ascontiguousarray(arrays["query_ids"], dtype=np.uint32)
    radius = float(arrays["physical_radius_f32"])
    token = ctypes.c_uint64(); error = ctypes.create_string_buffer(16384)
    _raise(int(prepare(
        ptx.encode(), _ptr(points, ctypes.c_float), _ptr(ids, ctypes.c_uint32),
        len(points), ctypes.c_float(float(arrays["initial_radius_f32"])),
        ctypes.byref(token), error, len(error))), error, "spatial prepare")
    if not token.value:
        raise RuntimeError("spatial prepare returned zero token")
    raw_count = ctypes.c_uint64(); overflow = ctypes.c_uint32()
    rows = (ctypes.c_uint32 * (CAPACITY * 2))()
    statuses = (SpatialStatus * len(queries))()
    counters = (ctypes.c_uint64 * 7)()
    telemetry = (ctypes.c_uint64 * 8)()

    def invoke():
        raw_count.value = 0; overflow.value = 0
        _reset(statuses); _reset(counters); _reset(telemetry); error.value = b""
        _raise(int(execute(
            token.value, _ptr(queries, ctypes.c_float),
            _ptr(query_ids, ctypes.c_uint32), len(queries),
            ctypes.c_float(radius), CAPACITY, ctypes.byref(raw_count),
            ctypes.byref(overflow), rows, statuses, counters, telemetry,
            error, len(error))), error, "spatial execute")

    def output():
        stored = min(int(raw_count.value), CAPACITY)
        return tuple(sorted({(int(rows[i * 2]), int(rows[i * 2 + 1]))
                             for i in range(stored)}))

    def validate():
        status = _status_rows(statuses)
        counts = tuple(int(item) for item in counters)
        if overflow.value or any(row[0] or row[1] for row in status):
            raise RuntimeError("spatial callback status/overflow failed")
        if counts[1] != len(queries) or counts[6] != len(queries) \
                or counts[4] + counts[5] != len(queries):
            raise RuntimeError(f"spatial lifecycle drift: {counts!r}")
        observed = set(output())
        expected_self = {(int(i), int(i)) for i in query_ids}
        if not expected_self.issubset(observed):
            raise RuntimeError("spatial exact-self subset oracle mismatch")
        return {"role_counters": counts, "raw_count": int(raw_count.value),
                "launch_status_sha256": _digest(status),
                "independent_self_subset_exact": True,
                "telemetry": tuple(int(item) for item in telemetry)}

    return _Variant(
        family=stage_a.ROW_ORDER[2], label=label, token=int(token.value),
        execute=execute, destroy=destroy, invoke=invoke, output=output,
        validate=validate, library=library,
        program_bundle="v4_custom_aabb_prepared_multiround_spatial_composed")


def _ptx_shape(ptx: str) -> dict[str, object]:
    lines = [line.strip() for line in ptx.splitlines()]
    opcodes = []
    for line in lines:
        if not line or line.startswith((".", "//", "{" , "}")):
            continue
        match = re.match(r"(?:@[!%A-Za-z0-9_]+\s+)?([A-Za-z][A-Za-z0-9_.]+)", line)
        if match:
            opcodes.append(match.group(1))
    return {
        "bytes": len(ptx.encode()), "line_count": len(lines),
        "instruction_like_count": len(opcodes),
        "opcode_histogram": {name: opcodes.count(name) for name in sorted(set(opcodes))},
    }


def _toolchain_diagnostic(ptx: str, *, arch: str, label: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="goal5779_ptxas_") as tmp:
        root = Path(tmp); source = root / f"{label}.ptx"; cubin = root / f"{label}.cubin"
        source.write_text(ptx, encoding="utf-8")
        command = ["ptxas", str(source), "-arch", arch, "-v", "-o", str(cubin)]
        try:
            completed = subprocess.run(command, text=True, capture_output=True, timeout=120)
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return {"available": False, "reason": type(exc).__name__}
        result = {
            "available": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        if completed.returncode == 0 and cubin.is_file():
            data = cubin.read_bytes()
            result.update({"module_bytes": len(data), "module_sha256": _sha_bytes(data)})
            try:
                usage = subprocess.run(
                    ["cuobjdump", "--dump-resource-usage", str(cubin)],
                    text=True, capture_output=True, timeout=60)
                sass = subprocess.run(
                    ["cuobjdump", "--dump-sass", str(cubin)],
                    text=True, capture_output=True, timeout=60)
                result.update({
                    "resource_usage": usage.stdout + usage.stderr,
                    "sass_line_count": len(sass.stdout.splitlines()),
                    "sass_sha256": _sha_bytes(sass.stdout.encode()),
                })
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                result["cuobjdump_unavailable"] = type(exc).__name__
        return result


def _bootstrap(values: list[float], seed: int) -> tuple[float, list[float]]:
    rng = random.Random(seed)
    draws = sorted(statistics.median(rng.choices(values, k=len(values)))
                   for _ in range(10000))
    return statistics.median(values), [draws[249], draws[9749]]


def _build_variants(args, expected: dict[str, object], library):
    target = stage_a.ReferenceTargetProfile(
        provider="optix", optix_sdk=args.optix_sdk,
        compute_capability=f"{args.compute_capability[0]}.{args.compute_capability[1]}",
        native_sha256=_sha_path(Path(args.native)),
        supports_custom_aabb=True, supports_builtin_triangle=True)
    result = []
    for row, builder in zip(expected["rows"],
                            (stage_a._triangle, stage_a._box, stage_a._spatial)):
        callback, abi, executable, role, control = builder(target, args)
        handwritten, _ = compile_handwritten_control(
            control, role, compiler_options=executable.compiler_options,
            compute_capability=args.compute_capability,
            callback_ir_sha256=callback.ir_sha256)
        composed, leaves = stage_a._replace_leaf(executable, role, handwritten)
        check = {
            "wrapper_ptx_sha256": executable.wrapper_ptx_sha256,
            "generated_composed_ptx_sha256": executable.composed.ptx_sha256,
            "handwritten_composed_ptx_sha256": composed.ptx_sha256,
            "handwritten_source_sha256": control.source_sha256,
            "handwritten_ptx_sha256": handwritten.ptx_sha256,
        }
        if any(row[key] != value for key, value in check.items()):
            raise RuntimeError(f"Stage-A PTX identity drift: {row['family_id']}")
        non_replaced = [x.ptx_sha256 for x in executable.compiled_leaves
                        if x.role != role.role.value]
        if non_replaced != row["unchanged_generated_leaf_ptx_sha256"]:
            raise RuntimeError(f"Stage-A non-replaced leaf drift: {row['family_id']}")
        generated_role = next(x for x in executable.compiled_leaves
                              if x.role == role.role.value)
        result.append((row, executable.composed.ptx, composed.ptx,
                       generated_role.ptx, handwritten.ptx))
    return result


def run(args) -> dict[str, object]:
    stage_a_path = Path(args.stage_a).resolve()
    if _sha_path(stage_a_path) != args.stage_a_sha256:
        raise RuntimeError("supplied Stage-A SHA-256 mismatch")
    expected = json.loads(stage_a_path.read_text(encoding="utf-8"))
    if not all(expected["stage_b_gate"].values()):
        raise RuntimeError("Stage-A gate is not fully true")
    if _sha_path(Path(args.native).resolve()) != expected["target"]["native_sha256"]:
        raise RuntimeError("Stage-A native identity drift")
    identity = expected["implementation_identity"]
    pins = [identity["stage_a_script"], identity["handwritten_control_script"]]
    pins.extend(identity["product_sources"])
    for pin in pins:
        path = stage_a.ROOT / pin["path"]
        if not path.is_file() or _sha_path(path) != pin["sha256"]:
            raise RuntimeError(f"Stage-A pinned source drift: {pin['path']}")
    native_path = Path(args.native).resolve()
    library = ctypes.CDLL(str(native_path))
    # Preserve the exact loaded-provider path required by the behavioral
    # traversal receipt front door; a raw ctypes.CDLL does not set it.
    library._rtdl_library_path = str(native_path)
    pairs = _build_variants(args, expected, library)
    fixtures = stage_a.fixture_arrays()
    preparers = (_prepare_triangle, _prepare_box, _prepare_spatial)
    prepared_rows = []
    try:
        for row_index, ((frozen, generated_ptx, handwritten_ptx,
                         generated_leaf_ptx, handwritten_leaf_ptx), prepare) in enumerate(
                             zip(pairs, preparers)):
            family = frozen["family_id"]
            generated = prepare(
                library, generated_ptx, fixtures[family], "generated_v4")
            handwritten = prepare(
                library, handwritten_ptx, fixtures[family],
                "handwritten_direct_optix_control")
            prepared_rows.append((row_index, frozen, generated_leaf_ptx,
                                  handwritten_leaf_ptx, generated, handwritten))
    except Exception:
        for _row_index, _frozen, _generated_leaf, _handwritten_leaf, \
                generated, handwritten in reversed(prepared_rows):
            handwritten.close(); generated.close()
        raise
    rows = []
    try:
        # All three semantic families must pass functional/output/behavioral
        # validation before the first device timing is observed.
        functional_rows = []
        for row_index, frozen, _generated_leaf, _handwritten_leaf, \
                generated, handwritten in prepared_rows:
            family = frozen["family_id"]
            functional = {
                "generated_v4": generated.functional(),
                "handwritten_direct_optix_control": handwritten.functional(),
            }
            if functional["generated_v4"]["output_sha256"] != \
                    functional["handwritten_direct_optix_control"]["output_sha256"]:
                raise RuntimeError(f"functional output mismatch: {family}")
            functional_rows.append(functional)
        for (row_index, frozen, generated_leaf_ptx, handwritten_leaf_ptx,
             generated, handwritten), functional in zip(
                 prepared_rows, functional_rows):
            family = frozen["family_id"]
            for _ in range(expected["schedule"]["warmup_launches_per_variant"]):
                handwritten.invoke(); handwritten.validate()
                generated.invoke(); generated.validate()
            observations = []
            pair_count = expected["schedule"]["pair_count_per_row"]
            for pair_index in range(pair_count):
                order = ((handwritten, generated) if pair_index % 2 == 0
                         else (generated, handwritten))
                times = {}
                for variant in order:
                    times[variant.label] = variant.timed()
                    variant.validate()
                ratio = (times["handwritten_direct_optix_control"] /
                         times["generated_v4"])
                observations.append({
                    "pair_index": pair_index,
                    "order": [variant.label for variant in order],
                    "handwritten_control_seconds":
                        times["handwritten_direct_optix_control"],
                    "generated_v4_seconds": times["generated_v4"],
                    "handwritten_over_generated_ratio": ratio,
                })
            values = [x["handwritten_over_generated_ratio"] for x in observations]
            median, ci = _bootstrap(values, 57_790_000 + row_index)
            rows.append({
                "row_index": row_index, "family_id": family,
                "functional": functional,
                "observations": observations,
                "paired_ratio_median": median, "bootstrap_ci95": ci,
                "competitive": ci[0] >= 0.95,
                "generated_leaf_diagnostic": {
                    "ptx": _ptx_shape(generated_leaf_ptx),
                    "toolchain": _toolchain_diagnostic(
                        generated_leaf_ptx, arch=f"sm_{args.compute_capability[0]}{args.compute_capability[1]}",
                        label=f"row{row_index}_generated"),
                },
                "handwritten_leaf_diagnostic": {
                    "ptx": _ptx_shape(handwritten_leaf_ptx),
                    "toolchain": _toolchain_diagnostic(
                        handwritten_leaf_ptx, arch=f"sm_{args.compute_capability[0]}{args.compute_capability[1]}",
                        label=f"row{row_index}_handwritten"),
                },
            })
    finally:
        for _row_index, _frozen, _generated_leaf, _handwritten_leaf, \
                generated, handwritten in reversed(prepared_rows):
            handwritten.close(); generated.close()
    return {
        "schema": SCHEMA, "goal": 5779,
        "status": "COMPLETE__OBSERVATION_ONLY",
        "stage_a": {"path": str(stage_a_path), "sha256": args.stage_a_sha256},
        "target": expected["target"],
        "comparison_scope": {
            "class": "same_plan_one_leaf_codegen_isolation",
            "control": "independently_hand_authored_direct_optix_not_prior_v2_bytes",
            "same_wrapper_gas_ray_layout_nonreplaced_leaves_output_contract": True,
            "application_endpoint_v2_v4_result": False,
            "stage_a_rebuild_policy": (
                "single compilation; require exact wrapper/leaf/composed PTX and "
                "all pinned product-source/native identities"),
            "wrapper_source_digest_used_as_execution_identity": False,
        },
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "competitive_count": sum(row["competitive"] for row in rows),
            "failed_count": sum(not row["competitive"] for row in rows),
            "broad_controlled_audit_competitiveness": all(
                row["competitive"] for row in rows),
        },
        "claim_boundary": {
            "product_source_changed": False, "pod_used": False,
            "application_v2_v4_performance_claimed": False,
            "universal_codegen_competitiveness_claimed": False,
            "diagnostics_override_timing_failure": False,
        },
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage-a", required=True)
    parser.add_argument("--stage-a-sha256", required=True)
    parser.add_argument("--native", required=True)
    parser.add_argument("--optix-include", required=True)
    parser.add_argument("--cuda-include", required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", default="6,1")
    parser.add_argument("--python-version", default="3.12.3")
    parser.add_argument("--numba-version", default="0.65.1")
    parser.add_argument("--numpy-version", default="2.4.4")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    args.compute_capability = tuple(map(int, args.compute_capability.split(",")))
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    payload = run(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=False)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    output.write_bytes(data.encode("utf-8"))
    print(json.dumps({
        "status": payload["status"], "output": str(output.resolve()),
        "sha256": _sha_bytes(data.encode()), "summary": payload["summary"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
