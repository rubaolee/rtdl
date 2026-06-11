from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_pod_bootstrap_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal4293_pod_probe_cuda_prefix_nvcc_2026-06-11.md"


class Goal4293PodProbeCudaPrefixNvccTest(unittest.TestCase):
    def test_probe_checks_cuda_prefix_candidates_for_nvcc(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("CUDA_PREFIX_CANDIDATES", source)
        self.assertIn('Path("/usr/local/cuda-12.8")', source)
        self.assertIn('candidate = prefix / "bin" / "nvcc"', source)
        self.assertIn("nvcc_path = _nvcc_path()", source)

    def test_report_records_probe_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("/usr/local/cuda-12.8/bin/nvcc", text)
        self.assertIn("does not install CUDA", text)
        self.assertIn("authorize release/performance claims", text)


if __name__ == "__main__":
    unittest.main()
