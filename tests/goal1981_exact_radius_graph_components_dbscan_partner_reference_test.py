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
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"
REPORT = ROOT / "docs" / "reports" / "goal1981_exact_radius_graph_components_dbscan_partner_reference_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1981_pod_exact_radius_graph_components_dbscan_cupy_perf.json"


class Goal1981ExactRadiusGraphComponentsDbscanPartnerReferenceTest(unittest.TestCase):
    def test_partner_adapter_exposes_radius_graph_components(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def radius_graph_components_2d_partner_columns", adapters)
        self.assertIn("generic_radius_graph_component_labels_2d", adapters)
        self.assertIn("min_neighbors", adapters)
        self.assertIn("component_label_policy", adapters)
        self.assertIn("torch.sum", adapters)
        self.assertIn("cupy.sum", adapters)
        self.assertIn("native_engine_row_contract", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("from .partner_adapters import radius_graph_components_2d_partner_columns", init_text)
        self.assertIn('"radius_graph_components_2d_partner_columns"', init_text)

    def test_dbscan_app_exposes_partner_exact_cluster_mode(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn('"partner_exact_clusters"', text)
        self.assertIn("rt.point_rows_to_partner_columns", text)
        self.assertIn("rt.radius_graph_components_2d_partner_columns", text)
        self.assertIn("generic radius-graph component labels", text)
        self.assertIn("not an RT-core claim", text)

    def test_cpu_reference_path_still_runs(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--copies",
                "1",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "dbscan_clustering")
        self.assertEqual(payload["backend"], "cpu_python_reference")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["cluster_sizes"], {"1": 4, "2": 3})

    def test_report_and_preflight_record_goal1981(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")

        self.assertIn("cluster expansion", report)
        self.assertIn("connected-component labels", report)
        self.assertIn("not DBSCAN inside the native engine", report)
        self.assertIn("0.59596x", report)
        self.assertIn("dense radius-graph labeling", report)
        self.assertIn("goal1981_pod_exact_radius_graph_components_dbscan_cupy_perf.json", report)
        self.assertIn("tests.goal1981_exact_radius_graph_components_dbscan_partner_reference_test", preflight)

    def test_pod_artifact_records_exact_cluster_boundary_and_current_debt(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["exact_partner_reference_path"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertEqual(rows[64]["partner_reference_contract"], "generic_radius_graph_component_labels_2d")
        self.assertTrue(rows[64]["matches_cpu_clusters"])
        self.assertLess(rows[64]["v2_vs_cpu_python_reference_ratio"], 1.0)
        self.assertTrue(rows[512]["matches_oracle"])
        self.assertGreater(rows[512]["v2_partner_exact_cluster_wall_s"]["median_s"], 1.0)


if __name__ == "__main__":
    unittest.main()
