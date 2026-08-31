from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"
AUTHOR_PLY_LOADER_EVIDENCE = ROOT / "history" / "internal_docs" / "goal5238_xhd_author_ply_loader_translation_contract_result_2026-07-09.md"

sys.path.insert(0, str(SCRIPT_DIR))

from xhd_input_loader import translate_point_matrix_to_min_bound


class Goal5238XhdAuthorPlyLoaderTranslationContractTest(unittest.TestCase):
    def test_rtdl_app_translation_matches_author_ply_loader_min_bound_contract(self) -> None:
        matrix = np.asarray(
            [
                [10.0, -2.0, 5.0],
                [13.0, 4.0, -7.0],
                [7.5, 1.5, 9.0],
            ],
            dtype=np.float64,
        )

        translated = translate_point_matrix_to_min_bound(matrix.copy(), copy=False)

        np.testing.assert_allclose(
            translated,
            np.asarray(
                [
                    [2.5, 0.0, 12.0],
                    [5.5, 6.0, 0.0],
                    [0.0, 3.5, 16.0],
                ],
                dtype=np.float64,
            ),
        )
        np.testing.assert_allclose(translated.min(axis=0), np.zeros(3, dtype=np.float64))

    def test_translation_contract_is_documented_as_app_owned_not_core_semantics(self) -> None:
        text = AUTHOR_PLY_LOADER_EVIDENCE.read_text(encoding="utf-8")
        collapsed = " ".join(text.split())
        self.assertIn("LoadPLY", text)
        self.assertIn("v[i] = (v[i] - vmin[i])", text)
        self.assertIn("app-owned preprocessing", text)
        self.assertIn("RTDL core", text)
        self.assertIn("not a generic RTDL coordinate transform", collapsed)


if __name__ == "__main__":
    unittest.main()
