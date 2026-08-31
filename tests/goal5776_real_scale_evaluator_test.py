from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from goal5776_evaluate_real_scale_v2_v4 import evaluate
from goal5776_real_scale_formal_contract import (
    COLD,
    PREPARED,
    UNIT_BY_ID,
    V2,
    V4,
    contract_document,
    contract_sha256,
    schedule,
)
from goal5776_recount_real_scale_v2_v4_raw import recount
from goal5776_close_formal_result import close
from goal5776_real_scale_frontdoors import _bind_receipt_to_registered_rows


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _receipt():
    return {
        "physical_executor_classification": "optix_traversal_observed",
        "native_snapshot": {
            "successful_launch_count": 1,
            "complete_context_launch_count": 1,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "unbound_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": "gas:first",
            "last_traversable": "gas:last",
        },
    }


class Goal5776RealScaleEvaluatorTest(unittest.TestCase):
    def build(self, root: Path) -> None:
        (root / "workers").mkdir(parents=True)
        (root / "FORMAL_CONTRACT.json").write_text(
            json.dumps(contract_document(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        rows = list(schedule())
        (root / "SCHEDULE.json").write_text(
            json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        for item in rows:
            unit = UNIT_BY_ID[item["unit_id"]]
            method = item["method"]
            pair_index = int(item["pair_index"])
            timed = []
            for row_id in unit.statistical_row_ids_for(item["lifecycle"]):
                # V4 is deterministically faster in this synthetic mechanism
                # test.  These values are not retained as performance data.
                seconds = (2.0 if method == V2 else 1.0) + pair_index / 100.0
                timed.append({
                    "row_id": row_id,
                    "input_sha256": _digest({"unit": unit.unit_id, "input": 1}),
                    "output_sha256": _digest({"row": row_id, "output": 7}),
                    "registered_complete_endpoint_seconds": seconds,
                })
            payload = {
                "schema": "rtdl.goal5776.synthetic_formal_worker.v1",
                "worker_index": item["worker_index"],
                "parent_pid": 100_000 + int(item["worker_index"]),
                "lifecycle": item["lifecycle"],
                "unit_id": unit.unit_id,
                "method": method,
                "pair_index": pair_index,
                "formal_worker": True,
                "matched": True,
                "registered_endpoint_boundary_id": (
                    "symmetric_user_input_to_canonical_output_bound_receipt_and_cold_teardown.v1"
                ),
                "comparator_inside_registered_timer": False,
                "close_inside_registered_timer": item["lifecycle"] == COLD,
                "preparation_seconds_reported_separately": (
                    None if item["lifecycle"] == COLD else 0.25
                ),
                "prepared_session_complete_wall_seconds_reported_separately": (
                    3.0 if unit.app == "rayjoin"
                    and item["lifecycle"] == PREPARED else None
                ),
                "loading_seconds_reported_separately": (
                    None if item["lifecycle"] == COLD else 0.125
                ),
                "default_selected_between_application_algorithms": False,
                "retry_resume_replacement_row_drop_relabel_used": False,
                "traversal_receipt": _bind_receipt_to_registered_rows(
                    _receipt(), timed),
                "phase_accounting": {
                    "loading_seconds": 0.0,
                    "preparation_seconds": 0.0,
                    "close_seconds": 0.0,
                    "row_execute_seconds": {
                        item["row_id"]: item[
                            "registered_complete_endpoint_seconds"
                        ] for item in timed
                    },
                    "same_worker_mutually_exclusive_phases": True,
                    "nested_phase_medians_summed": False,
                },
                "rows": timed,
                "leaf_cache": (
                    {"mode": "not_applicable_to_v2_direct"}
                    if method == V2 else ({
                        "mode": "sealed_read_only_manifest",
                        "hit_count": 7,
                        "miss_count": 0,
                        "disabled_count": 0,
                    } if unit.v4_numba_leaf_cache_required else {
                        "mode": "not_applicable_no_numba_leaf",
                        "hit_count": 0,
                        "miss_count": 0,
                        "disabled_count": 0,
                    })
                ),
                "bundle_sha256": "0" * 64,
                "data_archive_sha256": "9" * 64,
                "execution_source_sha256": "1" * 64,
                "source_tree_sha256": "2" * 64,
                "rtdbscan_evidence_sha256": "b" * 64,
                "native_library_sha256": "3" * 64,
                "target_identity_sha256": "4" * 64,
                "prepared_identity_sha256": "8" * 64,
                "plan_sha256": "5" * 64,
                "formal_identity_sha256": "6" * 64,
                "leaf_cache_manifest_sha256": "7" * 64,
                "expected_value_statement_sha256": "c" * 64,
                "formal_contract_sha256": contract_sha256(),
                "runtime_sha256": "a" * 64,
            }
            (root / "workers" / f'{item["worker_index"]:04d}.json').write_text(
                json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
            )

    def test_primary_and_independent_recount_match_full_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build(root)
            primary_path = evaluate(root, root / "PRIMARY.json")
            recount_path = recount(root, root / "RECOUNT.json")
            primary = json.loads(primary_path.read_text(encoding="utf-8"))
            independent = json.loads(recount_path.read_text(encoding="utf-8"))
            self.assertEqual(primary["worker_count"], 464)
            self.assertEqual(primary["row_count"], 34)
            self.assertEqual(primary["independent_row_count"], 34)
            self.assertTrue(primary["lifecycle_results"][COLD]["all_row_no_slower"])
            self.assertTrue(primary["lifecycle_results"][PREPARED]["all_row_no_slower"])
            self.assertFalse(primary["cross_app_compensation_used"])
            self.assertFalse(primary["cross_lifecycle_compensation_used"])
            self.assertEqual(independent["worker_count"], 464)
            self.assertEqual(independent["row_count"], 34)
            self.assertEqual(
                [
                    (row["lifecycle"], row["row_id"], row["paired_ratio_median"],
                     row["bootstrap_ci95"])
                    for row in primary["rows"]
                ],
                [
                    (row["lifecycle"], row["row_id"], row["paired_ratio_median"],
                     row["bootstrap_ci95"])
                    for row in independent["rows"]
                ],
            )

    def test_recount_imports_neither_primary_nor_python_contract(self):
        source = (Path(__file__).resolve().parents[1]
                  / "scripts/goal5776_recount_real_scale_v2_v4_raw.py").read_text()
        self.assertNotIn("goal5776_evaluate_real_scale_v2_v4", source)
        self.assertNotIn("goal5776_real_scale_formal_contract import", source)

    def test_closeout_requires_exact_primary_recount_agreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw"
            self.build(raw)
            final_path = close(raw, root / "closeout")
            final = json.loads(final_path.read_text(encoding="utf-8"))
            self.assertEqual(final["worker_count"], 464)
            self.assertEqual(final["pass_count"], 34)
            self.assertEqual(final["fail_count"], 0)
            self.assertTrue(final["primary_and_independent_rows_exactly_match"])
            self.assertFalse(final["prepared_result_replaces_cold"])

    def test_unbound_launch_fails_both_primary_and_recount(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build(root)
            worker_path = root / "workers/0000.json"
            worker = json.loads(worker_path.read_text(encoding="utf-8"))
            worker["traversal_receipt"]["native_snapshot"][
                "unbound_launch_count"
            ] = 1
            worker_path.write_text(
                json.dumps(worker, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "bound OptiX traversal"):
                evaluate(root, root / "PRIMARY.json")
            with self.assertRaisesRegex(RuntimeError, "unproven OptiX traversal"):
                recount(root, root / "RECOUNT.json")

    def test_registered_output_digest_drift_fails_both_statistics_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.build(root)
            worker_path = root / "workers/0000.json"
            worker = json.loads(worker_path.read_text(encoding="utf-8"))
            worker["rows"][0]["output_sha256"] = "f" * 64
            worker_path.write_text(
                json.dumps(worker, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(RuntimeError, "row receipt binding mismatch"):
                evaluate(root, root / "PRIMARY.json")
            with self.assertRaisesRegex(RuntimeError, "row binding mismatch"):
                recount(root, root / "RECOUNT.json")


if __name__ == "__main__":
    unittest.main()
