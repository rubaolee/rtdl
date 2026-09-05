from __future__ import annotations

import copy
import unittest

from experiments.goal5848_strong_baseline import contracts
from scripts import goal5848_run_instrumentation_overhead as instrumentation


class Goal5848InstrumentationOverheadTest(unittest.TestCase):
    @staticmethod
    def _worker(row: dict[str, object]) -> dict[str, object]:
        enabled = row["mode"] == "on"
        endpoint = 104 if enabled else 100
        partition = {name: 0 for name in contracts.PARTITION_KEYS}
        partition["unattributed_control_plane"] = 0 if enabled else endpoint
        if enabled:
            partition["canonical_input_construction"] = endpoint
        components = {
            name: (1 if enabled and name == "cuda_primary_context" else None)
            for name in contracts.COMPONENT_DIAGNOSTIC_KEYS
        }
        value = {
            "schema": contracts.WORKER_SCHEMA,
            "status": "PASS__GOAL5848_WORKER",
            "arm": contracts.RTDL_ARM,
            "task": row["task"],
            "block": row["block"],
            "worker_id": row["worker_id"],
            "classification": "exploration",
            "warmups": 1,
            "repetitions": 1,
            "python": "3.12",
            "source": {
                "commit": "a" * 40,
                "tree": "b" * 40,
                "status": "",
                "clean": True,
            },
            "hardware": {},
            "measurements": {
                "post_import_to_first_correct_result_ns": endpoint,
                "endpoint_partition_ns": partition,
                "component_diagnostics_ns": components,
                "evidence": {
                    "phase_instrumentation": enabled,
                    "provider_initialization_phases_ns": (
                        {"native_runtime_warm": 1} if enabled else {}
                    ),
                    "output_sha256": contracts.TASK_CONTRACTS[
                        str(row["task"])
                    ]["public_output_sha256"],
                },
            },
            "claim_boundary": {},
        }
        value["result_sha256"] = contracts.digest(value)
        return value

    @staticmethod
    def _evaluation_inputs(on_ns: int):
        receipts = []
        phases = {}
        for row in contracts.build_instrumentation_schedule():
            endpoint = on_ns if row["mode"] == "on" else 100
            receipts.append({
                "worker_id": row["worker_id"],
                "task": row["task"],
                "block": row["block"],
                "mode": row["mode"],
                "endpoint_ns": endpoint,
            })
            family = (
                "bounded_relation"
                if row["task"] == contracts.RELATION_TASK
                else "builtin_triangle"
            )
            phases[str(row["worker_id"])] = [
                {"family": family, "phase": "prepare.total", "duration_ns": 2},
                {"family": family, "phase": "prepare.gas", "duration_ns": 1},
            ] if row["mode"] == "on" else []
        return receipts, phases

    def test_schedule_is_frozen_balanced_and_fresh_process_sized(self):
        rows = contracts.build_instrumentation_schedule()
        self.assertEqual(rows, contracts.build_instrumentation_schedule())
        self.assertEqual(len(rows), 32)
        self.assertEqual(
            {row["sequence_index"] for row in rows}, set(range(32))
        )
        for task in contracts.TASKS:
            for block in range(contracts.INSTRUMENTATION_BLOCKS):
                selected = [
                    row for row in rows
                    if row["task"] == task and row["block"] == block
                ]
                self.assertEqual(
                    {row["mode"] for row in selected}, {"off", "on"}
                )

    def test_worker_validator_distinguishes_instrumented_and_plain_paths(self):
        for mode in ("off", "on"):
            row = next(
                row for row in contracts.build_instrumentation_schedule()
                if row["mode"] == mode
            )
            value = self._worker(row)
            self.assertGreater(
                instrumentation._validate_worker(
                    value,
                    row=row,
                    expected_source_commit="a" * 40,
                ),
                0,
            )

        value = self._worker(row)
        value["measurements"]["evidence"]["phase_instrumentation"] = False
        value["result_sha256"] = contracts.digest({
            key: item for key, item in value.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "endpoint differs"):
            instrumentation._validate_worker(
                value,
                row=row,
                expected_source_commit="a" * 40,
            )

    def test_native_trace_parser_rejects_foreign_or_incomplete_stderr(self):
        rows = instrumentation._parse_native_phases(
            b"RTDL_GOAL5807_NATIVE_PHASE|bounded_relation|prepare.total|9\n"
            b"RTDL_GOAL5807_NATIVE_PHASE|bounded_relation|prepare.gas|7\n",
            mode="on",
        )
        self.assertEqual(len(rows), 2)
        with self.assertRaisesRegex(RuntimeError, "foreign stderr"):
            instrumentation._parse_native_phases(b"warning\n", mode="on")
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            instrumentation._parse_native_phases(
                b"RTDL_GOAL5807_NATIVE_PHASE|x|prepare.total|1\n",
                mode="on",
            )
        with self.assertRaisesRegex(RuntimeError, "wrote stderr"):
            instrumentation._parse_native_phases(b"anything", mode="off")

    def test_evaluation_accepts_four_percent_and_rejects_six_percent(self):
        receipts, phases = self._evaluation_inputs(104)
        result = instrumentation._evaluate(receipts, phases)
        self.assertTrue(all(row["pass"] for row in result.values()))
        self.assertTrue(all(
            row["instrumentation_overhead_ppm"] == 40_000
            for row in result.values()
        ))
        failed_receipts, failed_phases = self._evaluation_inputs(106)
        with self.assertRaisesRegex(RuntimeError, "exceeds 5%"):
            instrumentation._evaluate(failed_receipts, failed_phases)

    def test_worker_validator_rejects_source_or_off_mode_probe_mutation(self):
        row = next(
            row for row in contracts.build_instrumentation_schedule()
            if row["mode"] == "off"
        )
        value = self._worker(row)
        changed = copy.deepcopy(value)
        changed["source"]["clean"] = False
        changed["result_sha256"] = contracts.digest({
            key: item for key, item in changed.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "receipt differs"):
            instrumentation._validate_worker(
                changed,
                row=row,
                expected_source_commit="a" * 40,
            )

        value["measurements"]["component_diagnostics_ns"][
            "cuda_primary_context"
        ] = 1
        value["result_sha256"] = contracts.digest({
            key: item for key, item in value.items()
            if key != "result_sha256"
        })
        with self.assertRaisesRegex(RuntimeError, "contains phase probes"):
            instrumentation._validate_worker(
                value,
                row=row,
                expected_source_commit="a" * 40,
            )


if __name__ == "__main__":
    unittest.main()
