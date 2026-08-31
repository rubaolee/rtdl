from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = (
    ROOT
    / "history/internal_docs/goal5789_successor_theory_readiness_review_packet_v2_manifest_20260821.json"
)
EXPECTED_MANIFEST_SHA256 = (
    "d42946aab47b2e458805b9444ff3ce3d92847a5e2a6e03bc24212ec96ef1c79e"
)
EXPECTED_MANIFEST_BYTES = 34_998
EXPECTED_PAYLOAD_SET_SHA256 = (
    "77d19ba4d2ba6f76be1a3e9046239fe5d3a133e15586196eec7eb2d310e672c9"
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_rows(rows: list[dict[str, object]]) -> bytes:
    return (
        json.dumps(
            rows,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def main() -> None:
    manifest_bytes = MANIFEST.read_bytes()
    if len(manifest_bytes) != EXPECTED_MANIFEST_BYTES:
        raise RuntimeError("manifest byte-count mismatch")
    if _sha(manifest_bytes) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("manifest file identity mismatch")

    manifest = json.loads(manifest_bytes.decode("utf-8"))
    rows = manifest.get("payloads")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise RuntimeError("manifest payload rows are not a list of objects")
    if manifest.get("payload_count") != len(rows):
        raise RuntimeError("manifest payload count mismatch")
    paths = [row.get("path") for row in rows]
    if not all(isinstance(path, str) and path for path in paths):
        raise RuntimeError("manifest payload path shape mismatch")
    if len(paths) != len(set(paths)):
        raise RuntimeError("manifest payload paths are not unique")

    observed = _sha(_canonical_rows(rows))
    if observed != EXPECTED_PAYLOAD_SET_SHA256:
        raise RuntimeError("recomputed payload-set identity mismatch")
    if manifest.get("payload_set_sha256") != observed:
        raise RuntimeError("manifest payload-set identity mismatch")

    print(
        json.dumps(
            {
                "status": "PASS__INDEPENDENT_CANONICAL_PAYLOAD_SET_DIGEST_RECOMPUTED",
                "manifest_sha256": _sha(manifest_bytes),
                "manifest_bytes": len(manifest_bytes),
                "payload_count": len(rows),
                "payload_set_sha256": observed,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
