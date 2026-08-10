"""App-owned RayJoin downstream-operator adapter for the RTDL 3.0 study."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import time
from types import MappingProxyType

import numpy as np

from rtdsl.action_api import (
    ActionProducerEventRegionKind,
    bind_action_event_columns,
    compile_action_source,
    compile_bound_action_for_target,
    detect_action_target_profile,
    prepare_bound_numba_action_columns,
    prepare_grouped_i64x2_count_sum_execution,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_host_continuation import (
    aligned_i64x2_count_sum_projection,
)
from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase
from rtdsl.action_ir import (
    I64,
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
from rtdsl.action_numba_continuation import execute_numba_grouped_i64x2_count_sum


APP_DIR = Path(__file__).resolve().parent

# Preserve the historical patch point while routing it through the new
# compiler-selected host/device grouped-execution front door.
prepare_action_execution = prepare_grouped_i64x2_count_sum_execution

# These are three required stages of one application algorithm, not competing
# plans.  Two are true-OptiX producers and one is the existing Numba partner
# continuation.  The generic segment-first-hit capability is not called by the
# current formal paper route and is therefore intentionally absent.
CANONICAL_ALGORITHM_BINDINGS = {
    "directed_segment_point_location": (
        "planar_map.directed_segment_point_location_2d.v1",
        "nvidia.optix_traversal.v1",
    ),
    "segment_pair_grouped_range_exact_count": (
        "planar_map.segment_pair_grouped_range_exact_count_2d.v1",
        "nvidia.optix_traversal.v1",
    ),
    "grouped_i64x2_count_sum": (
        "logical_events.grouped_i64x2_count_sum.v1",
        "numba.cuda_partner.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = (
    "directed_segment_point_location",
    "segment_pair_grouped_range_exact_count",
    "grouped_i64x2_count_sum",
)


def _canonical_authority_kwargs(target, algorithm: str) -> dict[str, str]:
    if target.production_selection_policy != "compiler_owned_default":
        return {}
    statement, backend = CANONICAL_ALGORITHM_BINDINGS[algorithm]
    return {
        "semantic_statement_stable_id": statement,
        "backend_contract_id": backend,
    }


_PREPARED_STATIC_IDENTITY_KEYS = (
    "identity_digest",
    "selected_backend",
    "selected_placement",
    "selected_template",
    "event_batch_row_count_mode",
    "max_event_rows",
)
_PREPARED_GROUPED_PHYSICAL_IDENTITIES = frozenset(
    {
        ("host", "host_continuation", "sorted_host_i64x2_count_sum"),
        ("numba", "device_continuation", "grouped_i64x2_count_sum"),
    }
)


def _prepared_static_identity_snapshot(
    prepared_metadata: object,
    *,
    expected_max_event_rows: int,
) -> MappingProxyType:
    """Validate and detach the exact static identity used by timed queries."""

    if type(prepared_metadata) is not dict:
        raise RuntimeError("prepared grouped execution metadata must be an exact dict")
    identity = prepared_metadata.get("identity")
    if type(identity) is not dict:
        raise RuntimeError("prepared grouped execution identity must be an exact dict")
    missing = set(_PREPARED_STATIC_IDENTITY_KEYS) - set(identity)
    if missing:
        raise RuntimeError(
            "prepared grouped execution static identity fields differ: "
            f"missing={sorted(missing)!r}"
        )
    snapshot = {
        key: identity[key]
        for key in _PREPARED_STATIC_IDENTITY_KEYS
    }
    digest = snapshot["identity_digest"]
    if not (
        type(digest) is str
        and len(digest) == 64
        and all(character in "0123456789abcdef" for character in digest)
    ):
        raise RuntimeError("prepared grouped execution identity digest is invalid")
    for key in ("selected_backend", "selected_placement", "selected_template"):
        if type(snapshot[key]) is not str or not snapshot[key]:
            raise RuntimeError(
                f"prepared grouped execution static identity {key} is invalid"
            )
    selected = (
        snapshot["selected_backend"],
        snapshot["selected_placement"],
        snapshot["selected_template"],
    )
    if selected not in _PREPARED_GROUPED_PHYSICAL_IDENTITIES:
        raise RuntimeError(
            "prepared grouped execution physical identity is unsupported: "
            f"{selected!r}"
        )
    if snapshot["event_batch_row_count_mode"] != "bounded_variable":
        raise RuntimeError(
            "prepared grouped execution row-count mode must be bounded_variable"
        )
    max_event_rows = snapshot["max_event_rows"]
    if (
        type(max_event_rows) is not int
        or max_event_rows < 0
        or max_event_rows != expected_max_event_rows
    ):
        raise RuntimeError(
            "prepared grouped execution max_event_rows differs from setup: "
            f"expected={expected_max_event_rows}; actual={max_event_rows!r}"
        )
    if set(snapshot) != set(_PREPARED_STATIC_IDENTITY_KEYS):
        raise RuntimeError("prepared grouped execution static identity schema differs")
    return MappingProxyType(snapshot)

ACTION_SOURCE = """
def action(event, params):
    length = event.group_length
    reduce("groups_by_pair")
    reduce("point_rows_by_pair", length)
"""


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "descriptor_group",
        (
            ActionField("group_stable_id", I64, nonnegative=True),
            ActionField("label_a", I64),
            ActionField("label_b", I64),
            ActionField("group_length", I64, nonnegative=True),
        ),
    )
    key_fields = ("label_a", "label_b")
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=ActionRecordType("parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("group_stable_id",),
            physical_delivery=PhysicalDelivery.PROVEN_SINGLE,
            enforcement=DeliveryEnforcement.PROVEN_SINGLE,
            proof_reference="prepared-index-single-delivery-contract-v1",
        ),
        reductions=(
            ActionReductionSpec(
                "groups_by_pair",
                key_fields,
                U64,
                ReductionOperator.COUNT,
                ActionScalarLiteral.from_python(U64, 0),
            ),
            ActionReductionSpec(
                "point_rows_by_pair",
                key_fields,
                I64,
                ReductionOperator.SUM,
                ActionScalarLiteral.from_python(I64, 0),
            ),
        ),
    )


def carrier_fixture() -> dict[str, np.ndarray]:
    return {
        "label_a": np.asarray([2, 1, 2, 1, 3], dtype=np.int64),
        "label_b": np.asarray([7, 5, 7, 5, 9], dtype=np.int64),
        "group_length": np.asarray([4, 3, 2, 5, 1], dtype=np.int64),
    }


def _events(carrier: dict[str, np.ndarray]) -> tuple[dict[str, object], ...]:
    events = tuple(
        {
            "group_stable_id": index,
            "label_a": int(carrier["label_a"][index]),
            "label_b": int(carrier["label_b"][index]),
            "group_length": int(carrier["group_length"][index]),
        }
        for index in range(len(carrier["label_a"]))
    )
    return tuple(
        sorted(
            events,
            key=lambda row: (row["label_a"], row["label_b"], row["group_stable_id"]),
        )
    )


def _event_columns(events: tuple[dict[str, object], ...]) -> dict[str, np.ndarray]:
    return {
        "group_stable_id": np.asarray(
            [row["group_stable_id"] for row in events], dtype=np.int64
        ),
        "label_a": np.asarray([row["label_a"] for row in events], dtype=np.int64),
        "label_b": np.asarray([row["label_b"] for row in events], dtype=np.int64),
        "group_length": np.asarray(
            [row["group_length"] for row in events], dtype=np.int64
        ),
    }


def _direct_event_columns(carrier: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    row_count = len(carrier["label_a"])
    group_stable_id = np.arange(row_count, dtype=np.int64)
    label_a = np.asarray(carrier["label_a"], dtype=np.int64)
    label_b = np.asarray(carrier["label_b"], dtype=np.int64)
    group_length = np.asarray(carrier["group_length"], dtype=np.int64)
    order = np.lexsort((group_stable_id, label_b, label_a))
    return {
        "group_stable_id": np.ascontiguousarray(group_stable_id[order]),
        "label_a": np.ascontiguousarray(label_a[order]),
        "label_b": np.ascontiguousarray(label_b[order]),
        "group_length": np.ascontiguousarray(group_length[order]),
    }


@lru_cache(maxsize=1)
def _load_v2_module():
    path = APP_DIR / "section57_overlay_columnar_binary.py"
    name = "rtdl_rayjoin_section57_overlay_columnar_binary"
    existing = sys.modules.get(name)
    if (
        existing is not None
        and Path(getattr(existing, "__file__", "")).resolve() == path.resolve()
    ):
        return existing
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _reduction_summary_with_top_indices(
    reduction_relations,
) -> tuple[dict[str, object], tuple[int, ...] | None]:
    reductions = {relation.name: relation for relation in reduction_relations}
    group_rows = reductions["groups_by_pair"].rows
    point_rows = reductions["point_rows_by_pair"].rows
    group_columns = getattr(group_rows, "to_i64x2_columns", None)
    point_columns = getattr(point_rows, "to_i64x2_columns", None)
    if callable(group_columns) and callable(point_columns):
        projection = aligned_i64x2_count_sum_projection(
            reduction_relations,
            count_reduction_name="groups_by_pair",
            sum_reduction_name="point_rows_by_pair",
        )
        group_a, group_b, group_counts, point_counts = (
            projection.to_python_columns()
        )
        pairs = tuple(
            {
                "label_a": label_a,
                "label_b": label_b,
                "group_count": group_count,
                "point_row_count": point_row_count,
            }
            for label_a, label_b, group_count, point_row_count in zip(
                group_a,
                group_b,
                group_counts,
                point_counts,
                strict=True,
            )
        )
        return (
            {
                "pair_count": projection.row_count,
                "total_groups": sum(group_counts),
                "total_point_rows": sum(point_counts),
                "pairs": pairs,
            },
            projection.top_indices_by_sum(10),
        )
    group_counts = {tuple(map(int, key)): int(value) for key, value in reductions["groups_by_pair"].rows}
    point_counts = {tuple(map(int, key)): int(value) for key, value in reductions["point_rows_by_pair"].rows}
    keys = tuple(sorted(set(group_counts) | set(point_counts)))
    return (
        {
            "pair_count": len(keys),
            "total_groups": sum(group_counts.values()),
            "total_point_rows": sum(point_counts.values()),
            "pairs": tuple(
                {
                    "label_a": key[0],
                    "label_b": key[1],
                    "group_count": group_counts[key],
                    "point_row_count": point_counts[key],
                }
                for key in keys
            ),
        },
        None,
    )


def _reduction_summary(reduction_relations) -> dict[str, object]:
    summary, _ = _reduction_summary_with_top_indices(reduction_relations)
    return summary


def _action_summary(result) -> dict[str, object]:
    return _reduction_summary(result.reductions)


def v2_summary_from_descriptor_consumer(
    carrier: dict[str, np.ndarray], descriptor_consumer
) -> dict[str, object]:
    raw = descriptor_consumer(carrier, include_pair_rows=True)
    rows = tuple(
        sorted(
            (
                {
                    "label_a": int(row["label_a"]),
                    "label_b": int(row["label_b"]),
                    "group_count": int(row["group_count"]),
                    "point_row_count": int(row["point_row_count"]),
                }
                for row in raw["pair_rows"]
            ),
            key=lambda row: (row["label_a"], row["label_b"]),
        )
    )
    return {
        "pair_count": int(raw["pair_count"]),
        "total_groups": int(raw["total_groups"]),
        "total_point_rows": int(raw["total_point_rows"]),
        "pairs": rows,
        "partner": raw["partner"],
    }


def _v2_summary(carrier: dict[str, np.ndarray]) -> dict[str, object]:
    return v2_summary_from_descriptor_consumer(
        carrier,
        _load_v2_module().descriptor_pair_count_projected,
    )


def _pair_rows_sha256(rows) -> str:
    payload = json.dumps(tuple(rows), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _consumer_result(
    carrier: dict[str, np.ndarray],
    *,
    execution_mode: str,
    validate_against_v2: bool = True,
    collect_phase_trace: bool = False,
) -> dict[str, object]:
    trace = (
        ActionPhaseTrace(app="rayjoin", route=f"descriptor_consumer_{execution_mode}")
        if collect_phase_trace
        else None
    )
    with action_phase(trace, "input_adapter", label="carrier_column_shape_access"):
        tuple(np.asarray(values).shape for values in carrier.values())
    with action_phase(
        trace, "action_compile_or_cache_hit", label="compile_action_source"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    if execution_mode == "reference":
        with action_phase(
            trace, "event_producer", label="carrier_columns_to_python_events"
        ):
            events = _events(carrier)
        if trace is not None:
            trace.mark_not_applicable(
                "binding_certificate", reason="CPU reference consumes normalized events directly"
            )
            trace.mark_not_applicable(
                "physical_plan", reason="CPU reference has no backend placement plan"
            )
            trace.mark_not_applicable(
                "backend_prepare", reason="CPU reference has no device backend preparation"
            )
            for phase in (
                "host_to_device_transfer",
                "device_to_host_transfer",
                "device_synchronization_wait",
            ):
                trace.mark_not_applicable(phase, reason="CPU reference is host-only")
        with action_phase(trace, "execute", label="cpu_reference_action_execute"):
            reductions = compiled.execute_reference(events, {}).reductions
        backend_metadata = compiled.to_metadata()
        selected_backend = "action_cpu_reference"
    elif execution_mode == "compiler":
        with action_phase(
            trace, "event_producer", label="carrier_columns_to_sorted_event_columns"
        ):
            columns = _direct_event_columns(carrier)
        with action_phase(
            trace,
            "binding_certificate",
            label="typed_column_digest_duplicate_and_order_binding",
        ):
            bound = bind_action_event_columns(
                compiled,
                columns,
                ordering_fields=("label_a", "label_b", "group_stable_id"),
            )
        with action_phase(
            trace, "physical_plan", label="target_probe_plan_and_lower"
        ):
            target = detect_action_target_profile(cpu_reference_available=False)
            planned = compile_bound_action_for_target(
                bound,
                target,
                extents={},
                parameters={},
                **_canonical_authority_kwargs(target, "grouped_i64x2_count_sum"),
            )
        with action_phase(
            trace,
            "backend_prepare",
            label="compiler_selected_grouped_execution_prepare",
        ):
            prepared_execution = prepare_action_execution(
                planned,
                extents={},
                parameters={},
                max_event_rows=len(columns["group_stable_id"]),
            )
        try:
            with action_phase(
                trace,
                "execute",
                label="compiler_selected_grouped_reduce_and_host_projection",
            ):
                query = prepared_execution.execute_columns(
                    columns,
                    extents={},
                    parameters={},
                )
                reductions = query.payload
            backend_metadata = {
                "planned": planned.to_metadata(),
                "prepared": prepared_execution.to_metadata(),
                "query": query.to_metadata(),
            }
        finally:
            with action_phase(
                trace,
                "backend_prepare",
                label="release_compiler_selected_prepared_state",
            ):
                prepared_execution.close()
        if trace is not None:
            if planned.lowered.backend == "numba":
                for name, kind in (
                    ("event_columns_upload", "host_to_device_transfer"),
                    ("reduction_columns_download", "device_to_host_transfer"),
                    ("reduction_ready_wait", "device_synchronization_wait"),
                ):
                    trace.fold_device_operation(
                        name=name,
                        kind=kind,
                        folded_into="execute",
                        reason="prepared device continuation exposes one reconciled synchronous query boundary",
                    )
            else:
                for phase in (
                    "host_to_device_transfer",
                    "device_to_host_transfer",
                    "device_synchronization_wait",
                ):
                    trace.mark_not_applicable(
                        phase,
                        reason="compiler selected the host grouped continuation",
                    )
        selected_backend = (
            "action_compiler_selected_"
            f"{planned.lowered.backend}_{planned.lowered.template_kind}"
        )
    else:
        raise ValueError(
            "RayJoin descriptor Action execution_mode must be reference or compiler"
        )

    with action_phase(trace, "projection", label="canonical_reduction_summary"):
        actual = _reduction_summary(reductions)
        top = tuple(
            sorted(
                actual["pairs"],
                key=lambda row: (
                    -int(row["point_row_count"]),
                    int(row["label_a"]),
                    int(row["label_b"]),
                ),
            )[:10]
        )
        actual_digest = _pair_rows_sha256(actual["pairs"])
        compact_actual = {
            "pair_count": actual["pair_count"],
            "total_groups": actual["total_groups"],
            "total_point_rows": actual["total_point_rows"],
            "top_pairs_by_point_rows": top,
            "pair_rows_sha256": actual_digest,
        }
    if validate_against_v2:
        with action_phase(trace, "app_validation", label="v2_consumer_comparator"):
            expected = _v2_summary(carrier)
            comparable_expected = {key: expected[key] for key in actual}
            expected_digest = _pair_rows_sha256(expected["pairs"])
            compact_expected = {
                "pair_count": expected["pair_count"],
                "total_groups": expected["total_groups"],
                "total_point_rows": expected["total_point_rows"],
                "top_pairs_by_point_rows": tuple(
                    sorted(
                        expected["pairs"],
                        key=lambda row: (
                            -int(row["point_row_count"]),
                            int(row["label_a"]),
                            int(row["label_b"]),
                        ),
                    )[:10]
                ),
                "pair_rows_sha256": expected_digest,
            }
    else:
        expected = None
        comparable_expected = None
        expected_digest = None
        compact_expected = None
        if trace is not None:
            trace.mark_not_applicable(
                "app_validation", reason="validate_against_v2 is false"
            )
    phase_trace = trace.finish() if trace is not None else None
    return {
        "pair_count": int(actual["pair_count"]),
        "total_groups": int(actual["total_groups"]),
        "total_point_rows": int(actual["total_point_rows"]),
        "top_pairs_by_point_rows": top,
        "partner": selected_backend,
        "consumer_contract": "typed_action_grouped_i64x2_count_and_sum.v1",
        "matched_v2_consumer": (
            actual == comparable_expected and actual_digest == expected_digest
            if expected is not None
            else None
        ),
        "actual_action_summary": compact_actual,
        "expected_v2_summary": compact_expected,
        "backend_metadata": backend_metadata,
        "runtime_performance_claimed": False,
        "phase_trace": phase_trace,
    }


def descriptor_action_consumer(
    *,
    execution_mode: str,
    validate_against_v2: bool = True,
    collect_phase_trace: bool = False,
):
    """Return an app-owned consumer for the full RayJoin producer pipeline."""

    def consume(carrier: dict[str, np.ndarray]) -> dict[str, object]:
        return _consumer_result(
            carrier,
            execution_mode=execution_mode,
            validate_against_v2=bool(validate_against_v2),
            collect_phase_trace=bool(collect_phase_trace),
        )

    return consume


class PreparedDescriptorActionConsumer:
    """Compiler-owned direct-column consumer reusable across bounded batches."""

    def __init__(
        self,
        *,
        max_event_rows: int,
        validate_against_v2: bool = True,
        collect_phase_trace: bool = True,
        comparison_order: str = "action_then_v2",
        v2_summary=None,
    ) -> None:
        if not isinstance(max_event_rows, int) or isinstance(max_event_rows, bool) or max_event_rows < 0:
            raise ValueError("max_event_rows must be a nonnegative integer")
        if comparison_order not in ("action_then_v2", "v2_then_action"):
            raise ValueError(
                "comparison_order must be action_then_v2 or v2_then_action"
            )
        started = time.perf_counter()
        self._compiled = compile_action_source(ACTION_SOURCE, action_contract())
        self._compile_seconds = time.perf_counter() - started
        self._max_event_rows = max_event_rows
        self._validate_against_v2 = bool(validate_against_v2)
        self._collect_phase_trace = bool(collect_phase_trace)
        self._comparison_order = comparison_order
        if v2_summary is None:
            v2_prepare_started = time.perf_counter()
            module = _load_v2_module()
            self._v2_summary = lambda carrier: v2_summary_from_descriptor_consumer(
                carrier, module.descriptor_pair_count_projected
            )
            self._v2_comparator_prepare_seconds = (
                time.perf_counter() - v2_prepare_started
            )
            self._v2_comparator_source = "app_cached_module"
        else:
            if not callable(v2_summary):
                raise ValueError("v2_summary must be callable")
            self._v2_summary = v2_summary
            self._v2_comparator_prepare_seconds = 0.0
            self._v2_comparator_source = "injected_existing_pipeline"
        plan_prepare_started = time.perf_counter()
        initial_columns = {
            "group_stable_id": np.asarray([], dtype=np.int64),
            "label_a": np.asarray([], dtype=np.int64),
            "label_b": np.asarray([], dtype=np.int64),
            "group_length": np.asarray([], dtype=np.int64),
        }
        bound = bind_action_event_columns(
            self._compiled,
            initial_columns,
            ordering_fields=("label_a", "label_b", "group_stable_id"),
        )
        target = detect_action_target_profile(
            producer_kind=bound.producer_kind,
            cpu_reference_available=False,
        )
        planned = compile_bound_action_for_target(
            bound,
            target,
            extents={},
            parameters={},
            producer_event_region=(
                ActionProducerEventRegionKind.COMPILER_OWNED_DEVICE_WRITE_LEASE
            ),
            **_canonical_authority_kwargs(target, "grouped_i64x2_count_sum"),
        )
        trace = planned.lowered.compiler_execution_trace
        production_default = (
            trace.get("production_default") if isinstance(trace, dict) else None
        )
        if not isinstance(production_default, dict):
            raise RuntimeError(
                "prepared RayJoin consumer lacks compiler-owned DEFAULT authority"
            )
        production_plan = production_default.get("plan")
        production_binding = production_default.get("binding")
        canonical_resolution = production_default.get("canonical_resolution")
        canonical_authority = production_default.get(
            "canonical_production_authority"
        )
        if (
            not isinstance(production_plan, dict)
            or production_plan.get("schema") != "rtdl.production_default.plan.v1"
            or not isinstance(production_binding, dict)
            or production_binding.get("schema")
            != "rtdl.production_default.binding.v1"
            or production_binding.get("production_plan_sha256")
            != production_plan.get("production_plan_sha256")
            or not isinstance(canonical_resolution, dict)
            or canonical_resolution.get("schema")
            != "rtdl.canonical_physical_resolution.receipt.v1"
            or not isinstance(canonical_authority, dict)
            or canonical_authority.get("schema")
            != "rtdl.canonical_physical_resolution.production_authority.v1"
        ):
            raise RuntimeError(
                "prepared RayJoin consumer canonical production authority is incomplete"
            )
        # The plan and binding already exist in the compiler trace.  Preserve
        # detached copies across the prepared lifetime so the composite app
        # cannot execute correctly while losing its production authority at
        # the endpoint evidence boundary.
        self._production_default_plan = deepcopy(production_plan)
        self._production_default_binding = deepcopy(production_binding)
        self._canonical_resolution = deepcopy(canonical_resolution)
        self._canonical_production_authority = deepcopy(canonical_authority)
        self._prepared = prepare_action_execution(
            planned,
            extents={},
            parameters={},
            max_event_rows=self._max_event_rows,
        )
        # The selected physical identity is invariant for this prepared
        # lifetime.  Snapshot it once in setup (which the six-batch contract
        # excludes) instead of serializing and HMAC-validating the complete
        # prepared lifecycle inside every timed consumer call.  Per-query
        # ownership/order evidence still comes from the query certificate, and
        # ``to_metadata`` below emits the complete live lifecycle after the
        # measured protocol.
        try:
            prepared_setup_metadata = self._prepared.to_metadata()
            self._prepared_identity_snapshot = _prepared_static_identity_snapshot(
                prepared_setup_metadata,
                expected_max_event_rows=self._max_event_rows,
            )
        except BaseException:
            # A prepared owner whose static identity cannot be proven must not
            # survive a failed consumer construction.
            self._prepared.close()
            raise
        self._plan_prepare_seconds = time.perf_counter() - plan_prepare_started
        self._call_count = 0
        self._closed = False

    @property
    def call_count(self) -> int:
        return self._call_count

    def begin_producer_owned_device_batch(self, *, capacity: int):
        """Open the compiler-owned host-continuation producer write lease."""

        if self._closed:
            raise RuntimeError("prepared descriptor Action consumer is closed")
        begin = getattr(
            self._prepared,
            "begin_producer_owned_device_batch",
            None,
        )
        if not callable(begin):
            return None
        return begin(capacity=capacity)

    def __call__(self, carrier: dict[str, np.ndarray]) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("prepared descriptor Action consumer is closed")
        ordinal = self._call_count
        trace = (
            ActionPhaseTrace(app="rayjoin", route=f"prepared_descriptor_batch_{ordinal}")
            if self._collect_phase_trace
            else None
        )
        device_resident = all(
            name in carrier
            for name in (
                "label_a_device",
                "label_b_device",
                "group_length_device",
                "group_count",
            )
        )
        producer_owned_batch = (
            carrier.get("_compiler_owned_unordered_i64x2_batch")
            if isinstance(carrier, dict)
            else None
        )
        with action_phase(trace, "input_adapter", label="carrier_column_shape_access"):
            if device_resident:
                row_count = int(carrier["group_count"])
                if row_count < 0:
                    raise ValueError("device carrier group_count must be nonnegative")
                for name in ("label_a_device", "label_b_device", "group_length_device"):
                    if int(carrier[name].shape[0]) < row_count:
                        raise ValueError(f"device carrier {name} is shorter than group_count")
            else:
                tuple(np.asarray(values).shape for values in carrier.values())

        expected = None
        expected_digest = None
        v2_seconds = None

        def measure_v2_consumer() -> None:
            nonlocal expected, expected_digest, v2_seconds
            with action_phase(trace, "app_validation", label="numba_sorted_pair_scan"):
                v2_started = time.perf_counter()
                expected = self._v2_summary(carrier)
                v2_seconds = time.perf_counter() - v2_started
                expected_digest = (
                    _pair_rows_sha256(expected["pairs"])
                    if "pairs" in expected
                    else None
                )

        if self._validate_against_v2 and self._comparison_order == "v2_then_action":
            measure_v2_consumer()

        action_consumer_started = time.perf_counter()
        consumer_observation_seconds: dict[str, float] = {}
        observation_started = time.perf_counter()
        with action_phase(
            trace, "event_producer", label="carrier_columns_to_sorted_event_columns"
        ):
            if device_resident:
                columns = {
                    "label_a": carrier["label_a_device"][:row_count],
                    "label_b": carrier["label_b_device"][:row_count],
                    "group_length": carrier["group_length_device"][:row_count],
                }
            else:
                columns = _direct_event_columns(carrier)
        consumer_observation_seconds["event_column_view_seconds"] = (
            time.perf_counter() - observation_started
        )

        initialized_this_query = False
        if trace is not None:
            trace.mark_not_applicable(
                "binding_certificate",
                reason=(
                    "input-independent compiler binding and plan were prepared before "
                    "the six-batch hot-body; fresh batch ownership is certified inside execute"
                ),
            )
            trace.mark_not_applicable(
                "physical_plan",
                reason="one compiler-owned physical plan is reused across the bounded stream",
            )
            trace.mark_not_applicable(
                "backend_prepare",
                reason="one compiler-owned prepared execution is reused across batches",
            )

        if trace is not None:
            with action_phase(
                trace,
                "action_compile_or_cache_hit",
                label="compiled_action_reuse",
            ):
                self._compiled.spec.semantic_digest
        with action_phase(
            trace,
            "execute",
            label="compiler_selected_grouped_reduce_and_host_projection",
        ):
            observation_started = time.perf_counter()
            execute_producer_owned = getattr(
                self._prepared,
                "execute_producer_owned_device_batch",
                None,
            )
            query = (
                execute_producer_owned(
                    producer_owned_batch,
                    extents={},
                    parameters={},
                )
                if producer_owned_batch is not None
                and callable(execute_producer_owned)
                else self._prepared.execute_device_columns(
                    columns,
                    extents={},
                    parameters={},
                )
                if device_resident
                else self._prepared.execute_columns(
                    columns,
                    extents={},
                    parameters={},
                )
            )
            reductions = query.payload
            consumer_observation_seconds["prepared_query_call_seconds"] = (
                time.perf_counter() - observation_started
            )
        observation_started = time.perf_counter()
        query_metadata = (
            query.to_metadata()
            if callable(getattr(query, "to_metadata", None))
            else {}
        )
        consumer_observation_seconds["query_metadata_detachment_seconds"] = (
            time.perf_counter() - observation_started
        )
        observation_started = time.perf_counter()
        if (
            getattr(query, "prepared_identity_digest", None)
            != self._prepared_identity_snapshot["identity_digest"]
        ):
            # Execution has already advanced the prepared owner.  Close both
            # layers before reporting the mismatch so caller-visible ordinals
            # can never diverge on a later query.
            self._closed = True
            try:
                self._prepared.close()
            except BaseException as close_error:
                raise RuntimeError(
                    "prepared grouped query identity differs from exact setup "
                    "snapshot; consumer failed closed and owner close failed"
                ) from close_error
            raise RuntimeError(
                "prepared grouped query identity differs from exact setup "
                "snapshot; consumer failed closed"
            )
        event_batch_certificate = query_metadata.get("event_batch_certificate")
        host_input_download = bool(
            isinstance(event_batch_certificate, dict)
            and event_batch_certificate.get("device_to_host_copy_used")
        )
        if trace is not None:
            if device_resident:
                trace.mark_not_applicable(
                    "host_to_device_transfer",
                    reason=(
                        "compiler-selected host continuation downloads the existing device columns"
                        if host_input_download
                        else "source event columns are already device resident; device continuation uses D2D ownership copies"
                    ),
                )
            else:
                if host_input_download:
                    trace.mark_not_applicable(
                        "host_to_device_transfer",
                        reason="compiler-selected host continuation consumes host columns",
                    )
                else:
                    trace.fold_device_operation(
                        name="event_columns_upload",
                        kind="host_to_device_transfer",
                        folded_into="execute",
                        reason="prepared device continuation column upload has no independent transfer timer",
                    )
            if host_input_download:
                trace.fold_device_operation(
                    name="source_event_columns_download",
                    kind="device_to_host_transfer",
                    folded_into="execute",
                    reason="compiler-selected host continuation synchronously owns the source columns on host",
                )
                trace.fold_device_operation(
                    name="source_event_columns_ready_wait",
                    kind="device_synchronization_wait",
                    folded_into="execute",
                    reason="the explicit device-to-host source copy waits before the host scan",
                )
            else:
                trace.fold_device_operation(
                    name="reduction_columns_download",
                    kind="device_to_host_transfer",
                    folded_into="execute",
                    reason="prepared device grouped projection downloads result columns inside execute_columns",
                )
                trace.fold_device_operation(
                    name="reduction_ready_wait",
                    kind="device_synchronization_wait",
                    folded_into="execute",
                    reason="prepared device grouped projection synchronizes before exposing host rows",
                )
        consumer_observation_seconds["identity_and_trace_accounting_seconds"] = (
            time.perf_counter() - observation_started
        )

        observation_started = time.perf_counter()
        with action_phase(trace, "projection", label="canonical_reduction_summary"):
            actual, top_indices = _reduction_summary_with_top_indices(reductions)
        consumer_observation_seconds["canonical_reduction_summary_seconds"] = (
            time.perf_counter() - observation_started
        )
        action_consumer_seconds = time.perf_counter() - action_consumer_started
        observation_started = time.perf_counter()
        with action_phase(
            trace,
            "projection",
            label="canonical_top_rows_and_optional_validation_digest",
        ):
            top = (
                tuple(actual["pairs"][index] for index in top_indices)
                if top_indices is not None
                else tuple(
                    sorted(
                        actual["pairs"],
                        key=lambda row: (
                            -int(row["point_row_count"]),
                            int(row["label_a"]),
                            int(row["label_b"]),
                        ),
                    )[:10]
                )
            )
            actual_digest = (
                _pair_rows_sha256(actual["pairs"])
                if self._validate_against_v2
                else None
            )
        consumer_observation_seconds[
            "canonical_top_rows_and_optional_digest_seconds"
        ] = (time.perf_counter() - observation_started)

        if self._validate_against_v2 and self._comparison_order == "action_then_v2":
            measure_v2_consumer()
        elif trace is not None and not self._validate_against_v2:
            trace.mark_not_applicable(
                "app_validation",
                reason=(
                    "the complete canonical pair-row comparator is mandatory "
                    "but is collected outside the writer-free registered hot body"
                ),
            )

        self._call_count += 1
        observation_started = time.perf_counter()
        phase_trace = trace.finish() if trace is not None else None
        consumer_observation_seconds["phase_trace_finish_seconds"] = (
            time.perf_counter() - observation_started
        )
        physical_identity = self._prepared_identity_snapshot
        comparable_expected = (
            {key: expected[key] for key in actual if key in expected}
            if expected is not None
            else None
        )
        comparable_actual = (
            {key: actual[key] for key in comparable_expected}
            if comparable_expected is not None
            else None
        )
        observation_started = time.perf_counter()
        result = {
            "pair_count": int(actual["pair_count"]),
            "total_groups": int(actual["total_groups"]),
            "total_point_rows": int(actual["total_point_rows"]),
            "pair_rows": tuple(actual["pairs"]),
            "top_pairs_by_point_rows": top,
            "pair_rows_sha256": actual_digest,
            "partner": "action_compiler_selected_grouped_i64x2_count_sum",
            "consumer_contract": "typed_action_grouped_i64x2_count_and_sum.prepared_stream.v2",
            "matched_v2_consumer": (
                comparable_actual == comparable_expected
                and (expected_digest is None or actual_digest == expected_digest)
                if expected is not None
                else None
            ),
            "expected_v2_pair_rows_sha256": expected_digest,
            "v2_numba_sorted_pair_scan_seconds": v2_seconds,
            "comparison_order": self._comparison_order,
            "prepared_query_ordinal": int(query.query_ordinal),
            "prepared_query_timing_regime": query.timing_regime,
            "prepared_query_seconds": float(query.elapsed_seconds),
            "device_event_batch_certificate": query_metadata.get(
                "event_batch_certificate"
            ),
            "source_event_columns_device_resident": device_resident,
            "compiler_preallocated_event_storage_used": bool(
                producer_owned_batch is not None
            ),
            "producer_owned_order_indexed_host_consumption_used": bool(
                isinstance(event_batch_certificate, dict)
                and event_batch_certificate.get("contract")
                == "rtdl.producer_owned_order_indexed_host_batch.v1"
                and event_batch_certificate.get(
                    "order_indexed_checked_scan_used"
                )
            ),
            "producer_owned_order_indexed_device_consumption_used": bool(
                isinstance(event_batch_certificate, dict)
                and event_batch_certificate.get("contract")
                == "rtdl.producer_owned_order_indexed_device_batch.v1"
                and event_batch_certificate.get(
                    "order_indexed_checked_scan_used"
                )
            ),
            "host_event_column_materialization_used": (
                not device_resident or host_input_download
            ),
            "prepared_consumer_phase_seconds": float(action_consumer_seconds),
            "prepared_initialized_this_query": initialized_this_query,
            "prepared_lifecycle": {
                "contract": "rtdl.rayjoin.prepared_descriptor_query_lifecycle.v2",
                "metadata_scope": "setup_identity_snapshot_plus_current_query",
                "identity": dict(physical_identity),
                "query_ordinal": int(query.query_ordinal),
                "timing_regime": query.timing_regime,
                # Keep both public certificate fields while preventing a
                # caller mutation through one view from changing the other.
                "event_batch_certificate": deepcopy(event_batch_certificate),
                "full_live_lifecycle_emitted_after_measured_protocol": True,
                "closed": False,
            },
            "selected_physical_backend": physical_identity.get(
                "selected_backend"
            ),
            "selected_physical_placement": physical_identity.get(
                "selected_placement"
            ),
            "selected_physical_template": physical_identity.get(
                "selected_template"
            ),
            "compiler_lifecycle": {
                "action_compile_count": 1,
                "physical_plan_count": 1,
                "prepared_execution_count": 1,
                "compile_seconds": float(self._compile_seconds),
                "v2_comparator_prepare_seconds": float(
                    self._v2_comparator_prepare_seconds
                ),
                "v2_comparator_source": self._v2_comparator_source,
                "plan_and_prepare_seconds": self._plan_prepare_seconds,
                "consumer_call_count": self._call_count,
                "max_event_rows": self._max_event_rows,
                "application_selected_backend": False,
            },
            "runtime_performance_claimed": False,
            "phase_trace": phase_trace,
        }
        consumer_observation_seconds["result_envelope_assembly_seconds"] = (
            time.perf_counter() - observation_started
        )
        full_consumer_seconds = time.perf_counter() - action_consumer_started
        consumer_observation_seconds["full_consumer_observed_seconds"] = float(
            full_consumer_seconds
        )
        consumer_observation_seconds["prepared_query_reported_seconds"] = float(
            query.elapsed_seconds
        )
        consumer_observation_seconds[
            "outside_prepared_query_observed_seconds"
        ] = max(0.0, full_consumer_seconds - float(query.elapsed_seconds))
        consumer_observation_seconds["observation_only"] = True
        consumer_observation_seconds["route_or_output_changed_by_observation"] = False
        result["prepared_consumer_observation_timing_seconds"] = (
            consumer_observation_seconds
        )
        return result

    def to_metadata(self) -> dict[str, object]:
        return {
            "contract": "rtdl.rayjoin.prepared_descriptor_action_consumer.v1",
            "consumer_call_count": self._call_count,
            "action_compile_count": 1,
            "physical_plan_count": 1 if self._prepared is not None else 0,
            "prepared_execution_count": 1 if self._prepared is not None else 0,
            "compile_seconds": float(self._compile_seconds),
            "v2_comparator_prepare_seconds": float(
                self._v2_comparator_prepare_seconds
            ),
            "v2_comparator_source": self._v2_comparator_source,
            "plan_and_prepare_seconds": self._plan_prepare_seconds,
            "max_event_rows": self._max_event_rows,
            "comparison_order": self._comparison_order,
            "production_default_plan": deepcopy(self._production_default_plan),
            "production_default_binding": deepcopy(
                self._production_default_binding
            ),
            "canonical_resolution": deepcopy(self._canonical_resolution),
            "canonical_production_authority": deepcopy(
                self._canonical_production_authority
            ),
            "prepared": self._prepared.to_metadata() if self._prepared is not None else None,
            "closed": self._closed,
            "python_event_rows_materialized": False,
            "runtime_performance_claimed": False,
            "application_selected_backend": False,
        }

    def close(self) -> None:
        if self._closed:
            return
        if self._prepared is not None:
            self._prepared.close()
        self._closed = True


def prepared_descriptor_action_consumer(
    *,
    max_event_rows: int,
    validate_against_v2: bool = True,
    collect_phase_trace: bool = True,
    comparison_order: str = "action_then_v2",
    v2_summary=None,
) -> PreparedDescriptorActionConsumer:
    return PreparedDescriptorActionConsumer(
        max_event_rows=max_event_rows,
        validate_against_v2=validate_against_v2,
        collect_phase_trace=collect_phase_trace,
        comparison_order=comparison_order,
        v2_summary=v2_summary,
    )


def run_local_semantic_pair() -> dict[str, object]:
    carrier = carrier_fixture()
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    result = compiled.execute_reference(_events(carrier), {})
    actual = _action_summary(result)
    expected = _v2_summary(carrier)
    comparable_expected = {key: expected[key] for key in actual}
    return {
        "schema": "rtdl.research.action.paper_app_pair.rayjoin.v1",
        "app": "rayjoin",
        "backend": "cpu_action_reference",
        "action_pattern": "keyed_count_and_sum_reductions",
        "semantic_slice": "downstream_binary_descriptor_pair_consumer",
        "actual": actual,
        "expected_v2": expected,
        "matched": actual == comparable_expected,
        "compiled_metadata": compiled.to_metadata(),
        "action_covers_lsi_reprojection_ordering_point_location_or_carrier": False,
        "backend_lowering_available": False,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_compiler_backend_pair() -> dict[str, object]:
    """Run the bounded fixture through the compiler-selected physical route.

    Unlike the historical explicit-Numba diagnostic below, this is the
    application ``execution_mode="compiler"`` surface.  It accepts the
    compiler's legal host fallback and never assumes a backend after planning.
    """

    carrier = carrier_fixture()
    columns = _direct_event_columns(carrier)
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_event_columns(
        compiled,
        columns,
        ordering_fields=("label_a", "label_b", "group_stable_id"),
    )
    target = detect_action_target_profile(
        producer_kind=bound.producer_kind,
        cpu_reference_available=False,
    )
    planned = compile_bound_action_for_target(
        bound,
        target,
        extents={},
        parameters={},
        **_canonical_authority_kwargs(target, "grouped_i64x2_count_sum"),
    )
    prepared = prepare_action_execution(
        planned,
        extents={},
        parameters={},
        max_event_rows=len(columns["group_stable_id"]),
    )
    try:
        query = prepared.execute_columns(columns, extents={}, parameters={})
        reductions = query.payload
        prepared_metadata = prepared.to_metadata()
        query_metadata = query.to_metadata()
    finally:
        prepared.close()

    actual = _reduction_summary(reductions)
    expected = _v2_summary(carrier)
    comparable_expected = {key: expected[key] for key in actual}
    identity = prepared_metadata.get("identity", {})
    selected_backend = identity.get("selected_backend", planned.lowered.backend)
    selected_template = identity.get(
        "selected_template", planned.lowered.template_kind
    )
    return {
        "schema": "rtdl.research.action.paper_app_compiler_pair.rayjoin_downstream.v1",
        "app": "rayjoin",
        "backend": f"compiler_selected_{selected_backend}_{selected_template}",
        "selected_physical_backend": selected_backend,
        "selected_physical_placement": identity.get(
            "selected_placement", planned.lowered.placement
        ),
        "selected_physical_template": selected_template,
        "action_pattern": "keyed_count_and_signed_i64_sum",
        "semantic_slice": "downstream_binary_descriptor_pair_consumer",
        "actual": actual,
        "expected_v2": expected,
        "matched": actual == comparable_expected,
        "planned_metadata": planned.to_metadata(),
        "prepared_metadata": prepared_metadata,
        "result_metadata": query_metadata,
        "action_covers_lsi_reprojection_ordering_point_location_or_carrier": False,
        "backend_lowering_available": True,
        "application_selected_backend": False,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_numba_backend_pair() -> dict[str, object]:
    """Historical explicit-Numba diagnostic; not a compiler-mode front door."""

    carrier = carrier_fixture()
    columns = _direct_event_columns(carrier)
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    bound = bind_action_event_columns(
        compiled,
        columns,
        ordering_fields=("label_a", "label_b", "group_stable_id"),
    )
    lowered = compile_bound_action_for_target(
        bound,
        detect_action_target_profile(cpu_reference_available=False),
        extents={},
        parameters={},
    ).lowered
    prepared = prepare_bound_numba_action_columns(lowered, columns, {})
    result = execute_numba_grouped_i64x2_count_sum(prepared)
    try:
        reductions = result.to_host_reductions()
        result_metadata = result.to_metadata()
    finally:
        result.close()
        prepared.close()
    actual = _reduction_summary(reductions)
    expected = _v2_summary(carrier)
    comparable_expected = {key: expected[key] for key in actual}
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.rayjoin_downstream.v1",
        "app": "rayjoin",
        "backend": "numba_grouped_i64x2_count_sum",
        "action_pattern": "keyed_count_and_signed_i64_sum",
        "semantic_slice": "downstream_binary_descriptor_pair_consumer",
        "actual": actual,
        "expected_v2": expected,
        "matched": actual == comparable_expected,
        "lowering_metadata": lowered.to_metadata(),
        "result_metadata": result_metadata,
        "action_covers_lsi_reprojection_ordering_point_location_or_carrier": False,
        "backend_lowering_available": True,
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "action_contract",
    "carrier_fixture",
    "descriptor_action_consumer",
    "prepared_descriptor_action_consumer",
    "PreparedDescriptorActionConsumer",
    "run_compiler_backend_pair",
    "run_local_semantic_pair",
    "run_numba_backend_pair",
)
