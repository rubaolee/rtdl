from __future__ import annotations

from dataclasses import dataclass
from typing import Any


V2_8_OVERLAY_AREA_CONTINUATION_VERSION = (
    "rtdl.v2_8.simple_polygon_overlay_area_continuation_contract.v1"
)
V2_8_OVERLAY_AREA_CONTINUATION_STATUS = "design_contract_no_runtime_kernel_yet"
V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY = (
    "v2.8 simple-polygon overlay-area continuation metadata defines generic "
    "runtime targets after exact oracle evidence. It does not authorize release, "
    "public speedup wording, RT-core speedup wording, true-zero-copy wording, "
    "paper reproduction claims, hidden partner selection, hidden dispatch, full "
    "overlay completion claims, or app-specific native-engine behavior."
)
V2_8_OVERLAY_AREA_INPUT_CONTRACT = "shape_pair_relation_flags_with_ordinals_and_geometry_payload"
V2_8_OVERLAY_AREA_SCALAR_TARGET = "scalar_exact_area"
V2_8_OVERLAY_GEOMETRY_STREAM_TARGET = "streamed_overlay_geometry"


@dataclass(frozen=True)
class V28OverlayAreaContinuationPlan:
    target: str
    priority: str
    input_contract: str
    output_contract: str
    algorithm_family: str
    oracle_basis: str
    acceptance_bars: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    status: str = V2_8_OVERLAY_AREA_CONTINUATION_STATUS
    app_specific_engine_logic_allowed: bool = False
    automatic_partner_selection_allowed: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    true_zero_copy_claim_authorized: bool = False
    full_overlay_completion_claim_authorized: bool = False

    def __post_init__(self) -> None:
        if self.target not in {V2_8_OVERLAY_AREA_SCALAR_TARGET, V2_8_OVERLAY_GEOMETRY_STREAM_TARGET}:
            raise ValueError(f"invalid overlay continuation target: {self.target}")
        if self.priority not in {"P0", "P1", "P2"}:
            raise ValueError("priority must be P0, P1, or P2")
        if self.input_contract != V2_8_OVERLAY_AREA_INPUT_CONTRACT:
            raise ValueError("overlay area continuation must consume the generic shape-pair relation payload")
        if not self.acceptance_bars:
            raise ValueError("overlay area continuation plan must have acceptance bars")
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "full_overlay_completion_claim_authorized",
        ):
            if getattr(self, field):
                raise ValueError(f"overlay area continuation plan must not authorize {field}")

    def to_metadata(self) -> dict[str, Any]:
        return {
            "version": V2_8_OVERLAY_AREA_CONTINUATION_VERSION,
            "status": self.status,
            "target": self.target,
            "priority": self.priority,
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
            "algorithm_family": self.algorithm_family,
            "oracle_basis": self.oracle_basis,
            "acceptance_bars": self.acceptance_bars,
            "evidence_refs": self.evidence_refs,
            "app_specific_engine_logic_allowed": self.app_specific_engine_logic_allowed,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "full_overlay_completion_claim_authorized": self.full_overlay_completion_claim_authorized,
            "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
        }


def v2_8_overlay_area_continuation_plan() -> tuple[dict[str, Any], ...]:
    plans = (
        V28OverlayAreaContinuationPlan(
            target=V2_8_OVERLAY_AREA_SCALAR_TARGET,
            priority="P0",
            input_contract=V2_8_OVERLAY_AREA_INPUT_CONTRACT,
            output_contract="row_aligned_float64_exact_area_plus_status",
            algorithm_family="generic_simple_polygon_scalar_area_continuation",
            oracle_basis=(
                "Goal3474 exact oracle: 4,543 active rows, 1,090 positive area rows, "
                "3,453 zero-area rows, 0 exceptions, total area 26.08321766231042."
            ),
            acceptance_bars=(
                "must match Goal3474 total exact area within explicit float64 tolerance",
                "must match positive/zero row counts against the exact oracle",
                "must fail closed on unsupported topology or scratch-capacity overflow",
                "must consume only generic relation ordinals and geometry payload columns",
                "must keep app/domain names out of native ABI and runtime metadata",
                "must keep all public/release/performance claim flags false",
            ),
            evidence_refs=("Goal3474", "Goal3475", "Goal3477", "Goal3478"),
        ),
        V28OverlayAreaContinuationPlan(
            target=V2_8_OVERLAY_GEOMETRY_STREAM_TARGET,
            priority="P1",
            input_contract=V2_8_OVERLAY_AREA_INPUT_CONTRACT,
            output_contract="streamed_component_vertex_columns_plus_owner_rows",
            algorithm_family="generic_simple_polygon_full_geometry_stream_continuation",
            oracle_basis=(
                "Goal3477 output oracle: 609 positive MultiPolygon rows, 48 positive "
                "GeometryCollection rows, 2,801 polygon components, 42,314 output vertices, "
                "max 22 polygon components and 586 output vertices in one row."
            ),
            acceptance_bars=(
                "must publish component, vertex, ring, and owner-row columns with fail-closed capacity status",
                "must preserve boundary/touch-only rows without converting them into positive area",
                "must define deterministic vertex ordering and tolerance policy",
                "must separate scalar area completion from full geometry completion claims",
                "must keep app/domain names out of native ABI and runtime metadata",
                "must keep all public/release/performance claim flags false",
            ),
            evidence_refs=("Goal3477", "Goal3478"),
        ),
    )
    return tuple(plan.to_metadata() for plan in plans)


def select_v2_8_overlay_area_continuation_target(*, output_mode: str) -> dict[str, Any]:
    normalized = str(output_mode).strip().lower()
    if normalized in {"area", "area_scalar", "scalar", V2_8_OVERLAY_AREA_SCALAR_TARGET}:
        target = V2_8_OVERLAY_AREA_SCALAR_TARGET
    elif normalized in {"geometry", "full_geometry", "streamed_geometry", V2_8_OVERLAY_GEOMETRY_STREAM_TARGET}:
        target = V2_8_OVERLAY_GEOMETRY_STREAM_TARGET
    else:
        raise ValueError(f"unsupported overlay continuation output_mode: {output_mode}")
    for plan in v2_8_overlay_area_continuation_plan():
        if plan["target"] == target:
            return plan
    raise AssertionError("overlay continuation plan target disappeared")


def validate_v2_8_overlay_area_continuation_plan() -> dict[str, Any]:
    plans = v2_8_overlay_area_continuation_plan()
    errors: list[str] = []
    targets = tuple(plan["target"] for plan in plans)
    if targets != (V2_8_OVERLAY_AREA_SCALAR_TARGET, V2_8_OVERLAY_GEOMETRY_STREAM_TARGET):
        errors.append("overlay continuation targets must remain scalar-first then streamed-geometry")
    if plans[0]["priority"] != "P0":
        errors.append("scalar exact-area continuation must be P0")
    if plans[1]["priority"] != "P1":
        errors.append("streamed overlay geometry continuation must be P1")
    for plan in plans:
        if plan["input_contract"] != V2_8_OVERLAY_AREA_INPUT_CONTRACT:
            errors.append(f"{plan['target']} has wrong input contract")
        for field in (
            "app_specific_engine_logic_allowed",
            "automatic_partner_selection_allowed",
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "full_overlay_completion_claim_authorized",
        ):
            if plan[field] is not False:
                errors.append(f"{plan['target']} authorizes {field}")
        boundary = str(plan["claim_boundary"])
        for phrase in (
            "does not authorize release",
            "public speedup wording",
            "app-specific native-engine behavior",
        ):
            if phrase not in boundary:
                errors.append(f"{plan['target']} claim boundary is missing {phrase}")
    return {
        "version": V2_8_OVERLAY_AREA_CONTINUATION_VERSION,
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "target_count": len(plans),
        "targets": targets,
        "claim_boundary": V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY,
    }


__all__ = [
    "V28OverlayAreaContinuationPlan",
    "V2_8_OVERLAY_AREA_CONTINUATION_CLAIM_BOUNDARY",
    "V2_8_OVERLAY_AREA_CONTINUATION_STATUS",
    "V2_8_OVERLAY_AREA_CONTINUATION_VERSION",
    "V2_8_OVERLAY_AREA_INPUT_CONTRACT",
    "V2_8_OVERLAY_AREA_SCALAR_TARGET",
    "V2_8_OVERLAY_GEOMETRY_STREAM_TARGET",
    "select_v2_8_overlay_area_continuation_target",
    "v2_8_overlay_area_continuation_plan",
    "validate_v2_8_overlay_area_continuation_plan",
]
