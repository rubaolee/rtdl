from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4639_release_scorecard import V4_GOAL4639_DECISION_IF_FAIL
from rtdsl.v4_goal4639_release_scorecard import V4_GOAL4639_DECISION_IF_PASS
from rtdsl.v4_goal4639_release_scorecard import evaluate_v4_goal4639_scorecard
from rtdsl.v4_goal4639_release_scorecard import validate_v4_goal4639_scorecard_payload
from rtdsl.v4_goal4639_release_scorecard import v4_goal4639_run_plan


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _fixed_row(gap: float, reduction: float) -> dict:
    return {
        "correctness_passed": True,
        "comparisons": {
            "route_d_count_rows": {"device_array_to_route_d_rows_gap": gap},
            "prior_prepared_summary_gap": {"device_array_gap_reduction_over_prior_summary": reduction},
        },
    }


def _seed_passing_scorecard(out: Path, *, weighted_floor: float = 1.6) -> None:
    _write(
        out / "fixed_radius_count_threshold.json",
        {
            "performance_gate": {
                "status": "pass",
                "passing_sizes": [{"copies": 8192}, {"copies": 32768}, {"copies": 131072}],
            },
            "results": [_fixed_row(0.4, 100.0), _fixed_row(0.2, 200.0), _fixed_row(0.1, 300.0)],
        },
    )
    _write(
        out / "closest_hit_grouped_argmin.json",
        {
            "results": [
                {
                    "correctness_passed": True,
                    "routes": {
                        "device_array_frontdoor": {"median_s": 1.0},
                        "legacy_host_materialize": {"median_s": 1.5},
                    },
                }
                for _ in range(3)
            ]
        },
    )
    _write(
        out / "ray_triangle_any_hit_flags.json",
        {
            "results": [
                {
                    "correctness_passed": True,
                    "comparison": {"torch_reference_to_device_frontdoor_ratio": 9.0},
                    "routes": {"device_array_frontdoor": {"metadata": {"host_materialization_in_hot_path": False}}},
                },
                {
                    "correctness_passed": True,
                    "comparison": {"torch_reference_to_device_frontdoor_ratio": None},
                    "routes": {"device_array_frontdoor": {"metadata": {"host_materialization_in_hot_path": False}}},
                },
                {
                    "correctness_passed": True,
                    "comparison": {"torch_reference_to_device_frontdoor_ratio": None},
                    "routes": {"device_array_frontdoor": {"metadata": {"host_materialization_in_hot_path": False}}},
                },
            ]
        },
    )
    for width in (1, 16, 256):
        _write(
            out / f"primitive_grouped_i64_width{width}.json",
            {
                "results": [
                    {
                        "parity_passed": True,
                        "comparison": {"legacy_host_output_over_device_output_median_speedup": 2.0},
                    },
                    {
                        "parity_passed": True,
                        "comparison": {"legacy_host_output_over_device_output_median_speedup": 3.0},
                    },
                ]
            },
        )
    for variant in ("mixed4", "mixed6"):
        _write(
            out / f"point_group_nearest_witness_{variant}.json",
            {
                "results": [
                    {
                        "parity": {"passed": True},
                        "same_contract_ratio_legacy_host_rows_over_direct_device_output": 500.0,
                    },
                    {
                        "parity": {"passed": True},
                        "same_contract_ratio_legacy_host_rows_over_direct_device_output": 1000.0,
                    },
                ]
            },
        )
    _write(
        out / "ray_triangle_any_hit_weighted_sum.json",
        {
            "results": [
                {
                    "parity_passed": True,
                    "comparison": {"host_materialization_over_device_resident_median_ratio": weighted_floor},
                    "routes": {
                        "device_output_frontdoor": {
                            "host_materialization_in_hot_path": False,
                            "host_scalar_read_before_consumer": False,
                            "weighted_sum_downloaded_to_host_in_hot_path": False,
                        }
                    },
                }
                for _ in range(4)
            ]
        },
    )
    _write(
        out / "fixed_radius_graph_component_union" / "summary.json",
        {
            "comparisons": {
                "all_variant_canonical_component_signatures_match": True,
                "runner_vs_embree_hot_speedup": 1.3,
                "runner_vs_embree_wall_speedup": 1.4,
                "runner_vs_legacy_wall_speedup": 1.1,
            }
        },
    )
    _write(
        out / "aabb_index_all_ops_count.json",
        {
            "comparison": {
                "all_counts_match_cross_backend": True,
                "all_same_contract_family": True,
                "same_contract_backend_pair": {
                    "embree_over_optix_query_median": 20.0,
                    "embree_query_total_sec": 20.0,
                    "optix_query_total_sec": 1.0,
                },
            }
        },
    )


class V4Goal4639ReleaseScorecardTest(unittest.TestCase):
    def test_run_plan_covers_all_frozen_surface_runs(self) -> None:
        plan = v4_goal4639_run_plan(Path("out"), python_exe="python", root=ROOT)

        self.assertEqual(11, len(plan))
        run_ids = {run.run_id for run in plan}
        self.assertIn("fixed_radius_count_threshold", run_ids)
        self.assertIn("primitive_grouped_i64_width1", run_ids)
        self.assertIn("primitive_grouped_i64_width16", run_ids)
        self.assertIn("primitive_grouped_i64_width256", run_ids)
        self.assertIn("point_group_nearest_witness_mixed4", run_ids)
        self.assertIn("point_group_nearest_witness_mixed6", run_ids)
        self.assertIn("aabb_index_all_ops_count", run_ids)

    def test_passing_scorecard_recommends_release_candidate_pending_3ai(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            _seed_passing_scorecard(out)

            payload = validate_v4_goal4639_scorecard_payload(evaluate_v4_goal4639_scorecard(out))

        self.assertEqual(V4_GOAL4639_DECISION_IF_PASS, payload["recommendation"])
        self.assertEqual(8, payload["summary"]["surface_passed"])
        self.assertEqual(4, payload["summary"]["strong_passed"])
        self.assertEqual(4, payload["summary"]["partial_passed"])
        self.assertEqual(2, payload["summary"]["deferred_excluded"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["all_benchmark_speedup_claim_authorized"])

    def test_failing_surface_keeps_result_as_performance_preview_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            _seed_passing_scorecard(out, weighted_floor=1.1)

            payload = validate_v4_goal4639_scorecard_payload(evaluate_v4_goal4639_scorecard(out))

        self.assertEqual(V4_GOAL4639_DECISION_IF_FAIL, payload["recommendation"])
        self.assertIn(
            "v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays",
            payload["summary"]["failed_surfaces"],
        )
        self.assertFalse(payload["release_candidate_authorized"])


if __name__ == "__main__":
    unittest.main()
