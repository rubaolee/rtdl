from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2371_native_prepared_frn3d_pod"
GOAL2369_DIR = ROOT / "docs" / "reports" / "goal2368_rtnn_prepared_column_pod"
REPORT = ROOT / "docs" / "reports" / "goal2371_native_prepared_bounded_neighbor_3d_2026-05-19.md"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
POD_RUNNER = ROOT / "scripts" / "goal2371_native_prepared_frn3d_pod_runner.sh"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2371NativePreparedBoundedNeighbor3DTest(unittest.TestCase):
    def test_native_abi_is_generic_and_python_facade_is_exposed(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        for text in (api, prelude, runtime):
            self.assertIn("rtdl_optix_prepare_fixed_radius_neighbors_3d", text)
            self.assertIn("rtdl_optix_run_prepared_fixed_radius_neighbors_3d", text)
            self.assertIn("rtdl_optix_destroy_prepared_fixed_radius_neighbors_3d", text)
            self.assertNotIn("rtnn_prepare", text.lower())
            self.assertNotIn("rtnn_run", text.lower())

        self.assertIn("class PreparedOptixFixedRadiusNeighbors3D", runtime)
        self.assertIn("def prepare_optix_fixed_radius_neighbors_3d", runtime)
        self.assertIn('"prepared_uniform_cell_compact"', runtime)
        self.assertIn("native-prepared-optix", runner)
        self.assertIn('"prepared_execution_reuses_native_search_grid"', runner)

        pod_runner = POD_RUNNER.read_text(encoding="utf-8")
        self.assertIn("make build-optix", pod_runner)
        self.assertIn("--execution-mode native-prepared-optix", pod_runner)
        self.assertIn("STEP_TIMEOUT_SECONDS", pod_runner)
        self.assertIn("[goal2371] summary", pod_runner)

    def test_pod_artifacts_show_native_prepared_mode_and_matching_rows(self) -> None:
        native_65 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_65536_r002_k50.json")
        native_262 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_262144_r002_k50.json")
        packed_65 = _load(GOAL2369_DIR / "rtdl_packed_run_optix_3d_65536_r002_k50.json")
        packed_262 = _load(GOAL2369_DIR / "rtdl_packed_run_optix_3d_262144_r002_k50.json")

        for payload in (native_65, native_262):
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["execution_mode"], "native-prepared-optix")
            self.assertEqual(payload["phase_timings"]["mode"], "prepared_uniform_cell_compact")
            self.assertEqual(payload["phase_timings"]["prepare"], 0.0)
            self.assertTrue(payload["claim_boundary"]["prepared_execution_reuses_native_search_grid"])
            self.assertFalse(payload["claim_boundary"]["prepared_execution_reuses_python_packed_inputs"])
            self.assertFalse(payload["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])

        self.assertEqual(native_65["row_count"], packed_65["row_count"])
        self.assertEqual(native_262["row_count"], packed_262["row_count"])
        self.assertLess(native_65["phase_timings"]["upload"], packed_65["phase_timings"]["upload"])
        self.assertLess(native_262["phase_timings"]["upload"], packed_262["phase_timings"]["upload"])
        self.assertGreater(packed_65["elapsed_sec"] / native_65["elapsed_sec"], 1.25)
        self.assertGreater(packed_262["elapsed_sec"] / native_262["elapsed_sec"], 1.05)

    def test_report_states_remaining_bottleneck_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("removes native search-grid rebuild/upload", text)
        self.assertIn("host exact refinement", text)
        self.assertIn("not RTNN-specific", text)
        self.assertIn("does not use RT cores", text)
        self.assertIn("does not authorize RTNN paper equivalence", text)
        self.assertIn("device-resident exact/filter", text)
        self.assertIn("row-summary", text)


if __name__ == "__main__":
    unittest.main()
