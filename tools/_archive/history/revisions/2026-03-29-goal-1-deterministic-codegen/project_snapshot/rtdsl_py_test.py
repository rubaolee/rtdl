import json
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")

import rtdsl as rt


@rt.kernel(backend="rayjoin", precision="float_approx")
def county_zip_join():
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
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


class RtDslPythonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output_dir = Path("build/generated_test")
        cls.golden_dir = Path("tests/golden/county_zip_join")

    def _generate(self):
        compiled = rt.compile_kernel(county_zip_join)
        plan = rt.lower_to_rayjoin(compiled)

        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

        generated = rt.generate_optix_project(plan, self.output_dir)
        return compiled, plan, generated

    def test_compile_kernel(self) -> None:
        compiled = rt.compile_kernel(county_zip_join)

        self.assertEqual(compiled.backend, "rayjoin")
        self.assertEqual(compiled.precision, "float_approx")
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
        compiled = rt.compile_kernel(county_zip_join)
        formatted = compiled.format()

        self.assertIn("Compiled RT Kernel", formatted)
        self.assertIn("Lower traversal and refine stages", formatted)

    def test_lower_and_codegen(self) -> None:
        _, plan, generated = self._generate()

        self.assertEqual(plan.build_input.name, "right")
        self.assertEqual(plan.probe_input.name, "left")
        self.assertEqual(plan.output_record.name, "IntersectionRecord")
        self.assertEqual(plan.launch_params[0].name, "traversable")
        self.assertEqual(plan.launch_params[5].name, "output_capacity")
        self.assertEqual(plan.payload_registers[0].name, "probe_index")
        self.assertEqual(plan.payload_registers[1].name, "build_primitive_index")
        self.assertEqual(plan.payload_registers[2].name, "hit_t_bits")
        self.assertTrue(generated["device"].exists())
        self.assertTrue(generated["host"].exists())
        self.assertTrue(generated["metadata"].exists())

        metadata = generated["metadata"].read_text(encoding="utf-8")
        rt.validate_plan_dict(json.loads(metadata))

    def test_generated_artifacts_match_golden_files(self) -> None:
        _, _, generated = self._generate()

        expected_metadata = (self.golden_dir / "plan.json").read_text(encoding="utf-8")
        expected_device = (self.golden_dir / "device_kernels.cu").read_text(encoding="utf-8")
        expected_host = (self.golden_dir / "host_launcher.cpp").read_text(encoding="utf-8")

        self.assertEqual(expected_metadata, generated["metadata"].read_text(encoding="utf-8"))
        self.assertEqual(expected_device, generated["device"].read_text(encoding="utf-8"))
        self.assertEqual(expected_host, generated["host"].read_text(encoding="utf-8"))

    def test_plan_json_validates_against_schema(self) -> None:
        _, _, generated = self._generate()
        payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
        rt.validate_plan_dict(payload)

    def test_lower_rejects_missing_segment_id(self) -> None:
        bad_layout = rt.layout(
            "BadSegment2D",
            rt.field("x0", rt.f32),
            rt.field("y0", rt.f32),
            rt.field("x1", rt.f32),
            rt.field("y1", rt.f32),
        )

        @rt.kernel(backend="rayjoin", precision="float_approx")
        def bad_kernel():
            left = rt.input("left", rt.Segments, layout=bad_layout, role="probe")
            right = rt.input("right", rt.Segments, layout=bad_layout, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "missing required fields: id"):
            rt.compile_kernel(bad_kernel)

    def test_lower_rejects_exact_precision_claim(self) -> None:
        @rt.kernel(backend="rayjoin", precision="exact")
        def exact_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        compiled = rt.compile_kernel(exact_kernel)

        with self.assertRaisesRegex(ValueError, "precision='float_approx'"):
            rt.lower_to_rayjoin(compiled)

    def test_lower_rejects_unsupported_acceleration(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def accel_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="grid")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "accel='bvh'"):
            rt.lower_to_rayjoin(rt.compile_kernel(accel_kernel))

    def test_lower_rejects_unsupported_emit_field(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def emit_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "bbox_min_x"])

        with self.assertRaisesRegex(ValueError, "unsupported emitted field"):
            rt.lower_to_rayjoin(rt.compile_kernel(emit_kernel))

    def test_lower_rejects_unsupported_geometry_pair(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def geometry_kernel():
            left = rt.input("left", rt.Points, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "segment-vs-segment"):
            rt.lower_to_rayjoin(rt.compile_kernel(geometry_kernel))

    def test_compile_rejects_invalid_role(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def invalid_role_kernel():
            left = rt.input("left", rt.Segments, role="source")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "input role must be one of"):
            rt.compile_kernel(invalid_role_kernel)

    def test_compile_rejects_duplicate_input_names(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def duplicate_input_kernel():
            left = rt.input("items", rt.Segments, role="probe")
            right = rt.input("items", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "duplicate input name"):
            rt.compile_kernel(duplicate_input_kernel)

    def test_lower_rejects_duplicate_explicit_roles(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def duplicate_role_kernel():
            left = rt.input("left", rt.Segments, role="build")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(
                hits,
                fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
            )

        with self.assertRaisesRegex(ValueError, "cannot share the same explicit role"):
            rt.lower_to_rayjoin(rt.compile_kernel(duplicate_role_kernel))

    def test_compile_rejects_kernel_without_emit(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def incomplete_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            return rt.refine(candidates, predicate=rt.segment_intersection(exact=False))

        with self.assertRaisesRegex(TypeError, "kernel function must return rt.emit"):
            rt.compile_kernel(incomplete_kernel)


if __name__ == "__main__":
    unittest.main()
