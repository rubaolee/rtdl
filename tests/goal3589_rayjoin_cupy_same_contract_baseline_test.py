from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3589_rayjoin_cupy_same_contract_baseline.py"
STANDARD_ARTIFACT = ROOT / "docs" / "reports" / "goal3589_rayjoin_cupy_same_contract_baseline_a5000" / "summary.json"
STRESS_ARTIFACT = ROOT / "docs" / "reports" / "goal3589_rayjoin_cupy_same_contract_baseline_stress_a5000" / "summary.json"


class Goal3589RayJoinCupySameContractBaselineTest(unittest.TestCase):
    def test_dry_run_lists_same_contract_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--tier",
                    "standard",
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
        self.assertEqual(payload["schema"], "rtdl.goal3589.rayjoin_cupy_same_contract_baseline.v1")
        self.assertTrue(payload["dry_run"])
        rows = {row["workload"]: row for row in payload["rows"]}
        self.assertEqual(rows["pip"]["candidate_pair_count"], 1024 * 512)
        self.assertEqual(rows["lsi"]["candidate_pair_count"], 512 * 512)
        self.assertEqual(rows["overlay_seed"]["candidate_pair_count"], 512 * 512)
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])

    def test_script_declares_cupy_baselines_as_non_rt_user_partner_code(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "cupy_rawkernel_cuda_core_dense_pip_count",
            "cupy_rawkernel_cuda_core_dense_lsi_count",
            "cupy_rawkernel_cuda_core_dense_shape_pair_active_count",
            "\"rt_core_accelerated\": False",
            "\"partner_accelerated\": True",
            "same_contract_baseline",
            "not a RayJoin paper",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifacts_preserve_claim_boundaries_when_present(self) -> None:
        for path in (STANDARD_ARTIFACT, STRESS_ARTIFACT):
            if not path.exists():
                continue
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["schema"], "rtdl.goal3589.rayjoin_cupy_same_contract_baseline.v1")
                self.assertFalse(payload["dry_run"])
                self.assertTrue(payload["summary"]["all_counts_match"])
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
                self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
                for row in payload["rows"]:
                    self.assertIsNotNone(row["rtdl_optix_speedup_vs_cupy_cuda_core"])
                    self.assertTrue(row["counts_match"])
                    self.assertFalse(row["cupy_cuda_core_baseline"]["rt_core_accelerated"])
                    self.assertTrue(row["cupy_cuda_core_baseline"]["partner_accelerated"])


if __name__ == "__main__":
    unittest.main()
