from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_14_BENCHMARK_CLEANUP_VERSION = "rtdl.v2_14.benchmark_cleanup_gap_matrix.goal4379.v1"
V2_14_BENCHMARK_CLEANUP_STATUS = "draft_not_release_ready_requires_fresh_measurement"
V2_14_CLAIM_BOUNDARY = (
    "The v2.14 benchmark cleanup gap matrix is a draft planning and validation "
    "surface. It does not authorize release action, tag action, public speedup "
    "wording, whole-application speedup wording, broad RT-core wording, "
    "RTDL-beats-RayJoin wording, RayJoin paper-reproduction wording, "
    "author-hot-compute parity wording, automatic partner selection, Intel/AMD "
    "GPU performance wording, true-zero-copy wording, or app-specific native "
    "engine logic."
)

V2_14_PUBLIC_STATUSES = (
    "blocked_until_fresh_v2_14_measurement",
    "blocked_until_phase_explanation",
    "blocked_until_rayjoin_author_caveat_review",
)


@dataclass(frozen=True)
class V214BenchmarkCleanupRow:
    row_id: str
    app: str
    row_label: str
    contract: str
    v2_13_starting_point: str
    optix_route_action: str
    embree_route_action: str
    partner_policy: str
    required_phase_explanation: str
    primary_blocker: str
    public_status: str = "blocked_until_fresh_v2_14_measurement"
    fresh_v2_14_measurement_required: bool = True
    same_contract_required: bool = True
    best_known_route_required: bool = True
    phase_explanation_required: bool = True
    rayjoin_author_caveat_required: bool = False
    release_ready: bool = False
    row_scoped_public_wording_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    broad_rt_core_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    author_hot_compute_parity_claim_authorized: bool = False
    app_specific_native_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"{self.row_id}: unknown promoted benchmark app {self.app}")
        if self.public_status not in V2_14_PUBLIC_STATUSES:
            raise ValueError(f"{self.row_id}: unsupported public status")
        for field in (
            "row_id",
            "row_label",
            "contract",
            "v2_13_starting_point",
            "optix_route_action",
            "embree_route_action",
            "partner_policy",
            "required_phase_explanation",
            "primary_blocker",
        ):
            value = getattr(self, field)
            if not value or str(value).strip().lower() in {"tbd", "n/a"}:
                raise ValueError(f"{self.row_id}: {field} must be explicit")
        if self.app == "spatial_rayjoin" and self.row_id.endswith("overlay"):
            if not self.rayjoin_author_caveat_required:
                raise ValueError("RayJoin overlay row must require the author-hot-path caveat")
            if "author" not in self.primary_blocker.lower():
                raise ValueError("RayJoin overlay blocker must name the author comparison caveat")
        for flag in (
            "release_ready",
            "row_scoped_public_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "automatic_partner_selection_authorized",
            "paper_reproduction_claim_authorized",
            "author_hot_compute_parity_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if getattr(self, flag):
                raise ValueError(f"{self.row_id}: {flag} must remain false in the draft matrix")

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "app": self.app,
            "row_label": self.row_label,
            "contract": self.contract,
            "v2_13_starting_point": self.v2_13_starting_point,
            "optix_route_action": self.optix_route_action,
            "embree_route_action": self.embree_route_action,
            "partner_policy": self.partner_policy,
            "required_phase_explanation": self.required_phase_explanation,
            "primary_blocker": self.primary_blocker,
            "public_status": self.public_status,
            "fresh_v2_14_measurement_required": self.fresh_v2_14_measurement_required,
            "same_contract_required": self.same_contract_required,
            "best_known_route_required": self.best_known_route_required,
            "phase_explanation_required": self.phase_explanation_required,
            "rayjoin_author_caveat_required": self.rayjoin_author_caveat_required,
            "release_ready": self.release_ready,
            "row_scoped_public_wording_authorized": self.row_scoped_public_wording_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "broad_rt_core_claim_authorized": self.broad_rt_core_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "author_hot_compute_parity_claim_authorized": self.author_hot_compute_parity_claim_authorized,
            "app_specific_native_engine_logic_allowed": self.app_specific_native_engine_logic_allowed,
        }


V2_14_BENCHMARK_CLEANUP_ROWS: tuple[V214BenchmarkCleanupRow, ...] = (
    V214BenchmarkCleanupRow(
        row_id="hausdorff_xhd_threshold",
        app="hausdorff_xhd",
        row_label="Hausdorff / X-HD threshold",
        contract="directed_threshold_prepared_fixed_radius_count",
        v2_13_starting_point="v2.13 row-scoped OptiX-over-Embree prepared threshold evidence",
        optix_route_action="rerun current best prepared OptiX threshold route on current head",
        embree_route_action="rerun current best prepared Embree threshold route with fixed CPU thread policy",
        partner_policy="primitive-only for release row; partner baselines stay separated",
        required_phase_explanation="prepare/build, traversal, and output count phases",
        primary_blocker="fresh v2.14 same-contract measurement and phase explanation missing",
    ),
    V214BenchmarkCleanupRow(
        row_id="spatial_rayjoin_lsi",
        app="spatial_rayjoin",
        row_label="Spatial RayJoin LSI",
        contract="public_cdb_lsi_count",
        v2_13_starting_point="v2.13 split scalar-count LSI row",
        optix_route_action="rerun current prepared segment-pair scalar-count OptiX path",
        embree_route_action="rerun current prepared segment-pair scalar-count Embree path",
        partner_policy="no partner in the scalar-count comparison",
        required_phase_explanation="segment-pair prepare, traversal/count, and avoided row materialization",
        primary_blocker="fresh v2.14 measurement after Goal4376 source changes missing",
    ),
    V214BenchmarkCleanupRow(
        row_id="spatial_rayjoin_pip",
        app="spatial_rayjoin",
        row_label="Spatial RayJoin PIP",
        contract="public_cdb_pip_count",
        v2_13_starting_point="v2.13 mixed PIP row plus Goal4368 exact prepared-points executor",
        optix_route_action="rerun current directed segment point-location scalar/device-column route",
        embree_route_action="rerun current Embree directed segment point-location scalar route",
        partner_policy="no hidden partner difference; any Numba/CuPy path must be a separated row",
        required_phase_explanation="prepare, point upload/device points, traversal, scalar count or device-column output",
        primary_blocker="PIP still needs fresh same-contract route choice and explanation under v2.14 wording",
    ),
    V214BenchmarkCleanupRow(
        row_id="spatial_rayjoin_overlay",
        app="spatial_rayjoin",
        row_label="Spatial RayJoin polygon overlay",
        contract="section57_overlay_lsi_vertex_pip_midpoint_pip_no_output",
        v2_13_starting_point="Goal4376 overlay face-id device-column and adaptive grouping evidence",
        optix_route_action="rerun Goal4376 optimized OptiX overlay route as a v2.14 row",
        embree_route_action="rerun matching RTDL Embree overlay route under the same output contract",
        partner_policy="RTDL partner cache allowed only as an explicit cached/preprocessed application-wall protocol",
        required_phase_explanation="author process wall, RTDL load/pack, LSI, point-location prepare, PIP traversal, materialization",
        primary_blocker="author process-wall comparison must not be read as author hot-compute parity",
        public_status="blocked_until_rayjoin_author_caveat_review",
        rayjoin_author_caveat_required=True,
    ),
    V214BenchmarkCleanupRow(
        row_id="rt_dbscan_core_flags_numba_signature",
        app="rt_dbscan",
        row_label="RT-DBSCAN core flags plus Numba signature",
        contract="fixed_radius_core_flags_plus_numba_column_signature",
        v2_13_starting_point="v2.13 row-scoped OptiX-over-Embree with explicit Numba continuation caveat",
        optix_route_action="rerun current OptiX fixed-radius core-flag route with fixed Numba continuation",
        embree_route_action="rerun matching Embree fixed-radius route with the same fixed Numba continuation",
        partner_policy="Numba continuation fixed and named; not a pure backend-only swap",
        required_phase_explanation="RT threshold/core flags, handoff, Numba continuation, signature reduction",
        primary_blocker="fresh current-head route and output-surface caveat required",
    ),
    V214BenchmarkCleanupRow(
        row_id="robot_collision_grouped_segment_flags",
        app="robot_collision",
        row_label="Robot collision grouped segment flags",
        contract="prepared_triangle_scene_grouped_segment_any_hit_flags",
        v2_13_starting_point="v2.13 traversal-phase-only prepared row",
        optix_route_action="rerun prepared OptiX grouped segment any-hit flags route",
        embree_route_action="rerun prepared Embree grouped segment any-hit flags route",
        partner_policy="primitive-only release row",
        required_phase_explanation="scene prepare, traversal, compact flag output, host loop tail",
        primary_blocker="must confirm whether v2.14 wording remains traversal-phase-only or can cover a wider hot loop",
    ),
    V214BenchmarkCleanupRow(
        row_id="contact_manifold_aabb_collect_k",
        app="contact_manifold",
        row_label="Contact manifold AABB collect-k broadphase",
        contract="generic_aabb_broadphase_contact_candidates_2d_grid16384",
        v2_13_starting_point="v2.13 modest OptiX-over-Embree prepared broadphase row",
        optix_route_action="rerun current prepared OptiX AABB collect-k broadphase",
        embree_route_action="rerun current prepared Embree AABB collect-k broadphase",
        partner_policy="primitive-only for broadphase row; exact manifold interpretation remains app logic",
        required_phase_explanation="AABB prepare, traversal, collect-k/witness bookkeeping, output compactness",
        primary_blocker="fresh v2.14 measurement and modest-speedup explanation required",
    ),
    V214BenchmarkCleanupRow(
        row_id="raydb_style_grouped_i64_count",
        app="raydb_style",
        row_label="RayDB-style grouped i64 count",
        contract="prepared_ray_triangle_grouped_i64_reduction_count",
        v2_13_starting_point="v2.13 prepared primitive-first grouped count row",
        optix_route_action="rerun prepared OptiX grouped i64 count reduction",
        embree_route_action="rerun prepared Embree grouped i64 count reduction",
        partner_policy="primitive-first native route; partner rows only for unfused continuations",
        required_phase_explanation="ray/triangle prepare, traversal, grouped reduction, avoided typed hit-stream materialization",
        primary_blocker="fresh current-head measurement and primitive-first-vs-partner wording required",
    ),
    V214BenchmarkCleanupRow(
        row_id="barnes_hut_node_coverage",
        app="barnes_hut",
        row_label="Barnes-Hut node coverage",
        contract="prepared_fixed_radius_node_coverage_threshold_decision",
        v2_13_starting_point="v2.13 prepared native node-coverage row",
        optix_route_action="rerun prepared OptiX node-coverage threshold route",
        embree_route_action="rerun prepared Embree node-coverage threshold route",
        partner_policy="native node-coverage row separated from Numba exact-force reference",
        required_phase_explanation="tree/body prepare, traversal, coverage threshold decision, excluded force-vector work",
        primary_blocker="fresh v2.14 measurement and force-law boundary wording required",
    ),
    V214BenchmarkCleanupRow(
        row_id="librts_spatial_index_aabb",
        app="librts_spatial_index",
        row_label="LibRTS-style AABB index",
        contract="generic_prepared_aabb_index_query_2d_all_ops",
        v2_13_starting_point="v2.13 large OptiX-over-Embree prepared AABB index row",
        optix_route_action="rerun current native OptiX AABB_INDEX_QUERY_2D all-ops route",
        embree_route_action="rerun current native Embree AABB_INDEX_QUERY_2D all-ops route",
        partner_policy="primitive-only release row",
        required_phase_explanation="scene prepare, point/range query traversal, all-ops count consistency, scene-prepare amortization",
        primary_blocker="fresh v2.14 measurement after native Embree/OptiX cleanup required",
    ),
    V214BenchmarkCleanupRow(
        row_id="rtnn_ranked_summary",
        app="rtnn",
        row_label="RTNN fixed-radius ranked summary",
        contract="prepared_3d_fixed_radius_ranked_summary_raw",
        v2_13_starting_point="v2.13 blocked RT-core neighbor-search claim with near-parity backend row",
        optix_route_action="rerun prepared OptiX fixed-radius ranked-summary row",
        embree_route_action="rerun prepared Embree fixed-radius ranked-summary row",
        partner_policy="primitive row only; ANN/paper and partner baselines remain separated",
        required_phase_explanation="prepared index/search, traversal, ranked-summary output, materialization cost",
        primary_blocker="RTNN remains blocked for RT-core neighbor-search public wording without stronger end-to-end claim boundary",
        public_status="blocked_until_phase_explanation",
    ),
    V214BenchmarkCleanupRow(
        row_id="triangle_counting_any_hit",
        app="triangle_counting",
        row_label="Triangle counting RT-2A1 summary",
        contract="rt_graph_2a1_generic_ray_triangle_any_hit",
        v2_13_starting_point="v2.13 prepared weighted any-hit summary row",
        optix_route_action="rerun prepared OptiX RT-2A1 generic ray/triangle any-hit summary",
        embree_route_action="rerun prepared Embree RT-2A1 generic ray/triangle any-hit summary",
        partner_policy="primitive-only release row",
        required_phase_explanation="ray/triangle prepare, any-hit traversal, scalar accumulation, excluded graph workload claims",
        primary_blocker="fresh v2.14 measurement and graph-scope boundary wording required",
    ),
)


def v2_14_benchmark_cleanup_rows() -> tuple[V214BenchmarkCleanupRow, ...]:
    return V2_14_BENCHMARK_CLEANUP_ROWS


def validate_v2_14_benchmark_cleanup_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rows = packet.get("rows")
    if not isinstance(rows, list):
        return ["rows must be a list"]
    row_ids = [row.get("row_id") for row in rows if isinstance(row, dict)]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row ids must be unique")
    apps = {row.get("app") for row in rows if isinstance(row, dict)}
    if apps != set(V2_8_PROMOTED_BENCHMARK_APPS):
        errors.append("packet must cover exactly the promoted benchmark apps")
    if len(rows) != 12:
        errors.append("v2.14 draft matrix must contain 12 release rows including RayJoin LSI/PIP/overlay")
    rayjoin_rows = [row for row in rows if isinstance(row, dict) and row.get("app") == "spatial_rayjoin"]
    if {row.get("row_id") for row in rayjoin_rows} != {
        "spatial_rayjoin_lsi",
        "spatial_rayjoin_pip",
        "spatial_rayjoin_overlay",
    }:
        errors.append("RayJoin must be split into LSI, PIP, and overlay rows")
    overlay = next((row for row in rayjoin_rows if row.get("row_id") == "spatial_rayjoin_overlay"), None)
    if not overlay or not overlay.get("rayjoin_author_caveat_required"):
        errors.append("RayJoin overlay must require author caveat")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("every row must be a dict")
            continue
        for flag in (
            "release_ready",
            "row_scoped_public_wording_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "automatic_partner_selection_authorized",
            "paper_reproduction_claim_authorized",
            "author_hot_compute_parity_claim_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            if row.get(flag) is not False:
                errors.append(f"{row.get('row_id')}: {flag} must be false")
        if row.get("fresh_v2_14_measurement_required") is not True:
            errors.append(f"{row.get('row_id')}: fresh measurement must be required")
        if not row.get("required_phase_explanation"):
            errors.append(f"{row.get('row_id')}: phase explanation requirement missing")
    summary = packet.get("summary", {})
    if summary.get("release_ready") is not False:
        errors.append("summary.release_ready must be false")
    if summary.get("row_count") != len(rows):
        errors.append("summary.row_count must match rows")
    if summary.get("promoted_app_count") != len(V2_8_PROMOTED_BENCHMARK_APPS):
        errors.append("summary.promoted_app_count must match promoted apps")
    return errors


def v2_14_benchmark_cleanup_packet() -> dict[str, Any]:
    rows = [row.to_dict() for row in V2_14_BENCHMARK_CLEANUP_ROWS]
    packet: dict[str, Any] = {
        "version": V2_14_BENCHMARK_CLEANUP_VERSION,
        "status": V2_14_BENCHMARK_CLEANUP_STATUS,
        "claim_boundary": V2_14_CLAIM_BOUNDARY,
        "rows": rows,
        "summary": {
            "release_ready": False,
            "row_count": len(rows),
            "promoted_app_count": len(V2_8_PROMOTED_BENCHMARK_APPS),
            "rayjoin_split_rows": 3,
            "fresh_measurement_required_count": sum(
                1 for row in rows if row["fresh_v2_14_measurement_required"]
            ),
            "public_wording_authorized_count": sum(
                1 for row in rows if row["row_scoped_public_wording_authorized"]
            ),
            "author_hot_compute_parity_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
    }
    errors = validate_v2_14_benchmark_cleanup_packet(packet)
    packet["validation"] = {
        "status": "accept_draft_gate" if not errors else "reject",
        "errors": errors,
    }
    return packet


def markdown_v2_14_benchmark_cleanup_gap_matrix(packet: dict[str, Any] | None = None) -> str:
    payload = packet or v2_14_benchmark_cleanup_packet()
    lines = [
        "# Goal4379 v2.14 Benchmark Cleanup Gap Matrix",
        "",
        "Status: draft gate; not a release packet.",
        "",
        "## Summary",
        "",
        f"- Validation: `{payload['validation']['status']}`",
        f"- Promoted apps covered: `{payload['summary']['promoted_app_count']}`",
        f"- Release rows: `{payload['summary']['row_count']}`",
        f"- Fresh measurement required rows: `{payload['summary']['fresh_measurement_required_count']}`",
        f"- Public wording authorized rows now: `{payload['summary']['public_wording_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| Row | App | Contract | Partner policy | Primary blocker |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {row_id} | {app} | {contract} | {partner_policy} | {primary_blocker} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            V2_14_CLAIM_BOUNDARY,
            "",
            "## Next Execution Order",
            "",
            "1. Freeze the v2.14 app/row inventory.",
            "2. Run fresh current-head OptiX and Embree rows for the primitive-only rows.",
            "3. Run fixed-partner rows where the partner is part of the contract.",
            "4. Re-run RayJoin LSI, PIP, and overlay with the author-code caveat table.",
            "5. Fill the v2.14 public comparison and phase-explanation documents.",
            "6. Ask external reviewers to reject any row without a phase explanation.",
        ]
    )
    return "\n".join(lines) + "\n"

