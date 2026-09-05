"""Narrow public API for schema-driven RTDL V4 protocol families.

This additive module leaves the historically frozen :mod:`rtdsl.v4` facade
unchanged.  It exports only the provider-neutral schema, lifecycle, and
provider SPI.  Concrete route declarations and providers live in extension
modules and are intentionally not re-exported here.
"""

from .v4_family_schema import (
    CanonicalFamilyCompilationPlan,
    FamilySchemaError,
    FamilySchemaV1,
    ProtocolInstanceV1,
    VerifiedFamilyAdmission,
    admit_family_schema,
    lower_canonical_compilation_plan,
    reverify_canonical_compilation_plan,
    reverify_family_admission,
)
from .v4_generic_family_lifecycle import (
    FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2,
    FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID,
    FAMILY_CALLBACK_ABI_ARTIFACT_ID,
    FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID,
    FamilyArtifactV1,
    FamilyDeploymentExportV1,
    FamilyExecutableIdentityV1,
    FamilyMaterializedHandleV1,
    FamilyPlanRequirementsV1,
    FamilyPreparedHandleV1,
    FamilyProgramArtifactsV1,
    FamilyProviderDescriptorV1,
    FamilyProviderExecutionV1,
    FamilyProviderProjectionV1,
    FamilyProviderV1,
    GenericFamilyExecutionResultV1,
    GenericFamilyLifecycleError,
    MaterializedGenericFamilyProgram,
    PreparedGenericFamilyProgram,
    VerifiedGenericFamilyProgram,
    bind_family_program_artifacts,
    compile_generic_family_program,
    derive_family_plan_requirements,
    derive_family_target_sha256,
    expected_provider_projection,
    reverify_family_program_artifacts,
    reverify_family_provider_descriptor,
)


V4_FAMILY_API_VERSION = "1.0.0"


__all__ = sorted([
    "CanonicalFamilyCompilationPlan",
    "FAMILY_BEHAVIOR_SCHEMA_ARTIFACT_ID",
    "FAMILY_CALLBACK_ABI_ARTIFACT_ID",
    "FAMILY_CALLBACK_PROGRAM_ARTIFACT_ID",
    "FAMILY_DEPLOYMENT_FORMAT_RTDLEXE_V2",
    "FamilyArtifactV1",
    "FamilyDeploymentExportV1",
    "FamilyExecutableIdentityV1",
    "FamilyMaterializedHandleV1",
    "FamilyPlanRequirementsV1",
    "FamilyPreparedHandleV1",
    "FamilyProgramArtifactsV1",
    "FamilyProviderDescriptorV1",
    "FamilyProviderExecutionV1",
    "FamilyProviderProjectionV1",
    "FamilyProviderV1",
    "FamilySchemaError",
    "FamilySchemaV1",
    "GenericFamilyExecutionResultV1",
    "GenericFamilyLifecycleError",
    "MaterializedGenericFamilyProgram",
    "PreparedGenericFamilyProgram",
    "ProtocolInstanceV1",
    "V4_FAMILY_API_VERSION",
    "VerifiedFamilyAdmission",
    "VerifiedGenericFamilyProgram",
    "admit_family_schema",
    "bind_family_program_artifacts",
    "compile_generic_family_program",
    "derive_family_plan_requirements",
    "derive_family_target_sha256",
    "expected_provider_projection",
    "lower_canonical_compilation_plan",
    "reverify_canonical_compilation_plan",
    "reverify_family_admission",
    "reverify_family_program_artifacts",
    "reverify_family_provider_descriptor",
])
