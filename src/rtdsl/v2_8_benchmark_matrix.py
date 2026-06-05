from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS


V2_8_BENCHMARK_MATRIX_VERSION = "rtdl.v2_8.benchmark_matrix.v1"
V2_8_BENCHMARK_MATRIX_STATUS = "internal_goal3518_refresh_not_release_authorization"
V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS = (
    "primitive_only",
    "partner_needed",
    "prepared_execution_needed",
)
V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY = (
    "Goal3518 refreshes the internal v2.8 benchmark-app matrix. It separates "
    "setup, warmup, steady-state, and validation timing where the source "
    "artifacts expose those phases. It does not authorize a v2.8 release, "
    "public speedup wording, whole-app speedup wording, broad RT-core wording, "
    "true-zero-copy wording, paper reproduction claims, hidden partner "
    "selection, hidden dispatch, full RayJoin overlay completion claims, or "
    "app-specific native-engine behavior."
)


@dataclass(frozen=True)
class V28BenchmarkMatrixRow:
    app: str
    row_id: str
    display_name: str
    classification: str
    recommended_path: str
    partner: str
    setup_sec: float | None
    setup_status: str
    warmup_sec: float | None
    warmup_status: str
    steady_state_sec: float
    steady_state_status: str
    validation_sec: float | None
    correctness_status: str
    claim_boundary_status: str
    evidence_refs: tuple[str, ...]
    notes: str
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    app_specific_engine_logic_allowed: bool = False

    def __post_init__(self) -> None:
        if self.app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown benchmark app: {self.app}")
        if self.classification not in V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS:
            raise ValueError(f"unknown classification: {self.classification}")
        if self.steady_state_sec < 0.0:
            raise ValueError("steady_state_sec must be non-negative")
        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "app_specific_engine_logic_allowed",
        ):
            if getattr(self, field):
                raise ValueError(f"Goal3518 matrix must not authorize {field}")
        for field in (
            "row_id",
            "display_name",
            "recommended_path",
            "partner",
            "setup_status",
            "warmup_status",
            "steady_state_status",
            "correctness_status",
            "claim_boundary_status",
            "notes",
        ):
            value = getattr(self, field)
            if not value or value.strip().lower() == "n/a":
                raise ValueError(f"{field} must be explicit, not n/a")
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_BENCHMARK_MATRIX_VERSION,
            "app": self.app,
            "row_id": self.row_id,
            "display_name": self.display_name,
            "classification": self.classification,
            "recommended_path": self.recommended_path,
            "partner": self.partner,
            "setup_sec": self.setup_sec,
            "setup_status": self.setup_status,
            "warmup_sec": self.warmup_sec,
            "warmup_status": self.warmup_status,
            "steady_state_sec": self.steady_state_sec,
            "steady_state_status": self.steady_state_status,
            "validation_sec": self.validation_sec,
            "correctness_status": self.correctness_status,
            "claim_boundary_status": self.claim_boundary_status,
            "evidence_refs": self.evidence_refs,
            "notes": self.notes,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "claim_boundary": V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY,
        }


V2_8_BENCHMARK_MATRIX_ROWS: tuple[V28BenchmarkMatrixRow, ...] = (
    V28BenchmarkMatrixRow(
        app="hausdorff_xhd",
        row_id="hausdorff_xhd_exact_rt_nearest_witness",
        display_name="Hausdorff / X-HD exact RT witness",
        classification="primitive_only",
        recommended_path="RTDL/OptiX grouped reduced nearest-witness primitive",
        partner="none on the promoted RT-core path; Numba exact partner front door remains a separate fallback/reference",
        setup_sec=None,
        setup_status="not_separately_recorded_in_goal2801; one RTDL warmup captures first-run setup",
        warmup_sec=0.8969316319562495,
        warmup_status="one RTDL warmup before nine measured runs",
        steady_state_sec=0.007444375194609165,
        steady_state_status="median RTDL/OptiX exact run at 8192x8192 reduced-target scenario",
        validation_sec=None,
        correctness_status="matches exact CuPy grid baseline with zero distance error",
        claim_boundary_status="no claim to beat X-HD or optimized CuPy grid",
        evidence_refs=("Goal2801", "Goal3048", "Goal3143", "Goal3160"),
        notes="Uses RT cores on the promoted path; the Goal3143 Numba front door is generic exact partner continuation, not RT-core accelerated.",
    ),
    V28BenchmarkMatrixRow(
        app="spatial_rayjoin",
        row_id="spatial_rayjoin_count_parity_prepared",
        display_name="Spatial RayJoin count/parity",
        classification="prepared_execution_needed",
        recommended_path="prepared OptiX generic point-shape, segment-pair, and shape-pair count/parity primitives",
        partner="none for the scalar count/parity path",
        setup_sec=0.00017450004816055298,
        setup_status="largest median static-scene preparation among Goal2799 count/parity rows",
        warmup_sec=None,
        warmup_status="two warmup repeats recorded by Goal2799, not reported as one aggregate",
        steady_state_sec=0.00016109785065054893,
        steady_state_status="largest median prepared-query time among PIP/LSI/overlay-seed rows",
        validation_sec=None,
        correctness_status="all three count/parity rows match CPU references",
        claim_boundary_status="count/parity only; not full RayJoin paper reproduction or full overlay",
        evidence_refs=("Goal2799", "Goal3151", "Goal3443"),
        notes="This is the fast scalar-prepared path. Full overlay-area scalar continuation is tracked in a separate row.",
    ),
    V28BenchmarkMatrixRow(
        app="spatial_rayjoin",
        row_id="spatial_rayjoin_overlay_area_exact_prepared",
        display_name="Spatial RayJoin exact overlay-area scalar",
        classification="prepared_execution_needed",
        recommended_path="prepared relation stream plus CuPy tile-task continuation over generic shape-pair payload columns",
        partner="CuPy for the exact-area tile-task continuation",
        setup_sec=0.192737128585577,
        setup_status="binary prepared-payload cache load; geometry/payload write is excluded from steady-state",
        warmup_sec=0.386260448955,
        warmup_status="sum of three active-relation device-column warmup calls",
        steady_state_sec=0.06988946907222271,
        steady_state_status="best relation stream plus best device planner plus best tile-task executor",
        validation_sec=0.26809314265847206,
        correctness_status="matches Shapely/GEOS total within 1e-8; 1086 positive rows observed",
        claim_boundary_status="no RayJoin reproduction, no rtdl-beats-RayJoin, and no full overlay-geometry claim",
        evidence_refs=("Goal3492", "Goal3509", "Goal3511", "Goal3517"),
        notes=(
            "This row is the prepared-execution exemplar: prepare/cache, warm, run steady-state, then validate. "
            "Steady-state is 0.0038709240034222603 relation stream + 0.05171292740851641 device planner "
            "+ 0.014305617660284042 tile executor."
        ),
    ),
    V28BenchmarkMatrixRow(
        app="rt_dbscan",
        row_id="rt_dbscan_grouped_stream_components",
        display_name="RT-DBSCAN grouped stream",
        classification="partner_needed",
        recommended_path="OptiX grouped stream plus CuPy connected-component continuation",
        partner="CuPy for component continuation",
        setup_sec=None,
        setup_status="not_separately_recorded_in_goal2802; tail median excludes whole packet orchestration",
        warmup_sec=None,
        warmup_status="not separately reported in Goal2802 current packet",
        steady_state_sec=0.3023378869984299,
        steady_state_status="largest grouped-stream tail median at 131072 points",
        validation_sec=None,
        correctness_status="grouped stream signature matches prepared CuPy grid signature",
        claim_boundary_status="no IPDPS paper reproduction or broad DBSCAN speedup claim",
        evidence_refs=("Goal2802", "Goal2968"),
        notes="Partner work remains app-level graph component labeling; native side is generic fixed-radius/grouped stream.",
    ),
    V28BenchmarkMatrixRow(
        app="robot_collision",
        row_id="robot_collision_prepared_anyhit_pose_flag",
        display_name="Robot collision flags",
        classification="prepared_execution_needed",
        recommended_path="prepared RT any-hit flag primitive",
        partner="none",
        setup_sec=None,
        setup_status="legacy_total_only_from_goal2654; current v2.8 phase refresh still needed",
        warmup_sec=None,
        warmup_status="legacy_total_only_from_goal2654",
        steady_state_sec=0.00161413,
        steady_state_status="accepted OptiX total from Goal2654, not a fresh v2.8 split",
        validation_sec=None,
        correctness_status="accepted app-level parity evidence from Goal2654",
        claim_boundary_status="Tier-C/no-regression style evidence; no public speedup claim",
        evidence_refs=("Goal2654",),
        notes="Included to keep the 10-app matrix complete while final current-head phase timing remains queued.",
    ),
    V28BenchmarkMatrixRow(
        app="contact_manifold",
        row_id="contact_manifold_prepared_witness_collection",
        display_name="Contact manifold witness collection",
        classification="primitive_only",
        recommended_path="prepared bounded witness collection primitive",
        partner="none on the accepted current path",
        setup_sec=None,
        setup_status="legacy_total_only_from_goal2654; current v2.8 phase refresh still needed",
        warmup_sec=None,
        warmup_status="legacy_total_only_from_goal2654",
        steady_state_sec=0.0184764,
        steady_state_status="accepted OptiX total from Goal2654, not a fresh v2.8 split",
        validation_sec=None,
        correctness_status="accepted app-level parity evidence from Goal2654",
        claim_boundary_status="Tier-C/no-regression style evidence; no public speedup claim",
        evidence_refs=("Goal2654",),
        notes="The native primitive stays generic; richer exact refinement would be a later partner/path refresh.",
    ),
    V28BenchmarkMatrixRow(
        app="raydb_style",
        row_id="raydb_style_count_primitive_first",
        display_name="RayDB-style count",
        classification="primitive_only",
        recommended_path="primitive-first OptiX fused grouped count reduction",
        partner="none; Triton hit-stream path is deliberately not promoted for fused scalar reductions",
        setup_sec=None,
        setup_status="same-contract gate reports prepared primitive median; setup excluded by gate contract",
        warmup_sec=None,
        warmup_status="not separately reported in Goal2965 gate",
        steady_state_sec=0.00045938510447740555,
        steady_state_status="primitive-first median wall time at 1000000 rows",
        validation_sec=None,
        correctness_status="all count comparisons pass",
        claim_boundary_status="internal decision gate only; no public speedup claim",
        evidence_refs=("Goal2965", "Goal2979"),
        notes="The gate shows Triton is slower for this fused scalar case, supporting primitive-first selection.",
    ),
    V28BenchmarkMatrixRow(
        app="raydb_style",
        row_id="raydb_style_sum_primitive_first",
        display_name="RayDB-style sum",
        classification="primitive_only",
        recommended_path="primitive-first OptiX fused grouped sum reduction",
        partner="none; Triton hit-stream path is deliberately not promoted for fused scalar reductions",
        setup_sec=None,
        setup_status="same-contract gate reports prepared primitive median; setup excluded by gate contract",
        warmup_sec=None,
        warmup_status="not separately reported in Goal2965 gate",
        steady_state_sec=0.002161583164706826,
        steady_state_status="primitive-first median wall time at 1000000 rows",
        validation_sec=None,
        correctness_status="all sum comparisons pass",
        claim_boundary_status="internal decision gate only; no public speedup claim",
        evidence_refs=("Goal2965", "Goal2979"),
        notes="The fused reduction is a generic native primitive, not an app-specific database engine.",
    ),
    V28BenchmarkMatrixRow(
        app="barnes_hut",
        row_id="barnes_hut_membership_plus_vector_sum",
        display_name="Barnes-Hut membership plus vector sum",
        classification="partner_needed",
        recommended_path="OptiX membership primitive plus measured CuPy grouped vector-sum partner",
        partner="CuPy selected for vector sum by measured same-contract timing",
        setup_sec=None,
        setup_status="frontier lowering is included in the largest-case total; vector partner timing is separate",
        warmup_sec=None,
        warmup_status="vector warmups recorded as two repeats, not reported as one aggregate",
        steady_state_sec=18.033107738010585,
        steady_state_status="largest-case OptiX total median at 8192 bodies; vector partner median is 0.000696728 sec",
        validation_sec=None,
        correctness_status="rows match between Embree and OptiX; first case reference-validated",
        claim_boundary_status="no author-code comparison, no paper reproduction, no automatic Triton selection",
        evidence_refs=("Goal2803", "Goal2968"),
        notes="RT membership is primitive-first; force-vector continuation is partner-owned and CuPy currently wins.",
    ),
    V28BenchmarkMatrixRow(
        app="librts_spatial_index",
        row_id="librts_prepared_aabb_index_query",
        display_name="LibRTS spatial index",
        classification="prepared_execution_needed",
        recommended_path="prepared generic AABB index query primitive",
        partner="none",
        setup_sec=0.4088708038907498,
        setup_status="scene preparation time from Goal2798",
        warmup_sec=None,
        warmup_status="three warmups per query row, not reported as one aggregate",
        steady_state_sec=0.001551950117573142,
        steady_state_status="largest median query time across point/range operations",
        validation_sec=None,
        correctness_status="all query counts match CPU reference",
        claim_boundary_status="Tier-C/no-regression harness; no partner or public RT claim",
        evidence_refs=("Goal2798", "Goal2968"),
        notes="Kept as a prepared-index no-regression benchmark, not a release headline row.",
    ),
    V28BenchmarkMatrixRow(
        app="rtnn",
        row_id="rtnn_ranked_summary_cuda_graph",
        display_name="RTNN ranked summary",
        classification="prepared_execution_needed",
        recommended_path="prepared-query fixed-radius ranked-summary aggregate with CUDA graph replay",
        partner="none on the promoted RTDL path; CuPy grid remains same-contract opponent",
        setup_sec=1.9405803510453552,
        setup_status="largest rtdl_prepare_sec among Goal2800 distributions",
        warmup_sec=None,
        warmup_status="nine steady runs reported; warmup not reported as one aggregate",
        steady_state_sec=0.017263920977711678,
        steady_state_status="largest median RTDL elapsed among uniform/clustered/shell distributions",
        validation_sec=None,
        correctness_status="ranked aggregate matches CuPy grid for all distributions",
        claim_boundary_status="Tier-B same-contract opponent; no claim to beat RTNN paper",
        evidence_refs=("Goal2800", "Goal2822", "Goal2959"),
        notes="Prepared input and graph replay dominate the serious-performance shape.",
    ),
    V28BenchmarkMatrixRow(
        app="triangle_counting",
        row_id="triangle_counting_generic_rt_summary",
        display_name="Triangle counting",
        classification="primitive_only",
        recommended_path="generic RT graph summary primitive",
        partner="none required on the fastest primitive row",
        setup_sec=0.0015500439330935478,
        setup_status="largest scene-build phase among Goal2797 rows",
        warmup_sec=None,
        warmup_status="not separately aggregated in Goal2797",
        steady_state_sec=0.0004133919719606638,
        steady_state_status="largest query median among accepted Goal2797 rows",
        validation_sec=None,
        correctness_status="triangle count matches oracle in every row",
        claim_boundary_status="canonical harness only; no public speedup claim",
        evidence_refs=("Goal2797", "Goal3151"),
        notes="The fastest route is generic RT traversal; CuPy appears only in one alternate row and is not required.",
    ),
)


def v2_8_benchmark_matrix_rows() -> tuple[V28BenchmarkMatrixRow, ...]:
    return V2_8_BENCHMARK_MATRIX_ROWS


def v2_8_benchmark_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_8_BENCHMARK_MATRIX_ROWS)


def summarize_v2_8_benchmark_matrix() -> dict[str, Any]:
    rows = v2_8_benchmark_matrix()
    by_classification: dict[str, int] = {name: 0 for name in V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS}
    for row in rows:
        by_classification[row["classification"]] += 1
    return {
        "version": V2_8_BENCHMARK_MATRIX_VERSION,
        "status": V2_8_BENCHMARK_MATRIX_STATUS,
        "app_count": len({row["app"] for row in rows}),
        "row_count": len(rows),
        "apps": tuple(sorted({row["app"] for row in rows})),
        "classifications": by_classification,
        "claim_boundary": V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "paper_reproduction_claim_authorized": False,
    }


def validate_v2_8_benchmark_matrix(rows: tuple[dict[str, Any], ...] | None = None) -> dict[str, Any]:
    matrix = rows if rows is not None else v2_8_benchmark_matrix()
    errors: list[str] = []
    apps = {row.get("app") for row in matrix}
    if apps != set(V2_8_PROMOTED_BENCHMARK_APPS):
        errors.append(f"app coverage mismatch: {sorted(apps)}")
    if len(matrix) < len(V2_8_PROMOTED_BENCHMARK_APPS):
        errors.append("matrix must have at least one row per promoted app")
    for row in matrix:
        row_id = row.get("row_id", "<missing>")
        if row.get("classification") not in V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS:
            errors.append(f"{row_id}: unknown classification")
        if not row.get("evidence_refs"):
            errors.append(f"{row_id}: missing evidence refs")
        for key in (
            "setup_status",
            "warmup_status",
            "steady_state_status",
            "correctness_status",
            "claim_boundary_status",
            "notes",
        ):
            value = row.get(key)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() == "n/a":
                errors.append(f"{row_id}: {key} must be explicit")
        if not isinstance(row.get("steady_state_sec"), (int, float)):
            errors.append(f"{row_id}: steady_state_sec must be numeric")
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "app_specific_engine_logic_allowed",
        ):
            if row.get(flag):
                errors.append(f"{row_id}: {flag} must remain false")
    return {
        "version": V2_8_BENCHMARK_MATRIX_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "row_count": len(matrix),
        "claim_boundary": V2_8_BENCHMARK_MATRIX_CLAIM_BOUNDARY,
    }
