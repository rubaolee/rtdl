from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .prepared_session_residency import PREPARED_SESSION_RESIDENCY_VERSION
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION = (
    "rtdl.v2_12.prepared_resident_query_plan.goal4355.v1"
)
V2_12_PREPARED_RESIDENT_QUERY_PLAN_STATUS = "v2_12_started_perf_work_not_release_authorization"
V2_12_PREPARED_RESIDENT_QUERY_PLAN_CLAIM_BOUNDARY = (
    "The v2.12 prepared-resident query plan records optimization debts and "
    "measurement gates for the next performance campaign. It does not authorize "
    "release action, public speedup wording, broad RT-core wording, whole-app "
    "speedup wording, true-zero-copy wording, paper reproduction claims, hidden "
    "partner/backend selection, or app-specific native-engine dispatch."
)
V2_12_CROSS_APP_BENCHMARK_APP = "_cross_app"
V2_12_REQUIRED_BACKENDS = ("optix", "embree")
V2_12_FORBIDDEN_CLAIM_FLAGS = (
    "ready_to_measure",
    "release_authorized",
    "public_speedup_claim_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_claim_authorized",
    "true_zero_copy_claim_authorized",
    "paper_reproduction_claim_authorized",
    "automatic_partner_selection_authorized",
    "app_specific_native_engine_dispatch_allowed",
)


@dataclass(frozen=True)
class V212PreparedResidentQueryWorkItem:
    row_id: str
    benchmark_app: str
    priority: int
    workload: str
    current_route: str
    target_route: str
    target_native_symbols: tuple[str, ...]
    required_backend_parity: tuple[str, ...]
    fairness_contract: str
    current_gap: str
    optimization_debts: tuple[str, ...]
    first_action: str
    success_gate: str
    evidence_refs: tuple[str, ...]
    partner_policy: str = "partner allowed only behind the same prepared native query contract"
    requires_native_repeat_loop: bool = True
    requires_duration_bounded_timing: bool = True
    requires_cold_hot_phase_split: bool = True
    requires_same_prepared_abi: bool = True
    requires_no_row_materialization: bool = True
    requires_exactness_gate: bool = True
    ready_to_measure: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_dispatch_allowed: bool = False

    def __post_init__(self) -> None:
        if not str(self.row_id).strip():
            raise ValueError("v2.12 work item requires a row_id")
        if self.benchmark_app not in V2_8_PROMOTED_BENCHMARK_APPS + (V2_12_CROSS_APP_BENCHMARK_APP,):
            raise ValueError(f"unknown v2.12 benchmark app: {self.benchmark_app}")
        if int(self.priority) <= 0:
            raise ValueError("v2.12 priority must be positive")
        if not str(self.workload).strip():
            raise ValueError(f"{self.row_id}: workload is required")
        if not str(self.current_route).strip():
            raise ValueError(f"{self.row_id}: current route is required")
        if not str(self.target_route).strip():
            raise ValueError(f"{self.row_id}: target route is required")
        if not self.target_native_symbols:
            raise ValueError(f"{self.row_id}: target native symbols are required")
        if tuple(self.required_backend_parity) != V2_12_REQUIRED_BACKENDS:
            raise ValueError(f"{self.row_id}: required backend parity must be optix, embree")
        if not str(self.fairness_contract).strip():
            raise ValueError(f"{self.row_id}: fairness contract is required")
        if not str(self.current_gap).strip():
            raise ValueError(f"{self.row_id}: current gap is required")
        if not self.optimization_debts:
            raise ValueError(f"{self.row_id}: optimization debts are required")
        if not str(self.first_action).strip():
            raise ValueError(f"{self.row_id}: first action is required")
        if not str(self.success_gate).strip():
            raise ValueError(f"{self.row_id}: success gate is required")
        if not self.evidence_refs:
            raise ValueError(f"{self.row_id}: evidence refs are required")
        for field in (
            "requires_native_repeat_loop",
            "requires_duration_bounded_timing",
            "requires_cold_hot_phase_split",
            "requires_same_prepared_abi",
            "requires_no_row_materialization",
            "requires_exactness_gate",
        ):
            if not getattr(self, field):
                raise ValueError(f"{self.row_id}: {field} must remain true")
        for field in V2_12_FORBIDDEN_CLAIM_FLAGS:
            if getattr(self, field):
                raise ValueError(f"{self.row_id}: {field} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION,
            "status": V2_12_PREPARED_RESIDENT_QUERY_PLAN_STATUS,
            "prepared_session_contract_version": PREPARED_SESSION_RESIDENCY_VERSION,
            "row_id": self.row_id,
            "benchmark_app": self.benchmark_app,
            "priority": int(self.priority),
            "workload": self.workload,
            "current_route": self.current_route,
            "target_route": self.target_route,
            "target_native_symbols": self.target_native_symbols,
            "required_backend_parity": self.required_backend_parity,
            "fairness_contract": self.fairness_contract,
            "current_gap": self.current_gap,
            "optimization_debts": self.optimization_debts,
            "first_action": self.first_action,
            "success_gate": self.success_gate,
            "evidence_refs": self.evidence_refs,
            "partner_policy": self.partner_policy,
            "requires_native_repeat_loop": self.requires_native_repeat_loop,
            "requires_duration_bounded_timing": self.requires_duration_bounded_timing,
            "requires_cold_hot_phase_split": self.requires_cold_hot_phase_split,
            "requires_same_prepared_abi": self.requires_same_prepared_abi,
            "requires_no_row_materialization": self.requires_no_row_materialization,
            "requires_exactness_gate": self.requires_exactness_gate,
            "ready_to_measure": self.ready_to_measure,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_dispatch_allowed": self.app_specific_native_engine_dispatch_allowed,
            "claim_boundary": V2_12_PREPARED_RESIDENT_QUERY_PLAN_CLAIM_BOUNDARY,
        }


V2_12_PREPARED_RESIDENT_QUERY_WORK_ITEMS: tuple[V212PreparedResidentQueryWorkItem, ...] = (
    V212PreparedResidentQueryWorkItem(
        row_id="spatial_rayjoin_pip_exact_native_resident_scalar_count",
        benchmark_app="spatial_rayjoin",
        priority=1,
        workload="pip",
        current_route="prepared_exact_closed_shape_membership_scalar_count",
        target_route="native_prepared_exact_point_in_polygon_scalar_count",
        target_native_symbols=(
            "rtdl_optix_prepared_exact_point_in_polygon_count_2d",
            "rtdl_embree_point_primitive_anyhit_2d_count",
        ),
        required_backend_parity=V2_12_REQUIRED_BACKENDS,
        fairness_contract=(
            "same exported RayJoin query stream, scalar count only, cold prepare outside "
            "the hot loop, no hit-row materialization, and identical exact boundary semantics"
        ),
        current_gap=(
            "Goal4354 measured RayJoin RT PIP query at 0.613610 ms and RTDL OptiX "
            "exact hot query at 7.081935 ms on the same stream, for 0.087x. The "
            "faster relation-status executor is rejected until it matches exact semantics."
        ),
        optimization_debts=(
            "replace Python-fronted exact membership loop with a native prepared resident scalar-count loop",
            "make the OptiX and Embree PIP count paths expose the same prepared-session ABI",
            "time the native loop with duration-bounded repeats in the 1-10s aggregate band",
            "keep the relation-status fast path diagnostic-only until the exactness gate passes",
        ),
        first_action=(
            "implement and benchmark the exact PIP native repeat loop before changing "
            "other RayJoin comparison wording"
        ),
        success_gate=(
            "either RTDL OptiX reaches RayJoin RT same-stream query time for exact PIP, "
            "or the packet reports a phase split that accounts for the full remaining gap"
        ),
        evidence_refs=("Goal4354", "Goal4352", "v2.11 release packet"),
    ),
    V212PreparedResidentQueryWorkItem(
        row_id="spatial_rayjoin_lsi_embree_packet_scalar_count",
        benchmark_app="spatial_rayjoin",
        priority=2,
        workload="lsi",
        current_route="prepared_embree_native_scalar_count",
        target_route="prepared_packet_segment_pair_intersection_scalar_count",
        target_native_symbols=(
            "rtdl_optix_prepared_segment_pair_intersection_count_2d",
            "rtdl_embree_segment_pair_intersections_2d_count",
        ),
        required_backend_parity=V2_12_REQUIRED_BACKENDS,
        fairness_contract=(
            "same segment-pair stream, scalar intersection count only, prepared geometry "
            "retained across repeats, and no intersection-row materialization"
        ),
        current_gap=(
            "Goal4354 measured RTDL OptiX LSI at 0.237690 ms, RayJoin RT at "
            "1.012010 ms, and RTDL Embree LSI at 183730.426896 ms. The OptiX row "
            "is strong, but the Embree packet path is not yet a serious CPU opponent."
        ),
        optimization_debts=(
            "audit Embree packet layout and thread scheduling for 2-D segment-pair counts",
            "remove any remaining scalar-per-query fallback inside the measured native call",
            "record Embree thread-count scaling using the same duration-bounded protocol",
        ),
        first_action="profile the Embree LSI prepared count symbol under 8, 32, and 64 threads",
        success_gate=(
            "Embree LSI must either move into a plausible CPU packet traversal regime or "
            "be labeled with a specific native-kernel bottleneck, not a generic Embree result"
        ),
        evidence_refs=("Goal4354", "Goal4352", "v2.11 release packet"),
    ),
    V212PreparedResidentQueryWorkItem(
        row_id="cross_app_duration_bounded_native_runner",
        benchmark_app=V2_12_CROSS_APP_BENCHMARK_APP,
        priority=3,
        workload="all_benchmark_apps",
        current_route="mixed_repeat_counts_and_process_wrappers",
        target_route="duration_bounded_prepared_native_query_runner",
        target_native_symbols=(
            "rtdl_measure_prepared_native_query_duration_bounded",
            "rtdl_measure_prepared_embree_query_duration_bounded",
        ),
        required_backend_parity=V2_12_REQUIRED_BACKENDS,
        fairness_contract=(
            "identical per-iteration work, backend-specific repeat counts only to reach "
            "stable aggregate wall time, and cold prepare excluded from hot query totals"
        ),
        current_gap=(
            "v2.11 comparison wording already targets 1-10s hot-query aggregates, but "
            "some rows still depend on artifact-specific repeat fields instead of one "
            "shared native runner contract."
        ),
        optimization_debts=(
            "factor the duration-bounded loop into a reusable runner",
            "emit total, median, repeat, warmup, and phase labels with the same keys on both backends",
            "reject rows that only report process-wrapper time",
        ),
        first_action="make the comparison script consume the reusable runner record shape",
        success_gate="every v2.12 comparison row has a native prepared-query timing record in the same schema",
        evidence_refs=("v2.11 release packet", "Goal4354"),
    ),
    V212PreparedResidentQueryWorkItem(
        row_id="cross_app_same_prepared_abi",
        benchmark_app=V2_12_CROSS_APP_BENCHMARK_APP,
        priority=4,
        workload="all_benchmark_apps",
        current_route="backend_specific_prepared_handles",
        target_route="same_prepared_session_abi_for_optix_and_embree",
        target_native_symbols=(
            "rtdl_optix_prepared_query_handle_v1",
            "rtdl_embree_prepared_query_handle_v1",
        ),
        required_backend_parity=V2_12_REQUIRED_BACKENDS,
        fairness_contract=(
            "same input fingerprints, same invalidation semantics, same scalar or row-output "
            "contract, and backend differences limited to traversal hardware/runtime"
        ),
        current_gap=(
            "v2.11 has prepared-session metadata, but the highest-confidence public wording "
            "requires each OptiX row and Embree row to cite the same prepared ABI boundary."
        ),
        optimization_debts=(
            "normalize prepared handle metadata for OptiX and Embree",
            "add stale-artifact guards for mismatched prepared contracts",
            "report partner involvement explicitly instead of inferring it from app names",
        ),
        first_action="add a shared prepared-query metadata record to new OptiX and Embree artifacts",
        success_gate="comparison rows can mechanically assert same prepared ABI before speedup is computed",
        evidence_refs=("Goal3873", "Goal3874", "v2.11 release packet"),
    ),
    V212PreparedResidentQueryWorkItem(
        row_id="cross_app_fused_scalar_reductions",
        benchmark_app=V2_12_CROSS_APP_BENCHMARK_APP,
        priority=5,
        workload="scalar_count_and_summary_rows",
        current_route="native_traversal_plus_partner_or_host_reduction",
        target_route="fused_native_traversal_scalar_reduction",
        target_native_symbols=(
            "rtdl_optix_prepared_traverse_reduce_i64",
            "rtdl_embree_prepared_traverse_reduce_i64",
        ),
        required_backend_parity=V2_12_REQUIRED_BACKENDS,
        fairness_contract=(
            "same predicate, same reduction, same output scalar, no intermediate row stream "
            "unless both backends expose and time that stream"
        ),
        current_gap=(
            "Several benchmark apps are now scalar-count or scalar-summary problems; "
            "separate traversal and continuation stages can dominate when the output is one scalar."
        ),
        optimization_debts=(
            "fuse count/sum reductions into native traversal where the benchmark contract is scalar",
            "keep Numba/CuPy only for continuation work that is identical on both sides",
            "emit phase data proving row materialization is absent from the hot path",
        ),
        first_action="start with scalar-count RayJoin and triangle-counting summaries",
        success_gate="scalar rows report native traversal+reduction timing, not hidden row-stream timing",
        evidence_refs=("v2.11 release packet", "Goal4352"),
    ),
)


def v2_12_prepared_resident_query_plan() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_12_PREPARED_RESIDENT_QUERY_WORK_ITEMS)


def summarize_v2_12_prepared_resident_query_plan(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_12_prepared_resident_query_plan()
    ordered = tuple(sorted(matrix, key=lambda row: (int(row["priority"]), str(row["row_id"]))))
    return {
        "version": V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION,
        "status": V2_12_PREPARED_RESIDENT_QUERY_PLAN_STATUS,
        "row_count": len(matrix),
        "top_priority_row_id": ordered[0]["row_id"] if ordered else None,
        "priority_order": tuple(row["row_id"] for row in ordered),
        "pip_exact_native_resident_first": bool(
            ordered
            and ordered[0]["row_id"] == "spatial_rayjoin_pip_exact_native_resident_scalar_count"
        ),
        "all_require_native_repeat_loop": all(
            bool(row.get("requires_native_repeat_loop")) for row in matrix
        ),
        "all_require_duration_bounded_timing": all(
            bool(row.get("requires_duration_bounded_timing")) for row in matrix
        ),
        "all_require_same_prepared_abi": all(
            bool(row.get("requires_same_prepared_abi")) for row in matrix
        ),
        "all_forbid_row_materialization": all(
            bool(row.get("requires_no_row_materialization")) for row in matrix
        ),
        "required_backends": V2_12_REQUIRED_BACKENDS,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "broad_rt_core_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
        "automatic_partner_selection_authorized": False,
        "claim_boundary": V2_12_PREPARED_RESIDENT_QUERY_PLAN_CLAIM_BOUNDARY,
    }


def validate_v2_12_prepared_resident_query_plan(
    rows: tuple[dict[str, Any], ...] | None = None,
) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_12_prepared_resident_query_plan()
    errors: list[str] = []
    row_ids = [str(row.get("row_id", "")) for row in matrix]
    if not matrix:
        errors.append("v2.12 prepared-resident query plan must not be empty")
    if len(row_ids) != len(set(row_ids)):
        errors.append("v2.12 prepared-resident query row ids must be unique")
    if "spatial_rayjoin_pip_exact_native_resident_scalar_count" not in row_ids:
        errors.append("RayJoin PIP exact native resident row must be present")

    for row in matrix:
        label = str(row.get("row_id", "<missing>"))
        if row.get("version") != V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION:
            errors.append(f"{label}: unexpected plan version")
        if row.get("prepared_session_contract_version") != PREPARED_SESSION_RESIDENCY_VERSION:
            errors.append(f"{label}: unexpected prepared-session contract version")
        if tuple(row.get("required_backend_parity", ())) != V2_12_REQUIRED_BACKENDS:
            errors.append(f"{label}: required backend parity must be optix, embree")
        if not row.get("target_native_symbols"):
            errors.append(f"{label}: missing target native symbols")
        if not row.get("optimization_debts"):
            errors.append(f"{label}: missing optimization debts")
        for field in (
            "requires_native_repeat_loop",
            "requires_duration_bounded_timing",
            "requires_cold_hot_phase_split",
            "requires_same_prepared_abi",
            "requires_no_row_materialization",
            "requires_exactness_gate",
        ):
            if not row.get(field):
                errors.append(f"{label}: {field} must be true")
        for field in V2_12_FORBIDDEN_CLAIM_FLAGS:
            if row.get(field):
                errors.append(f"{label}: {field} must remain false")

    ordered = tuple(sorted(matrix, key=lambda row: (int(row.get("priority", 999)), str(row.get("row_id", "")))))
    if ordered and ordered[0].get("row_id") != "spatial_rayjoin_pip_exact_native_resident_scalar_count":
        errors.append("RayJoin PIP exact row must be the first v2.12 priority")
    pip_rows = [
        row
        for row in matrix
        if row.get("row_id") == "spatial_rayjoin_pip_exact_native_resident_scalar_count"
    ]
    if pip_rows:
        pip_row = pip_rows[0]
        pip_text = " ".join(
            str(pip_row.get(name, ""))
            for name in ("workload", "current_route", "target_route", "current_gap", "success_gate")
        ).lower()
        if "pip" not in pip_text or "exact" not in pip_text:
            errors.append("RayJoin PIP row must preserve exact PIP semantics")
        if "relation-status" not in pip_text:
            errors.append("RayJoin PIP row must record the rejected relation-status fast path")
    return {
        "version": V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "row_count": len(matrix),
        "claim_boundary": V2_12_PREPARED_RESIDENT_QUERY_PLAN_CLAIM_BOUNDARY,
    }


__all__ = [
    "V212PreparedResidentQueryWorkItem",
    "V2_12_CROSS_APP_BENCHMARK_APP",
    "V2_12_FORBIDDEN_CLAIM_FLAGS",
    "V2_12_PREPARED_RESIDENT_QUERY_PLAN_CLAIM_BOUNDARY",
    "V2_12_PREPARED_RESIDENT_QUERY_PLAN_STATUS",
    "V2_12_PREPARED_RESIDENT_QUERY_PLAN_VERSION",
    "V2_12_PREPARED_RESIDENT_QUERY_WORK_ITEMS",
    "V2_12_REQUIRED_BACKENDS",
    "summarize_v2_12_prepared_resident_query_plan",
    "v2_12_prepared_resident_query_plan",
    "validate_v2_12_prepared_resident_query_plan",
]
