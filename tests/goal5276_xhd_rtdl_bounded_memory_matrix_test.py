import importlib.util
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MATRIX_HELPER = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "xhd_rtdl_memory_matrix.py"
RESULT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5276_rtdl_bounded_memory_matrix_2026-07-09.json"
SAMPLE = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json"


def _load_helper():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_memory_matrix_goal5276", MATRIX_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {MATRIX_HELPER}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(MATRIX_HELPER.parent))
    spec.loader.exec_module(module)
    return module


class Goal5276XhdRtdlBoundedMemoryMatrixTest(unittest.TestCase):
    def test_helper_builds_status_bearing_row_without_author_ratio(self):
        helper = _load_helper()
        matrix = helper.build_rtdl_memory_matrix(
            [(SAMPLE, "sample256")],
            date="2026-07-09",
        )
        self.assertEqual(matrix["schema"], "rtdl.paper_reproduction.xhd.rtdl_memory_matrix.v1")
        self.assertFalse(matrix["claim_boundary"]["figure11_reproduced"])
        self.assertFalse(matrix["claim_boundary"]["author_memory_parity_claimed"])
        self.assertFalse(matrix["claim_boundary"]["same_denominator_author_figure11_claimed"])
        self.assertEqual(matrix["coverage"]["measured_bvh_rows"], 1)
        row = matrix["rows"][0]
        self.assertEqual(row["row_label"], "sample256")
        self.assertFalse(row["same_denominator_author_figure11"])
        self.assertEqual(
            row["author_mapped_fields"]["BVH"]["status"],
            "measured_native_optix_accel_output_buffer",
        )
        self.assertEqual(row["author_mapped_fields"]["BVH"]["bytes"], 7552)
        self.assertEqual(
            row["author_mapped_fields"]["WL"]["status"],
            "estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
        )
        self.assertIn(
            "author WL is in_queue + miss_queue",
            row["author_mapped_fields"]["WL"]["method"],
        )
        self.assertIsNone(row["author_mapped_fields"]["WL Heavy Peak"]["bytes"])
        self.assertEqual(
            row["rtdl_only_fields"]["native_accel_build_temp"]["status"],
            "measured_native_optix_transient_accel_build_workspace",
        )

    def test_artifact_keeps_figure11_boundaries_false(self):
        matrix = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(matrix["status"], "rtdl_bounded_memory_matrix_ready__figure11_not_reproduced")
        self.assertEqual(matrix["row_count"], 2)
        self.assertEqual(matrix["coverage"]["measured_bvh_rows"], 2)
        self.assertEqual(matrix["coverage"]["wl_heavy_peak_unavailable_rows"], 2)
        self.assertFalse(matrix["coverage"]["all_rows_same_denominator_author_figure11"])
        for key, value in matrix["claim_boundary"].items():
            self.assertFalse(value, key)
        for row in matrix["rows"]:
            self.assertTrue(row["native_memory_telemetry_collected"])
            self.assertFalse(row["same_denominator_author_figure11"])
            self.assertEqual(
                row["author_mapped_fields"]["WL"]["status"],
                "estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue",
            )
            self.assertEqual(
                row["native_memory_telemetry_schema"],
                "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v1",
            )


if __name__ == "__main__":
    unittest.main()
