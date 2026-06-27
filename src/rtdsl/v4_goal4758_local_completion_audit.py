from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .v4 import claim_boundary_v4
from .v4_app_compatibility import validate_v4_app_compatibility_catalog
from .v4_goal4757_final_release_packet import validate_v4_goal4757_final_release_packet
from .v4_operator_catalog import certified_v4_partner_operator_catalog
from .v4_operator_catalog import measured_v4_tier2_operator_catalog


V4_GOAL4758_STATUS = "local_v4_0_completion_audit_passed_external_release_review_open"
V4_GOAL4758_DECISION = "local_development_testing_docs_and_release_evidence_complete_not_public_tag_authorized"


@dataclass(frozen=True)
class V4Goal4758Requirement:
    requirement: str
    status: str
    evidence: tuple[str, ...]
    limitation: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "requirement": self.requirement,
            "status": self.status,
            "evidence": self.evidence,
            "limitation": self.limitation,
        }


def _public_docs() -> tuple[str, ...]:
    return (
        "README.md",
        "docs/current_v4_status.md",
        "docs/app_level_benchmark_summary.md",
        "docs/learn/performance_wording.md",
        "tools/_archive/future/v4/README.md",
        "tools/_archive/future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md",
    )


def v4_goal4758_local_completion_audit(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    boundary = claim_boundary_v4()
    compatibility = validate_v4_app_compatibility_catalog()
    goal4757 = validate_v4_goal4757_final_release_packet(repo)
    measured_catalog = measured_v4_tier2_operator_catalog()
    certified_catalog = certified_v4_partner_operator_catalog()

    measured_partners = tuple(boundary["measured_partners"])
    certified_partners = tuple(boundary["certified_partners"])
    cupy_certified = tuple(row for row in certified_catalog if "cupy" in row["measured_partners"])
    numba_certified = tuple(row for row in certified_catalog if "numba" in row["measured_partners"])
    cupy_measured = tuple(row for row in measured_catalog if "cupy" in row["measured_partners"])
    numba_measured = tuple(row for row in measured_catalog if "numba" in row["measured_partners"])
    package_wheel = "tools/_archive/dist/goal4758_v4_release_candidate/rtdl_source_tree-4.0.0-py3-none-any.whl"
    package_log = "tools/_archive/future/v4/evidence/v4_goal4758_package_wheel_build_2026-06-26.log"
    wheel_install_log = (
        "tools/_archive/future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/"
        "wheel_install_with_deps.log"
    )
    wheel_import_log = (
        "tools/_archive/future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/"
        "import_claim_boundary_after_install.log"
    )
    wheel_smoke_summary = (
        "tools/_archive/future/v4/evidence/v4_goal4758_wheel_install_smoke_2026-06-26/"
        "summary.json"
    )
    review_manifest = "tools/_archive/future/v4/evidence/v4_goal4759_final_review_evidence_manifest_2026-06-26.json"
    wheel_path = repo / package_wheel
    wheel_sha256 = hashlib.sha256(wheel_path.read_bytes()).hexdigest() if wheel_path.exists() else ""
    wheel_size = wheel_path.stat().st_size if wheel_path.exists() else 0

    requirements = (
        V4Goal4758Requirement(
            requirement="V4.0 is a V2/V3 superset for promoted benchmark routes",
            status="proved",
            evidence=(
                "src/rtdsl/v4_app_compatibility.py",
                "tests/v4_goal4751_app_compatibility_catalog_test.py",
                "tools/_archive/future/v4/evidence/v4_goal4751_app_compatibility_catalog_2026-06-26.json",
            ),
        ),
        V4Goal4758Requirement(
            requirement="Complete 10-app same-semantics NVIDIA RT-core V2.14/V3.0.2/V4.0 matrix",
            status="proved",
            evidence=(
                "tools/_archive/future/v4/evidence/v4_goal4756_serious_all30_generated_spatial_2026-06-26/",
                "tools/_archive/future/v4/evidence/v4_goal4756_final_rt_core_matrix_analysis_2026-06-26.json",
                "tools/_archive/future/v4/v4_goal4756_final_rt_core_matrix_release_readout_2026-06-26.md",
            ),
            limitation="Does not authorize broad all-benchmark speedup wording.",
        ),
        V4Goal4758Requirement(
            requirement="First-class explicit CuPy partner support in V4.0",
            status="proved_bounded",
            evidence=(
                "src/rtdsl/v4_cupy_certification.py",
                "tests/v4_goal4649_cupy_certification_gate_test.py",
                "tools/_archive/future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json",
                "tools/_archive/future/v4/tier2_operator_catalog.md",
            ),
            limitation="Broad CuPy performance wording remains unauthorized; support is where explicitly measured/certified.",
        ),
        V4Goal4758Requirement(
            requirement="First-class explicit Numba partner support in V4.0",
            status="proved_bounded",
            evidence=(
                "src/rtdsl/v4_numba_fixed_continuation_certification.py",
                "src/rtdsl/v4_custom_predicate_early_exit.py",
                "tests/v4_goal4650_fixed_numba_continuation_certification_test.py",
                "tests/v4_goal4716_custom_predicate_early_exit_productization_test.py",
                "tools/_archive/future/v4/evidence/v4_goal4718_release_matrix_after_custom_predicate_2026-06-26.json",
            ),
            limitation="Arbitrary Numba ray-action callbacks remain V4.1/Tier-3 work.",
        ),
        V4Goal4758Requirement(
            requirement="Clean current docs/examples with one coherent V4.0 user story",
            status="proved",
            evidence=(
                "README.md",
                "docs/current_v4_status.md",
                "docs/app_level_benchmark_summary.md",
                "docs/learn/performance_wording.md",
                "tools/_archive/future/v4/README.md",
                "examples/README.md",
                "tutorials/current/README.md",
            ),
        ),
        V4Goal4758Requirement(
            requirement="Current-tree V4.0 Python wheel builds after final packet/audit changes",
            status="proved",
            evidence=(
                package_wheel,
                package_log,
            ),
        ),
        V4Goal4758Requirement(
            requirement="Current-tree V4.0 wheel installs with dependencies and exposes V4 front door",
            status="proved",
            evidence=(
                wheel_smoke_summary,
                wheel_install_log,
                wheel_import_log,
            ),
            limitation="Windows Python emits a platform-library warning in this workspace, but import/front-door smoke succeeds.",
        ),
        V4Goal4758Requirement(
            requirement="Final review evidence manifest records artifact hashes",
            status="proved",
            evidence=(
                review_manifest,
                "tools/_archive/future/v4/v4_goal4759_final_review_evidence_manifest_2026-06-26.md",
            ),
        ),
        V4Goal4758Requirement(
            requirement="Final release review evidence prepared",
            status="proved_external_review_open",
            evidence=(
                "tools/_archive/future/v4/v4_goal4757_final_v4_0_release_packet_after_goal4756_2026-06-26.md",
                "tools/_archive/future/v4/reviews/call_for_review_v4_goal4757_final_v4_0_release_after_goal4756_2026-06-26.md",
                "tools/_archive/future/v4/reviews/v4_goal4757_final_release_external_review_debt_2026-06-26.md",
            ),
            limitation="Public tag remains unauthorized until external release verdicts are obtained.",
        ),
    )

    return {
        "status": V4_GOAL4758_STATUS,
        "decision": V4_GOAL4758_DECISION,
        "requirement_count": len(requirements),
        "requirements": tuple(item.as_dict() for item in requirements),
        "front_door_status": boundary["status"],
        "measured_partners": measured_partners,
        "certified_partners": certified_partners,
        "measured_surface_count": boundary["measured_surface_count"],
        "certified_partner_surface_count": boundary["certified_partner_surface_count"],
        "cupy_certified_surface_count": len(cupy_certified),
        "cupy_measured_surface_count": len(cupy_measured),
        "numba_certified_surface_count": len(numba_certified),
        "numba_measured_surface_count": len(numba_measured),
        "app_compatibility_row_count": compatibility["row_count"],
        "app_compatibility_repair_required_apps": tuple(compatibility["repair_required_apps"]),
        "complete_rt_core_app_matrix_app_count": goal4757["app_count"],
        "complete_rt_core_app_matrix_row_count": goal4757["matrix_row_count"],
        "goal4756_material_candidate_apps": goal4757["material_candidate_apps"],
        "goal4756_regression_apps": goal4757["regression_apps"],
        "package_wheel": package_wheel,
        "package_wheel_size": wheel_size,
        "package_wheel_sha256": wheel_sha256,
        "package_build_log": package_log,
        "wheel_install_log": wheel_install_log,
        "wheel_import_log": wheel_import_log,
        "wheel_smoke_summary": wheel_smoke_summary,
        "final_review_manifest": review_manifest,
        "external_review_debt_open": goal4757["external_review_debt_open"],
        "release_authorized": False,
        "public_tag_authorized": False,
        "broad_v4_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "all_benchmark_speedup_claim_authorized": False,
        "cupy_performance_claim_authorized": False,
        "tier3_callback_claim_authorized": False,
        "raw_optix_callback_claim_authorized": False,
    }


def validate_v4_goal4758_local_completion_audit(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    audit = v4_goal4758_local_completion_audit(repo)

    if audit["status"] != V4_GOAL4758_STATUS:
        raise ValueError("Goal4758 completion audit status drift")
    if audit["decision"] != V4_GOAL4758_DECISION:
        raise ValueError("Goal4758 completion audit decision drift")
    if audit["requirement_count"] != 9:
        raise ValueError("Goal4758 must audit all nine objective/release requirements")
    if tuple(audit["measured_partners"]) != ("cupy", "numba", "rtdl_native", "torch"):
        raise ValueError("Goal4758 measured partner set drift")
    if "cupy" not in audit["certified_partners"] or "numba" not in audit["certified_partners"]:
        raise ValueError("Goal4758 requires certified CuPy and Numba partner surfaces")
    if audit["cupy_certified_surface_count"] < 1 or audit["cupy_measured_surface_count"] < 1:
        raise ValueError("Goal4758 requires bounded CuPy certified and measured surfaces")
    if audit["numba_certified_surface_count"] < 1 or audit["numba_measured_surface_count"] < 1:
        raise ValueError("Goal4758 requires bounded Numba certified and measured surfaces")
    if audit["app_compatibility_row_count"] != 10 or audit["app_compatibility_repair_required_apps"]:
        raise ValueError("Goal4758 requires all ten apps to be V4 compatibility-ready")
    if audit["complete_rt_core_app_matrix_app_count"] != 10:
        raise ValueError("Goal4758 matrix app count drift")
    if audit["complete_rt_core_app_matrix_row_count"] != 30:
        raise ValueError("Goal4758 matrix row count drift")
    if set(audit["goal4756_material_candidate_apps"]) != {"triangle_counting", "barnes_hut"}:
        raise ValueError("Goal4758 material candidate set drift")
    if audit["goal4756_regression_apps"]:
        raise ValueError("Goal4758 must not carry hot-path regression apps")
    if audit["package_wheel_size"] <= 0:
        raise ValueError("Goal4758 requires a current-tree V4.0 wheel artifact")
    if audit["package_wheel_sha256"] != "4f349985e0daa8e16cbbfe90cab8663c8517815b1f22c8d6be67901a7da2eed5":
        raise ValueError("Goal4758 package wheel sha256 drift")
    for path_key in (
        "package_wheel",
        "package_build_log",
        "wheel_install_log",
        "wheel_import_log",
        "wheel_smoke_summary",
        "final_review_manifest",
    ):
        if not (repo / audit[path_key]).exists():
            raise ValueError(f"Goal4758 missing package artifact: {audit[path_key]}")
    package_log = (repo / audit["package_build_log"]).read_text(encoding="utf-8")
    if "Successfully built rtdl-source-tree" not in package_log:
        raise ValueError("Goal4758 package build log must show successful wheel build")
    install_log = (repo / audit["wheel_install_log"]).read_text(encoding="utf-8")
    if "Successfully installed" not in install_log or "rtdl-source-tree-4.0.0" not in install_log:
        raise ValueError("Goal4758 wheel install log must show successful installed wheel")
    smoke = json.loads((repo / audit["wheel_smoke_summary"]).read_text(encoding="utf-8"))
    if smoke["status"] != "passed" or smoke["install_status"] != "passed" or smoke["smoke_status"] != "passed":
        raise ValueError("Goal4758 installed-wheel smoke must pass")
    if smoke["matrix_apps"] != 10 or smoke["matrix_rows"] != 30:
        raise ValueError("Goal4758 installed-wheel smoke matrix facts drift")
    if tuple(smoke["measured_partners"]) != ("cupy", "numba", "rtdl_native", "torch"):
        raise ValueError("Goal4758 installed-wheel smoke measured partners drift")
    if smoke["cupy_grouped_vector_sum_status"] != "certified_partner_measured_ready":
        raise ValueError("Goal4758 installed-wheel smoke must prove CuPy certified partner planner")
    if smoke["numba_component_union_status"] != "tier2_measured_ready":
        raise ValueError("Goal4758 installed-wheel smoke must prove Numba measured planner")
    if smoke["release_authorized"] or smoke["public_tag_authorized"]:
        raise ValueError("Goal4758 installed-wheel smoke must not authorize release")
    manifest = json.loads((repo / audit["final_review_manifest"]).read_text(encoding="utf-8"))
    if manifest["status"] != "ready_for_external_review_not_release_authorization":
        raise ValueError("Goal4758 final review manifest must be ready for external review")
    if manifest["artifact_count"] != 27 or manifest["missing_artifacts"] or manifest["empty_artifacts"]:
        raise ValueError("Goal4758 final review manifest must cover all required artifacts")
    manifest_ids = {artifact["id"] for artifact in manifest["artifacts"]}
    for required_delta in (
        "goal4769_barnes_hut_author_phase_report",
        "goal4769_barnes_hut_author_phase_stdout",
        "goal4770_barnes_hut_delta_json",
        "goal4770_barnes_hut_delta_md",
        "goal4770_barnes_hut_delta_review_debt",
    ):
        if required_delta not in manifest_ids:
            raise ValueError(f"Goal4758 final review manifest missing supplemental delta: {required_delta}")
    if manifest["release_authorized"] or manifest["public_tag_authorized"]:
        raise ValueError("Goal4758 final review manifest must not authorize release")
    if not audit["external_review_debt_open"]:
        raise ValueError("Goal4758 must keep external review debt open until verdicts arrive")
    for flag in (
        "release_authorized",
        "public_tag_authorized",
        "broad_v4_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "all_benchmark_speedup_claim_authorized",
        "cupy_performance_claim_authorized",
        "tier3_callback_claim_authorized",
        "raw_optix_callback_claim_authorized",
    ):
        if audit[flag]:
            raise ValueError(f"Goal4758 must not authorize {flag}")

    combined_public_docs = "\n".join((repo / path).read_text(encoding="utf-8") for path in _public_docs())
    for required in (
        "V2/V3 superset",
        "10 promoted benchmark apps",
        "CuPy",
        "Numba",
        "It does not say every benchmark app is",
        "public true-zero-copy",
        "Tier-3",
    ):
        if required not in combined_public_docs:
            raise ValueError(f"Goal4758 public docs missing boundary text: {required}")
    for stale in (
        "Barnes-Hut covered by V4.0",
        "Spatial RayJoin covered by V4.0",
        "near-OptiX performance from Python",
        "Representative operator geomean",
    ):
        if stale in combined_public_docs:
            raise ValueError(f"Goal4758 public docs retain stale wording: {stale}")
    return audit


__all__ = [
    "V4_GOAL4758_STATUS",
    "V4_GOAL4758_DECISION",
    "V4Goal4758Requirement",
    "v4_goal4758_local_completion_audit",
    "validate_v4_goal4758_local_completion_audit",
]
