"""Goal5838 selected family route outside every preselection-owned module."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path

from .v4_family_route_adapters import (
    DeclarativeFamilyRouteV1,
    _base_shape,
    _buffer,
    _instance,
    _plan,
    _program_artifacts,
    _provider_operator,
    _role,
)
from .v4_family_schema import CanonicalFamilyCompilationPlan, FamilySchemaV1
from .v4_generic_family_lifecycle import (
    FamilyExecutableIdentityV1,
    FamilyMaterializedHandleV1,
    FamilyPreparedHandleV1,
    FamilyProgramArtifactsV1,
    FamilyProviderDescriptorV1,
    FamilyProviderExecutionV1,
    FamilyProviderV1,
    derive_family_plan_requirements,
    expected_provider_projection,
)
from .v4_sphere_any_hit_count_contract import (
    SPHERE_ANY_HIT_COUNT_TEMPLATE,
    build_sphere_any_hit_count_authority,
)
from .v4_sphere_physical_schema import SphereTargetProfile

_MODULE_PATH = Path(__file__).resolve()
_SELECTED_CANDIDATE_ID = (
    "builtin_sphere::any_hit_count_continue_u64_per_query"
)
_SELECTION_RESULT_SHA256 = (
    "9f543f52cd9453e0410766aa79c3f302a6a0e39314487279842fa5ad5e57ed61"
)


def _module_sha256() -> str:
    return hashlib.sha256(_MODULE_PATH.read_bytes()).hexdigest()


def _sphere_any_hit_count_shape(
    resources: Mapping[str, object],
) -> dict[str, object]:
    prefix = "sphere_count"
    event = f"{prefix}_per_query_u64"
    operator_id = "rtdl.result.per_query_u64.v1"
    contract = {
        "schema": "rtdl.provider_operator_contract.v1",
        "operator_id": operator_id,
        "input": "verified_finalize_output",
        "operation": "commit_per_query_u64",
        "output": "u64_per_query",
        "count_relation": "query_count",
        "overflow": "fail_closed_before_output",
    }
    shape = _base_shape(
        prefix=prefix,
        parameters=[],
        primitive_kind="builtin_sphere",
        buffers=[
            _buffer(
                f"{prefix}_centers",
                0,
                "primitive.center",
                "primitive",
                "vec3f_bits",
                "read_only",
                "primitive_count",
                16,
            ),
            _buffer(
                f"{prefix}_radii",
                1,
                "primitive.radius",
                "primitive",
                "f32_bits",
                "read_only",
                "primitive_count",
                4,
            ),
            _buffer(
                f"{prefix}_queries",
                2,
                "query.motion_segment",
                "query",
                "ray3f_bits",
                "read_only",
                "query_count",
                16,
            ),
            _buffer(
                f"{prefix}_output",
                3,
                "result.per_query_u64",
                "result",
                "u64",
                "write_only",
                "query_count",
                8,
            ),
        ],
        channels=[],
        views=[],
        events=[
            {
                "event_id": event,
                "ordinal": 0,
                "value_type": "u64",
                "source": "ir_output",
            }
        ],
        roles=[
            _role("make_ray", ("trace_request",)),
            _role("any_hit", ("accept_continue",)),
            _role("miss", ("payload",)),
            _role("finalize", ("output",)),
        ],
        channel_bindings=[],
        result_pipeline=[
            _provider_operator(
                step_id=f"{prefix}_commit",
                operator_id=operator_id,
                contract=contract,
                inputs=[{"kind": "event", "event_ref": event}],
                output_type="u64",
                output_count_relation="query_count",
                algebra_properties=(
                    "associative",
                    "commutative",
                    "deterministic",
                    "fail_closed",
                ),
            )
        ],
        capabilities=(
            "any_hit_accept_continue",
            "builtin_sphere_intersection",
            "callback_ir",
            "fail_closed_status",
            "per_query_u64_output",
        ),
        resources=resources,
    )
    shape["physical"]["sbt"]["record_count_relation"] = "constant_one"
    return shape


def _output_adapter(
    result: object,
) -> tuple[object, str, Mapping[str, object]]:
    receipt = dict(result.traversal_receipt)
    receipt["selected_topology"] = _SELECTED_CANDIDATE_ID
    receipt["role_counters"] = list(result.counters)
    receipt["physical_receipt"] = dict(result.physical_receipt)
    return result.output, result.output_sha256, receipt


class _PreparedBridge(FamilyPreparedHandleV1):
    def __init__(self, prepared, identity, plan_sha256: str) -> None:
        self._prepared = prepared
        self._identity = identity
        self._plan_sha256 = plan_sha256

    @property
    def lifecycle_receipt(self) -> Mapping[str, object]:
        return self._prepared.lifecycle_receipt

    def execute(self, batch: object) -> FamilyProviderExecutionV1:
        result = self._prepared.execute(batch)
        output, output_sha256, receipt = _output_adapter(result)
        return FamilyProviderExecutionV1(
            self._plan_sha256,
            self._identity.identity_sha256,
            "OK",
            0,
            output,
            output_sha256,
            receipt,
        )

    def close(self) -> None:
        self._prepared.close()


class _MaterializedBridge(FamilyMaterializedHandleV1):
    def __init__(self, materialized, identity, plan_sha256: str) -> None:
        self._materialized = materialized
        self._identity = identity
        self._plan_sha256 = plan_sha256

    @property
    def identity(self) -> FamilyExecutableIdentityV1:
        return self._identity

    def prepare(self, static_input: object) -> FamilyPreparedHandleV1:
        return _PreparedBridge(
            self._materialized.prepare(static_input),
            self._identity,
            self._plan_sha256,
        )


class _SelectedSphereOptixProvider(FamilyProviderV1):
    def __init__(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: FamilyProgramArtifactsV1,
        *,
        callback: object,
        proof: object,
        abi: object,
        behavior: object,
        physical_schema_sha256: str,
    ) -> None:
        self._plan_sha256 = plan.plan_sha256
        self._artifacts = artifacts
        self._callback = callback
        self._proof = proof
        self._abi = abi
        self._behavior = behavior
        self._physical_schema_sha256 = physical_schema_sha256
        self._implementation_sha256 = _module_sha256()
        requirements = derive_family_plan_requirements(plan)
        self._descriptor = FamilyProviderDescriptorV1(
            provider_id="rtdl.optix.builtin_sphere_any_hit_count",
            provider_version="v1",
            target_api="optix.v4",
            implementation_sha256=self._implementation_sha256,
            graph_kinds=requirements.graph_kinds,
            primitive_kinds=requirements.primitive_kinds,
            callback_roles=requirements.callback_roles,
            provider_builtins=requirements.provider_builtins,
            artifact_formats=artifacts.artifact_formats,
            operator_contracts=requirements.operator_contracts,
            capabilities=requirements.capabilities,
        )

    def _check(
        self,
        plan: CanonicalFamilyCompilationPlan,
        artifacts: FamilyProgramArtifactsV1,
    ) -> None:
        if plan.plan_sha256 != self._plan_sha256:
            raise ValueError("selected provider is bound to a different plan")
        if artifacts != self._artifacts:
            raise ValueError("selected provider artifact bundle differs")
        if _module_sha256() != self._implementation_sha256:
            raise RuntimeError("selected provider bytes changed after binding")

    @property
    def descriptor(self) -> FamilyProviderDescriptorV1:
        return self._descriptor

    def project(self, plan, artifacts):
        self._check(plan, artifacts)
        return expected_provider_projection(plan, self._descriptor, artifacts)

    def materialize(
        self,
        plan,
        projection,
        artifacts,
        *,
        target,
        toolchain,
    ) -> FamilyMaterializedHandleV1:
        self._check(plan, artifacts)
        expected = expected_provider_projection(plan, self._descriptor, artifacts)
        if projection != expected:
            raise ValueError("selected provider projection differs")
        from .v4_public_sphere_any_hit_count import sphere_any_hit_count_source

        source = sphere_any_hit_count_source()
        program = source.compile(target=target)
        if (
            program.source.source_sha256 != source.source_sha256
            or program.authority.callback.ir_sha256 != self._callback.ir_sha256
            or program.authority.callback.effect_digest
            != self._callback.effect_digest
            or program.authority.schema.schema_sha256
            != self._physical_schema_sha256
            or program.proof != self._proof
            or program.abi.abi_sha256 != self._abi.abi_sha256
            or program.behavior.schema_sha256 != self._behavior.schema_sha256
        ):
            raise RuntimeError("selected sphere verified identities drifted")
        materialized = program.materialize(toolchain=toolchain)
        executable = materialized.executable
        identity = FamilyExecutableIdentityV1(
            self._descriptor.descriptor_sha256,
            projection.projection_sha256,
            plan.plan_sha256,
            program.target.profile.target_sha256,
            executable.executable_sha256,
            program.target.profile.native_sha256,
            executable.composed.ptx_sha256,
        )
        return _MaterializedBridge(materialized, identity, plan.plan_sha256)


def sphere_any_hit_count_family_route() -> DeclarativeFamilyRouteV1:
    """Bind the independent selection through only post-seal extension APIs."""

    # The family plan contains schema/proof identities, not this inert profile.
    planning_target = SphereTargetProfile(
        "optix", "9.0.0", "1.0", "0" * 64
    )
    authority, proof, abi, behavior = build_sphere_any_hit_count_authority(
        planning_target
    )
    callback = authority.callback
    schema = FamilySchemaV1(
        _sphere_any_hit_count_shape(
            callback.program.manifest.resources.to_dict()
        )
    )
    instance = _instance(
        schema,
        parameter_values=[],
        nominal_semantics={
            "event": "primitive.intersection_once",
            "output": "result.per_query_u64",
        },
        callback=callback,
        abi_sha256=abi.abi_sha256,
        authorities=[
            {
                "authority_kind": "any_hit_proof",
                "authority_sha256": proof.proof_sha256,
            },
            {
                "authority_kind": "physical_schema",
                "authority_sha256": authority.schema.schema_sha256,
            },
            {
                "authority_kind": "challenge_selection",
                "authority_sha256": _SELECTION_RESULT_SHA256,
            },
        ],
    )
    plan = _plan(
        schema,
        instance,
        behavior_schema_sha256=behavior.schema_sha256,
        template_id=SPHERE_ANY_HIT_COUNT_TEMPLATE,
    )
    artifacts = _program_artifacts(
        plan, callback=callback, abi=abi, behavior=behavior
    )
    provider = _SelectedSphereOptixProvider(
        plan,
        artifacts,
        callback=callback,
        proof=proof,
        abi=abi,
        behavior=behavior,
        physical_schema_sha256=authority.schema.schema_sha256,
    )
    return DeclarativeFamilyRouteV1(
        "prospective_selected_extension", plan, artifacts, provider
    )


__all__ = ["sphere_any_hit_count_family_route"]
