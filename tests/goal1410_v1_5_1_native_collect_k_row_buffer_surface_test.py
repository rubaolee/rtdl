from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1410V151NativeCollectKRowBufferSurfaceTest(unittest.TestCase):
    def test_embree_collection_wrapper_exposes_generic_row_buffer_metadata(self) -> None:
        runtime = (ROOT / "src/rtdsl/embree_runtime.py").read_text(encoding="utf-8")

        self.assertIn("from .v1_5_1_collect_k_bounded import collect_k_bounded_rows", runtime)
        self.assertIn("from .v1_5_1_collect_k_bounded import validate_collect_k_bounded_result", runtime)
        self.assertIn("row_buffer = collect_k_bounded_rows(candidate_pairs", runtime)
        self.assertIn('validate_collect_k_bounded_result(result, row_width=2, backend="embree")', runtime)
        self.assertIn('"app_generic": row_buffer["app_generic"]', runtime)
        self.assertIn('"candidate_id_rows": row_buffer["candidate_id_rows"]', runtime)
        self.assertIn('"valid_count": row_buffer["valid_count"]', runtime)
        self.assertIn('"generic_result_layout": row_buffer["result_layout"]', runtime)
        self.assertIn('"partial_result_on_overflow_allowed": row_buffer[', runtime)
        self.assertIn('"score_or_reduction_after_overflow_allowed": row_buffer[', runtime)

    def test_optix_collection_wrapper_exposes_generic_row_buffer_metadata(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")

        self.assertIn("from .v1_5_1_collect_k_bounded import collect_k_bounded_rows", runtime)
        self.assertIn("from .v1_5_1_collect_k_bounded import validate_collect_k_bounded_result", runtime)
        self.assertIn("row_buffer = collect_k_bounded_rows(candidate_pairs", runtime)
        self.assertIn('validate_collect_k_bounded_result(result, row_width=2, backend="optix")', runtime)
        self.assertIn('"app_generic": row_buffer["app_generic"]', runtime)
        self.assertIn('"candidate_id_rows": row_buffer["candidate_id_rows"]', runtime)
        self.assertIn('"valid_count": row_buffer["valid_count"]', runtime)
        self.assertIn('"generic_result_layout": row_buffer["result_layout"]', runtime)
        self.assertIn('"partial_result_on_overflow_allowed": row_buffer[', runtime)
        self.assertIn('"score_or_reduction_after_overflow_allowed": row_buffer[', runtime)

    def test_old_app_facing_candidate_pairs_field_is_preserved_during_transition(self) -> None:
        for relative in ("src/rtdsl/embree_runtime.py", "src/rtdsl/optix_runtime.py"):
            runtime = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn('"candidate_pairs": candidate_pairs', runtime)
            self.assertIn('"result_layout": "bounded_candidate_pair_ids"', runtime)


if __name__ == "__main__":
    unittest.main()
