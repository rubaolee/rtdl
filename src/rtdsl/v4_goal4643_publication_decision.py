from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .v4 import V4_AUTHORIZED_RELEASE_LABEL
from .v4 import claim_boundary_v4
from .v4_release_decision import validate_v4_goal4632_release_decision
from .v4_scope import validate_v4_0_scope_gate
from .v4_scope import v4_0_scope_gate


V4_GOAL4643_DECISION = "goal4643_publication_record_superseded_by_goal4720_release_candidate_review_debt"
V4_GOAL4643_STATUS = "v4_0_0_publication_record_superseded_by_goal4720"


def _project_version(pyproject_text: str) -> str:
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', pyproject_text)
    if not match:
        raise ValueError("pyproject.toml version not found")
    return match.group(1)


def v4_goal4643_publication_decision(root: Path | None = None) -> dict[str, Any]:
    """Return the machine-readable V4.0.0 publication decision."""

    repo = root or Path(__file__).resolve().parents[2]
    release_decision = validate_v4_goal4632_release_decision()
    scope_gate = v4_0_scope_gate().as_dict()
    scope_validation = validate_v4_0_scope_gate(scope_gate)
    front_door = claim_boundary_v4()
    pyproject_version = _project_version((repo / "pyproject.toml").read_text(encoding="utf-8"))
    version_file = (repo / "VERSION").read_text(encoding="utf-8").strip()
    required_reviews = (
        "tools/_archive/future/v4/reviews/v4_goal4717_custom_predicate_early_exit_serious_scale_validation_review_debt_2026-06-26.md",
        "tools/_archive/future/v4/reviews/v4_goal4718_release_matrix_after_custom_predicate_review_debt_2026-06-26.md",
        "tools/_archive/future/v4/reviews/v4_goal4719_public_docs_examples_release_candidate_cleanup_review_debt_2026-06-26.md",
    )
    required_docs = (
        "README.md",
        "docs/current_v4_status.md",
        "tools/_archive/future/v4/README.md",
        "tools/_archive/future/v4/tier2_operator_catalog.md",
        "tools/_archive/future/v4/v4_0_scope_gate.md",
    )

    return {
        "status": V4_GOAL4643_STATUS,
        "decision": V4_GOAL4643_DECISION,
        "authorized_release_label": V4_AUTHORIZED_RELEASE_LABEL,
        "version": version_file,
        "pyproject_version": pyproject_version,
        "release_authorized": False,
        "formal_release_authorized": False,
        "bounded_operator_surface_available": front_door["bounded_operator_surface_available"],
        "app_level_high_performance_authorized": front_door["app_level_high_performance_authorized"],
        "superseded_by_goal": "Goal4720",
        "current_decision_label": front_door["current_app_level_decision_label"],
        "front_door_status": front_door["status"],
        "front_door_formal_release_authorized": front_door["formal_release_authorized"],
        "scope_status": scope_gate["status"],
        "scope_release_authorized": scope_gate["release_authorized"],
        "scope_validation_status": scope_validation["status"],
        "release_decision": release_decision["decision"],
        "release_blockers": release_decision["release_blockers"],
        "scope_limitations": release_decision["scope_limitations"],
        "measured_surfaces_count": release_decision["measured_surfaces_count"],
        "candidate_surfaces_count": release_decision["candidate_surfaces_count"],
        "forbidden_claims": release_decision["forbidden_claims"],
        "required_reviews": required_reviews,
        "required_reviews_present": tuple(path for path in required_reviews if (repo / path).exists()),
        "required_public_docs": required_docs,
        "required_public_docs_present": tuple(path for path in required_docs if (repo / path).exists()),
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "c_abi_or_embedding_claim_authorized": False,
        "non_python_host_claim_authorized": False,
        "app_specific_native_kernel_authorized": False,
    }


def validate_v4_goal4643_publication_decision(root: Path | None = None) -> dict[str, Any]:
    decision = v4_goal4643_publication_decision(root)
    if decision["decision"] != V4_GOAL4643_DECISION:
        raise ValueError("Goal4643 publication decision drift")
    if decision["version"] != "v4.0.0":
        raise ValueError("VERSION must be v4.0.0 for publication")
    if decision["pyproject_version"] != "4.0.0":
        raise ValueError("pyproject version must be 4.0.0 for publication")
    if decision["authorized_release_label"] != V4_AUTHORIZED_RELEASE_LABEL:
        raise ValueError("Goal4643 authorized release label drift")
    if decision["release_authorized"] or decision["formal_release_authorized"]:
        raise ValueError("Goal4643 current record must not authorize the formal V4.0.0 release")
    if decision["front_door_formal_release_authorized"]:
        raise ValueError("V4 front door must not expose formal release authorization")
    if not decision["bounded_operator_surface_available"]:
        raise ValueError("Goal4643 current record must preserve bounded operator-surface availability")
    if decision["app_level_high_performance_authorized"]:
        raise ValueError("Goal4643 current record must not authorize app-level high performance")
    if decision["scope_release_authorized"]:
        raise ValueError("V4 scope gate must not authorize release")
    if decision["scope_validation_status"] != "passed":
        raise ValueError("V4 scope gate must validate")
    if not decision["release_blockers"]:
        raise ValueError("Goal4643 current record must carry current release blockers")
    if tuple(decision["required_reviews"]) != tuple(decision["required_reviews_present"]):
        raise ValueError("Goal4643 missing required review records")
    if tuple(decision["required_public_docs"]) != tuple(decision["required_public_docs_present"]):
        raise ValueError("Goal4643 missing required public docs")
    for claim in (
        "broad V4 speedup",
        "whole-application speedup",
        "all-benchmark speedup",
        "public true-zero-copy",
        "Tier-3 callback support",
        "raw OptiX callback support",
        "CuPy performance",
        "C ABI / embedding / non-Python host",
        "app-specific native kernels",
        "Barnes-Hut new V4-over-V3 speedup",
        "Spatial RayJoin speedup",
        "LibRTS paper reproduction",
    ):
        if claim not in decision["forbidden_claims"]:
            raise ValueError(f"Missing forbidden claim: {claim}")
    for flag in (
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
        "cupy_performance_claim_authorized",
        "c_abi_or_embedding_claim_authorized",
        "non_python_host_claim_authorized",
        "app_specific_native_kernel_authorized",
    ):
        if decision[flag]:
            raise ValueError(f"Goal4643 must not authorize {flag}")
    return decision


__all__ = [
    "V4_GOAL4643_DECISION",
    "V4_GOAL4643_STATUS",
    "v4_goal4643_publication_decision",
    "validate_v4_goal4643_publication_decision",
]
