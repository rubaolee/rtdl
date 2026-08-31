#!/usr/bin/env python3
"""Independent Goal5788-A1 source/timing attribution audit.

This program intentionally imports no Goal5776/Goal5785 evaluator or recount
implementation.  It reads the two immutable execution-source archives, the two
raw-worker evidence archives, and the frozen Goal5785 evaluation only as a
value to compare against an independently reconstructed result.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import random
import statistics
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"

INPUTS = {
    "goal5776_source": (
        DOCS / "goal5776_v9_execution_source_rtx4000ada_20260814.tar.gz",
        "9c21d6e709bade05bee6f2212bcc4e3d916c5cb3cae11f32ab67c13ff55dd021",
    ),
    "goal5776_evidence": (
        DOCS / "goal5776_v9_rtx4000ada_real_scale_v2_v4_evidence_20260814.tar.gz",
        "e06d49ddfb018bce1b64b4a2d0802c585e282c8d14b434c15abf1b0da2c04d07",
    ),
    "goal5785_source": (
        DOCS / "goal5785_v6_rtx4000ada_final_result_20260816" / "EXECUTION_SOURCE.tar.gz",
        "75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41",
    ),
    "goal5785_evidence": (
        DOCS / "goal5785_v6_rtx4000ada_final_result_20260816" / "GOAL5785_EVIDENCE.tar.gz",
        "2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a",
    ),
    "goal5785_evaluation": (
        DOCS / "goal5785_v6_rtx4000ada_final_result_20260816" / "EVALUATION.json",
        "af630fa74ff6b60d1917234b7998e703d8ee60cf91c47cf4ef49ccebf065846a",
    ),
    "goal5787_claim_authority": (
        DOCS / "goal5787_cgo_claim_matrix_20260816.json",
        "e0fe4cd216ac6aa20f83be24d71d1c342456ae55ed79d108a0efd4fbc4565875",
    ),
}

EXPECTED_DATA_SHA256 = "f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad"
EXPECTED_FORMAL_CONTRACT_SHA256 = "34f2ee85f57721f139c32fc77f0f96f21765713f568ae3bedb2a1b55585cb69e"
TRIANGLE_RUNTIME = "src/rtdsl/v4_triangle_reduction_device_runtime.py"
CHECKED_REDUCER = "src/rtdsl/v4_checked_u64_device_reduction.py"
TRIANGLE_APP = "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py"
SEGMENTED_GEOMETRY = "examples/current/research_benchmarks/triangle_counting/segmented_rt_graph.py"
V2_METHOD = "v2_direct_true_optix_backport"
V4_METHOD = "v4_restricted_callback_true_optix"


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def verified_inputs() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, (path, expected) in INPUTS.items():
        actual = sha256_path(path)
        if actual != expected:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")
        result[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": actual,
            "bytes": path.stat().st_size,
        }
    return result


def safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    names: set[str] = set()
    for member in members:
        pure = Path(member.name)
        if pure.is_absolute() or ".." in pure.parts:
            raise AssertionError(f"unsafe archive member: {member.name}")
        if member.name in names:
            raise AssertionError(f"duplicate archive member: {member.name}")
        names.add(member.name)
        if not (member.isfile() or member.isdir()):
            raise AssertionError(f"unsupported archive member type: {member.name}")
    return members


def source_file_map(path: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in safe_members(archive):
            if not member.isfile():
                continue
            marker = "/source/"
            if marker in member.name:
                relative = member.name.split(marker, 1)[1]
            elif member.name.startswith("source/"):
                relative = member.name[len("source/") :]
            else:
                relative = member.name
            extracted = archive.extractfile(member)
            if extracted is None:
                raise AssertionError(member.name)
            result[relative] = extracted.read()
    if TRIANGLE_RUNTIME not in result:
        raise AssertionError(f"missing {TRIANGLE_RUNTIME} from {path}")
    return result


def normalized_weighted_if(source: bytes) -> tuple[str, str]:
    tree = ast.parse(source.decode("utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if isinstance(node.test, ast.Name) and node.test.id == "weighted":
            body = ast.dump(ast.Module(body=node.body, type_ignores=[]), include_attributes=False)
            orelse = ast.dump(ast.Module(body=node.orelse, type_ignores=[]), include_attributes=False)
            if "reduced" in body and "reduced" in orelse:
                return body, orelse
    raise AssertionError("could not find `if weighted` branch")


def source_audit(old_path: Path, new_path: Path) -> dict[str, Any]:
    old = source_file_map(old_path)
    new = source_file_map(new_path)
    all_names = sorted(set(old) | set(new))
    changes = []
    for name in all_names:
        old_sha = hashlib.sha256(old[name]).hexdigest() if name in old else None
        new_sha = hashlib.sha256(new[name]).hexdigest() if name in new else None
        if old_sha != new_sha:
            changes.append(
                {
                    "path": name,
                    "change": "added" if name not in old else "removed" if name not in new else "modified",
                    "goal5776_sha256": old_sha,
                    "goal5785_sha256": new_sha,
                }
            )
    old_weighted, old_unweighted = normalized_weighted_if(old[TRIANGLE_RUNTIME])
    new_weighted, new_unweighted = normalized_weighted_if(new[TRIANGLE_RUNTIME])
    runtime_old = old[TRIANGLE_RUNTIME].decode("utf-8")
    runtime_new = new[TRIANGLE_RUNTIME].decode("utf-8")
    app_old = old[TRIANGLE_APP].decode("utf-8")
    app_new = new[TRIANGLE_APP].decode("utf-8")
    geometry_old = old[SEGMENTED_GEOMETRY].decode("utf-8")
    geometry_new = new[SEGMENTED_GEOMETRY].decode("utf-8")
    checks = {
        "goal5776_checked_reducer_absent": CHECKED_REDUCER not in old,
        "goal5785_checked_reducer_present": CHECKED_REDUCER in new,
        "weighted_branch_ast_changed": old_weighted != new_weighted,
        "unweighted_branch_ast_identical": old_unweighted == new_unweighted,
        "goal5776_weighted_materialized_product_present": "per_ray * ray_weights" in runtime_old,
        "goal5776_weighted_three_host_scalar_reads_present": all(
            token in runtime_old
            for token in (
                "cp.max(ray_weights).item()",
                "cp.sum(ray_weights, dtype=cp.uint64).item()",
                "per_ray * ray_weights, dtype=cp.uint64).item()",
            )
        ),
        "goal5785_weighted_checked_reducer_call_present": "checked_u64_weighted_sum_device(" in runtime_new,
        "goal5785_unweighted_sum_present": "cp.sum(per_ray, dtype=cp.uint64).item()" in runtime_new,
        "app_passes_segment_ray_weights_in_both_sources": all(
            "ray_weights=weights" in source for source in (app_old, app_new)
        ),
        "rt_1a2_geometry_returns_no_weights_in_both_sources": all(
            'if paper_algorithm == "RT-1A2":' in source
            and "return triangles, rays, None" in source
            for source in (geometry_old, geometry_new)
        ),
        "rt_2a1_geometry_returns_u64_weights_in_both_sources": all(
            "weights.astype(np.uint64, copy=False)" in source
            for source in (geometry_old, geometry_new)
        ),
        "device_segment_preserves_none_vs_device_weights_in_both_sources": all(
            '"ray_weights": None if weights is None else cp.asarray(weights)' in source
            for source in (geometry_old, geometry_new)
        ),
    }
    if not all(checks.values()):
        raise AssertionError(f"source audit failed: {checks}")
    src_changes = [item for item in changes if item["path"].startswith("src/")]
    classifications = {
        "src/rtdsl/__init__.py": "other_family_export__not_triangle_reduction_hot_path",
        "src/rtdsl/action_ray_triangle_scalar_summary.py": "additive_prepared_owner_lifecycle__not_v4_device_reduction_hot_path",
        "src/rtdsl/aggregate_hierarchy_native.py": "rt_barneshut_canonical_output_work__not_triangle",
        "src/rtdsl/fixed_radius_graph_refinement_registry.py": "regenerated_evidence_identity__not_triangle",
        "src/rtdsl/generic_primitives.py": "particle_prepared_closest_hit_owner__not_triangle_reduction",
        "src/rtdsl/v4_checked_u64_device_reduction.py": "triangle_rt_2a1_weighted_hot_path__new_checked_reducer",
        "src/rtdsl/v4_hierarchy_frontier.py": "rt_barneshut_packed_output_work__not_triangle",
        "src/rtdsl/v4_triangle_reduction_device_runtime.py": "triangle_rt_2a1_weighted_hot_path_callsite__rt_1a2_branch_unchanged",
    }
    if {item["path"] for item in src_changes} != set(classifications):
        raise AssertionError("unclassified changed src file")
    for item in src_changes:
        item["classification"] = classifications[item["path"]]
    return {
        "goal5776_source_file_count": len(old),
        "goal5785_source_file_count": len(new),
        "changed_source_tree_file_count": len(changes),
        "changed_src_file_count": len(src_changes),
        "changed_source_tree_files": changes,
        "changed_src_files": src_changes,
        "triangle_runtime_goal5776_sha256": hashlib.sha256(old[TRIANGLE_RUNTIME]).hexdigest(),
        "triangle_runtime_goal5785_sha256": hashlib.sha256(new[TRIANGLE_RUNTIME]).hexdigest(),
        "checks": checks,
        "application_to_runtime_trace": {
            "rt_1a2": [
                f"{SEGMENTED_GEOMETRY}: _host_geometry returns weights=None",
                f"{SEGMENTED_GEOMETRY}: device segment preserves ray_weights=None",
                f"{TRIANGLE_APP}: PreparedSegmentedTriangleCountingV4 forwards ray_weights",
                f"{TRIANGLE_RUNTIME}: weighted=False and unweighted cp.sum(per_ray) branch",
            ],
            "rt_2a1": [
                f"{SEGMENTED_GEOMETRY}: _host_geometry returns uint64 multiplicity weights",
                f"{SEGMENTED_GEOMETRY}: device segment copies weights to device",
                f"{TRIANGLE_APP}: PreparedSegmentedTriangleCountingV4 forwards ray_weights",
                f"{TRIANGLE_RUNTIME}: weighted=True and checked_u64_weighted_sum_device branch in Goal5785",
            ],
            "triangle_app_sha_equal_between_cohorts": hashlib.sha256(old[TRIANGLE_APP]).hexdigest()
            == hashlib.sha256(new[TRIANGLE_APP]).hexdigest(),
            "segmented_geometry_sha_equal_between_cohorts": hashlib.sha256(old[SEGMENTED_GEOMETRY]).hexdigest()
            == hashlib.sha256(new[SEGMENTED_GEOMETRY]).hexdigest(),
        },
        "causal_scope": {
            "rt_2a1_weighted_hot_path_changed": True,
            "rt_1a2_unweighted_hot_path_changed": False,
            "all_ten_goal5785_triangle_clear_wins_caused_by_checked_u64_reducer": False,
        },
    }


def worker_documents(path: Path) -> list[dict[str, Any]]:
    workers = []
    with tarfile.open(path, "r:gz") as archive:
        safe_members(archive)
        names = sorted(
            member.name
            for member in archive.getmembers()
            if member.isfile() and "/workers/" in f"/{member.name}" and member.name.endswith(".json")
        )
        for name in names:
            extracted = archive.extractfile(name)
            if extracted is None:
                raise AssertionError(name)
            workers.append(json.load(extracted))
    return workers


def cohort(path: Path) -> dict[str, Any]:
    workers = worker_documents(path)
    indices = [int(worker["worker_index"]) for worker in workers]
    pids = [int(worker["parent_pid"]) for worker in workers]
    methods = Counter(worker["method"] for worker in workers)
    lifecycles = Counter(worker["lifecycle"] for worker in workers)
    if len(workers) != 464 or sorted(indices) != list(range(464)) or len(set(pids)) != 464:
        raise AssertionError("worker cardinality/index/PID contract failed")
    if methods != Counter({V2_METHOD: 232, V4_METHOD: 232}):
        raise AssertionError(methods)
    if lifecycles != Counter(
        {"installed_cold_compile_prepare_execute": 240, "prepared_first_execute": 224}
    ):
        raise AssertionError(lifecycles)
    for field, expected in (
        ("data_archive_sha256", EXPECTED_DATA_SHA256),
        ("formal_contract_sha256", EXPECTED_FORMAL_CONTRACT_SHA256),
    ):
        values = {worker[field] for worker in workers}
        if values != {expected}:
            raise AssertionError((field, values))
    values: dict[tuple[str, str, str], list[tuple[int, float]]] = defaultdict(list)
    row_order: list[tuple[str, str]] = []
    seen_rows: set[tuple[str, str]] = set()
    for worker in sorted(workers, key=lambda item: int(item["worker_index"])):
        if not worker["matched"] or worker["retry_resume_replacement_row_drop_relabel_used"]:
            raise AssertionError(f"invalid worker {worker['worker_index']}")
        lifecycle = worker["lifecycle"]
        for row in worker["rows"]:
            row_key = (lifecycle, row["row_id"])
            if row_key not in seen_rows:
                seen_rows.add(row_key)
                row_order.append(row_key)
            seconds = float(row["registered_complete_endpoint_seconds"])
            if not seconds > 0.0:
                raise AssertionError(row)
            values[(lifecycle, row["row_id"], worker["method"])].append(
                (int(worker["pair_index"]), seconds)
            )
    if len(row_order) != 34:
        raise AssertionError(f"expected 34 independent rows, got {len(row_order)}")
    medians: dict[tuple[str, str, str], float] = {}
    raw: dict[tuple[str, str, str], dict[int, float]] = {}
    for key, observations in values.items():
        if len(observations) != 8 or sorted(pair for pair, _ in observations) != list(range(8)):
            raise AssertionError((key, observations))
        by_pair = dict(observations)
        raw[key] = by_pair
        medians[key] = statistics.median(by_pair.values())
    if len(values) != 68:
        raise AssertionError(f"expected 68 method-row cells, got {len(values)}")
    return {
        "worker_count": len(workers),
        "unique_parent_pid_count": len(set(pids)),
        "method_counts": dict(methods),
        "lifecycle_counts": dict(lifecycles),
        "row_order": row_order,
        "medians": medians,
        "raw": raw,
    }


def percentile_ci(ratios: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(ratios, k=len(ratios))) for _ in range(10_000))
    return [samples[249], samples[9749]]


def evaluation_recount(cohort_data: dict[str, Any], submitted_path: Path) -> dict[str, Any]:
    submitted = json.loads(submitted_path.read_text(encoding="utf-8"))
    submitted_rows = submitted["rows"]
    if len(submitted_rows) != 34:
        raise AssertionError(len(submitted_rows))
    submitted_by_key = {(row["lifecycle"], row["row_id"]): row for row in submitted_rows}
    rebuilt = []
    max_delta = 0.0
    for row_index, row_key in enumerate(cohort_data["row_order"]):
        lifecycle, row_id = row_key
        v2 = cohort_data["raw"][(lifecycle, row_id, V2_METHOD)]
        v4 = cohort_data["raw"][(lifecycle, row_id, V4_METHOD)]
        ratios = [v2[index] / v4[index] for index in range(8)]
        median = statistics.median(ratios)
        ci = percentile_ci(ratios, 57_760_000 + row_index)
        expected = submitted_by_key[row_key]
        candidates: Iterable[tuple[float, float]] = [
            (median, float(expected["paired_ratio_median"])),
            *zip(ci, map(float, expected["bootstrap_ci95"])),
            *zip(ratios, map(float, expected["paired_v2_over_v4_ratios"])),
        ]
        row_delta = max(abs(left - right) for left, right in candidates)
        max_delta = max(max_delta, row_delta)
        if row_delta > 1e-12:
            raise AssertionError(f"row {row_key} delta {row_delta}")
        rebuilt.append(
            {
                "row_index": row_index,
                "lifecycle": lifecycle,
                "row_id": row_id,
                "paired_ratio_median": median,
                "bootstrap_ci95": ci,
                "no_slower_pass": median >= 1.0,
                "ci_clear_v4_win": ci[0] > 1.0,
                "ci_clear_v4_loss": ci[1] < 1.0,
            }
        )
    return {
        "bootstrap_implementation": "stdlib random.Random.choices; 10000 draws; sorted indices 249/9749",
        "seed_rule": "57_760_000 + row_index in first-seen raw-worker row order",
        "row_count": len(rebuilt),
        "max_absolute_delta_vs_submitted": max_delta,
        "all_rows_match_to_1e_12": True,
        "rows": rebuilt,
    }


def triangle_rows(recount: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in recount["rows"] if row["row_id"].startswith("triangle__")]
    clear = [row for row in rows if row["ci_clear_v4_win"]]
    for row in clear:
        row["paper_algorithm"] = "RT-2A1" if "__rt_2a1::" in row["row_id"] else "RT-1A2"
        row["checked_u64_mechanism_association"] = (
            "eligible_association__not_yet_same_source_ablation"
            if row["paper_algorithm"] == "RT-2A1"
            else "ineligible__unweighted_hot_path_unchanged__cause_unknown"
        )
    counts = Counter(row["paper_algorithm"] for row in clear)
    if len(rows) != 12 or len(clear) != 10 or counts != Counter({"RT-1A2": 5, "RT-2A1": 5}):
        raise AssertionError((len(rows), len(clear), counts))
    return {
        "triangle_row_count": len(rows),
        "ci_clear_v4_win_count": len(clear),
        "clear_win_count_by_algorithm": dict(counts),
        "checked_u64_mechanism_associated_clear_win_count": counts["RT-2A1"],
        "unattributed_clear_win_count": counts["RT-1A2"],
        "clear_win_rows": clear,
    }


def cross_cohort(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(old["medians"]) & set(new["medians"]))
    rows = []
    for lifecycle, row_id, method in keys:
        old_median = old["medians"][(lifecycle, row_id, method)]
        new_median = new["medians"][(lifecycle, row_id, method)]
        rows.append(
            {
                "lifecycle": lifecycle,
                "row_id": row_id,
                "method": method,
                "goal5776_absolute_median_seconds": old_median,
                "goal5785_absolute_median_seconds": new_median,
                "goal5785_over_goal5776_factor": new_median / old_median,
            }
        )
    triangle = [row for row in rows if row["row_id"].startswith("triangle__")]
    v2_factors = [row["goal5785_over_goal5776_factor"] for row in triangle if row["method"] == V2_METHOD]
    v4_factors = [row["goal5785_over_goal5776_factor"] for row in triangle if row["method"] == V4_METHOD]
    nontriangle = [
        row
        for row in rows
        if not row["row_id"].startswith("triangle__") and row["method"] == V2_METHOD
    ]
    raw_nontriangle_factors = [row["goal5785_over_goal5776_factor"] for row in nontriangle]
    rayjoin_batches = [
        row["goal5785_over_goal5776_factor"]
        for row in nontriangle
        if row["row_id"].startswith("rayjoin__") and "::batch" in row["row_id"]
    ]
    logical_nontriangle = [
        row["goal5785_over_goal5776_factor"]
        for row in nontriangle
        if not (row["row_id"].startswith("rayjoin__") and "::batch" in row["row_id"])
    ] + [statistics.median(rayjoin_batches)]
    return {
        "definition": "absolute method-row median in Goal5785 divided by the corresponding absolute median in Goal5776",
        "causal_use_forbidden": True,
        "reason": "different source identities and different cohorts; factors are sensitivity observations, not intervention effects",
        "triangle_v2": {
            "n": len(v2_factors),
            "median_factor": statistics.median(v2_factors),
            "range": [min(v2_factors), max(v2_factors)],
        },
        "triangle_v4": {
            "n": len(v4_factors),
            "median_factor": statistics.median(v4_factors),
            "range": [min(v4_factors), max(v4_factors)],
        },
        "nontriangle_raw_independent_rows": {
            "n": len(raw_nontriangle_factors),
            "median_factor": statistics.median(raw_nontriangle_factors),
            "range": [min(raw_nontriangle_factors), max(raw_nontriangle_factors)],
        },
        "nontriangle_logical_units_with_rayjoin_batches_collapsed": {
            "n": len(logical_nontriangle),
            "median_factor": statistics.median(logical_nontriangle),
            "range": [min(logical_nontriangle), max(logical_nontriangle)],
            "rayjoin_batch_factor_median": statistics.median(rayjoin_batches),
        },
        "triangle_rows": triangle,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = verified_inputs()
    old = cohort(INPUTS["goal5776_evidence"][0])
    new = cohort(INPUTS["goal5785_evidence"][0])
    recount = evaluation_recount(new, INPUTS["goal5785_evaluation"][0])
    result = {
        "schema": "rtdl.goal5788_a1.independent_source_and_raw_reconstruction.v1",
        "goal": "5788-A1",
        "inputs": inputs,
        "independence": {
            "imports_goal5776_or_goal5785_evaluator": False,
            "imports_goal5776_or_goal5785_recount": False,
            "reads_submitted_evaluation_only_after_independent_raw_reconstruction": True,
        },
        "source_audit": source_audit(INPUTS["goal5776_source"][0], INPUTS["goal5785_source"][0]),
        "goal5776_cohort": {key: value for key, value in old.items() if key not in {"raw", "medians", "row_order"}},
        "goal5785_cohort": {key: value for key, value in new.items() if key not in {"raw", "medians", "row_order"}},
        "goal5785_independent_recount": recount,
        "triangle_attribution": triangle_rows(recount),
        "cross_cohort_sensitivity": cross_cohort(old, new),
        "verdict": {
            "all_ten_triangle_clear_wins_remain_valid_measured_results": True,
            "all_ten_attributable_to_checked_u64_reducer": False,
            "rt_2a1_clear_wins_mechanism_associated": 5,
            "rt_1a2_clear_wins_cause": "unknown",
            "same_source_same_cohort_ablation_required_for_causal_claim": True,
        },
        "claim_boundary": {
            "product_source_changed": False,
            "worker_or_gpu_used": False,
            "performance_result_changed": False,
            "cross_cohort_factor_called_causal": False,
            "predicted_saving_claimed": False,
        },
    }
    payload = canonical_json_bytes(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps({"output": str(args.output), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}))


if __name__ == "__main__":
    main()
