from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .current_benchmark_route_decisions import current_benchmark_route_decisions
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION = (
    "rtdl.v3_0.benchmark_implementation_queue.goal4524.v1"
)
V3_BENCHMARK_IMPLEMENTATION_QUEUE_STATUS = (
    "post_clean_target_runtime_build_queue_not_release_authorization"
)
V3_BENCHMARK_IMPLEMENTATION_QUEUE_CLAIM_BOUNDARY = (
    "This queue ranks post-clean-target implementation work after Goal4515 "
    "and Goal4523. It does not change any current benchmark app route and does "
    "not authorize public speedup, broad RT-core, paper-reproduction, automatic "
    "partner-selection, or app-specific native-engine wording."
)

V3_IMPLEMENTATION_WORK_CLASSES = (
    "runtime_blocker",
    "claim_or_evidence_blocker",
    "closed_current_target",
)


@dataclass(frozen=True)
class V3BenchmarkImplementationQueueRow:
    app: str
    priority: int | None
    work_class: str
    current_route_status: str
    remaining_gap: str
    next_build_target: str
    evidence_refs: tuple[str, ...]
    pod_needed_next: bool
    clean_target_closed: bool = True
    current_route_changed: bool = False
    public_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown benchmark app: {self.app}")
        if self.work_class not in V3_IMPLEMENTATION_WORK_CLASSES:
            raise ValueError(f"{self.app}: unknown work class {self.work_class!r}")
        if not self.evidence_refs:
            raise ValueError(f"{self.app}: evidence refs must not be empty")
        if self.work_class == "runtime_blocker":
            if self.priority is None or self.priority <= 0:
                raise ValueError(f"{self.app}: runtime blockers require a positive priority")
            if not self.pod_needed_next:
                raise ValueError(f"{self.app}: runtime blockers require pod validation")
        elif self.priority is not None and self.priority <= 0:
            raise ValueError(f"{self.app}: priority must be positive when present")
        for field in (
            "current_route_status",
            "remaining_gap",
            "next_build_target",
        ):
            value = getattr(self, field)
            if not value or value.strip().lower() == "n/a":
                raise ValueError(f"{self.app}: {field} must be explicit")
        for flag in (
            "current_route_changed",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.app}: {flag} must remain false")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION,
            "app": self.app,
            "priority": self.priority,
            "work_class": self.work_class,
            "current_route_status": self.current_route_status,
            "remaining_gap": self.remaining_gap,
            "next_build_target": self.next_build_target,
            "evidence_refs": self.evidence_refs,
            "pod_needed_next": self.pod_needed_next,
            "clean_target_closed": self.clean_target_closed,
            "current_route_changed": self.current_route_changed,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "app_specific_native_engine_logic_allowed": (
                self.app_specific_native_engine_logic_allowed
            ),
        }


_ROWS: tuple[V3BenchmarkImplementationQueueRow, ...] = (
    V3BenchmarkImplementationQueueRow(
        app="barnes_hut",
        priority=1,
        work_class="runtime_blocker",
        current_route_status=(
            "current V3 route is mixed explicit: CPU/Numba or Numba CUDA fused "
            "force summary by scale; prepared RTDL/OptiX remains device-column "
            "evidence, not Barnes-Hut RT-core traversal evidence"
        ),
        remaining_gap=(
            "AGGREGATE_TREE_FUSED_WEIGHTED_VECTOR_SUM_2D_RT_NATIVE has a generic "
            "contract and Python wrapper surface, but native prepare/run/destroy "
            "symbols, OptiX traversal proof, equivalence oracle, and timing split "
            "are still missing"
        ),
        next_build_target=(
            "implement app-agnostic aggregate-tree fused weighted-vector RT-native "
            "C++/OptiX ABI, then validate optixLaunch/"
            "optixTrace traversal against CPU/Numba force-summary references"
        ),
        evidence_refs=("Goal4497", "Goal4517", "Goal4518", "Goal4523", "Goal4525"),
        pod_needed_next=True,
    ),
    V3BenchmarkImplementationQueueRow(
        app="rt_dbscan",
        priority=2,
        work_class="runtime_blocker",
        current_route_status=(
            "current V3 route is predicate direct-status component signature with "
            "caller-owned CuPy point columns when the app can provide them"
        ),
        remaining_gap=(
            "chunk-local prepared direct-status handles are live-smoke validated, "
            "but prepared graph capture/replay for the chunked continuation is not"
        ),
        next_build_target=(
            "add a generic prepared graph capture/replay path for chunk-local "
            "direct-status handles and same-stream partner continuation, preserving "
            "no-hidden-upload and no pair-row materialization gates"
        ),
        evidence_refs=("Goal4509", "Goal4510", "Goal4516", "Goal4519", "Goal4520"),
        pod_needed_next=True,
    ),
    V3BenchmarkImplementationQueueRow(
        app="triangle_counting",
        priority=3,
        work_class="runtime_blocker",
        current_route_status=(
            "current V3 route is explicit numba_direct_sort_rle prepared segment "
            "replay after primitive evidence; it completes the large paper rows "
            "but remains an internal route"
        ),
        remaining_gap=(
            "scalar per-chunk unique counts are not associative when duplicate keys "
            "cross chunk boundaries; an M113-safe path needs key/count payload merge "
            "or proven disjoint key ranges plus graph capture"
        ),
        next_build_target=(
            "build a generic chunked key/count payload merge primitive or "
            "disjoint-key-range plan, then validate a coarser prepared continuation "
            "with fewer per-segment launches"
        ),
        evidence_refs=("Goal4479", "Goal4511", "Goal4521"),
        pod_needed_next=True,
    ),
    V3BenchmarkImplementationQueueRow(
        app="rtnn",
        priority=10,
        work_class="claim_or_evidence_blocker",
        current_route_status=(
            "current V3 route supports exact aggregate full-batch RTDL rows and "
            "large chunked CuPy/Numba partner-continuation rows"
        ),
        remaining_gap=(
            "public paper-reproduction and same-output author claims remain blocked "
            "by dataset recipes and output-contract differences, not by a missing "
            "current RTDL primitive"
        ),
        next_build_target=(
            "freeze exact paper-family dataset recipes and author output contract "
            "comparisons before any public RTNN wording expansion"
        ),
        evidence_refs=("Goal4498", "Goal4500", "Goal4501", "Goal4507", "Goal4508"),
        pod_needed_next=True,
    ),
    V3BenchmarkImplementationQueueRow(
        app="spatial_rayjoin",
        priority=11,
        work_class="claim_or_evidence_blocker",
        current_route_status=(
            "current V3 route is mixed explicit: Numba for bounded one-shot PIP, "
            "prepared RTDL/OptiX for repeated PIP, and RTDL/OptiX scalar or active "
            "count primitives for LSI/overlay-style contracts"
        ),
        remaining_gap=(
            "full RayJoin paper-reproduction wording and Section 5.7 8/8 overlay "
            "wording remain claim-scoped; the current limitation is not a missing "
            "generic primitive for the already scoped 2/8 overlay evidence"
        ),
        next_build_target=(
            "keep the current mixed route; only expand public wording with an "
            "explicitly scoped author/data packet that states which overlay rows "
            "are feasible and which are not"
        ),
        evidence_refs=("Goal4451", "Goal4514"),
        pod_needed_next=True,
    ),
    V3BenchmarkImplementationQueueRow(
        app="hausdorff_xhd",
        priority=None,
        work_class="closed_current_target",
        current_route_status="closed as primitive-first exact nearest-witness/grouped-max route",
        remaining_gap="no current V3 runtime blocker after Goal4513 clean-target audit",
        next_build_target="no immediate V3 build target; preserve scoped claim boundary",
        evidence_refs=("Goal4513",),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="robot_collision",
        priority=None,
        work_class="closed_current_target",
        current_route_status="closed as no-partner prepared grouped-segment any-hit route",
        remaining_gap="no current V3 runtime blocker after Goal4513 clean-target audit",
        next_build_target="no immediate V3 build target; preserve scoped claim boundary",
        evidence_refs=("Goal4446", "Goal4513"),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="contact_manifold",
        priority=None,
        work_class="closed_current_target",
        current_route_status="closed as no-partner bounded witness collect route",
        remaining_gap="no current V3 runtime blocker after Goal4513 clean-target audit",
        next_build_target="no immediate V3 build target; preserve scoped claim boundary",
        evidence_refs=("Goal4513",),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="raydb_style",
        priority=None,
        work_class="closed_current_target",
        current_route_status="closed as primitive-first fused grouped-reduction route",
        remaining_gap="no current V3 runtime blocker after Goal4513 clean-target audit",
        next_build_target="no immediate V3 build target; preserve scoped claim boundary",
        evidence_refs=("Goal4513",),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="librts_spatial_index",
        priority=None,
        work_class="closed_current_target",
        current_route_status="closed as no-partner prepared AABB index query slice",
        remaining_gap="no current V3 runtime blocker after Goal4513 clean-target audit",
        next_build_target="no immediate V3 build target; preserve scoped claim boundary",
        evidence_refs=("Goal4513",),
        pod_needed_next=False,
    ),
)


def v3_benchmark_implementation_queue_rows() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in _ROWS)


def v3_benchmark_implementation_queue() -> dict[str, Any]:
    rows = v3_benchmark_implementation_queue_rows()
    runtime_rows = sorted(
        (row for row in rows if row["work_class"] == "runtime_blocker"),
        key=lambda row: int(row["priority"]),
    )
    claim_rows = sorted(
        (row for row in rows if row["work_class"] == "claim_or_evidence_blocker"),
        key=lambda row: int(row["priority"]),
    )
    closed_rows = tuple(row for row in rows if row["work_class"] == "closed_current_target")
    return {
        "version": V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION,
        "status": V3_BENCHMARK_IMPLEMENTATION_QUEUE_STATUS,
        "claim_boundary": V3_BENCHMARK_IMPLEMENTATION_QUEUE_CLAIM_BOUNDARY,
        "rows": rows,
        "summary": {
            "app_count": len(rows),
            "all_ten_benchmark_apps_accounted_for": (
                {row["app"] for row in rows} == set(V2_8_PROMOTED_BENCHMARK_APPS)
            ),
            "runtime_build_queue": tuple(row["app"] for row in runtime_rows),
            "claim_or_evidence_queue": tuple(row["app"] for row in claim_rows),
            "closed_current_targets": tuple(row["app"] for row in closed_rows),
            "next_runtime_build_target": runtime_rows[0]["app"] if runtime_rows else None,
            "all_clean_targets_closed": all(row["clean_target_closed"] for row in rows),
            "all_public_speedup_claims_blocked": all(
                not row["public_speedup_claim_authorized"] for row in rows
            ),
            "all_broad_rt_core_claims_blocked": all(
                not row["broad_rt_core_claim_authorized"] for row in rows
            ),
            "all_paper_reproduction_claims_blocked": all(
                not row["paper_reproduction_claim_authorized"] for row in rows
            ),
            "all_automatic_partner_selection_blocked": all(
                not row["automatic_partner_selection_authorized"] for row in rows
            ),
            "all_app_specific_native_engine_logic_blocked": all(
                not row["app_specific_native_engine_logic_allowed"] for row in rows
            ),
            "runtime_targets_need_pod": all(row["pod_needed_next"] for row in runtime_rows),
        },
    }


def validate_v3_benchmark_implementation_queue(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if packet is None:
        packet = v3_benchmark_implementation_queue()
    rows = tuple(packet["rows"])
    apps = {row["app"] for row in rows}
    route_apps = {row["app"] for row in current_benchmark_route_decisions()}
    runtime_apps = tuple(
        row["app"]
        for row in sorted(
            (row for row in rows if row["work_class"] == "runtime_blocker"),
            key=lambda row: int(row["priority"]),
        )
    )
    checks = {
        "version_current": packet["version"] == V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION,
        "all_promoted_apps_present": apps == set(V2_8_PROMOTED_BENCHMARK_APPS),
        "all_route_apps_present": apps == route_apps,
        "runtime_queue_exact": runtime_apps
        == ("barnes_hut", "rt_dbscan", "triangle_counting"),
        "next_runtime_target_barnes_hut": (
            packet["summary"]["next_runtime_build_target"] == "barnes_hut"
        ),
        "claim_queue_exact": tuple(packet["summary"]["claim_or_evidence_queue"])
        == ("rtnn", "spatial_rayjoin"),
        "closed_count_is_five": len(packet["summary"]["closed_current_targets"]) == 5,
        "all_clean_targets_closed": bool(packet["summary"]["all_clean_targets_closed"]),
        "all_public_speedup_claims_blocked": bool(
            packet["summary"]["all_public_speedup_claims_blocked"]
        ),
        "all_broad_rt_core_claims_blocked": bool(
            packet["summary"]["all_broad_rt_core_claims_blocked"]
        ),
        "all_paper_reproduction_claims_blocked": bool(
            packet["summary"]["all_paper_reproduction_claims_blocked"]
        ),
        "runtime_targets_need_pod": bool(packet["summary"]["runtime_targets_need_pod"]),
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION,
        "status": "accept" if not failed else "reject",
        "checks": checks,
        "failed_checks": failed,
    }
