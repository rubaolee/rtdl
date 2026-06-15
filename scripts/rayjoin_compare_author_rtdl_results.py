from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _load(path: Path | None) -> dict | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stdout_lines(payload: dict) -> list[str]:
    summary = payload.get("stdout_summary") or {}
    return list(summary.get("head") or []) + list(summary.get("tail") or [])


def _first_int(pattern: str, lines: list[str]) -> int | None:
    rx = re.compile(pattern)
    for line in lines:
        match = rx.search(line)
        if match:
            return int(match.group(1))
    return None


def _author_row(program: str, payload: dict | None) -> list[dict[str, object]]:
    if payload is None:
        return []
    rows: list[dict[str, object]] = []
    timing_ms = payload.get("timing_ms") or {}
    lines = _stdout_lines(payload)
    count = None
    if program == "lsi":
        count = _first_int(r"Intersections:\s+([0-9]+)", lines)
    elif program == "overlay":
        count = _first_int(r"overlay_lsi_xsects\s+([0-9]+)", lines)

    rows.append(
        {
            "program": program,
            "implementation": "rayjoin_author_rt",
            "timing_view": "end_to_end_process",
            "seconds": float(payload["elapsed_sec"]) if "elapsed_sec" in payload else None,
            "count": count,
            "notes": "Author command wall time, includes its own read/init/build/query/cleanup phases.",
        }
    )
    if program in {"lsi", "pip"} and "Query" in timing_ms:
        rows.append(
            {
                "program": program,
                "implementation": "rayjoin_author_rt",
                "timing_view": "author_query",
                "seconds": float(timing_ms["Query"]) / 1000.0,
                "count": count,
                "notes": "Author-reported Query phase.",
            }
        )
    if program == "overlay":
        for key in ("Intersection edges", "Computer output polygons"):
            if key in timing_ms:
                rows.append(
                    {
                        "program": program,
                        "implementation": "rayjoin_author_rt",
                        "timing_view": key.lower().replace(" ", "_"),
                        "seconds": float(timing_ms[key]) / 1000.0,
                        "count": count if key == "Intersection edges" else None,
                        "notes": f"Author-reported {key} phase.",
                    }
                )
    return rows


def _rtdl_rows(payload: dict | None) -> list[dict[str, object]]:
    if payload is None:
        return []
    program = str(payload["program"])
    rows: list[dict[str, object]] = []
    for backend, result in (payload.get("results") or {}).items():
        implementation = f"rtdl_{backend}"
        if program in {"lsi", "pip"}:
            rows.append(
                {
                    "program": program,
                    "implementation": implementation,
                    "timing_view": "hot_median",
                    "seconds": result.get("hot_median_sec"),
                    "count": result.get("count"),
                    "notes": f"RTDL hot median after warmup={result.get('warmup')} repeat={result.get('repeat')}.",
                }
            )
            rows.append(
                {
                    "program": program,
                    "implementation": implementation,
                    "timing_view": "native_median",
                    "seconds": result.get("native_traversal_median_sec"),
                    "count": result.get("count"),
                    "notes": "Native traversal/RT phase where available.",
                }
            )
            continue

        if program == "overlay":
            phase = result.get("phase_seconds") or {}
            total = result.get("total_median_sec", phase.get("total_sec"))
            load_pack = result.get(
                "load_pack_median_sec",
                phase.get("load_pack_inputs_sec") or phase.get("pack_inputs_sec") or 0.0,
            )
            compute_without_load_pack = result.get("compute_without_load_pack_median_sec")
            if compute_without_load_pack is None and total is not None:
                compute_without_load_pack = float(total) - float(load_pack or 0.0)
            timing_note = "RTDL overlay median" if result.get("total_median_sec") is not None else "RTDL overlay total"
            rows.extend(
                [
                    {
                        "program": program,
                        "implementation": implementation,
                        "timing_view": "end_to_end",
                        "seconds": total,
                        "count": (result.get("lsi") or {}).get("intersection_count"),
                        "notes": (
                            f"{timing_note} including CDB load/pack/cache and compute"
                            f" after warmup={result.get('warmup')} repeat={result.get('repeat')}."
                        ),
                    },
                    {
                        "program": program,
                        "implementation": implementation,
                        "timing_view": "load_pack",
                        "seconds": load_pack,
                        "count": None,
                        "notes": "RTDL app ingestion plus packed-array load/pack.",
                    },
                    {
                        "program": program,
                        "implementation": implementation,
                        "timing_view": "compute_without_load_pack",
                        "seconds": compute_without_load_pack,
                        "count": (result.get("lsi") or {}).get("intersection_count"),
                        "notes": "RTDL overlay total minus load/pack phase.",
                    },
                ]
            )
    return rows


def _write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# RayJoin Author vs RTDL Comparison",
        "",
        "| Program | Implementation | Timing View | Seconds | Count | Notes |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        seconds = row.get("seconds")
        seconds_text = "" if seconds is None else f"{float(seconds):.6f}"
        count = row.get("count")
        count_text = "" if count is None else f"{int(count):,}"
        lines.append(
            "| {program} | {implementation} | {timing_view} | {seconds} | {count} | {notes} |".format(
                program=row["program"],
                implementation=row["implementation"],
                timing_view=row["timing_view"],
                seconds=seconds_text,
                count=count_text,
                notes=str(row.get("notes") or "").replace("|", "/"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize RayJoin author-code vs RTDL result JSONs.")
    parser.add_argument("--author-lsi", type=Path)
    parser.add_argument("--author-pip", type=Path)
    parser.add_argument("--author-overlay", type=Path)
    parser.add_argument("--rtdl-lsi", type=Path)
    parser.add_argument("--rtdl-pip", type=Path)
    parser.add_argument("--rtdl-overlay", type=Path)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    args = parser.parse_args()

    rows: list[dict[str, object]] = []
    rows.extend(_author_row("lsi", _load(args.author_lsi)))
    rows.extend(_author_row("pip", _load(args.author_pip)))
    rows.extend(_author_row("overlay", _load(args.author_overlay)))
    rows.extend(_rtdl_rows(_load(args.rtdl_lsi)))
    rows.extend(_rtdl_rows(_load(args.rtdl_pip)))
    rows.extend(_rtdl_rows(_load(args.rtdl_overlay)))

    payload = {
        "schema": "rtdl.rayjoin.author_rtdl_comparison_summary.v1",
        "rows": rows,
        "principle": (
            "Report end-to-end and compute/native timing separately; classify load/pack as partner/cache overhead, "
            "not RT traversal."
        ),
    }
    if args.output_json is not None:
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if args.output_md is not None:
        _write_markdown(args.output_md, rows)


if __name__ == "__main__":
    main()
