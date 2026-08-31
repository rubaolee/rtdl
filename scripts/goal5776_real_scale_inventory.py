"""Freeze the Goal5776 nine-app real-scale input/admission inventory.

This is deliberately an admission tool, not a benchmark runner.  It rehashes
the immutable Goal5634 seven-app data tree, records the public Triangle and
particle sources, and refuses to describe a lane as performance-ready when
the current V4 front door still consumes only a tiny fixture or would require
an unbounded host materialization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


EXPECTED_GOAL5634_TREE = (
    "21156f9c09eae177f09aa9fa3f06270ee9cd08f60e53bb2ea53ebf50d71fcf14"
)
EXPECTED_MANIFEST_FILE_COUNT = 30
PARTICLE_COMMIT = "5cfe63fed227c238905a8f24082b59b5d3160966"


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _goal5634_files(root: Path) -> dict[str, dict[str, object]]:
    manifest_path = root / "GOAL5634_DATA_MANIFEST.json"
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if raw.get("data_tree_digest") != EXPECTED_GOAL5634_TREE:
        raise RuntimeError("unexpected Goal5634 data-tree identity")
    rows = raw.get("files")
    if not isinstance(rows, list) or len(rows) != EXPECTED_MANIFEST_FILE_COUNT:
        raise RuntimeError("unexpected Goal5634 manifest membership")
    indexed: dict[str, dict[str, object]] = {}
    for row in rows:
        relative = str(row["path"])
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if size != int(row["size_bytes"]):
            raise RuntimeError(f"size mismatch: {relative}")
        observed = _sha(path)
        if observed != row["sha256"]:
            raise RuntimeError(f"sha256 mismatch: {relative}")
        indexed[relative] = {
            "path": str(path.resolve()), "size_bytes": size,
            "sha256": observed,
        }
    return indexed


def _required(files: dict[str, dict[str, object]], name: str):
    if name not in files:
        raise RuntimeError(f"required data member absent: {name}")
    return files[name]


def build_inventory(data_root: Path, particle_repo: Path | None) -> dict[str, object]:
    files = _goal5634_files(data_root)
    particle = None
    if particle_repo is not None:
        # The public RTxAdvection repository spells this directory
        # ``microfludics``; preserve the source spelling in the frozen path.
        micro = particle_repo / "dataset/microfludics/solution_4.vtu"
        porous = particle_repo / "dataset/porousMedia/solution_porousmedia.vtu"
        if not micro.is_file() or not porous.is_file():
            raise FileNotFoundError("Arkade/RTxAdvection particle VTU files missing")
        particle = {
            "repository": str(particle_repo.resolve()),
            "pinned_commit": PARTICLE_COMMIT,
            "microfluidics": {
                "path": str(micro.resolve()), "size_bytes": micro.stat().st_size,
                "sha256": _sha(micro), "points": 314_587, "cells": 1_659_240,
            },
            "porous_media": {
                "path": str(porous.resolve()), "size_bytes": porous.stat().st_size,
                "sha256": _sha(porous), "points": 186_650, "cells": 819_726,
            },
        }

    rows = [
        {
            "app": "RayDB", "workload": "SSB-SF10-Q1.1 packet",
            "scale": {"relational_rows": 59_986_052},
            "members": [_required(files, "raydb/q11/data.bin"),
                        _required(files, "raydb/q11/packet.json"),
                        _required(files, "raydb/q11/expected_rows.json")],
            "input_provenance": "deterministic SSB SF10 recipe; not exact paper bytes",
            "v2_reuse": "existing frozen Goal5634 columnar packet route",
            "v4_admission": "blocked_pending_columnar_row_to_event_adapter",
            "why_not_ready": "current V4 front door hard-codes bounded tiny rows",
        },
        {
            "app": "LibRTS", "workload": "parks.bz2 point/range contains",
            "scale": {"indexed_boxes": 11_544_398, "query_count": 100_000},
            "members": [_required(files, "librts/parks/cache/parks_bz2.npz"),
                        _required(files, "librts/parks/queries/point_contains_100000.wkt"),
                        _required(files, "librts/parks/queries/range_contains_100000.wkt")],
            "input_provenance": "public LibRTS reproduction corpus",
            "v2_reuse": "existing parks cache and prepared OptiX AABB index",
            "v4_admission": "blocked_pending_bounded_streaming_output_contract",
            "why_not_ready": "Cartesian capacity indexed*queries is illegal at this scale",
        },
        {
            "app": "RTNN", "workload": "KITTI-derived Level-B fixed-radius KNN",
            "scale": {"search_points": 12_000_000, "queries": 4096, "k": 4},
            "members": [_required(files, "rtnn/packet/search.xyz"),
                        _required(files, "rtnn/packet/queries.xyz"),
                        _required(files, "rtnn/packet/manifest.json")],
            "input_provenance": "same-source deterministic recipe; not exact paper bytes",
            "v2_reuse": "existing prepared direct-OptiX bounded-selection route",
            "v4_admission": "ready_after_binary32_columnar_loader_and_untimed_smoke",
            "why_not_ready": None,
        },
        {
            "app": "X-HD", "workload": "Stanford Dragon to Happy Buddha",
            "scale": {"source_points": 437_645, "target_points": 543_652},
            "members": [_required(files, "x_hd/dragon_vrip.ply"),
                        _required(files, "x_hd/happy_vrip.ply")],
            "input_provenance": "public Stanford full-resolution meshes",
            "v2_reuse": "existing exact-witness prepared true-OptiX route",
            "v4_admission": "ready_after_ply_loader_and_capacity_smoke",
            "why_not_ready": None,
        },
        {
            "app": "RT-DBSCAN", "workload": "largest declared admissible 3D case",
            "scale": {"point_count": 4096, "hard_bound": 4096},
            "members": [],
            "input_provenance": "must freeze a public/authored 4096-point slice before timing",
            "v2_reuse": "existing bounded prepared OptiX+Numba grouped route",
            "v4_admission": "blocked_pending_exact_dataset_and_slice_identity",
            "why_not_ready": "current proven route is explicitly bounded to <=4096",
        },
        {
            "app": "RayJoin", "workload": "Section-5.7 county x zipcode top4",
            "scale": {"county_edges": 1_705_027, "zipcode_edges": 9_982_960},
            "members": [_required(files, "rayjoin/top4_county.cdb"),
                        _required(files, "rayjoin/top4_zipcode.cdb")],
            "input_provenance": "public ArcGIS same-source packed CDB pair",
            "v2_reuse": "Goal4970-5039 packed CDB and six-batch lifecycle",
            "v4_admission": "blocked_pending_packed_streaming_candidate_adapter",
            "why_not_ready": "current V4 fixture uses capacity=4096 and Python row tuples",
        },
        {
            "app": "RT-BarnesHut", "workload": "author prepared hierarchy/force state",
            "scale": {"bodies": 32_768, "hierarchy_nodes": 1486},
            "members": [_required(files, "rt_barneshut/prepared_arrays.json"),
                        _required(files, "rt_barneshut/expected_forces.txt")],
            "input_provenance": "author device-state export and exact force output",
            "v2_reuse": "existing aggregate-hierarchy prepared true-OptiX route",
            "v4_admission": "ready_after_author_state_adapter_and_untimed_smoke",
            "why_not_ready": None,
        },
        {
            "app": "Triangle Counting", "workload": "three established SNAP datasets",
            "scale": {"datasets": ["com-dblp", "cit-Patents", "soc-LiveJournal1"]},
            "members": [],
            "input_provenance": "official SNAP edge lists; author counts already frozen",
            "v2_reuse": "Goal5735/5741 V2-direct true-OptiX lanes",
            "v4_admission": "blocked_pending_portable_snap_payloads",
            "why_not_ready": "edge files are not present in current data tree",
        },
        {
            "app": "Particle Tracking", "workload": "author microfluidics mesh point-location step",
            "scale": {"mesh_points": 314_587, "mesh_cells": 1_659_240,
                      "queries": 5000, "paper_steps": 50_000},
            "members": [] if particle is None else [particle["microfluidics"]],
            "input_provenance": "public author repository at exact commit",
            "v2_reuse": "static-triangle true-OptiX closest-hit front door",
            "v4_admission": "blocked_pending_vtu_mesh_converter_and_generalized_geometry_owner",
            "why_not_ready": "current V4 fixture is two tetrahedra and one transition, not full advection",
        },
    ]
    return {
        "schema": "rtdl.goal5776.nine_app_real_scale_inventory.v1",
        "goal": 5776,
        "data_tree": {
            "root": str(data_root.resolve()),
            "sha256": EXPECTED_GOAL5634_TREE,
            "manifest_file_count": len(files),
        },
        "particle_repository": particle,
        "apps": rows,
        "app_count": len(rows),
        "admission_summary": {
            "ready_after_loader_or_smoke": sum(
                row["v4_admission"].startswith("ready_after") for row in rows),
            "blocked_requires_adapter_or_data": sum(
                row["v4_admission"].startswith("blocked") for row in rows),
            "formal_performance_ready": 0,
        },
        "claim_boundary": {
            "performance_result_exists": False,
            "pod_authorized": False,
            "full_paper_input_claimed_for_every_app": False,
            "largest_admissible_scale_may_be_relabelled_as_paper_scale": False,
            "tiny_fixture_may_be_repeated_to_claim_real_scale": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    parser.add_argument("--particle-repo", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = build_inventory(args.data_root.resolve(), (
        None if args.particle_repo is None else args.particle_repo.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps(result["admission_summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
