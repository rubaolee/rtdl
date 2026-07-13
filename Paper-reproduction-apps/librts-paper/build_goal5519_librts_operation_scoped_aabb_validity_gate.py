from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def _read(name: str) -> dict[str, object]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    original = _read("goal5519_lakes_bz2_range_contains_100000.json")
    semantic = _read("goal5519_lakes_range_contains_semantic_audit.json")
    subset = _read("goal5519_lakes_collapsed_subset_gate.json")
    pre_strict = _read("goal5519_lakes_cached_pre_strict.json")
    strict = _read("goal5519_lakes_cached_strict.json")
    fixed = _read("goal5519_lakes_range_contains_operation_scoped_fix.json")
    operation_probe = _read("goal5519_operation_scoped_validity_probe.json")
    intersects_prefix = _read("goal5519_lakes_range_intersects_prefix_regression.json")
    intersects_degenerate = _read("goal5519_lakes_range_intersects_degenerate_regression.json")

    geometry_sha256 = original["input_identity"]["geometry_sha256"]
    query_sha256 = original["input_identity"]["query_sha256"]
    checks = {
        "original_exact_input_delta_is_79": (
            int(original["author"]["result_count"]) - int(original["rtdl"]["result_count"]) == 79
        ),
        "semantic_audit_uses_same_input_hashes": (
            semantic["input_identity"]["geometry_sha256"] == geometry_sha256
            and semantic["input_identity"]["query_sha256"] == query_sha256
        ),
        "float32_collapsed_rows_contribute_exact_delta": (
            semantic["indexed_validity"]["float32_collapsed_containment_contribution"] == 79
            and semantic["indexed_validity"]["float32_invalid_rows_with_nonzero_contribution"] == 2
        ),
        "native_ab_isolates_strict_validity_regression": (
            pre_strict["result_count"] == 101418 and strict["result_count"] == 101339
        ),
        "fixed_exact_columns_match_author": (
            fixed["result_count"] == original["author"]["result_count"] == 101418
            and fixed["input_identity"]["geometry_sha256"] == geometry_sha256
            and fixed["input_identity"]["query_sha256"] == query_sha256
            and fixed["input_identity"]["cache_row_count_matches"]
        ),
        "operation_discriminating_probe_matches": operation_probe["matched"],
        "range_intersects_prefix_regression_matches": (
            intersects_prefix["rtdl"]["result_count"] == 34581812
        ),
        "range_intersects_degenerate_regression_matches": (
            intersects_degenerate["rtdl"]["result_count"] == 0
        ),
        "minimal_author_subset_does_not_overprove_cause": (
            subset["author"]["result_count"] == 0
            and not subset["diagnosis"]["author_matches_float32_inclusive_oracle"]
        ),
    }
    if not all(checks.values()):
        raise ValueError(f"Goal5519 gate check failed: {checks}")

    source = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
    source_text = source.read_text(encoding="utf-8")
    operation_guard = (
        "if (params.operation == 3u) {\n"
        "        const uint32_t indexed_idx = params.intersect_pass == 1u ? qidx : prim;\n"
        "        if (!box_is_strictly_valid(params.indexed_boxes[indexed_idx])) return;\n"
        "    }"
    )
    if operation_guard not in source_text:
        raise ValueError("native strict-validity guard is not scoped to range_intersects")

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5519_operation_scoped_aabb_validity_fix.v1",
        "status": "generic_operation_scoped_aabb_validity_regression_fixed",
        "operation_contract": {
            "point_contains": "inclusive exact predicate after float32 numeric packing",
            "range_contains": "inclusive exact predicate after float32 numeric packing",
            "range_intersects": "OptiX strict indexed-box validity after float32 packing before segment predicate",
            "app_specific_behavior_added": False,
        },
        "root_cause": {
            "regression_source": "Goal5508 strict indexed-box validity guard was applied before all AABB operations",
            "full_exact_author_count": 101418,
            "pre_fix_rtdl_count": 101339,
            "delta": 79,
            "float32_invalid_indexed_count": semantic["indexed_validity"]["float32_strictly_invalid_count"],
            "float32_collapsed_indexed_count": semantic["indexed_validity"]["float64_valid_but_float32_collapsed_count"],
            "nonzero_contributing_collapsed_rows": semantic["indexed_validity"]["nonzero_contribution_rows"],
            "native_pre_strict_count": pre_strict["result_count"],
            "native_strict_count": strict["result_count"],
        },
        "corrected_exact_case": {
            "case_id": original["case_id"],
            "geometry_sha256": geometry_sha256,
            "query_sha256": query_sha256,
            "author_count": original["author"]["result_count"],
            "fixed_rtdl_count": fixed["result_count"],
            "matched": fixed["result_count"] == original["author"]["result_count"],
            "column_cache_contract": fixed["input_identity"]["app_owned_cache_contract"],
        },
        "generic_regressions": {
            "operation_discriminating_counts": operation_probe["counts"],
            "operation_discriminating_expected": operation_probe["expected_counts"],
            "range_intersects_prefix_count": intersects_prefix["rtdl"]["result_count"],
            "range_intersects_degenerate_count": intersects_degenerate["rtdl"]["result_count"],
        },
        "author_source_audit": {
            "rtspatial_commit": "7c54c181b1058c87768767998c00e225cc58666e",
            "contains_shader": {
                "path": "RTSpatial/src/shaders/shaders_contains_envelope_query_2d.cu",
                "sha256": "f5200603839e6c714bfc6ce9d085a04f2ca17aa44f9961cd4abc36c0b6caae5f",
                "observation": "uses envelope.Contains(query) without Envelope::IsValid guard",
            },
            "intersects_shader": {
                "path": "RTSpatial/src/shaders/shaders_intersects_envelope_query_2d.cu",
                "sha256": "1f1dc0507bfc2abb813d17c23ae39914f358b466caf4a3e9ced52354c91faea2",
                "observation": "uses geom.IsValid() for the indexed envelope path",
            },
        },
        "pod_build": {
            "pod": "157.157.221.29:25039",
            "build_root": "/tmp/rtdl-goal5519",
            "source_sha256": _sha256(source),
            "library_sha256": fixed["optix_library_sha256"],
            "workspace_quota_workaround": "read-only /workspace inputs plus writable /tmp build tree",
        },
        "checks": checks,
        "claim_boundary": {
            "generic_native_semantic_fix_claimed": True,
            "exact_lakes_range_contains_count_match_claimed": True,
            "complete_range_contains_matrix_claimed": False,
            "pointwise_relation_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure_reproduction_claimed": False,
            "complete_paper_reproduction_claimed": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "embree_in_scope": False,
        },
        "evidence": [
            f"results/{name}"
            for name in (
                "goal5519_lakes_bz2_range_contains_100000.json",
                "goal5519_lakes_range_contains_semantic_audit.json",
                "goal5519_lakes_collapsed_subset_gate.json",
                "goal5519_lakes_cached_pre_strict.json",
                "goal5519_lakes_cached_strict.json",
                "goal5519_lakes_range_contains_operation_scoped_fix.json",
                "goal5519_operation_scoped_validity_probe.json",
                "goal5519_lakes_range_intersects_prefix_regression.json",
                "goal5519_lakes_range_intersects_degenerate_regression.json",
                "goal5519_optix_build.log",
            )
        ],
    }
    output = RESULTS / "goal5519_operation_scoped_aabb_validity_fix_gate.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
