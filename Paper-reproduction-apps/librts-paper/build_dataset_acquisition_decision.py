from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_decision(
    *,
    availability: dict[str, object],
    zenodo_size_bytes: int,
    zenodo_md5: str,
    measured_bytes_per_sec: float,
    local_disk_available_bytes: int,
    local_ram_bytes: int,
    local_gpu: str,
    local_gpu_vram_mib: int,
) -> dict[str, object]:
    if availability["decision"]["exact_paper_inputs_available"]:
        raise ValueError("dataset acquisition decision expects exact inputs to be absent")
    estimated_seconds = zenodo_size_bytes / measured_bytes_per_sec
    local_meets_paper_hardware = (
        local_gpu_vram_mib >= 24 * 1024 and local_ram_bytes >= 64 * 1024**3
    )
    enough_download_space_only = local_disk_available_bytes >= 2 * zenodo_size_bytes
    acquire_here = bool(
        local_meets_paper_hardware
        and enough_download_space_only
        and estimated_seconds <= 2 * 60 * 60
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.dataset_acquisition_decision.v1",
        "status": (
            "exact_dataset_download_authorized_on_current_host"
            if acquire_here
            else "exact_dataset_download_deferred_to_suitable_host"
        ),
        "official_sources": {
            "sharepoint_archive_count": 3,
            "sharepoint_direct_head_status": [401, 401, 401],
            "author_onedrivedownloader_resolution_verified": False,
            "zenodo_record": "14209767",
            "zenodo_file": "PPoPPAE-v2.tar.gz",
            "zenodo_size_bytes": zenodo_size_bytes,
            "zenodo_md5": zenodo_md5,
            "zenodo_download_available": True,
        },
        "current_host": {
            "gpu": local_gpu,
            "gpu_vram_mib": local_gpu_vram_mib,
            "ram_bytes": local_ram_bytes,
            "disk_available_bytes": local_disk_available_bytes,
            "zenodo_probe_bytes_per_sec": measured_bytes_per_sec,
            "estimated_full_download_seconds": estimated_seconds,
            "estimated_full_download_hours": estimated_seconds / 3600.0,
            "meets_paper_hardware_guidance": local_meets_paper_hardware,
            "has_two_archive_sizes_free": enough_download_space_only,
        },
        "required_acquisition_host": {
            "gpu_class": "RTX 3090-class or newer RTX with RT cores",
            "minimum_vram_gib": 24,
            "minimum_ram_gib": 64,
            "minimum_free_disk_gib": 70,
            "recommended_sustained_download_mib_per_sec": 10,
            "linux_required": True,
        },
        "decision": {
            "download_on_current_host": acquire_here,
            "exact_input_blocker_removed": False,
            "pod_required_for_next_metadata_or_log_work": False,
            "pod_required_for_exact_dataset_execution": True,
            "next_goal": "prepare_resume_safe_zenodo_acquisition_and_smallest_exact_figure_gate",
        },
        "claim_boundary": {
            "exact_inputs_acquired": False,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "sharepoint_permanently_unavailable_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--availability", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--zenodo-size-bytes", type=int, required=True)
    parser.add_argument("--zenodo-md5", required=True)
    parser.add_argument("--measured-bytes-per-sec", type=float, required=True)
    parser.add_argument("--local-disk-available-bytes", type=int, required=True)
    parser.add_argument("--local-ram-bytes", type=int, required=True)
    parser.add_argument("--local-gpu", required=True)
    parser.add_argument("--local-gpu-vram-mib", type=int, required=True)
    args = parser.parse_args()
    availability = json.loads(args.availability.read_text(encoding="utf-8"))
    payload = build_decision(
        availability=availability,
        zenodo_size_bytes=args.zenodo_size_bytes,
        zenodo_md5=args.zenodo_md5,
        measured_bytes_per_sec=args.measured_bytes_per_sec,
        local_disk_available_bytes=args.local_disk_available_bytes,
        local_ram_bytes=args.local_ram_bytes,
        local_gpu=args.local_gpu,
        local_gpu_vram_mib=args.local_gpu_vram_mib,
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
