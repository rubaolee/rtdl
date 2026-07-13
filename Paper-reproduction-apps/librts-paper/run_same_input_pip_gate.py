from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

from librts_reproduction import APP_DIR, run_pip


AE_COMMIT = "d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b"
RTSPATIAL_COMMIT = "7c54c181b1058c87768767998c00e225cc58666e"
BENCHMARK_COMMIT = "9140ad997519713bb5fdceba639a357afa4609ad"
AUTHOR_RESULTS_RE = re.compile(r"^Results\s+(?P<count>[0-9]+)$", re.MULTILINE)
AUTHOR_LOAD_RE = re.compile(r"^Loading Time\s+(?P<value>[0-9.eE+-]+)\s+ms$", re.MULTILINE)
AUTHOR_QUERY_RE = re.compile(r"^Query Time\s+(?P<value>[0-9.eE+-]+)\s+ms$", re.MULTILINE)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_commit(path: Path, expected: str, *, label: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    actual = completed.stdout.strip()
    if completed.returncode != 0 or actual != expected:
        raise RuntimeError(
            f"{label} checkout does not match pin: expected {expected}, "
            f"got {actual or '<unavailable>'}"
        )
    return actual


def parse_author_output(stdout: str) -> dict[str, object]:
    count_match = AUTHOR_RESULTS_RE.search(stdout)
    if count_match is None:
        raise ValueError("author PIP output lacks Results count")
    load_match = AUTHOR_LOAD_RE.search(stdout)
    query_match = AUTHOR_QUERY_RE.search(stdout)
    return {
        "result_count": int(count_match.group("count")),
        "loading_ms_diagnostic_only": (
            float(load_match.group("value")) if load_match else None
        ),
        "query_ms_diagnostic_only": (
            float(query_match.group("value")) if query_match else None
        ),
    }


def build_summary(
    *,
    polygons_path: Path,
    points_path: Path,
    expected_path: Path,
    author_stdout: str,
    author_command: list[str],
    ae_commit: str = AE_COMMIT,
    rtspatial_commit: str = RTSPATIAL_COMMIT,
    benchmark_commit: str = BENCHMARK_COMMIT,
    environment_label: str = "unspecified",
    gpu_label: str = "unspecified",
) -> dict[str, object]:
    author = parse_author_output(author_stdout)
    rtdl = run_pip(
        polygons_path=polygons_path,
        points_path=points_path,
        expected_path=expected_path,
        backend="optix",
    )
    expected_count = len(rtdl["expected_rows"])
    matched = bool(
        rtdl["matched"]
        and rtdl["rt_core_accelerated"]
        and int(author["result_count"]) == expected_count
        and int(rtdl["result_count"]) == expected_count
        and rtdl["polygon_refine_discriminating"]
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.same_input_pip.v1",
        "status": (
            "bounded_same_input_refined_pip_count_matched"
            if matched
            else "bounded_same_input_refined_pip_count_mismatch"
        ),
        "matched": matched,
        "environment": {
            "label": environment_label,
            "host": platform.node(),
            "platform": platform.platform(),
            "gpu": gpu_label,
            "performance_evidence_authorized": False,
        },
        "provenance": {
            "ae_commit": ae_commit,
            "rtspatial_commit": rtspatial_commit,
            "spatial_query_benchmark_commit": benchmark_commit,
            "pip_source": "SpatialQueryBenchmark/src/query/rtspatial/pip_query.cu",
            "pip_callback": "SpatialQueryBenchmark/src/query/rtspatial/pip_handler.h",
        },
        "input_identity": {
            "same_files_passed_to_author_and_rtdl": True,
            "polygons_path": str(polygons_path),
            "polygons_sha256": _sha256(polygons_path),
            "points_path": str(points_path),
            "points_sha256": _sha256(points_path),
            "expected_path": str(expected_path),
            "expected_sha256": _sha256(expected_path),
        },
        "author": {
            "implementation": "AE-pinned SpatialQueryBenchmark integrated RTSpatial PIP",
            "backend": "optix",
            "command": author_command,
            "stdout": author_stdout,
            **author,
            "pair_rows_exposed": False,
            "algorithm": "polygon MBR SpatialIndex candidates plus device pnpoly callback",
        },
        "rtdl": rtdl,
        "expected": {
            "result_count": expected_count,
            "candidate_id_rows": rtdl["expected_rows"],
            "bbox_only_candidate_count": rtdl["bbox_only_candidate_count"],
        },
        "claim_boundary": {
            "bounded_same_input_refined_pip_count_agreement": matched,
            "rtdl_exact_rows_match_fixture": rtdl["matched"],
            "author_pair_relation_agreement_claimed": False,
            "paper_dataset_or_figure_reproduction_claimed": False,
            "figure12_performance_claimed": False,
            "ray_multicast_equivalence_claimed": False,
            "author_performance_parity_claimed": False,
            "full_paper_reproduction_claimed": False,
            "embree_evidence_used": False,
            "librts_specific_rtdl_primitive_added": False,
        },
    }


def run_gate(
    *,
    author_exec: Path,
    ae_source: Path,
    rtspatial_source: Path,
    benchmark_source: Path,
    polygons_path: Path,
    points_path: Path,
    expected_path: Path,
    environment_label: str,
    gpu_label: str,
) -> dict[str, object]:
    ae_commit = verify_commit(ae_source, AE_COMMIT, label="AE")
    rtspatial_commit = verify_commit(
        rtspatial_source, RTSPATIAL_COMMIT, label="RTSpatial"
    )
    benchmark_commit = verify_commit(
        benchmark_source, BENCHMARK_COMMIT, label="SpatialQueryBenchmark"
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
    return build_summary(
        polygons_path=polygons_path,
        points_path=points_path,
        expected_path=expected_path,
        author_stdout=completed.stdout,
        author_command=command,
        ae_commit=ae_commit,
        rtspatial_commit=rtspatial_commit,
        benchmark_commit=benchmark_commit,
        environment_label=environment_label,
        gpu_label=gpu_label,
    )


def main() -> int:
    fixtures = APP_DIR / "data" / "fixtures"
    parser = argparse.ArgumentParser(description="LibRTS bounded same-input PIP gate")
    parser.add_argument("--author-exec", required=True, type=Path)
    parser.add_argument("--ae-source", required=True, type=Path)
    parser.add_argument("--rtspatial-source", required=True, type=Path)
    parser.add_argument("--benchmark-source", required=True, type=Path)
    parser.add_argument("--polygons", type=Path, default=fixtures / "tiny_pip_polygons.wkt")
    parser.add_argument("--points", type=Path, default=fixtures / "tiny_pip_points.wkt")
    parser.add_argument("--expected", type=Path, default=fixtures / "tiny_pip_expected.json")
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--gpu-label", default="unspecified")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = run_gate(
        author_exec=args.author_exec.resolve(),
        ae_source=args.ae_source.resolve(),
        rtspatial_source=args.rtspatial_source.resolve(),
        benchmark_source=args.benchmark_source.resolve(),
        polygons_path=args.polygons.resolve(),
        points_path=args.points.resolve(),
        expected_path=args.expected.resolve(),
        environment_label=args.environment_label,
        gpu_label=args.gpu_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
