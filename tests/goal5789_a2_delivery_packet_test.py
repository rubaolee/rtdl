from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5789_a2_audit_review_packet as packet_auditor
from scripts import goal5789_a2_build_review_packet as packet_builder
from scripts import goal5789_a2_build_external_review_entrypoint as entrypoint_builder


ROOT = Path(__file__).resolve().parents[1]


class Goal5789A2DeliveryPacketTest(unittest.TestCase):
    def test_packet_rebuild_is_byte_identical_and_audit_rebuild_is_exact(self) -> None:
        archive, manifest_bytes, manifest = packet_builder.build_packet()
        self.assertEqual(archive, packet_builder.ARCHIVE.read_bytes())
        self.assertEqual(archive, packet_builder.TWIN.read_bytes())
        self.assertEqual(manifest_bytes, packet_builder.MANIFEST.read_bytes())
        self.assertEqual(manifest["payload_count"], len(manifest["payloads"]))
        rebuilt_audit = packet_auditor.audit()
        stored_audit = json.loads(packet_auditor.OUTPUT.read_bytes())
        self.assertEqual(rebuilt_audit, stored_audit)

    def test_packet_claim_and_authorization_boundaries_are_explicit(self) -> None:
        manifest = json.loads(packet_builder.MANIFEST.read_bytes())
        self.assertEqual(manifest["claim_boundary"]["goal5793_generalization_evidence_count"], 0)
        self.assertEqual(manifest["claim_boundary"]["user_usability_study_count"], 0)
        self.assertFalse(manifest["claim_boundary"]["generalization_claimed"])
        self.assertFalse(manifest["claim_boundary"]["easy_or_better_than_cuda_optix_claimed"])
        self.assertTrue(all(value is False for value in manifest["authorization"].values()))

    def test_packet_path_validator_rejects_unsafe_variants(self) -> None:
        for value in (
            "../escape",
            "/absolute",
            "drive:C/file",
            "nested\\backslash",
            "./alias",
            "nested//alias",
            "nested/./alias",
        ):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                packet_builder._safe(value)
        for member in (
            f"{packet_auditor.PREFIX}/./alias",
            f"{packet_auditor.PREFIX}/nested//alias",
            f"{packet_auditor.PREFIX}//alias",
        ):
            with self.subTest(member=member), self.assertRaises(RuntimeError):
                packet_auditor._safe_member(member)

    def test_delivery_claim_overreach_is_rejected_even_after_resigning(self) -> None:
        delivery = json.loads((ROOT / packet_builder.DELIVERY_REL).read_bytes())
        delivery["claim_boundary"]["generalization_claimed"] = True
        delivery["authorization"]["authorizes_goal5793"] = True
        body = {
            key: value
            for key, value in delivery.items()
            if key != "delivery_manifest_sha256"
        }
        delivery["delivery_manifest_sha256"] = hashlib.sha256(
            packet_builder._canonical(body)
        ).hexdigest()
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_delivery_claim_") as temporary:
            temporary_root = Path(temporary)
            path = temporary_root / packet_builder.DELIVERY_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(delivery, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            original_root = packet_builder.ROOT
            packet_builder.ROOT = temporary_root
            try:
                with self.assertRaisesRegex(RuntimeError, "scope or claim"):
                    packet_builder._load_delivery()
            finally:
                packet_builder.ROOT = original_root

    def test_packet_claim_overreach_is_rejected_before_archive_trust(self) -> None:
        manifest = json.loads(packet_builder.MANIFEST.read_bytes())
        manifest["claim_boundary"]["generalization_claimed"] = True
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_packet_claim_") as temporary:
            path = Path(temporary) / "mutated_manifest.json"
            path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            original_manifest = packet_auditor.MANIFEST
            packet_auditor.MANIFEST = path
            try:
                with self.assertRaisesRegex(RuntimeError, "status, claim, or authorization"):
                    packet_auditor.audit()
            finally:
                packet_auditor.MANIFEST = original_manifest

    def test_entrypoint_rejects_stale_resigned_packet_audit(self) -> None:
        original_load = entrypoint_builder._load

        def mutated_load(relative: str) -> dict[str, object]:
            value = deepcopy(original_load(relative))
            if relative == entrypoint_builder.PACKET_AUDIT_REL:
                value["archive"]["file_sha256"] = "0" * 64
                body = {
                    key: item
                    for key, item in value.items()
                    if key != "audit_sha256"
                }
                value["audit_sha256"] = entrypoint_builder._sha(
                    entrypoint_builder._canonical(body)
                )
            return value

        entrypoint_builder._load = mutated_load
        try:
            with self.assertRaisesRegex(RuntimeError, "stale packet audit archive identity"):
                entrypoint_builder.build_outputs()
        finally:
            entrypoint_builder._load = original_load


if __name__ == "__main__":
    unittest.main()
