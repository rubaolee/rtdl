#!/usr/bin/env python3
"""Independent compact recount of Goal5781 from Goal5776 raw workers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import tarfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _endpoint(worker: dict[str, object]) -> float:
    return float(worker["rows"][0]["registered_complete_endpoint_seconds"])


def _phases(worker: dict[str, object]) -> dict[str, float]:
    row = worker["phase_accounting"]
    execute = list(row["row_execute_seconds"].values())
    if len(execute) != 1:
        raise RuntimeError("unexpected cold execute row count")
    return {
        "loading": float(row["loading_seconds"]),
        "preparation": float(row["preparation_seconds"]),
        "execute": float(execute[0]),
        "close": float(row["close_seconds"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--primary", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    with tarfile.open(args.archive, "r:gz") as archive:
        workers = [json.load(archive.extractfile(member))
                   for member in archive.getmembers()
                   if member.name.startswith("RAW/workers/")
                   and member.name.endswith(".json")]
    cold = [worker for worker in workers
            if worker["lifecycle"] == "installed_cold_compile_prepare_execute"]
    units = sorted({worker["unit_id"] for worker in cold})
    rows: dict[str, dict[str, object]] = {}
    for unit in units:
        pairs = []
        for pair in range(8):
            selected = {worker["method"]: worker for worker in cold
                        if worker["unit_id"] == unit
                        and int(worker["pair_index"]) == pair}
            v2 = selected["v2_direct_true_optix_backport"]
            v4 = selected["v4_restricted_callback_true_optix"]
            p2, p4 = _phases(v2), _phases(v4)
            for worker, phases in ((v2, p2), (v4, p4)):
                if abs(sum(phases.values()) - _endpoint(worker)) > 1.0e-7:
                    raise RuntimeError("phase conservation failed")
            delta = {name: p4[name] - p2[name] for name in p2}
            positive = {name: value for name, value in delta.items() if value > 0}
            pairs.append({
                "ratio": _endpoint(v2) / _endpoint(v4),
                "delta": _endpoint(v4) - _endpoint(v2),
                "dominant": max(positive, key=positive.get) if positive else "none",
            })
        rows[str(unit)] = {
            "ratio": statistics.median(pair["ratio"] for pair in pairs),
            "delta": statistics.median(pair["delta"] for pair in pairs),
            "preparation_dominant_pairs": sum(
                pair["dominant"] == "preparation" for pair in pairs),
            "execute_dominant_pairs": sum(
                pair["dominant"] == "execute" for pair in pairs),
        }
    primary = json.loads(args.primary.read_text(encoding="utf-8"))
    primary_rows = {row["unit_id"]: row for row in primary["cold_rows"]}
    if set(rows) != set(primary_rows):
        raise RuntimeError("primary row universe mismatch")
    for unit, row in rows.items():
        submitted = primary_rows[unit]
        if row["ratio"] != submitted["paired_ratio_median_v2_over_v4"] \
                or row["delta"] != submitted["median_v4_minus_v2_endpoint_seconds"]:
            raise RuntimeError(f"primary row statistic mismatch: {unit}")
        if row["preparation_dominant_pairs"] \
                != submitted["largest_positive_phase_counts"]["preparation"]:
            raise RuntimeError(f"primary preparation classification mismatch: {unit}")
    v4 = [worker for worker in cold if worker["method"].startswith("v4_")]
    census = {
        "hits": sum(int(worker["leaf_cache"].get("hit_count", 0)) for worker in v4),
        "misses": sum(int(worker["leaf_cache"].get("miss_count", 0)) for worker in v4),
        "disabled": sum(int(worker["leaf_cache"].get("disabled_count", 0)) for worker in v4),
    }
    result = {
        "schema": "rtdl.goal5781.independent_cold_recount.v1",
        "status": "PASS__FIFTEEN_ROWS_REBUILT_FROM_RAW",
        "archive_sha256": _sha(args.archive),
        "primary_sha256": _sha(args.primary),
        "worker_count": len(workers),
        "cold_worker_count": len(cold),
        "cold_row_count": len(rows),
        "cold_pass_count": sum(row["ratio"] >= 1.0 for row in rows.values()),
        "cold_fail_count": sum(row["ratio"] < 1.0 for row in rows.values()),
        "preparation_dominant_failure_count": sum(
            row["ratio"] < 1.0 and row["preparation_dominant_pairs"] >= 6
            for row in rows.values()),
        "execute_dominant_failure_count": sum(
            row["ratio"] < 1.0 and row["execute_dominant_pairs"] >= 6
            for row in rows.values()),
        "leaf_cache_census": census,
        "rows": rows,
        "imports_primary_or_goal5777": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    print(json.dumps({
        "status": result["status"], "sha256": _sha(args.output),
        "cold": [result["cold_pass_count"], result["cold_fail_count"]],
        "preparation_dominant_failures": result["preparation_dominant_failure_count"],
        "execute_dominant_failures": result["execute_dominant_failure_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
