"""Hostile liveness tests for Goal5833 sphere Callback-IR lowering."""

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
from rtdsl.v4_callback_ir import CallbackRole, F32, FrozenConstant  # noqa: E402
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


def _authority_for(source: str, manifest):
    verified_source = verify_builtin_sphere_callback_source(source, manifest)
    callback = verified_source.callback
    schema = BuiltinSpherePhysicalSchema(
        callback.ir_sha256,
        callback.effect_digest,
        "sphere_centers",
        "sphere_radii",
        "application_ids",
        "motion_segments",
        "first_contacts",
        "device_status",
    )
    target = SphereTargetProfile("optix", "9.0.0", "8.9", "1" * 64)
    authority = verify_builtin_sphere_physical_schema(
        callback, schema, target=target)
    abi = compile_sphere_callback_abi(authority)
    wrapper = generate_trusted_optix_sphere_wrapper_v1(
        authority, authority.canonical_plan, abi)
    return authority, abi, wrapper


def _local_name(prefix: str, path: str) -> str:
    return prefix + "_" + "".join(ch if ch.isalnum() else "_" for ch in path)


class Goal5833SphereCallbackSemanticsA1Test(unittest.TestCase):
    def test_make_ray_interval_is_lowered_once_and_reused_consistently(self):
        _, _, wrapper = _authority_for(FIRST_CONTACT_SOURCE, first_contact_manifest())
        source = wrapper.source
        self.assertIn("const float ray_tmin=mr_out_trace_request_tmin;", source)
        self.assertIn("const float ray_tmax=mr_out_trace_request_tmax;", source)
        self.assertIn("ray_tmin,ray_tmax,0.0f,OptixVisibilityMask(255)", source)
        self.assertIn("selected_hit_t<ray_tmin || selected_hit_t>ray_tmax", source)
        self.assertIn("ray_tmin, ray_tmax", source)
        self.assertNotIn("0.0f,1.0f,0.0f,OptixVisibilityMask(255)", source)

    def test_valid_half_tmax_mutation_remains_live_at_trace_edge(self):
        base_manifest = first_contact_manifest()
        manifest = replace(
            base_manifest,
            constants=base_manifest.constants + (FrozenConstant("HALF_F32", F32, 0.5),),
        )
        mutated_source = FIRST_CONTACT_SOURCE.replace(
            "tmax=ONE_F32", "tmax=HALF_F32", 1)
        base_authority, base_abi, base_wrapper = _authority_for(
            FIRST_CONTACT_SOURCE, base_manifest)
        mutated_authority, mutated_abi, mutated_wrapper = _authority_for(
            mutated_source, manifest)

        self.assertNotEqual(
            base_authority.callback.ir_sha256,
            mutated_authority.callback.ir_sha256,
        )
        # The linked leaf and role symbols have a different identity.  Both
        # wrappers use the leaf output at the trace edge, so the linked leaf—
        # not a hard-coded literal—selects 1.0f versus 0.5f.
        self.assertNotEqual(base_wrapper.source_sha256, mutated_wrapper.source_sha256)
        self.assertNotEqual(
            generate_formal_sphere_numba_leaf(
                base_authority, base_abi, CallbackRole.MAKE_RAY,
            ).generated_source_sha256,
            generate_formal_sphere_numba_leaf(
                mutated_authority, mutated_abi, CallbackRole.MAKE_RAY,
            ).generated_source_sha256,
        )
        self.assertIn("ray_tmin,ray_tmax", base_wrapper.source)
        self.assertIn("ray_tmin,ray_tmax", mutated_wrapper.source)
        self.assertGreaterEqual(
            mutated_wrapper.source.count("mr_out_trace_request_tmax"), 3)

    def test_invalid_zero_tmax_mutation_is_not_silently_replaced_by_one(self):
        mutated_source = FIRST_CONTACT_SOURCE.replace(
            "tmax=ONE_F32", "tmax=ZERO_F32", 1)
        authority, abi, wrapper = _authority_for(
            mutated_source, first_contact_manifest())
        self.assertIn("tmax=ZERO_F32", mutated_source)
        self.assertIn("ray_tmin,ray_tmax", wrapper.source)
        self.assertNotIn("0.0f,1.0f,0.0f,OptixVisibilityMask(255)", wrapper.source)
        # The mutation is accepted as typed IR but receives its own identity;
        # the generated make-ray leaf's existing INVALID_TRACE_REQUEST guard
        # rejects tmin >= tmax before optixTrace can run.
        self.assertNotEqual(
            authority.callback.ir_sha256,
            _authority_for(FIRST_CONTACT_SOURCE, first_contact_manifest())[0]
            .callback.ir_sha256,
        )
        leaf = generate_formal_sphere_numba_leaf(
            authority, abi, CallbackRole.MAKE_RAY)
        arguments = {}
        outputs = {}
        for path, kind in zip(leaf.parameter_order, leaf.parameter_types):
            if kind.startswith("ptr<"):
                value = [0.0] if "f32" in kind or "f64" in kind else [0]
                arguments[path] = value
                outputs[path] = value
            elif kind.startswith("device_ptr<"):
                arguments[path] = [1.0] if path.endswith("end.x") else [0.0]
            else:
                arguments[path] = 0.0 if kind in {"f32", "f64"} else 0
        arguments["in.queries.length"] = 1
        namespace = {
            "__builtins__": {},
            "math": math,
            "_f32": np.float32,
            "range": range,
            "abs": abs,
        }
        exec(compile(leaf.generated_source, "<goal5833-zero-tmax>", "exec"),
             namespace, namespace)
        namespace[leaf.abi_name](
            *(arguments[path] for path in leaf.parameter_order))
        self.assertEqual(outputs["status.ok"][0], 0)
        self.assertEqual(outputs["status.error_code"][0], 9)
        self.assertEqual(outputs["out.effect_tag"][0], 0)

    def test_every_populated_role_output_has_a_downstream_use(self):
        _, abi, wrapper = _authority_for(FIRST_CONTACT_SOURCE, first_contact_manifest())
        prefixes = {
            "make_ray": "mr",
            "closest_hit": "ch",
            "miss": "ms",
            "finalize": "fin",
        }
        for role in abi.roles:
            prefix = prefixes[role.role.value]
            output_paths = role.parameter_order[len(role.inputs) + len(role.status):]
            self.assertTrue(output_paths, role.role.value)
            for path in output_paths:
                local = _local_name(prefix, path)
                # One occurrence declares the local and one passes its address
                # to the leaf.  A third occurrence is the minimum evidence that
                # the returned value affects wrapper control/data flow.
                self.assertGreaterEqual(
                    wrapper.source.count(local),
                    3,
                    f"inert accepted output leaf: {role.role.value}:{path}",
                )


if __name__ == "__main__":
    unittest.main()
