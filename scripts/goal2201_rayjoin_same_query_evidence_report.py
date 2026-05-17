from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ("lsi", "pip")
MODES = ("grid", "lbvh", "rt")
BLOCKED_CLAIM_KEYS = (
    "paper_scale_perf_claim_authorized",
    "rtdl_beats_rayjoin_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
    "v2_0_release_authorized",
)

TIMING_RE = re.compile(r"^\s*-\s*(?P<name>[^:]+):\s*(?P<value>[-+0-9.eE]+)\s*ms\s*$", re.MULTILINE)
INTERSECTIONS_RE = re.compile(r"Intersections:\s*(?P<count>[0-9]+)")
QUERY_COUNT_RE = re.compile(r"queries:\s*(?P<count>[0-9]+)")
MAP_CHECK_RE = re.compile(r"Map:\s*[0-9]+\s+passed check")


def _resolve(path: str | Path) -> Path:
    value = Path(path)
    if value.is_absolute():
        return value
    return ROOT / value


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _read_required_text(path: Path, *, kind: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"missing required {kind}: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def parse_rayjoin_log(path: Path) -> dict[str, Any]:
    text = _read_required_text(path, kind="RayJoin log")
    timing_ms = {
        match.group("name").strip(): float(match.group("value"))
        for match in TIMING_RE.finditer(text)
    }
    intersections = [int(match.group("count")) for match in INTERSECTIONS_RE.finditer(text)]
    query_counts = [int(match.group("count")) for match in QUERY_COUNT_RE.finditer(text)]
    return {
        "path": str(path),
        "exists": path.exists(),
        "timing_ms": timing_ms,
        "query_ms": timing_ms.get("Query"),
        "build_index_ms": timing_ms.get("Build Index"),
        "adaptive_grouping_ms": timing_ms.get("Adaptive Grouping"),
        "optix_launch_count": text.count("optixLaunch"),
        "intersections": intersections[-1] if intersections else None,
        "query_count_from_log": query_counts[-1] if query_counts else None,
        "built_in_check_passed": bool(MAP_CHECK_RE.search(text)),
    }


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def parse_rtdl_artifact(path: Path) -> dict[str, Any]:
    data = json.loads(_read_required_text(path, kind="RTDL same-stream artifact"))
    boundary = data.get("claim_boundary", {})
    for key in BLOCKED_CLAIM_KEYS:
        if boundary.get(key):
            raise ValueError(f"{path}: blocked claim key unexpectedly true: {key}")
    if data.get("query_stream_producer") != "rayjoin_query_exec_export_patch":
        raise ValueError(f"{path}: expected RayJoin-exported query stream")
    if not boundary.get("same_contract_with_rayjoin_query_exec"):
        raise ValueError(f"{path}: same_contract_with_rayjoin_query_exec is not true")

    backends: dict[str, Any] = {}
    for name, backend in data.get("backends", {}).items():
        elapsed_values = [float(value) for value in backend.get("elapsed_sec_values", [])]
        if not backend.get("all_parity_vs_cpu_python_reference"):
            raise ValueError(f"{path}: backend {name} failed parity")
        backends[name] = {
            "elapsed_sec_values": elapsed_values,
            "elapsed_sec_median": backend.get("elapsed_sec_median", _median(elapsed_values)),
            "row_counts": backend.get("row_counts", []),
            "all_parity_vs_cpu_python_reference": bool(backend.get("all_parity_vs_cpu_python_reference")),
            "rt_core_accelerated": bool(backend.get("rt_core_accelerated")),
        }

    return {
        "path": str(path),
        "workload": data["workload"],
        "query_count": int(data["query_count"]),
        "query_stream": data["query_stream"],
        "query_stream_producer": data["query_stream_producer"],
        "reference_row_count": int(data["reference_row_count"]),
        "backends": backends,
        "claim_boundary": boundary,
    }


def build_summary(artifact_dir: Path) -> dict[str, Any]:
    rayjoin: dict[str, dict[str, Any]] = {}
    rtdl: dict[str, Any] = {}
    for workload in WORKLOADS:
        rayjoin[workload] = {}
        for mode in MODES:
            rayjoin[workload][mode] = parse_rayjoin_log(artifact_dir / f"rayjoin_{workload}_{mode}.log")
        rtdl[workload] = parse_rtdl_artifact(artifact_dir / f"rtdl_{workload}_same_rayjoin_stream.json")

    derived: dict[str, Any] = {}
    for workload in WORKLOADS:
        rt_query_ms = rayjoin[workload]["rt"].get("query_ms")
        grid_query_ms = rayjoin[workload]["grid"].get("query_ms")
        lbvh_query_ms = rayjoin[workload]["lbvh"].get("query_ms")
        optix_sec = rtdl[workload]["backends"].get("optix", {}).get("elapsed_sec_median")
        embree_sec = rtdl[workload]["backends"].get("embree", {}).get("elapsed_sec_median")
        cpu_sec = rtdl[workload]["backends"].get("cpu", {}).get("elapsed_sec_median")
        derived[workload] = {
            "rayjoin_rt_vs_grid_query_ratio": (rt_query_ms / grid_query_ms) if rt_query_ms and grid_query_ms else None,
            "rayjoin_rt_vs_lbvh_query_ratio": (rt_query_ms / lbvh_query_ms) if rt_query_ms and lbvh_query_ms else None,
            "rtdl_optix_vs_cpu_ratio": (optix_sec / cpu_sec) if optix_sec and cpu_sec else None,
            "rtdl_optix_vs_embree_ratio": (optix_sec / embree_sec) if optix_sec and embree_sec else None,
            "rtdl_optix_sec": optix_sec,
            "rtdl_embree_sec": embree_sec,
            "rtdl_cpu_sec": cpu_sec,
        }

    return {
        "goal": "2201",
        "status": "parsed",
        "artifact_dir": str(artifact_dir),
        "rtdl_commit": _git_commit(),
        "rayjoin": rayjoin,
        "rtdl": rtdl,
        "derived": derived,
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": True,
            "paper_scale_perf_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }


def _fmt_ms(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6g}"


def _fmt_sec(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.6f}"


def _fmt_ratio(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.3f}x"


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Goal2201 RayJoin Same-Query Evidence Summary",
        "",
        "Status: generated from pod artifacts; claim boundaries remain locked unless a later reviewed report changes them.",
        "",
        "## Scope",
        "",
        "This report summarizes RayJoin-generated PIP/LSI query streams and RTDL replay over the same streams.",
        "It is not by itself a RayJoin paper reproduction or a v2.0 release authorization.",
        "",
        "## RayJoin Query Phase",
        "",
        "| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for workload in WORKLOADS:
        for mode in MODES:
            row = summary["rayjoin"][workload][mode]
            lines.append(
                "| "
                f"`{workload}` | `{mode}` | {_fmt_ms(row['query_ms'])} | "
                f"{_fmt_ms(row['build_index_ms'])} | {_fmt_ms(row['adaptive_grouping_ms'])} | "
                f"{row['optix_launch_count']} | {row['intersections'] if row['intersections'] is not None else 'n/a'} | "
                f"{'pass' if row['built_in_check_passed'] else 'n/a'} |"
            )

    lines.extend(
        [
            "",
            "## RTDL Same-Stream Replay",
            "",
            "| Workload | Query count | Reference rows | CPU sec | Embree sec | OptiX sec | OptiX/CPU | OptiX/Embree |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for workload in WORKLOADS:
        row = summary["rtdl"][workload]
        derived = summary["derived"][workload]
        lines.append(
            "| "
            f"`{workload}` | {row['query_count']} | {row['reference_row_count']} | "
            f"{_fmt_sec(derived['rtdl_cpu_sec'])} | {_fmt_sec(derived['rtdl_embree_sec'])} | "
            f"{_fmt_sec(derived['rtdl_optix_sec'])} | {_fmt_ratio(derived['rtdl_optix_vs_cpu_ratio'])} | "
            f"{_fmt_ratio(derived['rtdl_optix_vs_embree_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The summary keeps these claims unauthorized:",
            "",
            "- paper-scale RayJoin reproduction",
            "- RTDL beats RayJoin",
            "- broad RT-core speedup",
            "- v2.0 release readiness",
            "",
            "A stronger public performance claim needs the raw artifacts, external review, and a separate consensus report.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Goal2198 RayJoin same-query pod artifacts.")
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args(argv)

    artifact_dir = _resolve(args.artifact_dir)
    summary = build_summary(artifact_dir)

    output_json = _resolve(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    output_md = _resolve(args.output_md)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_markdown(summary), encoding="utf-8")

    print(f"[goal2201] wrote {output_json}")
    print(f"[goal2201] wrote {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
