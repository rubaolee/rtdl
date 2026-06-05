from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V2_8_VS_V2_3_COMPARISON_VERSION = "rtdl.goal3523.v2_8_vs_v2_3_same_contract.v1"
V2_8_VS_V2_3_COMPARISON_STATUS = "protocol_ready_pod_evidence_required"
V2_8_VS_V2_3_COMPARISON_CLAIM_BOUNDARY = (
    "Goal3523 defines the v2.8-vs-v2.3 benchmark comparison contract. It does "
    "not authorize public speedup wording, whole-app speedup wording, a v2.8 "
    "release, package-install claims, paper reproduction claims, broad RT-core "
    "claims, true zero-copy claims, hidden partner selection, or app-specific "
    "native-engine behavior."
)

COMPARISON_CLASSES = (
    "same_contract_existing_artifact",
    "same_output_evolved_runtime_existing_artifact",
    "fresh_same_contract_pod_required",
    "v2_3_not_promoted",
)


@dataclass(frozen=True)
class V28VsV23BenchmarkComparisonRow:
    app: str
    v2_3_promoted: bool
    v2_3_contract: str
    v2_3_source: str
    v2_3_optix_sec: float | None
    v2_8_contract: str
    v2_8_source: str
    v2_8_sec: float | None
    comparison_class: str
    ratio_authorized_from_existing_artifacts: bool
    required_next_action: str
    boundary: str
    public_claim_authorized: bool = False
    release_authorized: bool = False

    def __post_init__(self) -> None:
        if self.comparison_class not in COMPARISON_CLASSES:
            raise ValueError(f"unknown comparison_class: {self.comparison_class}")
        if self.public_claim_authorized or self.release_authorized:
            raise ValueError("Goal3523 rows must not authorize public claims or release")
        for field in (
            "app",
            "v2_3_contract",
            "v2_3_source",
            "v2_8_contract",
            "v2_8_source",
            "required_next_action",
            "boundary",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip() or value.strip().lower() == "n/a":
                raise ValueError(f"{field} must be explicit")
        if self.ratio_authorized_from_existing_artifacts:
            if self.v2_3_optix_sec is None or self.v2_8_sec is None:
                raise ValueError("authorized ratios require both timings")
            if self.v2_3_optix_sec <= 0.0 or self.v2_8_sec <= 0.0:
                raise ValueError("authorized ratio timings must be positive")

    @property
    def v2_8_speedup_vs_v2_3(self) -> float | None:
        if not self.ratio_authorized_from_existing_artifacts:
            return None
        assert self.v2_3_optix_sec is not None
        assert self.v2_8_sec is not None
        return self.v2_3_optix_sec / self.v2_8_sec

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_VS_V2_3_COMPARISON_VERSION,
            "app": self.app,
            "v2_3_promoted": self.v2_3_promoted,
            "v2_3_contract": self.v2_3_contract,
            "v2_3_source": self.v2_3_source,
            "v2_3_optix_sec": self.v2_3_optix_sec,
            "v2_8_contract": self.v2_8_contract,
            "v2_8_source": self.v2_8_source,
            "v2_8_sec": self.v2_8_sec,
            "comparison_class": self.comparison_class,
            "ratio_authorized_from_existing_artifacts": self.ratio_authorized_from_existing_artifacts,
            "v2_8_speedup_vs_v2_3": self.v2_8_speedup_vs_v2_3,
            "required_next_action": self.required_next_action,
            "boundary": self.boundary,
            "public_claim_authorized": self.public_claim_authorized,
            "release_authorized": self.release_authorized,
            "claim_boundary": V2_8_VS_V2_3_COMPARISON_CLAIM_BOUNDARY,
        }


V2_8_VS_V2_3_COMPARISON_ROWS: tuple[V28VsV23BenchmarkComparisonRow, ...] = (
    V28VsV23BenchmarkComparisonRow(
        app="hausdorff_xhd",
        v2_3_promoted=True,
        v2_3_contract="threshold-decision / grouped threshold-witness evidence",
        v2_3_source="v2.3 release report plus Goal2654 threshold row: OptiX 0.0311073 sec",
        v2_3_optix_sec=0.0311073,
        v2_8_contract="exact RT nearest-witness prepared path",
        v2_8_source="Goal3518 v2.8 matrix: 0.007444375 sec steady-state",
        v2_8_sec=0.007444375194609165,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Run both threshold-decision and exact-witness rows on v2.3 evidence checkout and v2.8 HEAD, then report both as separate contracts.",
        boundary="Existing artifacts mix threshold and exact-witness contracts; do not ratio them as one app speedup.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="spatial_rayjoin",
        v2_3_promoted=True,
        v2_3_contract="PIP, LSI, and overlay-seed scoped spatial relation rows",
        v2_3_source="v2.3 release report plus Goal2654 spatial summary row: OptiX 0.000529638 sec",
        v2_3_optix_sec=0.000529638,
        v2_8_contract="split count/parity prepared row plus exact overlay-area prepared continuation",
        v2_8_source="Goal3518 v2.8 matrix: count/parity 0.000161098 sec; overlay-area steady-state 0.069889469 sec",
        v2_8_sec=None,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Run count/parity and overlay-area as two explicit rows on the same public-CDB fixture in both lanes; do not collapse them into one RayJoin row.",
        boundary="v2.8 decomposes RayJoin into scalar count/parity and exact overlay-area phases; the older scoped summary is not the same row.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="rt_dbscan",
        v2_3_promoted=True,
        v2_3_contract="cluster signature over generic fixed-radius/component contract",
        v2_3_source="Goal2654 promoted row: OptiX 1.62144 sec",
        v2_3_optix_sec=1.62144,
        v2_8_contract="grouped stream plus CuPy component continuation, same cluster-signature output",
        v2_8_source="Goal3521 grouped-stream artifact: largest tail median 0.302337887 sec at 131072 points",
        v2_8_sec=0.3023378869984299,
        comparison_class="same_output_evolved_runtime_existing_artifact",
        ratio_authorized_from_existing_artifacts=True,
        required_next_action="Still rerun on one pod for final publication-quality table, but existing artifacts support a bounded internal same-output comparison.",
        boundary=(
            "Only the grouped-stream path gets the roughly 4x-5x continuation win; the raw RT-count row is not a win at every scale. "
            "Note: v2.3 timing is a total-run figure, while v2.8 timing is the grouped-stream tail median excluding preparation and warmup; "
            "the same-phase comparison must be established by the required pod rerun."
        ),
    ),
    V28VsV23BenchmarkComparisonRow(
        app="robot_collision",
        v2_3_promoted=True,
        v2_3_contract="prepared collision flags",
        v2_3_source="Goal2654 promoted row: OptiX 0.00161413 sec",
        v2_3_optix_sec=0.00161413,
        v2_8_contract="prepared any-hit pose flag path with phase-separated final validation evidence",
        v2_8_source="Goal3518 inherits Goal2654 total; Goal3521 fresh pod uses a different 256x32x3 workload",
        v2_8_sec=None,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Run identical pose/obstacle/link counts under v2.3 evidence baseline and v2.8 HEAD, separating setup/warmup/steady-state.",
        boundary="The fresh Goal3521 robot row is useful RTX validation, but its workload is not the same as the v2.3 row.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="contact_manifold",
        v2_3_promoted=True,
        v2_3_contract="generic AABB broadphase plus bounded witness collection",
        v2_3_source=(
            "Current docs/release_reports/v2_3 includes contact manifold as a promoted benchmark; "
            "the v2.3 tag copy lists nine promoted apps, so the final packet must disclose this tag/current-report drift. "
            "Goal2654 promoted row: OptiX 0.0184764 sec"
        ),
        v2_3_optix_sec=0.0184764,
        v2_8_contract="prepared bounded witness collection / contact broadphase",
        v2_8_source="Goal3518 plus Goal3521 grid-4096 phase split",
        v2_8_sec=0.027931150048971176,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action=(
            "Run the same AABB broadphase collect-k contract in both lanes with identical grid count, witness capacity, "
            "backend, setup, warmup, and steady-state timing phases."
        ),
        boundary=(
            "Contact has v2.3-era evidence in the current release report and Goal2654, but the v2.3 tag text listed nine apps; "
            "the final comparison must disclose that history instead of calling contact a v2.8-only app."
        ),
    ),
    V28VsV23BenchmarkComparisonRow(
        app="raydb_style",
        v2_3_promoted=True,
        v2_3_contract="prepared-query grouped count/sum evidence over generated 2M rows",
        v2_3_source="Goal2654 current RayDB rows: count 0.0001704 sec, sum 0.0009476 sec",
        v2_3_optix_sec=None,
        v2_8_contract="primitive-first fused grouped count/sum decision gate at 1M rows",
        v2_8_source="Goal3518/Goal2965: count 0.000459385 sec, sum 0.002161583 sec",
        v2_8_sec=None,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Rerun count and sum at the same row count, group count, predicate shape, warmup, and timing phase; compare count and sum separately.",
        boundary="Existing rows use different scales and evolved primitive-first rules; no combined RayDB ratio is authorized.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="barnes_hut",
        v2_3_promoted=True,
        v2_3_contract="node coverage prepared threshold decision",
        v2_3_source="Goal2654 promoted row: OptiX 0.00855045 sec",
        v2_3_optix_sec=0.00855045,
        v2_8_contract="membership plus vector-sum continuation",
        v2_8_source="Goal3518 largest-case OptiX total 18.033107738 sec; vector partner median 0.000696728 sec",
        v2_8_sec=None,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Run node-coverage and membership-plus-vector-sum as separate contracts in both lanes, or restrict the comparison to node coverage only.",
        boundary="Node coverage and membership-plus-vector-sum are not the same contract.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="librts_spatial_index",
        v2_3_promoted=True,
        v2_3_contract="AABB index all count-only",
        v2_3_source="Goal2654 promoted row: OptiX 0.691477 sec",
        v2_3_optix_sec=0.691477,
        v2_8_contract="prepared generic AABB index query",
        v2_8_source="Goal3518 prepared query row: largest median 0.001551950 sec",
        v2_8_sec=0.001551950117573142,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action="Run the same box count, query count, operation mix, and timing phase before ratioing the apparent improvement.",
        boundary="The apparent timing delta is too large to treat as final without confirming identical workload and metric definitions.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="rtnn",
        v2_3_promoted=True,
        v2_3_contract="prepared 3-D ranked summary",
        v2_3_source="Goal2654 promoted row: OptiX 0.00153247 sec",
        v2_3_optix_sec=0.00153247,
        v2_8_contract="prepared ranked-summary aggregate with CUDA graph replay across multiple distributions",
        v2_8_source="Goal3518 largest median across distributions: 0.017263921 sec",
        v2_8_sec=None,
        comparison_class="fresh_same_contract_pod_required",
        ratio_authorized_from_existing_artifacts=False,
        required_next_action=(
            "Run uniform/clustered/shell rows under both lanes with identical point counts and report each distribution separately; "
            "lead with the uniform row because v2.3's existing timing is a single uniform ranked-summary number."
        ),
        boundary="The v2.8 row is a worst-of-distribution matrix row, not the same single uniform row as the v2.3 standard table.",
    ),
    V28VsV23BenchmarkComparisonRow(
        app="triangle_counting",
        v2_3_promoted=True,
        v2_3_contract="RT-Graph-style RT-2A1 summary",
        v2_3_source="Goal2654 promoted row: OptiX 0.000364401 sec",
        v2_3_optix_sec=0.000364401,
        v2_8_contract="generic RT graph summary primitive",
        v2_8_source="Goal3518 accepted row: 0.000413392 sec",
        v2_8_sec=0.0004133919719606638,
        comparison_class="same_contract_existing_artifact",
        ratio_authorized_from_existing_artifacts=True,
        required_next_action="Rerun on one pod for final table, but existing artifacts are close enough to flag this as a same-contract carry-forward row.",
        boundary="This is a synthetic RT-Graph summary row, not paper-scale graph reproduction.",
    ),
)


def v2_8_vs_v2_3_benchmark_comparison_rows() -> tuple[V28VsV23BenchmarkComparisonRow, ...]:
    return V2_8_VS_V2_3_COMPARISON_ROWS


def v2_8_vs_v2_3_benchmark_comparison() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_8_VS_V2_3_COMPARISON_ROWS)


def summarize_v2_8_vs_v2_3_benchmark_comparison() -> dict[str, Any]:
    rows = v2_8_vs_v2_3_benchmark_comparison()
    class_counts = {name: 0 for name in COMPARISON_CLASSES}
    authorized = []
    for row in rows:
        class_counts[row["comparison_class"]] += 1
        if row["ratio_authorized_from_existing_artifacts"]:
            authorized.append(row)
    return {
        "version": V2_8_VS_V2_3_COMPARISON_VERSION,
        "status": V2_8_VS_V2_3_COMPARISON_STATUS,
        "app_count": len(rows),
        "class_counts": class_counts,
        "authorized_existing_artifact_ratio_count": len(authorized),
        "pod_required_before_final_all_app_table": True,
        "release_authorized": False,
        "public_claim_authorized": False,
        "claim_boundary": V2_8_VS_V2_3_COMPARISON_CLAIM_BOUNDARY,
    }


def validate_v2_8_vs_v2_3_benchmark_comparison() -> dict[str, Any]:
    rows = v2_8_vs_v2_3_benchmark_comparison()
    errors: list[str] = []
    expected_apps = {
        "hausdorff_xhd",
        "spatial_rayjoin",
        "rt_dbscan",
        "robot_collision",
        "contact_manifold",
        "raydb_style",
        "barnes_hut",
        "librts_spatial_index",
        "rtnn",
        "triangle_counting",
    }
    apps = {row["app"] for row in rows}
    if apps != expected_apps:
        errors.append(f"app coverage mismatch: {sorted(apps)}")
    contact = next((row for row in rows if row["app"] == "contact_manifold"), None)
    if contact is None:
        errors.append("contact_manifold row missing")
    elif not contact["v2_3_promoted"] or contact["comparison_class"] != "fresh_same_contract_pod_required":
        errors.append("contact_manifold must be treated as promoted in current v2.3 evidence but fresh-pod-required")
    if not any(row["ratio_authorized_from_existing_artifacts"] for row in rows):
        errors.append("comparison map should identify the already-ratioable rows")
    if sum(1 for row in rows if row["comparison_class"] == "fresh_same_contract_pod_required") < 6:
        errors.append("most rows must remain blocked pending fresh pod same-contract evidence")
    for row in rows:
        if row["release_authorized"] or row["public_claim_authorized"]:
            errors.append(f"{row['app']}: unauthorized claim flag")
        if row["ratio_authorized_from_existing_artifacts"] and row["v2_8_speedup_vs_v2_3"] is None:
            errors.append(f"{row['app']}: authorized ratio missing")
    return {
        "version": V2_8_VS_V2_3_COMPARISON_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "app_count": len(apps),
        "pod_required_before_final_all_app_table": True,
        "claim_boundary": V2_8_VS_V2_3_COMPARISON_CLAIM_BOUNDARY,
    }
