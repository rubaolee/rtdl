from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5751_formal_callback_runtime_home_evidence_20260811.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5751_formal_callback_runtime_home_evidence_twin_20260811.tar.gz"
DEVICE_ROOT = "history/internal_docs/goal5751_home_formal_device_validation_v4_20260811"
PAYLOADS = (
    "src/rtdsl/v4_callback_abi.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_callback_optix_wrapper_codegen.py",
    "src/rtdsl/v4_callback_artifact_cache.py",
    "src/rtdsl/v4_formal_optix_runtime.py",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "tests/goal5751_v4_callback_abi_test.py",
    "tests/goal5751_v4_formal_numba_codegen_test.py",
    "tests/goal5751_v4_callback_ptx_composer_test.py",
    "tests/goal5751_v4_optix_wrapper_codegen_test.py",
    "tests/goal5751_v4_callback_artifact_cache_test.py",
    "tests/goal5751_v4_formal_native_runtime_static_test.py",
    "scripts/goal5751_formal_device_validation.py",
    "scripts/goal5751_build_evidence.py",
    "docs/v4/callback_abi_v1.md",
    "history/internal_docs/review_goal5750_owner_returned_external_20260811.md",
    "history/internal_docs/goal5751_formal_callback_runtime_and_home_device_result_20260811.json",
    "history/internal_docs/goal5751_formal_callback_runtime_and_home_device_technical_report_20260811.md",
    "history/internal_docs/self_review_goal5751_formal_callback_runtime_and_home_device_20260811.md",
    "history/internal_docs/call_for_review_goal5751_formal_callback_runtime_and_home_device_20260811.md",
    f"{DEVICE_ROOT}/ANY_HIT_PROOF.json",
    f"{DEVICE_ROOT}/COMPOSED_FORMAL_CALLBACK.ptx",
    f"{DEVICE_ROOT}/NVRTC.log",
    f"{DEVICE_ROOT}/PROVIDER_CACHE/792d5eeced2524444007fd8199cb61cfdb3661f531b4ac191ceea68dd8d61676/artifact.json",
    f"{DEVICE_ROOT}/PROVIDER_CACHE/792d5eeced2524444007fd8199cb61cfdb3661f531b4ac191ceea68dd8d61676/composed.ptx",
    f"{DEVICE_ROOT}/RESULT.json",
    f"{DEVICE_ROOT}/TRUSTED_WRAPPER.cu",
    f"{DEVICE_ROOT}/TRUSTED_WRAPPER.ptx",
    f"{DEVICE_ROOT}/librtdl_optix.so",
    f"{DEVICE_ROOT}/MANIFEST.json",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _info(name: str, size: int) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = 0
    return info


def build() -> tuple[str, int, int]:
    rows: list[dict[str, object]] = []
    members: list[tuple[str, bytes]] = []
    for relative in PAYLOADS:
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"unsafe or missing Goal5751 evidence payload: {relative}")
        data = path.read_bytes()
        name = relative.replace("\\", "/")
        rows.append({"path": name, "bytes": len(data), "sha256": _sha(data)})
        members.append((name, data))
    manifest = {
        "schema": "rtdl.goal5751.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_data = (_canonical(manifest) + "\n").encode("utf-8")
    members.append(("GOAL5751_EVIDENCE_MANIFEST.json", manifest_data))

    def render() -> bytes:
        raw = io.BytesIO()
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for name, data in members:
                    archive.addfile(_info(name, len(data)), io.BytesIO(data))
        return raw.getvalue()

    first = render()
    second = render()
    if first != second:
        raise RuntimeError("Goal5751 deterministic evidence twin mismatch")
    OUTPUT.write_bytes(first)
    TWIN.write_bytes(second)
    return _sha(first), len(rows), int(manifest["payload_bytes"])


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


if __name__ == "__main__":
    digest, count, size = build()
    print(json.dumps({
        "sha256": digest, "payload_count": count, "payload_bytes": size,
    }, sort_keys=True))
