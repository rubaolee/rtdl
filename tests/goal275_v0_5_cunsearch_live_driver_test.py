import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.rtnn_cunsearch_live import _render_cunsearch_driver_source


class Goal275V05CuNSearchLiveDriverTest(unittest.TestCase):
    def test_build_config_reports_planned_when_headers_or_library_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config = rt.resolve_cunsearch_build_config(
                source_root=root / "src",
                build_root=root / "build",
            )
            self.assertEqual(config.current_status, "planned")
            self.assertIn("missing", config.notes)

    def test_build_config_reports_ready_when_library_and_headers_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            include_dir = root / "src" / "include"
            include_dir.mkdir(parents=True, exist_ok=True)
            (include_dir / "cuNSearch.h").write_text("// header\n", encoding="utf-8")
            build_dir = root / "build"
            build_dir.mkdir(parents=True, exist_ok=True)
            (build_dir / "libcuNSearch.a").write_bytes(b"archive")
            (build_dir / "CMakeCache.txt").write_text(
                "CUNSEARCH_USE_DOUBLE_PRECISION:BOOL=OFF\n",
                encoding="utf-8",
            )
            config = rt.resolve_cunsearch_build_config(
                source_root=root / "src",
                build_root=build_dir,
            )
            self.assertEqual(config.current_status, "ready")
            self.assertEqual(config.precision_mode, "float")

    def test_live_runner_rejects_wrong_request_shape_before_compilation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            include_dir = root / "src" / "include"
            include_dir.mkdir(parents=True, exist_ok=True)
            (include_dir / "cuNSearch.h").write_text("// header\n", encoding="utf-8")
            build_dir = root / "build"
            build_dir.mkdir(parents=True, exist_ok=True)
            (build_dir / "libcuNSearch.a").write_bytes(b"archive")

            request = root / "request.json"
            request.write_text(
                json.dumps({"adapter": "other", "workload": "fixed_radius_neighbors"}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unsupported cuNSearch request adapter"):
                rt.run_cunsearch_fixed_radius_request_live(
                    request,
                    root / "response.json",
                    source_root=root / "src",
                    build_root=build_dir,
                )

    def test_driver_source_renders_response_format_contract(self) -> None:
        payload = {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": 0.5,
            "k_max": 4,
            "query_points": [{"id": 1, "x": 0.0, "y": 0.0, "z": 0.0}],
            "search_points": [{"id": 2, "x": 0.0, "y": 0.0, "z": 0.2}],
        }
        source = _render_cunsearch_driver_source(payload, Path("/tmp/out.json"), precision_mode="float")
        self.assertIn('"response_format\\": \\"json_rows_v1\\"', source)
        self.assertIn('query_ids = { 1 }', source)
        self.assertIn('search_ids = { 2 }', source)
        self.assertIn("{0.0f, 0.0f, 0.0f}", source)
        self.assertIn("static_cast<double>(q[0]) - static_cast<double>(s[0])", source)
        self.assertIn("std::setprecision(9);", source)

    def test_driver_source_uses_double_literals_when_build_is_double(self) -> None:
        payload = {
            "adapter": "cunsearch",
            "workload": "fixed_radius_neighbors",
            "radius": 0.5,
            "k_max": 3,
            "query_points": [{"id": 1, "x": 1.25, "y": 2.5, "z": 3.75}],
            "search_points": [{"id": 2, "x": 4.0, "y": 5.0, "z": 6.0}],
        }
        source = _render_cunsearch_driver_source(payload, Path("/tmp/out.json"), precision_mode="double")
        self.assertIn("{1.25, 2.5, 3.75}", source)
        self.assertIn("NeighborhoodSearch nsearch(static_cast<Real>(0.5));", source)
        self.assertIn("std::min<std::size_t>(neighbors.size(), static_cast<std::size_t>(3))", source)
        self.assertIn("std::setprecision(17);", source)

    def test_precision_detection_defaults_to_double_without_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            include_dir = root / "src" / "include"
            include_dir.mkdir(parents=True, exist_ok=True)
            (include_dir / "cuNSearch.h").write_text("// header\n", encoding="utf-8")
            build_dir = root / "build"
            build_dir.mkdir(parents=True, exist_ok=True)
            (build_dir / "libcuNSearch.a").write_bytes(b"archive")
            config = rt.resolve_cunsearch_build_config(
                source_root=root / "src",
                build_root=build_dir,
            )
            self.assertEqual(config.precision_mode, "double")


if __name__ == "__main__":
    unittest.main()
