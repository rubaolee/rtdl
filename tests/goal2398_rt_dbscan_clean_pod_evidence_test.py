from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2398_rt_dbscan_clean_pod_evidence"
REPORT = ROOT / "docs" / "reports" / "goal2398_rt_dbscan_clean_pod_evidence_2026-05-19.md"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2398RtDbscanCleanPodEvidenceTest(unittest.TestCase):
    def test_clean_pod_environment_records_goal2397_commit(self) -> None:
        environment = (ARTIFACT_DIR / "environment.txt").read_text(encoding="utf-8")

        self.assertIn("commit=7b9cd29afd02c9790b8982b9d99423b34661d278", environment)
        self.assertIn("NVIDIA RTX A5000, 570.211.01", environment)
        self.assertIn("python=Python 3.12.3", environment)

    def test_repaired_device_grid_matches_host_bucket_and_is_faster(self) -> None:
        for dataset in ("clustered3d", "road3d"):
            with self.subTest(dataset=dataset):
                host = _load(f"{dataset}_partner_spatial_bucket_4096.json")
                grid = _load(f"{dataset}_partner_cupy_grid_4096.json")

                self.assertEqual(grid["signature"], host["signature"])
                self.assertLess(grid["elapsed_sec"], host["elapsed_sec"])
                self.assertEqual(
                    grid["metadata"]["component_union_policy"],
                    "monotonic_atomic_min_core_edge_union",
                )
                self.assertFalse(grid["claim_boundary"]["rt_core_accelerated"])

    def test_optix_artifacts_are_bounded_to_prepared_rows(self) -> None:
        clustered = _load("clustered3d_optix_prepared_rows_1024.json")
        road = _load("road3d_optix_prepared_rows_1024.json")

        self.assertTrue(clustered["claim_boundary"]["rt_core_accelerated"])
        self.assertTrue(road["claim_boundary"]["rt_core_accelerated"])
        self.assertEqual(clustered["metadata"]["path"], "optix_prepared_fixed_radius_neighbor_rows_3d")
        self.assertTrue(clustered["metadata"]["materializes_neighbor_rows"])
        self.assertTrue(road["metadata"]["materializes_neighbor_rows"])

    def test_report_keeps_claim_boundary_explicit(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("not an RT-core speedup claim", report)
        self.assertIn("materializes neighbor rows on the host", report)
        self.assertIn("OptiX fixed-radius device output to device-resident grouped/component continuation", report)


if __name__ == "__main__":
    unittest.main()
