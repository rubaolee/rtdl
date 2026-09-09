from __future__ import annotations

import unittest

from rtdsl.v4_callback_cuda_inline_codegen import (
    CudaInlineLoweringError,
    cuda_inline_value,
    cuda_inline_view,
    lower_straight_line_effect_to_cuda,
)
from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_triangle_standard_library import compile_keyed_callback
from tests.goal5755_v4_typed_physical_schema_test import verified_callback
from experiments.v4_authored_particle.program import (
    FACE_FIRST_SOURCE,
    face_first_manifest,
)
from rtdsl import v4


class V4CallbackCudaInlineCodegenTest(unittest.TestCase):
    def test_f32_literal_is_emitted_as_exact_nvrtc_compatible_bits(self):
        verified = v4.verify_builtin_triangle_callback_source(
            FACE_FIRST_SOURCE, face_first_manifest())._callback
        function = verified.program.function_for_role(CallbackRole.MAKE_RAY)
        projection = lower_straight_line_effect_to_cuda(
            verified,
            function,
            {
                function.arguments[0].name: cuda_inline_value(
                    function.arguments[0].value_type, "query"),
                function.arguments[1].name: cuda_inline_view(
                    function.arguments[1].value_type,
                    tuple(f"column_{index}" for index in range(7)), "count"),
            },
            prefix="literal",
            failure_statement="fail(); return;",
        )
        self.assertEqual(
            projection.field("tmin"), ("__int_as_float(0x00000000u)",))

    def test_projection_uses_verified_structure_not_application_field_order(self):
        verified = verified_callback()
        function = verified.program.function_for_role(CallbackRole.CLOSEST_HIT)
        projection = lower_straight_line_effect_to_cuda(
            verified,
            function,
            {
                function.arguments[0].name: cuda_inline_value(
                    function.arguments[0].value_type,
                    "hit_t", "primitive", "kind", "bary_x", "bary_y",
                ),
                function.arguments[1].name: cuda_inline_value(
                    function.arguments[1].value_type,
                    "old_cell", "old_neighbor", "old_face",
                ),
                function.arguments[2].name: cuda_inline_view(
                    function.arguments[2].value_type,
                    ("front",), "primitive_count"),
                function.arguments[3].name: cuda_inline_view(
                    function.arguments[3].value_type,
                    ("back",), "primitive_count"),
            },
            prefix="different_callback",
            failure_statement="fail(); return;",
        )
        payload = projection.field("payload")
        emitted = "\n".join(projection.lines)
        self.assertTrue(payload[2].endswith("_let_4_2"))
        self.assertIn(f"{payload[2]} = primitive;", emitted)
        self.assertIn("front[primitive]", emitted)
        self.assertIn("back[primitive]", emitted)
        self.assertNotIn("neighbor_id", emitted)

    def test_control_flow_role_fails_closed_to_ordinary_leaf(self):
        verified = compile_keyed_callback()
        function = verified.program.function_for_role(CallbackRole.ANY_HIT)
        arguments = {
            function.arguments[0].name: cuda_inline_value(
                function.arguments[0].value_type,
                "hit_t", "primitive", "kind", "bary_x", "bary_y"),
            function.arguments[1].name: cuda_inline_value(
                function.arguments[1].value_type, "accepted"),
            function.arguments[2].name: cuda_inline_view(
                function.arguments[2].value_type, ("stable_ids",), "count"),
            function.arguments[3].name: cuda_inline_view(
                function.arguments[3].value_type, ("signed_values",), "count"),
            function.arguments[4].name: cuda_inline_view(
                function.arguments[4].value_type, ("include_flags",), "count"),
        }
        with self.assertRaisesRegex(
                CudaInlineLoweringError, "one final effect"):
            lower_straight_line_effect_to_cuda(
                verified,
                function,
                arguments,
                prefix="control_flow",
                failure_statement="fail(); return;",
            )


if __name__ == "__main__":
    unittest.main()
