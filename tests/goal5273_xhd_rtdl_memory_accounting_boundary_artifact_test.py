import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5273_rtdl_memory_accounting_boundary_2026-07-09.json"
)


class Goal5273RtdlMemoryAccountingBoundaryArtifactTest(unittest.TestCase):
    def _artifact(self):
        return json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_declares_non_reproduction_boundary(self):
        payload = self._artifact()
        self.assertEqual(
            payload["status"],
            "rtdl_memory_accounting_boundary_ready__figure11_not_reproduced",
        )
        boundary = payload["claim_boundary"]
        for key in (
            "figure11_reproduced",
            "author_memory_parity_claimed",
            "exact_gpu_allocator_measurement_claimed",
            "author_bvh_memory_measured_by_rtdl",
            "author_heavy_worklist_peak_measured_by_rtdl",
            "performance_ratio_claimed",
        ):
            self.assertFalse(boundary[key], key)

    def test_exact_witness_rows_keep_unavailable_author_fields_explicit(self):
        payload = self._artifact()
        rows = payload["graphics_exact_witness_rows"]
        self.assertEqual(
            set(rows),
            {
                "Dragon\nAsian Dragon",
                "Dragon\nBuddha",
                "Thai\nAsian Dragon",
                "Thai\nBuddha",
            },
        )
        for row in rows.values():
            accounting = row["rtdl_accounting"]
            fields = accounting["author_mapped_fields"]
            self.assertEqual(
                fields["BVH"]["status"],
                "unavailable_opaque_native_acceleration_memory_not_reported",
            )
            self.assertIsNone(fields["BVH"]["bytes"])
            self.assertEqual(
                fields["WL Heavy Peak"]["status"],
                "unavailable_no_author_heavy_offload_equivalent_in_current_rtdl_route",
            )
            self.assertIsNone(fields["WL Heavy Peak"]["bytes"])
            self.assertGreater(fields["Grid"]["bytes"], 0)
            self.assertGreater(fields["MBRs B"]["bytes"], 0)

    def test_frontier_example_has_nonzero_worklist_but_is_not_figure11_row(self):
        payload = self._artifact()
        example = payload["frontier_route_accounting_example"]
        self.assertIn("not a Figure 11 reproduction row", example["why_included"])
        wl = example["rtdl_accounting"]["author_mapped_fields"]["WL"]
        self.assertIn("frontier_row_capacity", wl["status"])
        self.assertGreater(wl["bytes"], 0)


if __name__ == "__main__":
    unittest.main()
