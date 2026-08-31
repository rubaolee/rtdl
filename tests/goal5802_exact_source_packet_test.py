from __future__ import annotations

import gzip
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import unittest
import warnings
import zipfile

from scripts import goal5802_build_exact_source_packet as builder
from scripts import goal5802_verify_exact_source_packet as verifier


class Goal5802ExactSourcePacketTest(unittest.TestCase):
    @staticmethod
    def _duplicate_tar(second: bytes) -> bytes:
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for payload in (b"first harmless payload\n", second):
                info = tarfile.TarInfo("duplicate/member.bin")
                info.size = len(payload)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(payload))
        return buffer.getvalue()

    @staticmethod
    def _duplicate_zip(second: bytes) -> bytes:
        buffer = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(
                    buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr(
                    "duplicate/member.bin", b"first harmless payload\n")
                archive.writestr("duplicate/member.bin", second)
        return buffer.getvalue()

    def _git(self, repository: Path, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(completed.stderr.decode("utf-8", errors="replace"))
        return completed.stdout.decode("utf-8").strip()

    def _fixture(self, root: Path) -> tuple[Path, str, Path, bytes]:
        repository = root / "source"
        repository.mkdir()
        self._git(repository, "init", "--quiet")
        self._git(repository, "config", "user.name", "Goal5802 Test")
        self._git(repository, "config", "user.email", "goal5802@example.invalid")
        self._git(repository, "config", "core.autocrlf", "false")

        (repository / "lf.txt").write_bytes(b"alpha\nbeta\n")
        (repository / "executable.sh").write_bytes(b"#!/bin/sh\nprintf 'ok\\n'\n")
        # A field name is documentation/code, not leaked key material.  The
        # value-based scanner must not turn this literal into a false positive.
        (repository / "schema.py").write_bytes(
            b'PRIVATE_COMPONENT_FIELD = "rsa_private_exponent_base64"\n')
        with zipfile.ZipFile(
            repository / "harmless.zip", "w", compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            archive.writestr("nested.txt", b"harmless nested bytes\n")
        self._git(
            repository,
            "add", "--", "lf.txt", "executable.sh", "schema.py", "harmless.zip")
        self._git(repository, "update-index", "--chmod=+x", "executable.sh")
        self._git(repository, "commit", "--quiet", "-m", "fixture")
        commit = self._git(repository, "rev-parse", "HEAD")

        secret = b"goal5802-test-private-exponent-value-0123456789abcdef"
        private_key = root / "owner-private-key.json"
        private_key.write_bytes(json.dumps({
            "key_id": "test",
            "rsa_modulus_base64": "public-value",
            "rsa_private_exponent_base64": secret.decode("ascii"),
            "schema": "test.private.v1",
        }, sort_keys=True).encode("utf-8") + b"\n")

        # Simulate the Windows failure mode: work-tree bytes are CRLF while the
        # committed blob remains LF.  The packet must use the object bytes.
        self._git(repository, "config", "core.autocrlf", "true")
        (repository / "lf.txt").write_bytes(b"alpha\r\nbeta\r\n")
        return repository, commit, private_key, secret

    def test_roundtrip_is_object_exact_shallow_clean_and_value_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, commit, private_key, _secret = self._fixture(root)
            packet = root / "source-packet.tar.gz"
            manifest_path = root / "source-packet.manifest.json"
            manifest = builder.build(
                repository, commit, packet, manifest_path, [private_key])

            self.assertEqual(manifest["source_commit"], commit)
            self.assertEqual(manifest["worker_count"], 0)
            self.assertEqual(manifest["registered_performance_timing_count"], 0)
            self.assertEqual(manifest["unregistered_timing_count"], 0)
            rows = {row["path"]: row for row in manifest["source_inventory"]}
            self.assertEqual(rows["lf.txt"]["object_id"], builder._git_blob_sha1(b"alpha\nbeta\n"))
            self.assertNotEqual(rows["lf.txt"]["object_id"], builder._git_blob_sha1(b"alpha\r\nbeta\r\n"))
            self.assertEqual(rows["executable.sh"]["mode"], "100755")
            with tarfile.open(packet, "r:gz") as archive:
                self.assertEqual(archive.pax_headers["comment"], commit)
                self.assertEqual(
                    archive.pax_headers["rtdl.goal5802.schema"],
                    builder.PACKET_SCHEMA,
                )

            receipt = verifier.verify(packet, manifest_path, [private_key])
            self.assertEqual(set(receipt), verifier.RECEIPT_KEYS)
            self.assertEqual(
                receipt["status"],
                "PASS__INDEPENDENT_EXACT_SHALLOW_GIT_CHECKOUT_VERIFIED",
            )
            self.assertTrue(receipt["checkout_clean"])
            self.assertFalse(receipt["checkout_core_autocrlf"])
            self.assertEqual(receipt["shallow_commit_count"], 1)
            self.assertEqual(receipt["checkout_file_blob_match_count"], 4)
            self.assertEqual(receipt["checkout_index_mode_match_count"], 4)
            self.assertEqual(receipt["forbidden_private_key_value_match_count"], 0)
            self.assertEqual(receipt["private_material_scan_container_count"], 1)
            self.assertEqual(receipt["private_material_scan_payload_count"], 5)

            receipt_path = root / "verification.json"
            verifier._write_create_only(
                receipt_path, verifier._canonical(receipt) + b"\n")
            self.assertEqual(
                receipt_path.read_bytes(), verifier._canonical(receipt) + b"\n")
            with self.assertRaises(FileExistsError):
                verifier._write_create_only(
                    receipt_path, verifier._canonical(receipt) + b"\n")

            authority_sha256 = verifier._sha256(receipt_path.read_bytes())
            materialize_root = root / "pod-source-root"
            target_receipt = verifier.verify(
                packet,
                manifest_path,
                private_scan_authority_path=receipt_path,
                private_scan_authority_sha256=authority_sha256,
                materialize_root=materialize_root,
            )
            self.assertEqual(set(target_receipt), verifier.RECEIPT_KEYS)
            self.assertTrue(target_receipt["materialized_source_root"])
            self.assertFalse(target_receipt["private_material_value_scan_executed"])
            self.assertEqual(
                target_receipt["private_material_value_scan_mode"],
                "NOT_REEXECUTED__DETACHED_LOCAL_AUTHORITY_VERIFIED",
            )
            self.assertEqual(
                target_receipt["detached_private_scan_authority_sha256"],
                authority_sha256,
            )
            self.assertEqual(
                target_receipt["materialized_source_tree"], manifest["source_tree"])
            self.assertEqual(
                (materialize_root / "checkout" / "lf.txt").read_bytes(),
                b"alpha\nbeta\n",
            )
            materialized_git = materialize_root / "repository"
            materialized_work_tree = materialize_root / "checkout"
            self.assertEqual(
                verifier._run_git(materialized_git, "rev-parse", "HEAD").decode().strip(),
                commit,
            )
            status_args = ["status", "--porcelain=v1", "--untracked-files=all"]
            if os.name == "nt":
                status_args = ["-c", "core.filemode=false", *status_args]
            self.assertEqual(
                verifier._run_git(
                    materialized_git, *status_args, work_tree=materialized_work_tree),
                b"",
            )
            with self.assertRaises(FileExistsError):
                verifier.verify(
                    packet,
                    manifest_path,
                    private_scan_authority_path=receipt_path,
                    private_scan_authority_sha256=authority_sha256,
                    materialize_root=materialize_root,
                )
            with self.assertRaisesRegex(RuntimeError, "byte identity mismatch"):
                verifier.verify(
                    packet,
                    manifest_path,
                    private_scan_authority_path=receipt_path,
                    private_scan_authority_sha256="0" * 64,
                )
            with self.assertRaises(FileExistsError):
                builder.build(repository, commit, packet, root / "other.json", [private_key])

    def test_duplicate_archive_members_are_all_scanned_not_rejected_or_skipped(
            self) -> None:
        secret = b"goal5802-second-duplicate-private-value-0123456789"
        safe = b"second harmless payload\n"
        for module in (builder, verifier):
            for label, payload in (
                    ("duplicate.tar.gz", self._duplicate_tar(safe)),
                    ("duplicate.zip", self._duplicate_zip(safe))):
                statistics = {
                    "bytes": 0, "container_count": 0, "payload_count": 0}
                module._scan_private_stream(
                    io.BytesIO(payload), label, set(), [secret], statistics, 0)
                self.assertEqual(statistics["container_count"], 1)
                self.assertEqual(statistics["payload_count"], 3)

            for label, payload in (
                    ("duplicate.tar.gz", self._duplicate_tar(secret)),
                    ("duplicate.zip", self._duplicate_zip(secret))):
                statistics = {
                    "bytes": 0, "container_count": 0, "payload_count": 0}
                with self.assertRaisesRegex(
                        RuntimeError, "actual private-key value") as caught:
                    module._scan_private_stream(
                        io.BytesIO(payload), label, set(), [secret],
                        statistics, 0)
                self.assertIn("occurrence=2", str(caught.exception))

    def test_packet_and_manifest_mutation_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, commit, private_key, _secret = self._fixture(root)
            packet = root / "source-packet.tar.gz"
            manifest_path = root / "source-packet.manifest.json"
            builder.build(repository, commit, packet, manifest_path, [private_key])

            changed_packet = root / "changed.tar.gz"
            payload = bytearray(packet.read_bytes())
            payload[len(payload) // 2] ^= 1
            changed_packet.write_bytes(payload)
            with self.assertRaisesRegex(RuntimeError, "packet byte identity mismatch"):
                verifier.verify(changed_packet, manifest_path, [private_key])

            hostile = json.loads(manifest_path.read_text(encoding="utf-8"))
            hostile["source_inventory"][0]["mode"] = (
                "100755" if hostile["source_inventory"][0]["mode"] == "100644" else "100644")
            hostile_manifest = root / "hostile.json"
            hostile_manifest.write_bytes(verifier._canonical(hostile) + b"\n")
            with self.assertRaisesRegex(RuntimeError, "source inventory digest mismatch"):
                verifier.verify(packet, hostile_manifest, [private_key])

            wrong_key = root / "wrong-private-key.json"
            wrong_key.write_text(
                json.dumps({"rsa_private_exponent_base64": "x" * 64}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "authority mismatch"):
                verifier.verify(packet, manifest_path, [wrong_key])

    def test_checkout_preserves_a_path_beyond_legacy_windows_max_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _commit, private_key, _secret = self._fixture(root)
            self._git(repository, "config", "core.autocrlf", "false")
            self._git(repository, "config", "core.longpaths", "true")
            relative = Path(*(["long-segment-0123456789"] * 12)) / "payload.txt"
            blob = subprocess.run(
                ["git", "-C", str(repository), "hash-object", "-w", "--stdin"],
                input=b"long path exact payload\n",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            ).stdout.decode("ascii").strip()
            self._git(
                repository, "update-index", "--add", "--cacheinfo",
                f"100644,{blob},{relative.as_posix()}")
            self._git(repository, "commit", "--quiet", "-m", "long path")
            commit = self._git(repository, "rev-parse", "HEAD")
            packet = root / "long-path-packet.tar.gz"
            manifest = root / "long-path-manifest.json"
            builder.build(repository, commit, packet, manifest, [private_key])
            receipt = verifier.verify(packet, manifest, [private_key])
            self.assertEqual(
                receipt["status"],
                "PASS__INDEPENDENT_EXACT_SHALLOW_GIT_CHECKOUT_VERIFIED")
            self.assertEqual(
                receipt["checkout_file_blob_match_count"], 5)

    def test_actual_private_value_or_exact_key_file_is_rejected_but_field_name_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repository, _commit, private_key, secret = self._fixture(root)

            # The first commit, which contains only the field-name literal,
            # already passed in the round-trip test.  Adding the actual value
            # under a neutral filename must fail.
            self._git(repository, "config", "core.autocrlf", "false")
            (repository / "neutral.dat").write_bytes(b"prefix:" + secret + b":suffix\n")
            self._git(repository, "add", "--", "neutral.dat")
            self._git(repository, "commit", "--quiet", "-m", "leak actual value")
            leaked_commit = self._git(repository, "rev-parse", "HEAD")
            with self.assertRaisesRegex(RuntimeError, "actual private-key value"):
                builder.build(
                    repository,
                    leaked_commit,
                    root / "leaked.tar.gz",
                    root / "leaked.json",
                    [private_key],
                )

            self._git(repository, "reset", "--hard", "HEAD~1")
            (repository / "commit-marker.txt").write_text("marker\n", encoding="utf-8")
            self._git(repository, "add", "--", "commit-marker.txt")
            self._git(
                repository,
                "commit", "--quiet", "-m", f"accidental {secret.decode('ascii')}")
            message_commit = self._git(repository, "rev-parse", "HEAD")
            with self.assertRaisesRegex(RuntimeError, "Git commit object"):
                builder.build(
                    repository,
                    message_commit,
                    root / "message.tar.gz",
                    root / "message.json",
                    [private_key],
                )

            self._git(repository, "reset", "--hard", "HEAD~1")
            nested_zip = repository / "neutral.zip"
            with zipfile.ZipFile(nested_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("neutral.bin", b"compressed:" + secret + b"\n")
            self._git(repository, "add", "--", "neutral.zip")
            self._git(repository, "commit", "--quiet", "-m", "nested value")
            nested_commit = self._git(repository, "rev-parse", "HEAD")
            with self.assertRaisesRegex(RuntimeError, "actual private-key value"):
                builder.build(
                    repository,
                    nested_commit,
                    root / "nested.tar.gz",
                    root / "nested.json",
                    [private_key],
                )

            self._git(repository, "reset", "--hard", "HEAD~1")
            shutil.copyfile(private_key, repository / "ordinary.json")
            self._git(repository, "add", "--", "ordinary.json")
            self._git(repository, "commit", "--quiet", "-m", "leak exact file")
            exact_commit = self._git(repository, "rev-parse", "HEAD")
            with self.assertRaisesRegex(
                RuntimeError, "exact private-key file|actual private-key value"):
                builder.build(
                    repository,
                    exact_commit,
                    root / "exact.tar.gz",
                    root / "exact.json",
                    [private_key],
                )

    def test_archive_link_is_rejected_before_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = root / "link.tar.gz"
            with packet.open("wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                    with tarfile.open(
                        fileobj=compressed,
                        mode="w",
                        format=tarfile.PAX_FORMAT,
                        pax_headers={
                            "comment": "0" * 40,
                            "rtdl.goal5802.schema": verifier.PACKET_SCHEMA,
                        },
                    ) as archive:
                        info = tarfile.TarInfo("repository/HEAD")
                        info.type = tarfile.SYMTYPE
                        info.linkname = "../../outside"
                        archive.addfile(info)
            with self.assertRaisesRegex(RuntimeError, "link or special"):
                verifier._extract_packet(
                    packet,
                    "0" * 40,
                    {"repository/HEAD": {
                        "bytes": 0,
                        "mode": "0644",
                        "path": "repository/HEAD",
                        "sha256": verifier._sha256(b""),
                    }},
                    root / "extract",
                )


if __name__ == "__main__":
    unittest.main()
