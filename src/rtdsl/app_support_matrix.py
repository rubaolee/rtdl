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
        note="Primary graph app exposes CPU/Embree/OptiX/Vulkan for BFS and triangle-count scenarios.",
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
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial KNN app currently exposes CPU, Embree, and SciPy baseline. It intentionally does not expose OptiX because KNN ranking needs nearest-neighbor ordering, not fixed-radius threshold summaries.",
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
        note="Uses real OptiX DB BVH candidate discovery and native C++ exact filtering/grouping. App-level performance is still limited by Python/ctypes preparation, candidate bitset copy-back, grouped-row decoding, and row materialization unless compact_summary is selected.",
    ),
    "graph_analytics": OptixAppPerformanceSupport(
        app="graph_analytics",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Current OptiX-facing BFS and triangle routines are host-indexed correctness paths, not dominant OptiX ray traversal or RT-core acceleration paths.",
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
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public app CLI does not expose OptiX today. Existing generic OptiX KNN support is CUDA-through-OptiX, and fixed-radius threshold traversal cannot emit ranked nearest-depot assignments.",
    ),
    "road_hazard_screening": OptixAppPerformanceSupport(
        app="road_hazard_screening",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX app path uses host-indexed candidate reduction. Explicit native mode is now exposed for hit-count execution, but remains separately gated before any RT-core claim.",
    ),
    "segment_polygon_hitcount": OptixAppPerformanceSupport(
        app="segment_polygon_hitcount",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX path is host-indexed; explicit native OptiX mode exists and must pass Goal807 strict correctness/performance gating before promotion.",
    ),
    "segment_polygon_anyhit_rows": OptixAppPerformanceSupport(
        app="segment_polygon_anyhit_rows",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX pair-row path remains conservative, but explicit --output-mode rows --optix-mode native now calls the bounded native OptiX pair-row emitter. This is a true traversal path that still needs a real RTX artifact and overflow-free phase review before speedup claims.",
    ),
    "polygon_pair_overlap_area_rows": OptixAppPerformanceSupport(
        app="polygon_pair_overlap_area_rows",
        performance_class=PYTHON_INTERFACE_DOMINATED,
        note="Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then CPU/Python exact grid-cell area refinement. This is real traversal-assisted filtering, not a fully native polygon-area kernel.",
    ),
    "polygon_set_jaccard": OptixAppPerformanceSupport(
        app="polygon_set_jaccard",
        performance_class=PYTHON_INTERFACE_DOMINATED,
        note="Public app exposes OptiX native-assisted LSI/PIP positive candidate discovery, then CPU/Python exact grid-cell set-area/Jaccard refinement. This is real traversal-assisted filtering, not a fully native Jaccard kernel.",
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
        note="Default row path uses fixed-radius rows through CUDA-style kernels; explicit rt_count_threshold_prepared summary uses prepared OptiX traversal to avoid neighbor-row materialization, with RTX 4090 phase evidence preserved in Goals 793 and 795.",
    ),
    "dbscan_clustering": OptixAppPerformanceSupport(
        app="dbscan_clustering",
        performance_class=OPTIX_TRAVERSAL_PREPARED_SUMMARY,
        note="Default row path uses fixed-radius rows through CUDA-style kernels; explicit rt_core_flags_prepared summary uses prepared OptiX traversal for core flags only, while Python clustering expansion remains outside the native summary path.",
    ),
    "robot_collision_screening": OptixAppPerformanceSupport(
        app="robot_collision_screening",
        performance_class=OPTIX_TRAVERSAL,
        note="Uses OptiX ray/triangle any-hit traversal and is the best current OptiX flagship candidate; compact app output avoids returning full witness rows when only pose flags or hit counts are needed. OptiX has prepared scalar hit-count and prepared native pose-flag summary modes, while edge witnesses still require row mode.",
    ),
    "barnes_hut_force_app": OptixAppPerformanceSupport(
        app="barnes_hut_force_app",
        performance_class=CUDA_THROUGH_OPTIX,
        note="Candidate generation uses KNN/radius-style GPU compute; Python tree/opening-rule/force reduction dominates the end-to-end app.",
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
        NEEDS_INTERFACE_TUNING,
        "Goal706",
        "prepared dataset timing must split packing, BVH/build, launch/traversal, copy-back, exact filtering, grouping, and Python materialization",
        "candidate bitset copy-back, native host-side exact filtering/grouping, grouped-row decoding, and row materialization still need finer phase evidence",
        "correctness-capable OptiX DB path only; no RTX app speedup claim yet",
    ),
    "graph_analytics": _readiness(
        "graph_analytics",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal707",
        "BFS and triangle-count must run native GPU/OptiX traversal or be explicitly excluded from RTX app benchmarking",
        "current OptiX-facing graph paths are host-indexed correctness paths",
        "no RTX graph acceleration claim today",
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
        NEEDS_REAL_RTX_ARTIFACT,
        "Goal862",
        "prepared gap-summary mode already has local dry-run and same-semantics baseline evidence; promotion now requires a real RTX optix-mode artifact reviewed against those local baselines",
        "local phase-contract and required baseline work are complete, but no real RTX phase artifact has been recorded for this app yet",
        "bounded prepared gap-summary path only; no whole-app service-coverage speedup claim",
    ),
    "event_hotspot_screening": _readiness(
        "event_hotspot_screening",
        NEEDS_REAL_RTX_ARTIFACT,
        "Goal862",
        "prepared count-summary mode already has local dry-run and same-semantics baseline evidence; promotion now requires a real RTX optix-mode artifact reviewed against those local baselines",
        "local phase-contract and required baseline work are complete, but no real RTX phase artifact has been recorded for this app yet",
        "bounded prepared count-summary path only; no whole-app hotspot-screening speedup claim",
    ),
    "facility_knn_assignment": _readiness(
        "facility_knn_assignment",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "not an OptiX-exposed app today; a future path must prove traversal-based KNN ranking, not only threshold counts",
        "public app CLI does not expose OptiX because the current fixed-radius prepared primitive cannot produce nearest-neighbor ordering",
        "CPU/Embree/SciPy baseline app only until a real RT traversal plus ranking design is added",
    ),
    "road_hazard_screening": _readiness(
        "road_hazard_screening",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal807/808",
        "segment/polygon OptiX benchmark must use the explicit native hit-count path and compact outputs, not default host-indexed fallback",
        "native app mode exists, but strict RTX gate has not passed",
        "no RTX road-hazard speedup claim today",
    ),
    "segment_polygon_hitcount": _readiness(
        "segment_polygon_hitcount",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal807",
        "native OptiX hit-count mode must pass the Goal807 strict gate and be separated from host-indexed fallback",
        "explicit native mode exists, but strict RTX gate has not passed",
        "no RTX segment/polygon hit-count speedup claim today",
    ),
    "segment_polygon_anyhit_rows": _readiness(
        "segment_polygon_anyhit_rows",
        NEEDS_REAL_RTX_ARTIFACT,
        "Goal873",
        "explicit native bounded pair-row output must pass the Goal873 strict RTX gate before any default-public-path or speedup claim",
        "native bounded pair-row emitter is now exposed through explicit app CLI mode, but strict RTX artifact review has not passed",
        "native bounded pair-row traversal path only; no pair-row speedup claim today",
    ),
    "polygon_pair_overlap_area_rows": _readiness(
        "polygon_pair_overlap_area_rows",
        NEEDS_INTERFACE_TUNING,
        "Goal876",
        "native-assisted OptiX candidate discovery must split LSI/PIP traversal, candidate copyback, and CPU exact area refinement before any claim",
        "OptiX app surface exists, but exact area refinement is CPU/Python-owned and no RTX phase artifact exists",
        "native-assisted candidate-discovery path only; no full polygon-area speedup claim",
    ),
    "polygon_set_jaccard": _readiness(
        "polygon_set_jaccard",
        NEEDS_INTERFACE_TUNING,
        "Goal876",
        "native-assisted OptiX candidate discovery must split LSI/PIP traversal, candidate copyback, and CPU exact set-area/Jaccard refinement before any claim",
        "OptiX app surface exists, but exact set-area/Jaccard refinement is CPU/Python-owned and no RTX phase artifact exists",
        "native-assisted candidate-discovery path only; no full Jaccard speedup claim",
    ),
    "hausdorff_distance": _readiness(
        "hausdorff_distance",
        NEEDS_REAL_RTX_ARTIFACT,
        "Goal879",
        "directed_threshold_prepared decision mode needs RTX phase artifact and same-semantics threshold-decision baselines before any claim",
        "exact Hausdorff distance remains CUDA-through-OptiX KNN rows; only the threshold decision sub-path is traversal-backed",
        "prepared Hausdorff <= radius decision sub-path only; no exact-distance speedup claim",
    ),
    "ann_candidate_search": _readiness(
        "ann_candidate_search",
        NEEDS_REAL_RTX_ARTIFACT,
        "Goal880",
        "candidate_threshold_prepared decision mode needs RTX phase artifact and same-semantics threshold-decision baselines before any claim",
        "candidate reranking remains CUDA-through-OptiX KNN rows; only the threshold decision sub-path is traversal-backed",
        "prepared ANN candidate-coverage decision sub-path only; no full ANN index or ranking speedup claim",
    ),
    "outlier_detection": _readiness(
        "outlier_detection",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal795",
        "validation-free RTX timing must split rows versus rt_count_threshold summary, backend/materialization, postprocess, and oracle validation",
        "RTX 4090 evidence covers the prepared scalar threshold-count sub-path only; full anomaly-detection app and row-returning paths remain outside the claim",
        "prepared fixed-radius scalar threshold-count sub-path may enter claim review; no broad outlier-app speedup claim",
    ),
    "dbscan_clustering": _readiness(
        "dbscan_clustering",
        READY_FOR_RTX_CLAIM_REVIEW,
        "Goal795",
        "core-flag summary timing must be separated from Python cluster expansion and validation",
        "RTX 4090 evidence covers the prepared scalar core-threshold sub-path only; Python cluster expansion remains outside the native summary path",
        "prepared fixed-radius core-threshold summary may enter claim review; no full DBSCAN clustering acceleration claim",
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
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "Goal709",
        "must be benchmarked as CUDA/GPU compute or redesigned around a valid traversal primitive",
        "current app is CUDA-through-OptiX plus Python tree/opening-rule/reduction work",
        "no RT-core Barnes-Hut claim today",
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
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Use compact prepared-kernel outputs where the app needs counts/summaries, then add native phase counters proving Python is orchestration only.",
        "No broad DB speedup claim until compact_summary is rerun on RTX hardware and native phase counters prove materialization is not dominant.",
    ),
    "graph_analytics": _maturity(
        "graph_analytics",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Replace host-indexed CSR helpers with a real graph-to-RT lowering or explicitly remove graph from NVIDIA RT-core app targets.",
        "No paid graph RTX benchmark until a native traversal design and local correctness gate exist.",
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
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Keep the prepared OptiX gap-summary path bounded, then collect and review a real RTX phase artifact against the completed local baseline set before any claim.",
        "Cloud only after local profiler/baseline packaging is complete, and then only as a bounded RTX artifact batch; do not restart paid pods per app.",
    ),
    "event_hotspot_screening": _maturity(
        "event_hotspot_screening",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Keep the prepared OptiX count-summary path bounded, then collect and review a real RTX phase artifact against the completed local baseline set before any claim.",
        "Cloud only after local profiler/baseline packaging is complete, and then only as a bounded RTX artifact batch; do not restart paid pods per app.",
    ),
    "facility_knn_assignment": _maturity(
        "facility_knn_assignment",
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only if KNN assignment is redesigned around a true RT traversal plus native ranking primitive rather than CUDA-through-OptiX KNN rows or fixed-radius count thresholds.",
        "Cloud only after a native traversal/ranking design exists and has a local correctness gate.",
    ),
    "road_hazard_screening": _maturity(
        "road_hazard_screening",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Run the explicit native segment/polygon mode through Goal807 strict RTX gating before changing default OptiX behavior or claims.",
        "Cloud only in the focused Goal807 native-vs-host-indexed batch; no road-hazard speedup claim until that passes.",
    ),
    "segment_polygon_hitcount": _maturity(
        "segment_polygon_hitcount",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Use Goal807 to prove explicit native hit-count correctness/performance against host-indexed and PostGIS where available before promotion.",
        "Cloud only in a focused Goal807 native-vs-host-indexed batch after local gate packaging is complete.",
    ),
    "segment_polygon_anyhit_rows": _maturity(
        "segment_polygon_anyhit_rows",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Run the explicit native bounded pair-row app mode through Goal873 strict RTX validation, then decide whether to promote the default public rows path or keep native mode as an explicit bounded gate.",
        "Cloud only after the deferred Goal873 strict gate has a prepared batch slot; require row-digest parity, zero overflow, and independent review on RTX hardware.",
    ),
    "polygon_pair_overlap_area_rows": _maturity(
        "polygon_pair_overlap_area_rows",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact area refinement; add a phase profiler before any cloud claim.",
        "Cloud only after a local phase contract exists for candidate traversal, copyback, and CPU exact refinement.",
    ),
    "polygon_set_jaccard": _maturity(
        "polygon_set_jaccard",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Keep OptiX native-assisted LSI/PIP candidate discovery split from CPU exact set-area/Jaccard refinement; add a phase profiler before any cloud claim.",
        "Cloud only after a local phase contract exists for candidate traversal, copyback, and CPU exact refinement.",
    ),
    "hausdorff_distance": _maturity(
        "hausdorff_distance",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Use directed_threshold_prepared for traversal-backed Hausdorff decision workloads; exact-distance KNN rows remain outside the RT-core claim until a native ranking design exists.",
        "Cloud only after the threshold-decision profiler and baselines are packaged; no exact Hausdorff distance RT-core claim.",
    ),
    "ann_candidate_search": _maturity(
        "ann_candidate_search",
        RT_CORE_PARTIAL_READY,
        RT_CORE_READY,
        "Use candidate_threshold_prepared for traversal-backed candidate-coverage decisions; candidate-subset KNN ranking remains outside the RT-core claim until a native ranking design exists.",
        "Cloud only after the candidate-threshold profiler and baselines are packaged; no full ANN or ranking RT-core claim.",
    ),
    "outlier_detection": _maturity(
        "outlier_detection",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep prepared scalar threshold-count as the RT-core claim path and prevent default row mode from being presented as the claim.",
        "Include in the next batched cloud run only with the prepared scalar profiler.",
    ),
    "dbscan_clustering": _maturity(
        "dbscan_clustering",
        RT_CORE_READY,
        RT_CORE_READY,
        "Keep prepared scalar core-threshold summary as the RT-core claim path and split Python cluster expansion from native timing.",
        "Include in the next batched cloud run only with the prepared scalar profiler.",
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
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Redesign node candidate discovery around a true RT traversal primitive and keep force/opening reduction split from RTDL traversal timing.",
        "No RT-core cloud claim until a true traversal design exists.",
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
