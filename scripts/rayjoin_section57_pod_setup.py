from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rayjoin_paper_suite import RAYJOIN_PREPROCESSED_SHARE_URL
from rtdsl.rayjoin_paper_suite import availability_matrix
from rtdsl.rayjoin_paper_suite import paper_pairs


AUTHOR_REPO_URL = "https://github.com/pwrliang/RayJoin"
KNOWN_AUTHOR_COMMIT = "02bf6220d6d20b04af77ee20364eced75cc029c9"


def _run(command: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"returncode": None, "stdout": "", "stderr": str(exc), "available": False}
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "available": completed.returncode == 0,
    }


def _tool_status(name: str, version_args: list[str] | None = None) -> dict[str, object]:
    path = shutil.which(name)
    status: dict[str, object] = {"name": name, "path": path, "available": path is not None}
    if path and version_args:
        status["version_probe"] = _run([path, *version_args])
    return status


def _pkg_config_status(name: str) -> dict[str, object]:
    pkg_config = shutil.which("pkg-config")
    if pkg_config is None:
        return {"name": name, "available": False, "probe": "pkg-config unavailable"}
    probe = _run([pkg_config, "--exists", name])
    cflags = _run([pkg_config, "--cflags", name]) if probe["available"] else None
    libs = _run([pkg_config, "--libs", name]) if probe["available"] else None
    return {"name": name, "available": bool(probe["available"]), "cflags": cflags, "libs": libs}


def _optix_status() -> dict[str, object]:
    candidates: list[Path] = []
    for key in ("OPTIX_ROOT", "OptiX_INSTALL_DIR", "NVIDIA_OPTIX_SDK", "OPTIX_SDK_DIR"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value))
    for parent in (Path("/usr/local"), Path("/opt"), Path("/root/vendor")):
        if parent.exists():
            candidates.extend(parent.glob("*OptiX*"))
            candidates.extend(parent.glob("optix*"))
    rows = []
    for candidate in candidates:
        include = candidate / "include" / "optix.h"
        rows.append({"root": str(candidate), "include_optix_h": str(include), "exists": include.exists()})
    return {
        "available": any(row["exists"] for row in rows),
        "candidates": rows,
        "env_checked": ("OPTIX_ROOT", "OptiX_INSTALL_DIR", "NVIDIA_OPTIX_SDK", "OPTIX_SDK_DIR"),
    }


def _gpu_status() -> dict[str, object]:
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return {"nvidia_smi_available": False, "rt_core_likely": False, "gpu_names": []}
    probe = _run([nvidia_smi, "--query-gpu=name,driver_version", "--format=csv,noheader"])
    rows = [line.strip() for line in str(probe["stdout"]).splitlines() if line.strip()]
    names = [row.split(",", 1)[0].strip() for row in rows]
    rt_markers = ("RTX", "L4", "L40", "A10", "A16", "A40", "A4000", "A5000", "A6000", "T4")
    rt_core_likely = any(any(marker in name.upper() for marker in rt_markers) for name in names)
    return {
        "nvidia_smi_available": bool(probe["available"]),
        "rt_core_likely": bool(rt_core_likely),
        "gpu_names": names,
        "probe": probe,
    }


def _author_status(author_root: Path) -> dict[str, object]:
    release_bin = author_root / "release" / "bin"
    build_bin = author_root / "build" / "bin"
    query_candidates = (release_bin / "query_exec", build_bin / "query_exec")
    polyover_candidates = (release_bin / "polyover_exec", build_bin / "polyover_exec")
    commit = None
    if (author_root / ".git").exists():
        probe = _run(["git", "rev-parse", "HEAD"], cwd=author_root)
        if probe["available"]:
            commit = str(probe["stdout"]).strip()
    query_exec = next((path for path in query_candidates if path.exists()), None)
    polyover_exec = next((path for path in polyover_candidates if path.exists()), None)
    return {
        "root": str(author_root),
        "exists": author_root.exists(),
        "git_commit": commit,
        "known_probe_commit": KNOWN_AUTHOR_COMMIT,
        "query_exec": None if query_exec is None else str(query_exec),
        "query_exec_exists": query_exec is not None,
        "polyover_exec": None if polyover_exec is None else str(polyover_exec),
        "polyover_exec_exists": polyover_exec is not None,
        "binaries_ready": query_exec is not None and polyover_exec is not None,
    }


def _dataset_status(dataset_root: Path) -> dict[str, object]:
    pair_ids = tuple(pair.pair_id for pair in paper_pairs())
    rows = availability_matrix(dataset_root, pair_ids=pair_ids, program_ids=("overlay",))
    ready = sum(1 for row in rows if row.exact_input_ready)
    return {
        "root": str(dataset_root),
        "preprocessed_share_url": RAYJOIN_PREPROCESSED_SHARE_URL,
        "overlay_pairs_total": len(rows),
        "overlay_pairs_ready": ready,
        "all_overlay_pairs_ready": ready == len(rows),
        "rows": [
            {
                "pair_id": row.pair_id,
                "paper_label": row.paper_label,
                "exact_input_ready": row.exact_input_ready,
                "blocker": row.blocker,
                "left_path": row.left.path,
                "right_path": row.right.path,
            }
            for row in rows
        ],
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    tools = {
        "git": _tool_status("git", ["--version"]),
        "cmake": _tool_status("cmake", ["--version"]),
        "nvcc": _tool_status("nvcc", ["--version"]),
        "python": _tool_status("python3", ["--version"]),
    }
    packages = {
        "glog": _pkg_config_status("libglog"),
        "gflags": _pkg_config_status("gflags"),
    }
    optix = _optix_status()
    gpu = _gpu_status()
    author = _author_status(args.author_root)
    dataset = _dataset_status(args.dataset_root)
    clone_command = [
        "git",
        "clone",
        args.author_repo_url,
        str(args.author_root),
    ]
    build_command = [
        "cmake",
        "-S",
        str(args.author_root),
        "-B",
        str(args.author_root / "release"),
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    compile_command = ["cmake", "--build", str(args.author_root / "release"), "-j", str(args.jobs)]
    runbook_command = [
        "python3",
        "scripts/rayjoin_section57_pod_runbook.py",
        "--dataset-root",
        str(args.dataset_root),
        "--query-exec",
        author["query_exec"] or str(args.author_root / "release" / "bin" / "query_exec"),
        "--polyover-exec",
        author["polyover_exec"] or str(args.author_root / "release" / "bin" / "polyover_exec"),
        "--output-dir",
        str(args.output_dir),
    ]
    blockers: list[str] = []
    for tool in ("git", "cmake", "nvcc"):
        if not tools[tool]["available"]:
            blockers.append(f"missing_tool_{tool}")
    for package in ("glog", "gflags"):
        if not packages[package]["available"]:
            blockers.append(f"missing_pkg_config_{package}")
    if not optix["available"]:
        blockers.append("missing_optix_headers")
    if not gpu["rt_core_likely"]:
        blockers.append("rt_core_gpu_not_detected")
    if not author["exists"]:
        blockers.append("missing_author_source")
    if not author["binaries_ready"]:
        blockers.append("missing_author_binaries")
    if not dataset["all_overlay_pairs_ready"]:
        blockers.append("missing_exact_section57_cdb_inputs")
    return {
        "schema": "rtdl.rayjoin.section57_pod_setup.v1",
        "ready_for_section57_runbook": not blockers,
        "blockers": blockers,
        "author_repo": {
            "url": args.author_repo_url,
            "known_probe_commit": KNOWN_AUTHOR_COMMIT,
            "clone_command": clone_command,
            "configure_command": build_command,
            "build_command": compile_command,
        },
        "author": author,
        "dataset": dataset,
        "tools": tools,
        "packages": packages,
        "optix": optix,
        "gpu": gpu,
        "next_command": runbook_command,
        "claim_boundary": (
            "Setup readiness is not performance evidence. It only reports whether "
            "the author code, exact inputs, and POD runtime look ready for the "
            "Section 5.7 runbook."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight the POD setup required by RayJoin Section 5.7.")
    parser.add_argument("--author-root", type=Path, default=Path("/workspace/RayJoin_fresh"))
    parser.add_argument("--author-repo-url", default=AUTHOR_REPO_URL)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/rayjoin_section57"))
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    payload = build_payload(args)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
