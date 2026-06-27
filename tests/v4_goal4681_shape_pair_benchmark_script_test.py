from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_goal4681_shape_pair_relation_pod_benchmark.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("v4_goal4681_shape_pair_relation_pod_benchmark", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Goal4681 script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V4Goal4681ShapePairBenchmarkScriptTest(unittest.TestCase):
    def test_print_plan_freezes_serious_dataset_and_bars(self) -> None:
        module = _load_script_module()
        plan = module._print_plan("serious")

        self.assertEqual("rtdl.v4.goal4681.shape_pair_relation_focused_pod_benchmark.v1", plan["schema"])
        self.assertEqual(4096, plan["values"]["shape_count"])
        self.assertEqual("generated_square_grid_shape_pair_count4096", plan["serious_dataset"])
        self.assertIn("generated focused square-grid CDB pair", plan["dataset_source"])
        self.assertIn("not RayJoin paper input", plan["dataset_source"])
        self.assertEqual(1.20, plan["bars"]["v4_hot_over_v2_14_same_primitive_min_for_speed_credit"])
        self.assertEqual(1.10, plan["bars"]["v4_wall_over_v2_14_same_primitive_min_for_speed_credit"])
        self.assertFalse(plan["bars"]["partner_migration_counts_as_speed"])
        self.assertFalse(plan["bars"]["host_row_stream_materialization_allowed"])

    def test_analyze_passes_only_with_same_count_and_no_v4_host_materialization(self) -> None:
        module = _load_script_module()

        def payload(path: Path, *, hot: float, prep: float, count: int, v4: bool = False) -> None:
            body = {
                "row_count": count,
                "summary": {"active_seed_count": count},
                "phases_sec": {
                    "prepared_query_sec": hot,
                    "prepare_active_count_executor_sec": prep,
                },
            }
            if v4:
                body["claim_flags"] = {"host_row_stream_materialization_in_hot_path": False}
                body["phases_sec"] = {
                    "active_count_hot_seconds": hot,
                    "prepare_executor_seconds": prep,
                }
            path.write_text(json.dumps(body), encoding="utf-8")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executions = []
            for version, hot, prep, v4 in (
                ("v2_14", 0.0030, 0.0005, False),
                ("v3_0_2", 0.0012, 0.0003, False),
                ("v4_current", 0.0010, 0.0002, True),
            ):
                for run_kind in ("serious", "correctness"):
                    path = root / f"{version}_{run_kind}.json"
                    payload(path, hot=hot, prep=prep, count=42, v4=v4)
                    executions.append(
                        {
                            "version": version,
                            "run_kind": run_kind,
                            "stdout_json": str(path),
                            "returncode": 0,
                        }
                    )
            summary = module._analyze(executions, "serious", "synthetic.cdb + synthetic.cdb")

        self.assertEqual(
            "goal4681_pass_shape_pair_relation_material_same_primitive_improvement",
            summary["decision_label"],
        )
        self.assertTrue(summary["pass_fail"]["goal4681_speed_credit_pass"])
        self.assertGreaterEqual(summary["ratios"]["v4_hot_over_v2_14_same_primitive"], 1.20)
        self.assertGreaterEqual(summary["ratios"]["v4_wall_over_v2_14_same_primitive"], 1.10)
        self.assertFalse(summary["pass_fail"]["partner_migration_counted_as_speed"])
        self.assertFalse(summary["claim_boundary"]["release_authorized"])


if __name__ == "__main__":
    unittest.main()
