from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from experiments.goal5802_premeasurement import pyoptix_scalar_arm as old_arm
from experiments.goal5848_strong_baseline import preflight_worker, worker
from experiments.goal5848_strong_baseline.contracts import (
    RELATION_TASK,
    STRONG_PYOPTIX_ARM,
)


class _Initializing:
    def __init__(self) -> None:
        self.close = mock.Mock()


class Goal5848WorkerFailureCleanupTest(unittest.TestCase):
    def test_artifact_load_failure_closes_initializing_provider(self):
        initializing = _Initializing()
        deployment = SimpleNamespace(begin_provider_initialization=lambda *_a, **_k: initializing)
        runtime = SimpleNamespace(
            load_rtdlexe=mock.Mock(side_effect=RuntimeError("load failed"))
        )
        candidate = {"artifact": "artifact", "authority": "authority"}

        with self.assertRaisesRegex(RuntimeError, "load failed"):
            worker._admit_rtdl_artifact_and_start_provider(
                runtime,
                deployment,
                Path("native"),
                candidate,
                collect_phase_timings=False,
                legacy_provider_timing_api=False,
            )

        initializing.close.assert_called_once_with()

    def test_rtdl_input_failure_closes_initializing_provider(self):
        from rtdsl import v4_rtdlexe as runtime

        initializing = _Initializing()
        workload = SimpleNamespace(
            expected_rows=(),
            indexed_bounds_f32le=b"",
            indexed_ids_u32le=b"",
            source_bounds_f32le=b"",
            source_ids_u32le=b"",
            count=1,
        )
        args = argparse.Namespace(
            phase_instrumentation="off",
            candidate_manifest=Path("manifest"),
            task=RELATION_TASK,
            warmups=1,
            repetitions=1,
        )
        candidate = {
            "public": "public",
            "head": "head",
            "package": "package",
            "deployment_id": "slot",
        }

        with (
            mock.patch.object(worker, "_candidate", return_value=(candidate, Path("native"))),
            mock.patch.object(worker, "relation_workload", return_value=workload),
            mock.patch.object(runtime, "install_rtdlexe_deployment", return_value=object()),
            mock.patch.object(
                worker,
                "_admit_rtdl_artifact_and_start_provider",
                return_value=(initializing, object()),
            ),
            mock.patch.object(
                runtime,
                "BoundedRelationBufferStaticInput",
                side_effect=RuntimeError("input failed"),
            ),
            self.assertRaisesRegex(RuntimeError, "input failed"),
        ):
            worker._run_rtdl(args)

        initializing.close.assert_called_once_with()

    def test_preflight_input_failure_closes_initializing_provider(self):
        from rtdsl import v4_rtdlexe as runtime

        initializing = _Initializing()
        workload = SimpleNamespace(
            expected_rows=(),
            indexed_bounds_f32le=b"",
            indexed_ids_u32le=b"",
            source_bounds_f32le=b"",
            source_ids_u32le=b"",
            count=1,
        )
        args = argparse.Namespace(
            candidate_manifest=Path("manifest"),
            task=RELATION_TASK,
        )
        candidate = {
            "public": "public",
            "head": "head",
            "package": "package",
            "deployment_id": "slot",
        }

        with (
            mock.patch.object(
                preflight_worker,
                "_candidate",
                return_value=(candidate, Path("native")),
            ),
            mock.patch.object(
                preflight_worker,
                "relation_workload",
                return_value=workload,
            ),
            mock.patch.object(
                runtime,
                "install_rtdlexe_deployment",
                return_value=object(),
            ),
            mock.patch.object(
                preflight_worker,
                "_admit_rtdl_artifact_and_start_provider",
                return_value=(initializing, object()),
            ),
            mock.patch.object(
                runtime,
                "BoundedRelationBufferStaticInput",
                side_effect=RuntimeError("input failed"),
            ),
            self.assertRaisesRegex(RuntimeError, "input failed"),
        ):
            preflight_worker._rtdl(args)

        initializing.close.assert_called_once_with()

    def test_strong_adapter_load_or_prepare_failure_closes_adapter(self):
        with tempfile.TemporaryDirectory() as temporary:
            args = argparse.Namespace(
                task=RELATION_TASK,
                precompiled_ptx=Path(temporary) / "program.ptx",
                compaction_cubin=Path(temporary) / "compact.cubin",
                warmups=1,
                repetitions=1,
                arm=STRONG_PYOPTIX_ARM,
                phase_instrumentation="on",
            )
            for method in ("load", "prepare"):
                with self.subTest(method=method):
                    adapter = mock.Mock()
                    if method == "load":
                        adapter.load.side_effect = RuntimeError("load failed")
                    else:
                        adapter.prepare.side_effect = RuntimeError("prepare failed")
                    with (
                        mock.patch.object(
                            old_arm,
                            "preload_pyoptix_runtime",
                            return_value=(object(), {"status": "test"}),
                        ),
                        mock.patch(
                            "experiments.goal5848_strong_baseline.strong_pyoptix."
                            "StrongPyOptixAdapter",
                            return_value=adapter,
                        ),
                        self.assertRaisesRegex(RuntimeError, method),
                    ):
                        worker._run_strong_pyoptix(args)
                    adapter.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
