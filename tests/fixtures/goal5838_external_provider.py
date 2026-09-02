"""Package-external conformance provider for Goal5838 tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from rtdsl.v4_family import (
    FamilyExecutableIdentityV1,
    FamilyMaterializedHandleV1,
    FamilyPreparedHandleV1,
    FamilyProviderDescriptorV1,
    FamilyProviderExecutionV1,
    FamilyProviderV1,
    derive_family_plan_requirements,
    expected_provider_projection,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


class ExternalPrepared(FamilyPreparedHandleV1):
    def __init__(self, identity, plan_sha256, static_input) -> None:
        self._identity = identity
        self._plan_sha256 = plan_sha256
        self._static_input = static_input
        self._closed = False
        self.execution_count = 0

    @property
    def lifecycle_receipt(self):
        return {
            "schema": "external.provider.lifecycle.v1",
            "execution_count": self.execution_count,
            "static_input_sha256": _digest(self._static_input),
        }

    def execute(self, batch):
        self.execution_count += 1
        if batch.get("fail"):
            return FamilyProviderExecutionV1(
                self._plan_sha256,
                self._identity.identity_sha256,
                "ERROR",
                17,
                None,
                None,
                {"physical_executor_classification": "external_failure"},
            )
        output = {
            "static": self._static_input,
            "value": batch["value"],
        }
        return FamilyProviderExecutionV1(
            self._plan_sha256,
            self._identity.identity_sha256,
            "OK",
            0,
            output,
            _digest(output),
            {
                "physical_executor_classification": "external_conformance_cpu",
                "execution_count": self.execution_count,
            },
        )

    def close(self):
        self._closed = True


class ExternalMaterialized(FamilyMaterializedHandleV1):
    def __init__(self, identity, plan_sha256) -> None:
        self._identity = identity
        self._plan_sha256 = plan_sha256

    @property
    def identity(self):
        return self._identity

    def prepare(self, static_input):
        return ExternalPrepared(self._identity, self._plan_sha256, static_input)


class ExternalConformanceProvider(FamilyProviderV1):
    def __init__(self, plan, artifacts, *, omit_capability: str | None = None) -> None:
        requirements = derive_family_plan_requirements(plan)
        capabilities = tuple(
            item for item in requirements.capabilities if item != omit_capability
        )
        self._artifacts = artifacts
        self._descriptor = FamilyProviderDescriptorV1(
            provider_id="external.goal5838.conformance",
            provider_version="v1",
            target_api="cpu.reference",
            implementation_sha256=hashlib.sha256(
                Path(__file__).read_bytes()
            ).hexdigest(),
            graph_kinds=requirements.graph_kinds,
            primitive_kinds=requirements.primitive_kinds,
            callback_roles=requirements.callback_roles,
            provider_builtins=requirements.provider_builtins,
            artifact_formats=artifacts.artifact_formats,
            operator_contracts=requirements.operator_contracts,
            capabilities=capabilities,
        )
        self.corrupt_projection = False
        self.corrupt_target_identity = False

    @property
    def descriptor(self):
        return self._descriptor

    def project(self, plan, artifacts):
        if artifacts != self._artifacts:
            raise ValueError("external provider artifact bundle mismatch")
        result = expected_provider_projection(plan, self._descriptor, artifacts)
        if self.corrupt_projection:
            from dataclasses import replace

            return replace(result, callback_ir_sha256="f" * 64)
        return result

    def materialize(self, plan, projection, artifacts, *, target, toolchain):
        if artifacts != self._artifacts:
            raise ValueError("external provider artifact bundle mismatch")
        identity = FamilyExecutableIdentityV1(
            self._descriptor.descriptor_sha256,
            projection.projection_sha256,
            plan.plan_sha256,
            _digest("wrong-target") if self.corrupt_target_identity else _digest(target),
            _digest({"plan": plan.plan_sha256, "kind": "external_executable"}),
            _digest({"target": target, "kind": "external_native"}),
            _digest({"plan": plan.plan_sha256, "kind": "external_source"}),
        )
        return ExternalMaterialized(identity, plan.plan_sha256)
