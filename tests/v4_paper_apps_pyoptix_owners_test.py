from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from unittest import mock
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from experiments.v4_paper_apps_pyoptix.inputs import (
    _numbers,
    _wkt_mbrs,
    load_particle,
    sha256,
)
from experiments.v4_paper_apps_pyoptix.librts_owner import (
    DEVICE_SOURCE as LIBRTS_DEVICE_SOURCE,
)
from experiments.v4_paper_apps_pyoptix.librts_owner import (
    PARAM_DTYPE as LIBRTS_PARAM_DTYPE,
)
from experiments.v4_paper_apps_pyoptix.librts_owner import (
    LibRTSCountResult,
    PublicPyOptixLibRTSCountOwner,
    normalize_indexed_columns,
    normalize_queries,
)
from experiments.v4_paper_apps_pyoptix.particle_adapter import (
    DEVICE_SOURCE as PARTICLE_DEVICE_SOURCE,
)
from experiments.v4_paper_apps_pyoptix.public_runtime import (
    PublicRuntime,
    _canonicalize_nvrtc_ptx,
    _nvrtc_options,
    pipeline_options,
)
from experiments.v4_paper_apps_pyoptix.triangle_owner import (
    DEVICE_SOURCE as TRIANGLE_DEVICE_SOURCE,
)
from experiments.v4_paper_apps_pyoptix.triangle_owner import (
    PARAM_DTYPE as TRIANGLE_PARAM_DTYPE,
)


@dataclass
class _Indexed:
    min_x: np.ndarray
    min_y: np.ndarray
    max_x: np.ndarray
    max_y: np.ndarray


class V4PaperAppsPyOptixOwnersTest(unittest.TestCase):
    def test_device_sources_have_exact_public_entries_and_no_rtdl_import(self) -> None:
        particle = PARTICLE_DEVICE_SOURCE.read_text(encoding="utf-8")
        triangle = TRIANGLE_DEVICE_SOURCE.read_text(encoding="utf-8")
        librts = LIBRTS_DEVICE_SOURCE.read_text(encoding="utf-8")
        self.assertEqual(TRIANGLE_PARAM_DTYPE.itemsize, 56)
        self.assertEqual(LIBRTS_PARAM_DTYPE.itemsize, 104)
        for entry in (
            "__raygen__rtdl_particle_strict_interior",
            "__closesthit__rtdl_particle_strict_interior",
            "__miss__rtdl_particle_strict_interior",
        ):
            self.assertEqual(particle.count(entry), 1)
        for entry in (
            "__raygen__paper_triangle_count",
            "__anyhit__paper_triangle_count",
            "__miss__paper_triangle_count",
        ):
            self.assertEqual(triangle.count(entry), 1)
        for entry in (
            "__raygen__paper_librts_count",
            "__intersection__paper_librts_count",
            "__miss__paper_librts_count",
        ):
            self.assertEqual(librts.count(entry), 1)
        for source in (particle, triangle, librts):
            self.assertNotIn("rtdl_optix", source)
            self.assertNotIn("#include <math.h>", source)
        self.assertIn("float tmax;", triangle)
        self.assertIn("params.tmin, ray.tmax", triangle)

    def test_librts_column_and_query_normalization(self) -> None:
        indexed = _Indexed(
            min_x=np.array([0.0, -1.0], dtype=np.float64),
            min_y=np.array([0.0, -2.0], dtype=np.float64),
            max_x=np.array([1.0, 2.0], dtype=np.float64),
            max_y=np.array([1.0, 3.0], dtype=np.float64),
        )
        columns = normalize_indexed_columns(indexed)
        self.assertEqual(len(columns), 4)
        self.assertTrue(all(column.dtype == np.float32 for column in columns))
        point = normalize_queries("point_contains", ((0.25, 0.75),))
        self.assertTrue(np.array_equal(point[0], point[2]))
        self.assertTrue(np.array_equal(point[1], point[3]))
        box = normalize_queries("range_contains", ((0.0, 0.0, 1.0, 2.0),))
        self.assertEqual(
            tuple(float(column[0]) for column in box), (0.0, 0.0, 1.0, 2.0)
        )

    def test_librts_normalization_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            normalize_queries("point_contains", ())
        with self.assertRaises(ValueError):
            normalize_queries("range_contains", ((1.0, 0.0, 0.0, 1.0),))
        with self.assertRaises(ValueError):
            normalize_queries("unknown", ((0.0, 0.0),))
        bad = _Indexed(
            min_x=np.array([1.0]),
            min_y=np.array([0.0]),
            max_x=np.array([0.0]),
            max_y=np.array([1.0]),
        )
        with self.assertRaises(ValueError):
            normalize_indexed_columns(bad)

    def test_librts_streamed_columns_cover_each_row_once(self) -> None:
        owner = object.__new__(PublicPyOptixLibRTSCountOwner)
        owner._closed = False
        owner.query_operation = None
        owner.query_device = ()
        owner.query_count = 0
        owner.query_layout = None
        owner.query_counts = None
        owner.query_status = None
        owner.indexed_count = 2

        def bind(*, operation, columns):
            owner.query_operation = operation
            owner.query_count = len(columns["x"])
            owner.query_layout = "device_f32_soa"

        owner.bind_query_columns = mock.Mock(side_effect=bind)
        owner.execute_count = mock.Mock(side_effect=lambda **_: LibRTSCountResult(
            operation="point_contains",
            checked_u64=owner.query_count,
            query_count=owner.query_count,
            indexed_count=owner.indexed_count,
            device_status=0,
        ))
        result = owner.execute_count_query_column_stream(
            operation="point_contains",
            columns={
                "x": np.arange(5, dtype=np.float32),
                "y": np.arange(5, dtype=np.float32),
            },
            chunk_rows=2,
            expected_count=5,
        )
        self.assertEqual(result.checked_u64, 5)
        self.assertEqual(result.chunk_counts, (2, 2, 1))
        self.assertEqual(result.device_statuses, (0, 0, 0))
        self.assertEqual(owner.bind_query_columns.call_count, 3)
        self.assertIsNone(owner.query_operation)

    def test_librts_worker_binds_queries_symmetrically_before_execute(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "scripts/v4_paper_apps_pyoptix_worker.py"
        ).read_text(encoding="utf-8")
        body = source[source.index("def _librts_case"):source.index("def _prepare_case")]
        self.assertEqual(body.count("owner.bind_queries("), 2)
        self.assertIn("result = owner.execute_count()", body)
        self.assertNotIn("queries=data[\"queries\"]", body[body.index("def execute()", body.index("else:")):])

    def test_librts_scalar_count_front_door_avoids_legacy_compiler_imports(self) -> None:
        root = Path(__file__).resolve().parents[1]
        worker = (root / "scripts/v4_paper_apps_pyoptix_worker.py").read_text(
            encoding="utf-8"
        )
        worker_body = worker[
            worker.index("def _librts_case"):worker.index("def _prepare_case")
        ]
        self.assertIn("target, _ = _rtdl_target(config)", worker_body)
        self.assertNotIn("_rtdl_runtime(config)", worker_body)

        app = (
            root / "Paper-reproduction-apps/librts-paper/v4_whole_app.py"
        ).read_text(encoding="utf-8")
        eager_imports = app[:app.index("APP_DIR =")]
        self.assertNotIn("v4_bounded_relation", eager_imports)
        self.assertNotIn("v4_callback_abi", eager_imports)

    def test_owner_modules_do_not_import_rtdl(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for name in (
            "inputs.py",
            "librts_owner.py",
            "particle_adapter.py",
            "public_runtime.py",
            "triangle_owner.py",
        ):
            source = (root / "experiments/v4_paper_apps_pyoptix" / name).read_text(
                encoding="utf-8"
            )
            self.assertNotIn("import rtdsl", source)
            self.assertNotIn("from rtdsl", source)

    def test_wkt_parser_ignores_keywords_and_handles_multi_geometry(self) -> None:
        values = _numbers("LINESTRING (1e-2 2E+1, -3.5 .25)")
        self.assertTrue(np.array_equal(values, np.array([0.01, 20.0, -3.5, 0.25])))
        rows = _wkt_mbrs(
            "MULTIPOLYGON (((0 0, 2 0, 2 1, 0 0)), (((-5 -4, -3 -4, -3 -2, -5 -4))))"
        )
        self.assertEqual(rows, ((0.0, 0.0, 2.0, 1.0), (-5.0, -4.0, -3.0, -2.0)))

    def test_wkt_parser_fails_closed_on_bad_geometry(self) -> None:
        with self.assertRaises(ValueError):
            _wkt_mbrs("GEOMETRYCOLLECTION (POINT (0 0))")
        with self.assertRaises(ValueError):
            _wkt_mbrs("POLYGON ((0 0, 1))")

    def test_optix_9_pipeline_declares_selected_primitive_kind(self) -> None:
        captured = {}
        optix = SimpleNamespace(
            TRAVERSABLE_GRAPH_FLAG_ALLOW_SINGLE_GAS=1,
            EXCEPTION_FLAG_NONE=0,
            PRIMITIVE_TYPE_FLAGS_CUSTOM=2,
            PRIMITIVE_TYPE_FLAGS_TRIANGLE=4,
            version=lambda: (9, 1, 0),
            PipelineCompileOptions=lambda **kwargs: captured.update(kwargs) or kwargs,
        )
        pipeline_options(PublicRuntime(cp=None, optix=optix), custom_primitive=True)
        self.assertEqual(captured["usesPrimitiveTypeFlags"], 2)

    def test_nvrtc_architecture_option_preserves_multidigit_major(self) -> None:
        options = _nvrtc_options(
            optix_include="/opt/optix/include",
            cuda_include="/usr/local/cuda/include",
            compute_capability=(12, 0),
        )
        self.assertIn(b"--gpu-architecture=compute_120", options)
        with self.assertRaises(ValueError):
            _nvrtc_options(
                optix_include="/opt/optix/include",
                cuda_include="/usr/local/cuda/include",
                compute_capability=(12, 10),
            )

    def test_nvrtc_ptx_canonicalization_removes_only_required_terminator(self) -> None:
        self.assertEqual(
            _canonicalize_nvrtc_ptx(b".version 8.0\n.target sm_86\n\0"),
            b".version 8.0\n.target sm_86\n",
        )
        for malformed in (
            b".version 8.0\n",
            b".version 8.0\0.target sm_86\0",
            b"\0",
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(RuntimeError):
                    _canonicalize_nvrtc_ptx(malformed)

    def test_triangle_owner_requires_single_any_hit_delivery(self) -> None:
        source = (
            Path(__file__).resolve().parents[1]
            / "experiments/v4_paper_apps_pyoptix/triangle_owner.py"
        ).read_text(encoding="utf-8")
        self.assertIn("GEOMETRY_FLAG_REQUIRE_SINGLE_ANYHIT_CALL", source)
        self.assertNotIn("build_input.flags = [optix.GEOMETRY_FLAG_NONE]", source)

    def test_particle_loader_reconstructs_v4_oracle_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "particle"
            root.mkdir()
            arrays = {
                "vertices_f32.npy": np.zeros((1, 3), dtype=np.float32),
                "triangles_u32.npy": np.zeros((1, 3), dtype=np.uint32),
                "front_values_u32.npy": np.zeros(1, dtype=np.uint32),
                "back_values_u32.npy": np.zeros(1, dtype=np.uint32),
                "queries_f32.npy": np.zeros((1, 7), dtype=np.float32),
                "expected_u32.npy": np.zeros((1, 3), dtype=np.uint32),
                "query_cells_u32.npy": np.zeros(1, dtype=np.uint32),
            }
            members = {}
            for name, value in arrays.items():
                path = root / name
                np.save(path, value, allow_pickle=False)
                members[name] = {
                    "shape": list(value.shape),
                    "dtype": str(value.dtype),
                    "sha256": sha256(path),
                }
            manifest = {
                "schema": "rtdl.goal5776.particle_real_scale_input.v1",
                "members": members,
                "queries": {"construction": "unit-test-construction"},
                "source": {"sha256": "a" * 64},
            }
            (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
            loaded = load_particle(temporary)
            expected = hashlib.sha256(
                json.dumps(
                    {
                        "construction": "unit-test-construction",
                        "query_cells_sha256": members["query_cells_u32.npy"]["sha256"],
                        "expected_sha256": members["expected_u32.npy"]["sha256"],
                        "source_sha256": "a" * 64,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            self.assertEqual(loaded["independent_oracle_sha256"], expected)


if __name__ == "__main__":
    unittest.main()
