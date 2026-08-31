"""Hostile tests for the high-level Goal5802 POD-S0 config builder."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

from scripts import goal5802_build_pod_s0_config as builder
from scripts import goal5802_build_target_runtime_manifest as runtime_manifest
from scripts import goal5802_run_pod_s0_untimed as s0


ROOT = Path(__file__).resolve().parents[1]


def _required_long_options(path: Path, command: str | None) -> set[str]:
    """Recover required argparse options, scoped to a named subcommand."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    owners: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 \
                or not isinstance(node.targets[0], ast.Name) \
                or not isinstance(node.value, ast.Call) \
                or not isinstance(node.value.func, ast.Attribute) \
                or node.value.func.attr != "add_parser" \
                or not node.value.args \
                or not isinstance(node.value.args[0], ast.Constant) \
                or not isinstance(node.value.args[0].value, str):
            continue
        owners[node.targets[0].id] = node.value.args[0].value
    result: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) \
                or not isinstance(node.func, ast.Attribute) \
                or node.func.attr != "add_argument" or not node.args:
            continue
        required = any(
            keyword.arg == "required"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in node.keywords)
        option = node.args[0]
        if not required or not isinstance(option, ast.Constant) \
                or not isinstance(option.value, str) \
                or not option.value.startswith("--"):
            continue
        owner = node.func.value.id \
            if isinstance(node.func.value, ast.Name) else None
        if owner in owners and owners[owner] != command:
            continue
        result.add(option.value)
    return result


class Goal5802PodS0ConfigBuilderTest(unittest.TestCase):
    def test_runtime_manifest_consumes_all_current_pyoptix_boundary_leaves(
            self) -> None:
        value = {
            "schema": (
                "rtdl.goal5802.offline_pyoptix_clean_install_receipt.v1"),
            "status": "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED",
            "create_only": True,
            "pip_policy": copy.deepcopy(
                runtime_manifest.OFFLINE_PYOPTIX_PIP_POLICY),
            "validation_boundary": copy.deepcopy(
                runtime_manifest.OFFLINE_PYOPTIX_VALIDATION_BOUNDARY),
            "install_command": [
                "python", "-I", "-S", "-B", "-P", "-c", "pip", "--isolated",
                "install", "--no-index", "--no-deps", "--no-cache-dir",
                "--no-compile", "--disable-pip-version-check", "--target",
                "/exact/site-packages", "/exact/pyoptix.whl",
            ],
        }
        self.assertEqual(
            runtime_manifest._validate_offline_pyoptix_manifest_projection(
                value), value)
        for key, expected in (
                runtime_manifest.OFFLINE_PYOPTIX_VALIDATION_BOUNDARY.items()):
            hostile = copy.deepcopy(value)
            hostile["validation_boundary"][key] = (
                False if type(expected) is int else
                0 if expected is False else 1)
            with self.assertRaises(RuntimeError, msg=key):
                runtime_manifest._validate_offline_pyoptix_manifest_projection(
                    hostile)
        no_compile = copy.deepcopy(value)
        no_compile["pip_policy"]["no_compile"] = False
        with self.assertRaises(RuntimeError):
            runtime_manifest._validate_offline_pyoptix_manifest_projection(
                no_compile)
        no_compile = copy.deepcopy(value)
        no_compile["install_command"].remove("--no-compile")
        with self.assertRaises(RuntimeError):
            runtime_manifest._validate_offline_pyoptix_manifest_projection(
                no_compile)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name).resolve()
        self.run = self.base / "run"
        self.output = self.base / "pod_s0_config.json"
        self.input_root = self.base / "inputs"
        self.input_root.mkdir()
        self.wheelhouse = self.input_root / "wheelhouse"
        self.bootstrap = self.input_root / "bootstrap"
        self.cuda = self.input_root / "cuda"
        self.library = self.input_root / "lib"
        for path in (
                self.wheelhouse, self.bootstrap,
                self.cuda / "include", self.cuda / "bin", self.cuda / "lib64",
                self.library):
            path.mkdir(parents=True, exist_ok=True)
        (self.cuda / "lib64/libnvrtc.so.12").write_bytes(b"nvrtc\n")
        (self.cuda / "lib64/libnvrtc-builtins.so.12").write_bytes(
            b"builtins\n")
        self.pyoptix_wheel = self.wheelhouse / (
            "pyoptix-9.1.0-cp312-cp312-manylinux_2_17_x86_64.whl")
        with zipfile.ZipFile(self.pyoptix_wheel, "w") as archive:
            archive.writestr("optix/__init__.py", b"\n")
            archive.writestr(
                "optix/_optix.cpython-312-x86_64-linux-gnu.so", b"elf")
        self.wheelhouse_manifest = self.wheelhouse / "wheelhouse_manifest.json"
        self.wheelhouse_manifest.write_bytes(b"{}\n")
        self.wheel_rows = []
        for distribution, version in builder.wheelhouse.REQUIRED_DISTRIBUTIONS:
            path = self.pyoptix_wheel if distribution == "pyoptix" \
                else self.wheelhouse / f"{distribution}-{version}.whl"
            if not path.exists():
                path.write_bytes(distribution.encode("ascii"))
            self.wheel_rows.append({
                "distribution": distribution,
                "version": version,
                "saved_path": path.name,
                "path": path,
            })

        self.git = Path(shutil.which("git") or sys.executable).resolve()
        self.tools = {
            name: self._file(name, b"tool\n")
            for name in (
                "nvidia-smi", "nvcc", "make", "cxx", "uname", "ldd",
                "pkg-config", "strace")
        }
        for path in self.tools.values():
            path.chmod(0o755)
        self.files = {
            "packet": self._file("source.bundle", b"packet\n"),
            "packet_manifest": self._file("source_manifest.json", b"{}\n"),
            "scan": self._file("scan.json", b"scan\n"),
            "root": self._file("public_root.json", b"root\n"),
            "headers": self._file("headers.bundle", b"headers\n"),
            "old_build": self._file("old_build.json", b"{}\n"),
        }
        trust_body = {
            "schema": builder.TRUST_ROOT_SCHEMA,
            "key_id": (
                "TEST_ONLY_goal5802_final_home_qualification_builder_test"),
            "rsa_modulus_base64": "AQ==",
            "rsa_exponent": 65537,
        }
        trust_root = {
            **trust_body,
            "trust_root_sha256": hashlib.sha256(
                builder.TRUST_ROOT_DOMAIN
                + builder._canonical(trust_body)).hexdigest(),
        }
        self.files["root"].write_bytes(builder._canonical(trust_root) + b"\n")
        self.args = self._args()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _file(self, name: str, payload: bytes) -> Path:
        path = self.input_root / name
        path.write_bytes(payload)
        return path

    def _args(self) -> argparse.Namespace:
        scan_sha = hashlib.sha256(self.files["scan"].read_bytes()).hexdigest()
        return argparse.Namespace(
            source_root=ROOT,
            run_root=self.run,
            source_packet=self.files["packet"],
            source_packet_manifest=self.files["packet_manifest"],
            private_scan_authority=self.files["scan"],
            private_scan_authority_sha256=scan_sha,
            public_trust_root=self.files["root"],
            private_key_sha256="1" * 64,
            base_python=Path(sys.executable).resolve(),
            offline_wheelhouse_root=self.wheelhouse,
            virtualenv_bootstrap_root=self.bootstrap,
            optix_headers_bundle=self.files["headers"],
            pyoptix_wheel_build_receipt=self.files["old_build"],
            cuda_prefix=self.cuda,
            nvidia_smi=self.tools["nvidia-smi"],
            nvcc=self.tools["nvcc"],
            make=self.tools["make"],
            cxx=self.tools["cxx"],
            git=self.git,
            uname=self.tools["uname"],
            ldd=self.tools["ldd"],
            pkg_config=self.tools["pkg-config"],
            strace=self.tools["strace"],
            runtime_library_directory=[self.library],
            direct_library_directory=[self.library],
            manual_judgement=ROOT / builder.MANUAL_AUTHORITY_RELATIVE,
            engineering_effort_ledger=(
                ROOT / builder.ENGINEERING_LEDGER_RELATIVE),
            output=self.output,
        )

    def _config(self) -> dict[str, object]:
        with mock.patch.object(
                builder, "_source_identity",
                return_value=("a" * 40, "b" * 40, 1_777_777_777)), \
                mock.patch.object(builder, "_packet_identity"), \
                mock.patch.object(
                    builder, "_wheelhouse_rows",
                    return_value=(self.wheel_rows, self.wheelhouse_manifest)), \
                mock.patch.object(builder, "_python_version", return_value=(3, 12)):
            return builder.build_config(copy.deepcopy(self.args))

    @staticmethod
    def _by_name(config: dict[str, object]) -> dict[str, dict[str, object]]:
        rows = [*config["prepare_steps"], *config["finish_steps"]]
        return {str(row["name"]): row for row in rows}

    def test_exact_stage_order_and_production_schema_validation(self) -> None:
        config = self._config()
        self.assertEqual(
            [row["name"] for row in config["prepare_steps"]],
            list(s0.PREPARE_STEPS))
        self.assertEqual(
            [row["name"] for row in config["finish_steps"]],
            list(s0.FINISH_STEPS))
        self.output.write_bytes(builder._canonical(config) + b"\n")
        loaded = s0._load_config(self.output, self.run)
        self.assertEqual(loaded["claim_boundary"], {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "execution_authority_consumed": False,
            "gpu_use": "UNTIMED_TARGET_OBSERVATION_AND_OPERATION_KATS_ONLY",
            "retry_resume_replacement_allowed": False,
            "target_selection_allowed": False,
        })

    def test_tool_symlink_is_canonicalized_before_native_custody(self) -> None:
        target = self.tools["pkg-config"]
        alias = self.input_root / "pkg-config-alias"
        try:
            alias.symlink_to(target)
        except OSError as error:
            self.skipTest(f"file symlinks unavailable on this host: {error}")
        self.args.pkg_config = alias

        rows = self._by_name(self._config())
        native_args = rows["native_build"]["args"]
        native_value = native_args[native_args.index("--pkg-config") + 1]
        self.assertEqual(native_value, str(target.resolve(strict=True)))

        custody_args = rows["native_custody_capture"]["args"]
        tool_values = [
            custody_args[index + 1]
            for index, value in enumerate(custody_args[:-1])
            if value == "--tool"
        ]
        self.assertIn(
            f"pkg_config={target.resolve(strict=True)}", tool_values)
        self.assertNotIn(f"pkg_config={alias}", tool_values)

    def test_standard_cuda_include_symlink_is_resolved_for_strict_consumers(
            self) -> None:
        linked = self.cuda / "include"
        real = self.input_root / "cuda-target-include"
        linked.rmdir()
        real.mkdir()
        try:
            linked.symlink_to(real, target_is_directory=True)
        except OSError as error:
            real.rmdir()
            linked.mkdir()
            self.skipTest(f"directory symlinks unavailable: {error}")
        rows = self._by_name(self._config())
        expected = str(real.resolve(strict=True))
        for name in (
                "candidate_seed1", "candidate_seed777",
                "rtdl_clean_install", "header_projection", "matched_ptx"):
            arguments = rows[name]["args"]
            self.assertEqual(
                arguments[arguments.index("--cuda-include") + 1], expected,
                name)

    def test_every_stage_has_required_cli_shape(self) -> None:
        rows = self._by_name(self._config())
        required: dict[str, set[str]] = {
            "source_packet_verify": {"--packet", "--manifest", "--receipt"},
            "pyoptix_build_provenance_materialize": {
                "materialize", "--git", "--headers-bundle",
                "--original-build-receipt", "--pyoptix-wheel",
                "--output-directory"},
            "pyoptix_build_provenance_verify": {"verify", "--receipt"},
            "pyoptix_offline_plan": {
                "plan", "--output-directory", "--base-python",
                "--virtualenv-bootstrap-root", "--wheelhouse-root",
                "--plan-output"},
            "pyoptix_offline_run": {"run", "--plan"},
            "pyoptix_offline_verify": {"verify", "--output-directory"},
            "target_observation": {"--nvidia-smi", "--nvcc", "--output"},
            "origin_authority": {"--repository", "--commit", "--output-directory"},
            "native_build": {
                "--source-root", "--output-root", "--optix-prefix",
                "--cuda-prefix", "--build-id", "--cuda-arch", "--make",
                "--nvcc", "--host-cxx", "--git", "--uname", "--ldd",
                "--pkg-config"},
            "native_custody_capture": {
                "--output", "--source-root", "--source-commit",
                "--origin-commit", "--origin-tree", "--origin-commit-object",
                "--origin-inventory", "--native", "--build-cwd",
                "--build-source-root", "--build-command", "--build-stdout",
                "--build-stderr", "--build-exit-code", "--dependency-file",
                "--build-environment", "--tool", "--link-input",
                "--tool-receipt"},
            "candidate_seed1": {
                "build", "--native", "--optix-include", "--cuda-include",
                "--optix-sdk", "--compute-capability",
                "--deployment-generation", "--relation-minimum-overlap-f32",
                "--proof", "--output"},
            "candidate_seed777": {
                "build", "--native", "--optix-include", "--cuda-include",
                "--optix-sdk", "--compute-capability",
                "--deployment-generation", "--relation-minimum-overlap-f32",
                "--proof", "--output"},
            "rtdl_wheel_double_seed": {
                "--source-root", "--git", "--python", "--commit", "--tree",
                "--virtualenv-bootstrap-root", "--source-date-epoch",
                "--output"},
            "rtdl_clean_install": {
                "--output-directory", "--base-python",
                "--virtualenv-bootstrap-root", "--probe", "--wheel",
                "--source-root", "--candidate-manifest", "--trust-root",
                "--trust-head", "--trust-predecessor-package",
                "--trust-package", "--native", "--host-cc", "--cuda-include",
                "--nvrtc-library", "--nvrtc-trap-source", "--nvrtc-kat-source"},
            "combined_runtime_plan": {
                "plan", "--output-directory", "--base-python",
                "--virtualenv-bootstrap-root", "--wheel", "--plan-output"},
            "combined_runtime_run": {
                "run", "--plan", "--expected-plan-file-sha256"},
            "combined_runtime_verify": {"verify", "--output-directory"},
            "product_binding": {
                "--clean-root", "--source-commit", "--source-tree",
                "--standalone-verifier", "--native-custody-root",
                "--standalone-native-custody-verifier", "--output"},
            "freeze_inputs": {"export", "--root", "--output-directory"},
            "successor_forecast": {
                "--root", "--product-binding", "--clean-install-root",
                "--native-custody-root", "--standalone-clean-verifier",
                "--standalone-native-custody-verifier", "--workload-authority",
                "--operation-contract", "--comparative-schedule",
                "--build-cold-schedule", "--instrument-source-manifest",
                "--goal5799-binding", "--manual-judgement", "--output"},
            "local_freeze": {
                "--root", "--product-binding", "--engineering-effort-ledger",
                "--successor-forecast", "--output"},
            "local_freeze_verify": {
                "--root", "--freeze", "--clean-install-root",
                "--standalone-clean-install-verifier", "--native-custody-root",
                "--standalone-native-custody-verifier"},
            "header_projection": {
                "--nvcc", "--cxx", "--device-source", "--compaction-source",
                "--direct-source", "--optix-include", "--cuda-include",
                "--compute-capability", "--projection-root", "--receipt"},
            "header_projection_verify": {
                "--receipt", "--projection-root", "--mode"},
            "direct_recipe": {"--library-directory", "--output"},
            "direct_worker": {
                "--recipe", "--cxx", "--direct-source", "--optix-include",
                "--cuda-include", "--output", "--receipt"},
            "matched_ptx": {
                "--device-source", "--compaction-source", "--optix-include",
                "--cuda-include", "--original-optix-include",
                "--original-cuda-include", "--header-projection-root",
                "--header-projection-receipt", "--strace", "--replay-root",
                "--compute-capability", "--output", "--compaction-output",
                "--receipt"},
            "direct_kat": {
                "--worker", "--direct-source", "--ptx",
                "--compaction-cubin", "--output"},
            "pyoptix_kat": {"--ptx", "--compaction-cubin", "--output"},
            "rtdl_kat": {
                "--relation-artifact", "--relation-authority",
                "--relation-deployment-id",
                "--relation-executable-identity-sha256",
                "--triangle-artifact", "--triangle-authority",
                "--triangle-deployment-id",
                "--triangle-executable-identity-sha256", "--trust-root",
                "--trust-head", "--trust-package", "--native-library",
                "--rtdsl-init", "--rtdlexe-module", "--output"},
            "dual_validation": {
                "--root", "--freeze", "--runtime-manifest", "--output"},
            "plan_only": {"--freeze", "--root", "--plan-output"},
        }
        positional_only = {
            "native_custody_verify", "rtdl_clean_install_verify",
            "host_runtime"}
        for name, step in rows.items():
            arguments = set(step["args"])
            if name in required:
                self.assertTrue(
                    required[name] <= arguments,
                    f"{name} missing {sorted(required[name] - arguments)}")
            elif name not in positional_only and name != "target_runtime_manifest":
                self.fail(f"stage lacks CLI-shape assertion: {name}")

        manifest_args = set(rows["target_runtime_manifest"]["args"])
        for role in runtime_manifest.FILE_ROLES:
            self.assertIn(f"--{role.replace('_', '-')}", manifest_args)
        for role in runtime_manifest.DIRECTORY_ROLES:
            self.assertIn(f"--{role.replace('_', '-')}", manifest_args)
        self.assertTrue({
            "--relation-deployment-id", "--triangle-deployment-id",
            "--output"} <= manifest_args)

    def test_source_cli_required_flags_cannot_drift_past_builder(self) -> None:
        rows = self._by_name(self._config())
        commands = {
            "pyoptix_build_provenance_materialize": "materialize",
            "pyoptix_build_provenance_verify": "verify",
            "pyoptix_offline_plan": "plan",
            "pyoptix_offline_run": "run",
            "pyoptix_offline_verify": "verify",
            "candidate_seed1": "build", "candidate_seed777": "build",
            "combined_runtime_plan": "plan",
            "combined_runtime_run": "run",
            "combined_runtime_verify": "verify",
            "freeze_inputs": "export",
        }
        for name, step in rows.items():
            if name in {"plan_only", "target_runtime_manifest"}:
                continue
            required = _required_long_options(
                ROOT / str(step["target"]), commands.get(name))
            arguments = set(step["args"])
            self.assertTrue(
                required <= arguments,
                f"{name} source CLI added required flags not generated: "
                f"{sorted(required - arguments)}")

    def test_qualification_root_identity_is_explicit_at_every_clean_rebuild(
            self) -> None:
        config = self._config()
        rows = self._by_name(config)
        expected = hashlib.sha256(
            self.files["root"].read_bytes()).hexdigest()
        self.assertEqual(
            config["trust_root_file_sha256"], expected)
        self.assertEqual(
            config["trust_root_scope"],
            builder.QUALIFICATION_ONLY_TRUST_SCOPE)
        flag = "--qualification-only-expected-trust-root-file-sha256"
        for name in (
                "rtdl_clean_install_verify", "product_binding",
                "successor_forecast", "local_freeze_verify"):
            with self.subTest(name=name):
                arguments = rows[name]["args"]
                self.assertEqual(arguments.count(flag), 1)
                self.assertEqual(arguments[arguments.index(flag) + 1], expected)

    def test_unpinned_formal_root_cannot_be_relabelled_as_controlling(
            self) -> None:
        body = {
            "schema": builder.TRUST_ROOT_SCHEMA,
            "key_id": "TEST_ONLY_goal5802_rtx_measurement_root",
            "rsa_modulus_base64": "AQ==",
            "rsa_exponent": 65537,
        }
        value = {
            **body,
            "trust_root_sha256": hashlib.sha256(
                builder.TRUST_ROOT_DOMAIN
                + builder._canonical(body)).hexdigest(),
        }
        self.files["root"].write_bytes(builder._canonical(value) + b"\n")
        with self.assertRaisesRegex(
                builder.ConfigBuildError,
                "public trust-root scope or controlling identity"):
            self._config()

    def test_exact_formal_root_uses_default_controlling_verifier_path(
            self) -> None:
        self.args.public_trust_root = ROOT / (
            "history/internal_docs/"
            "goal5802_rtx_measurement_test_trust_public_root_v5_20260826.json")
        config = self._config()
        rows = self._by_name(config)
        self.assertEqual(
            config["trust_root_scope"],
            builder.FORMAL_MEASUREMENT_TRUST_SCOPE)
        self.assertEqual(
            config["trust_root_file_sha256"],
            builder.FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256)
        flag = "--qualification-only-expected-trust-root-file-sha256"
        for name in (
                "rtdl_clean_install_verify", "product_binding",
                "successor_forecast", "local_freeze_verify"):
            with self.subTest(name=name):
                self.assertNotIn(flag, rows[name]["args"])

    def test_interpreter_transitions_cannot_skip_new_environments(self) -> None:
        rows = self._by_name(self._config())
        base = str(Path(sys.executable).resolve())
        pyoptix = str(self.run / "prepare/pyoptix_runtime/venv/bin/python")
        combined = str(self.run / "finish/combined_runtime/venv/bin/python")
        for name in (
                "source_packet_verify",
                "pyoptix_build_provenance_materialize",
                "pyoptix_build_provenance_verify", "pyoptix_offline_plan",
                "pyoptix_offline_run"):
            self.assertEqual(rows[name]["interpreter"], base, name)
        pyoptix_rows = (
            "pyoptix_offline_verify", "target_observation",
            "origin_authority", "native_build", "native_custody_capture",
            "native_custody_verify", "candidate_seed1", "candidate_seed777",
            "rtdl_wheel_double_seed", "rtdl_clean_install",
            "rtdl_clean_install_verify", "combined_runtime_plan",
            "combined_runtime_run")
        for name in pyoptix_rows:
            self.assertEqual(rows[name]["interpreter"], pyoptix, name)
        combined_index = list(s0.FINISH_STEPS).index("combined_runtime_verify")
        for name in s0.FINISH_STEPS[combined_index:]:
            self.assertEqual(rows[name]["interpreter"], combined, name)

    def test_outputs_are_unique_and_verify_stdout_is_orchestrator_owned(self) -> None:
        config = self._config()
        rows = self._by_name(config)
        output_paths = [
            output["path"]
            for step in [*config["prepare_steps"], *config["finish_steps"]]
            for output in step["outputs"]]
        self.assertEqual(len(output_paths), len(set(output_paths)))
        expected_verify_stdout = {
            "pyoptix_build_provenance_verify": ("prepare", 3),
            "pyoptix_offline_verify": ("prepare", 6),
            "native_custody_verify": ("prepare", 11),
            "rtdl_clean_install_verify": ("finish", 3),
            "combined_runtime_verify": ("finish", 6),
            "local_freeze_verify": ("finish", 11),
            "header_projection_verify": ("finish", 13),
        }
        for name, (phase, ordinal) in expected_verify_stdout.items():
            self.assertEqual(rows[name]["outputs"], [{
                "path": str(
                    self.run / f"{phase}_journal/{ordinal:02d}_{name}.stdout.bin"),
                "kind": "file",
            }])
        for value in output_paths:
            Path(value).relative_to(self.run)

    def test_all_arms_use_the_single_materialized_optix_header_authority(self) -> None:
        rows = self._by_name(self._config())
        sdk = self.run / "prepare/pyoptix_build_provenance/optix_headers"
        include = sdk / "include"

        def option(name: str, flag: str) -> str:
            arguments = rows[name]["args"]
            return str(arguments[arguments.index(flag) + 1])

        self.assertEqual(option("native_build", "--optix-prefix"), str(sdk))
        for name in ("candidate_seed1", "candidate_seed777"):
            self.assertEqual(option(name, "--optix-include"), str(include))
        self.assertEqual(
            option("header_projection", "--optix-include"), str(include))
        self.assertEqual(
            option("target_runtime_manifest", "--optix-sdk"), str(sdk))
        self.assertEqual(
            option(
                "target_runtime_manifest", "--pyoptix-wheel-build-receipt"),
            str(self.run / "prepare/pyoptix_build_provenance/receipt.json"))
        self.assertEqual(
            option(
                "target_runtime_manifest", "--pyoptix-clean-install-receipt"),
            str(self.run / (
                "prepare/pyoptix_runtime/"
                "offline_pyoptix_clean_install_receipt.json")))
        self.assertNotIn("--optix-prefix", builder._parser()._option_string_actions)

    def test_all_direct_consumers_bind_the_frozen_goal5802_source(self) -> None:
        rows = self._by_name(self._config())
        expected_relative = (
            "experiments/goal5802_premeasurement/direct_scalar_worker.cpp")
        legacy_relative = "experiments/goal5796_matched/direct_optix.cpp"
        self.assertEqual(builder.SOURCE_PATHS["direct_source"], expected_relative)
        expected = str((ROOT / expected_relative).resolve(strict=True))
        legacy = str((ROOT / legacy_relative).resolve(strict=True))

        observed = []
        for name in ("header_projection", "direct_worker", "direct_kat"):
            arguments = rows[name]["args"]
            self.assertEqual(arguments.count("--direct-source"), 1, name)
            source = str(arguments[arguments.index("--direct-source") + 1])
            observed.append(source)
            self.assertEqual(source, expected, name)
            self.assertNotEqual(source, legacy, name)
        self.assertEqual(observed, [expected, expected, expected])

    def test_pyoptix_kat_and_manifest_bind_same_combined_runtime(self) -> None:
        rows = self._by_name(self._config())
        combined_root = self.run / "finish/combined_runtime"
        combined_python = combined_root / "venv/bin/python"
        combined_site = combined_root / "venv/lib/python3.12/site-packages"

        self.assertEqual(
            rows["pyoptix_kat"]["interpreter"], str(combined_python))
        manifest_args = rows["target_runtime_manifest"]["args"]

        def option(flag: str) -> str:
            return str(manifest_args[manifest_args.index(flag) + 1])

        self.assertEqual(
            option("--pyoptix-initializer"),
            str(combined_site / "optix/__init__.py"))
        self.assertEqual(
            option("--pyoptix-extension"),
            str(combined_site / "optix/_optix.cpython-312-x86_64-linux-gnu.so"))

    def test_dynamic_values_are_exact_tokens_and_authorities_are_mandatory(self) -> None:
        config = self._config()
        builder._assert_no_embedded_or_manual_dynamic(config)

        hostile = copy.deepcopy(config)
        step = self._by_name(hostile)["native_build"]
        step["args"][step["args"].index("${OBSERVED_SM}")] = (
            "sm_${OBSERVED_SM}")
        with self.assertRaises(builder.ConfigBuildError):
            builder._assert_no_embedded_or_manual_dynamic(hostile)

        hostile = copy.deepcopy(config)
        step = self._by_name(hostile)["rtdl_kat"]
        step["args"][step["args"].index("${RELATION_AUTHORITY}")] = (
            str(self.input_root / "manual_relation_authority.json"))
        with self.assertRaises(builder.ConfigBuildError):
            builder._assert_no_embedded_or_manual_dynamic(hostile)

        hostile = copy.deepcopy(config)
        self._by_name(hostile)["native_build"]["args"].append("${UNKNOWN}")
        with self.assertRaises(builder.ConfigBuildError):
            builder._assert_no_embedded_or_manual_dynamic(hostile)

    def test_semantic_inputs_reject_dynamic_paths_and_existing_outputs(self) -> None:
        hostile = copy.deepcopy(self.args)
        hostile.source_packet = Path(str(self.files["packet"]) + "${OBSERVED_CC}")
        with self.assertRaises(builder.ConfigBuildError):
            builder.build_config(hostile)

        self.run.mkdir()
        with self.assertRaises(builder.ConfigBuildError):
            builder.build_config(copy.deepcopy(self.args))

    def test_generated_graph_contains_no_formal_or_timing_authority(self) -> None:
        config = self._config()
        arguments = [
            argument
            for step in [*config["prepare_steps"], *config["finish_steps"]]
            for argument in step["args"]]
        for forbidden in (
                "--execution-authority", "execute_formal", "formal_worker",
                "registered_timing"):
            self.assertNotIn(forbidden, arguments)
        self.assertEqual(config["candidate_seeds"], [1, 777])
        self.assertEqual(config["wheel_seeds"], [1, 777])

    def test_base_python_probe_disables_site_and_environment_influence(self) -> None:
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"3.12\n", stderr=b"")
        with mock.patch.object(
                builder.subprocess, "run", return_value=completed) as run:
            self.assertEqual(
                builder._python_version(Path(sys.executable)), (3, 12))
        command = run.call_args.args[0]
        self.assertEqual(command[1:4], ["-I", "-S", "-B"])

    def test_write_validates_before_create_only_publication(self) -> None:
        config = self._config()
        with mock.patch.object(builder, "build_config", return_value=config):
            receipt = builder.write_config(copy.deepcopy(self.args))
        payload = builder._canonical(config) + b"\n"
        self.assertEqual(self.output.read_bytes(), payload)
        self.assertEqual(
            receipt["config_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertFalse(any(
            path.name.startswith(".goal5802-pod-s0-config-")
            for path in self.output.parent.iterdir()))

        self.output.unlink()
        with mock.patch.object(builder, "build_config", return_value=config), \
                mock.patch.object(
                    builder.s0, "_load_config",
                    side_effect=s0.S0Error("synthetic rejection")):
            with self.assertRaises(s0.S0Error):
                builder.write_config(copy.deepcopy(self.args))
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
