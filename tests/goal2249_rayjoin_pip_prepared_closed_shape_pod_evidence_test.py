import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2249_rayjoin_pip_prepared_closed_shape_pod_evidence_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2249_rayjoin_pip_prepared_closed_shape_same_query_pod_2026-05-17.json"


class Goal2249RayjoinPipPreparedClosedShapePodEvidenceTest(unittest.TestCase):
    def test_artifact_records_prepared_closed_shape_path(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        optix = data["backends"]["optix"]

        self.assertEqual(data["commit"], "9e8c60ef6ae6a1311940b76861fc9a665a52dcc5")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(data["reference_row_count"], 8686)
        self.assertEqual(optix["implementation_path"], "prepared_closed_shape_membership_2d_optix")
        self.assertEqual(
            optix["input_preparation_path"],
            "prepared_shape_scene_and_prepacked_points_once_per_run_stream",
        )
        self.assertTrue(optix["uses_generic_closed_shape_membership"])
        self.assertTrue(optix["all_parity_vs_reference"])
        self.assertTrue(optix["row_count_consistent"])
        self.assertEqual(set(optix["row_counts"]), {8686})
        self.assertLess(optix["elapsed_sec_median"], 0.07)

    def test_prepared_path_improves_goal2245_same_query_measurement(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        median = data["backends"]["optix"]["elapsed_sec_median"]
        goal2245_median = 0.08343074284493923

        self.assertLess(median, goal2245_median)
        self.assertLess(median / goal2245_median, 0.8)

    def test_claim_boundary_remains_narrow(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["claim_boundary"]

        self.assertTrue(boundary["same_contract_with_rayjoin_query_exec"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])

    def test_report_explains_prepared_scene_lesson(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("prepared-scene contract", text)
        self.assertIn("not RayJoin logic", text)
        self.assertIn("1.31x faster than Goal2245", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
