#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any


VERSION = "rtdl.v4.goal4669.full_app_level_pod_benchmark_after_hausdorff.v1"

ROOT = Path(__file__).resolve().parents[1]
_GOAL4654_PATH = ROOT / "scripts" / "v4_goal4654_full_app_level_pod_benchmark.py"
_SPEC = importlib.util.spec_from_file_location("_rtdl_goal4654_runner", _GOAL4654_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"could not load Goal4654 runner from {_GOAL4654_PATH}")
_goal4654 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_goal4654)


APP_ORDER = (
    "rt_dbscan",
    "raydb_style",
    "triangle_counting",
    "librts_spatial_index",
    "hausdorff_xhd",
)


def _versions() -> dict[str, dict[str, Any]]:
    return _goal4654._versions()


def _python(root: Path) -> str:
    return _goal4654._python(root)


def _profile_values(profile: str) -> dict[str, Any]:
    values = dict(_goal4654._profile_values(profile))
    if profile == "smoke":
        values.update(
            {
                "hausdorff_copies": 256,
                "hausdorff_repeat": 1,
                "hausdorff_warmup": 0,
                "hausdorff_correctness_copies": 1024,
                "hausdorff_correctness_coordinate_normalization_span": 1000000.0,
            }
        )
    elif profile == "serious":
        values.update(
            {
                "hausdorff_copies": 65536,
                "hausdorff_repeat": 9,
                "hausdorff_warmup": 5,
                "hausdorff_correctness_copies": 262144,
                "hausdorff_correctness_coordinate_normalization_span": 1000000.0,
            }
        )
    else:
        raise ValueError(f"unknown profile {profile!r}")
    return values


def _hausdorff_command(root: Path, version: str, profile: dict[str, Any], *, correctness_probe: bool = False) -> list[str]:
    py = _python(root)
    copies = (
        int(profile["hausdorff_correctness_copies"])
        if correctness_probe
        else int(profile["hausdorff_copies"])
    )
    if version == "v2_14":
        return [
            py,
            "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
            "--backend",
            "embree",
            "--embree-result-mode",
            "directed_summary",
            "--copies",
            str(copies),
        ]
    command = [
        py,
        "examples/benchmark_apps/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
        "--backend",
        "optix_device_max_nearest",
        "--partner",
        "cupy",
        "--copies",
        str(copies),
        "--repeat",
        str(profile["hausdorff_repeat"]),
        "--warmup",
        str(profile["hausdorff_warmup"]),
    ]
    if correctness_probe:
        command.extend(
            [
                "--coordinate-normalization-span",
                str(profile["hausdorff_correctness_coordinate_normalization_span"]),
            ]
        )
    return command


def _commands(root: Path, version: str, profile: dict[str, Any], triangle_file: Path) -> dict[str, list[str]]:
    commands = dict(_goal4654._commands(root, version, profile, triangle_file))
    commands["hausdorff_xhd"] = _hausdorff_command(root, version, profile)
    if version == "v4_current":
        py = _python(root)
        commands["raydb_style"] = [
            py,
            "examples/benchmark_apps/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "--mode",
            "sum",
            "--backend",
            "paper_rt_v4_cupy_device_grouped_reduction",
            "--fixture-kind",
            "generated",
            "--generated-rows",
            str(profile["raydb_rows"]),
            "--generated-groups",
            str(profile["raydb_groups"]),
            "--repeat",
            str(profile["raydb_repeat"]),
            "--warmup",
            str(profile["raydb_warmup"]),
            "--summary-only-iterations",
        ]
    return commands


def _read_payload(path: Path) -> dict[str, Any] | None:
    return _goal4654._read_payload(path)


def _first_number(*values: Any) -> float | None:
    return _goal4654._first_number(*values)


def _get_nested(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    return _goal4654._get_nested(data, path)


def _ratio(a: float | None, b: float | None) -> float | None:
    return _goal4654._ratio(a, b)


def _hausdorff_correctness(payload: dict[str, Any]) -> bool:
    if payload.get("matches_oracle") is True:
        return True
    if payload.get("matches_reference") is True:
        return True
    expected = _get_nested(payload, ("expected", "hausdorff_distance"))
    observed = payload.get("hausdorff_distance")
    if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
        return math.isclose(float(expected), float(observed), rel_tol=1e-5, abs_tol=1e-5)
    return False


def _extract_metrics(app: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    if app in {"hausdorff_xhd", "hausdorff_xhd_correctness_1m"}:
        if payload is None:
            return {
                "json_parse_ok": False,
                "correctness_parity": False,
                "primary_wall_sec": None,
                "hot_sec": None,
            }
        run_phases = payload.get("run_phases", {}) if isinstance(payload.get("run_phases"), dict) else {}
        route = str(payload.get("backend"))
        hot = _first_number(
            run_phases.get("hot_device_sec"),
            run_phases.get("native_directed_summary_sec"),
            run_phases.get("optix_device_max_nearest_directed_summary_sec"),
        )
        primary = _first_number(
            run_phases.get("optix_device_max_nearest_directed_summary_sec"),
            run_phases.get("native_directed_summary_sec"),
            payload.get("elapsed_sec"),
            hot,
        )
        return {
            "json_parse_ok": True,
            "correctness_parity": _hausdorff_correctness(payload),
            "primary_wall_sec": primary,
            "hot_sec": hot,
            "prepare_sec": _first_number(run_phases.get("scene_prepare_sec")),
            "materialize_sec": _first_number(run_phases.get("materialize_sec")),
            "route": route,
            "copies": payload.get("copies"),
            "points_per_side": int(payload.get("copies", 0)) * 4 if isinstance(payload.get("copies"), int) else None,
            "coordinate_normalization_used": bool(payload.get("coordinate_normalization_used")),
        }
    return _goal4654._extract_metrics(app, payload)


def _analyze(executions: list[dict[str, Any]], versions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    by_app_version: dict[tuple[str, str], dict[str, Any]] = {}
    rt_dbscan_parity_by_version: dict[str, dict[str, Any]] = {}
    hausdorff_correctness_probe: dict[str, Any] | None = None
    for execution in executions:
        payload = _read_payload(Path(execution["stdout_json"]))
        metrics = _extract_metrics(execution["app"], payload)
        row = {
            **execution,
            "payload_metrics": metrics,
            "version_label": versions[execution["version"]]["label"],
            "tag_native_optix_build": versions[execution["version"]]["tag_native_optix_build"],
            "optix_library_note": versions[execution["version"]]["optix_library_note"],
        }
        rows.append(row)
        by_app_version[(execution["app"], execution["version"])] = row
        if execution["app"] == "rt_dbscan_parity":
            rt_dbscan_parity_by_version[execution["version"]] = row
        if execution["app"] == "hausdorff_xhd_correctness_1m":
            hausdorff_correctness_probe = row

    app_scorecard = []
    for app in APP_ORDER:
        v2 = by_app_version.get((app, "v2_14"), {})
        v3 = by_app_version.get((app, "v3_0_2"), {})
        v4 = by_app_version.get((app, "v4_current"), {})
        v2_metrics = v2.get("payload_metrics", {})
        v3_metrics = v3.get("payload_metrics", {})
        v4_metrics = v4.get("payload_metrics", {})
        v2_hot = v2_metrics.get("hot_sec")
        v3_hot = v3_metrics.get("hot_sec")
        v4_hot = v4_metrics.get("hot_sec")
        v2_wall = v2_metrics.get("primary_wall_sec")
        v3_wall = v3_metrics.get("primary_wall_sec")
        v4_wall = v4_metrics.get("primary_wall_sec")

        def correctness_ok(version: str) -> bool:
            primary = by_app_version.get((app, version), {})
            if primary.get("payload_metrics", {}).get("correctness_parity") is True:
                return True
            if app == "rt_dbscan":
                companion = rt_dbscan_parity_by_version.get(version, {})
                return companion.get("payload_metrics", {}).get("correctness_parity") is True
            return False

        row = {
            "app": app,
            "v2_14_hot_sec": v2_hot,
            "v3_0_2_hot_sec": v3_hot,
            "v4_hot_sec": v4_hot,
            "v2_14_primary_wall_sec": v2_wall,
            "v3_0_2_primary_wall_sec": v3_wall,
            "v4_primary_wall_sec": v4_wall,
            "v4_vs_v2_14_hot_speedup": _ratio(v2_hot, v4_hot),
            "v4_vs_v3_0_2_hot_speedup": _ratio(v3_hot, v4_hot),
            "v3_0_2_vs_v2_14_hot_speedup": _ratio(v2_hot, v3_hot),
            "v4_vs_v2_14_primary_wall_speedup": _ratio(v2_wall, v4_wall),
            "v4_vs_v3_0_2_primary_wall_speedup": _ratio(v3_wall, v4_wall),
            "v3_0_2_vs_v2_14_primary_wall_speedup": _ratio(v2_wall, v3_wall),
            "v4_prepare_vs_v3_0_2_speedup": _ratio(
                v3_metrics.get("prepare_sec"),
                v4_metrics.get("prepare_sec"),
            ),
            "all_returncode_zero": all(
                int(by_app_version.get((app, version), {}).get("returncode", -1)) == 0
                for version in ("v2_14", "v3_0_2", "v4_current")
            ),
            "all_json_parse_ok": all(
                by_app_version.get((app, version), {})
                .get("payload_metrics", {})
                .get("json_parse_ok")
                is True
                for version in ("v2_14", "v3_0_2", "v4_current")
            ),
            "all_correctness_parity_or_skipped_oracle": all(
                correctness_ok(version) for version in ("v2_14", "v3_0_2", "v4_current")
            ),
            "correctness_supported_by_companion": app == "rt_dbscan"
            and all(correctness_ok(version) for version in ("v2_14", "v3_0_2", "v4_current")),
        }
        if app == "hausdorff_xhd":
            probe_metrics = (hausdorff_correctness_probe or {}).get("payload_metrics", {})
            row["coordinate_normalized_1m_correctness_probe_passed"] = (
                bool(hausdorff_correctness_probe)
                and int((hausdorff_correctness_probe or {}).get("returncode", -1)) == 0
                and probe_metrics.get("correctness_parity") is True
                and probe_metrics.get("coordinate_normalization_used") is True
            )
            row["hausdorff_frozen_bar_passed"] = (
                row["all_returncode_zero"]
                and row["all_correctness_parity_or_skipped_oracle"]
                and row["coordinate_normalized_1m_correctness_probe_passed"]
                and (row["v4_vs_v2_14_primary_wall_speedup"] or 0.0) >= 1.20
                and (row["v4_vs_v3_0_2_hot_speedup"] or 0.0) >= 1.20
                and (row["v4_prepare_vs_v3_0_2_speedup"] or 0.0) >= 0.80
            )
        app_scorecard.append(row)

    formal_native_purity = all(info["tag_native_optix_build"] for info in versions.values())
    return {
        "rows": rows,
        "app_scorecard": app_scorecard,
        "hausdorff_correctness_probe": hausdorff_correctness_probe,
        "formal_tag_native_optix_purity": formal_native_purity,
        "formal_release_blocker": None
        if formal_native_purity
        else "v2_14/v3_0_2 OptiX libraries could not be built on this POD because OptiX SDK headers are absent; OptiX-dependent old-version rows use a declared V4 compatibility native library",
        "all_rows_returncode_zero": all(int(row["returncode"]) == 0 for row in rows),
        "all_rows_json_parse_ok": all(row["payload_metrics"]["json_parse_ok"] for row in rows),
        "all_full_rows_have_hot_metric": all(
            row["payload_metrics"].get("hot_sec") is not None
            for row in rows
            if not row["app"].endswith("_correctness_1m")
        ),
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4669 Full App-Level POD Benchmark",
        "",
        f"Status: `{summary['status']}`",
        f"Profile: `{summary['profile']}`",
        "",
        "```text",
        "release_authorized: false",
        "broad_v4_speed_claim_authorized: false",
        "formal_high_performance_v4_authorized: false",
        f"formal_tag_native_optix_purity: {summary['analysis']['formal_tag_native_optix_purity']}",
        f"formal_release_blocker: {summary['analysis']['formal_release_blocker']}",
        "```",
        "",
        "## App Scorecard",
        "",
        "| App | V4/V2.14 hot | V4/V3.0.2 hot | V4/V2.14 primary wall | V4/V3.0.2 primary wall | RC OK | Parity |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary["analysis"]["app_scorecard"]:
        def fmt(value: Any) -> str:
            return "n/a" if value is None else f"{float(value):.3f}x"

        lines.append(
            f"| `{row['app']}` | {fmt(row['v4_vs_v2_14_hot_speedup'])} | "
            f"{fmt(row['v4_vs_v3_0_2_hot_speedup'])} | "
            f"{fmt(row['v4_vs_v2_14_primary_wall_speedup'])} | "
            f"{fmt(row['v4_vs_v3_0_2_primary_wall_speedup'])} | "
            f"{row['all_returncode_zero']} | {row['all_correctness_parity_or_skipped_oracle']} |"
        )
    lines.extend(
        [
            "",
            "## Hausdorff Boundary",
            "",
            "- Hausdorff is included because Goal4667 passed the focused gate.",
            "- The row is not a release by itself; it must remain classified inside the full app scorecard.",
            "- The 1M coordinate-normalized correctness probe is required and recorded separately.",
            "",
            "## Route And Provenance Notes",
            "",
            "- V2.14 and V3.0.2 source trees are clean tag archives from git.",
            "- V2.14 and V3.0.2 Embree libraries were built in their tag trees.",
            "- V2.14 and V3.0.2 OptiX native libraries could not be built on this POD because OptiX SDK headers are absent.",
            "- OptiX-dependent old-version rows therefore use a declared V4 compatibility native library; this blocks pure tag-native release authorization from Goal4669 alone.",
            "",
            "## Raw Rows",
            "",
            "| Version | App | RC | Hot sec | Wall sec | Route | Native purity |",
            "| --- | --- | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for row in summary["analysis"]["rows"]:
        metrics = row["payload_metrics"]
        hot = metrics.get("hot_sec")
        wall = metrics.get("primary_wall_sec")
        lines.append(
            f"| `{row['version']}` | `{row['app']}` | {row['returncode']} | "
            f"{'n/a' if hot is None else f'{float(hot):.6f}'} | "
            f"{'n/a' if wall is None else f'{float(wall):.6f}'} | "
            f"`{metrics.get('route')}` | {row['tag_native_optix_build']} |"
        )
    lines.extend(
        [
            "",
            "## Non-Authorization",
            "",
            "Goal4669 does not authorize public V4 release wording, broad speedup wording,",
            "or a formal high-performance V4 claim. The output is input to the next decision analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4669 refreshed five-app POD benchmark.")
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--output-dir", type=Path, default=Path("/root/v4_goal4669_full_app_level_pod_benchmark"))
    parser.add_argument("--timeout-sec", type=int, default=5400)
    args = parser.parse_args(argv)

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    versions = _versions()
    _goal4654._copy_compat_libraries(versions)
    profile = _profile_values(args.profile)

    fixture_env = _goal4654._env_for(versions["v4_current"]["root"], tag_native_optix_build=True)
    triangle_fixture = _goal4654._write_triangle_fixture(
        versions["v4_current"]["root"],
        out_dir / f"k4_{profile['triangle_k4_cliques']}.edgebin",
        int(profile["triangle_k4_cliques"]),
        _python(versions["v4_current"]["root"]),
        fixture_env,
    )

    executions: list[dict[str, Any]] = []
    for version, info in versions.items():
        root = info["root"]
        env = _goal4654._env_for(root, tag_native_optix_build=bool(info["tag_native_optix_build"]))
        commands = _commands(root, version, profile, Path(triangle_fixture["path"]))
        for app in APP_ORDER:
            executions.append(
                _goal4654._run_command(
                    version=version,
                    app=app,
                    command=commands[app],
                    cwd=root,
                    env=env,
                    out_dir=raw_dir,
                    timeout_sec=int(args.timeout_sec),
                )
            )
            if app == "rt_dbscan" and bool(profile.get("rt_dbscan_parity_companion")):
                executions.append(
                    _goal4654._run_command(
                        version=version,
                        app="rt_dbscan_parity",
                        command=_goal4654._rt_dbscan_command(root, version, profile, parity_companion=True),
                        cwd=root,
                        env=env,
                        out_dir=raw_dir,
                        timeout_sec=int(args.timeout_sec),
                    )
                )
        if version == "v4_current":
            executions.append(
                _goal4654._run_command(
                    version=version,
                    app="hausdorff_xhd_correctness_1m",
                    command=_hausdorff_command(root, version, profile, correctness_probe=True),
                    cwd=root,
                    env=env,
                    out_dir=raw_dir,
                    timeout_sec=int(args.timeout_sec),
                )
            )

    summary = {
        "schema": VERSION,
        "status": "goal4669_evidence_collected_not_release",
        "profile": args.profile,
        "profile_values": profile,
        "versions": {
            name: {
                **{key: value for key, value in info.items() if key != "root"},
                "root": str(info["root"]),
            }
            for name, info in versions.items()
        },
        "triangle_fixture": triangle_fixture,
        "executions": executions,
        "analysis": _analyze(executions, versions),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "formal_high_performance_v4_authorized": False,
            "partner_migration_counts_as_v4_speed_win": False,
            "v2_v3_old_optix_tag_native_purity_proven": False,
        },
        "decision_audit": {
            "was_i_stupid": "No for rerunning after a changed candidate row; yes would be publishing focused Hausdorff evidence as whole-app V4 proof.",
            "stupid_action_if_any": "Do not use operator-level or focused-route evidence as a substitute for app-level V2/V3/V4 evidence.",
            "alternative_path": "If Hausdorff fails inside the refreshed app scorecard, classify it as failed and do not preserve it by changing the bar.",
            "different_path_now": "Use this five-app evidence as input to the next decision analysis, not as a release authorization.",
        },
    }
    summary_path = out_dir / "summary.json"
    report_path = out_dir / "summary.md"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(_render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["analysis"]["all_rows_returncode_zero"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
