from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_staging_bundle.goal4576.v1"
OUT_JSON = Path("docs/reports/goal4576_v3_0_m177_c_abi_staging_bundle_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4576_v3_0_m177_c_abi_staging_bundle_2026-06-17.md")
MAKEFILE = Path("Makefile")
STAGING_CONTRACT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md")
C_ABI_DRAFT = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_draft.md")
LEARN_README = Path("docs/history/v4_preparatory_embedding/README.md")
EMBEDDING_README = Path("docs/history/v4_preparatory_embedding/examples/embedding/README.md")
CURRENT_MANIFEST = Path("docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_3.json")


def _shared_suffix() -> str:
    if os.name == "nt":
        return ".dll"
    return ".dylib" if os.uname().sysname == "Darwin" else ".so"


def _tail(text: str) -> tuple[str, ...]:
    return tuple(text.splitlines()[-12:])


def _stage_paths(root: Path) -> dict[str, Path]:
    stage = root / "build" / "c_api_stage"
    return {
        "stage": stage,
        "header": stage / "include" / "rtdl" / "rtdl.h",
        "library": stage / "lib" / ("librtdl_c_api" + _shared_suffix()),
        "manifest": stage / "share" / "rtdl" / "v3_0_c_abi_symbol_manifest.json",
        "readme": stage / "share" / "rtdl" / "README.md",
        "example": stage / "examples" / "c_api_aabb2_overlap_client.c",
        "example_exe": stage / "examples" / "rtdl_c_api_aabb2_overlap_client",
    }


def _existing_command(candidates: tuple[str, ...]) -> str | None:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def run_stage(root: Path) -> dict[str, Any]:
    make = shutil.which("make")
    cc = _existing_command(("cc", "gcc", "clang"))
    paths = _stage_paths(root)
    result: dict[str, Any] = {
        "make": make,
        "cc": cc,
        "stage_dir": paths["stage"].as_posix(),
        "make_result": None,
        "compile_result": None,
        "run_result": None,
        "staged_files": {},
        "staged_manifest": None,
        "ok": False,
    }
    if make is None:
        return result
    make_completed = subprocess.run(
        [make, "stage-c-api"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    staged_files = {
        name: {"path": path.as_posix(), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}
        for name, path in paths.items()
        if name not in {"stage", "example_exe"}
    }
    staged_manifest = None
    if paths["manifest"].exists():
        staged_manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    result.update(
        {
            "make_result": {
                "command": [make, "stage-c-api"],
                "returncode": make_completed.returncode,
                "ok": make_completed.returncode == 0,
                "stdout_tail": _tail(make_completed.stdout),
                "stderr_tail": _tail(make_completed.stderr),
            },
            "staged_files": staged_files,
            "staged_manifest": staged_manifest,
        }
    )
    if make_completed.returncode != 0 or cc is None:
        result["ok"] = False
        return result
    compile_completed = subprocess.run(
        [
            cc,
            "-std=c11",
            "-I",
            str(paths["stage"] / "include"),
            str(paths["example"]),
            "-o",
            str(paths["example_exe"]),
            "-ldl",
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["compile_result"] = {
        "command": [
            cc,
            "-std=c11",
            "-I",
            (paths["stage"] / "include").as_posix(),
            paths["example"].as_posix(),
            "-o",
            paths["example_exe"].as_posix(),
            "-ldl",
        ],
        "returncode": compile_completed.returncode,
        "ok": compile_completed.returncode == 0,
        "stdout_tail": _tail(compile_completed.stdout),
        "stderr_tail": _tail(compile_completed.stderr),
    }
    if compile_completed.returncode != 0:
        result["ok"] = False
        return result
    run_completed = subprocess.run(
        [str(paths["example_exe"]), str(paths["library"])],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result["run_result"] = {
        "command": [paths["example_exe"].as_posix(), paths["library"].as_posix()],
        "returncode": run_completed.returncode,
        "ok": run_completed.returncode == 0,
        "stdout": run_completed.stdout.strip(),
        "stderr_tail": _tail(run_completed.stderr),
    }
    result["ok"] = (
        result["make_result"]["ok"]
        and all(item["exists"] and item["size_bytes"] > 0 for item in staged_files.values())
        and staged_manifest is not None
        and staged_manifest.get("abi_version") == "0.1.3"
        and result["compile_result"]["ok"]
        and result["run_result"]["ok"]
        and result["run_result"]["stdout"] == "hit_count=1 first_pair=(0,0)"
    )
    return result


def build_packet(root: Path = Path("."), *, run_make: bool = False) -> dict[str, Any]:
    makefile = (root / MAKEFILE).read_text(encoding="utf-8")
    staging_contract = (root / STAGING_CONTRACT).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    learn = (root / LEARN_README).read_text(encoding="utf-8")
    embedding = (root / EMBEDDING_README).read_text(encoding="utf-8")
    manifest = json.loads((root / CURRENT_MANIFEST).read_text(encoding="utf-8"))
    stage_result = run_stage(root) if run_make else None
    checks = {
        "makefile_declares_stage_target": "\nstage-c-api:" in makefile,
        "stage_target_is_phony": "stage-c-api" in makefile.split(".PHONY:", 1)[-1],
        "stage_target_builds_c_api_first": "stage-c-api: build-c-api" in makefile,
        "stage_target_copies_header_library_manifest_readme_example": all(
            token in makefile
            for token in (
                "$(C_API_HEADER)",
                "$(C_API_STAGE_DIR)/include/rtdl/rtdl.h",
                "$(BUILD_DIR)/$(C_API_LIB_NAME)",
                "$(C_API_STAGE_MANIFEST)",
                "docs/history/v4_preparatory_embedding/examples/embedding/README.md",
                "docs/history/v4_preparatory_embedding/examples/embedding/c_api_aabb2_overlap_client.c",
            )
        ),
        "staging_contract_documents_bundle": "build/c_api_stage" in staging_contract
        and "v3_0_c_abi_symbol_manifest_v0_1_3.json" in staging_contract,
        "c_abi_draft_links_staging_contract": "v3_0_c_abi_staging_contract.md" in c_abi
        and "Goal4576" in c_abi,
        "history_archive_links_staging_contract": "V3.0 C ABI Staging Contract" in learn,
        "embedding_readme_mentions_stage_command": "make stage-c-api" in embedding
        and "build/c_api_stage" in embedding,
        "current_manifest_is_0_1_3": manifest["abi_version"] == "0.1.3",
    }
    if stage_result is not None:
        checks.update(
            {
                "make_available": bool(stage_result["make"]),
                "cc_available": bool(stage_result["cc"]),
                "stage_make_ok": bool(stage_result["make_result"] and stage_result["make_result"]["ok"]),
                "stage_all_files_exist": all(
                    item["exists"] and item["size_bytes"] > 0
                    for item in stage_result["staged_files"].values()
                ),
                "stage_manifest_matches_current_version": bool(
                    stage_result["staged_manifest"]
                    and stage_result["staged_manifest"].get("abi_version") == "0.1.3"
                ),
                "staged_example_compiles": bool(stage_result["compile_result"] and stage_result["compile_result"]["ok"]),
                "staged_example_runs_expected_query": bool(
                    stage_result["run_result"]
                    and stage_result["run_result"]["ok"]
                    and stage_result["run_result"]["stdout"] == "hit_count=1 first_pair=(0,0)"
                ),
            }
        )
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4576 / V3 M177",
        "status": "c_abi_staging_bundle_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "stage_result": stage_result,
        "claim_boundary": {
            "packaged_sdk_authorized": False,
            "install_prefix_authorized": False,
            "stable_abi_authorized": False,
            "optix_embree_c_abi_query_authorized": False,
            "performance_wording_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4576 adds and validates `make stage-c-api`, a source-tree staging "
            "bundle for non-Python C ABI embedding. The staged bundle contains the "
            "archived draft header, shared library, current draft symbol "
            "manifest, README, and example C client; the pod evidence compiles "
            "and runs the staged example against the staged library. This is not "
            "a packaged SDK or stable ABI promise."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    stage_result = packet["stage_result"] or {}
    lines = [
        "# Goal4576 / V3 M177 C ABI Staging Bundle",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Stage Result",
        "",
        f"- Stage dir: `{stage_result.get('stage_dir')}`",
        f"- OK: `{stage_result.get('ok')}`",
        f"- Example output: `{(stage_result.get('run_result') or {}).get('stdout')}`",
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This validates a source-tree staging bundle only.",
            "- No packaged SDK, install prefix, stable ABI, OptiX/Embree C ABI query, performance wording, or release claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--no-make", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet(run_make=not args.no_make)
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
