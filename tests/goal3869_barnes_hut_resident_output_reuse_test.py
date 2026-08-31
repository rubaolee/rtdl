from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "src/rtdsl/app_adapters/barnes_hut.py"
APP = ROOT / "examples/current/apps/simulation/rtdl_barnes_hut_force_app.py"
SCRIPT = ROOT / "scripts/goal3869_barnes_hut_resident_output_reuse_probe.py"
REPORT = ROOT / "docs/reports/goal3869_barnes_hut_resident_output_reuse_2026-06-08.md"
ARTIFACT = ROOT / "docs/reports/goal3869_barnes_hut_resident_output_reuse_a5000/summary.json"
EXIT_CODE = ROOT / "docs/reports/goal3869_barnes_hut_resident_output_reuse_a5000/exit_code"
SCALE_PROFILES = ROOT / "src/rtdsl/current_benchmark_scale_profiles.py"
ADEQUACY = ROOT / "src/rtdsl/v2_9_benchmark_adequacy.py"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal3869BarnesHutResidentOutputReuseTest(unittest.TestCase):
    def test_adapter_exposes_reusable_output_columns_without_native_engine_change(self) -> None:
        text = ADAPTER.read_text(encoding="utf-8")

        self.assertIn("output_columns: dict[str, object] | None = None", text)
        self.assertIn("output_columns_reused", text)
        self.assertIn("output_columns['force_x'] must match source_count", text)
        self.assertIn("output_force_x", text)
        self.assertIn("native_engine_row_contract", text)
        self.assertIn("not_called_partner_reference_only", text)

    def test_force_summary_loop_reuses_outputs_after_first_result(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("reusable_force_columns", text)
        self.assertIn("output_columns=reusable_force_columns", text)
        self.assertIn("prepared_force_output_columns_reused", text)
        self.assertIn("materializes_python_force_rows", text)

    def test_probe_and_report_document_boundary_and_rejected_atomic_path(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("reuse_outputs", script)
        self.assertIn("checksum_match", script)
        self.assertIn("release_authorized", script)
        for phrase in (
            "Goal3869",
            "symmetric half-pair Numba kernel",
            "determinism",
            "1.162x",
            "not a hierarchical Barnes-Hut acceleration path",
            "not an RT-core claim",
        ):
            self.assertIn(phrase, report)

    def test_a5000_artifact_is_clean_and_shows_resident_numba_improvement(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        payload = _load(ARTIFACT)

        self.assertEqual(payload["schema"], "rtdl.goal3869.barnes_hut_resident_output_reuse_probe.v1")
        self.assertEqual(payload["source_commit_short"], "539d61ef")
        self.assertEqual(payload["git_status_short"], "")
        self.assertFalse(payload["goal3869_scoped_source_dirty"])
        self.assertTrue(payload["summary"]["all_checksum_match"])
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertGreater(payload["summary"]["geomean_reuse_speedup_vs_no_reuse"], 1.03)

        rows = {(int(row["body_count"]), row["partner"]): row for row in payload["rows"]}
        numba_8192 = rows[(8192, "numba")]
        self.assertGreater(numba_8192["reuse_speedup_vs_no_reuse"], 1.15)
        self.assertTrue(numba_8192["checksum_match"])
        self.assertTrue(numba_8192["with_reuse"]["metadata"]["output_columns_reused"])
        self.assertFalse(numba_8192["with_reuse"]["metadata"]["raw_cuda_kernel_required"])
        self.assertFalse(numba_8192["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(numba_8192["claim_boundary"]["native_engine_app_specific"])

    def test_current_registry_records_goal3869_without_overclaiming(self) -> None:
        scale_text = SCALE_PROFILES.read_text(encoding="utf-8")
        adequacy_text = ADEQUACY.read_text(encoding="utf-8")

        self.assertIn("resident output reuse", scale_text)
        self.assertIn('"Goal3869"', scale_text)
        self.assertIn("1.162x", adequacy_text)
        self.assertIn("16384 remains compute-dominated", adequacy_text)
        self.assertIn("Richer hierarchical force acceleration remains separate future work", adequacy_text)


if __name__ == "__main__":
    unittest.main()
