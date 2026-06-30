from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class V4Goal4806RayJoinSection57DataAcquisitionAuditTest(unittest.TestCase):
    def test_audit_reports_exact_and_same_source_coverage_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_json = root / "audit.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_data_acquisition_audit.py",
                    "--dataset-root",
                    str(root / "missing_dataset"),
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)
            file_payload = json.loads(output_json.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal4806.rayjoin_section57_data_acquisition_audit.v1")
        self.assertEqual(file_payload["schema"], payload["schema"])
        self.assertEqual(payload["exact_overlay_pairs_ready"], 0)
        self.assertEqual(payload["exact_overlay_pairs_total"], 8)
        self.assertIn("missing_exact_section57_cdb_inputs", payload["blockers"])
        self.assertIn("same_source_generation_missing_lakes_parks_targets", payload["blockers"])
        scope = payload["same_source_generation_scope"]
        self.assertEqual(scope["supported_pairs"], ["county_zipcode", "block_water"])
        self.assertIn("lkaf_pkaf", scope["unsupported_pairs"])
        self.assertIn("not a recovered paper_preprocessed_cdb", scope["claim_boundary"])
        self.assertFalse(payload["network"]["checked"])

    def test_audit_counts_ready_exact_inputs_but_preserves_lakes_parks_gap(self) -> None:
        from rtdsl.rayjoin_paper_suite import paper_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset_root = root / "rayjoin_section57_cdb"
            for pair in paper_pairs(pair_ids=("county_zipcode", "block_water")):
                for relative in (pair.left_relative_path, pair.right_relative_path):
                    path = dataset_root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("1 2 1 2 1 0\n0 0\n1 0\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_section57_data_acquisition_audit.py",
                    "--dataset-root",
                    str(dataset_root),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            payload = json.loads(completed.stdout)

        self.assertEqual(payload["exact_overlay_pairs_ready"], 2)
        by_pair = {row["pair_id"]: row for row in payload["pair_rows"]}
        self.assertTrue(by_pair["county_zipcode"]["exact_input_ready"])
        self.assertTrue(by_pair["block_water"]["exact_input_ready"])
        self.assertFalse(by_pair["lkaf_pkaf"]["exact_input_ready"])
        self.assertTrue(by_pair["block_water"]["same_source_generation_supported"])
        self.assertFalse(by_pair["lkna_pkna"]["same_source_generation_supported"])


if __name__ == "__main__":
    unittest.main()
