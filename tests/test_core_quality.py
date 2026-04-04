"""
tests/test_core_quality.py

Comprehensive quality tests covering gaps in:
  - types.py:     Layout/Field validation and serialization
  - ir.py:        to_dict() and format() on all IR nodes
  - api.py:       predicate factory options, out-of-context errors, layout validation
  - lowering.py:  all error paths, role resolution, each _lower_* predicate
  - reference.py: geometric edge cases (parallel, boundary, degenerate, tie-breaking)
  - runtime.py:   input coercion, run_cpu_python_reference for all predicates
"""
import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.ir import CompiledKernel


@rt.kernel(backend="rtdl", precision="float_approx")
def _lsi_kernel():
    left = rt.input("left", rt.Segments, role="probe")
    right = rt.input("right", rt.Segments, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _pip_kernel():
    points = rt.input("points", rt.Points, role="probe")
    polygons = rt.input("polygons", rt.Polygons, role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _overlay_kernel():
    left = rt.input("left", rt.Polygons, role="probe")
    right = rt.input("right", rt.Polygons, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(seeds, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _ray_tri_kernel():
    rays = rt.input("rays", rt.Rays, role="probe")
    triangles = rt.input("triangles", rt.Triangles, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
    return rt.emit(hits, fields=["ray_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _seg_poly_kernel():
    polygons = rt.input("polygons", rt.Polygons, role="build")
    segments = rt.input("segments", rt.Segments, role="probe")
    candidates = rt.traverse(segments, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
    return rt.emit(hits, fields=["segment_id", "hit_count"])


@rt.kernel(backend="rtdl", precision="float_approx")
def _pns_kernel():
    points = rt.input("points", rt.Points, role="probe")
    segments = rt.input("segments", rt.Segments, role="build")
    candidates = rt.traverse(points, segments, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
    return rt.emit(hits, fields=["point_id", "segment_id", "distance"])


class TypesTest(unittest.TestCase):
    def test_layout_rejects_empty_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one field"):
            rt.layout("Empty")

    def test_layout_field_names(self) -> None:
        lay = rt.layout("T", rt.field("a", rt.f32), rt.field("b", rt.u32))
        self.assertEqual(lay.field_names(), ("a", "b"))

    def test_layout_require_fields_ok(self) -> None:
        lay = rt.layout("T", rt.field("x", rt.f32), rt.field("y", rt.f32), rt.field("id", rt.u32))
        lay.require_fields(("x", "y"))

    def test_layout_require_fields_missing_raises(self) -> None:
        lay = rt.layout("T", rt.field("x", rt.f32), rt.field("id", rt.u32))
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            lay.require_fields(("x", "y", "id"))

    def test_field_to_dict_structure(self) -> None:
        d = rt.field("myfield", rt.f32).to_dict()
        self.assertEqual(d["name"], "myfield")
        self.assertEqual(d["scalar_type"], "f32")
        self.assertEqual(d["c_type"], "float")
        self.assertEqual(d["cuda_type"], "float")
        self.assertEqual(d["size"], 4)

    def test_scalar_type_u32_properties(self) -> None:
        self.assertEqual(rt.u32.name, "u32")
        self.assertEqual(rt.u32.c_type, "uint32_t")
        self.assertEqual(rt.u32.size, 4)


class IrSerializationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.compiled = rt.compile_kernel(_lsi_kernel)
        self.plan = rt.lower_to_execution_plan(self.compiled)

    def test_geometry_input_to_dict_keys(self) -> None:
        d = self.compiled.inputs[0].to_dict()
        for key in ("name", "geometry", "layout", "role", "fields"):
            self.assertIn(key, d)
        self.assertIsInstance(d["fields"], list)

    def test_payload_register_to_dict_keys(self) -> None:
        d = self.plan.payload_registers[0].to_dict()
        self.assertEqual(d["index"], 0)
        self.assertIn("name", d)
        self.assertIn("encoding", d)

    def test_launch_param_to_dict_keys(self) -> None:
        d = self.plan.launch_params[0].to_dict()
        for key in ("name", "c_type", "role"):
            self.assertIn(key, d)

    def test_output_field_to_dict_keys(self) -> None:
        d = self.plan.output_record.fields[0].to_dict()
        self.assertIn("name", d)
        self.assertIn("c_type", d)

    def test_output_record_to_dict_keys(self) -> None:
        d = self.plan.output_record.to_dict()
        self.assertIn("name", d)
        self.assertIsInstance(d["fields"], list)
        self.assertGreater(len(d["fields"]), 0)

    def test_ray_spec_to_dict_keys(self) -> None:
        d = self.plan.ray_spec.to_dict()
        for key in ("origin", "direction", "tmin", "tmax", "description"):
            self.assertIn(key, d)
        self.assertIsInstance(d["origin"], list)
        self.assertEqual(len(d["origin"]), 3)

    def test_execution_plan_to_dict_schema_and_fields(self) -> None:
        d = self.plan.to_dict()
        self.assertIn("$schema", d)
        self.assertEqual(d["schema_version"], "v1alpha1")
        self.assertEqual(d["workload_kind"], "lsi")
        for key in ("payload_registers", "launch_params", "buffers", "output_record", "ray_spec"):
            self.assertIn(key, d)

    def test_execution_plan_format_sections(self) -> None:
        text = self.plan.format()
        for section in ("RTDL Backend Plan", "Payload Registers", "Launch Params", "Buffers", "Ray Spec", "Host Steps", "Device Programs"):
            self.assertIn(section, text, msg=f"missing section: {section}")
        self.assertIn("lsi", text)

    def test_compiled_kernel_format_sections(self) -> None:
        text = self.compiled.format()
        for section in ("Compiled RT Kernel", "Lowering Plan"):
            self.assertIn(section, text, msg=f"missing section: {section}")
        self.assertIn(self.compiled.name, text)

    def test_compiled_kernel_format_unspecified_role(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def no_role_kernel():
            left = rt.input("left", rt.Segments)
            right = rt.input("right", rt.Segments)
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        self.assertIn("unspecified", rt.compile_kernel(no_role_kernel).format())


class ApiTest(unittest.TestCase):
    def test_compile_kernel_rejects_non_callable(self) -> None:
        with self.assertRaisesRegex(TypeError, "compile_kernel expects a kernel function"):
            rt.compile_kernel(42)

    def test_input_outside_context_raises(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "inside @rt.kernel"):
            rt.input("x", rt.Segments)

    def test_traverse_outside_context_raises(self) -> None:
        from rtdsl.ir import GeometryInput

        dummy = GeometryInput(name="x", geometry=rt.Segments, layout=rt.Segment2DLayout)
        with self.assertRaisesRegex(RuntimeError, "inside @rt.kernel"):
            rt.traverse(dummy, dummy)

    def test_emit_outside_context_raises(self) -> None:
        from rtdsl.ir import CandidateSet, GeometryInput, Predicate, RefineOp

        gi = GeometryInput(name="x", geometry=rt.Segments, layout=rt.Segment2DLayout)
        cs = CandidateSet(left=gi, right=gi, accel="bvh")
        refine_op = RefineOp(
            candidates=cs,
            predicate=Predicate(name="segment_intersection", options={"exact": False}),
        )
        with self.assertRaisesRegex(RuntimeError, "inside @rt.kernel"):
            rt.emit(refine_op, fields=["left_id"])

    def test_input_with_layout_missing_required_fields_raises(self) -> None:
        incomplete = rt.layout("Bad", rt.field("x0", rt.f32), rt.field("id", rt.u32))

        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_layout():
            left = rt.input("left", rt.Segments, layout=incomplete, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "missing required fields"):
            rt.compile_kernel(bad_layout)

    def test_segment_intersection_predicate_options(self) -> None:
        p = rt.segment_intersection(exact=False)
        self.assertEqual(p.name, "segment_intersection")
        self.assertIs(p.options["exact"], False)
        self.assertIs(rt.segment_intersection(exact=True).options["exact"], True)

    def test_point_in_polygon_predicate_options(self) -> None:
        p = rt.point_in_polygon(exact=False, boundary_mode="inclusive")
        self.assertEqual(p.name, "point_in_polygon")
        self.assertEqual(p.options["boundary_mode"], "inclusive")

    def test_contains_alias_matches_point_in_polygon(self) -> None:
        self.assertEqual(
            rt.contains(exact=False, boundary_mode="inclusive"),
            rt.point_in_polygon(exact=False, boundary_mode="inclusive"),
        )

    def test_ray_triangle_hit_count_predicate_options(self) -> None:
        p = rt.ray_triangle_hit_count(exact=False)
        self.assertEqual(p.name, "ray_triangle_hit_count")
        self.assertIs(p.options["exact"], False)

    def test_segment_polygon_hitcount_predicate_options(self) -> None:
        p = rt.segment_polygon_hitcount(exact=False)
        self.assertEqual(p.name, "segment_polygon_hitcount")
        self.assertIs(p.options["exact"], False)

    def test_point_nearest_segment_predicate_options(self) -> None:
        p = rt.point_nearest_segment(exact=False)
        self.assertEqual(p.name, "point_nearest_segment")
        self.assertIs(p.options["exact"], False)

    def test_overlay_compose_predicate_options(self) -> None:
        p = rt.overlay_compose()
        self.assertEqual(p.name, "overlay_compose")
        self.assertEqual(p.options, {})


class LoweringTest(unittest.TestCase):
    def _incomplete_kernel(self) -> CompiledKernel:
        return CompiledKernel(
            name="incomplete",
            backend="rtdl",
            precision="float_approx",
            inputs=(),
            candidates=None,
            refine_op=None,
            emit_op=None,
        )

    def test_lower_rejects_unsupported_backend(self) -> None:
        @rt.kernel(backend="cuda", precision="float_approx")
        def cuda_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "unsupported backend"):
            rt.lower_to_execution_plan(rt.compile_kernel(cuda_kernel))

    def test_lower_rejects_incomplete_kernel(self) -> None:
        with self.assertRaisesRegex(ValueError, "incomplete"):
            rt.lower_to_execution_plan(self._incomplete_kernel())

    def test_lower_rejects_non_bvh_accel(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def hash_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="hash")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "accel='bvh'"):
            rt.lower_to_execution_plan(rt.compile_kernel(hash_kernel))

    def test_lower_rejects_non_float_approx_precision(self) -> None:
        @rt.kernel(backend="rtdl", precision="exact")
        def exact_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "float_approx"):
            rt.lower_to_execution_plan(rt.compile_kernel(exact_kernel))

    def test_lower_lsi_rejects_non_segment_inputs(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_lsi():
            left = rt.input("left", rt.Points, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "segment-vs-segment"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_lsi))

    def test_lower_lsi_rejects_exact_true(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def exact_lsi():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=True))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "float-based"):
            rt.lower_to_execution_plan(rt.compile_kernel(exact_lsi))

    def test_lower_segment_polygon_hitcount_rejects_wrong_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_sph():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_polygon_hitcount(exact=False))
            return rt.emit(hits, fields=["segment_id", "hit_count"])

        with self.assertRaisesRegex(ValueError, "polygon build input and segment probe input"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_sph))

    def test_lower_point_nearest_segment_rejects_wrong_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_pns():
            left = rt.input("left", rt.Points, role="probe")
            right = rt.input("right", rt.Points, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.point_nearest_segment(exact=False))
            return rt.emit(hits, fields=["point_id", "segment_id", "distance"])

        with self.assertRaisesRegex(ValueError, "segment build input and point probe input"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_pns))

    def test_lower_ray_triangle_hitcount_rejects_wrong_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_rth():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=False))
            return rt.emit(hits, fields=["ray_id", "hit_count"])

        with self.assertRaisesRegex(ValueError, "triangle build input and ray probe input"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_rth))

    def test_lower_ray_triangle_hitcount_rejects_exact_true(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def exact_rth():
            rays = rt.input("rays", rt.Rays, role="probe")
            triangles = rt.input("triangles", rt.Triangles, role="build")
            candidates = rt.traverse(rays, triangles, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.ray_triangle_hit_count(exact=True))
            return rt.emit(hits, fields=["ray_id", "hit_count"])

        with self.assertRaisesRegex(ValueError, "float-based"):
            rt.lower_to_execution_plan(rt.compile_kernel(exact_rth))

    def test_build_output_record_rejects_empty_emit_fields(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def empty_emit():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=[])

        with self.assertRaisesRegex(ValueError, "at least one field"):
            rt.lower_to_execution_plan(rt.compile_kernel(empty_emit))

    def test_build_output_record_rejects_unsupported_field_name(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_field():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["not_a_real_field"])

        with self.assertRaisesRegex(ValueError, "unsupported emitted field"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_field))

    def test_choose_roles_both_same_explicit_role_raises(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def both_build():
            left = rt.input("left", rt.Segments, role="build")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        with self.assertRaisesRegex(ValueError, "cannot share the same explicit role"):
            rt.lower_to_execution_plan(rt.compile_kernel(both_build))

    def test_choose_roles_explicit_probe_left_build_right(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def probe_left():
            left = rt.input("segs_a", rt.Segments, role="probe")
            right = rt.input("segs_b", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id"])

        plan = rt.lower_to_execution_plan(rt.compile_kernel(probe_left))
        self.assertEqual(plan.build_input.name, "segs_b")
        self.assertEqual(plan.probe_input.name, "segs_a")

    def test_choose_roles_geometry_fallback_polygons_are_build(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(_pip_kernel))
        self.assertEqual(plan.build_input.geometry.name, "polygons")
        self.assertEqual(plan.probe_input.geometry.name, "points")

    def test_lower_lsi_plan(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(_lsi_kernel))
        self.assertEqual(plan.workload_kind, "lsi")
        self.assertEqual(plan.backend, "rtdl")
        self.assertIn("left_id", plan.emit_fields)
        self.assertIn("right_id", plan.emit_fields)

    def test_lower_point_nearest_segment_plan(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(_pns_kernel))
        self.assertEqual(plan.workload_kind, "point_nearest_segment")
        self.assertIn("distance", plan.emit_fields)
        self.assertEqual(plan.build_input.geometry.name, "segments")
        self.assertEqual(plan.probe_input.geometry.name, "points")

    def test_lower_segment_polygon_hitcount_plan(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(_seg_poly_kernel))
        self.assertEqual(plan.workload_kind, "segment_polygon_hitcount")
        self.assertIn("hit_count", plan.emit_fields)

    def test_lower_ray_triangle_hitcount_plan(self) -> None:
        plan = rt.lower_to_execution_plan(rt.compile_kernel(_ray_tri_kernel))
        self.assertEqual(plan.workload_kind, "ray_tri_hitcount")
        self.assertEqual(plan.build_input.geometry.name, "triangles")
        self.assertEqual(plan.probe_input.geometry.name, "rays")

    def test_lower_to_rayjoin_alias_produces_same_plan(self) -> None:
        plan = rt.lower_to_rayjoin(rt.compile_kernel(_lsi_kernel))
        self.assertEqual(plan.workload_kind, "lsi")


class ReferenceGeometryTest(unittest.TestCase):
    def test_lsi_crossing_produces_one_hit_at_midpoint(self) -> None:
        rows = rt.lsi_cpu(
            (rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),),
            (rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),),
        )
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["intersection_point_x"], 1.0, places=5)
        self.assertAlmostEqual(rows[0]["intersection_point_y"], 1.0, places=5)

    def test_lsi_parallel_horizontal_no_hit(self) -> None:
        rows = rt.lsi_cpu(
            (rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=0.0),),
            (rt.Segment(id=2, x0=0.0, y0=1.0, x1=2.0, y1=1.0),),
        )
        self.assertEqual(len(rows), 0)

    def test_lsi_non_overlapping_collinear_no_hit(self) -> None:
        rows = rt.lsi_cpu(
            (rt.Segment(id=1, x0=0.0, y0=0.0, x1=1.0, y1=0.0),),
            (rt.Segment(id=2, x0=2.0, y0=0.0, x1=3.0, y1=0.0),),
        )
        self.assertEqual(len(rows), 0)

    def test_lsi_segments_that_do_not_reach_each_other_no_hit(self) -> None:
        rows = rt.lsi_cpu(
            (rt.Segment(id=1, x0=0.0, y0=0.0, x1=1.0, y1=0.0),),
            (rt.Segment(id=2, x0=5.0, y0=-1.0, x1=5.0, y1=1.0),),
        )
        self.assertEqual(len(rows), 0)

    def test_lsi_empty_inputs_return_empty(self) -> None:
        self.assertEqual(rt.lsi_cpu((), ()), ())
        self.assertEqual(rt.lsi_cpu((rt.Segment(id=1, x0=0.0, y0=0.0, x1=1.0, y1=0.0),), ()), ())

    def test_lsi_two_probe_segments_one_hit_each(self) -> None:
        left = (
            rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),
            rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),
        )
        right = (rt.Segment(id=3, x0=1.0, y0=-1.0, x1=1.0, y1=3.0),)
        rows = rt.lsi_cpu(left, right)
        self.assertEqual(len(rows), 2)

    def test_pip_point_inside(self) -> None:
        rows = rt.pip_cpu(
            (rt.Point(id=10, x=1.0, y=1.0),),
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0))),),
        )
        self.assertEqual(rows[0]["contains"], 1)

    def test_pip_point_outside(self) -> None:
        rows = rt.pip_cpu(
            (rt.Point(id=10, x=5.0, y=5.0),),
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["contains"], 0)

    def test_pip_point_on_edge_is_inclusive(self) -> None:
        rows = rt.pip_cpu(
            (rt.Point(id=10, x=1.0, y=0.0),),
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["contains"], 1)

    def test_pip_cartesian_product_shape(self) -> None:
        pts = (rt.Point(id=1, x=1.0, y=1.0), rt.Point(id=2, x=4.0, y=1.0))
        polys = (
            rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
            rt.Polygon(id=20, vertices=((3.0, 0.0), (5.0, 0.0), (5.0, 2.0), (3.0, 2.0))),
        )
        rows = rt.pip_cpu(pts, polys)
        self.assertEqual(len(rows), 4)
        mapping = {(r["point_id"], r["polygon_id"]): r["contains"] for r in rows}
        self.assertEqual(mapping[(1, 10)], 1)
        self.assertEqual(mapping[(1, 20)], 0)
        self.assertEqual(mapping[(2, 10)], 0)
        self.assertEqual(mapping[(2, 20)], 1)

    def test_pns_perpendicular_foot_distance(self) -> None:
        rows = rt.point_nearest_segment_cpu(
            (rt.Point(id=1, x=1.0, y=1.0),),
            (rt.Segment(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0),),
        )
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["distance"], 1.0, places=5)
        self.assertEqual(rows[0]["segment_id"], 10)

    def test_pns_endpoint_clamping(self) -> None:
        rows = rt.point_nearest_segment_cpu(
            (rt.Point(id=1, x=3.0, y=0.0),),
            (rt.Segment(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0),),
        )
        self.assertAlmostEqual(rows[0]["distance"], 1.0, places=5)

    def test_pns_degenerate_zero_length_segment(self) -> None:
        rows = rt.point_nearest_segment_cpu(
            (rt.Point(id=1, x=3.0, y=4.0),),
            (rt.Segment(id=5, x0=0.0, y0=0.0, x1=0.0, y1=0.0),),
        )
        self.assertAlmostEqual(rows[0]["distance"], 5.0, places=5)

    def test_pns_empty_segments_returns_no_rows(self) -> None:
        rows = rt.point_nearest_segment_cpu((rt.Point(id=1, x=1.0, y=1.0),), ())
        self.assertEqual(len(rows), 0)

    def test_pns_tie_breaking_selects_lower_id(self) -> None:
        rows = rt.point_nearest_segment_cpu(
            (rt.Point(id=1, x=0.0, y=1.0),),
            (
                rt.Segment(id=20, x0=-1.0, y0=0.0, x1=1.0, y1=0.0),
                rt.Segment(id=10, x0=-1.0, y0=0.0, x1=1.0, y1=0.0),
            ),
        )
        self.assertEqual(rows[0]["segment_id"], 10)

    def test_ray_triangle_miss(self) -> None:
        rows = rt.ray_triangle_hit_count_cpu(
            (rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=1.0),),
            (rt.Triangle(id=10, x0=5.0, y0=-1.0, x1=6.0, y1=1.0, x2=7.0, y2=-1.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 0)

    def test_ray_triangle_hit(self) -> None:
        rows = rt.ray_triangle_hit_count_cpu(
            (rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),),
            (rt.Triangle(id=10, x0=3.0, y0=-1.0, x1=4.0, y1=1.0, x2=5.0, y2=-1.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)

    def test_ray_origin_inside_triangle_counts_as_hit(self) -> None:
        rows = rt.ray_triangle_hit_count_cpu(
            (rt.Ray2D(id=1, ox=2.0, oy=0.0, dx=0.0, dy=1.0, tmax=5.0),),
            (rt.Triangle(id=10, x0=0.0, y0=-2.0, x1=4.0, y1=-2.0, x2=2.0, y2=3.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)

    def test_ray_hitcount_two_rays_different_outcomes(self) -> None:
        rays = (
            rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=5.0),
            rt.Ray2D(id=2, ox=0.0, oy=5.0, dx=1.0, dy=0.0, tmax=5.0),
        )
        triangles = (rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),)
        rows = rt.ray_triangle_hit_count_cpu(rays, triangles)
        hit_map = {r["ray_id"]: r["hit_count"] for r in rows}
        self.assertEqual(hit_map[1], 1)
        self.assertEqual(hit_map[2], 0)

    def test_sph_segment_inside_polygon_hits(self) -> None:
        rows = rt.segment_polygon_hitcount_cpu(
            (rt.Segment(id=1, x0=1.0, y0=1.0, x1=2.0, y1=2.0),),
            (rt.Polygon(id=10, vertices=((0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0))),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)

    def test_sph_segment_crossing_polygon_hits(self) -> None:
        rows = rt.segment_polygon_hitcount_cpu(
            (rt.Segment(id=1, x0=-1.0, y0=1.0, x1=3.0, y1=1.0),),
            (rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)

    def test_sph_segment_outside_polygon_no_hit(self) -> None:
        rows = rt.segment_polygon_hitcount_cpu(
            (rt.Segment(id=1, x0=5.0, y0=0.0, x1=6.0, y1=0.0),),
            (rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["hit_count"], 0)

    def test_overlay_non_overlapping_polygons(self) -> None:
        rows = rt.overlay_compose_cpu(
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))),),
            (rt.Polygon(id=2, vertices=((5.0, 0.0), (6.0, 0.0), (6.0, 1.0), (5.0, 1.0))),),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["requires_lsi"], 0)
        self.assertEqual(rows[0]["requires_pip"], 0)

    def test_overlay_crossing_polygons_requires_lsi(self) -> None:
        rows = rt.overlay_compose_cpu(
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
            (rt.Polygon(id=2, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),),
        )
        self.assertEqual(rows[0]["requires_lsi"], 1)


class RuntimeInputNormalizationTest(unittest.TestCase):
    def test_segment_from_dict_accepted(self) -> None:
        rows = rt.run_cpu_python_reference(
            _lsi_kernel,
            left=({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 2.0, "y1": 2.0},),
            right=({"id": 2, "x0": 0.0, "y0": 2.0, "x1": 2.0, "y1": 0.0},),
        )
        self.assertEqual(len(rows), 1)

    def test_segment_missing_field_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing fields"):
            rt.run_cpu(_lsi_kernel, left=({"id": 1, "x0": 0.0, "y0": 0.0, "x1": 1.0},), right=())

    def test_point_from_dataclass_accepted(self) -> None:
        rows = rt.run_cpu_python_reference(
            _pip_kernel,
            points=(rt.Point(id=1, x=0.5, y=0.5),),
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["contains"], 1)

    def test_point_missing_field_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing fields"):
            rt.run_cpu(_pip_kernel, points=({"id": 1, "x": 0.5},), polygons=())

    def test_polygon_non_iterable_vertices_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "iterable `vertices`"):
            rt.run_cpu(
                _pip_kernel,
                points=({"id": 1, "x": 0.0, "y": 0.0},),
                polygons=({"id": 10, "vertices": 999},),
            )

    def test_polygon_vertex_wrong_dimension_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "2 coordinates"):
            rt.run_cpu(
                _pip_kernel,
                points=({"id": 1, "x": 0.0, "y": 0.0},),
                polygons=({"id": 10, "vertices": ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.5, 1.0, 0.0))},),
            )

    def test_string_input_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be an iterable of records"):
            rt.run_cpu(_lsi_kernel, left="hello", right=())

    def test_non_iterable_input_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be an iterable of records"):
            rt.run_cpu(_lsi_kernel, left=42, right=())

    def test_opaque_object_record_raises(self) -> None:
        class _Opaque:
            pass

        with self.assertRaisesRegex(ValueError, "mapping or dataclass"):
            rt.run_cpu(_lsi_kernel, left=(_Opaque(),), right=())

    def test_triangle_from_dict_accepted(self) -> None:
        rows = rt.run_cpu_python_reference(
            _ray_tri_kernel,
            rays=(rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),),
            triangles=({"id": 10, "x0": 3.0, "y0": -1.0, "x1": 4.0, "y1": 1.0, "x2": 5.0, "y2": -1.0},),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["hit_count"], 1)

    def test_ray_from_dict_accepted(self) -> None:
        rows = rt.run_cpu_python_reference(
            _ray_tri_kernel,
            rays=({"id": 1, "ox": 0.0, "oy": 0.0, "dx": 1.0, "dy": 0.0, "tmax": 5.0},),
            triangles=(rt.Triangle(id=10, x0=2.0, y0=-1.0, x1=3.0, y1=1.0, x2=4.0, y2=-1.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)


class RunCpuPythonReferenceTest(unittest.TestCase):
    def test_lsi(self) -> None:
        rows = rt.run_cpu_python_reference(
            _lsi_kernel,
            left=(rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),),
            right=(rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),),
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["left_id"], 1)
        self.assertEqual(rows[0]["right_id"], 2)
        self.assertEqual(tuple(rows[0].keys()), ("left_id", "right_id", "intersection_point_x", "intersection_point_y"))

    def test_pip(self) -> None:
        rows = rt.run_cpu_python_reference(
            _pip_kernel,
            points=(rt.Point(id=10, x=1.0, y=1.0),),
            polygons=(rt.Polygon(id=20, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
        )
        self.assertEqual(rows[0]["contains"], 1)
        self.assertEqual(tuple(rows[0].keys()), ("point_id", "polygon_id", "contains"))

    def test_overlay(self) -> None:
        rows = rt.run_cpu_python_reference(
            _overlay_kernel,
            left=(rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
            right=(rt.Polygon(id=2, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),),
        )
        self.assertEqual(rows[0]["requires_lsi"], 1)

    def test_ray_triangle_hitcount(self) -> None:
        rows = rt.run_cpu_python_reference(
            _ray_tri_kernel,
            rays=(rt.Ray2D(id=1, ox=0.0, oy=0.0, dx=1.0, dy=0.0, tmax=10.0),),
            triangles=(rt.Triangle(id=10, x0=3.0, y0=-1.0, x1=4.0, y1=1.0, x2=5.0, y2=-1.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)
        self.assertEqual(tuple(rows[0].keys()), ("ray_id", "hit_count"))

    def test_segment_polygon_hitcount(self) -> None:
        rows = rt.run_cpu_python_reference(
            _seg_poly_kernel,
            polygons=(rt.Polygon(id=10, vertices=((0.0, 0.0), (5.0, 0.0), (5.0, 5.0), (0.0, 5.0))),),
            segments=(rt.Segment(id=1, x0=1.0, y0=1.0, x1=2.0, y1=2.0),),
        )
        self.assertEqual(rows[0]["hit_count"], 1)
        self.assertEqual(tuple(rows[0].keys()), ("segment_id", "hit_count"))

    def test_point_nearest_segment(self) -> None:
        rows = rt.run_cpu_python_reference(
            _pns_kernel,
            points=(rt.Point(id=1, x=1.0, y=1.0),),
            segments=(rt.Segment(id=10, x0=0.0, y0=0.0, x1=2.0, y1=0.0),),
        )
        self.assertAlmostEqual(rows[0]["distance"], 1.0, places=5)
        self.assertEqual(rows[0]["segment_id"], 10)
        self.assertEqual(tuple(rows[0].keys()), ("point_id", "segment_id", "distance"))

    def test_missing_inputs_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing RTDL simulator inputs"):
            rt.run_cpu_python_reference(_lsi_kernel, left=())

    def test_unexpected_inputs_raises(self) -> None:
        with self.assertRaisesRegex(ValueError, "unexpected RTDL simulator inputs"):
            rt.run_cpu_python_reference(_lsi_kernel, left=(), right=(), extra=())


if __name__ == "__main__":
    unittest.main()
