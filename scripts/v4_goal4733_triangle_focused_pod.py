#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
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


def _row_from_payload(execution: dict[str, Any]) -> dict[str, Any]:
    payload = _read(Path(execution["stdout_json"]))
    metrics = goal4669._extract_metrics("triangle_counting", payload)
    return {
        "execution": execution,
        "metrics": metrics,
        "mode": payload.get("mode") if isinstance(payload, dict) else None,
        "triangle_count_matches_oracle": (
            payload.get("triangle_count_matches_oracle") if isinstance(payload, dict) else None
        ),
        "triangle_count": payload.get("triangle_count") if isinstance(payload, dict) else None,
        "oracle_triangle_count": payload.get("oracle_triangle_count") if isinstance(payload, dict) else None,
        "timing_ms": payload.get("timing_ms", {}) if isinstance(payload, dict) else {},
        "phase_split_ms": payload.get("phase_split_ms", {}) if isinstance(payload, dict) else {},
        "prepared_reused": _nested(payload, ("generic_rt_summary", "last_segment_summary", "prepared_reused")),
        "prepared_scene_used": _nested(payload, ("generic_rt_summary", "last_segment_summary", "prepared_scene_used")),
        "prepared_ray_batch_used": _nested(payload, ("generic_rt_summary", "last_segment_summary", "prepared_ray_batch_used")),
        "ray_columns_partner_owned": _nested(
            payload,
            (
                "generic_rt_summary",
                "last_segment_summary",
                "transfer_metadata",
                "ray_columns_partner_owned",
            ),
        ),
        "query_rays_uploaded_each_run": _nested(
            payload,
            (
                "generic_rt_summary",
                "last_segment_summary",
                "transfer_metadata",
                "query_rays_uploaded_each_run",
            ),
        ),
        "ray_weights_uploaded_each_run": _nested(
            payload,
            (
                "generic_rt_summary",
                "last_segment_summary",
                "transfer_metadata",
                "ray_weights_uploaded_each_run",
            ),
        ),
        "last_phase_timing_seconds": _nested(
            payload,
            ("generic_rt_summary", "last_segment_summary", "phase_timing_seconds"),
        ),
    }


def run(
    output_dir: Path,
    *,
    profile: str,
    timeout_sec: int,
    repeat: int,
    warmup: int,
) -> dict[str, Any]:
    versions = goal4669._versions()
    goal4654._copy_compat_libraries(versions)
    values = goal4669._profile_values(profile)
    values["triangle_repeat"] = int(repeat)
    values["triangle_warmup"] = int(warmup)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    fixture_env = goal4654._env_for(versions["v4_current"]["root"], tag_native_optix_build=True)
    triangle_fixture = goal4654._write_triangle_fixture(
        versions["v4_current"]["root"],
        output_dir / f"k4_{values['triangle_k4_cliques']}.edgebin",
        int(values["triangle_k4_cliques"]),
        goal4669._python(versions["v4_current"]["root"]),
        fixture_env,
    )

    executions = []
    for version, info in versions.items():
        command = goal4669._commands(info["root"], version, values, Path(triangle_fixture["path"]))[
            "triangle_counting"
        ]
        env = goal4654._env_for(info["root"], tag_native_optix_build=bool(info["tag_native_optix_build"]))
        executions.append(
            goal4654._run_command(
                version=version,
                app="triangle_counting",
                command=command,
                cwd=info["root"],
                env=env,
                out_dir=raw_dir,
                timeout_sec=timeout_sec,
            )
        )

    rows = {execution["version"]: _row_from_payload(execution) for execution in executions}
    v2 = rows.get("v2_14", {}).get("metrics", {})
    v3 = rows.get("v3_0_2", {}).get("metrics", {})
    v4 = rows.get("v4_current", {}).get("metrics", {})
    v4_phase = rows.get("v4_current", {}).get("phase_split_ms", {})
    v3_phase = rows.get("v3_0_2", {}).get("phase_split_ms", {})
    v4_hot = v4.get("hot_sec")
    v3_hot = v3.get("hot_sec")
    analysis = {
        "v4_vs_v2_14_hot": _ratio(v2.get("hot_sec"), v4_hot),
        "v4_vs_v3_0_2_hot": _ratio(v3_hot, v4_hot),
        "v4_vs_v3_0_2_query_median_ms_delta": (
            (float(v4_hot) - float(v3_hot)) * 1000.0
            if isinstance(v4_hot, (int, float)) and isinstance(v3_hot, (int, float))
            else None
        ),
        "all_rows_parity": all(
            row.get("triangle_count_matches_oracle") is True
            for row in rows.values()
        ),
        "v4_residency_metadata_pass": (
            rows.get("v4_current", {}).get("prepared_reused") is True
            and rows.get("v4_current", {}).get("prepared_scene_used") is True
            and rows.get("v4_current", {}).get("prepared_ray_batch_used") is True
            and rows.get("v4_current", {}).get("ray_columns_partner_owned") is True
            and rows.get("v4_current", {}).get("query_rays_uploaded_each_run") is False
            and rows.get("v4_current", {}).get("ray_weights_uploaded_each_run") is False
        ),
        "v3_phase_split_ms": v3_phase,
        "v4_phase_split_ms": v4_phase,
        "classification_hint": None,
        "release_claim_authorized": False,
        "public_speedup_claim_authorized": False,
    }
    ratio_v3 = analysis["v4_vs_v3_0_2_hot"]
    if ratio_v3 is not None and ratio_v3 >= 0.98:
        analysis["classification_hint"] = "v3_regression_cleared_by_high_repeat_focused_rerun"
    elif ratio_v3 is not None:
        analysis["classification_hint"] = "v3_regression_persists_after_high_repeat_focused_rerun"
    payload = {
        "goal": "Goal4733",
        "status": "triangle_focused_pod_rerun_complete_not_release",
        "profile": profile,
        "profile_values": values,
        "output_dir": str(output_dir),
        "triangle_fixture": triangle_fixture,
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
        "# V4 Goal4733 Triangle Focused POD Rerun",
        "",
        f"Status: `{payload['status']}`",
        f"Repeat/warmup: `{repeat}/{warmup}`",
        "",
        "| version | mode | hot sec | query median ms | parity | prepared reused |",
        "|---|---|---:|---:|---|---|",
    ]
    for version in ("v2_14", "v3_0_2", "v4_current"):
        row = rows.get(version, {})
        metrics = row.get("metrics", {})
        timing = row.get("timing_ms", {})
        phase = row.get("phase_split_ms", {})
        query_median = timing.get("query_median_ms") or phase.get("measured_replay_query_median_ms")
        lines.append(
            f"| `{version}` | `{row.get('mode')}` | {metrics.get('hot_sec')} | "
            f"{query_median} | {row.get('triangle_count_matches_oracle')} | "
            f"{row.get('prepared_reused')} |"
        )
    lines.extend(
        [
            "",
            "## Ratios",
            "",
            f"- V4/V2.14 hot: `{analysis['v4_vs_v2_14_hot']}`",
            f"- V4/V3.0.2 hot: `{analysis['v4_vs_v3_0_2_hot']}`",
            f"- V4-V3 query median delta ms: `{analysis['v4_vs_v3_0_2_query_median_ms_delta']}`",
            f"- All rows parity: `{analysis['all_rows_parity']}`",
            f"- V4 residency metadata pass: `{analysis['v4_residency_metadata_pass']}`",
            f"- Classification hint: `{analysis['classification_hint']}`",
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
    parser = argparse.ArgumentParser(description="Run the Goal4733 focused triangle POD rerun.")
    parser.add_argument("--output-dir", type=Path, default=Path("/root/v4_goal4733_triangle_focused_20260626"))
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--timeout-sec", type=int, default=900)
    parser.add_argument("--repeat", type=int, default=201)
    parser.add_argument("--warmup", type=int, default=20)
    args = parser.parse_args()
    run(
        args.output_dir,
        profile=args.profile,
        timeout_sec=int(args.timeout_sec),
        repeat=int(args.repeat),
        warmup=int(args.warmup),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
