import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "v3_phoenix_m6_barnes_hut_intake.py"
HISTORICAL_M87 = REPO_ROOT / "docs" / "reports" / "goal4483_v3_0_m87_barnes_hut_large_scale_rerank_2026-06-16.json"
CURRENT_RAW = (
    REPO_ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_m6_barnes_hut_20260620"
    / "m6_barnes_hut_rerank_32768_65536_131072_partitioned_r11.json"
)


class V3PhoenixM6BarnesHutIntakeTest(unittest.TestCase):
    def test_historical_large_scale_rerank_passes_internal_intake(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--rerank-json",
                str(HISTORICAL_M87),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["overall_status"], "internal_m6_route_parity_evidence")
        self.assertEqual(payload["generic_capability"], "aggregate_frontier_vector_accumulation")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertEqual(payload["fastest_by_scale"]["65536"], "numba_cuda_fused")
        self.assertEqual(payload["fastest_by_scale"]["131072"], "numba_cuda_fused")
        self.assertTrue(payload["checks"]["route_parity_passed"])
        self.assertTrue(payload["checks"]["all_body_counts_have_four_routes"])
        self.assertTrue(payload["timing_basis_mixed"])
        self.assertEqual(payload["failures"], [])

    def test_current_raw_rerank_recomputes_same_internal_status(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--rerank-json",
                str(CURRENT_RAW),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["overall_status"], "internal_m6_route_parity_evidence")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertEqual(payload["phoenix_m7_qualified_release_rows"], 0)
        self.assertTrue(payload["timing_basis_mixed"])
        self.assertEqual(payload["fastest_by_scale"]["32768"], "numba_cuda_fused")
        self.assertEqual(payload["fastest_by_scale"]["65536"], "numba_cuda_fused")
        self.assertEqual(payload["fastest_by_scale"]["131072"], "numba_cuda_fused")
        self.assertEqual(payload["failures"], [])

    def test_checksum_mismatch_fails(self) -> None:
        source = json.loads(HISTORICAL_M87.read_text(encoding="utf-8"))
        source["rows"][0]["checksum_force_x"] += 1.0
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps(source), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--rerank-json",
                    str(bad),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(any("checksum delta" in failure for failure in payload["failures"]))


if __name__ == "__main__":
    unittest.main()
