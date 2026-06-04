import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3242_rtdl_rayjoin_count_contract_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3242_rtdl_rayjoin_count_contract_probe_2026-06-03.json"


class Goal3242RtdlRayJoinCountContractProbeTest(unittest.TestCase):
    def test_report_frames_count_contract_without_claims(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "fairer count-contract",
            "prepared_optix",
            "segment/segment intersection count",
            "point/shape positive-hit count",
            "269 intersections",
            "1430 positive assignments",
            "optimization target, not a release claim",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_counts_and_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass_with_optimization_gap")
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))
        routes = {(row["case"], row["route"]): row for row in data["rtdl_count_routes"]}
        self.assertEqual(routes[("lsi_county256_soil256_count512", "prepared_optix")]["row_count"], 269)
        self.assertEqual(routes[("pip_county512", "prepared_optix")]["positive_assignment_count"], 1430)
        self.assertGreater(
            routes[("lsi_county256_soil256_count512", "prepared_optix")]["query_sec"],
            0.001,
        )
        rayjoin = {(row["case"], row["mode"]): row for row in data["rayjoin_query_exec_smokes_from_goal3239"]}
        self.assertEqual(rayjoin[("lsi_county256_soil256_count512", "rt")]["intersections"], 269)
        self.assertFalse(rayjoin[("pip_county512", "rt")]["positive_assignment_count_available"])


if __name__ == "__main__":
    unittest.main()
