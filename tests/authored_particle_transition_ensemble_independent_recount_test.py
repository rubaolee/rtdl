from pathlib import Path
import unittest

from scripts import authored_particle_transition_ensemble_independent_recount as recount


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = (
    ROOT / "history/internal_docs/v4_authored_particle_20260909" /
    "formal_natural_7e4362ef9/RAW_FORMAL_EVIDENCE.tar.gz"
)


class AuthoredParticleTransitionEnsembleIndependentRecountTest(unittest.TestCase):
    def test_schedule_and_bootstrap_are_fixed(self):
        self.assertEqual(recount.QUERY_COUNT, 160_000_000)
        self.assertEqual(len(recount.ORDERS), 8)
        self.assertEqual(sum(row[0] == "rtdl" for row in recount.ORDERS), 4)
        self.assertEqual(sum(row[0] == "pyoptix" for row in recount.ORDERS), 4)
        values = [0.45, 0.48, 0.49, 0.50, 0.51, 0.52, 0.53, 0.54]
        self.assertEqual(
            recount.bootstrap_interval(values),
            recount.bootstrap_interval(values))

    def test_preserved_archive_recounts_without_controller_import(self):
        result = recount.recount(archive=ARCHIVE, source_repo=ROOT)
        self.assertEqual(
            result["status"],
            "PASS__SEPARATE_SCRIPT_RAW_RECONSTRUCTION__LEAD_RECOUNT_PENDING")
        self.assertTrue(result["engineering_targets_passed"])
        self.assertEqual(result["formal_worker_count"], 16)
        self.assertLess(result["paired_median_rtdl_over_pyoptix"], 1.20)
        self.assertLess(result["worst_block_rtdl_over_pyoptix"], 1.35)


if __name__ == "__main__":
    unittest.main()
