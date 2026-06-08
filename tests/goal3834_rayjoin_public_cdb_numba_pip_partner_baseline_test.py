from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3834_rayjoin_public_cdb_numba_pip_partner_baseline.py"
ARTIFACT = ROOT / "docs" / "reports" / "goal3834_rayjoin_public_cdb_numba_pip_partner_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3834_rayjoin_public_cdb_numba_pip_partner_baseline_2026-06-07.md"


class Goal3834RayJoinPublicCdbNumbaPipPartnerBaselineTest(unittest.TestCase):
    def test_dry_run_declares_numba_pip_same_contract_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--data-dir",
                    "/example/rayjoin_public_cdb",
                    "--repeat",
                    "7",
                    "--warmup",
                    "2",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=120,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-1000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3834.rayjoin_public_cdb_numba_pip_partner_baseline.v1")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["case_id"], "pip_county512")
        self.assertEqual(payload["workload"], "pip")
        self.assertIn("br_county_start256_count512.cdb", payload["dataset"])
        self.assertIn("Numba CUDA JIT dense all-pairs scalar count", payload["planned_numba_baseline"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_script_declares_no_rawkernel_numba_route_and_count_cross_checks(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "numba_cuda_jit_dense_pip_scalar_count",
            "\"raw_kernel_required\": False",
            "same_contract_with_goal3589_cupy_pip",
            "cuda.atomic.add",
            "Numba/CuPy PIP count mismatch",
            "Numba/RTDL PIP count mismatch",
            "not automatic dispatch",
            "not a RayJoin paper",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_is_checked_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3834 A5000 artifact not collected yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3834.rayjoin_public_cdb_numba_pip_partner_baseline.v1")
        self.assertFalse(payload["dry_run"])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertTrue(payload["summary"]["numba_no_rawkernel_route_available"])
        self.assertEqual(payload["summary"]["numba_row_count"], payload["summary"]["cupy_row_count"])
        self.assertEqual(payload["summary"]["numba_row_count"], payload["summary"]["rtdl_optix_row_count"])
        self.assertFalse(payload["numba_cuda_jit_baseline"]["rt_core_accelerated"])
        self.assertTrue(payload["numba_cuda_jit_baseline"]["partner_accelerated"])
        self.assertFalse(payload["numba_cuda_jit_baseline"]["raw_kernel_required"])
        self.assertEqual(payload["numba_cuda_jit_baseline"]["block_size"], 128)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_report_documents_user_partner_boundary_when_present(self) -> None:
        if not REPORT.exists():
            self.skipTest("Goal3834 report not written yet")
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3834",
            "Numba CUDA JIT",
            "no CuPy RawKernel",
            "same-contract",
            "not automatic dispatch",
            "not a RayJoin paper reproduction",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
