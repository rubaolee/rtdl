from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RtnnDatasetFamily:
    handle: str
    paper_label: str
    dimensionality: str
    source_family: str
    preferred_provenance: str
    current_status: str
    acquisition_plan: str
    notes: str


@dataclass(frozen=True)
class RtnnExperimentTarget:
    artifact: str
    paper_label: str
    workload: str
    dataset_handle: str
    reproduction_tier: str
    current_status: str
    notes: str


@dataclass(frozen=True)
class RtnnLocalProfile:
    profile_id: str
    artifact: str
    workload: str
    fidelity: str
    target_runtime: str
    notes: str


@dataclass(frozen=True)
class RtnnPaperDatasetTarget:
    handle: str
    family_handle: str
    paper_label: str
    point_count: int
    distribution_reading: str
    public_source_url: str
    exact_recipe_status: str
    acquisition_priority: str
    exact_recipe_gap: str
    bounded_fallback_policy: str


RTNN_DATASET_FAMILIES: tuple[RtnnDatasetFamily, ...] = (
    RtnnDatasetFamily(
        handle="kitti_velodyne_point_sets",
        paper_label="KITTI-derived point sets",
        dimensionality="3d",
        source_family="KITTI LiDAR / Velodyne frame series",
        preferred_provenance="exact-input preferred; bounded frame subsets acceptable",
        current_status="source-identified",
        acquisition_plan=(
            "Add a deterministic acquisition manifest for the accepted KITTI frame split, "
            "plus a bounded local frame subset for fast parity runs."
        ),
        notes="Primary autonomous-driving style point-cloud family named in the RTNN gap summary.",
    ),
    RtnnDatasetFamily(
        handle="stanford_3d_scan_point_sets",
        paper_label="Stanford 3D scan point sets",
        dimensionality="3d",
        source_family="Stanford mesh/scan family converted into point samples",
        preferred_provenance="exact-input preferred; deterministic point-sample derivation acceptable",
        current_status="source-identified",
        acquisition_plan=(
            "Freeze the exact scan list and deterministic point-sampling rule before any "
            "bounded analogue is called paper-consistent."
        ),
        notes="Represents the high-detail scanned-geometry family in the RTNN-style reproduction story.",
    ),
    RtnnDatasetFamily(
        handle="nbody_or_millennium_snapshots",
        paper_label="N-body or Millennium-style point snapshots",
        dimensionality="3d",
        source_family="Cosmology / N-body particle snapshots",
        preferred_provenance="exact-input preferred; bounded snapshot extraction acceptable",
        current_status="source-identified",
        acquisition_plan=(
            "Choose one accepted public particle-snapshot family, freeze the snapshot ids, "
            "and add a deterministic bounded extraction rule for local comparison."
        ),
        notes="Keeps the RTNN gap summary honest about the large-particle simulation family.",
    ),
)


RTNN_PAPER_DATASET_TARGETS: tuple[RtnnPaperDatasetTarget, ...] = (
    RtnnPaperDatasetTarget(
        handle="kitti_1m",
        family_handle="kitti_velodyne_point_sets",
        paper_label="KITTI-1M",
        point_count=1_000_000,
        distribution_reading="LiDAR surface samples, mostly xy-plane with narrow z range",
        public_source_url="https://www.cvlibs.net/datasets/kitti/raw_data.php",
        exact_recipe_status="blocked_on_frame_recipe",
        acquisition_priority="phase_1",
        exact_recipe_gap=(
            "paper states KITTI frames are combined to reach target point counts, "
            "but the exact frame ids and concatenation/truncation rule are not in "
            "the author repository"
        ),
        bounded_fallback_policy="may use a labeled bounded KITTI package only as bounded reproduction, not paper reproduction",
    ),
    RtnnPaperDatasetTarget(
        handle="kitti_6m",
        family_handle="kitti_velodyne_point_sets",
        paper_label="KITTI-6M",
        point_count=6_000_000,
        distribution_reading="LiDAR surface samples, mostly xy-plane with narrow z range",
        public_source_url="https://www.cvlibs.net/datasets/kitti/raw_data.php",
        exact_recipe_status="blocked_on_frame_recipe",
        acquisition_priority="phase_1",
        exact_recipe_gap="paper figure labels include KITTI-6M, but exact frame ids are not available in repo",
        bounded_fallback_policy="may use a labeled bounded KITTI package only as bounded reproduction, not paper reproduction",
    ),
    RtnnPaperDatasetTarget(
        handle="kitti_12m",
        family_handle="kitti_velodyne_point_sets",
        paper_label="KITTI-12M",
        point_count=12_000_000,
        distribution_reading="LiDAR surface samples, mostly xy-plane with narrow z range",
        public_source_url="https://www.cvlibs.net/datasets/kitti/raw_data.php",
        exact_recipe_status="blocked_on_frame_recipe",
        acquisition_priority="phase_1",
        exact_recipe_gap="exact KITTI frame ids and merge order are not available in repo",
        bounded_fallback_policy="may use a labeled bounded KITTI package only as bounded reproduction, not paper reproduction",
    ),
    RtnnPaperDatasetTarget(
        handle="kitti_25m",
        family_handle="kitti_velodyne_point_sets",
        paper_label="KITTI-25M",
        point_count=25_000_000,
        distribution_reading="LiDAR surface samples, mostly xy-plane with narrow z range",
        public_source_url="https://www.cvlibs.net/datasets/kitti/raw_data.php",
        exact_recipe_status="blocked_on_frame_recipe",
        acquisition_priority="phase_1",
        exact_recipe_gap="exact KITTI frame ids and merge order are not available in repo",
        bounded_fallback_policy="may use a labeled bounded KITTI package only as bounded reproduction, not paper reproduction",
    ),
    RtnnPaperDatasetTarget(
        handle="stanford_bunny_360k",
        family_handle="stanford_3d_scan_point_sets",
        paper_label="Bunny-360K",
        point_count=360_000,
        distribution_reading="3D scanned surface samples occupying full 3D space",
        public_source_url="https://graphics.stanford.edu/data/3Dscanrep/",
        exact_recipe_status="blocked_on_scan_to_point_recipe",
        acquisition_priority="phase_2",
        exact_recipe_gap="need exact Stanford file variant and point extraction/downsample rule",
        bounded_fallback_policy="may use deterministic sampled point set only as bounded reproduction until exact rule is known",
    ),
    RtnnPaperDatasetTarget(
        handle="stanford_dragon_3_6m",
        family_handle="stanford_3d_scan_point_sets",
        paper_label="Dragon-3.6M",
        point_count=3_600_000,
        distribution_reading="3D scanned surface samples occupying full 3D space",
        public_source_url="https://graphics.stanford.edu/data/3Dscanrep/",
        exact_recipe_status="blocked_on_scan_to_point_recipe",
        acquisition_priority="phase_2",
        exact_recipe_gap="need exact Asian Dragon file variant and point extraction/downsample rule",
        bounded_fallback_policy="may use deterministic sampled point set only as bounded reproduction until exact rule is known",
    ),
    RtnnPaperDatasetTarget(
        handle="stanford_buddha_4_6m",
        family_handle="stanford_3d_scan_point_sets",
        paper_label="Buddha-4.6M",
        point_count=4_600_000,
        distribution_reading="3D scanned surface samples occupying full 3D space",
        public_source_url="https://graphics.stanford.edu/data/3Dscanrep/",
        exact_recipe_status="blocked_on_scan_to_point_recipe",
        acquisition_priority="phase_2",
        exact_recipe_gap="need exact Buddha file variant and point extraction/downsample rule",
        bounded_fallback_policy="may use deterministic sampled point set only as bounded reproduction until exact rule is known",
    ),
    RtnnPaperDatasetTarget(
        handle="millennium_nbody_9m",
        family_handle="nbody_or_millennium_snapshots",
        paper_label="NBody-9M",
        point_count=9_000_000,
        distribution_reading="non-uniform cosmological particle or galaxy distribution in 3D",
        public_source_url="https://astro.dur.ac.uk/~jch/millennium/",
        exact_recipe_status="blocked_on_snapshot_trace_recipe",
        acquisition_priority="phase_3",
        exact_recipe_gap="need exact Millennium trace/snapshot id and coordinate extraction rule",
        bounded_fallback_policy="synthetic clustered/shell data is distribution evidence only, never a paper row",
    ),
    RtnnPaperDatasetTarget(
        handle="millennium_nbody_10m",
        family_handle="nbody_or_millennium_snapshots",
        paper_label="NBody-10M",
        point_count=10_000_000,
        distribution_reading="non-uniform cosmological particle or galaxy distribution in 3D",
        public_source_url="https://astro.dur.ac.uk/~jch/millennium/",
        exact_recipe_status="blocked_on_snapshot_trace_recipe",
        acquisition_priority="phase_3",
        exact_recipe_gap="need exact Millennium trace/snapshot id and coordinate extraction rule",
        bounded_fallback_policy="synthetic clustered/shell data is distribution evidence only, never a paper row",
    ),
)


RTNN_EXPERIMENT_TARGETS: tuple[RtnnExperimentTarget, ...] = (
    RtnnExperimentTarget(
        artifact="dataset_packaging",
        paper_label="KITTI bounded local package",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        dataset_handle="kitti_velodyne_point_sets",
        reproduction_tier="bounded_reproduction",
        current_status="planned",
        notes="First reproducible local package for Linux/macOS development loops.",
    ),
    RtnnExperimentTarget(
        artifact="dataset_packaging",
        paper_label="Stanford bounded local package",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        dataset_handle="stanford_3d_scan_point_sets",
        reproduction_tier="bounded_reproduction",
        current_status="planned",
        notes="Needs a deterministic scan list and point-sample rule before performance claims.",
    ),
    RtnnExperimentTarget(
        artifact="dataset_packaging",
        paper_label="N-body bounded local package",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        dataset_handle="nbody_or_millennium_snapshots",
        reproduction_tier="bounded_reproduction",
        current_status="planned",
        notes="Keeps the particle-snapshot family explicit in the first dataset layer.",
    ),
    RtnnExperimentTarget(
        artifact="paper_matrix",
        paper_label="RTNN exact reproduction candidates",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        dataset_handle="kitti_velodyne_point_sets",
        reproduction_tier="exact_reproduction_candidate",
        current_status="planned",
        notes="Can only move to exact reproduction after exact dataset handles and baseline-library adapters exist.",
    ),
    RtnnExperimentTarget(
        artifact="paper_matrix",
        paper_label="RTDL extension matrix",
        workload="fixed_radius_neighbors|knn_rows|bounded_knn_rows",
        dataset_handle="nbody_or_millennium_snapshots",
        reproduction_tier="rtdl_extension",
        current_status="planned",
        notes="Preserves the distinction between paper-faithful work and RTDL-specific extensions.",
    ),
    RtnnExperimentTarget(
        artifact="comparison_matrix",
        paper_label="Bounded external comparison matrix",
        workload="fixed_radius_neighbors|knn_rows|bounded_knn_rows",
        dataset_handle="kitti_velodyne_point_sets",
        reproduction_tier="bounded_reproduction",
        current_status="planned",
        notes="Dedicated artifact for bounded non-paper comparison rows such as SciPy-style baselines.",
    ),
)


RTNN_LOCAL_PROFILES: tuple[RtnnLocalProfile, ...] = (
    RtnnLocalProfile(
        profile_id="kitti_bounded_local_10min",
        artifact="dataset_packaging",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        fidelity="bounded_reproduction",
        target_runtime="<=10 minutes total package",
        notes="Use a fixed frame subset and stable point-count cap for local CI-style reruns.",
    ),
    RtnnLocalProfile(
        profile_id="stanford_bounded_local_10min",
        artifact="dataset_packaging",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        fidelity="bounded_reproduction",
        target_runtime="<=10 minutes total package",
        notes="Use a deterministic scan list and stable point-sampling cap for local reruns.",
    ),
    RtnnLocalProfile(
        profile_id="particle_snapshot_bounded_local_10min",
        artifact="dataset_packaging",
        workload="fixed_radius_neighbors|bounded_knn_rows",
        fidelity="bounded_reproduction",
        target_runtime="<=10 minutes total package",
        notes="Use a stable snapshot id list and deterministic bounded particle extraction.",
    ),
)


def rtnn_dataset_families(*, handle: str | None = None) -> tuple[RtnnDatasetFamily, ...]:
    families = RTNN_DATASET_FAMILIES
    if handle is not None:
        families = tuple(family for family in families if family.handle == handle)
    return families


def rtnn_paper_dataset_targets(
    *, handle: str | None = None, family_handle: str | None = None
) -> tuple[RtnnPaperDatasetTarget, ...]:
    targets = RTNN_PAPER_DATASET_TARGETS
    if handle is not None:
        targets = tuple(target for target in targets if target.handle == handle)
    if family_handle is not None:
        targets = tuple(target for target in targets if target.family_handle == family_handle)
    return targets


def rtnn_experiment_targets(
    *, artifact: str | None = None, reproduction_tier: str | None = None
) -> tuple[RtnnExperimentTarget, ...]:
    targets = RTNN_EXPERIMENT_TARGETS
    if artifact is not None:
        targets = tuple(target for target in targets if target.artifact == artifact)
    if reproduction_tier is not None:
        targets = tuple(target for target in targets if target.reproduction_tier == reproduction_tier)
    return targets


def rtnn_local_profiles(*, artifact: str | None = None, workload: str | None = None) -> tuple[RtnnLocalProfile, ...]:
    profiles = RTNN_LOCAL_PROFILES
    if artifact is not None:
        profiles = tuple(profile for profile in profiles if artifact in profile.artifact.split("|"))
    if workload is not None:
        profiles = tuple(profile for profile in profiles if workload in profile.workload.split("|"))
    return profiles
