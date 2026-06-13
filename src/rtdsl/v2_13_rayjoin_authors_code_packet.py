from __future__ import annotations

import json
from pathlib import Path
from typing import Any


V2_13_RAYJOIN_AUTHORS_CODE_PACKET_VERSION = (
    "rtdl.v2_13.rayjoin_authors_code_packet.goal4367.v1"
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAYJOIN_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal4358_rtx_a4000_v2_12_rayjoin_same_stream_2026-06-13"
    / "summary.json"
)


ARTIFACT_MANIFEST: tuple[dict[str, Any], ...] = (
    {
        "name": "rayjoin_lsi_gen100000_stream.json",
        "role": "RayJoin-exported LSI query stream consumed by RTDL",
        "bytes": 12629271,
        "sha256": "6bed3890d327cbd7f33c6fb3c14b306484aa9f1ccca001710ec164f4d03671bd",
    },
    {
        "name": "rayjoin_pip_gen100000_stream.json",
        "role": "RayJoin-exported PIP query stream consumed by RTDL",
        "bytes": 7059404,
        "sha256": "d5ba3289e346febf86492d2f5d7abdab1a14977a5b6518fc813fd665a90b63a0",
    },
    {
        "name": "rayjoin_lsi_grid.log",
        "role": "RayJoin original LSI grid-mode timing log",
        "bytes": 1190,
        "sha256": "ccebf3404481cb85e9aacf7db966b2501c8215acd25d8a51a627a4e5efab470b",
    },
    {
        "name": "rayjoin_lsi_lbvh.log",
        "role": "RayJoin original LSI LBVH-mode timing log",
        "bytes": 1190,
        "sha256": "9820ba846993571780398814349499d17005651b52a8662fcb8ce4e94f67426e",
    },
    {
        "name": "rayjoin_lsi_rt.log",
        "role": "RayJoin original LSI RT-mode timing log",
        "bytes": 2235,
        "sha256": "32a333baf2e19c7dd18d9f29a0af6b3f238df49ec480273f85a4e4cd70764889",
    },
    {
        "name": "rayjoin_pip_grid.log",
        "role": "RayJoin original PIP grid-mode timing log",
        "bytes": 675,
        "sha256": "f738fb717a05d0dca81440279d173deaa18929d22fe8c8e5c75111b8aabfb274",
    },
    {
        "name": "rayjoin_pip_lbvh.log",
        "role": "RayJoin original PIP LBVH-mode timing log",
        "bytes": 841,
        "sha256": "0f6fe2c1ff4249fd0835c68436cfadd90e940f874428f62a81ee409bfb430e60",
    },
    {
        "name": "rayjoin_pip_rt.log",
        "role": "RayJoin original PIP RT-mode timing log",
        "bytes": 1519,
        "sha256": "38a6ce23cbfd41bc5d0dcba781da2ca658d62f95c0262cb08c8a40e2a458af84",
    },
    {
        "name": "rtdl_lsi_same_rayjoin_stream.json",
        "role": "RTDL LSI same-stream scalar-count result",
        "bytes": 3051,
        "sha256": "0b46cf3145aee850c5ca89d609f0ffd32ec94193cc7c8bf57e73b7e6855009d6",
    },
    {
        "name": "rtdl_pip_same_rayjoin_stream.json",
        "role": "RTDL PIP same-stream scalar-count result",
        "bytes": 3123,
        "sha256": "e61dff24e56a62a9cb49e23e5d5c53213a0eeea0ec19914589f7488a73237ad7",
    },
    {
        "name": "summary.json",
        "role": "Compact goal4358 summary retained outside the source tree artifact dir",
        "bytes": 6951,
        "sha256": "9ed49df8d27ce759b8480c96df863fb683b612ec6c05dc9f764fd453133a8695",
    },
    {
        "name": "goal4354_lsi_pip100k_exact_prepared_points_rtx_a4000_summary_after_embree_lsi_no_bruteforce.json",
        "role": "Full same-stream summary after Embree LSI no-bruteforce repair",
        "bytes": 27926,
        "sha256": "f4bb3c96848c4d467362f688a3c12c8a7eb904fec5e972c52bddd5dd8007f584",
    },
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_absolute() else str(path)


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _rayjoin_log_rows(summary: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for workload in ("lsi", "pip"):
        for mode in ("grid", "lbvh", "rt"):
            log = summary["rayjoin"][workload][mode]
            correctness = "n/a"
            if workload == "lsi" and log.get("intersections") is not None:
                correctness = f"intersections={int(log['intersections'])}"
            if workload == "pip" and log.get("built_in_check_passed"):
                correctness = "built_in_check=True"
            rows.append(
                {
                    "workload": workload,
                    "mode": mode,
                    "query_ms": _round(log.get("query_ms")),
                    "build_index_ms": _round(log.get("build_index_ms")),
                    "adaptive_grouping_ms": _round(log.get("adaptive_grouping_ms")),
                    "optix_launch_count": int(log.get("optix_launch_count") or 0),
                    "correctness_signal": correctness,
                }
            )
    return tuple(rows)


def _rtdl_rows(summary: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for workload in ("lsi", "pip"):
        for backend in ("optix", "embree"):
            result = summary["rtdl"][workload]["backends"][backend]
            rows.append(
                {
                    "workload": workload,
                    "backend": backend,
                    "hot_query_ms": _round(float(result["hot_median_sec"]) * 1000.0),
                    "count": int(result["row_count"]),
                    "route": result["execution_route"],
                    "rt_core_accelerated": bool(result["rt_core_accelerated"]),
                    "row_stream_materialized": bool(result["row_stream_materialized"]),
                }
            )
    return tuple(rows)


def _comparison_rows(summary: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for row in summary["comparisons"]:
        rayjoin_over_rtdl = float(row["rayjoin_rt_over_rtdl"])
        if rayjoin_over_rtdl >= 1.0:
            readout = "RTDL backend faster than RayJoin RT for this scalar-count contract"
            reciprocal = None
        else:
            readout = "RayJoin RT faster than RTDL backend for this scalar-count contract"
            reciprocal = 1.0 / rayjoin_over_rtdl
        rows.append(
            {
                "workload": row["workload"],
                "rtdl_backend": row["backend"],
                "rayjoin_rt_query_ms": _round(row["rayjoin_rt_query_ms"]),
                "rtdl_hot_query_ms": _round(row["rtdl_hot_query_ms"]),
                "rayjoin_rt_over_rtdl": _round(rayjoin_over_rtdl, 3),
                "rayjoin_rt_faster_than_rtdl": _round(reciprocal, 2),
                "direction": "greater_than_1_means_rtdl_backend_faster_than_rayjoin_rt",
                "readout": readout,
            }
        )
    return tuple(rows)


def v2_13_rayjoin_authors_code_packet(
    *,
    rayjoin_summary_path: Path | None = None,
) -> dict[str, Any]:
    summary_path = rayjoin_summary_path or DEFAULT_RAYJOIN_SUMMARY
    summary = _load_json(summary_path)
    log_rows = _rayjoin_log_rows(summary)
    rtdl_rows = _rtdl_rows(summary)
    comparison_rows = _comparison_rows(summary)

    by_workload_backend = {
        (row["workload"], row["rtdl_backend"]): row for row in comparison_rows
    }
    lsi_optix = by_workload_backend[("lsi", "optix")]
    pip_optix = by_workload_backend[("pip", "optix")]
    manifest_by_name = {row["name"]: row for row in ARTIFACT_MANIFEST}

    errors: list[str] = []
    required_artifacts = (
        "rayjoin_lsi_gen100000_stream.json",
        "rayjoin_pip_gen100000_stream.json",
        "rayjoin_lsi_rt.log",
        "rayjoin_pip_rt.log",
        "rtdl_lsi_same_rayjoin_stream.json",
        "rtdl_pip_same_rayjoin_stream.json",
    )
    for artifact in required_artifacts:
        if artifact not in manifest_by_name:
            errors.append(f"missing artifact manifest row: {artifact}")
        elif len(str(manifest_by_name[artifact]["sha256"])) != 64:
            errors.append(f"artifact hash is not sha256-shaped: {artifact}")
    if not summary["claim_boundary"]["same_query_stream_with_rayjoin_query_exec"]:
        errors.append("same-query-stream flag is not true")
    if summary["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"]:
        errors.append("packet must not authorize broad RTDL-beats-RayJoin wording")
    if float(lsi_optix["rayjoin_rt_over_rtdl"]) <= 1.0:
        errors.append("LSI OptiX row should show RTDL faster than RayJoin RT for scalar count")
    if float(pip_optix["rayjoin_rt_over_rtdl"]) >= 0.1:
        errors.append("PIP OptiX row should remain a visible RayJoin RT win")
    if not summary["rtdl"]["lsi"]["correctness"]["rtdl_matches_rayjoin_rt_intersections"]:
        errors.append("LSI RTDL count must match RayJoin RT intersections")
    if not summary["rtdl"]["pip"]["correctness"]["cross_backend_counts_match"]:
        errors.append("PIP RTDL OptiX and Embree counts must match")
    if not summary["rtdl"]["pip"]["correctness"]["rayjoin_rt_builtin_check_passed"]:
        errors.append("PIP RayJoin RT built-in check must pass")

    return {
        "version": V2_13_RAYJOIN_AUTHORS_CODE_PACKET_VERSION,
        "status": "accepted_internal_authors_code_comparison_packet" if not errors else "rejected_packet",
        "source_artifacts": {
            "retained_summary": _relative(summary_path),
            "raw_pod_artifact_dir": "/workspace/goal4358_rayjoin_same_stream_rtx_a4000/artifacts",
            "rayjoin_source": summary["protocol"]["rayjoin_source"],
        },
        "hardware": summary["hardware"],
        "protocol": {
            "dataset_basis": summary["protocol"]["dataset_basis"],
            "query_basis": summary["protocol"]["query_basis"],
            "timed_metric": summary["protocol"]["timed_metric"],
            "rayjoin_timing_basis": summary["protocol"]["rayjoin_timing_basis"],
            "rtdl_timing_basis": summary["protocol"]["rtdl_timing_basis"],
            "repeats": int(summary["protocol"]["repeats"]),
            "warmups": int(summary["protocol"]["warmups"]),
        },
        "artifact_manifest": ARTIFACT_MANIFEST,
        "rayjoin_original_logs": log_rows,
        "rtdl_same_stream_results": rtdl_rows,
        "direct_comparison": comparison_rows,
        "interpretation": {
            "lsi": (
                "Reasonable strong RTDL result: the RTDL OptiX route is an exact prepared-left "
                "segment-pair scalar count on the same stream, counts match RayJoin RT intersections, "
                "and no row stream is materialized in the measured RTDL path."
            ),
            "pip": (
                "Reasonable but not good enough for RTDL: RayJoin RT remains much faster on PIP "
                "because the current RTDL exact prepared-points path spends material time in exact "
                "membership refinement and generic orchestration. This is a v2.13 optimization debt, "
                "not a public RTDL win."
            ),
        },
        "claim_boundary": {
            "same_query_stream_with_rayjoin_query_exec": True,
            "scalar_count_contract_only": True,
            "full_rayjoin_paper_reproduction": False,
            "whole_application_end_to_end_claim": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "validation": {
            "status": "accept" if not errors else "reject",
            "errors": tuple(errors),
        },
    }


def _fmt(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.3f}".rstrip("0").rstrip(".")


def _fmt_ratio(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    return f"{_fmt(value)}x"


def markdown_v2_13_rayjoin_authors_code_packet(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal4367 RayJoin Authors-Code Comparison Packet",
        "",
        "Status: accepted internal comparison packet; not RayJoin paper reproduction and not broad public speedup wording.",
        "",
        "## Direction Rule",
        "",
        (
            "For the direct comparison table, `RayJoin RT / RTDL` greater than 1 means the RTDL backend "
            "is faster than RayJoin RT for the same scalar-count contract. Values below 1 mean RayJoin RT is faster."
        ),
        "",
        "## Artifact Manifest",
        "",
        "| Artifact | Role | Bytes | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for artifact in payload["artifact_manifest"]:
        lines.append(
            f"| `{artifact['name']}` | {artifact['role']} | {artifact['bytes']} | `{artifact['sha256']}` |"
        )

    lines.extend(
        [
            "",
            "## RayJoin Original Logs",
            "",
            "| Workload | Mode | Query ms | Build/index ms | Adaptive grouping ms | OptiX launches | Correctness signal |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["rayjoin_original_logs"]:
        lines.append(
            "| `{workload}` | `{mode}` | {query} | {build} | {adaptive} | {launches} | {correctness} |".format(
                workload=row["workload"],
                mode=row["mode"],
                query=_fmt(row["query_ms"]),
                build=_fmt(row["build_index_ms"]),
                adaptive=_fmt(row["adaptive_grouping_ms"]),
                launches=row["optix_launch_count"],
                correctness=row["correctness_signal"],
            )
        )

    lines.extend(
        [
            "",
            "## RTDL Same-Stream Results",
            "",
            "| Workload | Backend | Hot query ms | Count | Route | RT-core accelerated | Row stream materialized |",
            "| --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in payload["rtdl_same_stream_results"]:
        lines.append(
            "| `{workload}` | `{backend}` | {hot} | {count} | `{route}` | `{rt}` | `{materialized}` |".format(
                workload=row["workload"],
                backend=row["backend"],
                hot=_fmt(row["hot_query_ms"]),
                count=row["count"],
                route=row["route"],
                rt=row["rt_core_accelerated"],
                materialized=row["row_stream_materialized"],
            )
        )

    lines.extend(
        [
            "",
            "## Direct Comparison",
            "",
            "| Workload | RTDL backend | RayJoin RT query ms | RTDL hot query ms | RayJoin RT / RTDL | Reciprocal when RayJoin is faster | Readout |",
            "| --- | --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["direct_comparison"]:
        lines.append(
            "| `{workload}` | `{backend}` | {rayjoin} | {rtdl} | {ratio} | {reciprocal} | {readout} |".format(
                workload=row["workload"],
                backend=row["rtdl_backend"],
                rayjoin=_fmt(row["rayjoin_rt_query_ms"]),
                rtdl=_fmt(row["rtdl_hot_query_ms"]),
                ratio=_fmt_ratio(row["rayjoin_rt_over_rtdl"]),
                reciprocal=_fmt_ratio(row["rayjoin_rt_faster_than_rtdl"]),
                readout=row["readout"],
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- LSI: {payload['interpretation']['lsi']}",
            f"- PIP: {payload['interpretation']['pip']}",
            "",
            "## Claim Boundary",
            "",
            (
                "This packet compares RayJoin authors-code logs with RTDL same-stream scalar-count "
                "results. It does not authorize full RayJoin paper reproduction, whole-application "
                "speedup wording, public RTDL-beats-RayJoin wording, or broad RT-core claims."
            ),
            "",
            f"Validation status: `{payload['validation']['status']}`.",
        ]
    )
    return "\n".join(lines) + "\n"
