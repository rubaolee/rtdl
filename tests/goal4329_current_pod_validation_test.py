from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "docs" / "reports" / "goal4329_current_pod_validation"
REPORT = ROOT / "docs" / "reports" / "goal4329_current_pod_validation_2026-06-11.md"


class Goal4329CurrentPodValidationTest(unittest.TestCase):
    def _load(self, relative: str) -> dict:
        return json.loads((ARTIFACT_ROOT / relative).read_text(encoding="utf-8"))

    def test_report_records_boundary_and_pod_shape(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("NVIDIA RTX 4000 Ada Generation", text)
        self.assertIn("Goal763 bootstrap", text)
        self.assertIn("scale_summary_allpass.json", text)
        self.assertIn("does not authorize a release", text)

    def test_bootstrap_passed_focused_optix_tests(self) -> None:
        payload = self._load("bootstrap.json")
        self.assertEqual(payload["status"], "ok")
        steps = {step["name"]: step["result"] for step in payload["steps"]}
        native = steps["native_optix_focused_tests"]
        self.assertEqual(native["status"], "ok")
        self.assertEqual(native["returncode"], 0)
        self.assertIn("Ran 35 tests", native["stderr_tail"])

    def test_clean_scale_packet_is_all_pass_and_non_authorizing(self) -> None:
        payload = self._load("scale_summary_allpass.json")
        self.assertIs(payload["all_pass"], True)
        self.assertEqual(payload["json_pass_count"], 10)
        self.assertEqual(len(payload["rows"]), 10)
        self.assertTrue(all(row["status"] == "pass" for row in payload["rows"]))
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertIs(payload[key], False)
        self.assertFalse(
            any(row["semantic_stdout_check"]["claim_flag_violations"] for row in payload["rows"])
        )

    def test_initial_rayjoin_failure_is_fixture_staging_only(self) -> None:
        initial = self._load("scale_summary.json")
        self.assertIs(initial["all_pass"], False)
        failed = [row for row in initial["rows"] if row["status"] != "pass"]
        self.assertEqual(
            [row["row_id"] for row in failed],
            ["spatial_rayjoin_public_cdb_representative_mixed_route_scale_default"],
        )
        stderr = (
            ARTIFACT_ROOT
            / "scale_outputs"
            / "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default.stderr.txt"
        ).read_text(encoding="utf-8")
        self.assertIn("RayJoin public-CDB data directory not found", stderr)

        materialize = self._load("rayjoin_materialize_probe.json")
        self.assertIn("br_county_start256_count512.cdb", json.dumps(materialize))
        self.assertIn("br_soil_start256_count512.cdb", json.dumps(materialize))

        rerun = self._load("rayjoin_rerun_summary.json")
        self.assertIs(rerun["all_pass"], True)
        self.assertEqual(rerun["json_pass_count"], 1)


if __name__ == "__main__":
    unittest.main()
