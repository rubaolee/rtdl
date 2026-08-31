"""Independent adversarial audit of every populated sphere Callback-IR leaf."""

from __future__ import annotations

from dataclasses import replace
import math
from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_builtin_sphere_standard_library import (  # noqa: E402
    FIRST_CONTACT_SOURCE,
    first_contact_manifest,
)
from rtdsl.v4_callback_ir import (  # noqa: E402
    CallbackRole,
    EffectKind,
    F32,
    FrozenConstant,
)
from rtdsl.v4_callback_optix_wrapper_codegen import (  # noqa: E402
    _effect_tag,
    _role_outputs,
)
from rtdsl.v4_public_builtin_sphere import (  # noqa: E402
    verify_builtin_sphere_callback_source,
)
from rtdsl.v4_sphere_callback_abi import compile_sphere_callback_abi  # noqa: E402
from rtdsl.v4_sphere_callback_numba_codegen import (  # noqa: E402
    generate_formal_sphere_numba_leaf,
)
from rtdsl.v4_sphere_optix_wrapper_codegen import (  # noqa: E402
    generate_trusted_optix_sphere_wrapper_v1,
)
from rtdsl.v4_sphere_physical_schema import (  # noqa: E402
    BuiltinSpherePhysicalSchema,
    SphereTargetProfile,
    verify_builtin_sphere_physical_schema,
)


def _authority(source=FIRST_CONTACT_SOURCE, manifest=None):
    manifest = first_contact_manifest() if manifest is None else manifest
    verified = verify_builtin_sphere_callback_source(source, manifest).callback
    schema = BuiltinSpherePhysicalSchema(
        verified.ir_sha256,
        verified.effect_digest,
        "sphere_centers",
        "sphere_radii",
        "application_ids",
        "motion_segments",
        "first_contacts",
        "device_status",
    )
    authority = verify_builtin_sphere_physical_schema(
        verified,
        schema,
        target=SphereTargetProfile("optix", "9.0.0", "8.9", "1" * 64),
    )
    abi = compile_sphere_callback_abi(authority)
    wrapper = generate_trusted_optix_sphere_wrapper_v1(
        authority, authority.canonical_plan, abi)
    return authority, abi, wrapper


def _default_value(kind: str, *, pointer: bool):
    scalar = kind[kind.find("<") + 1:-1] if "<" in kind else kind
    value = 0.0 if scalar in {"f32", "f64"} else 0
    return [value] if pointer else value


def _execute_leaf(authority, abi, role, inputs, *, source_transform=None):
    leaf = generate_formal_sphere_numba_leaf(authority, abi, role)
    arguments = {}
    for path, kind in zip(leaf.parameter_order, leaf.parameter_types):
        arguments[path] = _default_value(
            kind, pointer=kind.startswith("ptr<") or kind.startswith("device_ptr<"))
    arguments.update(inputs)
    namespace = {
        "__builtins__": {},
        "math": math,
        "_f32": np.float32,
        "range": range,
        "abs": abs,
    }
    source = (
        leaf.generated_source if source_transform is None
        else source_transform(leaf.generated_source))
    exec(compile(source, "<goal5833-leaf-audit>", "exec"),
         namespace, namespace)
    namespace[leaf.abi_name](
        *(arguments[path] for path in leaf.parameter_order))
    returned = {
        path: arguments[path][0]
        for path, kind in zip(leaf.parameter_order, leaf.parameter_types)
        if kind.startswith("ptr<")
    }
    return leaf, returned


_MAKE_RAY_INPUTS = {
    "in.context.launch_index": 0,
    "in.launch_id": 0,
    "in.queries.columns.start.x": [2.0],
    "in.queries.columns.start.y": [3.0],
    "in.queries.columns.start.z": [4.0],
    "in.queries.columns.end.x": [7.0],
    "in.queries.columns.end.y": [11.0],
    "in.queries.columns.end.z": [17.0],
    "in.queries.length": 1,
}
_CLOSEST_HIT_INPUTS = {
    "in.context.launch_index": 0,
    "in.hit.t": 0.375,
    "in.hit.hit_kind": 0xA5,
    "in.payload.hit": 17,
    "in.payload.toi": 0.625,
    "in.payload.application_id": 99,
    "in.application_ids.columns": [77],
    "in.application_ids.length": 1,
}
_MISS_INPUTS = {
    "in.context.launch_index": 0,
    "in.ray.origin.x": 2.0,
    "in.ray.origin.y": 3.0,
    "in.ray.origin.z": 4.0,
    "in.ray.direction.x": 5.0,
    "in.ray.direction.y": 8.0,
    "in.ray.direction.z": 13.0,
    "in.ray.tmin": 0.0,
    "in.ray.tmax": 1.0,
    "in.payload.hit": 17,
    "in.payload.toi": 0.625,
    "in.payload.application_id": 99,
}
_FINALIZE_INPUTS = {
    "in.context.launch_index": 0,
    "in.payload.hit": 23,
    "in.payload.toi": 0.125,
    "in.payload.application_id": 101,
}


class Goal5833SphereCallbackLeafAuditTest(unittest.TestCase):
    def test_generated_leaf_execution_populates_every_role_effect_leaf(self):
        authority, abi, _ = _authority()
        cases = (
            (CallbackRole.MAKE_RAY, _MAKE_RAY_INPUTS, {
                "out.effect_tag": 2,
                "out.trace_request.direction.x": 5.0,
                "out.trace_request.direction.y": 8.0,
                "out.trace_request.direction.z": 13.0,
                "out.trace_request.origin.x": 2.0,
                "out.trace_request.origin.y": 3.0,
                "out.trace_request.origin.z": 4.0,
                "out.trace_request.payload.application_id": 0xFFFFFFFF,
                "out.trace_request.payload.hit": 0,
                "out.trace_request.payload.toi": 1.0,
                "out.trace_request.tmax": 1.0,
                "out.trace_request.tmin": 0.0,
            }),
            (CallbackRole.CLOSEST_HIT, _CLOSEST_HIT_INPUTS, {
                "out.effect_tag": 8,
                "out.payload.payload.application_id": 77,
                "out.payload.payload.hit": 1,
                "out.payload.payload.toi": 0.375,
            }),
            (CallbackRole.MISS, _MISS_INPUTS, {
                "out.effect_tag": 8,
                "out.payload.payload.application_id": 99,
                "out.payload.payload.hit": 17,
                "out.payload.payload.toi": 0.625,
            }),
            (CallbackRole.FINALIZE, _FINALIZE_INPUTS, {
                "out.effect_tag": 9,
                "out.output.value.application_id": 101,
                "out.output.value.hit": 23,
                "out.output.value.toi": 0.125,
            }),
        )
        roles = {item.role: item for item in abi.roles}
        for role, inputs, expected in cases:
            with self.subTest(role=role.value):
                _, observed = _execute_leaf(authority, abi, role, inputs)
                output_paths = {field.path for field in _role_outputs(roles[role])}
                self.assertEqual(output_paths, set(expected))
                for path, value in expected.items():
                    self.assertEqual(observed[path], value, path)
                self.assertEqual(observed["status.ok"], 1)
                self.assertEqual(
                    observed["status.effect_tag"], observed["out.effect_tag"])

    def test_every_role_output_has_an_exact_physical_sink(self):
        _, abi, wrapper = _authority()
        source = wrapper.source
        expected_sinks = {
            (CallbackRole.MAKE_RAY, "out.effect_tag"):
                "if (mr_out_effect_tag != 2u)",
            (CallbackRole.MAKE_RAY, "out.trace_request.direction.x"):
                "ray_dx=__float_as_uint(mr_out_trace_request_direction_x)",
            (CallbackRole.MAKE_RAY, "out.trace_request.direction.y"):
                "ray_dy=__float_as_uint(mr_out_trace_request_direction_y)",
            (CallbackRole.MAKE_RAY, "out.trace_request.direction.z"):
                "ray_dz=__float_as_uint(mr_out_trace_request_direction_z)",
            (CallbackRole.MAKE_RAY, "out.trace_request.origin.x"):
                "ray_ox=__float_as_uint(mr_out_trace_request_origin_x)",
            (CallbackRole.MAKE_RAY, "out.trace_request.origin.y"):
                "ray_oy=__float_as_uint(mr_out_trace_request_origin_y)",
            (CallbackRole.MAKE_RAY, "out.trace_request.origin.z"):
                "ray_oz=__float_as_uint(mr_out_trace_request_origin_z)",
            (CallbackRole.MAKE_RAY, "out.trace_request.payload.application_id"):
                "payload_2 = mr_out_trace_request_payload_application_id",
            (CallbackRole.MAKE_RAY, "out.trace_request.payload.hit"):
                "payload_0 = mr_out_trace_request_payload_hit",
            (CallbackRole.MAKE_RAY, "out.trace_request.payload.toi"):
                "payload_1 = __float_as_uint(mr_out_trace_request_payload_toi)",
            (CallbackRole.MAKE_RAY, "out.trace_request.tmax"):
                "const float ray_tmax=mr_out_trace_request_tmax",
            (CallbackRole.MAKE_RAY, "out.trace_request.tmin"):
                "const float ray_tmin=mr_out_trace_request_tmin",
            (CallbackRole.CLOSEST_HIT, "out.effect_tag"):
                "if (ch_out_effect_tag != 8u)",
            (CallbackRole.CLOSEST_HIT, "out.payload.payload.application_id"):
                "payload_2 = ch_out_payload_payload_application_id",
            (CallbackRole.CLOSEST_HIT, "out.payload.payload.hit"):
                "payload_0 = ch_out_payload_payload_hit",
            (CallbackRole.CLOSEST_HIT, "out.payload.payload.toi"):
                "payload_1 = __float_as_uint(ch_out_payload_payload_toi)",
            (CallbackRole.MISS, "out.effect_tag"):
                "if (ms_out_effect_tag != 8u)",
            (CallbackRole.MISS, "out.payload.payload.application_id"):
                "payload_2 = ms_out_payload_payload_application_id",
            (CallbackRole.MISS, "out.payload.payload.hit"):
                "payload_0 = ms_out_payload_payload_hit",
            (CallbackRole.MISS, "out.payload.payload.toi"):
                "payload_1 = __float_as_uint(ms_out_payload_payload_toi)",
            (CallbackRole.FINALIZE, "out.effect_tag"):
                "if (fin_out_effect_tag != 9u)",
            (CallbackRole.FINALIZE, "out.output.value.application_id"):
                "params.output_2[query]=fin_out_output_value_application_id",
            (CallbackRole.FINALIZE, "out.output.value.hit"):
                "params.output_0[query]=fin_out_output_value_hit",
            (CallbackRole.FINALIZE, "out.output.value.toi"):
                "params.output_1[query]=__float_as_uint(fin_out_output_value_toi)",
        }
        observed_keys = {
            (role.role, field.path)
            for role in abi.roles
            for field in _role_outputs(role)
        }
        self.assertEqual(observed_keys, set(expected_sinks))
        for key, sink in expected_sinks.items():
            with self.subTest(role=key[0].value, path=key[1]):
                self.assertIn(sink, source)

        # The interval leaves are not merely copied: the exact locals reach
        # traversal, hit validation, and the miss-role ABI.
        self.assertIn(
            "ray_tmin,ray_tmax,0.0f,OptixVisibilityMask(255)", source)
        self.assertIn(
            "selected_hit_t<ray_tmin || selected_hit_t>ray_tmax", source)
        self.assertIn("ray_tmin, ray_tmax, payload_0", source)

    def test_status_effect_is_exact_not_any_nonzero_role_effect(self):
        _, abi, wrapper = _authority()
        source = wrapper.source
        roles = {item.role: item for item in abi.roles}
        expected = (
            (CallbackRole.MAKE_RAY, EffectKind.TRACE_REQUEST),
            (CallbackRole.CLOSEST_HIT, EffectKind.PAYLOAD),
            (CallbackRole.MISS, EffectKind.PAYLOAD),
            (CallbackRole.FINALIZE, EffectKind.OUTPUT),
        )
        for role, kind in expected:
            arm = (
                f"expected_role == {roles[role].role_tag}u ? "
                f"{_effect_tag(roles[role], kind)}u")
            self.assertIn(arm, source)
        self.assertIn("effect_tag == expected_effect_tag", source)
        self.assertIn("expected_effect_tag != 0u", source)
        self.assertNotIn(
            "first_error_claimed == 0u && effect_tag != 0u;", source)

        # A linked leaf with a correct out tag but a different nonzero status
        # tag was accepted by the predecessor predicate.  The successor's
        # generated exact-tag predicate rejects that concrete hostile state.
        make_ray = roles[CallbackRole.MAKE_RAY]
        correct = _effect_tag(make_ray, EffectKind.TRACE_REQUEST)
        hostile_status = _effect_tag(
            roles[CallbackRole.CLOSEST_HIT], EffectKind.PAYLOAD)
        self.assertNotEqual(correct, hostile_status)
        self.assertTrue(hostile_status != 0)  # predecessor predicate
        self.assertFalse(hostile_status == correct)  # generated successor predicate

        def corrupt_only_status_effect(generated_source):
            assignment = f"status_effect_tag[0] = {correct}"
            self.assertEqual(generated_source.count(assignment), 1)
            return generated_source.replace(
                assignment, f"status_effect_tag[0] = {hostile_status}", 1)

        _, hostile = _execute_leaf(
            *_authority()[:2],
            CallbackRole.MAKE_RAY,
            _MAKE_RAY_INPUTS,
            source_transform=corrupt_only_status_effect,
        )
        self.assertEqual(hostile["status.ok"], 1)
        self.assertEqual(hostile["out.effect_tag"], correct)
        self.assertEqual(hostile["status.effect_tag"], hostile_status)
        self.assertFalse(
            hostile["status.effect_tag"] == correct,
            "hostile nonzero status tag must fail the generated exact-role check",
        )

    def test_valid_source_mutations_change_each_data_leaf_before_wrapper_sinks(self):
        half_manifest = replace(
            first_contact_manifest(),
            constants=first_contact_manifest().constants + (
                FrozenConstant("HALF_F32", F32, 0.5),),
        )
        cases = (
            (CallbackRole.MAKE_RAY, "origin=query.start", "origin=query.end",
             "out.trace_request.origin.x", 7.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "origin=query.start", "origin=query.end",
             "out.trace_request.origin.y", 11.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "origin=query.start", "origin=query.end",
             "out.trace_request.origin.z", 17.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "direction=direction", "direction=query.start",
             "out.trace_request.direction.x", 2.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "direction=direction", "direction=query.start",
             "out.trace_request.direction.y", 3.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "direction=direction", "direction=query.start",
             "out.trace_request.direction.z", 4.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "tmin=ZERO_F32", "tmin=HALF_F32",
             "out.trace_request.tmin", 0.5, half_manifest),
            (CallbackRole.MAKE_RAY, "tmax=ONE_F32", "tmax=HALF_F32",
             "out.trace_request.tmax", 0.5, half_manifest),
            (CallbackRole.MAKE_RAY, "hit=ZERO_U32, toi=ONE_F32",
             "hit=ONE_U32, toi=ONE_F32",
             "out.trace_request.payload.hit", 1, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "toi=ONE_F32, application_id=U32_MAX",
             "toi=ZERO_F32, application_id=U32_MAX",
             "out.trace_request.payload.toi", 0.0, first_contact_manifest()),
            (CallbackRole.MAKE_RAY, "application_id=U32_MAX)",
             "application_id=ZERO_U32)",
             "out.trace_request.payload.application_id", 0,
             first_contact_manifest()),
            (CallbackRole.CLOSEST_HIT, "hit=ONE_U32, toi=hit.t",
             "hit=ZERO_U32, toi=hit.t",
             "out.payload.payload.hit", 0, first_contact_manifest()),
            (CallbackRole.CLOSEST_HIT, "toi=hit.t, application_id=application_ids[ZERO_U32]",
             "toi=payload.toi, application_id=application_ids[ZERO_U32]",
             "out.payload.payload.toi", 0.625, first_contact_manifest()),
            (CallbackRole.CLOSEST_HIT, "application_id=application_ids[ZERO_U32])",
             "application_id=payload.application_id)",
             "out.payload.payload.application_id", 99,
             first_contact_manifest()),
            (CallbackRole.MISS, "return optix.payload(payload=payload)",
             "return optix.payload(payload=FirstContactPayload(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32))",
             "out.payload.payload.hit", 1, first_contact_manifest()),
            (CallbackRole.MISS, "return optix.payload(payload=payload)",
             "return optix.payload(payload=FirstContactPayload(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32))",
             "out.payload.payload.toi", 0.0, first_contact_manifest()),
            (CallbackRole.MISS, "return optix.payload(payload=payload)",
             "return optix.payload(payload=FirstContactPayload(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32))",
             "out.payload.payload.application_id", 0,
             first_contact_manifest()),
            (CallbackRole.FINALIZE,
             "FirstContactOutput(hit=payload.hit, toi=payload.toi, application_id=payload.application_id)",
             "FirstContactOutput(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32)",
             "out.output.value.hit", 1, first_contact_manifest()),
            (CallbackRole.FINALIZE,
             "FirstContactOutput(hit=payload.hit, toi=payload.toi, application_id=payload.application_id)",
             "FirstContactOutput(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32)",
             "out.output.value.toi", 0.0, first_contact_manifest()),
            (CallbackRole.FINALIZE,
             "FirstContactOutput(hit=payload.hit, toi=payload.toi, application_id=payload.application_id)",
             "FirstContactOutput(hit=ONE_U32, toi=ZERO_F32, application_id=ZERO_U32)",
             "out.output.value.application_id", 0, first_contact_manifest()),
        )
        inputs = {
            CallbackRole.MAKE_RAY: _MAKE_RAY_INPUTS,
            CallbackRole.CLOSEST_HIT: _CLOSEST_HIT_INPUTS,
            CallbackRole.MISS: _MISS_INPUTS,
            CallbackRole.FINALIZE: _FINALIZE_INPUTS,
        }
        base_authority, _, _ = _authority()
        for role, old, new, path, expected, manifest in cases:
            with self.subTest(role=role.value, path=path):
                self.assertEqual(FIRST_CONTACT_SOURCE.count(old), 1)
                mutated = FIRST_CONTACT_SOURCE.replace(old, new, 1)
                authority, abi, _ = _authority(mutated, manifest)
                self.assertNotEqual(
                    authority.callback.ir_sha256, base_authority.callback.ir_sha256)
                _, observed = _execute_leaf(authority, abi, role, inputs[role])
                self.assertEqual(observed[path], expected)


if __name__ == "__main__":
    unittest.main()
