from __future__ import annotations

from dataclasses import dataclass


V4_GOAL4683_CONTACT_WITNESS_AUDIT_STATUS = (
    "goal4683_no_go_contact_witness_target_reuses_v2_14_collect_k_and_partner_witness"
)
V4_GOAL4683_AUDITED_TARGET = "AABB_PAIR_EXACT_WITNESS_DEVICE_COLUMNS_2D"
V4_GOAL4683_NEXT_GOAL = "Goal4684 high-performance V4 target reset"


@dataclass(frozen=True)
class V4Goal4683ContactWitnessDesignAudit:
    status: str
    audited_target: str
    verdict: str
    v2_14_preexisting_surfaces: tuple[str, ...]
    current_preexisting_surfaces: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    next_goal: str
    target_killed_for_v4_0_performance_path: bool = True
    implementation_authorized: bool = False
    pod_authorized: bool = False
    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    app_identity_kernel_authorized: bool = False
    partner_migration_speed_credit_authorized: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "audited_target": self.audited_target,
            "verdict": self.verdict,
            "v2_14_preexisting_surfaces": self.v2_14_preexisting_surfaces,
            "current_preexisting_surfaces": self.current_preexisting_surfaces,
            "blocking_reasons": self.blocking_reasons,
            "next_goal": self.next_goal,
            "target_killed_for_v4_0_performance_path": self.target_killed_for_v4_0_performance_path,
            "implementation_authorized": self.implementation_authorized,
            "pod_authorized": self.pod_authorized,
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "app_identity_kernel_authorized": self.app_identity_kernel_authorized,
            "partner_migration_speed_credit_authorized": self.partner_migration_speed_credit_authorized,
        }


def v4_goal4683_contact_witness_design_audit() -> V4Goal4683ContactWitnessDesignAudit:
    return V4Goal4683ContactWitnessDesignAudit(
        status=V4_GOAL4683_CONTACT_WITNESS_AUDIT_STATUS,
        audited_target=V4_GOAL4683_AUDITED_TARGET,
        verdict=(
            "no_go: the proposed contact/witness target is not a clean V4.0 "
            "high-performance lever. V2.14 already contains bounded collect-k "
            "native/OptiX/Embree surfaces, and the current tree already contains "
            "partner exact-witness device-column adapters. Continuing would risk "
            "rebranding V2.14 collect-k plus partner witness plumbing as a V4 win."
        ),
        v2_14_preexisting_surfaces=(
            "rtdl_optix_collect_k_bounded_i64",
            "rtdl_optix_collect_k_bounded_i64_device",
            "rtdl_embree_collect_k_bounded_i64",
            "collect_native_i64_rows_with_backend_symbol",
            "collect_native_i64_rows_into_prepared_output_buffer",
            "run_native_collect_k_bounded_rows_with_prepared_result_buffer",
        ),
        current_preexisting_surfaces=(
            "allocate_segment_polygon_witness_partner_device_output_columns",
            "segment_polygon_exact_witness_pair_page_optix_partner_columns",
            "segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns",
            "ray_primitive_witness_pair_page_optix_prepared_partner_columns",
            "bounded_collect_finalize_i64_partner_columns",
            "collect_k_bounded_i64_device",
        ),
        blocking_reasons=(
            "The generic bounded candidate collection core is preexisting V2.14 work, not a new V4 lever.",
            "The exact-witness device-column continuation exists as partner adapter work, so promoting it would be partner/productization credit unless a new fused native operator is designed.",
            "A contact-specific fused witness route would violate the V4 app-identity-kernel lock unless restated as a generic operator with fresh design and bars.",
            "No POD run is authorized because the design audit already fails the absent-lever gate.",
        ),
        next_goal=(
            "Goal4684 must reset the high-performance V4 search: either identify "
            "one genuinely absent, app-name-free Tier-2 fused primitive with a "
            "material-speed hypothesis, or stop the formal high-performance V4 "
            "path and keep the current bounded-operator/productization truth."
        ),
    )


def validate_v4_goal4683_contact_witness_design_audit() -> dict[str, object]:
    audit = v4_goal4683_contact_witness_design_audit()
    payload = audit.as_dict()
    missing: list[str] = []
    if payload["status"] != V4_GOAL4683_CONTACT_WITNESS_AUDIT_STATUS:
        missing.append("status")
    if payload["audited_target"] != V4_GOAL4683_AUDITED_TARGET:
        missing.append("audited_target")
    if "V2.14 already contains bounded collect-k" not in str(payload["verdict"]):
        missing.append("v2_14_collect_k_verdict")
    if not any("collect_k_bounded" in surface for surface in payload["v2_14_preexisting_surfaces"]):
        missing.append("v2_14_collect_k_surfaces")
    if not any("exact_witness" in surface for surface in payload["current_preexisting_surfaces"]):
        missing.append("current_exact_witness_surfaces")
    if "app-identity-kernel" not in " ".join(str(reason) for reason in payload["blocking_reasons"]):
        missing.append("app_identity_kernel_lock")
    if "Goal4684" not in str(payload["next_goal"]):
        missing.append("next_goal")
    for key in (
        "target_killed_for_v4_0_performance_path",
    ):
        if payload.get(key) is not True:
            missing.append(key)
    for key in (
        "implementation_authorized",
        "pod_authorized",
        "release_authorized",
        "public_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "app_identity_kernel_authorized",
        "partner_migration_speed_credit_authorized",
    ):
        if payload.get(key) is not False:
            missing.append(key)
    return {
        "status": "passed" if not missing else "failed",
        "missing_or_invalid": tuple(missing),
        "audit": payload,
        "release_authorized": False,
    }


__all__ = [
    "V4_GOAL4683_CONTACT_WITNESS_AUDIT_STATUS",
    "V4_GOAL4683_AUDITED_TARGET",
    "V4_GOAL4683_NEXT_GOAL",
    "V4Goal4683ContactWitnessDesignAudit",
    "v4_goal4683_contact_witness_design_audit",
    "validate_v4_goal4683_contact_witness_design_audit",
]
