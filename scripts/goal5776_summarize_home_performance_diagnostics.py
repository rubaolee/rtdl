#!/usr/bin/env python3
"""Build the non-formal Home performance diagnostic ledger for Goal5776.

The input files are correctness/capacity smokes, not a paired performance
cohort.  This script therefore records exact observed seconds and labels every
row as non-formal.  A diagnostic V2/V4 ratio is emitted only when the two
recorded endpoints have the same lifecycle boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
OUT = DOCS / "goal5776_home_real_scale_performance_diagnostics_20260813.json"


def _load(name: str) -> tuple[Path, dict[str, Any]]:
    path = DOCS / name
    return path, json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row(
    *, app: str, lane: str, v2: float, v4: float,
    contract: str, comparable: bool, note: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "application": app,
        "lane": lane,
        "timing_contract": contract,
        "v2_seconds_observed_not_formal": v2,
        "v4_seconds_observed_not_formal": v4,
        "v4_minus_v2_seconds_observed_not_saving": v4 - v2,
        "same_lifecycle_boundary": comparable,
        "ratio_claim_eligible": False,
        "note": note,
    }
    if comparable:
        row["diagnostic_v2_over_v4_ratio_not_formal"] = v2 / v4
    else:
        row["diagnostic_v2_over_v4_ratio_not_formal"] = None
    return row


def main() -> None:
    sources: dict[str, dict[str, Any]] = {}

    def take(key: str, name: str) -> dict[str, Any]:
        path, data = _load(name)
        sources[key] = {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha(path)}
        return data

    particle = take("particle", "goal5776_particle_home_real_scale_smoke_20260813.json")
    triangle = take("triangle", "goal5776_triangle_com_dblp_home_real_scale_smoke_20260813.json")
    dbscan = take("rt_dbscan", "goal5776_rtdbscan_home_real_scale_grouped_smoke_20260813.json")
    rtnn = take("rtnn", "goal5776_rtnn_home_real_scale_smoke_20260813.json")
    barnes = take("rt_barneshut", "goal5776_rt_barneshut_home_real_scale_smoke_20260813.json")
    xhd = take("x_hd", "goal5776_xhd_home_real_scale_smoke_20260813.json")
    raydb = take("raydb", "goal5776_raydb_home_real_scale_smoke_20260813.json")
    librts = take("librts", "goal5776_librts_home_real_scale_smoke_20260813.json")
    rayjoin = take("rayjoin", "goal5776_rayjoin_home_real_scale_smoke_20260813.json")

    rows: list[dict[str, Any]] = []
    rows.append(_row(
        app="ParticleAdvection", lane="full_mesh_5000_queries",
        v2=particle["v2_direct"]["execute_seconds_observed_not_formal"],
        v4=particle["v4"]["execute_seconds_observed_not_formal"],
        contract="v2_native_hit_vs_v4_verified_output__asymmetric",
        comparable=False,
        note="V2 stops before canonical face/output projection; V4 returns the verified application output.",
    ))
    for tr in triangle["rows"]:
        rows.append(_row(
            app="TriangleCounting", lane=f"com-dblp::{tr['paper_algorithm']}",
            v2=tr["v2_direct"]["complete_seconds_observed_not_formal"],
            v4=tr["v4"]["execute_seconds_observed_not_formal"],
            contract="v2_complete_vs_v4_prepared_execute__asymmetric",
            comparable=False,
            note="Retained for phase diagnosis only; it must not be rendered as a V2/V4 ratio.",
        ))
    rows.append(_row(
        app="RT-DBSCAN", lane="4096_points_grouped_radius_graph",
        v2=dbscan["v2_direct"]["execute_seconds_observed_not_formal"],
        v4=dbscan["v4"]["execute_seconds_observed_not_formal"],
        contract="v2_physical_columns_vs_v4_verified_output__asymmetric",
        comparable=False,
        note="V2 stops before canonical component projection and receipt finish; V4 returns the verified application output.",
    ))
    rows.append(_row(
        app="RTNN", lane="12m_search_4096_query_k4",
        v2=rtnn["v2_direct"]["execute_seconds_observed_not_formal"],
        v4=rtnn["v4"]["execute_seconds_observed_not_formal"],
        contract="v2_physical_rows_vs_v4_verified_canonical_rows__asymmetric",
        comparable=False,
        note="V2 stops before canonical paper-row projection and receipt finish; V4 includes both.",
    ))
    rows.append(_row(
        app="RT-BarnesHut", lane="32768_bodies_1486_nodes",
        v2=barnes["v2_direct"]["execute_seconds_observed_not_formal"],
        v4=barnes["v4"]["execute_seconds_observed_not_formal"],
        contract="v2_physical_rows_vs_v4_verified_force_rows__asymmetric",
        comparable=False,
        note="V2 stops before force projection and receipt finish; V4 includes canonical force materialization and receipt validation.",
    ))
    rows.append(_row(
        app="X-HD", lane="dragon_to_happy_global_witness",
        v2=xhd["v2_direct"]["complete_seconds_observed_not_formal"],
        v4=xhd["v4"]["execute_seconds_observed_not_formal"],
        contract="v2_complete_vs_v4_prepared_execute__asymmetric",
        comparable=False,
        note="Retained for phase diagnosis only; it must not be rendered as a V2/V4 ratio.",
    ))
    rows.append(_row(
        app="RayDB", lane="59986052_rows_12_partitions",
        v2=raydb["v2_direct"]["complete_packet_seconds_observed_not_formal"],
        v4=raydb["v4"]["complete_packet_seconds_observed_not_formal"],
        contract="complete_packet",
        comparable=True,
        note="V4 compiler time is recorded separately; this is the route-reported complete packet boundary.",
    ))
    for lane in ("point_contains", "range_contains"):
        rows.append(_row(
            app="LibRTS", lane=f"11544398_boxes_100000_queries::{lane}",
            v2=librts["v2_direct"]["operations"][lane]["execute_seconds_observed_not_formal"],
            v4=librts["v4"][lane]["execute_seconds_observed_not_formal"],
            contract="v2_physical_count_vs_v4_verified_count__asymmetric",
            comparable=False,
            note="V2 traversal-receipt finish is outside its timer; V4 receipt finish is inside execute_count.",
        ))
    rows.append(_row(
        app="RayJoin", lane="full_top4_county_zipcode_six_batch",
        v2=rayjoin["v2_direct"]["wall_seconds_observed_not_formal"],
        v4=rayjoin["v4"]["wall_seconds_observed_not_formal"],
        contract="v4_compile_plus_execute_vs_v2_prepared_six_batch__asymmetric",
        comparable=False,
        note="The V2 prepared arguments are constructed before its wall timer; no ratio is legal.",
    ))

    preparation = [
        {"application": "ParticleAdvection", "lane": "full_mesh", "v2": particle["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": particle["v4"]["prepare_seconds_observed_not_formal"]},
        {"application": "RT-DBSCAN", "lane": "4096_points", "v2": dbscan["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": dbscan["v4"]["prepare_seconds_observed_not_formal"]},
        {"application": "RTNN", "lane": "12m_search", "v2": rtnn["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": rtnn["v4"]["prepare_seconds_observed_not_formal"]},
        {"application": "RT-BarnesHut", "lane": "32768_bodies", "v2": barnes["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": barnes["v4"]["prepare_seconds_observed_not_formal"]},
        {"application": "LibRTS", "lane": "point_contains", "v2": librts["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": librts["v4"]["point_contains"]["prepare_seconds_observed_not_formal"]},
        {"application": "LibRTS", "lane": "range_contains", "v2": librts["v2_direct"]["prepare_seconds_observed_not_formal"], "v4": librts["v4"]["range_contains"]["prepare_seconds_observed_not_formal"]},
    ]
    for tr in triangle["rows"]:
        preparation.append({"application": "TriangleCounting", "lane": tr["paper_algorithm"], "v2": None, "v4": tr["v4"]["prepare_seconds_observed_not_formal"]})
    preparation.extend([
        {"application": "X-HD", "lane": "global_witness", "v2": None, "v4": xhd["v4"]["prepare_seconds_observed_not_formal"]},
        {"application": "RayDB", "lane": "compiler", "v2": None, "v4": raydb["v4"]["compiler_seconds_observed_not_formal"]},
    ])
    for item in preparation:
        item["seconds_observed_not_formal"] = {"v2": item.pop("v2"), "v4": item.pop("v4")}
        item["ratio_claim_eligible"] = False

    comparable_rows = [r for r in rows if r["same_lifecycle_boundary"]]
    slower = [r for r in comparable_rows if r["v4_minus_v2_seconds_observed_not_saving"] > 0]
    faster = [r for r in comparable_rows if r["v4_minus_v2_seconds_observed_not_saving"] < 0]
    result = {
        "schema": "rtdl.goal5776.home_real_scale_performance_diagnostics.v1",
        "status": "complete_nonformal_diagnostic_ledger",
        "source_results": sources,
        "rules": {
            "registered_performance_observation_created": False,
            "single_observation_per_lane": True,
            "bootstrap_or_confidence_interval_claimed": False,
            "modern_rtx_claimed": False,
            "no_slower_claimed": False,
            "asymmetric_rows_may_not_emit_ratio": True,
            "observed_phase_seconds_are_not_predicted_savings": True,
        },
        "prepared_or_packet_execution_rows": rows,
        "preparation_observations": preparation,
        "diagnostic_summary": {
            "row_count": len(rows),
            "same_boundary_row_count": len(comparable_rows),
            "same_boundary_v4_slower_count": len(slower),
            "same_boundary_v4_faster_count": len(faster),
            "asymmetric_row_count": len(rows) - len(comparable_rows),
            "largest_positive_execution_deltas_seconds_observed_not_saving": [
                {"application": r["application"], "lane": r["lane"], "seconds": r["v4_minus_v2_seconds_observed_not_saving"]}
                for r in sorted(slower, key=lambda x: x["v4_minus_v2_seconds_observed_not_saving"], reverse=True)
            ],
        },
        "claim_boundary": {
            "home_diagnostic_only": True,
            "formal_v2_v4_performance_result": False,
            "performance_cause_proven": False,
            "predicted_saving_claimed": False,
            "repair_authorized_by_this_ledger": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), **result["diagnostic_summary"]}, indent=2))


if __name__ == "__main__":
    main()
