"""Independent hostile tests for Goal5802 fresh-process NVRTC replay.

These tests deliberately state the evidence contract a reviewer needs rather
than mirroring implementation details.  A failing test is a red-team finding:
do not mark it expected-failure merely to make the suite green.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from types import SimpleNamespace
import inspect
import tempfile
import unittest
from unittest import mock

from experiments.goal5802_premeasurement import independent_recount as independent
from scripts import goal5802_prepare_matched_ptx_untimed as replay


class FreshChildEntrypointTest(unittest.TestCase):
    def test_bootstraps_project_imports_from_unrelated_cwd(self) -> None:
        child = (Path(__file__).resolve(strict=True).parents[1] / "scripts" /
                 "goal5802_nvrtc_compile_child.py")
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run(
                [sys.executable, "-I", str(child), "--help"],
                cwd=Path(temporary), capture_output=True, text=True,
                check=False)
        self.assertEqual(
            completed.returncode, 0,
            msg=f"stdout={completed.stdout!r}\nstderr={completed.stderr!r}")
        self.assertIn("--compute-capability", completed.stdout)

    def test_python_invocation_preserves_environment_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            target = root / "base-python"
            target.write_bytes(b"interpreter")
            link = root / "environment-python"
            try:
                link.symlink_to(target)
            except OSError as error:
                self.skipTest(f"host cannot create interpreter symlink: {error}")

            observed = replay._python_invocation_path(str(link.absolute()))
            identity = replay._python_replay_identity(observed)

        self.assertEqual(observed, link.absolute())
        self.assertNotEqual(observed, target)
        self.assertEqual(identity["invocation_path"], str(link.absolute()))
        self.assertEqual(identity["path"], str(target.resolve()))
        self.assertEqual(identity["bytes"], len(b"interpreter"))
        self.assertEqual(
            identity["sha256"], hashlib.sha256(b"interpreter").hexdigest())


def _quoted(path: Path | str) -> str:
    """Return the exact quoted spelling strace uses for ordinary paths."""

    return json.dumps(str(path))


def _trace_escaped(path: Path | str) -> str:
    return json.dumps(str(path))[1:-1]


def _openat(path: Path | str, result: int = 3) -> bytes:
    annotation = f"<{_trace_escaped(path)}>" if result >= 0 else ""
    return (
        f"openat(AT_FDCWD, {_quoted(path)}, O_RDONLY|O_CLOEXEC) = "
        f"{result}{annotation}\n"
    ).encode("utf-8")


class StraceParserContractTest(unittest.TestCase):
    def test_strict_success_uses_syscall_exit_kernel_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            alias = root / "alias-that-may-no-longer-exist"
            kernel_target = PurePosixPath("/original-sdk/optix.h")
            payload = (
                f"openat(AT_FDCWD<{_trace_escaped(root)}>, "
                f"{json.dumps(str(alias))}, O_RDONLY) = "
                f"3<{_trace_escaped(kernel_target)}>\n"
            ).encode("utf-8")

            rows = replay.parse_strace_file_accesses(
                [payload], cwd=root, trace_pids=[4242],
                require_kernel_targets=True)

            self.assertEqual(rows[0]["normalized_path"], str(kernel_target))
            self.assertEqual(rows[0]["kernel_target_path"], str(kernel_target))

            independent_rows = independent._parse_independent_strace_accesses(
                [payload], cwd=root, trace_pids=[4242])
            self.assertEqual(independent_rows, rows)

    def test_strict_success_without_kernel_target_fails_closed(self) -> None:
        payload = b'open("ordinary", O_RDONLY) = 3\n'
        with self.assertRaisesRegex(RuntimeError, "kernel target"):
            replay.parse_strace_file_accesses(
                [payload], cwd=Path.cwd(), trace_pids=[4242],
                require_kernel_targets=True)
        with self.assertRaisesRegex(RuntimeError, "lacks -y target"):
            independent._parse_independent_strace_accesses(
                [payload], cwd=Path.cwd(), trace_pids=[4242])

    def test_successful_open_and_openat_are_parsed_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            absolute = root / "absolute header.h"
            relative = Path("relative header.h")
            payload = (
                f"open({_quoted(absolute)}, O_RDONLY) = 7\n"
                f"openat(AT_FDCWD, {_quoted(relative)}, O_RDONLY) = -1 "
                "ENOENT (No such file or directory)\n"
            ).encode("utf-8")

            rows = replay.parse_strace_file_accesses([payload], cwd=root)

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["syscall"], "open")
            self.assertEqual(rows[0]["normalized_path"], str(absolute))
            self.assertIs(rows[0]["success"], True)
            self.assertEqual(rows[0]["result"], 7)
            self.assertEqual(rows[1]["syscall"], "openat")
            self.assertEqual(
                rows[1]["normalized_path"], str((root / relative).resolve()))
            self.assertIs(rows[1]["success"], False)
            self.assertEqual(rows[1]["result"], -1)

    def test_numeric_dirfd_relative_open_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "numeric dirfd"):
                replay.parse_strace_file_accesses(
                    [b'openat(19, "optix.h", O_RDONLY) = 20\n'],
                    cwd=Path(temporary).resolve())

    def test_unfinished_and_resumed_syscalls_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cwd = Path(temporary).resolve()
            for payload in (
                    b'openat(AT_FDCWD, "x", O_RDONLY <unfinished ...>\n',
                    b'<... openat resumed>) = 3\n'):
                with self.subTest(payload=payload):
                    with self.assertRaisesRegex(
                            RuntimeError, "unfinished/resumed"):
                        replay.parse_strace_file_accesses([payload], cwd=cwd)

    def test_unparseable_open_line_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "fully parseable"):
                replay.parse_strace_file_accesses(
                    [b"openat(AT_FDCWD, NULL, O_RDONLY) = -1 EFAULT\n"],
                    cwd=Path(temporary).resolve())

    def test_non_open_syscall_argument_named_openat_is_not_misparsed(
            self) -> None:
        """Legal paths in the traced execve argv may contain ``openat(``."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            ordinary = root / "ordinary.h"
            payload = (
                'execve("/usr/bin/python3", ["python3", '
                '"/work/openat(project)/child.py"], 0x1) = 0\n'
            ).encode("utf-8") + _openat(ordinary, 3)

            rows = replay.parse_strace_file_accesses([payload], cwd=root)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["normalized_path"], str(ordinary))

    def test_strace_truncated_quoted_path_fails_closed(self) -> None:
        """A quoted value followed by ``...`` is not an exact path."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            visible_prefix = root / "original-sdk" / "incl"
            payload = (
                f"openat(AT_FDCWD, {_quoted(visible_prefix)}..., "
                "O_RDONLY) = 3\n"
            ).encode("utf-8")
            with self.assertRaisesRegex(RuntimeError, "truncat|parseable"):
                replay.parse_strace_file_accesses([payload], cwd=root)

    def test_result_is_parsed_after_arguments_not_from_path_text(self) -> None:
        """An ``= <digits>`` substring in a legal path is not a return code."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = root / "sdk= 7 " / "optix.h"
            payload = (
                f"openat(AT_FDCWD, {_quoted(path)}, O_RDONLY) = -1 ENOENT\n"
            ).encode("utf-8")

            rows = replay.parse_strace_file_accesses([payload], cwd=root)

            self.assertEqual(rows[0]["result"], -1)
            self.assertIs(rows[0]["success"], False)

    def test_proc_self_magic_paths_do_not_bind_the_verifier_pid(self) -> None:
        payload = (
            b'openat(AT_FDCWD, "/proc/self/maps", O_RDONLY) = 3\n'
            b'openat(AT_FDCWD, "/proc/thread-self/status", O_RDONLY) = 4\n'
        )
        rows = replay.parse_strace_file_accesses(
            [payload], cwd=Path.cwd(), trace_pids=[4242])

        self.assertEqual(
            [row["normalized_path"] for row in rows],
            ["/proc/self/maps", "/proc/thread-self/status"])
        self.assertEqual([row["trace_pid"] for row in rows], [4242, 4242])

    def test_proc_self_cannot_alias_an_sdk_path(self) -> None:
        for path in (
                "/proc/self/root/original/optix.h",
                "/proc/self/fd/19/../../maps",
                "/proc/self/root/tmp/x/../../../status"):
            with self.subTest(path=path):
                payload = (
                    f"openat(AT_FDCWD, {json.dumps(path)}, O_RDONLY) = 3\n"
                ).encode("utf-8")
                with self.assertRaisesRegex(RuntimeError, "procfs magic"):
                    replay.parse_strace_file_accesses(
                        [payload], cwd=Path.cwd(), trace_pids=[4242])

    def test_numeric_pid_procfs_cannot_alias_an_sdk_path(self) -> None:
        for path in (
                "/proc/4242/root/original/optix.h",
                "/proc/4242/fd/19",
                "//proc/4242/fd/19"):
            with self.subTest(path=path):
                payload = (
                    f"openat(AT_FDCWD, {json.dumps(path)}, O_RDONLY) = 3\n"
                ).encode("utf-8")
                with self.assertRaisesRegex(RuntimeError, "numeric-PID procfs"):
                    replay.parse_strace_file_accesses(
                        [payload], cwd=Path.cwd(), trace_pids=[4242])

    def test_resolved_numeric_pid_procfs_alias_fails_closed(self) -> None:
        ordinary = Path("ordinary-sdk-alias") / "optix.h"
        payload = (
            f"openat(AT_FDCWD, {json.dumps(str(ordinary))}, O_RDONLY) = 3\n"
        ).encode("utf-8")
        with mock.patch.object(
                Path, "resolve",
                return_value=PurePosixPath(
                    "/proc/4242/root/original/optix.h")):
            with self.assertRaisesRegex(
                    RuntimeError, "resolved strace path.*numeric-PID procfs"):
                replay.parse_strace_file_accesses(
                    [payload], cwd=Path.cwd(), trace_pids=[4242])

    def test_real_symlink_to_dead_numeric_pid_procfs_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            alias = root / "sdk-alias"
            try:
                alias.symlink_to(
                    "/proc/4242/root/original-sdk", target_is_directory=True)
            except OSError as error:
                self.skipTest(f"host cannot create directory symlink: {error}")
            traced_path = alias / "optix.h"
            if not str(traced_path.resolve(strict=False)).startswith(
                    "/proc/4242/"):
                self.skipTest("host does not preserve POSIX procfs target")
            payload = (
                f"openat(AT_FDCWD, {json.dumps(str(traced_path))}, "
                "O_RDONLY) = 3\n"
            ).encode("utf-8")
            with self.assertRaisesRegex(
                    RuntimeError, "strace symlink hop.*numeric-PID procfs"):
                replay.parse_strace_file_accesses(
                    [payload], cwd=root, trace_pids=[4242])

    def test_live_proc_self_fd_symlink_hop_fails_closed(self) -> None:
        if os.name != "posix":
            self.skipTest("POSIX procfs test")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            benign = root / "benign"
            benign.mkdir()
            (benign / "optix.h").write_bytes(b"benign")
            directory_flag = getattr(os, "O_DIRECTORY", 0)
            descriptor = os.open(benign, os.O_RDONLY | directory_flag)
            try:
                alias = root / "ordinary-alias"
                alias.symlink_to(
                    f"/proc/self/fd/{descriptor}", target_is_directory=True)
                traced_path = alias / "optix.h"
                self.assertEqual(
                    traced_path.resolve(strict=True),
                    (benign / "optix.h").resolve(strict=True))
                payload = (
                    f"openat(AT_FDCWD, {json.dumps(str(traced_path))}, "
                    "O_RDONLY) = 3\n"
                ).encode("utf-8")
                with self.assertRaisesRegex(
                        RuntimeError, "strace symlink hop.*procfs magic"):
                    replay.parse_strace_file_accesses(
                        [payload], cwd=root, trace_pids=[4242])
            finally:
                os.close(descriptor)

    def test_dev_fd_alias_is_never_replayed_against_verifier_fd(self) -> None:
        payload = b'openat(AT_FDCWD, "/dev/fd/19", O_RDONLY) = 3\n'
        with self.assertRaisesRegex(RuntimeError, "dynamic /dev fd alias"):
            replay.parse_strace_file_accesses(
                [payload], cwd=Path.cwd(), trace_pids=[4242])


class TraceBoundaryContractTest(unittest.TestCase):
    def test_kernel_target_closes_post_exit_symlink_retarget(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original = root / "original"
            projected = root / "projected"
            original.mkdir()
            projected.mkdir()
            alias = root / "ordinary-alias"
            target = original / "optix.h"
            payload = (
                f"openat(AT_FDCWD<{_trace_escaped(root)}>, "
                f"{json.dumps(str(alias))}, O_RDONLY) = "
                f"3<{_trace_escaped(target)}>\n"
            ).encode("utf-8")
            (root / "trace.301").write_bytes(payload)

            with self.assertRaisesRegex(RuntimeError, "original SDK root"):
                replay._trace_identity_and_accesses(
                    root / "trace", cwd=root, original_roots=[original],
                    projected_roots=[projected], required_projected=[],
                    require_no_original_attempt=True, authority_pid=301)

    def test_any_original_root_attempt_is_rejected_even_when_open_failed(
            self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original = root / "original"
            projected = root / "projected"
            original.mkdir()
            projected.mkdir()
            prefix = root / "trace"
            (root / "trace.301").write_bytes(
                _openat(original / "optix.h", -1))

            with self.assertRaisesRegex(RuntimeError, "original SDK root"):
                replay._trace_identity_and_accesses(
                    prefix, cwd=root, original_roots=[original],
                    projected_roots=[projected], required_projected=[],
                    require_no_original_attempt=True, authority_pid=301)

    def test_required_projected_header_open_is_bound_to_trace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original = root / "original"
            projected = root / "projected"
            original.mkdir()
            projected.mkdir()
            required = projected / "optix.h"
            required.write_bytes(b"header")
            prefix = root / "trace"
            (root / "trace.302").write_bytes(_openat(required, 8))

            result = replay._trace_identity_and_accesses(
                prefix, cwd=root, original_roots=[original],
                projected_roots=[projected], required_projected=[required],
                require_no_original_attempt=True, authority_pid=302)

            self.assertEqual(result["traced_pids"], [302])
            self.assertEqual(result["original_sdk_attempt_count"], 0)
            self.assertEqual(result["projected_sdk_success_count"], 1)
            self.assertIs(
                result["required_projected_headers_observed_successfully"],
                True)

    def test_negative_kat_rejects_unrelated_precompile_failure(self) -> None:
        """Deleting optix.h is causal only if that missing path was attempted."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original = root / "original"
            projected = root / "negative-projection"
            original.mkdir()
            projected.mkdir()
            source = root / "device.cu"
            source.write_bytes(b"source")
            benign = root / "unrelated.py"
            benign.write_bytes(b"pass\n")
            replay_root = root / "replay"

            def fake_run(command, **_kwargs):
                prefix = Path(command[command.index("-o") + 1])
                prefix.with_name(prefix.name + ".701").write_bytes(
                    _openat(benign, 3))
                receipt = Path(command[command.index("--receipt") + 1])
                child_argv = command[command.index("--") + 1:]
                failure = {
                    "schema": "rtdl.goal5802.fresh_nvrtc_compile_failure.v2",
                    "status": "FAIL__FRESH_PROCESS_NVRTC_COMPILE__NO_PRODUCT",
                    "pid": 701,
                    "argv": child_argv[1:],
                    "product_created": False,
                    "error_message": "unrelated Python import failure",
                }
                failure["receipt_sha256"] = replay.digest(failure)
                receipt.write_text(json.dumps(failure), encoding="utf-8")
                return SimpleNamespace(
                    returncode=23, stdout=b"",
                    stderr=b"unrelated Python import failure\n")

            with mock.patch.object(
                    replay.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(
                        RuntimeError, "missing.*optix|optix.*missing"):
                    replay._run_fresh_child(
                        label="negative_missing_optix_h",
                        python=root / "python", strace=root / "strace",
                        child=root / "child.py", source=source,
                        optix_include=projected,
                        cuda_include=projected,
                        compute_capability="8.9", replay_root=replay_root,
                        original_roots=[original],
                        projected_roots=[projected],
                        required_projected=[projected / "optix.h"],
                        expect_success=False)

    def test_header_open_must_belong_to_receipt_process_not_an_unrelated_pid(
            self) -> None:
        """Flattening all trace files must not join two authorities."""

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            original = root / "original"
            projected = root / "projected"
            original.mkdir()
            projected.mkdir()
            required = projected / "optix.h"
            required.write_bytes(b"header")
            benign = root / "benign.py"
            benign.write_bytes(b"pass\n")
            source = root / "device.cu"
            source.write_bytes(b"source")
            replay_root = root / "replay"

            def fake_run(command, **_kwargs):
                prefix = Path(command[command.index("-o") + 1])
                prefix.with_name(prefix.name + ".801").write_bytes(
                    _openat(benign, 3))
                prefix.with_name(prefix.name + ".802").write_bytes(
                    _openat(required, 4))
                output = Path(command[command.index("--output") + 1])
                receipt = Path(command[command.index("--receipt") + 1])
                output.write_bytes(b"synthetic PTX")
                child_argv = command[command.index("--") + 1:]
                product = {
                    "path": str(output.resolve()),
                    "bytes": output.stat().st_size,
                    "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                }
                value = {
                    "schema": "rtdl.goal5802.fresh_nvrtc_compile_child.v2",
                    "status": "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE",
                    "pid": 801,
                    "argv": child_argv[1:],
                    "product": product,
                    "loaded_nvrtc": {"synthetic": True},
                    "clock_read_count": 0,
                    "gpu_kernel_launch_count": 0,
                    "formal_worker_count": 0,
                    "registered_performance_timing_count": 0,
                }
                value["receipt_sha256"] = replay.digest(value)
                receipt.write_text(
                    json.dumps(value), encoding="utf-8")
                return SimpleNamespace(
                    returncode=0, stdout=b"", stderr=b"")

            with mock.patch.object(
                    replay.subprocess, "run", side_effect=fake_run):
                with self.assertRaisesRegex(
                        RuntimeError,
                        "same.*pid|receipt.*pid|process|required header"):
                    replay._run_fresh_child(
                        label="projected", python=root / "python",
                        strace=root / "strace", child=root / "child.py",
                        source=source, optix_include=projected,
                        cuda_include=projected,
                        compute_capability="8.9", replay_root=replay_root,
                        original_roots=[original],
                        projected_roots=[projected],
                        required_projected=[required], expect_success=True)


class SourceBoundaryInspectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parent_path = Path(replay.__file__).resolve()
        cls.child_path = cls.parent_path.with_name(
            "goal5802_nvrtc_compile_child.py")
        cls.parent_source = cls.parent_path.read_text(encoding="utf-8")
        cls.child_source = cls.child_path.read_text(encoding="utf-8")

    def test_replay_parent_has_no_top_level_cuda_or_nvrtc_import(self) -> None:
        tree = ast.parse(self.parent_source)
        imported = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse([
            name for name in imported
            if name == "cuda" or name.startswith("cuda.")
            or "nvrtc" in name.lower()
        ], imported)

    def test_child_compiler_imports_are_lazy_not_module_level(self) -> None:
        tree = ast.parse(self.child_source)
        imported = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse([
            name for name in imported
            if name == "cuda" or name.startswith("cuda.")
            or "nvrtc" in name.lower()
        ], imported)

    def test_child_compiler_does_not_import_a_measured_runtime_arm(self) -> None:
        for forbidden in (
                "pyoptix_baseline", "import cupy", "import optix"):
            self.assertNotIn(forbidden, self.child_source)
        self.assertIn("def _check_nvrtc(", self.child_source)

    def test_negative_kat_source_requires_exact_missing_path_attempt(self) -> None:
        """Source review must find the causal check, not only nonzero exit."""

        function_source = inspect.getsource(replay._run_fresh_child)
        for required in (
                "missing_attempts", "normalized_path", "failure_pid",
                'row["success"] is False', '"optix.h"'):
            self.assertIn(required, function_source)

    def test_trace_document_preserves_pid_for_each_access(self) -> None:
        """A flattened digest cannot prove which PID opened which header."""

        sample = replay.parse_strace_file_accesses(
            [b'openat(AT_FDCWD, "C:\\\\header.h", O_RDONLY) = 3\n'],
            cwd=Path.cwd(), trace_pids=[4242])
        self.assertEqual(sample[0].get("trace_pid"), 4242)

    def test_outer_verifier_binds_trace_files_to_each_run_prefix(self) -> None:
        """Rehashing an arbitrary ``*.PID`` file is not run provenance."""

        source = inspect.getsource(
            replay.validate_matched_ptx_prepare_receipt)
        for required in (
                "expected_command", "trace_prefix.parent",
                "negative_trace_prefix.parent",
                'process.get("cwd") != child_value.get("cwd")'):
            self.assertIn(required, source)

    def test_both_recounts_distinguish_python_invocation_from_binary(self) \
            -> None:
        from experiments.goal5802_premeasurement import independent_recount

        primary = inspect.getsource(
            replay.validate_matched_ptx_prepare_receipt)
        secondary = inspect.getsource(
            independent_recount._validate_fresh_process_replay_independently)
        self.assertGreaterEqual(primary.count('["invocation_path"]'), 2)
        self.assertGreaterEqual(secondary.count('["invocation_path"]'), 2)
        self.assertIn("python_invocation.resolve(strict=True)", secondary)
        self.assertIn('"invocation_path": clean_python["path"]', secondary)

    def test_outer_verifier_binds_child_inputs_to_each_compile_role(self) -> None:
        """A child's self-declared source/include roots are not authority."""

        source = inspect.getsource(
            replay.validate_matched_ptx_prepare_receipt)
        self.assertGreaterEqual(source.count("device_source_sha256"), 2)
        self.assertGreaterEqual(source.count("compaction_source_sha256"), 2)
        self.assertIn("child_source != _file_identity", source)
        self.assertIn(
            "rtdl.goal5802.fresh_nvrtc_compile_child.v2", source)
        self.assertIn(
            "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE", source)

    def test_outer_verifier_binds_negative_child_to_missing_header_role(
            self) -> None:
        """The negative receipt may not choose its own source/root/CC."""

        source = inspect.getsource(
            replay.validate_matched_ptx_prepare_receipt)
        for required in (
                'failure.get("argv") != negative_argv[1:]',
                "failure_source != expected_failure_source",
                "failure_includes != {",
                'failure.get("compute_capability")',
                "any(not _plain_int(failure.get(key))"):
            self.assertIn(required, source)


class ProjectionPathProvenanceTest(unittest.TestCase):
    def test_manifest_rows_use_posix_string_order_for_prefix_collision(
            self) -> None:
        """Real SDKs contain a sibling file whose stem is also a directory."""

        from experiments.goal5802_premeasurement import independent_recount

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "bits" / "types").mkdir(parents=True)
            (root / "bits" / "types.h").write_bytes(b"sibling\n")
            (root / "bits" / "types" / "FILE.h").write_bytes(b"child\n")

            self.assertEqual(
                [row["path"] for row in replay._tree_rows(root)],
                ["bits/types.h", "bits/types/FILE.h"],
            )
            self.assertEqual(
                [row["path"]
                 for row in independent_recount._independent_tree_rows(root)],
                ["bits/types.h", "bits/types/FILE.h"],
            )

    def test_nested_symlink_chain_records_every_followed_link(self) -> None:
        from scripts import goal5802_build_header_projection_untimed as build

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            payload = root / "payload.h"
            payload.write_bytes(b"header")
            second = root / "second-link.h"
            first = root / "first-link.h"
            try:
                second.symlink_to(payload)
                first.symlink_to(second)
            except OSError as error:
                self.skipTest(f"host cannot create test symlinks: {error}")

            rows = build._symlink_chain(first)

            self.assertEqual(
                [row["link_path"] for row in rows],
                [str(first), str(second)],
                "the projection receipt omitted a symlink hop")


if __name__ == "__main__":
    unittest.main()
