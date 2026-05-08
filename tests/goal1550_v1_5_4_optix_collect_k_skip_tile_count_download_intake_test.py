from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1550_v1_5_4_optix_collect_k_skip_tile_count_download_intake_2026-05-08.md"
CANDIDATE_JSON = ROOT / "docs" / "reports" / "goal1550_v1_5_4_optix_collect_k_skip_tile_count_download_candidate_probe_2026-05-08.json"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1549_v1_5_4_optix_collect_k_device_level_counts_candidate_probe_2026-05-08.json"


class Goal1550V154OptixCollectKSkipTileCountDownloadIntakeTest(unittest.TestCase):
    def test_candidate_reduces_metadata_downloads_against_goal1549(self) -> None:
        baseline = {
            case["candidate_count"]: case
            for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]
        }
        candidate_data = json.loads(CANDIDATE_JSON.read_text(encoding="utf-8"))
        candidate = {
            case["candidate_count"]: case
            for case in candidate_data["cases"]
        }

        self.assertIs(candidate_data["accepted_goal1506_evidence"], True)
        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                case = candidate[count]
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertLess(
                    case["stage_profile"]["topology"]["metadata_fields_downloaded"],
                    baseline[count]["stage_profile"]["topology"]["metadata_fields_downloaded"],
                )
                self.assertLess(
                    case["transfer_accounting"]["device_to_host_transfers_after_backend_execution"],
                    baseline[count]["transfer_accounting"]["device_to_host_transfers_after_backend_execution"],
                )

        self.assertEqual(candidate[131072]["stage_profile"]["topology"]["metadata_fields_downloaded"], 67)

    def test_report_bounds_claim(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("skips the tile emitted-count download", text)
        self.assertIn("reduced metadata transfer, not true zero-copy", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("0.320287", text)
        self.assertIn("0.312151", text)


if __name__ == "__main__":
    unittest.main()
