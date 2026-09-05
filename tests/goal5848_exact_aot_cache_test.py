from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from rtdsl.v4_aot_cache import (
    REQUIRED_OUTPUT_ROLES,
    ExactAOTBuildRequest,
    ExactAOTCacheError,
    resolve_exact_aot,
)


class Goal5848ExactAOTCacheTest(unittest.TestCase):
    @staticmethod
    def _payload(role, fallback):
        return b"goal5848-trust-root" if role == "trust_root" else fallback

    @staticmethod
    def _request():
        return ExactAOTBuildRequest(
            source_commit="a" * 40,
            source_tree="b" * 40,
            family="bounded_relation",
            route_identity="v4:test",
            deployment_id="test-slot",
            task_semantics_sha256="1" * 64,
            native_library_sha256="2" * 64,
            target_sha256="3" * 64,
            toolchain_sha256="4" * 64,
            build_roots_sha256="5" * 64,
            compiler_source_manifest_sha256="6" * 64,
            signing_policy_sha256="7" * 64,
            trust_root_file_sha256=hashlib.sha256(
                b"goal5848-trust-root"
            ).hexdigest(),
        )

    def test_exact_hit_never_invokes_producer_again(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls = {"producer": 0, "verifier": 0}

            def producer(root):
                calls["producer"] += 1
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(
                        role, f"{role}-bytes".encode()
                    ))
                    outputs[role] = path
                return outputs

            def verifier(paths):
                calls["verifier"] += 1
                return tuple(sorted(paths))

            first = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=verifier,
            )
            second = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=verifier,
            )
            self.assertFalse(first.cache_hit)
            self.assertTrue(first.producer_invoked)
            self.assertTrue(second.cache_hit)
            self.assertFalse(second.producer_invoked)
            self.assertEqual(calls, {"producer": 1, "verifier": 2})
            self.assertEqual(first.output_sha256, second.output_sha256)

    def test_request_identity_change_is_a_miss(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls = 0

            def producer(root):
                nonlocal calls
                calls += 1
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(
                        role, f"{role}-{calls}".encode()
                    ))
                    outputs[role] = path
                return outputs

            verifier = lambda paths: tuple(paths)
            resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=verifier,
            )
            changed = replace(self._request(), target_sha256="8" * 64)
            second = resolve_exact_aot(
                changed,
                cache_root=temporary,
                producer=producer,
                verifier=verifier,
            )
            self.assertFalse(second.cache_hit)
            self.assertEqual(calls, 2)

    def test_every_bound_request_field_changes_exact_identity(self):
        request = self._request()
        replacements = {
            "source_commit": "c" * 40,
            "source_tree": "d" * 40,
            "family": "triangle_reduction",
            "route_identity": "v4:changed",
            "deployment_id": "changed-slot",
            "task_semantics_sha256": "8" * 64,
            "native_library_sha256": "9" * 64,
            "target_sha256": "a" * 64,
            "toolchain_sha256": "b" * 64,
            "build_roots_sha256": "c" * 64,
            "compiler_source_manifest_sha256": "d" * 64,
            "signing_policy_sha256": "e" * 64,
            "trust_root_file_sha256": "f" * 64,
        }
        for field, value in replacements.items():
            with self.subTest(field=field):
                changed = replace(request, **{field: value})
                self.assertNotEqual(
                    changed.identity_sha256,
                    request.identity_sha256,
                )

    def test_corrupted_entry_fails_without_rebuild(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls = 0

            def producer(root):
                nonlocal calls
                calls += 1
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            first = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=lambda paths: tuple(paths),
            )
            artifact = first.output_paths["artifact"]
            artifact.chmod(0o600)
            artifact.write_text("corrupt")
            with self.assertRaisesRegex(ExactAOTCacheError, "bytes differ"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=producer,
                    verifier=lambda paths: tuple(paths),
                )
            self.assertEqual(calls, 1)

    def test_incomplete_producer_never_publishes_entry(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                path = root / "artifact"
                path.write_bytes(b"artifact")
                return {"artifact": path}

            with self.assertRaisesRegex(ExactAOTCacheError, "roles"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=producer,
                    verifier=lambda paths: tuple(paths),
                )
            entries = Path(temporary) / "entries"
            self.assertEqual(list(entries.iterdir()), [])

    def test_hardening_failure_never_publishes_entry(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            original_chmod = Path.chmod

            def fail_payload_hardening(path, mode, *args, **kwargs):
                if path.name == "payloads" and mode == 0o500:
                    raise OSError("injected hardening failure")
                return original_chmod(path, mode, *args, **kwargs)

            with patch.object(
                    Path, "chmod", autospec=True,
                    side_effect=fail_payload_hardening), \
                    self.assertRaisesRegex(
                        OSError, "injected hardening failure"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=producer,
                    verifier=lambda paths: tuple(paths),
                )
            entries = Path(temporary) / "entries"
            self.assertEqual(list(entries.iterdir()), [])

    def test_entry_hardening_failure_rolls_back_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def producer(producer_root):
                producer_root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = producer_root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            original_chmod = Path.chmod

            def fail_entry_hardening(path, mode, *args, **kwargs):
                if path.parent.name == "entries" and mode == 0o500:
                    raise OSError("injected entry hardening failure")
                return original_chmod(path, mode, *args, **kwargs)

            with patch.object(
                    Path, "chmod", autospec=True,
                    side_effect=fail_entry_hardening), \
                    self.assertRaisesRegex(
                        OSError, "injected entry hardening failure"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=root,
                    producer=producer,
                    verifier=lambda paths: tuple(paths),
                )
            self.assertEqual(list((root / "entries").iterdir()), [])

    def test_symbolic_payload_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                real = root / "real"
                real.write_bytes(b"payload")
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    os.symlink(real, path)
                    outputs[role] = path
                return outputs

            with self.assertRaisesRegex(ExactAOTCacheError, "symbolic"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=producer,
                    verifier=lambda paths: tuple(paths),
                )

    def test_concurrent_exact_requests_publish_once(self):
        with tempfile.TemporaryDirectory() as temporary:
            calls = 0
            calls_lock = threading.Lock()
            barrier = threading.Barrier(4)
            results = []
            errors = []

            def producer(root):
                nonlocal calls
                with calls_lock:
                    calls += 1
                time.sleep(0.02)
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            def resolve():
                try:
                    barrier.wait()
                    results.append(resolve_exact_aot(
                        self._request(),
                        cache_root=temporary,
                        producer=producer,
                        verifier=lambda paths: tuple(paths),
                    ))
                except (ExactAOTCacheError, OSError, RuntimeError) as error:
                    errors.append(error)

            threads = [threading.Thread(target=resolve) for _ in range(4)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=2)
            self.assertEqual(errors, [])
            self.assertEqual(len(results), 4)
            self.assertEqual(calls, 1)
            self.assertEqual(sum(row.producer_invoked for row in results), 1)
            self.assertEqual(sum(row.cache_hit for row in results), 3)

    def test_symbolic_lock_file_fails_before_producer(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "entries").mkdir()
            locks = root / "locks"
            locks.mkdir()
            (root / "staging").mkdir()
            target = root / "target"
            target.write_text("not a lock")
            lock = locks / f"{self._request().identity_sha256}.lock"
            os.symlink(target, lock)
            with self.assertRaisesRegex(ExactAOTCacheError, "lock"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=root,
                    producer=lambda _: self.fail("producer called"),
                    verifier=lambda paths: tuple(paths),
                )

    def test_coherently_resealed_trust_root_substitution_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            first = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=lambda paths: tuple(paths),
            )
            entry = first.entry_path
            payloads = entry / "payloads"
            trust_root = payloads / "trust_root.bin"
            entry.chmod(0o700)
            payloads.chmod(0o700)
            trust_root.chmod(0o600)
            replacement = b"attacker-controlled-self-signed-root"
            trust_root.write_bytes(replacement)
            manifest_path = entry / "manifest.json"
            manifest_path.chmod(0o600)
            manifest = json.loads(manifest_path.read_bytes())
            manifest["outputs"]["trust_root"]["bytes"] = len(replacement)
            manifest["outputs"]["trust_root"]["sha256"] = hashlib.sha256(
                replacement
            ).hexdigest()
            unsigned = dict(manifest)
            unsigned.pop("entry_sha256")
            def canonical(value):
                return json.dumps(
                    value,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                    allow_nan=False,
                ).encode("ascii")
            manifest["entry_sha256"] = hashlib.sha256(
                canonical(unsigned)
            ).hexdigest()
            manifest_path.write_bytes(canonical(manifest) + b"\n")
            with self.assertRaisesRegex(ExactAOTCacheError, "trust root"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=lambda _: self.fail("producer called"),
                    verifier=lambda paths: tuple(paths),
                )

    def test_duplicate_manifest_key_fails_at_json_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            first = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=lambda paths: tuple(paths),
            )
            manifest = first.entry_path / "manifest.json"
            first.entry_path.chmod(0o700)
            manifest.chmod(0o600)
            raw = manifest.read_bytes()
            manifest.write_bytes(raw.rstrip()[:-1] + b',"schema":"duplicate"}\n')
            with self.assertRaisesRegex(ExactAOTCacheError, "duplicate JSON key"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=lambda _: self.fail("producer called"),
                    verifier=lambda paths: tuple(paths),
                )

    def test_nonfinite_manifest_value_fails_at_json_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            def producer(root):
                root.mkdir()
                outputs = {}
                for role in REQUIRED_OUTPUT_ROLES:
                    path = root / role
                    path.write_bytes(self._payload(role, role.encode()))
                    outputs[role] = path
                return outputs

            first = resolve_exact_aot(
                self._request(),
                cache_root=temporary,
                producer=producer,
                verifier=lambda paths: tuple(paths),
            )
            manifest = first.entry_path / "manifest.json"
            first.entry_path.chmod(0o700)
            manifest.chmod(0o600)
            raw = manifest.read_bytes()
            manifest.write_bytes(raw.rstrip()[:-1] + b',"nonfinite":NaN}\n')
            with self.assertRaisesRegex(ExactAOTCacheError, "non-finite JSON value"):
                resolve_exact_aot(
                    self._request(),
                    cache_root=temporary,
                    producer=lambda _: self.fail("producer called"),
                    verifier=lambda paths: tuple(paths),
                )


if __name__ == "__main__":
    unittest.main()
