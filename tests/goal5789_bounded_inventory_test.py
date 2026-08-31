from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tarfile
import unittest

from scripts import goal5789_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history/internal_docs/goal5789_contract_evidence_20260816"
FROZEN_SOURCES = (
    (
        ROOT / "history/internal_docs/goal5785_v6_rtx4000ada_final_result_20260816"
        / "EXECUTION_SOURCE.tar.gz",
        "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
    ),
    (
        ROOT / "history/internal_docs/goal5783_postfreeze_held_out_rtxrmq_evidence_20260814.tar.gz",
        "3bbc85e15aa89afba0c9b1332642e1ed12e7dab354debd91462761557522cf36",
    ),
    (
        ROOT / "history/internal_docs/goal5783_amendment_a1_external_rehash_supplement_20260814.tar.gz",
        "b9eb03b7dd0404b1f5ca46f04122699ab24fe622a62c57b1aa786db82f57a529",
    ),
)


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(path)
    return value


class Goal5789BoundedInventoryTest(unittest.TestCase):
    def test_every_paper_lane_replays_from_certificate(self) -> None:
        authority = _load(EVIDENCE / "AUTHORITY_BUNDLE.json")
        inventory = _load(EVIDENCE / "BOUNDED_INVENTORY.json")
        self.assertEqual(inventory["paper_app_count"], 9)
        self.assertEqual(inventory["registered_lane_count"], 15)
        self.assertEqual(inventory["semantic_compatible_count"], 6)
        self.assertEqual(inventory["semantic_unknown_count"], 9)
        self.assertEqual(inventory["semantic_incompatible_count"], 0)
        for row in inventory["inventory"]:
            unit = row["unit_id"]
            certificate = _load(EVIDENCE / "certificates" / f"{unit}.json")
            stored = _load(EVIDENCE / "results" / f"{unit}.json")
            rebuilt = checker.evaluate_certificate(certificate, authority)
            self.assertEqual(rebuilt, stored, unit)
            self.assertEqual(rebuilt["performance"]["verdict"], checker.NOT_EVALUATED)
            self.assertFalse(rebuilt["executable"])
            self.assertFalse(rebuilt["execution_authorized"])
            if row["semantic_authority_present"]:
                self.assertEqual(rebuilt["semantic_compatible"]["verdict"], checker.COMPATIBLE)
            else:
                self.assertEqual(rebuilt["semantic_compatible"]["verdict"], checker.UNKNOWN)
                self.assertIn("MISSING_INDEPENDENT_SEMANTIC_AUTHORITY", row["evidence_strength"])

    def test_source_manifest_rehashes_preserved_frozen_goal5789_bytes(self) -> None:
        authority = _load(EVIDENCE / "AUTHORITY_BUNDLE.json")
        manifest = authority["physical_authority"]["source_manifest"]
        preserved: dict[str, set[str]] = {}
        for source, expected_archive_sha in FROZEN_SOURCES:
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).hexdigest(),
                expected_archive_sha,
            )
            with tarfile.open(source, "r:gz") as archive:
                for member in archive.getmembers():
                    if not member.isfile():
                        continue
                    handle = archive.extractfile(member)
                    self.assertIsNotNone(handle, member.name)
                    preserved.setdefault(
                        member.name.removeprefix("./"), set()).add(
                            hashlib.sha256(handle.read()).hexdigest())
        for relative, expected in manifest.items():
            self.assertIn(expected, preserved.get(relative, set()), relative)

    def test_postfreeze_held_out_replay_is_not_a_checker_special_case(self) -> None:
        authority = _load(EVIDENCE / "HELD_OUT_AUTHORITY_BUNDLE.json")
        certificate = _load(EVIDENCE / "HELD_OUT_RTXRMQ_CERTIFICATE.json")
        stored = _load(EVIDENCE / "HELD_OUT_RTXRMQ_RESULT.json")
        self.assertEqual(checker.evaluate_certificate(certificate, authority), stored)
        self.assertTrue(stored["reference_admission_complete"])
        source = (ROOT / "scripts/goal5789_independent_compatibility_checker.py").read_text(encoding="utf-8")
        self.assertNotIn("rtxrmq", source.lower())

    def test_goal5790_freeze_requires_per_target_native_materialization(self) -> None:
        freeze = _load(EVIDENCE / "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json")
        family = freeze["executable_family_plan"]
        self.assertIn("reference_native_provenance_sha256", family)
        self.assertNotIn("native_library_sha256", family)
        policy = family["target_materialization_policy"]
        self.assertTrue(policy["actual_target_native_must_be_receipt_bound"])
        self.assertTrue(policy["actual_target_source_tree_must_be_receipt_bound"])
        self.assertFalse(policy["cross_target_native_byte_reproducibility_assumed"])
        self.assertFalse(policy["reference_native_is_execution_authority_for_other_targets"])
        self.assertTrue(policy["same_target_fusion_pair_must_share_exact_native"])
        self.assertTrue(policy["same_target_fusion_pair_must_share_exact_program_bundle"])
        self.assertTrue(policy["same_target_fusion_pair_must_share_exact_source_tree"])


if __name__ == "__main__":
    unittest.main()
