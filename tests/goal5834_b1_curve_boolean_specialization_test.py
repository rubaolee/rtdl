"""Goal5834-B1 fixed Boolean curve specialization regressions."""

from __future__ import annotations

import ctypes
from dataclasses import replace
import hashlib
import inspect
import os
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_builtin_curve_standard_library import (  # noqa: E402
    CURVE_ANY_CONTACT_BOOLEAN_SOURCE,
    build_curve_any_contact_boolean_authority,
    build_curve_first_contact_authority,
    curve_any_contact_boolean_manifest,
)
from rtdsl.v4_curve import (  # noqa: E402
    CurveBooleanSegmentBatch,
    V4CurveTarget,
    curve_any_contact_boolean_source,
)
from rtdsl.v4_curve_physical_schema import (  # noqa: E402
    BUILTIN_CURVE_BOOLEAN_TEMPLATE,
    BuiltinCurveBooleanPhysicalSchema,
    CurvePhysicalSchemaError,
    CurveTargetProfile,
    verify_builtin_curve_physical_schema,
    verify_curve_boolean_motion_segments,
)
from rtdsl.v4_public_builtin_curve import (  # noqa: E402
    PublicCurveLifecycleError,
    verify_builtin_curve_boolean_callback_source,
)
from rtdsl import v4_curve_prepared_runtime as runtime  # noqa: E402


def _target(native_sha: str = "1" * 64) -> CurveTargetProfile:
    return CurveTargetProfile("optix", "9.0.0", "8.9", native_sha)


def _boolean_authority():
    return build_curve_any_contact_boolean_authority(_target())


class Goal5834B1CurveBooleanSpecializationTest(unittest.TestCase):
    def test_fixed_public_boolean_source_compiles_without_native_rewrite(self):
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"goal5834-b1-native-identity")
            target = V4CurveTarget.from_native(
                native, optix_sdk="9.0.0", compute_capability="8.9")
            program = curve_any_contact_boolean_source().compile(target=target)
        self.assertIsInstance(
            program.authority.schema, BuiltinCurveBooleanPhysicalSchema)
        self.assertEqual(
            program.authority.canonical_plan.template_id,
            BUILTIN_CURVE_BOOLEAN_TEMPLATE)
        self.assertEqual(len(program.abi.roles), 4)
        self.assertIn("__raygen__rtdl_v4_curve", program.wrapper.source)
        self.assertIn("unsigned int payload_1 = 0u;", program.wrapper.source)
        self.assertIn("unsigned int payload_2 = 0u;", program.wrapper.source)
        self.assertIn("params.output_1[query]=0u;", program.wrapper.source)
        self.assertIn("params.output_2[query]=0u;", program.wrapper.source)
        self.assertNotIn("__intersection__", program.wrapper.source)

        # The shared-wrapper refactor must preserve the old First Contact bytes.
        _authority, _abi, old_wrapper = build_curve_first_contact_authority(
            _target())
        self.assertEqual(
            old_wrapper.source_sha256,
            "f014546e135b1645175f5d55723e23a44850ac192219f070b5b42893e63316a6")

    def test_boolean_query_verifier_is_structural_only(self):
        signature = inspect.signature(verify_curve_boolean_motion_segments)
        self.assertEqual(tuple(signature.parameters), ("starts", "ends"))
        source = inspect.getsource(verify_curve_boolean_motion_segments)
        for forbidden in (
                "control_points", "segment_indices",
                "_segment_segment_distance2", "_capsule_entry"):
            self.assertNotIn(forbidden, source)
        # Start-inside and parallel geometry are not computed here.
        rows = verify_curve_boolean_motion_segments(
            ((0.0, 0.0, 0.0),), ((1.0, 0.0, 0.0),))
        self.assertEqual(rows, ((0.0, 0.0, 0.0, 1.0, 0.0, 0.0),))
        with self.assertRaises(CurvePhysicalSchemaError):
            verify_curve_boolean_motion_segments(
                ((0.0, 0.0, 0.0),), ((0.0, 0.0, 0.0),))
        with self.assertRaises(PublicCurveLifecycleError):
            CurveBooleanSegmentBatch((((0, 0, 0), (1, 0, 0), (2, 0, 0)),))

    def test_every_boolean_schema_leaf_is_decision_bearing(self):
        authority, _abi, _wrapper = _boolean_authority()
        good = authority.schema
        mutations = {
            "callback_ir_sha256": "0" * 64,
            "effect_digest": "0" * 64,
            "control_point_field_id": "different_control_points",
            "width_field_id": "different_widths",
            "segment_index_field_id": "different_indices",
            "application_id_field_id": "different_ids",
            "query_field_id": "different_queries",
            "output_field_id": "different_outputs",
            "status_field_id": "different_status",
            "contract_name": "different_contract",
            "template_id": "different_template",
            "geometry_family": "different_family",
            "curve_type": "round_quadratic",
            "endcap_policy": "flat",
            "width_policy": "tapered",
            "gas_update_policy": "updateable",
            "graph_depth": 2,
            "sbt_record_count": 2,
            "motion_blur": True,
            "primitive_index_offset": 1,
            "stable_order": ("application_id",),
            "numeric_policy_id": "different_numeric_policy",
            "admission_mode": "pairwise_geometry",
            "provider_semantics": "mathematical_capsule_theorem",
            "control_points_buffer_contract": "different",
            "widths_buffer_contract": "different",
            "segment_indices_buffer_contract": "different",
            "application_ids_buffer_contract": "different",
            "queries_buffer_contract": "different",
            "outputs_buffer_contract": "different",
            "semantic_output_contract": "different",
            "status_buffer_contract": "different",
            "hidden_hit_channel_contract": "different",
            "schema_id": "different_schema",
            "schema_version": "v2",
        }
        self.assertEqual(set(mutations), set(good.__dataclass_fields__))
        for field, value in mutations.items():
            with self.subTest(field=field), self.assertRaises(
                    CurvePhysicalSchemaError):
                verify_builtin_curve_physical_schema(
                    authority.callback, replace(good, **{field: value}),
                    target=authority.target)

    def test_boolean_callback_delta_leaves_are_fixed(self):
        manifest = curve_any_contact_boolean_manifest()
        mutations = (
            ("updated = AnyContactPayload(hit=ONE_U32)",
             "updated = AnyContactPayload(hit=ZERO_U32)"),
            ("return optix.payload(payload=payload)",
             "return optix.payload(payload=AnyContactPayload(hit=ONE_U32))"),
            ("result = AnyContactOutput(hit=payload.hit)",
             "result = AnyContactOutput(hit=ONE_U32)"),
        )
        for old, new in mutations:
            mutated = CURVE_ANY_CONTACT_BOOLEAN_SOURCE.replace(old, new, 1)
            self.assertNotEqual(mutated, CURVE_ANY_CONTACT_BOOLEAN_SOURCE)
            with self.subTest(old=old), self.assertRaisesRegex(
                    PublicCurveLifecycleError, "GCB006_FIXED_SOURCE"):
                verify_builtin_curve_boolean_callback_source(mutated, manifest)

    @staticmethod
    def _fake_owner() -> runtime.PreparedBuiltinCurveOwner:
        owner = runtime.PreparedBuiltinCurveOwner.__new__(
            runtime.PreparedBuiltinCurveOwner)
        owner._closed = False
        owner._pid = os.getpid()
        owner._thread = threading.get_ident()
        owner._active = threading.Lock()
        owner._token = 13
        owner._execution_count = 0
        owner._native_sha = "a" * 64
        owner._ptx_sha = "b" * 64
        owner._physical_receipt = {"status_before_output": True}
        owner._last_failure_receipt = None
        owner._control_points = ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        owner._widths = (0.25, 0.25)
        owner._segment_indices = (0,)
        owner._application_ids = (7,)
        owner._fresh = SimpleNamespace(
            authority_nonce="nonce", target=SimpleNamespace())
        owner._plan = SimpleNamespace(plan_sha256="c" * 64)
        owner._abi = SimpleNamespace(abi_sha256="d" * 64)
        owner._library = object()
        owner._describe = object()
        owner._descriptor = {}
        owner._boolean_mode = True
        return owner

    def test_runtime_seals_raw_gpu_bits_then_host_or(self):
        owner = self._fake_owner()

        def execute(
            _token, _starts, _ends, count, output_0, output_1, output_2,
            observed_primitive, observed_kind, observed_t, _statuses,
            counters, _error, _capacity,
        ):
            self.assertEqual(count, 2)
            output_0[0] = 1; output_1[0] = 0; output_2[0] = 0
            output_0[1] = 0; output_1[1] = 0; output_2[1] = 0
            observed_primitive[0] = 0; observed_kind[0] = 0
            observed_primitive[1] = 0xFFFFFFFF
            observed_kind[1] = 0xFFFFFFFF
            observed_t[0] = ctypes.c_float(0.5).value
            counters[0] = 2
            return 0

        owner._execute = execute
        receipt = {"physical_executor_classification": "optix_traversal_observed"}
        audit = SimpleNamespace(
            finish=mock.Mock(return_value=receipt), abort=mock.Mock())
        queries = (
            ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
            ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        )
        with mock.patch.object(
                runtime.OptixTraversalAuditSession, "open",
                return_value=audit), mock.patch.object(
                    runtime, "validate_traversal_receipt"), mock.patch.object(
                    runtime, "_read_native_descriptor", return_value={}), \
                mock.patch.object(runtime, "_require_descriptor_transition"), \
                mock.patch.object(runtime, "_require_native_target_binding"), \
                mock.patch.object(runtime, "_require_execution_fingerprints"):
            result = owner.execute(queries)
        self.assertEqual(result.per_query_hit, (1, 0))
        self.assertEqual(result.any_hit, 1)
        self.assertEqual(
            result.physical_receipt["host_aggregation"],
            "OR_after_raw_receipt_seal")
        self.assertEqual(
            result.physical_receipt["raw_gpu_bit_vector_commitment_sha256"],
            result.output_sha256)
        self.assertNotEqual(result.output_sha256, result.physical_output_sha256)
        audit.finish.assert_called_once()
        with self.assertRaisesRegex(RuntimeError, "forbidden in the worker"):
            owner.execute(queries, expected_output=(1, 0))

    def test_runtime_rejects_nondeterministic_physical_padding(self):
        owner = self._fake_owner()

        def execute(
            _token, _starts, _ends, count, output_0, output_1, output_2,
            _primitive, _kind, _t, _statuses, _counters, _error, _capacity,
        ):
            self.assertEqual(count, 1)
            output_0[0] = 1; output_1[0] = 99; output_2[0] = 0
            return 0

        owner._execute = execute
        audit = SimpleNamespace(
            finish=mock.Mock(return_value={
                "physical_executor_classification": "optix_traversal_observed"}),
            abort=mock.Mock())
        with mock.patch.object(
                runtime.OptixTraversalAuditSession, "open",
                return_value=audit), mock.patch.object(
                    runtime, "_read_native_descriptor", return_value={}), \
                mock.patch.object(runtime, "_require_descriptor_transition"), \
                mock.patch.object(runtime, "_require_native_target_binding"), \
                mock.patch.object(runtime, "_require_execution_fingerprints"):
            with self.assertRaisesRegex(RuntimeError, "hit\+zero\+zero"):
                owner.execute((((0, 0, 0), (1, 0, 0)),))


if __name__ == "__main__":
    unittest.main()
