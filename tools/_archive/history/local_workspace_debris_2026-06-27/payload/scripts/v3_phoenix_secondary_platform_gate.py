#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "rebuild" / "v3" / "evidence"

ALL_BENCHMARK_LX1 = EVIDENCE_ROOT / "v3_all_benchmark_lx1_confirmation_20260620"
PAIRED_REPORT_LX1 = EVIDENCE_ROOT / "v3_paired_report_lx1_confirmation_20260620"
SECOND_MACHINE_LX1 = EVIDENCE_ROOT / "v3_second_machine_lx1_confirmation_20260620"
WAIVER_CANDIDATE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "v3_secondary_rt_hardware_scope_waiver_candidate_2026-06-21.md"
)
WAIVER_CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "claude_phoenix_v3_secondary_rt_hardware_scope_waiver_review_2026-06-21.md"
)
WAIVER_CODEX_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_secondary_rt_hardware_scope_waiver_2ai_consensus_2026-06-21.md"
)
WAIVER_SCOPE = "single_rtx_4000_ada_driver_550_127_05_pod"
WAIVER_METHOD = "reviewed_hardware_scoped_waiver"

EVIDENCE_DIRS = (ALL_BENCHMARK_LX1, PAIRED_REPORT_LX1, SECOND_MACHINE_LX1)

REQUIRED_WAIVER_CANDIDATE_PHRASES = (
    "secondary_rt_hardware_scope_waiver_candidate_pending_external_review",
    "hardware_performance_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "secondary_rt_performance_confirmation_authorized: false",
    "secondary_rt_hardware_scope_waiver_reviewed: true",
    "secondary_platform_closes_release_blocker: true",
    "secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "multi_gpu_performance_portability_claim_authorized: false",
    "release_authorized: false",
)

REQUIRED_WAIVER_REVIEW_PHRASES = (
    "accept-with-amendments-not-release",
    "secondary_rt_hardware_scope_waiver_reviewed",
    "secondary_platform_closes_release_blocker: true",
    "secondary_rt_performance_confirmation_authorized: false",
    "release_authorized: false",
    "single_rtx_4000_ada_driver_550_127_05_pod",
    "This review does not authorize V3 release.",
)

REQUIRED_WAIVER_CONSENSUS_PHRASES = (
    "claude_codex_consensus_secondary_rt_hardware_scope_waiver_not_release",
    "accept-with-amendments-not-release",
    "secondary_rt_hardware_scope_waiver_reviewed: true",
    "secondary_platform_closes_release_blocker: true",
    "secondary_platform_closes_release_blocker_method: reviewed_hardware_scoped_waiver",
    "secondary_platform_closes_release_blocker_scope: single_rtx_4000_ada_driver_550_127_05_pod",
    "secondary_rt_performance_confirmation_authorized: false",
    "multi_gpu_performance_portability_claim_authorized: false",
    "broad_v3_faster_than_v2_claim_authorized: false",
    "package_install_claim_authorized: false",
    "release_authorized: false",
    "This consensus does not authorize release.",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contains_all(path: Path, phrases: tuple[str, ...]) -> bool:
    if not path.exists():
        return False
    text = _read_text(path)
    return all(phrase in text for phrase in phrases)


def _host_payload(path: Path) -> dict[str, Any]:
    text = _read_text(path / "host.txt")
    return {
        "path": str((path / "host.txt").relative_to(ROOT)),
        "text": text.strip(),
        "host_lx1": "lx1" in text,
        "gpu": "NVIDIA GeForce GTX 1070" if "NVIDIA GeForce GTX 1070" in text else "unknown",
        "gtx_1070": "NVIDIA GeForce GTX 1070" in text,
    }


def _matrix_payload(path: Path) -> dict[str, Any]:
    payload = _read_json(path / "v3_rebuild_matrix.json")
    return {
        "path": str((path / "v3_rebuild_matrix.json").relative_to(ROOT)),
        "ok": payload.get("ok") is True,
        "module_count": payload.get("module_count"),
        "returncode": payload.get("returncode"),
    }


def _doctor_payload(path: Path) -> dict[str, Any]:
    payload = _read_json(path / "source_tree_doctor.json")
    return {
        "path": str((path / "source_tree_doctor.json").relative_to(ROOT)),
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "required_failures": payload.get("required_failures", []),
    }


def _wording_payload(path: Path) -> dict[str, Any]:
    payload = _read_json(path / "wording_gate.json")
    return {
        "path": str((path / "wording_gate.json").relative_to(ROOT)),
        "status": payload.get("status"),
        "pass": payload.get("status") == "pass",
        "violations": payload.get("violations", []),
    }


def _gpu_env_payload(path: Path) -> dict[str, Any]:
    payload = _read_json(path / "gpu_env_gate_summary.json")
    checks = payload.get("checks", {})
    return {
        "path": str((path / "gpu_env_gate_summary.json").relative_to(ROOT)),
        "status": payload.get("status"),
        "pass": payload.get("status") == "pass",
        "packages": payload.get("packages", {}),
        "cupy_rawkernel": checks.get("cupy_rawkernel", {}).get("status"),
        "torch_cuda": checks.get("torch_cuda", {}).get("status"),
        "numba_cuda_jit": checks.get("numba_cuda_jit", {}).get("status"),
    }


def build_payload() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    evidence: dict[str, Any] = {}

    for path in EVIDENCE_DIRS:
        checks[f"{path.name}_exists"] = path.exists()
        checks[f"{path.name}_host_exists"] = (path / "host.txt").exists()
        checks[f"{path.name}_matrix_exists"] = (path / "v3_rebuild_matrix.json").exists()
        checks[f"{path.name}_doctor_exists"] = (path / "source_tree_doctor.json").exists()
        checks[f"{path.name}_wording_exists"] = (path / "wording_gate.json").exists()

    checks["gpu_env_gate_exists"] = (SECOND_MACHINE_LX1 / "gpu_env_gate_summary.json").exists()
    checks["waiver_candidate_exists"] = WAIVER_CANDIDATE.exists()
    checks["waiver_claude_review_exists"] = WAIVER_CLAUDE_REVIEW.exists()
    checks["waiver_codex_consensus_exists"] = WAIVER_CODEX_CONSENSUS.exists()
    checks["waiver_candidate_has_required_scope"] = _contains_all(
        WAIVER_CANDIDATE, REQUIRED_WAIVER_CANDIDATE_PHRASES
    )
    checks["waiver_claude_review_accepts_not_release"] = _contains_all(
        WAIVER_CLAUDE_REVIEW, REQUIRED_WAIVER_REVIEW_PHRASES
    )
    checks["waiver_codex_consensus_accepts_not_release"] = _contains_all(
        WAIVER_CODEX_CONSENSUS, REQUIRED_WAIVER_CONSENSUS_PHRASES
    )

    if not all(checks.values()):
        return {
            "tool": "v3_phoenix_secondary_platform_gate",
            "status": "fail",
            "release_authorized": False,
            "secondary_rt_performance_confirmation_authorized": False,
            "failed_checks": [name for name, ok in checks.items() if not ok],
            "checks": checks,
            "evidence": evidence,
        }

    host_payloads = [_host_payload(path) for path in EVIDENCE_DIRS]
    matrix_payloads = [_matrix_payload(path) for path in EVIDENCE_DIRS]
    doctor_payloads = [_doctor_payload(path) for path in EVIDENCE_DIRS]
    wording_payloads = [_wording_payload(path) for path in EVIDENCE_DIRS]
    gpu_env = _gpu_env_payload(SECOND_MACHINE_LX1)

    checks.update(
        {
            "all_hosts_are_lx1": all(item["host_lx1"] for item in host_payloads),
            "all_hosts_are_gtx_1070": all(item["gtx_1070"] for item in host_payloads),
            "all_matrix_runs_ok": all(item["ok"] for item in matrix_payloads),
            "all_source_tree_doctors_ok": all(item["ok"] for item in doctor_payloads),
            "all_wording_gates_pass": all(item["pass"] for item in wording_payloads),
            "gpu_env_gate_pass": gpu_env["pass"],
            "no_lx1_all_app_performance_summary": not (ALL_BENCHMARK_LX1 / "summary.json").exists(),
            "no_lx1_paired_performance_summary": not (PAIRED_REPORT_LX1 / "paired_v2_v3_summary.json").exists(),
        }
    )

    evidence = {
        "hosts": host_payloads,
        "v3_rebuild_matrices": matrix_payloads,
        "source_tree_doctors": doctor_payloads,
        "wording_gates": wording_payloads,
        "gpu_env_gate": gpu_env,
        "hardware_scope_waiver": {
            "candidate": str(WAIVER_CANDIDATE.relative_to(ROOT)),
            "claude_review": str(WAIVER_CLAUDE_REVIEW.relative_to(ROOT)),
            "codex_consensus": str(WAIVER_CODEX_CONSENSUS.relative_to(ROOT)),
            "scope": WAIVER_SCOPE,
            "method": WAIVER_METHOD,
            "reviewed": (
                checks["waiver_claude_review_accepts_not_release"]
                and checks["waiver_codex_consensus_accepts_not_release"]
            ),
        },
        "classification": {
            "lx1_role": "secondary_compatibility_and_reproducibility_host",
            "gpu": "NVIDIA GeForce GTX 1070",
            "has_rt_cores_for_claims": False,
            "all_app_performance_suite_rerun_on_lx1": False,
            "paired_v2_v3_performance_suite_rerun_on_lx1": False,
        },
    }

    failed_checks = [name for name, ok in checks.items() if not ok]
    waiver_reviewed = (
        checks["waiver_claude_review_accepts_not_release"]
        and checks["waiver_codex_consensus_accepts_not_release"]
    )
    status = "fail" if failed_checks else "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release"

    return {
        "tool": "v3_phoenix_secondary_platform_gate",
        "status": status,
        "release_authorized": False,
        "secondary_compatibility_confirmed": status == "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release",
        "secondary_rt_performance_confirmation_authorized": False,
        "secondary_rt_hardware_scope_waiver_reviewed": waiver_reviewed,
        "secondary_platform_closes_release_blocker": waiver_reviewed,
        "secondary_platform_closes_release_blocker_method": WAIVER_METHOD if waiver_reviewed else None,
        "secondary_platform_closes_release_blocker_scope": WAIVER_SCOPE if waiver_reviewed else None,
        "hardware_performance_scope": WAIVER_SCOPE if waiver_reviewed else None,
        "multi_gpu_performance_portability_claim_authorized": False,
        "accepted_secondary_role": (
            "source-tree, dependency, wording, and GPU-Python compatibility confirmation; "
            "secondary RT blocker closed only by reviewed single-RTX hardware-scope waiver"
        ),
        "rejected_secondary_role": (
            "second RT-core performance confirmation and multi-GPU performance portability "
            "for V3 public speed claims"
        ),
        "required_next_action": (
            "Obtain a new aggregate release-readiness review that explicitly covers the "
            "source-tree/pod-gated thirteen-row scope, scoped installer closure, and "
            "single-RTX hardware waiver."
        ),
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": evidence,
        "decision_audit": {
            "decision": "Close the secondary RT blocker only by reviewed single-RTX hardware-scope waiver.",
            "was_i_foolish": "No. The gate keeps second-machine RT confirmation false while requiring both Claude review and Codex consensus for the waiver.",
            "foolish_actions": "The foolish action would be treating lx1 or the reachable RTX 4000 Ada pod as second-RT-hardware portability evidence.",
            "other_path": "Run a true second RTX-class machine. That remains stronger evidence but is not available in the known machine set.",
            "different_path_now": "Use the reviewed waiver to remove only the secondary blocker, then require aggregate release-readiness review before any release authorization.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify Phoenix V3 secondary platform evidence.")
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
    return 0 if payload["status"] == "compatibility_confirmed_hardware_scope_waiver_reviewed_not_release" else 2


if __name__ == "__main__":
    raise SystemExit(main())
