import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")

import rtdsl as rt


def segment_layout():
    return rt.layout(
        "Segment2D",
        rt.field("x0", rt.f32),
        rt.field("y0", rt.f32),
        rt.field("x1", rt.f32),
        rt.field("y1", rt.f32),
        rt.field("id", rt.u32),
    )


def point_layout():
    return rt.layout(
        "Point2D",
        rt.field("x", rt.f32),
        rt.field("y", rt.f32),
        rt.field("id", rt.u32),
    )


def polygon_layout():
    return rt.layout(
        "Polygon2DRef",
        rt.field("vertex_offset", rt.u32),
        rt.field("vertex_count", rt.u32),
        rt.field("id", rt.u32),
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def county_zip_join():
    left = rt.input("left", rt.Segments, layout=segment_layout(), role="probe")
    right = rt.input("right", rt.Segments, layout=segment_layout(), role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


@rt.kernel(backend="rtdl", precision="float_approx")
def point_in_counties():
    points = rt.input("points", rt.Points, layout=point_layout(), role="probe")
    polygons = rt.input("polygons", rt.Polygons, layout=polygon_layout(), role="build")
    candidates = rt.traverse(points, polygons, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
    return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])


@rt.kernel(backend="rtdl", precision="float_approx")
def county_soil_overlay():
    left = rt.input("left", rt.Polygons, layout=polygon_layout(), role="probe")
    right = rt.input("right", rt.Polygons, layout=polygon_layout(), role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    seeds = rt.refine(candidates, predicate=rt.overlay_compose())
    return rt.emit(
        seeds,
        fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"],
    )


class RtDslPythonTest(unittest.TestCase):
    fixtures_dir = Path("tests/fixtures")

    def setUp(self) -> None:
        self.output_dir = Path(tempfile.mkdtemp(prefix="rtdsl_generated_test_", dir="build"))
        self.addCleanup(shutil.rmtree, self.output_dir, ignore_errors=True)

    def _generate(self, kernel_fn):
        compiled = rt.compile_kernel(kernel_fn)
        plan = rt.lower_to_execution_plan(compiled)
        target_dir = self.output_dir / compiled.name

        generated = rt.generate_optix_project(plan, target_dir)
        return compiled, plan, generated

    def test_compile_three_workloads(self) -> None:
        lsi = rt.compile_kernel(county_zip_join)
        pip = rt.compile_kernel(point_in_counties)
        overlay = rt.compile_kernel(county_soil_overlay)

        self.assertEqual(lsi.emit_op.fields, ("left_id", "right_id", "intersection_point_x", "intersection_point_y"))
        self.assertEqual(pip.emit_op.fields, ("point_id", "polygon_id", "contains"))
        self.assertEqual(overlay.emit_op.fields, ("left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"))

    def test_legacy_rayjoin_aliases_still_work(self) -> None:
        @rt.kernel(backend="rayjoin", precision="float_approx")
        def legacy_kernel():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Segments, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
            return rt.emit(hits, fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"])

        compiled = rt.compile_kernel(legacy_kernel)
        plan = rt.lower_to_rayjoin(compiled)

        self.assertEqual(compiled.backend, "rayjoin")
        self.assertEqual(plan.backend, "rtdl")

    def test_lower_three_workloads(self) -> None:
        _, lsi_plan, _ = self._generate(county_zip_join)
        _, pip_plan, _ = self._generate(point_in_counties)
        _, overlay_plan, _ = self._generate(county_soil_overlay)

        self.assertEqual(lsi_plan.workload_kind, "lsi")
        self.assertEqual(pip_plan.workload_kind, "pip")
        self.assertEqual(overlay_plan.workload_kind, "overlay")
        self.assertEqual(pip_plan.build_input.geometry.name, "polygons")
        self.assertEqual(pip_plan.probe_input.geometry.name, "points")
        self.assertIn("compose", overlay_plan.exact_refine_mode)

    def test_generated_artifacts_match_golden_files(self) -> None:
        for kernel_name, kernel_fn in (
            ("county_zip_join", county_zip_join),
            ("point_in_counties", point_in_counties),
            ("county_soil_overlay", county_soil_overlay),
        ):
            _, _, generated = self._generate(kernel_fn)
            golden_dir = Path("tests/golden") / kernel_name

            self.assertEqual(
                (golden_dir / "plan.json").read_text(encoding="utf-8"),
                generated["metadata"].read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (golden_dir / "device_kernels.cu").read_text(encoding="utf-8"),
                generated["device"].read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (golden_dir / "host_launcher.cpp").read_text(encoding="utf-8"),
                generated["host"].read_text(encoding="utf-8"),
            )

    def test_plan_json_validates_against_schema(self) -> None:
        for kernel_fn in (county_zip_join, point_in_counties, county_soil_overlay):
            _, _, generated = self._generate(kernel_fn)
            payload = json.loads(generated["metadata"].read_text(encoding="utf-8"))
            rt.validate_plan_dict(payload)

    def test_rayjoin_cdb_parser_and_views(self) -> None:
        county = rt.load_cdb(self.fixtures_dir / "rayjoin/br_county_subset.cdb")
        soil = rt.load_cdb(self.fixtures_dir / "rayjoin/br_soil_subset.cdb")

        self.assertEqual(county.name, "br_county_subset")
        self.assertEqual(len(county.chains), 3)
        self.assertEqual(len(soil.chains), 2)
        self.assertEqual(len(rt.chains_to_segments(county, limit_chains=2)), 26)
        self.assertEqual(len(rt.chains_to_probe_points(soil)), 2)
        self.assertEqual(len(rt.chains_to_polygon_refs(county)), 2)
        self.assertEqual(len(rt.chains_to_polygon_refs(soil)), 4)

    def test_reference_lsi_pip_overlay(self) -> None:
        left_segments = (
            rt.Segment(id=1, x0=0.0, y0=0.0, x1=2.0, y1=2.0),
        )
        right_segments = (
            rt.Segment(id=2, x0=0.0, y0=2.0, x1=2.0, y1=0.0),
        )
        lsi_hits = rt.lsi_cpu(left_segments, right_segments)
        self.assertEqual(lsi_hits[0]["left_id"], 1)
        self.assertEqual(lsi_hits[0]["right_id"], 2)

        points = (
            rt.Point(id=10, x=0.5, y=0.5),
            rt.Point(id=11, x=5.0, y=5.0),
        )
        polygons = (
            rt.Polygon(id=20, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),
        )
        pip_hits = rt.pip_cpu(points, polygons)
        self.assertEqual(pip_hits[0]["contains"], 1)
        self.assertEqual(pip_hits[1]["contains"], 0)

        overlay_hits = rt.overlay_compose_cpu(
            (rt.Polygon(id=1, vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))),),
            (rt.Polygon(id=2, vertices=((1.0, -1.0), (3.0, -1.0), (3.0, 1.0), (1.0, 1.0))),),
        )
        self.assertEqual(overlay_hits[0]["left_polygon_id"], 1)
        self.assertEqual(overlay_hits[0]["right_polygon_id"], 2)
        self.assertEqual(overlay_hits[0]["requires_lsi"], 1)

    def test_reference_pip_ignores_degenerate_closing_edge_for_outside_point(self) -> None:
        points = (
            rt.Point(id=10, x=3.0, y=3.0),
        )
        polygons = (
            rt.Polygon(
                id=20,
                vertices=((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0), (0.0, 0.0)),
            ),
        )

        python_rows = rt.pip_cpu(points, polygons)
        native_rows = rt.run_cpu(point_in_counties, points=points, polygons=polygons)

        self.assertEqual(python_rows, ({"point_id": 10, "polygon_id": 20, "contains": 0},))
        self.assertEqual(native_rows, python_rows)

    def test_reference_pip_rejects_near_collinear_outside_point_on_short_edge(self) -> None:
        points = (
            rt.Point(id=10, x=0.0005, y=-0.000001),
        )
        polygons = (
            rt.Polygon(
                id=20,
                vertices=((0.0, 0.0), (0.001, 0.0), (0.001, 1.0), (0.0, 1.0), (0.0, 0.0)),
            ),
        )

        python_rows = rt.pip_cpu(points, polygons)
        native_rows = rt.run_cpu(point_in_counties, points=points, polygons=polygons)

        self.assertEqual(python_rows, ({"point_id": 10, "polygon_id": 20, "contains": 0},))
        self.assertEqual(native_rows, python_rows)

    def test_reference_pip_rejects_near_collinear_point_past_tiny_segment_endpoint(self) -> None:
        points = (
            rt.Point(id=10, x=-122.840168, y=38.863527),
        )
        polygons = (
            rt.Polygon(
                id=20,
                vertices=(
                    (-122.840126, 38.8632190000001),
                    (-122.840129, 38.8632410000001),
                    (-122.8401, 38.8635),
                    (-122.8404, 38.8635),
                    (-122.840126, 38.8632190000001),
                ),
            ),
        )

        python_rows = rt.pip_cpu(points, polygons)
        native_rows = rt.run_cpu(point_in_counties, points=points, polygons=polygons)

        self.assertEqual(python_rows, ({"point_id": 10, "polygon_id": 20, "contains": 0},))
        self.assertEqual(native_rows, python_rows)

    def test_lower_rejects_invalid_pip_boundary_mode(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_pip():
            points = rt.input("points", rt.Points, role="probe")
            polygons = rt.input("polygons", rt.Polygons, role="build")
            candidates = rt.traverse(points, polygons, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False, boundary_mode="exclusive"))
            return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])

        with self.assertRaisesRegex(ValueError, "boundary_mode='inclusive'"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_pip))

    def test_lower_rejects_wrong_pip_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_pip():
            left = rt.input("left", rt.Segments, role="probe")
            right = rt.input("right", rt.Polygons, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.point_in_polygon(exact=False))
            return rt.emit(hits, fields=["point_id", "polygon_id", "contains"])

        with self.assertRaisesRegex(ValueError, "polygon build input and point probe input"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_pip))

    def test_lower_rejects_wrong_overlay_geometry(self) -> None:
        @rt.kernel(backend="rtdl", precision="float_approx")
        def bad_overlay():
            left = rt.input("left", rt.Points, role="probe")
            right = rt.input("right", rt.Polygons, role="build")
            candidates = rt.traverse(left, right, accel="bvh")
            hits = rt.refine(candidates, predicate=rt.overlay_compose())
            return rt.emit(hits, fields=["left_polygon_id", "right_polygon_id", "requires_lsi", "requires_pip"])

        with self.assertRaisesRegex(ValueError, "polygon-vs-polygon"):
            rt.lower_to_execution_plan(rt.compile_kernel(bad_overlay))


if __name__ == "__main__":
    unittest.main()
