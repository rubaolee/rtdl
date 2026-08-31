from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_pod_bootstrap_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal4295_pod_probe_absolute_nvcc_execution_2026-06-11.md"


class Goal4295PodProbeAbsoluteNvccExecutionTest(unittest.TestCase):
    def _load_probe_module(self):
        spec = importlib.util.spec_from_file_location("rtdl_pod_bootstrap_probe_for_goal4295", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_probe_executes_discovered_nvcc_path(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("nvcc_path = _nvcc_path()", source)
        self.assertIn('_run([nvcc_path, "--version"], timeout=10)', source)
        self.assertNotIn('_run(["nvcc", "--version"], timeout=10)', source)

    def test_probe_runtime_uses_discovered_nvcc_path(self) -> None:
        module = self._load_probe_module()

        def fake_which(name: str) -> str | None:
            return {
                "nvidia-smi": "/usr/bin/nvidia-smi",
                "make": "/usr/bin/make",
                "g++": "/usr/bin/g++",
            }.get(name)

        with (
            patch.object(module, "_nvcc_path", return_value="/opt/cuda/bin/nvcc"),
            patch.object(module.shutil, "which", side_effect=fake_which),
            patch.object(module, "_run", return_value={"command": ["/opt/cuda/bin/nvcc", "--version"], "ok": True}),
            patch.object(module, "_module_status", return_value={"module": "stub", "available": True}),
            patch.object(module, "_optix_prefix_status", return_value={"available": True, "selected_prefix": "/opt/optix"}),
            patch.object(module, "_native_library_status", return_value={"available": True, "selected_library": "build/librtdl_optix.so"}),
        ):
            payload = module.probe()

        self.assertEqual("/opt/cuda/bin/nvcc", payload["checks"]["nvcc"]["path"])
        self.assertEqual(["/opt/cuda/bin/nvcc", "--version"], payload["checks"]["nvcc"]["probe"]["command"])
        self.assertEqual("ready", payload["status"])

    def test_report_documents_probe_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("executes the exact discovered path", text)
        self.assertIn("does not install CUDA", text)
        self.assertIn("does not authorize release/performance claims", text)


if __name__ == "__main__":
    unittest.main()
