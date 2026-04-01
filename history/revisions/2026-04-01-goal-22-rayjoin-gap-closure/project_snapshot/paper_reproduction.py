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


@dataclass(frozen=True)
class DatasetFamily:
    handle: str
    paper_pair: str
    source_family: str
    preferred_provenance: str
    current_status: str
    local_plan: str


@dataclass(frozen=True)
class LocalProfile:
    profile_id: str
    artifact: str
    workload: str
    fidelity: str
    build_size: str
    probe_series: str
    target_runtime: str
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


RAYJOIN_DATASET_FAMILIES: tuple[DatasetFamily, ...] = (
    DatasetFamily(
        handle="USCounty__Zipcode",
        paper_pair="County ⊲⊳ Zipcode",
        source_family="USCounty + Zipcode",
        preferred_provenance="exact-input preferred",
        current_status="partial",
        local_plan="Use the checked-in county fixture for parity now; add zipcode acquisition and conversion in a later Goal 22 slice.",
    ),
    DatasetFamily(
        handle="USACensusBlockGroupBoundaries__USADetailedWaterBodies",
        paper_pair="Block ⊲⊳ Water",
        source_family="BlockGroup + WaterBodies",
        preferred_provenance="exact-input preferred",
        current_status="missing",
        local_plan="Add public acquisition and conversion path before any bounded local analogue is treated as complete.",
    ),
    DatasetFamily(
        handle="lakes_parks_Africa",
        paper_pair="LKAF ⊲⊳ PKAF",
        source_family="Lakes + Parks / Africa",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
    DatasetFamily(
        handle="lakes_parks_Asia",
        paper_pair="LKAS ⊲⊳ PKAS",
        source_family="Lakes + Parks / Asia",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
    DatasetFamily(
        handle="lakes_parks_Australia",
        paper_pair="LKAU ⊲⊳ PKAU",
        source_family="Lakes + Parks / Australia",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
    DatasetFamily(
        handle="lakes_parks_Europe",
        paper_pair="LKEU ⊲⊳ PKEU",
        source_family="Lakes + Parks / Europe",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
    DatasetFamily(
        handle="lakes_parks_North_America",
        paper_pair="LKNA ⊲⊳ PKNA",
        source_family="Lakes + Parks / North America",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
    DatasetFamily(
        handle="lakes_parks_South_America",
        paper_pair="LKSA ⊲⊳ PKSA",
        source_family="Lakes + Parks / South America",
        preferred_provenance="exact-input preferred, derived-input acceptable",
        current_status="missing",
        local_plan="Acquire or derive the continent pair before bounded local runs.",
    ),
)


LOCAL_REPRODUCTION_PROFILES: tuple[LocalProfile, ...] = (
    LocalProfile(
        profile_id="figure13_lsi_local_5min",
        artifact="figure13",
        workload="lsi",
        fidelity="synthetic-input",
        build_size="R=100000 polygons",
        probe_series="S=100000,200000,300000,400000,500000 polygons",
        target_runtime="4-5 minutes",
        notes="Frozen local LSI scalability profile from Goal 21/Goal 14.",
    ),
    LocalProfile(
        profile_id="figure14_pip_local_5min",
        artifact="figure14",
        workload="pip",
        fidelity="synthetic-input",
        build_size="R=100000 polygons",
        probe_series="S=2000,4000,6000,8000,10000 polygons",
        target_runtime="3-5 minutes",
        notes="Frozen local PIP scalability profile from Goal 21/Goal 14.",
    ),
    LocalProfile(
        profile_id="table3_pair_bounded_local",
        artifact="table3",
        workload="lsi|pip",
        fidelity="derived-input or fixture-subset until exact-input is available",
        build_size="per-pair bounded local profile",
        probe_series="per-pair bounded local profile",
        target_runtime="<=2 minutes per workload per pair; <=10 minutes total package",
        notes="Goal 22 must fill in dataset-specific bounded profiles once acquisition status is known.",
    ),
    LocalProfile(
        profile_id="table4_overlay_bounded_local",
        artifact="table4|figure15",
        workload="overlay",
        fidelity="overlay-seed analogue",
        build_size="per-pair bounded local profile",
        probe_series="per-pair bounded local profile",
        target_runtime="<=2 minutes per pair; <=5 minutes total overlay package",
        notes="Every output must be labeled as an overlay-seed analogue rather than full overlay materialization.",
    ),
)


def paper_targets(*, artifact: str | None = None, workload: str | None = None) -> tuple[PaperTarget, ...]:
    targets = RAYJOIN_PAPER_TARGETS
    if artifact is not None:
        targets = tuple(target for target in targets if target.artifact == artifact)
    if workload is not None:
        targets = tuple(target for target in targets if target.workload == workload)
    return targets


def dataset_families(*, handle: str | None = None) -> tuple[DatasetFamily, ...]:
    families = RAYJOIN_DATASET_FAMILIES
    if handle is not None:
        families = tuple(family for family in families if family.handle == handle)
    return families


def local_profiles(*, artifact: str | None = None, workload: str | None = None) -> tuple[LocalProfile, ...]:
    profiles = LOCAL_REPRODUCTION_PROFILES
    if artifact is not None:
        profiles = tuple(profile for profile in profiles if artifact in profile.artifact.split("|"))
    if workload is not None:
        profiles = tuple(profile for profile in profiles if workload in profile.workload.split("|"))
    return profiles
