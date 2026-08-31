from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5750_formal_callback_ir_evidence_20260811.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5750_formal_callback_ir_evidence_twin_20260811.tar.gz"
PAYLOADS = (
    "src/rtdsl/v4_callback_ir.py",
    "src/rtdsl/v4_callback_frontend.py",
    "src/rtdsl/v4_callback_interpreter.py",
    "tests/goal5750_v4_callback_ir_test.py",
    "docs/v4/callback_ir_v1.md",
    "history/internal_docs/goal5750_formal_callback_ir_verifier_cpu_interpreter_result_20260811.json",
    "history/internal_docs/goal5750_formal_callback_ir_verifier_cpu_interpreter_technical_report_20260811.md",
    "history/internal_docs/self_review_goal5750_formal_callback_ir_verifier_cpu_interpreter_20260811.md",
    "history/internal_docs/call_for_review_goal5750_formal_callback_ir_verifier_cpu_interpreter_20260811.md",
    "history/internal_docs/review_goal5749_p1_linkage_and_composer_closure_owner_returned_external_20260811.md",
    "scripts/goal5750_build_evidence.py",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tar_info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = 0o644
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def build() -> tuple[str, int, int]:
    rows: list[dict[str, object]] = []
    members: list[tuple[str, bytes]] = []
    for relative in PAYLOADS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"unsafe or missing evidence payload: {relative}")
        data = path.read_bytes()
        members.append((relative.replace("\\", "/"), data))
        rows.append({"path": relative.replace("\\", "/"), "bytes": len(data), "sha256": _sha256(data)})
    manifest = {
        "schema": "rtdl.goal5750.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_data = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    members.append(("GOAL5750_EVIDENCE_MANIFEST.json", manifest_data))

    def render() -> bytes:
        raw = io.BytesIO()
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for name, data in members:
                    archive.addfile(_tar_info(name, len(data)), io.BytesIO(data))
        return raw.getvalue()

    first = render()
    second = render()
    if first != second:
        raise RuntimeError("deterministic evidence twin mismatch")
    OUTPUT.write_bytes(first)
    TWIN.write_bytes(second)
    return _sha256(first), len(rows), int(manifest["payload_bytes"])


if __name__ == "__main__":
    digest, count, size = build()
    print(json.dumps({"sha256": digest, "payload_count": count, "payload_bytes": size}, sort_keys=True))
