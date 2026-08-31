from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3867_full_scale_after_rayjoin_representative_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3867_full_scale_after_rayjoin_representative_a5000" / "summary.json"


class Goal3867FullScaleAfterRayJoinRepresentativeTest(unittest.TestCase):
    def test_full_packet_passes_all_ten_rows(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertEqual(payload["validation"]["status"], "accept")
        self.assertEqual(payload["validation"]["errors"], [])

        rows = payload["rows"]
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        self.assertTrue(all(row["semantic_stdout_check"]["stdout_json_parseable"] for row in rows))
        self.assertTrue(all(not row["semantic_stdout_check"]["claim_flag_violations"] for row in rows))

    def test_rayjoin_row_is_representative_and_long_enough(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rayjoin = next(row for row in payload["rows"] if row["app"] == "spatial_rayjoin")
        self.assertEqual(
            rayjoin["row_id"],
            "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
        )
        self.assertGreater(rayjoin["elapsed_sec"], 9.0)
        self.assertEqual(rayjoin["expected_runtime_class"], "representative_mixed_route_public_cdb")
        self.assertTrue(rayjoin["semantic_stdout_check"]["stdout_json_parseable"])
        self.assertEqual(rayjoin["semantic_stdout_check"]["claim_flag_violations"], [])
        self.assertGreater(rayjoin["stderr_bytes"], 0)
        self.assertIn("goal3866_rayjoin_representative_scale_profile.py", " ".join(rayjoin["command"]))

    def test_report_documents_boundary_and_result_table(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3867", text)
        self.assertIn("all_pass: true", text)
        self.assertIn("spatial_rayjoin_public_cdb_representative_mixed_route_scale_default", text)
        self.assertIn("does not authorize release action", text)
        self.assertIn("automatic partner selection", text)


if __name__ == "__main__":
    unittest.main()
