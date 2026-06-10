from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .partner_continuation_protocol import V2_5_ALLOWED_PARTNERS
from .partner_continuation_protocol import V2_5_CONFORMANCE_PARTNER
from .partner_continuation_protocol import V2_5_FALLBACK_PARTNER
from .partner_continuation_protocol import V2_5_PRIMARY_PARTNER
from .partner_continuation_protocol import V2_5_REFERENCE_PARTNER
from .primitive_hierarchy import PrimitiveHierarchyNode
from .primitive_hierarchy import find_primitive_hierarchy_node
from .primitive_recipes import COMPOSITION_RECIPES
from .primitive_recipes import CompositionRecipe
from .primitive_recipes import CompositionRecipeMatch
from .primitive_recipes import find_recipe
from .primitive_recipes import validate_composition_recipes
from .v2_5_partner_support_matrix import V2_5_SUPPORT_STATUS_UNSUPPORTED
from .v2_5_partner_support_matrix import plan_v2_5_partner_support


PRIMITIVE_ADVISORY_PLANNER_VERSION = "rtdl.primitive_advisory_planner.v1"
PRIMITIVE_ADVISORY_PLANNER_EXECUTES = False
PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED = False
PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY = (
    "Current primitive advisory plans are explain-only metadata. They do not "
    "execute, dispatch, auto-select partners, authorize release readiness, "
    "authorize public speedup wording, authorize broad RT-core wording, "
    "authorize true zero-copy wording, or promote internal/candidate primitive "
    "steps to stable public primitives."
)

_EXTERNAL_STABLE_STATUSES = (
    "stable_primitive",
    "stable_behavior",
    "stable_compatibility_path",
)


@dataclass(frozen=True)
class PrimitivePlanStep:
    primitive_id: str
    title: str
    layer: str
    primitive_status: str
    phase: str
    role: str
    required: bool
    outputs: tuple[str, ...]
    backends: tuple[str, ...]
    partner_ops: tuple[str, ...]
    boundary: str

    @property
    def externally_stable(self) -> bool:
        return self.primitive_status in _EXTERNAL_STABLE_STATUSES

    def to_dict(self) -> dict[str, object]:
        return {
            "primitive_id": self.primitive_id,
            "title": self.title,
            "layer": self.layer,
            "primitive_status": self.primitive_status,
            "phase": self.phase,
            "role": self.role,
            "required": self.required,
            "outputs": self.outputs,
            "backends": self.backends,
            "partner_ops": self.partner_ops,
            "boundary": self.boundary,
            "externally_stable": self.externally_stable,
        }


@dataclass(frozen=True)
class PrimitivePartnerOption:
    operation: str
    partner: str
    status: str
    supported: bool
    execution_backend: str
    requires_neutral_buffer_seam: bool
    requires_cuda: bool
    requires_sm70_plus: bool
    same_contract_reference_required: bool
    promoted_performance_path: bool
    public_speedup_claim_authorized: bool
    true_zero_copy_claim_authorized: bool
    notes: str
    claim_boundary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation,
            "partner": self.partner,
            "status": self.status,
            "supported": self.supported,
            "execution_backend": self.execution_backend,
            "requires_neutral_buffer_seam": self.requires_neutral_buffer_seam,
            "requires_cuda": self.requires_cuda,
            "requires_sm70_plus": self.requires_sm70_plus,
            "same_contract_reference_required": self.same_contract_reference_required,
            "promoted_performance_path": self.promoted_performance_path,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "true_zero_copy_claim_authorized": self.true_zero_copy_claim_authorized,
            "notes": self.notes,
            "claim_boundary": self.claim_boundary,
        }


@dataclass(frozen=True)
class PrimitiveAdvisoryPlan:
    recipe_id: str
    title: str
    recipe_status: str
    score: int
    matched_on: tuple[str, ...]
    recommendation: str
    primitive_steps: tuple[PrimitivePlanStep, ...]
    partner_options: tuple[PrimitivePartnerOption, ...]
    recipe_partner_policy: str
    recipe_claim_boundary: str
    recipe_boundary: str
    requested_partner: str | None = None
    selected_partner: str | None = None
    executes: bool = PRIMITIVE_ADVISORY_PLANNER_EXECUTES
    automatic_partner_selection_allowed: bool = PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED
    hidden_dispatch_allowed: bool = False
    requires_explicit_partner_choice: bool = False
    status_boundary: str = "advisory_plan_does_not_promote_internal_or_candidate_primitive_steps"
    claim_boundary: str = PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY
    evidence_paths: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def step_statuses(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(step.primitive_status for step in self.primitive_steps))

    @property
    def non_stable_step_ids(self) -> tuple[str, ...]:
        return tuple(
            step.primitive_id
            for step in self.primitive_steps
            if not step.externally_stable
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "planner_version": PRIMITIVE_ADVISORY_PLANNER_VERSION,
            "recipe_id": self.recipe_id,
            "title": self.title,
            "recipe_status": self.recipe_status,
            "score": self.score,
            "matched_on": self.matched_on,
            "recommendation": self.recommendation,
            "primitive_steps": tuple(step.to_dict() for step in self.primitive_steps),
            "step_statuses": self.step_statuses,
            "non_stable_step_ids": self.non_stable_step_ids,
            "partner_options": tuple(option.to_dict() for option in self.partner_options),
            "recipe_partner_policy": self.recipe_partner_policy,
            "recipe_claim_boundary": self.recipe_claim_boundary,
            "recipe_boundary": self.recipe_boundary,
            "requested_partner": self.requested_partner,
            "selected_partner": self.selected_partner,
            "executes": self.executes,
            "automatic_partner_selection_allowed": self.automatic_partner_selection_allowed,
            "hidden_dispatch_allowed": self.hidden_dispatch_allowed,
            "requires_explicit_partner_choice": self.requires_explicit_partner_choice,
            "status_boundary": self.status_boundary,
            "claim_boundary": self.claim_boundary,
            "evidence_paths": self.evidence_paths,
            "warnings": self.warnings,
        }


def plan_continuation(
    query: str | None = None,
    *,
    recipe_id: str | None = None,
    intent: str | None = None,
    shape: str | None = None,
    dim: str | None = None,
    output: str | None = None,
    exactness: str | None = None,
    keying: str | None = None,
    text: str | None = None,
    partner: str | None = None,
    max_plans: int = 3,
) -> tuple[PrimitiveAdvisoryPlan, ...]:
    """Return explain-only primitive/recipe plans for a caller intent.

    The planner consumes discovery recipes and partner-support metadata. It
    never calls native code, never dispatches a partner, and never selects a
    partner silently. The optional ``partner`` argument is recorded as a caller
    preference so the returned support cells can explain whether that partner is
    known for matching continuation operations.
    """

    if max_plans < 0:
        raise ValueError("max_plans must be non-negative")
    requested_partner = _normalize_partner(partner) if partner else None
    matches = _recipe_matches(
        query=query,
        recipe_id=recipe_id,
        intent=intent,
        shape=shape,
        dim=dim,
        output=output,
        exactness=exactness,
        keying=keying,
        text=text,
    )
    return tuple(
        _plan_from_match(match, requested_partner=requested_partner)
        for match in matches[:max_plans]
    )


def validate_primitive_advisory_planner() -> dict[str, object]:
    recipe_validation = validate_composition_recipes()
    errors: list[str] = []
    if recipe_validation.get("valid") is not True:
        errors.append("composition recipes must validate before planning")
    for recipe in COMPOSITION_RECIPES:
        plans = plan_continuation(recipe_id=recipe.id, max_plans=1)
        if len(plans) != 1:
            errors.append(f"{recipe.id} did not produce one direct advisory plan")
            continue
        plan = plans[0]
        if plan.executes is not False:
            errors.append(f"{recipe.id} plan must not execute")
        if plan.selected_partner is not None:
            errors.append(f"{recipe.id} plan must not select a partner")
        if plan.automatic_partner_selection_allowed is not False:
            errors.append(f"{recipe.id} plan must block automatic partner selection")
        if plan.hidden_dispatch_allowed is not False:
            errors.append(f"{recipe.id} plan must block hidden dispatch")
        if not plan.primitive_steps:
            errors.append(f"{recipe.id} plan must expose primitive steps")
        if not plan.step_statuses:
            errors.append(f"{recipe.id} plan must expose primitive step statuses")
        if plan.non_stable_step_ids and "does_not_promote" not in plan.status_boundary:
            errors.append(f"{recipe.id} plan must not promote non-stable primitive steps")
        for option in plan.partner_options:
            if option.promoted_performance_path:
                errors.append(f"{recipe.id} promotes partner performance path for {option.operation}")
            if option.public_speedup_claim_authorized:
                errors.append(f"{recipe.id} authorizes partner speedup claim for {option.operation}")
            if option.true_zero_copy_claim_authorized:
                errors.append(f"{recipe.id} authorizes zero-copy claim for {option.operation}")
    return {
        "status": "accept" if not errors else "reject",
        "planner_version": PRIMITIVE_ADVISORY_PLANNER_VERSION,
        "executes": PRIMITIVE_ADVISORY_PLANNER_EXECUTES,
        "automatic_partner_selection_allowed": PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED,
        "recipe_validation_valid": recipe_validation.get("valid"),
        "recipe_count": recipe_validation.get("recipe_count"),
        "errors": tuple(errors),
        "claim_boundary": PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY,
    }


def _recipe_matches(
    *,
    query: str | None,
    recipe_id: str | None,
    intent: str | None,
    shape: str | None,
    dim: str | None,
    output: str | None,
    exactness: str | None,
    keying: str | None,
    text: str | None,
) -> tuple[CompositionRecipeMatch, ...]:
    if recipe_id is not None:
        recipe = _recipe_by_id(recipe_id)
        return (
            CompositionRecipeMatch(
                recipe_id=recipe.id,
                title=recipe.title,
                status=recipe.status,
                score=1000,
                matched_on=(f"recipe_id:{recipe.id}",),
                primitive_ids=tuple(step.primitive_id for step in recipe.steps),
                partner_policy=recipe.partner_policy,
                claim_boundary=recipe.claim_boundary,
            ),
        )
    return find_recipe(
        query,
        intent=intent,
        shape=shape,
        dim=dim,
        output=output,
        exactness=exactness,
        keying=keying,
        text=text,
    )


def _plan_from_match(
    match: CompositionRecipeMatch,
    *,
    requested_partner: str | None,
) -> PrimitiveAdvisoryPlan:
    recipe = _recipe_by_id(match.recipe_id)
    steps = _plan_steps(recipe)
    partner_operations = tuple(
        dict.fromkeys(
            operation
            for step in steps
            for operation in step.partner_ops
        )
    )
    options = _partner_options(partner_operations, requested_partner=requested_partner)
    warnings = _plan_warnings(steps, options, requested_partner)
    return PrimitiveAdvisoryPlan(
        recipe_id=recipe.id,
        title=recipe.title,
        recipe_status=recipe.status,
        score=match.score,
        matched_on=match.matched_on,
        recommendation=_recommendation(recipe, options),
        primitive_steps=steps,
        partner_options=options,
        recipe_partner_policy=recipe.partner_policy,
        recipe_claim_boundary=recipe.claim_boundary,
        recipe_boundary=recipe.boundary,
        requested_partner=requested_partner,
        selected_partner=None,
        requires_explicit_partner_choice=bool(partner_operations),
        evidence_paths=recipe.evidence_paths,
        warnings=warnings,
    )


def _plan_steps(recipe: CompositionRecipe) -> tuple[PrimitivePlanStep, ...]:
    steps: list[PrimitivePlanStep] = []
    for recipe_step in recipe.steps:
        node = find_primitive_hierarchy_node(recipe_step.primitive_id)
        steps.append(_plan_step_from_node(node, recipe_step.phase, recipe_step.role, recipe_step.required))
    return tuple(steps)


def _plan_step_from_node(
    node: PrimitiveHierarchyNode,
    phase: str,
    role: str,
    required: bool,
) -> PrimitivePlanStep:
    return PrimitivePlanStep(
        primitive_id=node.id,
        title=node.title,
        layer=node.layer,
        primitive_status=node.status,
        phase=phase,
        role=role,
        required=required,
        outputs=node.outputs,
        backends=node.backends,
        partner_ops=node.partner_ops,
        boundary=node.boundary,
    )


def _partner_options(
    operations: Iterable[str],
    *,
    requested_partner: str | None,
) -> tuple[PrimitivePartnerOption, ...]:
    rows: list[PrimitivePartnerOption] = []
    for operation in operations:
        for partner in V2_5_ALLOWED_PARTNERS:
            cell = plan_v2_5_partner_support(operation, partner)
            if (
                cell["status"] == V2_5_SUPPORT_STATUS_UNSUPPORTED
                and partner != requested_partner
            ):
                continue
            rows.append(
                PrimitivePartnerOption(
                    operation=str(cell["operation"]),
                    partner=str(cell["partner"]),
                    status=str(cell["status"]),
                    supported=bool(cell["supported"]),
                    execution_backend=str(cell["execution_backend"]),
                    requires_neutral_buffer_seam=bool(cell["requires_neutral_buffer_seam"]),
                    requires_cuda=bool(cell["requires_cuda"]),
                    requires_sm70_plus=bool(cell["requires_sm70_plus"]),
                    same_contract_reference_required=bool(cell["same_contract_reference_required"]),
                    promoted_performance_path=bool(cell["promoted_performance_path"]),
                    public_speedup_claim_authorized=bool(cell["public_speedup_claim_authorized"]),
                    true_zero_copy_claim_authorized=bool(cell["true_zero_copy_claim_authorized"]),
                    notes=str(cell["notes"]),
                    claim_boundary=str(cell["claim_boundary"]),
                )
            )
    return tuple(rows)


def _plan_warnings(
    steps: tuple[PrimitivePlanStep, ...],
    options: tuple[PrimitivePartnerOption, ...],
    requested_partner: str | None,
) -> tuple[str, ...]:
    warnings: list[str] = []
    non_stable = tuple(step.primitive_id for step in steps if not step.externally_stable)
    if non_stable:
        warnings.append(
            "recipe references non-stable primitive steps; advisory plan does not promote them: "
            + ", ".join(non_stable)
        )
    if requested_partner is not None:
        warnings.append(
            f"requested partner `{requested_partner}` is recorded for explanation only; selected_partner remains None"
        )
        if options and not any(option.partner == requested_partner and option.supported for option in options):
            warnings.append(
                f"requested partner `{requested_partner}` has no supported option for the matched partner operations"
            )
    if options:
        warnings.append("partner options require explicit caller choice and same-contract evidence")
    return tuple(warnings)


def _recommendation(
    recipe: CompositionRecipe,
    options: tuple[PrimitivePartnerOption, ...],
) -> str:
    if options:
        return "primitive_first_with_explicit_partner_options"
    if "no partner" in recipe.partner_policy.lower():
        return "primitive_first"
    return "advisory_recipe_with_caller_owned_continuation"


def _recipe_by_id(recipe_id: str) -> CompositionRecipe:
    for recipe in COMPOSITION_RECIPES:
        if recipe.id == recipe_id:
            return recipe
    raise KeyError(f"unknown composition recipe: {recipe_id}")


def _normalize_partner(partner: str) -> str:
    normalized = str(partner).strip().lower().replace("-", "_")
    aliases = {
        "python": V2_5_REFERENCE_PARTNER,
        "reference": V2_5_REFERENCE_PARTNER,
        "triton_preview": V2_5_PRIMARY_PARTNER,
        "numba_fallback": V2_5_FALLBACK_PARTNER,
        "cupy": V2_5_CONFORMANCE_PARTNER,
        "cupy_conformance": V2_5_CONFORMANCE_PARTNER,
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in V2_5_ALLOWED_PARTNERS:
        raise ValueError(f"unsupported advisory-planner partner: {partner}")
    return normalized


__all__ = [
    "PRIMITIVE_ADVISORY_PLANNER_AUTO_PARTNER_SELECTION_ALLOWED",
    "PRIMITIVE_ADVISORY_PLANNER_CLAIM_BOUNDARY",
    "PRIMITIVE_ADVISORY_PLANNER_EXECUTES",
    "PRIMITIVE_ADVISORY_PLANNER_VERSION",
    "PrimitiveAdvisoryPlan",
    "PrimitivePartnerOption",
    "PrimitivePlanStep",
    "plan_continuation",
    "validate_primitive_advisory_planner",
]
