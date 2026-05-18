from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2353_v2_2_rtnn_pod_baseline_2026-05-18.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2353_rtnn_pod"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2353RtnnPodBaselineTest(unittest.TestCase):
    def test_report_records_pod_and_optix_abi_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("root@69.30.85.236 -p 22170", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("OptiX error: Unsupported ABI version", text)
        self.assertIn("OPTIX_VERSION (9, 0, 0)", text)
        self.assertIn("e41e5388", text)

    def test_rtnn_rows_succeeded_and_keep_claims_bounded(self) -> None:
        rows = [
            "rtnn_radius_3d_65536_r002_k50_partitioned_warm2.json",
            "rtnn_radius_3d_262144_r002_k50_partitioned_warm2.json",
            "rtnn_knn_3d_262144_r005_k5_exact_partitioned.json",
            "rtnn_knn_3d_262144_r005_k5_approx2_partitioned.json",
        ]
        for row in rows:
            payload = _load(row)
            self.assertEqual(payload["returncode"], 0, row)
            self.assertFalse(payload["claim_boundary"]["rtdl_speedup_claim_authorized"], row)
            self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"], row)
            self.assertIn("total search time", payload["timings"], row)
            self.assertIn("search compute", payload["timings"], row)

    def test_sort_partition_dominates_warm_rtnn_rows(self) -> None:
        for row in [
            "rtnn_radius_3d_65536_r002_k50_partitioned_warm2.json",
            "rtnn_radius_3d_262144_r002_k50_partitioned_warm2.json",
            "rtnn_knn_3d_262144_r005_k5_exact_partitioned.json",
        ]:
            payload = _load(row)
            total = payload["timings"]["total search time"]["last_ms"]
            sort = payload["timings"]["sort and/or partition queries"]["last_ms"]
            compute = payload["timings"]["search compute"]["last_ms"]
            self.assertGreater(total, compute, row)
            self.assertGreater(sort, compute, row)

    def test_current_rtdl_row_is_smoke_only(self) -> None:
        payload = _load("rtdl_current_2d_fixed_radius_smoke_8192.json")
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "current_2d_fixed_radius_count_threshold_optix_smoke")
        self.assertFalse(payload["claim_boundary"]["paper_equivalent_rtnn_row"])
        self.assertFalse(payload["claim_boundary"]["rtdl_speedup_claim_authorized"])

    def test_report_identifies_next_generic_primitive(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Current RTDL does not yet expose RTNN's exact 3D radius+K contract", text)
        self.assertIn("prepared_bounded_neighbor_search_3d", text)
        self.assertIn("keeps RTDL app-agnostic", text)


if __name__ == "__main__":
    unittest.main()
