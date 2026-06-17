from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .current_benchmark_route_decisions import current_benchmark_route_decisions
from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION = (
    "rtdl.v3_0.benchmark_implementation_queue.goal4541.v9"
)
V3_BENCHMARK_IMPLEMENTATION_QUEUE_STATUS = (
    "all_current_benchmark_apps_closed_future_rt_native_research_not_release_authorization"
)
V3_BENCHMARK_IMPLEMENTATION_QUEUE_CLAIM_BOUNDARY = (
    "This queue ranks post-clean-target implementation work after Goal4515 "
    "and Goal4523. Goal4533 closes RTNN and Spatial RayJoin as claim-scoped "
    "current targets without expanding their public/paper wording. Goal4534 "
    "records Barnes-Hut and Triangle Counting as future design targets rather "
    "than current app implementation blockers. Goal4539 then shows Triangle "
    "weighted replay graph capture remains invalid across CUDA capture modes "
    "while validating the device-output stream path, and Goal4540 accepts that "
    "non-graph stream continuation as enough to close Triangle's current V3 "
    "future-design target. Goal4541 then closes Barnes-Hut only as a current "
    "mixed-explicit route-classification target already supported by Goal4512; "
    "RT-native hierarchical traversal remains future optional research and "
    "claim-expansion work. "
    "This queue does not change any current benchmark app route and does not "
    "authorize public speedup, broad RT-core, paper-reproduction, automatic "
    "partner-selection, M113 graph-promotion, or app-specific native-engine "
    "wording."
)

V3_IMPLEMENTATION_WORK_CLASSES = (
    "runtime_blocker",
    "design_blocker",
    "future_design_target",
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
        priority=None,
        work_class="closed_current_target",
        current_route_status=(
            "current V3 route is mixed explicit: CPU/Numba or Numba CUDA fused "
            "force summary by scale; prepared RTDL/OptiX remains device-column "
            "evidence, not Barnes-Hut RT-core traversal evidence; Goal4541 "
            "closes the current route classification without implementing "
            "RT-native hierarchical traversal"
        ),
        remaining_gap=(
            "no current V3 app implementation blocker after Goal4512 and "
            "Goal4541; future RT-native Barnes-Hut acceleration remains optional "
            "research/claim-expansion work because "
            "Goal4527 blocks a naive node-AABB OptiX implementation: Barnes-Hut "
            "opening accepts a parent aggregate and must suppress its descendants, "
            "while a single custom-primitive GAS reports node AABBs independently "
            "and cannot enforce subtree-skip semantics without a reviewed generic "
            "hierarchical traversal design"
        ),
        next_build_target=(
            "no immediate V3 build target; preserve explicit scale-dependent "
            "CPU/Numba and Numba CUDA fused routes. Future optional RT-native "
            "research must not replace the fail-closed ABI with a direct all-node "
            "any-hit route until a reviewed generic hierarchical traversal "
            "lowering proves no double counting, keeps force math outside "
            "app-specific native engine code, and beats fused CPU/Numba plus "
            "fused Numba CUDA force-summary baselines"
        ),
        evidence_refs=(
            "Goal4497",
            "Goal4512",
            "Goal4517",
            "Goal4518",
            "Goal4523",
            "Goal4525",
            "Goal4526",
            "Goal4527",
            "Goal4541",
        ),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="rt_dbscan",
        priority=None,
        work_class="closed_current_target",
        current_route_status=(
            "current V3 route is predicate direct-status component signature with "
            "caller-owned CuPy point columns when the app can provide them; the "
            "future M113 chunk-local prepared graph shape is validated but does "
            "not replace the current route"
        ),
        remaining_gap=(
            "no current V3 runtime blocker after Goal4510 clean-target closure, "
            "Goal4520 live chunk-handle smoke, and Goal4528 prepared graph "
            "capture/replay validation"
        ),
        next_build_target=(
            "no immediate V3 build target; preserve the current direct-status "
            "component-signature route and keep M113 as an internal future "
            "same-stream-partner experiment shape"
        ),
        evidence_refs=("Goal4509", "Goal4510", "Goal4516", "Goal4519", "Goal4520", "Goal4528"),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="triangle_counting",
        priority=None,
        work_class="closed_current_target",
        current_route_status=(
            "current V3 route is explicit numba_direct_sort_rle prepared segment "
            "replay after primitive evidence; it completes the large paper rows "
            "but remains an internal route; Goal4540 accepts the non-graph "
            "device-output stream continuation evidence without promoting M113 "
            "CUDA graph wording"
        ),
        remaining_gap=(
            "no current V3 app implementation blocker after Goal4511 and "
            "Goal4540; future M113 graph-style Triangle replay remains blocked "
            "claim wording rather than a current app blocker because "
            "Goal4530 validates app-agnostic device key/count payload merge for "
            "cross-chunk duplicate keys, and Goal4531 validates a generic "
            "prepared weighted-replay device-output stream executor. Goal4539 "
            "confirms CUDA graph capture of that OptiX weighted launch remains "
            "fail-closed across capture modes. Goal4540 accepts the non-graph "
            "stream device-output continuation contract for current closure "
            "while keeping graph promotion blocked"
        ),
        next_build_target=(
            "no immediate V3 build target; preserve numba_direct_sort_rle plus "
            "prepared segment replay as the current internal route, accept the "
            "device-output stream executor only as a non-graph continuation "
            "contract, and require a separate reviewed capture-compatible OptiX "
            "weighted replay design before any M113 graph-readiness wording"
        ),
        evidence_refs=(
            "Goal4479",
            "Goal4511",
            "Goal4521",
            "Goal4530",
            "Goal4531",
            "Goal4539",
            "Goal4540",
        ),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="rtnn",
        priority=None,
        work_class="closed_current_target",
        current_route_status=(
            "current V3 route supports exact aggregate full-batch RTDL rows and "
            "large chunked CuPy/Numba partner-continuation rows"
        ),
        remaining_gap=(
            "no current V3 app implementation blocker after Goal4508; exact "
            "paper reproduction, same-output author comparisons, and public "
            "RT-core speedup wording remain future optional claim-expansion work "
            "because paper dataset recipes and output contracts are not frozen"
        ),
        next_build_target=(
            "no immediate V3 build target; preserve the scoped RTNN aggregate "
            "and partner-continuation evidence, and require exact dataset/output "
            "contract proof before any public paper, author-superiority, or "
            "speedup wording expansion"
        ),
        evidence_refs=("Goal4498", "Goal4500", "Goal4501", "Goal4507", "Goal4508", "Goal4533"),
        pod_needed_next=False,
    ),
    V3BenchmarkImplementationQueueRow(
        app="spatial_rayjoin",
        priority=None,
        work_class="closed_current_target",
        current_route_status=(
            "current V3 route is mixed explicit: Numba for bounded one-shot PIP, "
            "prepared RTDL/OptiX for repeated PIP, and RTDL/OptiX scalar or active "
            "count primitives for LSI/overlay-style contracts"
        ),
        remaining_gap=(
            "no current V3 app implementation blocker after Goal4514; full "
            "RayJoin paper-reproduction wording and Section 5.7 8/8 overlay "
            "wording remain future optional claim-expansion work because the "
            "current feasible public packet is scoped to the mixed route and "
            "2/8 overlay evidence"
        ),
        next_build_target=(
            "no immediate V3 build target; preserve the current mixed route and "
            "only expand public RayJoin wording with an explicitly scoped "
            "author/data packet that states which overlay rows are feasible and "
            "which are not"
        ),
        evidence_refs=("Goal4451", "Goal4514", "Goal4533"),
        pod_needed_next=False,
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
    design_rows = sorted(
        (row for row in rows if row["work_class"] == "design_blocker"),
        key=lambda row: int(row["priority"]),
    )
    future_design_rows = sorted(
        (row for row in rows if row["work_class"] == "future_design_target"),
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
            "design_blocker_queue": tuple(row["app"] for row in design_rows),
            "future_design_target_queue": tuple(row["app"] for row in future_design_rows),
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
            "design_targets_do_not_block_runtime_queue": all(
                not row["pod_needed_next"] for row in design_rows
            ),
            "future_design_targets_do_not_block_runtime_queue": all(
                not row["pod_needed_next"] for row in future_design_rows
            ),
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
    design_apps = tuple(
        row["app"]
        for row in sorted(
            (row for row in rows if row["work_class"] == "design_blocker"),
            key=lambda row: int(row["priority"]),
        )
    )
    future_design_apps = tuple(
        row["app"]
        for row in sorted(
            (row for row in rows if row["work_class"] == "future_design_target"),
            key=lambda row: int(row["priority"]),
        )
    )
    checks = {
        "version_current": packet["version"] == V3_BENCHMARK_IMPLEMENTATION_QUEUE_VERSION,
        "all_promoted_apps_present": apps == set(V2_8_PROMOTED_BENCHMARK_APPS),
        "all_route_apps_present": apps == route_apps,
        "runtime_queue_empty": runtime_apps == (),
        "design_queue_empty": design_apps == (),
        "future_design_queue_empty": future_design_apps == (),
        "next_runtime_target_none": packet["summary"]["next_runtime_build_target"] is None,
        "claim_queue_empty": tuple(packet["summary"]["claim_or_evidence_queue"]) == (),
        "design_targets_do_not_block_runtime_queue": bool(
            packet["summary"]["design_targets_do_not_block_runtime_queue"]
        ),
        "future_design_targets_do_not_block_runtime_queue": bool(
            packet["summary"]["future_design_targets_do_not_block_runtime_queue"]
        ),
        "closed_count_is_ten": len(packet["summary"]["closed_current_targets"]) == 10,
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
