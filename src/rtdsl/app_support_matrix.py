from __future__ import annotations

from dataclasses import dataclass


APP_ENGINES = ("cpu_python_reference", "embree", "optix", "vulkan", "hiprt", "apple_rt")

DIRECT_CLI_NATIVE = "direct_cli_native"
DIRECT_CLI_NATIVE_ASSISTED = "direct_cli_native_assisted"
DIRECT_CLI_COMPATIBILITY_FALLBACK = "direct_cli_compatibility_fallback"
PORTABLE_CPU_ORACLE = "portable_cpu_oracle"
PARTIAL_CPU_ORACLE = "partial_cpu_oracle"
NOT_EXPOSED_BY_APP_CLI = "not_exposed_by_app_cli"
APPLE_SPECIFIC = "apple_specific"

APP_SUPPORT_STATUSES = (
    DIRECT_CLI_NATIVE,
    DIRECT_CLI_NATIVE_ASSISTED,
    DIRECT_CLI_COMPATIBILITY_FALLBACK,
    PORTABLE_CPU_ORACLE,
    PARTIAL_CPU_ORACLE,
    NOT_EXPOSED_BY_APP_CLI,
    APPLE_SPECIFIC,
)

OPTIX_TRAVERSAL = "optix_traversal"
OPTIX_TRAVERSAL_PREPARED_SUMMARY = "optix_traversal_prepared_summary"
CUDA_THROUGH_OPTIX = "cuda_through_optix"
HOST_INDEXED_FALLBACK = "host_indexed_fallback"
PYTHON_INTERFACE_DOMINATED = "python_interface_dominated"
NOT_OPTIX_EXPOSED = "not_optix_exposed"
NOT_OPTIX_APPLICABLE = "not_optix_applicable"

OPTIX_APP_PERFORMANCE_CLASSES = (
    OPTIX_TRAVERSAL,
    OPTIX_TRAVERSAL_PREPARED_SUMMARY,
    CUDA_THROUGH_OPTIX,
    HOST_INDEXED_FALLBACK,
    PYTHON_INTERFACE_DOMINATED,
    NOT_OPTIX_EXPOSED,
    NOT_OPTIX_APPLICABLE,
)


@dataclass(frozen=True)
class AppEngineSupport:
    app: str
    engine: str
    status: str
    note: str


@dataclass(frozen=True)
class OptixAppPerformanceSupport:
    app: str
    performance_class: str
    note: str


@dataclass(frozen=True)
class OptixAppBenchmarkReadiness:
    app: str
    status: str
    next_goal: str
    benchmark_contract: str
    blocker: str
    allowed_claim: str


@dataclass(frozen=True)
class RtCoreAppMaturity:
    app: str
    current_status: str
    target_status: str
    required_action: str
    cloud_policy: str


READY_FOR_RTX_CLAIM_REVIEW = "ready_for_rtx_claim_review"
NEEDS_PHASE_CONTRACT = "needs_phase_contract"
NEEDS_REAL_RTX_ARTIFACT = "needs_real_rtx_artifact"
NEEDS_INTERFACE_TUNING = "needs_interface_tuning"
NEEDS_NATIVE_KERNEL_TUNING = "needs_native_kernel_tuning"
NEEDS_POSTPROCESS_SPLIT = "needs_postprocess_split"
EXCLUDE_FROM_RTX_APP_BENCHMARK = "exclude_from_rtx_app_benchmark"

OPTIX_APP_BENCHMARK_READINESS_STATUSES = (
    READY_FOR_RTX_CLAIM_REVIEW,
    NEEDS_PHASE_CONTRACT,
    NEEDS_REAL_RTX_ARTIFACT,
    NEEDS_INTERFACE_TUNING,
    NEEDS_NATIVE_KERNEL_TUNING,
    NEEDS_POSTPROCESS_SPLIT,
    EXCLUDE_FROM_RTX_APP_BENCHMARK,
)

RT_CORE_READY = "rt_core_ready"
RT_CORE_PARTIAL_READY = "rt_core_partial_ready"
NEEDS_RT_CORE_REDESIGN = "needs_rt_core_redesign"
NEEDS_OPTIX_APP_SURFACE = "needs_optix_app_surface"
NOT_NVIDIA_RT_CORE_TARGET = "not_nvidia_rt_core_target"

RT_CORE_APP_MATURITY_STATUSES = (
    RT_CORE_READY,
    RT_CORE_PARTIAL_READY,
    NEEDS_RT_CORE_REDESIGN,
    NEEDS_OPTIX_APP_SURFACE,
    NOT_NVIDIA_RT_CORE_TARGET,
)


def _support(app: str, engine: str, status: str, note: str) -> AppEngineSupport:
    return AppEngineSupport(app=app, engine=engine, status=status, note=note)


def _row(
    app: str,
    *,
    cpu_python_reference: str,
    embree: str,
    optix: str,
    vulkan: str,
    hiprt: str,
    apple_rt: str,
    note: str,
) -> dict[str, AppEngineSupport]:
    statuses = {
        "cpu_python_reference": cpu_python_reference,
        "embree": embree,
        "optix": optix,
        "vulkan": vulkan,
        "hiprt": hiprt,
        "apple_rt": apple_rt,
    }
    return {engine: _support(app, engine, status, note) for engine, status in statuses.items()}


_CPU = PORTABLE_CPU_ORACLE
_NATIVE = DIRECT_CLI_NATIVE
_ASSISTED = DIRECT_CLI_NATIVE_ASSISTED
_COMPAT = DIRECT_CLI_COMPATIBILITY_FALLBACK
_NOCLI = NOT_EXPOSED_BY_APP_CLI
_APPLE = APPLE_SPECIFIC


_APP_MATRIX: dict[str, dict[str, AppEngineSupport]] = {
    "database_analytics": _row(
        "database_analytics",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Primary DB app exposes CPU/Embree/OptiX/Vulkan; HIPRT and Apple DB feature paths exist below the app layer but are not exposed by this app CLI.",
    ),
    "graph_analytics": _row(
        "graph_analytics",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios; Embree BFS/triangle-count use ray traversal over graph-edge primitives for candidate generation.",
    ),
    "apple_rt_demo": _row(
        "apple_rt_demo",
        cpu_python_reference=PARTIAL_CPU_ORACLE,
        embree=_APPLE,
        optix=_APPLE,
        vulkan=_APPLE,
        hiprt=_APPLE,
        apple_rt=_ASSISTED,
        note="Primary Apple RT demo is Apple-specific; closest-hit has CPU reference parity, visibility-count is hardware-gated and may skip if Apple RT is unavailable.",
    ),
    "service_coverage_gaps": _row(
        "service_coverage_gaps",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial radius-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared gap-summary mode; Vulkan/HIPRT/Apple are not app CLI options.",
    ),
    "event_hotspot_screening": _row(
        "event_hotspot_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial self-join app exposes CPU, Embree, SciPy baseline, and an OptiX prepared count-summary mode.",
    ),
    "facility_knn_assignment": _row(
        "facility_knn_assignment",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial KNN app exposes CPU, Embree, SciPy baseline, and an OptiX prepared coverage-threshold mode. Ranked KNN assignment remains CPU/Embree/SciPy only.",
    ),
    "road_hazard_screening": _row(
        "road_hazard_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection, but native mode is still gated.",
    ),
    "segment_polygon_hitcount": _row(
        "segment_polygon_hitcount",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan; OptiX includes explicit auto/host_indexed/native mode selection.",
    ),
    "segment_polygon_anyhit_rows": _row(
        "segment_polygon_anyhit_rows",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan; explicit --backend optix --output-mode rows --optix-mode native uses the bounded native OptiX pair-row emitter while auto mode remains conservative.",
    ),
    "polygon_pair_overlap_area_rows": _row(
        "polygon_pair_overlap_area_rows",
        cpu_python_reference=_CPU,
        embree=_ASSISTED,
        optix=_ASSISTED,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus CPU exact area refinement.",
    ),
    "polygon_set_jaccard": _row(
        "polygon_set_jaccard",
        cpu_python_reference=_CPU,
        embree=_ASSISTED,
        optix=_ASSISTED,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Public script exposes CPU plus Embree/OptiX native-assisted modes: native LSI/PIP positive candidate discovery plus CPU exact set-area/Jaccard refinement.",
    ),
    "hausdorff_distance": _row(
        "hausdorff_distance",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="KNN app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "ann_candidate_search": _row(
        "ann_candidate_search",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Candidate-search app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "outlier_detection": _row(
        "outlier_detection",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Density app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "dbscan_clustering": _row(
        "dbscan_clustering",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="DBSCAN app exposes CPU, Embree, OptiX, Vulkan, and SciPy baseline.",
    ),
    "robot_collision_screening": _row(
        "robot_collision_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Discrete collision app exposes CPU, Embree, and OptiX; Vulkan is intentionally not exposed until a dedicated any-hit app gate exists.",
    ),
    "barnes_hut_force_app": _row(
        "barnes_hut_force_app",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NATIVE,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Candidate-generation app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "hiprt_ray_triangle_hitcount": _row(
        "hiprt_ray_triangle_hitcount",
        cpu_python_reference=_CPU,
        embree=_NOCLI,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NATIVE,
        apple_rt=_NOCLI,
        note="Scenario-specific HIPRT hit-count demo; HIPRT evidence is SDK/Orochi on tested hosts, not AMD GPU validation.",
    ),
}

_OPTIX_PERFORMANCE_MATRIX: dict[str, OptixAppPerformanceSupport] = {
    "database_analytics": OptixAppPerformanceSupport(
        app="database_analytics",
        performance_class=PYTHON_INTERFACE_DOMINATED,
        note="Uses real OptiX DB BVH candidate discovery and native C++ exact filtering/grouping. App-level performance is still limited by Python/ctypes preparation, candidate bitset copy-back, grouped-row decoding, and row materialization unless materialization-free compact_summary is selected; native-continuation metadata is active only for compact DB summaries that avoid row/group materialization.",
    ),
    "graph_analytics": OptixAppPerformanceSupport(
        app="graph_analytics",
        performance_class=OPTIX_TRAVERSAL,
        note="Explicit visibility_edges mode maps candidate graph edges to ray/triangle any-hit traversal; summary mode uses prepared any-hit count to avoid row materialization. Embree BFS/triangle-count are ray-traversal candidate-generation paths; OptiX BFS and triangle_count now have an explicit native graph-ray mode behind RTDL_OPTIX_GRAPH_MODE=native, and graph summary mode uses native C++ continuation after rows are produced. The default remains host-indexed until RTX validation.",
    ),
    "apple_rt_demo": OptixAppPerformanceSupport(
        app="apple_rt_demo",
        performance_class=NOT_OPTIX_APPLICABLE,
        note="Apple-specific app; OptiX is not an applicable app entry point.",
    ),
    "service_coverage_gaps": OptixAppPerformanceSupport(
        app="service_coverage_gaps",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Explicit gap_summary_prepared mode uses prepared OptiX fixed-radius threshold traversal and compact summary output; rows mode is not the RT-core claim path.",
    ),
    "event_hotspot_screening": OptixAppPerformanceSupport(
        app="event_hotspot_screening",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Explicit count_summary_prepared mode uses prepared OptiX fixed-radius count traversal and compact hotspot summaries; rows mode is not the RT-core claim path.",
    ),
    "facility_knn_assignment": OptixAppPerformanceSupport(
        app="facility_knn_assignment",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Explicit coverage_threshold_prepared mode uses prepared OptiX fixed-radius threshold traversal for service-coverage decisions only; ranked nearest-depot assignment remains outside the OptiX claim.",
    ),
    "road_hazard_screening": OptixAppPerformanceSupport(
        app="road_hazard_screening",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default segment/polygon OptiX app path remains conservative, but the prepared road-hazard summary profiler reuses a polygon BVH and runs native OptiX custom-AABB segment/polygon traversal for compact hazard summaries.",
    ),
    "segment_polygon_hitcount": OptixAppPerformanceSupport(
        app="segment_polygon_hitcount",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default segment/polygon OptiX path remains conservative, but the prepared hit-count profiler reuses a polygon BVH and runs native OptiX custom-AABB traversal for compact hit-count summaries.",
    ),
    "segment_polygon_anyhit_rows": OptixAppPerformanceSupport(
        app="segment_polygon_anyhit_rows",
        performance_class=OPTIX_TRAVERSAL,
        note="Default segment/polygon OptiX pair-row path remains conservative, but the prepared bounded pair-row profiler reuses a polygon BVH and runs native OptiX custom-AABB traversal with bounded output and overflow metadata.",
    ),
    "polygon_pair_overlap_area_rows": OptixAppPerformanceSupport(
        app="polygon_pair_overlap_area_rows",
        performance_class=PYTHON_INTERFACE_DOMINATED,
        note="Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then native C++ exact grid-cell area continuation. This is real traversal-assisted filtering plus native continuation, not a monolithic GPU polygon-area kernel.",
    ),
    "polygon_set_jaccard": OptixAppPerformanceSupport(
        app="polygon_set_jaccard",
        performance_class=PYTHON_INTERFACE_DOMINATED,
        note="Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then native C++ exact grid-cell set-area/Jaccard continuation. This is real traversal-assisted filtering plus native continuation, not a monolithic GPU Jaccard kernel.",
    ),
    "hausdorff_distance": OptixAppPerformanceSupport(
        app="hausdorff_distance",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default exact-distance mode uses KNN rows through CUDA-style kernels; explicit directed_threshold_prepared mode uses prepared OptiX fixed-radius threshold traversal for Hausdorff <= radius decisions only.",
    ),
    "ann_candidate_search": OptixAppPerformanceSupport(
        app="ann_candidate_search",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default candidate reranking uses KNN rows through CUDA-style kernels; explicit candidate_threshold_prepared mode uses prepared OptiX fixed-radius threshold traversal for candidate-coverage decisions only.",
    ),
    "outlier_detection": OptixAppPerformanceSupport(
        app="outlier_detection",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default row path uses fixed-radius rows through CUDA-style kernels; explicit rt_count_threshold_prepared summary uses prepared OptiX traversal and native threshold-count continuation metadata to avoid neighbor-row materialization, with RTX 4090 phase evidence preserved in Goals 793 and 795.",
    ),
    "dbscan_clustering": OptixAppPerformanceSupport(
        app="dbscan_clustering",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default row path uses fixed-radius rows through CUDA-style kernels; explicit rt_core_flags_prepared summary uses prepared OptiX traversal and native threshold-count continuation metadata for core flags only, while Python clustering expansion remains outside the native summary path.",
    ),
    "robot_collision_screening": OptixAppPerformanceSupport(
        app="robot_collision_screening",
        performance_class=OPTIX_TRAVERSAL,
        note="Uses OptiX ray/triangle any-hit traversal and is the best current OptiX flagship candidate; compact row-output modes avoid returning full witness rows, while prepared scalar hit-count and prepared native pose-flag summary modes report native continuation and avoid per-ray row materialization. Edge witnesses still require row mode.",
    ),
    "barnes_hut_force_app": OptixAppPerformanceSupport(
        app="barnes_hut_force_app",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default candidate rows use fixed-radius candidate generation and native C++ continuation for compact candidate summaries. Explicit node_coverage_prepared mode uses prepared OptiX fixed-radius threshold traversal for node-coverage decisions only. Python opening-rule and force reduction remain outside the claim.",
    ),
    "hiprt_ray_triangle_hitcount": OptixAppPerformanceSupport(
        app="hiprt_ray_triangle_hitcount",
        performance_class=NOT_OPTIX_EXPOSED,
        note="HIPRT-specific app; OptiX is not exposed by this public app CLI.",
    ),
}


def _readiness(
    app: str,
    status: str,
    next_goal: str,
    benchmark_contract: str,
    blocker: str,
    allowed_claim: str,
) -> OptixAppBenchmarkReadiness:
    return OptixAppBenchmarkReadiness(
        app=app,
        status=status,
        next_goal=next_goal,
        benchmark_contract=benchmark_contract,
        blocker=blocker,
        allowed_claim=allowed_claim,
    )


_OPTIX_BENCHMARK_READINESS_MATRIX: dict[str, OptixAppBenchmarkReadiness] = {
    "database_analytics": _readiness(
        "database_analytics",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal921/Goal941",
        "Goal941 provides real RTX compact-summary artifacts with native DB phase totals, strict output mode, and no row materialization operations for sales_risk and regional_dashboard",
        "DB claims must stay limited to compact-summary prepared sub-paths; no SQL engine, DBMS, full dashboard, row-materializing, or broad whole-app speedup claim is allowed",
        "prepared DB compact-summary traversal/filter/grouping sub-path may enter claim review; no DBMS or SQL-engine speedup claim",
    ),
    "graph_analytics": _readiness(
        "graph_analytics",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal889/Goal905/Goal929",
        "combined graph gate passed strict RTX validation for visibility any-hit plus native BFS and triangle-count graph-ray candidate generation; public claims still require final claim-review packaging",
        "Goal929 covers bounded graph RT sub-paths only; CPU-side frontier bookkeeping, triangle set-intersection, shortest-path, graph database, distributed analytics, and whole-app graph-system acceleration remain outside the claim",
        "bounded graph visibility any-hit plus native BFS/triangle graph-ray candidate-generation sub-paths may enter claim review; no whole-app graph speedup claim",
    ),
    "apple_rt_demo": _readiness(
        "apple_rt_demo",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "Apple-specific benchmark only; do not include in NVIDIA RTX cloud comparison",
        "OptiX is not an applicable app entry point",
        "Apple RT demo claim only, not NVIDIA OptiX",
    ),
    "service_coverage_gaps": _readiness(
        "service_coverage_gaps",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal917",
        "prepared gap-summary mode has same-scale CPU/Embree baseline parity and a reviewed RTX phase artifact; public claims still require final claim-review packaging",
        "Goal917 covers the bounded prepared gap-summary path only; row output, nearest-clinic output, and whole-app service-coverage optimization remain outside the claim",
        "bounded prepared gap-summary path may enter claim review; no whole-app service-coverage speedup claim",
    ),
    "event_hotspot_screening": _readiness(
        "event_hotspot_screening",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal917/Goal919",
        "prepared count-summary mode has a reviewed RTX phase artifact plus same-scale Embree baseline parity; public claims still require final claim-review packaging",
        "Goal917 and Goal919 cover the bounded prepared count-summary path only; neighbor-row output and whole-app hotspot analytics remain outside the claim",
        "bounded prepared count-summary path may enter claim review; no whole-app hotspot-screening speedup claim",
    ),
    "facility_knn_assignment": _readiness(
        "facility_knn_assignment",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal887/Goal920",
        "coverage_threshold_prepared decision mode has an RTX phase artifact and same-scale CPU oracle parity for the bounded service-coverage decision",
        "ranked nearest-depot assignment remains outside the OptiX claim; only the service-coverage decision sub-path is traversal-backed",
        "bounded prepared facility service-coverage decision sub-path may enter claim review; no KNN assignment or ranking speedup claim",
    ),
    "road_hazard_screening": _readiness(
        "road_hazard_screening",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal933/Goal941",
        "Goal941 provides a real RTX prepared road-hazard artifact with strict digest parity, separated prepare/query/postprocess/validation phases, and native OptiX segment/polygon traversal",
        "claim is limited to the prepared compact road-hazard summary gate; default public app behavior, full GIS/routing, and broad road-hazard speedup remain outside the claim",
        "prepared native road-hazard summary traversal sub-path may enter claim review; no full GIS/routing or default-app speedup claim",
    ),
    "segment_polygon_hitcount": _readiness(
        "segment_polygon_hitcount",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal933/Goal941",
        "Goal941 provides a real RTX prepared segment/polygon hit-count artifact with strict digest parity and separated prepared polygon-BVH query phases",
        "claim is limited to prepared compact hit-count traversal; pair-row output, road-hazard whole-app behavior, and broad speedup remain outside the claim",
        "prepared native segment/polygon hit-count traversal sub-path may enter claim review; no broad segment/polygon app speedup claim",
    ),
    "segment_polygon_anyhit_rows": _readiness(
        "segment_polygon_anyhit_rows",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal934/Goal941",
        "Goal941 provides a real RTX prepared bounded pair-row artifact with strict digest parity, zero overflow, emitted/copied counts, and separated prepare/query/postprocess phases",
        "claim is limited to bounded prepared pair-row traversal at the reviewed output capacity; unbounded row-volume performance and default public app behavior remain outside the claim",
        "prepared bounded native pair-row traversal sub-path may enter claim review; no unbounded pair-row or broad app speedup claim",
    ),
    "polygon_pair_overlap_area_rows": _readiness(
        "polygon_pair_overlap_area_rows",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal877/Goal929",
        "native-assisted OptiX candidate discovery has a phase-separated RTX artifact with parity; public claims still require final claim-review packaging",
        "exact area refinement remains CPU/Python-owned; only candidate discovery may enter claim review",
        "native-assisted candidate-discovery path only; no full polygon-area speedup claim",
    ),
    "polygon_set_jaccard": _readiness(
        "polygon_set_jaccard",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal877/Goal929",
        "native-assisted OptiX candidate discovery has a phase-separated RTX artifact with parity at the reviewed chunk-copies=20 contract; public claims still require final claim-review packaging",
        "exact set-area/Jaccard refinement remains CPU/Python-owned, and larger chunk sizes are diagnostic failures until root-caused",
        "native-assisted candidate-discovery path only; no full Jaccard speedup claim",
    ),
    "hausdorff_distance": _readiness(
        "hausdorff_distance",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal887/Goal941",
        "Goal941 provides a real RTX directed_threshold_prepared artifact with same-semantics oracle parity and separated prepared fixed-radius traversal phases",
        "exact Hausdorff distance, KNN-row output, nearest-neighbor ranking, and whole-app speedup remain outside the claim",
        "prepared Hausdorff <= radius decision sub-path may enter claim review; no exact-distance speedup claim",
    ),
    "ann_candidate_search": _readiness(
        "ann_candidate_search",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal887/Goal941",
        "Goal941 provides a real RTX candidate_threshold_prepared artifact with same-semantics oracle parity and separated prepared fixed-radius traversal phases",
        "full ANN indexing, nearest-neighbor ranking, FAISS/HNSW/IVF/PQ behavior, recall optimization, and whole-app speedup remain outside the claim",
        "prepared ANN candidate-coverage decision sub-path may enter claim review; no full ANN index or ranking speedup claim",
    ),
    "outlier_detection": _readiness(
        "outlier_detection",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal795/Goal992",
        "Goal992 exposes density_count as the public scalar claim path; validation-free RTX timing must split scalar threshold-count traversal, backend/materialization, postprocess, and oracle validation",
        "RTX 4090 evidence covers the prepared scalar threshold-count sub-path only; full anomaly-detection app, per-point outlier labels, and row-returning paths remain outside the claim",
        "prepared fixed-radius scalar threshold-count sub-path may enter claim review; no per-point outlier-label or broad outlier-app speedup claim",
    ),
    "dbscan_clustering": _readiness(
        "dbscan_clustering",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal795/Goal992",
        "Goal992 exposes core_count as the public scalar claim path; core-count timing must be separated from per-point core flags, Python cluster expansion, and validation",
        "RTX 4090 evidence covers the prepared scalar core-count sub-path only; per-point core flags and Python cluster expansion remain outside the native scalar path",
        "prepared fixed-radius scalar core-count sub-path may enter claim review; no per-point core-flag or full DBSCAN clustering acceleration claim",
    ),
    "robot_collision_screening": _readiness(
        "robot_collision_screening",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal795",
        "RTX timing must split prepared-scene build/reuse, ray buffer packing, OptiX traversal, compact output, and oracle validation",
        "RTX 4090 evidence covers prepared scalar pose-count traversal only; full robot kinematics and witness-row output remain outside the claim",
        "prepared ray/triangle any-hit scalar pose-count sub-path may enter claim review; no full robot-planning speedup claim",
    ),
    "barnes_hut_force_app": _readiness(
        "barnes_hut_force_app",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal887/Goal941",
        "Goal941 provides a real RTX node_coverage_prepared artifact with same-semantics oracle parity and separated prepared fixed-radius traversal phases",
        "Barnes-Hut opening-rule evaluation, candidate-row output, force-vector reduction, N-body simulation, and whole-app speedup remain outside the claim",
        "prepared Barnes-Hut node-coverage decision sub-path may enter claim review; no force-vector or opening-rule speedup claim",
    ),
    "hiprt_ray_triangle_hitcount": _readiness(
        "hiprt_ray_triangle_hitcount",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "HIPRT-specific app; not an OptiX app benchmark candidate",
        "public app CLI does not expose OptiX",
        "HIPRT validation only, not NVIDIA OptiX",
    ),
}


def _maturity(
    app: str,
    current_status: str,
    target_status: str,
    required_action: str,
    cloud_policy: str,
) -> RtCoreAppMaturity:
    return RtCoreAppMaturity(
        app=app,
        current_status=current_status,
        target_status=target_status,
        required_action=required_action,
        cloud_policy=cloud_policy,
    )


_RT_CORE_APP_MATURITY_MATRIX: dict[str, RtCoreAppMaturity] = {
    "database_analytics": _maturity(
        "database_analytics",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep compact_summary prepared DB outputs as the only RT-core claim path; row materialization, SQL-engine behavior, and whole-dashboard claims remain outside the RT-core claim.",
        "Goal941 supplies the RTX compact-summary artifacts; no new pod is needed for readiness, but same-semantics baseline review is still required before any public speedup wording.",
    ),
    "graph_analytics": _maturity(
        "graph_analytics",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep visibility_edges any-hit plus explicit native BFS/triangle graph-ray candidate generation as the bounded graph-to-RT lowerings; keep CPU-side frontier bookkeeping and neighbor-set intersection outside the RT-core claim.",
        "Goal929 provides the RTX graph gate artifact; no new pod is needed for readiness, but public graph claims require final claim-review packaging and same-semantics baseline review.",
    ),
    "apple_rt_demo": _maturity(
        "apple_rt_demo",
        NOT_NVIDIA_RT_CORE_TARGET,
        NOT_NVIDIA_RT_CORE_TARGET,
        "Keep as Apple Metal/MPS RT evidence; do not fold into NVIDIA OptiX claim tables.",
        "Never include in NVIDIA cloud batches.",
    ),
    "service_coverage_gaps": _maturity(
        "service_coverage_gaps",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep the prepared OptiX gap-summary path as the RT-core claim path, and prevent row output or nearest-clinic output from being presented as the claim.",
        "No new pod is needed for readiness; use the Goal917 artifact in claim-review packaging, and rerun only as part of a consolidated regression batch.",
    ),
    "event_hotspot_screening": _maturity(
        "event_hotspot_screening",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep the prepared OptiX count-summary path as the RT-core claim path, and prevent neighbor-row output or whole-app hotspot analytics from being presented as the claim.",
        "No new pod is needed for readiness; use the Goal917 RTX artifact and Goal919 same-scale baseline in claim-review packaging, and rerun only as part of a consolidated regression batch.",
    ),
    "facility_knn_assignment": _maturity(
        "facility_knn_assignment",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep coverage_threshold_prepared as the traversal-backed service-coverage decision path; no ranked KNN assignment RT-core claim exists, and KNN ranking/fallback assignment remain outside the RT-core claim until a native ranking design exists.",
        "No new pod is needed for readiness; use the Goal887 RTX artifact and Goal920 same-scale CPU oracle baseline in claim-review packaging, and rerun only as part of a consolidated regression batch.",
    ),
    "road_hazard_screening": _maturity(
        "road_hazard_screening",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep the prepared native road-hazard compact-summary gate separate from default app behavior and full GIS/routing claims.",
        "Goal941 supplies the prepared RTX artifact; no new pod is needed for readiness, but baseline/speedup review must stay bounded to the prepared summary gate.",
    ),
    "segment_polygon_hitcount": _maturity(
        "segment_polygon_hitcount",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep the prepared native hit-count gate separate from pair-row output and broader segment/polygon app claims.",
        "Goal941 supplies the prepared RTX artifact; no new pod is needed for readiness, but public wording must stay limited to compact hit-count traversal.",
    ),
    "segment_polygon_anyhit_rows": _maturity(
        "segment_polygon_anyhit_rows",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep the prepared bounded pair-row gate separate from unbounded row-volume performance and default app behavior.",
        "Goal941 supplies the prepared RTX artifact with zero overflow; no new pod is needed for readiness, but output-capacity and bounded-row wording must remain explicit.",
    ),
    "polygon_pair_overlap_area_rows": _maturity(
        "polygon_pair_overlap_area_rows",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact area refinement; claim only the candidate-discovery sub-path.",
        "Goal929 provides the RTX phase artifact; no new pod is needed for readiness, but no full polygon-area speedup claim is allowed.",
    ),
    "polygon_set_jaccard": _maturity(
        "polygon_set_jaccard",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact set-area/Jaccard refinement; claim only the reviewed chunked candidate-discovery sub-path.",
        "Goal929 provides the RTX phase artifact at chunk-copies=20; no new pod is needed for readiness, but larger chunks remain held and no full Jaccard speedup claim is allowed.",
    ),
    "hausdorff_distance": _maturity(
        "hausdorff_distance",
        RT_CORE_READY,
        RT_CORE_READY,
        "Use directed_threshold_prepared as the only RT-core Hausdorff claim path; exact-distance KNN rows remain outside the claim.",
        "Goal941 supplies the RTX threshold-decision artifact; no new pod is needed for readiness, but exact Hausdorff speedup wording remains forbidden.",
    ),
    "ann_candidate_search": _maturity(
        "ann_candidate_search",
        RT_CORE_READY,
        RT_CORE_READY,
        "Use candidate_threshold_prepared as the only RT-core ANN claim path; KNN ranking and full ANN indexing remain outside the claim.",
        "Goal941 supplies the RTX candidate-coverage artifact; no new pod is needed for readiness, but full ANN/ranking speedup wording remains forbidden.",
    ),
    "outlier_detection": _maturity(
        "outlier_detection",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep --output-mode density_count with prepared scalar threshold-count as the RT-core claim path and prevent default rows or per-point labels from being presented as the claim.",
        "No new pod is needed for readiness; rerun only in a consolidated regression/tuning batch with the prepared scalar profiler.",
    ),
    "dbscan_clustering": _maturity(
        "dbscan_clustering",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep --output-mode core_count with prepared scalar core-count as the RT-core claim path and split per-point core flags plus Python cluster expansion from native timing.",
        "No new pod is needed for readiness; rerun only in a consolidated regression/tuning batch with the prepared scalar profiler.",
    ),
    "robot_collision_screening": _maturity(
        "robot_collision_screening",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep prepared ray/triangle any-hit scalar pose-count as the flagship RT-core path and expand only with phase-clean profilers.",
        "Include in the next batched cloud run with prepared packed input and scalar pose-count mode.",
    ),
    "barnes_hut_force_app": _maturity(
        "barnes_hut_force_app",
        RT_CORE_READY,
        RT_CORE_READY,
        "Use node_coverage_prepared as the only RT-core Barnes-Hut claim path. Native C++ candidate-summary continuation is allowed as an app postprocess improvement, but opening-rule evaluation, force-vector reduction, and N-body simulation remain outside the RT-core claim.",
        "Goal941 supplies the RTX node-coverage artifact; no new pod is needed for readiness, but force-vector/opening-rule speedup wording remains forbidden.",
    ),
    "hiprt_ray_triangle_hitcount": _maturity(
        "hiprt_ray_triangle_hitcount",
        NOT_NVIDIA_RT_CORE_TARGET,
        NOT_NVIDIA_RT_CORE_TARGET,
        "Keep as HIPRT-specific validation; do not fold into NVIDIA OptiX app maturity.",
        "Never include in NVIDIA OptiX cloud batches.",
    ),
}


def public_apps() -> tuple[str, ...]:
    return tuple(_APP_MATRIX)


def app_engine_support(app: str, engine: str) -> AppEngineSupport:
    try:
        return _APP_MATRIX[app][engine]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL app/engine pair: app={app!r}, engine={engine!r}") from exc


def app_engine_support_matrix() -> dict[str, dict[str, AppEngineSupport]]:
    return {app: dict(entries) for app, entries in _APP_MATRIX.items()}


def optix_app_performance_support(app: str) -> OptixAppPerformanceSupport:
    try:
        return _OPTIX_PERFORMANCE_MATRIX[app]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL app: app={app!r}") from exc


def optix_app_performance_matrix() -> dict[str, OptixAppPerformanceSupport]:
    return dict(_OPTIX_PERFORMANCE_MATRIX)


def optix_app_benchmark_readiness(app: str) -> OptixAppBenchmarkReadiness:
    try:
        return _OPTIX_BENCHMARK_READINESS_MATRIX[app]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL app: app={app!r}") from exc


def optix_app_benchmark_readiness_matrix() -> dict[str, OptixAppBenchmarkReadiness]:
    return dict(_OPTIX_BENCHMARK_READINESS_MATRIX)


def rt_core_app_maturity(app: str) -> RtCoreAppMaturity:
    try:
        return _RT_CORE_APP_MATURITY_MATRIX[app]
    except KeyError as exc:
        raise ValueError(f"unknown RTDL app: app={app!r}") from exc


def rt_core_app_maturity_matrix() -> dict[str, RtCoreAppMaturity]:
    return dict(_RT_CORE_APP_MATURITY_MATRIX)
