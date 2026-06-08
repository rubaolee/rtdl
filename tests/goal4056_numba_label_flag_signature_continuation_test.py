from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NUMBA_RUNTIME = ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4056_numba_label_flag_signature_continuation_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4056_numba_label_flag_signature_pod_probe.json"


def _numba_cuda_available() -> bool:
    try:
        import _numba_cuda_redirector  # noqa: F401
        from numba import cuda
    except Exception:
        return False
    return bool(cuda.is_available())


class Goal4056NumbaLabelFlagSignatureContinuationTest(unittest.TestCase):
    def test_runtime_api_is_exported_and_generic(self) -> None:
        source = NUMBA_RUNTIME.read_text(encoding="utf-8")
        descriptor = rt.describe_numba_label_count_and_flag_count_i64()

        self.assertEqual(rt.NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION, "label_count_and_flag_count_i64")
        self.assertIn("run_numba_label_count_and_flag_count_i64", rt.__all__)
        self.assertEqual(descriptor["input_columns"], ("labels:int64", "flags:uint32"))
        self.assertEqual(
            descriptor["output_columns"],
            ("label_counts:int64", "flag_true_count:int64", "negative_label_count:int64"),
        )
        self.assertFalse(descriptor["host_column_materialization_used"])
        self.assertNotIn("dbscan", source.lower())
        self.assertNotIn("cluster", source.lower())
        self.assertNotIn("barnes", source.lower())

    def test_runtime_counts_labels_flags_and_negative_labels_when_numba_cuda_available(self) -> None:
        if not _numba_cuda_available():
            self.skipTest("Numba CUDA is not available")
        from numba import cuda

        labels = cuda.to_device(np.asarray([-1, 1, 1, 3, 3, 5], dtype=np.int64))
        flags = cuda.to_device(np.asarray([0, 1, 1, 0, 1, 1], dtype=np.uint32))

        result = rt.run_numba_label_count_and_flag_count_i64(
            labels,
            flags,
            label_count=6,
            validate_labels=True,
        )

        self.assertEqual(result["operation"], rt.NUMBA_LABEL_COUNT_AND_FLAG_COUNT_I64_OPERATION)
        self.assertEqual(result["outputs"]["label_counts"].copy_to_host().tolist(), [0, 2, 0, 2, 0, 1])
        self.assertEqual(int(result["outputs"]["flag_true_count"].copy_to_host()[0]), 4)
        self.assertEqual(int(result["outputs"]["negative_label_count"].copy_to_host()[0]), 1)
        self.assertFalse(result["host_column_materialization_used"])
        self.assertFalse(result["rt_core_speedup_claim_authorized"])
        self.assertFalse(result["promoted_performance_path"])

    def test_rt_dbscan_numba_column_signature_uses_label_flag_count(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("_cluster_signature_from_numba_label_columns", source)
        self.assertIn("rt.run_numba_label_count_and_flag_count_i64", source)
        self.assertIn("numba_label_count_and_flag_count_label_columns", source)
        self.assertIn("column_signature_uses_numba_label_count_and_flag_count", source)
        self.assertIn('"native_dbscan_abi_added": False', source)

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4056",
            "label/flag-count continuation",
            "not RT-DBSCAN-native engine semantics",
            "column_signature_materializes_point_ids: false",
            "does not add a DBSCAN native ABI",
            "does not authorize true-zero-copy claims",
        ):
            self.assertIn(phrase, text)

    def test_pod_probe_records_mixed_label_materialization_win_and_boundary(self) -> None:
        import json

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(artifact["status"], "pass")
        self.assertEqual(artifact["commit"], "c36f7575")
        self.assertTrue(artifact["mixed_label_case_observed"])
        mixed_rows = [row for row in artifact["rows"] if not row["all_core_flags_true"]]
        self.assertGreaterEqual(len(mixed_rows), 2)
        for row in mixed_rows:
            self.assertEqual(row["column_signature_strategy"], "numba_label_count_and_flag_count_label_columns")
            self.assertFalse(row["column_signature_materializes_point_ids"])
            self.assertFalse(row["column_signature_materializes_core_flags"])
        for flag, value in artifact["claim_boundary"].items():
            self.assertFalse(value, flag)


if __name__ == "__main__":
    unittest.main()
