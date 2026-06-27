#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import v3_gpu_python_env_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_gpu_python_env_gate


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "v3_install_gpu_pod_env.sh"
RUNBOOK = ROOT / "docs" / "rebuild" / "v3" / "v3_setup_and_rerun_runbook_2026-06-20.md"
BLOCKERS = ROOT / "docs" / "rebuild" / "v3" / "v3_release_authorization_blockers_2026-06-20.md"
CANDIDATE = (
    ROOT / "docs" / "rebuild" / "v3" / "v3_source_tree_pod_gated_reproducibility_candidate_2026-06-21.md"
)
SCOPED_WORDING_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "v3_source_tree_pod_gated_scoped_release_wording_candidate_2026-06-21.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_review_2026-06-21.md"
)
CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_source_tree_pod_gated_reproducibility_candidate_2ai_consensus_2026-06-21.md"
)
SCOPED_WORDING_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_source_tree_pod_gated_scoped_release_wording_review_2026-06-21.md"
)
SCOPED_WORDING_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_source_tree_pod_gated_scoped_release_wording_2ai_consensus_2026-06-21.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "v3_source_tree_pod_gated_thirteen_row_scope_extension_candidate_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_review_2026-06-22.md"
)
THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_source_tree_pod_gated_thirteen_row_scope_extension_2ai_consensus_2026-06-22.md"
)

ACCEPT_FLAG = "--accept-experimental-pod-gate"
SCOPED_RELEASE_SCOPE = "source_tree_pod_gated_thirteen_row"

REQUIRED_CANDIDATE_PHRASES = (
    "source_tree_pod_gated_candidate_reviewed_not_release",
    "not a general release installer",
    "not package-install wording",
    "not release authorization",
    "--accept-experimental-pod-gate",
    "NUMBA_CUDA_PREFIX",
    "CUDA_HOME",
    "CUDA_PATH",
    "numba_cuda_jit: pass",
    "status: blocked_not_release",
    "package_install_claim_authorized: false",
    "general_release_installer_ready: false",
    "installer_closes_release_blocker: true",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row",
    "source_tree_pod_gated_candidate_present: true",
    "source_tree_pod_gated_candidate_reviewed: true",
    "accepted source-tree/pod-gated release scope",
)

REQUIRED_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `approve-with-amendments-not-release`",
    "One concrete amendment is required",
    "Numba CUDA path exports",
    "source_tree_pod_gated_candidate_reviewed: true",
    "installer_closes_release_blocker` must remain `false`",
    "This review does not authorize release.",
)

REQUIRED_CODEX_CONSENSUS_PHRASES = (
    "claude_codex_consensus_source_tree_pod_gated_candidate_reviewed_not_release",
    "Claude verdict: `approve-with-amendments-not-release`",
    "source_tree_pod_gated_candidate_reviewed: true",
    "installer_closes_release_blocker: false",
    "release_authorized: false",
    "Why The Installer Blocker Remains Open",
)

REQUIRED_SCOPED_WORDING_CANDIDATE_PHRASES = (
    "source_tree_pod_gated_scoped_release_wording_reviewed_not_release",
    "release_scope: source_tree_pod_gated_twelve_row",
    "installer_closes_release_blocker: true",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_twelve_row",
    "source_tree_pod_gated_scoped_release_wording_reviewed: true",
    "release_authorized: false",
    "general_release_installer_ready: false",
    "package_install_claim_authorized: false",
    "secondary_rt_performance_confirmation_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "This is not a general package installer.",
    "This does not authorize package-install wording.",
    "This is source-tree/pod-gated evidence from a single RTX 4000 Ada pod.",
    "This does not confirm performance across RT-core hardware classes.",
    "This does not by itself authorize V3 release.",
    "No other install-gate fields may change in this update pass.",
)

REQUIRED_SCOPED_WORDING_CLAUDE_REVIEW_PHRASES = (
    "Verdict: `accept-with-amendments-not-release`",
    "source_tree_pod_gated_eleven_row",
    "`installer_closes_release_blocker` | `false` | `true`",
    "release_scope",
    "installer_closes_release_blocker_scope",
    "This review does not authorize release.",
)

REQUIRED_SCOPED_WORDING_CODEX_CONSENSUS_PHRASES = (
    "claude_codex_consensus_source_tree_pod_gated_scoped_installer_closure_not_release",
    "Claude verdict: `accept-with-amendments-not-release`",
    "release_scope: source_tree_pod_gated_eleven_row",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_eleven_row",
    "installer_closes_release_blocker: true",
    "release_authorized: false",
    "general_release_installer_ready: false",
    "package_install_claim_authorized: false",
    "secondary_rt_performance_confirmation_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE_PHRASES = (
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
    "source_tree_pod_gated_thirteen_row",
    "aggregate_13_row_installer_scope_review_required` to false",
    "`v3_install_gpu_pod_env.sh` covers the Spatial",
    "`point_location_topology_stream` default-path configuration",
    "No new package pins, build steps, or environment variables are required",
    "local native source SHA",
    "pod-built OptiX library SHA",
    "release_authorized: false",
    "package_install_claim_authorized: false",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW_PHRASES = (
    "accept-with-amendments-not-release",
    "One P0 amendment is required",
    "Install-script coverage confirmation",
    "`release_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row`",
    "`installer_closes_release_blocker_scope` | `source_tree_pod_gated_twelve_row` | `source_tree_pod_gated_thirteen_row`",
    "`source_tree_pod_gated_thirteen_row_scope_extension_reviewed` | `false` | `true`",
    "`aggregate_13_row_installer_scope_review_required` | `true` | `false`",
    "This review does not authorize release.",
)

REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS_PHRASES = (
    "claude_codex_consensus_source_tree_pod_gated_thirteen_row_scope_extension_reviewed_not_release",
    "Claude verdict: `accept-with-amendments-not-release`",
    "v3_install_gpu_pod_env.sh covers the Spatial",
    "release_scope: source_tree_pod_gated_thirteen_row",
    "installer_closes_release_blocker_scope: source_tree_pod_gated_thirteen_row",
    "source_tree_pod_gated_thirteen_row_scope_extension_reviewed: true",
    "aggregate_13_row_installer_scope_review_required: false",
    "release_authorized: false",
    "package_install_claim_authorized: false",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _package_pins() -> dict[str, str]:
    return dict(v3_gpu_python_env_gate.PACKAGE_REQUIREMENTS)


def build_payload() -> dict[str, Any]:
    checks: dict[str, bool] = {
        "installer_exists": INSTALLER.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "blockers_doc_exists": BLOCKERS.exists(),
        "source_tree_pod_gated_candidate_exists": CANDIDATE.exists(),
        "scoped_wording_candidate_exists": SCOPED_WORDING_CANDIDATE.exists(),
        "claude_candidate_review_exists": CLAUDE_REVIEW.exists(),
        "codex_candidate_consensus_exists": CODEX_CONSENSUS.exists(),
        "scoped_wording_claude_review_exists": SCOPED_WORDING_CLAUDE_REVIEW.exists(),
        "scoped_wording_codex_consensus_exists": SCOPED_WORDING_CODEX_CONSENSUS.exists(),
        "thirteen_row_scope_extension_candidate_exists": THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE.exists(),
        "thirteen_row_scope_extension_claude_review_exists": THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW.exists(),
        "thirteen_row_scope_extension_codex_consensus_exists": THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS.exists(),
    }
    evidence: dict[str, Any] = {
        "installer": str(INSTALLER.relative_to(ROOT)),
        "runbook": str(RUNBOOK.relative_to(ROOT)),
        "blockers_doc": str(BLOCKERS.relative_to(ROOT)),
        "source_tree_pod_gated_candidate": str(CANDIDATE.relative_to(ROOT)),
        "scoped_wording_candidate": str(SCOPED_WORDING_CANDIDATE.relative_to(ROOT)),
        "claude_candidate_review": str(CLAUDE_REVIEW.relative_to(ROOT)),
        "codex_candidate_consensus": str(CODEX_CONSENSUS.relative_to(ROOT)),
        "scoped_wording_claude_review": str(SCOPED_WORDING_CLAUDE_REVIEW.relative_to(ROOT)),
        "scoped_wording_codex_consensus": str(SCOPED_WORDING_CODEX_CONSENSUS.relative_to(ROOT)),
        "thirteen_row_scope_extension_candidate": str(THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE.relative_to(ROOT)),
        "thirteen_row_scope_extension_claude_review": str(
            THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW.relative_to(ROOT)
        ),
        "thirteen_row_scope_extension_codex_consensus": str(
            THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS.relative_to(ROOT)
        ),
        "required_packages": _package_pins(),
    }

    if not all(checks.values()):
        return {
            "tool": "v3_phoenix_install_reproducibility_gate",
            "status": "fail",
            "release_authorized": False,
            "staged_gpu_pod_gate_available": False,
            "general_release_installer_ready": False,
            "failed_checks": [name for name, ok in checks.items() if not ok],
            "checks": checks,
            "evidence": evidence,
        }

    installer = _read(INSTALLER)
    runbook = _read(RUNBOOK)
    blockers = _read(BLOCKERS)
    candidate = _read(CANDIDATE)
    scoped_wording_candidate = _read(SCOPED_WORDING_CANDIDATE)
    claude_review = _read(CLAUDE_REVIEW)
    codex_consensus = _read(CODEX_CONSENSUS)
    scoped_wording_claude_review = _read(SCOPED_WORDING_CLAUDE_REVIEW)
    scoped_wording_codex_consensus = _read(SCOPED_WORDING_CODEX_CONSENSUS)
    thirteen_row_scope_extension_candidate = _read(THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE)
    thirteen_row_scope_extension_claude_review = _read(THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW)
    thirteen_row_scope_extension_codex_consensus = _read(THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS)
    dry_run_payload = v3_gpu_python_env_gate.build_payload(dry_run=True)

    checks.update(
        {
            "installer_requires_explicit_accept_flag": ACCEPT_FLAG in installer,
            "installer_refuses_default_invocation": 'if [[ "${1:-}" != "--accept-experimental-pod-gate" ]]' in installer,
            "installer_names_staged_python_gpu_package_set": "staged Python GPU package set" in installer,
            "installer_says_not_general_release_installer": "not a general release installer" in installer,
            "installer_has_no_repair_pass_label": "Repair Pass" not in installer,
            "installer_runs_gpu_env_gate": "python3 scripts/v3_gpu_python_env_gate.py --pretty" in installer,
            "runbook_names_staged_installer": "Staged installer for the tested pod-style environment" in runbook,
            "runbook_contains_accept_command": f"bash scripts/v3_install_gpu_pod_env.sh {ACCEPT_FLAG}" in runbook,
            "runbook_says_not_general_release_installer": "not a general release installer" in runbook,
            "blockers_keep_general_release_installer_open": "General release installer is not packaged" in blockers,
            "source_tree_candidate_reviewed_not_release": all(
                phrase in candidate for phrase in REQUIRED_CANDIDATE_PHRASES
            ),
            "claude_candidate_review_approves_with_amendments_not_release": all(
                phrase in claude_review for phrase in REQUIRED_CLAUDE_REVIEW_PHRASES
            ),
            "codex_candidate_consensus_reviewed_not_release": all(
                phrase in codex_consensus for phrase in REQUIRED_CODEX_CONSENSUS_PHRASES
            ),
            "scoped_wording_candidate_reviewed_not_release": all(
                phrase in scoped_wording_candidate for phrase in REQUIRED_SCOPED_WORDING_CANDIDATE_PHRASES
            ),
            "scoped_wording_claude_review_accepts_with_amendments_not_release": all(
                phrase in scoped_wording_claude_review
                for phrase in REQUIRED_SCOPED_WORDING_CLAUDE_REVIEW_PHRASES
            ),
            "scoped_wording_codex_consensus_closes_installer_scope_not_release": all(
                phrase in scoped_wording_codex_consensus
                for phrase in REQUIRED_SCOPED_WORDING_CODEX_CONSENSUS_PHRASES
            ),
            "thirteen_row_scope_extension_candidate_reviewed_not_release": all(
                phrase in thirteen_row_scope_extension_candidate
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CANDIDATE_PHRASES
            ),
            "thirteen_row_scope_extension_claude_accepts_with_amendments_not_release": all(
                phrase in thirteen_row_scope_extension_claude_review
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CLAUDE_REVIEW_PHRASES
            ),
            "thirteen_row_scope_extension_codex_consensus_reviewed_not_release": all(
                phrase in thirteen_row_scope_extension_codex_consensus
                for phrase in REQUIRED_THIRTEEN_ROW_SCOPE_EXTENSION_CODEX_CONSENSUS_PHRASES
            ),
            "gpu_env_dry_run_status": dry_run_payload.get("status") == "dry_run",
            "gpu_env_requirements_match_installer": all(
                f'"{name}=={version}"' in installer for name, version in _package_pins().items()
            ),
            "torch_installed_from_cu124_index": "https://download.pytorch.org/whl/cu124" in installer,
        }
    )

    failed_checks = [name for name, ok in checks.items() if not ok]
    status = "fail" if failed_checks else "staged_pod_gate_present_general_release_installer_not_ready"

    evidence.update(
        {
            "accept_flag": ACCEPT_FLAG,
            "gpu_env_gate_dry_run": {
                "status": dry_run_payload.get("status"),
                "required_packages": dry_run_payload.get("required_packages"),
                "env_keys": sorted(dry_run_payload.get("env", {}).keys()),
            },
            "install_scope": {
                "staged_gpu_pod_gate_available": status == "staged_pod_gate_present_general_release_installer_not_ready",
                "release_scope": SCOPED_RELEASE_SCOPE,
                "source_tree_pod_gated_candidate_present": checks["source_tree_pod_gated_candidate_exists"],
                "source_tree_pod_gated_candidate_reviewed": True,
                "source_tree_pod_gated_scoped_release_wording_reviewed": True,
                "source_tree_pod_gated_thirteen_row_scope_extension_reviewed": True,
                "aggregate_13_row_installer_scope_review_required": False,
                "general_release_installer_ready": False,
                "installer_closes_release_blocker": True,
                "installer_closes_release_blocker_scope": SCOPED_RELEASE_SCOPE,
                "package_install_claim_authorized": False,
                "release_authorized": False,
            },
        }
    )

    return {
        "tool": "v3_phoenix_install_reproducibility_gate",
        "status": status,
        "release_authorized": False,
        "package_install_claim_authorized": False,
        "staged_gpu_pod_gate_available": status == "staged_pod_gate_present_general_release_installer_not_ready",
        "release_scope": SCOPED_RELEASE_SCOPE,
        "general_release_installer_ready": False,
        "source_tree_pod_gated_candidate_present": checks.get("source_tree_pod_gated_candidate_exists", False),
        "source_tree_pod_gated_candidate_reviewed": True,
        "source_tree_pod_gated_scoped_release_wording_reviewed": True,
        "source_tree_pod_gated_thirteen_row_scope_extension_reviewed": True,
        "aggregate_13_row_installer_scope_review_required": False,
        "installer_closes_release_blocker": True,
        "installer_closes_release_blocker_scope": SCOPED_RELEASE_SCOPE,
        "required_next_action": (
            "Keep the installer closure scoped to source_tree_pod_gated_thirteen_row and "
            "obtain the separate aggregate 13-row release-readiness review before any release wording."
        ),
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": evidence,
        "decision_audit": {
            "decision": "Extend installer/reproducibility closure only under the source_tree_pod_gated_thirteen_row scope.",
            "was_i_foolish": "No. Claude required explicit Spatial install-script coverage, Codex recorded consensus, and release/general-installer/package-install fields remain false.",
            "foolish_actions": "The foolish action would be silently broadening installer_closes_release_blocker_scope from twelve rows to thirteen rows without external review.",
            "other_path": "Build a general package installer first. That remains the path for future package-install wording.",
            "different_path_now": "Keep installer wording scoped and request the separate aggregate 13-row release-readiness review before any release wording.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify Phoenix V3 install/reproducibility readiness.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if payload["status"] == "staged_pod_gate_present_general_release_installer_not_ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
