from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import controller
from scripts import goal5801_rtdlexe_trust as trust
from scripts import goal5802_build_trust_postuse_custody_receipt as custody
from scripts import goal5802_create_qualification_trust_preuse as qualification
from scripts import goal5802_run_pod_s0_untimed as s0
from scripts import goal5802_sign_pod_s0_trust_request_offline as signer


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5802_create_qualification_trust_preuse.py"


class Goal5802QualificationTrustPreuseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve()
        cls.repository = ROOT
        cls.owner = cls.base / "owner"
        cls.owner.mkdir()
        cls.reserved_private = cls.base / "reserved-private.json"
        cls.reserved_public = cls.base / "reserved-public.json"
        trust.create_root(
            private_path=cls.reserved_private,
            public_path=cls.reserved_public,
            key_id="TEST_ONLY_goal5802_reserved_unit_key",
            bits=2048,
        )
        cls.args = argparse.Namespace(
            repository=cls.repository,
            private_key=cls.owner / "qualification-private.json",
            public_root=cls.owner / "qualification-public.json",
            diagnostic_receipt=cls.owner / "qualification-diagnostic.json",
            preuse_custody=cls.owner / "qualification-preuse.json",
            key_id="TEST_ONLY_goal5802_final_home_qualification_unit",
            bits=3072,
            reserved_measurement_private_key=cls.reserved_private,
            reserved_measurement_public_root=cls.reserved_public,
            forbidden_private_key_file=[],
            observed_at_utc="2026-08-25T19:00:00-04:00",
            observation_host_label="OWNER_UNIT_HOST",
        )
        reserved_public_value = json.loads(
            cls.reserved_public.read_text(encoding="utf-8"))
        cls.frozen = {
            "RESERVED_MEASUREMENT_PRIVATE_SHA256": hashlib.sha256(
                cls.reserved_private.read_bytes()).hexdigest(),
            "RESERVED_MEASUREMENT_PUBLIC_SHA256": hashlib.sha256(
                cls.reserved_public.read_bytes()).hexdigest(),
            "RESERVED_MEASUREMENT_KEY_ID": reserved_public_value["key_id"],
            "RESERVED_MEASUREMENT_TRUST_ROOT_SHA256":
                reserved_public_value["trust_root_sha256"],
        }
        with mock.patch.multiple(qualification, **cls.frozen):
            cls.preuse = qualification.create(cls.args)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exact_two_real_signatures_and_zero_trust_sequence(self) -> None:
        self.assertEqual(
            qualification.QUALIFICATION_ONLY_KEY_PREFIX,
            controller.QUALIFICATION_ONLY_TRUST_KEY_PREFIX)
        self.assertEqual(
            qualification.QUALIFICATION_ONLY_KEY_PREFIX,
            s0.QUALIFICATION_ONLY_TRUST_KEY_PREFIX)
        diagnostic_payload = self.args.diagnostic_receipt.read_bytes()
        diagnostic = json.loads(diagnostic_payload.decode("utf-8"))
        self.assertEqual(
            diagnostic_payload, qualification._canonical(diagnostic) + b"\n")
        body = dict(diagnostic)
        seal = body.pop("receipt_sha256")
        self.assertEqual(seal, qualification._digest(body))
        self.assertEqual(
            diagnostic["status"], qualification.DIAGNOSTIC_STATUS)
        self.assertEqual(
            diagnostic["diagnostic_signing_invocation_exact_count"], 2)
        self.assertEqual(len(diagnostic["diagnostic_signatures"]), 2)
        self.assertEqual(
            [row["diagnostic_ordinal"]
             for row in diagnostic["diagnostic_signatures"]], [1, 2])
        self.assertEqual(diagnostic["trust_package_signing_invocation_count"], 0)
        self.assertEqual(diagnostic["trust_head_signing_invocation_count"], 0)
        self.assertEqual(diagnostic["materialized_trust_sequence_count"], 0)

        root = trust.runtime._read_trust_root(self.args.public_root)
        modulus = trust._int_b64(root["rsa_modulus_base64"], "root.modulus")
        exponent = int(root["rsa_exponent"])
        for row in diagnostic["diagnostic_signatures"]:
            message = qualification.DIAGNOSTIC_DOMAIN + qualification._canonical(
                row["message_body"])
            self.assertEqual(row["message_sha256"], hashlib.sha256(message).hexdigest())
            signature = base64.b64decode(
                row["signature_base64"], validate=True)
            self.assertEqual(
                row["signature_sha256"], hashlib.sha256(signature).hexdigest())
            qualification._verify_signature(
                message, signature, modulus=modulus, exponent=exponent)

        names = {path.name for path in self.owner.iterdir()}
        self.assertEqual(names, {
            "qualification-private.json", "qualification-public.json",
            "qualification-diagnostic.json", "qualification-preuse.json",
        })
        self.assertFalse(any("package" in name or "head" in name for name in names))

    def test_preuse_is_canonical_bound_distinct_and_accepted_by_postuse(self) -> None:
        payload = self.args.preuse_custody.read_bytes()
        observed = json.loads(payload.decode("utf-8"))
        self.assertEqual(payload, qualification._canonical(observed) + b"\n")
        body = dict(observed)
        seal = body.pop("custody_receipt_sha256")
        self.assertEqual(seal, qualification._digest(body))
        self.assertEqual(observed, self.preuse)
        self.assertTrue(
            observed["diagnostic_keypair_signing_invocation_count_exactly_attested"])
        self.assertEqual(
            observed[
                "diagnostic_keypair_signing_invocation_exact_count_at_receipt_snapshot"],
            2)
        self.assertFalse(observed["reserved_real_measurement_key_used"])
        self.assertTrue(observed["qualification_only_not_formal_measurement_root"])

        root_payload = self.args.public_root.read_bytes()
        root = trust.runtime._read_trust_root(self.args.public_root)
        with mock.patch.multiple(qualification, **self.frozen):
            target = custody._validate_preuse(
                observed, root_payload=root_payload, root=root,
                preuse_path=self.args.preuse_custody,
                public_root_path=self.args.public_root)
        self.assertEqual(target, (6, 1))
        private_payload = self.args.private_key.read_bytes()
        custody._validate_private_key(
            self.args.private_key, private_payload, root=root, preuse=observed)
        reserved = json.loads(self.reserved_private.read_text(encoding="utf-8"))
        created = json.loads(self.args.private_key.read_text(encoding="utf-8"))
        self.assertNotEqual(
            reserved["rsa_modulus_base64"], created["rsa_modulus_base64"])
        self.assertNotEqual(
            hashlib.sha256(self.reserved_private.read_bytes()).hexdigest(),
            observed["private_key_file_sha256"])

    def _hostile_copy(self, name: str) -> tuple[Path, Path, Path]:
        root = self.base / name
        root.mkdir()
        public = root / self.args.public_root.name
        diagnostic = root / self.args.diagnostic_receipt.name
        preuse = root / self.args.preuse_custody.name
        for source, target in (
                (self.args.public_root, public),
                (self.args.diagnostic_receipt, diagnostic),
                (self.args.preuse_custody, preuse)):
            shutil.copy2(source, target)
        return public, diagnostic, preuse

    @staticmethod
    def _write_canonical(path: Path, value: object) -> None:
        path.write_bytes(qualification._canonical(value) + b"\n")

    def _reseal_hostile(
            self, diagnostic_path: Path, preuse_path: Path,
            diagnostic: dict[str, object]) -> None:
        diagnostic_body = dict(diagnostic)
        diagnostic_body.pop("receipt_sha256", None)
        diagnostic["receipt_sha256"] = qualification._digest(diagnostic_body)
        self._write_canonical(diagnostic_path, diagnostic)
        preuse = json.loads(preuse_path.read_text(encoding="utf-8"))
        payload = diagnostic_path.read_bytes()
        preuse["diagnostic_receipt"]["bytes"] = len(payload)
        preuse["diagnostic_receipt"]["sha256"] = hashlib.sha256(
            payload).hexdigest()
        preuse_body = dict(preuse)
        preuse_body.pop("custody_receipt_sha256", None)
        preuse["custody_receipt_sha256"] = qualification._digest(preuse_body)
        self._write_canonical(preuse_path, preuse)

    def test_resealed_signature_and_message_forgeries_reject(self) -> None:
        for case in ("signature", "message"):
            with self.subTest(case=case):
                public_path, diagnostic_path, preuse_path = self._hostile_copy(
                    f"hostile-{case}")
                diagnostic = json.loads(
                    diagnostic_path.read_text(encoding="utf-8"))
                row = diagnostic["diagnostic_signatures"][1]
                if case == "signature":
                    signature = bytearray(base64.b64decode(
                        row["signature_base64"], validate=True))
                    signature[-1] ^= 1
                    row["signature_base64"] = base64.b64encode(
                        signature).decode("ascii")
                    row["signature_sha256"] = hashlib.sha256(
                        signature).hexdigest()
                else:
                    row["message_body"]["purpose"] = (
                        "QUALIFICATION_ONLY__FORGED_PURPOSE")
                    message = qualification.DIAGNOSTIC_DOMAIN \
                        + qualification._canonical(row["message_body"])
                    row["message_sha256"] = hashlib.sha256(message).hexdigest()
                self._reseal_hostile(
                    diagnostic_path, preuse_path, diagnostic)
                root = trust.runtime._read_trust_root(public_path)
                preuse = json.loads(preuse_path.read_text(encoding="utf-8"))
                with mock.patch.multiple(qualification, **self.frozen), \
                        self.assertRaises(qualification.QualificationTrustError):
                    custody._validate_preuse(
                        preuse, root_payload=public_path.read_bytes(), root=root,
                        preuse_path=preuse_path,
                        public_root_path=public_path)

    def test_public_artifacts_exclude_private_envelope_and_exponent(self) -> None:
        private_payload = self.args.private_key.read_bytes()
        private = json.loads(private_payload.decode("utf-8"))
        private_exponent = private[
            "rsa_private_exponent_base64"].encode("ascii")
        for path in (
                self.args.public_root, self.args.diagnostic_receipt,
                self.args.preuse_custody):
            payload = path.read_bytes()
            self.assertNotIn(private_payload, payload)
            self.assertNotIn(private_exponent, payload)

    def _authority(
            self, directory: Path, slot: str,
            capability: list[int]) -> Path:
        body = {
            "schema": signer.AUTHORITY_SCHEMA,
            "authority_version": 1,
            "artifact_sha256": ("1" if slot == "relation" else "2") * 64,
            "artifact_bytes": 17,
            "product_projection_sha256": "3" * 64,
            "protocol_decision_sha256": "4" * 64,
            "executable_identity_sha256": "5" * 64,
            "native_library_sha256": "6" * 64,
            "target_sha256": "7" * 64,
            "deployment_id": f"goal5802/home/{slot}/qualification-unit",
            "family": signer.RELATION_FAMILY if slot == "relation" \
                else signer.TRIANGLE_FAMILY,
            "task_semantics_sha256": "8" * 64,
            "target_compute_capability": capability,
        }
        value = {
            **body,
            "authority_seal": hashlib.sha256(
                signer.trust.runtime._AUTHORITY_DOMAIN
                + signer._canonical(body)).hexdigest(),
        }
        path = directory / f"{slot}.authority.json"
        self._write_canonical(path, value)
        return path

    def _request(
            self, directory: Path, relation: Path, triangle: Path) -> Path:
        def record(path: Path, remote: str) -> dict[str, object]:
            payload = path.read_bytes()
            return {
                "path": remote,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }

        body = {
            "schema": signer.REQUEST_SCHEMA,
            "status": signer.REQUEST_STATUS,
            "prepared_state": {
                "path": "/pod/run/prepared_state.json",
                "bytes": 1,
                "sha256": "9" * 64,
            },
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "public_trust_root": record(
                self.args.public_root, "/pod/source/qualification-public.json"),
            "private_key_sha256": hashlib.sha256(
                self.args.private_key.read_bytes()).hexdigest(),
            "sequence_1": {
                "family": "relation",
                "authority": record(
                    relation, "/pod/run/relation.authority.json"),
                "previous_package_sha256": None,
            },
            "sequence_2": {
                "family": "triangle",
                "authority": record(
                    triangle, "/pod/run/triangle.authority.json"),
                "previous_sequence": 1,
            },
            "candidate_double_seed_sha256": "c" * 64,
            "required_package_signatures": 2,
            "required_head_signatures": 2,
            "private_key_must_never_enter_pod": True,
            "registered_performance_timing_count": 0,
            "formal_worker_count": 0,
            "execution_authority_consumed": False,
        }
        value = {**body, "request_sha256": signer._digest(body)}
        path = directory / "request.json"
        self._write_canonical(path, value)
        return path

    def test_offline_signer_enforces_home_compute_capability(self) -> None:
        for capability, accepted in (([6, 1], True), ([8, 9], False)):
            with self.subTest(capability=capability):
                directory = self.base / f"capability-{capability[0]}-{capability[1]}"
                directory.mkdir()
                relation = self._authority(
                    directory, "relation", capability)
                triangle = self._authority(
                    directory, "triangle", capability)
                request = self._request(directory, relation, triangle)
                operation = lambda: signer._validate_request(
                    request, relation, triangle, self.args.public_root,
                    self.args.private_key, self.args.preuse_custody)
                with mock.patch.multiple(qualification, **self.frozen):
                    if accepted:
                        validated = operation()
                        self.assertEqual(validated[4], 2)
                        self.assertEqual(validated[5], 2)
                        manifest = directory / "candidate-manifest.json"
                        self._write_canonical(manifest, {
                            "candidates": {
                                "relation": {
                                    "authority_path": str(relation),
                                    "deployment_id": json.loads(
                                        relation.read_text(encoding="utf-8"))[
                                            "deployment_id"],
                                },
                                "triangle": {
                                    "authority_path": str(triangle),
                                    "deployment_id": json.loads(
                                        triangle.read_text(encoding="utf-8"))[
                                            "deployment_id"],
                                },
                            },
                        })
                        output = directory / "signed-response"
                        args = argparse.Namespace(
                            request=request,
                            relation_authority=relation,
                            triangle_authority=triangle,
                            public_root=self.args.public_root,
                            private_key=self.args.private_key,
                            preuse_custody=self.args.preuse_custody,
                            observed_at_utc="2026-08-25T20:00:00-04:00",
                            observation_host_label="OWNER_QUALIFICATION_UNIT",
                            output_directory=output,
                        )
                        response = signer.sign_request(args)
                        custody_value = json.loads(
                            (output / "custody_receipt.json").read_text(
                                encoding="utf-8"))
                        counters = custody_value["explicit_actual_counters"]
                        self.assertTrue(counters[
                            "diagnostic_keypair_signing_invocation_count_exactly_attested"])
                        self.assertEqual(counters[
                            "diagnostic_keypair_signing_invocation_exact_count"], 2)
                        target_response = s0._validate_response(
                            output / "signed_trust_response.json", request, {
                                "public_trust_root": str(self.args.public_root),
                                "private_key_sha256": hashlib.sha256(
                                    self.args.private_key.read_bytes()).hexdigest(),
                                "candidate_manifests": {
                                    "seed1": str(manifest),
                                },
                            })
                        self.assertEqual(
                            target_response["status"], signer.RESPONSE_STATUS)
                        hostile = directory / "hostile-scalar-alias-response"
                        shutil.copytree(output, hostile)
                        hostile_custody_path = hostile / "custody_receipt.json"
                        hostile_custody = json.loads(
                            hostile_custody_path.read_text(encoding="utf-8"))
                        hostile_counters = hostile_custody[
                            "explicit_actual_counters"]
                        hostile_counters[
                            "diagnostic_keypair_signing_invocation_count_exactly_attested"] = 1
                        hostile_counters[
                            "diagnostic_keypair_signing_invocation_exact_count"] = 2.0
                        hostile_custody_body = dict(hostile_custody)
                        hostile_custody_body.pop("receipt_sha256")
                        hostile_custody["receipt_sha256"] = signer._digest(
                            hostile_custody_body)
                        self._write_canonical(
                            hostile_custody_path, hostile_custody)
                        hostile_response_path = hostile / "signed_trust_response.json"
                        hostile_response = json.loads(
                            hostile_response_path.read_text(encoding="utf-8"))
                        hostile_payload = hostile_custody_path.read_bytes()
                        hostile_response["custody_receipt"]["bytes"] = len(
                            hostile_payload)
                        hostile_response["custody_receipt"]["sha256"] = \
                            hashlib.sha256(hostile_payload).hexdigest()
                        hostile_response_body = dict(hostile_response)
                        hostile_response_body.pop("response_sha256")
                        hostile_response["response_sha256"] = signer._digest(
                            hostile_response_body)
                        self._write_canonical(
                            hostile_response_path, hostile_response)
                        with self.assertRaisesRegex(
                                s0.S0Error, "counter scalar types"):
                            s0._validate_response(
                                hostile_response_path, request, {
                                    "public_trust_root": str(
                                        self.args.public_root),
                                    "private_key_sha256": hashlib.sha256(
                                        self.args.private_key.read_bytes()
                                    ).hexdigest(),
                                    "candidate_manifests": {
                                        "seed1": str(manifest),
                                    },
                                })
                    else:
                        with self.assertRaisesRegex(
                                signer.OfflineSigningError,
                                "frozen Home compute capability"):
                            operation()

    def test_create_only_outside_repository_and_time_guards(self) -> None:
        with self.assertRaises(FileExistsError):
            qualification.create(self.args)

        inside = argparse.Namespace(**vars(self.args))
        inside.private_key = self.repository / ".goal5802_never_private.json"
        inside.public_root = self.repository / ".goal5802_never_public.json"
        inside.diagnostic_receipt = self.repository / ".goal5802_never_diag.json"
        inside.preuse_custody = self.repository / ".goal5802_never_preuse.json"
        with self.assertRaisesRegex(
                qualification.QualificationTrustError, "outside the repository"):
            qualification.create(inside)

        fresh = self.base / "bad-time"
        fresh.mkdir()
        bad_time = argparse.Namespace(**vars(self.args))
        bad_time.private_key = fresh / "private.json"
        bad_time.public_root = fresh / "public.json"
        bad_time.diagnostic_receipt = fresh / "diagnostic.json"
        bad_time.preuse_custody = fresh / "preuse.json"
        bad_time.observed_at_utc = "2026-08-25T19:00:00"
        with self.assertRaisesRegex(
                qualification.QualificationTrustError, "UTC offset"):
            qualification.create(bad_time)
        self.assertEqual(list(fresh.iterdir()), [])

    def test_legacy_forbidden_private_identity_is_read_without_rewriting(self) \
            -> None:
        path = self.base / "legacy-private-no-terminal-lf.json"
        value = {
            "schema": "rtdl.v4.rtdlexe.owner_rsa_private.v1",
            "modulus": "AQID",
            "private_exponent": "BAUG",
        }
        # The pinned Goal5801 byte predates sorted-key canonicalisation and
        # has no terminal LF.  It remains a strict duplicate-free JSON object.
        payload = (
            b'{"schema":"rtdl.v4.rtdlexe.owner_rsa_private.v1",'
            b'"modulus":"AQID","private_exponent":"BAUG"}')
        path.write_bytes(payload)
        resolved, observed, observed_payload = \
            qualification._forbidden_private_json(path, "legacy private key")
        self.assertEqual(resolved, path.resolve())
        self.assertEqual(observed, value)
        self.assertEqual(observed_payload, payload)
        self.assertEqual(
            qualification._private_modulus_identity(
                observed, "legacy private key"),
            "AQID")

    def test_direct_isolated_cli_entrypoint_is_runnable(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-P", str(SCRIPT), "--help"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--forbidden-private-key-file", completed.stdout)


if __name__ == "__main__":
    unittest.main()
