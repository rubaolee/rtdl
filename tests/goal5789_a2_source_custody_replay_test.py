from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import goal5789_a2_validate_source_custody_replay as custody


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / custody.PACKET_REL
SOURCE_ARCHIVE = ROOT / custody.SOURCE_ARCHIVE_REL
WORK_AUTHORITY = ROOT / custody.WORK_AUTHORITY_REL
SUPPLEMENT = ROOT / custody.SUPPLEMENT_REL
VALIDATOR = ROOT / custody.VALIDATOR_REL
TEST = ROOT / custody.TEST_REL


class Goal5789A2SourceCustodyReplayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = custody.load_packet(PACKET)
        cls.source = custody.load_source_custody(SOURCE_ARCHIVE)
        cls.work_authority, cls.work_authority_bytes = custody.load_work_authority(
            WORK_AUTHORITY
        )

    def test_exact_immutable_source_custody_chain(self) -> None:
        custody.verify_a2_roots(self.packet, self.source)
        source = self.source.payloads[custody.RTXRMQ_SOURCE_REL]
        self.assertEqual(len(source), 10_553)
        self.assertEqual(custody.sha(source), custody.RTXRMQ_SOURCE_SHA256)
        source_row = next(
            row
            for row in self.source.manifest["payloads"]
            if row["path"] == custody.RTXRMQ_SOURCE_REL
        )
        self.assertEqual(source_row["size"], 10_553)
        self.assertEqual(source_row["sha256"], custody.RTXRMQ_SOURCE_SHA256)

        certificate = json.loads(
            self.packet.payloads[custody.HELDOUT_CERTIFICATE_REL]
        )
        self.assertEqual(
            certificate["evidence_contract"]["source_pins"][custody.RTXRMQ_SOURCE_REL],
            custody.RTXRMQ_SOURCE_SHA256,
        )

    def test_stored_supplement_is_exact_reconstruction(self) -> None:
        reconstructed = custody.reconstruct_supplement_bytes(
            PACKET,
            SOURCE_ARCHIVE,
            WORK_AUTHORITY,
            VALIDATOR,
            TEST,
        )
        self.assertEqual(reconstructed, SUPPLEMENT.read_bytes())
        value = json.loads(reconstructed)
        body = {
            key: item for key, item in value.items() if key != "supplement_sha256"
        }
        self.assertEqual(value["supplement_sha256"], custody.sha(custody.canonical(body)))
        self.assertFalse(
            value["source_custody"]["mutable_workspace_rtxrmq_source_used_as_authority"]
        )
        self.assertEqual(
            value["work_authority"]["file_sha256"], custody.WORK_AUTHORITY_SHA256
        )

    def test_materializer_replays_exactly_from_two_frozen_inputs(self) -> None:
        original_read_bytes = Path.read_bytes
        forbidden_live_source = (ROOT / custody.RTXRMQ_SOURCE_REL).resolve()

        def guarded_read_bytes(path: Path) -> bytes:
            if path.resolve() == forbidden_live_source:
                raise AssertionError("validator attempted to read mutable live RTXRMQ source")
            return original_read_bytes(path)

        with patch.object(Path, "read_bytes", guarded_read_bytes):
            result = custody.validate_and_replay(
                PACKET,
                SOURCE_ARCHIVE,
                SUPPLEMENT,
                WORK_AUTHORITY,
                VALIDATOR,
                TEST,
            )
        self.assertEqual(
            result["status"],
            "PASS__EXACT_A2_MATERIALIZER_REPLAY_FROM_TWO_FROZEN_INPUTS",
        )
        self.assertEqual(result["replay"]["program_count"], 5)
        self.assertEqual(result["replay"]["executed_leaf_count"], 26)
        self.assertEqual(result["replay"]["admitted_binding_count"], 4)
        self.assertEqual(result["replay"]["consumer_source_count"], 5)
        self.assertTrue(result["replay"]["callback_authority_byte_identical"])
        self.assertTrue(result["replay"]["callback_authority_pin_byte_identical"])
        self.assertFalse(result["custody_checks"]["mutable_workspace_rtxrmq_source_read"])
        self.assertTrue(all(value is False for value in result["authorization"].values()))

    def test_coherently_resealed_supplement_redirect_is_rejected(self) -> None:
        value = json.loads(SUPPLEMENT.read_bytes())
        value["source_custody"]["rtxrmq_consumer_source"]["file_sha256"] = "0" * 64
        body = {
            key: item for key, item in value.items() if key != "supplement_sha256"
        }
        value["supplement_sha256"] = custody.sha(custody.canonical(body))
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_custody_redirect_") as temporary:
            mutated = Path(temporary) / "mutated.json"
            mutated.write_bytes(custody.pretty(value))
            with self.assertRaisesRegex(RuntimeError, "not exact reconstruction"):
                custody.load_supplement(
                    mutated,
                    self.packet,
                    self.source,
                    self.work_authority,
                    self.work_authority_bytes,
                    VALIDATOR.read_bytes(),
                    TEST.read_bytes(),
                )

    def test_wrong_source_archive_is_rejected_before_extraction(self) -> None:
        mutated = bytearray(SOURCE_ARCHIVE.read_bytes())
        mutated[-1] ^= 1
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_wrong_source_") as temporary:
            path = Path(temporary) / "wrong.tar.gz"
            path.write_bytes(mutated)
            with self.assertRaisesRegex(RuntimeError, "source archive identity mismatch"):
                custody.load_source_custody(path)

    def test_path_aliases_fail_closed(self) -> None:
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
                custody.safe_relative(value)


if __name__ == "__main__":
    unittest.main()
