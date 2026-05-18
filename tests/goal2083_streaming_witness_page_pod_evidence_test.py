from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2081_streaming_witness_page_pod"
REPORT = ROOT / "docs" / "reports" / "goal2083_streaming_witness_page_pod_evidence_2026-05-15.md"


class Goal2083StreamingWitnessPagePodEvidenceTest(unittest.TestCase):
    def _load(self, name: str) -> dict:
        return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))

    def test_pod_artifacts_show_streaming_path_beats_old_full_rows(self) -> None:
        for name in (
            "goal2081_streaming_witness_page_perf_pod_4096_cupy_capacity.json",
            "goal2081_streaming_witness_page_perf_pod_8192_cupy_capacity.json",
            "goal2081_streaming_witness_page_perf_pod_16384_cupy_capacity.json",
        ):
            with self.subTest(name=name):
                artifact = self._load(name)
                self.assertEqual(artifact["status"], "pass")
                new_path = artifact["v2_0_streaming_exact_witness_page_columns"]
                self.assertLess(new_path["ratio_vs_v1_8"], 1.0)
                self.assertLess(new_path["ratio_vs_old_v2_full_rows"], 1.0)
                metadata = new_path["metadata"]
                self.assertEqual(
                    metadata["adapter"],
                    "segment_polygon_exact_witness_pair_page_optix_prepared_partner_columns",
                )
                self.assertEqual(metadata["native_engine_row_contract"], "generic_ray_primitive_candidate_witness_pairs")
                self.assertTrue(metadata["full_python_row_table_materialization_avoided"])
                self.assertFalse(metadata["v2_0_release_authorized"])

    def test_report_keeps_contract_boundary_clear(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("old v2 full Python rows sec", report)
        self.assertIn("new v2 streaming witness columns sec", report)
        self.assertIn("| 16384 |", report)
        self.assertIn("The native engine remains app-agnostic", report)
        self.assertIn("external review is required", report)


if __name__ == "__main__":
    unittest.main()
