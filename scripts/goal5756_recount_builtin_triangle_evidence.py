"""Independent byte and semantic recount for Goal5756 Home evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import tarfile


ROOT = "goal5756_home_result"
FRONT = 0xFE
BACK = 0xFF
U32_MAX = 0xFFFFFFFF


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    parser.add_argument("--expected-archive-sha256", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    archive_bytes = open(args.archive, "rb").read()
    if _sha(archive_bytes) != args.expected_archive_sha256:
        raise RuntimeError("evidence archive SHA-256 mismatch")
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.name in seen:
                raise RuntimeError("unsafe or duplicate archive member")
            seen.add(member.name)
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError("non-regular archive member")
            if not path.parts or path.parts[0] != ROOT:
                raise RuntimeError("archive member outside evidence root")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError("regular member is unreadable")
            payloads["/".join(path.parts[1:])] = handle.read()

    manifest = json.loads(payloads["MANIFEST.json"])
    if len(manifest) != 18:
        raise RuntimeError("unexpected manifest cardinality")
    mismatches: list[str] = []
    for row in manifest:
        data = payloads.get(row["path"])
        if data is None or len(data) != row["size"] or _sha(data) != row["sha256"]:
            mismatches.append(row["path"])
    if mismatches:
        raise RuntimeError(f"manifest mismatches: {mismatches!r}")

    result = json.loads(payloads["RESULT.json"])
    expected = [[11, 13, 0], [13, 11, 0], [U32_MAX, U32_MAX, U32_MAX]]
    if result["cpu_output"] != expected or result["device_output"] != expected:
        raise RuntimeError("CPU/device outputs do not reproduce the exact fixture")
    hits = result["device_hit_observations"]
    if [item["primitive_index"] for item in hits] != [0, 0, None]:
        raise RuntimeError("primitive-index observations do not reproduce")
    if [item["hit_kind"] for item in hits] != [FRONT, BACK, None]:
        raise RuntimeError("front/back hit-kind observations do not reproduce")
    for item in hits[:2]:
        if abs(item["barycentric_x"] - 0.2) > 1e-6 \
                or abs(item["barycentric_y"] - 0.2) > 1e-6:
            raise RuntimeError("device barycentrics do not reproduce")
    if result["device_role_counters"] != [0, 3, 0, 0, 2, 1, 3]:
        raise RuntimeError("device role counters do not reproduce")
    required = (1 << 1) | (1 << 6)
    terminals = [(1 << 4), (1 << 4), (1 << 5)]
    for index, status in enumerate(result["device_launch_status"]):
        if status["first_error_claimed"] != 0 or status["error_code"] != 0:
            raise RuntimeError("device launch status is nonzero")
        if status["invocation_mask"] != required | terminals[index]:
            raise RuntimeError("per-launch role mask does not reproduce")
    receipt = result["traversal_receipt"]
    native = receipt["native_snapshot"]
    if receipt["physical_executor_classification"] != "optix_traversal_observed":
        raise RuntimeError("behavioral OptiX classification does not reproduce")
    if native["successful_launch_count"] != 1 \
            or native["complete_context_launch_count"] != 1 \
            or native["context_bind_count"] != 1 \
            or native["raygen_invocation_count"] != 3:
        raise RuntimeError("launch/binding/raygen receipt does not reproduce")
    for key in (
        "failed_launch_count", "incomplete_context_launch_count",
        "pending_context_at_finish", "session_error",
    ):
        if native[key] != 0:
            raise RuntimeError(f"receipt is not clean: {key}")
    if native["first_traversable"] == 0 \
            or native["first_traversable"] != native["last_traversable"]:
        raise RuntimeError("traversable binding does not reproduce")
    wrapper = payloads["TRUSTED_TRIANGLE_WRAPPER.cu"].decode("utf-8")
    for required_text in (
        "optixGetPrimitiveIndex()", "optixGetHitKind()",
        "optixGetTriangleBarycentrics()", "OPTIX_RAY_FLAG_DISABLE_ANYHIT",
    ):
        if required_text not in wrapper:
            raise RuntimeError(f"trusted wrapper lacks {required_text}")
    if "__intersection__" in wrapper or "__anyhit__" in wrapper:
        raise RuntimeError("trusted built-in-triangle wrapper contains a user IS/AH")

    recount = {
        "schema": "rtdl.goal5756.independent_builtin_triangle_recount.v1",
        "archive_sha256": _sha(archive_bytes),
        "manifest_payload_count": len(manifest),
        "manifest_mismatch_count": 0,
        "cpu_device_output_exact": True,
        "device_primitive_indices": [0, 0, None],
        "device_hit_kinds": [FRONT, BACK, None],
        "device_role_counters": result["device_role_counters"],
        "behavioral_true_optix": True,
        "user_intersection_or_anyhit_present": False,
        "performance_claimed": False,
        "held_out_generalization_claimed": False,
        "verdict": "PASS",
    }
    with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(recount, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
