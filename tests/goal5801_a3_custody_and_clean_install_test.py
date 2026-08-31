from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
from scripts import goal5801_a3_verify_native_custody as verifier
from scripts import goal5801_a3_verify_clean_install as clean_verifier
from scripts import goal5801_a3_clean_install_probe as clean_probe
from scripts import goal5801_a3_run_clean_install as clean_runner
from scripts import goal5802_verify_local_premeasurement_freeze as freeze_verifier


CAPTURE = ROOT / "scripts" / "goal5801_a3_capture_native_custody.py"
PROBE = ROOT / "scripts" / "goal5801_a3_clean_install_probe.py"


class Goal5801A3CustodyAndCleanInstallTest(unittest.TestCase):
    def test_clean_probe_binds_goal5802_threshold_before_building_fixtures(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "candidate.json"
            current = {
                "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
                "relation_protocol": {
                    "capacity": 4096,
                    "minimum_overlap_boundary": "inclusive",
                    "minimum_overlap_f32": 1.0,
                    "minimum_overlap_f32_bits": 0x3F800000,
                },
            }
            path.write_text(json.dumps(current), encoding="utf-8")
            self.assertEqual(
                clean_probe._goal5802_relation_protocol(path),
                current["relation_protocol"])
            for hostile in (
                    {**current, "schema": (
                        "rtdl.goal5801.lx1_untimed_candidate_manifest.v1")},
                    {**current, "relation_protocol": {
                        **current["relation_protocol"],
                        "minimum_overlap_f32": 0.0,
                        "minimum_overlap_f32_bits": 0,
                    }},
                    {**current, "relation_protocol": {
                        **current["relation_protocol"],
                        "minimum_overlap_f32": True,
                    }}):
                path.write_text(json.dumps(hostile), encoding="utf-8")
                with self.assertRaisesRegex(
                        RuntimeError, "exact Goal5802 relation protocol"):
                    clean_probe._goal5802_relation_protocol(path)

        source = PROBE.read_text(encoding="utf-8")
        self.assertIn("(0.5, 0.5, 1.5, 1.5, 10)", source)
        self.assertIn("(0.25, 2.0, 1.25, 3.0, index)", source)
        self.assertNotIn("(1.0, 1.0, 1.5, 1.5, 10)", source)
        self.assertNotIn("(0.1, 1.0, 0.2, 1.1, index)", source)

    def test_candidate_manifest_v2_cross_binds_relation_threshold(self) -> None:
        manifest = {
            "schema": "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
            "relation_protocol": {
                "capacity": 4096,
                "minimum_overlap_boundary": "inclusive",
                "minimum_overlap_f32": 1.0,
                "minimum_overlap_f32_bits": 0x3F800000,
            },
        }
        artifact = {
            "product_projection": {
                "runtime": {
                    "capacity": 4096,
                    "minimum_overlap_f32": 1.0,
                },
            },
        }
        clean_verifier._verify_candidate_relation_protocol(manifest, artifact)
        for label, changed_manifest, changed_artifact in (
                ("manifest/artifact threshold drift", manifest, {
                    "product_projection": {"runtime": {
                        "capacity": 4096, "minimum_overlap_f32": 0.0}}}),
                ("manifest bit-pattern drift", {
                    **manifest,
                    "relation_protocol": {
                        **manifest["relation_protocol"],
                        "minimum_overlap_f32_bits": 0,
                    }}, artifact),
                ("non-f32 threshold", {
                    **manifest,
                    "relation_protocol": {
                        **manifest["relation_protocol"],
                        "minimum_overlap_f32": 0.1,
                    }}, artifact)):
            with self.subTest(label=label), self.assertRaises(RuntimeError):
                clean_verifier._verify_candidate_relation_protocol(
                    changed_manifest, changed_artifact)

    def test_clean_verifier_positively_pins_controlling_trust_root(self) -> None:
        controlling = (
            "3364f744a637e27710319001c2fa505bd6c54f75904b51429de253bcd4da8dc4"
        )
        self.assertEqual(
            clean_verifier.CONTROLLING_TRUST_ROOT_FILE_SHA256, controlling)
        clean_verifier._verify_controlling_trust_root_sha256(controlling)
        for untrusted in (
            *clean_verifier.RETIRED_TEST_TRUST_ROOT_DISCLOSURE,
            "0" * 64,
            None,
        ):
            with self.subTest(untrusted=untrusted):
                with self.assertRaisesRegex(
                        RuntimeError, "controlling trust-root file identity"):
                    clean_verifier._verify_controlling_trust_root_sha256(untrusted)

        current_path = (
            ROOT / "history/internal_docs/"
            "goal5802_rtx_measurement_test_trust_public_root_v5_20260826.json")
        self.assertEqual(
            hashlib.sha256(current_path.read_bytes()).hexdigest(), controlling)
        current, _ = clean_verifier._read_json(current_path, canonical_lf=True)
        current_body = dict(current)
        current_seal = current_body.pop("trust_root_sha256")
        self.assertEqual(
            current_seal,
            hashlib.sha256(
                clean_verifier.TRUST_ROOT_DOMAIN
                + clean_verifier._canonical(current_body)).hexdigest())

    def test_clean_verifier_qualification_root_is_explicit_and_nonformal(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root_path = Path(temporary) / "qualification_root.json"
            value = {
                "key_id": (
                    "TEST_ONLY_goal5802_final_home_qualification_unit_test"),
            }
            root_path.write_bytes(
                json.dumps(
                    value, separators=(",", ":"), sort_keys=True
                ).encode("utf-8") + b"\n")
            expected = hashlib.sha256(root_path.read_bytes()).hexdigest()

            with self.assertRaisesRegex(
                    RuntimeError, "controlling trust-root file identity"):
                clean_verifier._verify_trust_root_file_identity(root_path)
            scope, observed = clean_verifier._verify_trust_root_file_identity(
                root_path, qualification_only_expected_sha256=expected)
            self.assertEqual(
                scope, "QUALIFICATION_ONLY__NOT_FORMAL_MEASUREMENT_ROOT")
            self.assertEqual(observed, expected)
            with self.assertRaisesRegex(
                    RuntimeError, "qualification-only trust-root file identity"):
                clean_verifier._verify_trust_root_file_identity(
                    root_path, qualification_only_expected_sha256="0" * 64)

            value["key_id"] = "TEST_ONLY_goal5802_rtx_measurement_root"
            root_path.write_bytes(
                json.dumps(
                    value, separators=(",", ":"), sort_keys=True
                ).encode("utf-8") + b"\n")
            wrong_scope_sha = hashlib.sha256(
                root_path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(
                    RuntimeError, "qualification-only trust-root key-id"):
                clean_verifier._verify_trust_root_file_identity(
                    root_path,
                    qualification_only_expected_sha256=wrong_scope_sha)

    def test_goal5802_measurement_root_rotation_is_append_only_and_explicit(self) -> None:
        documents = ROOT / "history/internal_docs"
        old_root_path = (
            documents
            / "goal5802_rtx_measurement_test_trust_public_root_v4_20260826.json")
        retirement_path = (
            documents
            / "goal5802_rtx_measurement_test_trust_root_v4_terminal_after_a4500_s0_20260826.json")
        new_root_path = (
            documents
            / "goal5802_rtx_measurement_test_trust_public_root_v5_20260826.json")
        new_receipt_path = (
            documents
            / "goal5802_rtx_measurement_test_trust_key_custody_v5_20260826.json")
        retirement = json.loads(retirement_path.read_text(encoding="utf-8"))
        new_receipt = json.loads(new_receipt_path.read_text(encoding="utf-8"))
        old_root = json.loads(old_root_path.read_text(encoding="utf-8"))
        new_root = json.loads(new_root_path.read_text(encoding="utf-8"))

        old_file_sha = hashlib.sha256(old_root_path.read_bytes()).hexdigest()
        new_file_sha = hashlib.sha256(new_root_path.read_bytes()).hexdigest()
        self.assertEqual(old_file_sha, retirement["public_root_file_sha256"])
        self.assertEqual(old_root["trust_root_sha256"], retirement["trust_root_sha256"])
        self.assertEqual(retirement["maximum_preserved_sequence"], 2)
        self.assertTrue(retirement["owner_local_private_key_copy_exists"])
        self.assertTrue(retirement["retirement_is_administrative_not_cryptographic_erasure"])
        self.assertFalse(retirement["future_signing_authorized"])
        self.assertEqual(
            clean_verifier.RETIRED_TEST_TRUST_ROOT_DISCLOSURE[old_file_sha],
            {"maximum_preserved_sequence": 2,
             "unmaterialized_sequence_range": None})

        self.assertNotEqual(old_file_sha, new_file_sha)
        self.assertNotEqual(old_root["key_id"], new_root["key_id"])
        self.assertEqual(new_file_sha, clean_verifier.CONTROLLING_TRUST_ROOT_FILE_SHA256)
        self.assertEqual(new_receipt["public_root_file_sha256"], new_file_sha)
        self.assertEqual(new_receipt["trust_root_sha256"], new_root["trust_root_sha256"])
        self.assertFalse(
            new_receipt["private_key_committed_or_embedded_at_receipt_snapshot"])
        self.assertFalse(
            new_receipt["diagnostic_keypair_signing_occurred_before_receipt_snapshot"])
        self.assertFalse(
            new_receipt["diagnostic_keypair_signing_invocation_count_exactly_attested"])
        self.assertEqual(
            new_receipt[
                "diagnostic_keypair_signing_invocation_known_minimum_at_receipt_snapshot"],
            0)
        self.assertEqual(
            new_receipt["trust_package_signing_invocation_count_at_receipt_snapshot"],
            0)
        self.assertEqual(
            new_receipt["trust_head_signing_invocation_count_at_receipt_snapshot"],
            0)
        self.assertEqual(
            new_receipt["materialized_trust_sequence_count_at_receipt_snapshot"],
            0)
        self.assertEqual(
            new_receipt["formal_worker_count_at_receipt_snapshot"], 0)
        self.assertEqual(
            new_receipt["registered_performance_timing_count_at_receipt_snapshot"],
            0)
        self.assertTrue(
            new_receipt[
                "owner_provided_modern_rtx_target_observed_at_receipt_snapshot"])
        self.assertTrue(new_receipt["future_state_not_claimed"])
        self.assertTrue(new_receipt["post_use_run_local_receipt_required"])
        self.assertTrue(
            new_receipt[
                "tracked_source_receipt_must_not_be_reinterpreted_as_current_after_pod"])

        retired = (
            ROOT / "history/internal_docs/"
            "goal5802_retired_test_trust_root_a9b199_seq4_20260825")
        retired_root, _ = clean_verifier._read_json(
            retired / "root.json", canonical_lf=True)
        retired_package, retired_package_raw = clean_verifier._read_json(
            retired / "package_seq4.json", canonical_lf=True)
        retired_head, _ = clean_verifier._read_json(
            retired / "head_seq4.json", canonical_lf=True)
        self.assertEqual(
            hashlib.sha256((retired / "root.json").read_bytes()).hexdigest(),
            clean_verifier.RETIRED_UNMATERIALIZED_SEQUENCE_ROOT_SHA256)
        self.assertEqual(retired_package["sequence"], 4)
        self.assertEqual(len(retired_package["authorities"]), 4)
        modulus = int.from_bytes(clean_verifier._strict_b64(
            retired_root["rsa_modulus_base64"], "retired.modulus"), "big")
        package_body = dict(retired_package)
        package_signature = package_body.pop("signature_base64")
        clean_verifier._verify_rsa(
            package_signature,
            clean_verifier.TRUST_PACKAGE_DOMAIN
            + clean_verifier._canonical(package_body),
            modulus=modulus, exponent=retired_root["rsa_exponent"],
            label="retired package")
        self.assertEqual(
            retired_head["current_package_sha256"],
            hashlib.sha256(retired_package_raw).hexdigest())
        head_body = dict(retired_head)
        head_signature = head_body.pop("signature_base64")
        clean_verifier._verify_rsa(
            head_signature,
            clean_verifier.TRUST_HEAD_DOMAIN
            + clean_verifier._canonical(head_body),
            modulus=modulus, exponent=retired_root["rsa_exponent"],
            label="retired head")

    def test_clean_verifier_reconstructs_real_sequence_one_to_two_chain(
            self) -> None:
        trust = (
            ROOT / "history/internal_docs/"
            "goal5801_rtdlexe_lx1_untimed_evidence_20260824/"
            "test_trust_public")
        current, predecessor = clean_verifier._verify_trust(
            trust / "root.json", trust / "head_seq2.json",
            trust / "package_seq1.json", trust / "package_seq2.json")
        self.assertEqual(len(predecessor), 1)
        self.assertEqual(len(current), 2)
        self.assertEqual(
            predecessor[0]["family"], "custom_aabb_bounded_relation_v1")
        self.assertEqual(current[0], predecessor[0])
        with self.assertRaisesRegex(RuntimeError, "sequence 1 envelope"):
            clean_verifier._verify_trust(
                trust / "root.json", trust / "head_seq2.json",
                trust / "package_seq2.json", trust / "package_seq2.json")
        with self.assertRaisesRegex(RuntimeError, "sequence 2 envelope"):
            clean_verifier._verify_trust(
                trust / "root.json", trust / "head_seq3.json",
                trust / "package_seq1.json", trust / "package_seq3.json")

    def test_wheel_declares_runtime_schema_package_data(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[tool.setuptools.package-data]", pyproject)
        self.assertIn('rtdsl = ["schemas/*.json"]', pyproject)

    def test_pinned_virtualenv_bootstrap_needs_no_system_venv_sudo_or_network(
            self) -> None:
        command = clean_runner._virtualenv_command(
            Path("/base/python"), Path("/pinned/virtualenv-20.35.4"),
            Path("/fresh/venv"))
        self.assertEqual(command[1:3], ["-I", "-c"])
        joined = " ".join(command)
        self.assertIn("/pinned/virtualenv-20.35.4", joined)
        self.assertIn("--no-download", joined)
        self.assertIn("--copies", joined)
        self.assertIn("--app-data", joined)
        self.assertIn("/fresh/virtualenv_app_data", joined)
        self.assertNotIn("-m venv", joined)
        self.assertNotIn("sudo", joined)

    def test_virtualenv_bootstrap_rows_use_flat_posix_path_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "virtualenv").mkdir()
            (root / "virtualenv/__main__.py").write_bytes(b"")
            (root / "distlib").mkdir()
            (root / "distlib/member.py").write_bytes(b"package\n")
            (root / "distlib-1.0.dist-info").mkdir()
            (root / "distlib-1.0.dist-info/METADATA").write_bytes(b"metadata\n")
            rows = clean_runner._tree_rows(root)
            paths = [str(row["path"]) for row in rows]
            self.assertEqual(paths, sorted(paths))
            self.assertLess(
                paths.index("distlib-1.0.dist-info/METADATA"),
                paths.index("distlib/member.py"))

    def test_native_custody_round_trip_and_native_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            (source / "Makefile").write_text("build-optix:\n\t@true\n", encoding="utf-8")
            (source / "native.cpp").write_text("int rtdl_optix = 1;\n", encoding="utf-8")
            git = shutil.which("git")
            self.assertIsNotNone(git)
            subprocess.run([str(git), "-C", str(source), "init", "-q"], check=True)
            subprocess.run([str(git), "-C", str(source), "config", "user.email",
                            "goal5801@example.invalid"], check=True)
            subprocess.run([str(git), "-C", str(source), "config", "user.name",
                            "Goal5801 Test"], check=True)
            subprocess.run([str(git), "-C", str(source), "config", "core.autocrlf",
                            "false"], check=True)
            subprocess.run([str(git), "-C", str(source), "add", "Makefile", "native.cpp"],
                           check=True)
            subprocess.run([str(git), "-C", str(source), "commit", "-qm", "fixture"],
                           check=True)
            commit = subprocess.check_output(
                [str(git), "-C", str(source), "rev-parse", "HEAD"],
                text=True).strip()
            build = root / "build"
            build.mkdir()
            dependency = source / "native.cpp"
            depfile = build / "native.d"
            depfile.write_text(
                f"native.o: {dependency.as_posix()}\n", encoding="utf-8")
            native = build / "librtdl_optix.so"
            native.write_bytes(b"synthetic-native")
            command = build / "command.txt"
            command.write_text("nvcc src/native/rtdl_optix.cpp -o librtdl_optix.so\n",
                               encoding="utf-8")
            stdout = build / "stdout.txt"; stdout.write_text("nvcc command\n", encoding="utf-8")
            stderr = build / "stderr.txt"; stderr.write_bytes(b"")
            exit_code = build / "exit_code.txt"; exit_code.write_text("0\n", encoding="ascii")
            environment = build / "environment.json"
            environment.write_bytes((json.dumps(
                {"PATH": "/exact/toolchain/bin"}, separators=(",", ":"),
                sort_keys=True) + "\n").encode("utf-8"))
            origin_inventory = build / "origin_ls_tree.txt"
            origin_inventory.write_bytes(subprocess.check_output([
                str(git), "-C", str(source), "ls-tree", "-rz", "--full-tree",
                commit,
            ]))
            origin_commit_object = build / "origin_commit_object.bin"
            origin_commit_object.write_bytes(subprocess.check_output([
                str(git), "-C", str(source), "cat-file", "commit", commit,
            ]))
            tree = subprocess.check_output(
                [str(git), "-C", str(source), "rev-parse", f"{commit}^{{tree}}"],
                text=True).strip()

            named: dict[str, Path] = {}
            for name in (
                    "nvcc", "make", "host_cxx", "git", "cuda", "nvrtc", "geos_c",
                    "nvcc_version", "make_version", "host_cxx_version",
                    "git_version", "uname", "native_ldd"):
                path = build / name
                path.write_bytes((name + "\n").encode())
                named[name] = path
            output = root / "custody"
            command_line = [
                sys.executable, str(CAPTURE), "--output", str(output),
                "--source-root", str(source),
                "--source-commit", commit,
                "--origin-commit", commit,
                "--origin-tree", tree,
                "--origin-commit-object", str(origin_commit_object),
                "--origin-inventory", str(origin_inventory),
                "--native", str(native), "--build-cwd", str(build),
                "--build-source-root", str(source),
                "--build-command", str(command), "--build-stdout", str(stdout),
                "--build-stderr", str(stderr), "--build-exit-code", str(exit_code),
                "--dependency-file", str(depfile),
                "--build-environment", str(environment),
            ]
            named["git"] = Path(str(git))
            for name in ("nvcc", "make", "host_cxx", "git"):
                command_line.extend(("--tool", f"{name}={named[name]}"))
            for name in ("cuda", "nvrtc", "geos_c"):
                command_line.extend(("--link-input", f"{name}={named[name]}"))
            for name in ("nvcc_version", "make_version", "host_cxx_version", "git_version",
                         "uname", "native_ldd"):
                command_line.extend(("--tool-receipt", f"{name}={named[name]}"))
            completed = subprocess.run(
                command_line, check=False, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = verifier.verify(output)
            self.assertEqual(
                result["status"], "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION")
            self.assertEqual(result["source_file_count"], 2)
            self.assertEqual(result["dependency_file_count"], 1)
            self.assertEqual(result["toolchain_payload_count"], 13)
            self.assertFalse(result["hermetic_native_rebuild_claimed"])
            custody_verifier_path = (
                ROOT / "scripts/goal5801_a3_verify_native_custody.py")
            custody_binding = {
                "native_custody_verifier_status": result["status"],
                "native_custody_verifier_sha256": hashlib.sha256(
                    custody_verifier_path.read_bytes()).hexdigest(),
                "native_custody_manifest_sha256": hashlib.sha256(
                    (output / "manifest.json").read_bytes()).hexdigest(),
                "native_custody_custody_sha256": hashlib.sha256(
                    (output / "custody.json").read_bytes()).hexdigest(),
                "native_custody_source_file_count": result["source_file_count"],
                "native_custody_dependency_file_count": result[
                    "dependency_file_count"],
                "native_custody_toolchain_payload_count": result[
                    "toolchain_payload_count"],
                "native_custody_source_commit": result["source_commit"],
                "native_custody_source_tree": result["source_tree"],
                "source_commit": result["origin_commit"],
                "source_tree": result["origin_tree"],
                "native_custody_hermetic_native_rebuild_claimed": False,
                "native_sha256": result["native_sha256"],
            }
            projected = freeze_verifier.verify_native_custody_projection(
                custody_binding, output, custody_verifier_path)
            self.assertEqual(projected["source_commit"], commit)
            forged_binding = dict(custody_binding)
            forged_binding["native_custody_source_commit"] = "0" * 40
            with self.assertRaisesRegex(
                    RuntimeError,
                    "product binding/native-custody projection differs"):
                freeze_verifier.verify_native_custody_projection(
                    forged_binding, output, custody_verifier_path)

            coherent_commit_forgery = root / "custody_coherent_commit_forgery"
            shutil.copytree(output, coherent_commit_forgery)
            source_manifest_path = (
                coherent_commit_forgery / "source/manifest.json")
            source_manifest = json.loads(
                source_manifest_path.read_text(encoding="utf-8"))
            source_manifest["source_commit"] = "0" * 40
            source_manifest_raw = (json.dumps(
                source_manifest, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8")
            source_manifest_path.write_bytes(source_manifest_raw)
            custody_path = coherent_commit_forgery / "custody.json"
            custody_value = json.loads(custody_path.read_text(encoding="utf-8"))
            custody_value["source_commit"] = "0" * 40
            custody_value["source_manifest_sha256"] = hashlib.sha256(
                source_manifest_raw).hexdigest()
            custody_raw = (json.dumps(
                custody_value, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8")
            custody_path.write_bytes(custody_raw)
            outer_path = coherent_commit_forgery / "manifest.json"
            outer = json.loads(outer_path.read_text(encoding="utf-8"))
            for relative, payload in (
                    ("source/manifest.json", source_manifest_raw),
                    ("custody.json", custody_raw)):
                row = next(item for item in outer["files"]
                           if item["path"] == relative)
                row["bytes"] = len(payload)
                row["sha256"] = hashlib.sha256(payload).hexdigest()
            outer["total_payload_bytes"] = sum(
                int(item["bytes"]) for item in outer["files"])
            outer_path.write_bytes((json.dumps(
                outer, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8"))
            # The generic verifier proves the raw origin, but deliberately
            # treats source labels as claims.  Goal5802 requires equality.
            forged_observed = verifier.verify(coherent_commit_forgery)
            self.assertEqual(forged_observed["source_commit"], "0" * 40)
            self.assertEqual(forged_observed["origin_commit"], commit)
            forged_binding = dict(custody_binding)
            forged_binding["source_commit"] = "0" * 40
            forged_binding["native_custody_source_commit"] = "0" * 40
            forged_binding["native_custody_manifest_sha256"] = hashlib.sha256(
                outer_path.read_bytes()).hexdigest()
            forged_binding["native_custody_custody_sha256"] = hashlib.sha256(
                custody_path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(
                    RuntimeError, "raw-proven origin identity"):
                freeze_verifier.verify_native_custody_projection(
                    forged_binding, coherent_commit_forgery,
                    custody_verifier_path)

            for link_kind in ("file", "directory"):
                hostile_root = root / f"custody_{link_kind}_symlink"
                shutil.copytree(output, hostile_root)
                external = root / f"external_{link_kind}"
                if link_kind == "file":
                    external.write_bytes(b"external-native")
                    target = hostile_root / "native/librtdl_optix.so"
                    target.unlink()
                    try:
                        target.symlink_to(external)
                    except OSError:
                        shutil.rmtree(hostile_root)
                        source_text = (ROOT / "scripts/goal5801_a3_verify_native_custody.py").read_text(
                            encoding="utf-8")
                        self.assertIn(
                            "native-custody evidence contains a symlink",
                            source_text)
                        continue
                else:
                    external.mkdir()
                    (external / "command.txt").write_bytes(b"external-command")
                    target = hostile_root / "build"
                    shutil.rmtree(target)
                    try:
                        target.symlink_to(external, target_is_directory=True)
                    except OSError:
                        shutil.rmtree(hostile_root)
                        source_text = (ROOT / "scripts/goal5801_a3_verify_native_custody.py").read_text(
                            encoding="utf-8")
                        self.assertIn(
                            "native-custody evidence contains a symlink",
                            source_text)
                        continue
                with self.subTest(link_kind=link_kind), self.assertRaisesRegex(
                        RuntimeError, "native-custody evidence contains a symlink"):
                    verifier.verify(hostile_root)

            root_link = root / "custody_root_symlink"
            try:
                root_link.symlink_to(output, target_is_directory=True)
            except OSError:
                source_text = (ROOT / "scripts/goal5801_a3_verify_native_custody.py").read_text(
                    encoding="utf-8")
                self.assertIn("root must not be a symlink", source_text)
            else:
                with self.assertRaisesRegex(RuntimeError, "root must not be a symlink"):
                    verifier.verify(root_link)

            def hostile_capture(
                    name: str, option: str, value: str) -> subprocess.CompletedProcess[str]:
                hostile = list(command_line)
                hostile[hostile.index("--output") + 1] = str(root / name)
                hostile[hostile.index(option) + 1] = value
                return subprocess.run(
                    hostile, check=False, capture_output=True, text=True)

            changed_commit = hostile_capture(
                "changed_commit", "--origin-commit", "0" * 40)
            self.assertNotEqual(changed_commit.returncode, 0)
            self.assertIn("does not hash to origin commit", changed_commit.stderr)
            changed_tree = hostile_capture(
                "changed_tree", "--origin-tree", "1" * 40)
            self.assertNotEqual(changed_tree.returncode, 0)
            self.assertIn("does not bind the declared origin tree", changed_tree.stderr)
            truncated_inventory = build / "origin_ls_tree_truncated.bin"
            truncated_inventory.write_bytes(origin_inventory.read_bytes()[:-1])
            changed_inventory = hostile_capture(
                "changed_inventory", "--origin-inventory",
                str(truncated_inventory))
            self.assertNotEqual(changed_inventory.returncode, 0)
            self.assertIn("NUL-terminated", changed_inventory.stderr)
            bad_inventory = build / "origin_ls_tree_changed.txt"
            inventory_bytes = origin_inventory.read_bytes()
            object_start = inventory_bytes.index(b" blob ") + len(b" blob ")
            changed = bytearray(inventory_bytes)
            changed[object_start] = ord("0") \
                if changed[object_start] != ord("0") else ord("1")
            bad_inventory.write_bytes(changed)
            changed_blob = hostile_capture(
                "changed_blob", "--origin-inventory",
                str(bad_inventory))
            self.assertNotEqual(changed_blob.returncode, 0)
            self.assertIn("does not reconstruct origin tree", changed_blob.stderr)

            forged_tree = root / "forged_source_tree"
            shutil.copytree(output, forged_tree)
            source_manifest_path = forged_tree / "source/manifest.json"
            source_manifest = json.loads(
                source_manifest_path.read_text(encoding="utf-8"))
            source_manifest["source_tree"] = "0" * 40
            source_manifest_raw = (json.dumps(
                source_manifest, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8")
            source_manifest_path.write_bytes(source_manifest_raw)
            custody_path = forged_tree / "custody.json"
            custody = json.loads(custody_path.read_text(encoding="utf-8"))
            custody["source_tree"] = "0" * 40
            custody["source_manifest_sha256"] = hashlib.sha256(
                source_manifest_raw).hexdigest()
            custody_raw = (json.dumps(
                custody, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8")
            custody_path.write_bytes(custody_raw)
            forged_outer_path = forged_tree / "manifest.json"
            forged_outer = json.loads(
                forged_outer_path.read_text(encoding="utf-8"))
            for relative, payload in (
                    ("source/manifest.json", source_manifest_raw),
                    ("custody.json", custody_raw)):
                row = next(item for item in forged_outer["files"]
                           if item["path"] == relative)
                row["bytes"] = len(payload)
                row["sha256"] = hashlib.sha256(payload).hexdigest()
            forged_outer["total_payload_bytes"] = sum(
                int(item["bytes"]) for item in forged_outer["files"])
            forged_outer_path.write_bytes((json.dumps(
                forged_outer, separators=(",", ":"), sort_keys=True)
                + "\n").encode("utf-8"))
            with self.assertRaisesRegex(
                    RuntimeError,
                    "source inventory does not reconstruct declared source tree"):
                verifier.verify(forged_tree)

            original_native = (output / "native/librtdl_optix.so").read_bytes()
            (output / "native/librtdl_optix.so").write_bytes(b"changed")
            with self.assertRaisesRegex(RuntimeError, "outer manifest: payload mismatch"):
                verifier.verify(output)
            (output / "native/librtdl_optix.so").write_bytes(original_native)

            origin_object = output / "source/origin_commit_object.bin"
            origin_object.write_bytes(origin_object.read_bytes() + b"changed")
            manifest_path = output / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            row = next(row for row in manifest["files"]
                       if row["path"] == "source/origin_commit_object.bin")
            row["bytes"] = origin_object.stat().st_size
            row["sha256"] = hashlib.sha256(origin_object.read_bytes()).hexdigest()
            manifest["total_payload_bytes"] = sum(
                int(candidate["bytes"]) for candidate in manifest["files"])
            manifest_path.write_bytes((json.dumps(
                manifest, separators=(",", ":"), sort_keys=True) + "\n"
            ).encode("utf-8"))
            with self.assertRaisesRegex(RuntimeError, "origin commit object"):
                verifier.verify(output)

    def test_latest_deployment_aliases_are_top_level_and_unambiguous(self) -> None:
        preserved = {
            name: module for name, module in sys.modules.items()
            if name == "rtdsl" or name.startswith("rtdsl.")
        }
        for name in preserved:
            del sys.modules[name]
        try:
            with patch.object(sys, "path", [str(ROOT / "src"), *sys.path]):
                import rtdsl
                from rtdsl import v4
                from rtdsl.v4_rtdlexe import (
                    BoundedRelationBatch,
                    BoundedRelationStaticInput,
                    TriangleReductionBatch,
                    TriangleReductionStaticInput,
                )

                self.assertIs(rtdsl.RTDLExecutableBoundedRelationBatch,
                              BoundedRelationBatch)
                self.assertIs(rtdsl.RTDLExecutableBoundedRelationStaticInput,
                              BoundedRelationStaticInput)
                self.assertIs(rtdsl.RTDLExecutableTriangleReductionBatch,
                              TriangleReductionBatch)
                self.assertIs(rtdsl.RTDLExecutableTriangleReductionStaticInput,
                              TriangleReductionStaticInput)
                self.assertIsNot(rtdsl.RTDLExecutableBoundedRelationBatch,
                                 v4.BoundedRelationBatch)
                self.assertIsNot(rtdsl.RTDLExecutableTriangleReductionBatch,
                                 v4.TriangleReductionBatch)
        finally:
            for name in tuple(sys.modules):
                if name == "rtdsl" or name.startswith("rtdsl."):
                    del sys.modules[name]
            sys.modules.update(preserved)

    def test_clean_install_probe_has_exact_claim_and_import_boundary(self) -> None:
        source = PROBE.read_text(encoding="utf-8")
        runner = (ROOT / "scripts/goal5801_a3_run_clean_install.py").read_text(
            encoding="utf-8")
        self.assertIn("registered_performance_timing_count\": 0", source)
        self.assertIn("RTDLExecutableBoundedRelationBatch", source)
        self.assertIn("RTDLExecutableTriangleReductionBatch", source)
        self.assertIn("expected_reduced_u64=7", source)
        self.assertNotIn("from rtdsl.v4 import", source)
        self.assertNotIn("import rtdsl.v4", source)
        self.assertNotIn("ctypes.CDLL(str(native))", source)
        self.assertIn('getattr(prepared, "_owner", None)', source)
        self.assertIn(
            "EVIDENCE_ONLY_PRIVATE_PREPARED_OWNER_LIBRARY_INTROSPECTION",
            source)
        self.assertIn(
            "same_sha_process_cache_is_bounded_to_one_loader_image",
            source)
        self.assertIn("fast_path_operation_kat", source)
        self.assertIn("NATIVE_MAPPING_LIFETIME_ROUNDS = 3", source)
        self.assertIn('Path("/proc/self/maps")', source)
        self.assertIn("native_mapping_lifetime_kat", source)
        self.assertIn("source tree is present on clean-install sys.path", source)
        self.assertIn("--no-download", runner)
        self.assertIn("virtualenv_bootstrap_files", runner)
        self.assertNotIn('[base, "-I", "-m", "venv"', runner)
        self.assertNotIn("sudo", runner)
        self.assertEqual(clean_verifier.CONTROLLING_TRUST_SEQUENCE, 2)
        self.assertEqual(clean_verifier.RETAINED_PREDECESSOR_DEPLOYMENTS, {})
        self.assertEqual(
            clean_verifier.RETIRED_TEST_TRUST_ROOT_DISCLOSURE[
                clean_verifier.RETIRED_UNMATERIALIZED_SEQUENCE_ROOT_SHA256],
            {
                "maximum_preserved_sequence": 4,
                "unmaterialized_sequence_range": [5, 16],
            })
        verifier_source = (
            ROOT / "scripts/goal5801_a3_verify_clean_install.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "expected_sequence=CONTROLLING_TRUST_SEQUENCE", verifier_source)
        self.assertIn(
            "sequence-1 predecessor is not the exact current relation authority",
            verifier_source)

    def test_clean_install_result_binds_counters_to_one_cached_dso(
            self) -> None:
        native_sha = "a" * 64
        native_path = "/old/packet/inputs/native/librtdl_optix.so"
        boundary = {
            "application_lifecycle_calls_use_public_api_only": True,
            "cross_owner_dso_cache_or_reuse_claimed": True,
            "evidence_method": (
                "EVIDENCE_ONLY_PRIVATE_PREPARED_OWNER_LIBRARY_INTROSPECTION"),
            "product_api_expanded_for_evidence": False,
            "relation_and_triangle_share_one_dso_handle": True,
            "relation_and_triangle_share_one_memfd_descriptor": True,
            "relation_and_triangle_share_one_loader_alias": True,
            "relation_and_triangle_same_native_sha256": True,
            "relation_and_triangle_use_distinct_native_leases": True,
            "same_sha_process_cache_is_bounded_to_one_loader_image": True,
        }

        def dso(lease_id: int) -> dict[str, object]:
            return {
                "compiler_attempt_count_after": 0,
                "compiler_attempt_count_before": 0,
                "ctypes_handle": 1001,
                "lease_abandon_finalizer_alive_after_execute_before_close": True,
                "lease_abandon_finalizer_alive_before_execute": True,
                "loaded_library_path": native_path,
                "loaded_library_sha256": native_sha,
                "native_image_bytes": 123,
                "native_cache_entry_identity": f"1:{native_sha}",
                "native_cache_lease_id": lease_id,
                "native_cache_active_lease_count_before_execute": 2,
                "native_cache_active_lease_count_after_execute": 2,
                "native_cache_acquisition_count_before_execute": 2,
                "native_cache_acquisition_count_after_execute": 2,
                "native_image_fd": 11,
                "native_image_seals_after": 15,
                "native_image_seals_before": 15,
                "native_loader_alias": (
                    f"/tmp/rtdl-native-1-shared/image-{native_sha}.so"),
                "native_loader_alias_parent_removed_before_execute": True,
                "native_loader_alias_removed_before_execute": True,
                "required_native_image_seals": 15,
                "same_owner_library_object_after_execute": True,
                "sealed_image_sha256_after": native_sha,
                "sealed_image_sha256_before": native_sha,
            }

        result = {
            "prepared_native_dso_evidence_boundary": boundary,
            "relation": {"actual_loaded_native_dso": dso(1)},
            "triangle": {"actual_loaded_native_dso": dso(2)},
        }
        clean_verifier._verify_actual_prepared_native_dsos(
            result, native_sha256=native_sha, native_bytes=123,
            expected_loaded_path=native_path)

        nonzero = json.loads(json.dumps(result))
        nonzero["relation"]["actual_loaded_native_dso"][
            "compiler_attempt_count_before"] = 4
        nonzero["relation"]["actual_loaded_native_dso"][
            "compiler_attempt_count_after"] = 4
        with self.assertRaisesRegex(RuntimeError, "relation actual executing DSO"):
            clean_verifier._verify_actual_prepared_native_dsos(
                nonzero, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        bool_alias = json.loads(json.dumps(result))
        bool_alias["relation"]["actual_loaded_native_dso"][
            "compiler_attempt_count_before"] = False
        with self.assertRaisesRegex(RuntimeError, "relation actual executing DSO"):
            clean_verifier._verify_actual_prepared_native_dsos(
                bool_alias, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        boundary_alias = json.loads(json.dumps(result))
        boundary_alias["prepared_native_dso_evidence_boundary"][
            "application_lifecycle_calls_use_public_api_only"] = 1
        with self.assertRaisesRegex(RuntimeError, "evidence boundary"):
            clean_verifier._verify_actual_prepared_native_dsos(
                boundary_alias, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        split = json.loads(json.dumps(result))
        split["triangle"]["actual_loaded_native_dso"]["ctypes_handle"] = 1002
        with self.assertRaisesRegex(RuntimeError, "do not share one image"):
            clean_verifier._verify_actual_prepared_native_dsos(
                split, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        substituted = json.loads(json.dumps(result))
        substituted["triangle"]["actual_loaded_native_dso"][
            "sealed_image_sha256_after"] = "b" * 64
        with self.assertRaisesRegex(RuntimeError, "triangle actual executing DSO"):
            clean_verifier._verify_actual_prepared_native_dsos(
                substituted, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

    def test_clean_result_requires_bounded_repeated_native_mapping_lifetime(
            self) -> None:
        native_sha = "a" * 64
        native_path = "/old/packet/inputs/native/librtdl_optix.so"
        boundary = {
            "application_lifecycle_calls_use_public_api_only": True,
            "cross_owner_dso_cache_or_reuse_claimed": True,
            "evidence_method": (
                "EVIDENCE_ONLY_PRIVATE_PREPARED_OWNER_LIBRARY_INTROSPECTION"),
            "product_api_expanded_for_evidence": False,
            "relation_and_triangle_share_one_dso_handle": True,
            "relation_and_triangle_share_one_memfd_descriptor": True,
            "relation_and_triangle_share_one_loader_alias": True,
            "relation_and_triangle_same_native_sha256": True,
            "relation_and_triangle_use_distinct_native_leases": True,
            "same_sha_process_cache_is_bounded_to_one_loader_image": True,
        }

        def dso(lease_id: int, active_before: int, active_after: int) \
                -> dict[str, object]:
            return {
                "compiler_attempt_count_after": 0,
                "compiler_attempt_count_before": 0,
                "ctypes_handle": 1001,
                "lease_abandon_finalizer_alive_after_execute_before_close": True,
                "lease_abandon_finalizer_alive_before_execute": True,
                "loaded_library_path": native_path,
                "loaded_library_sha256": native_sha,
                "native_image_bytes": 123,
                "native_cache_entry_identity": f"1:{native_sha}",
                "native_cache_lease_id": lease_id,
                "native_cache_active_lease_count_before_execute": active_before,
                "native_cache_active_lease_count_after_execute": active_after,
                "native_cache_acquisition_count_before_execute": lease_id,
                "native_cache_acquisition_count_after_execute": lease_id,
                "native_image_fd": 11,
                "native_image_seals_after": 15,
                "native_image_seals_before": 15,
                "native_loader_alias": (
                    f"/tmp/rtdl-native-1-shared/image-{native_sha}.so"),
                "native_loader_alias_parent_removed_before_execute": True,
                "native_loader_alias_removed_before_execute": True,
                "required_native_image_seals": 15,
                "same_owner_library_object_after_execute": True,
                "sealed_image_sha256_after": native_sha,
                "sealed_image_sha256_before": native_sha,
            }

        closed = {
            "cache_image_fd_open_after_close": True,
            "cache_loader_handle_live_after_close": True,
            "lease_abandon_finalizer_alive_after_close": False,
            "lease_image_fd_value_after_close": -1,
            "lease_library_handle_after_close": 0,
            "lease_release_phase_after_close": "COMPLETE",
            "lease_released_after_close": True,
            "owner_library_released_after_close": True,
            "owner_release_complete_after_close": True,
            "prepared_closed_after_close": True,
        }
        rounds = []
        for index in range(3):
            relation_closed = dict(closed)
            relation_closed["cache_active_lease_count_after_close"] = 1
            triangle_closed = dict(closed)
            triangle_closed["cache_active_lease_count_after_close"] = 0
            rounds.append({
                "after_close_map_count": 5,
                "after_idempotent_close_map_count": 5,
                "before_prepare_map_count": 5,
                "live_map_count": 5,
                "relation_closed_state": relation_closed,
                "relation_live_dso": dso(index * 2 + 1, 1, 2),
                "relation_output": [[10, 100]],
                "round_index": index,
                "triangle_closed_state": triangle_closed,
                "triangle_live_dso": dso(index * 2 + 2, 2, 1),
                "triangle_output": 7,
            })
        result = {
            "prepared_native_dso_evidence_boundary": boundary,
            "native_mapping_lifetime_kat": {
                "fork_child_prepare_code": "RX047_NATIVE_CACHE_FORK_POISONED",
                "map_identity_marker": (
                    f"/memfd:rtdl-native-{native_sha[:16]} (deleted)"),
                "maximum_live_map_count": 32,
                "prepared_owner_count_per_round": 2,
                "round_count": 3,
                "rounds": rounds,
                "schema": "rtdl.goal5801.native_mapping_lifetime_kat.v2",
                "warm_process_cache_map_count": 5,
            },
        }
        clean_verifier._verify_native_mapping_lifetime_kat(
            result, native_sha256=native_sha, native_bytes=123,
            expected_loaded_path=native_path)

        leaked = json.loads(json.dumps(result))
        leaked["native_mapping_lifetime_kat"]["rounds"][1][
            "after_close_map_count"] = 6
        with self.assertRaisesRegex(RuntimeError, "lifetime KAT round 1"):
            clean_verifier._verify_native_mapping_lifetime_kat(
                leaked, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        bool_alias = json.loads(json.dumps(result))
        bool_alias["native_mapping_lifetime_kat"]["rounds"][0][
            "before_prepare_map_count"] = False
        with self.assertRaisesRegex(RuntimeError, "lifetime KAT round 0"):
            clean_verifier._verify_native_mapping_lifetime_kat(
                bool_alias, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

        not_unloaded = json.loads(json.dumps(result))
        not_unloaded["native_mapping_lifetime_kat"]["rounds"][2][
            "triangle_closed_state"]["cache_loader_handle_live_after_close"] = False
        with self.assertRaisesRegex(RuntimeError, "lifetime KAT round 2"):
            clean_verifier._verify_native_mapping_lifetime_kat(
                not_unloaded, native_sha256=native_sha, native_bytes=123,
                expected_loaded_path=native_path)

    def test_clean_result_requires_exact_fast_operation_receipts(self) -> None:
        def family(*, relation: bool) -> dict[str, object]:
            control = 16 if relation else 4
            output = 32_768 if relation else 8
            calls = [2, 0, 2, 2] if relation else [8, 0, 8, 8]
            builds = [1, 0, 1, 1] if relation else [0, 0, 0, 0]
            receipts = []
            for index in range(4):
                row = {
                    "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
                    "optix_launch_count": 2 if relation else 1,
                    "host_blocking_boundary_count": 2 if index < 3 else 1,
                    "control_d2h_bytes": control,
                    "output_d2h_bytes": output if index < 3 else 0,
                    "status_before_output": True,
                    "output_d2h_after_status_failure": 0,
                    "role_counters_materialized": False,
                    "prepared_input_reused": index == 1,
                    "dynamic_device_upload_call_count": calls[index],
                    "dynamic_device_upload_bytes": 0 if index == 1 else 52,
                    "dynamic_accel_build_count": builds[index],
                    "dynamic_explicit_sync_count": 0,
                    "dynamic_blocking_upload_call_count": 0,
                    "dynamic_input_generation": [1, 1, 2, 3][index],
                    "callback_status_kernel_launch_count": 5 if relation else 3,
                    "checked_product_kernel_launch_count": 0 if relation else 2,
                    "compact_control_finalizer_kernel_launch_count": 1,
                    "total_auxiliary_cuda_kernel_launch_count": 7 if relation else 6,
                    "execution_parameter_h2d_bytes": 224 if relation else 200,
                    "execution_parameter_h2d_copy_call_count": 2 if relation else 1,
                    "stream_ordered_memset_call_count": 9 if relation else 4,
                    "status_d2h_copy_call_count": 1,
                    "output_d2h_copy_call_count": 1 if index < 3 else 0,
                    "semantic_compaction_launch_count": 1 if relation else 0,
                    "semantic_compaction_key_capacity": 8192 if relation else 0,
                    "semantic_compaction_scratch_bytes": 98_312 if relation else 0,
                }
                receipts.append(row)
            value = {
                "failure_code": "RX035_DEVICE_STATUS_INVALID",
                "receipt_sha256": [hashlib.sha256(json.dumps(
                    row, allow_nan=False, separators=(",", ":"),
                    sort_keys=True).encode()).hexdigest() for row in receipts],
                "receipts": receipts,
                "success_control_d2h_bytes": control,
                "success_output_d2h_bytes": output,
                "success_total_d2h_bytes": control + output,
            }
            if relation:
                value.update({"output_row_count": 4096,
                              "raw_event_count": 8192,
                              "unique_event_count": 4096})
                def semantic_receipt(*, reused: bool, success: bool,
                                     generation: int, upload_bytes: int):
                    return {
                        "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
                        "optix_launch_count": 2,
                        "host_blocking_boundary_count": 2 if success else 1,
                        "control_d2h_bytes": 16,
                        "output_d2h_bytes": 8 if success else 0,
                        "status_before_output": True,
                        "output_d2h_after_status_failure": 0,
                        "role_counters_materialized": False,
                        "prepared_input_reused": reused,
                        "dynamic_device_upload_call_count": 0 if reused else 2,
                        "dynamic_device_upload_bytes": upload_bytes,
                        "dynamic_accel_build_count": 0 if reused else 1,
                        "dynamic_explicit_sync_count": 0,
                        "dynamic_blocking_upload_call_count": 0,
                        "dynamic_input_generation": generation,
                        "semantic_compaction_launch_count": 1,
                        "semantic_compaction_key_capacity": 8192,
                        "semantic_compaction_scratch_bytes": 98_312,
                        "callback_status_kernel_launch_count": 5,
                        "checked_product_kernel_launch_count": 0,
                        "compact_control_finalizer_kernel_launch_count": 1,
                        "total_auxiliary_cuda_kernel_launch_count": 7,
                        "execution_parameter_h2d_bytes": 224,
                        "execution_parameter_h2d_copy_call_count": 2,
                        "stream_ordered_memset_call_count": 9,
                        "status_d2h_copy_call_count": 1,
                        "output_d2h_copy_call_count": 1 if success else 0,
                    }
                max_u32 = (1 << 32) - 1
                value["semantic_compaction_hostile"] = {
                    "k_plus_one_compact_control": {
                        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
                        "raw_event_count": 4097,
                        "unique_event_count": 4097,
                        "overflowed": 1,
                        "status": 0xffff5102,
                        "semantic_capacity": 4096,
                        "control_d2h_bytes": 16,
                    },
                    "k_plus_one_failure_code": "RX035_DEVICE_STATUS_INVALID",
                    "k_plus_one_receipt": semantic_receipt(
                        reused=False, success=False, generation=2,
                        upload_bytes=52 * 4097),
                    "max_u64_key_output": [[max_u32, max_u32]],
                    "max_u64_key_receipts": [
                        semantic_receipt(
                            reused=False, success=True, generation=1,
                            upload_bytes=52),
                        semantic_receipt(
                            reused=True, success=True, generation=1,
                            upload_bytes=0),
                    ],
                    "raw_capacity": 8192,
                    "raw_count_below_raw_capacity": True,
                    "registered_performance_timing_count": 0,
                    "same_input_reuse_clears_compaction_scratch": True,
                }
            return value

        result = {"fast_path_operation_kat": {
            "registered_performance_timing_count": 0,
            "relation": family(relation=True),
            "schema": "rtdl.goal5801.fast_path_operation_kat.v1",
            "triangle": family(relation=False),
        }}
        clean_verifier._verify_fast_path_operation_kat(result)
        asymmetric = json.loads(json.dumps(result))
        asymmetric["fast_path_operation_kat"]["relation"]["receipts"][0][
            "dynamic_blocking_upload_call_count"] = 1
        with self.assertRaisesRegex(RuntimeError, "relation\[0\] facts"):
            clean_verifier._verify_fast_path_operation_kat(asymmetric)
        hidden_output = json.loads(json.dumps(result))
        hidden_output["fast_path_operation_kat"]["triangle"]["receipts"][3][
            "output_d2h_bytes"] = 8
        with self.assertRaisesRegex(RuntimeError, "triangle\[3\] facts"):
            clean_verifier._verify_fast_path_operation_kat(hidden_output)

    @staticmethod
    def _write_valid_wheel(path: Path, source_root: Path, *, extra=None) -> None:
        package = {"__init__.py": b"VALUE = 1\n"}
        source_root.mkdir(parents=True)
        (source_root / "__init__.py").write_bytes(package["__init__.py"])
        dist = "rtdl_source_tree-4.0.0rc1.dist-info"
        members = {
            "rtdsl/__init__.py": package["__init__.py"],
            f"{dist}/METADATA": (
                b"Metadata-Version: 2.1\nName: rtdl-source-tree\n"
                b"Version: 4.0.0rc1\nRequires-Python: >=3.10\n"
                b"Requires-Dist: numpy>=1.26\n\n"),
            f"{dist}/WHEEL": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
            f"{dist}/top_level.txt": b"rtdsl\n",
        }
        if extra:
            members.update(extra)
        record = []
        for name, payload in members.items():
            digest = hashlib.sha256(payload).digest()
            import base64
            encoded = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            record.append([name, f"sha256={encoded}", str(len(payload))])
        record_name = f"{dist}/RECORD"
        record.append([record_name, "", ""])
        import csv, io
        stream = io.StringIO(newline="")
        csv.writer(stream, lineterminator="\n").writerows(record)
        members[record_name] = stream.getvalue().encode()
        with zipfile.ZipFile(path, "w") as archive:
            for name, payload in members.items():
                archive.writestr(name, payload)

    def test_clean_install_wheel_record_and_source_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheel = root / "candidate.whl"
            source = root / "source"
            self._write_valid_wheel(wheel, source)
            clean_runner._validate_wheel(wheel, source)
            count, tree = clean_verifier._verify_wheel(wheel, source)
            self.assertEqual(count, 1)
            self.assertRegex(tree, r"^[0-9a-f]{64}$")
            (source / "__init__.py").write_bytes(b"VALUE = 2\n")
            with self.assertRaisesRegex(RuntimeError, "differs from frozen source"):
                clean_verifier._verify_wheel(wheel, source)

    def test_clean_install_wheel_rejects_pth_even_with_coherent_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheel = root / "candidate.whl"
            source = root / "source"
            self._write_valid_wheel(wheel, source, extra={"escape.pth": b"/tmp\n"})
            with self.assertRaisesRegex(RuntimeError, "outside boundary"):
                clean_verifier._verify_wheel(wheel, source)

    def test_clean_install_coherent_candidate_reseal_cannot_bypass_trust(self) -> None:
        original = {
            "deployment_id": "relation-v1", "family": "relation",
            "task_semantics_sha256": "1" * 64,
            "authority_sha256": "2" * 64, "artifact_sha256": "3" * 64,
            "executable_identity_sha256": "4" * 64,
            "target_sha256": "5" * 64, "native_library_sha256": "6" * 64,
            "compute_capability": [6, 1],
        }
        clean_verifier._verify_trusted_candidate_entries(
            {"relation": original}, [dict(original)])
        retired = {
            **original,
            "deployment_id": "retired-relation-v0",
            "native_library_sha256": "9" * 64,
        }
        clean_verifier._verify_trusted_candidate_entries(
            {"relation": original}, [dict(original), retired],
            retained_predecessors={"retired-relation-v0": "9" * 64})
        with self.assertRaisesRegex(RuntimeError, "retained/current"):
            clean_verifier._verify_trusted_candidate_entries(
                {"relation": original}, [dict(original), retired])
        wrong_retired_native = dict(retired)
        wrong_retired_native["native_library_sha256"] = "8" * 64
        with self.assertRaisesRegex(RuntimeError, "predecessor native"):
            clean_verifier._verify_trusted_candidate_entries(
                {"relation": original}, [dict(original), wrong_retired_native],
                retained_predecessors={"retired-relation-v0": "9" * 64})
        coherent_reseal = dict(original)
        coherent_reseal["artifact_sha256"] = "7" * 64
        coherent_reseal["authority_sha256"] = "8" * 64
        with self.assertRaisesRegex(RuntimeError, "trust slot differs"):
            clean_verifier._verify_trusted_candidate_entries(
                {"relation": coherent_reseal}, [dict(original)])

    def test_clean_install_copy_rejects_supplied_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"; target.write_bytes(b"x")
            link = root / "link"
            try:
                link.symlink_to(target)
            except OSError as error:
                # Windows CI may not grant symlink creation.  Still exercise
                # the pre-resolve rejection branch rather than silently skip
                # the security property.
                with patch.object(Path, "is_symlink", return_value=True), \
                        self.assertRaisesRegex(
                            RuntimeError, "must not be a symlink"):
                    clean_runner._copy_input(
                        "hostile", target, root / "copy", root, [])
                self.assertIsInstance(error, OSError)
                return
            packet = root / "packet"; packet.mkdir()
            with self.assertRaisesRegex(RuntimeError, "must not be a symlink"):
                clean_runner._copy_input(
                    "hostile", link, packet / "copy", packet, [])

    def test_clean_install_verifier_rejects_parent_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            packet = root / "packet"; packet.mkdir()
            external = root / "external"; external.mkdir()
            (external / "payload").write_bytes(b"x")
            link = packet / "linked"
            try:
                link.symlink_to(external, target_is_directory=True)
            except OSError:
                source = (ROOT / "scripts/goal5801_a3_verify_clean_install.py").read_text(
                    encoding="utf-8")
                self.assertIn("symlink component is forbidden", source)
                self.assertIn("evidence contains a symlink", source)
                return
            with self.assertRaisesRegex(RuntimeError, "symlink component is forbidden"):
                clean_verifier._safe_path(packet, "linked/payload", "hostile")

    def test_clean_install_verifier_only_excludes_top_level_venv(self) -> None:
        verifier = (ROOT / "scripts/goal5801_a3_verify_clean_install.py").read_text(
            encoding="utf-8")
        runner = (ROOT / "scripts/goal5801_a3_run_clean_install.py").read_text(
            encoding="utf-8")
        exact_guard = 'path.relative_to(root).parts[:1] == ("venv",)'
        exact_filter = 'path.relative_to(root).parts[:1] != ("venv",)'
        self.assertIn(exact_guard, verifier)
        self.assertIn(exact_filter, verifier)
        self.assertIn(
            'path.relative_to(output).parts[:1] != ("venv",)', runner)
        self.assertNotIn('"venv" not in path.relative_to(root).parts', verifier)
        self.assertNotIn('"venv" not in path.relative_to(output).parts', runner)
        self.assertIn("clean-install input role grammar differs", verifier)

    def test_saved_command_path_matching_survives_packet_relocation(self) -> None:
        old_root = Path("/old/packet")
        new_root = Path("/new/randomized/packet")
        saved = new_root / "inputs/toolchain/libnvrtc.so"
        command = ["cc", str(old_root / "inputs/toolchain/libnvrtc.so")]
        self.assertTrue(clean_verifier._command_has_saved_path(
            command, packet_root=new_root, saved_path=saved))
        self.assertFalse(clean_verifier._command_has_saved_path(
            ["cc", "/old/packet/other/libnvrtc.so"],
            packet_root=new_root, saved_path=saved))

    def test_clean_install_exact_command_contract_survives_relocation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            packet = Path(temporary) / "new-randomized-packet"
            receipts = packet / "receipts"
            receipts.mkdir(parents=True)
            old = "/old/execution/packet"
            inputs = {
                role: packet / relative for role, relative in {
                    "probe_source": "inputs/probe/probe.py",
                    "relation_descriptor": "inputs/relation.descriptor.json",
                    "triangle_descriptor": "inputs/triangle.descriptor.json",
                    "candidate_manifest": "inputs/candidate_manifest.json",
                    "trust_root": "inputs/trust_root.json",
                    "trust_head": "inputs/trust_head.json",
                    "trust_package": "inputs/trust_package.json",
                    "native": "inputs/native/librtdl_optix.so",
                    "wheel": "inputs/wheel/rtdl.whl",
                    "nvrtc_header": "inputs/toolchain/nvrtc.h",
                    "nvrtc_trap_source": "inputs/trap/trap.c",
                    "nvrtc_kat_source": "inputs/trap/kat.c",
                    "nvrtc_library": "inputs/toolchain/libnvrtc.so",
                }.items()
            }
            records = {
                "base_python": {"source_path": "/usr/bin/python3.12"},
                "host_cc": {"source_path": "/usr/bin/gcc"},
                "source_pyproject": {
                    "source_path": "/frozen/source/pyproject.toml",
                },
                "virtualenv_bootstrap/virtualenv/__main__.py": {
                    "source_path": "/pinned/bootstrap/virtualenv/__main__.py",
                },
                "virtualenv_bootstrap/distlib/member.py": {
                    "source_path": "/pinned/bootstrap/distlib/member.py",
                },
            }

            def write_command(name: str, command: list[str]) -> None:
                (receipts / f"{name}.command.json").write_bytes(
                    clean_verifier._canonical(command) + b"\n")

            write_command("venv", clean_runner._virtualenv_command(
                Path("/usr/bin/python3.12"), Path("/pinned/bootstrap"),
                Path(f"{old}/venv")))
            write_command("install", [
                f"{old}/venv/bin/python", "-I", "-m", "pip", "install",
                "--isolated", "--no-index", "--no-deps", "--no-cache-dir",
                "--no-compile",
                f"{old}/inputs/wheel/rtdl.whl",
            ])
            probe = [
                f"{old}/venv/bin/python", "-I", "-B",
                f"{old}/inputs/probe/probe.py",
                "--relation", f"{old}/inputs/relation.descriptor.json",
                "--triangle", f"{old}/inputs/triangle.descriptor.json",
                "--candidate-manifest", f"{old}/inputs/candidate_manifest.json",
                "--trust-root", f"{old}/inputs/trust_root.json",
                "--trust-head", f"{old}/inputs/trust_head.json",
                "--trust-package", f"{old}/inputs/trust_package.json",
                "--native", f"{old}/inputs/native/librtdl_optix.so",
                "--wheel", f"{old}/inputs/wheel/rtdl.whl",
                "--forbid-source-root", "/frozen/source",
                "--nvrtc-trap-library",
                f"{old}/build/goal5801_nvrtc_forbidden_preload.so",
                "--nvrtc-trap-log", f"{old}/build/nvrtc_lifecycle.log",
                "--output", f"{old}/result.json",
            ]
            write_command("probe", probe)
            write_command("trap_build", [
                "/usr/bin/gcc", "-shared", "-fPIC", "-I",
                f"{old}/inputs/toolchain", f"{old}/inputs/trap/trap.c",
                "-o", f"{old}/build/goal5801_nvrtc_forbidden_preload.so",
            ])
            write_command("kat_build", [
                "/usr/bin/gcc", "-I", f"{old}/inputs/toolchain",
                f"{old}/inputs/trap/kat.c",
                f"{old}/inputs/toolchain/libnvrtc.so", "-o",
                f"{old}/build/goal5801_nvrtc_positive_kat",
            ])
            write_command("kat", [
                f"{old}/build/goal5801_nvrtc_positive_kat",
            ])
            self.assertEqual(clean_verifier._verify_execution_commands(
                packet, inputs, records), old)

            install = json.loads(
                (receipts / "install.command.json").read_text(encoding="utf-8"))
            install.remove("--no-index")
            write_command("install", install)
            with self.assertRaisesRegex(RuntimeError, "install command"):
                clean_verifier._verify_execution_commands(packet, inputs, records)

            install.insert(6, "--no-index")
            write_command("install", install)
            hostile_probe = list(probe)
            hostile_probe[3] = "--triangle"
            write_command("probe", hostile_probe)
            with self.assertRaisesRegex(RuntimeError, "probe command"):
                clean_verifier._verify_execution_commands(packet, inputs, records)

    @unittest.skipUnless(
        os.environ.get("RTDL_GOAL5801_CLEAN_EVIDENCE"),
        "set RTDL_GOAL5801_CLEAN_EVIDENCE for real relocation verification",
    )
    def test_real_clean_packet_relocates_without_ephemeral_venv(self) -> None:
        source = Path(os.environ["RTDL_GOAL5801_CLEAN_EVIDENCE"]).resolve()
        self.assertTrue((source / "run.json").is_file())
        with tempfile.TemporaryDirectory(prefix="goal5801-relocation-") as temporary:
            moved = Path(temporary) / "randomized" / "clean-evidence"

            def ignore(directory: str, names: list[str]) -> set[str]:
                if Path(directory).resolve() == source and "venv" in names:
                    return {"venv"}
                return set()

            shutil.copytree(source, moved, symlinks=True, ignore=ignore)
            self.assertFalse((moved / "venv").exists())
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts" /
                    "goal5801_a3_verify_clean_install.py"), str(moved)],
                cwd=temporary, check=False, capture_output=True, text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(
                result["status"],
                "PASS__INDEPENDENT_CLEAN_INSTALL_V3_VERIFICATION")
            self.assertEqual(result["current_trusted_deployment_count"], 2)
            self.assertEqual(
                result["retained_predecessor_deployment_count"], 0)
            self.assertEqual(
                result["signed_trust_package_deployment_count"], 2)
            self.assertFalse(
                result["unmaterialized_retired_sequences_reconstructed"])


if __name__ == "__main__":
    unittest.main()
