from __future__ import annotations

import dataclasses
import math
import unittest

import numpy as np

from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_callback_numba_codegen import (
    CallbackCodegenError,
    generate_formal_numba_leaf,
)
from tests.goal5750_v4_callback_ir_test import SOURCE, manifest


class Goal5751FormalNumbaCodegenTest(unittest.TestCase):
    def setUp(self) -> None:
        self.program = compile_callback_source(SOURCE, manifest())
        contract = self.program.program.manifest.any_hit_delivery
        assert contract is not None
        self.proof = AnyHitProofAuthority(
            callback_ir_sha256=self.program.ir_sha256,
            effect_digest=self.program.effect_digest,
            delivery_contract=contract,
            proof_sha256="a" * 64,
            proof_kind="external_machine_checked_order_independence_v1",
        )
        self.abi = compile_callback_abi(
            self.program, any_hit_proof_authority=self.proof
        )

    def leaf(self, role: CallbackRole):
        return generate_formal_numba_leaf(
            self.program,
            self.abi,
            role,
            any_hit_proof_authority=self.proof,
        )

    def test_all_seven_roles_generate_deterministic_closed_source(self):
        leaves = [self.leaf(role) for role in CallbackRole]
        self.assertEqual(len(leaves), 7)
        for leaf in leaves:
            self.assertEqual(leaf, self.leaf(leaf.role))
            self.assertEqual(len(leaf.parameter_order), len(leaf.parameter_types))
            self.assertIn(f"def {leaf.abi_name}(", leaf.generated_source)
            self.assertNotIn("@optix", leaf.generated_source)
            self.assertNotIn("SearchProgram", leaf.generated_source)
            self.assertNotIn("import ", leaf.generated_source)
            self.assertNotIn("exec(", leaf.generated_source)
            self.assertNotIn("eval(", leaf.generated_source)
            compile(leaf.generated_source, "<test-generated>", "exec")

    def test_codegen_rejects_missing_any_hit_proof_and_stale_abi(self):
        with self.assertRaises(CallbackCodegenError) as missing:
            generate_formal_numba_leaf(
                self.program,
                self.abi,
                CallbackRole.INTERSECTION,
            )
        self.assertEqual(missing.exception.code, "abi_admission")
        stale = dataclasses.replace(self.abi, abi_sha256="0" * 64)
        with self.assertRaises(CallbackCodegenError):
            generate_formal_numba_leaf(
                self.program,
                stale,
                CallbackRole.INTERSECTION,
                any_hit_proof_authority=self.proof,
            )

    def test_checked_integer_arithmetic_is_rejected_not_silently_wrapped(self):
        overflow_source = SOURCE.replace(
            "updated = SearchPayload(best_t=hit.t, best_id=hit.hit_kind)",
            "overflow_id = hit.hit_kind + U32_MAX\n            updated = SearchPayload(best_t=hit.t, best_id=overflow_id)",
            1,
        )
        program = compile_callback_source(overflow_source, manifest())
        proof = dataclasses.replace(
            self.proof,
            callback_ir_sha256=program.ir_sha256,
            effect_digest=program.effect_digest,
        )
        abi = compile_callback_abi(program, any_hit_proof_authority=proof)
        with self.assertRaises(CallbackCodegenError) as caught:
            generate_formal_numba_leaf(
                program, abi, CallbackRole.ANY_HIT,
                any_hit_proof_authority=proof,
            )
        self.assertEqual(caught.exception.code, "integer_numeric_codegen_pending")

    def test_intersection_leaf_executes_exact_hit_and_explicit_status(self):
        leaf = self.leaf(CallbackRole.INTERSECTION)
        outputs, arguments = self._arguments(leaf)
        arguments.update({
            "in.context.launch_index": 7,
            "in.ray.origin.x": 0.0,
            "in.ray.origin.y": 0.0,
            "in.ray.origin.z": 0.0,
            "in.ray.direction.x": 1.0,
            "in.ray.direction.y": 0.0,
            "in.ray.direction.z": 0.0,
            "in.ray.tmin": 0.0,
            "in.ray.tmax": 100.0,
            "in.primitive.center.x": 5.0,
            "in.primitive.center.y": 0.0,
            "in.primitive.center.z": 0.0,
            "in.primitive.radius": 1.0,
            "in.primitive.item_id": 3,
        })
        self._run(leaf, arguments)
        self.assertEqual(outputs["status.ok"][0], 1)
        self.assertEqual(outputs["status.error_code"][0], 0)
        self.assertEqual(outputs["status.launch_index"][0], 7)
        self.assertEqual(outputs["out.hit.t"][0], 4.0)
        self.assertEqual(outputs["out.hit.hit_kind"][0], 3)
        self.assertEqual(outputs["out.hit.attributes.0"][0], 3)

        invalid_outputs, invalid_arguments = self._arguments(leaf)
        invalid_arguments.update(arguments)
        invalid_arguments.update(invalid_outputs)
        invalid_arguments["in.primitive.item_id"] = 999
        self._run(leaf, invalid_arguments)
        self.assertEqual(invalid_outputs["status.ok"][0], 0)
        self.assertNotEqual(invalid_outputs["status.error_code"][0], 0)

    def test_remaining_effect_roles_execute_exactly_and_invalid_aabb_fails(self):
        bounds = self.leaf(CallbackRole.BOUNDS)
        bounds_outputs, bounds_arguments = self._arguments(bounds)
        bounds_arguments.update({
            "in.context.launch_index": 1,
            "in.primitive.center.x": 5.0,
            "in.primitive.center.y": 0.0,
            "in.primitive.center.z": 0.0,
            "in.primitive.radius": 1.0,
            "in.primitive.item_id": 3,
        })
        self._run(bounds, bounds_arguments)
        self.assertEqual(bounds_outputs["status.ok"][0], 1)
        self.assertEqual(bounds_outputs["out.aabb.lower.x"][0], 4.0)
        self.assertEqual(bounds_outputs["out.aabb.upper.x"][0], 6.0)

        invalid_outputs, invalid_arguments = self._arguments(bounds)
        invalid_arguments.update(bounds_arguments)
        invalid_arguments.update(invalid_outputs)
        invalid_arguments["in.primitive.radius"] = -1.0
        self._run(bounds, invalid_arguments)
        self.assertEqual(invalid_outputs["status.ok"][0], 0)
        self.assertNotEqual(invalid_outputs["status.error_code"][0], 0)

        for role in (CallbackRole.ANY_HIT, CallbackRole.CLOSEST_HIT):
            with self.subTest(role=role):
                leaf = self.leaf(role)
                outputs, arguments = self._arguments(leaf)
                arguments.update({
                    "in.context.launch_index": 8,
                    "in.hit.t": 4.0,
                    "in.hit.hit_kind": 3,
                    "in.payload.best_t": 100.0,
                    "in.payload.best_id": 0xFFFFFFFF,
                })
                self._run(leaf, arguments)
                self.assertEqual(outputs["status.ok"][0], 1)
                prefix = "out.accept_continue.payload" if role is CallbackRole.ANY_HIT else "out.payload.payload"
                self.assertEqual(outputs[f"{prefix}.best_t"][0], 4.0)
                self.assertEqual(outputs[f"{prefix}.best_id"][0], 3)

        missed = self.leaf(CallbackRole.MISS)
        outputs, arguments = self._arguments(missed)
        arguments.update({
            "in.context.launch_index": 9,
            "in.ray.origin.x": 0.0,
            "in.ray.origin.y": 0.0,
            "in.ray.origin.z": 0.0,
            "in.ray.direction.x": 1.0,
            "in.ray.direction.y": 0.0,
            "in.ray.direction.z": 0.0,
            "in.ray.tmin": 0.0,
            "in.ray.tmax": 100.0,
            "in.payload.best_t": 100.0,
            "in.payload.best_id": 0xFFFFFFFF,
        })
        self._run(missed, arguments)
        self.assertEqual(outputs["status.ok"][0], 1)
        self.assertEqual(outputs["out.payload.payload.best_id"][0], 0xFFFFFFFF)

    def test_make_ray_view_bounds_and_finalize_helper_are_executable(self):
        make_ray = self.leaf(CallbackRole.MAKE_RAY)
        outputs, arguments = self._arguments(make_ray)
        arguments.update({
            "in.context.launch_index": 2,
            "in.launch_id": 0,
            "in.queries.columns.origin.x": [1.0],
            "in.queries.columns.origin.y": [2.0],
            "in.queries.columns.origin.z": [3.0],
            "in.queries.columns.tmax": [9.0],
            "in.queries.length": 1,
        })
        self._run(make_ray, arguments)
        self.assertEqual(outputs["status.ok"][0], 1)
        self.assertEqual(outputs["out.trace_request.origin.x"][0], 1.0)
        self.assertEqual(outputs["out.trace_request.tmax"][0], 9.0)

        bad_outputs, bad_arguments = self._arguments(make_ray)
        bad_arguments.update(arguments)
        bad_arguments.update(bad_outputs)
        bad_arguments["in.launch_id"] = 1
        self._run(make_ray, bad_arguments)
        self.assertEqual(bad_outputs["status.ok"][0], 0)
        self.assertNotEqual(bad_outputs["status.error_code"][0], 0)

        finalize = self.leaf(CallbackRole.FINALIZE)
        final_outputs, final_arguments = self._arguments(finalize)
        final_arguments.update({
            "in.context.launch_index": 4,
            "in.payload.best_t": 12.5,
            "in.payload.best_id": 17,
        })
        self._run(finalize, final_arguments)
        self.assertEqual(final_outputs["status.ok"][0], 1)
        self.assertEqual(final_outputs["out.output.value.item_id"][0], 17)
        self.assertEqual(final_outputs["out.output.value.distance"][0], 12.5)

    def _arguments(self, leaf):
        arguments = {}
        outputs = {}
        for path, kind in zip(leaf.parameter_order, leaf.parameter_types):
            if kind.startswith("ptr<"):
                value = [0.0] if "f32" in kind or "f64" in kind else [0]
                arguments[path] = value
                outputs[path] = value
            elif kind.startswith("device_ptr<"):
                arguments[path] = []
            else:
                arguments[path] = 0.0 if kind in {"f32", "f64"} else 0
        return outputs, arguments

    def _run(self, leaf, arguments):
        namespace = {
            "__builtins__": {},
            "math": math,
            "_f32": np.float32,
            "range": range,
            "abs": abs,
        }
        exec(compile(leaf.generated_source, "<test-generated>", "exec"), namespace, namespace)
        function = namespace[leaf.abi_name]
        function(*(arguments[path] for path in leaf.parameter_order))


if __name__ == "__main__":
    unittest.main()
