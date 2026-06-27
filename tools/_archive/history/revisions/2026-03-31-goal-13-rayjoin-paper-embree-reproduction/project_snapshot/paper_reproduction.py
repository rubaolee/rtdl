from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaperTarget:
    artifact: str
    paper_label: str
    workload: str
    status: str
    dataset_strategy: str
    dataset_handle: str
    notes: str


RAYJOIN_PAPER_TARGETS: tuple[PaperTarget, ...] = (
    PaperTarget(
        artifact="table3",
        paper_label="County ⊲⊳ Zipcode",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred; fixture-subset currently available only for county-side local checks",
        dataset_handle="USCounty__Zipcode",
        notes="Shares provenance with the paired PIP target.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="County ⊲⊳ Zipcode",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred; fixture-subset currently available only for county-side local checks",
        dataset_handle="USCounty__Zipcode",
        notes="Shares provenance with the paired LSI target.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="Block ⊲⊳ Water",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred",
        dataset_handle="USACensusBlockGroupBoundaries__USADetailedWaterBodies",
        notes="RayJoin scripts use the full internal names shown in experiment logs.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="Block ⊲⊳ Water",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred",
        dataset_handle="USACensusBlockGroupBoundaries__USADetailedWaterBodies",
        notes="RayJoin scripts use the full internal names shown in experiment logs.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAF ⊲⊳ PKAF",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Africa",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAF ⊲⊳ PKAF",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Africa",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAS ⊲⊳ PKAS",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Asia",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAS ⊲⊳ PKAS",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Asia",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAU ⊲⊳ PKAU",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Australia",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKAU ⊲⊳ PKAU",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Australia",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKEU ⊲⊳ PKEU",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Europe",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKEU ⊲⊳ PKEU",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_Europe",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKNA ⊲⊳ PKNA",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_North_America",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKNA ⊲⊳ PKNA",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_North_America",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKSA ⊲⊳ PKSA",
        workload="lsi",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_South_America",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="table3",
        paper_label="LKSA ⊲⊳ PKSA",
        workload="pip",
        status="planned",
        dataset_strategy="exact-input preferred or derived-input from public SpatialHadoop Lakes/Parks",
        dataset_handle="lakes_parks_South_America",
        notes="Resolved from RayJoin plotting scripts.",
    ),
    PaperTarget(
        artifact="figure13",
        paper_label="Figure 13(a-d) LSI scalability",
        workload="lsi",
        status="planned",
        dataset_strategy="deterministic synthetic or derived-input scaling series",
        dataset_handle="lsi_scaling_uniform_and_gaussian",
        notes="Requires 1M..5M scaling series with explicit provenance and throughput derivation.",
    ),
    PaperTarget(
        artifact="figure14",
        paper_label="Figure 14(a-d) PIP scalability",
        workload="pip",
        status="planned",
        dataset_strategy="deterministic synthetic or derived-input scaling series",
        dataset_handle="pip_scaling_uniform_and_gaussian",
        notes="Requires 1M..5M scaling series with explicit provenance and throughput derivation.",
    ),
    PaperTarget(
        artifact="table4",
        paper_label="Polygon overlay execution table",
        workload="overlay",
        status="planned",
        dataset_strategy="same dataset pairs as Table 3 where available",
        dataset_handle="overlay_from_table3_pairs",
        notes="Current RTDL overlay remains compositional seed generation.",
    ),
    PaperTarget(
        artifact="figure15",
        paper_label="Polygon overlay speedup summary",
        workload="overlay",
        status="planned",
        dataset_strategy="derived from Table 4 analogue results",
        dataset_handle="overlay_speedup_summary",
        notes="Must be labeled as Embree baseline analogue.",
    ),
)


def paper_targets(*, artifact: str | None = None, workload: str | None = None) -> tuple[PaperTarget, ...]:
    targets = RAYJOIN_PAPER_TARGETS
    if artifact is not None:
        targets = tuple(target for target in targets if target.artifact == artifact)
    if workload is not None:
        targets = tuple(target for target in targets if target.workload == workload)
    return targets
