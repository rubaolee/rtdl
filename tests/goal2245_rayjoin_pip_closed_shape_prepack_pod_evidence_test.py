import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2245_rayjoin_pip_closed_shape_prepack_pod_evidence_2026-05-17.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2245_rayjoin_pip_closed_shape_prepack_same_query_pod_2026-05-17.json"


class Goal2245RayjoinPipClosedShapePrepackPodEvidenceTest(unittest.TestCase):
    def test_artifact_records_closed_shape_prepack_path(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        optix = data["backends"]["optix"]

        self.assertEqual(data["commit"], "f0e2583019c62326a28ce59cbedc3d59ea2dbdcb")
        self.assertEqual(data["query_count"], 100000)
        self.assertEqual(optix["implementation_path"], "closed_shape_membership_2d_optix")
        self.assertEqual(optix["input_preparation_path"], "prepacked_points_and_shapes_once_per_run_stream")
        self.assertTrue(optix["uses_generic_closed_shape_membership"])
        self.assertTrue(optix["all_parity_vs_reference"])
        self.assertTrue(optix["row_count_consistent"])
        self.assertEqual(set(optix["row_counts"]), {8686})
        self.assertLess(optix["elapsed_sec_median"], 0.1)

    def test_claim_boundary_remains_narrow(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["claim_boundary"]

        self.assertTrue(boundary["same_contract_with_rayjoin_query_exec"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])

    def test_report_explains_design_lesson(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("repeated Python packing", text)
        self.assertIn("prepack stable inputs once", text)
        self.assertIn("native engine: closed-shape membership", text)
        self.assertIn("does not authorize", text)


if __name__ == "__main__":
    unittest.main()
