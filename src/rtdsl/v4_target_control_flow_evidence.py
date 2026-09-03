"""Exact source evidence for Goal5840's bounded continuation checks.

The target-side checker does not import this module.  It receives the exact
source bytes captured here and validates them against a separately supplied
manifest digest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .v4_target_evidence_bundle import make_blob_record


TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA = (
    "rtdl.v4.target_control_flow_evidence.v1"
)
TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN = (
    b"rtdl.v4.target_control_flow_evidence.v1\0"
)

_SOURCE_PATHS_BY_ROUTE = {
    "stable::bounded_relation::canonical_bounded_pair_collection": (
        "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
        "src/rtdsl/v4_bounded_relation.py",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
        "src/native/optix/rtdl_optix_core.cpp",
    ),
    "stable::triangle_reduction::checked_u64_reduction": (
        "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    ),
    "prospective::builtin_sphere::any_hit_count_continue_u64_per_query": (
        "src/rtdsl/v4_sphere_any_hit_count_prepared_runtime.py",
        "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    ),
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def capture_target_control_flow_evidence(
    route_id: str,
    *,
    repository_root: Path | None = None,
) -> dict[str, object]:
    """Capture only preregistered route source files, byte for byte."""

    try:
        source_paths = _SOURCE_PATHS_BY_ROUTE[route_id]
    except KeyError as error:
        raise ValueError(f"unsupported Goal5840 route: {route_id}") from error
    root = (
        _repository_root()
        if repository_root is None
        else repository_root.resolve(strict=True)
    )
    sources = []
    for relative_path in source_paths:
        path = (root / relative_path).resolve(strict=True)
        try:
            path.relative_to(root)
        except ValueError as error:
            raise RuntimeError(
                f"control-flow source escaped repository: {relative_path}"
            ) from error
        if not path.is_file():
            raise FileNotFoundError(path)
        sources.append(
            {
                "repository_path": relative_path,
                "payload": make_blob_record(path.read_bytes()),
            }
        )
    body: dict[str, object] = {
        "schema": TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA,
        "route_id": route_id,
        "sources": sources,
    }
    body["manifest_sha256"] = hashlib.sha256(
        TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN + _canonical_bytes(body)
    ).hexdigest()
    return body


__all__ = [
    "TARGET_CONTROL_FLOW_EVIDENCE_DOMAIN",
    "TARGET_CONTROL_FLOW_EVIDENCE_SCHEMA",
    "capture_target_control_flow_evidence",
]
