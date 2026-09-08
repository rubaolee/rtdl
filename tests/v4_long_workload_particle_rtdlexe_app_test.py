from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
from types import MappingProxyType, SimpleNamespace
import unittest
from unittest import mock

import numpy as np

from scripts import v4_paper_apps_pyoptix_worker as worker


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = (
    ROOT
    / "Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py"
)


def _load_app():
    name = "particle_rtdlexe_app_test"
    spec = importlib.util.spec_from_file_location(name, APP_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class _Closable:
    def __init__(self) -> None:
        self.closed = 0

    def close(self) -> None:
        self.closed += 1


class ParticleRTDLExecutableAppTest(unittest.TestCase):
    def test_execute_preserves_output_contract_and_compact_receipt(self) -> None:
        app = _load_app()
        output = np.arange(15_000, dtype=np.uint32).reshape(5_000, 3)
        expected = output.copy()
        native_receipt = MappingProxyType({
            "schema_version": 1,
            "optix_launch_count": 1,
            "query_count": 5_000,
        })
        owner = _Closable()
        owner.execute_complete_prevalidated = mock.Mock(return_value=SimpleNamespace(
            output_u32x3=output,
            artifact_sha256="a" * 64,
            ptx_sha256="b" * 64,
            receipt=native_receipt,
        ))
        loaded = _Closable()
        prepared = app.PreparedParticleTrackingV4RTDLExecutable(
            loaded=loaded,
            owner=owner,
            admitted_input=object(),
            expected=expected,
            native_library_sha256="c" * 64,
            total_prepare_seconds=1.25,
        )

        result = prepared.execute()

        digest = hashlib.sha256()
        digest.update(output.dtype.str.encode("ascii"))
        digest.update(str(tuple(output.shape)).encode("ascii"))
        digest.update(memoryview(output).cast("B"))
        expected_digest = digest.hexdigest()
        self.assertEqual(result["output_sha256"], expected_digest)
        self.assertEqual(
            result["traversal_receipt"]["output_digest"], expected_digest)
        self.assertEqual(
            result["traversal_receipt"]["physical_executor_classification"],
            "optix_traversal_observed",
        )
        self.assertEqual(
            result["traversal_receipt"]["native_execution_receipt"],
            dict(native_receipt),
        )
        self.assertEqual(result["native_library_sha256"], "c" * 64)
        self.assertTrue(result["matched"])

        prepared.close()
        prepared.close()
        self.assertEqual(owner.closed, 1)
        self.assertEqual(loaded.closed, 1)
        with self.assertRaisesRegex(RuntimeError, "closed"):
            prepared.execute()

    def test_prepare_uses_public_identity_bound_lifecycle(self) -> None:
        app = _load_app()
        owner = _Closable()
        loaded = _Closable()
        loaded.orientation_authority_sha256 = "e" * 64
        loaded.prepare = mock.Mock(return_value=owner)
        artifact = "a" * 64
        native = "b" * 64
        protocol = "c" * 64
        semantic = "d" * 64
        deployment = object()
        admitted = object()
        data = {
            "vertices": np.zeros((3, 3), dtype=np.float32),
            "triangles": np.zeros((1, 3), dtype=np.uint32),
            "front_values": np.zeros(1, dtype=np.uint32),
            "back_values": np.zeros(1, dtype=np.uint32),
            "queries": np.zeros((5_000, 7), dtype=np.float32),
            "expected": np.zeros((5_000, 3), dtype=np.uint32),
            "input_sha256": "f" * 64,
            "independent_oracle_sha256": "1" * 64,
            "route_independent_expected": True,
        }
        import rtdsl.v4_particle_rtdlexe as public
        import rtdsl.v4_builtin_triangle_standard_library as standard
        orientation = SimpleNamespace(authority_sha256="e" * 64)

        with (
            mock.patch.object(
                public, "install_particle_rtdlexe_deployment",
                return_value=deployment,
            ) as install,
            mock.patch.object(public, "load_particle_rtdlexe", return_value=loaded) as load,
            mock.patch.object(
                public, "prevalidate_particle_rtdlexe_exact_core_input",
                return_value=admitted,
            ) as prevalidate,
            mock.patch.object(standard, "compile_adjacency_callback", return_value=object()),
            mock.patch.object(standard, "make_orientation_authority", return_value=orientation),
        ):
            prepared = app.prepare_v4_rtdlexe(
                native_library_path="/tmp/native.so",
                artifact_path="/tmp/program.rtdlexe",
                deployment_id="successor/particle",
                expected_artifact_sha256=artifact,
                expected_native_sha256=native,
                expected_protocol_decision_sha256=protocol,
                expected_template_semantic_sha256=semantic,
                expected_input_sha256="f" * 64,
                expected_independent_oracle_sha256="1" * 64,
                expected_orientation_authority_sha256="e" * 64,
                prepared_input=data,
            )

        install.assert_called_once_with(
            deployment_id="successor/particle",
            expected_artifact_sha256=artifact,
            expected_native_sha256=native,
            expected_protocol_decision_sha256=protocol,
            expected_template_semantic_sha256=semantic,
        )
        load.assert_called_once_with(
            "/tmp/program.rtdlexe",
            deployment=deployment,
            native_library_path="/tmp/native.so",
        )
        loaded.prepare.assert_called_once()
        prevalidate.assert_called_once()
        prevalidate_args = prevalidate.call_args.args
        prevalidate_expected = prevalidate.call_args.kwargs["expected_u32x3"]
        self.assertEqual(len(prevalidate_args), 7)
        for column in prevalidate_args:
            self.assertEqual(column.shape, (5_000,))
            self.assertEqual(column.dtype, np.dtype("<f4"))
            self.assertTrue(column.flags.owndata)
            self.assertTrue(column.flags.c_contiguous)
            self.assertFalse(column.flags.writeable)
        self.assertEqual(prevalidate_expected.shape, (5_000, 3))
        self.assertEqual(prevalidate_expected.dtype, np.dtype("<u4"))
        self.assertTrue(prevalidate_expected.flags.owndata)
        self.assertTrue(prevalidate_expected.flags.c_contiguous)
        self.assertFalse(prevalidate_expected.flags.writeable)
        self.assertIs(prepared.admitted_input, admitted)
        self.assertEqual(prepared.native_library_sha256, native)
        prepared.close()

    def test_worker_selects_aot_only_from_explicit_exact_config(self) -> None:
        owner = _Closable()
        fake_app = SimpleNamespace(prepare_v4_rtdlexe=mock.Mock(return_value=owner))
        config = {
            "source_root": str(ROOT),
            "native_library_path": "/tmp/native.so",
            "particle_rtdlexe": {
                "artifact_path": "/tmp/program.rtdlexe",
                "deployment_id": "successor/particle",
                "expected_artifact_sha256": "a" * 64,
                "expected_native_sha256": "b" * 64,
                "expected_protocol_decision_sha256": "c" * 64,
                "expected_template_semantic_sha256": "d" * 64,
                "expected_input_sha256": "e" * 64,
                "expected_independent_oracle_sha256": "f" * 64,
                "expected_orientation_authority_sha256": "1" * 64,
            },
        }
        with mock.patch.object(worker, "_load_module", return_value=fake_app):
            _execute, close, metadata = worker._particle_case(
                "v4", config, {"expected": np.zeros((5_000, 3), dtype=np.uint32)}
            )

        self.assertTrue(metadata["rtdlexe_lifecycle_used"])
        self.assertFalse(metadata["restricted_callback_compile_in_complete"])
        self.assertFalse(metadata["arbitrary_user_dsl_generalization_claimed"])
        fake_app.prepare_v4_rtdlexe.assert_called_once()
        close()
        self.assertEqual(owner.closed, 1)

    def test_worker_rejects_extra_aot_config_field(self) -> None:
        config = {
            "source_root": str(ROOT),
            "native_library_path": "/tmp/native.so",
            "particle_rtdlexe": {"unexpected": True},
        }
        with mock.patch.object(
            worker, "_load_module", return_value=SimpleNamespace()
        ):
            with self.assertRaisesRegex(ValueError, "config fields differ"):
                worker._particle_case(
                    "v4", config,
                    {"expected": np.zeros((5_000, 3), dtype=np.uint32)},
                )


if __name__ == "__main__":
    unittest.main()
