from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1829_optix_device_column_pod_binding_fix_2026-05-13.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1828_optix_device_column_pod_validation.json"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal1829OptixDeviceColumnPodBindingFixTest(unittest.TestCase):
    def test_report_records_ctypes_bug_and_bounded_pod_pass(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("ctypes", text)
        self.assertIn("rtdl_optix_prepare_ray_anyhit_2d_device_triangles", text)
        self.assertIn("rtdl_optix_count_prepared_ray_anyhit_2d_device_rays", text)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", text)
        self.assertIn("It is not a v2.0 release proof", text)
        self.assertIn("true zero-copy", text)

    def test_pod_artifact_proves_narrow_execution_without_release_overclaim(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["observed_count"], data["expected_count"])
        self.assertEqual(data["device"], "NVIDIA RTX 4000 Ada Generation")
        self.assertTrue(data["claim_boundary"]["direct_device_column_execution_observed"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_authorized"])
        self.assertFalse(data["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["v2_0_release_authorized"])
        self.assertEqual(data["ray_metadata"]["source_protocols"], ["torch"])
        self.assertEqual(data["triangle_metadata"]["source_protocols"], ["torch"])

    def test_runtime_registers_native_ctypes_signatures(self) -> None:
        text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        registration = text[text.index("def _register_argtypes") :]
        self.assertIn("optional_prepare_anyhit2d_device_triangles.argtypes", registration)
        self.assertIn("optional_count_anyhit2d_device_rays.argtypes", registration)
        self.assertIn("optional_prepare_anyhit2d_device_triangles.restype = ctypes.c_int", registration)
        self.assertIn("optional_count_anyhit2d_device_rays.restype = ctypes.c_int", registration)


if __name__ == "__main__":
    unittest.main()
