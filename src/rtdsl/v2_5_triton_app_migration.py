from __future__ import annotations

from dataclasses import dataclass

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER


V2_5_TRITON_APP_MIGRATION_VERSION = "rtdl.v2_5.triton_app_migration.v1"
V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS = (
    "segmented_count_i64",
    "segmented_sum_f64",
    "segmented_min_f64",
    "segmented_max_f64",
    "compact_mask_i64",
)


@dataclass(frozen=True)
class V25TritonBenchmarkAppPlan:
    app_id: str
    benchmark_name: str
    promoted_benchmark: bool
    current_hot_path_partner: str
    v2_5_required_operations: tuple[str, ...]
    v2_5_status: str
    first_port_action: str
    notes: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "app_id": self.app_id,
            "benchmark_name": self.benchmark_name,
            "promoted_benchmark": self.promoted_benchmark,
            "current_hot_path_partner": self.current_hot_path_partner,
            "v2_5_required_operations": self.v2_5_required_operations,
            "v2_5_status": self.v2_5_status,
            "first_port_action": self.first_port_action,
            "notes": self.notes,
        }


V2_5_TRITON_BENCHMARK_APP_PLANS: tuple[V25TritonBenchmarkAppPlan, ...] = (
    V25TritonBenchmarkAppPlan(
        app_id="raydb_style",
        benchmark_name="RayDB-style grouped aggregates",
        promoted_benchmark=True,
        current_hot_path_partner="triton_adapter_front_door_for_count_sum_min_max",
        v2_5_required_operations=("segmented_count_i64", "segmented_sum_f64", "segmented_min_f64", "segmented_max_f64"),
        v2_5_status="first_adapter_front_door_preview_for_count_sum_min_max",
        first_port_action="Use public partner='triton' grouped reduction adapters for RT hit-stream group/value output.",
        notes="RayDB is the first v2.5 app wired through public Triton adapter front doors; the path remains preview-not-promoted.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="spatial_rayjoin",
        benchmark_name="Spatial RayJoin",
        promoted_benchmark=True,
        current_hot_path_partner="none_native_rtdl_optix_embree",
        v2_5_required_operations=("segmented_count_i64", "compact_mask_i64"),
        v2_5_status="native_rt_hot_path_plus_compact_preview_if_needed",
        first_port_action="Only move optional row post-processing to Triton if it enters benchmark timing; compact has preview coverage.",
        notes="The promoted hot path is native RTDL traversal/query logic, not CuPy/PyTorch continuation.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="librts_spatial_index",
        benchmark_name="LibRTS-style AABB index query",
        promoted_benchmark=True,
        current_hot_path_partner="none_native_rtdl_optix_embree",
        v2_5_required_operations=("segmented_count_i64",),
        v2_5_status="native_rt_hot_path_no_cupy_pytorch_partner",
        first_port_action="Use Triton only for optional grouped summaries outside the native query path.",
        notes="The existing performance path comes from native generic AABB query primitives.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="hausdorff_xhd",
        benchmark_name="Hausdorff/X-HD",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_some_exact_partner_continuations",
        v2_5_required_operations=("grouped_argmin_f64", "segmented_max_f64"),
        v2_5_status="covered_by_grouped_argmin_and_segmented_max_preview_pending_app_wiring",
        first_port_action="Replace legacy CuPy paths with generic Triton grouped argmin plus segmented max, then collect CUDA evidence.",
        notes="Do not add Hausdorff-specific native code; nearest-witness scoring remains generic grouped reduction.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="rt_dbscan",
        benchmark_name="RT-DBSCAN",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_component_continuations",
        v2_5_required_operations=("compact_mask_i64", "bounded_collect_finalize_i64"),
        v2_5_status="covered_by_compact_and_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Replace legacy CuPy component/adjacency continuation with generic Triton compaction and bounded finalize previews.",
        notes="DBSCAN cluster semantics must stay in app code; RTDL owns fixed-radius row generation only.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="rtnn",
        benchmark_name="RTNN neighbor search",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_topk_or_candidate_continuations",
        v2_5_required_operations=("grouped_argmin_f64", "bounded_collect_finalize_i64"),
        v2_5_status="covered_by_grouped_argmin_and_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Use grouped argmin preview where top-1 is enough; use bounded finalize for bounded top-k rows.",
        notes="Approximate-neighbor policy remains app code; primitive behavior is grouped candidate ranking.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="triangle_counting",
        benchmark_name="RT-Graph triangle counting",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_some_graph_continuations",
        v2_5_required_operations=("segmented_count_i64", "compact_mask_i64"),
        v2_5_status="covered_by_count_and_compact_preview_pending_app_wiring",
        first_port_action="Keep RT candidate discovery native and move generic row filtering/count continuation to Triton.",
        notes="Graph semantics stay in the app; Triton should see generic row ids, masks, and segment ids.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="barnes_hut",
        benchmark_name="Barnes-Hut / aggregate frontier",
        promoted_benchmark=True,
        current_hot_path_partner="app_owned_math_with_legacy_partner_force_helpers",
        v2_5_required_operations=("bounded_collect_finalize_i64", "segmented_sum_f64"),
        v2_5_status="blocked_on_generic_frontier_to_triton_reduction",
        first_port_action="Lower aggregate-frontier rows to generic Triton reductions while force math stays app-owned.",
        notes="Never embed inverse-square force law inside the engine or Triton primitive contract.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="robot_collision",
        benchmark_name="Robot collision screening",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_torch_or_cupy_optional_reduction",
        v2_5_required_operations=("compact_mask_i64", "bounded_collect_finalize_i64"),
        v2_5_status="covered_by_compact_and_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Use Triton compact preview for masks; route bounded witness/contact finalization through generic Triton collect/finalize.",
        notes="Collision/contact labels stay app-owned; primitive behavior is bounded witness collection.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="contact_manifold",
        benchmark_name="Bounded contact-manifold witness",
        promoted_benchmark=True,
        current_hot_path_partner="python_reference_or_native_rows",
        v2_5_required_operations=("bounded_collect_finalize_i64",),
        v2_5_status="covered_by_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Wire bounded witness finalize to the generic Triton continuation and collect parity evidence.",
        notes="The engine primitive must say bounded witness collection, not collision or contact.",
    ),
)


def v2_5_triton_benchmark_app_migration_plan() -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "migration_version": V2_5_TRITON_APP_MIGRATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "preview_kernel_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
        "benchmark_app_count": len(V2_5_TRITON_BENCHMARK_APP_PLANS),
        "apps": tuple(plan.to_metadata() for plan in V2_5_TRITON_BENCHMARK_APP_PLANS),
        "claim_boundary": (
            "This is a v2.5 implementation/migration plan. It is not a release "
            "gate, not a public speedup claim, and not authorization to replace "
            "RTDL/OptiX traversal with partner code."
        ),
    }


def validate_v2_5_triton_benchmark_app_migration_plan() -> dict[str, object]:
    plan = v2_5_triton_benchmark_app_migration_plan()
    errors: list[str] = []
    app_ids = [str(app["app_id"]) for app in plan["apps"]]  # type: ignore[index]
    if len(app_ids) != len(set(app_ids)):
        errors.append("duplicate benchmark app id in v2.5 Triton migration plan")
    if plan["primary_partner"] != "triton":
        errors.append("v2.5 benchmark migration must remain Triton-first")
    for app in plan["apps"]:  # type: ignore[assignment]
        if not app["promoted_benchmark"]:
            errors.append(f"{app['app_id']} is not marked as a promoted benchmark")
        status = app["v2_5_status"].lower()
        if "target_cupy" in status or "target_pytorch" in status:
            errors.append(f"{app['app_id']} v2.5 status must not make CuPy/PyTorch the target partner")
        missing_operations = sorted(
            set(app["v2_5_required_operations"]) - set(V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        )
        if missing_operations:
            errors.append(
                f"{app['app_id']} requires operations without Triton previews: {missing_operations}"
            )
    return {
        "status": "accept" if not errors else "reject",
        "benchmark_app_count": plan["benchmark_app_count"],
        "primary_partner": plan["primary_partner"],
        "errors": tuple(errors),
    }


def v2_5_triton_front_door_coverage() -> dict[str, object]:
    """Report which benchmark-app continuations have adapter-level Triton access.

    All required operations may have low-level Triton dispatcher previews, while
    only a subset has public generic partner-adapter front doors. Keeping this
    split explicit avoids claiming that every benchmark app has already been
    rewired to `partner="triton"`.
    """

    adapter_ops = set(V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS)
    dispatcher_ops = set(V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
    rows = []
    fully_front_door_ready = 0
    for app in V2_5_TRITON_BENCHMARK_APP_PLANS:
        required = set(app.v2_5_required_operations)
        adapter_ready = tuple(operation for operation in app.v2_5_required_operations if operation in adapter_ops)
        dispatcher_only = tuple(
            operation
            for operation in app.v2_5_required_operations
            if operation in dispatcher_ops and operation not in adapter_ops
        )
        missing = tuple(operation for operation in app.v2_5_required_operations if operation not in dispatcher_ops)
        status = "adapter_front_door_ready" if required.issubset(adapter_ops) else "dispatcher_ready_app_wiring_required"
        if missing:
            status = "missing_triton_preview_operation"
        if status == "adapter_front_door_ready":
            fully_front_door_ready += 1
        rows.append(
            {
                "app_id": app.app_id,
                "benchmark_name": app.benchmark_name,
                "required_operations": app.v2_5_required_operations,
                "adapter_front_door_operations": adapter_ready,
                "dispatcher_only_operations": dispatcher_only,
                "missing_operations": missing,
                "front_door_status": status,
            }
        )
    return {
        "migration_version": V2_5_TRITON_APP_MIGRATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "adapter_front_door_operations": V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS,
        "dispatcher_preview_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
        "benchmark_app_count": len(rows),
        "fully_front_door_ready_count": fully_front_door_ready,
        "apps": tuple(rows),
        "claim_boundary": (
            "Adapter front-door readiness is local API coverage only. It is not "
            "CUDA pod evidence, benchmark completion, or public performance wording."
        ),
    }
