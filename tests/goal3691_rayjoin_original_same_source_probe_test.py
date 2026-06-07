from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal3691_rayjoin_original_same_source_probe.py"


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


if __name__ == "__main__":
    unittest.main()
