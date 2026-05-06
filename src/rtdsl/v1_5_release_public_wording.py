from __future__ import annotations

from pathlib import Path
from typing import Any

from .v1_5_benchmark_evidence import validate_v1_5_benchmark_evidence_summary
from .v1_5_standalone_app_classification import (
    validate_v1_5_standalone_app_classification_matrix,
)
from .v1_5_standalone_correctness import validate_v1_5_standalone_correctness_summary
from .v1_5_support_maturity import validate_v1_5_support_maturity_summary


V1_5_RELEASE_PUBLIC_WORDING_STATUS = "release_candidate_docs_ready"
V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_DOCS = (
    "README.md",
    "docs/README.md",
    "docs/release_reports/v1_5/README.md",
    "docs/release_reports/v1_5/release_statement.md",
    "docs/release_reports/v1_5/support_matrix.md",
    "docs/release_reports/v1_5/audit_report.md",
    "docs/release_reports/v1_5/tag_preparation.md",
)
V1_5_RELEASE_PUBLIC_WORDING_ALLOWED_STATEMENT = (
    "RTDL v1.5 is the standalone Embree+OptiX language/runtime completion "
    "candidate for the supported v1.5 surface: generic traversal-plus-reduction "
    "primitives, 14 included app contracts, explicit exclusion of row-returning "
    "COLLECT_K_BOUNDED apps, and no new whole-app speedup claim."
)
V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_PHRASES = (
    "standalone Embree+OptiX",
    "14 included",
    "4 excluded",
    "COLLECT_K_BOUNDED",
    "v1.5.1",
    "no whole-app speedup",
    "PYTHONPATH=src:. python",
    "explicit release/tag action",
)
V1_5_RELEASE_PUBLIC_WORDING_FORBIDDEN_PHRASES = (
    "pip install -e .",
    "all applications are faster",
    "whole-app speedup is authorized",
    "COLLECT_K_BOUNDED is stable",
    "Vulkan is an active v1.5 backend",
    "HIPRT is an active v1.5 backend",
    "Apple RT is an active v1.5 backend",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_doc(relative_path: str) -> str:
    path = _repo_root() / relative_path
    if not path.exists():
        raise ValueError(f"missing v1.5 release/public wording doc: {relative_path}")
    return path.read_text(encoding="utf-8")


def v1_5_release_public_wording_gate() -> dict[str, Any]:
    """Return the v1.5 release-doc/public-wording gate.

    This gate is deliberately narrower than a tag operation. Passing it means
    the release-candidate docs and wording boundary are present and internally
    consistent; it does not move `v1.0`, create `v1.5`, or authorize broad
    speedup language.
    """
    classification = validate_v1_5_standalone_app_classification_matrix()
    correctness = validate_v1_5_standalone_correctness_summary()
    support = validate_v1_5_support_maturity_summary()
    benchmark = validate_v1_5_benchmark_evidence_summary()
    docs = {relative_path: _read_doc(relative_path) for relative_path in V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_DOCS}
    combined = "\n".join(docs.values())
    included_apps = tuple(
        sorted(app for app, row in classification.items() if row["standalone_included"])
    )
    excluded_apps = tuple(
        sorted(app for app, row in classification.items() if not row["standalone_included"])
    )
    missing_required_phrases = tuple(
        phrase for phrase in V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_PHRASES if phrase not in combined
    )
    present_forbidden_phrases = tuple(
        phrase for phrase in V1_5_RELEASE_PUBLIC_WORDING_FORBIDDEN_PHRASES if phrase in combined
    )
    return {
        "status": V1_5_RELEASE_PUBLIC_WORDING_STATUS,
        "required_docs": V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_DOCS,
        "allowed_public_statement": V1_5_RELEASE_PUBLIC_WORDING_ALLOWED_STATEMENT,
        "included_apps": included_apps,
        "excluded_apps": excluded_apps,
        "included_app_count": len(included_apps),
        "excluded_app_count": len(excluded_apps),
        "correctness_gate_complete": correctness["release_gate_complete"],
        "support_maturity_gate_complete": support["release_gate_complete"],
        "benchmark_evidence_gate_complete": benchmark["release_gate_complete"],
        "missing_required_phrases": missing_required_phrases,
        "present_forbidden_phrases": present_forbidden_phrases,
        "release_docs_and_public_wording_complete": (
            not missing_required_phrases
            and not present_forbidden_phrases
            and correctness["release_gate_complete"]
            and support["release_gate_complete"]
            and benchmark["release_gate_complete"]
        ),
        "public_release_authorized_by_this_gate": False,
        "release_tag_action_authorized_by_this_gate": False,
        "public_speedup_wording_authorized_by_this_gate": False,
        "explicit_release_approval_required": True,
    }


def validate_v1_5_release_public_wording_gate() -> dict[str, Any]:
    gate = v1_5_release_public_wording_gate()
    if gate["status"] != V1_5_RELEASE_PUBLIC_WORDING_STATUS:
        raise ValueError("invalid v1.5 release/public wording gate status")
    if tuple(gate["required_docs"]) != V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_DOCS:
        raise ValueError("v1.5 release/public wording docs mismatch")
    if int(gate["included_app_count"]) != 14:
        raise ValueError("v1.5 release/public wording must list 14 included apps")
    if int(gate["excluded_app_count"]) != 4:
        raise ValueError("v1.5 release/public wording must list 4 excluded apps")
    if tuple(gate["missing_required_phrases"]) != ():
        raise ValueError(
            "v1.5 release/public wording is missing required phrases: "
            + ", ".join(gate["missing_required_phrases"])
        )
    if tuple(gate["present_forbidden_phrases"]) != ():
        raise ValueError(
            "v1.5 release/public wording contains forbidden phrases: "
            + ", ".join(gate["present_forbidden_phrases"])
        )
    for field in (
        "correctness_gate_complete",
        "support_maturity_gate_complete",
        "benchmark_evidence_gate_complete",
        "release_docs_and_public_wording_complete",
    ):
        if gate[field] is not True:
            raise ValueError(f"v1.5 release/public wording gate must complete {field}")
    for field in (
        "public_release_authorized_by_this_gate",
        "release_tag_action_authorized_by_this_gate",
        "public_speedup_wording_authorized_by_this_gate",
    ):
        if gate[field] is not False:
            raise ValueError(f"v1.5 release/public wording gate must not authorize {field}")
    if gate["explicit_release_approval_required"] is not True:
        raise ValueError("v1.5 release/public wording must require explicit release approval")
    return gate
