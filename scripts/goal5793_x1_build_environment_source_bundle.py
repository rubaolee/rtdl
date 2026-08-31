"""Build the exact Goal5793 S0 326-row source bundle for X1 environment capture."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUTHORITY = ROOT / "history/internal_docs/goal5793_s0_source_and_admission_freeze_20260822.json"


class BundleError(ValueError):
    pass


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _safe_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise BundleError("source_row_path_invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise BundleError(f"source_row_path_unsafe:{value}")
    return path.as_posix()


def build_bundle(root: Path = ROOT) -> tuple[bytes, dict[str, object]]:
    authority = json.loads((root / SOURCE_AUTHORITY.relative_to(ROOT)).read_text(encoding="utf-8"))
    rows = authority["declared_product_native_source_zero_drift_authority"]["rows"]
    if not isinstance(rows, list) or len(rows) != 326:
        raise BundleError("source_row_count_mismatch")
    paths = [_safe_path(row.get("path")) for row in rows]
    if paths != sorted(paths, key=lambda value: value.encode("utf-8")) or len(paths) != len(set(paths)):
        raise BundleError("source_rows_not_sorted_unique")

    payloads: list[tuple[str, bytes]] = []
    for row, rel in zip(rows, paths, strict=True):
        path = root / Path(*PurePosixPath(rel).parts)
        if path.is_symlink() or not path.is_file():
            raise BundleError(f"source_row_not_regular:{rel}")
        payload = path.read_bytes()
        if set(row) != {"path", "sha256", "size_bytes"}:
            raise BundleError(f"source_row_keyset_mismatch:{rel}")
        if len(payload) != row["size_bytes"] or _sha256(payload) != row["sha256"]:
            raise BundleError(f"source_row_identity_mismatch:{rel}")
        payloads.append((rel, payload))

    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for rel, payload in payloads:
            member = tarfile.TarInfo(rel)
            member.size = len(payload)
            member.mode = 0o444
            member.uid = 0
            member.gid = 0
            member.uname = ""
            member.gname = ""
            member.mtime = 0
            archive.addfile(member, io.BytesIO(payload))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, compresslevel=9, mtime=0) as stream:
        stream.write(raw.getvalue())
    bundle = compressed.getvalue()
    summary: dict[str, object] = {
        "schema": "rtdl.goal5793.x1.environment_source_bundle_summary.v1",
        "source_authority_file_sha256": _sha256((root / SOURCE_AUTHORITY.relative_to(ROOT)).read_bytes()),
        "source_authority_internal_sha256": authority["source_authority_sha256"],
        "file_count": len(payloads),
        "payload_bytes": sum(len(payload) for _, payload in payloads),
        "bundle_bytes": len(bundle),
        "bundle_sha256": _sha256(bundle),
    }
    return bundle, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise BundleError("create_only_output_exists")
    bundle, summary = build_bundle()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as handle:
        handle.write(bundle)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
