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
REPORT = ROOT / "docs" / "reports" / "goal3593_rayjoin_public_cdb_cupy_same_contract_probe_2026-06-06.md"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.goal3589_rayjoin_cupy_same_contract_baseline import _segment_array  # noqa: E402
from rtdsl.segment_columns import SegmentColumns2D  # noqa: E402


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

    def test_goal3589_cupy_segment_baseline_accepts_segment_columns(self) -> None:
        try:
            import numpy as np
        except Exception as exc:  # pragma: no cover - numpy is available in normal gates.
            self.skipTest(f"numpy unavailable: {exc}")
        columns = SegmentColumns2D(
            ids=np.asarray([10, 11], dtype=np.int64),
            x0=np.asarray([1.0, 2.0], dtype=np.float64),
            y0=np.asarray([3.0, 4.0], dtype=np.float64),
            x1=np.asarray([5.0, 6.0], dtype=np.float64),
            y1=np.asarray([7.0, 8.0], dtype=np.float64),
            count=2,
        )
        array = _segment_array(columns, np)
        self.assertEqual(array.tolist(), [[1.0, 3.0, 5.0, 7.0], [2.0, 4.0, 6.0, 8.0]])

    def test_report_documents_mixed_public_cdb_outcome_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "PIP remains",
            "LSI strongly favors RTDL/OptiX",
            "Overlay active-pair dependency count also strongly favors RTDL/OptiX",
            "not a RayJoin paper reproduction",
            "not automatic dispatch",
        ):
            self.assertIn(phrase, text)

    def test_readme_documents_public_cdb_route_choice(self) -> None:
        text = README.read_text(encoding="utf-8")
        for phrase in (
            "bounded public CDB slices used in Goal3593",
            "PIP positive assignment count | CuPy dense CUDA-core count",
            "LSI segment-intersection count | RTDL/OptiX prepared route",
            "Overlay active pair-dependency count | RTDL/OptiX prepared route",
            "goal3593_rayjoin_public_cdb_cupy_same_contract_probe",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
