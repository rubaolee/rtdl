from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import goal5774_prepared_v2_v4_controller as controller
import goal5774_evaluate_prepared_v2_v4 as evaluator


class Goal5774FormalHarnessTest(unittest.TestCase):
    def test_schedule_shape_and_balance(self):
        rows = controller.schedule()
        self.assertEqual(len(rows), 208)
        for lane in controller.LANES:
            selected = [row for row in rows if row["lane_id"] == lane.lane_id]
            self.assertEqual(len(selected), 16)
            self.assertEqual(
                {method: sum(row["method"] == method for row in selected)
                 for method in controller.METHODS},
                {method: 8 for method in controller.METHODS})

    def test_authority_failure_precedes_subprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "runtime.json"
            authority = root / "authority.json"
            runtime.write_text("{}")
            authority.write_text(json.dumps({
                "schema": "rtdl.goal5774.owner_formal_authority.v1",
                "owner_authorized_exactly_once": False,
                "bundle_sha256": "a", "prepared_identity_sha256": "b",
                "target_identity_sha256": "c",
                "formal_identity_sha256": "d",
                "expected_worker_count": 208,
                "expected_independent_row_count": 26,
                "repair_retry_resume_allowed": False,
                "v3_worker_allowed": False,
                "authority_sha256": "invalid",
            }))
            with mock.patch.object(controller.subprocess, "run") as run:
                with self.assertRaises(PermissionError):
                    controller.run(runtime=runtime, output_root=root / "out",
                                   authorization=authority)
                run.assert_not_called()

    def test_controller_uses_frozen_worker_environment(self):
        source = (ROOT / "scripts/goal5774_prepared_v2_v4_controller.py").read_text()
        self.assertIn('"RTDL_FIXED_RADIUS_GRAPH_REFINEMENT_EVIDENCE"', source)
        self.assertIn("env=worker_environment", source)

    def test_primary_evaluator_rebuilds_26_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            workers = root / "workers"
            workers.mkdir()
            for index, schedule_row in enumerate(controller.schedule()):
                method = schedule_row["method"]
                seconds = 2.0 if method == controller.METHODS[0] else 1.0
                payload = {
                    **schedule_row,
                    "parent_pid": index + 1000,
                    "formal_worker": True,
                    "prepare_count": 1,
                    "activation_count": 1,
                    "execute_count": 2,
                    "v3_used_or_required": False,
                    "bundle_sha256": "a" * 64,
                    "prepared_identity_sha256": "b" * 64,
                    "target_identity_sha256": "c" * 64,
                    "formal_identity_sha256": "d" * 64,
                    "native_library_sha256": "e" * 64,
                    "activation": {
                        "matched": True,
                        "activation_only": True,
                        "registered_performance_observation": False,
                        "dynamic_input_sha256": "0" * 64,
                        "output_sha256": "1" * 64,
                    },
                    "calls": [
                        {"matched": True,
                         "registered_performance_observation": True,
                         "dynamic_input_sha256": "2" * 64,
                         "output_sha256": "3" * 64,
                         "registered_prepared_execution_seconds": seconds},
                        {"matched": True,
                         "registered_performance_observation": True,
                         "dynamic_input_sha256": "4" * 64,
                         "output_sha256": "5" * 64,
                         "registered_prepared_execution_seconds": seconds},
                    ],
                }
                (workers / f"{index:03d}.json").write_text(json.dumps(payload))
            output = root / "evaluation.json"
            evaluator.evaluate(root, output)
            result = json.loads(output.read_text())
            self.assertEqual(result["row_count"], 26)
            self.assertEqual(result["pass_count"], 26)
            self.assertTrue(result["all_row_no_slower"])

    def test_recount_imports_no_primary_module(self):
        source = (ROOT / "scripts/goal5774_recount_prepared_v2_v4_raw.py").read_text()
        self.assertNotIn("goal5774_evaluate_prepared_v2_v4", source)
        self.assertNotIn("goal5774_prepared_v2_v4_controller", source)
        self.assertNotIn("goal5774_prepared_three_way_frontdoors", source)

    def test_target_prepare_is_create_only(self):
        source = (ROOT / "scripts/goal5774_target_prepare.py").read_text()
        self.assertIn('"formal_worker_count": 0', source)
        self.assertIn('"registered_formal_timing_count": 0', source)
        self.assertNotIn('"--authorization"', source)

    def test_bundle_is_v2_v4_only_and_has_no_prebuilt_native(self):
        source = (ROOT / "scripts/goal5774_build_v2_v4_pre_pod_bundle.py").read_text()
        self.assertIn('"method_count": 2', source)
        self.assertIn('"v3_required_or_executed": False', source)
        self.assertIn('"source_payload_is_free_of_prebuilt_target_native": True', source)
        self.assertIn("V3_ONLY_OVERLAY_EXCLUSIONS", source)
        self.assertIn("selected.difference_update(V3_ONLY_OVERLAY_EXCLUSIONS)", source)
        self.assertIn('"src/rtdsl/action_ray_triangle_scalar_summary.py"', source)

    def test_formal_authority_is_self_digested_and_exact(self):
        source = (ROOT / "scripts/goal5774_prepared_v2_v4_controller.py").read_text()
        self.assertIn("claimed_authority_sha256 != _digest(authority_body)", source)
        self.assertIn("set(authority) != expected", source)
        self.assertIn('authority["expected_worker_count"] != 208', source)


if __name__ == "__main__":
    unittest.main()
