from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal3613LsiLeftIdDenseCountExactPredicateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_left_id_dense_count_pipeline_switches_to_strict_predicate(self):
        needle = "segment-pair left-id count kernel predicate snippet not found"
        self.assertIn(needle, self.source)
        predicate_block_start = self.source.index("static void ensure_segment_pair_left_id_count_device_columns_pipeline()")
        predicate_block_end = self.source.index("static void finalize_segment_pair_intersection_rows", predicate_block_start)
        block = self.source[predicate_block_start:predicate_block_end]
        self.assertIn("old_candidate_predicate", block)
        self.assertIn("new_exact_predicate", block)
        self.assertIn("seg_intersect_conservative_candidate(", block)
        self.assertIn("float hit_t = 0.0f;", block)
        self.assertIn("seg_intersect(", block)
        self.assertIn("&hit_t, &ix, &iy", block)


if __name__ == "__main__":
    unittest.main()
