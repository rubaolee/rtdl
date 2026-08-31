from __future__ import annotations

import importlib.util
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
sys.path.insert(0, str(APP))
SPEC = importlib.util.spec_from_file_location(
    "librts_archive_operation_inventory",
    APP / "audit_exact_archive_operation_inventory.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Goal5492LibrtsExactArchiveOperationInventoryTest(unittest.TestCase):
    def test_classifies_operations_and_pairs_same_basename(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "archive.tar.gz"
            source_root = root / "source"
            (source_root / "PPoPPAE/datasets/polygons").mkdir(parents=True)
            (source_root / "PPoPPAE/datasets/queries/range-contains_queries_1000").mkdir(parents=True)
            (source_root / "PPoPPAE/datasets/queries/range-intersects_select_1000").mkdir(parents=True)
            geometry = source_root / "PPoPPAE/datasets/polygons/sample.wkt"
            geometry.write_text("POLYGON ((0 0, 1 0, 0 1, 0 0))\n", encoding="utf-8")
            (source_root / "PPoPPAE/datasets/queries/range-contains_queries_1000/sample.wkt").write_text("BOX\n", encoding="utf-8")
            (source_root / "PPoPPAE/datasets/queries/range-intersects_select_1000/sample.wkt").write_text("BOX\n", encoding="utf-8")
            with tarfile.open(archive_path, "w:gz") as archive:
                archive.add(source_root / "PPoPPAE", arcname="PPoPPAE")
            result = MODULE.audit_archive(
                archive_path=archive_path,
                archive_result={"claim_boundary": {"archive_verified": True}},
            )
        self.assertTrue(result["decision"]["range_contains_exact_pairs_available"])
        self.assertTrue(result["decision"]["range_intersects_exact_pairs_available"])
        self.assertEqual(result["inventory"]["operation_exact_pair_counts"]["range_contains"], 1)
        self.assertFalse(result["decision"]["pip_exact_pairs_available"])
        self.assertFalse(result["decision"]["performance_ratio_authorized"])

    def test_requires_verified_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "archive.tar.gz"
            path.write_bytes(b"not-an-archive")
            with self.assertRaises(ValueError):
                MODULE.audit_archive(
                    archive_path=path,
                    archive_result={"claim_boundary": {"archive_verified": False}},
                )


if __name__ == "__main__":
    unittest.main()
