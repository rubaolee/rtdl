from __future__ import annotations

import hashlib
import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "Paper-reproduction-apps" / "librts-paper" / "extend_verified_operation_batch.py"
SPEC = importlib.util.spec_from_file_location("librts_extend_verified_operation_batch", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal5522VerifiedBatchExtensionTest(unittest.TestCase):
    def test_reuses_verified_geometry_and_atomically_adds_queries(self):
        geometry_name = "PPoPPAE/datasets/polygons/base.wkt"
        query_names = [
            "PPoPPAE/datasets/queries/point-contains_queries_1/base.wkt",
            "PPoPPAE/datasets/queries/point-contains_queries_2/base.wkt",
        ]
        payloads = {geometry_name: b"POINT (0 0)\n", query_names[0]: b"POINT (1 1)\n", query_names[1]: b"POINT (2 2)\n"}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "archive.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                for name, data in payloads.items():
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    output.addfile(member, io.BytesIO(data))
            destination = root / "target"
            geometry = destination / geometry_name
            geometry.parent.mkdir(parents=True)
            geometry.write_bytes(payloads[geometry_name])
            geometry_record = {
                "relative_path": geometry_name,
                "size_bytes": len(payloads[geometry_name]),
                "sha256": hashlib.sha256(payloads[geometry_name]).hexdigest(),
            }
            pairs = [{"geometry": geometry_name, "query": name} for name in query_names]
            result = MODULE.extend_batch(
                archive_path=archive,
                archive_result={"claim_boundary": {"archive_verified": True}, "verification": {"size_bytes": archive.stat().st_size, "md5": "fixture"}},
                operation_inventory={"status": "verified_archive_operation_inventory_complete", "inventory": {"exact_pairs": {"point_contains": pairs}}},
                operation="point_contains",
                pairs=pairs,
                destination=destination,
                base_extraction={"extraction": {"final_path": str(destination), "selected_members": [geometry_record]}},
            )
            self.assertEqual(result["extraction"]["reused_verified_member_count"], 1)
            self.assertEqual(result["extraction"]["newly_extracted_member_count"], 2)
            self.assertTrue(result["extraction"]["atomic_member_promotion"])
            for name in query_names:
                self.assertEqual((destination / name).read_bytes(), payloads[name])

    def test_rejects_unverified_existing_query(self):
        geometry_name = "PPoPPAE/datasets/polygons/base.wkt"
        query_name = "PPoPPAE/datasets/queries/point-contains_queries_1/base.wkt"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / "archive.tar.gz"
            with tarfile.open(archive, "w:gz") as output:
                for name in (geometry_name, query_name):
                    data = b"POINT (0 0)\n"
                    member = tarfile.TarInfo(name)
                    member.size = len(data)
                    output.addfile(member, io.BytesIO(data))
            destination = root / "target"
            geometry = destination / geometry_name
            query = destination / query_name
            geometry.parent.mkdir(parents=True)
            query.parent.mkdir(parents=True)
            geometry.write_bytes(b"POINT (0 0)\n")
            query.write_bytes(b"unverified\n")
            record = {
                "relative_path": geometry_name,
                "size_bytes": geometry.stat().st_size,
                "sha256": hashlib.sha256(geometry.read_bytes()).hexdigest(),
            }
            pair = {"geometry": geometry_name, "query": query_name}
            with self.assertRaisesRegex(FileExistsError, "unverified existing selected member"):
                MODULE.extend_batch(
                    archive_path=archive,
                    archive_result={"claim_boundary": {"archive_verified": True}, "verification": {"size_bytes": archive.stat().st_size, "md5": "fixture"}},
                    operation_inventory={"status": "verified_archive_operation_inventory_complete", "inventory": {"exact_pairs": {"point_contains": [pair]}}},
                    operation="point_contains",
                    pairs=[pair],
                    destination=destination,
                    base_extraction={"extraction": {"final_path": str(destination), "selected_members": [record]}},
                )


if __name__ == "__main__":
    unittest.main()
