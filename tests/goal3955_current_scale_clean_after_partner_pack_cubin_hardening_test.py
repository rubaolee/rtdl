import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3955_current_scale_clean_after_partner_pack_cubin_hardening_2026-06-08"
)
SUMMARY_JSON = ARTIFACT_DIR / "goal3955_current_scale_clean_after_partner_pack_cubin.json"


class Goal3955CurrentScaleCleanAfterPartnerPackCubinHardeningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    def test_clean_commit_and_full_current_scale_pass(self) -> None:
        runtime = self.summary["runtime_environment"]
        self.assertEqual("d9c736c5", runtime["source_commit_short"])
        self.assertTrue(runtime["working_tree_clean"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", runtime["nvidia_smi"])
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(10, self.summary["json_pass_count"])
        self.assertEqual(10, len(self.summary["rows"]))
        self.assertEqual("accept", self.summary["validation"]["status"])

    def test_all_rows_are_claim_clean(self) -> None:
        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual("pass", row["status"])
                semantic = row["semantic_stdout_check"]
                self.assertTrue(semantic["stdout_json_parseable"])
                self.assertEqual([], semantic["claim_flag_violations"])
                self.assertGreater(row["stdout_bytes"], 0)

    def test_partner_and_optix_rows_are_present(self) -> None:
        top = self.summary["summary"]
        self.assertEqual(10, top["row_count"])
        self.assertEqual(
            [
                "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
                "rt_dbscan_optix_numba_scale_default_65536_no_validation",
                "barnes_hut_numba_scale_default_8192",
            ],
            top["numba_required_rows"],
        )
        self.assertEqual(10, len(top["optix_required_rows"]))

    def test_top_level_claim_boundaries_remain_false(self) -> None:
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(self.summary[flag])
            self.assertFalse(self.summary["summary"][flag])


if __name__ == "__main__":
    unittest.main()
