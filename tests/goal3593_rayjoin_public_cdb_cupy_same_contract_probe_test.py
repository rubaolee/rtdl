from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py"
ARTIFACT = ROOT / "docs" / "reports" / "goal3593_rayjoin_public_cdb_cupy_same_contract_a5000" / "summary.json"


class Goal3593RayJoinPublicCdbCupySameContractProbeTest(unittest.TestCase):
    def test_dry_run_lists_public_cdb_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--data-dir",
                    "/example/rayjoin_public_cdb",
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
        self.assertEqual(payload["schema"], "rtdl.goal3593.rayjoin_public_cdb_cupy_same_contract_probe.v1")
        rows = {row["case_id"]: row for row in payload["rows"]}
        self.assertEqual(rows["pip_county512"]["workload"], "pip")
        self.assertEqual(rows["lsi_county512_soil512"]["workload"], "lsi")
        self.assertEqual(rows["overlay_county512_soil512"]["workload"], "overlay_seed")
        self.assertIn("br_county_start256_count512.cdb", rows["pip_county512"]["dataset"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_script_reuses_goal3589_baseline_runner_and_blocks_claims(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "run_cupy_baseline",
            "run_rtdl_optix",
            "not a RayJoin paper",
            "not a public RT-core speedup claim",
            "not release evidence",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_is_checked_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3593 A5000 artifact not collected yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3593.rayjoin_public_cdb_cupy_same_contract_probe.v1")
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        for row in payload["rows"]:
            self.assertTrue(row["counts_match"])
            self.assertFalse(row["cupy_cuda_core_baseline"]["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
