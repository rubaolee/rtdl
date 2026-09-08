from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest import mock

from rtdsl import v4_rtdlexe


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"
WORKER = ROOT / "scripts/v4_paper_apps_pyoptix_worker.py"


def _load_app():
    spec = importlib.util.spec_from_file_location(
        "v4_long_workload_triangle_rtdlexe_app_test", APP)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TriangleRTDLExecutableAppTest(unittest.TestCase):
    def setUp(self):
        self.app = _load_app()
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.paths = {}
        for name in (
            "artifact", "authority", "trust_root", "trust_head",
            "trust_package", "native",
        ):
            path = root / name
            path.write_bytes((name + " exact bytes").encode("ascii"))
            self.paths[name] = path
        self.hashes = {name: _sha(path) for name, path in self.paths.items()}
        self.executor = SimpleNamespace(close=lambda: None)
        self.graph = SimpleNamespace(expected_triangle_count=29)
        self.loaded = SimpleNamespace(
            artifact_sha256=self.hashes["artifact"],
            authority_sha256=self.hashes["authority"],
            trust_root_sha256=self.hashes["trust_root"],
            trust_package_sha256=self.hashes["trust_package"],
            deployment_id="graph/aot/test",
            family="builtin_triangle_reduction_v1",
            family_executable_identity_sha256="f" * 64,
            product_projection={
                "target_toolchain": {
                    "native_library_sha256": self.hashes["native"],
                },
                "runtime": {"triangle_mode": "weighted_hit_count"},
                "provider_key": {"callback_abi_projection": {
                    "any_hit_proof_sha256": "e" * 64,
                }},
            },
            prepare_triangle_device_columns=mock.Mock(return_value=self.executor),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def _arguments(self):
        return {
            "paper_algorithm": "RT-2A1",
            "native_library_path": self.paths["native"],
            "edge_file": "/input/graph.bin",
            "expected_triangle_count": 29,
            "artifact_path": self.paths["artifact"],
            "authority_path": self.paths["authority"],
            "trust_root_path": self.paths["trust_root"],
            "trust_head_path": self.paths["trust_head"],
            "trust_package_path": self.paths["trust_package"],
            "deployment_id": "graph/aot/test",
            "expected_artifact_sha256": self.hashes["artifact"],
            "expected_authority_sha256": self.hashes["authority"],
            "expected_trust_root_sha256": self.hashes["trust_root"],
            "expected_trust_head_sha256": self.hashes["trust_head"],
            "expected_trust_package_sha256": self.hashes["trust_package"],
            "expected_any_hit_proof_sha256": "e" * 64,
            "expected_family_executable_identity_sha256": "f" * 64,
            "expected_native_sha256": self.hashes["native"],
            "prepared_graph_contract": self.graph,
        }

    def test_signed_artifact_prepares_existing_segmented_owner(self):
        deployment = object()
        with mock.patch.object(
            v4_rtdlexe, "install_rtdlexe_deployment", return_value=deployment
        ) as install, mock.patch.object(
            v4_rtdlexe, "load_rtdlexe", return_value=self.loaded
        ) as load:
            owner = self.app.prepare_v4_segmented_rtdlexe(**self._arguments())
        self.assertIs(owner.executor, self.executor)
        self.assertIs(owner.graph_contract, self.graph)
        self.assertFalse(owner.rtdlexe_lifecycle["compile_in_prepare"])
        self.assertEqual(owner.rtdlexe_lifecycle["triangle_mode"],
                         "weighted_hit_count")
        install.assert_called_once()
        load.assert_called_once()
        self.loaded.prepare_triangle_device_columns.assert_called_once_with(
            native_library_path=self.paths["native"].resolve())

    def test_artifact_bytes_and_mode_mismatch_fail_closed(self):
        arguments = self._arguments()
        arguments["expected_artifact_sha256"] = "0" * 64
        with mock.patch.object(
            v4_rtdlexe, "install_rtdlexe_deployment"
        ) as install, self.assertRaisesRegex(ValueError, "input bytes differ"):
            self.app.prepare_v4_segmented_rtdlexe(**arguments)
        install.assert_not_called()

        arguments = self._arguments()
        self.loaded.product_projection["runtime"]["triangle_mode"] = "all_hit_count"
        with mock.patch.object(
            v4_rtdlexe, "install_rtdlexe_deployment", return_value=object()
        ), mock.patch.object(
            v4_rtdlexe, "load_rtdlexe", return_value=self.loaded
        ), self.assertRaisesRegex(ValueError, "deployment identity differs"):
            self.app.prepare_v4_segmented_rtdlexe(**arguments)

    def test_worker_keeps_dynamic_fallback_and_explicit_aot_gate(self):
        source = WORKER.read_text(encoding="utf-8")
        self.assertIn('rtdlexe = config.get("triangle_rtdlexe")', source)
        self.assertIn("app.prepare_v4_segmented_rtdlexe(", source)
        self.assertIn('"rtdlexe_lifecycle_used": True', source)
        self.assertIn('"restricted_callback_compile_in_complete": False', source)
        self.assertIn("app.prepare_v4_segmented(", source)


if __name__ == "__main__":
    unittest.main()
