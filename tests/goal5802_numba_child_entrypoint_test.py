from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import unittest
from pathlib import Path
from unittest import mock

from rtdsl.v4_callback_ir import CallbackRole
from rtdsl import v4_callback_numba_codegen as codegen


class Goal5802NumbaChildEntrypointTest(unittest.TestCase):
    @staticmethod
    def leaf(
        role: CallbackRole = CallbackRole.MAKE_RAY,
        *,
        abi_name: str = "rtdl_v4_goal5802_child_test",
    ) -> codegen.GeneratedFormalNumbaLeaf:
        source = f"def {abi_name}():\n    return\n"
        return codegen.GeneratedFormalNumbaLeaf(
            schema=codegen.FORMAL_NUMBA_SOURCE_SCHEMA,
            role=role,
            abi_name=abi_name,
            parameter_order=(),
            parameter_types=(),
            generated_source=source,
            generated_source_sha256=hashlib.sha256(
                source.encode("utf-8")
            ).hexdigest(),
            callback_ir_sha256="1" * 64,
            callback_effect_digest="2" * 64,
            callback_abi_sha256="3" * 64,
            nonce_word=17,
            numeric_mode="strict",
            error_sites=(),
            compiler_function_count=1,
        )

    @staticmethod
    def compile_arguments() -> dict[str, object]:
        return {
            "compute_capability": (6, 1),
            "accepted_ptx_isa": ("8.0", "8.9"),
            "allowed_external_symbols": frozenset(),
            "expected_python_version": platform.python_version(),
            "expected_numba_version": "0.65.1",
            "expected_numpy_version": "2.4.4",
            "python_executable": os.fspath(Path(sys.executable).resolve()),
        }

    def assert_direct_child_invocation(
        self,
        invocation: mock._Call,
        *,
        stdout: str,
        stderr: str,
    ) -> None:
        argv = invocation.args[0]
        kwargs = invocation.kwargs
        expected_child = Path(codegen.__file__).with_name(
            "_v4_numba_compile_child.py"
        ).resolve(strict=True)

        self.assertEqual(
            argv[:4],
            [self.compile_arguments()["python_executable"], "-s", "-B", "-P"],
        )
        self.assertEqual(Path(argv[-3]), expected_child)
        self.assertEqual(Path(argv[-2]).name, "request.json")
        self.assertEqual(Path(argv[-1]).name, "response.json")
        self.assertNotIn("-m", argv)
        self.assertNotIn("rtdsl._v4_numba_compile_child", argv)
        self.assertEqual(
            [item for item in argv if item.endswith("_v4_numba_compile_child.py")],
            [os.fspath(expected_child)],
        )

        self.assertTrue(kwargs["capture_output"])
        self.assertTrue(kwargs["text"])
        self.assertFalse(kwargs["check"])
        normalized_environment = {
            key.upper(): value for key, value in kwargs["env"].items()
        }
        self.assertEqual(
            {
                key: value
                for key, value in normalized_environment.items()
                if key.startswith("PYTHON")
            },
            {
                "PYTHONHASHSEED": "0",
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONSAFEPATH": "1",
            },
        )
        self.assertEqual(normalized_environment["GOAL5802_KEEP_ME"], "retained")
        self.assertEqual(stdout, "child-stdout\n")
        self.assertEqual(stderr, "child-stderr\n")

    @staticmethod
    def failing_child() -> mock.Mock:
        def fail(argv, **kwargs):
            if not Path(argv[-2]).is_file():
                raise AssertionError("request was not materialized before child spawn")
            if Path(argv[-2]).parent != Path(argv[-1]).parent:
                raise AssertionError("request and response escaped their closed root")
            return mock.Mock(
                returncode=23,
                stdout="child-stdout\n",
                stderr="child-stderr\n",
            )

        return mock.Mock(side_effect=fail)

    @staticmethod
    def successful_child() -> mock.Mock:
        def response_for(item: dict[str, object]) -> dict[str, object]:
            abi_name = str(item["abi_name"])
            ptx = (
                ".version 8.0\n"
                ".target sm_61\n"
                ".address_size 64\n"
                f".visible .func {abi_name}() {{\n    ret;\n}}\n"
            )
            return {
                "schema": "rtdl.v4.numba_compile_response.v1",
                "generated_source_sha256": item["generated_source_sha256"],
                "ptx": ptx,
                "numba_version": "0.65.1",
                "numpy_version": "2.4.4",
                "python_version": platform.python_version(),
                "cuda_available_was_queried": False,
                "explicit_compute_capability": [6, 1],
            }

        def succeed(argv, **kwargs):
            request_path = Path(argv[-2])
            response_path = Path(argv[-1])
            request = json.loads(request_path.read_text(encoding="utf-8"))
            if request["schema"] \
                    == "rtdl.v4.generated_formal_numba_leaf_batch.v1":
                response = {
                    "schema": "rtdl.v4.numba_compile_batch_response.v1",
                    "responses": [
                        response_for(item) for item in request["requests"]
                    ],
                }
            else:
                response = response_for(request)
            response_path.write_text(json.dumps(response), encoding="utf-8")
            return mock.Mock(returncode=0, stdout="", stderr="")

        return mock.Mock(side_effect=succeed)

    def hostile_environment(self) -> dict[str, str]:
        return {
            "PYTHONPATH": "attacker-path",
            "PythonHome": "attacker-home",
            "PyThOnStartup": "attacker-startup",
            "PYTHONHASHSEED": "attacker-seed",
            "PYTHONNOUSERSITE": "0",
            "PYTHONDONTWRITEBYTECODE": "0",
            "PYTHONSAFEPATH": "0",
            "GOAL5802_KEEP_ME": "retained",
        }

    def test_single_uses_resolved_source_child_and_sanitized_environment(self):
        runner = self.failing_child()
        with mock.patch.dict(
            os.environ, self.hostile_environment(), clear=True
        ), mock.patch.object(codegen.subprocess, "run", runner):
            with self.assertRaises(codegen.CallbackCodegenError) as caught:
                codegen.compile_formal_numba_leaf_isolated(
                    self.leaf(), **self.compile_arguments()
                )

        self.assertEqual(caught.exception.code, "isolated_numba_compile")
        self.assertIn("child-stdout\n", caught.exception.message)
        self.assertIn("child-stderr\n", caught.exception.message)
        runner.assert_called_once()
        self.assert_direct_child_invocation(
            runner.call_args,
            stdout=caught.exception.message.split("stdout:\n", 1)[1]
            .split("\nstderr:\n", 1)[0],
            stderr=caught.exception.message.split("\nstderr:\n", 1)[1],
        )

    def test_batch_uses_resolved_source_child_and_sanitized_environment(self):
        runner = self.failing_child()
        leaves = (
            self.leaf(),
            self.leaf(
                CallbackRole.INTERSECTION,
                abi_name="rtdl_v4_goal5802_child_test_intersect",
            ),
        )
        with mock.patch.dict(
            os.environ, self.hostile_environment(), clear=True
        ), mock.patch.object(codegen.subprocess, "run", runner):
            with self.assertRaises(codegen.CallbackCodegenError) as caught:
                codegen.compile_formal_numba_leaves_isolated(
                    leaves, **self.compile_arguments()
                )

        self.assertEqual(caught.exception.code, "isolated_numba_compile_batch")
        self.assertIn("child-stdout\n", caught.exception.message)
        self.assertIn("child-stderr\n", caught.exception.message)
        runner.assert_called_once()
        self.assert_direct_child_invocation(
            runner.call_args,
            stdout=caught.exception.message.split("stdout:\n", 1)[1]
            .split("\nstderr:\n", 1)[0],
            stderr=caught.exception.message.split("\nstderr:\n", 1)[1],
        )

    def test_single_and_batch_success_responses_return_audited_artifacts(self):
        runner = self.successful_child()
        first = self.leaf()
        second = self.leaf(
            CallbackRole.INTERSECTION,
            abi_name="rtdl_v4_goal5802_child_test_intersection",
        )
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            codegen.subprocess, "run", runner
        ):
            single = codegen.compile_formal_numba_leaf_isolated(
                first, **self.compile_arguments()
            )
            batch = codegen.compile_formal_numba_leaves_isolated(
                (first, second), **self.compile_arguments()
            )

        self.assertEqual(runner.call_count, 2)
        self.assertEqual(single.abi_name, first.abi_name)
        self.assertEqual(single.generated_source_sha256, first.generated_source_sha256)
        self.assertEqual([artifact.abi_name for artifact in batch], [
            first.abi_name,
            second.abi_name,
        ])
        self.assertEqual([artifact.role for artifact in batch], [
            CallbackRole.MAKE_RAY.value,
            CallbackRole.INTERSECTION.value,
        ])
        self.assertTrue(all(artifact.ptx_sha256 for artifact in (single, *batch)))

    def test_symlink_child_fails_closed_before_single_spawn(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            Path, "is_symlink", return_value=True
        ), mock.patch.object(codegen.subprocess, "run") as runner:
            with self.assertRaises(codegen.CallbackCodegenError) as caught:
                codegen.compile_formal_numba_leaf_isolated(
                    self.leaf(), **self.compile_arguments()
                )

        self.assertEqual(caught.exception.code, "isolated_numba_compile_child")
        self.assertEqual(caught.exception.message, "symlink forbidden")
        runner.assert_not_called()

    def test_missing_child_fails_closed_before_batch_spawn(self):
        original_resolve = Path.resolve
        expected_child_name = "_v4_numba_compile_child.py"

        def fail_only_for_child(path: Path, *args, **kwargs):
            if path.name == expected_child_name:
                raise FileNotFoundError(os.fspath(path))
            return original_resolve(path, *args, **kwargs)

        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            Path, "resolve", autospec=True, side_effect=fail_only_for_child
        ), mock.patch.object(codegen.subprocess, "run") as runner:
            with self.assertRaises(codegen.CallbackCodegenError) as caught:
                codegen.compile_formal_numba_leaves_isolated(
                    (self.leaf(),), **self.compile_arguments()
                )

        self.assertEqual(caught.exception.code, "isolated_numba_compile_child")
        self.assertEqual(caught.exception.message, "child is absent")
        runner.assert_not_called()

    def test_nonregular_child_fails_closed_before_spawn(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            Path, "is_file", return_value=False
        ), mock.patch.object(codegen.subprocess, "run") as runner:
            with self.assertRaises(codegen.CallbackCodegenError) as caught:
                codegen.compile_formal_numba_leaf_isolated(
                    self.leaf(), **self.compile_arguments()
                )

        self.assertEqual(caught.exception.code, "isolated_numba_compile_child")
        self.assertEqual(caught.exception.message, "child is not a regular file")
        runner.assert_not_called()


if __name__ == "__main__":
    unittest.main()
