from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import goal5801_independent_closeout_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "history" / "internal_docs" / "goal5801_rtdlexe_lx1_untimed_evidence_20260824"


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _rewrite_manifest(root: Path) -> None:
    path = root / "manifest.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in sorted(root.rglob("*")):
        if not item.is_file() or item == path:
            continue
        payload = item.read_bytes()
        rows.append({
            "bytes": len(payload),
            "path": item.relative_to(root).as_posix(),
            "sha256": _sha(payload),
        })
    rows.sort(key=lambda row: row["path"])
    value["files"] = rows
    value["file_count"] = len(rows)
    value["total_payload_bytes"] = sum(row["bytes"] for row in rows)
    path.write_bytes(json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8"))


class Goal5801IndependentCloseoutVerifierTest(unittest.TestCase):
    def _copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name) / "packet"
        shutil.copytree(PACKET, root)
        _rewrite_manifest(root)
        return temporary, root

    def test_actual_raw_packet_passes_without_rtdsl_import(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        result = verifier.verify(root)
        self.assertEqual(result["status"], "PASS__INDEPENDENT_RAW_CLOSEOUT_VERIFICATION")
        self.assertFalse(result["imports_rtdsl"])
        self.assertEqual(result["trusted_authority_count"], 4)
        self.assertEqual(result["compiled_reducer_case_count"], 12)
        self.assertEqual(result["lifecycle_lock_count"], 4)
        self.assertTrue(result["v11_custody_present"])
        self.assertGreaterEqual(result["v11_prebuild_source_file_count"], 500)
        self.assertEqual(result["v11_candidate_hash_seed_count"], 3)

    def test_v11_source_listing_maps_paths_to_digests(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        result = verifier._verify_v11_custody(root)
        self.assertTrue(result["v11_custody_present"])
        self.assertGreaterEqual(result["v11_prebuild_source_file_count"], 500)

    def test_coherently_rehashed_result_mutation_still_fails_semantics(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        result_path = root / "evidence_v2" / "lifecycle_result.json"
        value = json.loads(result_path.read_text(encoding="utf-8"))
        value["relation"]["repeat_device_status"]["prepared_input_reused"] = False
        result_path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        stdout = root / "evidence_v2" / "lifecycle.stdout"
        stdout.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
        _rewrite_manifest(root)
        with self.assertRaisesRegex(verifier.VerificationError, "fixed success facts"):
            verifier.verify(root)

    def test_coherently_rehashed_package_mutation_fails_rsa(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        path = root / "test_trust_public" / "package_seq2.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["authorities"][0]["family"] = "coherent-but-unsigned-forgery"
        path.write_bytes(verifier._canonical(value) + b"\n")
        _rewrite_manifest(root)
        with self.assertRaisesRegex(verifier.VerificationError, "RSA PKCS#1"):
            verifier.verify(root)

    def test_coherently_rehashed_semantic_proof_mutation_fails_frozen_pin(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        proof = root / "semantic_proof" / "semantic_spec.json"
        proof.write_bytes(proof.read_bytes() + b"\n")
        _rewrite_manifest(root)
        with self.assertRaisesRegex(verifier.VerificationError, "semantic proof identity"):
            verifier.verify(root)

    def test_authority_and_artifact_integer_versions_reject_bool_aliases(self):
        temporary, root = self._copy()
        self.addCleanup(temporary.cleanup)
        candidate = root / "candidates_v10"
        original_authority = json.loads(
            (candidate / "relation.authority.json").read_text(encoding="utf-8"))
        artifact = candidate / "artifacts" / (
            original_authority["artifact_sha256"] + ".rtdlexe")

        authority = dict(original_authority)
        authority["authority_version"] = True
        body = dict(authority); body.pop("authority_seal")
        authority["authority_seal"] = _sha(
            verifier.AUTHORITY_DOMAIN + verifier._canonical(body))
        authority_path = Path(temporary.name) / "bool-version.authority.json"
        authority_path.write_bytes(verifier._canonical(authority) + b"\n")
        with self.assertRaisesRegex(verifier.VerificationError, "schema/version"):
            verifier._verify_artifact_authority(
                artifact, authority_path, exact_execution_contract=True)

        artifact_value = json.loads(artifact.read_text(encoding="utf-8"))
        artifact_value["format_version"] = True
        artifact_path = Path(temporary.name) / "bool-format.rtdlexe"
        artifact_payload = verifier._canonical(artifact_value) + b"\n"
        artifact_sha = _sha(artifact_payload)
        artifact_path = artifact_path.with_name(artifact_sha + ".rtdlexe")
        artifact_path.write_bytes(artifact_payload)
        authority = dict(original_authority)
        authority["artifact_sha256"] = artifact_sha
        authority["artifact_bytes"] = len(artifact_payload)
        body = dict(authority); body.pop("authority_seal")
        authority["authority_seal"] = _sha(
            verifier.AUTHORITY_DOMAIN + verifier._canonical(body))
        authority_path = Path(temporary.name) / "bool-format.authority.json"
        authority_path.write_bytes(verifier._canonical(authority) + b"\n")
        with self.assertRaisesRegex(verifier.VerificationError, "schema/version"):
            verifier._verify_artifact_authority(
                artifact_path, authority_path, exact_execution_contract=True)


if __name__ == "__main__":
    unittest.main()
