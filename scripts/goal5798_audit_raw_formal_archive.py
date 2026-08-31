#!/usr/bin/env python3
"""Standard-library audit of a Goal5798 formal evidence archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import statistics
import tarfile


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read_json(archive: tarfile.TarFile, name: str) -> dict[str, object]:
    member = archive.getmember(name)
    stream = archive.extractfile(member)
    if stream is None:
        raise RuntimeError(f"archive member has no bytes: {name}")
    value = json.loads(stream.read())
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON member is not an object: {name}")
    return value


def read_bytes(archive: tarfile.TarFile, name: str) -> bytes:
    stream = archive.extractfile(archive.getmember(name))
    if stream is None:
        raise RuntimeError(f"archive member has no bytes: {name}")
    return stream.read()


def median(values: list[int | float]) -> int | float:
    if not values:
        raise RuntimeError("median requires a nonempty sample")
    return statistics.median(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    receipts: list[dict[str, object]] = []
    unsafe_members: list[str] = []
    with tarfile.open(args.archive, "r:gz") as archive:
        names = set()
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.name in names:
                unsafe_members.append(member.name)
            names.add(member.name)
        final_names = sorted(
            name for name in names
            if name.startswith("formal_result/") and name.endswith("/final_receipt.json"))
        for name in final_names:
            receipt = read_json(archive, name)
            claimed = receipt.pop("receipt_sha256", None)
            observed = digest(receipt)
            receipt["receipt_sha256"] = claimed
            receipt["_receipt_seal_reproduced"] = claimed == observed
            receipt["_archive_member"] = name
            receipts.append(receipt)
        controller_bytes = read_bytes(
            archive, "formal_result/controller_result.json")
        recount_bytes = read_bytes(archive, "artifacts/independent_recount.json")
        controller = json.loads(controller_bytes)
        recount = json.loads(recount_bytes)

    worker_ids = [str(row.get("worker_id")) for row in receipts]
    performance = [row for row in receipts if row.get("timing_eligible") is True]
    memory = [row for row in receipts if row.get("mode") == "MEMORY_SEPARATE_NON_TIMED"]
    grouped: dict[tuple[str, str, str], list[dict[str, object]]] = {}
    for row in performance:
        key = (str(row["task"]), str(row["mode"]), str(row["arm"]))
        grouped.setdefault(key, []).append(row)
    absolute_rows = []
    for (task, mode, arm), rows in sorted(grouped.items()):
        samples = [int(row["primary_sample_ns"]) for row in rows]
        absolute_rows.append({
            "task": task,
            "mode": mode,
            "arm": arm,
            "sample_count": len(samples),
            "median_complete_execute_ns": median(samples),
            "min_complete_execute_ns": min(samples),
            "max_complete_execute_ns": max(samples),
        })

    comparisons = []
    recount_by_id = {
        str(row["row_id"]): row for row in recount["comparison_rows"]
    }
    tasks_modes = sorted({(str(row["task"]), str(row["mode"])) for row in performance})
    for task, mode in tasks_modes:
        rtdl = {
            int(row["row_sample_index"]): int(row["primary_sample_ns"])
            for row in grouped[(task, mode, "D_RTDL_PUBLIC")]
        }
        for baseline, short in (
            ("A_DIRECT_CUDA_OPTIX", "A"),
            ("B_CURRENT_NVIDIA_PYOPTIX_COMPATIBLE_API", "B"),
        ):
            base = {
                int(row["row_sample_index"]): int(row["primary_sample_ns"])
                for row in grouped[(task, mode, baseline)]
            }
            if set(base) != set(rtdl):
                raise RuntimeError(f"paired sample indices differ: {task}/{mode}/{baseline}")
            ratios = [base[index] / rtdl[index] for index in sorted(base)]
            row_id = f"{task}__{mode}__{short}_OVER_D"
            observed_median = median(ratios)
            published = recount_by_id[row_id]
            comparisons.append({
                "row_id": row_id,
                "paired_sample_count": len(ratios),
                "median_ratio_baseline_over_rtdl": observed_median,
                "independent_recount_median_ratio": published["median_ratio"],
                "median_ratio_exact_match": observed_median == published["median_ratio"],
                "favors_rtdl": observed_median > 1.0,
            })

    memory_groups: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in memory:
        memory_groups.setdefault((str(row["task"]), str(row["arm"])), []).append(row)
    memory_rows = []
    for (task, arm), rows in sorted(memory_groups.items()):
        memory_rows.append({
            "task": task,
            "arm": arm,
            "sample_count": len(rows),
            "host_peak_rss_median_bytes": median([
                int(row["memory"]["host_peak_rss_bytes"]) for row in rows]),
            "gpu_steady_prepared_median_bytes": median([
                int(row["memory"]["gpu_process_steady_prepared_bytes"])
                for row in rows]),
            "gpu_sampled_peak_median_bytes": median([
                int(row["memory"]["gpu_process_sampled_peak_bytes"])
                for row in rows]),
        })

    result: dict[str, object] = {
        "schema": "rtdl.goal5798.raw_formal_archive_audit.v2",
        "status": "PASS",
        "standard_library_only": True,
        "imports_project_statistics_or_workers": False,
        "archive_path": args.archive.as_posix(),
        "archive_bytes": args.archive.stat().st_size,
        "archive_sha256": file_sha256(args.archive),
        "unsafe_or_duplicate_archive_member_count": len(unsafe_members),
        "worker_count": len(receipts),
        "unique_worker_count": len(set(worker_ids)),
        "performance_worker_count": len(performance),
        "memory_worker_count": len(memory),
        "correct_worker_count": sum(
            row.get("status") == "PASS"
            and row.get("correctness", {}).get("oracle_exact") is True
            for row in receipts),
        "receipt_seal_reproduction_count": sum(
            row["_receipt_seal_reproduced"] is True for row in receipts),
        "retry_count": controller["retry_count"],
        "resume_count": controller["resume_count"],
        "replacement_count": controller["replacement_count"],
        "dropped_row_count": controller["dropped_row_count"],
        "absolute_rows": absolute_rows,
        "comparison_rows": comparisons,
        "prepared_pyoptix_rows_favoring_rtdl": sum(
            row["favors_rtdl"] is True
            and "PREPARED_EXECUTION__B_OVER_D" in row["row_id"]
            for row in comparisons),
        "cold_pyoptix_rows_favoring_rtdl": sum(
            row["favors_rtdl"] is True
            and "COLD_FRESH_PROCESS__B_OVER_D" in row["row_id"]
            for row in comparisons),
        "memory_rows": memory_rows,
        "controller_result_file_sha256": hashlib.sha256(
            controller_bytes).hexdigest(),
        "controller_result_file_sha256_matches_published_recount": (
            hashlib.sha256(controller_bytes).hexdigest()
            == recount["controller_result_sha256"]),
        "independent_recount_file_sha256": hashlib.sha256(
            recount_bytes).hexdigest(),
        "published_recount_sha256": recount["recount_sha256"],
    }
    required = (
        result["unsafe_or_duplicate_archive_member_count"] == 0,
        result["worker_count"] == 318,
        result["unique_worker_count"] == 318,
        result["performance_worker_count"] == 288,
        result["memory_worker_count"] == 30,
        result["correct_worker_count"] == 318,
        result["receipt_seal_reproduction_count"] == 318,
        all(row["median_ratio_exact_match"] for row in comparisons),
        result["controller_result_file_sha256_matches_published_recount"] is True,
        result["retry_count"] == result["resume_count"]
        == result["replacement_count"] == result["dropped_row_count"] == 0,
    )
    if not all(required):
        result["status"] = "FAIL"
    unsigned = dict(result)
    result["audit_sha256"] = digest(unsigned)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": result["status"],
        "archive_sha256": result["archive_sha256"],
        "worker_count": result["worker_count"],
        "prepared_pyoptix_rows_favoring_rtdl": (
            result["prepared_pyoptix_rows_favoring_rtdl"]),
        "audit_sha256": result["audit_sha256"],
    }, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
