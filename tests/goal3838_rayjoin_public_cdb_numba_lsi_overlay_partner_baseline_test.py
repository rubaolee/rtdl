from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.py"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_a5000"
    / "summary.json"
)
REPORT = ROOT / "docs" / "reports" / "goal3838_rayjoin_public_cdb_numba_lsi_overlay_partner_baseline_2026-06-08.md"
MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
PARTNER_GUIDE = ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md"


class Goal3838RayJoinNumbaLsiOverlayPartnerBaselineTest(unittest.TestCase):
    def test_dry_run_lists_lsi_and_overlay_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--data-dir",
                    "/example/rayjoin_public_cdb",
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("[goal3838] wrote", completed.stdout)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3838.rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.v1")
        self.assertEqual(payload["cases"], ["lsi_county512_soil512", "overlay_county512_soil512"])
        self.assertEqual([row["workload"] for row in payload["rows"]], ["lsi", "overlay_seed"])
        self.assertIn("Numba CUDA JIT dense all-pairs scalar count", payload["rows"][0]["planned_numba_baseline"])
        self.assertFalse(payload["claim_boundary"]["release_authorized"])

    def test_script_defines_no_rawkernel_numba_routes_and_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("rtdl.goal3838.rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.v1", text)
        self.assertIn("@cuda.jit", text)
        self.assertIn("def lsi_count", text)
        self.assertIn("def overlay_active_count", text)
        self.assertIn("cuda.atomic.add(count_out, 0, 1)", text)
        self.assertIn('"raw_kernel_required": False', text)
        self.assertIn("run_cupy_baseline(workload, dataset", text)
        self.assertIn("run_rtdl_optix(workload, dataset", text)
        self.assertIn("not automatic dispatch", text)
        self.assertIn("not a RayJoin paper reproduction", text)

    def test_pod_artifact_when_present_records_same_contract_counts(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3838 A5000 artifact not generated yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3838.rayjoin_public_cdb_numba_lsi_overlay_partner_baseline.v1")
        self.assertEqual(payload["git_commit"][:8], "ae8d19c3")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertEqual(payload["cases"], ["lsi_county512_soil512", "overlay_county512_soil512"])
        self.assertEqual(payload["repeat"], 200)
        self.assertEqual(payload["warmup"], 5)
        self.assertTrue(payload["summary"]["all_counts_match"])
        for row in payload["rows"]:
            self.assertTrue(row["counts_match"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["paper_reproduction_claim_authorized"])
            numba = row["numba_cuda_jit_baseline"]
            self.assertEqual(numba["partner"], "numba")
            self.assertFalse(numba["raw_kernel_required"])
            self.assertEqual(numba["row_count"], row["cupy_cuda_core_baseline"]["row_count"])
            self.assertEqual(numba["row_count"], row["rtdl_optix"]["row_count"])
            self.assertGreater(row["cupy_speedup_vs_numba"], 1.0)
            self.assertLess(row["numba_speedup_vs_rtdl_optix"], 0.01)

    def test_report_and_learner_docs_state_primitive_first_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("RayJoin Numba LSI/Overlay Partner Baseline", report)
        self.assertIn("Goal3834/3838", MATRIX.read_text(encoding="utf-8"))
        self.assertIn("PIP/LSI/overlay scalar-count reference rows", PARTNER_GUIDE.read_text(encoding="utf-8"))
        self.assertIn("RTDL/OptiX vs Numba", report)
        self.assertIn("262.643x", report)
        self.assertIn("258.081x", report)
        self.assertIn("not a native engine change", report)
        self.assertIn("does not authorize", report)


if __name__ == "__main__":
    unittest.main()
