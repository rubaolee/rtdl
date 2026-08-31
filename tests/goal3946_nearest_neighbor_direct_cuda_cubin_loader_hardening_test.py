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
    / "goal3946_nearest_neighbor_direct_cuda_cubin_loader_hardening_2026-06-08"
)


class Goal3946NearestNeighborDirectCudaCubinLoaderHardeningTest(unittest.TestCase):
    def test_nearest_neighbor_direct_cuda_loaders_use_cubin(self) -> None:
        text = NATIVE.read_text(encoding="utf-8")
        for source_name, file_name in (
            ("kPointNearestKernelSrc", "pns_kernel.cu"),
            ("kFixedRadiusNeighborsKernelSrc", "frn_kernel.cu"),
            ("kPackPoint2DDeviceAabbsKernelSrc", "partner_point2d_fixed_radius_aabb_pack_kernel.cu"),
            ("kKnnRowsKernelSrc", "k_closest_hits_kernel.cu"),
            ("kKnnRows3DKernelSrc", "knn3d_kernel.cu"),
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

    def test_pod_smoke_artifacts_cover_user_facing_neighbor_paths(self) -> None:
        for stem, app, expected_rows in (
            ("fixed_radius_neighbors_optix", "fixed_radius_neighbors", 4),
            ("knn_rows_optix", "knn_rows", 6),
            ("point_nearest_segment_optix", "point_nearest_segment", 2),
        ):
            with self.subTest(stem=stem):
                stdout = ARTIFACT_DIR / f"{stem}.json"
                stderr = ARTIFACT_DIR / f"{stem}.stderr"
                self.assertTrue(stdout.exists())
                self.assertTrue(stderr.exists())
                self.assertEqual("", stderr.read_text(encoding="utf-8"))
                data = json.loads(stdout.read_text(encoding="utf-8"))
                self.assertEqual(app, data["app"])
                self.assertEqual("optix", data["backend"])
                self.assertEqual(expected_rows, len(data["rows"]))


if __name__ == "__main__":
    unittest.main()
