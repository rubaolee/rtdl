#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_road_hazard_screening as road_app
from examples.rtdl_polygon_pair_overlap_area_rows import make_authored_polygon_pair_overlap_case
from examples.rtdl_polygon_set_jaccard import make_authored_polygon_set_jaccard_case
from rtdsl.baseline_runner import load_representative_case
from scripts.goal839_baseline_artifact_schema import build_baseline_artifact
from scripts.goal839_baseline_artifact_schema import load_goal835_row
from scripts.goal839_baseline_artifact_schema import write_baseline_artifact
import rtdsl as rt


GOAL = "Goal975 Linux PostGIS remaining baseline collector"
DATE = "2026-04-26"


def _median(samples: list[float]) -> float:
    return float(statistics.median(samples)) if samples else 0.0


def _time(fn: Callable[[], Any]) -> tuple[Any, float]:
    start = time.perf_counter()
    return fn(), time.perf_counter() - start


def _artifact_path(app: str, path_name: str, baseline_name: str) -> Path:
    return ROOT / "docs" / "reports" / f"goal835_baseline_{app}_{path_name}_{baseline_name}_2026-04-23.json"


def _write(
    *,
    app: str,
    path_name: str,
    baseline_name: str,
    benchmark_scale: dict[str, Any] | None,
    repeats: int,
    parity: bool,
    phase_seconds: dict[str, float],
    summary: dict[str, Any],
    notes: list[str],
    validation: dict[str, Any],
) -> dict[str, Any]:
    row = load_goal835_row(app=app, path_name=path_name, baseline_name=baseline_name)
    artifact = build_baseline_artifact(
        row=row,
        baseline_name=baseline_name,
        source_backend="postgis",
        benchmark_scale=benchmark_scale,
        repeated_runs=repeats,
        correctness_parity=parity,
        phase_seconds=phase_seconds,
        summary=summary,
        notes=notes,
        validation=validation,
    )
    path = _artifact_path(app, path_name, baseline_name)
    write_baseline_artifact(path, artifact)
    return {"path": str(path), "artifact": artifact}


def _segpoly_phase(input_sec: float, query_samples: list[float], validation_sec: float = 0.0) -> dict[str, float]:
    return {
        "input_build_sec": input_sec,
        "optix_prepare_sec": 0.0,
        "optix_query_sec": _median(query_samples),
        "python_postprocess_sec": 0.0,
        "validation_sec": validation_sec,
        "optix_close_sec": 0.0,
    }


def _anyhit_phase(input_sec: float, query_samples: list[float], row_count: int, *, parity: bool) -> dict[str, float]:
    return {
        "input_build_sec": input_sec,
        "cpu_reference_total_sec": 0.0,
        "optix_prepare_sec": 0.0,
        "optix_query_sec": _median(query_samples),
        "python_postprocess_sec": 0.0,
        "validation_sec": 0.0,
        "optix_close_sec": 0.0,
        "emitted_count": float(row_count),
        "copied_count": float(row_count),
        "overflowed": 0.0,
        "strict_pass": 1.0 if parity else 0.0,
        "strict_failures": 0.0 if parity else 1.0,
        "status": 1.0 if parity else 0.0,
    }


def _polygon_phase(input_sec: float, query_samples: list[float], *, parity: bool) -> dict[str, float]:
    return {
        "input_build_sec": input_sec,
        "cpu_reference_sec": 0.0,
        "optix_candidate_discovery_sec": _median(query_samples),
        "cpu_exact_refinement_sec": 0.0,
        "native_exact_continuation_sec": 0.0,
        "parity_vs_cpu": 1.0 if parity else 0.0,
        "rt_core_candidate_discovery_active": 0.0,
    }


def _polygon_wkt(vertices: tuple[tuple[float, float], ...]) -> str:
    ring = vertices if vertices and vertices[0] == vertices[-1] else vertices + (vertices[0],)
    body = ",".join(f"{x} {y}" for x, y in ring)
    return f"POLYGON(({body}))"


def _copy_segments(cur, schema: str, table: str, rows) -> None:
    cur.execute(
        f"CREATE TABLE {schema}.{table}_raw (id BIGINT, x0 DOUBLE PRECISION, y0 DOUBLE PRECISION, x1 DOUBLE PRECISION, y1 DOUBLE PRECISION)"
    )
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row.id), row.x0, row.y0, row.x1, row.y1])
    payload.seek(0)
    cur.copy_expert(
        f"COPY {schema}.{table}_raw (id, x0, y0, x1, y1) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE {schema}.{table} AS
        SELECT id,
               ST_GeomFromText('LINESTRING(' || x0 || ' ' || y0 || ',' || x1 || ' ' || y1 || ')', 4326)::geometry(LINESTRING, 4326) AS geom
        FROM {schema}.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON {schema}.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE {schema}.{table}")


def _copy_polygons(cur, schema: str, table: str, rows, *, srid: int = 4326) -> None:
    cur.execute(f"CREATE TABLE {schema}.{table}_raw (id BIGINT, wkt TEXT)")
    payload = io.StringIO()
    writer = csv.writer(payload, delimiter="\t", lineterminator="\n")
    for row in rows:
        writer.writerow([int(row.id), _polygon_wkt(tuple(row.vertices))])
    payload.seek(0)
    cur.copy_expert(
        f"COPY {schema}.{table}_raw (id, wkt) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t')",
        payload,
    )
    cur.execute(
        f"""
        CREATE TABLE {schema}.{table} AS
        SELECT id, ST_GeomFromText(wkt, {srid})::geometry(POLYGON, {srid}) AS geom
        FROM {schema}.{table}_raw
        """
    )
    cur.execute(f"CREATE INDEX {table}_geom_idx ON {schema}.{table} USING GIST (geom)")
    cur.execute(f"ANALYZE {schema}.{table}")


def _rows_equal(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(right, sort_keys=True, separators=(",", ":"))


def _road_postgis_once(*, db_name: str, db_user: str | None, copies: int) -> tuple[dict[str, Any], float, bool]:
    from rtdsl.goal114_segment_polygon_postgis import connect_postgis

    case = road_app.make_demo_case(copies=copies)
    conn = connect_postgis(db_name, db_user)
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS goal975_road CASCADE")
            cur.execute("CREATE SCHEMA goal975_road")
            _copy_segments(cur, "goal975_road", "roads", tuple(case["roads"]))
            _copy_polygons(cur, "goal975_road", "hazards", tuple(case["hazards"]))
            start = time.perf_counter()
            cur.execute(
                """
                SELECT
                    r.id::BIGINT AS segment_id,
                    COUNT(h.id)::BIGINT AS hit_count
                FROM goal975_road.roads AS r
                LEFT JOIN goal975_road.hazards AS h
                    ON ST_Intersects(r.geom, h.geom)
                GROUP BY r.id
                ORDER BY r.id
                """
            )
            rows = tuple({"segment_id": int(segment_id), "hit_count": int(hit_count)} for segment_id, hit_count in cur.fetchall())
            sec = time.perf_counter() - start
    finally:
        conn.close()
    summary = {
        "row_count": len(rows),
        "hit_sum": sum(int(row["hit_count"]) for row in rows),
        "positive_count": sum(1 for row in rows if int(row["hit_count"]) > 0),
        "priority_segment_count": sum(1 for row in rows if int(row["hit_count"]) >= 2),
    }
    return summary, sec, True


def _goal114_once(*, db_name: str, db_user: str | None, copies: int) -> tuple[dict[str, Any], float, bool]:
    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    payload = rt.run_goal114_segment_polygon_postgis_validation(
        dataset=dataset,
        backends=("cpu",),
        db_name=db_name,
        db_user=db_user,
    )
    record = payload["records"][0]
    summary = {
        "row_count": int(payload["postgis"]["row_count"]),
        "sha256": str(payload["postgis"]["sha256"]),
        "backend_row_count": int(record["row_count"]),
        "backend_sha256": str(record["hash"]["sha256"]),
    }
    return summary, float(payload["postgis"]["sec"]), bool(record["parity_vs_postgis"])


def _goal128_once(*, db_name: str, db_user: str | None, copies: int) -> tuple[dict[str, Any], float, bool]:
    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    payload = rt.run_goal128_segment_polygon_anyhit_postgis_validation(
        dataset=dataset,
        backends=("cpu",),
        db_name=db_name,
        db_user=db_user,
    )
    record = payload["records"][0]
    summary = {
        "row_count": int(payload["postgis"]["row_count"]),
        "sha256": str(payload["postgis"]["sha256"]),
        "backend_row_count": int(record["row_count"]),
        "backend_sha256": str(record["hash"]["sha256"]),
    }
    return summary, float(payload["postgis"]["sec"]), bool(record["parity_vs_postgis"])


def _goal138_once(*, db_name: str, db_user: str | None) -> tuple[dict[str, Any], float, bool]:
    payload = rt.run_goal138_polygon_overlap_postgis_validation(db_name=db_name, db_user=db_user)
    rows = tuple(payload["postgis_rows"])
    summary = {
        "row_count": len(rows),
        "intersection_area_sum": sum(int(row["intersection_area"]) for row in rows),
        "union_area_sum": sum(int(row["union_area"]) for row in rows),
    }
    return summary, float(payload["postgis_sec"]), bool(payload["python_parity_vs_postgis"] and payload["cpu_parity_vs_postgis"])


def _goal140_once(*, db_name: str, db_user: str | None) -> tuple[dict[str, Any], float, bool]:
    payload = rt.run_goal140_polygon_set_jaccard_postgis_validation(db_name=db_name, db_user=db_user)
    row = dict(payload["postgis_rows"][0])
    summary = {
        "intersection_area": int(row["intersection_area"]),
        "left_area": int(row["left_area"]),
        "right_area": int(row["right_area"]),
        "union_area": int(row["union_area"]),
        "jaccard_similarity": float(row["jaccard_similarity"]),
    }
    return summary, float(payload["postgis_sec"]), bool(payload["python_parity_vs_postgis"] and payload["cpu_parity_vs_postgis"])


def _repeat(fn: Callable[[], tuple[dict[str, Any], float, bool]], repeats: int) -> tuple[dict[str, Any], list[float], bool]:
    summaries: list[dict[str, Any]] = []
    timings: list[float] = []
    parities: list[bool] = []
    for _ in range(repeats):
        summary, sec, parity = fn()
        summaries.append(summary)
        timings.append(sec)
        parities.append(parity)
    stable = all(_rows_equal(summaries[0], summary) for summary in summaries[1:]) if summaries else False
    return summaries[-1], timings, bool(stable and all(parities))


def collect(*, db_name: str, db_user: str | None, copies: int, repeats: int) -> dict[str, Any]:
    outputs: list[dict[str, Any]] = []

    _, road_input_sec = _time(lambda: road_app.make_demo_case(copies=copies))
    road_reference = road_app.run_case("cpu_python_reference", copies=copies, output_mode="summary")
    road_ref_summary = {
        "row_count": int(road_reference["row_count"]),
        "priority_segment_count": int(road_reference["priority_segment_count"]),
    }
    road_summary, road_timings, road_parity = _repeat(
        lambda: _road_postgis_once(db_name=db_name, db_user=db_user, copies=copies),
        repeats,
    )
    road_validation = {
        "stable_repeated_summary": road_parity,
        "reference_summary": road_ref_summary,
        "postgis_summary_subset_matches_reference": (
            road_summary["row_count"] == road_ref_summary["row_count"]
            and road_summary["priority_segment_count"] == road_ref_summary["priority_segment_count"]
        ),
    }
    outputs.append(
        _write(
            app="road_hazard_screening",
            path_name="road_hazard_native_summary_gate",
            baseline_name="postgis_when_available",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=bool(road_validation["postgis_summary_subset_matches_reference"] and road_parity),
            phase_seconds=_segpoly_phase(road_input_sec, road_timings),
            summary=road_summary,
            notes=["Linux PostGIS baseline for road-hazard segment/polygon hit-count summary semantics."],
            validation=road_validation,
        )
    )

    dataset = rt.segment_polygon_large_dataset_name(copies=copies)
    _, hitcount_input_sec = _time(lambda: load_representative_case("segment_polygon_hitcount", dataset))
    hit_summary, hit_timings, hit_parity = _repeat(lambda: _goal114_once(db_name=db_name, db_user=db_user, copies=copies), repeats)
    outputs.append(
        _write(
            app="segment_polygon_hitcount",
            path_name="segment_polygon_hitcount_native_experimental",
            baseline_name="postgis_when_available",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=hit_parity,
            phase_seconds=_segpoly_phase(hitcount_input_sec, hit_timings),
            summary=hit_summary,
            notes=["Linux PostGIS baseline for segment/polygon hit-count semantics with GiST indexed geometry tables."],
            validation={"dataset": dataset, "stable_and_cpu_parity": hit_parity},
        )
    )

    _, anyhit_input_sec = _time(lambda: load_representative_case("segment_polygon_anyhit_rows", dataset))
    anyhit_summary, anyhit_timings, anyhit_parity = _repeat(lambda: _goal128_once(db_name=db_name, db_user=db_user, copies=copies), repeats)
    outputs.append(
        _write(
            app="segment_polygon_anyhit_rows",
            path_name="segment_polygon_anyhit_rows_prepared_bounded_gate",
            baseline_name="postgis_when_available_for_same_pair_semantics",
            benchmark_scale={"copies": copies, "iterations": repeats},
            repeats=repeats,
            parity=anyhit_parity,
            phase_seconds=_anyhit_phase(anyhit_input_sec, anyhit_timings, int(anyhit_summary["row_count"]), parity=anyhit_parity),
            summary=anyhit_summary,
            notes=["Linux PostGIS baseline for strict segment/polygon pair-row semantics."],
            validation={"dataset": dataset, "stable_and_cpu_parity": anyhit_parity},
        )
    )

    _, pair_input_sec = _time(make_authored_polygon_pair_overlap_case)
    pair_summary, pair_timings, pair_parity = _repeat(lambda: _goal138_once(db_name=db_name, db_user=db_user), repeats)
    outputs.append(
        _write(
            app="polygon_pair_overlap_area_rows",
            path_name="polygon_pair_overlap_optix_native_assisted_phase_gate",
            baseline_name="postgis_when_available_for_same_unit_cell_contract",
            benchmark_scale={"copies": 1, "iterations": repeats},
            repeats=repeats,
            parity=pair_parity,
            phase_seconds=_polygon_phase(pair_input_sec, pair_timings, parity=pair_parity),
            summary=pair_summary,
            notes=["Linux PostGIS baseline for the current authored unit-cell polygon-pair area contract."],
            validation={"stable_and_cpu_parity": pair_parity},
        )
    )

    _, jaccard_input_sec = _time(make_authored_polygon_set_jaccard_case)
    jaccard_summary, jaccard_timings, jaccard_parity = _repeat(lambda: _goal140_once(db_name=db_name, db_user=db_user), repeats)
    outputs.append(
        _write(
            app="polygon_set_jaccard",
            path_name="polygon_set_jaccard_optix_native_assisted_phase_gate",
            baseline_name="postgis_when_available_for_same_unit_cell_contract",
            benchmark_scale={"copies": 1, "iterations": repeats},
            repeats=repeats,
            parity=jaccard_parity,
            phase_seconds=_polygon_phase(jaccard_input_sec, jaccard_timings, parity=jaccard_parity),
            summary=jaccard_summary,
            notes=["Linux PostGIS baseline for the current authored unit-cell polygon-set Jaccard contract."],
            validation={"stable_and_cpu_parity": jaccard_parity},
        )
    )

    return {
        "goal": GOAL,
        "date": DATE,
        "db_name": db_name,
        "db_user": db_user,
        "copies": copies,
        "repeats": repeats,
        "artifact_count": len(outputs),
        "artifacts": [{key: value for key, value in item.items() if key != "artifact"} for item in outputs],
        "status": "ok" if all(item["artifact"]["status"] == "ok" for item in outputs) else "invalid",
        "boundary": "PostGIS is an external same-semantics baseline. These artifacts do not authorize public RTX speedup claims.",
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal975 Linux PostGIS Remaining Baselines",
        "",
        f"Status: `{payload['status']}`",
        "",
        payload["boundary"],
        "",
        f"- database: `{payload['db_name']}`",
        f"- copies: `{payload['copies']}`",
        f"- repeats: `{payload['repeats']}`",
        f"- artifacts: `{payload['artifact_count']}`",
        "",
        "| Artifact |",
        "|---|",
    ]
    for artifact in payload["artifacts"]:
        lines.append(f"| `{artifact['path']}` |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect remaining Goal835 PostGIS baseline artifacts on Linux.")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--copies", type=int, default=256)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-json", default=str(ROOT / "docs" / "reports" / "goal975_linux_postgis_remaining_baselines_2026-04-26.json"))
    parser.add_argument("--output-md", default=str(ROOT / "docs" / "reports" / "goal975_linux_postgis_remaining_baselines_2026-04-26.md"))
    args = parser.parse_args(argv)
    payload = collect(db_name=args.db_name, db_user=args.db_user, copies=args.copies, repeats=args.repeats)
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
