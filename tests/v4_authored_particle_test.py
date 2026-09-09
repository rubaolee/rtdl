from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import numpy as np

from experiments.v4_authored_particle.program import (
    FACE_FIRST_SOURCE,
    build_face_first_physical_plan,
    face_first_expected,
    face_first_manifest,
)
from rtdsl import v4
from rtdsl.v4_builtin_triangle_standard_library import ADJACENCY_SOURCE


class V4AuthoredParticleTest(unittest.TestCase):
    def test_face_first_oracle_projection_is_exact_and_read_only(self):
        adjacency = np.array(
            [[11, 12, 90], [21, 22, 91]], dtype=np.uint32)
        observed = face_first_expected(adjacency)
        np.testing.assert_array_equal(
            observed,
            np.array([[90, 11, 12], [91, 21, 22]], dtype=np.uint32),
        )
        self.assertFalse(observed.flags.writeable)
        self.assertTrue(observed.flags.c_contiguous)

    def test_source_is_distinct_and_compiles_through_public_plan(self):
        self.assertNotEqual(
            hashlib.sha256(FACE_FIRST_SOURCE.encode()).hexdigest(),
            hashlib.sha256(ADJACENCY_SOURCE.encode()).hexdigest(),
        )
        verified = v4.verify_builtin_triangle_callback_source(
            FACE_FIRST_SOURCE, face_first_manifest())
        plan = build_face_first_physical_plan(
            verified, independent_cpu_oracle_sha256="1" * 64)
        with tempfile.TemporaryDirectory() as directory:
            native = Path(directory) / "librtdl_optix.so"
            native.write_bytes(b"identity-only")
            target = v4.V4Target.from_native(
                native,
                optix_sdk="9.0.0",
                compute_capability=(8, 9),
                supports_custom_aabb=True,
                supports_builtin_triangle=True,
            )
            program = verified.compile(physical_plan=plan, target=target)
        self.assertEqual(
            {item.role for item in program.callback.program.functions},
            {
                v4.CallbackRole.MAKE_RAY,
                v4.CallbackRole.CLOSEST_HIT,
                v4.CallbackRole.MISS,
                v4.CallbackRole.FINALIZE,
            },
        )
        self.assertIn("face_first_transitions", plan.schema.buffers[5].field_id)
        self.assertEqual(program.identity.source_sha256, verified.source_sha256)

    def test_oracle_projection_rejects_wrong_contract(self):
        with self.assertRaises(ValueError):
            face_first_expected(np.zeros((2, 3), dtype=np.int64))
        with self.assertRaises(ValueError):
            face_first_expected(np.zeros((2, 4), dtype=np.uint32))

    def test_public_prepared_batch_is_owner_bound_and_requires_bulk_input(self):
        from rtdsl import v4_public_builtin_triangle as public_triangle

        class FakeOwner:
            lifecycle_receipt = {}

            def prepare_query_batch(self, queries):
                return ("runtime_batch", id(queries))

        identity = v4.BuiltinTriangleCallbackExecutableIdentity(
            program_identity_sha256="1" * 64,
            physical_schema_sha256="2" * 64,
            canonical_plan_sha256="3" * 64,
            callback_abi_sha256="4" * 64,
            wrapper_source_sha256="5" * 64,
            generated_executable_sha256="6" * 64,
            composed_ptx_sha256="7" * 64,
            native_library_sha256="8" * 64,
        )
        decision = v4.ProtocolContractDecision(
            verdict="ACCEPT",
            findings=(),
            contract_sha256="9" * 64,
            projection_sha256="a" * 64,
        )
        owner = public_triangle.PreparedBuiltinTriangleCallbackProgram(
            owner=FakeOwner(),
            identity=identity,
            decision=decision,
            _construction_token=public_triangle._CONSTRUCTION_TOKEN,
        )
        batch = v4.BuiltinTriangleCallbackBatch(
            queries=np.zeros((2, 7), dtype=np.float32),
        )
        prepared = owner.prepare_batch(batch)
        self.assertEqual(prepared.query_count, 2)
        with self.assertRaises(AttributeError):
            prepared.query_count = 3
        with self.assertRaises(v4.PublicCallbackLifecycleError) as sequence:
            owner.prepare_batch(v4.BuiltinTriangleCallbackBatch(queries=(
                ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 1.0),
            )))
        self.assertEqual(
            sequence.exception.code, "GC032_PREPARED_BATCH_REQUIRES_BULK")


if __name__ == "__main__":
    unittest.main()
