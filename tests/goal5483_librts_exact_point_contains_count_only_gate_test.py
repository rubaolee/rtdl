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
    "librts_exact_point_contains_count_only", APP / "run_exact_point_contains_count_only_gate.py"
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5483LibrtsExactPointContainsCountOnlyGateTest(unittest.TestCase):
    def test_count_gate_uses_public_count_api_without_row_materialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            extracted = root / "extracted"
            geometry = extracted / "PPoPPAE/datasets/polygons/x.wkt"
            query = extracted / "PPoPPAE/datasets/queries/point-contains_queries_100000/x.wkt"
            geometry.parent.mkdir(parents=True)
            query.parent.mkdir(parents=True)
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n")
            query.write_text("POINT (0.1 0.1)\n")
            extraction = {
                "claim_boundary": {"archive_subset_extracted": True},
                "extraction": {
                    "final_path": str(extracted),
                    "selected_members": [
                        {
                            "relative_path": geometry.relative_to(extracted).as_posix(),
                            "size_bytes": geometry.stat().st_size,
                            "sha256": __import__("hashlib").sha256(geometry.read_bytes()).hexdigest(),
                        },
                        {
                            "relative_path": query.relative_to(extracted).as_posix(),
                            "size_bytes": query.stat().st_size,
                            "sha256": __import__("hashlib").sha256(query.read_bytes()).hexdigest(),
                        },
                    ],
                },
            }
            archive = {"claim_boundary": {"archive_verified": True}}
            author = {
                "geometry_count": 1,
                "query_count": 1,
                "result_count": 1,
                "query_ms_internal": 0.1,
                "loading_ms_diagnostic": 0.2,
            }
            count_payload = {
                "backend": "optix",
                "counts": {"point_contains": 1},
                "run_phases": {"query_aabb_index_2d_sec": 0.01},
                "rt_core_accelerated": True,
                "native_engine_customization": False,
            }
            with (
                mock.patch.object(MODULE, "run_author", return_value=(author, "", ["author"])),
                mock.patch.object(MODULE, "load_geometry_mbrs", return_value=((0.0, 0.0, 1.0, 1.0),)),
                mock.patch.object(MODULE, "load_point_queries", return_value=((0.1, 0.1),)),
                mock.patch.object(MODULE.rt, "query_aabb_index_2d", return_value=count_payload) as query_mock,
                mock.patch.object(MODULE.rt, "expanded_aabb_point_membership_rows_2d") as rows_mock,
            ):
                result = MODULE.run_gate(
                    author_binary=root / "author",
                    ae_root=root,
                    geometry_path=geometry,
                    query_path=query,
                    serialize_dir=root / "serialize",
                    archive_result=archive,
                    extraction_result=extraction,
                )
            self.assertTrue(result["matched"])
            self.assertEqual(result["rtdl"]["public_api"], "query_aabb_index_2d")
            self.assertTrue(result["rtdl"]["count_only"])
            query_mock.assert_called_once()
            rows_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
