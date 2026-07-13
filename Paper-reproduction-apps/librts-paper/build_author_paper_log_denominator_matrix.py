from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import Counter
from pathlib import Path


FLOAT = r"([0-9.eE+-]+)"


def _figure_for_category(category: str) -> int:
    if category.startswith("point-contains_queries_"):
        return 6
    if category.startswith("range-contains_queries_"):
        return 7
    if category.startswith("range-intersects_select_"):
        return 8
    if category.startswith("ray_duplication_range-intersects_"):
        return 9
    if "_update_" in category or category.startswith(("insertion_", "deletion_")):
        return 10
    if category.startswith("scalability_"):
        return 11
    if category.startswith("pip_queries_"):
        return 12
    raise ValueError(f"unclassified paper-log category: {category}")


def _first(pattern: str, text: str, cast):
    match = re.search(pattern, text, re.MULTILINE)
    return None if match is None else cast(match.group(1))


def _parse_record(name: str, text: str) -> dict[str, object]:
    parts = name.split("/")
    category = parts[1]
    if len(parts) == 3:
        index_type = "rtspatial"
        dataset = parts[2]
    else:
        index_type = parts[2]
        dataset = parts[-1]
    k_query_times = {
        1 << int(k): float(value)
        for k, value in re.findall(rf"^(\d+), Query Time {FLOAT} ms$", text, re.MULTILINE)
    }
    phase_rows = [
        {
            "forward_ms": float(forward),
            "forward_results": int(forward_results),
            "query_bvh_ms": float(bvh),
            "backward_ms": float(backward),
            "backward_results": int(backward_results),
        }
        for forward, forward_results, bvh, backward, backward_results in re.findall(
            rf"^Forward pass {FLOAT} ms, results (\d+) BVH {FLOAT} ms, "
            rf"Backward pass {FLOAT} ms, results (\d+)$",
            text,
            re.MULTILINE,
        )
    ]
    return {
        "path": name,
        "paper_figure": _figure_for_category(category),
        "category": category,
        "index_type": index_type,
        "dataset": dataset,
        "loaded_geometries": _first(r"^Loaded polygons (\d+)$", text, int),
        "loaded_queries": _first(r"^Loaded (?:queries|points) (\d+)$", text, int),
        "loading_ms": _first(rf"^Loading Time {FLOAT} ms$", text, float),
        "query_ms": _first(rf"^Query Time {FLOAT} ms$", text, float),
        "query_after_update_ms": _first(
            rf"^Query Time After Updates {FLOAT} ms$", text, float
        ),
        "result_count": _first(r"^Results (\d+)$", text, int),
        "selectivity": _first(rf"^Selectivity: {FLOAT}$", text, float),
        "throughput_geometries_per_sec": _first(
            rf"Throughput {FLOAT} geoms/sec$", text, float
        ),
        "predicted_partition_count": _first(
            r"^Predicated Parallelism (\d+) Time", text, int
        ),
        "prediction_ms": _first(
            rf"^Predicated Parallelism \d+ Time {FLOAT} ms$", text, float
        ),
        "k_query_time_ms": k_query_times,
        "partition_phase_rows": phase_rows,
    }


def build_matrix(archive_path: Path) -> dict[str, object]:
    records = []
    with zipfile.ZipFile(archive_path) as archive:
        for name in sorted(archive.namelist()):
            parts = name.split("/")
            if len(parts) < 3 or parts[0] != "logs" or not name.endswith(".log"):
                continue
            text = archive.read(name).decode("utf-8", errors="replace")
            records.append(_parse_record(name, text))

    figure_counts = Counter(record["paper_figure"] for record in records)
    index_counts = Counter(record["index_type"] for record in records)
    summaries = []
    denominator_contracts = {
        6: "author internal Query Time; index Loading Time excluded",
        7: "author internal Query Time; index Loading Time excluded",
        8: "author internal Query Time; incoming-query BVH construction included by paper policy",
        9: "per-k Query Time = forward cast + query BVH build + backward cast; prediction time reported separately",
        10: "mixed: Loading Time for build, geometries/sec for mutation throughput, after/before Query Time for slowdown",
        11: "author internal Query Time; result storage included",
        12: "paper plotting script uses Loading Time + Query Time as end-to-end PIP time",
    }
    for figure in range(6, 13):
        figure_records = [record for record in records if record["paper_figure"] == figure]
        rt_records = [
            record
            for record in figure_records
            if str(record["index_type"]).startswith("rtspatial")
        ]
        summaries.append(
            {
                "paper_figure": figure,
                "record_count": len(figure_records),
                "rtspatial_record_count": len(rt_records),
                "datasets": sorted({str(record["dataset"]) for record in figure_records}),
                "index_types": sorted({str(record["index_type"]) for record in figure_records}),
                "denominator_contract": denominator_contracts[figure],
                "query_time_value_count": sum(record["query_ms"] is not None for record in figure_records),
                "loading_time_value_count": sum(record["loading_ms"] is not None for record in figure_records),
                "result_count_value_count": sum(record["result_count"] is not None for record in figure_records),
            }
        )

    ray_multicast = [
        record
        for record in records
        if record["paper_figure"] == 9 and record["index_type"] == "rtspatial-vary-parallelism"
    ]
    if len(ray_multicast) != 6:
        raise RuntimeError(f"expected six Ray-Multicast logs, found {len(ray_multicast)}")
    if not all(len(record["k_query_time_ms"]) == 10 for record in ray_multicast):
        raise RuntimeError("Ray-Multicast logs do not each contain ten k timings")

    return {
        "schema": "rtdl.paper_reproduction.librts.author_log_denominators.v1",
        "status": "author_paper_log_denominators_extracted__not_rtdl_reproduction",
        "source": {
            "archive": str(archive_path),
            "record_count": len(records),
            "figure_record_counts": {str(key): value for key, value in sorted(figure_counts.items())},
            "index_type_record_counts": dict(sorted(index_counts.items())),
        },
        "figure_summaries": summaries,
        "ray_multicast_author_targets": ray_multicast,
        "records": records,
        "decision": {
            "author_target_values_available": True,
            "same_denominator_rtdl_values_available": False,
            "performance_ratio_authorized": False,
            "next_goal": "select_one_exact_input_acquisition_or_bounded_same_input_figure_gate",
            "pod_required_next": False,
        },
        "claim_boundary": {
            "paper_figures_reproduced": False,
            "author_logs_are_reference_targets_only": True,
            "rtspatial_is_author_name_not_rtdl_backend": True,
            "cross_hardware_ratio_authorized": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_matrix(args.archive.resolve())
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
