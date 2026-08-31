from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.public_rt_vs_embree_comparison import (
    markdown_public_rt_vs_embree_comparison,
    public_rt_vs_embree_comparison_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_public_rt_vs_embree_comparison.py"


class Goal4348PublicRtVsEmbreeComparisonTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = public_rt_vs_embree_comparison_packet()

    def test_validation_accepts_and_main_rows_are_optix_phase_wins(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertTrue(self.payload["summary"]["prepared_phase_wording_ready"])
        self.assertEqual(
            self.payload["summary"]["main_ratio_row_count"],
            self.payload["summary"]["optix_faster_row_count"],
        )
        self.assertGreaterEqual(
            self.payload["summary"]["min_optix_speedup_vs_embree_on_optix_win_rows"],
            1.2,
        )
        self.assertFalse(self.payload["summary"]["whole_app_speedup_claim_authorized"])

    def test_contact_micro_row_is_excluded_and_broadphase_replaces_it(self) -> None:
        main_contact = [row for row in self.payload["main_rows"] if row["app"] == "contact_manifold"]
        self.assertEqual(1, len(main_contact))
        self.assertIn("generic_aabb_broadphase", main_contact[0]["contract"])
        self.assertEqual(16384, main_contact[0]["grid_count"])
        self.assertGreater(main_contact[0]["embree_divided_by_optix"], 1.2)

        excluded_contracts = {row["contract"] for row in self.payload["excluded_main_ratio_rows"]}
        self.assertIn("native_collect_k_bounded_witness_rows", excluded_contracts)
        diagnostics = self.payload["contact_native_collect_diagnostics"]
        self.assertEqual(3, len(diagnostics))
        self.assertTrue(all(row["repeat_count"] == 10000 for row in diagnostics))

    def test_contact_scale_rows_show_tiny_case_and_larger_scale(self) -> None:
        rows = {row["grid_count"]: row for row in self.payload["contact_broadphase_scale_rows"]}
        self.assertEqual({64, 512, 4096, 16384}, set(rows))
        self.assertEqual("embree", rows[64]["faster_backend"])
        self.assertEqual("optix", rows[512]["faster_backend"])
        self.assertEqual("optix", rows[4096]["faster_backend"])
        self.assertEqual("optix", rows[16384]["faster_backend"])

    def test_markdown_contains_table_and_public_wording(self) -> None:
        markdown = markdown_public_rt_vs_embree_comparison(self.payload)
        self.assertIn("Prepared Phase Table", markdown)
        self.assertIn("Contact Manifold", markdown)
        self.assertIn("not whole-application speedups", markdown)
        self.assertIn("RTX 4000 Ada", markdown)

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "packet.json"
            out_md = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Prepared Phase Table", report)
            self.assertIn("contact_manifold", report)


if __name__ == "__main__":
    unittest.main()
