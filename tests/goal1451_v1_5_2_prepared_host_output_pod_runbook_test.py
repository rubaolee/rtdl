from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal1451V152PreparedHostOutputPodRunbookTest(unittest.TestCase):
    def test_pod_executor_requires_embree_and_optix_and_records_artifacts(self) -> None:
        script = (
            ROOT
            / "scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("make build-optix", script)
        self.assertIn("--backends embree optix", script)
        self.assertIn("--required-backends embree optix", script)
        self.assertIn("goal1450_pod_environment.log", script)
        self.assertIn("goal1450_make_build_optix.log", script)
        self.assertIn("goal1450_pod_summary.json", script)
        self.assertIn("RTDL_OPTIX_LIB", script)
        self.assertIn("does not authorize true zero-copy", script)

    def test_runbook_keeps_pod_acceptance_and_claim_boundary_precise(self) -> None:
        runbook = (
            ROOT / "docs/handoff/goal1450_pod_runbook_2026-05-07.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Use current `main`", runbook)
        self.assertIn("bash scripts/goal1450_v1_5_2_prepared_host_output_pod_executor.sh", runbook)
        self.assertIn("both Embree and OptiX", runbook)
        self.assertIn("pass=4, fail=0, skipped=0", runbook)
        self.assertIn("Required backend skips: none", runbook)
        self.assertIn("does not authorize true zero-copy wording", runbook)
        self.assertIn("external claim review is still required", runbook)


if __name__ == "__main__":
    unittest.main()
