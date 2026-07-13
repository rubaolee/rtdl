from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import tempfile
from pathlib import Path

from librts_author_pip_compat import run_author_compatible_pip_rows
from librts_reproduction import APP_DIR
from run_same_input_pip_gate import (
    AE_COMMIT,
    BENCHMARK_COMMIT,
    RTSPATIAL_COMMIT,
    parse_author_output,
    verify_commit,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_row_sha256(rows: list[list[int]]) -> str:
    digest = hashlib.sha256()
    for point_id, polygon_id in rows:
        digest.update(f"{point_id},{polygon_id}\n".encode("ascii"))
    return digest.hexdigest()


def _load_author_rows(path: Path) -> list[list[int]]:
    rows: list[list[int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        values = line.split(",")
        if len(values) != 2:
            raise ValueError(f"invalid author PIP row: {line!r}")
        rows.append([int(values[0]), int(values[1])])
    rows.sort()
    return rows


def build_summary(
    *,
    polygons_path: Path,
    points_path: Path,
    dataset_manifest_path: Path,
    author_stdout: str,
    author_command: list[str],
    instrumented_author_stdout: str,
    instrumented_author_command: list[str],
    author_rows_path: Path,
    environment_label: str,
    gpu_label: str,
) -> dict[str, object]:
    dataset = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
    author = parse_author_output(author_stdout)
    instrumented_author = parse_author_output(instrumented_author_stdout)
    author_rows = _load_author_rows(author_rows_path)
    rtdl = run_author_compatible_pip_rows(
        polygons_path=polygons_path,
        points_path=points_path,
        backend="optix",
    )
    rows = rtdl.pop("candidate_id_rows")
    row_hash = _canonical_row_sha256(rows)
    author_row_hash = _canonical_row_sha256(author_rows)
    matched = bool(
        dataset["identity_level"] == "level_b_public_source_representative_subset"
        and int(dataset["polygon_count"]) == int(rtdl["polygon_count"])
        and int(dataset["query_count"]) == int(rtdl["point_count"])
        and int(author["result_count"]) == int(rtdl["result_count"])
        and int(instrumented_author["result_count"]) == int(author["result_count"])
        and len(author_rows) == int(author["result_count"])
        and author_rows == rows
        and rtdl["rt_core_accelerated"]
        and not rtdl["native_engine_customization"]
    )
    rtdl["canonical_row_sha256"] = row_hash
    rtdl["candidate_rows_materialized_for_hash"] = len(rows)
    return {
        "schema": "rtdl.paper_reproduction.librts.representative_pip.v1",
        "status": (
            "level_b_representative_same_input_pip_relation_matched"
            if matched
            else "level_b_representative_same_input_pip_relation_mismatch"
        ),
        "matched": matched,
        "environment": {
            "label": environment_label,
            "host": platform.node(),
            "platform": platform.platform(),
            "gpu": gpu_label,
            "performance_evidence_authorized": False,
        },
        "dataset": {
            **dataset,
            "manifest_path": str(dataset_manifest_path),
            "polygons_path": str(polygons_path),
            "polygons_sha256": _sha256(polygons_path),
            "points_path": str(points_path),
            "points_sha256": _sha256(points_path),
            "same_files_passed_to_author_and_rtdl": True,
        },
        "author": {
            "implementation": "AE-pinned SpatialQueryBenchmark integrated RTSpatial PIP",
            "backend": "optix",
            "command": author_command,
            "stdout": author_stdout,
            **author,
            "pair_rows_exposed": False,
        },
        "instrumented_author_comparator": {
            "implementation": "AE-pinned author PIP plus app-owned row-dump instrumentation",
            "command": instrumented_author_command,
            "stdout": instrumented_author_stdout,
            **instrumented_author,
            "pair_rows_exposed": True,
            "row_count": len(author_rows),
            "canonical_row_sha256": author_row_hash,
            "instrumentation_only_copies_existing_result_queue": True,
            "instrumentation_changes_predicate_or_queue_append": False,
        },
        "rtdl": rtdl,
        "comparison": {
            "author_result_count": int(author["result_count"]),
            "instrumented_author_result_count": int(instrumented_author["result_count"]),
            "rtdl_result_count": int(rtdl["result_count"]),
            "count_equal": int(author["result_count"]) == int(rtdl["result_count"]),
            "author_pair_rows_available_via_app_instrumentation": True,
            "canonical_row_sha256_equal": author_row_hash == row_hash,
            "pair_rows_equal": author_rows == rows,
        },
        "claim_boundary": {
            "level_b_representative_same_input_relation_agreement": matched,
            "exact_paper_dataset_reproduction_claimed": False,
            "author_pair_relation_agreement_claimed": matched,
            "author_pair_relation_scope": "app-instrumented representative fixture only",
            "figure12_reproduction_claimed": False,
            "ray_multicast_equivalence_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
            "robust_exact_arithmetic_pip_claimed": False,
            "librts_specific_rtdl_primitive_added": False,
            "embree_evidence_used": False,
        },
    }


def run_gate(
    *,
    author_exec: Path,
    instrumented_author_exec: Path,
    ae_source: Path,
    rtspatial_source: Path,
    benchmark_source: Path,
    polygons_path: Path,
    points_path: Path,
    dataset_manifest_path: Path,
    environment_label: str,
    gpu_label: str,
) -> dict[str, object]:
    verify_commit(ae_source, AE_COMMIT, label="AE")
    verify_commit(rtspatial_source, RTSPATIAL_COMMIT, label="RTSpatial")
    verify_commit(
        benchmark_source,
        BENCHMARK_COMMIT,
        label="SpatialQueryBenchmark",
    )
    command = [
        str(author_exec),
        f"--geom={polygons_path}",
        f"--query={points_path}",
        "--query_type=pip",
        "--index_type=rtspatial",
        "--load_factor=1.0",
        "--warmup=0",
        "--repeat=1",
        "--serialize=",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            f"author PIP executable failed with exit {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )
    instrumented_command = [str(instrumented_author_exec), *command[1:]]
    with tempfile.TemporaryDirectory() as temporary:
        author_rows_path = Path(temporary) / "author_rows.csv"
        environment = dict(os.environ)
        environment["LIBRTS_PIP_ROW_DUMP"] = str(author_rows_path)
        instrumented = subprocess.run(
            instrumented_command,
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        if instrumented.returncode != 0:
            raise RuntimeError(
                "instrumented author PIP executable failed with exit "
                f"{instrumented.returncode}: {instrumented.stderr.strip()}"
            )
        return build_summary(
            polygons_path=polygons_path,
            points_path=points_path,
            dataset_manifest_path=dataset_manifest_path,
            author_stdout=completed.stdout,
            author_command=command,
            instrumented_author_stdout=instrumented.stdout,
            instrumented_author_command=instrumented_command,
            author_rows_path=author_rows_path,
            environment_label=environment_label,
            gpu_label=gpu_label,
        )


def main() -> int:
    data_dir = (
        APP_DIR
        / "data"
        / "representative"
        / "goal5466_blockgroups_simple64_100k"
    )
    parser = argparse.ArgumentParser(
        description="LibRTS Level-B representative same-input PIP gate"
    )
    parser.add_argument("--author-exec", required=True, type=Path)
    parser.add_argument("--instrumented-author-exec", required=True, type=Path)
    parser.add_argument("--ae-source", required=True, type=Path)
    parser.add_argument("--rtspatial-source", required=True, type=Path)
    parser.add_argument("--benchmark-source", required=True, type=Path)
    parser.add_argument(
        "--polygons",
        type=Path,
        default=data_dir / "blockgroups_simple64_arcgis.wkt",
    )
    parser.add_argument(
        "--points",
        type=Path,
        default=data_dir / "blockgroups_simple64_queries_seed0_100k.wkt",
    )
    parser.add_argument("--dataset-manifest", type=Path, default=data_dir / "manifest.json")
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--gpu-label", default="unspecified")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = run_gate(
        author_exec=args.author_exec.resolve(),
        instrumented_author_exec=args.instrumented_author_exec.resolve(),
        ae_source=args.ae_source.resolve(),
        rtspatial_source=args.rtspatial_source.resolve(),
        benchmark_source=args.benchmark_source.resolve(),
        polygons_path=args.polygons.resolve(),
        points_path=args.points.resolve(),
        dataset_manifest_path=args.dataset_manifest.resolve(),
        environment_label=args.environment_label,
        gpu_label=args.gpu_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
