from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts import goal5789_a2_build_packet_audit_supplement as supplement


ROOT = Path(__file__).resolve().parents[1]


class Goal5789A2PacketAuditSupplementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.archive = (ROOT / supplement.ARCHIVE_REL).read_bytes()
        cls.twin = (ROOT / supplement.TWIN_REL).read_bytes()
        cls.manifest = (ROOT / supplement.MANIFEST_REL).read_bytes()
        cls.audit_v1 = (ROOT / supplement.AUDIT_REL).read_bytes()

    def test_fixed_packet_reports_payload_identity_and_set_digest(self) -> None:
        result = supplement.audit()
        self.assertEqual(
            result["status"],
            "PASS__APPEND_ONLY_PACKET_PAYLOAD_IDENTITY_AND_PAYLOAD_SET_CHECKS_EXPLICIT",
        )
        self.assertIs(result["checks"]["payload_identity"], True)
        self.assertIs(result["checks"]["payload_set_digest"], True)
        self.assertEqual(result["payload_identity_checked_count"], 120)
        self.assertEqual(result["payload_identity_mismatch_count"], 0)
        self.assertEqual(result["payload_bytes"], 52_007_905)
        self.assertEqual(
            result["payload_set_digest_declared"],
            "a94730860617895531f89473cbb367588d2404848b750429f0621f0bb665c487",
        )
        self.assertEqual(
            result["payload_set_digest_recomputed"],
            result["payload_set_digest_declared"],
        )
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_twin_drift_is_rejected(self) -> None:
        changed = self.twin[:-1] + bytes([self.twin[-1] ^ 1])
        with self.assertRaisesRegex(RuntimeError, "fixed packet, twin, manifest, or audit"):
            supplement.audit(twin_bytes=changed)

    def test_manifest_payload_set_drift_is_rejected(self) -> None:
        manifest = json.loads(self.manifest)
        manifest["payload_set_sha256"] = "0" * 64
        changed = supplement._pretty(manifest)
        with self.assertRaisesRegex(RuntimeError, "fixed packet, twin, manifest, or audit"):
            supplement.audit(manifest_bytes=changed)

    def test_prior_audit_reporting_drift_is_rejected(self) -> None:
        audit = json.loads(self.audit_v1)
        audit["checks"]["payload_identity"] = True
        body = {key: value for key, value in audit.items() if key != "audit_sha256"}
        audit["audit_sha256"] = supplement._sha(supplement._canonical(body))
        changed = supplement._pretty(audit)
        with self.assertRaisesRegex(RuntimeError, "fixed packet, twin, manifest, or audit"):
            supplement.audit(audit_bytes=changed)

    def test_disk_output_matches_fresh_reaudit_when_present(self) -> None:
        if not supplement.OUTPUT.exists():
            self.skipTest("create-only supplemental audit has not been emitted yet")
        self.assertEqual(supplement.OUTPUT.read_bytes(), supplement._pretty(supplement.audit()))


if __name__ == "__main__":
    unittest.main()
