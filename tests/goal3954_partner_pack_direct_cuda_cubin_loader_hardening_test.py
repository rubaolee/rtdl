import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3954_partner_pack_direct_cuda_cubin_loader_hardening_2026-06-08"
    / "goal3954_partner_pack_smoke.json"
)


class Goal3954PartnerPackDirectCudaCubinLoaderHardeningTest(unittest.TestCase):
    def test_partner_pack_direct_cuda_loaders_use_cubin(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for source_name, file_name in (
            ("kPackTriangle3DDeviceColumnsKernelSrc", "partner_triangle3d_device_columns_pack_kernel.cu"),
            ("kPackRay3DDeviceColumnsKernelSrc", "partner_ray3d_device_columns_pack_kernel.cu"),
            ("kPackTriangle2DDeviceColumnsKernelSrc", "partner_triangle2d_device_columns_pack_kernel.cu"),
            ("kPackRay2DDeviceColumnsKernelSrc", "partner_ray2d_device_columns_pack_kernel.cu"),
        ):
            pattern = (
                rf"compile_to_cubin\(\s*{source_name},\s*\"{re.escape(file_name)}\"\s*\)"
                r"[\s\S]{0,260}?cuModuleLoadData\(&[^,]+,\s*cubin\.data\(\)\)"
            )
            self.assertRegex(text, pattern)
            self.assertNotIn(
                f'compile_to_ptx({source_name}, "{file_name}")',
                text,
            )

    def test_partner_pack_pod_smoke_artifact_is_clean(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["summary"]["row_count"], 4)
        self.assertEqual(data["summary"]["app_count"], 4)
        self.assertEqual(data["validation"]["status"], "accept")
        self.assertFalse(data["summary"]["release_authorized"])
        self.assertFalse(data["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["summary"]["broad_rt_core_claim_authorized"])
        self.assertFalse(data["summary"]["paper_reproduction_claim_authorized"])

        apps = {row["app"] for row in data["rows"]}
        self.assertEqual(
            apps,
            {
                "spatial_rayjoin",
                "robot_collision",
                "contact_manifold",
                "triangle_counting",
            },
        )
        self.assertTrue(all(row["status"] == "pass" for row in data["rows"]))


if __name__ == "__main__":
    unittest.main()
