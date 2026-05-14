from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_dbscan_clustering_app.py"
REPORT = ROOT / "docs" / "reports" / "goal1985_spatial_bucket_dbscan_partner_reference_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1985_pod_spatial_bucket_dbscan_cupy_perf.json"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
ANALYSIS_SCRIPT = ROOT / "scripts" / "goal1931_current_all_app_v18_v2_perf_analysis.py"


class Goal1985SpatialBucketDbscanPartnerReferenceTest(unittest.TestCase):
    def test_adapter_and_exports_record_spatial_bucket_boundary(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def radius_graph_components_2d_spatial_bucket_partner_columns", adapters)
        self.assertIn("generic_spatial_bucket_radius_graph_component_labels_2d", adapters)
        self.assertIn("host_bucket_index_used", adapters)
        self.assertIn("direct_device_handoff_authorized", adapters)
        self.assertIn("from .partner_adapters import radius_graph_components_2d_spatial_bucket_partner_columns", init_text)
        self.assertIn('"radius_graph_components_2d_spatial_bucket_partner_columns"', init_text)

    def test_dbscan_app_exposes_spatial_bucket_mode_and_skip_validation(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_spatial_exact_clusters"', text)
        self.assertIn("radius_graph_components_2d_spatial_bucket_partner_columns", text)
        self.assertIn("--skip-validation", text)
        self.assertIn("host-built sparse bucket index", text)
        self.assertIn("not a true zero-copy claim", text)

    def test_cpu_reference_path_still_runs(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(EXAMPLE), "--backend", "cpu_python_reference", "--copies", "1"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "dbscan_clustering")
        self.assertTrue(payload["matches_oracle"])
        self.assertFalse(payload["validation_skipped"])

    def test_report_preflight_and_analysis_record_goal1985(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        analysis_script = ANALYSIS_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("0.25631x", report)
        self.assertIn("not yet true zero-copy", report)
        self.assertIn("O(n^2) Python oracle", report)
        self.assertIn("goal1985_pod_spatial_bucket_dbscan_cupy_perf.json", report)
        self.assertIn("tests.goal1985_spatial_bucket_dbscan_partner_reference_test", preflight)
        self.assertIn("_goal1985_spatial_bucket_dbscan_rows", analysis_script)

    def test_pod_artifact_records_sparse_speedup_and_claim_boundary(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["exact_partner_reference_path"])
        self.assertTrue(payload["claim_boundary"]["host_bucket_index_used"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertEqual(rows[64]["partner_reference_contract"], "generic_spatial_bucket_radius_graph_component_labels_2d")
        self.assertTrue(rows[64]["validation_matches_oracle"])
        self.assertLess(rows[64]["spatial_vs_dense_exact_ratio"], 0.30)
        self.assertLess(rows[512]["spatial_vs_dense_exact_ratio"], 0.27)
        self.assertEqual(rows[4096]["point_count"], 32768)
        self.assertEqual(rows[4096]["candidate_edge_count"], 36864)


if __name__ == "__main__":
    unittest.main()
