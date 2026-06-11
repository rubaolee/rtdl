from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_pod_bootstrap_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal4295_pod_probe_absolute_nvcc_execution_2026-06-11.md"


class Goal4295PodProbeAbsoluteNvccExecutionTest(unittest.TestCase):
    def test_probe_executes_discovered_nvcc_path(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("nvcc_path = _nvcc_path()", source)
        self.assertIn('_run([nvcc_path, "--version"], timeout=10)', source)
        self.assertNotIn('_run(["nvcc", "--version"], timeout=10)', source)

    def test_report_documents_probe_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("executes the exact discovered path", text)
        self.assertIn("does not install CUDA", text)
        self.assertIn("does not authorize release/performance claims", text)


if __name__ == "__main__":
    unittest.main()
