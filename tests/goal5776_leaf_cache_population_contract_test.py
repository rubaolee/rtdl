from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5776_home_populate_leaf_cache_from_canonical_paths.sh"
FINAL = ROOT / "scripts" / "goal5776_home_final_frontdoor_trial.py"


class Goal5776LeafCachePopulationContractTest(unittest.TestCase):
    def test_all_nine_app_groups_and_exact_record_counts_are_sealed(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for label in (
            "triangle_reduction", "particle_relation", "hierarchy", "multiround",
        ):
            self.assertIn(label, source)
        self.assertIn('"triangle_reduction": 6', source)
        self.assertIn('"particle_relation": 12', source)
        self.assertIn('"hierarchy": 4', source)
        self.assertIn('"multiround": 6', source)
        self.assertIn("materialize_formal_numba_leaf_cache_manifest", source)
        self.assertIn('chmod -R a-w "${OUTPUT_ROOT}/cache"', source)

    def test_final_raydb_rayjoin_trial_requires_sealed_cache_hits(self) -> None:
        source = FINAL.read_text(encoding="utf-8")
        self.assertIn('cache_delta["hit_count"] <= 0', source)
        self.assertIn('cache_delta["miss_count"] != 0', source)
        self.assertIn('cache_delta["disabled_count"] != 0', source)
        self.assertIn("validate_behavioral_true_optix", source)


if __name__ == "__main__":
    unittest.main()
