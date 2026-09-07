"""Application-owned RTDL V4 front door for both RT-Graph algorithms.

Unlike the Goal5759 semantic fixture, this module starts from graph edges and
executes the paper-owned RT-1A2 or RT-2A1 lowering.  The application chooses the
algorithm; RTDL only verifies and compiles its restricted callback/schema.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
from pathlib import Path
import time

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_triangle_reduction_optix_runtime import (
    run_builtin_triangle_reduction_callback,
)
from rtdsl.v4_triangle_reduction_prepared_runtime import (
    prepare_triangle_reduction_callback,
)
from rtdsl.v4_triangle_reduction_device_runtime import (
    VerifiedTriangleDeviceColumnCountExecutor,
)
from rtdsl.v4_triangle_standard_library import (
    all_hit_count_schema,
    compile_count_callback,
    compile_standard_triangle_program,
    weighted_hit_count_schema,
)


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = (
    ROOT / "examples/current/research_benchmarks/triangle_counting/"
    "rtdl_triangle_counting_benchmark_app.py"
)
FORMAL_PAPER_ALGORITHMS = ("RT-1A2", "RT-2A1")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _benchmark():
    spec = importlib.util.spec_from_file_location("rtdl_v4_triangle_app", BENCHMARK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen Triangle Counting benchmark")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class V4TriangleCountingInput:
    paper_algorithm: str
    vertices: tuple[tuple[float, float, float], ...]
    triangles: tuple[tuple[int, int, int], ...]
    queries: tuple[
        tuple[tuple[float, float, float], tuple[float, float, float], float], ...
    ]
    metadata: dict[str, tuple[int, ...]]
    expected_triangle_count: int
    input_sha256: str


def _indexed_geometry(triangles, rays):
    vertices: list[tuple[float, float, float]] = []
    indices: list[tuple[int, int, int]] = []
    for triangle in triangles:
        base = len(vertices)
        vertices.extend((
            (float(triangle.x0), float(triangle.y0), float(triangle.z0)),
            (float(triangle.x1), float(triangle.y1), float(triangle.z1)),
            (float(triangle.x2), float(triangle.y2), float(triangle.z2)),
        ))
        indices.append((base, base + 1, base + 2))
    queries = tuple((
        (float(ray.ox), float(ray.oy), float(ray.oz)),
        (float(ray.dx), float(ray.dy), float(ray.dz)),
        float(ray.tmax),
    ) for ray in rays)
    return tuple(vertices), tuple(indices), queries


def build_v4_input(
    paper_algorithm: str,
    *,
    fixture: str = "degree_oriented_two_triangles",
    edge_file: str | None = None,
    edge_format: str = "text",
) -> V4TriangleCountingInput:
    if paper_algorithm not in FORMAL_PAPER_ALGORITHMS:
        raise ValueError("paper_algorithm must be RT-1A2 or RT-2A1")
    app = _benchmark()
    edges, _ = app._load_rt_graph_edges(
        fixture=fixture,
        edge_file=edge_file,
        edge_format=edge_format,
        fixture_copies=1,
    )
    graph = app.build_rt_graph_triangle_contract(edges)
    if paper_algorithm == "RT-1A2":
        primitive_rows, ray_rows = app._build_rt_graph_1a2_geometry(graph)
        ray_weights: tuple[int, ...] = ()
    else:
        primitive_rows, ray_rows, ray_weights = (
            app._build_rt_graph_2a1_geometry(graph))
    vertices, triangles, queries = _indexed_geometry(primitive_rows, ray_rows)
    metadata = (
        {} if paper_algorithm == "RT-1A2"
        else {"query.weight": tuple(int(value) for value in ray_weights)}
    )
    semantic = {
        "paper_algorithm": paper_algorithm,
        "vertices": vertices,
        "triangles": triangles,
        "queries": queries,
        "metadata": metadata,
        "expected_triangle_count": int(graph.triangle_count),
    }
    return V4TriangleCountingInput(
        paper_algorithm,
        vertices,
        triangles,
        queries,
        metadata,
        int(graph.triangle_count),
        _digest(semantic),
    )


def _proof(callback) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "triangle_counting_paper_mapping_order_independence_v1",
            "callback": callback.ir_sha256,
            "app_source": _sha(Path(__file__)),
            "benchmark_source": _sha(BENCHMARK),
            "paper_algorithms": FORMAL_PAPER_ALGORITHMS,
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


@dataclass
class PreparedTriangleCountingV4:
    owner: object
    paper_algorithm: str
    prepared_input: V4TriangleCountingInput
    total_prepare_seconds: float

    def execute(self, *, queries=None, query_metadata=None):
        query_values = (
            self.prepared_input.queries if queries is None else tuple(queries))
        if query_metadata is None:
            query_metadata = {
                key: value for key, value in self.prepared_input.metadata.items()
                if key.startswith("query.")}
        started = time.perf_counter()
        executed = self.owner.execute(
            query_values, query_metadata=query_metadata)
        elapsed = time.perf_counter() - started
        matched = int(executed.reduced_output) \
            == self.prepared_input.expected_triangle_count
        return {
            "schema": "rtdl.paper_reproduction.triangle_counting.v4.prepared.v1",
            "paper_algorithm": self.paper_algorithm,
            "output": {"triangle_count": int(executed.reduced_output)},
            "expected": {"triangle_count":
                         self.prepared_input.expected_triangle_count},
            "matched": matched,
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


@dataclass
class PreparedSegmentedTriangleCountingV4:
    """Program/CSR owner for bounded real-scale device-column execution."""

    executor: VerifiedTriangleDeviceColumnCountExecutor
    graph_contract: object
    paper_algorithm: str
    max_relation_rows: int
    total_prepare_seconds: float

    def execute(self) -> dict[str, object]:
        import cupy as cp

        app = _benchmark()
        started = time.perf_counter()
        scalar_sum = 0
        segment_rows = []
        receipts = []
        for segment in app.iter_segmented_rt_graph_device_geometry(
            self.graph_contract,
            paper_algorithm=self.paper_algorithm,
            max_relation_rows=self.max_relation_rows,
            max_directed_edge_rows=self.max_relation_rows,
        ):
            triangles = segment["triangles"]
            rays = segment["rays"]
            weights = segment["ray_weights"]
            executed = self.executor.execute_segment(
                triangles, rays, ray_weights=weights)
            value = int(executed["reduced_output"])
            if value < 0 or scalar_sum > ((1 << 64) - 1) - value:
                raise OverflowError("segmented V4 triangle U64 scalar sum overflow")
            scalar_sum += value
            receipts.append(executed["traversal_receipt"])
            segment_rows.append({
                "segment_id": int(segment["segment_id"]),
                "scalar_sum": value,
                "ray_count": int(executed["query_count"]),
                "primitive_count": int(executed["triangle_count"]),
                "relation_count": int(segment["relation_count"]),
                "partition": segment["partition"],
                "device_columns_preserved": True,
                "per_ray_host_materialized": False,
                "checked_u64_weighted_reduction": executed[
                    "checked_u64_weighted_reduction"],
            })
            del executed, triangles, rays, weights, segment
            cp.get_default_memory_pool().free_all_blocks()
        if not segment_rows:
            raise RuntimeError("segmented V4 execution produced no physical segment")
        elapsed = time.perf_counter() - started
        expected = int(self.graph_contract.expected_triangle_count)
        return {
            "schema": "rtdl.paper_reproduction.triangle_counting.v4.segmented.v1",
            "paper_algorithm": self.paper_algorithm,
            "output": {"triangle_count": scalar_sum},
            "expected": {"triangle_count": expected},
            "matched": scalar_sum == expected,
            "registered_prepared_execution_seconds": elapsed,
            "reported_total_prepare_seconds": self.total_prepare_seconds,
            "prepare_is_free": False,
            "cold_result_replaced": False,
            "segmented_execution": True,
            "segment_count": len(segment_rows),
            "segments": segment_rows,
            "traversal_receipts": receipts,
            "native_library_sha256": self.executor.native_library_sha256,
            "application_selected_algorithm": True,
            "default_selected_between_paper_algorithms": False,
            "global_two_hop_materialized": False,
            "device_columns_preserved": True,
            "per_ray_host_materialized": False,
        }

    def close(self) -> None:
        self.executor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_v4_segmented(
    paper_algorithm: str,
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path, edge_file: str, expected_triangle_count: int,
    max_relation_rows: int = 1_000_000,
    prepared_graph_contract=None,
) -> PreparedSegmentedTriangleCountingV4:
    """Compile once, then execute bounded real graph segments on device."""

    if paper_algorithm not in FORMAL_PAPER_ALGORITHMS:
        raise ValueError("paper_algorithm must be RT-1A2 or RT-2A1")
    if not edge_file or max_relation_rows <= 0:
        raise ValueError("segmented V4 requires a binary edge file and row bound")
    started = time.perf_counter()
    app = _benchmark()
    graph_contract = (
        prepared_graph_contract
        if prepared_graph_contract is not None
        else app.build_segmented_rt_graph_csr_binary(
            edge_file, expected_triangle_count=expected_triangle_count)
    )
    if int(graph_contract.expected_triangle_count) != int(expected_triangle_count):
        raise ValueError("prepared graph contract has the wrong triangle oracle")
    callback = compile_count_callback()
    schema = (
        all_hit_count_schema(callback)
        if paper_algorithm == "RT-1A2"
        else weighted_hit_count_schema(callback))
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, target, proof,
        compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    executor = VerifiedTriangleDeviceColumnCountExecutor(
        authority=program.authority, contract=program.contract,
        abi=program.abi, any_hit_proof_authority=program.proof,
        executable=program.executable,
        native_library_path=native_library_path)
    return PreparedSegmentedTriangleCountingV4(
        executor, graph_contract, paper_algorithm, max_relation_rows,
        time.perf_counter() - started)


def run_v4_segmented_complete(**kwargs) -> dict[str, object]:
    started = time.perf_counter()
    prepared = prepare_v4_segmented(**kwargs)
    result = prepared.execute()
    result["registered_complete_seconds"] = time.perf_counter() - started
    result["complete_timer_includes"] = (
        "binary_graph_load_and_degree_oriented_csr",
        "restricted_callback_parse_verify_and_compile",
        "bounded_device_geometry_production",
        "device_column_triangle_gas_prepare",
        "optix_execute_and_device_checked_reduction",
        "scalar_host_materialization",
    )
    return result


def prepare_v4(
    paper_algorithm: str,
    *, target, compute_capability, optix_include, cuda_include,
    expected_python_version, expected_numba_version, expected_numpy_version,
    native_library_path, fixture="degree_oriented_two_triangles",
    edge_file=None, edge_format="text",
) -> PreparedTriangleCountingV4:
    started = time.perf_counter()
    prepared_input = build_v4_input(
        paper_algorithm, fixture=fixture, edge_file=edge_file,
        edge_format=edge_format)
    callback = compile_count_callback()
    schema = (
        all_hit_count_schema(callback)
        if paper_algorithm == "RT-1A2"
        else weighted_hit_count_schema(callback))
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback, schema, target, proof,
        compute_capability=compute_capability,
        optix_include=optix_include, cuda_include=cuda_include,
        expected_python_version=expected_python_version,
        expected_numba_version=expected_numba_version,
        expected_numpy_version=expected_numpy_version)
    primitive_metadata = {
        key: value for key, value in prepared_input.metadata.items()
        if key.startswith("primitive.")}
    owner = prepare_triangle_reduction_callback(
        authority=program.authority, contract=program.contract,
        abi=program.abi, any_hit_proof_authority=program.proof,
        executable=program.executable, vertices=prepared_input.vertices,
        triangles=prepared_input.triangles, metadata=primitive_metadata,
        event_capacity=1, native_library_path=native_library_path)
    return PreparedTriangleCountingV4(
        owner, paper_algorithm, prepared_input,
        time.perf_counter() - started)


def run_v4_complete(
    paper_algorithm: str,
    *,
    target,
    compute_capability: tuple[int, int],
    optix_include,
    cuda_include,
    expected_python_version: str,
    expected_numba_version: str,
    expected_numpy_version: str,
    native_library_path,
    fixture: str = "degree_oriented_two_triangles",
    edge_file: str | None = None,
    edge_format: str = "text",
) -> dict[str, object]:
    started = time.perf_counter()
    prepared_input = build_v4_input(
        paper_algorithm, fixture=fixture, edge_file=edge_file,
        edge_format=edge_format)
    callback = compile_count_callback()
    schema = (
        all_hit_count_schema(callback)
        if paper_algorithm == "RT-1A2"
        else weighted_hit_count_schema(callback)
    )
    proof = _proof(callback)
    program = compile_standard_triangle_program(
        callback,
        schema,
        target,
        proof,
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
        event_capacity=1,
        expected_reduced_output=prepared_input.expected_triangle_count,
        native_library_path=native_library_path,
    )
    complete_seconds = time.perf_counter() - started
    return {
        "schema": "rtdl.paper_reproduction.triangle_counting.v4.v1",
        "paper_algorithm": paper_algorithm,
        "input_sha256": prepared_input.input_sha256,
        "output": {"triangle_count": int(executed.reduced_output)},
        "expected": {
            "triangle_count": prepared_input.expected_triangle_count},
        "matched": int(executed.reduced_output)
        == prepared_input.expected_triangle_count,
        "registered_complete_seconds": complete_seconds,
        "complete_timer_includes": (
            "graph_input_load",
            "paper_graph_to_ray_triangle_lowering",
            "restricted_callback_parse_verify",
            "abi_and_wrapper_compile",
            "gas_pipeline_sbt_prepare",
            "optix_execute",
            "checked_reduction_and_host_materialization",
        ),
        "traversal_receipt": executed.traversal_receipt,
        "native_library_sha256": executed.native_library_sha256,
        "default_selected_between_paper_algorithms": False,
    }


__all__ = [
    "FORMAL_PAPER_ALGORITHMS",
    "V4TriangleCountingInput",
    "build_v4_input",
    "prepare_v4",
    "prepare_v4_segmented",
    "run_v4_complete",
    "run_v4_segmented_complete",
]
