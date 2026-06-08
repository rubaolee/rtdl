from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3841_rayjoin_pip_contract_boundary_correction_2026-06-08.md"
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
PARTNER_GUIDE = ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md"


class Goal3841RayJoinPipContractBoundaryCorrectionTest(unittest.TestCase):
    def test_current_version_and_claim_boundary_are_updated(self) -> None:
        self.assertEqual(
            rt.CURRENT_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3842.v1",
        )
        validation = rt.validate_current_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

    def test_spatial_rayjoin_distinguishes_native_pip_packets(self) -> None:
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]
        reading = spatial["current_performance_reading"]
        self.assertIn("Goal3761", reading)
        self.assertIn("Goal3833/3834", reading)
        self.assertIn("bounded 512 public-CDB PIP row", reading)
        self.assertIn("CuPy faster than RTDL/OptiX and Numba", reading)
        self.assertIn("universal PIP-dominance", reading)
        self.assertFalse(spatial["public_speedup_claim_authorized"])
        self.assertFalse(spatial["paper_reproduction_claim_authorized"])

    def test_report_records_no_new_runtime_artifact(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no new runtime artifact", text)
        self.assertIn("bounded 512 public-CDB PIP", text)
        self.assertIn("universal PIP-dominance", text)
        self.assertIn("does not authorize", text)

    def test_learner_docs_carry_same_rayjoin_caveat(self) -> None:
        matrix = MATRIX.read_text(encoding="utf-8")
        partner = PARTNER_GUIDE.read_text(encoding="utf-8")
        self.assertIn("bounded public-CDB PIP scalar-count row", matrix)
        self.assertIn("bounded public-CDB PIP scalar-count row", partner)
        self.assertIn("LSI/overlay scalar-count rows", partner)
        self.assertIn("260x", matrix)
        self.assertIn("260x", partner)


if __name__ == "__main__":
    unittest.main()
