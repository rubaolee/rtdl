from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts import goal5847_build_aot_startup_authority as authority


class Goal5847AOTStartupAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.archive = authority.EvidenceArchive()

    def test_recount_matches_stored_authority(self) -> None:
        rebuilt = authority.build()
        stored = json.loads(authority.AUTHORITY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(rebuilt, stored)
        self.assertEqual(
            rebuilt["status"],
            "PASS__GOAL5847_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING",
        )
        performance = rebuilt["performance"]
        self.assertEqual(
            performance["retained_samples_per_arm"],
            {authority.RTDL_ARM: 1024, authority.PYOPTIX_ARM: 1024},
        )
        self.assertLess(performance["median_within_block_primary_ratio"], 0.5)
        self.assertLess(performance["pooled_steady_rtdl_to_pyoptix_ratio"], 0.2)

    def test_verifier_has_no_rtdl_or_gpu_import(self) -> None:
        source = Path(authority.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "from rtdsl",
            "import rtdsl",
            "import cupy",
            "import torch",
            "import numba",
            "import optix",
            "import cuda",
        ):
            self.assertNotIn(forbidden, source)

    def test_captured_member_mutation_is_rejected(self) -> None:
        changed = copy.copy(self.archive)
        changed.members = dict(self.archive.members)
        changed.members["native/build.log"] += b"tampered"
        with self.assertRaisesRegex(RuntimeError, "captured bytes differ"):
            authority._validate_capture(changed)

    def test_resealed_native_counter_mutation_is_rejected(self) -> None:
        worker = self.archive.json(
            "formal/block-00-position-0-RTDL_FAMILY_RTDLEXE_AOT.json"
        )
        receipt = copy.deepcopy(
            worker["measurements"]["evidence"]["diagnostic_traversal_receipt"]
        )
        receipt["native_snapshot"]["successful_launch_count"] = 1
        receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = authority._digest(receipt)
        with self.assertRaisesRegex(RuntimeError, "native counters differ"):
            authority._validate_traversal_receipt(
                receipt,
                route="v4_callback_ir:custom_aabb_bounded_relation_v1",
                output_sha256=authority.OUTPUT_SHA256,
                bundle="v4_custom_aabb_bounded_relation_composed",
                launches=2,
                raygen=8192,
            )

    def test_resealed_timing_summary_mutation_is_rejected(self) -> None:
        worker = self.archive.json(
            "formal/block-00-position-0-RTDL_FAMILY_RTDLEXE_AOT.json"
        )
        timing = copy.deepcopy(
            worker["measurements"]["steady_complete_execution"]
        )
        timing["median_ns"] += 1
        with self.assertRaisesRegex(RuntimeError, "timing differs"):
            authority._timing(timing, 128, label="mutated timing")

    def test_rsa_signature_bit_flip_is_rejected(self) -> None:
        root = self.archive.json("candidates/relation.public.json")
        package = self.archive.json("candidates/relation.package.json")
        modulus = int.from_bytes(
            base64.b64decode(root["rsa_modulus_base64"], validate=True), "big"
        )
        body = dict(package)
        signature = bytearray(
            base64.b64decode(body.pop("signature_base64"), validate=True)
        )
        message = authority._TRUST_PACKAGE_DOMAIN + authority._canonical_bytes(body)
        self.assertTrue(
            authority._rsa_pkcs1_v15_sha256_verify(
                bytes(signature),
                message,
                modulus=modulus,
                exponent=root["rsa_exponent"],
            )
        )
        signature[-1] ^= 1
        self.assertFalse(
            authority._rsa_pkcs1_v15_sha256_verify(
                bytes(signature),
                message,
                modulus=modulus,
                exponent=root["rsa_exponent"],
            )
        )

    def test_archive_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.tar.gz"
            payload = b"bad"
            with tarfile.open(path, "w:gz") as archive_file:
                member = tarfile.TarInfo("../escape")
                member.size = len(payload)
                archive_file.addfile(member, io.BytesIO(payload))
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(RuntimeError, "escapes its root"):
                authority.EvidenceArchive(path, expected_sha256=expected)


if __name__ == "__main__":
    unittest.main()
