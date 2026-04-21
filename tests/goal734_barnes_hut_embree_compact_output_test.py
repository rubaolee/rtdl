import unittest

from examples import rtdl_barnes_hut_force_app as app


class Goal734BarnesHutEmbreeCompactOutputTest(unittest.TestCase):
    def test_default_full_output_remains_oracle_checked(self) -> None:
        payload = app.run_app("cpu_python_reference")

        self.assertEqual(payload["output_mode"], "full")
        self.assertIn("candidate_rows", payload)
        self.assertIn("force_rows", payload)
        self.assertIn("exact_force_rows", payload)
        self.assertLess(payload["max_relative_error"], 0.01)

    def test_candidate_summary_omits_heavy_rows(self) -> None:
        payload = app.run_app("cpu_python_reference", body_count=64, output_mode="candidate_summary")

        self.assertEqual(payload["output_mode"], "candidate_summary")
        self.assertEqual(payload["body_count"], 64)
        self.assertGreater(payload["candidate_row_count"], 0)
        self.assertNotIn("candidate_rows", payload)
        self.assertNotIn("force_rows", payload)
        self.assertNotIn("exact_force_rows", payload)

    def test_embree_candidate_summary_matches_cpu_reference(self) -> None:
        expected = app.run_app("cpu_python_reference", body_count=128, output_mode="candidate_summary")
        actual = app.run_app("embree", body_count=128, output_mode="candidate_summary")

        self.assertEqual(actual["candidate_row_count"], expected["candidate_row_count"])
        self.assertEqual(actual["body_count_with_candidates"], expected["body_count_with_candidates"])
        self.assertEqual(actual["node_count_seen"], expected["node_count_seen"])

    def test_force_summary_omits_exact_oracle_rows(self) -> None:
        payload = app.run_app("embree", body_count=128, output_mode="force_summary")

        self.assertEqual(payload["output_mode"], "force_summary")
        self.assertGreater(payload["force_row_count"], 0)
        self.assertNotIn("candidate_rows", payload)
        self.assertNotIn("exact_force_rows", payload)
        self.assertNotIn("error_rows", payload)

    def test_rejects_invalid_options(self) -> None:
        with self.assertRaisesRegex(ValueError, "body_count must be positive"):
            app.run_app("cpu_python_reference", body_count=0, output_mode="candidate_summary")
        with self.assertRaisesRegex(ValueError, "output_mode"):
            app.run_app("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
