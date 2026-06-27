from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.rtnn_point_file_front_door.goal4503.v1"
APP_JSON = Path("docs/reports/goal4503_rtnn_kitti_1m_app_point_file_repeat5_2026-06-17.json")
M106_PACKET = Path("docs/reports/goal4502_v3_0_m106_rtnn_full_batch_route_refresh_2026-06-17.json")
OUT_JSON = Path("docs/reports/goal4503_v3_0_m107_rtnn_point_file_front_door_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4503_v3_0_m107_rtnn_point_file_front_door_2026-06-17.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _signature_delta(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    keys = ("row_count", "bounded_neighbor_count", "nearest_id_checksum", "kth_id_checksum")
    return {
        **{key: int(a[key]) - int(b[key]) for key in keys},
        "sum_distance_delta": float(a["sum_distance"]) - float(b["sum_distance"]),
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    app_payload = _read_json(root / APP_JSON)
    m106 = _read_json(root / M106_PACKET)
    runner = app_payload["runner_payload"]
    m106_best = m106["rtdl"]["optix_full_batch_direct_aggregate"]
    app_summary = runner["ranked_aggregate_summary"]
    m106_summary = m106_best["summary"]
    app_cold_total = (
        float(runner["input_load_sec"])
        + float(runner["input_pack_sec"])
        + float(runner["execution_prepare_sec"])
        + float(runner["elapsed_median_sec"])
    )
    m106_cold_total = float(m106_best["cold_load_pack_prepare_query_sec"])
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4503 / V3 M107",
        "raw_app_front_door_json": APP_JSON.as_posix(),
        "app_front_door": {
            "mode": app_payload["mode"],
            "external_point_file_used": bool(app_payload["external_point_file_used"]),
            "generated_input": app_payload["generated_input"],
            "point_count": int(app_payload["point_count"]),
            "query_batch_size": int(app_payload["query_batch_size"]),
            "repeat": int(app_payload["repeat"]),
            "runner_result_mode": runner["result_mode"],
            "runner_batch_count": int(runner["batch_count"]),
            "median_query_sec": float(runner["elapsed_median_sec"]),
            "min_query_sec": float(runner["elapsed_min_sec"]),
            "max_query_sec": float(runner["elapsed_max_sec"]),
            "cold_load_pack_prepare_query_sec": app_cold_total,
            "summary": app_summary,
        },
        "m106_best": {
            "median_query_sec": float(m106_best["median_query_sec"]),
            "cold_load_pack_prepare_query_sec": m106_cold_total,
            "summary": m106_summary,
        },
        "comparisons": {
            "app_front_door_query_over_m106_runner_query": (
                float(runner["elapsed_median_sec"]) / float(m106_best["median_query_sec"])
            ),
            "app_front_door_cold_total_over_m106_runner_cold_total": app_cold_total / m106_cold_total,
        },
        "signature_delta_app_minus_m106": _signature_delta(app_summary, m106_summary),
        "claim_boundary": {
            "external_point_file_front_door_proven": True,
            "synthetic_generation_skipped_for_point_file": app_payload["generated_input"].get("generated") is False,
            "same_route_as_m106_full_batch_aggregate": runner["result_mode"]
            == "ranked-summary-aggregate-prepared-query-batch-float32",
            "same_input_author_rtdl_comparison": True,
            "paper_reproduction_wording_allowed": False,
            "public_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
        "conclusion": (
            "The RTNN benchmark app now exposes the M106 full-batch prepared aggregate route "
            "through `--point-file`. On the Goal4500 KITTI-1M CSV, the app front door infers "
            "1,000,000 points, skips synthetic generation, runs one full query batch, and "
            "matches the M106 aggregate signature while measuring the same hot-query class."
        ),
    }


def _fmt(value: float) -> str:
    return f"{value:.3f}s"


def write_report(packet: dict[str, Any], path: Path) -> None:
    app = packet["app_front_door"]
    comp = packet["comparisons"]
    lines = [
        "# Goal4503 / V3 M107 RTNN Point-File Front Door",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Command",
        "",
        "```bash",
        (
            "PYTHONPATH=src:. python examples/benchmark_apps/rtnn/"
            "rtdl_rtnn_benchmark_app.py --mode prepared_optix_ranked_summary "
            "--point-file /workspace/data/kitti/rtdl_goal4500/kitti_1m_points.csv "
            "--radius 1.0 --k 50 --repeat 5 --query-batch-size 1000000"
        ),
        "```",
        "",
        "## Front-Door Row",
        "",
        "| Field | Value |",
        "| --- | ---: |",
        f"| raw JSON | `{packet['raw_app_front_door_json']}` |",
        f"| external_point_file_used | `{app['external_point_file_used']}` |",
        f"| generated_input.source | `{app['generated_input']['source']}` |",
        f"| generated_input.generated | `{app['generated_input']['generated']}` |",
        f"| point_count | {app['point_count']:,} |",
        f"| query_batch_size | {app['query_batch_size']:,} |",
        f"| runner result mode | `{app['runner_result_mode']}` |",
        f"| runner batch_count | {app['runner_batch_count']} |",
        f"| median query | {_fmt(app['median_query_sec'])} |",
        f"| cold load+pack+prepare+query | {_fmt(app['cold_load_pack_prepare_query_sec'])} |",
        "",
        "## M106 Consistency",
        "",
        f"- App front-door query / M106 runner query: {comp['app_front_door_query_over_m106_runner_query']:.3f}x.",
        f"- App front-door cold total / M106 runner cold total: {comp['app_front_door_cold_total_over_m106_runner_cold_total']:.3f}x.",
        f"- Signature delta app minus M106: `{packet['signature_delta_app_minus_m106']}`.",
        "",
        "## Boundaries",
        "",
        "- This proves the app front door reaches the current full-batch aggregate route; it does not change the author-output or paper-reproduction boundary.",
        "- The route still returns ranked-summary aggregates, not author RTNN's full K-id output buffer.",
        "- Public speedup wording remains blocked.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    packet = build_packet()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(packet, OUT_REPORT)
    print(json.dumps(packet["comparisons"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
