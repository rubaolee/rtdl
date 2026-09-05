"""Standard-library-only contract for the Goal5847 AOT comparison."""

from __future__ import annotations

import hashlib
import json

RTDL_ARM = "RTDL_FAMILY_RTDLEXE_AOT"
PYOPTIX_ARM = "PYOPTIX_PRECOMPILED_PTX_VALIDATION_OFF"
ARMS = (RTDL_ARM, PYOPTIX_ARM)
RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def expected_schedule(blocks: int) -> tuple[tuple[int, int, str], ...]:
    rows = []
    for block in range(blocks):
        order = ARMS if block % 2 == 0 else tuple(reversed(ARMS))
        rows.extend((block, position, arm) for position, arm in enumerate(order))
    return tuple(rows)


__all__ = [
    "ARMS",
    "PYOPTIX_ARM",
    "PYOPTIX_COMMIT",
    "PYOPTIX_TREE",
    "RELATION_TASK",
    "RTDL_ARM",
    "TRIANGLE_TASK",
    "canonical",
    "digest",
    "expected_schedule",
]
