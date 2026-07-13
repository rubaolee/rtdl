from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


PINNED_COMMITS = {
    "ae": "d605fe1bd5708cbf3c457a3a9698e0cc7bcdc14b",
    "rtspatial": "7c54c181b1058c87768767998c00e225cc58666e",
    "rayjoin": "2151f56d09cbcfd4edbff259d97ac3123705411b",
    "spatial_query_benchmark": "9140ad997519713bb5fdceba639a357afa4609ad",
}
RESULT_RE = re.compile(r"^Results\s+(?P<count>\d+)\s*$", re.MULTILINE)


def _run(command: list[str]) -> str:
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _commit(path: Path) -> str:
    return _run(["git", "-C", str(path), "rev-parse", "HEAD"])


def _parse_result_count(path: Path) -> int:
    match = RESULT_RE.search(path.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError(f"author smoke log lacks Results count: {path}")
    return int(match.group("count"))


def build_summary(
    *,
    ae_root: Path,
    query_binary: Path,
    pip_binary: Path,
    query_smoke_log: Path,
    pip_smoke_log: Path,
) -> dict[str, object]:
    commits = {
        "ae": _commit(ae_root),
        "rtspatial": _commit(ae_root / "RTSpatial"),
        "rayjoin": _commit(ae_root / "RayJoin"),
        "spatial_query_benchmark": _commit(ae_root / "SpatialQueryBenchmark"),
    }
    commit_matches = {
        name: commits[name] == expected for name, expected in PINNED_COMMITS.items()
    }
    query_count = _parse_result_count(query_smoke_log)
    pip_count = _parse_result_count(pip_smoke_log)
    matched = all(commit_matches.values()) and query_count == 5 and pip_count == 4
    gpu_line = _run(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    ).splitlines()[0]
    return {
        "schema": "rtdl.paper_reproduction.librts.author_pod_environment.v1",
        "status": (
            "pinned_author_gpu_query_and_pip_smoke_passed"
            if matched
            else "pinned_author_gpu_environment_mismatch"
        ),
        "matched": matched,
        "provenance": {
            "commits": commits,
            "expected_commits": PINNED_COMMITS,
            "commit_matches": commit_matches,
        },
        "environment": {
            "gpu_csv": gpu_line,
            "cmake": _run(["cmake", "--version"]).splitlines()[0],
            "cuda": _run(["/usr/local/cuda/bin/nvcc", "--version"]).splitlines()[-1],
            "benchmark_host_compiler": "gcc/g++ 12",
            "geos": "3.11.0 private AE prefix",
            "optix": "8.0 bundled AE SDK",
            "embree_used": False,
        },
        "binaries": {
            "query": {
                "path": str(query_binary),
                "size_bytes": query_binary.stat().st_size,
                "sha256": _sha256(query_binary),
            },
            "pip": {
                "path": str(pip_binary),
                "size_bytes": pip_binary.stat().st_size,
                "sha256": _sha256(pip_binary),
            },
        },
        "smoke": {
            "query_point_contains_result_count": query_count,
            "query_expected_count": 5,
            "pip_result_count": pip_count,
            "pip_expected_count": 4,
            "counts_match": query_count == 5 and pip_count == 4,
            "timing_fields_diagnostic_only": True,
        },
        "claim_boundary": {
            "author_gpu_environment_ready_for_exact_input_gates": matched,
            "exact_archive_download_completed": False,
            "exact_inputs_identified": False,
            "paper_figure_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_matrix_gpu_capacity_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--query-binary", type=Path, required=True)
    parser.add_argument("--pip-binary", type=Path, required=True)
    parser.add_argument("--query-smoke-log", type=Path, required=True)
    parser.add_argument("--pip-smoke-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_summary(
        ae_root=args.ae_root.resolve(),
        query_binary=args.query_binary.resolve(),
        pip_binary=args.pip_binary.resolve(),
        query_smoke_log=args.query_smoke_log.resolve(),
        pip_smoke_log=args.pip_smoke_log.resolve(),
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
