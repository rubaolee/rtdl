from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


SCHEMA = "rtdl.paper_reproduction.librts.goal5503_author_range_intersects_contract.v2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(text: str, needle: str, label: str) -> dict[str, object]:
    return {"label": label, "needle": needle, "present": needle in text}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.author_root.resolve()

    files = {
        "benchmark_config": root / "SpatialQueryBenchmark/src/config.h",
        "benchmark_geometry": root / "SpatialQueryBenchmark/src/geom_common.h",
        "benchmark_range_query": root / "SpatialQueryBenchmark/src/query/rtspatial/range_query.cu",
        "benchmark_common": root / "SpatialQueryBenchmark/src/query/rtspatial/common.h",
        "wkt_loader": root / "SpatialQueryBenchmark/src/wkt_loader.h",
        "envelope": root / "RTSpatial/include/rtspatial/geom/envelope.cuh",
        "point": root / "RTSpatial/include/rtspatial/geom/point.cuh",
        "helpers": root / "RTSpatial/include/rtspatial/utils/helpers.h",
        "ray_params": root / "RTSpatial/include/rtspatial/details/ray_params.h",
        "intersects_shader": root / "RTSpatial/src/shaders/shaders_intersects_envelope_query_2d.cu",
    }
    missing = [name for name, path in files.items() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing author source files: {missing}")
    contents = {name: path.read_text(encoding="utf-8") for name, path in files.items()}

    checks = [
        require(contents["benchmark_config"], "using coord_t = float;", "benchmark_coord_t_float"),
        require(contents["benchmark_geometry"], "model::box<point_t>", "benchmark_boxes_use_coord_t"),
        require(contents["benchmark_range_query"], "SpatialIndex<coord_t, 2>", "benchmark_instantiates_coord_t_index"),
        require(contents["benchmark_range_query"], "QueryType::kRangeIntersects", "benchmark_dispatches_range_intersects"),
        require(contents["benchmark_range_query"], "Predicate::kIntersects", "benchmark_calls_intersects_predicate"),
        require(contents["benchmark_common"], "Point<coord_t, 2>", "benchmark_copies_coord_t_envelopes"),
        require(contents["wkt_loader"], "coord_t lows[2]", "wkt_loader_accumulates_coord_t_bounds"),
        require(contents["envelope"], "other.min_.get_coordinate(dim) <= max_.get_coordinate(dim)", "intersects_inclusive_lower_upper"),
        require(contents["envelope"], "other.max_.get_coordinate(dim) >= min_.get_coordinate(dim)", "intersects_inclusive_upper_lower"),
        require(contents["envelope"], "EnvelopeToOptixAabb<float, 2>", "float_optix_aabb_path_exists"),
        require(contents["envelope"], "aabb.minX = min_point.get_x();", "float_optix_aabb_direct_min_assignment"),
        require(contents["envelope"], "EnvelopeToOptixAabb<double, 2>", "double_optix_aabb_path_exists"),
        require(contents["helpers"], "next_float_from_double", "double_optix_path_has_explicit_float_rounding_helper"),
        require(contents["point"], "class Point<double, 2>", "double_point_template_exists"),
        require(contents["point"], "DEV_HOST_INLINE float get_coordinate", "double_point_coordinate_return_type_is_float_in_source"),
        require(contents["ray_params"], "struct RayParams<float, 2>", "gpu_float_ray_params_specialization_exists"),
        require(contents["ray_params"], "float t0 = 0, t1 = nextafterf(1.0, FLT_MAX);", "gpu_float_hit_interval_uses_nextafter_one"),
        require(contents["ray_params"], "tFar *= 1 + 2 * FLT_GAMMA(3);", "gpu_float_hit_interval_expands_tfar"),
        require(contents["ray_params"], "if (t0 > t1)", "gpu_float_hit_interval_rejects_disjoint_slabs"),
        require(contents["intersects_shader"], "ray_params.Compute(query, true);", "gpu_forward_intersects_uses_query_diagonal_ray"),
        require(contents["intersects_shader"], "bool query_hit = ray_params.IsHit(envelope);", "gpu_forward_intersects_tests_envelope_with_ray"),
        require(contents["intersects_shader"], "ray_params.Compute(envelope, false);", "gpu_forward_intersects_reverses_envelope_ray"),
        require(contents["intersects_shader"], "bool box_hit = ray_params.IsHit(query);", "gpu_forward_intersects_tests_query_with_reverse_ray"),
        require(contents["intersects_shader"], "if (!box_hit)", "gpu_forward_intersects_requires_reverse_hit"),
    ]
    failed = [check["label"] for check in checks if not check["present"]]
    if failed:
        raise AssertionError(f"author contract source checks failed: {failed}")

    commits = {}
    for name, repo in (("rtspatial", root / "RTSpatial"), ("benchmark", root / "SpatialQueryBenchmark")):
        completed = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        commits[name] = completed.stdout.strip() if completed.returncode == 0 else None

    payload = {
        "schema": SCHEMA,
        "status": "author_contract_audit_completed",
        "exit_label": "author_float32_gpu_rayparams_contract_audited_cpu_reference_distinguished",
        "author_root": str(root),
        "author_commits": commits,
        "source_files": {
            name: {"path": str(path), "sha256": sha256(path)}
            for name, path in files.items()
        },
        "checks": checks,
        "contract": {
            "benchmark_coordinate_type": "float32",
            "benchmark_cpu_reference_predicate": "inclusive_aabb_intersects",
            "benchmark_gpu_predicate": "float32_rayparams_slab_hit_with_nextafter_t1_and_tfar_gamma",
            "benchmark_float_optix_conversion": "direct_float_to_OptixAabb_assignment",
            "benchmark_float_padding": False,
            "benchmark_gpu_t0": 0.0,
            "benchmark_gpu_t1": "nextafterf(1.0, FLT_MAX)",
            "benchmark_gpu_tfar_multiplier": "1 + 2 * FLT_GAMMA(3)",
            "benchmark_gpu_query_shape": "forward_query_diagonal_then_reverse_envelope_diagonal",
            "cpu_reference_and_gpu_predicate_equivalence_proven": False,
            "double_template_exists": True,
            "double_optix_conversion": "next_float_from_double_round_outward_two_steps",
            "double_path_used_by_benchmark": False,
            "source_anomaly_double_get_coordinate_returns_float": True,
        },
        "claim_boundary": {
            "author_contract_source_audited": True,
            "author_validity_proven_for_full_inputs": False,
            "full_input_root_cause_resolved": False,
            "rtdl_core_change_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
