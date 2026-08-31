from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = (
    ROOT / "history/internal_docs/"
    "goal5791_frozen_triangle_data_and_oracle_authority_20260817.json"
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


class Goal5791DataOracleAuthorityTest(unittest.TestCase):
    def test_bundle_manifest_datasets_oracles_and_non_authorization(self):
        value = json.loads(AUTHORITY.read_text(encoding="utf-8"))
        claimed = value.pop("authority_sha256")
        self.assertEqual(_sha_bytes(_canonical(value)), claimed)
        bundle_record = value["data_bundle"]
        bundle = ROOT / bundle_record["path"]
        self.assertEqual(_sha_file(bundle), bundle_record["sha256"])
        self.assertEqual(bundle.stat().st_size, bundle_record["bytes"])
        with tarfile.open(bundle, "r:gz") as archive:
            manifest_bytes = archive.extractfile(
                bundle_record["manifest_member"]).read()
        self.assertEqual(
            _sha_bytes(manifest_bytes), bundle_record["manifest_member_sha256"])
        self.assertEqual(len(manifest_bytes), bundle_record["manifest_member_bytes"])
        manifest = json.loads(manifest_bytes)
        rows = {row["path"]: row for row in manifest["files"]}

        expected = {
            "com_dblp": ("com-dblp.edge", 2_224_385),
            "cit_patents": ("cit-Patents.edge", 7_515_023),
            "soc_livejournal1": ("soc-LiveJournal1.edge", 285_730_264),
        }
        self.assertEqual(set(value["datasets"]), set(expected))
        for dataset_id, (filename, triangle_count) in expected.items():
            row = value["datasets"][dataset_id]
            self.assertEqual(row["member"], f"DATA/triangle/{filename}")
            self.assertEqual(row["expected_triangle_count"], triangle_count)
            self.assertEqual(rows[row["member"]]["sha256"], row["sha256"])
            self.assertEqual(rows[row["member"]]["size_bytes"], row["bytes"])
            oracle = row["oracle_contract"]
            self.assertEqual(oracle["dataset_id"], dataset_id)
            self.assertEqual(oracle["input_sha256"], row["sha256"])
            self.assertEqual(oracle["expected_triangle_count"], triangle_count)
            self.assertEqual(
                _sha_bytes(_canonical(oracle)), row["oracle_authority_sha256"])

        self.assertTrue(all(
            item is False for item in value["authorization"].values()))
        self.assertFalse(value["scope"]["rt_barneshut_bundle_members_scheduled"])

    def test_resigned_oracle_and_scope_attacks_still_fail_independent_truth(self):
        original = json.loads(AUTHORITY.read_text(encoding="utf-8"))
        unsigned_original = dict(original)
        claimed_original = unsigned_original.pop("authority_sha256")
        self.assertEqual(_sha_bytes(_canonical(unsigned_original)), claimed_original)
        expected = {
            "com_dblp": ("DATA/triangle/com-dblp.edge", 2_224_385),
            "cit_patents": ("DATA/triangle/cit-Patents.edge", 7_515_023),
            "soc_livejournal1": (
                "DATA/triangle/soc-LiveJournal1.edge", 285_730_264),
        }
        self.assertEqual(set(original["datasets"]), set(expected))
        for dataset_id, (member, triangle_count) in expected.items():
            row = original["datasets"][dataset_id]
            self.assertEqual(row["member"], member)
            self.assertEqual(row["expected_triangle_count"], triangle_count)
            oracle = row["oracle_contract"]
            self.assertEqual(oracle["dataset_id"], dataset_id)
            self.assertEqual(oracle["input_sha256"], row["sha256"])
            self.assertEqual(oracle["expected_triangle_count"], triangle_count)
            self.assertEqual(
                _sha_bytes(_canonical(oracle)), row["oracle_authority_sha256"])
        self.assertTrue(all(
            item is False for item in original["authorization"].values()))
        self.assertFalse(
            original["scope"]["rt_barneshut_bundle_members_scheduled"])
        for mutation in ("oracle", "member", "authorization"):
            value = json.loads(json.dumps(original))
            if mutation == "oracle":
                value["datasets"]["com_dblp"]["expected_triangle_count"] += 1
                value["datasets"]["com_dblp"]["oracle_contract"][
                    "expected_triangle_count"] += 1
                value["datasets"]["com_dblp"]["oracle_authority_sha256"] = (
                    _sha_bytes(_canonical(value["datasets"]["com_dblp"][
                        "oracle_contract"])))
            elif mutation == "member":
                value["datasets"]["com_dblp"]["member"] = (
                    "DATA/common/rt_barneshut/prepared_arrays.json")
            else:
                value["authorization"]["authorizes_formal_worker_zero"] = True
            unsigned = dict(value)
            unsigned.pop("authority_sha256")
            value["authority_sha256"] = _sha_bytes(_canonical(unsigned))
            # The frozen scientific values are independent of a self-consistent
            # re-sign, so none of these may equal the shipped authority.
            self.assertNotEqual(value, original)
            if mutation == "oracle":
                self.assertNotEqual(
                    value["datasets"]["com_dblp"]["expected_triangle_count"],
                    2_224_385,
                )
            elif mutation == "member":
                self.assertNotIn(
                    value["datasets"]["com_dblp"]["member"],
                    {row["member"] for row in original["datasets"].values()},
                )
            else:
                self.assertFalse(all(
                    item is False for item in value["authorization"].values()))


if __name__ == "__main__":
    unittest.main()
