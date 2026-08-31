from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from goal5776_estimate_formal_runtime import estimate, _load_roots
from goal5776_real_scale_formal_contract import schedule


class Goal5776FormalRuntimeBudgetTest(unittest.TestCase):
    def test_combined_home_result_file_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "combined.json"
            path.write_text(json.dumps({"results": [
                {
                    "unit_id": "raydb__ssb_sf10_q11",
                    "lifecycle": "installed_cold_compile_prepare_execute",
                    "method": "v2_direct_true_optix_backport",
                    "rows": [{"registered_complete_endpoint_seconds": 4.0}],
                },
                {
                    "unit_id": "rayjoin__top4_six_batch",
                    "lifecycle": "prepared_first_execute",
                    "method": "v4_restricted_callback_true_optix",
                    "rows": [{"registered_complete_endpoint_seconds": 0.5}],
                    "prepared_session_complete_wall_seconds_reported_separately": 9.0,
                },
            ]}) + "\n")
            observed = _load_roots([path])
            self.assertEqual(len(observed), 2)
            self.assertEqual(observed[
                ("rayjoin__top4_six_batch", "prepared_first_execute",
                 "v4_restricted_callback_true_optix")], 9.0)

    def test_budget_requires_complete_exact_route_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seen = []
            for row in schedule():
                key = (row["unit_id"], row["lifecycle"], row["method"])
                if key not in seen:
                    seen.append(key)
            for index, (unit, lifecycle, method) in enumerate(seen):
                record = {
                    "unit_id": unit, "lifecycle": lifecycle, "method": method,
                    "rows": [{"registered_complete_endpoint_seconds": 1.0}],
                }
                if unit == "rayjoin__top4_six_batch" \
                        and lifecycle == "prepared_first_execute":
                    record["prepared_session_complete_wall_seconds_reported_separately"] = 10.0
                (root / f"{index:03d}.json").write_text(json.dumps(record) + "\n")
            result = estimate(
                [root], process_overhead_seconds=1.0, safety_factor=1.25)
            self.assertEqual(result["worker_count"], 464)
            self.assertEqual(result["covered_method_lifecycle_units"], 58)
            self.assertEqual(result["formal_method_lifecycle_units"], 58)
            self.assertEqual(
                result["functional_only_observations_excluded_from_budget"], 0)
            self.assertAlmostEqual(
                result["conservative_budget_seconds"], 1340.0)
            (root / "000.json").unlink()
            with self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                estimate([root])


if __name__ == "__main__":
    unittest.main()
