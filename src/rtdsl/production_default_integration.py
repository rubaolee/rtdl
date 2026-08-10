"""Production binding for the compiler-owned deterministic DEFAULT.

This module is the only bridge from compiler semantic/resource facts to the
Goal5696 DEFAULT front door.  It accepts no candidate, backend, template,
program, application, paper, dataset, or harness identity.  A selected plan is
not executable until :func:`bind_default_plan_to_lowering` proves that the
actual registered lowering has the exact winner backend/template and source
identity.

Mandatory NVIDIA RT Actions require the source-bound OptiX program contract
from ``default_compiler_frontdoor``.  Continuation-only Actions may be planned
as explicit partner stages, but their plans carry no behavioral OptiX claim
and cannot satisfy a whole-program traversal obligation by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from .default_compiler_frontdoor import (
    PreparedDefaultProofAuthority,
    _compile_canonical_provider_plan,
    _compile_prepared_default_plan,
    compile_default_plan,
)
from .default_physical_selection import (
    ANNOTATION_NONE,
    NORMAL_PROFILE,
    OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,
    ActionSelectionDescriptor,
    CandidateDeclaration,
    TargetSelectionDescriptor,
    current_registry_snapshot,
    select_default,
)


PRODUCTION_DEFAULT_POLICY_VERSION = "rtdl.production_default.goal5697.v1"
PRODUCTION_DEFAULT_PLAN_SCHEMA = "rtdl.production_default.plan.v1"
PRODUCTION_DEFAULT_BINDING_SCHEMA = "rtdl.production_default.binding.v1"
PRODUCTION_DEFAULT_ADMISSION_SCHEMA = "rtdl.production_default.admission.v1"


class ProductionDefaultIntegrationError(RuntimeError):
    """Typed fail-closed production DEFAULT error."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = str(code)
        self.detail = str(detail)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_device_memory_limit_bytes() -> int | None:
    """Return an actual runtime device-memory fact without selecting a route."""

    try:
        from numba import cuda

        total = int(cuda.current_context().get_memory_info()[1])
        if total > 0:
            return total
    except Exception:  # pragma: no cover - backend availability is host-specific
        pass
    try:
        import cupy as cp

        total = int(cp.cuda.runtime.memGetInfo()[1])
        if total > 0:
            return total
    except Exception:  # pragma: no cover - backend availability is host-specific
        pass
    return None


def _checked_u64(value: object, *, field: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value >= 1 << 64
    ):
        raise ProductionDefaultIntegrationError("INVALID_UNSIGNED_FACT", field)
    return value


def _validate_sha256(value: object, *, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ProductionDefaultIntegrationError("INVALID_SHA256", field)
    try:
        int(value, 16)
    except ValueError as exc:
        raise ProductionDefaultIntegrationError("INVALID_SHA256", field) from exc
    if value != value.lower():
        raise ProductionDefaultIntegrationError("NONCANONICAL_SHA256", field)
    return value


def _matching_declarations(
    semantic_kind: str,
    action_contract_class: str,
) -> tuple[CandidateDeclaration, ...]:
    registry = current_registry_snapshot()
    rows = tuple(
        row
        for row in registry.declarations
        if row.semantic_kind == semantic_kind
        and action_contract_class in row.accepted_action_contract_classes
    )
    if not rows:
        raise ProductionDefaultIntegrationError(
            "PRODUCTION_ACTION_OUTSIDE_REVIEWED_REGISTRY",
            f"{semantic_kind}/{action_contract_class}",
        )
    return rows


def make_production_action_descriptor(
    *,
    semantic_kind: str,
    action_contract_class: str,
    action_semantic_digest: str,
    output_contract: object,
    work_domain: object,
    input_bytes: int,
    output_bytes: int,
    prepared_bytes: int,
    logical_cardinality_bound: int,
    pair_cardinality_bound: int,
    logical_item_bytes_bound: int,
    pair_item_bytes_bound: int,
) -> ActionSelectionDescriptor:
    """Derive a descriptor from compiler facts, never from a fixture/candidate."""

    rows = _matching_declarations(semantic_kind, action_contract_class)
    action_digest = _validate_sha256(
        action_semantic_digest, field="action_semantic_digest"
    )
    values = {
        "input_bytes": input_bytes,
        "output_bytes": output_bytes,
        "prepared_bytes": prepared_bytes,
        "logical_cardinality_bound": logical_cardinality_bound,
        "pair_cardinality_bound": pair_cardinality_bound,
        "logical_item_bytes_bound": logical_item_bytes_bound,
        "pair_item_bytes_bound": pair_item_bytes_bound,
    }
    checked = {
        name: _checked_u64(value, field=name) for name, value in values.items()
    }
    return ActionSelectionDescriptor(
        semantic_kind=semantic_kind,
        action_contract_class=action_contract_class,
        action_digest=action_digest,
        output_contract_digest=_digest(output_contract),
        work_domain_digest=_digest(work_domain),
        input_bytes=checked["input_bytes"],
        output_bytes=checked["output_bytes"],
        prepared_bytes=checked["prepared_bytes"],
        logical_cardinality_bound=checked["logical_cardinality_bound"],
        pair_cardinality_bound=checked["pair_cardinality_bound"],
        logical_item_bytes_bound=checked["logical_item_bytes_bound"],
        pair_item_bytes_bound=checked["pair_item_bytes_bound"],
        host_visible_canonical_output_required=True,
        admitted_proof_digests=tuple(sorted(row.proof_digest for row in rows)),
        admitted_resource_bound_digests=tuple(
            sorted(row.resource_bound_digest for row in rows)
        ),
        admitted_reuse_contract_digests=tuple(
            sorted(row.reuse_contract_digest for row in rows)
        ),
        admitted_template_digests=tuple(
            sorted(row.template_digest for row in rows)
        ),
    )


def make_production_target_descriptor(
    *,
    target_identity: object,
    available_providers: Iterable[str],
    memory_limit_bytes: int,
    mandatory_nvidia_rt: bool,
) -> TargetSelectionDescriptor:
    """Bind compiler-probed target facts to the current registry."""

    providers = tuple(sorted(set(str(item) for item in available_providers)))
    if not providers:
        raise ProductionDefaultIntegrationError("EMPTY_PRODUCTION_PROVIDER_SET")
    memory_limit = _checked_u64(memory_limit_bytes, field="memory_limit_bytes")
    if memory_limit == 0:
        raise ProductionDefaultIntegrationError("ZERO_PRODUCTION_MEMORY_LIMIT")
    registry = current_registry_snapshot()
    admitted_abis = tuple(
        sorted(
            row.provider_abi_requirement_digest
            for row in registry.declarations
            if set(row.required_providers).issubset(set(providers))
        )
    )
    return TargetSelectionDescriptor(
        target_digest=_digest(target_identity),
        available_providers=providers,
        allowed_execution_classes=(),
        required_physical_capabilities=(
            (OPTIX_TRAVERSAL_PROGRAM_CAPABILITY,)
            if mandatory_nvidia_rt
            else ()
        ),
        available_provider_abi_requirement_digests=admitted_abis,
        memory_limit_bytes=memory_limit,
        profile=NORMAL_PROFILE,
        unprofiled=True,
    )


def _partner_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    annotation_mode: str,
) -> dict[str, object]:
    registry = current_registry_snapshot()
    selection = select_default(
        action,
        target,
        registry=registry,
        annotation_mode=annotation_mode,
    )
    if selection.get("status") != "SELECTED":
        raise ProductionDefaultIntegrationError(
            "PARTNER_DEFAULT_SELECTION_FAILED",
            str(selection.get("error_code", "UNKNOWN")),
        )
    body: dict[str, object] = {
        "schema": "rtdl.production_default.partner_plan.v1",
        "policy_version": PRODUCTION_DEFAULT_POLICY_VERSION,
        "status": "PLANNED_PARTNER_STAGE",
        "action": action.as_dict(),
        "target": target.as_dict(),
        "registry_sha256": registry.digest,
        "selection_receipt": selection,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "selected_candidate_stable_id": selection["winner_stable_id"],
        "selected_candidate_sha256": selection["winner_candidate_sha256"],
        "mandatory_optix_target": False,
        "behavioral_optix_receipt_required": False,
        "partner_stage_only": True,
        "partner_stage_can_satisfy_rt_claim": False,
        "candidate_override_accepted": False,
        "application_identity_used": False,
        "production_default_changed": True,
    }
    body["plan_sha256"] = _digest(body)
    return body


def _compile_production_default_plan_impl(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    mandatory_nvidia_rt: bool,
    repository_root: Path,
    annotation_mode: str = ANNOTATION_NONE,
    prepared_proof_authority: PreparedDefaultProofAuthority | None = None,
) -> dict[str, object]:
    """Select one production plan from compiler-owned facts only."""

    required = OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in (
        target.required_physical_capabilities
    )
    if required is not mandatory_nvidia_rt:
        raise ProductionDefaultIntegrationError(
            "PRODUCTION_TARGET_POLICY_MISMATCH"
        )
    registry = current_registry_snapshot()
    if mandatory_nvidia_rt:
        if prepared_proof_authority is None:
            selected = compile_default_plan(
                action,
                target,
                registry_sha256=registry.digest,
                annotation_mode=annotation_mode,
                repository_root=repository_root,
            )
        else:
            selected = _compile_prepared_default_plan(
                action,
                target,
                registry_sha256=registry.digest,
                annotation_mode=annotation_mode,
                repository_root=repository_root,
                prepared_proof_authority=prepared_proof_authority,
            )
        if selected.get("status") != "PLANNED":
            selected_code = str(selected.get("error_code", "UNKNOWN"))
            selected_detail = str(selected.get("error_detail", ""))
            raise ProductionDefaultIntegrationError(
                "MANDATORY_RT_DEFAULT_SELECTION_FAILED",
                (
                    f"{selected_code}:{selected_detail}"
                    if selected_detail
                    else selected_code
                ),
            )
        plan = dict(selected)
    else:
        plan = _partner_plan(action, target, annotation_mode=annotation_mode)
    body: dict[str, object] = {
        "schema": PRODUCTION_DEFAULT_PLAN_SCHEMA,
        "policy_version": PRODUCTION_DEFAULT_POLICY_VERSION,
        "status": "PLANNED",
        "mandatory_nvidia_rt": mandatory_nvidia_rt,
        "partner_stage_only": not mandatory_nvidia_rt,
        "default_plan": plan,
        "default_plan_sha256": plan["plan_sha256"],
        "selected_candidate_stable_id": plan["selected_candidate_stable_id"],
        "selected_candidate_sha256": plan["selected_candidate_sha256"],
        "selected_physical_configuration_policy": plan.get(
            "selected_physical_configuration_policy"
        ),
        "selected_physical_configuration_policy_sha256": plan.get(
            "selected_physical_configuration_policy_sha256"
        ),
        "candidate_override_accepted": False,
        "backend_override_accepted": False,
        "template_override_accepted": False,
        "program_override_accepted": False,
        "application_identity_used": False,
        "production_default_changed": True,
        "behavioral_optix_claimed": False,
        "silicon_rt_core_utilization_claimed": False,
    }
    body["production_plan_sha256"] = _digest(body)
    return body


def compile_production_default_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    mandatory_nvidia_rt: bool,
    repository_root: Path,
    annotation_mode: str = ANNOTATION_NONE,
) -> dict[str, object]:
    """Public production front door; no prepared or selection override exists."""

    return _compile_production_default_plan_impl(
        action,
        target,
        mandatory_nvidia_rt=mandatory_nvidia_rt,
        repository_root=repository_root,
        annotation_mode=annotation_mode,
        prepared_proof_authority=None,
    )


def _compile_canonical_production_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    mandatory_nvidia_rt: bool,
    canonical_provider_stable_id: str,
    repository_root: Path,
    annotation_mode: str = ANNOTATION_NONE,
) -> dict[str, object]:
    """Materialize one already resolved canonical provider, without choice."""

    required = OPTIX_TRAVERSAL_PROGRAM_CAPABILITY in (
        target.required_physical_capabilities
    )
    if required is not mandatory_nvidia_rt:
        raise ProductionDefaultIntegrationError(
            "CANONICAL_PRODUCTION_MATERIALIZER_RT_REQUIREMENT_MISMATCH"
        )
    registry = current_registry_snapshot()
    selected = _compile_canonical_provider_plan(
        action,
        target,
        registry_sha256=registry.digest,
        canonical_provider_stable_id=canonical_provider_stable_id,
        annotation_mode=annotation_mode,
        repository_root=repository_root,
    )
    if selected.get("status") != "PLANNED":
        raise ProductionDefaultIntegrationError(
            "CANONICAL_PROVIDER_MATERIALIZATION_FAILED",
            str(selected.get("error_code", "UNKNOWN")),
        )
    body: dict[str, object] = {
        "schema": PRODUCTION_DEFAULT_PLAN_SCHEMA,
        "policy_version": PRODUCTION_DEFAULT_POLICY_VERSION,
        "status": "PLANNED",
        "mandatory_nvidia_rt": mandatory_nvidia_rt,
        "partner_stage_only": not mandatory_nvidia_rt,
        "default_plan": selected,
        "default_plan_sha256": selected["plan_sha256"],
        "selected_candidate_stable_id": selected[
            "selected_candidate_stable_id"
        ],
        "selected_candidate_sha256": selected["selected_candidate_sha256"],
        "selected_physical_configuration_policy": selected.get(
            "selected_physical_configuration_policy"
        ),
        "selected_physical_configuration_policy_sha256": selected.get(
            "selected_physical_configuration_policy_sha256"
        ),
        "candidate_override_accepted": False,
        "backend_override_accepted": False,
        "template_override_accepted": False,
        "program_override_accepted": False,
        "application_identity_used": False,
        "production_default_changed": True,
        "canonical_provider_materialization_only": True,
        "default_optimizer_selected_provider": False,
        "behavioral_optix_claimed": False,
        "silicon_rt_core_utilization_claimed": False,
    }
    body["production_plan_sha256"] = _digest(body)
    return body


def _compile_prepared_production_default_plan(
    action: ActionSelectionDescriptor,
    target: TargetSelectionDescriptor,
    *,
    mandatory_nvidia_rt: bool,
    repository_root: Path,
    prepared_proof_authority: PreparedDefaultProofAuthority,
    annotation_mode: str = ANNOTATION_NONE,
) -> dict[str, object]:
    """Compiler-internal prepared production front door."""

    if not isinstance(prepared_proof_authority, PreparedDefaultProofAuthority):
        raise TypeError("prepared_proof_authority must be compiler-owned")
    return _compile_production_default_plan_impl(
        action,
        target,
        mandatory_nvidia_rt=mandatory_nvidia_rt,
        repository_root=repository_root,
        annotation_mode=annotation_mode,
        prepared_proof_authority=prepared_proof_authority,
    )


def _selected_declaration(plan: Mapping[str, object]) -> CandidateDeclaration:
    stable_id = plan.get("selected_candidate_stable_id")
    registry = current_registry_snapshot()
    declaration = next(
        (row for row in registry.declarations if row.stable_id == stable_id),
        None,
    )
    if declaration is None:
        raise ProductionDefaultIntegrationError(
            "PRODUCTION_WINNER_NOT_IN_CURRENT_REGISTRY", str(stable_id)
        )
    return declaration


def bind_default_plan_to_lowering(
    plan: Mapping[str, object],
    *,
    actual_backend: str,
    actual_template: str,
    repository_root: Path,
) -> dict[str, object]:
    """Bind the selected DEFAULT row to the actual compiler lowering."""

    if plan.get("schema") != PRODUCTION_DEFAULT_PLAN_SCHEMA:
        raise ProductionDefaultIntegrationError("INVALID_PRODUCTION_PLAN_SCHEMA")
    production_sha = _validate_sha256(
        plan.get("production_plan_sha256"), field="production_plan_sha256"
    )
    body_without_sha = dict(plan)
    body_without_sha.pop("production_plan_sha256", None)
    if _digest(body_without_sha) != production_sha:
        raise ProductionDefaultIntegrationError("PRODUCTION_PLAN_DIGEST_MISMATCH")
    declaration = _selected_declaration(plan)
    nested_plan = plan.get("default_plan")
    if not isinstance(nested_plan, Mapping):
        raise ProductionDefaultIntegrationError("PRODUCTION_DEFAULT_PLAN_MISSING")
    if (
        nested_plan.get("selected_physical_configuration_policy")
        != plan.get("selected_physical_configuration_policy")
        or nested_plan.get("selected_physical_configuration_policy_sha256")
        != plan.get("selected_physical_configuration_policy_sha256")
    ):
        raise ProductionDefaultIntegrationError(
            "PRODUCTION_PHYSICAL_CONFIGURATION_POLICY_BINDING_MISMATCH"
        )
    if actual_backend != declaration.backend:
        raise ProductionDefaultIntegrationError(
            "DEFAULT_BACKEND_LOWERING_MISMATCH",
            f"{actual_backend}!={declaration.backend}",
        )
    if actual_template != declaration.template:
        raise ProductionDefaultIntegrationError(
            "DEFAULT_TEMPLATE_LOWERING_MISMATCH",
            f"{actual_template}!={declaration.template}",
        )
    root = Path(repository_root).resolve()
    path = (root / declaration.source_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ProductionDefaultIntegrationError(
            "DEFAULT_SOURCE_OUTSIDE_REPOSITORY", declaration.source_path
        ) from exc
    if not path.is_file():
        raise ProductionDefaultIntegrationError(
            "DEFAULT_SELECTED_SOURCE_MISSING", declaration.source_path
        )
    if _sha256_file(path) != declaration.source_sha256:
        raise ProductionDefaultIntegrationError(
            "DEFAULT_SELECTED_SOURCE_SHA_MISMATCH", declaration.source_path
        )
    if declaration.source_anchor not in path.read_text(encoding="utf-8"):
        raise ProductionDefaultIntegrationError(
            "DEFAULT_SELECTED_SOURCE_ANCHOR_MISSING", declaration.stable_id
        )
    binding: dict[str, object] = {
        "schema": PRODUCTION_DEFAULT_BINDING_SCHEMA,
        "policy_version": PRODUCTION_DEFAULT_POLICY_VERSION,
        "status": "BOUND",
        "production_plan_sha256": production_sha,
        "selected_candidate_stable_id": declaration.stable_id,
        "selected_candidate_sha256": plan.get("selected_candidate_sha256"),
        "selected_physical_configuration_policy": plan.get(
            "selected_physical_configuration_policy"
        ),
        "selected_physical_configuration_policy_sha256": plan.get(
            "selected_physical_configuration_policy_sha256"
        ),
        "actual_backend": actual_backend,
        "actual_template": actual_template,
        "selected_source_path": declaration.source_path,
        "selected_source_sha256": declaration.source_sha256,
        "selected_source_anchor": declaration.source_anchor,
        "mandatory_nvidia_rt": plan.get("mandatory_nvidia_rt") is True,
        "partner_stage_only": plan.get("partner_stage_only") is True,
        "candidate_override_accepted": False,
        "backend_override_accepted": False,
        "template_override_accepted": False,
        "program_override_accepted": False,
        "behavioral_optix_claimed": False,
        "behavioral_receipt_required_before_optix_claim": (
            plan.get("mandatory_nvidia_rt") is True
        ),
        "silicon_rt_core_utilization_claimed": False,
    }
    binding["binding_sha256"] = _digest(binding)
    return binding


def admit_production_default_execution(
    plan: Mapping[str, object],
    binding: Mapping[str, object],
    traversal_receipt: Mapping[str, object],
    *,
    verified_output_digest: str,
    expected_provider_library_sha256: str,
    repository_root: Path,
) -> dict[str, object]:
    """Admit behavior only after both production binding and traversal proof."""

    if plan.get("schema") != PRODUCTION_DEFAULT_PLAN_SCHEMA:
        raise ProductionDefaultIntegrationError("INVALID_PRODUCTION_PLAN_SCHEMA")
    if binding.get("schema") != PRODUCTION_DEFAULT_BINDING_SCHEMA:
        raise ProductionDefaultIntegrationError("INVALID_PRODUCTION_BINDING_SCHEMA")
    binding_sha = _validate_sha256(
        binding.get("binding_sha256"), field="binding.binding_sha256"
    )
    binding_body = dict(binding)
    binding_body.pop("binding_sha256", None)
    if _digest(binding_body) != binding_sha:
        raise ProductionDefaultIntegrationError("PRODUCTION_BINDING_DIGEST_MISMATCH")
    if (
        binding.get("production_plan_sha256")
        != plan.get("production_plan_sha256")
    ):
        raise ProductionDefaultIntegrationError("PLAN_BINDING_IDENTITY_MISMATCH")
    if plan.get("mandatory_nvidia_rt") is not True:
        raise ProductionDefaultIntegrationError(
            "PARTNER_STAGE_CANNOT_SATISFY_RT_ADMISSION"
        )
    default_plan = plan.get("default_plan")
    if not isinstance(default_plan, Mapping):
        raise ProductionDefaultIntegrationError("DEFAULT_PLAN_MISSING")
    from .default_compiler_frontdoor import admit_default_execution

    admission = admit_default_execution(
        default_plan,
        traversal_receipt,
        verified_output_digest=verified_output_digest,
        expected_provider_library_sha256=expected_provider_library_sha256,
        repository_root=repository_root,
    )
    if admission.get("status") != "PASS":
        raise ProductionDefaultIntegrationError(
            "BEHAVIORAL_OPTIX_ADMISSION_FAILED",
            str(admission.get("error_code", "UNKNOWN")),
        )
    body: dict[str, object] = {
        "schema": PRODUCTION_DEFAULT_ADMISSION_SCHEMA,
        "policy_version": PRODUCTION_DEFAULT_POLICY_VERSION,
        "status": "ADMITTED",
        "production_plan_sha256": plan["production_plan_sha256"],
        "binding_sha256": binding_sha,
        "default_execution_admission": admission,
        "default_execution_admission_sha256": admission["admission_sha256"],
        "traversal_receipt": dict(traversal_receipt),
        "traversal_receipt_sha256": traversal_receipt["receipt_sha256"],
        "behavioral_optix_proven": True,
        "partner_stage_claimed_as_rt": False,
        "whole_endpoint_rt_only_proven": False,
        "silicon_rt_core_utilization_proven": False,
        "performance_claimed": False,
    }
    body["production_admission_sha256"] = _digest(body)
    return body


__all__ = [
    "PRODUCTION_DEFAULT_BINDING_SCHEMA",
    "PRODUCTION_DEFAULT_ADMISSION_SCHEMA",
    "PRODUCTION_DEFAULT_PLAN_SCHEMA",
    "PRODUCTION_DEFAULT_POLICY_VERSION",
    "ProductionDefaultIntegrationError",
    "bind_default_plan_to_lowering",
    "admit_production_default_execution",
    "compile_production_default_plan",
    "make_production_action_descriptor",
    "make_production_target_descriptor",
    "probe_device_memory_limit_bytes",
]
