import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")

import rtdsl as rt


@rt.kernel(backend="rayjoin", precision="exact")
def join_kernel():
    segment_layout = rt.layout(
        "Segment2D",
        rt.field("x0", rt.f32),
        rt.field("y0", rt.f32),
        rt.field("x1", rt.f32),
        rt.field("y1", rt.f32),
        rt.field("id", rt.u32),
    )
    left = rt.input("left", rt.Segments, layout=segment_layout, role="probe")
    right = rt.input("right", rt.Segments, layout=segment_layout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=True))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


class RtDslPythonTest(unittest.TestCase):
    def test_compile_kernel(self) -> None:
        compiled = rt.compile_kernel(join_kernel)

        self.assertEqual(compiled.backend, "rayjoin")
        self.assertEqual(compiled.precision, "exact")
        self.assertEqual(len(compiled.inputs), 2)
        self.assertEqual(compiled.inputs[0].geometry.name, "segments")
        self.assertEqual(compiled.inputs[0].role, "probe")
        self.assertEqual(compiled.inputs[1].role, "build")
        self.assertEqual(compiled.inputs[0].layout.name, "Segment2D")
        self.assertEqual(
            compiled.emit_op.fields,
            ("left_id", "right_id", "intersection_point_x", "intersection_point_y"),
        )

    def test_formatted_output_mentions_lowering(self) -> None:
        compiled = rt.compile_kernel(join_kernel)
        formatted = compiled.format()

        self.assertIn("Compiled RT Kernel", formatted)
        self.assertIn("Lower traversal and refine stages", formatted)

    def test_lower_and_codegen(self) -> None:
        compiled = rt.compile_kernel(join_kernel)
        plan = rt.lower_to_rayjoin(compiled)
        output_dir = Path("build/generated_test")

        if output_dir.exists():
            shutil.rmtree(output_dir)

        generated = rt.generate_optix_project(plan, output_dir)

        self.assertEqual(plan.build_input.name, "right")
        self.assertEqual(plan.probe_input.name, "left")
        self.assertEqual(plan.output_record.name, "IntersectionRecord")
        self.assertEqual(plan.launch_params[0].name, "traversable")
        self.assertEqual(plan.payload_registers[0].name, "probe_index")
        self.assertEqual(plan.payload_registers[1].name, "build_primitive_index")
        self.assertEqual(plan.payload_registers[2].name, "hit_t_bits")
        self.assertTrue(generated["device"].exists())
        self.assertTrue(generated["host"].exists())
        self.assertTrue(generated["metadata"].exists())

        device_source = generated["device"].read_text(encoding="utf-8")
        self.assertIn("__raygen__rtdl_probe", device_source)
        self.assertIn("optixTrace(", device_source)
        self.assertIn("OptixTraversableHandle", device_source)
        self.assertIn("struct Segment2D", device_source)
        self.assertIn("struct IntersectionRecord", device_source)
        self.assertEqual(device_source.count("struct Segment2D"), 1)
        self.assertIn("rtdl_intersect_segments(", device_source)
        self.assertIn("fabsf(denom)", device_source)
        self.assertIn("params.left_segments[probe_index]", device_source)
        self.assertIn("params.right_segments[build_primitive_index]", device_source)
        self.assertIn("rtdl_store_record(probe.id, build.id, ix, iy);", device_source)

        metadata = generated["metadata"].read_text(encoding="utf-8")
        self.assertIn("\"payload_registers\"", metadata)
        self.assertIn("\"launch_params\"", metadata)
        self.assertIn("\"exact_refine_mode\"", metadata)
        self.assertIn("\"probe_index\"", metadata)
        self.assertIn("\"build_primitive_index\"", metadata)

    def test_lower_rejects_missing_segment_id(self) -> None:
        bad_layout = rt.layout(
            "BadSegment2D",
            rt.field("x0", rt.f32),
            rt.field("y0", rt.f32),
            rt.field("x1", rt.f32),
            rt.field("y1", rt.f32),
        )

        @rt.kernel(backend="rayjoin", precision="exact")
        def bad_kernel():
            left = rt.input("left", rt.Segments, layout=bad_layout, role="probe")
            right = rt.input("right", rt.Segments, layout=bad_layout, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=True))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        compiled = rt.compile_kernel(bad_kernel)

        with self.assertRaisesRegex(ValueError, "missing required fields: id"):
            rt.lower_to_rayjoin(compiled)


if __name__ == "__main__":
    unittest.main()
