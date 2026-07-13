from __future__ import annotations

import importlib.util
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_verified_operation_subset",
    APP / "extract_verified_operation_subset.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5493LibrtsVerifiedOperationSubsetTest(unittest.TestCase):
    def test_extracts_only_inventory_approved_pair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            geometry = source / "PPoPPAE/datasets/polygons/dtl_cnty.wkt"
            query = source / "PPoPPAE/datasets/queries/range-contains_queries_100000/dtl_cnty.wkt"
            query.parent.mkdir(parents=True)
            geometry.parent.mkdir(parents=True)
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            query.write_text("POLYGON ((0 0, 0.5 0, 0 0.5, 0 0))\n", encoding="utf-8")
            archive = root / "archive.tar.gz"
            with tarfile.open(archive, "w:gz") as handle:
                handle.add(source / "PPoPPAE", arcname="PPoPPAE")
            inventory = {
                "status": "verified_archive_operation_inventory_complete",
                "inventory": {
                    "exact_pairs": {
                        "range_contains": [
                            {"geometry": "PPoPPAE/datasets/polygons/dtl_cnty.wkt", "query": "PPoPPAE/datasets/queries/range-contains_queries_100000/dtl_cnty.wkt"}
                        ]
                    }
                },
            }
            result = MODULE.extract_subset(
                archive_path=archive,
                archive_result={"verification": {"size_bytes": archive.stat().st_size, "md5": "test"}, "claim_boundary": {"archive_verified": True}},
                operation_inventory=inventory,
                operation="range_contains",
                geometry_member="PPoPPAE/datasets/polygons/dtl_cnty.wkt",
                query_member="PPoPPAE/datasets/queries/range-contains_queries_100000/dtl_cnty.wkt",
                destination=root / "selected",
            )
        self.assertTrue(result["claim_boundary"]["archive_subset_extracted"])
        self.assertEqual(result["extraction"]["selected_member_count"], 2)

    def test_rejects_unlisted_pair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "archive.tar.gz"
            with tarfile.open(archive, "w:gz"):
                pass
            with self.assertRaises(ValueError):
                MODULE.extract_subset(
                    archive_path=archive,
                    archive_result={"claim_boundary": {"archive_verified": True}, "verification": {}},
                    operation_inventory={"status": "verified_archive_operation_inventory_complete", "inventory": {"exact_pairs": {"range_contains": []}}},
                    operation="range_contains",
                    geometry_member="a",
                    query_member="b",
                    destination=root / "selected",
                )


if __name__ == "__main__":
    unittest.main()
