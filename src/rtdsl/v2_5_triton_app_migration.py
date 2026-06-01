from __future__ import annotations

from dataclasses import dataclass

from .partner_continuation_protocol import V2_5_PARTNER_CONTINUATION_VERSION
from .partner_continuation_protocol import V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER
from .v2_5_partner_selection_guidance import V2_5_PARTNER_SELECTION_GUIDANCE_VERSION
from .v2_5_partner_selection_guidance import plan_v2_5_partner_selection


V2_5_TRITON_APP_MIGRATION_VERSION = "rtdl.v2_5.triton_app_migration.v1"
V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS = (
    "segmented_count_i64",
    "segmented_sum_f64",
    "segmented_min_f64",
    "segmented_max_f64",
    "compact_mask_i64",
    "bounded_collect_finalize_i64",
    "grouped_argmin_f64",
    "grouped_argmax_f64",
    "grouped_topk_f64",
    "grouped_vector_sum_f64x2",
)
V2_5_TIERED_BENCHMARK_MANIFEST_VERSION = "rtdl.v2_5.tiered_benchmark_manifest.v1"


@dataclass(frozen=True)
class V25TritonBenchmarkAppPlan:
    app_id: str
    benchmark_name: str
    promoted_benchmark: bool
    current_hot_path_partner: str
    v2_5_required_operations: tuple[str, ...]
    v2_5_status: str
    first_port_action: str
    notes: str
    measured_selection_shapes: tuple[tuple[str, str], ...] = ()

    def to_metadata(self) -> dict[str, object]:
        partner_selection_guidance = tuple(
            plan_v2_5_partner_selection(operation, workload_shape)
            for operation, workload_shape in self.measured_selection_shapes
        )
        measured_negative_guidance_count = sum(
            1
            for guidance in partner_selection_guidance
            if guidance["status"] == "measured_negative_preview_guidance"
        )
        measured_mixed_guidance_count = sum(
            1
            for guidance in partner_selection_guidance
            if guidance["status"] == "measured_mixed_preview_guidance"
        )
        return {
            "app_id": self.app_id,
            "benchmark_name": self.benchmark_name,
            "promoted_benchmark": self.promoted_benchmark,
            "current_hot_path_partner": self.current_hot_path_partner,
            "v2_5_required_operations": self.v2_5_required_operations,
            "v2_5_status": self.v2_5_status,
            "first_port_action": self.first_port_action,
            "notes": self.notes,
            "partner_selection_guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
            "partner_selection_guidance": partner_selection_guidance,
            "measured_negative_preview_guidance_count": measured_negative_guidance_count,
            "measured_mixed_preview_guidance_count": measured_mixed_guidance_count,
            "auto_select_preview_partner_allowed": False,
        }


@dataclass(frozen=True)
class V25TieredBenchmarkManifestRow:
    app_id: str
    tier: str
    benchmark_track: str
    parity_target: str
    canonical_harness_status: str
    same_contract_opponent: str
    required_partner_operations: tuple[str, ...]
    pod_evidence_status: str
    next_action: str

    def to_metadata(self) -> dict[str, object]:
        return {
            "app_id": self.app_id,
            "tier": self.tier,
            "benchmark_track": self.benchmark_track,
            "parity_target": self.parity_target,
            "canonical_harness_status": self.canonical_harness_status,
            "same_contract_opponent": self.same_contract_opponent,
            "required_partner_operations": self.required_partner_operations,
            "pod_evidence_status": self.pod_evidence_status,
            "next_action": self.next_action,
        }


V2_5_TRITON_BENCHMARK_APP_PLANS: tuple[V25TritonBenchmarkAppPlan, ...] = (
    V25TritonBenchmarkAppPlan(
        app_id="raydb_style",
        benchmark_name="RayDB-style grouped aggregates",
        promoted_benchmark=True,
        current_hot_path_partner="primitive_first_fused_rtdl_for_grouped_scalar_reductions",
        v2_5_required_operations=("segmented_count_i64", "segmented_sum_f64", "segmented_min_f64", "segmented_max_f64"),
        v2_5_status="primitive_first_after_Goal2896_same_contract_perf_gate_hit_stream_reserved_for_unfused_continuations",
        first_port_action=(
            "Route grouped count/sum/min/max to the prepared fused RTDL primitive; "
            "reserve typed hit-stream adapters for unfused continuations. Goal2896 "
            "is the current same-contract performance-decision gate."
        ),
        notes=(
            "Goal2896 measured the prepared hit-stream plus Triton path as "
            "22.58x-205.08x slower than primitive-first for RayDB count/sum on "
            "the RTX A5000 pod. Do not promote Triton simply to use Triton."
        ),
        measured_selection_shapes=(
            ("segmented_count_i64", "raydb_scalar_grouped_reduction_frontdoor"),
            ("segmented_sum_f64", "raydb_scalar_grouped_reduction_frontdoor"),
            ("segmented_min_f64", "raydb_scalar_grouped_reduction_frontdoor"),
            ("segmented_max_f64", "raydb_scalar_grouped_reduction_frontdoor"),
        ),
    ),
    V25TritonBenchmarkAppPlan(
        app_id="spatial_rayjoin",
        benchmark_name="Spatial RayJoin",
        promoted_benchmark=True,
        current_hot_path_partner="primitive_first_prepared_generic_rtdl_count_or_parity",
        v2_5_required_operations=("segmented_count_i64", "compact_mask_i64"),
        v2_5_status="primitive_first_plan_native_rt_count_not_relabelled_as_triton",
        first_port_action="Keep prepared RTDL count/parity paths on fused generic primitives; add Triton only for optional compact/grouped post-processing.",
        notes="Primitive-first rule applies: Spatial RayJoin count/parity timing should not be routed through a partner just to use a partner.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="librts_spatial_index",
        benchmark_name="LibRTS-style AABB index query",
        promoted_benchmark=True,
        current_hot_path_partner="primitive_first_prepared_generic_aabb_index_query_2d",
        v2_5_required_operations=("segmented_count_i64",),
        v2_5_status="primitive_first_plan_native_aabb_query_not_relabelled_as_triton",
        first_port_action="Keep point/range count queries on prepared AABB_INDEX_QUERY_2D; use Triton only for optional grouped summaries outside the native query path.",
        notes="The existing performance path is the fused generic AABB query primitive, not a partner continuation.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="hausdorff_xhd",
        benchmark_name="Hausdorff/X-HD",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_some_exact_partner_continuations",
        v2_5_required_operations=("grouped_argmin_f64", "grouped_argmax_f64"),
        v2_5_status="wired_with_goal2790_thresholded_tiled_triton_selection_guidance",
        first_port_action=(
            "Keep optimized Torch/CuPy/CUDA or another explicitly selected same-contract "
            "partner for dense exact Hausdorff witness reduction unless the caller "
            "explicitly selects the Goal2790 tiled Triton route for large dense shapes "
            "after same-contract measurement. Goal2790 is thresholded evidence, not "
            "a blanket default."
        ),
        notes=(
            "Do not add Hausdorff-specific native code; nearest-witness scoring remains "
            "generic point-nearest plus grouped reduction. Goal2787 and Goal2788 block "
            "blind Triton auto-selection for dense exact Hausdorff-style witness "
            "reduction, while Goal2790 adds mixed thresholded guidance after the tiled "
            "route wins only at the measured 16K dense shape."
        ),
        measured_selection_shapes=(
            ("grouped_argmin_f64", "dense_exact_hausdorff_argmin_argmax"),
            ("grouped_argmin_f64", "dense_exact_hausdorff_nearest_then_global_max"),
            ("grouped_argmin_f64", "dense_exact_hausdorff_tiled_nearest_then_global_max"),
        ),
    ),
    V25TritonBenchmarkAppPlan(
        app_id="rt_dbscan",
        benchmark_name="RT-DBSCAN",
        promoted_benchmark=True,
        current_hot_path_partner="app_chosen_cupy_component_phase_with_numba_as_generic_fallback_partner",
        v2_5_required_operations=("compact_mask_i64", "bounded_collect_finalize_i64"),
        v2_5_status="app_chosen_cupy_phase_allowed_generic_fallback_partner_remains_numba",
        first_port_action=(
            "Wire generic Triton compaction and bounded finalize previews where they fit; "
            "keep any CuPy component/union-find phase as an explicit app-chosen phase, "
            "not as the v2.5 generic fallback partner."
        ),
        notes=(
            "DBSCAN cluster semantics must stay in app code; RTDL owns fixed-radius row "
            "generation and generic continuation contracts only. The declared v2.5 "
            "fallback partner is Numba; CuPy remains conformance/interoperability or an "
            "explicit app-chosen phase."
        ),
    ),
    V25TritonBenchmarkAppPlan(
        app_id="rtnn",
        benchmark_name="RTNN neighbor search",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_cupy_for_topk_or_candidate_continuations",
        v2_5_required_operations=("grouped_argmin_f64", "grouped_topk_f64", "bounded_collect_finalize_i64"),
        v2_5_status="covered_but_dense_topk_has_goal2784_negative_triton_selection_guidance",
        first_port_action=(
            "Use grouped argmin preview where top-1 is enough; for dense exact top-k, keep "
            "Torch/CuPy or another explicitly selected same-contract partner until a tiled "
            "top-k Triton design replaces the iterative preview."
        ),
        notes="Approximate-neighbor policy remains app code; primitive behavior is grouped candidate ranking. Goal2784 blocks blind Triton auto-selection for dense exact top-k while recording the improved no-dense-score adapter.",
        measured_selection_shapes=(("grouped_topk_f64", "dense_exact_topk_candidate_ranking"),),
    ),
    V25TritonBenchmarkAppPlan(
        app_id="triangle_counting",
        benchmark_name="RT-Graph triangle counting",
        promoted_benchmark=True,
        current_hot_path_partner="primitive_first_native_scalar_summary_plus_optional_cupy",
        v2_5_required_operations=("segmented_count_i64", "compact_mask_i64"),
        v2_5_status="primitive_first_plan_native_summary_not_relabelled_as_triton",
        first_port_action="Keep scalar triangle-count summaries on fused RTDL primitives; use Triton only for row-stream or compact-mask continuations.",
        notes="Goal2728's primitive-first rule applies: do not route scalar summaries through a slower partner path just to use a partner.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="barnes_hut",
        benchmark_name="Barnes-Hut / aggregate frontier",
        promoted_benchmark=True,
        current_hot_path_partner="explicit_measured_cupy_for_grouped_vector_sum_after_goal2933",
        v2_5_required_operations=("bounded_collect_finalize_i64", "grouped_vector_sum_f64x2"),
        v2_5_status="covered_with_goal2933_cupy_vector_sum_selection_and_goal2786_negative_triton_guidance",
        first_port_action=(
            "Lower aggregate-frontier rows to generic grouped vector-sum metadata, but keep "
            "CuPy, Torch, or another explicitly selected same-contract partner for dense "
            "vector sums until a segmented/block-reduction Triton design beats both the atomic "
            "preview and the presegmented row-offset preview."
        ),
        notes=(
            "Never embed inverse-square force law inside the engine or Triton primitive "
            "contract. Goal2786 keeps blind Triton auto-selection blocked for dense "
            "grouped vector sums after batched row-offset tuning failed to beat Torch. "
            "Goal2933 then shows the app-level same-contract selector can choose CuPy "
            "for this generic vector-sum shape when CuPy wins timing."
        ),
        measured_selection_shapes=(("grouped_vector_sum_f64x2", "dense_grouped_vector_sum_2d"),),
    ),
    V25TritonBenchmarkAppPlan(
        app_id="robot_collision",
        benchmark_name="Robot collision screening",
        promoted_benchmark=True,
        current_hot_path_partner="legacy_torch_or_cupy_optional_reduction",
        v2_5_required_operations=("compact_mask_i64", "bounded_collect_finalize_i64"),
        v2_5_status="covered_by_compact_and_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Use Triton compact preview for masks; route bounded witness/contact finalization through generic Triton collect/finalize.",
        notes="Collision/contact labels stay app-owned; primitive behavior is bounded witness collection.",
    ),
    V25TritonBenchmarkAppPlan(
        app_id="contact_manifold",
        benchmark_name="Bounded contact-manifold witness",
        promoted_benchmark=True,
        current_hot_path_partner="python_reference_or_native_rows",
        v2_5_required_operations=("bounded_collect_finalize_i64",),
        v2_5_status="covered_by_bounded_finalize_preview_pending_app_wiring",
        first_port_action="Wire bounded witness finalize to the generic Triton continuation and collect parity evidence.",
        notes="The engine primitive must say bounded witness collection, not collision or contact.",
    ),
)


V2_5_TIERED_BENCHMARK_MANIFEST_ROWS: tuple[V25TieredBenchmarkManifestRow, ...] = (
    V25TieredBenchmarkManifestRow(
        app_id="raydb_style",
        tier="A",
        benchmark_track="partner_continuation",
        parity_target="primitive-first prepared steady-state parity first; whole-app timing remains separately bounded",
        canonical_harness_status="ready_with_goal2720_goal2722_goal2727_and_Goal2896_prepared_pod_evidence",
        same_contract_opponent="Goal2896 prepared fused primitive-first path versus prepared typed hit-stream plus Triton alternative",
        required_partner_operations=("segmented_count_i64", "segmented_sum_f64", "segmented_min_f64", "segmented_max_f64"),
        pod_evidence_status="Goal2896 current prepared pod evidence same-contract performance gate passed for count/sum; Goal2727/2728 historical prepared evidence retained",
        next_action="keep Goal2896 gate current; use hit-stream path only for unfused continuations",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="triangle_counting",
        tier="A",
        benchmark_track="primitive_first_rt_summary",
        parity_target="same-contract scalar summary first; row-stream partner continuation only when summary is insufficient",
        canonical_harness_status="ready_with_goal2797_canonical_harness",
        same_contract_opponent="existing fused RTDL summary path, optional CuPy summary path, and RT-Graph authors-code rows",
        required_partner_operations=("segmented_count_i64", "segmented_sum_f64", "compact_mask_i64"),
        pod_evidence_status="Goal2797 current OptiX canonical harness evidence recorded for RT-2A1 and RT-1A2 primitive-first summary rows",
        next_action="keep Goal2797 canonical harness current; add Triton only for row-stream or compact-mask modes when scalar summary is insufficient",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="spatial_rayjoin",
        tier="A",
        benchmark_track="primitive_first_rt_count_or_parity_rows_overlay_deferred_tier_b",
        parity_target="Tier A count/parity same-contract comparison; row/overlay modes are deferred Tier B continuation work",
        canonical_harness_status="ready_with_goal2799_prepared_count_harness",
        same_contract_opponent="prepared OptiX count/parity path and RayJoin-exported same-query streams",
        required_partner_operations=("segmented_count_i64", "compact_mask_i64"),
        pod_evidence_status="Goal2799 current OptiX prepared count evidence recorded for PIP, LSI, and overlay-seed count/parity rows",
        next_action="keep primitive-first count/parity selection canonical; keep row/overlay output as deferred Tier B device-resident continuation work",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="librts_spatial_index",
        tier="C",
        benchmark_track="rt_core_aabb_no_partner_parity",
        parity_target="RT AABB count no-regression only",
        canonical_harness_status="ready_with_goal2798_warm_median_harness",
        same_contract_opponent="prepared RTDL AABB count path and authors-code RTSpatial baseline",
        required_partner_operations=(),
        pod_evidence_status="Goal2798 current OptiX warm median evidence recorded for all three AABB_INDEX_QUERY_2D count operations",
        next_action="keep as RT-core no-regression baseline; do not convert count-only AABB queries into partner-parity claims",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="rt_dbscan",
        tier="B",
        benchmark_track="partner_continuation_high_risk",
        parity_target="per-app parity or documented accepted miss with fallback-backed components op",
        canonical_harness_status="ready_with_goal2802_live_grouped_stream_harness",
        same_contract_opponent="existing CuPy grouped-stream/microcell component-continuation path",
        required_partner_operations=("compact_mask_i64", "bounded_collect_finalize_i64", "grouped_components_or_fallback"),
        pod_evidence_status="Goal2802 current OptiX grouped-stream and CuPy prepared-grid same-contract evidence recorded",
        next_action="keep Goal2802 live harness current; keep pure Triton components auto-selection blocked until a generic component continuation or accepted fallback beats the same-contract CuPy/grid/grouped-stream opponent",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="rtnn",
        tier="B",
        benchmark_track="partner_continuation",
        parity_target="bounded top-k/ranked-summary parity against same-contract CuPy opponent",
        canonical_harness_status="ready_with_goal2800_live_ranked_summary_harness",
        same_contract_opponent="existing CuPy ranked-summary / top-k continuation path",
        required_partner_operations=("grouped_argmin_f64", "bounded_collect_finalize_i64", "bounded_topk_or_ranked_summary"),
        pod_evidence_status="Goal2800 current OptiX ranked-summary and CuPy grid same-contract live harness evidence recorded",
        next_action="keep Goal2800 live harness current; keep dense exact top-k Triton auto-selection blocked until a tiled top-k route beats the same-contract CuPy grid opponent",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="barnes_hut",
        tier="B",
        benchmark_track="partner_continuation",
        parity_target="grouped weighted vector-sum parity or accepted fallback",
        canonical_harness_status="ready_with_goal2803_consolidated_harness",
        same_contract_opponent="existing fused CuPy/Torch frontier-vector-sum path",
        required_partner_operations=("bounded_collect_finalize_i64", "segmented_sum_f64", "grouped_vector_sum"),
        pod_evidence_status=(
            "Goal2803 current OptiX expanded-membership and Torch/Triton grouped-vector-sum "
            "same-contract evidence recorded; Goal2933 records CuPy as the measured selected "
            "same-contract vector-sum partner on the bounded pod smoke"
        ),
        next_action="keep CuPy as an explicit measured vector-sum partner where it wins; keep Triton vector-sum auto-selection blocked until it beats the same-contract Torch/CuPy vector-sum opponent",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="hausdorff_xhd",
        tier="B",
        benchmark_track="partner_continuation",
        parity_target="grouped max-plus-witness parity against optimized CUDA/CuPy same-contract opponent",
        canonical_harness_status="ready_with_goal2801_canonical_exact_entrypoint",
        same_contract_opponent="optimized X-HD-guided CuPy/CUDA witness-reduction path",
        required_partner_operations=("grouped_argmin_f64", "segmented_max_f64", "grouped_argmax_witness"),
        pod_evidence_status="Goal2801 current OptiX exact witness and CuPy grid same-contract canonical entrypoint evidence recorded",
        next_action="keep Goal2801 canonical entrypoint current; keep Triton witness auto-selection blocked until it beats the same-contract CuPy grid opponent",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="contact_manifold",
        tier="C",
        benchmark_track="rt_core_collection_no_partner_parity",
        parity_target="RT path no-regression only",
        canonical_harness_status="ready_with_goal2929_tier_c_no_regression_smoke",
        same_contract_opponent="prepared OptiX bounded witness collection path",
        required_partner_operations=("bounded_collect_finalize_i64",),
        pod_evidence_status="Goal2929 current OptiX AABB broadphase and bounded witness collection no-regression smoke recorded",
        next_action="measure no-regression only unless exact refinement is intentionally partnerized",
    ),
    V25TieredBenchmarkManifestRow(
        app_id="robot_collision",
        tier="C",
        benchmark_track="rt_core_anyhit_no_partner_parity",
        parity_target="prepared RT any-hit no-regression only",
        canonical_harness_status="ready_with_goal2929_tier_c_no_regression_smoke",
        same_contract_opponent="prepared Embree/OptiX pose flag path",
        required_partner_operations=("compact_mask_i64",),
        pod_evidence_status="Goal2929 current prepared OptiX pose-flags validation and timing smoke recorded",
        next_action="keep in RT-core no-regression track and avoid partner benchmark category error",
    ),
)


def v2_5_triton_benchmark_app_migration_plan() -> dict[str, object]:
    return {
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "migration_version": V2_5_TRITON_APP_MIGRATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "partner_selection_guidance_version": V2_5_PARTNER_SELECTION_GUIDANCE_VERSION,
        "partner_selection_guidance_integrated": True,
        "auto_select_preview_partner_allowed": False,
        "preview_kernel_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
        "benchmark_app_count": len(V2_5_TRITON_BENCHMARK_APP_PLANS),
        "apps": tuple(plan.to_metadata() for plan in V2_5_TRITON_BENCHMARK_APP_PLANS),
        "claim_boundary": (
            "This is a v2.5 implementation/migration plan. It is not a release "
            "gate, not a public speedup claim, not authorization to replace "
            "RTDL/OptiX traversal with partner code, and not authorization to "
            "auto-select Triton just because a preview kernel exists."
        ),
    }


def v2_5_tiered_benchmark_manifest() -> dict[str, object]:
    rows = tuple(row.to_metadata() for row in V2_5_TIERED_BENCHMARK_MANIFEST_ROWS)
    tier_counts: dict[str, int] = {}
    for row in rows:
        tier = str(row["tier"])
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    return {
        "manifest_version": V2_5_TIERED_BENCHMARK_MANIFEST_VERSION,
        "contract_version": V2_5_PARTNER_CONTINUATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "benchmark_app_count": len(rows),
        "tier_counts": tier_counts,
        "apps": rows,
        "same_contract_required": True,
        "phase_separated_timing_required": True,
        "sm70_plus_pod_required_for_triton_perf": True,
        "public_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "claim_boundary": (
            "This manifest scopes v2.5 benchmark parity work. It is not a "
            "release gate, not public performance wording, and not permission "
            "to treat RT-core-only apps as partner-continuation benchmarks."
        ),
    }


def validate_v2_5_tiered_benchmark_manifest() -> dict[str, object]:
    manifest = v2_5_tiered_benchmark_manifest()
    errors: list[str] = []
    rows = tuple(manifest["apps"])  # type: ignore[arg-type]
    app_ids = [str(row["app_id"]) for row in rows]  # type: ignore[index]
    if len(app_ids) != len(set(app_ids)):
        errors.append("duplicate app id in v2.5 tiered benchmark manifest")
    if len(rows) != 10:
        errors.append("v2.5 tiered benchmark manifest must cover exactly 10 apps")
    if manifest["primary_partner"] != V2_5_PRIMARY_PARTNER:
        errors.append("manifest primary partner must match v2.5 primary partner")
    if manifest["public_speedup_claim_authorized"] is not False:
        errors.append("manifest must not authorize public speedup claims")
    if manifest["true_zero_copy_claim_authorized"] is not False:
        errors.append("manifest must not authorize true zero-copy claims")
    expected_tiers = {"A": 3, "B": 4, "C": 3}
    if manifest["tier_counts"] != expected_tiers:
        errors.append("unexpected v2.5 benchmark tier partition")
    for row in rows:
        tier = row["tier"]  # type: ignore[index]
        app_id = row["app_id"]  # type: ignore[index]
        if tier == "C" and "partner" in str(row["parity_target"]).lower():
            errors.append(f"{app_id} tier C row must not require partner parity")
        if tier in {"A", "B"} and not row["same_contract_opponent"]:  # type: ignore[index]
            errors.append(f"{app_id} must name a same-contract opponent")
        if app_id == "librts_spatial_index":
            if tier != "C":
                errors.append("librts_spatial_index must remain Tier C no-partner no-regression")
            if row["required_partner_operations"]:  # type: ignore[index]
                errors.append("librts_spatial_index Tier C row must not require partner operations")
            if "no-regression" not in str(row["parity_target"]):  # type: ignore[index]
                errors.append("librts_spatial_index must be framed as no-regression evidence")
        if app_id == "spatial_rayjoin":
            row_text = " ".join(
                str(row[field])  # type: ignore[index]
                for field in ("benchmark_track", "parity_target", "next_action")
            )
            if "Tier A count/parity" not in row_text or "deferred Tier B" not in row_text:
                errors.append("spatial_rayjoin must split Tier A count/parity from deferred Tier B row/overlay")
        if "raydb" in str(app_id):
            status = str(row["pod_evidence_status"])  # type: ignore[index]
            if "prepared" not in status or "pod evidence" not in status:
                errors.append("RayDB row must record prepared pod evidence")
            row_text = " ".join(
                str(row[field])  # type: ignore[index]
                for field in ("canonical_harness_status", "same_contract_opponent", "pod_evidence_status", "next_action")
            )
            if "Goal2896" not in row_text:
                errors.append("RayDB row must index Goal2896 same-contract performance gate")
    return {
        "status": "accept" if not errors else "reject",
        "manifest_version": manifest["manifest_version"],
        "benchmark_app_count": manifest["benchmark_app_count"],
        "tier_counts": manifest["tier_counts"],
        "errors": tuple(errors),
    }


def validate_v2_5_triton_benchmark_app_migration_plan() -> dict[str, object]:
    plan = v2_5_triton_benchmark_app_migration_plan()
    errors: list[str] = []
    app_ids = [str(app["app_id"]) for app in plan["apps"]]  # type: ignore[index]
    if len(app_ids) != len(set(app_ids)):
        errors.append("duplicate benchmark app id in v2.5 Triton migration plan")
    if plan["primary_partner"] != "triton":
        errors.append("v2.5 benchmark migration must keep Triton as the declared primary partner")
    if plan["auto_select_preview_partner_allowed"] is not False:
        errors.append("v2.5 benchmark migration plan must not auto-select preview partners")
    if plan["partner_selection_guidance_integrated"] is not True:
        errors.append("v2.5 benchmark migration plan must integrate partner-selection guidance")
    for app in plan["apps"]:  # type: ignore[assignment]
        if not app["promoted_benchmark"]:
            errors.append(f"{app['app_id']} is not marked as a promoted benchmark")
        status = app["v2_5_status"].lower()
        if "target_cupy" in status or "target_pytorch" in status:
            errors.append(f"{app['app_id']} v2.5 status must not make CuPy/PyTorch the target partner")
        missing_operations = sorted(
            set(app["v2_5_required_operations"]) - set(V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        )
        if missing_operations:
            errors.append(
                f"{app['app_id']} requires operations without Triton previews: {missing_operations}"
            )
        if app.get("auto_select_preview_partner_allowed") is not False:
            errors.append(f"{app['app_id']} must not auto-select a preview partner")
        if app["app_id"] == "raydb_style":
            raydb_text = " ".join(
                str(app[field])
                for field in ("current_hot_path_partner", "v2_5_status", "first_port_action", "notes")
            )
            if "Goal2896" not in raydb_text:
                errors.append("raydb_style migration plan must cite Goal2896 current performance gate")
            if "primitive_first" not in str(app["current_hot_path_partner"]):
                errors.append("raydb_style current hot path must remain primitive-first")
        for guidance in app.get("partner_selection_guidance", ()):
            if guidance["status"] == "measured_negative_preview_guidance":
                if guidance["auto_select_partner_allowed"] is not False:
                    errors.append(f"{app['app_id']} measured negative guidance must block auto-selection")
            if guidance["status"] == "measured_mixed_preview_guidance":
                if guidance["auto_select_partner_allowed"] is not False:
                    errors.append(f"{app['app_id']} measured mixed guidance must block auto-selection")
    return {
        "status": "accept" if not errors else "reject",
        "benchmark_app_count": plan["benchmark_app_count"],
        "primary_partner": plan["primary_partner"],
        "errors": tuple(errors),
    }


def v2_5_triton_front_door_coverage() -> dict[str, object]:
    """Report which benchmark-app continuations have adapter-level Triton access.

    All required operations may have low-level Triton dispatcher previews, while
    only a subset has public generic partner-adapter front doors. Keeping this
    split explicit avoids claiming that every benchmark app has already been
    rewired to `partner="triton"`.
    """

    adapter_ops = set(V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS)
    dispatcher_ops = set(V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
    rows = []
    fully_front_door_ready = 0
    for app in V2_5_TRITON_BENCHMARK_APP_PLANS:
        required = set(app.v2_5_required_operations)
        adapter_ready = tuple(operation for operation in app.v2_5_required_operations if operation in adapter_ops)
        dispatcher_only = tuple(
            operation
            for operation in app.v2_5_required_operations
            if operation in dispatcher_ops and operation not in adapter_ops
        )
        missing = tuple(operation for operation in app.v2_5_required_operations if operation not in dispatcher_ops)
        status = "adapter_front_door_ready" if required.issubset(adapter_ops) else "dispatcher_ready_app_wiring_required"
        if missing:
            status = "missing_triton_preview_operation"
        if status == "adapter_front_door_ready":
            fully_front_door_ready += 1
        rows.append(
            {
                "app_id": app.app_id,
                "benchmark_name": app.benchmark_name,
                "required_operations": app.v2_5_required_operations,
                "adapter_front_door_operations": adapter_ready,
                "dispatcher_only_operations": dispatcher_only,
                "missing_operations": missing,
                "front_door_status": status,
            }
        )
    return {
        "migration_version": V2_5_TRITON_APP_MIGRATION_VERSION,
        "primary_partner": V2_5_PRIMARY_PARTNER,
        "adapter_front_door_operations": V2_5_TRITON_PARTNER_ADAPTER_FRONT_DOOR_OPERATIONS,
        "dispatcher_preview_operations": V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS,
        "benchmark_app_count": len(rows),
        "fully_front_door_ready_count": fully_front_door_ready,
        "apps": tuple(rows),
        "claim_boundary": (
            "Adapter front-door readiness is local API coverage only. It is not "
            "CUDA pod evidence, benchmark completion, or public performance wording."
        ),
    }
