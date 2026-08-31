#!/usr/bin/env python3
"""Build deterministic Goal5766 portable-RC evidence and byte-identical twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5766_portable_v4_release_candidate_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5766_portable_v4_release_candidate_evidence_twin_20260812.tar.gz"

STATIC = (
    "scripts/goal5766_build_portable_rc.py",
    "scripts/goal5766_portable_validate.py",
    "scripts/goal5766_build_evidence.py",
    "scripts/goal5765_integrated_nine_app_recount.py",
    "scripts/goal5757_verify_core_freeze.py",
    "history/internal_docs/goal5766_v4_portable_rc_v3_20260812.tar.gz",
    "history/internal_docs/goal5766_independent_nine_app_recount_20260812.json",
    "history/internal_docs/goal5766_development_lineages_20260812.json",
    "history/internal_docs/goal5766_portable_v4_release_candidate_result_20260812.json",
    "history/internal_docs/goal5766_portable_v4_release_candidate_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5766_portable_v4_release_candidate_20260812.md",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _paths() -> list[str]:
    paths = list(STATIC)
    base = ROOT / "history/internal_docs/goal5766_home_clean_validation_result_20260812"
    paths.extend(
        path.relative_to(ROOT).as_posix()
        for path in sorted(candidate for candidate in base.rglob("*") if candidate.is_file())
    )
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate evidence payload")
    missing = [name for name in paths if not (ROOT / name).is_file()]
    if missing:
        raise FileNotFoundError(missing)
    return sorted(paths)


def _archive_bytes() -> tuple[bytes, dict]:
    payloads: list[tuple[str, bytes]] = []
    rows = []
    for name in _paths():
        data = (ROOT / name).read_bytes()
        payloads.append((name, data))
        rows.append({"path": name, "sha256": _sha(data), "size_bytes": len(data)})
    manifest = {
        "schema": "rtdl.goal5766.evidence_manifest.v1",
        "goal": 5766,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads.append((
        "GOAL5766_EVIDENCE_MANIFEST.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    ))
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return compressed.getvalue(), manifest


def main() -> None:
    data, manifest = _archive_bytes()
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(data)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("evidence twin differs")
    print(json.dumps({
        "archive_sha256": _sha(data),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
