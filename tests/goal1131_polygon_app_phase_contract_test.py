import unittest
from unittest import mock

from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


def _candidate_pairs(*_args, **_kwargs):
    return {(1, 10), (2, 11)}


class Goal1131PolygonAppPhaseContractTest(unittest.TestCase):
    def test_pair_summary_reports_candidate_and_continuation_phases(self) -> None:
        payload = pair_app.run_case("embree", copies=2, output_mode="summary")

        self.assertEqual(payload["output_mode"], "summary")
        self.assertNotIn("rows", payload)
        self.assertIn("rt_candidate_discovery_sec", payload["run_phases"])
        self.assertIn("native_exact_continuation_sec", payload["run_phases"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertGreater(payload["candidate_row_count"], 0)

    def test_jaccard_summary_omits_rows_but_keeps_summary(self) -> None:
        rows_payload = jaccard_app.run_case("cpu_python_reference", copies=4, output_mode="rows")
        summary_payload = jaccard_app.run_case("cpu_python_reference", copies=4, output_mode="summary")

        self.assertNotIn("rows", summary_payload)
        self.assertEqual(summary_payload["summary"], rows_payload["rows"][0])
        self.assertEqual(summary_payload["row_count"], rows_payload["row_count"])
        self.assertIn("query_and_materialize_sec", summary_payload["run_phases"])
        self.assertIn("summary_postprocess_sec", summary_payload["run_phases"])

    def test_jaccard_native_assisted_reports_candidate_and_continuation_phases(self) -> None:
        with mock.patch.object(jaccard_app, "_positive_candidate_pairs_optix", side_effect=_candidate_pairs):
            payload = jaccard_app.run_case("optix", copies=1, output_mode="summary")

        self.assertEqual(payload["backend_mode"], "optix_native_assisted")
        self.assertNotIn("rows", payload)
        self.assertEqual(payload["candidate_row_count"], 2)
        self.assertTrue(payload["rt_core_candidate_discovery_active"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("rt_candidate_discovery_sec", payload["run_phases"])
        self.assertIn("native_exact_continuation_sec", payload["run_phases"])

    def test_jaccard_rejects_invalid_output_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_mode"):
            jaccard_app.run_case("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
