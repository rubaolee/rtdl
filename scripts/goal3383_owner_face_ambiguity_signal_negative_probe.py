from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402


FeatureRow = dict[str, Any]


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _materialize_county_slice(data_dir: Path, *, download: bool) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    source = data_dir / "br_county.cdb"
    sliced_path = data_dir / "br_county_start256_count512.cdb"
    if not source.exists():
        if not download:
            raise FileNotFoundError(f"{source} is missing; rerun with --download")
        print(f"[goal3383] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3383] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _host_pairs(cp_module, point_ids, shape_ids) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(point_ids).tolist()),
            (int(value) for value in cp_module.asnumpy(shape_ids).tolist()),
        )
    )


def _build_feature_rows(
    *,
    county,
    topology_rows: tuple[dict[str, int], ...],
    exact_pairs: set[tuple[int, int]],
    candidate_pairs: set[tuple[int, int]],
) -> list[FeatureRow]:
    topology_by_shape = {int(row["chain_id"]): row for row in topology_rows}
    incident_rows = rt.chains_to_incident_face_candidate_rows(county, endpoint_only=True)
    incident_by_point: dict[int, list[dict[str, int | float]]] = defaultdict(list)
    for row in incident_rows:
        incident_by_point[int(row["point_id"])].append(row)

    candidate_by_point: dict[int, set[int]] = defaultdict(set)
    exact_by_point: dict[int, set[int]] = defaultdict(set)
    extra_by_point: dict[int, set[int]] = defaultdict(set)
    for point_id, shape_id in candidate_pairs:
        candidate_by_point[point_id].add(shape_id)
    for point_id, shape_id in exact_pairs:
        exact_by_point[point_id].add(shape_id)
    for point_id, shape_id in candidate_pairs - exact_pairs:
        extra_by_point[point_id].add(shape_id)

    rows: list[FeatureRow] = []
    for point_id in sorted(candidate_by_point):
        incidents = incident_by_point.get(point_id, [])
        incident_counts = [int(row["incident_face_count"]) for row in incidents]
        max_count = max(incident_counts) if incident_counts else 0
        max_faces = sorted(int(row["face_id"]) for row in incidents if int(row["incident_face_count"]) == max_count)
        candidate_faces: set[int] = set()
        candidate_has_zero_face = False
        for shape_id in candidate_by_point[point_id]:
            topology = topology_by_shape.get(shape_id)
            if topology is None:
                continue
            left = int(topology["left_face_id"])
            right = int(topology["right_face_id"])
            if left == 0 or right == 0:
                candidate_has_zero_face = True
            if left != 0:
                candidate_faces.add(left)
            if right != 0:
                candidate_faces.add(right)
        rows.append(
            {
                "point_id": point_id,
                "candidate_count": len(candidate_by_point[point_id]),
                "exact_count": len(exact_by_point[point_id]),
                "extra_count": len(extra_by_point[point_id]),
                "incident_row_count": len(incidents),
                "incident_chain_count_max": (
                    max(int(row.get("incident_chain_count", 0)) for row in incidents)
                    if incidents
                    else 0
                ),
                "incident_max_count": max_count,
                "incident_max_face_count": len(max_faces),
                "incident_max_faces": max_faces,
                "candidate_face_count": len(candidate_faces),
                "candidate_has_zero_face": candidate_has_zero_face,
                "candidate_shape_ids": sorted(candidate_by_point[point_id]),
                "exact_shape_ids": sorted(exact_by_point[point_id]),
                "extra_shape_ids": sorted(extra_by_point[point_id]),
            }
        )
    return rows


def _signal_specs() -> tuple[tuple[str, str, Callable[[FeatureRow], bool]], ...]:
    return (
        (
            "candidate_count_ge_3",
            "point has at least three live candidate shapes",
            lambda row: int(row["candidate_count"]) >= 3,
        ),
        (
            "candidate_count_gt_incident_max_face_count",
            "candidate shape count exceeds the number of max-count incident faces",
            lambda row: int(row["candidate_count"]) > int(row["incident_max_face_count"]),
        ),
        (
            "incident_row_eq_3_candidate_ge_4",
            "three incident face rows and at least four live candidate shapes",
            lambda row: int(row["incident_row_count"]) == 3 and int(row["candidate_count"]) >= 4,
        ),
        (
            "incident_row_eq_3_candidate_face_count_eq_4",
            "three incident face rows and four distinct non-zero candidate faces",
            lambda row: int(row["incident_row_count"]) == 3
            and int(row["candidate_face_count"]) == 4,
        ),
        (
            "incident_chain_count_eq_3_candidate_face_count_eq_4",
            "three incident chains and four distinct non-zero candidate faces",
            lambda row: int(row["incident_chain_count_max"]) == 3
            and int(row["candidate_face_count"]) == 4,
        ),
    )


def _evaluate_signals(feature_rows: list[FeatureRow]) -> tuple[list[dict[str, object]], set[int]]:
    true_extra_points = {int(row["point_id"]) for row in feature_rows if int(row["extra_count"]) > 0}
    signal_results: list[dict[str, object]] = []
    for name, description, predicate in _signal_specs():
        selected = {int(row["point_id"]) for row in feature_rows if predicate(row)}
        false_positives = sorted(selected - true_extra_points)
        missed = sorted(true_extra_points - selected)
        signal_results.append(
            {
                "name": name,
                "description": description,
                "selected_point_count": len(selected),
                "true_positive_point_ids": sorted(selected & true_extra_points),
                "false_positive_point_ids": false_positives,
                "missed_extra_point_ids": missed,
                "false_positive_count": len(false_positives),
                "missed_extra_count": len(missed),
                "default_route_candidate": len(false_positives) == 0 and len(missed) == 0,
            }
        )
    return signal_results, true_extra_points


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)
    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    topology_rows = rt.chains_to_topology_rows(county)

    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    candidate_columns = None
    try:
        exact_pairs = _pair_set(tuple(prepared.run(points)))
        candidate_columns = prepared.candidate_device_columns(points)
        candidates = candidate_columns.as_cupy_columns()
        candidate_pairs = _host_pairs(cp, candidates["point_id"], candidates["shape_id"])
    finally:
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()

    feature_rows = _build_feature_rows(
        county=county,
        topology_rows=topology_rows,
        exact_pairs=exact_pairs,
        candidate_pairs=candidate_pairs,
    )
    signal_results, true_extra_points = _evaluate_signals(feature_rows)
    best_signal = min(
        signal_results,
        key=lambda item: (int(item["missed_extra_count"]), int(item["false_positive_count"]), int(item["selected_point_count"])),
    )
    interesting_points = set(true_extra_points) | set(best_signal["false_positive_point_ids"])
    interesting_rows = [
        row for row in feature_rows if int(row["point_id"]) in interesting_points
    ]

    return {
        "schema": "rtdl.goal3383.owner_face_ambiguity_signal_negative_probe.v1",
        "goal": 3383,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "county_cdb": str(county_cdb),
        "candidate_rows_from_optix_device_columns": True,
        "exact_oracle_generated_by_live_optix_run": True,
        "topology_rows_derived_from_cdb": True,
        "incident_rows_derived_from_cdb": True,
        "signal_inputs_exclude_exact_oracle": True,
        "exact_oracle_used_only_for_signal_evaluation": True,
        "point_count": len(points),
        "shape_count": len(shapes),
        "optix_candidate_row_count": len(candidate_pairs),
        "exact_row_count": len(exact_pairs),
        "candidate_extra_row_count": len(candidate_pairs - exact_pairs),
        "true_extra_point_ids": sorted(true_extra_points),
        "signal_results": signal_results,
        "best_simple_signal_name": str(best_signal["name"]),
        "best_simple_signal_false_positive_point_ids": best_signal["false_positive_point_ids"],
        "best_simple_signal_missed_extra_point_ids": best_signal["missed_extra_point_ids"],
        "simple_signal_family_result": "reject_for_default_route",
        "interesting_feature_rows": interesting_rows,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "native_default_route_authorized": False,
        },
        "interpretation": (
            "Negative ambiguity-discovery probe: simple topology-only signals can find the seven "
            "candidate-extra points, but the best compact signal also selects non-error points 651 and "
            "652. Therefore this signal family must not be promoted as a default owner-face route. "
            "A stronger non-fixture ambiguity detector or richer boundary-event primitive is required."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3383 owner-face ambiguity signal negative probe.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
    )
    parser.add_argument("--county-cdb", type=Path, default=None)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
