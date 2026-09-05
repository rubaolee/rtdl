from __future__ import annotations

import json
import shutil
import statistics
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.goal5842_causal_admission.contracts import digest
from scripts import goal5844_build_public_parity_authority as authority


class Goal5844PublicParityAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = authority.build()

    def test_adverse_attempt_is_retained(self) -> None:
        attempt = self.value["attempts"]["attempt1_adverse"]
        self.assertEqual(
            attempt["status"], "ADVERSE__CONTINUE_PERFORMANCE_ENGINEERING"
        )
        self.assertGreater(attempt["median_within_block_ratio"], 1.25)
        self.assertTrue(self.value["comparison"]["first_adverse_transaction_retained"])
        self.assertFalse(self.value["comparison"]["transactions_pooled"])

    def test_successor_meets_internal_target_in_every_block(self) -> None:
        attempt = self.value["attempts"]["attempt2_target_met"]
        self.assertEqual(
            attempt["status"], "PASS__INTERNAL_ENGINEERING_TARGET_MET"
        )
        self.assertLessEqual(attempt["median_within_block_ratio"], 1.25)
        self.assertLessEqual(attempt["maximum_block_ratio"], 1.25)

    def test_native_time_remains_stable(self) -> None:
        ratio = self.value["comparison"]["direct_native_median_after_over_before"]
        self.assertGreater(ratio, 0.90)
        self.assertLess(ratio, 1.10)

    def test_claim_ceiling_remains_internal(self) -> None:
        claim = self.value["claim_boundary"]
        self.assertTrue(claim["internal_engineering_evidence_only"])
        self.assertFalse(claim["public_or_manuscript_claim_authorized"])
        self.assertFalse(claim["external_review_complete"])
        self.assertFalse(claim["consensus_claimed"])

    def _copy_evidence(self, root: Path) -> Path:
        target = root / "evidence"
        shutil.copytree(authority.EVIDENCE_ROOT, target)
        return target

    def test_resealed_worker_timing_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = next(
                (evidence / "attempt2_target_met/workers").glob("*RTDL*.json")
            )
            value = json.loads(path.read_text(encoding="utf-8"))
            timing = value["measurements"]["steady_public"]
            timing["samples_ns"][0] += 1
            timing["minimum_ns"] = min(timing["samples_ns"])
            timing["median_ns"] = int(statistics.median(timing["samples_ns"]))
            timing["maximum_ns"] = max(timing["samples_ns"])
            value.pop("result_sha256")
            value["result_sha256"] = digest(value)
            path.write_text(json.dumps(value), encoding="utf-8")
            with patch.object(authority, "EVIDENCE_ROOT", evidence):
                with self.assertRaisesRegex(RuntimeError, "worker hash order"):
                    authority.build()

    def test_dropped_adverse_worker_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            next(
                (evidence / "attempt1_adverse/workers").glob("*RTDL*.json")
            ).unlink()
            with patch.object(authority, "EVIDENCE_ROOT", evidence):
                with self.assertRaisesRegex(RuntimeError, "worker count"):
                    authority.build()

    def test_resealed_public_claim_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "attempt2_target_met/SUMMARY.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["claim_boundary"]["public_or_manuscript_claim_authorized"] = True
            value.pop("result_sha256")
            value["result_sha256"] = digest(value)
            path.write_text(json.dumps(value), encoding="utf-8")
            with patch.object(authority, "EVIDENCE_ROOT", evidence):
                with self.assertRaisesRegex(RuntimeError, "frozen result identity"):
                    authority.build()

    def test_archive_digest_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            evidence = self._copy_evidence(Path(name))
            path = evidence / "attempt2_target_met/FULL_ARCHIVE.sha256"
            path.write_text("0" * 64 + "  /tmp/fake.tar.gz\n", encoding="ascii")
            with patch.object(authority, "EVIDENCE_ROOT", evidence):
                with self.assertRaisesRegex(RuntimeError, "archive digest"):
                    authority.build()


if __name__ == "__main__":
    unittest.main()
