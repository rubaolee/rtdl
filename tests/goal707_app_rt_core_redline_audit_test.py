from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal707_app_rt_core_redline_and_db_graph_spatial_audit_2026-04-21.md"
APP_MATRIX = ROOT / "docs/app_engine_support_matrix.md"
APP_CATALOG = ROOT / "docs/application_catalog.md"


class Goal707AppRtCoreRedlineAuditTest(unittest.TestCase):
    def test_report_records_rtdl_app_red_line(self):
        text = REPORT.read_text()
        compact_text = " ".join(text.split())
        required = [
            "RTDL does not need to reproduce a full paper implementation",
            "the RTDL language/runtime owns the ray-tracing or spatial-query acceleration core",
            "NVIDIA RT-core acceleration only when the measured OptiX path uses OptiX traversal",
            "CUDA kernels inside the OptiX backend library are GPU compute, not RT-core traversal",
            "Embree BVH and point-query execution is real RT-style CPU traversal, not GPU RT-core execution",
        ]
        for phrase in required:
            self.assertIn(phrase, compact_text)

    def test_report_answers_db_graph_spatial_status(self):
        text = REPORT.read_text()
        compact_text = " ".join(text.split())
        required = [
            "DB can be a valid RTDL app today",
            "DB is not yet a clean NVIDIA RT-core app-performance flagship",
            "Graph is a valid RTDL language/runtime app today",
            "Graph is not yet a valid OptiX RT-core performance app today",
            "Only apps whose current measured path uses real OptiX traversal",
            "Robot collision is the current cleanest OptiX traversal candidate",
        ]
        for phrase in required:
            self.assertIn(phrase, compact_text)

    def test_public_docs_expose_honesty_boundary(self):
        matrix = APP_MATRIX.read_text()
        catalog = APP_CATALOG.read_text()
        self.assertIn("`--backend optix` is not automatically a NVIDIA RT-core acceleration claim", matrix)
        self.assertIn("RTDL owns the accelerated core only when the app routes", catalog)

    def test_host_indexed_optix_apps_are_marked_compatibility_fallback(self):
        matrix = rt.app_engine_support_matrix()
        for app in (
            "graph_analytics",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
        ):
            self.assertEqual(matrix[app]["optix"].status, "direct_cli_compatibility_fallback")
            self.assertEqual(
                rt.optix_app_performance_support(app).performance_class,
                "host_indexed_fallback",
            )


if __name__ == "__main__":
    unittest.main()
