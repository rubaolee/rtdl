from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
import unittest

from scripts import goal5793_x1_build_s0_reproduction_capsule as builder
from scripts import goal5793_x1_verify_s0_reproduction_capsule as verifier


class Goal5793X1S0ReproductionCapsuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = builder.build_outputs()

    def test_deterministic_archive_twin_manifest_and_audit(self) -> None:
        second = builder.build_outputs()
        self.assertEqual(self.outputs, second)
        self.assertEqual(
            self.outputs[builder.ARCHIVE_NAME], self.outputs[builder.TWIN_NAME]
        )
        manifest = json.loads(self.outputs[builder.MANIFEST_NAME])
        audit = json.loads(self.outputs[builder.AUDIT_NAME])
        self.assertEqual(len(manifest["hostile_fail_ids"]), 20)
        self.assertEqual(audit["checks"]["source_rows_reconstructed"], 326)
        self.assertEqual(audit["checks"]["v26_byte_identical_rows"], 324)
        self.assertEqual(audit["checks"]["current_delta_rows"], 2)
        self.assertEqual(audit["checks"]["hostile_fail_id_pass_count"], 20)

    def test_archive_validates_in_fresh_temp_without_workspace(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_test_") as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            result = verifier.verify_archive(archive)
            self.assertEqual(result["checks"]["workspace_src_reads"], 0)
            self.assertEqual(result["checks"]["git_invocations"], 0)
            self.assertEqual(result["checks"]["network_calls"], 0)
            self.assertEqual(result["checks"]["original_build_documents_calls"], 0)

    def test_embedded_verifier_runs_after_safe_temp_extraction(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_subprocess_") as temp:
            temp_path = Path(temp)
            archive_path = temp_path / builder.ARCHIVE_NAME
            archive_path.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            with tarfile.open(archive_path, "r:gz") as archive:
                for member in archive:
                    self.assertFalse(member.issym() or member.islnk())
                archive.extractall(temp_path, filter="data")
            root = temp_path / verifier.CAPSULE_DIRNAME
            tool = root / "tools/goal5793_x1_verify_s0_reproduction_capsule.py"
            completed = subprocess.run(
                [sys.executable, str(tool), "--capsule-root", str(root)],
                cwd=temp_path,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["hostile_pass_count"], 20)
            self.assertEqual(result["source_rows"], 326)

    def test_payload_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_mutation_") as temp:
            archive = Path(temp) / builder.ARCHIVE_NAME
            archive.write_bytes(self.outputs[builder.ARCHIVE_NAME])
            root = verifier._safe_extract_capsule(archive, Path(temp) / "extract")
            version = root / verifier.DELTA_VERSION_PATH
            version.write_bytes(version.read_bytes() + b"x")
            with self.assertRaises(verifier.VerificationFailure) as raised:
                verifier.verify_capsule_root(root)
            self.assertEqual(raised.exception.fail_id, "CAPSULE_PAYLOAD_MISMATCH")

    def test_create_only_refuses_any_existing_output_before_writing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_create_only_") as temp:
            output_dir = Path(temp)
            sentinel = output_dir / builder.AUDIT_NAME
            sentinel.write_bytes(b"owner")
            with self.assertRaises(FileExistsError):
                builder.write_create_only(output_dir, self.outputs)
            self.assertEqual(sentinel.read_bytes(), b"owner")
            self.assertFalse((output_dir / builder.ARCHIVE_NAME).exists())


if __name__ == "__main__":
    unittest.main()
