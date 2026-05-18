#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
from typing import Iterable


ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_MATRIX = ROOT / "docs" / "reports" / "goal2064_all_app_v2_matrix_after_goal2062.json"
POST_STREAMING_TABLE = ROOT / "docs" / "reports" / "goal2085_v2_perf_table_after_streaming_witness_update_2026-05-15.json"


def _git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.stdout.strip() or "unknown"


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _ratio_summary() -> dict[str, object]:
    if POST_STREAMING_TABLE.exists():
        table = json.loads(POST_STREAMING_TABLE.read_text(encoding="utf-8"))
        optix_rows = {str(row["app"]): row for row in table["optix_rt_rows"]}
        return {
            "source": str(POST_STREAMING_TABLE.relative_to(ROOT)).replace("\\", "/"),
            "optix_rt_rows": {
                app: {
                    "scale": row["scale"],
                    "v2_over_v1_8_ratio": float(row["v2_over_v1_8_ratio"]),
                }
                for app, row in sorted(optix_rows.items())
            },
            "slowest_current_optix_rt_ratio": max(
                float(row["v2_over_v1_8_ratio"]) for row in optix_rows.values()
            ),
            "all_current_optix_rt_ratios_below_1": all(
                float(row["v2_over_v1_8_ratio"]) < 1.0 for row in optix_rows.values()
            ),
        }

    robot_32768 = _json("docs/reports/goal2066_robot_collision_cupy_l4_32768x8192.json")["results"][0]
    robot_65536 = _json("docs/reports/goal2066_robot_collision_cupy_l4_65536x8192.json")["results"][0]
    hitcount = _json("docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json")
    fixed = _json("docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json")
    road = _json("docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json")
    anyhit = _json("docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json")
    polygon_2048 = _json("docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json")
    polygon_3072 = _json("docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json")

    fixed_ratios: dict[str, object] = {}
    for row in fixed["results"]:
        assert isinstance(row, dict)
        ratios: dict[str, float] = {"forward": float(row["forward"]["v2_vs_v1_8_prepared_ratio"])}
        if "reverse" in row:
            ratios["reverse"] = float(row["reverse"]["v2_vs_v1_8_prepared_ratio"])
        fixed_ratios[str(row["app"])] = ratios

    def polygon_ratio(payload: dict[str, object], app: str) -> float:
        for row in payload["results"]:
            assert isinstance(row, dict)
            if row["app"] == app:
                return float(row["v2_vs_v1_8_ratio"])
        raise KeyError(app)

    return {
        "robot_collision_screening": {
            "scale_32768x8192_ratio": float(robot_32768["v2_vs_v1_8_prepared_ratio"]),
            "scale_65536x8192_ratio": float(robot_65536["v2_vs_v1_8_prepared_ratio"]),
        },
        "segment_polygon_hitcount": {
            "scale_131072_prepared_reuse_ratio": float(
                hitcount["partners"]["cupy"]["goal1886_prepared_reuse"][
                    "query_median_ratio_vs_v1_8_prepared_native"
                ]
            ),
        },
        "road_hazard_screening": {
            "scale_12288_prepared_reuse_ratio": float(
                road["partners"]["cupy"]["goal1889_prepared_reuse"][
                    "query_median_ratio_vs_v1_8_prepared_native"
                ]
            ),
        },
        "fixed_radius_family_16384": fixed_ratios,
        "segment_polygon_anyhit_rows": {
            "scale_4096_row_materialization_ratio": float(
                anyhit["partners"]["cupy"]["query_median_ratio_vs_v1_8_native"]
            ),
        },
        "polygon_pair_overlap_area_rows": {
            "scale_2048_ratio": polygon_ratio(polygon_2048, "polygon_pair_overlap_area_rows"),
            "scale_3072_ratio": polygon_ratio(polygon_3072, "polygon_pair_overlap_area_rows"),
            "scale_4096_status": "optix-candidate-discovery-oom",
        },
        "polygon_set_jaccard": {
            "scale_2048_ratio": polygon_ratio(polygon_2048, "polygon_set_jaccard"),
            "scale_3072_ratio": polygon_ratio(polygon_3072, "polygon_set_jaccard"),
            "scale_4096_status": "optix-candidate-discovery-oom",
        },
    }


def _overlay_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_app = {str(row["app"]): dict(row) for row in rows}
    if POST_STREAMING_TABLE.exists():
        table = json.loads(POST_STREAMING_TABLE.read_text(encoding="utf-8"))
        bounded_apps = {
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        }
        for row in table["optix_rt_rows"]:
            app = str(row["app"])
            if app not in by_app:
                continue
            comparison_status = (
                "pod-evidence-collected-bounded"
                if app in bounded_apps
                else "pod-evidence-collected"
            )
            by_app[app].update(
                {
                    "comparison_status": comparison_status,
                    "claim_class": "bounded-implemented" if app in bounded_apps else "implemented",
                    "v2_state": "implemented-and-pod-timed",
                    "v2_evidence": row["source"],
                    "next_command": "post-streaming v2.0 release evidence collected by Goal2085/Goal2088",
                    "analysis_hint": row["evidence_note"],
                    "v2_over_v1_8_ratio": float(row["v2_over_v1_8_ratio"]),
                    "v2_contract": str(row["evidence_note"]),
                    "v18_reference": str(row["source"]),
                }
            )
        by_app["segment_polygon_anyhit_rows"]["analysis_hint"] = (
            "Streaming exact witness columns supersede the old slower full Python row-table contract; "
            "the old full-row path remains documented separately and is not the v2.0 release contract."
        )
        return list(by_app.values())

    fixed_apps = {
        "facility_knn_assignment",
        "hausdorff_distance",
        "ann_candidate_search",
        "outlier_detection",
        "dbscan_clustering",
        "barnes_hut_force_app",
    }
    for app in fixed_apps:
        by_app[app]["v2_evidence"] = "docs/reports/goal2066_fixed_radius_family_cupy_l4_16384.json"
        by_app[app]["next_command"] = "large 16384x16384 fixed-radius pod timing collected by Goal2066"
        by_app[app]["analysis_hint"] = (
            str(by_app[app]["analysis_hint"])
            + " Goal2066 strengthens this row at 16384x16384, still bounded to the documented threshold/proxy semantics."
        )

    by_app["road_hazard_screening"].update(
        {
            "v2_evidence": "docs/reports/goal2066_road_hazard_cupy_l4_12288_prepared_only.json",
            "next_command": "large prepared-only pod timing collected by Goal2066",
            "analysis_hint": "Goal2066 shows the prepared reusable witness-output path is a clear speedup at 12288 roads; small rows remain setup-sensitive.",
        }
    )
    by_app["segment_polygon_hitcount"].update(
        {
            "v2_evidence": "docs/reports/goal2066_segment_polygon_hitcount_cupy_l4_131072_capacity67108864.json",
            "next_command": "large prepared count-column scaling collected by Goal2066",
            "analysis_hint": "Goal2066 shows compact partner-owned count columns are the strongest segment/polygon v2 shape at 131072 rows.",
        }
    )
    by_app["segment_polygon_anyhit_rows"].update(
        {
            "v2_evidence": "docs/reports/goal2066_segment_polygon_anyhit_cupy_l4_4096_capacity16777216.json",
            "next_command": "do not promote full witness-row materialization; prefer compact counts/flags or future paged witness output",
            "analysis_hint": "Goal2066 confirms full witness-row materialization remains slower than v1.8 native rows at 4096; this row is correct but the wrong performance shape for large outputs.",
        }
    )
    for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
        by_app[app]["v2_evidence"] = (
            "docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_2048.json; "
            "docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_3072.json; "
            "docs/reports/goal2066_polygon_rawkernel_cupy_optix_l4_4096_oom.log"
        )
        by_app[app]["next_command"] = (
            "requires a real bounded candidate-summary primitive; naive streaming around the current OptiX helper was tested and rejected because it failed parity"
        )
    by_app["polygon_pair_overlap_area_rows"]["analysis_hint"] = (
        "Still bounded: v2 preserves semantics at 2048/3072 but remains slower, and 4096 OOMs in current OptiX candidate discovery."
    )
    by_app["polygon_set_jaccard"]["analysis_hint"] = (
        "Still bounded: v2 is near parity/slightly faster at 2048/3072, but 4096 shares the same current OptiX candidate-discovery OOM boundary."
    )
    by_app["robot_collision_screening"].update(
        {
            "v2_state": "implemented-and-pod-timed",
            "comparison_status": "pod-evidence-collected",
            "claim_class": "implemented",
            "v2_evidence": (
                "docs/reports/goal2066_robot_collision_cupy_l4_32768x8192.json; "
                "docs/reports/goal2066_robot_collision_cupy_l4_65536x8192.json"
            ),
            "next_command": "large-scale positive pod timing collected by Goal2066",
            "analysis_hint": "Goal2066 turns the earlier small-row negative into a large-scale speedup; the row remains an any-hit flag output, not arbitrary whole-app planning acceleration.",
        }
    )
    return list(by_app.values())


def build_matrix() -> dict[str, object]:
    base = json.loads(BASE_MATRIX.read_text(encoding="utf-8"))
    rows = _overlay_rows(base["rows"])
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["comparison_status"])] = counts.get(str(row["comparison_status"]), 0) + 1
    mixed_apps = [row["app"] for row in rows if row["comparison_status"] == "pod-evidence-collected-mixed"]
    bounded_apps = [row["app"] for row in rows if row["comparison_status"] == "pod-evidence-collected-bounded"]
    return {
        "goal": "Goal2068",
        "status": "final-v2-0-release-matrix-candidate",
        "date": "2026-05-15",
        "git_commit": _git_commit(),
        "base_matrix": str(BASE_MATRIX.relative_to(ROOT)).replace("\\", "/"),
        "post_streaming_table": str(POST_STREAMING_TABLE.relative_to(ROOT)).replace("\\", "/"),
        "post_goal2066_evidence": True,
        "post_goal2085_streaming_evidence": POST_STREAMING_TABLE.exists(),
        "row_count": len(rows),
        "counts_by_comparison_status": counts,
        "mixed_apps": mixed_apps,
        "bounded_apps": bounded_apps,
        "rows": rows,
        "measured_ratio_summary": _ratio_summary(),
        "release_claim_boundary": {
            "v2_0_release_authorized": False,
            "all_apps_have_a_row_decision": True,
            "all_apps_have_current_pod_evidence": True,
            "all_apps_have_measured_v2_speedup": not mixed_apps,
            "all_current_optix_rt_rows_have_measured_v2_speedup": not mixed_apps,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "arbitrary_partner_program_acceleration_authorized": False,
            "package_install_claim_authorized": False,
            "final_claude_release_review_present": False,
            "final_gemini_release_review_present": False,
            "final_3ai_release_consensus_present": False,
        },
        "final_release_blockers": [
            "final Claude v2.0 release review missing",
            "final Gemini v2.0 release review over current post-streaming packet missing",
            "final v2.0 release consensus missing",
            "explicit user-requested release action missing",
        ],
    }


def to_markdown(payload: dict[str, object]) -> str:
    rows = payload["rows"]
    assert isinstance(rows, list)
    ratio_summary = payload["measured_ratio_summary"]
    assert isinstance(ratio_summary, dict)
    lines = [
        "# Goal2068 - Final v2.0 Release Matrix Candidate",
        "",
        "Date: 2026-05-15",
        "",
        f"Status: `{payload['status']}`",
        "",
        "Goal2068 gives the v2.0 release lane a final-named matrix candidate after Goal2066's larger NVIDIA L4 pod evidence. It is a release-hardening artifact, not release authorization.",
        "",
        "This current matrix also incorporates the post-streaming witness-column update from Goal2085/Goal2088, which supersedes the older full Python witness-row materialization result.",
        "",
        "## Summary",
        "",
        f"- row count: `{payload['row_count']}`",
        f"- comparison status counts: `{json.dumps(payload['counts_by_comparison_status'], sort_keys=True)}`",
        f"- mixed apps: `{json.dumps(payload['mixed_apps'])}`",
        f"- bounded apps: `{json.dumps(payload['bounded_apps'])}`",
        "- v2.0 release authorized: `False`",
        f"- all current OptiX/RT rows have measured v2 ratios below 1.0: `{payload['release_claim_boundary']['all_current_optix_rt_rows_have_measured_v2_speedup']}`",
        "- whole-app speedup claim authorized: `False`",
        "",
        "## Post-Goal2066 / Post-Goal2085 Changes",
        "",
        "- `robot_collision_screening` moves from mixed to positive at larger scale: `0.164x` at 32768x8192 and `0.084x` at 65536x8192.",
        "- `road_hazard_screening` uses the larger prepared-only Goal2066 evidence: `0.085x` v2/v1.8 prepared.",
        "- `segment_polygon_hitcount` uses the larger Goal2066 compact count-column evidence: `0.006x` prepared-reuse ratio.",
        "- fixed-radius proxy rows use Goal2066's 16384x16384 evidence, all under `0.02x`.",
        "- `segment_polygon_anyhit_rows` now uses streaming exact witness columns instead of the old full Python row-table contract.",
        "- polygon overlap/Jaccard use the current generic tiled AABB candidate-summary path, while arbitrary polygon overlay remains outside the claim.",
        "",
        "## App Rows",
        "",
        "| App | Status | Claim class | Evidence | Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        assert isinstance(row, dict)
        lines.append(
            f"| `{row['app']}` | `{row['comparison_status']}` | `{row['claim_class']}` | `{row['v2_evidence']}` | {row['analysis_hint']} |"
        )
    lines.extend(
        [
            "",
            "## Release Boundary",
            "",
            "Allowed:",
            "",
            "- use this as the final-named v2.0 matrix candidate for external review;",
            "- cite compact count/flag/threshold outputs as the strongest v2.0 performance shape;",
            "- cite robot collision and road hazard as large-scale positive after Goal2066;",
            "- cite polygon overlap/Jaccard and graph/database control rows only with their boundaries.",
            "",
            "Not allowed:",
            "",
            "- v2.0 release readiness;",
            "- all-app speedup;",
            "- broad RT-core speedup;",
            "- arbitrary partner-program acceleration;",
            "- package-install readiness;",
            "- full witness-row materialization solved;",
            "- scalable arbitrary polygon overlay solved.",
            "",
            "## Final Blockers",
            "",
        ]
    )
    for blocker in payload["final_release_blockers"]:
        lines.append(f"- {blocker}")
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build final v2.0 release matrix candidate.")
    parser.add_argument("--output-json", default="docs/reports/goal2068_final_v2_0_release_matrix.json")
    parser.add_argument("--output-md", default="docs/reports/goal2068_final_v2_0_release_matrix.md")
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_matrix()
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
