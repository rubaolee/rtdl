import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3942_frn3d_direct_cuda_cubin_toolchain_repair_2026-06-08"
)


class Goal3942Frn3dDirectCudaCubinToolchainRepairTest(unittest.TestCase):
    def test_fixed_radius_3d_direct_cuda_modules_use_cubin(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for source_name, file_name in (
            ("kFixedRadiusNeighbors3DKernelSrc", "frn3d_kernel.cu"),
            ("kFixedRadiusNeighbors3DGridKernelSrc", "frn3d_grid_kernel.cu"),
        ):
            pattern = (
                rf"compile_to_cubin\({source_name}, \"{re.escape(file_name)}\"\)"
                r"[\s\S]{0,240}?cuModuleLoadData\(&[^,]+,\s*cubin\.data\(\)\)"
            )
            self.assertRegex(text, pattern)
            self.assertNotIn(
                f'compile_to_ptx({source_name}, "{file_name}")',
                text,
            )

    def test_pod_rtnn_artifact_proves_previous_row_runs(self) -> None:
        stderr = ARTIFACT_DIR / "rtnn_frn3d_cubin.stderr.txt"
        payload = ARTIFACT_DIR / "rtnn_frn3d_cubin.json"
        self.assertTrue(payload.exists())
        self.assertTrue(stderr.exists())
        self.assertEqual("", stderr.read_text(encoding="utf-8"))

        data = json.loads(payload.read_text(encoding="utf-8"))
        runner = data["runner_payload"]
        self.assertEqual("rtnn_neighbor_search", data["benchmark_app"])
        self.assertEqual("prepared_optix_ranked_summary", data["mode"])
        self.assertEqual(65536, data["point_count"])
        self.assertEqual(50, data["k"])
        self.assertTrue(runner["ok"])
        self.assertEqual("", runner["error"])
        self.assertEqual(65536, runner["row_count"])
        self.assertEqual(
            "fixed_radius_neighbors_3d",
            runner["contract"]["family"],
        )
        self.assertFalse(runner["claim_boundary"]["rtdl_speedup_claim_authorized"])
        self.assertFalse(runner["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["amd_performance_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
