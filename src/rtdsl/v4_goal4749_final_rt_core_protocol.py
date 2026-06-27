from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA = "rtdl.v4.goal4749.final_same_semantics_rt_core_protocol.v1"
STATUS = "goal4749_final_same_semantics_rt_core_protocol_frozen_not_run"
DATE = "2026-06-26"

APP_ORDER = (
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "rtnn",
    "spatial_rayjoin",
    "barnes_hut",
)

VERSION_ORDER = ("v2_14", "v3_0_2", "v4_0")

ROUTE_RUNNABLE = "runnable_protocol_template"
ROUTE_REPAIR = "v4_0_repair_required_before_final_timing"
ROUTE_DISCOVERY = "command_binding_required_in_goal4750"

SUPPORT_INHERITED = "v4_superset_inherited_compatibility"
SUPPORT_NEW = "v4_new_operator_or_workflow"
SUPPORT_BOTH = "v4_inherited_compatibility_plus_new_operator"


def _route(
    *,
    status: str,
    route: str,
    backend: str = "optix_rt_core",
    partner: str = "rtdl_native",
    command_hint: str = "bind_in_goal4750_runner",
    blocker: str = "",
) -> dict[str, Any]:
    return {
        "route_status": status,
        "route": route,
        "backend": backend,
        "partner": partner,
        "command_hint": command_hint,
        "blocker": blocker,
        "primary_denominator_allowed": backend == "optix_rt_core",
    }


def _partner(cupy: str, numba: str) -> dict[str, str]:
    return {
        "cupy": cupy,
        "numba": numba,
    }


def _row(
    *,
    app: str,
    semantic_contract: str,
    correctness_oracle: str,
    scale_policy: str,
    v4_support_class: str,
    partner_contract: dict[str, str],
    versions: dict[str, dict[str, Any]],
    metrics: tuple[str, ...] = ("hot_median_sec", "wall_median_sec"),
    claim_boundary: str = "no_speed_claim_until_goal4753_4754_matrix",
    supplemental_notes: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "app": app,
        "semantic_contract": semantic_contract,
        "same_semantics_required": True,
        "rt_core_primary_required": True,
        "embree_role": "control_only_not_primary_denominator",
        "correctness_oracle": correctness_oracle,
        "primary_metrics": list(metrics),
        "scale_policy": scale_policy,
        "v4_support_class": v4_support_class,
        "v4_superset_obligation": "must expose or inherit V2.14/V3 RT-core capability in V4.0",
        "partner_contract": partner_contract,
        "versions": versions,
        "claim_boundary": claim_boundary,
        "supplemental_notes": list(supplemental_notes),
    }


def protocol_rows() -> list[dict[str, Any]]:
    return [
        _row(
            app="rt_dbscan",
            semantic_contract="fixed-radius count-threshold neighbors plus component labels",
            correctness_oracle="component-label signature parity and cluster-count parity",
            scale_policy="serious clustered3d point_count=262144; smoke/parity companion allowed at smaller point_count",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "inherited_supported_for_grouped_stream_or_component_work",
                "measured_supported_for_v4_component_union",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX count-threshold 3D plus grouped-stream CuPy/Numba continuation",
                    partner="cupy_or_numba",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX count-threshold 3D plus grouped-stream continuation",
                    partner="cupy_or_numba",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 fixed-radius count-threshold plus Numba component-union surface",
                    partner="numba",
                ),
            },
        ),
        _row(
            app="raydb_style",
            semantic_contract="ray/triangle primitive grouped i64 count/sum reduction",
            correctness_oracle="grouped reduction parity by group id and aggregate value",
            scale_policy="rows >=131072; group widths include 1/16/256 where supported",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "measured_supported_for_grouped_vector_sum_and_inherited_reduction",
                "declared_unmeasured_for_this_surface",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="primitive-first OptiX grouped count/sum reduction",
                    partner="rtdl_native_or_cupy",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared grouped reduction route",
                    partner="rtdl_native_or_cupy",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 grouped-i64/device-output grouped reduction route",
                    partner="rtdl_native_or_cupy",
                ),
            },
        ),
        _row(
            app="triangle_counting",
            semantic_contract="graph triangle/cycle count lowered to ray-triangle weighted any-hit sum",
            correctness_oracle="triangle count and weighted any-hit sum parity",
            scale_policy="serious k4/graph fixture plus weighted any-hit shapes through 524288 where available",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "inherited_supported_for_vectorized_continuation",
                "inherited_supported_for_triangle_compact_mask_or_ray_output_builders",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="generic RT graph relationship-count composition using OptiX weighted any-hit sum",
                    partner="cupy_or_numba",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="segmented/prepared RT graph weighted any-hit route",
                    partner="cupy_or_numba",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 ray-triangle any-hit weighted-sum plus grouped reduction surface",
                    partner="cupy_or_numba_or_rtdl_native",
                ),
            },
        ),
        _row(
            app="librts_spatial_index",
            semantic_contract="prepared AABB spatial index query count/all-ops",
            correctness_oracle="AABB query count parity for the same operations",
            scale_policy="box_count=1000000 query_count=1000 operation=all where available",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "declared_unmeasured_for_native_aabb_surface",
                "declared_unmeasured_for_native_aabb_surface",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX AABB spatial-index query primitive",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX AABB spatial-index query primitive",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 prepared AABB all-ops/count route",
                ),
            },
        ),
        _row(
            app="hausdorff_xhd",
            semantic_contract="directed Hausdorff threshold-decision RT-core route for three-version fairness",
            correctness_oracle="threshold decision parity and, separately, exact nearest-witness correctness when exact route exists",
            scale_policy="primary fair matrix uses threshold-decision semantics; V3/V4 exact nearest-witness is supplemental until V2.14 exact route is bound or implemented",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "measured_supported_for_v4_exact_argmax_supplemental_route",
                "declared_unmeasured_for_exact_argmax; possible inherited threshold support",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="OptiX directed-threshold-prepared Hausdorff decision route",
                    partner="rtdl_native",
                    command_hint="--backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="inherited OptiX directed-threshold-prepared route for fair primary row; exact route is supplemental",
                    partner="rtdl_native_or_cupy",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 compatibility threshold route for fair primary row; exact nearest-witness route remains supplemental V4-new evidence",
                    partner="rtdl_native_or_cupy",
                ),
            },
            supplemental_notes=(
                "The previous V2.14 Embree denominator is forbidden for the primary matrix.",
                "The V4/V3 exact nearest-witness row may be reported separately, but not divided by the V2.14 threshold route.",
            ),
        ),
        _row(
            app="robot_collision",
            semantic_contract="prepared any-hit collision flags/count",
            correctness_oracle="collision flag vector and scalar count parity",
            scale_policy="use promoted robot-collision benchmark shape; exact scale to bind in Goal4750",
            v4_support_class=SUPPORT_INHERITED,
            partner_contract=_partner(
                "not_required_for_primary_flag_route",
                "not_required_for_primary_flag_route",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX any-hit collision flag primitive including device-buffer modes",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX any-hit flag stream family",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 superset compatibility route inherits prepared any-hit collision flags/count",
                    command_hint="--mode optix_prepared_device_buffers --dataset scaled --pose-count 8192 --obstacle-count 2048 --link-count 2 --repeats 51 --warmup 5 --lowering-mode numpy_arrays --summary-only-runs --skip-group-metadata",
                ),
            },
        ),
        _row(
            app="contact_manifold",
            semantic_contract="bounded contact/witness collect-k route with fail-closed output semantics",
            correctness_oracle="bounded witness rows, cap handling, and fail-closed parity",
            scale_policy="use promoted contact-manifold benchmark shape; exact scale to bind in Goal4750",
            v4_support_class=SUPPORT_INHERITED,
            partner_contract=_partner(
                "not_required_for_primary_collect_route",
                "not_required_for_primary_collect_route",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared bounded OptiX contact-witness collect primitive",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared bounded collect/witness route family",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 superset compatibility route inherits bounded collect-k/contact witness primitive",
                    command_hint="--mode aabb_broadphase_collect_k --backend optix --discovery-backend optix --dataset grid --witness-capacity 8",
                ),
            },
        ),
        _row(
            app="rtnn",
            semantic_contract="fixed-radius ranked nearest-summary aggregate",
            correctness_oracle="ranked-summary signature and distance/value parity",
            scale_policy="point_count=262144 and 1048576 serious rows where available",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "declared_unmeasured_for_ranked_summary",
                "declared_unmeasured_for_ranked_summary",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared OptiX fixed-radius ranked-summary aggregate",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="prepared ranked-summary/top-k/nearest aggregate family",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 ranked-summary prepared runner, currently measured no-win/deferred for speed credit",
                ),
            },
        ),
        _row(
            app="spatial_rayjoin",
            semantic_contract="relation/topology rayjoin counts using prepared point/shape/segment RT-core primitives",
            correctness_oracle="relation/topology count parity; exact route cannot silently fall back",
            scale_policy="use promoted spatial-rayjoin benchmark shape; exact scale to bind in Goal4750",
            v4_support_class=SUPPORT_INHERITED,
            partner_contract=_partner(
                "inherited_supported_where_old_route_uses_cupy_continuation",
                "inherited_supported_where_old_route_uses_fixed_numba_toolchain",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="mixed explicit OptiX RayJoin route with point/closed-shape batch count, segment-pair exact count, and shape-pair active count",
                    partner="cupy_or_numba_or_rtdl_native",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="topology/runner experiments around the same RT-core route family",
                    partner="cupy_or_numba_or_rtdl_native",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 superset compatibility route inherits relation/topology RT-core route",
                    partner="cupy_or_numba_or_rtdl_native",
                    command_hint="--workload overlay_seed --backend optix --execution-route prepared_optix_shape_pair_active_count --result-mode count --repeat 25 --warmup 3 --no-rows",
                ),
            },
        ),
        _row(
            app="barnes_hut",
            semantic_contract="aggregate-frontier membership plus weighted vector continuation",
            correctness_oracle="frontier membership and weighted vector summary parity",
            scale_policy="32768 bodies serious focused workflow; larger row optional after parity",
            v4_support_class=SUPPORT_BOTH,
            partner_contract=_partner(
                "measured_supported_for_device-column/vector continuation",
                "inherited_reference_or_declared_unmeasured_for_current_v4_surface",
            ),
            versions={
                "v2_14": _route(
                    status=ROUTE_RUNNABLE,
                    route="OptiX aggregate-frontier membership with host-materialized frontier and explicit partner continuation",
                    partner="cupy_or_numba_reference",
                ),
                "v3_0_2": _route(
                    status=ROUTE_RUNNABLE,
                    route="device-column aggregate-frontier/partner continuation family",
                    partner="cupy",
                ),
                "v4_0": _route(
                    status=ROUTE_RUNNABLE,
                    route="V4 aggregate-frontier device-columns prepared workflow with explicit partner continuation",
                    partner="cupy",
                ),
            },
        ),
    ]


def build_protocol() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "date": DATE,
        "decision_label": "final_v4_0_same_semantics_rt_core_protocol_frozen_before_pod_matrix",
        "purpose": (
            "Freeze the final 10 benchmark-app V2.14/V3.0.2/V4.0 same-semantics "
            "NVIDIA RT-core protocol before the complete POD matrix. This replaces "
            "older V2-vs-V4-only and Embree-denominator app summaries for final "
            "V4.0 release evidence."
        ),
        "version_order": list(VERSION_ORDER),
        "app_order": list(APP_ORDER),
        "global_rules": {
            "v2_means_v2_14": True,
            "v3_means_v3_0_2": True,
            "v4_means_current_v4_0_candidate": True,
            "nvidia_rt_core_primary_required": True,
            "embree_primary_denominator_authorized": False,
            "embree_control_reference_authorized": True,
            "no_na_rows_authorized": True,
            "same_semantics_required": True,
            "correctness_parity_required_before_speed_credit": True,
            "v4_is_v2_v3_superset_release_line": True,
            "partner_migration_counts_as_v4_speed_win": False,
            "inherited_compatibility_counts_as_support_not_new_speed": True,
            "pod_authorized_by_goal4749": False,
            "final_pod_matrix_goal": "Goal4753",
        },
        "allowed_route_statuses": [ROUTE_RUNNABLE, ROUTE_REPAIR, ROUTE_DISCOVERY],
        "allowed_v4_support_classes": [SUPPORT_INHERITED, SUPPORT_NEW, SUPPORT_BOTH],
        "rows": protocol_rows(),
        "claim_boundary": {
            "release_authorized": False,
            "public_speed_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
            "embree_primary_ratio_authorized": False,
            "v4_1_numba_ray_action_work_in_scope": False,
        },
    }


def _contains_na(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"n/a", "na", "not applicable"}
    if isinstance(value, dict):
        return any(_contains_na(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_na(v) for v in value)
    return False


def validate_protocol(protocol: dict[str, Any] | None = None) -> dict[str, Any]:
    protocol = build_protocol() if protocol is None else protocol
    errors: list[str] = []
    rows = protocol.get("rows", [])
    by_app = {row.get("app"): row for row in rows if isinstance(row, dict)}

    if tuple(protocol.get("app_order", ())) != APP_ORDER:
        errors.append("app_order must match the promoted 10 benchmark apps")
    if len(rows) != 10 or set(by_app) != set(APP_ORDER):
        errors.append("protocol must contain exactly one row for each promoted app")

    if _contains_na(protocol):
        errors.append("protocol contains an n/a-style value")

    rules = protocol.get("global_rules", {})
    if rules.get("embree_primary_denominator_authorized") is not False:
        errors.append("Embree primary denominator must be forbidden")
    if rules.get("nvidia_rt_core_primary_required") is not True:
        errors.append("NVIDIA RT-core primary route must be required")
    if rules.get("v4_is_v2_v3_superset_release_line") is not True:
        errors.append("V4 superset rule must be explicit")

    allowed_statuses = set(protocol.get("allowed_route_statuses", ()))
    allowed_support = set(protocol.get("allowed_v4_support_classes", ()))
    for row in rows:
        app = row.get("app", "<missing>")
        if row.get("same_semantics_required") is not True:
            errors.append(f"{app}: same semantics must be required")
        if row.get("rt_core_primary_required") is not True:
            errors.append(f"{app}: RT-core primary route must be required")
        if row.get("v4_support_class") not in allowed_support:
            errors.append(f"{app}: invalid V4 support class")
        versions = row.get("versions", {})
        if set(versions) != set(VERSION_ORDER):
            errors.append(f"{app}: must define v2_14/v3_0_2/v4_0 routes")
            continue
        for version, route in versions.items():
            status = route.get("route_status")
            if status not in allowed_statuses:
                errors.append(f"{app}/{version}: invalid route status {status!r}")
            backend = str(route.get("backend", "")).lower()
            if "embree" in backend:
                errors.append(f"{app}/{version}: Embree cannot be the primary backend")
            if route.get("primary_denominator_allowed") is not True and status == ROUTE_RUNNABLE:
                errors.append(f"{app}/{version}: runnable route must be allowed as primary denominator")
            if status in {ROUTE_REPAIR, ROUTE_DISCOVERY} and not route.get("blocker"):
                errors.append(f"{app}/{version}: non-runnable route must name the blocker")
        v4_status = versions["v4_0"].get("route_status")
        if v4_status in {ROUTE_REPAIR, ROUTE_DISCOVERY} and not versions["v4_0"].get("blocker"):
            errors.append(f"{app}: V4 non-runnable row must name a V4.0 repair blocker")

    return {
        "schema": f"{SCHEMA}.validation",
        "status": "passed" if not errors else "failed",
        "error_count": len(errors),
        "errors": errors,
    }


def write_protocol_artifacts(
    *,
    evidence_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    protocol = build_protocol()
    validation = validate_protocol(protocol)
    payload = {**protocol, "validation": validation}
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(payload), encoding="utf-8")
    return payload


def _render_report(protocol: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4749 Final Same-Semantics RT-Core Protocol",
        "",
        f"Status: `{protocol['status']}`",
        "",
        "This freezes the final V4.0 benchmark protocol before the full POD matrix.",
        "It supersedes older V2-vs-V4-only matrices for release evidence.",
        "",
        "## Hard Rules",
        "",
        "- Primary performance denominators must be NVIDIA OptiX/RT-core routes, not Embree.",
        "- No user-facing `n/a` rows are allowed.",
        "- V4.0 is a V2.14/V3.0.2 superset release line.",
        "- Correctness parity is required before speed credit.",
        "- Inherited compatibility is support; it is not automatically V4-new speedup.",
        "",
        "## App Rows",
        "",
        "| App | Semantic Contract | V4.0 Status | V4.0 Support Class |",
        "| --- | --- | --- | --- |",
    ]
    for row in protocol["rows"]:
        v4_route = row["versions"]["v4_0"]
        lines.append(
            "| {app} | {semantic} | {status} | {support} |".format(
                app=row["app"],
                semantic=row["semantic_contract"],
                status=v4_route["route_status"],
                support=row["v4_support_class"],
            )
        )
    lines.extend(
        [
            "",
            "## V4.0 Repair Rows Before Final Matrix",
            "",
        ]
    )
    repair_rows = [
        row for row in protocol["rows"] if row["versions"]["v4_0"]["route_status"] != ROUTE_RUNNABLE
    ]
    if repair_rows:
        for row in repair_rows:
            lines.append(f"- `{row['app']}`: {row['versions']['v4_0']['blocker']}")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- status: `{protocol['validation']['status']}`",
            f"- error_count: `{protocol['validation']['error_count']}`",
            "",
            "## Next",
            "",
            "Goal4750 builds the unified dry-run/POD runner from this protocol. Goal4753 runs the final matrix.",
            "",
        ]
    )
    return "\n".join(lines)


__all__ = [
    "APP_ORDER",
    "VERSION_ORDER",
    "build_protocol",
    "validate_protocol",
    "write_protocol_artifacts",
]
