#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"
MANIFEST = APP_DIR / "data" / "manifest.json"
DEFAULT_CHECKOUT = APP_DIR / "_work" / "source_contract_gate" / "OWLRayTracing"
RUN_DIR = APP_DIR / "_runs" / "author_source_contract_gate"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_command(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=os.environ.copy(),
    )


def ensure_pinned_checkout(manifest: dict[str, Any], checkout: Path) -> dict[str, Any]:
    author = manifest["author_artifact"]
    checkout = checkout.resolve()
    work_root = (APP_DIR / "_work").resolve()
    try:
        checkout.relative_to(work_root)
    except ValueError:
        return {
            "ok": False,
            "safety_error": "automatic checkout/reset/clean is only allowed under the app _work directory",
            "checkout": str(checkout),
            "allowed_root": str(work_root),
        }
    checkout.parent.mkdir(parents=True, exist_ok=True)
    commands: list[dict[str, Any]] = []
    if not (checkout / ".git").exists():
        clone = run_command(
            [
                "git",
                "clone",
                "--branch",
                author["branch"],
                author["repository"],
                str(checkout),
            ],
            cwd=checkout.parent,
        )
        commands.append(
            {
                "step": "clone",
                "returncode": clone.returncode,
                "stdout_tail": clone.stdout[-2000:],
                "stderr_tail": clone.stderr[-2000:],
            }
        )
        if clone.returncode != 0:
            return {"ok": False, "commands": commands}

    fetch = run_command(["git", "fetch", "--all", "--tags"], cwd=checkout)
    commands.append(
        {
            "step": "fetch",
            "returncode": fetch.returncode,
            "stdout_tail": fetch.stdout[-2000:],
            "stderr_tail": fetch.stderr[-2000:],
        }
    )
    if fetch.returncode != 0:
        return {"ok": False, "commands": commands}

    checkout_cmd = run_command(
        ["git", "-c", "advice.detachedHead=false", "checkout", "--force", author["commit"]],
        cwd=checkout,
    )
    commands.append(
        {
            "step": "checkout",
            "returncode": checkout_cmd.returncode,
            "stdout_tail": checkout_cmd.stdout[-2000:],
            "stderr_tail": checkout_cmd.stderr[-2000:],
        }
    )
    if checkout_cmd.returncode != 0:
        return {"ok": False, "commands": commands}

    clean = run_command(["git", "clean", "-fdx"], cwd=checkout)
    commands.append(
        {
            "step": "clean_generated_checkout",
            "returncode": clean.returncode,
            "stdout_tail": clean.stdout[-2000:],
            "stderr_tail": clean.stderr[-2000:],
        }
    )
    return {"ok": clean.returncode == 0, "commands": commands}


def git_metadata(source_root: Path) -> dict[str, Any]:
    if not (source_root / ".git").exists():
        return {"is_git_checkout": False}
    head = run_command(["git", "rev-parse", "HEAD"], cwd=source_root)
    status = run_command(["git", "status", "--short"], cwd=source_root)
    return {
        "is_git_checkout": True,
        "head": head.stdout.strip() if head.returncode == 0 else None,
        "head_returncode": head.returncode,
        "status_short": status.stdout,
        "status_returncode": status.returncode,
        "clean": status.returncode == 0 and not status.stdout.strip(),
    }


def contains(text: str, needle: str) -> bool:
    return needle in text


def matches(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.MULTILINE | re.DOTALL) is not None


def check(name: str, passed: bool, evidence: Any) -> dict[str, Any]:
    return {"name": name, "status": "passed" if passed else "failed", "evidence": evidence}


def audit_author_source(source_root: Path, manifest: dict[str, Any], *, require_git: bool = True) -> dict[str, Any]:
    author = manifest["author_artifact"]
    sample = source_root / author["sample_path"]
    paths = {
        "hostCode.cu": sample / "hostCode.cu",
        "GeomTypes.h": sample / "GeomTypes.h",
        "barnesHutTree.h": sample / "barnesHutTree.h",
        "barnesHutTree.cpp": sample / "barnesHutTree.cpp",
        "deviceCode.cu": sample / "deviceCode.cu",
        "less.hpp": sample / "less.hpp",
    }
    texts: dict[str, str] = {}
    file_checks = []
    for label, path in paths.items():
        exists = path.exists()
        file_checks.append(check(f"file_exists:{label}", exists, str(path)))
        texts[label] = path.read_text(encoding="utf-8", errors="replace") if exists else ""

    host = texts["hostCode.cu"]
    geom = texts["GeomTypes.h"]
    tree_h = texts["barnesHutTree.h"]
    tree_cpp = texts["barnesHutTree.cpp"]
    device = texts["deviceCode.cu"]
    less = texts["less.hpp"]

    metadata = git_metadata(source_root)
    git_checks = (
        [
            check("git_head_matches_manifest", metadata.get("head") == author["commit"], metadata),
            check("git_checkout_clean", bool(metadata.get("clean")), metadata),
        ]
        if require_git
        else [check("git_checks_disabled_for_fixture", True, metadata)]
    )
    checks: list[dict[str, Any]] = [
        *file_checks,
        *git_checks,
        check("raw_source_num_points_is_unpatched", matches(geom, r"^constexpr\s+int\s+NUM_POINTS\s*=\s*100000000\s*;"), "GeomTypes.h active NUM_POINTS"),
        check("raw_source_num_steps_is_one", matches(geom, r"^constexpr\s+int\s+NUM_STEPS\s*=\s*1\s*;"), "GeomTypes.h active NUM_STEPS"),
        check("threshold_constant_is_author_value", matches(tree_h, r"#define\s+THRESHOLD\s+0\.5f"), "barnesHutTree.h"),
        check("gravity_constant_is_author_value", matches(tree_h, r"#define\s+GRAVITATIONAL_CONSTANT\s+\.1f"), "barnesHutTree.h"),
        check("bucket_size_is_author_value", matches(tree_h, r"#define\s+BUCKET_SIZE\s+32"), "barnesHutTree.h"),
        check("new_mode_exists", contains(host, 'std::string(av[1]) == "new"'), "hostCode.cu"),
        check("treelogy_mode_exists", contains(host, 'std::string(av[1]) == "treelogy"'), "hostCode.cu"),
        check("new_mode_writes_five_headers", all(needle in host for needle in [
            'fprintf(outFile, "%d\\n", NUM_POINTS)',
            'fprintf(outFile, "%d\\n", NUM_STEPS)',
            'fprintf(outFile, "%f\\n", (0.025))',
            'fprintf(outFile, "%f\\n", (0.05))',
            'fprintf(outFile, "%f\\n", THRESHOLD)',
        ]), "new-mode header rows"),
        check("new_mode_writes_seven_column_rows", contains(host, 'fprintf(outFile, "%f %f %f %f %f %f %f\\n"'), "new-mode body rows"),
        check("treelogy_reads_five_headers", contains(host, "for(int i = 0; i < 5; i++)") and contains(host, 'fscanf(inFile, "%f\\n", &randomStuff)'), "treelogy header read"),
        check("treelogy_reads_seven_column_rows", contains(host, 'fscanf(inFile, "%f %f %f %f %f %f %f"') and contains(host, "== 7"), "treelogy body rows"),
        check("zorder_sort_uses_less_hpp", contains(host, '#include "less.hpp"') and contains(host, "zorder_knn::Less<sortPoint, 3>()"), "z-order sort"),
        check("less_hpp_has_float_xor_msb_comparator", contains(less, "FloatXorMsb") and contains(less, "struct Less"), "less.hpp"),
        check("post_sort_ids_are_reassigned", contains(host, "p.idX = i;"), "post-sort idX reassignment"),
        check("bucket_leaf_count_uses_bucket_size", contains(host, "std::ceil(leaves.size() / double(BUCKET_SIZE))"), "bucket leaves"),
        check("bucket_leaf_groups_particles", contains(host, "for(int j = 0; j < BUCKET_SIZE; j++)") and contains(host, "new_node->particles.push_back"), "bucket particle grouping"),
        check("bucket_leaf_inserted_into_octree", contains(host, "tree->insertNode(root, new_node, gridSize * 0.5)"), "bucket insert"),
        check("center_of_mass_recomputed", contains(host, "tree->computeCOM(root)"), "COM recompute"),
        check("leaf_force_self_skip_exists", contains(tree_cpp, "bhNode->particles[i] != point.idX"), "leaf self-skip"),
        check("cpu_force_uses_inverse_square_gravity_scale", contains(tree_cpp, "GRAVITATIONAL_CONSTANT") and contains(tree_cpp, "(mass_one * mass_two) / r_2"), "CPU force formula"),
        check("cpu_opening_rule_matches_reference", contains(tree_cpp, "node->s < distanceBetweenObjects(point, node) * THRESHOLD"), "CPU opening rule"),
        check("device_force_uses_inverse_square_gravity_scale", contains(device, "GRAVITATIONAL_CONSTANT") and contains(device, "r_2"), "device force formula"),
        check("device_opening_uses_threshold_scaled_distance", contains(device, "sqrtf(r_2) * THRESHOLD"), "device opening rule"),
        check("author_force_phase_is_measured_before_any_patch_dump", contains(host, "owlLaunch2D(rayGen, points.size(), 1, lp)") and contains(host, "profileStats->forceCalculationTime"), "force timing"),
        check("raw_source_has_no_force_dump_patch", "RTBH_FORCE_OUT" not in host, "raw source should not contain comparator patch"),
    ]

    passed = all(row["status"] == "passed" for row in checks)
    return {
        "mode": "rt_barneshut_author_source_contract_gate",
        "status": "passed" if passed else "failed",
        "paper_reproduction_complete": False,
        "source_root": str(source_root),
        "manifest_author_artifact": author,
        "git": metadata,
        "checks": checks,
        "claim_boundary": (
            "Author source contract audit only. It verifies that the pinned raw "
            "source contains the input, ordering, bucket-tree, opening-rule, and "
            "force-law anchors assumed by the RT-BarnesHut paper app. It does not "
            "build or run the author binary and does not prove paper reproduction."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit pinned RT-BarnesHut author source contract anchors.")
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--checkout-dir", type=Path, default=DEFAULT_CHECKOUT)
    parser.add_argument("--output", type=Path, default=RUN_DIR / "summary.json")
    parser.add_argument("--no-fetch", action="store_true", help="Do not clone/fetch; require --source-root or existing checkout-dir.")
    args = parser.parse_args(argv)

    manifest = read_json(MANIFEST)
    source_root = args.source_root.resolve() if args.source_root else args.checkout_dir.resolve()
    prepare: dict[str, Any] | None = None
    if args.source_root is None and not args.no_fetch:
        prepare = ensure_pinned_checkout(manifest, source_root)
        if not prepare.get("ok"):
            summary = {
                "mode": "rt_barneshut_author_source_contract_gate",
                "status": "blocked_checkout_failed",
                "paper_reproduction_complete": False,
                "source_root": str(source_root),
                "prepare": prepare,
            }
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(args.output)
            return 2

    if not source_root.exists():
        summary = {
            "mode": "rt_barneshut_author_source_contract_gate",
            "status": "blocked_missing_source_root",
            "paper_reproduction_complete": False,
            "source_root": str(source_root),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(args.output)
        return 2

    summary = audit_author_source(source_root, manifest, require_git=True)
    if prepare is not None:
        summary["prepare"] = prepare
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if summary["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
