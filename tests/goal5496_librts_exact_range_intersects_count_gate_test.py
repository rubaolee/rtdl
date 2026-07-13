from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_range_intersects_count_gate",
    APP / "run_exact_range_intersects_count_gate.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Prepared:
    def count(self, *, box_queries, operation):
        self.operation = operation
        return {
            "backend": "optix",
            "counts": {"range_intersects": 1},
            "run_phases": {"query_aabb_index_2d_sec": 0.03},
            "rt_core_accelerated": True,
            "native_engine_customization": False,
        }

    def close(self):
        pass


class Goal5496LibrtsExactRangeIntersectsCountGateTest(unittest.TestCase):
    def test_parses_pinned_author_output(self):
        result = MODULE.parse_author_range_intersects_output(
            "Loaded boxes 12\n"
            "Loaded box queries 10000\n"
            "RT, load 0.4182 ms, query 0.0844 ms, results: 117314\n"
        )
        self.assertEqual(result["geometry_count"], 12)
        self.assertEqual(result["query_count"], 10000)
        self.assertEqual(result["result_count"], 117314)

    def test_parses_large_polygon_author_output(self):
        result = MODULE.parse_author_range_intersects_output(
            "Loaded polygons 12234\n"
            "Loaded queries 10000\n"
            "Loading Time 0.4224 ms\n"
            "Query Time 0.7796 ms\n"
            "Results 1570285\n"
        )
        self.assertEqual(result["geometry_count"], 12234)
        self.assertEqual(result["query_count"], 10000)
        self.assertEqual(result["result_count"], 1570285)

    def test_gate_preserves_exact_count_and_claim_boundaries(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geometry = root / "geometry.wkt"
            query = root / "query.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            query.write_text("POLYGON ((0 0, 0.5 0, 0 0.5, 0 0))\n", encoding="utf-8")
            extraction = {
                "claim_boundary": {"archive_subset_extracted": True},
                "extraction": {
                    "final_path": str(root),
                    "selected_members": [
                        {
                            "relative_path": "geometry.wkt",
                            "size_bytes": geometry.stat().st_size,
                            "sha256": MODULE._sha256(geometry),
                        },
                        {
                            "relative_path": "query.wkt",
                            "size_bytes": query.stat().st_size,
                            "sha256": MODULE._sha256(query),
                        },
                    ],
                },
            }
            author = {"geometry_count": 1, "query_count": 1, "result_count": 1}
            with (
                mock.patch.object(
                    MODULE,
                    "run_author_range_intersects",
                    return_value=(author, "", ["author", "-query_type", "range-intersects"]),
                ),
                mock.patch.object(MODULE.rt, "prepare_aabb_index_2d_columns", return_value=_Prepared()),
            ):
                result = MODULE.run_gate(
                    author_binary=root / "author",
                    ae_root=root,
                    geometry_path=geometry,
                    query_path=query,
                    serialize_dir=root / "serialize",
                    archive_result={"claim_boundary": {"archive_verified": True}},
                    extraction_result=extraction,
                )
        self.assertTrue(result["matched"])
        self.assertEqual(result["rtdl"]["operation"], "range_intersects")
        self.assertFalse(result["claim_boundary"]["pointwise_intersection_equivalence_claimed"])
        self.assertFalse(result["claim_boundary"]["performance_ratio_authorized"])


if __name__ == "__main__":
    unittest.main()
