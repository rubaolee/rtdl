from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2404_rt_dbscan_optix_backend_claim_boundary_correction_2026-05-19.md"
GOAL2401_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2401_rt_dbscan_optix_summary_bridge_pod"
GOAL2403_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2403_rt_dbscan_repeat_probe_pod"


class Goal2404RtDbscanOptixBackendClaimBoundaryCorrectionTest(unittest.TestCase):
    def test_app_metadata_no_longer_claims_rt_core_for_prepared_3d_modes(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn('"native_execution_path": "prepared_uniform_cell_cuda_grid_3d"', app)
        self.assertIn('"optix_backend_used": True', app)
        self.assertIn('"rt_core_accelerated": False', app)
        self.assertIn("It is not an RT-core claim", readme)
        self.assertIn("not the RT-core paper path", readme)

    def test_corrected_pod_artifacts_mark_backend_but_not_rt_core(self) -> None:
        for name in (
            "clustered3d_optix_core_flags_cupy_grid_4096.json",
            "road3d_optix_core_flags_cupy_grid_4096.json",
            "clustered3d_optix_prepared_rows_1024.json",
            "road3d_optix_prepared_rows_1024.json",
        ):
            with self.subTest(name=name):
                payload = json.loads((GOAL2401_ARTIFACT_DIR / name).read_text(encoding="utf-8"))

                self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
                self.assertTrue(payload["claim_boundary"]["optix_backend_used"])
                self.assertEqual(payload["metadata"]["native_execution_path"], "prepared_uniform_cell_cuda_grid_3d")

        for dataset in ("clustered3d", "road3d"):
            with self.subTest(dataset=dataset):
                payload = json.loads((GOAL2403_ARTIFACT_DIR / f"{dataset}_repeat4.json").read_text(encoding="utf-8"))
                bridge_rows = [
                    row
                    for row in payload["rows"]
                    if row["mode"] == "optix_core_flags_cupy_grid_components_3d"
                ]

                self.assertEqual(len(bridge_rows), 4)
                self.assertTrue(all(row["rt_core_accelerated"] is False for row in bridge_rows))

    def test_correction_report_sets_next_target(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("prepared_uniform_cell_cuda_grid_3d", report)
        self.assertIn("rt_core_accelerated=false", report)
        self.assertIn("No RT-core claim", report)
        self.assertIn("3-D fixed-radius threshold/count device columns", report)


if __name__ == "__main__":
    unittest.main()
