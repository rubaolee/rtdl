from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from experiments.goal5802_premeasurement import pyoptix_scalar_arm as old_arm
from experiments.goal5848_strong_baseline.contracts import (
    RELATION_TASK,
    TRIANGLE_TASK,
)
from experiments.goal5848_strong_baseline.strong_pyoptix import (
    StrongPyOptixAdapter,
)
from experiments.goal5848_strong_baseline.workloads import (
    relation_workload,
    triangle_workload,
)


class Goal5848StrongPyOptixAdapterTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.ptx = self.root / "program.ptx"
        self.cubin = self.root / "compact.cubin"
        self.runtime = SimpleNamespace(__name__=old_arm.PYOPTIX_BASELINE_MODULE)
        self.preload = {"status": "TEST_ONLY_NO_GPU"}

    def tearDown(self):
        self.temporary.cleanup()

    def test_relation_contract_contains_no_nested_input_rows(self):
        adapter = StrongPyOptixAdapter(
            RELATION_TASK,
            relation_workload(),
            ptx_path=self.ptx,
            compaction_cubin_path=self.cubin,
            preloaded_runtime=self.runtime,
            runtime_preload_receipt=self.preload,
        )
        self.assertEqual(adapter.delegate.workload["indexed"], ())
        self.assertEqual(adapter.delegate.workload["sources"], ())
        self.assertEqual(adapter.delegate.workload["semantic_capacity"], 4096)
        self.assertEqual(len(adapter.delegate.workload["expected_rows"]), 4096)

    def test_triangle_contract_contains_no_nested_geometry_or_queries(self):
        adapter = StrongPyOptixAdapter(
            TRIANGLE_TASK,
            triangle_workload(),
            ptx_path=self.ptx,
            compaction_cubin_path=None,
            preloaded_runtime=self.runtime,
            runtime_preload_receipt=self.preload,
        )
        self.assertEqual(adapter.delegate.workload["vertices"], ())
        self.assertEqual(adapter.delegate.workload["queries"], ())
        self.assertEqual(adapter.delegate.workload["weights"], ())
        self.assertEqual(
            adapter.delegate.workload["expected_reduced_u64"],
            65530,
        )

    def test_task_workload_mismatch_fails_before_runtime_use(self):
        with self.assertRaisesRegex(TypeError, "differ"):
            StrongPyOptixAdapter(
                RELATION_TASK,
                triangle_workload(),
                ptx_path=self.ptx,
                compaction_cubin_path=self.cubin,
                preloaded_runtime=self.runtime,
                runtime_preload_receipt=self.preload,
            )


if __name__ == "__main__":
    unittest.main()
