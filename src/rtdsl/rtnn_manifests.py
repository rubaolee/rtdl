from __future__ import annotations
import hashlib
import json
from dataclasses import asdict
from dataclasses import dataclass
from typing import Optional, Tuple
from pathlib import Path

from .rtnn_reproduction import rtnn_dataset_families
from .rtnn_reproduction import rtnn_local_profiles


@dataclass(frozen=True)
class RtnnBoundedDatasetManifest:
    dataset_handle: str
    dataset_label: str
    dimensionality: str
    source_family: str
    preferred_provenance: str
    bounded_profile_id: str
    bounded_rule: str
    runtime_target: str
    current_status: str
    notes: str


RTNN_BOUNDED_DATASET_MANIFESTS: tuple[RtnnBoundedDatasetManifest, ...] = (
    RtnnBoundedDatasetManifest(
        dataset_handle="kitti_velodyne_point_sets",
        dataset_label="KITTI-derived point sets",
        dimensionality="3d",
        source_family="KITTI LiDAR / Velodyne frame series",
        preferred_provenance="exact-input preferred; bounded frame subsets acceptable",
        bounded_profile_id="kitti_bounded_local_10min",
        bounded_rule=(
            "Freeze an accepted frame list, preserve original 3D coordinates, "
            "and cap total point count with a stable frame-order truncation rule."
        ),
        runtime_target="<=10 minutes total package",
        current_status="planned",
        notes="First bounded Linux comparison package should start here.",
    ),
    RtnnBoundedDatasetManifest(
        dataset_handle="stanford_3d_scan_point_sets",
        dataset_label="Stanford 3D scan point sets",
        dimensionality="3d",
        source_family="Stanford mesh/scan family converted into point samples",
        preferred_provenance="exact-input preferred; deterministic point-sample derivation acceptable",
        bounded_profile_id="stanford_bounded_local_10min",
        bounded_rule=(
            "Freeze a scan list, preserve the same deterministic point-sampling rule, "
            "and cap total points with a stable per-scan sample ceiling."
        ),
        runtime_target="<=10 minutes total package",
        current_status="planned",
        notes="Point-sampling rule must be frozen before performance claims.",
    ),
    RtnnBoundedDatasetManifest(
        dataset_handle="nbody_or_millennium_snapshots",
        dataset_label="N-body or Millennium-style point snapshots",
        dimensionality="3d",
        source_family="Cosmology / N-body particle snapshots",
        preferred_provenance="exact-input preferred; bounded snapshot extraction acceptable",
        bounded_profile_id="particle_snapshot_bounded_local_10min",
        bounded_rule=(
            "Freeze snapshot ids, preserve original particle coordinates, "
            "and apply a deterministic bounded extraction order before any shuffle."
        ),
        runtime_target="<=10 minutes total package",
        current_status="planned",
        notes="Keep snapshot choice explicit so bounded runs do not drift over time.",
    ),
)


def rtnn_bounded_dataset_manifests(
    *, dataset_handle: Optional[str] = None
) -> tuple[RtnnBoundedDatasetManifest, ...]:
    manifests = RTNN_BOUNDED_DATASET_MANIFESTS
    if dataset_handle is not None:
        manifests = tuple(manifest for manifest in manifests if manifest.dataset_handle == dataset_handle)
    return manifests


def write_rtnn_bounded_dataset_manifest(
    dataset_handle: str,
    destination: Union[str, Path],
) -> Path:
    dataset_map = {family.handle: family for family in rtnn_dataset_families()}
    profile_map = {profile.profile_id: profile for profile in rtnn_local_profiles(artifact="dataset_packaging")}
    manifest_map = {manifest.dataset_handle: manifest for manifest in rtnn_bounded_dataset_manifests()}

    if dataset_handle not in manifest_map:
        raise ValueError(f"unknown RTNN bounded dataset manifest handle: {dataset_handle}")

    manifest = manifest_map[dataset_handle]
    dataset = dataset_map[dataset_handle]
    profile = profile_map[manifest.bounded_profile_id]
    payload = {
        "manifest_kind": "rtnn_bounded_dataset_manifest_v1",
        "dataset": asdict(dataset),
        "bounded_manifest": asdict(manifest),
        "local_profile": asdict(profile),
    }

    # Audit recommendation: Data integrity hashing
    serialized = json.dumps(payload, indent=2, sort_keys=True)
    payload["sha256"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
