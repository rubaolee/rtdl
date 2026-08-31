from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3262ClosedShapePreparedEdgeLayoutTest(unittest.TestCase):
    def test_kernel_has_prepared_edge_column_path_and_split_vertex_fallback(self) -> None:
        text = CORE.read_text(encoding="utf-8")
        start = text.index("static __forceinline__ __device__ bool point_in_polygon(")
        end = text.index('extern "C" __global__ void __raygen__pip_probe()', start)
        body = text[start:end]

        self.assertIn("struct GpuPreparedClosedShapeEdge2D", text)
        self.assertIn("const GpuPreparedClosedShapeEdge2D* prepared_edges;", text)
        self.assertIn("if (params.prepared_edges != nullptr)", body)
        self.assertIn("const GpuPreparedClosedShapeEdge2D edge = params.prepared_edges[off + i];", body)
        self.assertIn("edge.crossing_scale * (py - by) + bx", body)
        self.assertIn("float ax = params.vertices_x[off + j];", body)
        self.assertIn("float ay = params.vertices_y[off + j];", body)
        self.assertLess(body.index("params.prepared_edges != nullptr"), body.index("params.vertices_x[off + j]"))

    def test_prepared_handle_builds_and_uploads_generic_edge_columns(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("struct PreparedShapePairRelationBuild")
        end = text.index("static PreparedShapePairRelationBuild* prepare_point_closed_shape_membership_2d_optix", start)
        body = text[start:end]

        for phrase in (
            "std::vector<GpuPreparedClosedShapeEdge2D> right_edges;",
            "DevPtr d_right_edges;",
            "right_edges(vert_xy_count / 2u)",
            "d_right_edges(sizeof(GpuPreparedClosedShapeEdge2D) * (vert_xy_count / 2u))",
            "right_edges[off + i] = {",
            "dx * dx + dy * dy",
            "(ax - bx) / (ay_minus_by != 0.0f ? ay_minus_by : point_eps_den)",
            "upload(d_right_edges.ptr, right_edges.data(), right_edges.size())",
        ):
            self.assertIn(phrase, body)

    def test_prepared_edge_layout_is_explicitly_opt_in_for_prepared_launches(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")

        self.assertEqual(text.count("lp.prepared_edges = nullptr;"), 1)
        self.assertIn("static bool use_prepared_closed_shape_edge_layout()", text)
        self.assertIn("RTDL_OPTIX_POINT_PRIMITIVE_USE_PREPARED_EDGE_LAYOUT", text)
        self.assertEqual(text.count("use_prepared_closed_shape_edge_layout()"), 4)
        self.assertEqual(
            text.count(
                "reinterpret_cast<const GpuPreparedClosedShapeEdge2D*>(prepared->d_right_edges.ptr)\n"
                "        : nullptr;"
            ),
            3,
        )

        for function_name in (
            "run_prepared_point_closed_shape_membership_2d_optix",
            "count_prepared_point_closed_shape_membership_2d_optix",
            "count_prepared_point_closed_shape_membership_device_filtered_2d_optix",
        ):
            start = text.index(f"static void {function_name}")
            end = text.find("static ", start + 1)
            if end == -1:
                end = len(text)
            body = text[start:end]
            self.assertIn("lp.prepared_edges = use_prepared_closed_shape_edge_layout()", body)
            self.assertIn("reinterpret_cast<const GpuPreparedClosedShapeEdge2D*>", body)
            self.assertIn(": nullptr;", body)

    def test_prepared_edge_layout_is_app_agnostic(self) -> None:
        combined = (CORE.read_text(encoding="utf-8") + WORKLOADS.read_text(encoding="utf-8")).lower()
        start = combined.index("gpupreparedclosedshapeedge2d")
        window = combined[start : start + 5000]

        for forbidden in ("rayjoin", "county", "soil", "brazil"):
            self.assertNotIn(forbidden, window)


if __name__ == "__main__":
    unittest.main()
