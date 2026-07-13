from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_figure11_disposition.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5283_figure11_disposition_2026-07-09.json"
)
AUTHOR_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json"
)
RTDL_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json"
)
OFFLOAD_MAPPING = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5282_author_offload_mapping_2026-07-09.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location("build_xhd_figure11_disposition", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5283XhdFigure11DispositionTest(unittest.TestCase):
    def test_builder_closes_current_figure11_line_without_ratio(self) -> None:
        module = _load_script()
        artifact = module.build_figure11_disposition(
            author_matrix_path=AUTHOR_MATRIX,
            rtdl_matrix_path=RTDL_MATRIX,
            offload_mapping_path=OFFLOAD_MAPPING,
            date="2026-07-09",
        )
        self.assertEqual(
            artifact["status"],
            "figure11_closed_denominator_not_aligned_after_native_mapping",
        )
        self.assertTrue(artifact["matched"])
        self.assertTrue(artifact["decision"]["close_current_figure11_line"])
        self.assertFalse(artifact["decision"]["same_denominator_author_figure11"])
        self.assertFalse(artifact["decision"]["figure11_reproduced"])
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)

    def test_shape_only_candidate_is_not_a_figure11_row(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        candidate = payload["shape_only_candidate"]
        self.assertFalse(candidate["figure11_row"])
        self.assertFalse(candidate["paper_dataset_identity"])
        self.assertFalse(candidate["same_denominator_author_figure11"])
        self.assertEqual(candidate["author_shaped_fields"]["OffloadingSize"]["value"], 6)
        self.assertEqual(candidate["author_shaped_fields"]["WL Heavy Peak"]["bytes"], 48)
        self.assertEqual(
            candidate["rtdl_measured_fields"]["generic_heavy_offload_queue_peak"]["bytes"],
            96,
        )
        self.assertGreaterEqual(len(candidate["why_not_figure11_row"]), 4)

    def test_author_reference_and_rtdl_matrix_are_present_but_not_compared_by_ratio(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        author = payload["author_figure11_reference"]["datasets"]
        self.assertEqual(author["graphics"]["row_count"], 4)
        self.assertEqual(author["geo"]["row_count"], 3)
        self.assertIn("WL Heavy Peak", author["graphics"]["xhd_mean_breakdown_mb"])
        matrix = payload["rtdl_current_memory_matrix"]
        self.assertFalse(matrix["coverage"]["all_rows_same_denominator_author_figure11"])
        self.assertFalse(payload["claim_boundary"]["memory_ratio_claimed"])
        for forbidden in (
            "author_vs_rtdl_memory_ratio",
            "xhd_memory_ratio",
            "figure11_memory_ratio_value",
        ):
            self.assertNotIn(forbidden, payload)


if __name__ == "__main__":
    unittest.main()
