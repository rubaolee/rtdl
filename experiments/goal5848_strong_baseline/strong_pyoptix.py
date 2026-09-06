"""Strong PyOptix adapter over frozen precompiled device programs.

This adapter deliberately composes the independent Goal5802 PyOptix owner. It
changes only the host representation to Goal5848's packed byte authority; it
does not call RTDL code or alter traversal/continuation semantics.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.goal5802_premeasurement import pyoptix_scalar_arm as arm

from .contracts import RELATION_TASK, TRIANGLE_TASK
from .packed_partner_inputs import relation_host_inputs, triangle_host_inputs
from .workloads import PackedRelationWorkload, PackedTriangleWorkload


class StrongPyOptixAdapter:
    """Own one precompiled PyOptix task with packed input construction."""

    def __init__(
        self,
        task: str,
        workload: PackedRelationWorkload | PackedTriangleWorkload,
        *,
        ptx_path: Path,
        compaction_cubin_path: Path | None,
        record_operation_evidence: bool = False,
        preloaded_runtime: Any | None = None,
        runtime_preload_receipt: dict[str, Any] | None = None,
    ) -> None:
        if task == RELATION_TASK and type(workload) is PackedRelationWorkload:
            contract_workload: dict[str, object] = {
                "indexed": (),
                "sources": (),
                "minimum_overlap_f32": workload.minimum_overlap_f32,
                "semantic_capacity": workload.count,
                "expected_rows": [list(row) for row in workload.expected_rows],
            }
        elif task == TRIANGLE_TASK and type(workload) is PackedTriangleWorkload:
            contract_workload = {
                "vertices": (),
                "queries": (),
                "weights": (),
                "tmin": workload.tmin_f32,
                "expected_reduced_u64": workload.expected_reduced_u64,
            }
        else:
            raise TypeError("Goal5848 task and packed workload differ")
        self.task = task
        self.workload = workload
        delegate_task = (
            arm.RELATION_TASK if task == RELATION_TASK else arm.TRIANGLE_TASK
        )
        self.delegate = arm.PyOptixScalarAdapter(
            delegate_task,
            contract_workload,
            ptx_path=ptx_path,
            compaction_cubin_path=compaction_cubin_path,
            record_operation_evidence=record_operation_evidence,
            preloaded_runtime=preloaded_runtime,
            runtime_preload_receipt=runtime_preload_receipt,
        )

    def load(self) -> None:
        self.delegate.load()

    def prepare(self) -> None:
        delegate = self.delegate
        if not delegate._loaded or delegate.ptx is None:
            raise RuntimeError("Goal5848 strong PyOptix prepare precedes load")
        if delegate.owner is not None:
            raise RuntimeError("Goal5848 strong PyOptix prepare called twice")
        baseline = delegate.baseline
        delegate.context, delegate.logger = arm._make_validation_off_context(
            baseline
        )
        set_cache_enabled = getattr(delegate.context, "setCacheEnabled", None)
        if not callable(set_cache_enabled):
            raise TypeError(
                "PyOptix context does not expose disk-cache disable control"
            )
        set_cache_enabled(False)
        kind = "relation" if self.task == RELATION_TASK else "triangle"
        (
            delegate.pipeline,
            delegate.pipeline_keepalive,
            _logs,
        ) = arm._build_comparative_pipeline(
            baseline,
            delegate.context,
            delegate.ptx,
            task=kind,
        )
        delegate.sbt, delegate.sbt_keepalive = baseline.make_sbt(
            delegate.pipeline_keepalive
        )
        if self.task == RELATION_TASK:
            if (
                delegate.compaction_cubin is None
                or delegate._compaction_cubin_memfd is None
            ):
                raise RuntimeError("relation compaction CUBIN was not loaded")
            arm._validate_write_sealed_memfd(delegate._compaction_cubin_memfd)
            delegate.compaction_module = baseline.cp.RawModule(
                path=delegate._compaction_cubin_memfd["proc_fd_path"]
            )
            delegate.compaction_kernel = (
                delegate.compaction_module.get_function(
                    "goal5802_relation_unique_compact"
                )
            )
            if not isinstance(self.workload, PackedRelationWorkload):
                raise TypeError("strong relation workload type differs")
            host_inputs = relation_host_inputs(baseline, self.workload)
            fixture = {
                "indexed": (),
                "sources": (),
                "minimum_overlap": self.workload.minimum_overlap_f32,
                "capacity": self.workload.count,
                "expected_rows": [
                    list(row) for row in self.workload.expected_rows
                ],
            }
            delegate.owner = arm.DeferredRelationPrepared(
                baseline,
                delegate.context,
                delegate.pipeline,
                delegate.sbt,
                fixture,
                pipeline_keepalive=delegate.pipeline_keepalive,
                sbt_keepalive=delegate.sbt_keepalive,
                compaction_kernel=delegate.compaction_kernel,
                host_inputs=host_inputs,
                record_operation_evidence=delegate.record_operation_evidence,
            )
        else:
            if not isinstance(self.workload, PackedTriangleWorkload):
                raise TypeError("strong triangle workload type differs")
            host_inputs = triangle_host_inputs(baseline, self.workload)
            triangle_contract = {
                "vertices": (),
                "queries": (),
                "weights": (),
                "tmin": self.workload.tmin_f32,
                "expected_reduced_u64": self.workload.expected_reduced_u64,
            }
            delegate.owner = arm.ScalarTrianglePrepared(
                baseline,
                delegate.context,
                delegate.pipeline,
                delegate.sbt,
                triangle_contract,
                pipeline_keepalive=delegate.pipeline_keepalive,
                sbt_keepalive=delegate.sbt_keepalive,
                host_inputs=host_inputs,
                record_operation_evidence=delegate.record_operation_evidence,
            )
        owner = delegate.owner
        delegate._measurement_execute = lambda: owner.execute()

    def execute(self) -> Any:
        return self.delegate.execute()

    def execute_with_operation_guard(self) -> dict[str, Any]:
        """Run the operation-evidence path outside every comparative timer."""

        return self.delegate.execute_with_operation_guard()

    def measurement_execution_callable(self) -> Any:
        return self.delegate.measurement_execution_callable()

    def measurement_lifecycle_receipt(self, raw_result: Any) -> dict[str, Any]:
        return self.delegate.measurement_lifecycle_receipt(raw_result)

    def finalize_measurement_evidence(self, raw_result: Any) -> dict[str, Any]:
        return self.delegate.finalize_measurement_evidence(raw_result)

    def runtime_identity(self) -> dict[str, Any]:
        return self.delegate.runtime_identity()

    def close(self) -> None:
        self.delegate.close()


__all__ = ["StrongPyOptixAdapter"]
