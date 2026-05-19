from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2357_v2_2_rtnn_uniform_cell_neighbor_step_2026-05-18.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2357_rtdl_3d_neighbor_rt"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2357V22RtnnUniformCellNeighborStepTest(unittest.TestCase):
    def test_source_has_three_bounded_neighbor_modes(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("kFixedRadiusNeighbors3DGridKernelSrc", core)
        self.assertIn("fixed_radius_neighbors_3d_grid", core)
        self.assertIn("run_fixed_radius_neighbors_grid_cuda_3d", workloads)
        self.assertIn("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_CUDA", api)
        self.assertIn("RTDL_OPTIX_FIXED_RADIUS_3D_FORCE_RT", api)
        self.assertIn("generic uniform-cell bounded-neighbor traversal", runner)

    def test_pod_artifacts_show_grid_beats_old_cuda_on_warm_raw_rows(self) -> None:
        grid65 = _load("rtdl_grid_compact_raw_repeat_3d_65536_r002_k50.json")
        cuda65 = _load("rtdl_cuda_raw_repeat_3d_65536_r002_k50.json")
        grid262 = _load("rtdl_grid_compact_raw_repeat_3d_262144_r002_k50.json")
        cuda262 = _load("rtdl_cuda_raw_repeat_3d_262144_r002_k50.json")

        for row in (grid65, cuda65, grid262, cuda262):
            self.assertTrue(row["ok"])
            self.assertEqual(row["result_mode"], "raw")
            self.assertEqual(row["repeat"], 3)
            self.assertFalse(row["claim_boundary"]["rtdl_speedup_claim_authorized"])

        self.assertLess(grid65["elapsed_sec"], cuda65["elapsed_sec"])
        self.assertLess(grid262["elapsed_sec"], cuda262["elapsed_sec"])
        self.assertEqual(grid65["row_count"], cuda65["row_count"])
        self.assertEqual(grid262["row_count"], cuda262["row_count"])

    def test_report_keeps_rtnn_boundary_honest(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not RTNN parity", text)
        self.assertIn("default path is RT-core accelerated", text)
        self.assertIn("0.557x", text)
        self.assertIn("prepared_bounded_neighbor_search_3d", text)
        self.assertIn("not v3.0 user-defined shader injection", text)


if __name__ == "__main__":
    unittest.main()
