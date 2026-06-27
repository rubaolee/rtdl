#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


APP_REL = Path("examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py")
PREPARED_EXEC_REL = Path("src/rtdsl/prepared_execution.py")
MODE_NAMES = (
    "prepared_execution_fused_vector_sum_numba_cuda",
    "fused_frontier_force_sum_bucketized_numba_cuda",
    "fused_frontier_force_sum_bucketized_cpu",
    "grouped_vector_sum_typed_stream_plan",
    "v2_8_grouped_vector_sum_plan",
    "embree_node_coverage_prepared",
    "optix_node_coverage_prepared",
    "prepared_aggregate_frontier_weighted_vector_optix",
)
FUNCTION_NAMES = (
    "run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phoenix V3 M29 Barnes-Hut v2.14/current surface classification."
    )
    parser.add_argument("--v2-tree", required=True, type=Path)
    parser.add_argument("--current-tree", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--pod-host", default="unknown")
    parser.add_argument("--pod-port", default="unknown")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_payload(
        v2_tree=args.v2_tree,
        current_tree=args.current_tree,
        pod_host=args.pod_host,
        pod_port=str(args.pod_port),
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "classification": payload["classification"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if payload["status"] != "blocked" else 2


def build_payload(*, v2_tree: Path, current_tree: Path, pod_host: str, pod_port: str) -> dict[str, Any]:
    v2_info = inspect_tree(v2_tree)
    current_info = inspect_tree(current_tree)
    classification = classify(v2_info=v2_info, current_info=current_info)
    status = "blocked" if classification.startswith("blocked") else "classified_not_release"
    return {
        "schema": "rtdl.phoenix_v3.m29.barnes_hut_surface_classification.v1",
        "status": status,
        "classification": classification,
        "pod": {
            "host": pod_host,
            "port": pod_port,
            "gpu": _command_output(
                [
                    "nvidia-smi",
                    "--query-gpu=name,driver_version",
                    "--format=csv,noheader",
                ],
                Path("/root"),
            ),
        },
        "v2_14": v2_info,
        "current": current_info,
        "m28_carry_forward": {
            "m28_local_base_commit": "8e0f052bffec02507aaf5ed05f75dfe995f39883",
            "m28_remote_execution_git_commit": None,
            "m28_remote_execution_git_commit_null_reason": "remote execution tree was not a git checkout",
            "runtime_sourced_material_gain_true_scope": (
                "historical OptiX/frontier displacement only, not current runner/control parity"
            ),
            "validation_skipped_scope": (
                "large-row per-row CPU/oracle validation skipped; runner/control equivalence is covered "
                "by contribution count and checksum X/Y gates"
            ),
        },
        "non_authorization": {
            "release_authorized": False,
            "all_app_run_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_over_v2_claim_authorized": False,
            "rt_core_speedup_claim_authorized_for_numba_cuda_fused_route": False,
            "true_zero_copy_claim_authorized": False,
            "v4_work_authorized": False,
        },
    }


def inspect_tree(root: Path) -> dict[str, Any]:
    app = root / APP_REL
    prepared_execution = root / PREPARED_EXEC_REL
    app_text = app.read_text(encoding="utf-8") if app.exists() else ""
    prepared_text = prepared_execution.read_text(encoding="utf-8") if prepared_execution.exists() else ""
    modes = _modes_from_source(app_text)
    is_git_checkout = (root / ".git").exists()
    return {
        "path": str(root),
        "exists": root.exists(),
        "is_git_checkout": is_git_checkout,
        "git_head": _command_output(["git", "rev-parse", "HEAD"], root) if is_git_checkout else None,
        "git_status_short": _command_output(["git", "status", "--short"], root) if is_git_checkout else None,
        "version": (root / "VERSION").read_text(encoding="utf-8").strip()
        if (root / "VERSION").exists()
        else None,
        "app_file_exists": app.exists(),
        "prepared_execution_file_exists": prepared_execution.exists(),
        "app_sha256": _sha256(app),
        "prepared_execution_sha256": _sha256(prepared_execution),
        "mode_count": len(modes),
        "modes": modes,
        "mode_presence": {name: name in modes or name in app_text for name in MODE_NAMES},
        "function_presence": {name: name in prepared_text for name in FUNCTION_NAMES},
    }


def classify(*, v2_info: dict[str, Any], current_info: dict[str, Any]) -> str:
    current_modes = dict(current_info["mode_presence"])
    current_functions = dict(current_info["function_presence"])
    if not (
        current_modes["prepared_execution_fused_vector_sum_numba_cuda"]
        and current_functions["run_aggregate_tree_fused_weighted_vector_sum_2d_prepared_session"]
    ):
        return "blocked_current_surface_missing"

    v2_modes = dict(v2_info["mode_presence"])
    if (
        v2_modes["prepared_execution_fused_vector_sum_numba_cuda"]
        or v2_modes["fused_frontier_force_sum_bucketized_numba_cuda"]
    ):
        return "v2_14_has_equivalent_fused_surface"
    if v2_modes["fused_frontier_force_sum_bucketized_cpu"] or v2_modes["grouped_vector_sum_typed_stream_plan"]:
        return "v2_14_has_cpu_fused_or_typed_stream_only"
    if v2_modes["embree_node_coverage_prepared"] or v2_modes["optix_node_coverage_prepared"]:
        return "v2_14_has_only_node_coverage_or_frontier_route"
    return "v2_14_lacks_current_trunk_surface"


def _modes_from_source(text: str) -> list[str]:
    if not text:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "MODES" for target in node.targets):
            continue
        try:
            value = ast.literal_eval(node.value)
        except Exception:
            return []
        return list(value) if isinstance(value, tuple) else []
    return []


def _sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _command_output(command: list[str], cwd: Path) -> str | None:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None


def _readme(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Phoenix V3 M29 Barnes-Hut Surface Classification",
            "",
            f"Status: `{payload['status']}`",
            f"Classification: `{payload['classification']}`",
            "",
            f"V2.14 HEAD: `{payload['v2_14']['git_head']}`",
            f"Current git head: `{payload['current']['git_head']}`",
            f"Current is git checkout: `{payload['current']['is_git_checkout']}`",
            "",
            "This packet authorizes no release, no all-app run, no public speedup claim, "
            "no broad V3-over-V2 claim, no RT-core speedup claim, no true-zero-copy claim, "
            "and no V4 work.",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
