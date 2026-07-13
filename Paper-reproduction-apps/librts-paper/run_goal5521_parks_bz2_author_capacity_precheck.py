from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

from run_exact_point_contains_count_gate import _sha256, parse_author_output


GEOMETRY_MEMBER = "PPoPPAE/datasets/polygons/parks.bz2.wkt"
QUERY_MEMBER = "PPoPPAE/datasets/queries/range-contains_queries_50000/parks.bz2.wkt"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-target", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--serialize-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--author-binary",
        type=Path,
        default=Path("/workspace/librts-ae/SpatialQueryBenchmark/build/query"),
    )
    parser.add_argument("--ae-root", type=Path, default=Path("/workspace/librts-ae"))
    args = parser.parse_args()

    extraction = json.loads(args.extraction.read_text(encoding="utf-8"))
    members = {
        item["relative_path"]: item
        for item in extraction["extraction"]["selected_members"]
    }
    geometry = args.base_target / GEOMETRY_MEMBER
    query = args.base_target / QUERY_MEMBER
    if _sha256(geometry) != members[GEOMETRY_MEMBER]["sha256"]:
        raise ValueError("parks.bz2 geometry SHA-256 mismatch")
    if _sha256(query) != members[QUERY_MEMBER]["sha256"]:
        raise ValueError("parks.bz2 50K query SHA-256 mismatch")

    args.serialize_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(args.author_binary),
        "-geom",
        str(geometry),
        "-query",
        str(query),
        "-serialize",
        str(args.serialize_dir),
        "-query_type",
        "range-contains",
        "-index_type",
        "rtspatial",
        "-load_factor",
        "0.0001",
    ]
    environment = os.environ.copy()
    deps_lib = str(args.ae_root / "deps" / "lib")
    environment["LD_LIBRARY_PATH"] = deps_lib + (
        ":" + environment["LD_LIBRARY_PATH"] if environment.get("LD_LIBRARY_PATH") else ""
    )
    completed = subprocess.run(command, capture_output=True, text=True, env=environment, check=False)
    combined = completed.stdout + "\n" + completed.stderr
    capacity_failure = any(
        token in combined
        for token in ("cudaErrorMemoryAllocation", "bad_alloc", "out of memory")
    )
    if completed.returncode == 0:
        author = parse_author_output(completed.stdout)
        status = "parks_bz2_author_50000_completed"
    else:
        author = None
        status = (
            "parks_bz2_author_50000_capacity_failure"
            if capacity_failure
            else "parks_bz2_author_50000_unclassified_failure"
        )
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5521_parks_bz2_author_capacity_precheck.v1",
        "status": status,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "author": author,
        "capacity_failure": capacity_failure,
        "input_identity": {
            "geometry_sha256": members[GEOMETRY_MEMBER]["sha256"],
            "query_sha256": members[QUERY_MEMBER]["sha256"],
            "exact_archive_members": True,
        },
        "decision": {
            "authorize_rtdl_cache_and_matrix": completed.returncode == 0,
            "stop_before_rtdl_if_author_fails": completed.returncode != 0,
        },
        "claim_boundary": {
            "author_capacity_precheck_only": True,
            "rtdl_executed": False,
            "matrix_completed": False,
            "performance_ratio_authorized": False,
            "paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if completed.returncode == 0 or capacity_failure else 1


if __name__ == "__main__":
    raise SystemExit(main())
