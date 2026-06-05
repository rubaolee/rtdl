from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3534_rayjoin_v23_contract_baseline_probe.py"


class Goal3534RayJoinV23ContractBaselineProbeTest(unittest.TestCase):
    def test_dry_run_lists_common_contract_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-1000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3534.rayjoin_v23_contract_baseline_probe.v1")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(
            payload["common_contract_rows"],
            [
                "rayjoin_common_pip_prepared_optix_count",
                "rayjoin_common_lsi_prepared_optix_scalar_count",
                "rayjoin_common_overlay_seed_prepared_optix_active_count",
            ],
        )
        self.assertFalse(payload["claim_boundary"]["release_authorized"])

    def test_script_keeps_promoted_contracts_separate_from_v23_baselines(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "no_equivalent_contract_in_v23_evidence_checkout",
            "common_scalar_contract_measured",
            "common_scalar_output_contract_measured_but_v2_8_route_is_device_continuation_variant",
            "no_same_contract_v23_has_scalar_total_lsi_count_only",
            "prepared_optix",
            "median(phases_sec.prepared_query_sec)",
            "public_speedup_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
