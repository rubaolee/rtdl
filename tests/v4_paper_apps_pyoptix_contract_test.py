from __future__ import annotations

import unittest

from experiments.v4_paper_apps_pyoptix.contracts import APP_SPECS, app_spec
from scripts.build_v4_paper_apps_source_manifest import build_manifest


class V4PaperAppsPyOptixContractTest(unittest.TestCase):
    def test_inventory_is_exactly_nine_and_preserves_all_names(self) -> None:
        self.assertEqual(len(APP_SPECS), 9)
        self.assertEqual(
            {row.app_id for row in APP_SPECS},
            {
                "particle_tracking",
                "triangle_counting",
                "librts",
                "rtnn",
                "x_hd",
                "rt_dbscan",
                "raydb",
                "rayjoin",
                "rt_barneshut",
            },
        )

    def test_first_batch_is_not_the_total_denominator(self) -> None:
        first = {row.app_id for row in APP_SPECS if row.execution_priority == 1}
        self.assertEqual(first, {"particle_tracking", "triangle_counting", "librts"})
        self.assertEqual(len(APP_SPECS), 9)

    def test_recovered_source_manifest_is_fail_closed(self) -> None:
        manifest = build_manifest()
        self.assertEqual(manifest["application_count"], 9)
        self.assertEqual(len(manifest["applications"]), 9)
        self.assertEqual(manifest["file_count"], 134)
        self.assertFalse(manifest["goal5785_final_archive_recovered"])
        self.assertFalse(
            manifest["claim_boundary"]["six_old_historical_authorities_recovered"]
        )
        self.assertTrue(
            manifest["claim_boundary"]["six_sources_available_as_new_candidate_inputs"]
        )
        self.assertEqual(
            app_spec("triangle_counting").selected_operation,
            "RT-2A1 on an official SNAP graph",
        )


if __name__ == "__main__":
    unittest.main()
