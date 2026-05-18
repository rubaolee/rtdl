from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from rtdsl.baseline_runner import segments_from_records
from rtdsl.datasets import chains_to_segments
from rtdsl.datasets import load_cdb
from rtdsl.optix_runtime import pack_segments
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
from scripts.goal2192_rayjoin_same_query_stream_runner import _stream_segments
from scripts.goal2192_rayjoin_same_query_stream_runner import load_query_stream


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_rayjoin_pairs(path: Path, *, one_based: bool) -> set[tuple[int, int]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    query_key = "query_eid1" if one_based else "query_eid0"
    base_key = "base_eid1" if one_based else "base_eid0"
    return {
        (int(row[query_key]), int(row[base_key]))
        for row in payload["xsects"]
    }


def _pair_list(pairs: set[tuple[int, int]], *, limit: int = 20) -> list[dict[str, int]]:
    return [
        {"query_id": int(query_id), "base_id": int(base_id)}
        for query_id, base_id in sorted(pairs)[:limit]
    ]


def _segment_record(row: object) -> dict[str, float | int]:
    if isinstance(row, dict):
        return {
            "id": int(row["id"]),
            "x0": float(row["x0"]),
            "y0": float(row["y0"]),
            "x1": float(row["x1"]),
            "y1": float(row["y1"]),
        }
    return {
        "id": int(getattr(row, "id")),
        "x0": float(getattr(row, "x0")),
        "y0": float(getattr(row, "y0")),
        "x1": float(getattr(row, "x1")),
        "y1": float(getattr(row, "y1")),
    }


def _orient(a: dict[str, float | int], b: dict[str, float | int], px: float, py: float) -> float:
    return (float(b["x1"]) - float(b["x0"])) * (py - float(b["y0"])) - (
        float(b["y1"]) - float(b["y0"])
    ) * (px - float(b["x0"]))


def _pair_detail(
    query_id: int,
    base_id: int,
    left_by_id: dict[int, dict[str, float | int]],
    right_by_id: dict[int, dict[str, float | int]],
) -> dict[str, object]:
    query = left_by_id.get(query_id)
    base = right_by_id.get(base_id)
    detail: dict[str, object] = {"query_id": query_id, "base_id": base_id}
    if query is None or base is None:
        detail["lookup_status"] = "missing_record"
        return detail
    detail["lookup_status"] = "ok"
    detail["query_segment"] = query
    detail["base_segment"] = base
    detail["float_orientation"] = {
        "base_against_query_p0": _orient(query, base, float(query["x0"]), float(query["y0"])),
        "base_against_query_p1": _orient(query, base, float(query["x1"]), float(query["y1"])),
        "query_against_base_p0": _orient(base, query, float(base["x0"]), float(base["y0"])),
        "query_against_base_p1": _orient(base, query, float(base["x1"]), float(base["y1"])),
    }
    return detail


def _run_rtdl_pairs(
    stream_path: Path,
) -> tuple[
    set[tuple[int, int]],
    dict[str, object],
    dict[int, dict[str, float | int]],
    dict[int, dict[str, float | int]],
]:
    stream = load_query_stream(stream_path)
    if stream["workload"] != "lsi":
        raise ValueError("LSI stream expected")

    base = load_cdb(Path(str(stream["base_cdb"])))
    left_records = _stream_segments(stream)
    right_records = segments_from_records(chains_to_segments(base))

    start = time.perf_counter()
    packed_left = pack_segments(records=left_records)
    left_pack_sec = time.perf_counter() - start

    start = time.perf_counter()
    prepared = prepare_segment_pair_intersection_optix(right_records)
    prepare_sec = time.perf_counter() - start

    try:
        start = time.perf_counter()
        rows = prepared.run_raw(packed_left)
        query_sec = time.perf_counter() - start
        try:
            dict_rows = rows.to_dict_rows()
        finally:
            rows.close()
        phase = prepared.last_phase_timings()
    finally:
        prepared.close()

    pairs = {
        (int(row["left_id"]), int(row["right_id"]))
        for row in dict_rows
    }
    metadata = {
        "left_pack_sec": left_pack_sec,
        "prepare_sec": prepare_sec,
        "query_sec": query_sec,
        "query_count": int(stream["query_count"]),
        "query_stream_producer": stream["producer"],
        "right_segments": len(right_records),
        "rtdl_row_count": len(dict_rows),
        "phase": phase,
    }
    left_by_id = {int(_segment_record(row)["id"]): _segment_record(row) for row in left_records}
    right_by_id = {int(_segment_record(row)["id"]): _segment_record(row) for row in right_records}
    return pairs, metadata, left_by_id, right_by_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare RayJoin LSI xsect ids with RTDL emitted rows.")
    parser.add_argument("--stream", required=True)
    parser.add_argument("--rayjoin-xsects", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    stream_path = Path(args.stream)
    rayjoin_xsects_path = Path(args.rayjoin_xsects)
    output_path = Path(args.output)

    rtdl_pairs, metadata, left_by_id, right_by_id = _run_rtdl_pairs(stream_path)
    rayjoin_one_based = _load_rayjoin_pairs(rayjoin_xsects_path, one_based=True)
    rayjoin_zero_based = _load_rayjoin_pairs(rayjoin_xsects_path, one_based=False)

    one_based_delta = rayjoin_one_based.symmetric_difference(rtdl_pairs)
    zero_based_delta = rayjoin_zero_based.symmetric_difference(rtdl_pairs)
    if len(one_based_delta) <= len(zero_based_delta):
        alignment = "one_based"
        rayjoin_pairs = rayjoin_one_based
    else:
        alignment = "zero_based"
        rayjoin_pairs = rayjoin_zero_based

    missing_from_rtdl = rayjoin_pairs - rtdl_pairs
    extra_in_rtdl = rtdl_pairs - rayjoin_pairs
    payload = {
        "goal": 2333,
        "schema": "rtdl.rayjoin.lsi_mismatch_probe.v1",
        "generated_at_utc": _now(),
        "stream": str(stream_path),
        "rayjoin_xsects": str(rayjoin_xsects_path),
        "alignment": alignment,
        "rayjoin_count": len(rayjoin_pairs),
        "rtdl_count": len(rtdl_pairs),
        "missing_from_rtdl_count": len(missing_from_rtdl),
        "extra_in_rtdl_count": len(extra_in_rtdl),
        "missing_from_rtdl": _pair_list(missing_from_rtdl),
        "extra_in_rtdl": _pair_list(extra_in_rtdl),
        "missing_details": [
            _pair_detail(query_id, base_id, left_by_id, right_by_id)
            for query_id, base_id in sorted(missing_from_rtdl)[:20]
        ],
        "metadata": metadata,
        "claim_boundary": {
            "same_contract_with_rayjoin_query_exec": len(missing_from_rtdl) == 0 and len(extra_in_rtdl) == 0,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "paper_scale_perf_claim_authorized": False,
            "v2_0_release_authorized": False,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
