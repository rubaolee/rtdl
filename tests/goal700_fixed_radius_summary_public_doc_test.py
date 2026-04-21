import unittest
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]


class Goal700FixedRadiusSummaryPublicDocTest(unittest.TestCase):
    def test_optix_performance_matrix_mentions_summary_modes_without_reclassifying(self):
        matrix = rt.optix_app_performance_matrix()
        outlier = matrix["outlier_detection"]
        dbscan = matrix["dbscan_clustering"]

        self.assertEqual(outlier.performance_class, "cuda_through_optix")
        self.assertEqual(dbscan.performance_class, "cuda_through_optix")
        self.assertIn("rt_count_threshold", outlier.note)
        self.assertIn("RTX-class measurements are still pending", outlier.note)
        self.assertIn("rt_core_flags", dbscan.note)
        self.assertIn("Python clustering expansion remains outside", dbscan.note)

    def test_public_docs_describe_summary_modes_and_boundaries(self):
        docs = {
            "README.md": ROOT / "README.md",
            "examples/README.md": ROOT / "examples" / "README.md",
            "docs/application_catalog.md": ROOT / "docs" / "application_catalog.md",
            "docs/app_engine_support_matrix.md": ROOT / "docs" / "app_engine_support_matrix.md",
        }
        required_by_doc = {
            "README.md": (
                "rt_count_threshold",
                "rt_core_flags",
                "still require RTX-class performance validation",
            ),
            "examples/README.md": (
                "--optix-summary-mode\n  rt_count_threshold",
                "--optix-summary-mode\n  rt_core_flags",
                "full DBSCAN cluster\n  expansion still needs neighbor connectivity",
            ),
            "docs/application_catalog.md": (
                "optional OptiX `rt_count_threshold`",
                "optional OptiX `rt_core_flags`",
                "They do not imply KNN, Hausdorff, ANN, Barnes-Hut",
            ),
            "docs/app_engine_support_matrix.md": (
                "optional `rt_count_threshold`",
                "optional `rt_core_flags`",
                "RTX-class measurements are still pending",
            ),
        }
        for label, path in docs.items():
            text = path.read_text(encoding="utf-8")
            for phrase in required_by_doc[label]:
                with self.subTest(doc=label, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_apps_still_report_bounded_summary_boundaries(self):
        outlier_payload = __import__("examples.rtdl_outlier_detection_app", fromlist=["run_app"]).run_app()
        dbscan_payload = __import__("examples.rtdl_dbscan_clustering_app", fromlist=["run_app"]).run_app()
        self.assertIn("fixed-radius count prototype", outlier_payload["boundary"])
        self.assertIn("not a KNN/Hausdorff/Barnes-Hut claim", outlier_payload["boundary"])
        self.assertIn("core predicate prototype", dbscan_payload["boundary"])
        self.assertIn("not KNN/Hausdorff/Barnes-Hut", dbscan_payload["boundary"])


if __name__ == "__main__":
    unittest.main()
