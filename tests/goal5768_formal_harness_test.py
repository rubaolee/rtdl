from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.goal5768_evaluate_three_way_formal import evaluate
from scripts.goal5768_formal_controller import (
    FORMAL_WORKER_ENVIRONMENT_KEYS,
    _formal_worker_environment,
    build_prepared_plan,
    execute,
    validate_plan,
)
from scripts.goal5768_recount_three_way_raw import recount


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _receipt() -> dict[str, object]:
    value = {
        "physical_executor_classification": "optix_traversal_observed",
        "native_snapshot": {
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": 11,
            "last_traversable": 11,
            "first_program_bundle_id": 19,
            "last_program_bundle_id": 19,
        },
    }
    value["receipt_sha256"] = _digest(value)
    return value


class Goal5768FormalHarnessTest(unittest.TestCase):
    def _plan(self) -> dict[str, object]:
        lane_contracts = {
            lane_id: {
                "input_sha256": hashlib.sha256(lane_id.encode()).hexdigest(),
                "output_sha256": hashlib.sha256(lane_id.encode()).hexdigest(),
                "expected_sha256": hashlib.sha256(lane_id.encode()).hexdigest(),
            }
            for lane_id in (
                "triangle__rt_1a2", "triangle__rt_2a1", "raydb__q21",
                "librts__range_rows", "librts__overlap_filter",
                "rtnn__ranked_window", "rtdbscan__components",
                "xhd__global_witness", "rayjoin__point_location",
                "rayjoin__segment_pairs", "rayjoin__grouped_events",
                "rtbh__force", "particle__cell_transition",
            )
        }
        return build_prepared_plan(
            bundle_sha256="1" * 64,
            execution_source_sha256="2" * 64,
            execution_tree_sha256="3" * 64,
            native_library_sha256="4" * 64,
            prepared_identity_sha256="5" * 64,
            target_identity_sha256="6" * 64,
            python_executable=str(Path(__file__).resolve()),
            python_version="test",
            runtime={
                "native_library_path": "/frozen/native.so",
                "formal_worker_environment": {
                    name: (None if name in {
                        "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES",
                    } else f"/frozen/{name.lower()}")
                    for name in FORMAL_WORKER_ENVIRONMENT_KEYS
                },
            },
            lane_contracts=lane_contracts,
        )

    def test_plan_has_exact_312_worker_balanced_shape(self) -> None:
        plan = self._plan()
        validate_plan(plan)
        self.assertEqual(len(plan["units"]), 312)
        self.assertEqual(len(plan["lane_ids"]), 13)
        self.assertEqual(plan["independent_rows"], 26)
        counts: dict[tuple[str, str], int] = {}
        for unit in plan["units"]:
            key = (unit["lane_id"], unit["method"])
            counts[key] = counts.get(key, 0) + 1
        self.assertEqual(set(counts.values()), {8})

    def test_invalid_authority_fails_before_subprocess_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan = self._plan()
            plan_path = root / "PLAN.json"
            authority_path = root / "AUTHORITY.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            authority_path.write_text(json.dumps({
                "authority_sha256": "0" * 64,
            }), encoding="utf-8")
            output = root / "formal"
            with mock.patch(
                    "scripts.goal5768_formal_controller.subprocess.run") as run:
                with self.assertRaises(PermissionError):
                    execute(plan_path, authority_path, output)
                run.assert_not_called()
            self.assertFalse(output.exists())

    def test_formal_worker_gets_exact_stage_a_partner_environment(self) -> None:
        plan = self._plan()
        with mock.patch.dict("os.environ", {
            "PYTHONPATH": "ambient-python",
            "CUDA_VISIBLE_DEVICES": "ambient-cuda",
            "NVIDIA_VISIBLE_DEVICES": "ambient-nvidia",
        }, clear=False):
            environment = _formal_worker_environment(plan)
        frozen = plan["runtime"]["formal_worker_environment"]
        for name in FORMAL_WORKER_ENVIRONMENT_KEYS:
            if frozen[name] is None:
                self.assertNotIn(name, environment)
            else:
                self.assertEqual(environment[name], frozen[name])

    def test_primary_and_independent_recount_match_on_312_raw_workers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            plan = self._plan()
            plan_path = root / "PLAN.json"
            plan_path.write_text(
                json.dumps(plan, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            raw_root = root / "raw"
            for ordinal, unit in enumerate(plan["units"]):
                method = unit["method"]
                seconds = {
                    "v2_direct_true_optix_backport": 2.0,
                    "v3_compiler_true_optix": 0.5,
                    "v4_restricted_callback_true_optix": 1.0,
                }[method]
                lane_digest = hashlib.sha256(
                    unit["lane_id"].encode()).hexdigest()
                endpoint = {
                    "lane_id": unit["lane_id"],
                    "method": method,
                    "matched": True,
                    "registered_complete_seconds": seconds,
                    "comparator_inside_registered_timer": False,
                    "traversal_receipt": _receipt(),
                    "native_library_sha256": plan["native_library_sha256"],
                    "input_sha256": lane_digest,
                    "output_sha256": lane_digest,
                    "expected_sha256": lane_digest,
                    "stock_v2_or_v3_claimed": False,
                    "default_selected_between_application_algorithms": False,
                }
                record = {
                    "plan_sha256": plan["plan_sha256"],
                    "formal_identity_sha256": plan["formal_identity_sha256"],
                    "parent_pid": 10_000 + ordinal,
                    "unit": unit,
                    "endpoint": endpoint,
                }
                unit_root = raw_root / unit["unit_id"]
                unit_root.mkdir(parents=True)
                (unit_root / "RESULT.json").write_text(
                    json.dumps(record, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
            primary = evaluate(plan_path, raw_root)
            primary_path = root / "EVALUATION.json"
            primary_path.write_text(
                json.dumps(primary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            independent = recount(plan_path, raw_root, primary_path)
            self.assertTrue(independent["primary_core_exact_match"])
            self.assertEqual(primary["worker_count"], 312)
            self.assertEqual(primary["unique_parent_pid_count"], 312)
            self.assertEqual(primary["independent_row_count"], 26)
            self.assertEqual(primary["pass_count"], 13)
            self.assertEqual(primary["fail_count"], 13)
            self.assertFalse(primary["all_row_no_slower"])
            self.assertTrue(all(
                row["paired_ratio_median"] == 2.0
                for row in primary["rows"]
                if row["baseline"] == "v2_direct_true_optix_backport"
            ))
            self.assertTrue(all(
                row["paired_ratio_median"] == 0.5
                for row in primary["rows"]
                if row["baseline"] == "v3_compiler_true_optix"
            ))

    def test_independent_recount_imports_no_primary_or_frontdoor(self) -> None:
        source = (Path(__file__).resolve().parents[1]
                  / "scripts/goal5768_recount_three_way_raw.py").read_text(
                      encoding="utf-8")
        self.assertNotIn("goal5768_formal_controller", source)
        self.assertNotIn("goal5768_evaluate_three_way_formal", source)
        self.assertNotIn("goal5768_three_way_frontdoors", source)


if __name__ == "__main__":
    unittest.main()
