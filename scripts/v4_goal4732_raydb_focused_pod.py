#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GOAL4669_PATH = ROOT / "scripts" / "v4_goal4669_full_app_level_pod_benchmark.py"
SPEC = importlib.util.spec_from_file_location("_goal4669", GOAL4669_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"could not load {GOAL4669_PATH}")
goal4669 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(goal4669)
goal4654 = goal4669._goal4654


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return float(numerator) / float(denominator)


def _read(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any] | None, path: tuple[str, ...]) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def run(output_dir: Path, *, profile: str, timeout_sec: int) -> dict[str, Any]:
    versions = goal4669._versions()
    goal4654._copy_compat_libraries(versions)
    values = goal4669._profile_values(profile)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    triangle_file = output_dir / "unused_triangle_fixture_for_raydb_only.edgebin"

    executions = []
    for version, info in versions.items():
        command = goal4669._commands(info["root"], version, values, triangle_file)["raydb_style"]
        env = goal4654._env_for(info["root"], tag_native_optix_build=bool(info["tag_native_optix_build"]))
        executions.append(
            goal4654._run_command(
                version=version,
                app="raydb_style",
                command=command,
                cwd=info["root"],
                env=env,
                out_dir=raw_dir,
                timeout_sec=timeout_sec,
            )
        )

    rows = {}
    for execution in executions:
        payload = _read(Path(execution["stdout_json"]))
        metrics = goal4669._extract_metrics("raydb_style", payload)
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        rows[execution["version"]] = {
            "execution": execution,
            "metrics": metrics,
            "backend": payload.get("backend") if isinstance(payload, dict) else None,
            "matches_cpu_reference": payload.get("matches_cpu_reference") if isinstance(payload, dict) else None,
            "v4_api_surface": metadata.get("v4_api_surface"),
            "prepared_ray_batch_layout": metadata.get("prepared_ray_batch_layout"),
            "prepared_ray_batch_column_partner": metadata.get("prepared_ray_batch_column_partner"),
            "native_direct_device_output_columns": metadata.get("native_direct_device_output_columns"),
            "host_row_bridge_bypassed": metadata.get("host_row_bridge_bypassed"),
            "group_rows_downloaded_to_host_in_hot_path": metadata.get(
                "group_rows_downloaded_to_host_in_hot_path"
            ),
            "adapter": _nested(metadata, ("v4_adapter_metadata", "adapter")),
            "adapter_partner": _nested(metadata, ("v4_adapter_metadata", "partner")),
            "partner_claim_status": _nested(metadata, ("v4_adapter_metadata", "partner_claim_status")),
        }

    v2 = rows.get("v2_14", {}).get("metrics", {})
    v3 = rows.get("v3_0_2", {}).get("metrics", {})
    v4 = rows.get("v4_current", {}).get("metrics", {})
    analysis = {
        "v4_vs_v2_14_hot": _ratio(v2.get("hot_sec"), v4.get("hot_sec")),
        "v4_vs_v3_0_2_hot": _ratio(v3.get("hot_sec"), v4.get("hot_sec")),
        "v4_vs_v2_14_primary_wall": _ratio(v2.get("primary_wall_sec"), v4.get("primary_wall_sec")),
        "v4_vs_v3_0_2_primary_wall": _ratio(v3.get("primary_wall_sec"), v4.get("primary_wall_sec")),
        "v4_route_metadata_pass": (
            rows.get("v4_current", {}).get("backend") == "paper_rt_v4_cupy_device_grouped_reduction"
            and rows.get("v4_current", {}).get("matches_cpu_reference") is True
            and rows.get("v4_current", {}).get("adapter")
            == "v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays"
            and rows.get("v4_current", {}).get("native_direct_device_output_columns") is True
            and rows.get("v4_current", {}).get("host_row_bridge_bypassed") is True
            and rows.get("v4_current", {}).get("group_rows_downloaded_to_host_in_hot_path") is False
        ),
        "release_claim_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    payload = {
        "goal": "Goal4732",
        "status": "raydb_focused_pod_rerun_complete_not_release",
        "profile": profile,
        "output_dir": str(output_dir),
        "executions": executions,
        "rows": rows,
        "analysis": analysis,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
        },
    }
    (output_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# V4 Goal4732 RayDB Focused POD Rerun",
        "",
        f"Status: `{payload['status']}`",
        "",
        "| version | backend | hot sec | wall sec | parity | route |",
        "|---|---|---:|---:|---|---|",
    ]
    for version in ("v2_14", "v3_0_2", "v4_current"):
        row = rows.get(version, {})
        metrics = row.get("metrics", {})
        lines.append(
            f"| `{version}` | `{row.get('backend')}` | {metrics.get('hot_sec')} | "
            f"{metrics.get('primary_wall_sec')} | {row.get('matches_cpu_reference')} | "
            f"`{row.get('adapter') or row.get('prepared_ray_batch_layout')}` |"
        )
    lines.extend(
        [
            "",
            "## Ratios",
            "",
            f"- V4/V2.14 hot: `{analysis['v4_vs_v2_14_hot']}`",
            f"- V4/V3.0.2 hot: `{analysis['v4_vs_v3_0_2_hot']}`",
            f"- V4 route metadata pass: `{analysis['v4_route_metadata_pass']}`",
            "",
            "## Non-Authorization",
            "",
            "This focused rerun does not authorize final V4 tag, public speedup wording, "
            "whole-app high-performance wording, or all-benchmark speedup claims.",
            "",
        ]
    )
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Goal4732 focused RayDB POD rerun.")
    parser.add_argument("--output-dir", type=Path, default=Path("/root/v4_goal4732_raydb_focused_20260626"))
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--timeout-sec", type=int, default=900)
    args = parser.parse_args()
    run(args.output_dir, profile=args.profile, timeout_sec=int(args.timeout_sec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
