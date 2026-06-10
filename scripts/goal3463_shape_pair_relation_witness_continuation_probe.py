from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "full_overlay_area_claim_authorized": False,
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    left_polygons = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_polygons = tuple(chains_to_polygons(load_cdb(args.right_cdb)))
    print(
        f"[goal3463] loaded left={len(left_polygons)} right={len(right_polygons)}",
        flush=True,
    )

    relation_start = time.perf_counter()
    with prepare_rayjoin_optix_shape_pair_active_count(
        right_polygons,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3463 relation witness continuation probe.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_polygons)
        with prepared.active_relation_device_columns(
            packed_left,
            max_rows=int(args.max_rows),
        ) as columns:
            cp.cuda.Stream.null.synchronize()
            relation_sec = time.perf_counter() - relation_start
            print(
                f"[goal3463] relation columns rows={int(columns.row_count)} relation_sec={relation_sec:.6f}",
                flush=True,
            )
            witness_start = time.perf_counter()
            witness = rt.shape_pair_relation_witness_cupy(columns)
            cp.cuda.Stream.null.synchronize()
            witness_sec = time.perf_counter() - witness_start
            witness_metadata = witness.to_metadata()
            ids = columns.as_cupy_columns()
            segment_count = int(cp.sum(ids["requires_segment_intersection"]).get())
            containment_count = int(cp.sum(ids["requires_point_containment"]).get())
            witness_kind = cp.asnumpy(witness.witness_kind).tolist()
            left_boundary = cp.asnumpy(witness.left_boundary_ordinal).tolist()
            right_boundary = cp.asnumpy(witness.right_boundary_ordinal).tolist()
            segment_t = cp.asnumpy(witness.segment_t).tolist()
            segment_u = cp.asnumpy(witness.segment_u).tolist()
            left_ids = cp.asnumpy(ids["left_id"]).tolist()
            right_ids = cp.asnumpy(ids["right_id"]).tolist()
            sample = [
                {
                    "left_id": int(left_id),
                    "right_id": int(right_id),
                    "witness_kind": int(kind),
                    "left_boundary_ordinal": int(left_edge),
                    "right_boundary_ordinal": int(right_edge),
                    "segment_t": float(t),
                    "segment_u": float(u),
                }
                for left_id, right_id, kind, left_edge, right_edge, t, u in zip(
                    left_ids,
                    right_ids,
                    witness_kind,
                    left_boundary,
                    right_boundary,
                    segment_t,
                    segment_u,
                )
            ][: int(args.sample_limit)]
            columns_metadata = columns.to_metadata()

    kind_counts = {str(key): int(value) for key, value in witness_metadata["witness_kind_counts"].items()}
    segment_witness_count = int(kind_counts.get("1", 0))
    containment_witness_count = int(kind_counts.get("2", 0)) + int(kind_counts.get("3", 0))
    unresolved_witness_count = int(kind_counts.get("0", 0)) + int(kind_counts.get("4", 0)) + int(kind_counts.get("5", 0))
    segment_rows_have_segment_witness = segment_witness_count == segment_count
    containment_rows_have_containment_witness = containment_witness_count == containment_count
    all_rows_have_witness = bool(witness_metadata["all_rows_have_witness"]) and unresolved_witness_count == 0
    print(
        "[goal3463] "
        f"kinds={kind_counts} segment_flags={segment_count} containment_flags={containment_count} "
        f"witness_sec={witness_sec:.6f} all_rows_have_witness={all_rows_have_witness}",
        flush=True,
    )

    return {
        "schema": "rtdl.goal3463.shape_pair_relation_witness_continuation.v1",
        "goal": 3463,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "left_shape_count": len(left_polygons),
        "right_shape_count": len(right_polygons),
        "row_count": int(sum(kind_counts.values())),
        "segment_flag_count": segment_count,
        "containment_flag_count": containment_count,
        "witness_kind_counts": kind_counts,
        "segment_rows_have_segment_witness": segment_rows_have_segment_witness,
        "containment_rows_have_containment_witness": containment_rows_have_containment_witness,
        "all_rows_have_witness": all_rows_have_witness,
        "unresolved_witness_count": unresolved_witness_count,
        "relation_columns_sec": relation_sec,
        "witness_continuation_sec": witness_sec,
        "witness_metadata": witness_metadata,
        "relation_metadata_geometry_payload_device_resident": bool(
            columns_metadata["runtime"]["geometry_payload"]["device_resident"]
        ),
        "relation_metadata_ordinal_columns_device_resident": bool(
            columns_metadata["runtime"]["ordinal_columns"]["device_resident"]
        ),
        "witness_sample": sample,
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3463 generic shape-pair relation witness continuation probe.")
    parser.add_argument(
        "--left-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--sample-limit", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if (
        not payload["all_rows_have_witness"]
        or not payload["segment_rows_have_segment_witness"]
        or not payload["containment_rows_have_containment_witness"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
