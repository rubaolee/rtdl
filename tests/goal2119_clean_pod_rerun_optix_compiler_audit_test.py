from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal2119CleanPodRerunOptixCompilerAuditTest(unittest.TestCase):
    def test_report_records_clean_rerun_and_boundaries(self) -> None:
        report = ROOT / "docs" / "reports" / "goal2119_clean_pod_rerun_optix_compiler_audit_2026-05-16.md"
        text = report.read_text(encoding="utf-8")
        self.assertIn("Clean rerun: `accept`", text)
        self.assertIn("OptiX RT-core HD evidence on this pod: `needs-new-pod`", text)
        self.assertIn("RT-core Hausdorff speedup claim: `needs-more-evidence`", text)
        self.assertIn("Known-good RTDL OptiX ray/triangle any-hit control", text)
        self.assertIn("CUDA/CuPy HD positive control", text)

    def test_artifacts_capture_cuda_success_and_optix_compiler_block(self) -> None:
        cuda_artifact = ROOT / "docs" / "reports" / "goal2119_clean_cuda_positive_control_4096.json"
        nearest_artifact = ROOT / "docs" / "reports" / "goal2119_clean_rt_nearest_rayorigin_512.json"
        threshold_artifact = ROOT / "docs" / "reports" / "goal2119_clean_rt_threshold_rayorigin_512.json"

        cuda_data = json.loads(cuda_artifact.read_text(encoding="utf-8"))
        self.assertTrue(cuda_data["results"]["cupy_rawkernel"]["ok"])
        self.assertTrue(cuda_data["results"]["rtdl_v2_user_cuda"]["ok"])
        self.assertTrue(cuda_data["results"]["rtdl_v2_user_cuda"]["matches_exact_reference"])

        nearest_data = json.loads(nearest_artifact.read_text(encoding="utf-8"))
        nearest_error = nearest_data["results"]["rtdl_rt_nearest_witness"]["error"]
        self.assertIn("OptiX module compile error", nearest_error)
        self.assertIn("Internal compiler error", nearest_error)

        threshold_data = json.loads(threshold_artifact.read_text(encoding="utf-8"))
        threshold_error = threshold_data["results"]["rtdl_rt_threshold_search"]["error"]
        self.assertIn("OptiX module compile error", threshold_error)
        self.assertIn("Internal compiler error", threshold_error)


if __name__ == "__main__":
    unittest.main()
