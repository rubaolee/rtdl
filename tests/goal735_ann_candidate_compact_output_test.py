import unittest

from examples import rtdl_ann_candidate_app as app


class Goal735AnnCandidateCompactOutputTest(unittest.TestCase):
    def test_default_full_output_preserves_quality_rows(self) -> None:
        payload = app.run_app("cpu_python_reference")

        self.assertEqual(payload["output_mode"], "full")
        self.assertIn("approximate_rows", payload)
        self.assertIn("exact_rows", payload)
        self.assertIn("comparison_rows", payload)
        self.assertEqual(payload["recall_at_1"], 2 / 3)

    def test_rerank_summary_omits_quality_work_and_rows(self) -> None:
        payload = app.run_app("cpu_python_reference", copies=16, output_mode="rerank_summary")

        self.assertEqual(payload["output_mode"], "rerank_summary")
        self.assertEqual(payload["query_count"], 48)
        self.assertEqual(payload["approximate_row_count"], 48)
        self.assertNotIn("approximate_rows", payload)
        self.assertNotIn("exact_rows", payload)
        self.assertNotIn("comparison_rows", payload)
        self.assertNotIn("recall_at_1", payload)

    def test_quality_summary_omits_rows_but_preserves_metrics(self) -> None:
        payload = app.run_app("cpu_python_reference", copies=4, output_mode="quality_summary")

        self.assertEqual(payload["output_mode"], "quality_summary")
        self.assertIn("recall_at_1", payload)
        self.assertIn("mean_distance_ratio", payload)
        self.assertNotIn("approximate_rows", payload)
        self.assertNotIn("exact_rows", payload)
        self.assertNotIn("comparison_rows", payload)

    def test_embree_rerank_summary_matches_cpu_reference(self) -> None:
        expected = app.run_app("cpu_python_reference", copies=64, output_mode="rerank_summary")
        actual = app.run_app("embree", copies=64, output_mode="rerank_summary")

        self.assertEqual(actual["approximate_row_count"], expected["approximate_row_count"])
        self.assertEqual(actual["query_count_with_candidate"], expected["query_count_with_candidate"])
        self.assertEqual(actual["max_neighbor_rank"], expected["max_neighbor_rank"])

    def test_rejects_invalid_output_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_mode"):
            app.run_app("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
