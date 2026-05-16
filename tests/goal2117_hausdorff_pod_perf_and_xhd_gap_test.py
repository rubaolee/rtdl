import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2117_hausdorff_pod_perf_and_xhd_gap_2026-05-16.md"
REPORTS = ROOT / "docs" / "reports"


class Goal2117HausdorffPodPerfAndXhdGapTest(unittest.TestCase):
    def _load(self, name: str) -> dict:
        return json.loads((REPORTS / name).read_text(encoding="utf-8"))

    def test_report_preserves_claim_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("no RT-core exact Hausdorff speedup claim is authorized", text)
        self.assertIn("no X-HD parity claim is authorized", text)
        self.assertIn("RTDL v2.0 should not bake \"Hausdorff\" into the native engine", text)
        self.assertIn("Exact RTDL v2 user HD path: `accept`", text)
        self.assertIn("RT-core HD claim: `needs-more-evidence`", text)

    def test_rtdl_v2_user_cuda_matches_exact_large_rows(self):
        for name in (
            "goal2117_pod_hd_cuda_cpp_sm89_32768.json",
            "goal2117_pod_hd_cuda_cpp_sm89_65536.json",
            "goal2117_pod_hd_cuda_cpp_sm89_131072.json",
            "goal2117_pod_hd_cuda_cpp_sm89_262144.json",
        ):
            payload = self._load(name)
            exact = payload["exact_reference"]
            rtdl = payload["results"]["rtdl_v2_user_cuda"]
            cuda = payload["results"]["cuda_cpp"]
            self.assertTrue(rtdl["ok"], name)
            self.assertTrue(cuda["ok"], name)
            self.assertTrue(rtdl["matches_exact_reference"], name)
            self.assertTrue(cuda["matches_exact_reference"], name)
            self.assertTrue(math.isclose(rtdl["distance"], exact["distance"], rel_tol=1e-12, abs_tol=1e-12), name)
            self.assertTrue(math.isclose(cuda["distance"], exact["distance"], rel_tol=1e-12, abs_tol=1e-12), name)

    def test_cuda_cpp_failure_is_explicit_before_arch_pin(self):
        payload = self._load("goal2117_pod_hd_cuda_cpp_errorcheck_512.json")
        cuda = payload["results"]["cuda_cpp"]
        self.assertFalse(cuda["ok"])
        self.assertIn("stage=12", cuda["error"])
        self.assertIn("cuda_status=222", cuda["error"])

    def test_optix_rt_attempt_is_blocked_by_compiler_ice(self):
        payload = self._load("goal2117_pod_hd_smoke_512_host_count_split.json")
        for method in (
            "rtdl_rt_threshold_search",
            "rtdl_rt_nearest_witness",
            "rtdl_rt_nearest_witness_oracle_radius",
        ):
            row = payload["results"][method]
            self.assertFalse(row["ok"], method)
            self.assertIn("OptiX module compile error: Internal compiler error", row["error"])
        self.assertTrue(payload["results"]["rtdl_v2_user_cuda"]["matches_exact_reference"])


if __name__ == "__main__":
    unittest.main()
