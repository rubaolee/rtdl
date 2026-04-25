import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from examples import rtdl_graph_analytics_app as graph_app


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal889_graph_visibility_optix_gate.py"


class Goal889GraphVisibilityOptixGateTest(unittest.TestCase):
    def test_graph_app_visibility_edges_cpu_summary(self) -> None:
        payload = graph_app.run_app("cpu_python_reference", "visibility_edges", copies=1, output_mode="summary")
        section = payload["sections"]["visibility_edges"]
        self.assertEqual(section["row_count"], 4)
        self.assertIn("visible_edge_count", section["summary"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("visibility_edges is an OptiX", payload["honesty_boundary"])
        self.assertIn("native graph-ray mode remains gated", payload["honesty_boundary"])

    def test_require_rt_core_all_still_rejects_bfs_triangle_count(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "limited to --scenario visibility_edges"):
            graph_app.run_app("optix", "all", require_rt_core=True)

    def test_non_strict_gate_records_missing_optix_without_failing(self) -> None:
        from scripts import goal889_graph_visibility_optix_gate as goal889

        with mock.patch.object(
            goal889.graph_app,
            "run_app",
            side_effect=[
                RuntimeError("no optix"),
                RuntimeError("no optix"),
                RuntimeError("no optix"),
            ],
        ):
            payload = goal889.run_gate(copies=1, output_mode="summary", strict=False)
        self.assertEqual(payload["status"], "non_strict_recorded_gaps")
        self.assertFalse(payload["strict_pass"])
        self.assertIn("optix_visibility_anyhit did not run", payload["strict_failures"])
        self.assertIn("optix_native_graph_ray_bfs did not run", payload["strict_failures"])
        self.assertIn("optix_native_graph_ray_triangle_count did not run", payload["strict_failures"])

    def test_strict_passes_when_optix_matches_cpu_digest(self) -> None:
        from scripts import goal889_graph_visibility_optix_gate as goal889

        cpu_visibility = graph_app.run_app("cpu_python_reference", "visibility_edges", copies=1, output_mode="summary")
        cpu_bfs = graph_app.run_app("cpu_python_reference", "bfs", copies=1, output_mode="summary")
        cpu_triangle = graph_app.run_app("cpu_python_reference", "triangle_count", copies=1, output_mode="summary")
        with mock.patch.object(
            goal889.graph_app,
            "run_app",
            side_effect=[
                cpu_visibility,
                cpu_bfs,
                cpu_triangle,
                cpu_visibility,
                cpu_bfs,
                cpu_triangle,
            ],
        ):
            payload = goal889.run_gate(
                copies=1,
                output_mode="summary",
                strict=True,
                validation_mode="full_reference",
            )
        self.assertEqual(payload["status"], "pass")
        optix_records = [record for record in payload["records"] if str(record["label"]).startswith("optix_")]
        self.assertEqual(len(optix_records), 3)
        self.assertTrue(all(record["parity_vs_cpu_python_reference"] for record in optix_records))
        self.assertEqual(optix_records[1]["optix_graph_mode"], "native")
        self.assertEqual(optix_records[2]["optix_graph_mode"], "native")

    def test_summary_strict_uses_analytic_validation_without_cpu_reference(self) -> None:
        from scripts import goal889_graph_visibility_optix_gate as goal889

        optix_visibility = graph_app.run_app("cpu_python_reference", "visibility_edges", copies=1, output_mode="summary")
        optix_bfs = graph_app.run_app("cpu_python_reference", "bfs", copies=1, output_mode="summary")
        optix_triangle = graph_app.run_app("cpu_python_reference", "triangle_count", copies=1, output_mode="summary")
        with mock.patch.object(
            goal889.graph_app,
            "run_app",
            side_effect=[optix_visibility, optix_bfs, optix_triangle],
        ) as mocked:
            payload = goal889.run_gate(
                copies=1,
                output_mode="summary",
                strict=True,
                validation_mode="analytic_summary",
                chunk_copies=1,
            )
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(mocked.call_count, 3)
        labels = {record["label"] for record in payload["records"]}
        self.assertIn("analytic_expected_visibility_edges", labels)
        self.assertIn("analytic_expected_bfs", labels)
        self.assertIn("analytic_expected_triangle_count", labels)
        optix_records = [record for record in payload["records"] if str(record["label"]).startswith("optix_")]
        self.assertTrue(all(record["parity_vs_analytic_expected"] for record in optix_records))

    def test_cli_writes_non_strict_json(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "build") as tmpdir:
            output = Path(tmpdir) / "graph.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--copies",
                    "1",
                    "--output-mode",
                    "summary",
                    "--output-json",
                    str(output.relative_to(ROOT)),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            summary = json.loads(completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(summary["output_json"], str(output.relative_to(ROOT)))
            self.assertIn(payload["status"], {"pass", "non_strict_recorded_gaps"})
            self.assertIn("cloud_claim_contract", payload)
            labels = {record["label"] for record in payload["records"]}
            self.assertIn("optix_native_graph_ray_bfs", labels)
            self.assertIn("optix_native_graph_ray_triangle_count", labels)


if __name__ == "__main__":
    unittest.main()
