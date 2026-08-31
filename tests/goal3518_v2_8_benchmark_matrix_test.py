import unittest

import rtdsl


class Goal3518V28BenchmarkMatrixTest(unittest.TestCase):
    def test_matrix_covers_all_ten_promoted_apps(self):
        rows = rtdsl.v2_8_benchmark_matrix()
        apps = {row["app"] for row in rows}

        self.assertEqual(apps, set(rtdsl.V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertGreaterEqual(len(rows), len(rtdsl.V2_8_PROMOTED_BENCHMARK_APPS))
        self.assertIn("spatial_rayjoin_overlay_area_exact_prepared", {row["row_id"] for row in rows})
        self.assertIn("hausdorff_xhd_exact_rt_nearest_witness", {row["row_id"] for row in rows})

    def test_classifications_are_explicit_and_use_all_lanes(self):
        rows = rtdsl.v2_8_benchmark_matrix()
        classes = {row["classification"] for row in rows}

        self.assertEqual(classes, set(rtdsl.V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS))
        for row in rows:
            self.assertIn(row["classification"], rtdsl.V2_8_BENCHMARK_MATRIX_CLASSIFICATIONS)
            self.assertNotEqual(row["partner"].strip().lower(), "n/a")

    def test_timing_cells_are_filled_or_explained(self):
        rows = rtdsl.v2_8_benchmark_matrix()

        for row in rows:
            self.assertIsInstance(row["steady_state_sec"], float)
            self.assertGreaterEqual(row["steady_state_sec"], 0.0)
            for key in (
                "setup_status",
                "warmup_status",
                "steady_state_status",
                "correctness_status",
                "claim_boundary_status",
                "notes",
            ):
                value = row[key].strip()
                self.assertTrue(value, f"{row['row_id']} has empty {key}")
                self.assertNotEqual(value.lower(), "n/a", f"{row['row_id']} has n/a {key}")

    def test_claim_boundaries_remain_false(self):
        rows = rtdsl.v2_8_benchmark_matrix()

        for row in rows:
            for flag in (
                "release_authorized",
                "public_speedup_claim_authorized",
                "whole_app_speedup_claim_authorized",
                "rt_core_speedup_claim_authorized",
                "true_zero_copy_claim_authorized",
                "paper_reproduction_claim_authorized",
                "app_specific_engine_logic_allowed",
            ):
                self.assertIs(row[flag], False, f"{row['row_id']} leaked {flag}")

        summary = rtdsl.summarize_v2_8_benchmark_matrix()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], len(rows))
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])

    def test_overlay_steady_state_formula_is_explicit(self):
        rows = {row["row_id"]: row for row in rtdsl.v2_8_benchmark_matrix()}
        overlay = rows["spatial_rayjoin_overlay_area_exact_prepared"]

        expected = 0.0038709240034222603 + 0.05171292740851641 + 0.014305617660284042
        self.assertAlmostEqual(overlay["steady_state_sec"], expected, places=15)
        self.assertIn("0.0038709240034222603 relation stream", overlay["notes"])
        self.assertIn("0.05171292740851641 device planner", overlay["notes"])
        self.assertIn("0.014305617660284042 tile executor", overlay["notes"])

    def test_validator_accepts_current_matrix(self):
        validation = rtdsl.validate_v2_8_benchmark_matrix()

        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        self.assertEqual(validation["app_count"], 10)


if __name__ == "__main__":
    unittest.main()
