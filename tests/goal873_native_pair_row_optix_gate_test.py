from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import goal873_native_pair_row_optix_gate as goal873


ROOT = Path(__file__).resolve().parents[1]


class Goal873NativePairRowOptixGateTest(unittest.TestCase):
    def test_row_digest_is_order_insensitive(self) -> None:
        left = goal873._row_digest(
            (
                {"segment_id": 2, "polygon_id": 20},
                {"segment_id": 1, "polygon_id": 10},
            )
        )
        right = goal873._row_digest(
            (
                {"segment_id": 1, "polygon_id": 10},
                {"segment_id": 2, "polygon_id": 20},
            )
        )
        self.assertEqual(left, right)
        self.assertEqual(left["row_count"], 2)

    def test_non_strict_gate_records_missing_optix_without_failing(self) -> None:
        with mock.patch.object(goal873, "_run_cpu_reference", return_value=({"segment_id": 1, "polygon_id": 10},)):
            with mock.patch.object(goal873, "_run_native_bounded", side_effect=RuntimeError("no optix")):
                payload = goal873.run_gate(
                    dataset="authored_segment_polygon_minimal",
                    output_capacity=16,
                    strict=False,
                )
        self.assertEqual(payload["status"], "non_strict_recorded_gaps")
        self.assertFalse(payload["strict_pass"])
        self.assertEqual(payload["records"][1]["status"], "unavailable_or_failed")

    def test_strict_gate_fails_when_native_unavailable(self) -> None:
        with mock.patch.object(goal873, "_run_cpu_reference", return_value=({"segment_id": 1, "polygon_id": 10},)):
            with mock.patch.object(goal873, "_run_native_bounded", side_effect=RuntimeError("no optix")):
                payload = goal873.run_gate(
                    dataset="authored_segment_polygon_minimal",
                    output_capacity=16,
                    strict=True,
                )
        self.assertEqual(payload["status"], "fail")
        self.assertIn("optix_native_bounded did not run", payload["strict_failures"])

    def test_gate_rejects_zero_output_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "output_capacity must be positive"):
            goal873.run_gate(
                dataset="authored_segment_polygon_minimal",
                output_capacity=0,
                strict=True,
            )

    def test_strict_gate_passes_native_digest_parity(self) -> None:
        rows = ({"segment_id": 1, "polygon_id": 10},)
        native = {
            "emitted_count": 1,
            "copied_count": 1,
            "overflowed": 0,
            "row_digest": goal873._row_digest(rows),
        }
        with mock.patch.object(goal873, "_run_cpu_reference", return_value=rows):
            with mock.patch.object(goal873, "_run_native_bounded", return_value=native):
                payload = goal873.run_gate(
                    dataset="authored_segment_polygon_minimal",
                    output_capacity=16,
                    strict=True,
                )
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["strict_pass"])
        self.assertTrue(payload["records"][1]["parity_vs_cpu_python_reference"])

    def test_cli_writes_json_and_keeps_non_strict_exit_zero_without_optix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "gate.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal873_native_pair_row_optix_gate.py",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                check=True,
                capture_output=True,
                text=True,
            )
            stdout = json.loads(completed.stdout)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(stdout["output_json"], str(output_json))
            self.assertIn(payload["status"], {"pass", "non_strict_recorded_gaps"})
            self.assertTrue(output_json.exists())


if __name__ == "__main__":
    unittest.main()
