from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_exact_point_contains_prepared_phase",
    APP / "run_exact_point_contains_prepared_phase_gate.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Prepared:
    def count(self, *, point_queries, operation):
        self.point_queries = tuple(point_queries)
        self.operation = operation
        return {
            "backend": "optix",
            "counts": {"point_contains": 1},
            "run_phases": {"query_aabb_index_2d_sec": 0.02},
            "rt_core_accelerated": True,
            "native_engine_customization": False,
        }

    def close(self):
        self.closed = True


class Goal5485LibrtsExactPointContainsPreparedPhaseGateTest(unittest.TestCase):
    def test_prepared_phase_separates_prepare_and_query_and_closes_ratio(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geometry = root / "geometry.wkt"
            query = root / "query.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n")
            query.write_text("POINT (0.1 0.1)\n")
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
            author = {
                "geometry_count": 1,
                "query_count": 1,
                "result_count": 1,
                "query_ms_internal": 0.1,
                "loading_ms_diagnostic": 0.2,
            }
            prepared = _Prepared()
            with (
                mock.patch.object(MODULE, "run_author", return_value=(author, "", ["author"])),
                mock.patch.object(MODULE, "load_geometry_mbrs", return_value=((0.0, 0.0, 1.0, 1.0),)),
                mock.patch.object(MODULE, "load_point_queries", return_value=((0.1, 0.1),)),
                mock.patch.object(MODULE.rt, "prepare_aabb_index_2d", return_value=prepared) as prepare_mock,
                mock.patch.object(MODULE.rt, "query_aabb_index_2d") as one_shot_mock,
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
            self.assertIn("prepare_index_sec", result["rtdl"])
            self.assertIn("prepared_query_wall_sec", result["rtdl"])
            self.assertTrue(result["phase_boundary"]["prepared_query_phase_comparison_candidate"])
            self.assertFalse(result["phase_boundary"]["performance_ratio_authorized"])
            prepare_mock.assert_called_once()
            one_shot_mock.assert_not_called()

    def test_committed_pod_result_is_matched_and_ratio_closed(self):
        result_path = (
            ROOT
            / "Paper-reproduction-apps"
            / "librts-paper"
            / "results"
            / "librts_goal5485_dtl_cnty_prepared_phase.json"
        )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertTrue(result["matched"])
        self.assertEqual(result["author"]["result_count"], 136475)
        self.assertEqual(result["rtdl"]["result_count"], 136475)
        self.assertTrue(result["input_identity"]["same_files_passed_to_author_and_rtdl"])
        self.assertTrue(result["phase_boundary"]["prepared_query_phase_comparison_candidate"])
        self.assertFalse(result["phase_boundary"]["performance_ratio_authorized"])
        self.assertFalse(result["claim_boundary"]["pointwise_containment_equivalence_claimed"])


if __name__ == "__main__":
    unittest.main()
