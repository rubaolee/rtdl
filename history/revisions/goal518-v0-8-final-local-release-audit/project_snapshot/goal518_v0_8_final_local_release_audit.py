from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_DOCS = [
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/current_architecture.md"),
    Path("docs/capability_boundaries.md"),
    Path("docs/release_facing_examples.md"),
    Path("docs/rtdl/README.md"),
    Path("docs/rtdl/itre_app_model.md"),
    Path("docs/tutorials/README.md"),
    Path("docs/tutorials/v0_8_app_building.md"),
    Path("docs/tutorials/feature_quickstart_cookbook.md"),
    Path("examples/README.md"),
]

FORBIDDEN_PUBLIC_STRINGS = [
    "released `v0.8",
    "released v0.8",
    "v0.8.0",
    "in-progress `v0.8",
    "in progress v0.8",
]


def run_command(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-6000:],
        "stderr_tail": completed.stderr[-6000:],
    }


def check_forbidden_public_strings() -> dict[str, object]:
    findings: list[dict[str, object]] = []
    for rel_path in PUBLIC_DOCS:
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        for needle in FORBIDDEN_PUBLIC_STRINGS:
            if needle in text:
                findings.append({"path": str(rel_path), "needle": needle})
    return {"valid": not findings, "findings": findings}


def check_git_status() -> dict[str, object]:
    result = run_command(["git", "status", "--short"])
    allowed_dirty_prefixes = (
        "docs/reports/goal495_complete_history_",
        "docs/reports/goal515_public_command_truth_audit_",
        "docs/reports/goal518_",
        "history/COMPLETE_HISTORY.md",
        "history/history.db",
        "history/revision_dashboard.html",
        "history/revision_dashboard.md",
        "scripts/goal518_",
        "tests/goal518_",
    )
    unexpected: list[str] = []
    for line in str(result["stdout_tail"]).splitlines():
        path = line[3:] if len(line) > 3 else line
        if not path.startswith(allowed_dirty_prefixes):
            unexpected.append(line)
    return {
        **result,
        "valid": result["returncode"] == 0 and not unexpected,
        "unexpected": unexpected,
        "policy": "Only current Goal518 audit artifacts and regenerated audit/history indexes may be dirty during this pre-commit audit.",
    }


def main() -> int:
    checks = {
        "forbidden_public_strings": check_forbidden_public_strings(),
        "targeted_release_tests": run_command(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.goal517_itre_app_model_doc_test",
                "tests.goal516_linux_public_command_validation_artifact_test",
                "tests.goal515_public_command_truth_audit_test",
                "tests.goal513_public_example_smoke_test",
                "tests.goal512_public_doc_smoke_audit_test",
                "-v",
            ]
        ),
        "public_command_truth": run_command(
            [sys.executable, "scripts/goal515_public_command_truth_audit.py"]
        ),
        "complete_history_map": run_command(
            [sys.executable, "scripts/goal495_complete_history_map.py"]
        ),
        "py_compile": run_command(
            [
                sys.executable,
                "-m",
                "py_compile",
                "scripts/goal518_v0_8_final_local_release_audit.py",
                "tests/goal517_itre_app_model_doc_test.py",
                "tests/goal516_linux_public_command_validation_artifact_test.py",
            ]
        ),
        "git_status": check_git_status(),
    }
    for name in ("targeted_release_tests", "public_command_truth", "complete_history_map", "py_compile"):
        checks[name]["valid"] = checks[name]["returncode"] == 0
    payload = {
        "goal": "518",
        "name": "v0.8 final local release audit",
        "valid": all(bool(check.get("valid")) for check in checks.values()),
        "checks": checks,
    }
    report_dir = ROOT / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "goal518_v0_8_final_local_release_audit_2026-04-17.json"
    md_path = report_dir / "goal518_v0_8_final_local_release_audit_2026-04-17.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "checks": {k: v["valid"] for k, v in checks.items()}}, sort_keys=True))
    return 0 if payload["valid"] else 1


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Goal518 v0.8 Final Local Release Audit",
        "",
        "Date: 2026-04-17",
        "",
        f"- Valid: `{str(payload['valid']).lower()}`",
        "",
        "## Checks",
        "",
    ]
    for name, check in dict(payload["checks"]).items():
        lines.append(f"- `{name}`: `{str(check['valid']).lower()}`")
    lines.extend(["", "## Notes", ""])
    lines.append("- This is a local release-readiness audit, not release authorization.")
    lines.append("- It verifies public wording, targeted release gates, command truth, history validity, Python syntax, and that no unexpected files are dirty during the pre-commit audit.")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
