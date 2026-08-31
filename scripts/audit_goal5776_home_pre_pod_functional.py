#!/usr/bin/env python3
"""Independently recount the final Goal5776 Home functional lineages.

This review tool intentionally imports neither the Goal5776 contract nor any
application route.  Its expected key set is frozen locally so that a matching
producer bug cannot silently redefine the claimed 126-path coverage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile


V2 = "v2_direct_true_optix_backport"
V4 = "v4_restricted_callback_true_optix"
COLD = "installed_cold_compile_prepare_execute"
PREPARED = "prepared_first_execute"
METHODS = (V2, V4)

UNIT_LIFECYCLES = {
    "particle__microfluidics_5000": (COLD, PREPARED),
    **{
        f"triangle__{dataset}__{algorithm}": (COLD, PREPARED)
        for dataset in ("com_dblp", "cit_patents", "soc_livejournal1")
        for algorithm in ("rt_1a2", "rt_2a1")
    },
    **{
        f"rtdbscan__{case}": (COLD, PREPARED)
        for case in (
            "locked12", "endpoint_exact", "endpoint_below", "endpoint_above",
            "duplicate_pair", "grid3_sparse", "grid3_dense", "grid4_sparse",
            "grid4_dense", "grid6_sparse", "grid6_dense", "grid8_sparse",
            "grid8_dense", "grid10_sparse", "grid10_dense",
            "float32_sqrt_rounding_counterexample", "nx2_zero_z_lift",
            "goal5776_clustered3d_4096",
        )
    },
    "rtnn__kitti12m_q4096_k4": (COLD, PREPARED),
    "xhd__dragon_to_happy": (COLD, PREPARED),
    "rtbh__author_32768": (COLD, PREPARED),
    "raydb__ssb_sf10_q11": (COLD,),
    "librts__parks_point_contains": (COLD, PREPARED),
    "librts__parks_range_contains": (COLD, PREPARED),
    "rayjoin__top4_six_batch": (COLD, PREPARED),
}

TAIL_UNITS = frozenset({
    "rtbh__author_32768",
    "librts__parks_point_contains",
    "librts__parks_range_contains",
})
NO_LEAF_UNITS = TAIL_UNITS


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tar_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            leaf = member.name.rsplit("/", 1)[-1]
            if not member.isfile() or len(leaf) != 8 \
                    or not leaf[:3].isdigit() or not leaf.endswith(".json"):
                continue
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable Home record: {member.name}")
            rows.append(json.loads(handle.read()))
    return rows


def _receipt_ok(row: dict[str, object]) -> tuple[bool, str]:
    receipt = row["traversal_receipt"]
    assert isinstance(receipt, dict)
    native = receipt["native_snapshot"]
    assert isinstance(native, dict)
    ok = (
        receipt.get("physical_executor_classification")
        == "optix_traversal_observed"
        and int(native.get("successful_launch_count", -1)) > 0
        and native.get("successful_launch_count")
        == native.get("complete_context_launch_count")
        and int(native.get("failed_launch_count", -1)) == 0
        and int(native.get("incomplete_context_launch_count", -1)) == 0
        and int(native.get("pending_context_at_finish", -1)) == 0
        and int(native.get("session_error", -1)) == 0
        and int(native.get("first_traversable", 0)) != 0
        and int(native.get("last_traversable", 0)) != 0
    )
    return ok, str(receipt["provider_library_sha256"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix-archive", type=Path, required=True)
    parser.add_argument("--tail-archive", type=Path, required=True)
    parser.add_argument("--final-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)

    prefix = [row for row in _tar_rows(args.prefix_archive)
              if str(row["unit_id"]) not in TAIL_UNITS]
    tail = _tar_rows(args.tail_archive)
    final_doc = json.loads(args.final_json.read_text(encoding="utf-8"))
    final = list(final_doc["results"])
    rows = prefix + tail + final

    expected = {
        (unit, method, lifecycle)
        for unit, lifecycles in UNIT_LIFECYCLES.items()
        for lifecycle in lifecycles
        for method in METHODS
    }
    observed: dict[tuple[str, str, str], dict[str, object]] = {}
    native_shas: set[str] = set()
    required_cache_records = 0
    no_leaf_cache_records = 0
    for row in rows:
        key = (str(row["unit_id"]), str(row["method"]), str(row["lifecycle"]))
        if key in observed:
            raise RuntimeError(f"duplicate final Home functional key: {key}")
        observed[key] = row
        if row.get("matched") is not True:
            raise RuntimeError(f"incorrect Home functional row: {key}")
        receipt_ok, native_sha = _receipt_ok(row)
        if not receipt_ok:
            raise RuntimeError(f"invalid traversal receipt: {key}")
        native_shas.add(native_sha)
        cache = row["formal_leaf_cache_delta"]
        assert isinstance(cache, dict)
        if key[1] == V2:
            if cache.get("mode") != "not_applicable_to_v2_direct":
                raise RuntimeError(f"V2 cache attribution invalid: {key}")
        elif key[0] in NO_LEAF_UNITS:
            if cache.get("mode") != "not_applicable_no_numba_leaf" \
                    or any(int(cache.get(name, -1)) != 0 for name in (
                        "hit_count", "miss_count", "disabled_count")):
                raise RuntimeError(f"no-leaf cache attribution invalid: {key}")
            no_leaf_cache_records += 1
        else:
            if int(cache.get("hit_count", 0)) <= 0 \
                    or int(cache.get("miss_count", -1)) != 0 \
                    or int(cache.get("disabled_count", -1)) != 0:
                raise RuntimeError(f"sealed cache hit contract invalid: {key}")
            required_cache_records += 1

    if set(observed) != expected:
        raise RuntimeError(json.dumps({
            "missing": sorted(expected - set(observed)),
            "extra": sorted(set(observed) - expected),
        }, sort_keys=True))
    if len(native_shas) != 1:
        raise RuntimeError(f"mixed Home native providers: {sorted(native_shas)}")

    result = {
        "schema": "rtdl.goal5776.home_pre_pod_functional_recount.v1",
        "status": "PASS",
        "record_count": len(rows),
        "expected_record_count": 126,
        "execution_unit_count": len(UNIT_LIFECYCLES),
        "correct_output_count": len(rows),
        "behavioral_true_optix_count": len(rows),
        "v2_cache_not_applicable_count": sum(
            1 for key in observed if key[1] == V2),
        "v4_required_cache_hit_record_count": required_cache_records,
        "v4_no_leaf_cache_not_applicable_record_count": no_leaf_cache_records,
        "distinct_native_provider_count": len(native_shas),
        "native_provider_sha256": next(iter(native_shas)),
        "formal_performance_result_created": False,
        "modern_rtx_claimed": False,
        "prefix_archive_sha256": _sha(args.prefix_archive),
        "tail_archive_sha256": _sha(args.tail_archive),
        "final_json_sha256": _sha(args.final_json),
        "producer_contract_or_app_imported": False,
    }
    args.output.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
