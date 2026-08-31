from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3534_rayjoin_v23_contract_baseline_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3534_rayjoin_v23_contract_baseline_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3534_rayjoin_v23_contract_baseline_a5000" / "summary.json"


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

    def test_a5000_artifact_records_common_contract_baselines(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3534.rayjoin_v23_contract_baseline_probe.v1")
        self.assertEqual(payload["v23_commit"], "2a28365d0246d51f3e3322b546f8a68c58632db4")
        self.assertEqual(payload["v28_commit"], "c237b0db296c890455661b16e6066c1c71ee2e97")
        self.assertEqual(payload["repeats"], 7)
        rows = {row["row_id"]: row for row in payload["common_contract_comparisons"]}
        self.assertAlmostEqual(rows["rayjoin_common_pip_prepared_optix_count"]["v28_speedup_vs_v23"], 1.0315161678998916)
        self.assertAlmostEqual(rows["rayjoin_common_lsi_prepared_optix_scalar_count"]["v28_speedup_vs_v23"], 1.0039245628769948)
        self.assertAlmostEqual(rows["rayjoin_common_overlay_seed_prepared_optix_active_count"]["v28_speedup_vs_v23"], 1.0395339208149745)
        for row in payload["common_contract_comparisons"]:
            self.assertFalse(row["claim_boundary"]["release_authorized"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])

    def test_a5000_artifact_classifies_promoted_rows_honestly(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        promoted = {row["row_id"]: row for row in payload["v2_8_promoted_rows_without_v23_equivalent"]}
        self.assertEqual(
            promoted["rayjoin_count_parity_pip_prepared_optix"]["v23_equivalent_status"],
            "common_scalar_contract_measured",
        )
        self.assertEqual(
            promoted["rayjoin_count_parity_lsi_left_id_dense_count"]["v23_equivalent_status"],
            "no_same_contract_v23_has_scalar_total_lsi_count_only",
        )
        self.assertEqual(
            promoted["rayjoin_relation_columns_cdb_pair"]["v23_equivalent_status"],
            "no_equivalent_contract_in_v23_evidence_checkout",
        )

    def test_report_states_no_fake_ratios(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "refuses fake comparisons",
            "about `1.00x` to `1.04x`",
            "mostly v2.8-only evidence",
            "not ratio-able against v2.3",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
