from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import statistics
import time

from . import aggregate_tree_reference as aggregate_reference
from . import embree_runtime
from . import optix_runtime
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import REQUIRED_PHASE_NAMES
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_instrumentation import EvidenceRecord
from .v3_0_instrumentation import InstrumentationPacket
from .v3_0_instrumentation import PhaseTimingRecord
from .v3_0_instrumentation import ResidencyEvidence
from .v3_0_m6_aggregate_pilots import M6_FRONTIER_CONTRACT_KEY
from .v3_0_m7_harness import BenchmarkHarnessPacket
from .v3_0_m7_harness import BenchmarkHarnessRow
from .v3_0_m7_harness import validate_benchmark_harness_packet


V3_M8_MEASURED_LOWERING_VERSION = "rtdl.v3_0.measured_lowering.m8"
V3_M8_MEASURED_LOWERING_STATUS = "m8_native_lowering_measured_no_public_claim"
V3_M8_AGGREGATE_FRONTIER_GRAPH_ID = "aggregate_frontier_lowering_pilot"
V3_M8_AGGREGATE_FRONTIER_COMPARISON_GROUP = "aggregate_frontier_native_lowering"
V3_M8_AGGREGATE_FRONTIER_DATASET = "deterministic_weighted_point_grid"
V3_M8_AGGREGATE_FRONTIER_CONTRACT = aggregate_reference.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT
V3_M8_AGGREGATE_FRONTIER_NATIVE_ABI = aggregate_reference.AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT

BackendFunction = Callable[..., dict[str, object]]


def make_v3_m8_weighted_point_grid(point_count: int) -> tuple[dict[str, float | int], ...]:
    """Return a deterministic generic weighted-point fixture."""

    count = int(point_count)
    if count <= 0:
        raise GraphValidationError("point_count must be positive")
    width = max(1, int(count ** 0.5))
    return tuple(
        {
            "id": index,
            "x": float(index % width),
            "y": float(index // width),
            "mass": 1.0 + float((index * 17) % 11) / 16.0,
        }
        for index in range(count)
    )


def run_v3_m8_aggregate_frontier_lowering_case(
    *,
    point_count: int = 512,
    bucket_size: int = 16,
    theta: float = 0.5,
    warmups: int = 1,
    repeats: int = 3,
    hardware: str = "local_host",
    backend_functions: Mapping[str, BackendFunction] | None = None,
) -> dict[str, object]:
    """Run a measured same-contract native lowering pilot for aggregate-frontier rows."""

    if int(bucket_size) <= 0:
        raise GraphValidationError("bucket_size must be positive")
    if float(theta) <= 0.0:
        raise GraphValidationError("theta must be positive")
    if int(warmups) < 0 or int(repeats) <= 0:
        raise GraphValidationError("warmups/repeats are invalid")
    validate_v3_public_name(V3_M8_AGGREGATE_FRONTIER_GRAPH_ID, label="M8 graph id")

    backend_functions = dict(backend_functions or _default_backend_functions())
    for backend in ("embree", "optix"):
        if backend not in backend_functions:
            raise GraphValidationError(f"M8 lowering case requires {backend} backend function")

    prepare_start = time.perf_counter()
    points = make_v3_m8_weighted_point_grid(int(point_count))
    prepare_seconds = time.perf_counter() - prepare_start

    build_start = time.perf_counter()
    tree = aggregate_reference.build_bucketized_aggregate_tree_2d(points, bucket_size=int(bucket_size))
    build_seconds = time.perf_counter() - build_start

    reference_start = time.perf_counter()
    expected = aggregate_reference.collect_aggregate_frontier_2d(
        points,
        tree["nodes"],
        theta=float(theta),
    )
    reference_seconds = time.perf_counter() - reference_start
    expected_row_count = int(expected["summary"]["frontier_row_count"])

    backend_rows: list[dict[str, object]] = []
    harness_rows: list[BenchmarkHarnessRow] = []
    for backend in ("embree", "optix"):
        backend_result = _run_backend_samples(
            backend=backend,
            fn=backend_functions[backend],
            points=points,
            tree_nodes=tree["nodes"],
            theta=float(theta),
            max_total_rows=expected_row_count,
            expected=expected,
            warmups=int(warmups),
            repeats=int(repeats),
        )
        instrumentation = build_v3_m8_lowering_instrumentation(
            backend=backend,
            hardware=hardware,
            prepare_seconds=prepare_seconds,
            build_seconds=build_seconds,
            native_seconds=float(backend_result["median_seconds"]),
            validation_seconds=reference_seconds,
            native_symbol=str(backend_result["native_symbol"]),
            frontier_row_count=expected_row_count,
        )
        harness_rows.append(
            BenchmarkHarnessRow(
                row_id=f"aggregate_frontier_{backend}_lowering_row",
                graph_id=V3_M8_AGGREGATE_FRONTIER_GRAPH_ID,
                comparison_group=V3_M8_AGGREGATE_FRONTIER_COMPARISON_GROUP,
                comparison_role=f"rtdl_{backend}",
                backend=backend,
                partner="none",
                dataset=V3_M8_AGGREGATE_FRONTIER_DATASET,
                scale=f"point_count={int(point_count)};tree_node_count={int(tree['summary']['tree_node_count'])}",
                hardware=hardware,
                timing_basis="phase_split",
                same_contract_key=M6_FRONTIER_CONTRACT_KEY,
                instrumentation=instrumentation,
                warmups=int(warmups),
                repeats=int(repeats),
                includes_build=True,
                includes_upload=False,
                includes_download=True,
                includes_validation=True,
            )
        )
        backend_rows.append(
            {
                **backend_result,
                "claim_readiness": instrumentation.claim_readiness,
                "public_claim_authorized": False,
            }
        )

    harness = BenchmarkHarnessPacket(
        packet_id="aggregate_frontier_lowering_packet",
        rows=tuple(harness_rows),
    )
    validation = validate_benchmark_harness_packet(harness)
    embree = next(row for row in backend_rows if row["backend"] == "embree")
    optix = next(row for row in backend_rows if row["backend"] == "optix")
    optix_seconds = float(optix["median_seconds"])
    embree_seconds = float(embree["median_seconds"])
    return {
        "version": V3_M8_MEASURED_LOWERING_VERSION,
        "status": V3_M8_MEASURED_LOWERING_STATUS,
        "graph_id": V3_M8_AGGREGATE_FRONTIER_GRAPH_ID,
        "contract": V3_M8_AGGREGATE_FRONTIER_CONTRACT,
        "native_abi_contract": V3_M8_AGGREGATE_FRONTIER_NATIVE_ABI,
        "dataset": V3_M8_AGGREGATE_FRONTIER_DATASET,
        "parameters": {
            "point_count": int(point_count),
            "bucket_size": int(bucket_size),
            "theta": float(theta),
            "warmups": int(warmups),
            "repeats": int(repeats),
        },
        "fixture_summary": {
            "point_count": len(points),
            "tree_node_count": int(tree["summary"]["tree_node_count"]),
            "frontier_row_count": expected_row_count,
            "reference_seconds": reference_seconds,
            "prepare_seconds": prepare_seconds,
            "build_seconds": build_seconds,
        },
        "backend_rows": tuple(backend_rows),
        "comparison": {
            "embree_median_seconds": embree_seconds,
            "optix_median_seconds": optix_seconds,
            "embree_over_optix_ratio": embree_seconds / optix_seconds if optix_seconds > 0 else None,
            "winner": "optix" if optix_seconds < embree_seconds else "embree",
        },
        "harness": harness.to_metadata(),
        "harness_validation": validation,
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "reason": (
                "This M8 case proves measured same-contract native lowering for a generic "
                "frontier row primitive. The current wrappers return host-materialized rows "
                "and do not prove same-stream partner continuation or RT-core speedup."
            ),
        },
    }


def build_v3_m8_lowering_instrumentation(
    *,
    backend: str,
    hardware: str,
    prepare_seconds: float,
    build_seconds: float,
    native_seconds: float,
    validation_seconds: float,
    native_symbol: str,
    frontier_row_count: int,
) -> InstrumentationPacket:
    if backend not in {"embree", "optix"}:
        raise GraphValidationError("M8 lowering instrumentation supports embree and optix")
    timer_kind = "embree_phase_timer" if backend == "embree" else "host_timer"
    timer_source = "embree_timer" if backend == "embree" else "host_timer"
    native_handle_id = f"{backend}_native_handle_record"
    native_timer_id = f"{backend}_native_timer_record"
    materialization_id = f"{backend}_host_materialization_record"
    validation_id = f"{backend}_validation_timer_record"
    evidence = (
        EvidenceRecord(
            evidence_id=native_handle_id,
            kind="backend_native_handle",
            backend=backend,
            phase="prepare",
            source="native_symbol_lookup",
            hardware=hardware,
            details={"native_symbol": native_symbol},
        ),
        EvidenceRecord(
            evidence_id=native_timer_id,
            kind=timer_kind,
            backend=backend,
            phase="rt_traversal",
            source="python_perf_counter_wrapper",
            hardware=hardware,
            details={
                "native_seconds_median": float(native_seconds),
                "frontier_row_count": int(frontier_row_count),
                "wrapper_includes_host_row_materialization": True,
            },
        ),
        EvidenceRecord(
            evidence_id=materialization_id,
            kind="host_timer",
            backend=backend,
            phase="download_or_materialization",
            source="native_wrapper_output_contract",
            hardware=hardware,
            details={"host_materialized_rows": int(frontier_row_count)},
        ),
        EvidenceRecord(
            evidence_id=validation_id,
            kind="host_timer",
            backend=backend,
            phase="validation",
            source="cpu_reference_parity_check",
            hardware=hardware,
            details={"validation_seconds": float(validation_seconds)},
        ),
    )
    timings = tuple(
        PhaseTimingRecord(
            phase=phase,
            seconds=_phase_seconds(
                phase,
                prepare_seconds=prepare_seconds,
                build_seconds=build_seconds,
                native_seconds=native_seconds,
                validation_seconds=validation_seconds,
            ),
            backend=backend,
            timing_source=_phase_source(phase, timer_source=timer_source),
            evidence_ids=_phase_evidence_ids(
                phase,
                native_handle_id=native_handle_id,
                native_timer_id=native_timer_id,
                materialization_id=materialization_id,
                validation_id=validation_id,
            ),
            steady_state_candidate=phase in {"rt_traversal", "stream_handoff", "continuation_or_reduction"},
            setup_candidate=phase in {"prepare", "build", "upload", "query_prepare"},
            materialization_candidate=phase == "download_or_materialization",
        )
        for phase in REQUIRED_PHASE_NAMES
    )
    residency = (
        ResidencyEvidence(
            value_name="frontier_rows",
            storage="host",
            residency="materialized",
            lifetime="session_retained",
            stream_ordering="host_synchronized",
            data_ptr_observed=False,
            backend_handle_observed=True,
            transfer_counter_observed=False,
            host_materialized=True,
            hidden_copy_observed=False,
            evidence_ids=(native_handle_id, materialization_id),
        ),
    )
    return InstrumentationPacket(
        graph_id=V3_M8_AGGREGATE_FRONTIER_GRAPH_ID,
        backend=backend,
        hardware=hardware,
        phase_timings=timings,
        evidence_records=evidence,
        residency_evidence=residency,
    )


def validate_v3_m8_aggregate_frontier_lowering_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if payload.get("version") != V3_M8_MEASURED_LOWERING_VERSION:
        raise GraphValidationError("unexpected M8 measured lowering version")
    if payload.get("status") != V3_M8_MEASURED_LOWERING_STATUS:
        raise GraphValidationError("unexpected M8 measured lowering status")
    if payload.get("native_abi_contract") != V3_M8_AGGREGATE_FRONTIER_NATIVE_ABI:
        raise GraphValidationError("unexpected M8 native ABI contract")
    rows = tuple(payload.get("backend_rows", ()))
    if len(rows) != 2:
        raise GraphValidationError("M8 aggregate-frontier lowering requires two backend rows")
    backends = {str(row["backend"]) for row in rows if isinstance(row, Mapping)}
    if backends != {"embree", "optix"}:
        raise GraphValidationError("M8 aggregate-frontier rows must cover embree and optix")
    if bool(payload.get("claim_boundary", {}).get("public_speedup_claim_authorized")):
        raise GraphValidationError("M8 payload must not authorize public speedup claims")
    validation = payload.get("harness_validation")
    if not isinstance(validation, Mapping) or validation.get("public_claim_authorized") is not False:
        raise GraphValidationError("M8 harness validation must keep public claims locked")
    return {
        "status": V3_M8_MEASURED_LOWERING_STATUS,
        "backend_count": len(rows),
        "public_claim_authorized": False,
        "native_abi_contract": V3_M8_AGGREGATE_FRONTIER_NATIVE_ABI,
    }


def _default_backend_functions() -> dict[str, BackendFunction]:
    return {
        "embree": embree_runtime.collect_aggregate_frontier_2d_embree,
        "optix": optix_runtime.collect_aggregate_frontier_2d_optix,
    }


def _run_backend_samples(
    *,
    backend: str,
    fn: BackendFunction,
    points: Iterable[object],
    tree_nodes: Iterable[object],
    theta: float,
    max_total_rows: int,
    expected: Mapping[str, object],
    warmups: int,
    repeats: int,
) -> dict[str, object]:
    for _ in range(warmups):
        warmup = fn(points, tree_nodes, theta=theta, max_total_rows=max_total_rows)
        _validate_same_rows(backend, warmup, expected)

    samples: list[float] = []
    last_result: dict[str, object] | None = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn(points, tree_nodes, theta=theta, max_total_rows=max_total_rows)
        elapsed = time.perf_counter() - start
        _validate_same_rows(backend, result, expected)
        samples.append(elapsed)
        last_result = result

    if last_result is None:
        raise GraphValidationError("M8 backend run produced no samples")
    metadata = last_result.get("metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    return {
        "backend": backend,
        "samples_seconds": tuple(samples),
        "median_seconds": statistics.median(samples),
        "min_seconds": min(samples),
        "max_seconds": max(samples),
        "frontier_row_count": int(last_result["summary"]["frontier_row_count"]),
        "native_symbol": str(metadata.get("native_symbol", f"{backend}_reference_function")),
        "native_engine_app_specific": bool(metadata.get("native_engine_app_specific", False)),
        "rows_match_reference": True,
    }


def _validate_same_rows(backend: str, actual: Mapping[str, object], expected: Mapping[str, object]) -> None:
    if actual["frontier_i64_rows"] != expected["frontier_i64_rows"]:
        raise GraphValidationError(f"{backend} frontier rows do not match the CPU reference")
    if actual["row_offsets"] != expected["row_offsets"]:
        raise GraphValidationError(f"{backend} row offsets do not match the CPU reference")
    if actual["source_ids"] != expected["source_ids"]:
        raise GraphValidationError(f"{backend} source ids do not match the CPU reference")


def _phase_seconds(
    phase: str,
    *,
    prepare_seconds: float,
    build_seconds: float,
    native_seconds: float,
    validation_seconds: float,
) -> float:
    if phase == "prepare":
        return float(prepare_seconds)
    if phase == "build":
        return float(build_seconds)
    if phase == "rt_traversal":
        return float(native_seconds)
    if phase == "download_or_materialization":
        return 0.0
    if phase == "validation":
        return float(validation_seconds)
    return 0.0


def _phase_source(phase: str, *, timer_source: str) -> str:
    if phase == "rt_traversal":
        return timer_source
    if phase in {"prepare", "build", "validation", "download_or_materialization", "host_wrapper"}:
        return "host_timer"
    return "metadata_only"


def _phase_evidence_ids(
    phase: str,
    *,
    native_handle_id: str,
    native_timer_id: str,
    materialization_id: str,
    validation_id: str,
) -> tuple[str, ...]:
    if phase == "prepare":
        return (native_handle_id,)
    if phase == "rt_traversal":
        return (native_timer_id,)
    if phase == "download_or_materialization":
        return (materialization_id,)
    if phase == "validation":
        return (validation_id,)
    return ()
