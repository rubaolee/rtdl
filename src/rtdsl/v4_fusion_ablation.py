"""Closed same-semantic-IR fusion-ablation plan for checked U64 reduction.

The plan is app-neutral: it admits one registered reducer mechanism and never
examines an app, paper, dataset, batch, result, or timing value.  Both variants
bind the exact Goal5789 semantic/physical/reference/executable-family freeze.
The only admitted difference is the downstream reducer lowering, its
target/dependency-bound operation-recipe identity, and the corresponding
ordered operation-evidence sequence.  The recipe identity does not claim
captured PTX/cubin bytes for opaque CuPy operations.

This module defines a functional experiment contract.  It does not select a
variant, execute a device operation, measure time, or authorize a performance
or compiler-fusion claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Mapping

from .v4_checked_u64_device_reduction import (
    checked_u64_downstream_operation_identity,
)
from .v4_operation_evidence import (
    OperationKind,
    OperationRequirement,
    OperationSequenceContract,
    verify_operation_sequence_contract,
)


FUSION_ABLATION_PLAN_SCHEMA = "rtdl.v4.fusion_ablation_plan.v2"
SHARED_CONTRACT_FREEZE_SCHEMA = "rtdl.goal5789_goal5790.shared_contract_freeze.v1"
TARGET_MATERIALIZATION_AUTHORITY_SCHEMA = (
    "rtdl.v4.target_materialization_authority.v2"
)
CHECKED_U64_PRODUCT_SUM_MECHANISM = "checked_u64_product_sum_downstream_lowering.v1"

# The exact serialized Goal5789 freeze and its canonical self-digest.  Keeping
# both prevents whitespace/key-order substitutions from being relabelled as the
# reviewed freeze while still independently validating the embedded digest.
SHARED_CONTRACT_FREEZE_FILE_SHA256 = (
    "b62217a5374732cece8c7eaef93c0f21eb580666559e912eb8dd1bb2aaa7628b"
)
SHARED_CONTRACT_FREEZE_SHA256 = (
    "8ada80c377241aa9a4fde29f26fdc9380257f93cc2264a3e60f2a96a437fced5"
)
SEMANTIC_REQUEST_SHA256 = (
    "492c59b92f3ab8138d5bff6b481bff16e51db5028868732d266ef2948810f02e"
)
PHYSICAL_ENCODING_SHA256 = (
    "7f1d101e8f588571c58958152ed7f20ef43387a50d9fd00c5c7925d7405dc656"
)
ADMITTED_REFERENCE_PLAN_SHA256 = (
    "8dc1c000146e6df31e77ad86f21ae799bb543aeda68de4054932222523409d8e"
)
EXECUTABLE_FAMILY_PLAN_SHA256 = (
    "ddb4909e48ca37b5065e1db86b34ff9610bc9d9a915a76efb651bb692028faa3"
)
TRANSFORMATION_VARIANT_CONTRACT_SHA256 = (
    "425bb6cffe4edb121f8e1bf3e9a730405439e2af32507b3c8b0c8d6a6b613ff3"
)

_REFERENCE_NATIVE_PROVENANCE_SHA256 = (
    "efcc147b3e3dbf06731f424b3883b0a785cb80e227334d27b672dd01ac56feab"
)
_REFERENCE_SOURCE_TREE_SHA256 = (
    "6f83542265b01dd3c9acaf797117dc02e31298e3c0c591d0c909c50b457e25ef"
)
_EXPECTED_PROGRAM_BUNDLE = "v4_builtin_triangle_checked_reduction_composed"
_EXPECTED_PHYSICAL_SCHEMA_SHA256 = (
    "97e3e85f8ab60e612e922a156fe2ecd8349b94e51a34d6984d8ce75133070e73"
)
_EXPECTED_FAMILY_ID = (
    "v4_triangle_per_ray_optix_producer_plus_checked_u64_continuation.v1"
)
_EXPECTED_TARGET_MATERIALIZATION_POLICY = {
    "actual_target_native_must_be_receipt_bound": True,
    "actual_target_source_tree_must_be_receipt_bound": True,
    "cross_target_native_byte_reproducibility_assumed": False,
    "reference_native_is_execution_authority_for_other_targets": False,
    "same_target_fusion_pair_must_share_exact_native": True,
    "same_target_fusion_pair_must_share_exact_program_bundle": True,
    "same_target_fusion_pair_must_share_exact_source_tree": True,
}
_EXPECTED_ALLOWLIST = (
    "downstream_checked_u64_reducer_operation_identity_and_event_sequence"
)

_ID = re.compile(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_NONCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{15,255}")
_U64_MAX = (1 << 64) - 1


class FusionAblationError(ValueError):
    """Stable fail-closed diagnostic for the ablation contract."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"V4 fusion ablation rejected: {code}@{path}: {message}")


def _fail(code: str, path: str, message: str) -> None:
    raise FusionAblationError(code, path, message)


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _fail("canonical_json", "value", str(exc))


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: object, path: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail("sha256", path, repr(value))
    return value


def _identifier(value: object, path: str) -> str:
    if not isinstance(value, str) or _ID.fullmatch(value) is None:
        _fail("identifier", path, repr(value))
    return value


def _u64(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= _U64_MAX:
        _fail("u64", path, repr(value))
    return value


class FusionVariant(str, Enum):
    FUSION_ON = "fusion_on"
    FUSION_OFF = "fusion_off"


@dataclass(frozen=True)
class VerifiedDownstreamOperationRecipe:
    """Deeply immutable structured recipe, not opaque binary attestation."""

    variant: FusionVariant
    target_identity_sha256: str
    cupy_version: str
    kind: str
    entry: str | None
    source_sha256: str | None
    options: tuple[str, ...]
    operations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        implementation: dict[str, object] = {
            "kind": self.kind,
            "opaque_partner_kernel_binary_claimed": False,
        }
        if self.variant is FusionVariant.FUSION_ON:
            implementation.update({
                "entry": self.entry,
                "source_sha256": self.source_sha256,
                "options": list(self.options),
            })
        else:
            implementation["operations"] = list(self.operations)
        return {
            "schema": "rtdl.v4.checked_u64_downstream_operation_identity.v1",
            "variant": self.variant.value,
            "target_identity_sha256": self.target_identity_sha256,
            "cupy_version": self.cupy_version,
            "implementation": implementation,
        }


def _verified_downstream_recipe(
    value: object,
    *,
    variant: FusionVariant,
    target_identity_sha256: str,
    cupy_version: str,
    path: str,
) -> VerifiedDownstreamOperationRecipe:
    if not isinstance(value, Mapping):
        _fail("downstream_recipe_type", path, type(value).__name__)
    expected = checked_u64_downstream_operation_identity(
        variant.value,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
    )
    if dict(value) != expected:
        _fail("downstream_recipe_identity", path, "recipe payload mismatch")
    implementation = expected["implementation"]
    assert isinstance(implementation, dict)
    return VerifiedDownstreamOperationRecipe(
        variant=variant,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
        kind=str(implementation["kind"]),
        entry=(
            str(implementation["entry"])
            if "entry" in implementation else None
        ),
        source_sha256=(
            str(implementation["source_sha256"])
            if "source_sha256" in implementation else None
        ),
        options=tuple(str(item) for item in implementation.get("options", ())),
        operations=tuple(
            str(item) for item in implementation.get("operations", ())
        ),
    )


@dataclass(frozen=True)
class VerifiedSharedContractFreeze:
    file_sha256: str
    freeze_sha256: str
    semantic_request_sha256: str
    physical_encoding_sha256: str
    admitted_reference_plan_sha256: str
    executable_family_plan_sha256: str
    transformation_variant_contract_sha256: str
    physical_schema_sha256: str
    executable_family_id: str
    reference_native_provenance_sha256: str
    reference_source_tree_sha256: str
    target_materialization_policy_sha256: str
    program_bundle: str

    def to_dict(self) -> dict[str, object]:
        return {
            "file_sha256": self.file_sha256,
            "freeze_sha256": self.freeze_sha256,
            "semantic_request_sha256": self.semantic_request_sha256,
            "physical_encoding_sha256": self.physical_encoding_sha256,
            "admitted_reference_plan_sha256": self.admitted_reference_plan_sha256,
            "executable_family_plan_sha256": self.executable_family_plan_sha256,
            "transformation_variant_contract_sha256": (
                self.transformation_variant_contract_sha256
            ),
            "physical_schema_sha256": self.physical_schema_sha256,
            "executable_family_id": self.executable_family_id,
            "reference_native_provenance_sha256": (
                self.reference_native_provenance_sha256
            ),
            "reference_source_tree_sha256": self.reference_source_tree_sha256,
            "target_materialization_policy_sha256": (
                self.target_materialization_policy_sha256
            ),
            "program_bundle": self.program_bundle,
        }


@dataclass(frozen=True)
class VerifiedTargetMaterializationAuthority:
    """Exact target-local source/native/program authority from external evidence."""

    shared_contract_freeze_sha256: str
    execution_source_archive_sha256: str
    execution_source_tree_sha256: str
    callback_ir_sha256: str
    callback_authority_nonce: str
    contract_sha256: str
    abi_sha256: str
    provider_identity: str
    program_bundle_identity: str
    composed_program_sha256: str
    cupy_version: str
    fusion_on_downstream_operation_recipe: VerifiedDownstreamOperationRecipe
    fusion_off_downstream_operation_recipe: VerifiedDownstreamOperationRecipe
    fusion_on_downstream_operation_recipe_sha256: str
    fusion_off_downstream_operation_recipe_sha256: str
    native_library_sha256: str
    native_payload_sha256: str
    target_identity_sha256: str
    materializer_source_sha256: str
    source_manifest_sha256: str
    evidence_archive_sha256: str
    materialization_nonce: str
    receipt_sha256: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
            "shared_contract_freeze_sha256": self.shared_contract_freeze_sha256,
            "execution_source_archive_sha256": self.execution_source_archive_sha256,
            "execution_source_tree_sha256": self.execution_source_tree_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_authority_nonce": self.callback_authority_nonce,
            "contract_sha256": self.contract_sha256,
            "abi_sha256": self.abi_sha256,
            "provider_identity": self.provider_identity,
            "program_bundle_identity": self.program_bundle_identity,
            "composed_program_sha256": self.composed_program_sha256,
            "cupy_version": self.cupy_version,
            "fusion_on_downstream_operation_recipe": (
                self.fusion_on_downstream_operation_recipe.to_dict()
            ),
            "fusion_off_downstream_operation_recipe": (
                self.fusion_off_downstream_operation_recipe.to_dict()
            ),
            "fusion_on_downstream_operation_recipe_sha256": (
                self.fusion_on_downstream_operation_recipe_sha256
            ),
            "fusion_off_downstream_operation_recipe_sha256": (
                self.fusion_off_downstream_operation_recipe_sha256
            ),
            "native_library_sha256": self.native_library_sha256,
            "native_payload_sha256": self.native_payload_sha256,
            "target_identity_sha256": self.target_identity_sha256,
            "materializer_source_sha256": self.materializer_source_sha256,
            "source_manifest_sha256": self.source_manifest_sha256,
            "evidence_archive_sha256": self.evidence_archive_sha256,
            "materialization_nonce": self.materialization_nonce,
            "actual_native_rehashed_from_preserved_payload": True,
            "actual_source_tree_recounted_from_preserved_archive": True,
            "cross_target_native_byte_reproducibility_claimed": False,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "receipt_sha256": self.receipt_sha256}


def load_verified_shared_contract_freeze(
    serialized: bytes,
) -> VerifiedSharedContractFreeze:
    """Validate and bind the exact frozen Goal5789 shared contract bytes."""

    if not isinstance(serialized, bytes):
        _fail("freeze_bytes", "serialized", type(serialized).__name__)
    raw_sha = hashlib.sha256(serialized).hexdigest()
    if raw_sha != SHARED_CONTRACT_FREEZE_FILE_SHA256:
        _fail("freeze_file_identity", "serialized", raw_sha)
    try:
        value = json.loads(serialized)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail("freeze_json", "serialized", str(exc))
    if not isinstance(value, dict):
        _fail("freeze_type", "freeze", type(value).__name__)
    if value.get("schema") != SHARED_CONTRACT_FREEZE_SCHEMA \
            or value.get("status") != "FROZEN_FOR_LOCAL_GOAL5790_IMPLEMENTATION_ONLY":
        _fail("freeze_schema_status", "freeze", repr((
            value.get("schema"), value.get("status"))))
    declared = value.get("shared_contract_freeze_sha256")
    unsigned = dict(value)
    unsigned.pop("shared_contract_freeze_sha256", None)
    if declared != SHARED_CONTRACT_FREEZE_SHA256 or _digest(unsigned) != declared:
        _fail("freeze_digest", "freeze.shared_contract_freeze_sha256", repr(declared))

    semantic = value.get("semantic_request")
    physical = value.get("physical_encoding")
    reference = value.get("admitted_reference_plan")
    executable = value.get("executable_family_plan")
    variant = value.get("transformation_variant_contract")
    for name, item in (
        ("semantic_request", semantic),
        ("physical_encoding", physical),
        ("admitted_reference_plan", reference),
        ("executable_family_plan", executable),
        ("transformation_variant_contract", variant),
    ):
        if not isinstance(item, dict):
            _fail("freeze_object", f"freeze.{name}", type(item).__name__)
    if value.get("semantic_request_sha256") != SEMANTIC_REQUEST_SHA256 \
            or _digest(semantic) != SEMANTIC_REQUEST_SHA256:
        _fail("semantic_request_identity", "freeze.semantic_request", "digest mismatch")
    if value.get("physical_encoding_sha256") != PHYSICAL_ENCODING_SHA256 \
            or _digest(physical) != PHYSICAL_ENCODING_SHA256:
        _fail("physical_encoding_identity", "freeze.physical_encoding", "digest mismatch")
    if _digest(reference) != ADMITTED_REFERENCE_PLAN_SHA256:
        _fail("reference_plan_identity", "freeze.admitted_reference_plan", "digest mismatch")
    if _digest(executable) != EXECUTABLE_FAMILY_PLAN_SHA256:
        _fail("executable_family_identity", "freeze.executable_family_plan", "digest mismatch")
    if _digest(variant) != TRANSFORMATION_VARIANT_CONTRACT_SHA256:
        _fail("variant_contract_identity", "freeze.transformation_variant_contract",
              "digest mismatch")

    claims = value.get("claim_boundary")
    if not isinstance(claims, dict) or claims != {
        "compiler_fusion_claim_authorized": False,
        "event_derived_operation_receipts_required": True,
        "pod_or_target_worker_authorized": False,
        "product_performance_claimed": False,
        "same_optix_producer_required": True,
        "same_semantic_ir_required": True,
    }:
        _fail("freeze_claim_boundary", "freeze.claim_boundary", repr(claims))
    if variant.get("mechanism_id") != CHECKED_U64_PRODUCT_SUM_MECHANISM \
            or variant.get("only_allowlisted_difference") != _EXPECTED_ALLOWLIST:
        _fail("freeze_variant_scope", "freeze.transformation_variant_contract",
              "mechanism, allowlist, or exclusion changed")
    if physical.get("schema_sha256") != _EXPECTED_PHYSICAL_SCHEMA_SHA256 \
            or reference.get("schema_sha256") != _EXPECTED_PHYSICAL_SCHEMA_SHA256:
        _fail("freeze_physical_schema", "freeze", "schema identity changed")
    bundles = executable.get("program_bundles")
    policy = executable.get("target_materialization_policy")
    if executable.get("family_id") != _EXPECTED_FAMILY_ID \
            or executable.get("reference_native_provenance_sha256") \
                != _REFERENCE_NATIVE_PROVENANCE_SHA256 \
            or executable.get("reference_source_tree_sha256") \
                != _REFERENCE_SOURCE_TREE_SHA256 \
            or bundles != [_EXPECTED_PROGRAM_BUNDLE] \
            or policy != _EXPECTED_TARGET_MATERIALIZATION_POLICY:
        _fail("freeze_executable_scope", "freeze.executable_family_plan",
              "family/native/program identity changed")
    return VerifiedSharedContractFreeze(
        file_sha256=raw_sha,
        freeze_sha256=declared,
        semantic_request_sha256=SEMANTIC_REQUEST_SHA256,
        physical_encoding_sha256=PHYSICAL_ENCODING_SHA256,
        admitted_reference_plan_sha256=ADMITTED_REFERENCE_PLAN_SHA256,
        executable_family_plan_sha256=EXECUTABLE_FAMILY_PLAN_SHA256,
        transformation_variant_contract_sha256=(
            TRANSFORMATION_VARIANT_CONTRACT_SHA256
        ),
        physical_schema_sha256=_EXPECTED_PHYSICAL_SCHEMA_SHA256,
        executable_family_id=_EXPECTED_FAMILY_ID,
        reference_native_provenance_sha256=(
            _REFERENCE_NATIVE_PROVENANCE_SHA256),
        reference_source_tree_sha256=_REFERENCE_SOURCE_TREE_SHA256,
        target_materialization_policy_sha256=_digest(policy),
        program_bundle=_EXPECTED_PROGRAM_BUNDLE,
    )


def verify_target_materialization_authority(
    value: Mapping[str, object],
) -> VerifiedTargetMaterializationAuthority:
    """Validate a target-local materialization receipt; never mint one here.

    The trusted materializer and evidence archive remain in the TCB.  This
    verifier prevents a plan caller from supplying a naked native digest: it
    must supply the complete, self-digested source/native/target receipt.
    """

    if not isinstance(value, Mapping):
        _fail("target_authority_mapping", "target_authority", type(value).__name__)
    # Snapshot exactly once.  A caller-controlled stateful Mapping must not
    # expose one value to the receipt check and another to the returned
    # authority fields.
    value = dict(value)
    expected = {
        "schema", "shared_contract_freeze_sha256",
        "execution_source_archive_sha256", "execution_source_tree_sha256",
        "callback_ir_sha256", "callback_authority_nonce", "contract_sha256",
        "abi_sha256", "provider_identity", "program_bundle_identity",
        "composed_program_sha256", "cupy_version",
        "fusion_on_downstream_operation_recipe",
        "fusion_off_downstream_operation_recipe",
        "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256", "native_library_sha256",
        "native_payload_sha256", "target_identity_sha256",
        "materializer_source_sha256", "source_manifest_sha256",
        "evidence_archive_sha256", "materialization_nonce",
        "actual_native_rehashed_from_preserved_payload",
        "actual_source_tree_recounted_from_preserved_archive",
        "cross_target_native_byte_reproducibility_claimed", "receipt_sha256",
    }
    if set(value) != expected:
        _fail("target_authority_fields", "target_authority",
              repr(sorted(set(value) ^ expected)))
    if value["schema"] != TARGET_MATERIALIZATION_AUTHORITY_SCHEMA \
            or value["shared_contract_freeze_sha256"] \
                != SHARED_CONTRACT_FREEZE_SHA256:
        _fail("target_authority_schema", "target_authority", repr(value["schema"]))
    if value["provider_identity"] != "optix" \
            or value["program_bundle_identity"] != _EXPECTED_PROGRAM_BUNDLE:
        _fail("target_authority_provider", "target_authority",
              "provider or program bundle changed")
    if value["native_library_sha256"] != value["native_payload_sha256"]:
        _fail("target_native_payload", "target_authority",
              "declared native differs from preserved payload")
    if value["fusion_on_downstream_operation_recipe_sha256"] \
            == value["fusion_off_downstream_operation_recipe_sha256"]:
        _fail("target_downstream_pair", "target_authority",
              "downstream variant identities must be distinct")
    if value["actual_native_rehashed_from_preserved_payload"] is not True \
            or value["actual_source_tree_recounted_from_preserved_archive"] is not True \
            or value["cross_target_native_byte_reproducibility_claimed"] is not False:
        _fail("target_authority_boundary", "target_authority",
              "rehash/recount/cross-target policy changed")
    cupy_version = value["cupy_version"]
    if not isinstance(cupy_version, str) or not cupy_version \
            or len(cupy_version) > 64:
        _fail("target_cupy_version", "target_authority.cupy_version",
              repr(cupy_version))
    callback_authority_nonce = value["callback_authority_nonce"]
    if not isinstance(callback_authority_nonce, str) \
            or _NONCE.fullmatch(callback_authority_nonce) is None:
        _fail("callback_authority_nonce",
              "target_authority.callback_authority_nonce",
              repr(callback_authority_nonce))
    target_identity_sha256 = _sha(
        value["target_identity_sha256"],
        "target_authority.target_identity_sha256",
    )
    on_recipe = _verified_downstream_recipe(
        value["fusion_on_downstream_operation_recipe"],
        variant=FusionVariant.FUSION_ON,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
        path="target_authority.fusion_on_downstream_operation_recipe",
    )
    off_recipe = _verified_downstream_recipe(
        value["fusion_off_downstream_operation_recipe"],
        variant=FusionVariant.FUSION_OFF,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
        path="target_authority.fusion_off_downstream_operation_recipe",
    )
    if value["fusion_on_downstream_operation_recipe_sha256"] \
            != _digest(on_recipe.to_dict()) \
            or value["fusion_off_downstream_operation_recipe_sha256"] \
            != _digest(off_recipe.to_dict()):
        _fail("target_downstream_recipe_digest", "target_authority",
              "structured recipe does not match declared digest")
    for name in (
        "execution_source_archive_sha256", "execution_source_tree_sha256",
        "callback_ir_sha256", "contract_sha256", "abi_sha256",
        "composed_program_sha256",
        "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256",
        "native_library_sha256", "native_payload_sha256",
        "target_identity_sha256", "materializer_source_sha256",
        "source_manifest_sha256", "evidence_archive_sha256", "receipt_sha256",
    ):
        _sha(value[name], "target_authority." + name)
    nonce = value["materialization_nonce"]
    if not isinstance(nonce, str) or _NONCE.fullmatch(nonce) is None:
        _fail("target_authority_nonce", "target_authority.materialization_nonce",
              repr(nonce))
    unsigned = dict(value)
    claimed = unsigned.pop("receipt_sha256")
    # Bind the receipt to the exact immutable recipe objects produced above,
    # not to caller-owned nested Mapping/dict-subclass serialization views.
    # This closes split-view objects whose key lookup appears canonical while
    # ``json.dumps`` observes attacker-controlled ``items()`` content.
    unsigned["fusion_on_downstream_operation_recipe"] = on_recipe.to_dict()
    unsigned["fusion_off_downstream_operation_recipe"] = off_recipe.to_dict()
    if _digest(unsigned) != claimed:
        _fail("target_authority_digest", "target_authority.receipt_sha256",
              str(claimed))
    return VerifiedTargetMaterializationAuthority(
        shared_contract_freeze_sha256=value["shared_contract_freeze_sha256"],
        execution_source_archive_sha256=value["execution_source_archive_sha256"],
        execution_source_tree_sha256=value["execution_source_tree_sha256"],
        callback_ir_sha256=value["callback_ir_sha256"],
        callback_authority_nonce=callback_authority_nonce,
        contract_sha256=value["contract_sha256"],
        abi_sha256=value["abi_sha256"],
        provider_identity=value["provider_identity"],
        program_bundle_identity=value["program_bundle_identity"],
        composed_program_sha256=value["composed_program_sha256"],
        cupy_version=cupy_version,
        fusion_on_downstream_operation_recipe=on_recipe,
        fusion_off_downstream_operation_recipe=off_recipe,
        fusion_on_downstream_operation_recipe_sha256=(
            value["fusion_on_downstream_operation_recipe_sha256"]),
        fusion_off_downstream_operation_recipe_sha256=(
            value["fusion_off_downstream_operation_recipe_sha256"]),
        native_library_sha256=value["native_library_sha256"],
        native_payload_sha256=value["native_payload_sha256"],
        target_identity_sha256=value["target_identity_sha256"],
        materializer_source_sha256=value["materializer_source_sha256"],
        source_manifest_sha256=value["source_manifest_sha256"],
        evidence_archive_sha256=value["evidence_archive_sha256"],
        materialization_nonce=nonce,
        receipt_sha256=claimed,
    )


def _on_requirements() -> tuple[OperationRequirement, ...]:
    return (
        OperationRequirement(
            ordinal=0,
            operation_id="checked_summary.kernel_launch",
            kind=OperationKind.COMPILER_KERNEL_INVOCATION,
            units_per_value=1,
        ),
        OperationRequirement(
            ordinal=1,
            operation_id="checked_summary.summary_copy_sync",
            kind=OperationKind.HOST_COPY_SYNCHRONIZATION,
            fixed_units=4,
            bytes_per_unit=8,
            host_visibility_boundary=True,
        ),
    )


def _off_requirements() -> tuple[OperationRequirement, ...]:
    # This order is the exact legal V4 reference order in the frozen Goal5776
    # runtime: max(weights), sum(weights), materialize values*weights, sum it.
    return (
        OperationRequirement(
            ordinal=0,
            operation_id="maximum_weight.logical_reduce",
            kind=OperationKind.LOGICAL_REDUCTION,
            units_per_value=1,
        ),
        OperationRequirement(
            ordinal=1,
            operation_id="maximum_weight.scalar_copy_sync",
            kind=OperationKind.HOST_COPY_SYNCHRONIZATION,
            fixed_units=1,
            bytes_per_unit=8,
            host_visibility_boundary=True,
        ),
        OperationRequirement(
            ordinal=2,
            operation_id="weight_sum.logical_reduce",
            kind=OperationKind.LOGICAL_REDUCTION,
            units_per_value=1,
        ),
        OperationRequirement(
            ordinal=3,
            operation_id="weight_sum.scalar_copy_sync",
            kind=OperationKind.HOST_COPY_SYNCHRONIZATION,
            fixed_units=1,
            bytes_per_unit=8,
            host_visibility_boundary=True,
        ),
        OperationRequirement(
            ordinal=4,
            operation_id="weighted_product.materialize",
            kind=OperationKind.DEVICE_MATERIALIZATION,
            units_per_value=1,
            bytes_per_unit=8,
        ),
        OperationRequirement(
            ordinal=5,
            operation_id="weighted_product_sum.logical_reduce",
            kind=OperationKind.LOGICAL_REDUCTION,
            units_per_value=1,
        ),
        OperationRequirement(
            ordinal=6,
            operation_id="weighted_product_sum.scalar_copy_sync",
            kind=OperationKind.HOST_COPY_SYNCHRONIZATION,
            fixed_units=1,
            bytes_per_unit=8,
            host_visibility_boundary=True,
        ),
    )


def expected_operation_requirements(
    variant: FusionVariant,
) -> tuple[OperationRequirement, ...]:
    if variant is FusionVariant.FUSION_ON:
        return _on_requirements()
    if variant is FusionVariant.FUSION_OFF:
        return _off_requirements()
    _fail("variant", "variant", repr(variant))


@dataclass(frozen=True)
class FusionAblationPlan:
    mechanism_id: str
    variant: FusionVariant
    shared_contract_file_sha256: str
    shared_contract_freeze_sha256: str
    semantic_request_sha256: str
    physical_encoding_sha256: str
    admitted_reference_plan_sha256: str
    executable_family_plan_sha256: str
    transformation_variant_contract_sha256: str
    physical_schema_sha256: str
    executable_family_id: str
    execution_source_archive_sha256: str
    execution_source_tree_sha256: str
    callback_ir_sha256: str
    callback_authority_nonce: str
    contract_sha256: str
    abi_sha256: str
    native_library_sha256: str
    provider_identity: str
    program_bundle_identity: str
    composed_program_sha256: str
    cupy_version: str
    fusion_on_downstream_operation_recipe: VerifiedDownstreamOperationRecipe
    fusion_off_downstream_operation_recipe: VerifiedDownstreamOperationRecipe
    fusion_on_downstream_operation_recipe_sha256: str
    fusion_off_downstream_operation_recipe_sha256: str
    target_identity_sha256: str
    target_materialization_receipt_sha256: str
    materializer_source_sha256: str
    source_manifest_sha256: str
    materialization_evidence_archive_sha256: str
    materialization_nonce: str
    input_sha256: str
    output_contract_sha256: str
    oracle_sha256: str
    timer_contract_sha256: str
    lifecycle_contract_sha256: str
    value_count: int
    lowering_node: str
    downstream_operation_recipe_sha256: str
    operation_requirements: tuple[OperationRequirement, ...]
    shared_identity_sha256: str
    plan_sha256: str
    schema: str = FUSION_ABLATION_PLAN_SCHEMA
    executable: bool = False

    def common_payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "mechanism_id": self.mechanism_id,
            "shared_contract_file_sha256": self.shared_contract_file_sha256,
            "shared_contract_freeze_sha256": self.shared_contract_freeze_sha256,
            "semantic_request_sha256": self.semantic_request_sha256,
            "physical_encoding_sha256": self.physical_encoding_sha256,
            "admitted_reference_plan_sha256": self.admitted_reference_plan_sha256,
            "executable_family_plan_sha256": self.executable_family_plan_sha256,
            "transformation_variant_contract_sha256": (
                self.transformation_variant_contract_sha256
            ),
            "physical_schema_sha256": self.physical_schema_sha256,
            "executable_family_id": self.executable_family_id,
            "execution_source_archive_sha256": self.execution_source_archive_sha256,
            "execution_source_tree_sha256": self.execution_source_tree_sha256,
            "callback_ir_sha256": self.callback_ir_sha256,
            "callback_authority_nonce": self.callback_authority_nonce,
            "contract_sha256": self.contract_sha256,
            "abi_sha256": self.abi_sha256,
            "native_library_sha256": self.native_library_sha256,
            "provider_identity": self.provider_identity,
            "program_bundle_identity": self.program_bundle_identity,
            "composed_program_sha256": self.composed_program_sha256,
            "cupy_version": self.cupy_version,
            "fusion_on_downstream_operation_recipe": (
                self.fusion_on_downstream_operation_recipe.to_dict()
            ),
            "fusion_off_downstream_operation_recipe": (
                self.fusion_off_downstream_operation_recipe.to_dict()
            ),
            "fusion_on_downstream_operation_recipe_sha256": (
                self.fusion_on_downstream_operation_recipe_sha256
            ),
            "fusion_off_downstream_operation_recipe_sha256": (
                self.fusion_off_downstream_operation_recipe_sha256
            ),
            "target_identity_sha256": self.target_identity_sha256,
            "target_materialization_receipt_sha256": (
                self.target_materialization_receipt_sha256
            ),
            "materializer_source_sha256": self.materializer_source_sha256,
            "source_manifest_sha256": self.source_manifest_sha256,
            "materialization_evidence_archive_sha256": (
                self.materialization_evidence_archive_sha256
            ),
            "materialization_nonce": self.materialization_nonce,
            "input_sha256": self.input_sha256,
            "output_contract_sha256": self.output_contract_sha256,
            "oracle_sha256": self.oracle_sha256,
            "timer_contract_sha256": self.timer_contract_sha256,
            "lifecycle_contract_sha256": self.lifecycle_contract_sha256,
            "value_count": self.value_count,
            "same_semantic_ir_required": True,
            "same_optix_producer_required": True,
            "performance_or_timing_claimed": False,
            "variant_selected_from_app_dataset_result_or_timing": False,
            "executable": self.executable,
        }

    def payload_without_digests(self) -> dict[str, object]:
        return {
            **self.common_payload(),
            "variant": self.variant.value,
            "only_allowlisted_difference": _EXPECTED_ALLOWLIST,
            "lowering_node": self.lowering_node,
            "downstream_operation_recipe_sha256": (
                self.downstream_operation_recipe_sha256),
            "operation_requirements": [
                item.to_dict() for item in self.operation_requirements
            ],
        }

    def to_dict(self) -> dict[str, object]:
        return {
            **self.payload_without_digests(),
            "shared_identity_sha256": self.shared_identity_sha256,
            "plan_sha256": self.plan_sha256,
        }

    def operation_contract(self) -> OperationSequenceContract:
        return verify_operation_sequence_contract(OperationSequenceContract(
            plan_sha256=self.plan_sha256,
            mechanism_id=self.mechanism_id,
            variant=self.variant.value,
            declared_value_count=self.value_count,
            requirements=self.operation_requirements,
        ))


def _plan_lowering_node(variant: FusionVariant) -> str:
    if variant is FusionVariant.FUSION_ON:
        return "checked_summary_kernel_then_one_summary_copy_sync"
    if variant is FusionVariant.FUSION_OFF:
        return "max_sum_materialize_product_sum_then_three_scalar_copy_sync"
    _fail("variant", "variant", repr(variant))


def build_checked_u64_product_sum_ablation_plan(
    freeze: VerifiedSharedContractFreeze,
    *,
    variant: FusionVariant,
    target_materialization: VerifiedTargetMaterializationAuthority,
    input_sha256: str,
    output_contract_sha256: str,
    oracle_sha256: str,
    timer_contract_sha256: str,
    lifecycle_contract_sha256: str,
    value_count: int,
) -> FusionAblationPlan:
    if not isinstance(freeze, VerifiedSharedContractFreeze):
        _fail("freeze_authority", "freeze", type(freeze).__name__)
    if freeze.to_dict() != VerifiedSharedContractFreeze(
        file_sha256=SHARED_CONTRACT_FREEZE_FILE_SHA256,
        freeze_sha256=SHARED_CONTRACT_FREEZE_SHA256,
        semantic_request_sha256=SEMANTIC_REQUEST_SHA256,
        physical_encoding_sha256=PHYSICAL_ENCODING_SHA256,
        admitted_reference_plan_sha256=ADMITTED_REFERENCE_PLAN_SHA256,
        executable_family_plan_sha256=EXECUTABLE_FAMILY_PLAN_SHA256,
        transformation_variant_contract_sha256=(
            TRANSFORMATION_VARIANT_CONTRACT_SHA256),
        physical_schema_sha256=_EXPECTED_PHYSICAL_SCHEMA_SHA256,
        executable_family_id=_EXPECTED_FAMILY_ID,
        reference_native_provenance_sha256=(
            _REFERENCE_NATIVE_PROVENANCE_SHA256),
        reference_source_tree_sha256=_REFERENCE_SOURCE_TREE_SHA256,
        target_materialization_policy_sha256=_digest(
            _EXPECTED_TARGET_MATERIALIZATION_POLICY),
        program_bundle=_EXPECTED_PROGRAM_BUNDLE,
    ).to_dict():
        _fail("freeze_authority", "freeze", "not the exact registered authority")
    if not isinstance(variant, FusionVariant):
        _fail("variant", "variant", repr(variant))
    if not isinstance(target_materialization, VerifiedTargetMaterializationAuthority):
        _fail("target_materialization_authority", "target_materialization",
              type(target_materialization).__name__)
    # Reparse the portable payload so a dataclass constructed directly by a
    # caller cannot bypass receipt and target/source binding checks.
    target_materialization = verify_target_materialization_authority(
        target_materialization.to_dict())
    for name, value in (
        ("input_sha256", input_sha256),
        ("output_contract_sha256", output_contract_sha256),
        ("oracle_sha256", oracle_sha256),
        ("timer_contract_sha256", timer_contract_sha256),
        ("lifecycle_contract_sha256", lifecycle_contract_sha256),
    ):
        _sha(value, name)
    if target_materialization.shared_contract_freeze_sha256 != freeze.freeze_sha256:
        _fail("target_materialization_freeze", "target_materialization",
              "target receipt binds another semantic/physical freeze")
    _u64(value_count, "value_count")
    if value_count == 0:
        _fail("value_count", "value_count", "nonempty reducer domain required")

    requirements = expected_operation_requirements(variant)
    downstream_operation_recipe_sha256 = (
        target_materialization.fusion_on_downstream_operation_recipe_sha256
        if variant is FusionVariant.FUSION_ON
        else target_materialization.fusion_off_downstream_operation_recipe_sha256
    )
    common = {
        "schema": FUSION_ABLATION_PLAN_SCHEMA,
        "mechanism_id": CHECKED_U64_PRODUCT_SUM_MECHANISM,
        "shared_contract_file_sha256": freeze.file_sha256,
        "shared_contract_freeze_sha256": freeze.freeze_sha256,
        "semantic_request_sha256": freeze.semantic_request_sha256,
        "physical_encoding_sha256": freeze.physical_encoding_sha256,
        "admitted_reference_plan_sha256": freeze.admitted_reference_plan_sha256,
        "executable_family_plan_sha256": freeze.executable_family_plan_sha256,
        "transformation_variant_contract_sha256": (
            freeze.transformation_variant_contract_sha256),
        "physical_schema_sha256": freeze.physical_schema_sha256,
        "executable_family_id": freeze.executable_family_id,
        "execution_source_archive_sha256": (
            target_materialization.execution_source_archive_sha256),
        "execution_source_tree_sha256": (
            target_materialization.execution_source_tree_sha256),
        "callback_ir_sha256": target_materialization.callback_ir_sha256,
        "callback_authority_nonce": (
            target_materialization.callback_authority_nonce),
        "contract_sha256": target_materialization.contract_sha256,
        "abi_sha256": target_materialization.abi_sha256,
        "native_library_sha256": target_materialization.native_library_sha256,
        "provider_identity": target_materialization.provider_identity,
        "program_bundle_identity": target_materialization.program_bundle_identity,
        "composed_program_sha256": target_materialization.composed_program_sha256,
        "cupy_version": target_materialization.cupy_version,
        "fusion_on_downstream_operation_recipe": (
            target_materialization.fusion_on_downstream_operation_recipe.to_dict()),
        "fusion_off_downstream_operation_recipe": (
            target_materialization.fusion_off_downstream_operation_recipe.to_dict()),
        "fusion_on_downstream_operation_recipe_sha256": (
            target_materialization.fusion_on_downstream_operation_recipe_sha256),
        "fusion_off_downstream_operation_recipe_sha256": (
            target_materialization.fusion_off_downstream_operation_recipe_sha256),
        "target_identity_sha256": target_materialization.target_identity_sha256,
        "target_materialization_receipt_sha256": (
            target_materialization.receipt_sha256),
        "materializer_source_sha256": (
            target_materialization.materializer_source_sha256),
        "source_manifest_sha256": target_materialization.source_manifest_sha256,
        "materialization_evidence_archive_sha256": (
            target_materialization.evidence_archive_sha256),
        "materialization_nonce": target_materialization.materialization_nonce,
        "input_sha256": input_sha256,
        "output_contract_sha256": output_contract_sha256,
        "oracle_sha256": oracle_sha256,
        "timer_contract_sha256": timer_contract_sha256,
        "lifecycle_contract_sha256": lifecycle_contract_sha256,
        "value_count": value_count,
        "same_semantic_ir_required": True,
        "same_optix_producer_required": True,
        "performance_or_timing_claimed": False,
        "variant_selected_from_app_dataset_result_or_timing": False,
        "executable": False,
    }
    variant_payload = {
        **common,
        "variant": variant.value,
        "only_allowlisted_difference": _EXPECTED_ALLOWLIST,
        "lowering_node": _plan_lowering_node(variant),
        "downstream_operation_recipe_sha256": downstream_operation_recipe_sha256,
        "operation_requirements": [item.to_dict() for item in requirements],
    }
    return verify_fusion_ablation_plan(FusionAblationPlan(
        mechanism_id=CHECKED_U64_PRODUCT_SUM_MECHANISM,
        variant=variant,
        shared_contract_file_sha256=freeze.file_sha256,
        shared_contract_freeze_sha256=freeze.freeze_sha256,
        semantic_request_sha256=freeze.semantic_request_sha256,
        physical_encoding_sha256=freeze.physical_encoding_sha256,
        admitted_reference_plan_sha256=freeze.admitted_reference_plan_sha256,
        executable_family_plan_sha256=freeze.executable_family_plan_sha256,
        transformation_variant_contract_sha256=(
            freeze.transformation_variant_contract_sha256),
        physical_schema_sha256=freeze.physical_schema_sha256,
        executable_family_id=freeze.executable_family_id,
        execution_source_archive_sha256=(
            target_materialization.execution_source_archive_sha256),
        execution_source_tree_sha256=(
            target_materialization.execution_source_tree_sha256),
        callback_ir_sha256=target_materialization.callback_ir_sha256,
        callback_authority_nonce=target_materialization.callback_authority_nonce,
        contract_sha256=target_materialization.contract_sha256,
        abi_sha256=target_materialization.abi_sha256,
        native_library_sha256=target_materialization.native_library_sha256,
        provider_identity=target_materialization.provider_identity,
        program_bundle_identity=target_materialization.program_bundle_identity,
        composed_program_sha256=target_materialization.composed_program_sha256,
        cupy_version=target_materialization.cupy_version,
        fusion_on_downstream_operation_recipe=(
            target_materialization.fusion_on_downstream_operation_recipe),
        fusion_off_downstream_operation_recipe=(
            target_materialization.fusion_off_downstream_operation_recipe),
        fusion_on_downstream_operation_recipe_sha256=(
            target_materialization.fusion_on_downstream_operation_recipe_sha256),
        fusion_off_downstream_operation_recipe_sha256=(
            target_materialization.fusion_off_downstream_operation_recipe_sha256),
        target_identity_sha256=target_materialization.target_identity_sha256,
        target_materialization_receipt_sha256=(
            target_materialization.receipt_sha256),
        materializer_source_sha256=(
            target_materialization.materializer_source_sha256),
        source_manifest_sha256=target_materialization.source_manifest_sha256,
        materialization_evidence_archive_sha256=(
            target_materialization.evidence_archive_sha256),
        materialization_nonce=target_materialization.materialization_nonce,
        input_sha256=input_sha256,
        output_contract_sha256=output_contract_sha256,
        oracle_sha256=oracle_sha256,
        timer_contract_sha256=timer_contract_sha256,
        lifecycle_contract_sha256=lifecycle_contract_sha256,
        value_count=value_count,
        lowering_node=_plan_lowering_node(variant),
        downstream_operation_recipe_sha256=downstream_operation_recipe_sha256,
        operation_requirements=requirements,
        shared_identity_sha256=_digest(common),
        plan_sha256=_digest(variant_payload),
    ))


def verify_fusion_ablation_plan(plan: FusionAblationPlan) -> FusionAblationPlan:
    if type(plan) is not FusionAblationPlan:
        _fail("plan_type", "plan", type(plan).__name__)
    if plan.schema != FUSION_ABLATION_PLAN_SCHEMA or plan.executable is not False:
        _fail("plan_schema", "plan", repr((plan.schema, plan.executable)))
    if plan.mechanism_id != CHECKED_U64_PRODUCT_SUM_MECHANISM:
        _fail("mechanism", "plan.mechanism_id", plan.mechanism_id)
    if not isinstance(plan.variant, FusionVariant):
        _fail("variant", "plan.variant", repr(plan.variant))
    if type(plan.fusion_on_downstream_operation_recipe) \
            is not VerifiedDownstreamOperationRecipe \
            or type(plan.fusion_off_downstream_operation_recipe) \
            is not VerifiedDownstreamOperationRecipe:
        _fail(
            "plan_downstream_recipe_type",
            "plan",
            "recipes must be exact immutable verified recipe values",
        )
    frozen = (
        (plan.shared_contract_file_sha256, SHARED_CONTRACT_FREEZE_FILE_SHA256),
        (plan.shared_contract_freeze_sha256, SHARED_CONTRACT_FREEZE_SHA256),
        (plan.semantic_request_sha256, SEMANTIC_REQUEST_SHA256),
        (plan.physical_encoding_sha256, PHYSICAL_ENCODING_SHA256),
        (plan.admitted_reference_plan_sha256, ADMITTED_REFERENCE_PLAN_SHA256),
        (plan.executable_family_plan_sha256, EXECUTABLE_FAMILY_PLAN_SHA256),
        (plan.transformation_variant_contract_sha256,
         TRANSFORMATION_VARIANT_CONTRACT_SHA256),
        (plan.physical_schema_sha256, _EXPECTED_PHYSICAL_SCHEMA_SHA256),
    )
    for index, (actual, expected) in enumerate(frozen):
        if actual != expected:
            _fail("frozen_identity", f"plan.frozen[{index}]", actual)
    if plan.executable_family_id != _EXPECTED_FAMILY_ID \
            or plan.provider_identity != "optix" \
            or plan.program_bundle_identity != _EXPECTED_PROGRAM_BUNDLE:
        _fail("provider_family_binding", "plan", "provider family changed")
    if not isinstance(plan.callback_authority_nonce, str) \
            or _NONCE.fullmatch(plan.callback_authority_nonce) is None:
        _fail(
            "callback_authority_nonce",
            "plan.callback_authority_nonce",
            repr(plan.callback_authority_nonce),
        )
    if not isinstance(plan.cupy_version, str) or not plan.cupy_version \
            or len(plan.cupy_version) > 64:
        _fail("plan_cupy_version", "plan.cupy_version", repr(plan.cupy_version))
    for name in (
        "execution_source_archive_sha256", "execution_source_tree_sha256",
        "callback_ir_sha256", "contract_sha256", "abi_sha256",
        "native_library_sha256", "composed_program_sha256",
        "fusion_on_downstream_operation_recipe_sha256",
        "fusion_off_downstream_operation_recipe_sha256",
        "target_identity_sha256", "target_materialization_receipt_sha256",
        "materializer_source_sha256", "source_manifest_sha256",
        "materialization_evidence_archive_sha256",
        "input_sha256", "output_contract_sha256", "oracle_sha256",
        "timer_contract_sha256", "lifecycle_contract_sha256",
        "downstream_operation_recipe_sha256", "shared_identity_sha256", "plan_sha256",
    ):
        _sha(getattr(plan, name), "plan." + name)
    on_recipe = _verified_downstream_recipe(
        plan.fusion_on_downstream_operation_recipe.to_dict()
        if isinstance(
            plan.fusion_on_downstream_operation_recipe,
            VerifiedDownstreamOperationRecipe,
        ) else plan.fusion_on_downstream_operation_recipe,
        variant=FusionVariant.FUSION_ON,
        target_identity_sha256=plan.target_identity_sha256,
        cupy_version=plan.cupy_version,
        path="plan.fusion_on_downstream_operation_recipe",
    )
    off_recipe = _verified_downstream_recipe(
        plan.fusion_off_downstream_operation_recipe.to_dict()
        if isinstance(
            plan.fusion_off_downstream_operation_recipe,
            VerifiedDownstreamOperationRecipe,
        ) else plan.fusion_off_downstream_operation_recipe,
        variant=FusionVariant.FUSION_OFF,
        target_identity_sha256=plan.target_identity_sha256,
        cupy_version=plan.cupy_version,
        path="plan.fusion_off_downstream_operation_recipe",
    )
    if plan.fusion_on_downstream_operation_recipe_sha256 \
            != _digest(on_recipe.to_dict()) \
            or plan.fusion_off_downstream_operation_recipe_sha256 \
            != _digest(off_recipe.to_dict()):
        _fail(
            "plan_downstream_recipe_digest",
            "plan",
            "structured recipe does not match declared digest",
        )
    verify_target_materialization_authority({
        "schema": TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
        "shared_contract_freeze_sha256": plan.shared_contract_freeze_sha256,
        "execution_source_archive_sha256": plan.execution_source_archive_sha256,
        "execution_source_tree_sha256": plan.execution_source_tree_sha256,
        "callback_ir_sha256": plan.callback_ir_sha256,
        "callback_authority_nonce": plan.callback_authority_nonce,
        "contract_sha256": plan.contract_sha256,
        "abi_sha256": plan.abi_sha256,
        "provider_identity": plan.provider_identity,
        "program_bundle_identity": plan.program_bundle_identity,
        "composed_program_sha256": plan.composed_program_sha256,
        "cupy_version": plan.cupy_version,
        "fusion_on_downstream_operation_recipe": on_recipe.to_dict(),
        "fusion_off_downstream_operation_recipe": off_recipe.to_dict(),
        "fusion_on_downstream_operation_recipe_sha256": (
            plan.fusion_on_downstream_operation_recipe_sha256),
        "fusion_off_downstream_operation_recipe_sha256": (
            plan.fusion_off_downstream_operation_recipe_sha256),
        "native_library_sha256": plan.native_library_sha256,
        "native_payload_sha256": plan.native_library_sha256,
        "target_identity_sha256": plan.target_identity_sha256,
        "materializer_source_sha256": plan.materializer_source_sha256,
        "source_manifest_sha256": plan.source_manifest_sha256,
        "evidence_archive_sha256": plan.materialization_evidence_archive_sha256,
        "materialization_nonce": plan.materialization_nonce,
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
        "receipt_sha256": plan.target_materialization_receipt_sha256,
    })
    _u64(plan.value_count, "plan.value_count")
    if plan.value_count == 0:
        _fail("value_count", "plan.value_count", "nonempty reducer domain required")
    selected_downstream = (
        plan.fusion_on_downstream_operation_recipe_sha256
        if plan.variant is FusionVariant.FUSION_ON
        else plan.fusion_off_downstream_operation_recipe_sha256
    )
    if plan.downstream_operation_recipe_sha256 != selected_downstream:
        _fail(
            "downstream_operation_recipe_binding",
            "plan.downstream_operation_recipe_sha256",
            plan.downstream_operation_recipe_sha256,
        )
    if plan.lowering_node != _plan_lowering_node(plan.variant):
        _fail("lowering_node", "plan.lowering_node", plan.lowering_node)
    expected_requirements = expected_operation_requirements(plan.variant)
    if plan.operation_requirements != expected_requirements:
        _fail("operation_requirements", "plan.operation_requirements",
              "not the registered ordered sequence")
    if plan.shared_identity_sha256 != _digest(plan.common_payload()):
        _fail("shared_identity", "plan.shared_identity_sha256",
              plan.shared_identity_sha256)
    if plan.plan_sha256 != _digest(plan.payload_without_digests()):
        _fail("plan_digest", "plan.plan_sha256", plan.plan_sha256)
    plan.operation_contract()
    return plan


def verify_fusion_ablation_pair(
    fusion_on: FusionAblationPlan,
    fusion_off: FusionAblationPlan,
) -> tuple[FusionAblationPlan, FusionAblationPlan]:
    """Prove that a pair differs only by the frozen downstream allowlist."""

    on = verify_fusion_ablation_plan(fusion_on)
    off = verify_fusion_ablation_plan(fusion_off)
    if on.variant is not FusionVariant.FUSION_ON \
            or off.variant is not FusionVariant.FUSION_OFF:
        _fail("pair_variants", "pair", repr((on.variant, off.variant)))
    if on.common_payload() != off.common_payload() \
            or on.shared_identity_sha256 != off.shared_identity_sha256:
        _fail("pair_shared_identity", "pair", "non-allowlisted field differs")
    if on.downstream_operation_recipe_sha256 == off.downstream_operation_recipe_sha256:
        _fail("pair_downstream_identity", "pair",
              "distinct downstream implementations require distinct identities")
    left = on.to_dict()
    right = off.to_dict()
    changed = {key for key in left if left[key] != right[key]}
    allowed = {
        "variant", "lowering_node", "downstream_operation_recipe_sha256",
        "operation_requirements", "plan_sha256",
    }
    if changed != allowed:
        _fail("pair_delta", "pair", repr(sorted(changed)))
    return on, off


def plan_from_mapping(value: Mapping[str, object]) -> FusionAblationPlan:
    """Strict portable parser used by clean validators and independent tools."""

    if not isinstance(value, Mapping):
        _fail("plan_mapping", "plan", type(value).__name__)
    # As with target authority parsing, bind one immutable view of a portable
    # caller mapping before any shape, digest or field checks.
    value = dict(value)
    data_fields = set(FusionAblationPlan.__dataclass_fields__)
    boundary_fields = {
        "only_allowlisted_difference", "same_semantic_ir_required",
        "same_optix_producer_required", "performance_or_timing_claimed",
        "variant_selected_from_app_dataset_result_or_timing",
    }
    expected = data_fields | boundary_fields
    if set(value) != expected:
        _fail("plan_fields", "plan", repr(sorted(set(value) ^ expected)))
    if value["only_allowlisted_difference"] != _EXPECTED_ALLOWLIST \
            or value["same_semantic_ir_required"] is not True \
            or value["same_optix_producer_required"] is not True \
            or value["performance_or_timing_claimed"] is not False \
            or value["variant_selected_from_app_dataset_result_or_timing"] is not False:
        _fail("plan_boundary", "plan", "claim or allowlist boundary changed")
    raw_requirements = value["operation_requirements"]
    if not isinstance(raw_requirements, list):
        _fail("requirements_type", "plan.operation_requirements",
              type(raw_requirements).__name__)
    requirements: list[OperationRequirement] = []
    requirement_fields = set(OperationRequirement.__dataclass_fields__)
    for index, row in enumerate(raw_requirements):
        if not isinstance(row, Mapping) or set(row) != requirement_fields:
            _fail("requirement_fields", f"plan.operation_requirements[{index}]",
                  repr(row))
        try:
            kind = OperationKind(row["kind"])
        except (TypeError, ValueError):
            _fail("operation_kind", f"plan.operation_requirements[{index}].kind",
                  repr(row.get("kind")))
        requirements.append(OperationRequirement(
            ordinal=row["ordinal"],
            operation_id=row["operation_id"],
            kind=kind,
            units_per_value=row["units_per_value"],
            fixed_units=row["fixed_units"],
            bytes_per_unit=row["bytes_per_unit"],
            fixed_bytes=row["fixed_bytes"],
            host_visibility_boundary=row["host_visibility_boundary"],
            compiler_visible_only=row["compiler_visible_only"],
        ))
    try:
        variant = FusionVariant(value["variant"])
    except (TypeError, ValueError):
        _fail("variant", "plan.variant", repr(value.get("variant")))
    target_identity_sha256 = _sha(
        value["target_identity_sha256"], "plan.target_identity_sha256")
    cupy_version = value["cupy_version"]
    if not isinstance(cupy_version, str) or not cupy_version \
            or len(cupy_version) > 64:
        _fail("plan_cupy_version", "plan.cupy_version", repr(cupy_version))
    on_recipe = _verified_downstream_recipe(
        value["fusion_on_downstream_operation_recipe"],
        variant=FusionVariant.FUSION_ON,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
        path="plan.fusion_on_downstream_operation_recipe",
    )
    off_recipe = _verified_downstream_recipe(
        value["fusion_off_downstream_operation_recipe"],
        variant=FusionVariant.FUSION_OFF,
        target_identity_sha256=target_identity_sha256,
        cupy_version=cupy_version,
        path="plan.fusion_off_downstream_operation_recipe",
    )
    return verify_fusion_ablation_plan(FusionAblationPlan(
        **{
            key: value[key]
            for key in data_fields
            if key not in {
                "variant", "operation_requirements",
                "fusion_on_downstream_operation_recipe",
                "fusion_off_downstream_operation_recipe",
            }
        },
        variant=variant,
        fusion_on_downstream_operation_recipe=on_recipe,
        fusion_off_downstream_operation_recipe=off_recipe,
        operation_requirements=tuple(requirements),
    ))


__all__ = (
    "ADMITTED_REFERENCE_PLAN_SHA256",
    "CHECKED_U64_PRODUCT_SUM_MECHANISM",
    "EXECUTABLE_FAMILY_PLAN_SHA256",
    "FUSION_ABLATION_PLAN_SCHEMA",
    "FusionAblationError",
    "FusionAblationPlan",
    "FusionVariant",
    "PHYSICAL_ENCODING_SHA256",
    "SEMANTIC_REQUEST_SHA256",
    "SHARED_CONTRACT_FREEZE_FILE_SHA256",
    "SHARED_CONTRACT_FREEZE_SHA256",
    "TARGET_MATERIALIZATION_AUTHORITY_SCHEMA",
    "TRANSFORMATION_VARIANT_CONTRACT_SHA256",
    "VerifiedSharedContractFreeze",
    "VerifiedDownstreamOperationRecipe",
    "VerifiedTargetMaterializationAuthority",
    "build_checked_u64_product_sum_ablation_plan",
    "expected_operation_requirements",
    "load_verified_shared_contract_freeze",
    "plan_from_mapping",
    "verify_target_materialization_authority",
    "verify_fusion_ablation_pair",
    "verify_fusion_ablation_plan",
)
