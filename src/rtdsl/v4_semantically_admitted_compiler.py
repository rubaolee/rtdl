"""Semantic-admission facade for three V4 OptiX compiler families.

The facade never accepts a caller-supplied live binding or candidate set.
Those facts are rederived from the actual compiler authority, canonical
plan/contract, ABI, and target immediately before the existing low-level
compiler is called.  The low-level compilers remain unchanged.

Code claiming this admission property must enter through this facade's
admit/compile/run chain.  Pre-existing low-level modules remain compatibility
internals and do not acquire semantic-admission status merely by being called.

This module does not make a physical guarantee true.  It binds an independently
issued semantic/physical admission to the exact live compiler inputs and keeps
a process-local executable-to-admission registry for an admitted runtime path.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from weakref import WeakKeyDictionary

from .v4_bounded_relation import (
    BOUNDED_RELATION_TEMPLATE,
    CompiledBoundedRelationContract,
    VerifiedBoundedRelationAuthority,
)
from .v4_callback_abi import CompiledCallbackAbi
from .v4_semantic_physical_admission import (
    CanonicalCandidateV1,
    LiveFamilyBindingV1,
    NO_ORIENTATION_CONTRACT_SHA256,
    VerifiedPhysicalGuaranteeAuthority,
    VerifiedSemanticRequirementAuthority,
    VerifiedSemanticPhysicalAdmissionAuthority,
    canonical_candidates_from_registry,
    reverify_registered_physical_guarantee_authority,
    reverify_semantic_physical_admission,
    reverify_semantic_requirement_authority,
    verify_semantic_physical_admission,
)
from .v4_triangle_reduction import (
    TRIANGLE_REDUCTION_TEMPLATE,
    CompiledTriangleReductionContract,
    VerifiedTriangleReductionAuthority,
)
from .v4_typed_physical_schema import (
    CanonicalPhysicalPlan,
    GeometryFamily,
    ReferenceTemplateId,
    VerifiedPhysicalSchemaAuthority,
)


ADMITTED_EXECUTABLE_BINDING_SCHEMA = (
    "rtdl.v4.semantically_admitted_executable_binding.v1")
_SHA256 = re.compile(r"[0-9a-f]{64}")


class SemanticallyAdmittedCompilerError(RuntimeError):
    """Stable fail-closed diagnostic emitted before low-level compilation."""

    def __init__(self, code: str, path: str, message: str):
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class _FamilyInputs:
    family: str
    live_binding: LiveFamilyBindingV1
    candidates: tuple[CanonicalCandidateV1, ...]


@dataclass(frozen=True)
class _ExecutableAdmissionRecord:
    schema: str
    family: str
    admission_sha256: str
    executable_sha256: str
    live_binding: LiveFamilyBindingV1
    candidates: tuple[CanonicalCandidateV1, ...]


_ADMITTED_EXECUTABLES: WeakKeyDictionary[
    object, _ExecutableAdmissionRecord
] = WeakKeyDictionary()


SemanticDeclaration = VerifiedSemanticRequirementAuthority
PhysicalDeclaration = VerifiedPhysicalGuaranteeAuthority


def admit_builtin_triangle_compilation(
    semantic_requirement: SemanticDeclaration,
    physical_guarantee: PhysicalDeclaration,
    *,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> VerifiedSemanticPhysicalAdmissionAuthority:
    """Admit one exact built-in-triangle compiler tuple; never compile it."""

    semantic, physical = _declarations(semantic_requirement, physical_guarantee)
    family = _builtin_triangle_inputs(physical, authority, plan, abi)
    return verify_semantic_physical_admission(
        semantic, physical,
        live_binding=family.live_binding,
    )


def admit_triangle_reduction_compilation(
    semantic_requirement: SemanticDeclaration,
    physical_guarantee: PhysicalDeclaration,
    *,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
) -> VerifiedSemanticPhysicalAdmissionAuthority:
    """Admit one exact triangle-reduction compiler tuple; never compile it."""

    semantic, physical = _declarations(semantic_requirement, physical_guarantee)
    family = _triangle_reduction_inputs(physical, authority, contract, abi)
    return verify_semantic_physical_admission(
        semantic, physical,
        live_binding=family.live_binding,
    )


def admit_bounded_relation_compilation(
    semantic_requirement: SemanticDeclaration,
    physical_guarantee: PhysicalDeclaration,
    *,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
) -> VerifiedSemanticPhysicalAdmissionAuthority:
    """Admit one exact bounded-relation compiler tuple; never compile it."""

    semantic, physical = _declarations(semantic_requirement, physical_guarantee)
    family = _bounded_relation_inputs(physical, authority, contract, abi)
    return verify_semantic_physical_admission(
        semantic, physical,
        live_binding=family.live_binding,
    )


def compile_semantically_admitted_builtin_triangle_executable(
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
    **compiler_options,
):
    """Reverify admission, then call the existing triangle compiler once."""

    family = _builtin_triangle_inputs(
        _physical_from_admission(admission), authority, plan, abi)
    _reverify(admission, family)
    result = _compile_verified_triangle_executable(
        authority, plan, abi, **compiler_options)
    _register_result(result, admission, family)
    return result


def compile_semantically_admitted_triangle_reduction_executable(
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    **compiler_options,
):
    """Reverify admission, then call the existing reduction compiler once."""

    family = _triangle_reduction_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _reverify(admission, family)
    result = _compile_verified_triangle_reduction_executable(
        authority, contract, abi, **compiler_options)
    _register_result(result, admission, family)
    return result


def compile_semantically_admitted_bounded_relation_executable(
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    **compiler_options,
):
    """Reverify admission, then call the existing relation compiler once."""

    family = _bounded_relation_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _reverify(admission, family)
    result = _compile_verified_bounded_relation_executable(
        authority, contract, abi, **compiler_options)
    _register_result(result, admission, family)
    return result


def require_semantically_admitted_builtin_triangle_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> object:
    family = _builtin_triangle_inputs(
        _physical_from_admission(admission), authority, plan, abi)
    return _require_semantically_admitted_executable(
        executable, admission, family)


def require_semantically_admitted_triangle_reduction_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
) -> object:
    family = _triangle_reduction_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    return _require_semantically_admitted_executable(
        executable, admission, family)


def require_semantically_admitted_bounded_relation_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
) -> object:
    family = _bounded_relation_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    return _require_semantically_admitted_executable(
        executable, admission, family)


def consume_semantically_admitted_builtin_triangle_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
) -> str:
    """Atomically reverify semantic admission and consume one executable."""

    family = _builtin_triangle_inputs(
        _physical_from_admission(admission), authority, plan, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _consume_verified_triangle_executable(
            executable, authority, plan, abi)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def consume_semantically_admitted_triangle_reduction_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    **consume_options,
) -> str:
    family = _triangle_reduction_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _consume_verified_triangle_reduction_executable(
            executable, authority, contract, abi, **consume_options)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def consume_semantically_admitted_bounded_relation_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    **consume_options,
) -> str:
    family = _bounded_relation_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _consume_verified_bounded_relation_executable(
            executable, authority, contract, abi, **consume_options)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def run_semantically_admitted_builtin_triangle_callback(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedPhysicalSchemaAuthority,
    plan: CanonicalPhysicalPlan,
    abi: CompiledCallbackAbi,
    **runtime_options,
):
    """Reverify the compiler tuple and invoke the real runtime atomically.

    Admission does not certify arbitrary runtime arrays.  Concrete-instance
    validity remains the runtime validator/oracle's separate responsibility.
    """

    family = _builtin_triangle_inputs(
        _physical_from_admission(admission), authority, plan, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _run_builtin_triangle_callback(
            authority, plan, abi, executable, **runtime_options)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def run_semantically_admitted_triangle_reduction_callback(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedTriangleReductionAuthority,
    contract: CompiledTriangleReductionContract,
    abi: CompiledCallbackAbi,
    **runtime_options,
):
    """Reverify the compiler tuple and invoke the real runtime atomically.

    Admission does not certify arbitrary runtime arrays.  Concrete-instance
    validity remains the runtime validator/oracle's separate responsibility.
    """

    family = _triangle_reduction_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _run_builtin_triangle_reduction_callback(
            authority, contract, abi, executable, **runtime_options)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def run_semantically_admitted_bounded_relation_callback(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    authority: VerifiedBoundedRelationAuthority,
    contract: CompiledBoundedRelationContract,
    abi: CompiledCallbackAbi,
    **runtime_options,
):
    """Reverify the compiler tuple and invoke the real runtime atomically.

    Admission does not certify arbitrary runtime arrays.  Concrete-instance
    validity remains the runtime validator/oracle's separate responsibility.
    """

    family = _bounded_relation_inputs(
        _physical_from_admission(admission), authority, contract, abi)
    _require_semantically_admitted_executable(executable, admission, family)
    try:
        return _run_bounded_relation_callback(
            authority, contract, abi, executable, **runtime_options)
    finally:
        _ADMITTED_EXECUTABLES.pop(executable, None)


def _require_semantically_admitted_executable(
    executable: object,
    admission: VerifiedSemanticPhysicalAdmissionAuthority,
    family: _FamilyInputs,
) -> object:

    try:
        record = _ADMITTED_EXECUTABLES.get(executable)
    except TypeError as exc:
        raise SemanticallyAdmittedCompilerError(
            "SA004_EXECUTABLE_NOT_ADMITTED", "executable",
            "expected the original weak-referenceable executable") from exc
    if record is None:
        raise SemanticallyAdmittedCompilerError(
            "SA004_EXECUTABLE_NOT_ADMITTED", "executable",
            "no process-local semantic admission record")
    if record.family != family.family \
            or record.live_binding != family.live_binding \
            or record.candidates != family.candidates:
        raise SemanticallyAdmittedCompilerError(
            "SA007_RUNTIME_FAMILY_DRIFT", "family",
            "current compiler family differs from the compile-time record")
    if getattr(executable, "executable_sha256", None) != record.executable_sha256:
        raise SemanticallyAdmittedCompilerError(
            "SA005_EXECUTABLE_IDENTITY_DRIFT", "executable.executable_sha256",
            "executable identity changed after compilation")
    if not isinstance(admission, VerifiedSemanticPhysicalAdmissionAuthority) \
            or admission.admission_sha256 != record.admission_sha256:
        raise SemanticallyAdmittedCompilerError(
            "SA006_ADMISSION_BINDING_MISMATCH", "admission",
            "executable was admitted under another authority")
    reverify_semantic_physical_admission(
        admission,
        admission.semantic_authority,
        admission.physical_authority,
        live_binding=family.live_binding,
    )
    return executable


def _declarations(semantic, physical):
    if not isinstance(semantic, VerifiedSemanticRequirementAuthority) \
            or not isinstance(physical, VerifiedPhysicalGuaranteeAuthority):
        _fail(
            "SA001_DECLARATION_REQUIRED", "declarations",
            "live semantic and registered physical authorities are required",
        )
    reverify_semantic_requirement_authority(semantic)
    reverify_registered_physical_guarantee_authority(physical)
    return semantic, physical


def _physical_from_admission(admission):
    if not isinstance(admission, VerifiedSemanticPhysicalAdmissionAuthority):
        _fail("SA002_ADMISSION_REQUIRED", "admission", "live admission authority")
    return admission.physical_authority


def _builtin_triangle_inputs(
    physical_authority, authority, plan, abi,
) -> _FamilyInputs:
    physical_authority = reverify_registered_physical_guarantee_authority(
        physical_authority)
    physical = physical_authority.guarantee
    if not isinstance(authority, VerifiedPhysicalSchemaAuthority) \
            or not isinstance(plan, CanonicalPhysicalPlan) \
            or not isinstance(abi, CompiledCallbackAbi):
        _fail("SA010_FAMILY_INPUT_TYPE", "builtin_triangle", "authority/plan/ABI")
    callback = authority.callback
    schema = authority.schema
    target = authority.target
    if schema.geometry_family is not GeometryFamily.BUILTIN_TRIANGLE \
            or authority.triangle_orientation_authority is None:
        _fail("SA011_FAMILY_IDENTITY", "builtin_triangle.authority", "built-in triangle")
    orientation_sha256 = getattr(
        authority.triangle_orientation_authority, "authority_sha256", None)
    if not _is_sha(orientation_sha256):
        _fail(
            "SA013_DIGEST_INVALID", "builtin_triangle.orientation_authority",
            repr(orientation_sha256))
    _match(
        "physical.orientation_contract_sha256",
        physical.orientation_contract_sha256, orientation_sha256)
    if plan.template_id is not ReferenceTemplateId.BUILTIN_TRIANGLE_V1 \
            or plan.executable:
        _fail("SA012_CANONICAL_ARTIFACT", "builtin_triangle.plan", "sole inert template")
    _match("plan.callback_ir_sha256", plan.callback_ir_sha256, callback.ir_sha256)
    _match("plan.effect_digest", plan.effect_digest, callback.effect_digest)
    _match("plan.schema_sha256", plan.schema_sha256, schema.schema_sha256)
    _match("plan.target_sha256", plan.target_sha256, target.target_sha256)
    _match("plan.authority_nonce", plan.authority_nonce, authority.authority_nonce)
    _abi_matches(abi, callback)
    return _family_inputs(
        physical=physical,
        family="builtin_triangle",
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE.value,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        schema_sha256=schema.schema_sha256,
        target=target,
        artifact_sha256=plan.plan_sha256,
        template_id=plan.template_id.value,
        authority_nonce=authority.authority_nonce,
        abi_sha256=abi.abi_sha256,
        registry=physical_authority.registry,
    )


def _triangle_reduction_inputs(
    physical_authority, authority, contract, abi,
) -> _FamilyInputs:
    physical_authority = reverify_registered_physical_guarantee_authority(
        physical_authority)
    physical = physical_authority.guarantee
    if not isinstance(authority, VerifiedTriangleReductionAuthority) \
            or not isinstance(contract, CompiledTriangleReductionContract) \
            or not isinstance(abi, CompiledCallbackAbi):
        _fail("SA010_FAMILY_INPUT_TYPE", "triangle_reduction", "authority/contract/ABI")
    callback = authority.callback
    schema = authority.schema
    target = authority.target
    _match(
        "physical.orientation_contract_sha256",
        physical.orientation_contract_sha256,
        NO_ORIENTATION_CONTRACT_SHA256)
    if contract.template_id != TRIANGLE_REDUCTION_TEMPLATE or contract.executable:
        _fail("SA012_CANONICAL_ARTIFACT", "triangle_reduction.contract", "sole inert template")
    _match("contract.callback_ir_sha256", contract.callback_ir_sha256, callback.ir_sha256)
    _match("contract.effect_digest", contract.effect_digest, callback.effect_digest)
    _match("contract.schema_sha256", contract.schema_sha256, schema.schema_sha256)
    _match("contract.target_sha256", contract.target_sha256, target.target_sha256)
    _match("contract.authority_nonce", contract.authority_nonce, authority.authority_nonce)
    _match("contract.abi_sha256", contract.abi_sha256, abi.abi_sha256)
    _abi_matches(abi, callback)
    return _family_inputs(
        physical=physical,
        family="triangle_reduction",
        geometry_family=GeometryFamily.BUILTIN_TRIANGLE.value,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        schema_sha256=schema.schema_sha256,
        target=target,
        artifact_sha256=contract.contract_sha256,
        template_id=contract.template_id,
        authority_nonce=authority.authority_nonce,
        abi_sha256=abi.abi_sha256,
        registry=physical_authority.registry,
    )


def _bounded_relation_inputs(
    physical_authority, authority, contract, abi,
) -> _FamilyInputs:
    physical_authority = reverify_registered_physical_guarantee_authority(
        physical_authority)
    physical = physical_authority.guarantee
    if not isinstance(authority, VerifiedBoundedRelationAuthority) \
            or not isinstance(contract, CompiledBoundedRelationContract) \
            or not isinstance(abi, CompiledCallbackAbi):
        _fail("SA010_FAMILY_INPUT_TYPE", "bounded_relation", "authority/contract/ABI")
    callback = authority.physical.callback
    physical_schema = authority.physical.schema
    relation_schema = authority.schema
    target = authority.physical.target
    _match(
        "physical.orientation_contract_sha256",
        physical.orientation_contract_sha256,
        NO_ORIENTATION_CONTRACT_SHA256)
    if physical_schema.geometry_family is not GeometryFamily.CUSTOM_AABB:
        _fail("SA011_FAMILY_IDENTITY", "bounded_relation.authority", "custom AABB")
    if contract.template_id != BOUNDED_RELATION_TEMPLATE or contract.executable:
        _fail("SA012_CANONICAL_ARTIFACT", "bounded_relation.contract", "sole inert template")
    _match("contract.callback_ir_sha256", contract.callback_ir_sha256, callback.ir_sha256)
    _match("contract.effect_digest", contract.effect_digest, callback.effect_digest)
    _match(
        "contract.physical_schema_sha256", contract.physical_schema_sha256,
        physical_schema.schema_sha256)
    _match(
        "contract.relation_schema_sha256", contract.relation_schema_sha256,
        relation_schema.schema_sha256)
    _match("contract.target_sha256", contract.target_sha256, target.target_sha256)
    _match("contract.authority_nonce", contract.authority_nonce, authority.authority_nonce)
    _match("contract.abi_sha256", contract.abi_sha256, abi.abi_sha256)
    _abi_matches(abi, callback)
    return _family_inputs(
        physical=physical,
        family="bounded_relation",
        geometry_family=GeometryFamily.CUSTOM_AABB.value,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        schema_sha256=relation_schema.schema_sha256,
        target=target,
        artifact_sha256=contract.contract_sha256,
        template_id=contract.template_id,
        authority_nonce=authority.authority_nonce,
        abi_sha256=abi.abi_sha256,
        registry=physical_authority.registry,
    )


def _family_inputs(
    *, physical, family, geometry_family, callback_ir_sha256, effect_digest,
    schema_sha256, target, artifact_sha256, template_id, authority_nonce,
    abi_sha256, registry,
) -> _FamilyInputs:
    for path, value in (
        ("callback_ir_sha256", callback_ir_sha256),
        ("effect_digest", effect_digest),
        ("schema_sha256", schema_sha256),
        ("target_sha256", target.target_sha256),
        ("artifact_sha256", artifact_sha256),
        ("abi_sha256", abi_sha256),
    ):
        if not _is_sha(value):
            _fail("SA013_DIGEST_INVALID", path, repr(value))
    if target.provider != "optix":
        _fail("SA014_TARGET_PROVIDER", "target.provider", repr(target.provider))
    capabilities = _target_capabilities(target)
    family_authority_sha256 = _digest({
        "schema": "rtdl.v4.live_compiler_family_authority.v1",
        "family": family,
        "callback_ir_sha256": callback_ir_sha256,
        "effect_digest": effect_digest,
        "schema_sha256": schema_sha256,
        "target_sha256": target.target_sha256,
        "canonical_artifact_sha256": artifact_sha256,
        "canonical_template_id": template_id,
        "abi_sha256": abi_sha256,
        "authority_nonce": authority_nonce,
    })
    binding = LiveFamilyBindingV1(
        callback_ir_sha256=callback_ir_sha256,
        effect_digest=effect_digest,
        family_schema_sha256=schema_sha256,
        target_sha256=target.target_sha256,
        target_provider=target.provider,
        target_capabilities=capabilities,
        canonical_artifact_sha256=artifact_sha256,
        canonical_template_id=template_id,
        family_authority_sha256=family_authority_sha256,
        family_authority_nonce=authority_nonce,
    )
    candidates = canonical_candidates_from_registry(
        registry, live_binding=binding, geometry_family=geometry_family)
    return _FamilyInputs(family, binding, candidates)


def _target_capabilities(target) -> tuple[str, ...]:
    values = {"bound_program_bundle", "optix"}
    if target.supports_builtin_triangle:
        values.add("optix_builtin_triangle")
    if target.supports_custom_aabb:
        values.add("optix_custom_aabb")
    return tuple(sorted(values))


def _abi_matches(abi, callback) -> None:
    _match("abi.callback_ir_sha256", abi.callback_ir_sha256, callback.ir_sha256)
    _match(
        "abi.callback_effect_digest", abi.callback_effect_digest,
        callback.effect_digest)


def _match(path, actual, expected) -> None:
    if actual != expected:
        _fail("SA015_LIVE_IDENTITY_DRIFT", path, f"{actual!r} != {expected!r}")


def _reverify(admission, family) -> None:
    reverify_semantic_physical_admission(
        admission,
        admission.semantic_authority,
        admission.physical_authority,
        live_binding=family.live_binding,
    )


def _register_result(result, admission, family) -> None:
    if not isinstance(result, tuple) or len(result) != 2:
        _fail("SA020_LOW_LEVEL_RESULT", "compiler", "expected (executable, log)")
    executable = result[0]
    executable_sha256 = getattr(executable, "executable_sha256", None)
    if not _is_sha(executable_sha256):
        _fail(
            "SA020_LOW_LEVEL_RESULT", "executable.executable_sha256",
            repr(executable_sha256))
    record = _ExecutableAdmissionRecord(
        schema=ADMITTED_EXECUTABLE_BINDING_SCHEMA,
        family=family.family,
        admission_sha256=admission.admission_sha256,
        executable_sha256=executable_sha256,
        live_binding=family.live_binding,
        candidates=family.candidates,
    )
    try:
        if executable in _ADMITTED_EXECUTABLES:
            _fail("SA021_EXECUTABLE_ALREADY_REGISTERED", "executable", family.family)
        _ADMITTED_EXECUTABLES[executable] = record
    except TypeError as exc:
        raise SemanticallyAdmittedCompilerError(
            "SA020_LOW_LEVEL_RESULT", "executable",
            "executable must support identity weak references") from exc


def _compile_verified_triangle_executable(*args, **kwargs):
    from .v4_triangle_optix_compiler import compile_verified_triangle_executable
    return compile_verified_triangle_executable(*args, **kwargs)


def _compile_verified_triangle_reduction_executable(*args, **kwargs):
    from .v4_triangle_reduction_optix_compiler import (
        compile_verified_triangle_reduction_executable,
    )
    return compile_verified_triangle_reduction_executable(*args, **kwargs)


def _compile_verified_bounded_relation_executable(*args, **kwargs):
    from .v4_bounded_relation_optix_compiler import (
        compile_verified_bounded_relation_executable,
    )
    return compile_verified_bounded_relation_executable(*args, **kwargs)


def _consume_verified_triangle_executable(*args, **kwargs):
    from .v4_triangle_optix_compiler import consume_verified_triangle_executable
    return consume_verified_triangle_executable(*args, **kwargs)


def _consume_verified_triangle_reduction_executable(*args, **kwargs):
    from .v4_triangle_reduction_optix_compiler import (
        consume_verified_triangle_reduction_executable,
    )
    return consume_verified_triangle_reduction_executable(*args, **kwargs)


def _consume_verified_bounded_relation_executable(*args, **kwargs):
    from .v4_bounded_relation_optix_compiler import (
        consume_verified_bounded_relation_executable,
    )
    return consume_verified_bounded_relation_executable(*args, **kwargs)


def _run_builtin_triangle_callback(*args, **kwargs):
    from .v4_triangle_optix_runtime import run_builtin_triangle_callback
    return run_builtin_triangle_callback(*args, **kwargs)


def _run_builtin_triangle_reduction_callback(*args, **kwargs):
    from .v4_triangle_reduction_optix_runtime import (
        run_builtin_triangle_reduction_callback,
    )
    return run_builtin_triangle_reduction_callback(*args, **kwargs)


def _run_bounded_relation_callback(*args, **kwargs):
    from .v4_bounded_relation_optix_runtime import run_bounded_relation_callback
    return run_bounded_relation_callback(*args, **kwargs)


def _fail(code, path, message):
    raise SemanticallyAdmittedCompilerError(code, path, message)


def _is_sha(value) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


__all__ = [
    "SemanticallyAdmittedCompilerError",
    "admit_bounded_relation_compilation",
    "admit_builtin_triangle_compilation",
    "admit_triangle_reduction_compilation",
    "compile_semantically_admitted_bounded_relation_executable",
    "compile_semantically_admitted_builtin_triangle_executable",
    "compile_semantically_admitted_triangle_reduction_executable",
    "consume_semantically_admitted_bounded_relation_executable",
    "consume_semantically_admitted_builtin_triangle_executable",
    "consume_semantically_admitted_triangle_reduction_executable",
    "require_semantically_admitted_bounded_relation_executable",
    "require_semantically_admitted_builtin_triangle_executable",
    "require_semantically_admitted_triangle_reduction_executable",
    "run_semantically_admitted_bounded_relation_callback",
    "run_semantically_admitted_builtin_triangle_callback",
    "run_semantically_admitted_triangle_reduction_callback",
]
