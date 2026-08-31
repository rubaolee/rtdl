"""Create-only local evidence for Goal5758/M1's three frozen lanes."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sys
import tarfile

from rtdsl.v4_callback_abi import AnyHitProofAuthority
from rtdsl.v4_callback_interpreter import execute_callback_role
from rtdsl.v4_callback_ir import AnyHitDeliveryContract, CallbackRole
from rtdsl.v4_triangle_reduction import (
    compile_triangle_reduction_contract,
    compile_triangle_reduction_abi,
    execute_checked_reducer,
    verify_triangle_reduction_schema,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

from scripts.goal5758_m1_consumer_fixtures import (
    COUNT_SOURCE,
    KEYED_SOURCE,
    all_hit_schema,
    compile_count_callback,
    compile_keyed_callback,
    keyed_schema,
    weighted_schema,
)
from scripts.goal5758_m1_independent_oracles import (
    checked_u64_product_sum,
    checked_u64_sum,
    keyed_i64_identical_dedup,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "history/internal_docs/goal5758_m1_generic_triangle_metadata_reduction_contract_20260812.json"
REVIEW = ROOT / "history/internal_docs/review_goal5757_owner_returned_external_20260812.md"
FREEZE = ROOT / "history/internal_docs/goal5757_pre_support_lane_contract_freeze_20260811.json"
ORACLE = ROOT / "scripts/goal5758_m1_independent_oracles.py"
FIXTURES = ROOT / "scripts/goal5758_m1_consumer_fixtures.py"
PRODUCT = ROOT / "src/rtdsl/v4_triangle_reduction.py"
ABI = ROOT / "src/rtdsl/v4_callback_abi.py"
PARTICLE_SCHEMA = ROOT / "src/rtdsl/v4_typed_physical_schema.py"
RAYDB_APP = ROOT / "Paper-reproduction-apps/raydb-paper/rtdl3_action_migration.py"
TRIANGLE_APP = ROOT / "Paper-reproduction-apps/triangle-counting-paper/run_functional_receipt.py"
GOAL5756_RESULT = ROOT / "history/internal_docs/goal5756_builtin_triangle_runtime_and_home_result_20260811.json"
RUNNER = ROOT / "scripts/goal5758_run_m1_evidence.py"
RECOUNT = ROOT / "scripts/goal5758_recount_m1_evidence.py"
PRODUCT_TEST = ROOT / "tests/goal5758_v4_triangle_reduction_test.py"
EVIDENCE_TEST = ROOT / "tests/goal5758_m1_evidence_test.py"
OUTPUT_DEFAULT = ROOT / "history/internal_docs/goal5758_m1_local_evidence_20260812"
ARCHIVE_DEFAULT = ROOT / "history/internal_docs/goal5758_m1_local_evidence_20260812.tar.gz"
TWIN_DEFAULT = ROOT / "history/internal_docs/goal5758_m1_local_evidence_twin_20260812.tar.gz"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> str:
    data = canonical(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha_bytes(data)


def load_paper_lanes() -> dict[tuple[str, str], dict[str, object]]:
    payload = json.loads(FREEZE.read_text(encoding="utf-8"))
    result = {}
    for lane in payload["lanes"]:
        key = (lane["app_id"], lane["lane_id"])
        if key in {
            ("raydb", "ray_triangle.keyed_i64_sum.v1"),
            ("triangle_counting", "ray_triangle_scalar.all_hit_count_value.v1"),
            ("triangle_counting", "ray_triangle_scalar.any_hit_weighted_value.v1"),
        }:
            for relative, expected in lane["source_pins"]:
                observed = sha_file(ROOT / relative)
                if observed != expected:
                    raise RuntimeError(f"source pin drift: {relative}: {observed} != {expected}")
            result[key] = lane
    if len(result) != 3:
        raise RuntimeError(f"expected three M1 lanes, got {len(result)}")
    return result


def target() -> ReferenceTargetProfile:
    # The target is the exact, previously reviewed Goal5756 Home identity.
    # M1 does not possess that runtime authority and therefore emits only a
    # non-executable contract; this pin must not be read as a new GPU receipt.
    return ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256="9c9ffd91e02a53aba7a2b399e65985ce3cb76d1620a2b3960b845efddb7bc5cd",
        supports_custom_aabb=True,
        supports_builtin_triangle=True)


def any_hit_proof(callback) -> AnyHitProofAuthority:
    proof_sha = sha_bytes(canonical({
        "kind": "goal5758_local_external_order_independence_oracle_v1",
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "oracle_sha256": sha_file(ORACLE),
    }))
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=proof_sha,
        proof_kind="external_machine_checked_order_independence_v1")


def load_raydb_module():
    app_dir = RAYDB_APP.parent
    sys.path.insert(0, str(app_dir))
    try:
        spec = importlib.util.spec_from_file_location("goal5758_raydb_adapter", RAYDB_APP)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load frozen RayDB adapter")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(app_dir))


def compile_lane(callback, schema):
    authority = verify_triangle_reduction_schema(callback, schema, target=target())
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=any_hit_proof(callback))
    contract = compile_triangle_reduction_contract(authority, abi_sha256=abi.abi_sha256)
    return authority, abi, contract


def raydb_lane(lane: dict[str, object]) -> dict[str, object]:
    callback = compile_keyed_callback()
    schema = keyed_schema(callback)
    _, abi, contract = compile_lane(callback, schema)
    app = load_raydb_module()
    events = app.fixture_events()
    rows = tuple({
        "launch_index": int(item["query_id"]),
        "primitive_index": int(item["primitive_stable_id"]),
        "primitive.stable_id": int(item["primitive_stable_id"]),
        "primitive.signed_value": int(item["value"]),
        "primitive.include": int(bool(item["include"])),
    } for item in events)
    observed = execute_checked_reducer(schema.reducer, rows)
    independent = keyed_i64_identical_dedup(rows, capacity=4096)
    groups = tuple(sorted({row.group_values for row in app.bounded_q21_rows()}))
    mapped = [
        {"group": list(groups[key[0]]), "value": int(value)}
        for key, value in observed
    ]
    mapped.sort(key=lambda row: tuple(row["group"]))
    app_reference = app.run_reference_rows(
        app.bounded_q21_rows(), app.bounded_q21_predicate())
    callback_probe = execute_callback_role(callback, CallbackRole.ANY_HIT, {
        "hit": {"t": 1.0, "primitive_index": 1, "hit_kind": 0xFE, "barycentrics": (0.25, 0.25)},
        "payload": {"accepted": 2}, "stable_ids": [4, 7],
        "signed_values": [9, -3], "include_flags": [0, 1],
    })
    matched = (observed == independent and mapped == app_reference["expected_rows"])
    if not matched:
        raise RuntimeError("RayDB M1 reducer mismatch")
    return lane_payload(
        lane, callback, schema, abi.abi_sha256, contract.to_dict(),
        reducer_input_count=len(rows), observed=observed,
        raw_reducer_rows=rows,
        independent=independent, matched=matched,
        callback_probe_semantic_sha256=callback_probe.semantic_sha256,
        app_reference_rows=app_reference["expected_rows"],
        duplicate_delivery_observed=len(events) > len({
            (item["primitive_stable_id"], item["query_id"]) for item in events}),
    )


def triangle_lane(lane: dict[str, object], *, weighted: bool) -> dict[str, object]:
    callback = compile_count_callback()
    schema = weighted_schema(callback) if weighted else all_hit_schema(callback)
    _, abi, contract = compile_lane(callback, schema)
    author_count = 2_224_385
    if weighted:
        rows = ({"count": 444_877, "query.weight": 5},)
        independent = checked_u64_product_sum((
            (row["count"], row["query.weight"]) for row in rows))
    else:
        values = (1_000_000, 1_000_000, 224_385)
        rows = tuple({"count": value} for value in values)
        independent = checked_u64_sum(values)
    observed = execute_checked_reducer(schema.reducer, rows)
    callback_probe = execute_callback_role(callback, CallbackRole.ANY_HIT, {
        "hit": {"t": 1.0, "primitive_index": 3, "hit_kind": 0xFE, "barycentrics": (0.25, 0.25)},
        "payload": {"count": 7},
    })
    callback_count = int(callback_probe.effect.field("payload").field("count"))
    matched = observed == independent == author_count and callback_count == 8
    if not matched:
        raise RuntimeError("Triangle Counting M1 reducer mismatch")
    return lane_payload(
        lane, callback, schema, abi.abi_sha256, contract.to_dict(),
        reducer_input_count=len(rows), observed=observed,
        raw_reducer_rows=rows,
        independent=independent, matched=matched,
        callback_probe_semantic_sha256=callback_probe.semantic_sha256,
        author_dataset="com-dblp", author_expected_triangle_count=author_count,
        paper_algorithm_decomposition_is_reducer_fixture_not_traversal_execution=True,
    )


def lane_payload(lane, callback, schema, abi_sha, contract, **evidence):
    return {
        "schema": "rtdl.goal5758.m1_lane_local_contract_result.v1",
        "goal": 5758,
        "app_id": lane["app_id"], "lane_id": lane["lane_id"],
        "paper_algorithm": lane["paper_algorithm"],
        "input_contract": lane["input_contract"],
        "output_contract": lane["output_contract"],
        "source_pins": lane["source_pins"],
        "callback_ir_sha256": callback.ir_sha256,
        "callback_effect_digest": callback.effect_digest,
        "typed_schema_sha256": schema.schema_sha256,
        "callback_abi_sha256": abi_sha,
        "canonical_contract_sha256": contract["contract_sha256"],
        "canonical_template_id": contract["template_id"],
        "reducer_algebra": schema.reducer.algebra.value,
        "canonical_contract_executable": contract["executable"],
        "target_execution_receipt_required": contract["target_execution_receipt_required"],
        "cpu_reducer_oracle_matched": evidence.pop("matched"),
        "local_pipeline_complete_through_nonexecuting_target_contract": True,
        "behavioral_gpu_execution_observed": False,
        "classification_after_m1": "LOCAL_SEMANTIC_AND_COMPILER_CONTRACT_COMPLETE__GPU_TARGET_EXECUTION_PENDING",
        **evidence,
    }


def scan_product_identity_dispatch() -> dict[str, object]:
    text = PRODUCT.read_text(encoding="utf-8").lower()
    forbidden = ("raydb", "triangle_counting", "triangle counting", "rt-1a2", "rt-2a1")
    hits = [item for item in forbidden if item in text]
    return {"forbidden_tokens": list(forbidden), "hits": hits, "hit_count": len(hits)}


def build_archive(output_root: Path, archive_path: Path) -> None:
    members: list[tuple[str, bytes]] = []
    for path in sorted(item for item in output_root.rglob("*") if item.is_file()):
        members.append(("goal5758_m1_local_evidence/" + path.relative_to(output_root).as_posix(), path.read_bytes()))
    carried = (CONTRACT, REVIEW, FREEZE, ORACLE, FIXTURES, PRODUCT, ABI,
               PARTICLE_SCHEMA, RAYDB_APP, TRIANGLE_APP, GOAL5756_RESULT,
               RUNNER, RECOUNT, PRODUCT_TEST, EVIDENCE_TEST)
    for path in carried:
        members.append(("goal5758_m1_local_evidence/CARRIED/" + path.relative_to(ROOT).as_posix(), path.read_bytes()))
    manifest = [{"path": name, "size": len(data), "sha256": sha_bytes(data)} for name, data in members]
    manifest_data = canonical({
        "schema": "rtdl.goal5758.m1_evidence_manifest.v1",
        "payload_count": len(manifest),
        "payload_bytes": sum(item["size"] for item in manifest),
        "payloads": manifest,
    })
    members.append(("goal5758_m1_local_evidence/MANIFEST.json", manifest_data))
    with archive_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for name, data in sorted(members):
                    info = tarfile.TarInfo(name)
                    info.size = len(data); info.mtime = 0; info.uid = info.gid = 0
                    info.uname = info.gname = ""; info.mode = 0o644
                    archive.addfile(info, io.BytesIO(data))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--archive", type=Path, default=ARCHIVE_DEFAULT)
    parser.add_argument("--twin", type=Path, default=TWIN_DEFAULT)
    args = parser.parse_args()
    if args.output_root.exists() or args.archive.exists() or args.twin.exists():
        raise FileExistsError("Goal5758 evidence paths are create-only")
    args.output_root.mkdir(parents=True)
    lanes = load_paper_lanes()
    outputs = (
        raydb_lane(lanes[("raydb", "ray_triangle.keyed_i64_sum.v1")]),
        triangle_lane(lanes[("triangle_counting", "ray_triangle_scalar.all_hit_count_value.v1")], weighted=False),
        triangle_lane(lanes[("triangle_counting", "ray_triangle_scalar.any_hit_weighted_value.v1")], weighted=True),
    )
    lane_shas = []
    for lane in outputs:
        name = re.sub(r"[^a-z0-9]+", "_", (lane["app_id"] + "__" + lane["lane_id"]).lower()).strip("_") + ".json"
        lane_shas.append((name, write_json(args.output_root / "LANES" / name, lane)))
    dispatch = scan_product_identity_dispatch()
    if dispatch["hit_count"] != 0:
        raise RuntimeError(f"product identity dispatch tokens: {dispatch['hits']}")
    result = {
        "schema": "rtdl.goal5758.m1_local_result.v1", "goal": 5758,
        "status": "LOCAL_SEMANTIC_AND_COMPILER_CONTRACT_COMPLETE__GPU_EXECUTION_PENDING",
        "lane_count": 3, "local_pipeline_pass_count": sum(
            bool(item["local_pipeline_complete_through_nonexecuting_target_contract"])
            and bool(item["cpu_reducer_oracle_matched"]) for item in outputs),
        "behavioral_gpu_lane_count": 0,
        "consumer_count": 2,
        "reducer_algebras": sorted({item["reducer_algebra"] for item in outputs}),
        "lane_artifact_sha256": dict(lane_shas),
        "product_identity_dispatch_scan": dispatch,
        "particle_v1_sha256_before_and_after": sha_file(PARTICLE_SCHEMA),
        "particle_v1_unchanged": sha_file(PARTICLE_SCHEMA) == "cdc279c10d3b2a687275dcdd10eb64b6d9b35ce960662ab7ea1b6f6e53377345",
        "historical_goal5757_result_changed": False,
        "paper_app_source_changed": False,
        "native_or_gpu_executed": False,
        "pod_or_performance_used": False,
        "m2_or_later_started": False,
        "claim_boundary": {
            "m1_local_product_semantics_complete": True,
            "m1_behavioral_gpu_complete": False,
            "three_lanes_supported_now_claimed": False,
            "nine_app_support_claimed": False,
            "performance_claimed": False,
            "production_public_submission_claimed": False,
        },
    }
    write_json(args.output_root / "RESULT.json", result)
    build_archive(args.output_root, args.archive)
    build_archive(args.output_root, args.twin)
    if args.archive.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("deterministic evidence twin mismatch")
    print(json.dumps({
        "result": result, "archive_sha256": sha_file(args.archive),
        "archive_bytes": args.archive.stat().st_size,
        "twin_sha256": sha_file(args.twin),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
