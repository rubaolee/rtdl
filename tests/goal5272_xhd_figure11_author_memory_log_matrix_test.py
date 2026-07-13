import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5272_figure11_author_memory_log_matrix_2026-07-09.json"
)


class Goal5272Figure11AuthorMemoryLogMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_author_draw_mem_contract_is_encoded(self):
        self.assertEqual(
            self.data["schema"],
            "rtdl.paper_reproduction.xhd.figure11_author_memory_log_matrix.v1",
        )
        self.assertEqual(
            self.data["author_draw_script"],
            "/tmp/xhd-goal5112/author/expr/draw_mem.py",
        )
        self.assertEqual(
            [row["label"] for row in self.data["methods"]],
            ["NN-KD", "NN-Clover", "X-HD"],
        )

    def test_geo_and_graphics_rows_match_author_figure11_scope(self):
        geo = self.data["datasets"]["geo"]
        graphics = self.data["datasets"]["graphics"]
        self.assertEqual(geo["row_count"], 3)
        self.assertEqual(graphics["row_count"], 4)
        self.assertIn("USCounty\nUSZipcode", geo["rows"])
        self.assertIn("OSMLakes\nOSMParks", geo["rows"])
        self.assertIn("Dragon\nAsian Dragon", graphics["rows"])
        self.assertIn("Thai\nBuddha", graphics["rows"])
        for section in [geo, graphics]:
            for row in section["rows"].values():
                for method in ["NN-KD", "NN-Clover", "X-HD"]:
                    self.assertIn(method, row)
                    self.assertGreater(row[method], 0.0)

    def test_xhd_breakdown_uses_draw_mem_sum_of_components_contract(self):
        graphics = self.data["datasets"]["graphics"]
        row = graphics["rows"]["Dragon\nAsian Dragon"]
        breakdown = graphics["xhd_breakdown_mb"]["Dragon\nAsian Dragon"]
        self.assertAlmostEqual(
            row["X-HD"],
            sum(breakdown.values()),
            places=9,
        )
        self.assertEqual(
            sorted(breakdown),
            ["BVH", "Grid", "MBRs B", "WL", "WL Heavy Peak"],
        )

    def test_claim_boundary_forbids_figure11_and_rtdl_memory_claims(self):
        boundary = self.data["claim_boundary"]
        for key in [
            "figure11_reproduced",
            "full_paper_reproduction_claimed",
            "exact_paper_dataset_identity_claimed",
            "rtdl_memory_parity_claimed",
            "performance_ratio_claimed",
        ]:
            self.assertFalse(boundary[key], key)


if __name__ == "__main__":
    unittest.main()
