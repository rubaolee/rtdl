"""App-owned RayDB semantic adapter for the private RTDL 3.0 Action study."""

from __future__ import annotations

from rtdsl.action_api import (
    ActionProducerKind,
    bind_action_producer,
    compile_action_source,
    compile_bound_action_for_target,
    detect_action_target_profile,
)
from rtdsl.action_frontend import RestrictedActionFrontendContract
from rtdsl.action_optix_lowering import all_included_primitive_mask
from rtdsl.action_phase_trace import ActionPhaseTrace, action_phase
from rtdsl.action_ir import (
    BOOL,
    I64,
    U32,
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
from rtdsl.action_prepared import (
    prepare_consumed_triangle_grouped_i64_action_execution,
)
from rtdsl.generic_primitives import checked_partitioned_grouped_i64_add

from raydb_reproduction import (
    ExactListPredicate,
    FlatRow,
    bounded_q21_predicate,
    bounded_q21_rows,
    canonical_grouped_sum_rows,
    lower_rows_to_generic_rt,
)

# Preserve the historical app patch point while routing all RayDB payloads
# through the compiler-owned consumed-resource preparation contract.
prepare_action_execution = prepare_consumed_triangle_grouped_i64_action_execution


CANONICAL_ALGORITHM_BINDINGS = {
    "partitioned_triangle_grouped_i64_sum": (
        "ray_triangle.keyed_i64_sum.v1",
        "nvidia.optix_traversal.v1",
    ),
}
FORMAL_PAPER_ALGORITHMS = ("partitioned_triangle_grouped_i64_sum",)


def _canonical_authority_kwargs(target, algorithm: str) -> dict[str, str]:
    if target.production_selection_policy != "compiler_owned_default":
        return {}
    statement, backend = CANONICAL_ALGORITHM_BINDINGS[algorithm]
    return {
        "semantic_statement_stable_id": statement,
        "backend_contract_id": backend,
    }


ACTION_SOURCE = """
def action(event, params):
    include = event.include
    require(include)
    value = event.value
    reduce("sum_by_query", value)
"""


def action_contract() -> RestrictedActionFrontendContract:
    event_type = ActionRecordType(
        "relation_event",
        (
            ActionField("primitive_stable_id", U64),
            ActionField("query_id", U32),
            ActionField("include", BOOL),
            ActionField("value", I64),
        ),
    )
    reduction = ActionReductionSpec(
        "sum_by_query",
        ("query_id",),
        I64,
        ReductionOperator.SUM,
        ActionScalarLiteral.from_python(I64, 0),
    )
    return RestrictedActionFrontendContract(
        event_type=event_type,
        parameter_type=ActionRecordType("parameters", ()),
        logical_event=LogicalEventContract(
            key_fields=("primitive_stable_id", "query_id"),
            physical_delivery=PhysicalDelivery.MAY_REPEAT,
            enforcement=DeliveryEnforcement.KEYED_DEDUP,
        ),
        reductions=(reduction,),
    )


def events_from_rows(
    rows: tuple[FlatRow, ...],
    predicate: ExactListPredicate,
    *,
    duplicate_first_included: bool = False,
) -> tuple[dict[str, object], ...]:
    groups = tuple(sorted({row.group_values for row in rows}))
    group_ids = {group: index for index, group in enumerate(groups)}
    events = [
        {
            "primitive_stable_id": primitive_id,
            "query_id": group_ids[row.group_values],
            "include": predicate.accepts(row.scan_values),
            "value": row.aggregate_value,
        }
        for primitive_id, row in enumerate(rows)
    ]
    if duplicate_first_included:
        first_included = next(event for event in events if event["include"])
        events.insert(1, dict(first_included))
    return tuple(events)


def fixture_events() -> tuple[dict[str, object], ...]:
    return events_from_rows(
        bounded_q21_rows(),
        bounded_q21_predicate(),
        duplicate_first_included=True,
    )


def run_reference_rows(
    rows: tuple[FlatRow, ...], predicate: ExactListPredicate
) -> dict[str, object]:
    rows = tuple(rows)
    groups = tuple(sorted({row.group_values for row in rows}))
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    events = events_from_rows(rows, predicate)
    result = compiled.execute_reference(events, {})
    actual = [
        {"group": list(groups[int(key[0])]), "value": int(value)}
        for key, value in result.reductions[0].rows
        if int(value) != 0
    ]
    actual.sort(key=lambda row: tuple(row["group"]))
    expected = canonical_grouped_sum_rows(rows, predicate)
    return {
        "backend": "action_cpu_reference",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "logical_input_row_count": len(rows),
        "compiled_metadata": compiled.to_metadata(),
    }


class PreparedRaydbGroupedSumSession:
    """App-owned projection around one compiler-owned prepared Action session."""

    def __init__(
        self,
        prepared,
        planned,
        workload,
        *,
        phase_trace=None,
        partition_index: int | None = None,
    ) -> None:
        self._prepared = prepared
        self._planned = planned
        self._workload = workload
        self._phase_trace = phase_trace
        self._partition_label = (
            "unpartitioned"
            if partition_index is None
            else f"partition_{int(partition_index)}"
        )

    @property
    def default_rays(self):
        return self._workload["rays"]

    @property
    def query_count(self) -> int:
        return self._prepared.query_count

    def execute_rays(self, rays) -> dict[str, object]:
        ordinal = self._prepared.query_count
        with action_phase(
            self._phase_trace,
            "execute",
            label=f"prepared_ray_grouped_sum_batch_{ordinal}",
        ):
            query_result = self._prepared.execute_queries(
                rays,
                extents={},
                parameters={},
            )
        if self._phase_trace is not None:
            suffix = f"batch_{ordinal}"
            self._phase_trace.fold_device_operation(
                name=f"ray_rows_upload_{suffix}",
                kind="host_to_device_transfer",
                folded_into="execute",
                reason="prepared Action query owns ray upload without an independent timer",
            )
            self._phase_trace.fold_device_operation(
                name=f"grouped_sum_rows_download_{suffix}",
                kind="device_to_host_transfer",
                folded_into="execute",
                reason="prepared Action query returns host grouped rows without an independent timer",
            )
            self._phase_trace.fold_device_operation(
                name=f"grouped_sum_ready_wait_{suffix}",
                kind="device_synchronization_wait",
                folded_into="execute",
                reason="prepared Action query synchronizes before exposing grouped rows",
            )
        return self._project_query_result(query_result, ordinal)

    def prepare_rays(self, rays):
        with action_phase(
            self._phase_trace,
            "event_producer",
            label="prepare_shared_ray_batch_once",
        ):
            prepared_rays = self._prepared.prepare_query_batch(
                rays,
                extents={},
                parameters={},
            )
        if self._phase_trace is not None:
            self._phase_trace.fold_device_operation(
                name="shared_ray_batch_upload",
                kind="host_to_device_transfer",
                folded_into="event_producer",
                reason="prepared Action query batch owns the one-time ray upload",
            )
        return prepared_rays

    def execute_prepared_rays(self, prepared_rays) -> dict[str, object]:
        ordinal = self._prepared.query_count
        with action_phase(
            self._phase_trace,
            "execute",
            label=(
                f"prepared_resident_ray_grouped_sum_{self._partition_label}_batch_{ordinal}"
            ),
        ):
            query_result = self._prepared.execute_prepared_query_batch(
                prepared_rays,
                extents={},
                parameters={},
            )
        if self._phase_trace is not None:
            suffix = f"{self._partition_label}_batch_{ordinal}"
            self._phase_trace.fold_device_operation(
                name=f"grouped_sum_rows_download_{suffix}",
                kind="device_to_host_transfer",
                folded_into="execute",
                reason="prepared Action query returns host grouped rows without an independent timer",
            )
            self._phase_trace.fold_device_operation(
                name=f"grouped_sum_ready_wait_{suffix}",
                kind="device_synchronization_wait",
                folded_into="execute",
                reason="prepared Action query synchronizes before exposing grouped rows",
            )
        return self._project_query_result(query_result, ordinal)

    def _project_query_result(self, query_result, ordinal: int) -> dict[str, object]:
        payload = query_result.payload
        with action_phase(
            self._phase_trace,
            "projection",
            label=f"group_ids_to_group_tuples_{self._partition_label}_batch_{ordinal}",
        ):
            groups = self._workload["group_tuples"]
            rows = [
                {
                    "group": [int(item) for item in groups[int(group_id)]],
                    "value": int(value),
                }
                for group_id, value in payload["rows"]
                if int(value) != 0
            ]
            rows.sort(key=lambda row: tuple(row["group"]))
        return {
            "actual_rows": rows,
            "runtime_metadata": payload["metadata"],
            "query_metadata": query_result.to_metadata(),
        }

    def close(self) -> None:
        with action_phase(
            self._phase_trace,
            "backend_prepare",
            label=f"release_prepared_triangle_grouped_sum_{self._partition_label}",
        ):
            self._prepared.close()

    def to_metadata(self) -> dict[str, object]:
        return {
            "prepared_action": self._prepared.to_metadata(),
            "lowering": self._planned.lowered.to_metadata(),
            "application_selected_backend": False,
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


class PartitionedRaydbGroupedSumPlan:
    """One compiler-owned Action plan applied to bounded primitive partitions."""

    def __init__(self, planned, group_tuples, rays, *, phase_trace=None) -> None:
        self._planned = planned
        self._group_tuples = tuple(tuple(int(item) for item in row) for row in group_tuples)
        self._rays = rays
        self._phase_trace = phase_trace
        self._prepared_partition_count = 0
        self._closed = False

    def execute_partitions(
        self,
        partitions,
        *,
        expected_primitive_count: int,
    ) -> dict[str, object]:
        if self._closed:
            raise RuntimeError("partitioned RayDB Action plan is closed")
        if (
            not isinstance(expected_primitive_count, int)
            or isinstance(expected_primitive_count, bool)
            or expected_primitive_count < 0
        ):
            raise ValueError("expected_primitive_count must be nonnegative")
        merged: dict[tuple[int, ...], int] = {}
        ledger = []
        next_primitive_id = 0
        prepared_rays = None
        try:
            for partition_index, raw_partition in enumerate(partitions):
                partition = dict(raw_partition)
                primitive_id_start = int(partition["primitive_id_start"])
                if primitive_id_start != next_primitive_id:
                    raise ValueError(
                        "partition primitive ranges must be contiguous and start at zero"
                    )
                group_ids = partition["primitive_group_ids"]
                values = partition["primitive_values"]
                primitive_count = len(group_ids)
                if len(values) != primitive_count:
                    raise ValueError("partition group/value lengths differ")
                includes = partition.get("primitive_includes")
                if includes is None:
                    includes = all_included_primitive_mask(primitive_count)
                if len(includes) != primitive_count:
                    raise ValueError("partition include length differs")
                with action_phase(
                    self._phase_trace,
                    "backend_prepare",
                    label=f"prepare_triangle_grouped_sum_partition_{partition_index}",
                ):
                    prepared = prepare_action_execution(
                        self._planned,
                        triangles=partition["triangles"],
                        primitive_group_ids=group_ids,
                        primitive_values=values,
                        primitive_includes=includes,
                        group_count=len(self._group_tuples),
                        extents={},
                        parameters={},
                    )
                self._prepared_partition_count += 1
                session = PreparedRaydbGroupedSumSession(
                    prepared,
                    self._planned,
                    {"group_tuples": self._group_tuples, "rays": self._rays},
                    phase_trace=self._phase_trace,
                    partition_index=partition_index,
                )
                try:
                    if prepared_rays is None:
                        prepared_rays = session.prepare_rays(self._rays)
                    batch = session.execute_prepared_rays(prepared_rays)
                finally:
                    session.close()
                prepared_metadata = session.to_metadata()["prepared_action"]
                for row in batch["actual_rows"]:
                    key = tuple(int(item) for item in row["group"])
                    merged[key] = checked_partitioned_grouped_i64_add(
                        merged.get(key, 0),
                        int(row["value"]),
                        field="sum",
                    )
                next_primitive_id += primitive_count
                ledger.append(
                    {
                        "partition_index": partition_index,
                        "primitive_id_start": primitive_id_start,
                        "primitive_count": primitive_count,
                        "primitive_id_stop_exclusive": next_primitive_id,
                        "query_ordinal": int(batch["query_metadata"]["query_ordinal"]),
                        "prepared_identity_digest": prepared_metadata["identity"][
                            "identity_digest"
                        ],
                        "prepared_action_metadata": prepared_metadata,
                        "runtime_metadata": batch["runtime_metadata"],
                    }
                )
        finally:
            if prepared_rays is not None:
                prepared_rays.close()
        if next_primitive_id != expected_primitive_count:
            raise ValueError(
                "partition primitive coverage differs from expected_primitive_count"
            )
        rows = [
            {"group": list(key), "value": int(value)}
            for key, value in sorted(merged.items())
            if int(value) != 0
        ]
        return {
            "actual_rows": rows,
            "partition_count": len(ledger),
            "expected_primitive_count": expected_primitive_count,
            "prepared_partition_count": self._prepared_partition_count,
            "partition_ledger": ledger,
            "compiler_plan_reused_across_partitions": True,
            "prepared_ray_batch_reused_across_partitions": bool(len(ledger) > 0),
            "prepared_ray_batch_execution_count": (
                int(prepared_rays.execution_count) if prepared_rays is not None else 0
            ),
            "prepared_ray_batch_metadata": (
                prepared_rays.to_metadata() if prepared_rays is not None else None
            ),
            "application_selected_backend": False,
        }

    def to_metadata(self) -> dict[str, object]:
        return {
            "lowering": self._planned.lowered.to_metadata(),
            "prepared_partition_count": self._prepared_partition_count,
            "compiler_plan_count": 1,
            "application_selected_backend": False,
            "closed": self._closed,
        }

    def close(self) -> None:
        self._closed = True

    def __enter__(self):
        if self._closed:
            raise RuntimeError("partitioned RayDB Action plan is closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def prepare_partitioned_compiler_plan(
    *,
    group_tuples,
    rays,
    phase_trace=None,
) -> PartitionedRaydbGroupedSumPlan:
    if len(group_tuples) <= 0:
        raise ValueError("at least one grouped-reduction key is required")
    with action_phase(
        phase_trace, "action_compile_or_cache_hit", label="compile_action_source_once"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(
        phase_trace, "binding_certificate", label="bind_stable_triangle_producer_once"
    ):
        bound = bind_action_producer(
            compiled, ActionProducerKind.STABLE_RAY_TRIANGLE_CANDIDATES_3D
        )
    with action_phase(
        phase_trace, "physical_plan", label="target_probe_plan_and_lower_once"
    ):
        target = detect_action_target_profile(cpu_reference_available=False)
        planned = compile_bound_action_for_target(
            bound,
            target,
            extents={},
            parameters={},
            **_canonical_authority_kwargs(
                target, "partitioned_triangle_grouped_i64_sum"
            ),
        )
    return PartitionedRaydbGroupedSumPlan(
        planned,
        group_tuples,
        rays,
        phase_trace=phase_trace,
    )


def prepare_compiler_rows(
    rows: tuple[FlatRow, ...],
    predicate: ExactListPredicate,
    *,
    phase_trace=None,
) -> PreparedRaydbGroupedSumSession:
    with action_phase(phase_trace, "input_adapter", label="freeze_flat_rows"):
        rows = tuple(rows)
    with action_phase(phase_trace, "event_producer", label="rows_to_generic_rt_workload"):
        workload = lower_rows_to_generic_rt(rows, predicate)
        includes = tuple(predicate.accepts(row.scan_values) for row in rows)
    return prepare_compiler_payload(
        triangles=workload["triangles"],
        primitive_group_ids=workload["primitive_group_ids"],
        primitive_values=workload["primitive_values"],
        primitive_includes=includes,
        group_tuples=workload["group_tuples"],
        rays=workload["rays"],
        phase_trace=phase_trace,
    )


def prepare_compiler_payload(
    *,
    triangles,
    primitive_group_ids,
    primitive_values,
    primitive_includes,
    group_tuples,
    rays,
    phase_trace=None,
) -> PreparedRaydbGroupedSumSession:
    """Bind columnar primitive payloads without materializing app row objects."""

    if len(group_tuples) <= 0:
        raise ValueError("at least one grouped-reduction key is required")
    workload = {
        "group_tuples": group_tuples,
        "rays": rays,
    }
    with action_phase(
        phase_trace, "action_compile_or_cache_hit", label="compile_action_source"
    ):
        compiled = compile_action_source(ACTION_SOURCE, action_contract())
    with action_phase(
        phase_trace, "binding_certificate", label="bind_stable_triangle_producer"
    ):
        bound = bind_action_producer(
            compiled, ActionProducerKind.STABLE_RAY_TRIANGLE_CANDIDATES_3D
        )
    with action_phase(phase_trace, "physical_plan", label="target_probe_plan_and_lower"):
        target = detect_action_target_profile(cpu_reference_available=False)
        planned = compile_bound_action_for_target(
            bound,
            target,
            extents={},
            parameters={},
            **_canonical_authority_kwargs(
                target, "partitioned_triangle_grouped_i64_sum"
            ),
        )
    with action_phase(
        phase_trace, "backend_prepare", label="prepare_triangle_grouped_sum"
    ):
        prepared = prepare_action_execution(
            planned,
            triangles=triangles,
            primitive_group_ids=primitive_group_ids,
            primitive_values=primitive_values,
            primitive_includes=primitive_includes,
            group_count=len(group_tuples),
            extents={},
            parameters={},
        )
    if phase_trace is not None:
        phase_trace.fold_device_operation(
            name="triangle_payload_upload",
            kind="host_to_device_transfer",
            folded_into="backend_prepare",
            reason="prepared Action construction owns triangle and payload upload without an independent timer",
        )
    return PreparedRaydbGroupedSumSession(
        prepared,
        planned,
        workload,
        phase_trace=phase_trace,
    )


def run_optix_rows(
    rows: tuple[FlatRow, ...],
    predicate: ExactListPredicate,
    *,
    collect_phase_trace: bool = False,
) -> dict[str, object]:
    trace = (
        ActionPhaseTrace(app="raydb", route="stable_triangle_grouped_i64_sum")
        if collect_phase_trace
        else None
    )
    session = prepare_compiler_rows(rows, predicate, phase_trace=trace)
    try:
        batch = session.execute_rays(session.default_rays)
    finally:
        session.close()
    actual = batch["actual_rows"]
    with action_phase(trace, "app_validation", label="canonical_grouped_sum_comparator"):
        expected = canonical_grouped_sum_rows(rows, predicate)
    phase_trace = trace.finish() if trace is not None else None
    return {
        "backend": "action_optix",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "logical_input_row_count": len(rows),
        "lowering_metadata": session.to_metadata()["lowering"],
        "runtime_metadata": batch["runtime_metadata"],
        "prepared_execution_metadata": session.to_metadata()["prepared_action"],
        "prepared_query_metadata": batch["query_metadata"],
        "phase_trace": phase_trace,
    }


def run_local_semantic_pair() -> dict[str, object]:
    rows = bounded_q21_rows()
    groups = tuple(sorted({row.group_values for row in rows}))
    compiled = compile_action_source(ACTION_SOURCE, action_contract())
    result = compiled.execute_reference(fixture_events(), {})
    actual = [
        {"group": list(groups[int(key[0])]), "value": int(value)}
        for key, value in result.reductions[0].rows
        if int(value) != 0
    ]
    actual.sort(key=lambda row: tuple(row["group"]))
    expected = canonical_grouped_sum_rows(rows, bounded_q21_predicate())
    return {
        "schema": "rtdl.research.action.paper_app_pair.raydb.v1",
        "app": "raydb",
        "cohort": "cohort_2_seven_app_paired_migration",
        "v2_semantic_baseline": "goal5552_bounded_q21_and_goal5567_strongest_route",
        "action_pattern": "filter_keyed_i64_reduction",
        "physical_event_count": len(fixture_events()),
        "logical_input_row_count": len(rows),
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "compiled_metadata": compiled.to_metadata(),
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


def run_optix_semantic_pair() -> dict[str, object]:
    rows = bounded_q21_rows()
    predicate = bounded_q21_predicate()
    session = prepare_compiler_rows(rows, predicate)
    try:
        batch = session.execute_rays(session.default_rays)
    finally:
        session.close()
    actual = batch["actual_rows"]
    expected = canonical_grouped_sum_rows(rows, predicate)
    session_metadata = session.to_metadata()
    return {
        "schema": "rtdl.research.action.paper_app_backend_pair.raydb.v1",
        "app": "raydb",
        "backend": "optix",
        "action_pattern": "filter_keyed_i64_reduction",
        "actual_rows": actual,
        "expected_rows": expected,
        "matched": actual == expected,
        "lowering_metadata": session_metadata["lowering"],
        "runtime_metadata": batch["runtime_metadata"],
        "prepared_execution_metadata": session_metadata["prepared_action"],
        "prepared_query_metadata": batch["query_metadata"],
        "runtime_performance_claimed": False,
        "strongest_route_runtime_pair_complete": False,
    }


__all__ = (
    "CANONICAL_ALGORITHM_BINDINGS",
    "FORMAL_PAPER_ALGORITHMS",
    "action_contract",
    "events_from_rows",
    "fixture_events",
    "prepare_compiler_payload",
    "prepare_partitioned_compiler_plan",
    "prepare_compiler_rows",
    "PartitionedRaydbGroupedSumPlan",
    "PreparedRaydbGroupedSumSession",
    "run_local_semantic_pair",
    "run_optix_semantic_pair",
    "run_optix_rows",
    "run_reference_rows",
)
