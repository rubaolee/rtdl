"""Focused hostile tests for the Goal5802 POD-S0 helper CLIs."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts import goal5802_build_combined_runtime_untimed as combined
from scripts import goal5802_build_trust_postuse_custody_receipt as custody
from scripts import goal5802_export_freeze_inputs_untimed as freeze_export


ROOT = Path(__file__).resolve().parents[1]
TRUST = ROOT / (
    "history/internal_docs/goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
    "test_trust_public")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_bytes(canonical(value) + b"\n")


def build_wheel(path: Path, *, version: str = "1.2.3") -> None:
    dist_info = f"demo_pkg-{version}.dist-info"
    members = {
        "demo_pkg/__init__.py": f"__version__ = {version!r}\n".encode(),
        f"{dist_info}/METADATA": (
            f"Metadata-Version: 2.1\nName: demo-pkg\nVersion: {version}\n\n"
        ).encode(),
        f"{dist_info}/WHEEL": (
            "Wheel-Version: 1.0\nGenerator: goal5802-test\n"
            "Root-Is-Purelib: true\nTag: py3-none-any\n\n"
        ).encode(),
        f"{dist_info}/top_level.txt": b"demo_pkg\n",
    }
    record_name = f"{dist_info}/RECORD"
    rows = []
    for name, payload in members.items():
        encoded = base64.urlsafe_b64encode(
            hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
        rows.append([name, f"sha256={encoded}", str(len(payload))])
    rows.append([record_name, "", ""])
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    members[record_name] = stream.getvalue().encode("utf-8")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)


class FreezeInputExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.values = freeze_export.build_values(ROOT)

    def test_authoritative_counts_and_zero_execution_scope(self) -> None:
        self.assertEqual(len(self.values["comparative_schedule"]), 432)
        self.assertEqual(len(self.values["build_cold_schedule"]), 72)
        receipt = freeze_export.build_receipt(ROOT, self.values)
        self.assertEqual(receipt["execution_scope"], {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
            "execution_authority_consumed": False,
            "pod_execution_authorized": False,
            "performance_claim_authorized": False,
        })
        body = dict(receipt)
        seal = body.pop("receipt_sha256")
        self.assertEqual(seal, freeze_export._digest(body))

    def test_export_verify_tamper_and_create_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "freeze_inputs"
            first = freeze_export.export(ROOT, output)
            self.assertEqual(freeze_export.verify(ROOT, output), first)
            with self.assertRaises(FileExistsError):
                freeze_export.export(ROOT, output)
            target = output / "operation_contract.json"
            target.write_bytes(target.read_bytes() + b" ")
            with self.assertRaises(freeze_export.FreezeInputExportError):
                freeze_export.verify(ROOT, output)


class CombinedRuntimePlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.bootstrap = self.root / "bootstrap"
        (self.bootstrap / "virtualenv").mkdir(parents=True)
        (self.bootstrap / "virtualenv" / "__main__.py").write_text(
            "raise SystemExit('test bootstrap must not execute')\n",
            encoding="utf-8")
        for name, version in combined.BOOTSTRAP_DISTRIBUTIONS.items():
            metadata = self.bootstrap / f"{name}-{version}.dist-info" / "METADATA"
            metadata.parent.mkdir()
            metadata.write_text(
                f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n\n",
                encoding="utf-8")
        self.wheel = self.root / "demo_pkg-1.2.3-py3-none-any.whl"
        build_wheel(self.wheel)
        self.output = self.root / "combined"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def plan(self) -> dict[str, object]:
        return combined.build_plan(
            output=self.output,
            base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap,
            wheel_specs=[f"demo={self.wheel}"],
        )

    def test_plan_is_sealed_explicit_and_never_calls_pip_shebang(self) -> None:
        plan = self.plan()
        self.assertEqual(combined._validate_plan(plan), plan)
        install = plan["commands"][1]["argv"]
        self.assertEqual(install[1:6], ["-I", "-S", "-B", "-P", "-c"])
        self.assertIn("runpy.run_module('pip'", install[6])
        self.assertIn("--isolated", install)
        self.assertIn("--no-index", install)
        self.assertIn("--no-deps", install)
        self.assertEqual(install.count("--no-compile"), 1)
        self.assertEqual(
            install[install.index("--target") + 1],
            str(self.output / combined._venv_site_packages_relative(os.name)))
        self.assertTrue(plan["authority_boundary"][
            "plan_sha256_is_integrity_not_input_authority"])
        self.assertEqual(plan["execution_scope"]["formal_worker_count"], 0)
        self.assertEqual(plan["execution_scope"]["registered_performance_timing_count"], 0)
        self.assertEqual(plan["wheels"][0]["distribution"], "demo-pkg")
        self.assertEqual(plan["wheels"][0]["version"], "1.2.3")
        self.assertTrue(plan["pip_invocation_policy"][
            "pip_bytecode_compilation_during_install_forbidden"])

    def test_resealed_plan_cannot_restore_pip_bytecode_compilation(self) -> None:
        plan = self.plan()
        plan["commands"][1]["argv"].remove("--no-compile")
        body = dict(plan)
        body.pop("plan_sha256")
        plan["plan_sha256"] = combined._digest(body)
        with self.assertRaisesRegex(
                combined.CombinedRuntimeError, "fixed offline recipe"):
            combined._validate_plan(plan)

    def test_plan_rejects_duplicate_distribution_and_wheel_drift(self) -> None:
        second = self.root / "second.whl"
        build_wheel(second)
        with self.assertRaises(combined.CombinedRuntimeError):
            combined.build_plan(
                output=self.output, base_python=Path(sys.executable),
                bootstrap_root=self.bootstrap,
                wheel_specs=[f"first={self.wheel}", f"second={second}"],
            )
        plan = self.plan()
        self.wheel.write_bytes(self.wheel.read_bytes() + b"drift")
        with self.assertRaises(combined.CombinedRuntimeError):
            combined._validate_plan_inputs(plan)

    def test_copy_uses_one_opened_payload_and_matches_plan_projection(self) -> None:
        plan = self.plan()
        destination = self.root / "copied.whl"
        original = self.wheel.read_bytes()

        def vulnerable_two_read_probe(*_args, **_kwargs):
            self.wheel.write_bytes(b"MUTATED_AFTER_CHECK")
            raise AssertionError("_copy_exact must not call _file_record")

        with mock.patch.object(
                combined, "_file_record", side_effect=vulnerable_two_read_probe):
            combined._copy_exact(self.wheel, destination, plan["wheels"][0])
        self.assertEqual(destination.read_bytes(), original)

        expected = combined._expected_input_copy_manifest(self.output, plan)
        expected_paths = {
            f"inputs/virtualenv_bootstrap/{row['path']}"
            for row in plan["virtualenv_bootstrap"]["files"]
        }
        expected_paths.update({
            plan["wheels"][0]["saved_path"],
            plan["runner_source"]["saved_path"],
        })
        self.assertEqual({row["path"] for row in expected}, expected_paths)

    def test_create_only_run_receipt_and_failure_preservation(self) -> None:
        plan = self.plan()
        plan_path = self.root / "plan.json"
        combined.write_plan(plan_path, plan)
        snapshot_body = {
            "schema": combined.SNAPSHOT_SCHEMA,
            "status": "PASS__COMPLETE_INSTALLED_DISTRIBUTION_SNAPSHOT",
            "venv_root": str(self.output / "venv"),
            "site_packages": str(
                self.output / combined._venv_site_packages_relative(os.name)),
            "site_module_imported": False,
            "python_executable": {
                "invocation_path": str(self.output / "venv/python"),
                "resolved_path": str(self.output / "venv/python"),
                "path_kind": "REGULAR_FILE", "bytes": 1, "sha256": "0" * 64,
            },
            "package_count": 1,
            "packages": [{
                "distribution": "demo-pkg", "metadata_name": "demo-pkg",
                "version": "1.2.3", "file_count": 1, "payload_bytes": 1,
                "tree_sha256": combined._digest([{
                    "path": "venv/demo_pkg/__init__.py",
                    "bytes": 1, "sha256": "0" * 64,
                }]), "files": [{
                    "path": "venv/demo_pkg/__init__.py",
                    "bytes": 1, "sha256": "0" * 64,
                }],
            }],
        }
        snapshot = {**snapshot_body,
                    "snapshot_sha256": combined._digest(snapshot_body)}
        boundary = {
            "roots": [], "root_count": 0,
            "projection_sha256": combined._digest([]),
        }
        calls = 0

        def fake_run(row, *, output, environment):
            nonlocal calls
            calls += 1
            label = str(row["label"])
            if calls == 1:
                combined._write_create_only(
                    output / "virtualenv_app_data" / "seed.txt", b"seed\n")
                combined._write_create_only(
                    output / combined._venv_python_relative(os.name), b"p")
                combined._write_create_only(
                    output / combined._venv_site_packages_relative(os.name)
                    / "demo_pkg" / "__init__.py", b"x")
            receipt_dir = output / "command_receipts" / label
            combined._write_create_only(
                receipt_dir / "argv.json", canonical(row["argv"]) + b"\n")
            stdout = canonical(snapshot) + b"\n" if calls == 4 else b""
            combined._write_create_only(receipt_dir / "stdout", stdout)
            combined._write_create_only(receipt_dir / "stderr", b"")
            combined._write_create_only(receipt_dir / "exit_code", b"0\n")
            combined._write_create_only(receipt_dir / "environment.json", b"{}\n")
            return subprocess.CompletedProcess(row["argv"], 0, stdout, b"")

        with mock.patch.object(combined, "_run_command", side_effect=fake_run), \
                mock.patch.object(
                    combined, "_capture_current_snapshot", return_value=snapshot), \
                mock.patch.object(
                    combined, "_base_site_boundary", return_value=boundary):
            receipt = combined.run_plan(
                plan_path,
                expected_plan_file_sha256=sha(plan_path.read_bytes()))
        self.assertEqual(receipt["status"],
                         "PASS__OFFLINE_CREATE_ONLY_COMBINED_RUNTIME_BUILT")
        self.assertTrue((self.output / "combined_runtime_receipt.json").is_file())
        hostile = self.output / "venv" / "UNRECEIPTED_HOSTILE_PAYLOAD.txt"
        hostile.write_text("hostile", encoding="utf-8")
        with mock.patch.object(
                combined, "_capture_current_snapshot", return_value=snapshot), \
                mock.patch.object(
                    combined, "_base_site_boundary", return_value=boundary):
            with self.assertRaises(combined.CombinedRuntimeError):
                combined.verify_run(self.output)
        hostile.unlink()
        with self.assertRaises(FileExistsError):
            combined.run_plan(
                plan_path,
                expected_plan_file_sha256=sha(plan_path.read_bytes()))

        failure_output = self.root / "failed_combined"
        failed_plan = combined.build_plan(
            output=failure_output, base_python=Path(sys.executable),
            bootstrap_root=self.bootstrap, wheel_specs=[f"demo={self.wheel}"],
        )
        failed_path = self.root / "failed_plan.json"
        combined.write_plan(failed_path, failed_plan)
        with mock.patch.object(
                combined, "_run_command",
                side_effect=combined.CombinedRuntimeError("injected failure")), \
                mock.patch.object(
                    combined, "_base_site_boundary", return_value=boundary):
            with self.assertRaises(combined.CombinedRuntimeError):
                combined.run_plan(
                    failed_path,
                    expected_plan_file_sha256=sha(failed_path.read_bytes()))
        self.assertTrue((failure_output / "terminal_failure_receipt.json").is_file())
        self.assertFalse((failure_output / "combined_runtime_receipt.json").exists())

    def test_caller_pin_blocks_resealed_plan_replacement_before_output(self) -> None:
        plan = self.plan()
        plan_path = self.root / "plan.json"
        combined.write_plan(plan_path, plan)
        original_file_sha = sha(plan_path.read_bytes())
        replaced = dict(plan)
        replaced["output_directory"] = str(self.root / "attacker-output")
        body = dict(replaced)
        body.pop("plan_sha256")
        replaced["plan_sha256"] = combined._digest(body)
        write_json(plan_path, replaced)
        with self.assertRaises(combined.CombinedRuntimeError):
            combined.run_plan(
                plan_path, expected_plan_file_sha256=original_file_sha)
        self.assertFalse((self.root / "attacker-output").exists())


class TrustPostuseCustodyTest(unittest.TestCase):
    def arguments(self, root: Path) -> argparse.Namespace:
        public_root = TRUST / "root.json"
        public = json.loads(public_root.read_text(encoding="utf-8"))
        preuse = {
            "schema": "rtdl.goal5802.test_trust_key_custody_receipt.v3",
            "key_id": public["key_id"],
            "trust_root_sha256": public["trust_root_sha256"],
            "public_root_file_sha256": sha(public_root.read_bytes()),
            "private_key_file_sha256": "a" * 64,
            "post_use_run_local_receipt_required": True,
            "future_state_not_claimed": True,
        }
        preuse_path = root / "preuse.json"
        write_json(preuse_path, preuse)
        return argparse.Namespace(
            preuse_custody=preuse_path,
            public_root=public_root,
            private_key=root / "absent-private-key.json",
            private_key_state=custody.ABSENT,
            trust_package=[TRUST / "package_seq1.json", TRUST / "package_seq2.json"],
            trust_head=[TRUST / "head_seq1.json", TRUST / "head_seq2.json"],
            expected_deployment_id=None,
            observed_at_utc="2026-08-25T18:00:00Z",
            observation_host_label="TEST_HOST",
            diagnostic_signing_known_minimum=2,
            diagnostic_signing_exact_count=None,
            trust_package_signing_count=2,
            trust_head_signing_count=2,
            formal_worker_count=0,
            registered_timing_count=0,
            untimed_gpu_kernel_launch_count=7,
            output=root / "postuse.json",
        )

    def test_signed_chain_and_absence_never_become_erasure_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self.arguments(Path(temporary))
            receipt = custody.build_receipt(args)
            self.assertEqual(
                receipt["materialized_trust_chain"]["materialized_sequence_count"], 2)
            self.assertEqual(
                receipt["explicit_actual_counters"]["untimed_gpu_kernel_launch_count"], 7)
            self.assertFalse(receipt["claim_boundaries"]["private_key_erasure_attested"])
            self.assertFalse(
                receipt["claim_boundaries"]["private_key_nonrecoverability_attested"])
            self.assertEqual(
                receipt["private_key_observation"]["observed_state"], custody.ABSENT)
            body = dict(receipt)
            seal = body.pop("receipt_sha256")
            self.assertEqual(seal, custody._digest(body))

    def test_explicit_counters_cannot_understate_preserved_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self.arguments(Path(temporary))
            args.trust_package_signing_count = 1
            with self.assertRaises(custody.TrustPostuseError):
                custody.build_receipt(args)
            args = self.arguments(Path(temporary))
            args.registered_timing_count = 1
            with self.assertRaises(custody.TrustPostuseError):
                custody.build_receipt(args)

    def test_head_or_package_reordering_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self.arguments(Path(temporary))
            args.trust_package.reverse()
            with self.assertRaises(custody.TrustPostuseError):
                custody.build_receipt(args)


if __name__ == "__main__":
    unittest.main()
