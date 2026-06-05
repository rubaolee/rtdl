from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V2_7_INTERNAL_CLOSEOUT_VERSION = "rtdl.v2_7.internal_closeout.v1"
V2_7_INTERNAL_CLOSEOUT_STATUS = "closed_internal_version_not_release_authorization"
V2_8_BENCHMARK_RUNTIME_GAP_VERSION = "rtdl.v2_8.benchmark_runtime_gap.v1"
V2_8_BENCHMARK_RUNTIME_GAP_STATUS = "v2_8_started_benchmark_runtime_gap_mapping"
V2_8_FIRST_RUNTIME_TARGET = "typed_device_resident_result_streams_and_grouped_continuation"
V2_8_PROMOTED_BENCHMARK_APPS = (
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
)
V2_8_CLAIM_BOUNDARY = (
    "v2.8 benchmark-runtime gap mapping starts an internal development lane. "
    "It does not authorize a v2.8 release, public speedup wording, whole-app "
    "speedup wording, broad RT-core wording, true-zero-copy wording, paper "
    "reproduction claims, hidden partner selection, hidden dispatch, or "
    "app-specific native-engine behavior."
)


@dataclass(frozen=True)
class V28BenchmarkRuntimeGapRow:
    benchmark_app: str
    display_name: str
    benchmark_path: str
    current_best_path: str
    partner_position: str
    current_bottleneck: str
    generic_runtime_target: str
    target_family: str
    priority: str
    evidence_refs: tuple[str, ...]
    app_specific_engine_logic_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if self.benchmark_app not in V2_8_PROMOTED_BENCHMARK_APPS:
            raise ValueError(f"unknown v2.8 benchmark app: {self.benchmark_app}")
        if self.priority not in ("P0", "P1", "P2"):
            raise ValueError("priority must be P0, P1, or P2")
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"v2.8 gap row must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_BENCHMARK_RUNTIME_GAP_VERSION,
            "benchmark_app": self.benchmark_app,
            "display_name": self.display_name,
            "benchmark_path": self.benchmark_path,
            "current_best_path": self.current_best_path,
            "partner_position": self.partner_position,
            "current_bottleneck": self.current_bottleneck,
            "generic_runtime_target": self.generic_runtime_target,
            "target_family": self.target_family,
            "priority": self.priority,
            "evidence_refs": self.evidence_refs,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "claim_boundary": V2_8_CLAIM_BOUNDARY,
        }


V2_8_BENCHMARK_RUNTIME_GAP_ROWS: tuple[V28BenchmarkRuntimeGapRow, ...] = (
    V28BenchmarkRuntimeGapRow(
        benchmark_app="hausdorff_xhd",
        display_name="Hausdorff / X-HD style",
        benchmark_path="examples/v2_0/research_benchmarks/hausdorff_xhd/",
        current_best_path=(
            "generic directed max-of-nearest-distance partner front door for exact partner "
            "continuation; active-frontier RTDL/OptiX path remains the RT-core research harness"
        ),
        partner_position=(
            "Numba is the recommended exact partner continuation for the scalar max-nearest path; "
            "CuPy remains the CUDA-core fairness baseline."
        ),
        current_bottleneck=(
            "front-door naming is now generic, and the RT-core nearest-witness stream device-column "
            "path now emits reusable typed producer metadata; remaining work is serious-scale "
            "device-resident continuation proof, broader partner conformance, and prepared input "
            "residency without claiming true zero-copy."
        ),
        generic_runtime_target="typed nearest-witness streams plus grouped max-distance continuation",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=("Goal3046", "Goal3048", "Goal3052", "Goal3143", "Goal3160", "Goal3178"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="spatial_rayjoin",
        display_name="Spatial RayJoin",
        benchmark_path="examples/v2_0/research_benchmarks/spatial_rayjoin/",
        current_best_path=(
            "primitive-first scalar count/parity and first-hit paths; direct v2.8 compact-mask "
            "typed-stream front door for explicit candidate-row filtering; generic 2-D relation-row "
            "typed producer metadata for prepared shape/segment row views; generic prepared "
            "shape-pair active-count route for overlay-seed scalar summaries; instance-aware "
            "closed-shape candidate columns plus prepared CuPy exact refiner for PIP row/count "
            "continuation; reusable prepared handles for PIP exact continuation, LSI grouped/dense "
            "counts, and overlay-seed active-count summaries; generic device-side active-count "
            "continuation is now the default overlay scalar-summary route"
        ),
        partner_position=(
            "Numba is the recommended custom continuation when row-stream compaction is part of the app; "
            "CuPy is the measured prepared closed-shape refinement partner for exact PIP continuation."
        ),
        current_bottleneck=(
            "compact-mask continuation now has a direct caller-column front door, and generic "
            "relation-row typed producer metadata now exists for host row views; overlay active-count "
            "mode now skips final host row allocation; PIP closed-shape exact continuation now has "
            "instance-aware candidate columns and a prepared CuPy refiner with pod timing evidence; "
            "prepared/reusable route shape now covers PIP, LSI, and overlay-seed scalar summaries. "
            "Goal3441 showed the former host overlay active-count bottleneck was flag download, "
            "CPU containment, host active scan, and orchestration rather than OptiX traversal; "
            "Goal3442/3443 moved the scalar active-count continuation onto the device and made it "
            "the default route with pod evidence. Remaining work is device-resident relation-row "
            "output for full overlay rows, richer parity/count grouping over resident row streams "
            "beyond scalar active-count, and boundary-witness ownership at serious scale."
        ),
        generic_runtime_target="typed hit streams with grouped parity/count and compact-mask continuation",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=(
            "Goal3003",
            "Goal3052",
            "Goal3147",
            "Goal3171",
            "Goal3181",
            "Goal3183",
            "Goal3424",
            "Goal3427",
            "Goal3428",
            "Goal3435",
            "Goal3438",
            "Goal3441",
            "Goal3442",
            "Goal3443",
        ),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="rt_dbscan",
        display_name="RT-DBSCAN",
        benchmark_path="examples/v2_0/research_benchmarks/rt_dbscan/",
        current_best_path=(
            "fixed-radius/core-summary primitives plus v2.8 fixed-radius graph component front door "
            "over the measured OptiX+CuPy grouped-stream path, with typed adjacency/grouped-stream "
            "producer metadata from Goal3158"
        ),
        partner_position=(
            "CuPy is the current measured component-continuation reference through an explicit v2.8 front door; "
            "Numba remains a candidate for future same-contract conformance."
        ),
        current_bottleneck=(
            "the grouped-stream component path is now front-door reachable and typed producer metadata "
            "now exists; the remaining shared work is broader partner conformance and larger "
            "device-resident continuation coverage without DBSCAN-native engine semantics"
        ),
        generic_runtime_target="fixed-radius graph component front door plus typed adjacency/grouped-stream producer metadata",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=("Goal2425 lineage", "Goal2478", "Goal3154", "Goal3155", "Goal3156", "Goal3158", "Goal3179"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="robot_collision",
        display_name="Robot collision",
        benchmark_path="examples/v2_0/research_benchmarks/robot_collision/",
        current_best_path=(
            "generic any-hit/collision flag primitive over prepared static scenes; direct v2.8 bounded-collect "
            "typed-stream front door for optional grouped witness rows"
        ),
        partner_position="torch/triton bounded collect is available only when users explicitly request grouped witness continuation.",
        current_bottleneck=(
            "bounded-collect continuation now has a direct caller-column front door; remaining work is native "
            "typed flag/witness producer evidence, prepared-scene residency metadata, and same-scale optional "
            "witness benchmarks."
        ),
        generic_runtime_target="bounded flag/witness result pages with prepared-scene residency metadata",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P1",
        evidence_refs=("Goal2491", "Goal3173"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="contact_manifold",
        display_name="Contact manifold",
        benchmark_path="examples/v2_0/research_benchmarks/contact_manifold/",
        current_best_path=(
            "bounded witness collection with fail-closed overflow behavior; direct v2.8 bounded-collect "
            "typed-stream front door over grouped item rows"
        ),
        partner_position="torch/triton bounded collect is available only when users explicitly request grouped witness continuation.",
        current_bottleneck=(
            "bounded-collect continuation now has a direct caller-column front door; remaining work is native "
            "typed bounded-witness producer evidence, device-residency proof, and same-scale partner/native "
            "benchmarks."
        ),
        generic_runtime_target="typed bounded witness pages with fail-closed completion metadata",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P1",
        evidence_refs=("Goal2510 lineage", "Goal3173"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="raydb_style",
        display_name="RayDB-style grouped aggregates",
        benchmark_path="examples/v2_0/research_benchmarks/raydb_style/",
        current_best_path=(
            "fused columnar grouped reductions when the primitive exactly matches; "
            "v2.8 grouped-reduction typed-stream front door for explicit unfused partner continuation; "
            "generic ray/triangle grouped-i64 typed producer metadata"
        ),
        partner_position="Numba is recommended only for unfused grouped scalar continuations.",
        current_bottleneck=(
            "front-door schema for unfused grouped reductions now exists, and native typed producer metadata now exists; "
            "the remaining native typed producer/residency evidence gap is device-resident output stream "
            "evidence and broader partner conformance without overriding fused primitives."
        ),
        generic_runtime_target="typed grouped-reduction streams with explicit fused-vs-continuation selection",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=("Goal2995", "Goal3052", "Goal3162", "Goal3176"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="barnes_hut",
        display_name="Barnes-Hut / RT-BarnesHut style",
        benchmark_path="examples/v2_0/research_benchmarks/barnes_hut/",
        current_best_path=(
            "aggregate-frontier collect primitive plus v2.8 grouped-vector typed-stream "
            "front door for app-owned force/vector continuation"
        ),
        partner_position=(
            "CuPy remains the current force-vector continuation reference; torch/triton are "
            "also supported by the generic grouped-vector front door."
        ),
        current_bottleneck=(
            "grouped vector continuation now has a generic front door; remaining work is native "
            "typed aggregate-frontier producer/residency evidence and force-law ownership boundaries "
            "at serious scale."
        ),
        generic_runtime_target="typed aggregate-frontier streams with prepared residency plus grouped vector continuation",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P1",
        evidence_refs=("Goal2905 lineage", "Goal3169"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="librts_spatial_index",
        display_name="LibRTS-style spatial index",
        benchmark_path="examples/v2_0/research_benchmarks/librts_spatial_index/",
        current_best_path="generic point/range query rows and count-oriented no-regression evidence",
        partner_position="no promoted v2.6 custom partner path",
        current_bottleneck="mutable index/update policy remains app-owned; v2.8 should avoid treating this as the first runtime extension.",
        generic_runtime_target="prepared spatial-index residency and no-regression query harness",
        target_family="prepared_residency_and_harness",
        priority="P2",
        evidence_refs=("Goal2570 lineage",),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="rtnn",
        display_name="RTNN neighbor search",
        benchmark_path="examples/v2_0/research_benchmarks/rtnn/",
        current_best_path=(
            "prepared fixed-radius ranked-summary primitives with batched request hardening; "
            "v2.8 ranked-summary typed-stream front door for explicit grouped top-k/arg continuation"
        ),
        partner_position=(
            "torch/triton are the current grouped_topk_f64 continuation partners; "
            "numba supports grouped argmin/argmax but not promoted top-k yet; CuPy remains an all-pairs baseline."
        ),
        current_bottleneck=(
            "ranked-summary top-k handoff now has a generic front door; remaining work is prepared "
            "packed-column residency, native typed producer evidence, and replay/chunking at serious scale."
        ),
        generic_runtime_target="typed ranked-summary streams with prepared packed-column residency and native producer evidence",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=("Goal2821", "Goal2822", "Goal2958", "Goal3165"),
    ),
    V28BenchmarkRuntimeGapRow(
        benchmark_app="triangle_counting",
        display_name="Triangle counting",
        benchmark_path="examples/v2_0/research_benchmarks/triangle_counting/",
        current_best_path=(
            "native scalar triangle-count primitive for scalar answers; direct v2.8 compact-mask "
            "typed-stream front door for explicit candidate-row interpretation; generic ray/triangle "
            "hit-stream typed producer metadata"
        ),
        partner_position="Numba compact-mask continuation is only for explicit candidate-row interpretation.",
        current_bottleneck=(
            "compact-mask continuation now has a direct caller-column front door, and generic native "
            "typed candidate-row producer metadata now exists through the ray/triangle hit-stream "
            "contract; remaining work is segmented/streamed graph lowering, benchmark-app adoption of "
            "resident candidate streams, and resident continuation at serious scale."
        ),
        generic_runtime_target="typed graph candidate streams with segmented compact-mask continuation",
        target_family=V2_8_FIRST_RUNTIME_TARGET,
        priority="P0",
        evidence_refs=("Goal3000", "Goal3052", "Goal3147", "Goal3171", "Goal3180"),
    ),
)


def v2_7_internal_closeout_status() -> dict[str, Any]:
    return {
        "version": V2_7_INTERNAL_CLOSEOUT_VERSION,
        "status": V2_7_INTERNAL_CLOSEOUT_STATUS,
        "current_closeout_report": "docs/reports/goal3102_v2_7_post_semantic_search_current_closeout_2026-06-03.md",
        "current_consensus_report": "docs/reports/goal3104_v2_7_post_d8_closeout_2ai_consensus_2026-06-03.md",
        "d1_through_d8_closed": True,
        "d8_semantic_search_preview_only": True,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_CLAIM_BOUNDARY,
    }


def v2_8_benchmark_runtime_gap_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(row.to_metadata() for row in V2_8_BENCHMARK_RUNTIME_GAP_ROWS)


def v2_8_runtime_target_summary() -> dict[str, Any]:
    rows = v2_8_benchmark_runtime_gap_matrix()
    first_target_apps = tuple(
        row["benchmark_app"]
        for row in rows
        if row["target_family"] == V2_8_FIRST_RUNTIME_TARGET
    )
    return {
        "version": V2_8_BENCHMARK_RUNTIME_GAP_VERSION,
        "status": V2_8_BENCHMARK_RUNTIME_GAP_STATUS,
        "first_runtime_target": V2_8_FIRST_RUNTIME_TARGET,
        "first_target_app_count": len(first_target_apps),
        "first_target_apps": first_target_apps,
        "first_target_reason": (
            "typed device-resident result streams and grouped continuation are "
            "the shared bottleneck across row-heavy spatial, neighbor, graph, "
            "database, Hausdorff, collision, and witness workloads"
        ),
        "not_first_target": (
            "app-specific RayJoin/RayDB/DBSCAN/Hausdorff kernels",
            "hidden partner auto-selection",
            "user-defined shader injection",
        ),
        "v3_boundary": "user-defined shader injection remains a later v3.0 lane",
        "claim_boundary": V2_8_CLAIM_BOUNDARY,
    }


def validate_v2_8_benchmark_runtime_gap_map(
    *,
    expected_apps: tuple[str, ...] = V2_8_PROMOTED_BENCHMARK_APPS,
) -> dict[str, Any]:
    closeout = v2_7_internal_closeout_status()
    rows = v2_8_benchmark_runtime_gap_matrix()
    summary = v2_8_runtime_target_summary()
    errors: list[str] = []

    apps = tuple(row["benchmark_app"] for row in rows)
    if apps != expected_apps:
        errors.append("benchmark app order/coverage changed")
    if len(set(apps)) != len(expected_apps):
        errors.append("benchmark apps must be unique")
    if closeout.get("status") != V2_7_INTERNAL_CLOSEOUT_STATUS:
        errors.append("v2.7 internal closeout status is not closed")
    if closeout.get("d1_through_d8_closed") is not True:
        errors.append("v2.7 D-1 through D-8 must be closed before v2.8 starts")
    if closeout.get("d8_semantic_search_preview_only") is not True:
        errors.append("v2.7 D-8 must remain preview-only")
    if summary.get("first_runtime_target") != V2_8_FIRST_RUNTIME_TARGET:
        errors.append("first v2.8 runtime target changed")
    if int(summary.get("first_target_app_count", 0)) < 7:
        errors.append("first runtime target must cover at least seven benchmark apps")
    for app in ("hausdorff_xhd", "spatial_rayjoin", "rt_dbscan", "raydb_style", "rtnn", "triangle_counting"):
        if app not in tuple(summary.get("first_target_apps", ())):
            errors.append(f"first runtime target must cover {app}")
    for row in rows:
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
        ):
            if row.get(field) is not False:
                errors.append(f"{row.get('benchmark_app')} authorizes {field}")
        if not row.get("current_bottleneck"):
            errors.append(f"{row.get('benchmark_app')} is missing current bottleneck")
        if not row.get("generic_runtime_target"):
            errors.append(f"{row.get('benchmark_app')} is missing generic runtime target")
    for field in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if closeout.get(field) is not False:
            errors.append(f"v2.7 closeout must not authorize {field}")

    return {
        "status": "accept" if not errors else "reject",
        "version": V2_8_BENCHMARK_RUNTIME_GAP_VERSION,
        "errors": tuple(errors),
        "v2_7_status": closeout.get("status"),
        "v2_8_status": V2_8_BENCHMARK_RUNTIME_GAP_STATUS,
        "app_count": len(rows),
        "first_runtime_target": summary.get("first_runtime_target"),
        "first_target_app_count": summary.get("first_target_app_count"),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": V2_8_CLAIM_BOUNDARY,
    }


__all__ = [
    "V28BenchmarkRuntimeGapRow",
    "V2_7_INTERNAL_CLOSEOUT_STATUS",
    "V2_7_INTERNAL_CLOSEOUT_VERSION",
    "V2_8_BENCHMARK_RUNTIME_GAP_STATUS",
    "V2_8_BENCHMARK_RUNTIME_GAP_VERSION",
    "V2_8_CLAIM_BOUNDARY",
    "V2_8_FIRST_RUNTIME_TARGET",
    "V2_8_PROMOTED_BENCHMARK_APPS",
    "v2_7_internal_closeout_status",
    "v2_8_benchmark_runtime_gap_matrix",
    "v2_8_runtime_target_summary",
    "validate_v2_8_benchmark_runtime_gap_map",
]
