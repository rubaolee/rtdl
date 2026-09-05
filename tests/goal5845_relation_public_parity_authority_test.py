from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import goal5845_build_relation_public_parity_authority as authority


class Goal5845RelationPublicParityAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = authority.build()

    def test_exact_prepared_relation_target_is_met(self) -> None:
        result = self.value["result"]
        self.assertEqual(
            self.value["status"],
            "PASS__GOAL5845_RELATION_PUBLIC_STEADY_PERFORMANCE_DEBT_CLOSED__"
            "EXTERNAL_REVIEW_PENDING",
        )
        self.assertEqual(result["public_samples_per_arm"], 1024)
        self.assertTrue(result["all_samples_retained"])
        self.assertLessEqual(result["median_within_block_rtdl_over_pyoptix"], 1.25)
        self.assertLessEqual(result["worst_block_rtdl_over_pyoptix"], 1.50)
        self.assertGreater(result["rtdl_over_pyoptix_speedup"], 9.0)

    def test_all_blocks_pass_with_stable_order_strata(self) -> None:
        blocks = self.value["result"]["block_rows"]
        self.assertEqual(len(blocks), 8)
        self.assertTrue(all(row["rtdl_over_pyoptix"] <= 1.25 for row in blocks))
        rtdl_first = [row["rtdl_over_pyoptix"] for row in blocks[0::2]]
        pyoptix_first = [row["rtdl_over_pyoptix"] for row in blocks[1::2]]
        self.assertLess(max(rtdl_first) - min(rtdl_first), 0.01)
        self.assertLess(max(pyoptix_first) - min(pyoptix_first), 0.01)

    def test_public_path_retains_checks_and_bounded_native_overhead(self) -> None:
        result = self.value["result"]
        boundary = self.value["architecture_boundary"]
        self.assertLessEqual(result["median_rtdl_public_over_direct_native"], 1.75)
        self.assertEqual(result["attribution_samples_per_layer"], 512)
        self.assertTrue(boundary["two_actual_optix_launches_per_execution"])
        self.assertTrue(boundary["ordinary_path_uses_device_semantic_compaction"])
        self.assertFalse(boundary["ordinary_path_materializes_role_counters"])

    def test_claim_ceiling_remains_internal_and_exact_scope(self) -> None:
        claim = self.value["claim_boundary"]
        self.assertTrue(claim["internal_engineering_evidence_only"])
        self.assertTrue(claim["exact_task_and_prepared_steady_path_only"])
        self.assertFalse(claim["public_or_manuscript_claim_authorized"])
        self.assertFalse(claim["external_review_complete"])
        self.assertFalse(claim["consensus_claimed"])
        self.assertFalse(claim["cold_start_parity_claim_authorized"])
        self.assertFalse(claim["intrinsic_language_or_api_speedup_claim_authorized"])

    def test_stored_authority_matches_independent_recount(self) -> None:
        stored = json.loads(authority.AUTHORITY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.value)

    def _copy_evidence(self, root: Path) -> Path:
        target = root / "evidence"
        shutil.copytree(authority.EVIDENCE_ROOT, target)
        return target

    def test_resealed_worker_timing_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "formal_comparison/workers/block_00_rtdl.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["measurements"]["steady_public"]["samples_ns"][0] += 1
            value["result_sha256"] = authority._digest(
                {key: item for key, item in value.items() if key != "result_sha256"}
            )
            path.write_text(json.dumps(value), encoding="utf-8")
            path.with_name("block_00_rtdl.stdout.txt").write_text(
                json.dumps(value), encoding="utf-8"
            )
            with (
                patch.object(authority, "EVIDENCE_ROOT", evidence),
                self.assertRaisesRegex(RuntimeError, "embedded and retained"),
            ):
                authority.build()

    def test_resealed_native_stamp_semantic_mutation_is_rejected(self) -> None:
        summary = json.loads(
            (authority.EVIDENCE_ROOT / "formal_comparison/SUMMARY.json").read_text(
                encoding="utf-8"
            )
        )
        receipt = next(
            worker["measurements"]["evidence"]["latest_compact_receipt"]
            for worker in summary["workers"]
            if worker["arm"] == authority.RTDL_ARM
        )
        receipt["native_stamp"][18] ^= 1
        receipt["receipt_sha256"] = authority._digest(
            {key: item for key, item in receipt.items() if key != "receipt_sha256"}
        )
        with self.assertRaisesRegex(RuntimeError, "stamp semantics"):
            authority._validate_compact_receipt(receipt)

    def test_fast_receipt_overclaim_is_rejected(self) -> None:
        summary = json.loads(
            (authority.EVIDENCE_ROOT / "formal_comparison/SUMMARY.json").read_text(
                encoding="utf-8"
            )
        )
        receipt = next(
            worker["measurements"]["evidence"]["latest_fast_operation_receipt"]
            for worker in summary["workers"]
            if worker["arm"] == authority.RTDL_ARM
        )
        receipt["role_counters_materialized"] = True
        with self.assertRaisesRegex(RuntimeError, "fast operation receipt"):
            authority._validate_fast_receipt(receipt)

    def test_resealed_transaction_public_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "POD_TRANSACTION.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["claim_boundary"]["public_or_manuscript_claim_authorized"] = True
            value["transaction_sha256"] = authority._digest(
                {
                    key: item
                    for key, item in value.items()
                    if key != "transaction_sha256"
                }
            )
            path.write_text(json.dumps(value), encoding="utf-8")
            with (
                patch.object(authority, "EVIDENCE_ROOT", evidence),
                self.assertRaisesRegex(RuntimeError, "transaction fields"),
            ):
                authority.build()

    def test_native_v8_symbol_record_removal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "post_formal/native_defined_symbols.txt"
            lines = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if authority.NATIVE_SYMBOL not in line
            ]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with (
                patch.object(authority, "EVIDENCE_ROOT", evidence),
                self.assertRaisesRegex(RuntimeError, "native v8 symbol"),
            ):
                authority.build()

    def test_resealed_build_source_substitution_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "native/build_manifest.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["repository"]["source_files"][0]["sha256"] = "0" * 64
            body = dict(value)
            body["result_sha256"] = ""
            value["result_sha256"] = hashlib.sha256(
                value["schema"].encode("ascii")
                + b"\0"
                + authority._canonical_bytes(body)
            ).hexdigest()
            path.write_text(json.dumps(value), encoding="utf-8")
            changed_file_sha = authority._sha256_file(path)
            with (
                patch.object(authority, "EVIDENCE_ROOT", evidence),
                patch.object(
                    authority,
                    "BUILD_MANIFEST_FILE_SHA256",
                    changed_file_sha,
                ),
                patch.object(
                    authority,
                    "BUILD_MANIFEST_RESULT_SHA256",
                    value["result_sha256"],
                ),
                self.assertRaisesRegex(RuntimeError, "Git binding"),
            ):
                authority._validate_build_manifest()


if __name__ == "__main__":
    unittest.main()
