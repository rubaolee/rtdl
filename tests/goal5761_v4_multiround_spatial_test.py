from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

from rtdsl.v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract
from rtdsl.v4_multiround_spatial import (
    DistanceWindowBoundaryPolicy,
    MultiRoundSpatialError,
    MultiRoundSpatialSchema,
    MultiRoundTelemetry,
    bounded_radius_schedule,
    expected_radius_candidates,
    product_source_has_forbidden_identity_dispatch,
    radius_graph_components_partner,
    ranked_distance_window_partner,
    validate_multiround_telemetry,
    verify_multiround_spatial_schema,
)
from rtdsl.v4_multiround_spatial_optix_wrapper_codegen import (
    generate_trusted_multiround_spatial_wrapper_v1,
)
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from scripts.goal5761_m3_spatial_fixtures import (
    SPATIAL_CANDIDATE_SOURCE,
    compile_callback,
    physical_schema,
)


ROOT = Path(__file__).resolve().parents[1]


def _compiled(*, capacity=4096, maximum_rounds=8):
    callback = compile_callback()
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256="a" * 64,
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256,
        callback.effect_digest,
        physical.schema.schema_sha256,
        capacity,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256="b" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )
    abi = compile_callback_abi(
        callback,
        any_hit_proof_authority=proof,
        physical_schema_authority=physical,
    )
    relation_contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    schema = MultiRoundSpatialSchema(
        relation_schema_sha256=relation.schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        maximum_rounds=maximum_rounds,
        maximum_event_capacity=capacity,
    )
    authority = verify_multiround_spatial_schema(
        relation, relation_contract, abi, schema,
        any_hit_proof_authority=proof)
    return authority, proof


class Goal5761MultiRoundSpatialTests(unittest.TestCase):
    def test_goal5757_freeze_verifier_accepts_exact_m3_successor_chain(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/goal5757_verify_core_freeze.py")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(
            completed.returncode, 0,
            f"stdout={completed.stdout}\nstderr={completed.stderr}")
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertTrue(any(
            "goal5761" in path for path in payload["successor_manifests"]
        ))

    def test_frozen_rtnn_prose_conflict_is_append_only_and_mechanically_bound(self):
        reconciliation_path = ROOT / (
            "history/internal_docs/"
            "goal5761_preimplementation_rtnn_contract_reconciliation_20260812.json")
        record = json.loads(reconciliation_path.read_text())
        for key in ("base_freeze", "pinned_rtnn_source"):
            item = record[key]
            data = (ROOT / item["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
        source = (ROOT / record["pinned_rtnn_source"]["path"]).read_text()
        self.assertIn(
            "if float(min_distance) < distance < float(max_distance):", source)
        self.assertEqual(
            record["resolution"]["distance_boundary_policy"],
            DistanceWindowBoundaryPolicy.OPEN.value)
        self.assertFalse(record["finding"]["base_freeze_changed"])

    def test_schema_requires_declared_refit_and_exact_closed_algebras(self):
        authority, proof = _compiled()
        self.assertEqual(
            authority.relation.physical.schema.gas.update_policy.value,
            "declared_refit")
        with self.assertRaisesRegex(MultiRoundSpatialError, "maximum_rounds"):
            verify_multiround_spatial_schema(
                authority.relation, authority.relation_contract, authority.abi,
                dataclasses.replace(authority.schema, maximum_rounds=0),
                any_hit_proof_authority=proof)
        with self.assertRaisesRegex(MultiRoundSpatialError, "capacity_binding"):
            verify_multiround_spatial_schema(
                authority.relation, authority.relation_contract, authority.abi,
                dataclasses.replace(
                    authority.schema,
                    maximum_event_capacity=authority.relation.schema.capacity + 1),
                any_hit_proof_authority=proof)

    def test_wrapper_is_app_neutral_true_optix_and_u32_identity_safe(self):
        authority, proof = _compiled()
        wrapper = generate_trusted_multiround_spatial_wrapper_v1(
            authority.relation, authority.relation_contract, authority.abi,
            any_hit_proof_authority=proof)
        for required in (
            "optixTrace", "optixReportIntersection", "optixGetAttribute_0()",
            "optixIgnoreIntersection();",
            "isect_out_hit_hit_kind != 0u", "params.event_capacity + 1ull",
            "__raygen__rtdl_v4_multiround_spatial",
        ):
            self.assertIn(required, wrapper.source)
        self.assertNotIn("primitive.item_id, attributes", SPATIAL_CANDIDATE_SOURCE)
        for forbidden in ("rtnn", "dbscan", "paper", "application_id"):
            self.assertNotIn(forbidden, wrapper.source.lower())

    def test_ranked_distance_partner_matches_independent_all_pairs(self):
        search = np.asarray([
            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 2.0, 0.0),
            (3.0, 0.0, 0.0), (1.0, 1.0, 0.0),
        ], dtype=np.float32)
        queries = np.asarray([(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)], dtype=np.float32)
        candidates = expected_radius_candidates(search, queries, 4.0)
        actual = ranked_distance_window_partner(
            search, queries, candidates, k=3,
            minimum_distance=0.0, maximum_distance=4.0)
        expected = []
        for qid, query in enumerate(queries):
            values = []
            for iid, item in enumerate(search):
                delta = np.subtract(query, item, dtype=np.float32)
                squared = np.multiply(delta, delta, dtype=np.float32)
                d2 = np.add(np.add(squared[0], squared[1], dtype=np.float32),
                            squared[2], dtype=np.float32)
                distance = np.sqrt(d2, dtype=np.float32)
                if 0.0 < float(distance) < 4.0:
                    values.append((distance, iid))
            for rank, (distance, iid) in enumerate(
                    sorted(values, key=lambda row: (float(row[0]), row[1]))[:3], 1):
                expected.append((qid, iid, rank, float(np.multiply(
                    distance, distance, dtype=np.float32))))
        self.assertEqual(actual, tuple(expected))

    def test_distance_boundary_policy_is_explicit_closed_vocabulary(self):
        search = np.asarray([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)], dtype=np.float32)
        query = np.asarray([(0.0, 0.0, 0.0)], dtype=np.float32)
        candidates = ((0, 0), (0, 1))
        opened = ranked_distance_window_partner(
            search, query, candidates, k=2, minimum_distance=0.0,
            maximum_distance=1.0,
            boundary_policy=DistanceWindowBoundaryPolicy.OPEN)
        closed = ranked_distance_window_partner(
            search, query, candidates, k=2, minimum_distance=0.0,
            maximum_distance=1.0,
            boundary_policy=DistanceWindowBoundaryPolicy.CLOSED)
        self.assertEqual(opened, ())
        self.assertEqual(tuple(row[1] for row in closed), (0, 1))
        with self.assertRaisesRegex(MultiRoundSpatialError, "boundary_policy"):
            ranked_distance_window_partner(
                search, query, candidates, k=2, minimum_distance=0.0,
                maximum_distance=1.0, boundary_policy="open")

    def test_radius_component_partner_is_separate_typed_algebra(self):
        points = np.asarray([
            (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 0.0, 0.0),
            (8.0, 0.0, 0.0), (8.4, 0.0, 0.0), (20.0, 0.0, 0.0),
        ], dtype=np.float32)
        candidates = expected_radius_candidates(points, points, 1.0)
        result = radius_graph_components_partner(
            points, candidates, epsilon=1.0, min_points=2)
        self.assertEqual(result["neighbor_counts"], (3, 3, 3, 2, 2, 1))
        self.assertEqual(result["core_flags"], (True, True, True, True, True, False))
        self.assertEqual(result["canonical_component_labels"], (0, 0, 0, 1, 1, -1))

    def test_round_schedule_is_bounded_and_exhaustion_fails_closed(self):
        self.assertEqual(
            bounded_radius_schedule(
                initial_radius=0.5, maximum_radius=4.0, maximum_rounds=4),
            (0.5, 1.0, 2.0, 4.0))
        with self.assertRaisesRegex(MultiRoundSpatialError, "round_bound_exhausted"):
            bounded_radius_schedule(
                initial_radius=0.5, maximum_radius=8.0, maximum_rounds=4)

    def test_lifecycle_proof_requires_one_build_and_refit_per_changed_round(self):
        valid = MultiRoundTelemetry(
            prepared_token=4, gas_build_count=1, gas_refit_count=2,
            launch_count=3, traversable_handle_first=77,
            traversable_handle_last=77, radii=(1.0, 2.0, 4.0))
        validate_multiround_telemetry(valid, expected_rounds=3)
        with self.assertRaisesRegex(MultiRoundSpatialError, "gas_build_count"):
            validate_multiround_telemetry(
                dataclasses.replace(valid, gas_build_count=3), expected_rounds=3)

    def test_product_sources_have_no_app_identity_dispatch(self):
        paths = (
            ROOT / "src/rtdsl/v4_multiround_spatial.py",
            ROOT / "src/rtdsl/v4_multiround_spatial_optix_wrapper_codegen.py",
            ROOT / "src/rtdsl/v4_multiround_spatial_optix_compiler.py",
            ROOT / "src/rtdsl/v4_multiround_spatial_optix_runtime.py",
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        )
        for path in paths:
            self.assertFalse(
                product_source_has_forbidden_identity_dispatch(path.read_text()),
                str(path))

    def test_native_has_generic_prepared_owner_and_no_app_named_symbols(self):
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()
        implementation = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        for symbol in (
            "rtdl_optix_v4_prepare_multiround_spatial_callback_v1",
            "rtdl_optix_v4_execute_multiround_spatial_callback_v1",
            "rtdl_optix_v4_destroy_multiround_spatial_callback_v1",
        ):
            self.assertEqual(api.count(symbol), 1)
        self.assertIn("OPTIX_BUILD_FLAG_ALLOW_UPDATE", implementation)
        self.assertIn("refit_custom_accel_with_flags", implementation)
        self.assertIn("gas_refit_count += 1", implementation)


if __name__ == "__main__":
    unittest.main()
