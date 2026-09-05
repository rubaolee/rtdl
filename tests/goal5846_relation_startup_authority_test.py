from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import goal5846_build_relation_startup_authority as authority


class Goal5846RelationStartupAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = authority.build()

    def test_exact_registered_target_is_met(self) -> None:
        result = self.value["result"]
        self.assertEqual(
            self.value["status"],
            "PASS__GOAL5846_EXACT_WARM_CACHE_FRESH_PROCESS_STARTUP_TARGET_MET__"
            "EXTERNAL_REVIEW_PENDING",
        )
        self.assertEqual(result["registered_samples_per_arm"], 1024)
        self.assertEqual(result["sample_discard_count"], 0)
        self.assertLessEqual(
            result["median_within_block_rtdl_over_pyoptix_setup_plus_first"],
            1.25,
        )
        self.assertLessEqual(
            result["worst_block_rtdl_over_pyoptix_setup_plus_first"], 2.0
        )
        self.assertLessEqual(result["rtdl_steady_over_goal5845_reference"], 1.15)

    def test_first_fill_and_aot_debts_are_not_hidden(self) -> None:
        boundary = self.value["closure_boundary"]
        self.assertGreater(
            self.value["first_ever_cache_fill"]["total_ns"], 30_000_000_000
        )
        self.assertFalse(boundary["first_ever_cache_fill_debt_closed"])
        self.assertFalse(boundary["precompiled_pyoptix_aot_parity_closed"])
        self.assertFalse(boundary["all_startup_performance_debt_closed"])

    def test_claim_ceiling_and_logical_cache_wording_are_exact(self) -> None:
        claim = self.value["claim_boundary"]
        architecture = self.value["architecture_boundary"]
        self.assertTrue(claim["internal_engineering_evidence_only"])
        self.assertFalse(claim["public_or_manuscript_claim_authorized"])
        self.assertFalse(claim["external_review_complete"])
        self.assertFalse(claim["consensus_claimed"])
        self.assertTrue(
            architecture["sealed_cache_policy_is_logical_hit_only_not_os_permission"]
        )

    def test_stored_authority_matches_independent_recount(self) -> None:
        stored = json.loads(authority.AUTHORITY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.value)

    def _copy_capture(self, root: Path) -> Path:
        target = root / "pod_capture"
        shutil.copytree(authority.EVIDENCE_ROOT, target)
        return target

    def test_resealed_worker_substitution_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            capture = self._copy_capture(Path(name))
            path = capture / "registered-transaction/workers/block_00_rtdl.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["measurements"]["steady_public"]["samples_ns"][0] += 1
            timing = value["measurements"]["steady_public"]
            timing["maximum_ns"] = max(timing["samples_ns"])
            value["result_sha256"] = authority._digest(
                {key: item for key, item in value.items() if key != "result_sha256"}
            )
            path.write_text(json.dumps(value), encoding="utf-8")
            path.with_name("block_00_rtdl.stdout.txt").write_text(
                json.dumps(value), encoding="utf-8"
            )
            with (
                patch.object(authority, "EVIDENCE_ROOT", capture),
                self.assertRaisesRegex(RuntimeError, "embedded and retained"),
            ):
                summary = authority._load(
                    capture / "registered-transaction/SUMMARY.json"
                )
                authority._load_workers(summary)

    def test_resealed_native_stamp_mutation_is_rejected(self) -> None:
        summary = authority._load(
            authority.EVIDENCE_ROOT / "registered-transaction/SUMMARY.json"
        )
        receipt = next(
            row["measurements"]["evidence"]["latest_compact_receipt"]
            for row in summary["workers"]
            if row["arm"] == authority.RTDL_ARM
        )
        receipt = json.loads(json.dumps(receipt))
        receipt["native_stamp"][18] ^= 1
        receipt["receipt_sha256"] = authority._digest(
            {key: item for key, item in receipt.items() if key != "receipt_sha256"}
        )
        with self.assertRaisesRegex(RuntimeError, "stamp semantics"):
            authority._validate_compact_receipt(receipt)

    def test_cache_artifact_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            capture = self._copy_capture(Path(name))
            path = next((capture / "executable-cache").glob("*/artifact.json"))
            payload = bytearray(path.read_bytes())
            payload[-2] ^= 1
            path.write_bytes(payload)
            with (
                patch.object(authority, "EVIDENCE_ROOT", capture),
                self.assertRaisesRegex(RuntimeError, "cache artifact differs"),
            ):
                authority._validate_cache_preparation()

    def test_native_symbol_record_removal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            capture = self._copy_capture(Path(name))
            path = capture / "post-formal-v2/native_defined_symbols.txt"
            lines = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if authority.WARM_SYMBOL not in line
            ]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with (
                patch.object(authority, "EVIDENCE_ROOT", capture),
                self.assertRaisesRegex(RuntimeError, "native symbols"),
            ):
                authority._validate_post_formal()


if __name__ == "__main__":
    unittest.main()
