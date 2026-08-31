from __future__ import annotations

import math
import pathlib
import unittest

import numpy as np

from rtdsl.v4_callback_poc import (
    CallbackRole,
    CallbackRuntimeError,
    CallbackVerificationError,
    EffectKind,
    StatusCode,
    audit_ptx,
    compile_numba_scalar_probe_isolated,
    generate_numba_leaf,
    generate_numba_scalar_probe,
    interpret_callback,
    trace_spheres_with_interpreter,
    verified_sphere_aabb,
    verify_callback_source,
    verify_sphere_aabb,
)


SOURCE = r'''
@optix.intersection
def sphere_intersection(ox: f32, oy: f32, oz: f32, dx: f32, dy: f32, dz: f32,
                        tmin: f32, tmax: f32, cx: f32, cy: f32, cz: f32,
                        radius: f32, item_id: u32):
    ocx = ox - cx
    ocy = oy - cy
    ocz = oz - cz
    b = ocx * dx + ocy * dy + ocz * dz
    c = ocx * ocx + ocy * ocy + ocz * ocz - radius * radius
    disc = b * b - c
    if disc >= 0.0:
        root = optix.sqrt(disc)
        near_t = -b - root
        far_t = -b + root
        t = near_t if near_t >= tmin else far_t
        if t >= tmin and t <= tmax:
            return optix.hit(t=t, item_id=item_id)
        else:
            return optix.no_hit()
    else:
        return optix.no_hit()

@optix.any_hit
def nearest_any_hit(hit_t: f32, hit_id: u32, best_t: f32, best_id: u32):
    if hit_t < best_t or (hit_t == best_t and hit_id < best_id):
        return optix.accept_continue(best_t=hit_t, best_id=hit_id)
    else:
        return optix.accept_continue(best_t=best_t, best_id=best_id)

@optix.miss
def preserve_miss(best_t: f32, best_id: u32):
    return optix.payload(best_t=best_t, best_id=best_id)
'''


class Goal5749CallbackPocTest(unittest.TestCase):
    def test_source_parses_to_stable_ir_without_execution(self):
        first = verify_callback_source(SOURCE)
        second = verify_callback_source(SOURCE)
        self.assertEqual(first.ir_sha256, second.ir_sha256)
        self.assertEqual(first.source_sha256, second.source_sha256)
        self.assertEqual([item.role for item in first.functions],
                         [CallbackRole.ANY_HIT, CallbackRole.INTERSECTION, CallbackRole.MISS])
        for role in CallbackRole:
            leaf = generate_numba_leaf(first, role)
            self.assertTrue(leaf.abi_name.startswith("rtdl_v4_"))
            self.assertFalse(leaf.abi_name.startswith("__direct_callable__"))

    def test_top_level_python_execution_and_foreign_calls_fail_closed(self):
        with self.assertRaises(CallbackVerificationError):
            verify_callback_source("open('stolen', 'w')\n" + SOURCE)
        with self.assertRaises(CallbackVerificationError):
            verify_callback_source(SOURCE.replace("optix.sqrt(disc)", "evil.sqrt(disc)"))

    def test_role_abi_and_effect_mismatch_fail_closed(self):
        with self.assertRaises(CallbackVerificationError):
            verify_callback_source(SOURCE.replace("item_id: u32", "item_id: f32", 1))
        with self.assertRaises(CallbackVerificationError):
            verify_callback_source(SOURCE.replace(
                "return optix.no_hit()", "return optix.payload(best_t=tmax, best_id=item_id)", 1))

    def test_interpreter_exact_nearest_and_tie_break(self):
        module = verify_callback_source(SOURCE)
        result = trace_spheres_with_interpreter(
            module,
            origin=(0.0, 0.0, 0.0),
            direction=(1.0, 0.0, 0.0),
            tmin=0.0,
            tmax=100.0,
            spheres=(((5.0, 0.0, 0.0), 1.0, 9),
                     ((5.0, 0.0, 0.0), 1.0, 3),
                     ((10.0, 0.0, 0.0), 1.0, 1)),
        )
        self.assertEqual(result.kind, EffectKind.PAYLOAD)
        self.assertEqual(result.u0, 3)
        self.assertEqual(result.f0, 4.0)

    def test_interpreter_no_hit_and_runtime_faults(self):
        module = verify_callback_source(SOURCE)
        result = trace_spheres_with_interpreter(
            module, origin=(0, 0, 0), direction=(1, 0, 0), tmin=0, tmax=2,
            spheres=(((10, 0, 0), 1, 7),),
        )
        self.assertEqual(result.kind, EffectKind.PAYLOAD)
        self.assertEqual(result.u0, 0xFFFFFFFF)
        with self.assertRaises(CallbackRuntimeError) as caught:
            interpret_callback(module.function(CallbackRole.MISS),
                               {"best_t": math.inf, "best_id": 0})
        self.assertEqual(caught.exception.status, StatusCode.NONFINITE_EFFECT)

    def test_predeclared_device_error_variants_match_interpreter_status(self):
        nonfinite = SOURCE.replace(
            "            return optix.hit(t=t, item_id=item_id)",
            "            bad_t = radius * 3.4e38\n"
            "            bad_t2 = bad_t * 2.0\n"
            "            return optix.hit(t=bad_t2, item_id=item_id)",
        )
        with self.assertRaises(CallbackRuntimeError) as nonfinite_error:
            trace_spheres_with_interpreter(
                verify_callback_source(nonfinite),
                origin=(0, 0, 0), direction=(1, 0, 0), tmin=0, tmax=100,
                spheres=(((5, 0, 0), 1, 9),),
            )
        self.assertEqual(nonfinite_error.exception.status, StatusCode.NONFINITE_EFFECT)

        overflow = SOURCE.replace(
            "        return optix.accept_continue(best_t=hit_t, best_id=hit_id)",
            "        overflow_id = hit_id + 4294967295\n"
            "        return optix.accept_continue(best_t=hit_t, best_id=overflow_id)",
        )
        with self.assertRaises(CallbackRuntimeError) as overflow_error:
            trace_spheres_with_interpreter(
                verify_callback_source(overflow),
                origin=(0, 0, 0), direction=(1, 0, 0), tmin=0, tmax=100,
                spheres=(((5, 0, 0), 1, 9),),
            )
        self.assertEqual(overflow_error.exception.status, StatusCode.U32_OVERFLOW)

    def test_verified_sphere_contract_rejects_underbound_box(self):
        box = verified_sphere_aabb((1.0, 2.0, 3.0), 0.5)
        verify_sphere_aabb((1.0, 2.0, 3.0), 0.5, box)
        underbound = list(box)
        underbound[3] = 1.49
        with self.assertRaises(CallbackVerificationError):
            verify_sphere_aabb((1.0, 2.0, 3.0), 0.5, underbound)

    def test_codegen_is_deterministic_and_contains_explicit_status_envelope(self):
        module = verify_callback_source(SOURCE)
        for role in CallbackRole:
            first = generate_numba_leaf(module, role)
            second = generate_numba_leaf(module, role)
            self.assertEqual(first.generated_source_sha256, second.generated_source_sha256)
            self.assertIn("out_status[0] = 5", first.generated_source)
            self.assertIn("out_nonce[0]", first.generated_source)
            self.assertNotIn("optix.", first.generated_source)
            self.assertNotIn("eval(", first.generated_source)

        scalar_first = generate_numba_scalar_probe(module)
        scalar_second = generate_numba_scalar_probe(module)
        self.assertEqual(scalar_first, scalar_second)
        self.assertIn("return value + 1.0", scalar_first.generated_source)
        self.assertEqual(scalar_first.ir_sha256, module.ir_sha256)

    def test_generated_source_differentially_matches_interpreter(self):
        module = verify_callback_source(SOURCE)
        function = module.function(CallbackRole.INTERSECTION)
        leaf = generate_numba_leaf(module, CallbackRole.INTERSECTION)
        namespace = {"__builtins__": {}, "math": math}
        exec(compile(leaf.generated_source, "<generated-test>", "exec"), namespace, namespace)
        generated = namespace[leaf.abi_name]
        arguments = {
            "ox": 0.0, "oy": 0.0, "oz": 0.0,
            "dx": 1.0, "dy": 0.0, "dz": 0.0,
            "tmin": 0.0, "tmax": 100.0,
            "cx": 5.0, "cy": 0.0, "cz": 0.0,
            "radius": 1.0, "item_id": 17,
        }
        reference = interpret_callback(function, arguments)
        status = np.zeros(1, dtype=np.uint32)
        effect = np.zeros(1, dtype=np.uint32)
        f0 = np.zeros(1, dtype=np.float32)
        u0 = np.zeros(1, dtype=np.uint32)
        nonce = np.zeros(1, dtype=np.uint32)
        generated(*(arguments[name] for name, _ in function.arguments),
                  status, effect, f0, u0, nonce)
        self.assertEqual(int(status[0]), 0)
        self.assertEqual(int(effect[0]), 1)
        self.assertEqual(float(f0[0]), reference.f0)
        self.assertEqual(int(u0[0]), reference.u0)
        self.assertEqual(int(nonce[0]), leaf.nonce_word)

    def test_native_poc_is_isolated_and_has_both_link_routes_and_stack_rules(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        source = (root / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        prelude = (root / "src/native/optix/rtdl_optix_prelude.h").read_text()
        self.assertIn("V4CallbackPipelineHolder", source)
        self.assertIn("OPTIX_PROGRAM_GROUP_KIND_CALLABLES", source)
        self.assertIn("__direct_callable__rtdl_v4_intersection_bridge", source)
        self.assertIn("direct_callable_route ? 3u : 0u", source)
        self.assertIn("index < bridge_symbols.size()", source)
        self.assertIn('"--relocatable-device-code=true"', source)
        self.assertIn("v4_compose_wrapper_and_leaf_ptx", source)
        self.assertIn("v4_wrapper_without_leaf_externs", source)
        self.assertIn("V4 Numba environment symbol is referenced by leaf PTX", source)
        self.assertIn("v4_wrapper_arch_option(leaf_ptx[0])", source)
        self.assertIn('"--gpu-architecture=compute_" + suffix', source)
        self.assertIn("unsigned long long @INTERSECTION_SYMBOL@", source)
        self.assertIn("@SCALAR_SYMBOL@(41.0f)", source)
        self.assertIn("direct_callable_route ? 1u : 0u", source)
        self.assertIn(
            "rtdlOptixAccumulateStackSizesCompat(group, &sizes, holder->pipeline)",
            source,
        )
        self.assertIn(
            "optixUtilAccumulateStackSizes(group, sizes, pipeline)", prelude)
        self.assertIn("optixDirectCall<void", source)
        self.assertIn("rtdl_optix_bind_traversal_audit_context", source)
        self.assertIn("atomicCAS(&record->status, 0u, code)", source)
        self.assertIn("atomicOr(&params.status[query].invocation_mask", source)
        self.assertNotIn("arkade", source.lower())
        self.assertNotIn("x_hd", source.lower())
        policy = (root / "history/internal_docs/goal5749_amendment_a1_composed_numba_leaf_policy_20260811.json").read_text()
        self.assertIn('"link_routes": ["ordinary_composed", "direct_callable"]', policy)
        driver = (root / "scripts/goal5749_v4_callback_poc_driver.py").read_text()
        self.assertIn("goal5749_amendment_a1_composed_numba_leaf_policy_20260811.json", driver)
        self.assertNotIn('route="ordinary_external"', driver)
        executor = (root / "scripts/goal5749_modern_rtx_executor.sh").read_text()
        self.assertIn("exactly one visible GPU", executor)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", executor)
        self.assertIn("preserved_before_worker_zero", executor)
        self.assertIn("registered_performance_timing_count", executor)
        executor_bytes = (root / "scripts/goal5749_modern_rtx_executor.sh").read_bytes()
        self.assertNotIn(b"\r", executor_bytes)

    def test_ptx_audit_requires_symbol_isa_and_closed_externals(self):
        ptx = '''
.version 7.8
.target sm_61
.address_size 64
.visible .func rtdl_v4_intersection_leaf_deadbeef() { ret; }
'''
        receipt = audit_ptx(
            ptx,
            abi_name="rtdl_v4_intersection_leaf_deadbeef",
            accepted_isa=("7.0", "8.8"),
            allowed_external_symbols=frozenset(),
        )
        self.assertEqual(receipt["ptx_version"], "7.8")
        with self.assertRaises(CallbackVerificationError):
            audit_ptx(ptx.replace(".version 7.8", ".version 9.9"),
                      abi_name="rtdl_v4_intersection_leaf_deadbeef",
                      accepted_isa=("7.0", "8.8"), allowed_external_symbols=frozenset())
        with self.assertRaises(CallbackVerificationError):
            audit_ptx(ptx.replace(".address_size 64", ".extern .func evil();"),
                      abi_name="rtdl_v4_intersection_leaf_deadbeef",
                      accepted_isa=("7.0", "8.8"), allowed_external_symbols=frozenset())


if __name__ == "__main__":
    unittest.main()
