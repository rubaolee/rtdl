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
NEEDS_INTERFACE_TUNING = "needs_interface_tuning"
NEEDS_NATIVE_KERNEL_TUNING = "needs_native_kernel_tuning"
NEEDS_POSTPROCESS_SPLIT = "needs_postprocess_split"
EXCLUDE_FROM_RTX_APP_BENCHMARK = "exclude_from_rtx_app_benchmark"

OPTIX_APP_BENCHMARK_READINESS_STATUSES = (
    READY_FOR_RTX_CLAIM_REVIEW,
    NEEDS_PHASE_CONTRACT,
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
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial radius-join app currently exposes CPU, Embree, and SciPy baseline; other RT engines are not app CLI options.",
    ),
    "event_hotspot_screening": _row(
        "event_hotspot_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial self-join app currently exposes CPU, Embree, and SciPy baseline.",
    ),
    "facility_knn_assignment": _row(
        "facility_knn_assignment",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Spatial KNN app currently exposes CPU, Embree, and SciPy baseline.",
    ),
    "road_hazard_screening": _row(
        "road_hazard_screening",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Segment/polygon app exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "segment_polygon_hitcount": _row(
        "segment_polygon_hitcount",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon example exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "segment_polygon_anyhit_rows": _row(
        "segment_polygon_anyhit_rows",
        cpu_python_reference=_CPU,
        embree=_NATIVE,
        optix=_COMPAT,
        vulkan=_NATIVE,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Released segment/polygon pair-emitting example exposes CPU, Embree, OptiX, and Vulkan.",
    ),
    "polygon_pair_overlap_area_rows": _row(
        "polygon_pair_overlap_area_rows",
        cpu_python_reference=_CPU,
        embree=_ASSISTED,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Public script exposes CPU and Embree native-assisted mode: Embree overlay/candidate discovery plus CPU exact area refinement.",
    ),
    "polygon_set_jaccard": _row(
        "polygon_set_jaccard",
        cpu_python_reference=_CPU,
        embree=_ASSISTED,
        optix=_NOCLI,
        vulkan=_NOCLI,
        hiprt=_NOCLI,
        apple_rt=_NOCLI,
        note="Public script exposes CPU and Embree native-assisted mode: Embree overlay/candidate discovery plus CPU exact set-area/Jaccard refinement.",
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
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public app CLI does not expose OptiX today.",
    ),
    "event_hotspot_screening": OptixAppPerformanceSupport(
        app="event_hotspot_screening",
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public app CLI does not expose OptiX today.",
    ),
    "facility_knn_assignment": OptixAppPerformanceSupport(
        app="facility_knn_assignment",
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public app CLI does not expose OptiX today.",
    ),
    "road_hazard_screening": OptixAppPerformanceSupport(
        app="road_hazard_screening",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX app path uses host-indexed candidate reduction unless native OptiX mode is explicitly enabled and separately gated.",
    ),
    "segment_polygon_hitcount": OptixAppPerformanceSupport(
        app="segment_polygon_hitcount",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX path is host-indexed; native OptiX mode must be promoted only after correctness and performance gates.",
    ),
    "segment_polygon_anyhit_rows": OptixAppPerformanceSupport(
        app="segment_polygon_anyhit_rows",
        performance_class=HOST_INDEXED_FALLBACK,
        note="Default segment/polygon OptiX pair-row path is host-indexed and can also be row-volume dominated.",
    ),
    "polygon_pair_overlap_area_rows": OptixAppPerformanceSupport(
        app="polygon_pair_overlap_area_rows",
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public script is CPU-reference only today.",
    ),
    "polygon_set_jaccard": OptixAppPerformanceSupport(
        app="polygon_set_jaccard",
        performance_class=NOT_OPTIX_EXPOSED,
        note="Public script is CPU-reference only today.",
    ),
    "hausdorff_distance": OptixAppPerformanceSupport(
        app="hausdorff_distance",
        performance_class=CUDA_THROUGH_OPTIX,
        note="Uses KNN rows through CUDA-style kernels in the OptiX backend library; useful GPU compute, but not an RT-core traversal claim.",
    ),
    "ann_candidate_search": OptixAppPerformanceSupport(
        app="ann_candidate_search",
        performance_class=CUDA_THROUGH_OPTIX,
        note="Uses KNN rows through CUDA-style kernels in the OptiX backend library; recall metrics remain app/Python work.",
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
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "not an OptiX-exposed app today",
        "public app CLI does not expose OptiX",
        "CPU/Embree/SciPy baseline app only until an OptiX path is added",
    ),
    "event_hotspot_screening": _readiness(
        "event_hotspot_screening",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "not an OptiX-exposed app today",
        "public app CLI does not expose OptiX",
        "CPU/Embree/SciPy baseline app only until an OptiX path is added",
    ),
    "facility_knn_assignment": _readiness(
        "facility_knn_assignment",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "not an OptiX-exposed app today",
        "public app CLI does not expose OptiX",
        "CPU/Embree/SciPy baseline app only until an OptiX path is added",
    ),
    "road_hazard_screening": _readiness(
        "road_hazard_screening",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal708",
        "segment/polygon OptiX benchmark must use the native any-hit/hit-count path and compact outputs, not host-indexed fallback",
        "default app path remains host-indexed fallback",
        "no RTX road-hazard speedup claim today",
    ),
    "segment_polygon_hitcount": _readiness(
        "segment_polygon_hitcount",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal708",
        "native OptiX hit-count mode must be the measured path and must be separated from host-indexed fallback",
        "default app path remains host-indexed fallback",
        "no RTX segment/polygon hit-count speedup claim today",
    ),
    "segment_polygon_anyhit_rows": _readiness(
        "segment_polygon_anyhit_rows",
        NEEDS_NATIVE_KERNEL_TUNING,
        "Goal708",
        "benchmark must first promote and gate a native OptiX any-hit path, then compare row output against compact segment flags/counts",
        "default app path remains host-indexed fallback, and pair-row output volume can dominate after native traversal is promoted",
        "no RTX pair-row speedup claim today",
    ),
    "polygon_pair_overlap_area_rows": _readiness(
        "polygon_pair_overlap_area_rows",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "CPU-reference script only today",
        "public app CLI does not expose OptiX",
        "CPU correctness app only",
    ),
    "polygon_set_jaccard": _readiness(
        "polygon_set_jaccard",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "none",
        "CPU-reference script only today",
        "public app CLI does not expose OptiX",
        "CPU correctness app only",
    ),
    "hausdorff_distance": _readiness(
        "hausdorff_distance",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "Goal709",
        "must be redesigned or explicitly benchmarked as CUDA/GPU compute, not RT-core traversal",
        "current OptiX path is CUDA-through-OptiX KNN rows",
        "GPU-compute comparison only; no RT-core acceleration claim",
    ),
    "ann_candidate_search": _readiness(
        "ann_candidate_search",
        EXCLUDE_FROM_RTX_APP_BENCHMARK,
        "Goal709",
        "must be benchmarked against ANN/KNN baselines as GPU compute unless a true traversal design is implemented",
        "current OptiX path is CUDA-through-OptiX KNN rows",
        "GPU-compute comparison only; no RT-core acceleration claim",
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
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only if the radius-join slice is implemented as true prepared traversal or compact native summary.",
        "Cloud only after local OptiX surface, correctness tests, and phase-clean profiler exist.",
    ),
    "event_hotspot_screening": _maturity(
        "event_hotspot_screening",
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only if self-join candidate discovery and compact summaries use true RT traversal.",
        "Cloud only after local OptiX surface, correctness tests, and phase-clean profiler exist.",
    ),
    "facility_knn_assignment": _maturity(
        "facility_knn_assignment",
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only if KNN assignment is redesigned around a true RT traversal primitive rather than CUDA-through-OptiX KNN rows.",
        "Cloud only after a native traversal design exists.",
    ),
    "road_hazard_screening": _maturity(
        "road_hazard_screening",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Promote a native segment/polygon compact summary path and make the road-hazard app use it by default for OptiX.",
        "No paid RTX road-hazard benchmark while the public path is host-indexed.",
    ),
    "segment_polygon_hitcount": _maturity(
        "segment_polygon_hitcount",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Turn the env-gated native hit-count path into a default, profiled, correctness-gated path only if it beats or justifies replacing host-indexed fallback.",
        "Cloud only in a focused native-vs-host-indexed-vs-PostGIS batch after local gate passes.",
    ),
    "segment_polygon_anyhit_rows": _maturity(
        "segment_polygon_anyhit_rows",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Implement native OptiX any-hit rows or compact flags/counts; avoid broad row-output speedup claims when row volume dominates.",
        "No cloud benchmark until native any-hit or compact summary exists locally.",
    ),
    "polygon_pair_overlap_area_rows": _maturity(
        "polygon_pair_overlap_area_rows",
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only after polygon-pair overlap is mapped to true traversal plus bounded exact refinement.",
        "Cloud only after native OptiX surface and local correctness gate exist.",
    ),
    "polygon_set_jaccard": _maturity(
        "polygon_set_jaccard",
        NEEDS_OPTIX_APP_SURFACE,
        RT_CORE_READY,
        "Add an OptiX app surface only after Jaccard candidate discovery and compact overlap summaries use true traversal.",
        "Cloud only after native OptiX surface and local correctness gate exist.",
    ),
    "hausdorff_distance": _maturity(
        "hausdorff_distance",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Replace CUDA-through-OptiX KNN rows with a true traversal-friendly Hausdorff candidate/summary design or keep it as GPU-compute only.",
        "No RT-core cloud claim until a true traversal design exists.",
    ),
    "ann_candidate_search": _maturity(
        "ann_candidate_search",
        NEEDS_RT_CORE_REDESIGN,
        RT_CORE_READY,
        "Redesign candidate search around a true RT traversal primitive or keep it as GPU-compute/re-ranking evidence.",
        "No RT-core cloud claim until a true traversal design exists.",
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
