#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


VERSION = "rtdl.v4.goal4654.full_app_level_pod_benchmark.v1"


APP_ORDER = ("rt_dbscan", "raydb_style", "triangle_counting", "librts_spatial_index")


def _python(root: Path) -> str:
    return os.environ.get("RTDL_GOAL4654_PYTHON", "/root/rtdl_v4_venv/bin/python")


def _cuda_prefix() -> Path:
    return Path(
        os.environ.get(
            "RTDL_GOAL4654_CUDA_PREFIX",
            "/root/rtdl_v4_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc",
        )
    )


def _versions() -> dict[str, dict[str, Any]]:
    return {
        "v2_14": {
            "root": Path(os.environ.get("RTDL_GOAL4654_V2_ROOT", "/root/rtdl_v2_14_tag")),
            "label": "V2.14 tag",
            "tag_native_optix_build": False,
            "optix_library_note": "uses V4 candidate prebuilt librtdl_optix.so as compatibility library because OptiX SDK headers are absent on this POD",
        },
        "v3_0_2": {
            "root": Path(os.environ.get("RTDL_GOAL4654_V3_ROOT", "/root/rtdl_v3_0_2_tag")),
            "label": "V3.0.2 tag",
            "tag_native_optix_build": False,
            "optix_library_note": "uses V4 candidate prebuilt librtdl_optix.so as compatibility library because OptiX SDK headers are absent on this POD",
        },
        "v4_current": {
            "root": Path(os.environ.get("RTDL_GOAL4654_V4_ROOT", "/root/rtdl_v4_candidate_pod")),
            "label": "V4 current candidate",
            "tag_native_optix_build": True,
            "optix_library_note": "uses V4 candidate prebuilt native library in its own tree",
        },
    }


def _profile_values(profile: str) -> dict[str, Any]:
    if profile == "smoke":
        return {
            "rt_dbscan_point_count": 2048,
            "rt_dbscan_repeat": 1,
            "rt_dbscan_warmup": 0,
            "rt_dbscan_no_validation": False,
            "rt_dbscan_parity_companion": False,
            "raydb_rows": 2048,
            "raydb_groups": 64,
            "raydb_repeat": 1,
            "raydb_warmup": 0,
            "triangle_k4_cliques": 512,
            "triangle_repeat": 1,
            "triangle_warmup": 0,
            "librts_boxes": 2048,
            "librts_queries": 32,
            "librts_repeat": 1,
            "librts_warmup": 0,
        }
    if profile == "serious":
        return {
            "rt_dbscan_point_count": 262144,
            "rt_dbscan_repeat": 5,
            "rt_dbscan_warmup": 1,
            "rt_dbscan_no_validation": True,
            "rt_dbscan_parity_companion": True,
            "rt_dbscan_parity_point_count": 2048,
            "raydb_rows": 131072,
            "raydb_groups": 1024,
            "raydb_repeat": 7,
            "raydb_warmup": 2,
            "triangle_k4_cliques": 32768,
            "triangle_repeat": 7,
            "triangle_warmup": 2,
            "librts_boxes": 1_000_000,
            "librts_queries": 1000,
            "librts_repeat": 240,
            "librts_warmup": 1,
        }
    raise ValueError(f"unknown profile {profile!r}")


def _env_for(root: Path, *, tag_native_optix_build: bool) -> dict[str, str]:
    env = os.environ.copy()
    cuda_prefix = _cuda_prefix()
    env["PYTHONPATH"] = f"{root / 'src'}:{root}"
    env["CUDA_HOME"] = str(cuda_prefix)
    env["CUDA_PATH"] = str(cuda_prefix)
    env["NUMBA_CUDA_PREFIX"] = str(cuda_prefix)
    env["NUMBA_CUDA_NVVM"] = str(cuda_prefix / "nvvm" / "lib64" / "libnvvm.so")
    env["LD_LIBRARY_PATH"] = f"{cuda_prefix / 'nvvm' / 'lib64'}:{env.get('LD_LIBRARY_PATH', '')}"
    if tag_native_optix_build:
        optix = root / "build" / "librtdl_optix.so"
    else:
        optix = root / "build" / "librtdl_optix.v4compat.so"
    embree = root / "build" / "librtdl_embree.so"
    env["RTDL_OPTIX_LIBRARY"] = str(optix)
    env["RTDL_OPTIX_LIB"] = str(optix)
    env["RTDL_EMBREE_LIBRARY"] = str(embree)
    env["RTDL_EMBREE_LIB"] = str(embree)
    return env


def _copy_compat_libraries(versions: dict[str, dict[str, Any]]) -> None:
    v4_optix = versions["v4_current"]["root"] / "build" / "librtdl_optix.so"
    if not v4_optix.exists():
        return
    for name in ("v2_14", "v3_0_2"):
        root = versions[name]["root"]
        target = root / "build" / "librtdl_optix.v4compat.so"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.stat().st_size != v4_optix.stat().st_size:
            target.write_bytes(v4_optix.read_bytes())


def _run_command(
    *,
    version: str,
    app: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    out_dir: Path,
    timeout_sec: int,
) -> dict[str, Any]:
    stem = f"{version}_{app}"
    stdout_path = out_dir / f"{stem}.json"
    stderr_path = out_dir / f"{stem}.stderr.txt"
    started = time.time()
    started_perf = time.perf_counter()
    print(f"[goal4654] BEGIN {stem}", flush=True)
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_sec,
                check=False,
            )
            rc = int(completed.returncode)
            timed_out = False
            error = None
        except subprocess.TimeoutExpired as exc:
            rc = 124
            timed_out = True
            error = f"timeout after {exc.timeout} seconds"
    elapsed = time.perf_counter() - started_perf
    print(f"[goal4654] END {stem} rc={rc} elapsed={elapsed:.3f}s", flush=True)
    return {
        "version": version,
        "app": app,
        "command": command,
        "cwd": str(cwd),
        "stdout_json": str(stdout_path),
        "stderr": str(stderr_path),
        "returncode": rc,
        "timed_out": timed_out,
        "error": error,
        "runner_elapsed_sec": elapsed,
        "started_unix": started,
        "ended_unix": time.time(),
    }


def _write_triangle_fixture(root: Path, output: Path, cliques: int, python_exe: str, env: dict[str, str]) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        python_exe,
        "scripts/goal2631_generate_triangle_k4_binary.py",
        "--output",
        str(output),
        "--cliques",
        str(cliques),
    ]
    proc = subprocess.run(cmd, cwd=root, env=env, text=True, capture_output=True, check=False)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "path": str(output),
        "cliques": cliques,
        "edge_count": cliques * 6,
    }


def _rt_dbscan_command(
    root: Path,
    version: str,
    profile: dict[str, Any],
    *,
    parity_companion: bool = False,
) -> list[str]:
    py = _python(root)
    rt_mode = (
        "optix_rt_core_grouped_stream_numba_column_signature_3d"
        if version == "v4_current"
        else "optix_rt_core_grouped_stream_cupy_column_signature_3d"
    )
    point_count = (
        int(profile["rt_dbscan_parity_point_count"])
        if parity_companion
        else int(profile["rt_dbscan_point_count"])
    )
    repeat = 1 if parity_companion else int(profile["rt_dbscan_repeat"])
    warmup = 0 if parity_companion else int(profile["rt_dbscan_warmup"])
    command = [
        py,
        "examples/current/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py",
        "--mode",
        rt_mode,
        "--dataset",
        "clustered3d",
        "--point-count",
        str(point_count),
        "--radius",
        "3.0",
        "--min-neighbors",
        "4",
        "--partner",
        "numba" if version == "v4_current" else "cupy",
        "--repeat",
        str(repeat),
        "--warmup",
        str(warmup),
    ]
    if bool(profile.get("rt_dbscan_no_validation")) and not parity_companion:
        command.append("--no-validation")
    return command


def _commands(root: Path, version: str, profile: dict[str, Any], triangle_file: Path) -> dict[str, list[str]]:
    py = _python(root)
    triangle_mode = (
        "rt_graph_2a1_segmented_generic_rt"
        if version in {"v3_0_2", "v4_current"}
        else "rt_graph_2a1_generic_rt"
    )
    triangle_cmd = [
        py,
        "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
        "--mode",
        triangle_mode,
        "--edge-file",
        str(triangle_file),
        "--edge-format",
        "binary",
        "--backend",
        "optix",
        "--detail",
        "summary",
        "--partner",
        "cupy",
        "--warmup",
        str(profile["triangle_warmup"]),
        "--repeat",
        str(profile["triangle_repeat"]),
    ]
    if triangle_mode == "rt_graph_2a1_segmented_generic_rt":
        triangle_cmd.extend(
            [
                "--segment-ray-representation",
                "unique_weighted",
                "--segment-query-schedule",
                "prepared_segment_replay",
                "--validate-oracle",
            ]
        )
    return {
        "rt_dbscan": _rt_dbscan_command(root, version, profile),
        "raydb_style": [
            py,
            "examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py",
            "--mode",
            "sum",
            "--backend",
            "paper_rt_optix_prepared_grouped_reduction",
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
        ],
        "triangle_counting": triangle_cmd,
        "librts_spatial_index": [
            py,
            "examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py",
            "--mode",
            "optix_aabb_index",
            "--dataset",
            "uniform",
            "--operation",
            "all",
            "--box-count",
            str(profile["librts_boxes"]),
            "--query-count",
            str(profile["librts_queries"]),
            "--repeat",
            str(profile["librts_repeat"]),
            "--warmup",
            str(profile["librts_warmup"]),
            "--skip-counts",
        ],
    }


def _read_payload(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _first_number(*values: Any) -> float | None:
    for value in values:
        if isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) > 0:
            return float(value)
    return None


def _get_nested(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _extract_metrics(app: str, payload: dict[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "json_parse_ok": False,
            "correctness_parity": False,
            "primary_wall_sec": None,
            "hot_sec": None,
        }
    if app.startswith("rt_dbscan"):
        hot = _first_number(
            _get_nested(payload, ("metadata", "prepared_execution_session_runner_last_metadata", "measured_median_sec")),
            payload.get("elapsed_sec"),
        )
        return {
            "json_parse_ok": True,
            "correctness_parity": payload.get("matches_reference") is True,
            "primary_wall_sec": _first_number(payload.get("elapsed_sec"), hot),
            "hot_sec": hot,
            "route": payload.get("mode"),
            "point_count": payload.get("point_count"),
        }
    if app == "raydb_style":
        hot = _first_number(
            _get_nested(payload, ("metadata", "prepared_iteration_wall_summary", "median_sec")),
            _get_nested(payload, ("metadata", "timings", "native_call_wall")),
            payload.get("elapsed_sec"),
        )
        return {
            "json_parse_ok": True,
            "correctness_parity": payload.get("matches_cpu_reference") is True,
            "primary_wall_sec": _first_number(payload.get("elapsed_sec"), hot),
            "hot_sec": hot,
            "route": payload.get("backend"),
            "row_count": payload.get("row_count"),
        }
    if app == "triangle_counting":
        query_ms = _first_number(
            _get_nested(payload, ("timing_ms", "query_median_ms")),
            _get_nested(payload, ("phase_split_ms", "measured_replay_query_median_ms")),
        )
        hot = query_ms / 1000.0 if query_ms else None
        return {
            "json_parse_ok": True,
            "correctness_parity": payload.get("triangle_count_matches_oracle") is True,
            "primary_wall_sec": hot,
            "hot_sec": hot,
            "route": payload.get("mode"),
            "ray_count": payload.get("ray_count"),
            "logical_ray_count": payload.get("logical_ray_count"),
        }
    if app == "librts_spatial_index":
        hot = _first_number(
            _get_nested(payload, ("repeat_protocol", "query_sec_median")),
            _get_nested(payload, ("run_phases", "query_median_sec")),
            payload.get("elapsed_sec"),
        )
        return {
            "json_parse_ok": True,
            "correctness_parity": payload.get("matches_cpu_reference") is True or payload.get("cpu_reference_skipped") is True,
            "primary_wall_sec": _first_number(payload.get("elapsed_sec"), hot),
            "hot_sec": hot,
            "route": payload.get("mode"),
            "operation": payload.get("operation"),
        }
    return {"json_parse_ok": True, "correctness_parity": False, "primary_wall_sec": None, "hot_sec": None}


def _ratio(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return a / b


def _analyze(executions: list[dict[str, Any]], versions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = []
    by_app_version: dict[tuple[str, str], dict[str, Any]] = {}
    rt_dbscan_parity_by_version: dict[str, dict[str, Any]] = {}
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
    app_scorecard = []
    for app in APP_ORDER:
        v2 = by_app_version.get((app, "v2_14"), {})
        v3 = by_app_version.get((app, "v3_0_2"), {})
        v4 = by_app_version.get((app, "v4_current"), {})
        v2_sec = v2.get("payload_metrics", {}).get("hot_sec")
        v3_sec = v3.get("payload_metrics", {}).get("hot_sec")
        v4_sec = v4.get("payload_metrics", {}).get("hot_sec")
        def correctness_ok(version: str) -> bool:
            primary = by_app_version.get((app, version), {})
            if primary.get("payload_metrics", {}).get("correctness_parity") is True:
                return True
            if app == "rt_dbscan":
                companion = rt_dbscan_parity_by_version.get(version, {})
                return companion.get("payload_metrics", {}).get("correctness_parity") is True
            return False

        app_scorecard.append(
            {
                "app": app,
                "v2_14_hot_sec": v2_sec,
                "v3_0_2_hot_sec": v3_sec,
                "v4_hot_sec": v4_sec,
                "v4_vs_v2_14_hot_speedup": _ratio(v2_sec, v4_sec),
                "v4_vs_v3_0_2_hot_speedup": _ratio(v3_sec, v4_sec),
                "v3_0_2_vs_v2_14_hot_speedup": _ratio(v2_sec, v3_sec),
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
        )
    formal_native_purity = all(info["tag_native_optix_build"] for info in versions.values())
    return {
        "rows": rows,
        "app_scorecard": app_scorecard,
        "formal_tag_native_optix_purity": formal_native_purity,
        "formal_release_blocker": None
        if formal_native_purity
        else "v2_14/v3_0_2 OptiX libraries could not be built on this POD because OptiX SDK headers are absent; OptiX-dependent old-version rows use a declared V4 compatibility native library",
        "all_rows_returncode_zero": all(int(row["returncode"]) == 0 for row in rows),
        "all_rows_json_parse_ok": all(row["payload_metrics"]["json_parse_ok"] for row in rows),
        "all_full_rows_have_hot_metric": all(
            row["payload_metrics"].get("hot_sec") is not None for row in rows
        ),
    }


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4654 Full App-Level POD Benchmark",
        "",
        f"Status: `{summary['status']}`",
        f"Profile: `{summary['profile']}`",
        "",
        "```text",
        f"release_authorized: false",
        f"broad_v4_speed_claim_authorized: false",
        f"formal_tag_native_optix_purity: {summary['analysis']['formal_tag_native_optix_purity']}",
        f"formal_release_blocker: {summary['analysis']['formal_release_blocker']}",
        "```",
        "",
        "## App Scorecard",
        "",
        "| App | V4/V2.14 hot | V4/V3.0.2 hot | V3.0.2/V2.14 hot | RC OK | Parity |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary["analysis"]["app_scorecard"]:
        def fmt(value: Any) -> str:
            return "n/a" if value is None else f"{float(value):.3f}x"

        lines.append(
            f"| `{row['app']}` | {fmt(row['v4_vs_v2_14_hot_speedup'])} | "
            f"{fmt(row['v4_vs_v3_0_2_hot_speedup'])} | "
            f"{fmt(row['v3_0_2_vs_v2_14_hot_speedup'])} | "
            f"{row['all_returncode_zero']} | {row['all_correctness_parity_or_skipped_oracle']} |"
        )
    lines.extend(
        [
            "",
            "## Route And Provenance Notes",
            "",
            "- V2.14 and V3.0.2 source trees are clean tag archives from git.",
            "- V2.14 and V3.0.2 Embree libraries were built in their tag trees.",
            "- V2.14 and V3.0.2 OptiX native libraries could not be built on this POD because OptiX SDK headers are absent.",
            "- OptiX-dependent old-version rows therefore use a declared V4 compatibility native library; this blocks pure tag-native release authorization from Goal4654 alone.",
            "- This benchmark is still useful for app front-door/runtime route comparison, but Goal4655 must keep the provenance caveat visible.",
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
            "Goal4654 does not authorize public V4 release wording, whole-app speedup wording,",
            "or a formal high-performance V4 claim. Goal4655 must analyze these rows with",
            "the partner-migration and native-provenance locks intact.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4654 full app-level POD benchmark.")
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--output-dir", type=Path, default=Path("/root/v4_goal4654_full_app_level_pod_benchmark"))
    parser.add_argument("--timeout-sec", type=int, default=3600)
    args = parser.parse_args(argv)

    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    versions = _versions()
    _copy_compat_libraries(versions)
    profile = _profile_values(args.profile)

    fixture_env = _env_for(versions["v4_current"]["root"], tag_native_optix_build=True)
    triangle_fixture = _write_triangle_fixture(
        versions["v4_current"]["root"],
        out_dir / f"k4_{profile['triangle_k4_cliques']}.edgebin",
        int(profile["triangle_k4_cliques"]),
        _python(versions["v4_current"]["root"]),
        fixture_env,
    )

    executions: list[dict[str, Any]] = []
    for version, info in versions.items():
        root = info["root"]
        env = _env_for(root, tag_native_optix_build=bool(info["tag_native_optix_build"]))
        commands = _commands(root, version, profile, Path(triangle_fixture["path"]))
        for app in APP_ORDER:
            executions.append(
                _run_command(
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
                    _run_command(
                        version=version,
                        app="rt_dbscan_parity",
                        command=_rt_dbscan_command(root, version, profile, parity_companion=True),
                        cwd=root,
                        env=env,
                        out_dir=raw_dir,
                        timeout_sec=int(args.timeout_sec),
                    )
                )

    summary = {
        "schema": VERSION,
        "status": "goal4654_evidence_collected_not_release",
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
            "was_i_stupid": "No for building this runner; the stupid alternative was to publish operator-level evidence as app-level evidence.",
            "stupid_action_if_any": "The old-version OptiX compatibility library is explicitly labeled and cannot be used as pure tag-native release proof.",
            "alternative_path": "Block Goal4654 until a POD with OptiX SDK headers can rebuild v2.14 and v3.0.2 native OptiX libraries.",
            "different_path_now": "Collect app-level runtime evidence now with provenance visible, then let Goal4655 classify whether it is release-quality or blocked.",
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
