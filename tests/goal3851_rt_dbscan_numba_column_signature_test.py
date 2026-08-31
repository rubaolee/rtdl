from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples/current/research_benchmarks/rt_dbscan/README.md"
REPORT = ROOT / "docs/reports/goal3851_rt_dbscan_numba_column_signature_2026-06-08.md"
OLD_ARTIFACT = (
    ROOT
    / "docs/reports/goal3850_post_aabb_full_scale_refresh_a5000"
    / "outputs"
    / "rt_dbscan_optix_numba_scale_default_65536_no_validation.stdout.json"
)
ARTIFACT_DIR = ROOT / "docs/reports/goal3851_rt_dbscan_numba_column_signature_a5000"
DIRECT_ARTIFACT = ARTIFACT_DIR / "rt_dbscan_optix_numba_column_signature_65k.json"
RUNNER_SUMMARY = ARTIFACT_DIR / "scale_profile_summary.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3851RtDbscanNumbaColumnSignatureTest(unittest.TestCase):
    def test_app_exposes_numba_column_signature_mode_without_native_dbscan(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("optix_rt_core_flags_numba_prepared_grid_column_signature_3d", text)
        self.assertIn("partner_column_arrays_no_python_row_dicts", text)
        self.assertIn("prepared_query_repeat_protocol", text)
        self.assertIn("materializes_python_rows", text)
        self.assertIn("rt.fixed_radius_count_threshold_3d_optix_prepared_partner_device_columns", text)
        self.assertIn("rt.radius_graph_components_3d_numba_prepared_grid_partner_columns", text)
        self.assertNotIn("native_dbscan_abi_added\": true", text)

    def test_registry_keeps_numba_no_row_route_for_current_rt_dbscan_row(self) -> None:
        row = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "rt_dbscan")

        self.assertEqual(row["row_id"], "rt_dbscan_optix_numba_scale_default_65536_no_validation")
        self.assertIn("numba", " ".join(row["command"]))
        self.assertIn("Goal3851", row["evidence_refs"])
        self.assertTrue(row["requires_numba"])
        self.assertFalse(row["release_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])

    def test_docs_explain_no_row_perf_route_and_boundaries(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        flattened_report = " ".join(report.split())

        self.assertIn("no-row column-signature variant", readme)
        self.assertIn("Goal3851", report)
        self.assertIn("8.56x", report)
        self.assertIn("process startup", report)
        self.assertIn("does not authorize", report.lower())
        self.assertIn("not a DBSCAN-specific native engine", flattened_report)

    def test_a5000_direct_payload_avoids_python_rows_and_improves_steady_state(self) -> None:
        old_payload = _load(OLD_ARTIFACT)
        payload = _load(DIRECT_ARTIFACT)
        metadata = payload["metadata"]

        self.assertEqual(
            metadata["path"],
            "optix_rt_count_threshold_numba_prepared_grid_radius_graph_column_signature_3d",
        )
        self.assertFalse(metadata["materializes_python_rows"])
        self.assertEqual(metadata["signature_source"], "partner_column_arrays_no_python_row_dicts")
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["repeat"], 3)
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["warmup"], 1)
        self.assertLess(payload["elapsed_sec"], old_payload["elapsed_sec"] / 5.0)
        self.assertGreater(old_payload["elapsed_sec"] / payload["elapsed_sec"], 7.0)
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["rt_core_speedup_claim_authorized"])

    def test_a5000_runner_row_passes_but_keeps_cold_process_boundary_visible(self) -> None:
        summary = _load(RUNNER_SUMMARY)

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["json_pass_count"], 1)
        row = summary["rows"][0]
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["stderr_bytes"], 0)
        self.assertIn("optix_rt_core_flags_numba_prepared_grid_column_signature_3d", row["command"])
        self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

        payload = _load(ROOT / row["stdout_path"])
        self.assertLess(payload["elapsed_sec"], 0.5)
        self.assertGreater(row["elapsed_sec"], payload["elapsed_sec"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
