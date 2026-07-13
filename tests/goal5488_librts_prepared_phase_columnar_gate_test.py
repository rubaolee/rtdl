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
    "librts_exact_point_contains_prepared_phase_columns",
    APP / "run_exact_point_contains_prepared_phase_columns_gate.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class _Prepared:
    def count(self, *, point_queries, operation):
        return {
            "backend": "optix",
            "counts": {"point_contains": 1},
            "run_phases": {"query_aabb_index_2d_sec": 0.02},
            "rt_core_accelerated": True,
            "native_engine_customization": False,
        }

    def close(self):
        self.closed = True


class Goal5488LibrtsPreparedPhaseColumnarGateTest(unittest.TestCase):
    def test_loader_emits_generic_columns(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "geometry.wkt"
            path.write_text(
                "POLYGON ((0 0, 1 0, 0 1, 0 0))\n"
                "POLYGON ((2 2, 4 2, 2 5, 2 2))\n",
                encoding="utf-8",
            )
            columns = MODULE.load_geometry_mbr_columns(path)
        self.assertEqual(len(columns), 2)
        self.assertEqual(columns.ids.tolist(), [0, 1])
        self.assertEqual(columns.min_x.tolist(), [0.0, 2.0])
        self.assertEqual(columns.max_y.tolist(), [1.0, 5.0])

    def test_gate_uses_columnar_prepare_and_keeps_claims_closed(self):
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
                mock.patch.object(MODULE.rt, "prepare_aabb_index_2d_columns", return_value=prepared) as prepare_mock,
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
            prepare_mock.assert_called_once()
            self.assertEqual(result["rtdl"]["input_contract"], "generic_host_aabb_2d_columns")
            self.assertFalse(result["claim_boundary"]["device_zero_copy_claimed"])
            self.assertFalse(result["phase_boundary"]["performance_ratio_authorized"])


if __name__ == "__main__":
    unittest.main()
