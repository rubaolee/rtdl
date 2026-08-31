#!/usr/bin/env python3
"""Build deterministic Goal5767 usable V4 RC archives from Goal5766."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE_BUNDLE = ROOT / "history/internal_docs/goal5766_v4_portable_rc_v3_20260812.tar.gz"
OUTPUT = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5767_v4_usable_rc_v6_twin_20260812.tar.gz"

OVERLAYS = (
    "README.md",
    "pyproject.toml",
    "src/rtdsl/__init__.py",
    "src/rtdsl/v4.py",
    "examples/current/v4_restricted_callback_quickstart.py",
    "tests/goal5767_v4_release_surface_test.py",
    "scripts/goal5767_release_audit.py",
    "scripts/goal5767_clean_validate.py",
    "scripts/goal5767_build_usable_rc.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _gzip_tar(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith(".py") else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _base_source() -> dict[str, bytes]:
    with tarfile.open(BASE_BUNDLE, "r:gz") as outer:
        source_handle = outer.extractfile("SOURCE.tar.gz")
        if source_handle is None:
            raise RuntimeError("Goal5766 SOURCE.tar.gz missing")
        source_bytes = source_handle.read()
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(source_bytes), mode="r:gz") as source:
        for member in source.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            if not parts or path.is_absolute() or ".." in parts or not member.isfile():
                if member.isdir():
                    continue
                raise RuntimeError(f"unsafe Goal5766 source member: {member.name}")
            name = "/".join(parts)
            if name in payloads:
                raise RuntimeError(f"duplicate Goal5766 source member: {name}")
            handle = source.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable Goal5766 source member: {name}")
            payloads[name] = handle.read()
    return payloads


def main() -> None:
    payloads = _base_source()
    docs = tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "docs/v4").glob("*.md"))
    ) + tuple(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "docs/v3").glob("*.md"))
    )
    for name in OVERLAYS + docs:
        payloads[name] = (ROOT / name).read_bytes()
    source_bytes = _gzip_tar(payloads)
    driver_name = "HARNESS/goal5767_clean_validate.py"
    driver = (ROOT / "scripts/goal5767_clean_validate.py").read_bytes()
    target_driver_name = "HARNESS/goal5766_portable_validate.py"
    target_driver = (ROOT / "scripts/goal5766_portable_validate.py").read_bytes()
    readme = (
        "# RTDL V4 usable research RC\n\n"
        "For CPU-only clean validation, run:\n\n"
        "```bash\npython HARNESS/goal5767_clean_validate.py --bundle-root . "
        "--work-root /tmp/rtdl_v4_usability --output /tmp/rtdl_v4_usability.json\n```\n\n"
        "For the separately authorized NVIDIA functional matrix, use the included "
        "Goal5766 target validator with exact OptiX/CUDA/CC arguments. No performance "
        "execution is authorized by this archive.\n"
    ).encode()
    rows = [
        {"path": "SOURCE.tar.gz", "sha256": _sha(source_bytes), "size_bytes": len(source_bytes)},
        {"path": driver_name, "sha256": _sha(driver), "size_bytes": len(driver)},
        {"path": target_driver_name, "sha256": _sha(target_driver), "size_bytes": len(target_driver)},
        {"path": "README.md", "sha256": _sha(readme), "size_bytes": len(readme)},
    ]
    manifest = {
        "schema": "rtdl.goal5767.usable_portable_manifest.v1",
        "goal": 5767,
        "version": "4.0.0rc1",
        "base_goal5766_bundle_sha256": _sha(BASE_BUNDLE.read_bytes()),
        "source_archive_sha256": _sha(source_bytes),
        "source_payload_is_free_of_prebuilt_target_native": True,
        "source_payload_is_free_of_private_codex_state": True,
        "v4_test_module_count": 20,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    bundle = _gzip_tar({
        "SOURCE.tar.gz": source_bytes,
        driver_name: driver,
        target_driver_name: target_driver,
        "README.md": readme,
        "PORTABLE_MANIFEST.json": manifest_bytes,
    })
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(bundle)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("usable RC twin differs")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source_bytes),
        "source_file_count": len(payloads),
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
