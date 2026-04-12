from __future__ import annotations

from dataclasses import dataclass

from .rtnn_baselines import rtnn_baseline_libraries
from .rtnn_reproduction import rtnn_dataset_families
from .rtnn_reproduction import rtnn_experiment_targets


@dataclass(frozen=True)
class RtnnMatrixEntry:
    artifact: str
    dataset_handle: str
    dataset_label: str
    workload: str
    reproduction_tier: str
    baseline_handle: str
    baseline_label: str
    matrix_status: str
    notes: str


def _matrix_status_for(*, reproduction_tier: str, baseline_handle: str) -> str:
    if baseline_handle in {"postgis", "scipy_ckdtree"}:
        return "nonpaper_comparison_only"
    if reproduction_tier == "bounded_reproduction":
        return "planned_bounded_matrix"
    if reproduction_tier == "exact_reproduction_candidate":
        return "blocked_on_exact_dataset_and_adapter"
    return "planned_rtdl_extension"


def rtnn_reproduction_matrix(*, artifact: str | None = None) -> tuple[RtnnMatrixEntry, ...]:
    datasets_by_handle = {family.handle: family for family in rtnn_dataset_families()}
    libraries = rtnn_baseline_libraries()
    entries: list[RtnnMatrixEntry] = []

    for target in rtnn_experiment_targets():
        if artifact is not None and target.artifact != artifact:
            continue
        dataset = datasets_by_handle[target.dataset_handle]
        for target_workload in target.workload.split("|"):
            for library in libraries:
                if target.artifact in {"dataset_packaging", "paper_matrix"}:
                    if library.handle in {"postgis", "scipy_ckdtree"}:
                        continue
                library_workloads = set(library.workload_shape.split("|"))
                if target_workload not in library_workloads:
                    continue
                entries.append(
                    RtnnMatrixEntry(
                        artifact=target.artifact,
                        dataset_handle=target.dataset_handle,
                        dataset_label=dataset.paper_label,
                        workload=target_workload,
                        reproduction_tier=target.reproduction_tier,
                        baseline_handle=library.handle,
                        baseline_label=library.paper_label,
                        matrix_status=_matrix_status_for(
                            reproduction_tier=target.reproduction_tier,
                            baseline_handle=library.handle,
                        ),
                        notes=target.notes,
                    )
                )
    return tuple(entries)
