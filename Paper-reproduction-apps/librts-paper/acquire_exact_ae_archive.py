from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path


ARCHIVE_NAME = "PPoPPAE-v2.tar.gz"
ARCHIVE_URL = (
    "https://zenodo.org/records/14209767/files/PPoPPAE-v2.tar.gz?download=1"
)
ARCHIVE_SIZE_BYTES = 23_062_425_365
ARCHIVE_MD5 = "89e589f086038f1cd3af9e3ed67da8c8"
MINIMUM_FREE_DISK_BYTES = 70 * 1024**3
MINIMUM_RAM_BYTES = 64 * 1024**3
MINIMUM_GPU_VRAM_MIB = 24 * 1024


def _total_ram_bytes() -> int:
    if hasattr(os, "sysconf"):
        try:
            return int(os.sysconf("SC_PAGE_SIZE")) * int(
                os.sysconf("SC_PHYS_PAGES")
            )
        except (OSError, TypeError, ValueError):
            pass
    return 0


def _gpu_identity() -> tuple[str, int]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "unavailable", 0
    if result.returncode != 0:
        return "unavailable", 0
    parsed: list[tuple[str, int]] = []
    for line in result.stdout.splitlines():
        name, separator, raw_memory = line.rpartition(",")
        if not separator:
            continue
        try:
            parsed.append((name.strip(), int(raw_memory.strip())))
        except ValueError:
            continue
    return max(parsed, key=lambda item: item[1], default=("unavailable", 0))


def curl_resume_command(partial_path: Path) -> list[str]:
    return [
        "curl",
        "--location",
        "--fail",
        "--retry",
        "8",
        "--retry-all-errors",
        "--continue-at",
        "-",
        "--output",
        str(partial_path),
        ARCHIVE_URL,
    ]


def build_plan(
    *,
    destination_dir: Path,
    platform_name: str,
    free_disk_bytes: int,
    ram_bytes: int,
    gpu_name: str,
    gpu_vram_mib: int,
) -> dict[str, object]:
    archive_path = destination_dir / ARCHIVE_NAME
    partial_path = destination_dir / f"{ARCHIVE_NAME}.part"
    acquisition_resource_checks = {
        "linux": platform_name.lower() == "linux",
        "free_disk": free_disk_bytes >= MINIMUM_FREE_DISK_BYTES,
        "ram": ram_bytes >= MINIMUM_RAM_BYTES,
    }
    execution_resource_checks = {
        **acquisition_resource_checks,
        "gpu_vram": gpu_vram_mib >= MINIMUM_GPU_VRAM_MIB,
    }
    download_authorized = all(acquisition_resource_checks.values())
    paper_execution_host_suitable = all(execution_resource_checks.values())
    return {
        "schema": "rtdl.paper_reproduction.librts.resume_safe_acquisition.v1",
        "status": (
            "resume_safe_acquisition_authorized"
            if download_authorized
            else "resume_safe_acquisition_prepared__host_resource_gate_failed"
        ),
        "archive": {
            "name": ARCHIVE_NAME,
            "url": ARCHIVE_URL,
            "expected_size_bytes": ARCHIVE_SIZE_BYTES,
            "expected_md5": ARCHIVE_MD5,
            "final_path": str(archive_path),
            "partial_path": str(partial_path),
        },
        "host": {
            "platform": platform_name,
            "free_disk_bytes": free_disk_bytes,
            "ram_bytes": ram_bytes,
            "gpu_name": gpu_name,
            "gpu_vram_mib": gpu_vram_mib,
            "acquisition_resource_checks": acquisition_resource_checks,
            "paper_execution_resource_checks": execution_resource_checks,
            "download_authorized": download_authorized,
            "paper_execution_host_suitable": paper_execution_host_suitable,
        },
        "resume_contract": {
            "command": curl_resume_command(partial_path),
            "partial_file_survives_failed_transfer": True,
            "promotion_requires_size_and_md5": True,
            "promotion_is_atomic_replace": True,
            "extract_is_a_separate_gate": True,
        },
        "claim_boundary": {
            "download_executed": False,
            "exact_inputs_acquired": False,
            "archive_verified": False,
            "archive_extracted": False,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(
    path: Path,
    *,
    expected_size_bytes: int = ARCHIVE_SIZE_BYTES,
    expected_md5: str = ARCHIVE_MD5,
) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(f"archive is missing: {path}")
    actual_size = path.stat().st_size
    if actual_size != expected_size_bytes:
        raise ValueError(
            f"archive size mismatch: expected {expected_size_bytes}, got {actual_size}"
        )
    actual_md5 = md5_file(path)
    if actual_md5.lower() != expected_md5.lower():
        raise ValueError(
            f"archive MD5 mismatch: expected {expected_md5}, got {actual_md5}"
        )
    return {
        "path": str(path),
        "size_bytes": actual_size,
        "md5": actual_md5,
        "verified": True,
    }


def promote_verified_partial(
    partial_path: Path,
    final_path: Path,
    *,
    expected_size_bytes: int = ARCHIVE_SIZE_BYTES,
    expected_md5: str = ARCHIVE_MD5,
) -> dict[str, object]:
    verification = verify_archive(
        partial_path,
        expected_size_bytes=expected_size_bytes,
        expected_md5=expected_md5,
    )
    os.replace(partial_path, final_path)
    verification["path"] = str(final_path)
    verification["promoted_from_partial"] = True
    return verification


def _write_json(payload: dict[str, object], output: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("plan", "download", "verify"), required=True)
    parser.add_argument("--destination-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    destination_dir = args.destination_dir.resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    gpu_name, gpu_vram_mib = _gpu_identity()
    plan = build_plan(
        destination_dir=destination_dir,
        platform_name=platform.system(),
        free_disk_bytes=shutil.disk_usage(destination_dir).free,
        ram_bytes=_total_ram_bytes(),
        gpu_name=gpu_name,
        gpu_vram_mib=gpu_vram_mib,
    )
    archive_path = destination_dir / ARCHIVE_NAME
    partial_path = destination_dir / f"{ARCHIVE_NAME}.part"

    if args.mode == "plan":
        _write_json(plan, args.output)
        return 0
    if args.mode == "verify":
        payload = {**plan, "verification": verify_archive(archive_path)}
        payload["status"] = "exact_ae_archive_verified__not_extracted"
        payload["claim_boundary"]["archive_verified"] = True
        _write_json(payload, args.output)
        return 0
    if not plan["host"]["download_authorized"]:
        raise RuntimeError("host resource gate failed; refusing exact archive download")

    completed = subprocess.run(curl_resume_command(partial_path), check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"curl failed with exit {completed.returncode}; partial file retained for resume"
        )
    verification = promote_verified_partial(partial_path, archive_path)
    payload = {**plan, "verification": verification}
    payload["status"] = "exact_ae_archive_downloaded_and_verified__not_extracted"
    payload["claim_boundary"]["download_executed"] = True
    payload["claim_boundary"]["archive_verified"] = True
    _write_json(payload, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
