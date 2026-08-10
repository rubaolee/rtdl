"""App-owned mapping of each required paper algorithm to generic V3 contracts."""

from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import sys

from rtdsl.action_api import ActionTargetProfile, compile_action_source
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_ir import (
    U64,
    ActionField,
    ActionRecordType,
    ActionReductionSpec,
    ActionScalarLiteral,
    DeliveryEnforcement,
    LogicalEventContract,
    PhysicalDelivery,
    ReductionOperator,
)
from rtdsl.action_ray_triangle_scalar_summary import (
    CompilerPreparedRayTriangleScalarSummaryProgram,
    PreparedRayTriangleScalarSummaryForkTicket,
    RayTriangleScalarProducerKind,
    compile_ray_triangle_scalar_summary,
    detect_ray_triangle_scalar_summary_target,
    prepare_ray_triangle_scalar_summary_program,
)


APP_DIR = Path(__file__).resolve().parent
ROOT = next(parent for parent in APP_DIR.parents if (parent / "src" / "rtdsl").exists())
BENCHMARK_PATH = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)

# RT-1A2 and RT-2A1 are two required paper algorithms.  The application
# selects one explicitly; the compiler implements both and never chooses
# between them.
CANONICAL_ALGORITHM_BINDINGS = {
    "RT-1A2": (
        "ray_triangle_scalar.all_hit_count_value.v1",
        "nvidia.optix_traversal.v1",
    ),
    "RT-2A1": (
        "ray_triangle_scalar.any_hit_weighted_value.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("RT-1A2", "RT-2A1")

ACTION_SOURCE = """
def action(event, params):
    value = event.value
    reduce("scalar_sum", value)
"""


def action_contract() -> RestrictedActionFrontendContract:
    return RestrictedActionFrontendContract(
        event_type=ActionRecordType(
            "ray_value_event",
            (ActionField("ray_id", U64), ActionField("value", U64)),
        ),
        parameter_type=ActionRecordType("parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("ray_id",),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="one-logical-value-per-ray-v1",
        ),
        reductions=(
            ActionReductionSpec(
                "scalar_sum",
                (),
                U64,
                ReductionOperator.SUM,
                ActionScalarLiteral.from_python(U64, 0),
            ),
        ),
    )


def _load_benchmark():
    name = "goal5725_triangle_counting_benchmark_v3"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, BENCHMARK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {BENCHMARK_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _producer_for_algorithm(paper_algorithm: str) -> RayTriangleScalarProducerKind:
    if paper_algorithm == "RT-1A2":
        return RayTriangleScalarProducerKind.RAY_ALL_HIT_COUNT_VALUE_3D
    if paper_algorithm == "RT-2A1":
        return RayTriangleScalarProducerKind.RAY_ANY_HIT_WEIGHTED_VALUE_3D
    raise ValueError("paper_algorithm must be RT-1A2 or RT-2A1")


def _canonical_authority_kwargs(
    target: ActionTargetProfile,
    paper_algorithm: str,
) -> dict[str, str]:
    """Bind production compilation to the app-selected paper algorithm."""

    if (
        target.production_selection_policy != "compiler_owned_default"
        or not target.optix_available
    ):
        return {}
    statement_id, backend_id = CANONICAL_ALGORITHM_BINDINGS[paper_algorithm]
    return {
        "semantic_statement_stable_id": statement_id,
        "backend_contract_id": backend_id,
    }


def prepare_v3_segmented_compiler_program(
    *,
    target_profile: ActionTargetProfile,
) -> CompilerPreparedRayTriangleScalarSummaryProgram:
    """Prepare both required producer contracts without choosing between them."""

    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    contracts = tuple(
        (
            _producer_for_algorithm(paper_algorithm),
            CANONICAL_ALGORITHM_BINDINGS[paper_algorithm][0],
            CANONICAL_ALGORITHM_BINDINGS[paper_algorithm][1],
        )
        for paper_algorithm in FORMAL_PAPER_ALGORITHMS
    )
    return prepare_ray_triangle_scalar_summary_program(
        compiled,
        producer_contracts=contracts,
        target_profile=target_profile,
    )


def run_v3_algorithm(
    *,
    paper_algorithm: str,
    fixture: str = "degree_oriented_two_triangles",
    edge_file: str | None = None,
    edge_format: str = "text",
    partner: str = "none",
    target_profile: ActionTargetProfile | None = None,
    require_optix: bool = True,
    expected_triangle_count: int | None = None,
    segmented: bool = False,
    max_relation_rows: int = 1_000_000,
) -> dict[str, object]:
    """Compile and execute exactly one caller-requested paper algorithm."""

    app = _load_benchmark()
    if segmented:
        if edge_file is None or edge_format != "binary" or partner != "cupy":
            raise ValueError("segmented V3 requires CuPy binary edge-file execution")
        if expected_triangle_count is None:
            raise ValueError("segmented paper-dataset execution requires author expected count")
        graph_contract = app.build_segmented_rt_graph_csr_binary(
            edge_file,
            expected_triangle_count=expected_triangle_count,
        )
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
        producer = _producer_for_algorithm(paper_algorithm)
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
        target = target_profile or detect_ray_triangle_scalar_summary_target()
        plan = compile_ray_triangle_scalar_summary(
            compiled,
            producer_kind=producer,
            target_profile=target,
            require_optix=require_optix,
            **_canonical_authority_kwargs(target, paper_algorithm),
        )
        executed = plan.execute_segments(
            app.iter_segmented_rt_graph_device_geometry(
                graph_contract,
                paper_algorithm=paper_algorithm,
                max_relation_rows=max_relation_rows,
            )
        )
        actual = int(executed["scalar_sum"])
        expected = int(graph_contract.expected_triangle_count)
        return {
            "schema": "rtdl.paper_reproduction.rt_graph_triangle_counting.v3.v2",
            "version": "v3",
            "paper_algorithm": paper_algorithm,
            "application_selected_algorithm": True,
            "default_selected_between_paper_algorithms": False,
            "producer_kind": producer.value,
            "device_column_execution": True,
            "segmented_execution": True,
            "input_source": input_source,
            "output": {"triangle_count": actual},
            "expected": {"triangle_count": expected},
            "matched": actual == expected,
            "plan": plan.to_metadata(),
            "execution": executed,
        }

    device_column_execution = edge_file is not None and edge_format == "binary" and partner == "cupy"
    if device_column_execution:
        graph_contract = app.build_rt_graph_triangle_summary_contract_cupy_binary(edge_file)
        input_source = {"kind": "edge_file", "format": "binary", "path": edge_file}
    else:
        edges, input_source = app._load_rt_graph_edges(
            fixture=fixture,
            edge_file=edge_file,
            edge_format=edge_format,
            fixture_copies=1,
        )
        graph_contract = app.build_rt_graph_triangle_contract(edges)
    producer = _producer_for_algorithm(paper_algorithm)
    if paper_algorithm == "RT-1A2":
        if device_column_execution:
            triangles, rays = app._build_rt_graph_1a2_device_geometry(graph_contract)
        else:
            triangles, rays = app._build_rt_graph_1a2_geometry(graph_contract)
        ray_weights = None
    else:
        if device_column_execution:
            triangles, rays, ray_weights = app._build_rt_graph_2a1_device_geometry(graph_contract)
        else:
            triangles, rays, ray_weights = app._build_rt_graph_2a1_geometry(graph_contract)

    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    target = target_profile or detect_ray_triangle_scalar_summary_target()
    plan = compile_ray_triangle_scalar_summary(
        compiled,
        producer_kind=producer,
        target_profile=target,
        require_optix=require_optix,
        **_canonical_authority_kwargs(target, paper_algorithm),
    )
    executed = plan.execute(
        triangles=triangles,
        rays=rays,
        ray_weights=ray_weights,
    )
    actual = int(executed["scalar_sum"])
    expected = int(graph_contract.triangle_count)
    return {
        "schema": "rtdl.paper_reproduction.rt_graph_triangle_counting.v3.v1",
        "version": "v3",
        "paper_algorithm": paper_algorithm,
        "application_selected_algorithm": True,
        "default_selected_between_paper_algorithms": False,
        "producer_kind": producer.value,
        "device_column_execution": device_column_execution,
        "input_source": input_source,
        "output": {"triangle_count": actual},
        "expected": {"triangle_count": expected},
        "matched": actual == expected,
        "plan": plan.to_metadata(),
        "execution": executed,
    }


def run_v3_segmented_contract_epoch(
    *,
    graph_contract,
    paper_algorithm: str,
    max_relation_rows: int,
    start_segment_id: int,
    stop_segment_id: int,
    target_profile: ActionTargetProfile | None = None,
    require_optix: bool = True,
    prepared_program: CompilerPreparedRayTriangleScalarSummaryProgram | None = None,
    prepared_execution_ticket: PreparedRayTriangleScalarSummaryForkTicket | None = None,
) -> dict[str, object]:
    """Execute one fresh-process epoch, optionally from a compiler program."""

    app = _load_benchmark()
    producer = _producer_for_algorithm(paper_algorithm)
    if prepared_program is not None and prepared_execution_ticket is not None:
        raise ValueError("prepared program and execution ticket are mutually exclusive")
    if prepared_program is None and prepared_execution_ticket is None:
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
        target = target_profile or detect_ray_triangle_scalar_summary_target()
        plan = compile_ray_triangle_scalar_summary(
            compiled,
            producer_kind=producer,
            target_profile=target,
            require_optix=require_optix,
            **_canonical_authority_kwargs(target, paper_algorithm),
        )
        compiler_lifecycle = "cold_compile_and_execute"
    else:
        if target_profile is not None:
            raise ValueError("prepared compiler program owns its target profile")
        if require_optix is not True:
            raise ValueError("prepared canonical program requires OptiX")
        prepared_authority = (
            prepared_execution_ticket
            if prepared_execution_ticket is not None
            else prepared_program
        )
        plan = prepared_authority.require_plan(
            producer_kind=producer,
            expected_action_source_digest=hashlib.sha256(
                ACTION_SOURCE.encode("utf-8")
            ).hexdigest(),
        )
        compiler_lifecycle = "compiler_prepared_then_execute"
    executed = plan.execute_segments(
        app.iter_segmented_rt_graph_device_geometry(
            graph_contract,
            paper_algorithm=paper_algorithm,
            max_relation_rows=max_relation_rows,
            max_directed_edge_rows=max_relation_rows,
            start_segment_id=start_segment_id,
            stop_segment_id=stop_segment_id,
        )
    )
    return {
        "version": "v3",
        "paper_algorithm": paper_algorithm,
        "producer_kind": producer.value,
        "compiler_lifecycle": compiler_lifecycle,
        "output": {"triangle_count": int(executed["scalar_sum"])},
        "plan": plan.to_metadata(),
        "execution": executed,
    }


__all__ = [
    "ACTION_SOURCE",
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "action_contract",
    "prepare_v3_segmented_compiler_program",
    "run_v3_algorithm",
    "run_v3_segmented_contract_epoch",
]
