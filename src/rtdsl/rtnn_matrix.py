from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

from .rtnn_baselines import rtnn_baseline_libraries
from .rtnn_reproduction import rtnn_dataset_families
from .rtnn_reproduction import rtnn_experiment_targets
from .rtnn_reproduction import RtnnReproductionTier


@dataclass(frozen=True)
class RtnnMatrixEntry:
    artifact: str
    dataset_handle: str
    dataset_label: str
    workload: str
    reproduction_tier: RtnnReproductionTier
    baseline_handle: str
    baseline_label: str
    matrix_status: str
    notes: str


def _matrix_status_for(*, reproduction_tier: RtnnReproductionTier, baseline_handle: str) -> str:
    if baseline_handle in {"postgis", "scipy_ckdtree"}:
        return "nonpaper_comparison_only"
    if reproduction_tier == RtnnReproductionTier.BOUNDED_REPRODUCTION:
        return "planned_bounded_matrix"
    if reproduction_tier == RtnnReproductionTier.EXACT_REPRODUCTION_CANDIDATE:
        return "blocked_on_exact_dataset_and_adapter"
    return "planned_rtdl_extension"


def rtnn_reproduction_matrix(*, artifact: Optional[str] = None) -> Tuple[RtnnMatrixEntry, ...]:
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

    # Deterministic sorting (tier -> workload -> dataset -> baseline)
    entries.sort(
        key=lambda e: (
            str(e.reproduction_tier),
            e.workload,
            e.dataset_handle,
            e.baseline_handle,
        )
    )
    return tuple(entries)
