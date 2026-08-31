"""Trusted OptiX round-linear-curve wrapper for Goal5834 Callback IR."""

from __future__ import annotations

from .v4_callback_abi import CompiledCallbackAbi
from .v4_callback_optix_wrapper_codegen import (
    CallbackWrapperCodegenError,
    GeneratedOptixWrapper,
)
from .v4_curve_callback_abi import verify_curve_callback_abi
from .v4_callback_ir import ScalarKind
from .v4_curve_physical_schema import (
    BUILTIN_CURVE_BOOLEAN_TEMPLATE,
    BUILTIN_CURVE_TEMPLATE,
    CurveCanonicalPlan,
    VerifiedCurvePhysicalAuthority,
    verify_builtin_curve_physical_schema,
)
from .v4_sphere_optix_wrapper_codegen import (
    _generate_trusted_optix_first_contact_wrapper_v1,
)


def _fresh(authority, plan):
    if not isinstance(authority, VerifiedCurvePhysicalAuthority):
        raise CallbackWrapperCodegenError(
            "curve_authority", "live VerifiedCurvePhysicalAuthority required")
    fresh = verify_builtin_curve_physical_schema(
        authority.callback, authority.schema, target=authority.target)
    if fresh != authority or plan != fresh.canonical_plan:
        raise CallbackWrapperCodegenError(
            "curve_authority", "authority/plan does not rederive exactly")
    if plan.template_id != authority.schema.template_id \
            or plan.template_id not in {
                BUILTIN_CURVE_TEMPLATE, BUILTIN_CURVE_BOOLEAN_TEMPLATE} \
            or plan.executable:
        raise CallbackWrapperCodegenError(
            "curve_plan", "non-executable canonical curve plan required")
    return fresh


def generate_trusted_optix_curve_wrapper_v1(
    authority: VerifiedCurvePhysicalAuthority,
    plan: CurveCanonicalPlan,
    abi: CompiledCallbackAbi,
) -> GeneratedOptixWrapper:
    boolean = plan.template_id == BUILTIN_CURVE_BOOLEAN_TEMPLATE
    return _generate_trusted_optix_first_contact_wrapper_v1(
        authority,
        plan,
        abi,
        fresh_validator=_fresh,
        abi_validator=verify_curve_callback_abi,
        template_id=BUILTIN_CURVE_TEMPLATE,
        namespace="curve",
        wrapper_schema=(
            "rtdl.v4.generated_trusted_optix_curve_boolean_wrapper.v1"
            if boolean else
            "rtdl.v4.generated_trusted_optix_curve_wrapper.v1"),
        record_scalar_kinds=(
            (ScalarKind.U32,) if boolean else
            (ScalarKind.U32, ScalarKind.F32, ScalarKind.U32)),
    )


__all__ = ["generate_trusted_optix_curve_wrapper_v1"]
