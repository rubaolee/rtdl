#!/usr/bin/env python3
"""Build deterministic Goal5767 evidence and byte-identical twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5767_v4_usable_release_surface_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5767_v4_usable_release_surface_evidence_twin_20260812.tar.gz"
STATIC = (
    "README.md", "pyproject.toml", "src/rtdsl/__init__.py", "src/rtdsl/v4.py",
    "examples/current/v4_restricted_callback_quickstart.py",
    "tests/goal5767_v4_release_surface_test.py",
    "scripts/goal5767_release_audit.py",
    "scripts/goal5767_clean_validate.py",
    "scripts/goal5767_build_usable_rc.py",
    "scripts/goal5767_source_delta_audit.py",
    "scripts/goal5767_build_evidence.py",
    "history/internal_docs/goal5767_v4_usable_rc_v6_20260812.tar.gz",
    "history/internal_docs/goal5767_clean_usability_result_v6_20260812.json",
    "history/internal_docs/goal5767_release_audit_20260812.json",
    "history/internal_docs/goal5767_source_delta_audit_v6_20260812.json",
    "history/internal_docs/goal5767_development_lineages_20260812.json",
    "history/internal_docs/goal5767_v4_usable_release_surface_result_20260812.json",
    "history/internal_docs/goal5767_v4_usable_release_surface_technical_report_20260812.md",
    "history/internal_docs/self_review_goal5767_v4_usable_release_surface_20260812.md",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    paths = list(STATIC)
    paths.extend(
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "docs/v4").glob("*.md"))
    )
    if len(paths) != len(set(paths)):
        raise RuntimeError("duplicate evidence payload")
    payloads = []
    rows = []
    for name in sorted(paths):
        data = (ROOT / name).read_bytes()
        payloads.append((name, data))
        rows.append({"path": name, "sha256": _sha(data), "size_bytes": len(data)})
    manifest = {
        "schema": "rtdl.goal5767.evidence_manifest.v1",
        "goal": 5767,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads.append((
        "GOAL5767_EVIDENCE_MANIFEST.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    ))
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(payloads):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    data = output.getvalue()
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
