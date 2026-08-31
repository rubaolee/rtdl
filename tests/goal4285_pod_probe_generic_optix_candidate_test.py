from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_pod_bootstrap_probe.py"
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_pod_bootstrap_probe.md"
REPORT = ROOT / "docs" / "reports" / "goal4285_pod_probe_generic_optix_candidate_2026-06-11.md"


class Goal4285PodProbeGenericOptixCandidateTest(unittest.TestCase):
    def test_probe_has_no_developer_specific_optix_candidate(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        runbook = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn('Path.home() / "vendor" / "optix-dev"', source)
        self.assertIn("/workspace/vendor/optix-sdk", source)
        self.assertIn("/workspace/vendor/optix-dev", source)
        self.assertNotIn("/home/lestat/vendor/optix-dev", source)
        self.assertNotIn("/home/lestat/vendor/optix-dev", runbook)

    def test_report_records_non_authorizing_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4285", text)
        self.assertIn("does not install OptiX", text)
        self.assertIn("authorize any performance claim", text)


if __name__ == "__main__":
    unittest.main()
