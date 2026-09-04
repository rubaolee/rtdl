from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5843_build_final_authority.py"
EVIDENCE = (
    ROOT / "history/internal_docs/goal5843_post_r1_fair_baseline_20260904"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "goal5843_build_final_authority", SCRIPT
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Goal5843 final authority builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class Goal5843FinalAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_module()
        cls.authority = cls.module.build()
        cls.preregistration = _load_json(EVIDENCE / "PREREGISTRATION.json")

    def test_stored_authority_rederives_exactly(self):
        stored = _load_json(EVIDENCE / "GOAL5843_FINAL_INTERNAL_AUTHORITY.json")
        self.assertEqual(stored, self.authority)
        observed = stored["authority_sha256"]
        unsealed = dict(stored)
        unsealed.pop("authority_sha256")
        self.assertEqual(observed, self.module.digest(unsealed))

    def test_completion_and_claim_ceiling_are_exact(self):
        self.assertEqual(
            self.authority["status"],
            "PASS__GOAL5843_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING",
        )
        self.assertEqual(
            self.authority["counts"],
            {
                "composites": 108,
                "subworker_receipts": 216,
                "rtdl_triangle_receipt_gate_passes": 36,
                "bound_artifacts": 6,
                "external_reviews": 0,
            },
        )
        boundary = self.authority["claim_boundary"]
        self.assertTrue(boundary["internal_technical_evidence_only"])
        self.assertFalse(boundary["public_performance_claim_authorized"])
        self.assertFalse(boundary["manuscript_performance_claim_authorized"])
        self.assertFalse(boundary["external_review_or_consensus"])

    def test_v4_archive_and_recounts_are_exact(self):
        archive = EVIDENCE / "FORMAL_TRANSACTION.tar.gz"
        verification = _load_json(EVIDENCE / "ARCHIVE_VERIFICATION.json")
        pod_recount = (EVIDENCE / "POD_RECOUNT.json").read_bytes()
        local_recount = (EVIDENCE / "LOCAL_RECOUNT.json").read_bytes()
        self.assertEqual(
            _sha256(archive),
            "0b8374a70c2fc06f538f45a1911099d4ae5b87bc8ab93f239af2c900fbbf014a",
        )
        self.assertEqual(verification["archive_sha256"], _sha256(archive))
        self.assertEqual(pod_recount, local_recount)
        self.assertTrue(verification["pod_local_recount_byte_identical"])

    def test_terminal_v3_transaction_is_preserved_and_not_pooled(self):
        records = self.preregistration["superseded_formal_transactions"]
        self.assertEqual(len(records), 1)
        record = records[0]
        archive = EVIDENCE / "FORMAL_TRANSACTION_V3_TERMINAL_ARCHIVE_VERIFIER_FAILURE.tar.gz"
        self.assertEqual(record["transaction_id"], "GOAL5843_V3")
        self.assertEqual(
            record["terminal_status"],
            "TERMINAL__V3_POST_DOWNLOAD_ARCHIVE_VERIFIER_MODE_NORMALIZATION_DEFECT__NO_RETRY",
        )
        self.assertFalse(record["downloaded_archive_verification_complete"])
        self.assertFalse(record["rows_eligible_for_successor_pooling"])
        self.assertFalse(record["post_worker_zero_retry_used"])
        self.assertEqual(record["formal_timing_samples_recorded"], 7020)
        self.assertEqual(_sha256(archive), record["archive_sha256"])

    def test_goal5838_frozen_core_hashes_remain_exact(self):
        expected = self.preregistration["frozen_core_sha256"]
        self.assertEqual(
            set(expected),
            {
                "src/rtdsl/v4_family.py",
                "src/rtdsl/v4_family_schema.py",
                "src/rtdsl/v4_generic_family_lifecycle.py",
            },
        )
        for relative, expected_sha256 in expected.items():
            with self.subTest(path=relative):
                self.assertEqual(_sha256(ROOT / relative), expected_sha256)


if __name__ == "__main__":
    unittest.main()
