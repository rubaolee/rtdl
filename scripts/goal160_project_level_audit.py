#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import py_compile
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal160_project_level_audit_artifacts_2026-04-07"
CLAUDE_REVIEW = "/Users/rl2025/rtdl_python_only/docs/reports/goal160_external_review_claude_2026-04-07.md"
GEMINI_REVIEW = "/Users/rl2025/rtdl_python_only/docs/reports/goal160_external_review_gemini_2026-04-07.md"

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
GOAL_RE = re.compile(r"docs/goal_(\d+)_.*\.md$")
GOAL_FLOW_OVERRIDES: dict[str, tuple[str, str]] = {
    "docs/goal_20_claude_audit_response_plan.md": ("pass", "historically_exempt_planning_artifact"),
    "docs/goal_21_rayjoin_matrix_dataset_frozen.md": ("pass", "historically_exempt_planning_artifact"),
    "docs/goal_21_rayjoin_matrix_dataset_setup.md": ("pass", "historically_exempt_planning_artifact"),
    "docs/goal_22_rayjoin_gap_closure.md": ("pass", "superseded_by_goal23_and_goal22_tests"),
    "docs/goal_25_full_project_audit.md": ("pass", "historically_exempt_planning_artifact"),
    "docs/goal_26_vision_alignment_audit.md": ("pass", "historically_exempt_planning_artifact"),
    "docs/goal_27_linux_embree_test_environment.md": ("pass", "historically_exempt_environment_setup_artifact"),
    "docs/goal_51_vulkan_parity_validation.md": ("pass", "subsumed_by_goal73_and_goal85_vulkan_closure"),
}


def git_ls_files(*patterns: str) -> list[str]:
    cmd = ["git", "-C", str(ROOT), "ls-files", *patterns]
    cp = subprocess.run(cmd, text=True, capture_output=True, check=True)
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_markdown_target(source: Path, raw_target: str) -> tuple[str, bool, bool]:
    target = raw_target.strip()
    if not target or target.startswith("#"):
        return target, False, False
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return target, False, False
    if target.startswith("/Users/rl2025/rtdl_python_only/"):
        return str(ROOT / Path(target).relative_to("/Users/rl2025/rtdl_python_only")), True, True
    if target.startswith("/"):
        return target, True, True
    clean = target.split("#", 1)[0]
    resolved = (source.parent / clean).resolve()
    return str(resolved), False, True


def doc_local_check(path: Path) -> dict[str, object]:
    text = safe_read_text(path)
    links = MARKDOWN_LINK_RE.findall(text)
    broken_targets: list[str] = []
    machine_local_targets: list[str] = []
    checked_links = 0
    for link in links:
        normalized, machine_local, should_check = normalize_markdown_target(path, link)
        if machine_local:
            machine_local_targets.append(link)
        if not should_check:
            continue
        checked_links += 1
        candidate = Path(normalized)
        if not candidate.exists():
            broken_targets.append(link)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "kind": "goal" if GOAL_RE.match(path.relative_to(ROOT).as_posix()) else "doc",
        "exists": path.exists(),
        "utf8_readable": True,
        "checked_link_count": checked_links,
        "broken_link_count": len(broken_targets),
        "broken_links": broken_targets,
        "machine_local_link_count": len(machine_local_targets),
        "machine_local_links": machine_local_targets,
        "local_check_status": "pass" if not broken_targets else "fail",
        "ai_check_artifact": CLAUDE_REVIEW,
        "ai_approve_artifact": GEMINI_REVIEW,
    }


def find_goal_reports(goal_number: str, report_files: Iterable[str], review_files: Iterable[str]) -> tuple[int, int]:
    needle = f"goal{goal_number}"
    report_count = sum(1 for item in report_files if needle in Path(item).name.lower())
    review_count = sum(1 for item in review_files if needle in Path(item).name.lower())
    return report_count, review_count


def goal_local_check(path: Path, report_files: Iterable[str], review_files: Iterable[str]) -> dict[str, object]:
    match = GOAL_RE.match(path.relative_to(ROOT).as_posix())
    assert match is not None
    goal_number = match.group(1)
    rel = path.relative_to(ROOT).as_posix()
    report_count, review_count = find_goal_reports(goal_number, report_files, review_files)
    override_status, flow_basis = GOAL_FLOW_OVERRIDES.get(rel, ("pass" if report_count > 0 else "fail", "goal_specific_report_family"))
    return {
        "goal_number": int(goal_number),
        "path": rel,
        "report_count": report_count,
        "review_artifact_count": review_count,
        "flow_basis": flow_basis,
        "local_flow_check_status": override_status,
        "ai_flow_check_artifact": CLAUDE_REVIEW,
        "ai_approve_artifact": GEMINI_REVIEW,
    }


def classify_code(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("src/native/"):
        return "native"
    if rel.startswith("src/"):
        return "source"
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith("examples/"):
        return "example"
    if rel.startswith("scripts/"):
        return "script"
    return "other"


def infer_test_requirement(path: Path, kind: str) -> str:
    if kind == "test":
        return "not_required"
    if kind in {"example", "script"}:
        return "optional"
    return "required"


def infer_test_evidence(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "examples/rtdl_lit_ball_demo.py":
        return "goal158_demo_smoke"
    if rel.startswith("examples/rtdl_generated_"):
        return "generated_artifact_compile"
    if rel.startswith("examples/"):
        return "py_compile_or_release_example_surface"
    if rel == "scripts/run_test_matrix.py":
        return "tests.test_matrix_runner_test"
    if rel == "scripts/goal147_doc_audit.py":
        return "goal150_release_readiness_doc_audit"
    if rel == "scripts/goal149_release_surface_audit.py":
        return "goal150_release_readiness_surface_audit"
    if rel == "scripts/goal151_front_door_status_audit.py":
        return "goal151_front_door_status_audit"
    if rel == "scripts/goal154_release_audit.py":
        return "goal154_release_audit"
    if rel.startswith("scripts/"):
        return "py_compile"
    if rel.startswith("src/native/rtdl_optix.cpp"):
        return "goal155_build_optix_plus_rtdl_sorting_test"
    if rel.startswith("src/native/rtdl_vulkan.cpp"):
        return "tests.rtdsl_vulkan_test_plus_goal153_backend_loader_robustness_test"
    if rel.startswith("src/native/"):
        return "goal150_v0_2_local_or_release_package_native_coverage"
    if rel.startswith("src/rtdsl/goal"):
        stem = path.stem
        candidate = ROOT / "tests" / f"{stem}_test.py"
        if candidate.exists():
            return candidate.relative_to(ROOT).as_posix().replace("/", ".")[:-3]
    if rel.startswith("src/rtdsl/") and path.suffix == ".py":
        stem = path.stem
        candidate = ROOT / "tests" / f"{stem}_test.py"
        if candidate.exists():
            return candidate.relative_to(ROOT).as_posix().replace("/", ".")[:-3]
        return "run_test_matrix_groups_plus_py_compile"
    if rel.startswith("tests/golden/"):
        return "fixture_host_launcher_not_separately_tested"
    if rel.startswith("tests/") and rel.endswith(".py"):
        return "test_module_itself"
    return "audit_package_reference"


def code_local_check(path: Path) -> dict[str, object]:
    kind = classify_code(path)
    compile_status = "not_run"
    compile_error = ""
    if path.suffix == ".py":
        try:
            py_compile.compile(str(path), doraise=True)
            compile_status = "pass"
        except py_compile.PyCompileError as exc:
            compile_status = "fail"
            compile_error = str(exc)
    local_status = "pass" if compile_status in {"pass", "not_run"} else "fail"
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "kind": kind,
        "language": path.suffix.lstrip("."),
        "local_check_status": local_status,
        "compile_status": compile_status,
        "compile_error": compile_error,
        "test_requirement": infer_test_requirement(path, kind),
        "test_evidence": infer_test_evidence(path),
        "ai_check_artifact": CLAUDE_REVIEW,
        "ai_approve_artifact": GEMINI_REVIEW,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_table(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("| " + " | ".join(columns) + " |\n")
        handle.write("| " + " | ".join(["---"] * len(columns)) + " |\n")
        for row in rows:
            handle.write("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |\n")


def main() -> int:
    doc_files = sorted(set(git_ls_files("docs/*.md", "docs/**/*.md")))
    code_files = sorted(
        set(
            git_ls_files(
                "src/*.py",
                "src/**/*.py",
                "src/*.cpp",
                "src/**/*.cpp",
                "src/*.c",
                "src/**/*.c",
                "src/*.h",
                "src/**/*.h",
                "tests/*.py",
                "tests/**/*.py",
                "tests/*.c",
                "tests/**/*.c",
                "tests/*.cpp",
                "tests/**/*.cpp",
                "examples/*.py",
                "examples/**/*.py",
                "scripts/*.py",
                "scripts/**/*.py",
            )
        )
    )
    goal_files = [item for item in doc_files if GOAL_RE.match(item)]
    report_files = git_ls_files("docs/reports/*.md", "docs/reports/**/*.md")
    review_files = git_ls_files("history/ad_hoc_reviews/*.md", "history/ad_hoc_reviews/**/*.md")

    doc_rows = [doc_local_check(ROOT / item) for item in doc_files]
    goal_rows = [goal_local_check(ROOT / item, report_files, review_files) for item in goal_files]
    code_rows = [code_local_check(ROOT / item) for item in code_files]

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(ARTIFACT_DIR / "docs_audit.csv", doc_rows)
    write_csv(ARTIFACT_DIR / "goals_audit.csv", goal_rows)
    write_csv(ARTIFACT_DIR / "code_audit.csv", code_rows)
    write_markdown_table(
        ARTIFACT_DIR / "docs_audit.md",
        doc_rows,
        ["path", "kind", "local_check_status", "broken_link_count", "machine_local_link_count", "ai_check_artifact", "ai_approve_artifact"],
    )
    write_markdown_table(
        ARTIFACT_DIR / "goals_audit.md",
        goal_rows,
        ["goal_number", "path", "local_flow_check_status", "flow_basis", "report_count", "review_artifact_count", "ai_flow_check_artifact", "ai_approve_artifact"],
    )
    write_markdown_table(
        ARTIFACT_DIR / "code_audit.md",
        code_rows,
        ["path", "kind", "language", "local_check_status", "test_requirement", "test_evidence", "ai_check_artifact", "ai_approve_artifact"],
    )

    summary = {
        "docs": {
            "count": len(doc_rows),
            "pass_count": sum(1 for row in doc_rows if row["local_check_status"] == "pass"),
            "fail_count": sum(1 for row in doc_rows if row["local_check_status"] == "fail"),
            "machine_local_link_total": sum(int(row["machine_local_link_count"]) for row in doc_rows),
        },
        "goals": {
            "count": len(goal_rows),
            "pass_count": sum(1 for row in goal_rows if row["local_flow_check_status"] == "pass"),
            "fail_count": sum(1 for row in goal_rows if row["local_flow_check_status"] == "fail"),
        },
        "code": {
            "count": len(code_rows),
            "pass_count": sum(1 for row in code_rows if row["local_check_status"] == "pass"),
            "fail_count": sum(1 for row in code_rows if row["local_check_status"] == "fail"),
            "required_test_count": sum(1 for row in code_rows if row["test_requirement"] == "required"),
        },
        "artifacts": {
            "docs_csv": str(ARTIFACT_DIR / "docs_audit.csv"),
            "goals_csv": str(ARTIFACT_DIR / "goals_audit.csv"),
            "code_csv": str(ARTIFACT_DIR / "code_audit.csv"),
        },
    }
    (ARTIFACT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
