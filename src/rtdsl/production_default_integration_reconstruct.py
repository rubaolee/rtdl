"""Independent reconstruction for Goal5697 production DEFAULT artifacts.

This module imports neither the production integration, selector, compiler
front door, nor any paper application.  It reconstructs their canonical
artifacts from embedded bytes and delegates only to the two predecessor
independent reconstructors.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from .default_compiler_frontdoor_reconstruct import (
    reconstruct_default_execution_admission,
    reconstruct_default_plan,
)
from .default_physical_selection_reconstruct import reconstruct_default_receipt


class ProductionDefaultReconstructionError(RuntimeError):
    pass


def _fail(code: str, detail: str = "") -> None:
    raise ProductionDefaultReconstructionError(
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


def _mapping(value: object, field: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _fail("EXPECTED_MAPPING", field)
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reconstruct_production_plan(
    plan: Mapping[str, object], *, repository_root: Path
) -> dict[str, object]:
    if plan.get("schema") != "rtdl.production_default.plan.v1":
        _fail("INVALID_PRODUCTION_PLAN_SCHEMA")
    body = dict(plan)
    claimed = body.pop("production_plan_sha256", None)
    if claimed != _digest(body):
        _fail("PRODUCTION_PLAN_DIGEST_MISMATCH")
    nested = _mapping(plan.get("default_plan"), "default_plan")
    if plan.get("default_plan_sha256") != nested.get("plan_sha256"):
        _fail("NESTED_PLAN_IDENTITY_MISMATCH")
    mandatory = plan.get("mandatory_nvidia_rt") is True
    if mandatory:
        reconstruct_default_plan(nested, repository_root=repository_root)
        if nested.get("mandatory_optix_target") is not True:
            _fail("MANDATORY_PLAN_LOST_OPTIX_TARGET")
    else:
        nested_body = dict(nested)
        nested_claimed = nested_body.pop("plan_sha256", None)
        if nested_claimed != _digest(nested_body):
            _fail("PARTNER_PLAN_DIGEST_MISMATCH")
        receipt = _mapping(nested.get("selection_receipt"), "selection_receipt")
        reconstruct_default_receipt(receipt)
        if (
            nested.get("partner_stage_only") is not True
            or nested.get("partner_stage_can_satisfy_rt_claim") is not False
        ):
            _fail("PARTNER_STAGE_RT_BOUNDARY_WEAKENED")
    if (
        plan.get("selected_candidate_stable_id")
        != nested.get("selected_candidate_stable_id")
        or plan.get("selected_candidate_sha256")
        != nested.get("selected_candidate_sha256")
    ):
        _fail("PRODUCTION_WINNER_NESTED_MISMATCH")
    for field in (
        "candidate_override_accepted",
        "backend_override_accepted",
        "template_override_accepted",
        "program_override_accepted",
        "application_identity_used",
        "behavioral_optix_claimed",
        "silicon_rt_core_utilization_claimed",
    ):
        if plan.get(field) is not False:
            _fail("PRODUCTION_PLAN_BOUNDARY_WEAKENED", field)
    return {
        "status": "PASS",
        "production_plan_sha256": claimed,
        "mandatory_nvidia_rt": mandatory,
        "selected_candidate_stable_id": plan["selected_candidate_stable_id"],
    }


def _selected_declaration(plan: Mapping[str, object]) -> Mapping[str, object]:
    nested = _mapping(plan.get("default_plan"), "default_plan")
    receipt = _mapping(nested.get("selection_receipt"), "selection_receipt")
    registry = _mapping(receipt.get("registry"), "selection_receipt.registry")
    rows = registry.get("declarations")
    if not isinstance(rows, list):
        _fail("EXPECTED_DECLARATION_LIST")
    stable_id = plan.get("selected_candidate_stable_id")
    matches = [row for row in rows if isinstance(row, Mapping) and row.get("stable_id") == stable_id]
    if len(matches) != 1:
        _fail("SELECTED_DECLARATION_NOT_UNIQUE")
    return matches[0]


def reconstruct_production_binding(
    plan: Mapping[str, object],
    binding: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    reconstruct_production_plan(plan, repository_root=repository_root)
    if binding.get("schema") != "rtdl.production_default.binding.v1":
        _fail("INVALID_PRODUCTION_BINDING_SCHEMA")
    body = dict(binding)
    claimed = body.pop("binding_sha256", None)
    if claimed != _digest(body):
        _fail("PRODUCTION_BINDING_DIGEST_MISMATCH")
    if binding.get("production_plan_sha256") != plan.get("production_plan_sha256"):
        _fail("PLAN_BINDING_IDENTITY_MISMATCH")
    declaration = _selected_declaration(plan)
    exact = {
        "selected_candidate_stable_id": "stable_id",
        "actual_backend": "backend",
        "actual_template": "template",
        "selected_source_path": "source_path",
        "selected_source_sha256": "source_sha256",
        "selected_source_anchor": "source_anchor",
    }
    for actual, expected in exact.items():
        if binding.get(actual) != declaration.get(expected):
            _fail("BINDING_DECLARATION_MISMATCH", actual)
    root = Path(repository_root).resolve()
    source = (root / str(binding["selected_source_path"])).resolve()
    try:
        source.relative_to(root)
    except ValueError:
        _fail("BOUND_SOURCE_OUTSIDE_REPOSITORY")
    if not source.is_file() or _sha256_file(source) != binding.get(
        "selected_source_sha256"
    ):
        _fail("BOUND_SOURCE_BYTES_MISMATCH")
    if str(binding["selected_source_anchor"]) not in source.read_text(
        encoding="utf-8"
    ):
        _fail("BOUND_SOURCE_ANCHOR_MISSING")
    return {"status": "PASS", "binding_sha256": claimed}


def reconstruct_production_admission(
    plan: Mapping[str, object],
    binding: Mapping[str, object],
    admission: Mapping[str, object],
    *,
    repository_root: Path,
) -> dict[str, object]:
    binding_result = reconstruct_production_binding(
        plan, binding, repository_root=repository_root
    )
    if admission.get("schema") != "rtdl.production_default.admission.v1":
        _fail("INVALID_PRODUCTION_ADMISSION_SCHEMA")
    body = dict(admission)
    claimed = body.pop("production_admission_sha256", None)
    if claimed != _digest(body):
        _fail("PRODUCTION_ADMISSION_DIGEST_MISMATCH")
    if (
        admission.get("production_plan_sha256")
        != plan.get("production_plan_sha256")
        or admission.get("binding_sha256") != binding_result["binding_sha256"]
    ):
        _fail("ADMISSION_IDENTITY_MISMATCH")
    nested = _mapping(
        admission.get("default_execution_admission"),
        "default_execution_admission",
    )
    traversal = _mapping(admission.get("traversal_receipt"), "traversal_receipt")
    if admission.get("traversal_receipt_sha256") != traversal.get(
        "receipt_sha256"
    ):
        _fail("TRAVERSAL_RECEIPT_IDENTITY_MISMATCH")
    reconstruct_default_execution_admission(
        plan["default_plan"], traversal, nested
    )
    if (
        admission.get("behavioral_optix_proven") is not True
        or admission.get("partner_stage_claimed_as_rt") is not False
        or admission.get("whole_endpoint_rt_only_proven") is not False
        or admission.get("silicon_rt_core_utilization_proven") is not False
        or admission.get("performance_claimed") is not False
    ):
        _fail("PRODUCTION_ADMISSION_CLAIM_BOUNDARY_WEAKENED")
    return {
        "status": "PASS",
        "production_admission_sha256": claimed,
        "behavioral_optix_proven": True,
    }


__all__ = [
    "ProductionDefaultReconstructionError",
    "reconstruct_production_admission",
    "reconstruct_production_binding",
    "reconstruct_production_plan",
]
