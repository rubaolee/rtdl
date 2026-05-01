#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLOUD_DIR = ROOT / "docs" / "reports" / "cloud_2026_04_26"
EXPECTED_COMMIT = "914122ecd2f2c73f6a51ec2d5b04ca3d575d5681"
EXPECTED_ENTRY_COUNT = 17


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def audit(cloud_dir: Path) -> dict[str, Any]:
    final_summary = cloud_dir / "goal1003_rtx_a5000_final_merged_summary_2026-04-26.json"
    final_report = cloud_dir / "goal1003_rtx_a5000_final_artifact_report_2026-04-26.md"
    run_summary = cloud_dir / "goal1003_rtx_a5000_pod_run_summary_2026-04-26.md"
    final_bundle = cloud_dir / "goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz"

    required = [final_summary, final_report, run_summary, final_bundle]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]

    payload = _load_json(final_summary) if final_summary.exists() else {}
    report_text = _read(final_report) if final_report.exists() else ""
    run_text = _read(run_summary) if run_summary.exists() else ""

    results = payload.get("results") if isinstance(payload.get("results"), list) else []
    failed_results = [
        {
            "app": item.get("app"),
            "path_name": item.get("path_name"),
            "status": (item.get("result") or {}).get("status"),
        }
        for item in results
        if isinstance(item, dict) and (item.get("result") or {}).get("status") != "ok"
    ]
    apps = sorted({str(item.get("app")) for item in results if isinstance(item, dict)})
    checks = {
        "required_files_present": not missing,
        "summary_dry_run_false": payload.get("dry_run") is False,
        "summary_status_ok": payload.get("status") == "ok",
        "summary_failed_count_zero": payload.get("failed_count") == 0,
        "summary_entry_count_17": payload.get("entry_count") == EXPECTED_ENTRY_COUNT,
        "all_result_statuses_ok": not failed_results and len(results) == EXPECTED_ENTRY_COUNT,
        "commit_matches_validated_branch": payload.get("git_head") == EXPECTED_COMMIT,
        "nvidia_smi_json_confirms_rtx_a5000": "NVIDIA RTX A5000" in str(payload.get("nvidia_smi", "")),
        "final_report_status_ok": "Status: `ok`." in report_text,
        "final_report_preserves_no_speedup_boundary": "does not authorize RTX speedup claims" in report_text,
        "run_summary_names_rtx_a5000": "NVIDIA RTX A5000" in run_text,
        "run_summary_records_geos_incident": "libgeos-dev" in run_text and "-lgeos_c" in run_text,
        "run_summary_records_17_of_17": "Manifest entries executed: 17" in run_text
        and "Final failed entries: 0" in run_text,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "suite": "goal1004_rtx_a5000_artifact_audit",
        "cloud_dir": str(cloud_dir),
        "expected_commit": EXPECTED_COMMIT,
        "expected_entry_count": EXPECTED_ENTRY_COUNT,
        "missing_files": missing,
        "checks": checks,
        "failed_checks": failures,
        "result_count": len(results),
        "apps": apps,
        "failed_results": failed_results,
        "status": "ok" if not failures else "needs_attention",
        "boundary": (
            "This audit validates saved RTX A5000 execution evidence. It does not authorize public speedup "
            "claims; those require same-semantics baselines and independent review."
        ),
    }


def _write_md(payload: dict[str, Any], output_md: Path) -> None:
    checks = payload["checks"]
    lines = [
        "# Goal1004 RTX A5000 Artifact Audit",
        "",
        f"Status: `{payload['status']}`.",
        "",
        "This audit checks the saved RTX A5000 pod artifacts for completeness and honesty boundaries.",
        "It does not authorize public speedup claims.",
        "",
        "## Evidence",
        "",
        f"- Cloud dir: `{Path(payload['cloud_dir']).relative_to(ROOT)}`",
        f"- Expected commit: `{payload['expected_commit']}`",
        f"- Result count: `{payload['result_count']}`",
        f"- Apps covered: `{len(payload['apps'])}`",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "|---|---:|",
    ]
    for name, ok in checks.items():
        lines.append(f"| {name} | {'ok' if ok else 'fail'} |")
    lines.extend(
        [
            "",
            "## Apps",
            "",
            ", ".join(payload["apps"]),
            "",
            "## Boundary",
            "",
            payload["boundary"],
        ]
    )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit saved RTX A5000 cloud artifacts.")
    parser.add_argument("--cloud-dir", default=str(DEFAULT_CLOUD_DIR))
    parser.add_argument(
        "--output-json",
        default=str(DEFAULT_CLOUD_DIR / "goal1004_rtx_a5000_artifact_audit_2026-04-26.json"),
    )
    parser.add_argument(
        "--output-md",
        default=str(DEFAULT_CLOUD_DIR / "goal1004_rtx_a5000_artifact_audit_2026-04-26.md"),
    )
    args = parser.parse_args()
    payload = audit(Path(args.cloud_dir))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_md(payload, Path(args.output_md))
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
