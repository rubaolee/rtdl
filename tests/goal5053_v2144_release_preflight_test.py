from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5053_v2144_release_preflight.py"


class Goal5053V2144ReleasePreflightTest(unittest.TestCase):
    def test_preflight_script_records_current_release_gate_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "goal5053_preflight.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--allow-blocked",
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual("rtdl.goal5053.v2_14_4_release_preflight.v1", payload["schema"])
        self.assertEqual("ready_for_public_release_staging", payload["overall_status"])
        self.assertEqual([], payload["blockers"])
        review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
        self.assertIn("malformed", review_check)
        self.assertIn("malformed_reasons", review_check)
        self.assertEqual("pass", review_check["status"])
        self.assertEqual([], review_check["open"])
        self.assertEqual({}, review_check["malformed"])
        self.assertIn("review_v2_14_4_all_open_review_debt_2026-07-06.md", review_check["found"]["Goal5062"])
        strict_check = next(check for check in payload["checks"] if check["id"] == "strict_pod_smoke")
        self.assertEqual("pass", strict_check["status"])
        self.assertTrue(strict_check["observed_strict"])
        self.assertEqual("pass", strict_check["observed_overall_status"])
        legacy_check = next(check for check in payload["checks"] if check["id"] == "legacy_rayjoin_public_exports_disclosed")
        self.assertEqual("pass", legacy_check["status"])
        self.assertEqual(17, len(legacy_check["exports"]))
        self.assertIn("chains_to_rayjoin_cdb_segments", legacy_check["exports"])
        self.assertIn("PreparedOptixRayjoinCdbPointLocation2D", legacy_check["exports"])
        self.assertEqual([], legacy_check["unexpected_rayjoin_exports_from_rtdsl_all"])
        self.assertEqual(
            {
                "public_release_ready_without_review": True,
                "public_release_ready_without_pod_smoke": True,
                "v2_14_4_speedup_claim": True,
                "true_zero_copy_claim": True,
                "author_parity_claim": True,
                "device_group_by_public_ready": True,
            },
            payload["not_authorized"],
        )

    def test_public_leak_scan_is_part_of_the_gate(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("public_surface_internal_leak_scan", text)
        self.assertIn("Goal[0-9]+", text)
        self.assertIn("call_for_review|verdict", text)
        self.assertIn("history/internal_docs|internal_docs", text)
        self.assertIn("Paper-reproduction-apps", text)
        self.assertIn("legacy_rayjoin_public_exports_disclosed", text)
        self.assertIn("REVIEW_MIN_CHARACTERS", text)
        self.assertIn("REVIEW_MIN_GOAL_SECTION_CHARACTERS", text)
        self.assertIn("REVIEW_FORBIDDEN_PADDING_PHRASES", text)
        self.assertIn("CONSOLIDATED_REVIEW_PATTERNS", text)
        self.assertIn("EXPECTED_RAYJOIN_PUBLIC_EXPORTS", text)
        self.assertIn("_rayjoin_exports_from_init_all", text)

    def test_preflight_default_succeeds_when_release_gates_are_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "goal5053_preflight.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual("ready_for_public_release_staging", payload["overall_status"])

    def test_preflight_default_fails_when_a_malformed_review_is_present(self) -> None:
        probe = ROOT / "history" / "internal_docs" / "review_goal5062_template_probe.md"
        probe.write_text(
            "# Review for Goal5062\n\nverdict_label: approve\nblocking_findings: none\n",
            encoding="utf-8",
        )
        try:
            with tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / "goal5053_preflight.json"
                proc = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--output-json",
                        str(output),
                    ],
                    cwd=str(ROOT),
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(0, proc.returncode)
                payload = json.loads(output.read_text(encoding="utf-8"))
            review_check = next(check for check in payload["checks"] if check["id"] == "external_review_debt")
            self.assertIn("Goal5062", review_check["malformed_reasons"])
            reasons = review_check["malformed_reasons"]["Goal5062"]["review_goal5062_template_probe.md"]
            self.assertIn("too_short_min_800_characters", reasons)
        finally:
            probe.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
