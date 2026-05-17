import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal2209_rayjoin_same_query_pod_evidence_2026-05-17.json"
REPORT = ROOT / "docs" / "reports" / "goal2209_rayjoin_same_query_pod_evidence_interpretation_2026-05-17.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2209_rayjoin_same_query_pod_evidence"


class Goal2209RayJoinSameQueryPodEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.evidence = cls.data["evidence_summary"]

    def test_import_keeps_raw_streams_out_of_repo_but_hashes_them(self) -> None:
        self.assertEqual(self.data["status"], "imported")
        self.assertFalse(self.data["include_streams"])
        for stream in self.data["stream_provenance"]:
            self.assertFalse(stream["copied_into_repo"])
            self.assertGreater(stream["bytes"], 1_000_000)
            self.assertRegex(stream["sha256"], r"^[0-9a-f]{64}$")
            self.assertFalse((ARTIFACT_DIR / stream["name"]).exists())

    def test_claim_boundaries_remain_locked(self) -> None:
        boundary = self.data["claim_boundary"]
        self.assertTrue(boundary["same_contract_with_rayjoin_query_exec"])
        for key in (
            "paper_scale_perf_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "v2_0_release_authorized",
        ):
            self.assertFalse(boundary[key])

    def test_rayjoin_rt_logs_show_real_optix_launches_and_checks(self) -> None:
        rayjoin = self.evidence["rayjoin"]
        self.assertGreaterEqual(rayjoin["lsi"]["rt"]["optix_launch_count"], 4)
        self.assertGreaterEqual(rayjoin["pip"]["rt"]["optix_launch_count"], 4)
        self.assertTrue(rayjoin["pip"]["rt"]["built_in_check_passed"])
        self.assertLess(rayjoin["lsi"]["rt"]["query_ms"], rayjoin["lsi"]["lbvh"]["query_ms"])
        self.assertLess(rayjoin["pip"]["rt"]["query_ms"], rayjoin["pip"]["lbvh"]["query_ms"])

    def test_rtdl_backends_preserve_same_stream_parity(self) -> None:
        for workload in ("lsi", "pip"):
            artifact = self.evidence["rtdl"][workload]
            self.assertEqual(artifact["reference_backend"], "cpu")
            self.assertEqual(artifact["query_count"], 100000)
            self.assertGreater(artifact["reference_row_count"], 0)
            for backend in ("cpu", "embree", "optix"):
                item = artifact["backends"][backend]
                self.assertTrue(item["all_parity_vs_reference"], (workload, backend))
                self.assertEqual(item["parity_reference_backend"], "cpu")

    def test_interpretation_records_lsi_success_and_pip_weak_spot(self) -> None:
        derived = self.evidence["derived"]
        self.assertLess(derived["lsi"]["rtdl_optix_vs_cpu_ratio"], 0.1)
        self.assertGreater(derived["pip"]["rtdl_optix_vs_embree_ratio"], 10.0)
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not RayJoin-competitive", text)
        self.assertIn("PIP is the clearest weak spot", text)
        self.assertIn("Not authorized", text)


if __name__ == "__main__":
    unittest.main()
