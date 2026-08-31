#!/usr/bin/env python3
"""Exact four-unit input mapping for Goal5784."""

from __future__ import annotations

import hashlib
from pathlib import Path

from goal5784_targeted_formal_contract import TARGET_UNIT_IDS


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_targeted_inputs(data_root: str | Path) -> dict[str, dict[str, object]]:
    data = Path(data_root).resolve()
    prepared = data / "common/rt_barneshut/prepared_arrays.json"
    forces = data / "common/rt_barneshut/expected_forces.txt"
    result: dict[str, dict[str, object]] = {
        "rtbh__author_32768": {
            "prepared_arrays": str(prepared),
            "expected_forces": str(forces),
            "expected_prepared_sha256": _sha(prepared),
            "expected_forces_sha256": _sha(forces),
        },
    }
    for dataset, filename, count in (
        ("com_dblp", "com-dblp.edge", 2_224_385),
        ("cit_patents", "cit-Patents.edge", 7_515_023),
        ("soc_livejournal1", "soc-LiveJournal1.edge", 285_730_264),
    ):
        result[f"triangle__{dataset}__rt_2a1"] = {
            "edge_file": str(data / "triangle" / filename),
            "expected_triangle_count": count,
            "max_relation_rows": 1_000_000,
        }
    if set(result) != set(TARGET_UNIT_IDS):
        raise RuntimeError("Goal5784 exact input-map cardinality mismatch")
    for identity in result.values():
        for key in ("prepared_arrays", "expected_forces", "edge_file"):
            if key in identity:
                path = Path(str(identity[key]))
                if not path.is_file() or path.is_symlink():
                    raise FileNotFoundError(path)
    return result


__all__ = ["build_targeted_inputs"]
