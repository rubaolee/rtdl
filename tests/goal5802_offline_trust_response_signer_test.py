from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5802_sign_pod_s0_trust_request_offline.py"
SPEC = importlib.util.spec_from_file_location("goal5802_offline_signer", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
signer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(signer)
S0_SCRIPT = ROOT / "scripts" / "goal5802_run_pod_s0_untimed.py"
S0_SPEC = importlib.util.spec_from_file_location("goal5802_pod_s0", S0_SCRIPT)
assert S0_SPEC is not None and S0_SPEC.loader is not None
s0 = importlib.util.module_from_spec(S0_SPEC)
S0_SPEC.loader.exec_module(s0)


def _write(path: Path, value: object) -> None:
    path.write_bytes(signer._canonical(value) + b"\n")


def _record(path: Path, remote: str | None = None) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": remote or str(path),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


class Goal5802OfflineTrustResponseSignerTest(unittest.TestCase):
    def test_reserved_formal_key_requires_exact_tracked_preuse_byte(self) -> None:
        path = signer.FORMAL_MEASUREMENT_PREUSE_PATH
        payload = path.read_bytes()
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            signer.FORMAL_MEASUREMENT_PREUSE_SHA256)
        root = {"key_id": signer.FORMAL_MEASUREMENT_KEY_ID}
        signer._enforce_formal_preuse_identity(root, path, payload)

        copied = self.base / "copied_formal_preuse.json"
        copied.write_bytes(payload)
        with self.assertRaisesRegex(
                signer.OfflineSigningError,
                "formal-measurement pre-use receipt identity"):
            signer._enforce_formal_preuse_identity(root, copied, payload)
        signer._enforce_formal_preuse_identity(
            {"key_id": "TEST_ONLY_goal5802_unit_root"}, copied, payload)

    def test_direct_script_entrypoint_is_runnable_from_repository_root(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", "-B", "-P", str(SCRIPT), "--help"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--preuse-custody", completed.stdout)

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temporary.name).resolve()
        cls.private = cls.base / "outside_repo_private.json"
        cls.root = cls.base / "public_root.json"
        with contextlib.redirect_stdout(io.StringIO()):
            signer.trust.create_root(
                private_path=cls.private, public_path=cls.root,
                key_id="TEST_ONLY_goal5802_unit_root", bits=2048)
        cls.relation = cls._authority("relation")
        cls.triangle = cls._authority("triangle")
        root_value = json.loads(cls.root.read_text(encoding="utf-8"))
        cls.preuse = cls.base / "preuse.json"
        _write(cls.preuse, {
            "schema": "rtdl.goal5802.test_trust_key_custody_receipt.v3",
            "status": "TEST_ONLY_PRETARGET_CUSTODY_SNAPSHOT__ZERO_TRUST_SEQUENCE_MATERIALIZED",
            "key_id": root_value["key_id"],
            "trust_root_sha256": root_value["trust_root_sha256"],
            "public_root_file_sha256": hashlib.sha256(
                cls.root.read_bytes()).hexdigest(),
            "private_key_file_sha256": hashlib.sha256(
                cls.private.read_bytes()).hexdigest(),
            "post_use_run_local_receipt_required": True,
            "future_state_not_claimed": True,
            "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot": 2,
        })

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def _authority(cls, slot: str) -> Path:
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
            "deployment_id": f"goal5801/lx1/{slot}/unit-v1",
            "family": signer.RELATION_FAMILY if slot == "relation" \
                else signer.TRIANGLE_FAMILY,
            "task_semantics_sha256": "8" * 64,
            "target_compute_capability": [8, 9],
        }
        value = {
            **body,
            "authority_seal": hashlib.sha256(
                signer.trust.runtime._AUTHORITY_DOMAIN
                + signer._canonical(body)).hexdigest(),
        }
        path = cls.base / f"{slot}.authority.json"
        _write(path, value)
        return path

    def _request_value(self) -> dict[str, object]:
        body = {
            "schema": signer.REQUEST_SCHEMA,
            "status": signer.REQUEST_STATUS,
            "prepared_state": {
                "path": "/pod/run/prepared_state.json",
                "bytes": 123,
                "sha256": "9" * 64,
            },
            "source_commit": "a" * 40,
            "source_tree": "b" * 40,
            "public_trust_root": _record(
                self.root, "/pod/source/history/internal_docs/public_root.json"),
            "private_key_sha256": hashlib.sha256(
                self.private.read_bytes()).hexdigest(),
            "sequence_1": {
                "family": "relation",
                "authority": _record(
                    self.relation, "/pod/run/seed1/relation.authority.json"),
                "previous_package_sha256": None,
            },
            "sequence_2": {
                "family": "triangle",
                "authority": _record(
                    self.triangle, "/pod/run/seed1/triangle.authority.json"),
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
        return {**body, "request_sha256": signer._digest(body)}

    def _request(self, name: str, value: dict[str, object] | None = None) -> Path:
        path = self.base / name
        _write(path, value or self._request_value())
        return path

    def _args(self, request: Path, output: Path, **changes: object) \
            -> argparse.Namespace:
        values = {
            "request": request,
            "relation_authority": self.relation,
            "triangle_authority": self.triangle,
            "private_key": self.private,
            "public_root": self.root,
            "preuse_custody": self.preuse,
            "observed_at_utc": "2026-08-25T16:00:00-04:00",
            "observation_host_label": "owner-unit-host",
            "output_directory": output,
        }
        values.update(changes)
        return argparse.Namespace(**values)

    def test_end_to_end_exact_two_sequence_portable_response(self) -> None:
        request = self._request("request_pass.json")
        output = self.base / "response_pass"
        with contextlib.redirect_stdout(io.StringIO()):
            response = signer.sign_request(self._args(request, output))
        self.assertEqual(response["status"], signer.RESPONSE_STATUS)
        self.assertEqual(
            {path.name for path in output.iterdir()}, {
                "package_seq1.json", "head_seq1.json", "package_seq2.json",
                "head_seq2.json", "custody_receipt.json",
                "signed_trust_response.json",
            })
        signer._validate_response_envelope(response)
        for role in (
                "package_seq1", "head_seq1", "package_seq2", "head_seq2",
                "custody_receipt"):
            self.assertEqual(Path(response[role]["path"]).parent, Path("."))
            payload = (output / response[role]["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(),
                             response[role]["sha256"])
        root = signer.trust.runtime._read_trust_root(self.root)
        package1, entries1 = signer.trust.runtime._verify_trust_package(
            output / "package_seq1.json", root=root)
        package2, entries2 = signer.trust.runtime._verify_trust_package(
            output / "package_seq2.json", root=root)
        self.assertEqual(package1["sequence"], 1)
        self.assertEqual(package2["sequence"], 2)
        self.assertEqual(len(entries1), 1)
        self.assertEqual(len(entries2), 2)
        self.assertEqual(
            package2["previous_package_sha256"],
            hashlib.sha256((output / "package_seq1.json").read_bytes()).hexdigest())
        custody_value = json.loads(
            (output / "custody_receipt.json").read_text(encoding="utf-8"))
        counters = custody_value["explicit_actual_counters"]
        self.assertEqual(counters["trust_package_signing_invocation_count"], 2)
        self.assertEqual(counters["trust_head_signing_invocation_count"], 2)
        self.assertEqual(counters["formal_worker_count"], 0)
        self.assertEqual(counters["registered_performance_timing_count"], 0)
        self.assertFalse(
            custody_value["claim_boundaries"]["private_key_committed_or_embedded"])
        private_value = json.loads(self.private.read_text(encoding="utf-8"))
        private_exponent = private_value[
            "rsa_private_exponent_base64"].encode("ascii")
        self.assertTrue(all(
            private_exponent not in path.read_bytes() for path in output.iterdir()))

        candidate_manifest = self.base / "candidate_manifest_for_s0.json"
        _write(candidate_manifest, {
            "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
            "status": "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED",
            "registered_timing_count": 0,
            "candidates": {
                "relation": {
                    "authority_path": str(self.relation),
                    "deployment_id": json.loads(
                        self.relation.read_text())["deployment_id"],
                },
                "triangle": {
                    "authority_path": str(self.triangle),
                    "deployment_id": json.loads(
                        self.triangle.read_text())["deployment_id"],
                },
            },
        })
        validated = s0._validate_response(
            output / "signed_trust_response.json", request,
            {
                "public_trust_root": str(self.root),
                "private_key_sha256": hashlib.sha256(
                    self.private.read_bytes()).hexdigest(),
                "candidate_manifests": {"seed1": str(candidate_manifest)},
            },
        )
        self.assertEqual(validated["status"], signer.RESPONSE_STATUS)

    def test_request_authority_private_and_root_mismatches_reject(self) -> None:
        value = self._request_value()
        value["private_key_sha256"] = "0" * 64
        body = dict(value); body.pop("request_sha256")
        value["request_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer.sign_request(self._args(
                self._request("request_bad_private.json", value),
                self.base / "response_bad_private"))
        self.assertFalse((self.base / "response_bad_private").exists())

        value = self._request_value()
        value["public_trust_root"]["sha256"] = "0" * 64
        body = dict(value); body.pop("request_sha256")
        value["request_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer.sign_request(self._args(
                self._request("request_bad_root.json", value),
                self.base / "response_bad_root"))

        altered = self.base / "relation_altered.authority.json"
        authority = json.loads(self.relation.read_text(encoding="utf-8"))
        authority["target_sha256"] = "f" * 64
        authority_body = dict(authority); authority_body.pop("authority_seal")
        authority["authority_seal"] = hashlib.sha256(
            signer.trust.runtime._AUTHORITY_DOMAIN
            + signer._canonical(authority_body)).hexdigest()
        _write(altered, authority)
        with self.assertRaises(signer.OfflineSigningError):
            signer.sign_request(self._args(
                self._request("request_bad_authority.json"),
                self.base / "response_bad_authority",
                relation_authority=altered))

    def test_existing_output_extra_and_duplicate_request_keys_reject(self) -> None:
        request = self._request("request_existing.json")
        existing = self.base / "response_existing"
        existing.mkdir()
        with self.assertRaises(FileExistsError):
            signer.sign_request(self._args(request, existing))

        value = self._request_value()
        value["unexpected"] = False
        body = dict(value); body.pop("request_sha256")
        value["request_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer.sign_request(self._args(
                self._request("request_extra.json", value),
                self.base / "response_extra"))

        duplicate = self.base / "request_duplicate.json"
        raw = signer._canonical(self._request_value())
        duplicate.write_bytes(b'{"schema":"duplicate",' + raw[1:] + b"\n")
        with self.assertRaises(signer.OfflineSigningError):
            signer.sign_request(self._args(
                duplicate, self.base / "response_duplicate"))

    def test_wrong_custody_counter_or_claim_rejects(self) -> None:
        output = self.base / "response_for_counter_mutation"
        with contextlib.redirect_stdout(io.StringIO()):
            signer.sign_request(self._args(
                self._request("request_counter.json"), output))
        receipt = json.loads(
            (output / "custody_receipt.json").read_text(encoding="utf-8"))
        relation = json.loads(self.relation.read_text(encoding="utf-8"))
        triangle = json.loads(self.triangle.read_text(encoding="utf-8"))

        hostile = copy.deepcopy(receipt)
        hostile["explicit_actual_counters"][
            "trust_package_signing_invocation_count"] = 3
        body = dict(hostile); body.pop("receipt_sha256")
        hostile["receipt_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer._validate_custody_receipt(
                hostile,
                root_payload_sha=hashlib.sha256(self.root.read_bytes()).hexdigest(),
                private_sha=hashlib.sha256(self.private.read_bytes()).hexdigest(),
                relation_deployment=relation["deployment_id"],
                triangle_deployment=triangle["deployment_id"],
                diagnostic_minimum=2,
                diagnostic_exact=None)

        response = json.loads(
            (output / "signed_trust_response.json").read_text(encoding="utf-8"))
        response["unexpected"] = False
        body = dict(response); body.pop("response_sha256")
        response["response_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer._validate_response_envelope(response)

        hostile = copy.deepcopy(receipt)
        hostile["claim_boundaries"]["performance_claim_authorized"] = True
        body = dict(hostile); body.pop("receipt_sha256")
        hostile["receipt_sha256"] = signer._digest(body)
        with self.assertRaises(signer.OfflineSigningError):
            signer._validate_custody_receipt(
                hostile,
                root_payload_sha=hashlib.sha256(self.root.read_bytes()).hexdigest(),
                private_sha=hashlib.sha256(self.private.read_bytes()).hexdigest(),
                relation_deployment=relation["deployment_id"],
                triangle_deployment=triangle["deployment_id"],
                diagnostic_minimum=2,
                diagnostic_exact=None)


if __name__ == "__main__":
    unittest.main()
