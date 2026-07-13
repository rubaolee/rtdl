from __future__ import annotations

import importlib.util
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


EXTRACTOR = _load("librts_verified_operation_batch", APP / "extract_verified_operation_batch.py")
RUNNER = _load("librts_exact_range_intersects_batch", APP / "run_exact_range_intersects_batch.py")


class Goal5500LibRTSExactRangeIntersectsBatchToolsTest(unittest.TestCase):
    def test_batch_extractor_scans_shared_geometry_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            geometry = source / "PPoPPAE/datasets/polygons/dtl_cnty.wkt"
            query_a = source / "PPoPPAE/datasets/queries/range-intersects_select_0.01_queries_10000/dtl_cnty.wkt"
            query_b = source / "PPoPPAE/datasets/queries/range-intersects_select_0.001_queries_10000/dtl_cnty.wkt"
            for path, value in ((geometry, "POLYGON ((0 0, 1 0, 0 1, 0 0))\n"), (query_a, "POLYGON ((0 0, 1 0, 0 1, 0 0))\n"), (query_b, "POLYGON ((0 0, 2 0, 0 2, 0 0))\n")):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value, encoding="utf-8")
            archive = root / "archive.tar.gz"
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(source / "PPoPPAE", arcname="PPoPPAE")
            pairs = [
                {"geometry": "PPoPPAE/datasets/polygons/dtl_cnty.wkt", "query": "PPoPPAE/datasets/queries/range-intersects_select_0.01_queries_10000/dtl_cnty.wkt"},
                {"geometry": "PPoPPAE/datasets/polygons/dtl_cnty.wkt", "query": "PPoPPAE/datasets/queries/range-intersects_select_0.001_queries_10000/dtl_cnty.wkt"},
            ]
            result = EXTRACTOR.extract_batch(
                archive_path=archive,
                archive_result={"claim_boundary": {"archive_verified": True}, "verification": {"size_bytes": archive.stat().st_size, "md5": "test"}},
                operation_inventory={"status": "verified_archive_operation_inventory_complete", "inventory": {"exact_pairs": {"range_intersects": pairs}}},
                operation="range_intersects",
                pairs=pairs,
                destination=root / "selected",
            )
        self.assertTrue(result["claim_boundary"]["archive_subset_extracted"])
        self.assertEqual(result["extraction"]["selected_pair_count"], 2)
        self.assertEqual(result["extraction"]["selected_member_count"], 3)

    def test_batch_runner_preserves_all_case_results_and_claim_boundary(self):
        cases = [{"geometry": "/g0", "query": "/q0", "serialize_dir": "/s0"}, {"geometry": "/g1", "query": "/q1", "serialize_dir": "/s1"}]
        with mock.patch.object(RUNNER, "run_gate", side_effect=[{"matched": True, "case": 0}, {"matched": True, "case": 1}]) as gate:
            result = RUNNER.run_batch(
                author_binary=Path("author"),
                ae_root=Path("ae"),
                cases=cases,
                archive_result={},
                extraction_result={},
            )
        self.assertTrue(result["matched"])
        self.assertEqual(result["case_count"], 2)
        self.assertEqual(result["matched_case_count"], 2)
        self.assertFalse(result["claim_boundary"]["complete_range_intersects_matrix_claimed"])
        self.assertEqual(gate.call_count, 2)


if __name__ == "__main__":
    unittest.main()
