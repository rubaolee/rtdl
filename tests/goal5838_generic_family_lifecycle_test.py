from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import pickle
import sys
import threading
import unittest
from unittest.mock import PropertyMock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "fixtures"))

from tests.goal5833_family_schema_compilation_plan_test import (  # noqa: E402
    _instance,
    _shape,
)
from goal5838_external_provider import ExternalConformanceProvider  # noqa: E402
from rtdsl.v4_family_schema import (  # noqa: E402
    FamilySchemaError,
    FamilySchemaV1,
    ProtocolInstanceV1,
    admit_family_schema,
    lower_canonical_compilation_plan,
)
from rtdsl.v4_generic_family_lifecycle import (  # noqa: E402
    FamilyArtifactV1,
    FamilyProviderExecutionV1,
    GenericFamilyLifecycleError,
    bind_family_program_artifacts,
    compile_generic_family_program,
    derive_family_plan_requirements,
    expected_provider_projection,
    reverify_family_program_artifacts,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _provider_shape() -> dict[str, object]:
    value = _shape()
    value["channels"][0]["producer"] = {
        "kind": "provider_builtin",
        "builtin": "trace.primitive_index",
    }
    value["physical"]["channel_bindings"][0] = {
        "channel_ref": "author_attr0",
        "provider_builtin": "trace.primitive_index",
    }
    value["events"][0]["source"] = "provider_builtin"
    value["events"][0]["provider_builtin"] = "trace.accepted_record"
    value["result_pipeline"] = [
        {
            "operator": "provider_operator",
            "step_id": "collect",
            "operator_id": "external.example.collect.v1",
            "operator_contract_sha256": _sha("external.example.collect.v1"),
            "inputs": [
                {"kind": "event", "event_ref": "author_row"},
                {"kind": "parameter", "parameter_ref": "author_capacity"},
            ],
            "output_type": "u32x2",
            "output_count_relation": "result_count",
            "algebra_properties": ["deterministic", "fail_closed"],
            "commits_output": True,
        },
    ]
    return value


def _plan():
    schema = FamilySchemaV1(_provider_shape())
    instance = ProtocolInstanceV1(_instance(schema.family_shape_sha256))
    return lower_canonical_compilation_plan(admit_family_schema(
        schema,
        instance,
        behavior_schema_sha256=_sha("behavior"),
        canonical_template_id="external.example.template.v1",
    ))


def _artifacts(plan):
    def payload(kind: str) -> bytes:
        return json.dumps(
            {"kind": kind, "plan_sha256": plan.plan_sha256},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")

    return bind_family_program_artifacts(plan, (
        FamilyArtifactV1(
            "rtdl.callback.program",
            "rtdl.callback_program.canonical_json.v1",
            payload("callback_program"),
        ),
        FamilyArtifactV1(
            "rtdl.callback.abi",
            "rtdl.callback_abi.canonical_json.v1",
            payload("callback_abi"),
        ),
        FamilyArtifactV1(
            "rtdl.behavior.schema",
            "rtdl.behavior_schema.canonical_json.v1",
            payload("behavior_schema"),
        ),
    ))


def _external_program(plan):
    artifacts = _artifacts(plan)
    provider = ExternalConformanceProvider(plan, artifacts)
    return compile_generic_family_program(plan, provider, artifacts=artifacts)


class Goal5838GenericFamilyLifecycleTest(unittest.TestCase):
    def test_provider_operator_is_identity_bearing_and_generic(self) -> None:
        first = _plan()
        changed = _provider_shape()
        changed["result_pipeline"][0]["operator_contract_sha256"] = _sha("changed")
        schema = FamilySchemaV1(changed)
        instance = ProtocolInstanceV1(_instance(schema.family_shape_sha256))
        second = lower_canonical_compilation_plan(admit_family_schema(
            schema,
            instance,
            behavior_schema_sha256=_sha("behavior"),
            canonical_template_id="external.example.template.v1",
        ))
        self.assertNotEqual(first.plan_sha256, second.plan_sha256)
        requirements = derive_family_plan_requirements(first)
        self.assertEqual(
            requirements.operator_contracts,
            (("external.example.collect.v1", _sha("external.example.collect.v1")),),
        )
        self.assertEqual(
            requirements.provider_builtins,
            ("trace.accepted_record", "trace.primitive_index"),
        )

    def test_provider_operator_output_cardinality_is_identity_bearing(self) -> None:
        first = _plan()
        changed = _provider_shape()
        changed["result_pipeline"][0]["output_count_relation"] = "query_count"
        schema = FamilySchemaV1(changed)
        instance = ProtocolInstanceV1(_instance(schema.family_shape_sha256))
        second = lower_canonical_compilation_plan(admit_family_schema(
            schema,
            instance,
            behavior_schema_sha256=_sha("behavior"),
            canonical_template_id="external.example.template.v1",
        ))
        self.assertNotEqual(first.plan_sha256, second.plan_sha256)

    def test_provider_builtin_event_requires_named_capability(self) -> None:
        changed = _provider_shape()
        del changed["events"][0]["provider_builtin"]
        with self.assertRaisesRegex(FamilySchemaError, "FS046_CHANNEL_PRODUCER"):
            FamilySchemaV1(changed)

    def test_physical_channel_binding_must_match_declared_producer(self) -> None:
        changed = _provider_shape()
        changed["physical"]["channel_bindings"][0]["provider_builtin"] = (
            "trace.instance_index"
        )
        with self.assertRaisesRegex(FamilySchemaError, "FS046_CHANNEL_PRODUCER"):
            FamilySchemaV1(changed)

    def test_physical_metadata_must_match_logical_buffer_view(self) -> None:
        changed = _provider_shape()
        changed["physical"]["metadata_bindings"][0]["buffer_ref"] = "author_result"
        with self.assertRaisesRegex(FamilySchemaError, "FS046_CHANNEL_PRODUCER"):
            FamilySchemaV1(changed)

    def test_every_channel_requires_one_physical_binding(self) -> None:
        missing = _provider_shape()
        missing["physical"]["channel_bindings"] = []
        with self.assertRaisesRegex(FamilySchemaError, "FS046_CHANNEL_PRODUCER"):
            FamilySchemaV1(missing)

        duplicate = _provider_shape()
        duplicate["physical"]["channel_bindings"].append(copy.deepcopy(
            duplicate["physical"]["channel_bindings"][0]
        ))
        with self.assertRaisesRegex(FamilySchemaError, "FS024_DUPLICATE"):
            FamilySchemaV1(duplicate)

    def test_provider_operator_cannot_reference_future_step(self) -> None:
        changed = _provider_shape()
        changed["result_pipeline"][0]["inputs"] = [
            {"kind": "step", "step_ref": "future"},
        ]
        with self.assertRaisesRegex(FamilySchemaError, "FS045_PIPELINE_DATAFLOW"):
            FamilySchemaV1(changed)

    def test_one_operator_id_cannot_name_two_contracts(self) -> None:
        changed = _provider_shape()
        changed["result_pipeline"] = [
            {
                **changed["result_pipeline"][0],
                "commits_output": False,
            },
            {
                **changed["result_pipeline"][0],
                "step_id": "second",
                "operator_contract_sha256": _sha("different-contract"),
            },
        ]
        with self.assertRaisesRegex(FamilySchemaError, "FS047_OPERATOR_IDENTITY"):
            FamilySchemaV1(changed)

    def test_package_external_provider_runs_generic_lifecycle(self) -> None:
        plan = _plan()
        program = _external_program(plan)
        materialized = program.materialize(
            target={"target": "cpu"}, toolchain={"toolchain": "reference"}
        )
        self.assertEqual(materialized.state, "materialized")
        prepared = materialized.prepare({"static": [1, 2, 3]})
        result = prepared.execute({"value": 17})
        self.assertEqual(result.output["value"], 17)
        self.assertEqual(materialized.state, "prepared")
        receipt = prepared.lifecycle_receipt
        self.assertTrue(receipt["nonserializable"])
        self.assertTrue(receipt["nonreentrant"])
        self.assertEqual(receipt["provider_receipt"]["execution_count"], 1)
        prepared.close()
        prepared.close()
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF018_STATE"):
            prepared.execute({"value": 18})

    def test_required_program_artifacts_cannot_be_omitted(self) -> None:
        plan = _plan()
        complete = _artifacts(plan)
        rows = tuple(
            row for row in complete.artifacts
            if row.artifact_id != "rtdl.callback.abi"
        )
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF035_ARTIFACT_BUNDLE"
        ):
            bind_family_program_artifacts(plan, rows)

    def test_artifact_payload_drift_is_rejected(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        first = artifacts.artifacts[0]
        object.__setattr__(first, "payload", b"forged-after-binding")
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF037_ARTIFACT_DRIFT"
        ):
            reverify_family_program_artifacts(plan, artifacts)

    def test_artifact_bytes_are_bound_into_provider_projection(self) -> None:
        plan = _plan()
        first = _artifacts(plan)
        changed_rows = tuple(
            FamilyArtifactV1(row.artifact_id, row.format_id, (
                row.payload + b" "
                if row.artifact_id == "rtdl.callback.program" else row.payload
            ))
            for row in first.artifacts
        )
        second = bind_family_program_artifacts(plan, changed_rows)
        provider = ExternalConformanceProvider(plan, first)
        first_projection = expected_provider_projection(
            plan, provider.descriptor, first
        )
        second_projection = expected_provider_projection(
            plan, provider.descriptor, second
        )
        self.assertNotEqual(first.bundle_sha256, second.bundle_sha256)
        self.assertNotEqual(
            first_projection.projection_sha256,
            second_projection.projection_sha256,
        )

    def test_live_capabilities_are_not_serializable(self) -> None:
        plan = _plan()
        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF030_NONSERIALIZABLE"
        ):
            pickle.dumps(materialized)
        prepared = materialized.prepare({"static": [1]})
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF030_NONSERIALIZABLE"
        ):
            pickle.dumps(prepared)
        prepared.close()

    def test_destroy_failure_permanently_invalidates_capability(self) -> None:
        plan = _plan()
        prepared = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        ).prepare(
            {"static": [1]}
        )
        prepared._handle.close = lambda: (_ for _ in ()).throw(  # type: ignore[method-assign]
            RuntimeError("destroy failed")
        )
        with self.assertRaisesRegex(RuntimeError, "destroy failed"):
            prepared.close()
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF018_STATE"):
            prepared.execute({"value": 2})

    def test_missing_capability_fails_before_provider_projection(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        provider = ExternalConformanceProvider(
            plan, artifacts, omit_capability="external.test_leaf"
        )
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF009_PROVIDER_CAPABILITY"
        ):
            compile_generic_family_program(plan, provider, artifacts=artifacts)

    def test_every_provider_requirement_category_is_enforced(self) -> None:
        plan = _plan()
        for field in (
            "graph_kinds",
            "primitive_kinds",
            "callback_roles",
            "provider_builtins",
            "artifact_formats",
            "operator_contracts",
            "capabilities",
        ):
            with self.subTest(field=field):
                artifacts = _artifacts(plan)
                provider = ExternalConformanceProvider(plan, artifacts)
                supported = getattr(provider.descriptor, field)
                self.assertGreater(len(supported), 0)
                provider._descriptor = replace(  # type: ignore[attr-defined]
                    provider.descriptor,
                    **{field: supported[1:]},
                )
                with self.assertRaisesRegex(
                    GenericFamilyLifecycleError, "GF009_PROVIDER_CAPABILITY"
                ):
                    compile_generic_family_program(
                        plan, provider, artifacts=artifacts
                    )

    def test_corrupt_provider_projection_fails_closed(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        provider = ExternalConformanceProvider(plan, artifacts)
        provider.corrupt_projection = True
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF029_PROVIDER_PROJECTION_MISMATCH"
        ):
            compile_generic_family_program(plan, provider, artifacts=artifacts)

    def test_provider_descriptor_drift_is_rejected_at_both_boundaries(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        provider = ExternalConformanceProvider(plan, artifacts)
        original_project = provider.project

        def project_then_drift(project_plan, project_artifacts):
            projection = original_project(project_plan, project_artifacts)
            provider._descriptor = replace(  # type: ignore[attr-defined]
                provider.descriptor, provider_version="v2"
            )
            return projection

        provider.project = project_then_drift  # type: ignore[method-assign]
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF039_PROVIDER_DESCRIPTOR_DRIFT"
        ):
            compile_generic_family_program(plan, provider, artifacts=artifacts)

        provider = ExternalConformanceProvider(plan, artifacts)
        program = compile_generic_family_program(
            plan, provider, artifacts=artifacts
        )
        provider._descriptor = replace(  # type: ignore[attr-defined]
            provider.descriptor, provider_version="v2"
        )
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF039_PROVIDER_DESCRIPTOR_DRIFT"
        ):
            program.materialize(
                target={"target": "cpu"}, toolchain={"version": 1}
            )

    def test_provider_cannot_self_assert_wrong_target_identity(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        provider = ExternalConformanceProvider(plan, artifacts)
        provider.corrupt_target_identity = True
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF015_EXECUTABLE_IDENTITY"
        ):
            compile_generic_family_program(
                plan, provider, artifacts=artifacts
            ).materialize(
                target={"target": "cpu"}, toolchain={"version": 1}
            )

    def test_materialized_identity_is_snapshotted_and_drift_rejected(self) -> None:
        plan = _plan()
        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        original = materialized.identity
        materialized._handle._identity = replace(  # type: ignore[attr-defined]
            original, executable_sha256="f" * 64
        )
        self.assertEqual(materialized.identity, original)
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF033_EXECUTABLE_IDENTITY_DRIFT"
        ):
            materialized.prepare({"static": []})
        self.assertEqual(materialized.state, "failed")

    def test_execution_envelope_identity_mismatch_is_rejected(self) -> None:
        plan = _plan()
        prepared = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        ).prepare(
            {"static": []}
        )
        prepared._handle._plan_sha256 = "f" * 64  # type: ignore[attr-defined]
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF022_EXECUTION_IDENTITY"
        ):
            prepared.execute({"value": 3})
        prepared.close()

    def test_execution_envelope_cannot_pair_error_with_output(self) -> None:
        plan = _plan()
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF010_STATUS"):
            FamilyProviderExecutionV1(
                plan.plan_sha256,
                "1" * 64,
                "ERROR",
                17,
                {"forbidden": True},
                _sha("forbidden"),
                {},
            )

    def test_provider_receipts_require_canonical_mappings(self) -> None:
        plan = _plan()
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF021_EXECUTION_ENVELOPE"
        ):
            FamilyProviderExecutionV1(
                plan.plan_sha256,
                "1" * 64,
                "ERROR",
                17,
                None,
                None,
                [],  # type: ignore[arg-type]
            )

        prepared = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        ).prepare(
            {"static": []}
        )
        with patch.object(
            type(prepared._handle),  # type: ignore[attr-defined]
            "lifecycle_receipt",
            new_callable=PropertyMock,
            return_value=[],
        ), self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF021_EXECUTION_ENVELOPE"
        ):
            _ = prepared.lifecycle_receipt
        prepared.close()

    def test_materialized_prepare_is_single_use(self) -> None:
        plan = _plan()
        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        prepared = materialized.prepare({"static": []})
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF018_STATE"):
            materialized.prepare({"static": []})
        prepared.close()

    def test_cross_thread_operations_fail_before_provider_use(self) -> None:
        plan = _plan()
        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        errors: list[Exception] = []

        def cross_thread_prepare() -> None:
            try:
                materialized.prepare({"static": []})
            except Exception as exc:  # Expected hostile call.
                errors.append(exc)

        worker = threading.Thread(target=cross_thread_prepare)
        worker.start()
        worker.join(timeout=2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], GenericFamilyLifecycleError)
        self.assertEqual(errors[0].code, "GF017_THREAD_AFFINITY")
        prepared = materialized.prepare({"static": []})

        errors.clear()

        def cross_thread_receipt() -> None:
            try:
                _ = prepared.lifecycle_receipt
            except Exception as exc:  # Expected hostile call.
                errors.append(exc)

        worker = threading.Thread(target=cross_thread_receipt)
        worker.start()
        worker.join(timeout=2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "GF017_THREAD_AFFINITY")
        prepared.close()

    def test_recursive_prepare_and_execute_fail_instead_of_deadlocking(self) -> None:
        plan = _plan()
        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        materialized._handle.prepare = (  # type: ignore[method-assign]
            lambda static_input: materialized.prepare(static_input)
        )
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF020_REENTRANT"):
            materialized.prepare({"static": []})
        self.assertEqual(materialized.state, "failed")

        materialized = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        )
        prepared = materialized.prepare({"static": []})
        original_execute = prepared._handle.execute  # type: ignore[attr-defined]
        prepared._handle.execute = (  # type: ignore[method-assign]
            lambda batch: prepared.execute(batch)
        )
        with self.assertRaisesRegex(GenericFamilyLifecycleError, "GF020_REENTRANT"):
            prepared.execute({"value": 5})
        prepared._handle.execute = original_execute  # type: ignore[method-assign]
        self.assertEqual(prepared.execute({"value": 6}).output["value"], 6)
        prepared.close()

    def test_execution_result_and_receipts_are_read_only(self) -> None:
        plan = _plan()
        prepared = _external_program(plan).materialize(
            target={"target": "cpu"}, toolchain={"version": 1}
        ).prepare(
            {"static": [1, 2]}
        )
        result = prepared.execute({"value": 7})
        with self.assertRaises(TypeError):
            result.output["value"] = 8
        with self.assertRaises(TypeError):
            result.traversal_receipt["execution_count"] = 9
        with self.assertRaises(TypeError):
            prepared.lifecycle_receipt["process_bound"] = False
        prepared.close()

    def test_provider_failure_exposes_no_output(self) -> None:
        plan = _plan()
        artifacts = _artifacts(plan)
        provider = ExternalConformanceProvider(plan, artifacts)
        prepared = compile_generic_family_program(
            plan, provider, artifacts=artifacts
        ).materialize(
            target={"target": "cpu"}, toolchain={"toolchain": "reference"}
        ).prepare({"static": []})
        with self.assertRaisesRegex(
            GenericFamilyLifecycleError, "GF023_PROVIDER_STATUS"
        ):
            prepared.execute({"fail": True})
        prepared.close()

    def test_generic_core_has_no_concrete_or_application_dispatch(self) -> None:
        for relative in (
            "src/rtdsl/v4_family_schema.py",
            "src/rtdsl/v4_generic_family_lifecycle.py",
            "src/rtdsl/v4_family.py",
        ):
            source = (ROOT / relative).read_text("utf-8").lower()
            for forbidden in (
                "bounded_relation",
                "triangle_reduction",
                "owner_grouped",
                "custom_aabb",
                "builtin_triangle",
                "curve",
                "sphere",
                "collision",
                "raydb",
            ):
                with self.subTest(relative=relative, forbidden=forbidden):
                    self.assertNotIn(forbidden, source)

    def test_external_provider_uses_only_additive_public_family_api(self) -> None:
        fixture = ROOT / "tests/fixtures/goal5838_external_provider.py"
        self.assertFalse(fixture.is_relative_to(ROOT / "src/rtdsl"))
        source = fixture.read_text("utf-8")
        self.assertIn("from rtdsl.v4_family import", source)
        self.assertNotIn("v4_generic_family_lifecycle", source)


if __name__ == "__main__":
    unittest.main()
