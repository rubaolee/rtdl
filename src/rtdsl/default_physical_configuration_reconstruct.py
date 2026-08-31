"""Independent reconstruction of prepared physical configuration.

This module intentionally imports neither the production selector/front door
nor the cell-MBR resolver/executor.  It reconstructs the public deterministic
rule from a plan policy, certified population column and returned resolution.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

import numpy as np


class PhysicalConfigurationReconstructionError(RuntimeError):
    pass


def _fail(code: str, detail: str = "") -> None:
    raise PhysicalConfigurationReconstructionError(
        f"{code}: {detail}" if detail else code
    )


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reconstruct_cell_mbr_inline_configuration(
    policy_contract: Mapping[str, object],
    resolved_configuration: Mapping[str, object],
    certified_point_counts,
    *,
    repository_root: Path,
) -> dict[str, object]:
    if (
        policy_contract.get("schema")
        != "rtdl.physical_configuration_policy.cell_mbr_inline.v1"
        or policy_contract.get("policy_id")
        != "cell_mbr_cover_certified_population_up_to_reviewed_cap_v1"
        or policy_contract.get("application_identity_used") is not False
        or policy_contract.get("timing_or_learned_input_used") is not False
        or policy_contract.get("universal_optimality_claimed") is not False
    ):
        _fail("INVALID_POLICY_CONTRACT")
    claimed_policy = policy_contract.get("policy_contract_sha256")
    policy_body = dict(policy_contract)
    policy_body.pop("policy_contract_sha256", None)
    if claimed_policy != _digest(policy_body):
        _fail("POLICY_CONTRACT_DIGEST_MISMATCH")
    relative = policy_contract.get("source_path")
    anchor = policy_contract.get("source_anchor")
    if not isinstance(relative, str) or not isinstance(anchor, str):
        _fail("INVALID_POLICY_SOURCE")
    root = Path(repository_root).resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        _fail("POLICY_SOURCE_OUTSIDE_REPOSITORY")
    if not path.is_file() or _sha256_file(path) != policy_contract.get("source_sha256"):
        _fail("POLICY_SOURCE_IDENTITY_MISMATCH")
    if anchor not in path.read_text(encoding="utf-8"):
        _fail("POLICY_SOURCE_ANCHOR_MISSING")

    raw = np.asarray(certified_point_counts)
    if raw.ndim != 1 or raw.size == 0 or raw.dtype.kind not in {"u", "i"}:
        _fail("INVALID_CERTIFIED_POINT_COUNTS")
    if np.any(raw < 0):
        _fail("NEGATIVE_CERTIFIED_POINT_COUNT")
    counts = np.ascontiguousarray(raw, dtype="<u8")
    maximum = int(np.max(counts))
    floor = policy_contract.get("prior_floor")
    cap = policy_contract.get("reviewed_cap")
    if (
        isinstance(floor, bool)
        or not isinstance(floor, int)
        or floor <= 0
        or isinstance(cap, bool)
        or not isinstance(cap, int)
        or cap < floor
        or maximum <= 0
    ):
        _fail("INVALID_POLICY_RANGE_OR_POPULATION")
    selected = min(cap, max(floor, maximum))
    counts_hasher = hashlib.sha256()
    counts_hasher.update(b"rtdl.certified_cell_population_column.v1\x00")
    counts_hasher.update(str(int(counts.size)).encode("ascii"))
    counts_hasher.update(b"\x00")
    counts_hasher.update(counts.tobytes(order="C"))
    expected = {
        "schema": "rtdl.resolved_physical_configuration.cell_mbr_inline.v1",
        "policy_contract_sha256": claimed_policy,
        "policy_id": policy_contract["policy_id"],
        "certified_point_counts_sha256": counts_hasher.hexdigest(),
        "certified_cell_count": int(counts.size),
        "max_certified_cell_population": maximum,
        "prior_floor": floor,
        "reviewed_cap": cap,
        "selected_max_inline_points": selected,
        "full_cell_population_covered": selected >= maximum,
        "residual_heavy_cell_count": int(np.count_nonzero(counts > selected)),
        "caller_requested_max_inline_points": resolved_configuration.get(
            "caller_requested_max_inline_points"
        ),
        "caller_parameter_override_accepted": False,
        "application_identity_used": False,
        "timing_or_learned_input_used": False,
        "universal_optimality_claimed": False,
    }
    expected["resolved_configuration_sha256"] = _digest(expected)
    if _canonical_bytes(expected) != _canonical_bytes(dict(resolved_configuration)):
        _fail("RESOLVED_CONFIGURATION_MISMATCH")
    return {
        "schema": "rtdl.physical_configuration_reconstruction.v1",
        "status": "PASS",
        "policy_contract_sha256": claimed_policy,
        "resolved_configuration_sha256": expected[
            "resolved_configuration_sha256"
        ],
        "selected_max_inline_points": selected,
        "full_cell_population_covered": selected >= maximum,
        "imports_resolver_selector_frontdoor_or_executor": False,
    }


__all__ = (
    "PhysicalConfigurationReconstructionError",
    "reconstruct_cell_mbr_inline_configuration",
)
