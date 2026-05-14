from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2037_v2_embree_cpu_partner_all_thread_plan_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2037_v2_embree_cpu_partner_all_thread_plan_2026-05-14.json"


class Goal2037V2EmbreeCpuPartnerAllThreadPlanTest(unittest.TestCase):
    def test_report_defines_cpu_partner_architecture_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Embree engine on local Linux using all available CPU threads", text)
        self.assertIn("NumPy", text)
        self.assertIn("Torch-CPU", text)
        self.assertIn("Numba-CPU", text)
        self.assertIn("**Python C extension** only as an interoperability demonstration", text)
        self.assertIn("must not claim", text)
        self.assertIn("v2.0 release readiness", text)

    def test_report_requires_all_thread_progress_and_artifacts(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for token in (
            "OMP_NUM_THREADS",
            "TBB_NUM_THREADS",
            "MKL_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "per-row timeouts",
            "Print progress",
            "Save partial artifacts",
        ):
            self.assertIn(token, text)

    def test_json_blocks_release_claims_and_names_partner_choices(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["goal"], "Goal2037")
        self.assertEqual(payload["initial_verdict"], "needs-implementation")
        self.assertIn("numpy", payload["default_cpu_partners"])
        self.assertIn("torch_cpu", payload["default_cpu_partners"])
        self.assertIn("numba_cpu", payload["conditional_cpu_partners"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_host_zero_copy_for_every_row_authorized"])
        self.assertFalse(payload["claim_boundary"]["triton_numba_public_backend_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
