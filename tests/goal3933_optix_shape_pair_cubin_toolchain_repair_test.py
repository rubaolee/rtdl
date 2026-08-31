from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3933_optix_shape_pair_cubin_toolchain_repair_2026-06-08.md"
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3933_optix_shape_pair_cubin_toolchain_repair_pod_2026-06-08"
)


class Goal3933OptixShapePairCubinToolchainRepairTest(unittest.TestCase):
    def test_shape_pair_active_count_direct_helper_uses_cubin_not_ptx(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")

        start = workloads.index("static void ensure_shape_pair_relation_active_count_device_pipeline")
        end = workloads.index("static GpuBounds2DF32 bounds_to_gpu_f32", start)
        block = workloads[start:end]

        self.assertIn("compile_to_cubin(", block)
        self.assertIn("kShapePairRelationActiveCountDeviceKernelSrc", block)
        self.assertIn("shape_pair_relation_active_count_device_kernel.cu", block)
        self.assertIn("cuModuleLoadData", block)
        self.assertNotIn("compile_to_ptx(", block)
        self.assertNotIn("--device-as-default-execution-space", block)

    def test_closed_shape_early_optix_strings_do_not_pull_host_math_header(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        kernels = (
            "kSegmentFirstHitKernelSrc",
            "kPipKernelSrc",
            "kPointClosedShapeBoundaryEventKernelSrc",
            "kShapePairRelationKernelSrc",
            "kShapePairRelationActiveCountDeviceKernelSrc",
        )
        for index, name in enumerate(kernels):
            start = core.index(f"static const char* {name}")
            if index + 1 < len(kernels):
                end = core.index(f"static const char* {kernels[index + 1]}", start)
            else:
                end = core.index("static const char* kRayHitCountKernelSrc", start)
            kernel = core[start:end]
            self.assertNotIn("#include <math.h>", kernel, name)

        for helper in ("pip_absf", "boundary_event_absf", "shape_pair_relation_absf", "dclampf"):
            self.assertIn(helper, core)

    def test_report_records_non_authorizing_toolchain_repair_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "unsupported toolchain",
            "CUBIN",
            "generic and app-agnostic",
            "accept_with_boundary",
            "authorize release wording",
            "blocked_candidate_slower_keep_unblocked_default",
        ):
            self.assertIn(phrase, text)

    def test_pod_artifacts_pass_with_boundaries_closed(self) -> None:
        manifest = json.loads((ARTIFACT_DIR / "summary_manifest.json").read_text(encoding="utf-8"))
        evaluation = json.loads((ARTIFACT_DIR / "goal3931_evaluation.json").read_text(encoding="utf-8"))
        rayjoin = json.loads((ARTIFACT_DIR / "rayjoin_summary.json").read_text(encoding="utf-8"))
        unblocked = json.loads((ARTIFACT_DIR / "rtdbscan_unblocked.json").read_text(encoding="utf-8"))
        blocked = json.loads((ARTIFACT_DIR / "rtdbscan_blocked.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", manifest["status"])
        self.assertEqual("accept_with_boundary", evaluation["status"])
        self.assertEqual([], evaluation["errors"])
        self.assertEqual("edc90516+goal3933_cubin_sourcefix", manifest["source_commit_label"])
        self.assertIn("src/native/optix/rtdl_optix_workloads.cpp", "\n".join(manifest["source_dirty"]))

        self.assertTrue(rayjoin["all_counts_match"])
        self.assertEqual(3, len(rayjoin["cases"]))
        self.assertFalse(rayjoin["claim_boundary"]["release_authorized"])
        self.assertFalse(rayjoin["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertGreater(
            rayjoin["representative_hot_path_summary"]["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"],
            100.0,
        )
        self.assertGreater(
            rayjoin["representative_hot_path_summary"]["overlay_active_count"]["rtdl_optix_speedup_vs_numba"],
            100.0,
        )

        self.assertEqual("numba", unblocked["metadata"]["count_metadata"]["partner"])
        self.assertEqual("numba", blocked["metadata"]["count_metadata"]["partner"])
        self.assertLess(unblocked["elapsed_sec"], blocked["elapsed_sec"])
        self.assertEqual(
            "blocked_candidate_slower_keep_unblocked_default",
            evaluation["rtdbscan"]["recommendation"],
        )
        self.assertTrue(all(value is False for value in evaluation["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
