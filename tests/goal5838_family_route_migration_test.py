from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from rtdsl.v4_callback_lifecycle import (
    AnyHitProtocolProof,
    BoundedRelationBatch,
    BoundedRelationProtocol,
    BoundedRelationStaticInput,
    MaterializedProtocolProgram,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    V4Target,
    V4Toolchain,
    standard_protocol_physical_plan,
)
from rtdsl.v4_curve_owner_grouped_any_hit_public import (
    OwnerGroupedCurveQueryBatch,
    OwnerGroupedCurveStaticInput,
    V4CurveTarget,
)
from rtdsl.v4_family_route_adapters import (
    bounded_relation_family_route,
    curve_owner_grouped_any_hit_family_route,
    triangle_reduction_family_route,
)
from rtdsl.v4_owner_grouped_any_hit import (
    OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA,
    owner_grouped_any_hit_output_sha256,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _proof(protocol, label: str) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        plan.callback_ir_sha256,
        plan.effect_digest,
        _sha(label),
        "external_machine_checked_order_independence_v1",
    )


class _FakeLegacyPrepared:
    def __init__(self, output: object, traversal_receipt: dict[str, object]) -> None:
        self.output = output
        self.traversal_receipt = traversal_receipt
        self.execution_count = 0
        self.close_count = 0

    @property
    def lifecycle_receipt(self):
        return {
            "schema": "rtdl.test.legacy_lifecycle.v1",
            "execution_count": self.execution_count,
        }

    def execute(self, _batch):
        self.execution_count += 1
        return SimpleNamespace(
            output=self.output,
            output_sha256=_digest(self.output),
            traversal_receipt=self.traversal_receipt,
        )

    def close(self):
        self.close_count += 1


class _FakeOwnerPrepared:
    def __init__(self, **_kwargs) -> None:
        self.execution_count = 0
        self.close_count = 0

    @property
    def lifecycle_receipt(self):
        return {
            "schema": "rtdl.test.owner_lifecycle.v1",
            "execution_count": self.execution_count,
        }

    def execute(self, _queries):
        self.execution_count += 1
        output = {
            "schema": OWNER_GROUPED_ANY_HIT_OUTPUT_SCHEMA,
            "owner_hit_bits": (1, 0, 1),
        }
        return SimpleNamespace(
            owner_hit_bits=(1, 0, 1),
            output_sha256=_digest(output),
            traversal_receipt={
                "physical_executor_classification": "optix_traversal_observed",
                "execution_count": self.execution_count,
            },
        )

    def close(self):
        self.close_count += 1


class Goal5838FamilyRouteMigrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.native = root / "librtdl_optix.so"
        self.native.write_bytes(b"goal5838-route-migration-native")
        self.optix = root / "optix"
        self.cuda = root / "cuda"
        self.optix.mkdir()
        self.cuda.mkdir()
        self.target = V4Target.from_native(
            self.native,
            optix_sdk="9.0.0",
            compute_capability=(8, 9),
        )
        self.curve_target = V4CurveTarget.from_native(
            self.native,
            optix_sdk="9.0.0",
            compute_capability="8.9",
        )
        self.toolchain = V4Toolchain(
            compute_capability=(8, 9),
            optix_include=self.optix,
            cuda_include=self.cuda,
            expected_python_version="3.12.0",
            expected_numba_version="test",
            expected_numpy_version="test",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _executable(label: str):
        return SimpleNamespace(
            executable_sha256=_sha(f"{label}:executable"),
            composed=SimpleNamespace(ptx_sha256=_sha(f"{label}:ptx")),
        )

    def test_two_stable_routes_and_successor_have_declarative_plans(self) -> None:
        bounded_protocol = BoundedRelationProtocol(16, 0.25)
        weighted_protocol = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT
        )
        all_protocol = TriangleReductionProtocol(
            TriangleReductionMode.ALL_HIT_COUNT
        )
        bounded = bounded_relation_family_route(
            bounded_protocol, _proof(bounded_protocol, "bounded")
        )
        weighted = triangle_reduction_family_route(
            weighted_protocol, _proof(weighted_protocol, "weighted")
        )
        all_hits = triangle_reduction_family_route(
            all_protocol, _proof(all_protocol, "all")
        )
        owner = curve_owner_grouped_any_hit_family_route()

        self.assertEqual(bounded.classification, "stable_constructor")
        self.assertEqual(weighted.classification, "stable_constructor")
        self.assertEqual(all_hits.classification, "stable_constructor")
        self.assertEqual(owner.classification, "closed_successor")
        self.assertEqual(
            weighted.plan.to_dict()["family_shape_sha256"],
            all_hits.plan.to_dict()["family_shape_sha256"],
        )
        self.assertNotEqual(weighted.plan.plan_sha256, all_hits.plan.plan_sha256)
        self.assertEqual(len({
            bounded.plan.to_dict()["family_shape_sha256"],
            weighted.plan.to_dict()["family_shape_sha256"],
            owner.plan.to_dict()["family_shape_sha256"],
        }), 3)
        for route in (bounded, weighted, all_hits, owner):
            compiled = route.compile()
            self.assertEqual(compiled.plan.plan_sha256, route.plan.plan_sha256)

    def test_generic_family_front_door_is_on_additive_public_api(self) -> None:
        import rtdsl.v4_family as v4_family

        for name in (
            "FamilyArtifactV1",
            "FamilySchemaV1",
            "FamilyProgramArtifactsV1",
            "ProtocolInstanceV1",
            "FamilyProviderV1",
            "bind_family_program_artifacts",
            "compile_generic_family_program",
        ):
            self.assertIn(name, v4_family.__all__)
            self.assertIsNotNone(getattr(v4_family, name))

        public_source = Path(v4_family.__file__).read_text(encoding="utf-8")
        for concrete_word in ("bounded_relation", "triangle_reduction", "owner_grouped"):
            self.assertNotIn(concrete_word, public_source)

    def test_provider_is_exactly_plan_bound(self) -> None:
        bounded_protocol = BoundedRelationProtocol(8)
        triangle_protocol = TriangleReductionProtocol()
        bounded = bounded_relation_family_route(
            bounded_protocol, _proof(bounded_protocol, "bounded")
        )
        triangle = triangle_reduction_family_route(
            triangle_protocol, _proof(triangle_protocol, "triangle")
        )
        with self.assertRaisesRegex(ValueError, "different family plan"):
            bounded.provider.project(triangle.plan, triangle.artifacts)

    def test_route_plans_are_deterministic_and_target_neutral(self) -> None:
        bounded_protocol = BoundedRelationProtocol(12, 0.125)
        triangle_protocol = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT
        )
        constructors = (
            lambda: bounded_relation_family_route(
                bounded_protocol, _proof(bounded_protocol, "deterministic-bounded")
            ),
            lambda: triangle_reduction_family_route(
                triangle_protocol, _proof(triangle_protocol, "deterministic-triangle")
            ),
            curve_owner_grouped_any_hit_family_route,
        )
        forbidden_deployment_keys = {
            "compute_capability",
            "executable_sha256",
            "generated_artifact_sha256",
            "provider_artifact_sha256",
            "optix_sdk",
            "ptx_sha256",
            "target_sha256",
            "toolchain_sha256",
        }

        def keys(value: object) -> set[str]:
            if isinstance(value, dict):
                return set(value) | set().union(*(keys(item) for item in value.values()))
            if isinstance(value, list):
                return set().union(*(keys(item) for item in value))
            return set()

        for constructor in constructors:
            with self.subTest(constructor=constructor):
                first = constructor()
                second = constructor()
                self.assertEqual(first.plan.canonical_bytes, second.plan.canonical_bytes)
                self.assertEqual(first.plan.plan_sha256, second.plan.plan_sha256)
                self.assertTrue(
                    forbidden_deployment_keys.isdisjoint(keys(first.plan.to_dict()))
                )

    def test_family_parameters_change_instance_not_shape(self) -> None:
        first_protocol = BoundedRelationProtocol(8, 0.0)
        second_protocol = BoundedRelationProtocol(32, 0.25)
        first = bounded_relation_family_route(
            first_protocol, _proof(first_protocol, "parameterized-bounded")
        )
        second = bounded_relation_family_route(
            second_protocol, _proof(second_protocol, "parameterized-bounded")
        )
        self.assertEqual(
            first.plan.to_dict()["family_shape_sha256"],
            second.plan.to_dict()["family_shape_sha256"],
        )
        self.assertNotEqual(
            first.plan.to_dict()["protocol_instance_sha256"],
            second.plan.to_dict()["protocol_instance_sha256"],
        )
        self.assertNotEqual(first.plan.plan_sha256, second.plan.plan_sha256)

    def test_routes_transport_full_identity_bound_program_artifacts(self) -> None:
        bounded_protocol = BoundedRelationProtocol(8)
        triangle_protocol = TriangleReductionProtocol()
        routes = (
            bounded_relation_family_route(
                bounded_protocol, _proof(bounded_protocol, "artifact-bounded")
            ),
            triangle_reduction_family_route(
                triangle_protocol, _proof(triangle_protocol, "artifact-triangle")
            ),
            curve_owner_grouped_any_hit_family_route(),
        )
        expected_ids = {
            "rtdl.behavior.schema",
            "rtdl.callback.abi",
            "rtdl.callback.program",
            "rtdl.callback.verification",
        }
        for route in routes:
            with self.subTest(plan=route.plan.plan_sha256):
                self.assertEqual(route.artifacts.plan_sha256, route.plan.plan_sha256)
                self.assertEqual(
                    {row.artifact_id for row in route.artifacts.artifacts},
                    expected_ids,
                )
                program = json.loads(
                    route.artifacts.artifact("rtdl.callback.program").payload
                )
                abi = json.loads(route.artifacts.artifact("rtdl.callback.abi").payload)
                self.assertEqual(
                    hashlib.sha256(program["normalized_source"].encode("utf-8")).hexdigest(),
                    route.artifacts.callback_source_sha256,
                )
                self.assertEqual(
                    program["source_sha256"], route.artifacts.callback_source_sha256
                )
                self.assertEqual(
                    abi["callback_ir_sha256"], route.artifacts.callback_ir_sha256
                )
                self.assertEqual(
                    abi["callback_effect_digest"], route.artifacts.effect_digest
                )
                self.assertEqual(abi["abi_sha256"], route.artifacts.abi_sha256)

    def test_bounded_route_runs_through_generic_public_lifecycle(self) -> None:
        protocol = BoundedRelationProtocol(8)
        route = bounded_relation_family_route(
            protocol, _proof(protocol, "bounded")
        )
        executable = self._executable("bounded")
        old_prepared = _FakeLegacyPrepared(
            ((100, 10), (101, 20)),
            {"physical_executor_classification": "optix_traversal_observed"},
        )
        with patch(
            "rtdsl.v4_bounded_relation_optix_compiler."
            "compile_verified_bounded_relation_executable",
            return_value=(executable, "compiler log"),
        ), patch.object(
            MaterializedProtocolProgram,
            "prepare",
            return_value=old_prepared,
        ):
            materialized = route.compile().materialize(
                target=self.target, toolchain=self.toolchain
            )
            prepared = materialized.prepare(BoundedRelationStaticInput(()))
            result = prepared.execute(BoundedRelationBatch(()))
        self.assertEqual(result.output, ((100, 10), (101, 20)))
        self.assertEqual(
            result.executable_identity_sha256,
            materialized.identity.identity_sha256,
        )
        prepared.close()
        prepared.close()
        self.assertEqual(old_prepared.close_count, 1)

    def test_triangle_route_runs_through_same_generic_public_lifecycle(self) -> None:
        protocol = TriangleReductionProtocol(
            TriangleReductionMode.WEIGHTED_HIT_COUNT
        )
        route = triangle_reduction_family_route(
            protocol, _proof(protocol, "triangle")
        )
        executable = self._executable("triangle")
        old_prepared = _FakeLegacyPrepared(
            16,
            {"physical_executor_classification": "optix_traversal_observed"},
        )
        static = TriangleReductionStaticInput(
            vertices=((0.0, 0.0, 1.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)),
            triangles=((0, 1, 2),),
            primitive_metadata={},
        )
        batch = TriangleReductionBatch(
            queries=(((0.1, 0.1, 0.0), (0.0, 0.0, 1.0), 4.0),),
            query_metadata={"query.weight": (16,)},
        )
        with patch(
            "rtdsl.v4_triangle_reduction_optix_compiler."
            "compile_verified_triangle_reduction_executable",
            return_value=(executable, "compiler log"),
        ), patch.object(
            MaterializedProtocolProgram,
            "prepare",
            return_value=old_prepared,
        ):
            prepared = route.compile().materialize(
                target=self.target, toolchain=self.toolchain
            ).prepare(static)
            result = prepared.execute(batch)
        self.assertEqual(result.output, 16)
        prepared.close()

    def test_owner_grouped_successor_runs_through_generic_public_lifecycle(self) -> None:
        route = curve_owner_grouped_any_hit_family_route()
        executable = self._executable("owner")
        static = OwnerGroupedCurveStaticInput(
            control_points=((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
            widths=(0.1, 0.1),
            segment_indices=(0,),
            owner_ids=(0,),
            owner_count=3,
        )
        batch = OwnerGroupedCurveQueryBatch((
            ((0.5, -1.0, 0.0), (0.5, 1.0, 0.0)),
        ))
        with patch(
            "rtdsl.v4_curve_owner_grouped_any_hit_public."
            "compile_verified_curve_owner_grouped_any_hit_executable",
            return_value=(executable, "compiler log"),
        ), patch(
            "rtdsl.v4_curve_owner_grouped_any_hit_public."
            "PreparedCurveOwnerGroupedAnyHit",
            _FakeOwnerPrepared,
        ):
            prepared = route.compile().materialize(
                target=self.curve_target, toolchain=self.toolchain
            ).prepare(static)
            result = prepared.execute(batch)
        self.assertEqual(result.output["owner_hit_bits"], (1, 0, 1))
        self.assertEqual(
            result.output_sha256,
            owner_grouped_any_hit_output_sha256((1, 0, 1)),
        )
        prepared.close()


if __name__ == "__main__":
    unittest.main()
