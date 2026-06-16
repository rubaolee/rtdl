from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src/native/embree/rtdl_embree_api.cpp"
PRELUDE = ROOT / "src/native/embree/rtdl_embree_prelude.h"
RUNTIME = ROOT / "src/rtdsl/embree_runtime.py"
INIT = ROOT / "src/rtdsl/__init__.py"
SCRIPT = ROOT / "scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py"
REPORT = ROOT / "docs/reports/goal4430_v3_0_m33_rayjoin_overlay_active_count_same_contract_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4430_v3_0_m33_rayjoin_overlay_active_count_same_contract_2026-06-16.json"
)


class Goal4430V30M33RayjoinOverlayActiveCountSameContractTest(unittest.TestCase):
    def test_embree_native_surface_adds_generic_prepared_active_count(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for phrase in (
            "RtdlEmbreeShapePairActiveCount2D",
            "rtdl_embree_shape_pair_active_count_2d_create",
            "rtdl_embree_shape_pair_active_count_2d_count",
            "rtdl_embree_shape_pair_active_count_2d_destroy",
        ):
            self.assertIn(phrase, prelude)
            self.assertIn(phrase, api)

        count_start = api.index("RTDL_EMBREE_EXPORT int rtdl_embree_shape_pair_active_count_2d_count")
        count_end = api.index("RTDL_EMBREE_EXPORT void rtdl_embree_shape_pair_active_count_2d_destroy", count_start)
        count_body = api[count_start:count_end]
        self.assertIn("run_query_index_ranges", count_body)
        self.assertIn("active_count_out", count_body)
        self.assertIn("total_count.fetch_add", count_body)
        self.assertIn("shape_pair_needs_containment_continuation", count_body)
        self.assertNotIn("RtdlShapePairRelationRow", count_body)
        self.assertNotIn("copy_rows_out", count_body)
        for forbidden in ("rayjoin", "county", "soil", "zipcode"):
            self.assertNotIn(forbidden, count_body.lower())

    def test_python_runtime_exports_prepared_embree_shape_pair_active_count(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        init = INIT.read_text(encoding="utf-8")
        for phrase in (
            "class PreparedEmbreeShapePairActiveCount2D",
            "def prepare_embree_shape_pair_active_count_2d",
            "rtdl_embree_shape_pair_active_count_2d_count",
            "row_materialization_avoided",
            "overlay_active_pair_dependency_count",
        ):
            self.assertIn(phrase, runtime)
        self.assertIn("prepare_embree_shape_pair_active_count_2d", init)
        self.assertIn("PreparedEmbreeShapePairActiveCount2D", init)

    def test_runner_dry_run_rejects_old_raw_relation_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=str(ROOT),
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["planned"]["output_contract"], "overlay_active_pair_dependency_count")
        self.assertEqual(set(payload["planned"]["same_contract_backends"]), {"embree", "optix"})
        self.assertTrue(payload["comparison"]["old_raw_relation_row_contract_rejected"])
        self.assertFalse(payload["claim_boundary"]["full_polygon_overlay_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_report_records_m33_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "old fair-run overlay row",
            "generic prepared 2-D shape-pair active-count primitive",
            "overlay_active_pair_dependency_count",
            "Full polygon overlay materialization",
            "no public speedup wording",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_same_contract_embree_and_optix_rows(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M33 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        comparison = payload["comparison"]
        self.assertTrue(comparison["same_output_contract"])
        self.assertTrue(comparison["active_counts_match"])
        self.assertTrue(comparison["all_counts_stable"])
        self.assertTrue(comparison["all_row_materialization_avoided"])
        self.assertTrue(comparison["old_raw_relation_row_count_not_comparable"])
        self.assertFalse(comparison["public_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        self.assertEqual(rows["embree"]["output_contract"], rows["optix"]["output_contract"])
        self.assertEqual(rows["embree"]["active_count"], rows["optix"]["active_count"])
        self.assertEqual(rows["embree"]["execution_route"], "prepared_embree_shape_pair_active_count_2d")
        self.assertEqual(
            rows["optix"]["execution_route"],
            "prepared_optix_shape_pair_active_count_device_continuation_reuse",
        )
        for row in rows.values():
            self.assertGreater(row["timed_total_sec"], 0.0)
            self.assertTrue(row["row_materialization_avoided"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
