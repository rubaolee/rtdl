#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from scripts import run_test_matrix
from scripts.rtdl_source_tree_doctor import gather_checks
from scripts.v4_0_current_front_door_claim_boundary_scan import scan as scan_claims


ROOT = Path(__file__).resolve().parents[1]
REPORT_ID = "v4_0_release_promotion_gate_2026-06-19"


def _git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _release_files() -> tuple[str, ...]:
    base = "docs/release_reports/v4_0_0"
    return (
        f"{base}/README.md",
        f"{base}/release_statement.md",
        f"{base}/support_matrix.md",
        f"{base}/public_wording_boundaries.md",
        f"{base}/publication.md",
        f"{base}/final_closeout.md",
        f"{base}/major_release_requirements_trace.md",
    )


def _evidence_files() -> tuple[str, ...]:
    return (
        "docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md",
        "docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json",
        "docs/reports/v4_0_m1_linux_gpu_release_gate_2026-06-19.json",
        "docs/reports/v2_v3_v4_large_scale_performance_comparison_2026-06-19.md",
        "tutorials/v4_0/README.md",
        "examples/v4_0/README.md",
    )


def _path_status(paths: tuple[str, ...]) -> list[dict[str, object]]:
    return [{"path": path, "exists": (ROOT / path).exists()} for path in paths]


def _pyproject_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("version = "):
            return stripped.split('"', 2)[1]
    return ""


def build_payload() -> dict[str, Any]:
    claim_scan = scan_claims(ROOT)
    doctor = gather_checks()
    release_paths = _path_status(_release_files())
    evidence_paths = _path_status(_evidence_files())
    v4_current_modules = run_test_matrix.group_modules("v4_current")

    failures: list[dict[str, object]] = []
    if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "v4.0.0":
        failures.append({"check": "version_marker", "message": "VERSION must be v4.0.0"})
    if _pyproject_version() != "4.0.0":
        failures.append({"check": "pyproject_version", "message": "pyproject version must be 4.0.0"})
    if claim_scan["status"] != "pass":
        failures.append({"check": "claim_scan", "findings": claim_scan["findings"]})
    claims = claim_scan["claim_boundaries"]
    for key in (
        "v4_current_release_claim_authorized",
        "v4_release_package_claim_authorized",
        "fixed_radius_m1_python_gpu_operator_claim_authorized",
    ):
        if claims.get(key) is not True:
            failures.append({"check": "required_positive_claim", "key": key})
    for key in (
        "stable_v4_sdk_claim_authorized",
        "package_install_claim_authorized",
        "public_true_zero_copy_claim_authorized",
        "async_claim_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "pytorch_route_claim_authorized",
        "full_dlpack_route_claim_authorized",
    ):
        if claims.get(key) is not False:
            failures.append({"check": "blocked_claim", "key": key, "value": claims.get(key)})
    if not doctor["ok"]:
        failures.append({"check": "source_tree_doctor", "required_failures": doctor["required_failures"]})
    for row in release_paths + evidence_paths:
        if not row["exists"]:
            failures.append({"check": "required_path", "path": row["path"]})
    if "tests.v4_0_current_release_publication_test" not in v4_current_modules:
        failures.append({"check": "v4_current_matrix", "message": "publication guard missing"})

    ok = not failures
    return {
        "report_id": REPORT_ID,
        "status": "pass" if ok else "fail",
        "ok": ok,
        "date": "2026-06-19",
        "git": {"head": _git_value("rev-parse", "HEAD"), "tree": _git_value("rev-parse", "HEAD^{tree}")},
        "version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "pyproject_version": _pyproject_version(),
        "release_paths": release_paths,
        "evidence_paths": evidence_paths,
        "v4_current_modules": v4_current_modules,
        "claim_scan": claim_scan,
        "source_tree_doctor": doctor,
        "claim_boundaries": claims,
        "release_reading": {
            "v4_0_0_current_source_tree_release_authorized": ok,
            "fixed_radius_m1_python_gpu_operator_claim_authorized": ok,
            "package_install_claim_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the bounded V4.0.0 front-door promotion.")
    parser.add_argument("--output", default=f"docs/reports/{REPORT_ID}.json")
    args = parser.parse_args()

    payload = build_payload()
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
