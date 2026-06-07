from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal3691_rayjoin_original_same_source_probe.py"
REPORT = ROOT / "docs/reports/goal3691_rayjoin_original_same_source_probe_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3691_rayjoin_original_same_source_probe_a5000/summary.json"


class Goal3691RayJoinOriginalSameSourceProbeTest(unittest.TestCase):
    def test_probe_runs_original_rayjoin_and_rtdl_same_sources(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("release\" / \"bin\" / \"query_exec", source)
        self.assertIn("rtdl_cross_map_native_relation_status_corrected_scalar_count_executor", source)
        self.assertIn("_run_exact_lsi_prepared_optix", source)
        self.assertIn("br_county_clean_25_odyssey_final.txt", source)
        self.assertIn("br_soil_ascii_odyssey_final.txt", source)
        self.assertIn("pip_query_speedup_rtdl_vs_rayjoin", source)
        self.assertIn("lsi_query_speedup_rtdl_vs_rayjoin", source)
        self.assertIn("goal3691_scoped_source_dirty", source)
        self.assertIn("SCOPED_SOURCE_PATHS", source)

    def test_probe_preserves_claim_boundaries_and_contract_caveats(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"rayjoin_paper_reproduction_claim_authorized": False', source)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', source)
        self.assertIn('"rt_core_speedup_claim_authorized": False', source)
        self.assertIn('"native_default_route_authorized": False', source)
        self.assertIn('"pip_count_comparable_to_rayjoin": False', source)
        self.assertIn("RayJoin query_exec timing output does not print the PIP hit count", source)
        self.assertIn("lsi_count_delta_rtdl_minus_rayjoin", source)

    def test_report_states_pip_win_and_lsi_blocker(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Cross-map PIP is promising", report)
        self.assertIn("LSI is still a blocker", report)
        self.assertIn("RTDL reports `20859`, RayJoin reports `20860`", report)
        self.assertIn("does not authorize", report)

    def test_a5000_artifact_same_source_probe(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3691.rayjoin_original_same_source_probe.v1")
        self.assertEqual(payload["rtdl_source_commit_short"], "c8f9adf0")
        self.assertFalse(payload["goal3691_scoped_source_dirty"])
        self.assertEqual(payload["rayjoin_source_commit_short"], "02bf622")
        self.assertIn("M src/util/markers.h", payload["rayjoin_git_status_short"])
        self.assertFalse(payload["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        comparison = payload["comparison"]
        self.assertFalse(comparison["pip_count_comparable_to_rayjoin"])
        self.assertGreater(comparison["pip_query_speedup_rtdl_vs_rayjoin"], 1.0)
        self.assertLess(comparison["lsi_query_speedup_rtdl_vs_rayjoin"], 1.0)
        self.assertEqual(comparison["rayjoin_lsi_intersections"], 20860)
        self.assertEqual(comparison["rayjoin_lsi_check_intersections"], 20860)
        self.assertEqual(comparison["rtdl_lsi_row_count"], 20859)
        self.assertEqual(comparison["lsi_count_delta_rtdl_minus_rayjoin"], -1)


if __name__ == "__main__":
    unittest.main()
