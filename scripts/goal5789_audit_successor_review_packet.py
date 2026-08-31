from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "goal5789_successor_theory_readiness_review_packet_v2"
ARCHIVE = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_20260821.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_twin_20260821.tar.gz"
MANIFEST = ROOT / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_manifest_20260821.json"
EXPECTED_ARCHIVE_SHA256 = "06165a074fc792f631898208d7243275a838d3eafd49e5e4e2704fa4fd4a0b46"
EXPECTED_ARCHIVE_BYTES = 66468192
EXPECTED_MANIFEST_SHA256 = "d42946aab47b2e458805b9444ff3ce3d92847a5e2a6e03bc24212ec96ef1c79e"
EXPECTED_MANIFEST_BYTES = 34998


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member(name: str) -> str:
    value = PurePosixPath(name)
    if value.is_absolute() or any(part in {"", ".", ".."} for part in value.parts):
        raise RuntimeError(f"unsafe member: {name!r}")
    expected_prefix = PREFIX + "/"
    if not name.startswith(expected_prefix):
        raise RuntimeError(f"wrong packet prefix: {name!r}")
    return name[len(expected_prefix) :]


def main() -> None:
    archive = ARCHIVE.read_bytes()
    twin = TWIN.read_bytes()
    manifest_bytes = MANIFEST.read_bytes()
    if len(archive) != EXPECTED_ARCHIVE_BYTES or _sha(archive) != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("archive identity mismatch")
    if archive != twin:
        raise RuntimeError("archive twin mismatch")
    if len(manifest_bytes) != EXPECTED_MANIFEST_BYTES or _sha(manifest_bytes) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("external manifest identity mismatch")
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or manifest.get("payload_count") != len(rows):
        raise RuntimeError("manifest payload shape mismatch")
    expected = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256", "provenance"}:
            raise RuntimeError("manifest payload row mismatch")
        path = row["path"]
        if path in expected:
            raise RuntimeError(f"duplicate manifest path: {path}")
        expected[path] = row
    observed: dict[str, bytes] = {}
    with gzip.GzipFile(fileobj=io.BytesIO(archive), mode="rb") as uncompressed:
        with tarfile.open(fileobj=uncompressed, mode="r:") as packet:
            for member in packet.getmembers():
                relative = _safe_member(member.name)
                if not member.isfile() or member.issym() or member.islnk():
                    raise RuntimeError(f"non-regular member: {member.name}")
                if member.mtime != 0 or member.uid != 0 or member.gid != 0 or member.mode != 0o444:
                    raise RuntimeError(f"non-canonical metadata: {member.name}")
                if relative in observed:
                    raise RuntimeError(f"duplicate archive member: {relative}")
                stream = packet.extractfile(member)
                if stream is None:
                    raise RuntimeError(f"unreadable member: {member.name}")
                observed[relative] = stream.read()
    embedded_manifest = observed.pop("PACKET_MANIFEST.json", None)
    if embedded_manifest != manifest_bytes:
        raise RuntimeError("embedded/external manifest mismatch")
    if set(observed) != set(expected):
        raise RuntimeError("archive/manifest exact member-set mismatch")
    for path, row in expected.items():
        data = observed[path]
        if len(data) != row["bytes"] or _sha(data) != row["sha256"]:
            raise RuntimeError(f"payload identity mismatch: {path}")
    if sum(len(data) for data in observed.values()) != manifest["payload_bytes"]:
        raise RuntimeError("payload byte total mismatch")
    print(
        json.dumps(
            {
                "status": "PASS__INDEPENDENT_EXACT_REVIEW_PACKET_AUDIT",
                "archive_sha256": _sha(archive),
                "archive_bytes": len(archive),
                "manifest_sha256": _sha(manifest_bytes),
                "manifest_bytes": len(manifest_bytes),
                "payload_count": len(observed),
                "payload_bytes": sum(len(data) for data in observed.values()),
                "twin_byte_identical": True,
                "exact_member_set": True,
                "unsafe_or_nonregular_member_count": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
