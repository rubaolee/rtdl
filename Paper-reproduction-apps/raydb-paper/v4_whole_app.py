"""Application-owned RTDL V4 front door for the bounded RayDB Q2.1 lane.

The front door starts from the frozen relational rows and predicate.  RayDB
owns their conversion into query-keyed physical events; V4 verifies and
compiles the closed keyed-I64 triangle callback/reducer contract.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from rtdsl.optix_runtime import _load_optix_library
from rtdsl.v4_partitioned_grouped_i64_lowering import (
    execute_verified_partitioned_grouped_i64_v4,
)

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_triangle_reduction_optix_runtime import (
    run_builtin_triangle_reduction_callback,
)
from rtdsl.v4_triangle_reduction_prepared_runtime import (
    prepare_triangle_reduction_callback,
)
from rtdsl.v4_triangle_standard_library import (
    compile_keyed_callback,
    compile_standard_triangle_program,
    keyed_i64_sum_schema,
)


APP_DIR = Path(__file__).resolve().parent
MIGRATION = APP_DIR / "rtdl3_action_migration.py"


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_app_adapter():
    name = "rtdl_v4_raydb_app_adapter"
    if name in sys.modules:
        return sys.modules[name]
    sys.path.insert(0, str(APP_DIR))
    try:
        spec = importlib.util.spec_from_file_location(name, MIGRATION)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load frozen RayDB adapter")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(APP_DIR))


@dataclass(frozen=True)
class V4RayDBInput:
    vertices: tuple[tuple[float, float, float], ...]
    triangles: tuple[tuple[int, int, int], ...]
    queries: tuple[
        tuple[tuple[float, float, float], tuple[float, float, float], float], ...
    ]
    metadata: dict[str, tuple[int, ...]]
    group_values: tuple[tuple[int, ...], ...]
    expected_keyed_rows: tuple[tuple[tuple[int, ...], int], ...]
    expected_paper_rows: tuple[dict[str, object], ...]
    input_sha256: str


def _geometry(events: tuple[dict[str, object], ...]):
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    stable_ids: list[int] = []
    signed_values: list[int] = []
    include_flags: list[int] = []
    query_count = 1 + max(int(row["query_id"]) for row in events)
    for index, row in enumerate(events):
        x = float(int(row["query_id"]) * 4)
        z = 1.0 + 0.125 * index
        base = len(vertices)
        vertices.extend(((x - 0.75, -0.75, z),
                         (x + 0.75, -0.75, z),
                         (x, 0.75, z)))
        triangles.append((base, base + 1, base + 2))
        stable_ids.append(int(row["primitive_stable_id"]))
        signed_values.append(int(row["value"]))
        include_flags.append(int(bool(row["include"])))
    queries = tuple(
        ((float(index * 4), 0.0, 0.0), (0.0, 0.0, 1.0), 100.0)
        for index in range(query_count)
    )
    return (
        tuple(vertices), tuple(triangles), queries,
        {
            "primitive.stable_id": tuple(stable_ids),
            "primitive.signed_value": tuple(signed_values),
            "primitive.include": tuple(include_flags),
        },
    )


def build_v4_input() -> V4RayDBInput:
    app = _load_app_adapter()
    rows = tuple(app.bounded_q21_rows())
    predicate = app.bounded_q21_predicate()
    events = tuple(app.events_from_rows(rows, predicate))
    group_values = tuple(sorted({tuple(row.group_values) for row in rows}))
    vertices, triangles, queries, metadata = _geometry(events)
    reference = app.run_reference_rows(rows, predicate)
    if not reference["matched"]:
        raise RuntimeError("RayDB route-independent reference mismatch")
    expected_paper_rows = tuple(reference["expected_rows"])
    group_ids = {group: index for index, group in enumerate(group_values)}
    expected_keyed_rows = tuple(
        ((group_ids[tuple(row["group"])],), int(row["value"]))
        for row in expected_paper_rows
    )
    semantic = {
        "rows": [
            {
                "group_values": tuple(int(v) for v in row.group_values),
                "scan_values": tuple(int(v) for v in row.scan_values),
                "aggregate_value": int(row.aggregate_value),
            }
            for row in rows
        ],
        "events": events,
        "vertices": vertices,
        "triangles": triangles,
        "queries": queries,
        "metadata": metadata,
        "expected_paper_rows": expected_paper_rows,
    }
    return V4RayDBInput(
        vertices, triangles, queries, metadata, group_values,
        expected_keyed_rows, expected_paper_rows, _digest(semantic),
    )


def _proof(callback) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "raydb_keyed_dedup_order_independence_v1",
            "callback": callback.ir_sha256,
            "app_source": _sha(Path(__file__)),
            "migration_source": _sha(MIGRATION),
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _paper_rows(keyed_rows, group_values):
    rows = tuple(
        {
            "group": list(group_values[int(key[0])]),
            "value": int(value),
        }
        for key, value in keyed_rows
        if int(value) != 0
    )
    return tuple(sorted(rows, key=lambda row: tuple(row["group"])))


@dataclass
class PreparedRayDbV4:
    owner: object
    prepared_input: V4RayDBInput
    total_prepare_seconds: float

    def execute(self, *, queries=None):
        query_values = (
            self.prepared_input.queries if queries is None else tuple(queries))
        started = time.perf_counter()
        executed = self.owner.execute(query_values, query_metadata={})
        paper_rows = _paper_rows(
            executed.reduced_output, self.prepared_input.group_values)
        elapsed = time.perf_counter() - started
        return {
            "schema": "rtdl.paper_reproduction.raydb.v4.prepared.v1",
            "output": {"grouped_rows": paper_rows},
            "expected": {"grouped_rows":
                         self.prepared_input.expected_paper_rows},
            "matched": paper_rows == self.prepared_input.expected_paper_rows,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "lifecycle_receipt": self.owner.lifecycle_receipt,
            "traversal_receipt": executed.traversal_receipt,
            "native_library_sha256": executed.native_library_sha256,
        }

    def close(self):
        self.owner.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()


def prepare_v4(
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path,
) -> PreparedRayDbV4:
    started = time.perf_counter()
    prepared_input = build_v4_input()
    callback = compile_keyed_callback()
    schema = keyed_i64_sum_schema(callback)
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, target, proof,
        compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    owner = prepare_triangle_reduction_callback(
        authority=program.authority, contract=program.contract,
        abi=program.abi, any_hit_proof_authority=program.proof,
        executable=program.executable, vertices=prepared_input.vertices,
        triangles=prepared_input.triangles, metadata=prepared_input.metadata,
        event_capacity=64, native_library_path=native_library_path)
    return PreparedRayDbV4(
        owner, prepared_input, time.perf_counter() - started)


def run_v4_complete(
    *,
    target,
    compute_capability: tuple[int, int],
    optix_include,
    cuda_include,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    native_library_path,
) -> dict[str, object]:
    started = time.perf_counter()
    prepared_input = build_v4_input()
    callback = compile_keyed_callback()
    schema = keyed_i64_sum_schema(callback)
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, target, proof,
        compute_capability=compute_capability,
        optix_include=optix_include,
        cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version,
    )
    executed = run_builtin_triangle_reduction_callback(
        program.authority,
        program.contract,
        program.abi,
        program.executable,
        any_hit_proof_authority=program.proof,
        vertices=prepared_input.vertices,
        triangles=prepared_input.triangles,
        queries=prepared_input.queries,
        metadata=prepared_input.metadata,
        event_capacity=64,
        expected_reduced_output=prepared_input.expected_keyed_rows,
        native_library_path=native_library_path,
    )
    paper_rows = _paper_rows(executed.reduced_output, prepared_input.group_values)
    complete_seconds = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.raydb.v4.v1",
        "workload": "bounded_q21_grouped_signed_i64_sum",
        "input_sha256": prepared_input.input_sha256,
        "output": {"grouped_rows": paper_rows},
        "expected": {"grouped_rows": prepared_input.expected_paper_rows},
        "matched": paper_rows == prepared_input.expected_paper_rows,
        "registered_complete_seconds": complete_seconds,
        "complete_timer_includes": (
            "relational_input_and_predicate_load",
            "app_owned_row_to_ray_triangle_lowering",
            "restricted_callback_parse_verify",
            "abi_and_wrapper_compile",
            "gas_pipeline_sbt_prepare",
            "optix_execute",
            "checked_dedup_grouped_reduction_and_host_materialization",
        ),
        "traversal_receipt": executed.traversal_receipt,
        "native_library_sha256": executed.native_library_sha256,
        "default_selected_between_paper_algorithms": False,
    }


def _load_packet_runner():
    path = APP_DIR / "run_ssb_packet_rtdl.py"
    name = "rtdl_v4_raydb_packet_runner"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the frozen RayDB packet runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_v4_real_scale_packet(
    *, packet_path, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path, partition_rows: int,
) -> dict[str, object]:
    """Run a frozen columnar packet without Python row/event materialization."""

    started = time.perf_counter()
    callback = compile_keyed_callback()
    schema = keyed_i64_sum_schema(callback)
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, target, proof,
        compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    compile_seconds = time.perf_counter() - started
    runner = _load_packet_runner()
    library = _load_optix_library()
    result = execute_verified_partitioned_grouped_i64_v4(
        program,
        packet_runner=runner.run_packet,
        packet_path=packet_path,
        native_library=library,
        native_library_path=native_library_path,
        partition_rows=partition_rows,
    )
    physical = result.physical_result
    return {
        "schema": "rtdl.paper_reproduction.raydb.v4.real_scale.v1",
        "output": {"grouped_rows": physical["rtdl_rows"]},
        "expected": {"grouped_rows": physical["expected_rows"]},
        "matched": bool(physical["rtdl_matches_oracle"]),
        "reported_compiler_seconds": compile_seconds,
        "reported_complete_packet_seconds": physical[
            "registered_primary_timing"]["elapsed_seconds"],
        "prepare_is_free": False,
        "physical_lowering": result.physical_lowering,
        "callback_ptx_sha256": result.callback_ptx_sha256,
        "traversal_receipt": result.traversal_receipt,
        "native_library_sha256": physical["native_library_sha256"],
        "partition_count": physical["partition_count"],
        "partition_rows": physical["partition_rows"],
        "row_count": physical["row_count"],
        "phase_timing_seconds": physical["phase_timing_seconds"],
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "PreparedRayDbV4", "V4RayDBInput", "build_v4_input", "prepare_v4",
    "run_v4_complete", "run_v4_real_scale_packet",
]
