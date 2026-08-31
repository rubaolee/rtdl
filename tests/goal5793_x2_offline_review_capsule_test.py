from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_build_offline_review_capsule as builder
from scripts import goal5793_x2_verify_offline_review_capsule as verifier


ROOT = Path(__file__).resolve().parents[1]


def _refresh_manifest(root: Path, relative: str) -> dict:
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target = root / Path(*relative.split("/"))
    data = target.read_bytes()
    row = next(row for row in manifest["payloads"] if row["path"] == relative)
    row["bytes"] = len(data)
    row["sha256"] = hashlib.sha256(data).hexdigest()
    manifest["payload_summary"] = {
        "file_count": len(manifest["payloads"]),
        "total_bytes": sum(row["bytes"] for row in manifest["payloads"]),
        "rows_sha256": hashlib.sha256(canonical_json_bytes(manifest["payloads"])).hexdigest(),
    }
    manifest["manifest_sha256"] = seal_document(
        manifest, seal_field="manifest_sha256", domain=verifier.MANIFEST_DOMAIN, version=2
    )
    manifest_path.write_bytes(canonical_json_bytes(manifest) + b"\n")
    return manifest


class Goal5793X2OfflineReviewCapsuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = builder.build_outputs()

    def test_01_deterministic_compact_outputs_and_twin(self) -> None:
        again = builder.build_outputs()
        self.assertEqual(self.outputs, again)
        self.assertEqual(self.outputs[builder.ARCHIVE_NAME], self.outputs[builder.TWIN_NAME])
        self.assertLess(len(self.outputs[builder.ARCHIVE_NAME]), 8_000_000)

    def test_02_archive_verifies_from_temporary_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            audit = verifier.verify_archive(archive)
        self.assertTrue(audit["claim_boundary"]["compact_reviewability_closed"])
        self.assertFalse(audit["claim_boundary"]["x2_closure_authorized"])

    def test_03_embedded_standalone_verifier_needs_no_repo_git_or_network(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            extracted = verifier._safe_extract(archive, Path(temp) / "extract")
            tool = extracted / "tools/goal5793_x2_verify_offline_review_capsule.py"
            child_python = os.environ.get("RTDL_X2_ISOLATED_PYTHON", sys.executable)
            result = subprocess.run(
                [child_python, "-B", str(tool), "--capsule-root", str(extracted)],
                cwd=temp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60, check=False,
                env={"PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "RTDL_X2_ISOLATED_PYTHON": child_python},
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_04_coordinated_alias_row_removal_and_reseal_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            root = verifier._safe_extract(archive, Path(temp) / "extract")
            rel = "generated/goal5793_x2_exposure_alias_authority_20260822.json"
            path = root / Path(*rel.split("/"))
            alias = json.loads(path.read_text(encoding="utf-8"))
            alias["rows"] = alias["rows"][:-1]
            alias["counts"]["bibliography_rows"] = 185
            alias["authority_sha256"] = seal_document(alias, seal_field="authority_sha256", domain=verifier.ALIAS_DOMAIN, version=1)
            path.write_bytes(canonical_json_bytes(alias) + b"\n")
            manifest = _refresh_manifest(root, rel)
            with self.assertRaisesRegex(verifier.VerificationFailure, "EXPOSURE_ALIAS_AUTHORITY_MISMATCH"):
                verifier.recompute_audit(root, manifest)

    def test_05_coordinated_live_normative_overclaim_and_reseal_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            root = verifier._safe_extract(archive, Path(temp) / "extract")
            rel = "generated/goal5793_x2_nist_normative_offline_authority_20260822.json"
            path = root / Path(*rel.split("/"))
            authority = json.loads(path.read_text(encoding="utf-8"))
            authority["claim_boundary"]["live_nist_verifier_complete"] = True
            authority["authority_sha256"] = seal_document(
                authority,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x2.nist_normative_offline_authority",
                version=1,
            )
            path.write_bytes(canonical_json_bytes(authority) + b"\n")
            manifest = _refresh_manifest(root, rel)
            with self.assertRaisesRegex(verifier.VerificationFailure, "NIST_NORMATIVE_AUTHORITY_MISMATCH"):
                verifier.recompute_audit(root, manifest)

    def test_06_formal_outputs_are_absent_before_create_only_write(self) -> None:
        for name in (builder.ARCHIVE_NAME, builder.TWIN_NAME, builder.MANIFEST_NAME, builder.AUDIT_NAME):
            self.assertFalse((ROOT / "history/internal_docs" / name).exists())


if __name__ == "__main__":
    unittest.main()
