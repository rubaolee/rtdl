from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK as DIRECT_RELATION_TASK,
)
from experiments.goal5802_premeasurement.workload import (
    TRIANGLE_TASK as DIRECT_TRIANGLE_TASK,
)
from experiments.goal5848_strong_baseline import direct_bridge
from experiments.goal5848_strong_baseline.contracts import (
    RELATION_TASK,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TASK_CONTRACTS,
    TRIANGLE_TASK,
    digest,
)
from experiments.goal5848_strong_baseline.workloads import (
    relation_workload,
    triangle_workload,
)


class Goal5848DirectBridgeTest(unittest.TestCase):
    @staticmethod
    def _receipt(task):
        relation = task == RELATION_TASK
        value = {
            "schema": "rtdl.goal5802.direct_scalar.worker.v1",
            "status": "PASS",
            "arm": "A_DIRECT_CUDA_OPTIX",
            "worker_id": "WORKER_0",
            "task": DIRECT_RELATION_TASK if relation else DIRECT_TRIANGLE_TASK,
            "regime": "STEADY_E2E",
            "registered_performance_timing_count": STEADY_REPETITIONS,
            "execute_or_regime_durations_ns": [100] * STEADY_REPETITIONS,
            "execution_lifecycle_receipts": [
                {"prepared_input_reused": index > 0}
                for index in range(STEADY_WARMUPS + STEADY_REPETITIONS)
            ],
            "correctness": (
                {
                    "oracle_exact": True,
                    "canonical_rows": [
                        list(row) for row in relation_workload().expected_rows
                    ],
                    "canonical_row_count": 4096,
                    "raw_event_count": 8192,
                    "semantic_unique_count": 4096,
                    "device_status": 0,
                    "device_overflow": 0,
                }
                if relation
                else {
                    "oracle_exact": True,
                    "reduced_u64": triangle_workload().expected_reduced_u64,
                    "device_status": 0,
                }
            ),
            "operation_ledger": {
                "optix_launch_count": 2 if relation else 1,
                "semantic_compaction_launch_count": 1 if relation else 0,
                "application_output_d2h_bytes": TASK_CONTRACTS[task][
                    "public_output_bytes"
                ],
                "per_ray_d2h_bytes": 0,
                "status_output_commit_blocking_boundary_count": 2,
            },
        }
        return value

    def test_relation_and_triangle_receipts_validate(self):
        for task in (RELATION_TASK, TRIANGLE_TASK):
            direct_bridge._validate_direct_receipt(
                self._receipt(task),
                task=task,
                worker_id="WORKER_0",
            )

    def test_missing_direct_sample_fails_closed(self):
        value = self._receipt(TRIANGLE_TASK)
        value["execute_or_regime_durations_ns"].pop()
        with self.assertRaisesRegex(RuntimeError, "samples"):
            direct_bridge._validate_direct_receipt(
                value,
                task=TRIANGLE_TASK,
                worker_id="WORKER_0",
            )

    def test_compatibility_preflight_has_required_trailing_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "preflight.json"
            file_sha, self_sha = direct_bridge._compatibility_preflight(
                path,
                runtime_manifest_sha256="a" * 64,
            )
            text = path.read_text(encoding="utf-8")
            self.assertEqual(len(file_sha), 64)
            self.assertIn(
                f'  "preflight_sha256": "{self_sha}",\n', text
            )
            self.assertIn(
                '  "status": "PASS__LIVE_TARGET_AND_CROSS_ARM_'
                'NVRTC_BEFORE_WORKER_ZERO",\n',
                text,
            )

    def test_direct_build_receipt_requires_internal_seal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / "direct"
            binary.write_bytes(b"binary")
            derivation = {
                "schema": "rtdl.goal5848.direct_source_derivation.v1",
                "status": "PASS__EXACT_TWO_CONSTANT_DERIVATION",
                "derived_sha256": "a" * 64,
                "parent_sha256": "b" * 64,
                "optix_cuda_or_output_logic_changed": False,
            }
            derivation["receipt_sha256"] = digest(derivation)
            derivation_path = root / "derivation.json"
            derivation_path.write_text(json.dumps(derivation))
            build = {
                "schema": (
                    "rtdl.goal5802.direct_worker_untimed_build_receipt.v2"
                ),
                "status": "PASS__SOURCE_TO_DIRECT_WORKER__UNTIMED",
                "direct_source_sha256": "a" * 64,
                "output_bytes": len(b"binary"),
                "output_sha256": direct_bridge._sha256_file(binary),
            }
            build["receipt_sha256"] = digest(build)
            build_path = root / "build.json"
            build_path.write_text(json.dumps(build))
            args = argparse.Namespace(
                derivation_receipt=derivation_path,
                direct_build_receipt=build_path,
                direct_worker=binary,
            )
            direct_bridge._validate_derivation_and_build(args)
            build["output_bytes"] += 1
            build_path.write_text(json.dumps(build))
            with self.assertRaisesRegex(RuntimeError, "identity differs"):
                direct_bridge._validate_derivation_and_build(args)


if __name__ == "__main__":
    unittest.main()
