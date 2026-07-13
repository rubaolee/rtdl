from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_point_contains_prepared_phase_columns_repeat",
    APP / "run_exact_point_contains_prepared_phase_columns_repeat.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CACHE_SPEC = importlib.util.spec_from_file_location(
    "librts_build_exact_aabb_column_cache",
    APP / "build_exact_aabb_column_cache.py",
)
assert CACHE_SPEC is not None and CACHE_SPEC.loader is not None
CACHE_MODULE = importlib.util.module_from_spec(CACHE_SPEC)
CACHE_SPEC.loader.exec_module(CACHE_MODULE)


class _Prepared:
    def __init__(self):
        self.calls = 0

    def count(self, *, point_queries, operation):
        self.calls += 1
        return {
            "backend": "optix",
            "counts": {"point_contains": 1},
            "run_phases": {"query_aabb_index_2d_sec": 0.01 * self.calls},
            "rt_core_accelerated": True,
        }

    def close(self):
        self.closed = True


class Goal5489LibrtsPreparedPhaseRepeatTest(unittest.TestCase):
    def test_exact_column_cache_round_trips_with_source_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geometry = root / "geometry.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            prefix = root / "cache" / "geometry"
            built = CACHE_MODULE.build_cache(geometry_path=geometry, cache_prefix=prefix)
            columns, metadata = CACHE_MODULE.load_cached_columns(
                geometry_path=geometry,
                cache_prefix=prefix,
            )
            self.assertEqual(columns.ids.tolist(), [0])
            self.assertEqual(columns.max_y.tolist(), [1.0])
            self.assertEqual(metadata["source_sha256"], built["source_sha256"])
            self.assertEqual(metadata["row_count"], 1)
            geometry.write_text("POLYGON ((0 0, 2 0, 0 2, 0 0))\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                CACHE_MODULE.load_cached_columns(
                    geometry_path=geometry,
                    cache_prefix=prefix,
                )
    def test_numeric_loader_matches_regex_loader(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "geometry.wkt"
            path.write_text(
                "POLYGON ((0 0, 1e0 0, 0 1, 0 0))\n"
                "MULTIPOLYGON (((2 2, 4 2, 2 5, 2 2)))\n",
                encoding="utf-8",
            )
            regex = MODULE.load_geometry_mbr_columns(path)
            numeric = MODULE.load_geometry_mbr_columns_fast(path)
        self.assertEqual(regex.ids.tolist(), numeric.ids.tolist())
        self.assertEqual(regex.min_x.tolist(), numeric.min_x.tolist())
        self.assertEqual(regex.min_y.tolist(), numeric.min_y.tolist())
        self.assertEqual(regex.max_x.tolist(), numeric.max_x.tolist())
        self.assertEqual(regex.max_y.tolist(), numeric.max_y.tolist())

    def test_repeat_requires_reuse_and_records_each_query(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geometry = root / "geometry.wkt"
            query = root / "query.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            query.write_text("POINT (0.1 0.1)\n", encoding="utf-8")
            extraction = {
                "claim_boundary": {"archive_subset_extracted": True},
                "extraction": {
                    "final_path": str(root),
                    "selected_members": [
                        {"relative_path": "geometry.wkt", "size_bytes": geometry.stat().st_size, "sha256": MODULE._sha256(geometry)},
                        {"relative_path": "query.wkt", "size_bytes": query.stat().st_size, "sha256": MODULE._sha256(query)},
                    ],
                },
            }
            prepared = _Prepared()
            author = {"geometry_count": 1, "query_count": 1, "result_count": 1}
            with (
                mock.patch.object(MODULE, "run_author", return_value=(author, "", ["author"])),
                mock.patch.object(MODULE.rt, "prepare_aabb_index_2d_columns", return_value=prepared),
            ):
                result = MODULE.run_repeat(
                    author_binary=root / "author",
                    ae_root=root,
                    geometry_path=geometry,
                    query_path=query,
                    serialize_dir=root / "serialize",
                    archive_result={"claim_boundary": {"archive_verified": True}},
                    extraction_result=extraction,
                    repeat=3,
                )
            self.assertTrue(result["matched"])
            self.assertEqual(prepared.calls, 3)
            self.assertEqual(len(result["rtdl"]["queries"]), 3)
            self.assertGreaterEqual(result["rtdl"]["query_wall_summary"]["first_sec"], 0.0)
            self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])

    def test_repeat_rejects_single_measurement(self):
        with self.assertRaises(ValueError):
            MODULE.run_repeat(
                author_binary=Path("author"),
                ae_root=Path("root"),
                geometry_path=Path("geometry"),
                query_path=Path("query"),
                serialize_dir=Path("serialize"),
                archive_result={},
                extraction_result={},
                repeat=1,
            )


if __name__ == "__main__":
    unittest.main()
