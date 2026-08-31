#!/usr/bin/env python3
"""Build deterministic, non-self-referential Goal5790 Home evidence.

This post-run packager is read-only with respect to the preserved Home closure.
It rehashes every local closure file, independently checks the ten raw lanes,
and emits an evidence archive/twin plus a separate authoritative result.  The
result is deliberately outside the archive so it can bind the archive digest
without creating a self-reference.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CLOSURE = (
    ROOT / "history/internal_docs/goal5790_v8_home_functional_closure_20260816"
)
DEFAULT_BUNDLE = (
    ROOT / "history/internal_docs/"
    "goal5790_local_functional_candidate_v8_20260816.tar.gz"
)
DEFAULT_SOURCE = (
    ROOT / "history/internal_docs/goal5790_portable_source_v8_20260816.tar.gz"
)
EXPECTED_BUNDLE_SHA256 = (
    "ac6f6212d974785951dc553dbd87b99e254f5c966c4f63112db74445bdf3d33c"
)
EXPECTED_SOURCE_SHA256 = (
    "8d4f3821a4d701bf3b87bab0c1e7765c4745d2d8eaaddbddcb82c55f95e3b126"
)
EXPECTED_SOURCE_TREE_SHA256 = (
    "119e1408fe506ebb110dae648a0e867573fd9328dd08ebe0a6ce70bc74df63e8"
)
EXPECTED_SOURCE_MANIFEST_SHA256 = (
    "0287764ae4f86a8b2607d5e6f27e865ab797a96dfa6c381306a1530ad7d9c819"
)
EXPECTED_NATIVE_SHA256 = (
    "4686286f03c9ff55afd31ef97917a46a0412230d129dedfd05723eed8f70d325"
)
EXPECTED_HOME_RESULT_SHA256 = (
    "90ca7bd7c6cc07bc669f439d459e9b550c68832a5ab1a784ccbfb2ba36bc59de"
)
EXPECTED_RECOUNT_SHA256 = (
    "33596aca56af9d3dbf3ab1cef0492b86e5ab62e8f425f61247bcc3305d3bd8e6"
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ensure_ascii=False,
    ).encode("utf-8")


def _json_bytes(value: object) -> bytes:
    return (json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False,
        ensure_ascii=False,
    ) + "\n").encode("utf-8")


def _read_archive(data: bytes) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts \
                    or name in payloads or not member.isfile():
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            payloads[name] = stream.read()
    return payloads


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _verified_candidate(bundle: Path, source: Path) -> dict[str, object]:
    bundle_bytes = bundle.read_bytes()
    source_bytes = source.read_bytes()
    if _sha(bundle_bytes) != EXPECTED_BUNDLE_SHA256 \
            or _sha(source_bytes) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Goal5790 v8 bundle/source identity drift")
    outer = _read_archive(bundle_bytes)
    manifest_bytes = outer.pop("PORTABLE_MANIFEST.json")
    manifest = json.loads(manifest_bytes)
    rows = {str(row["path"]): row for row in manifest["payloads"]}
    if set(rows) != set(outer) or manifest.get("payload_count") != len(rows) \
            or manifest.get("payload_bytes") != sum(
                int(row["size_bytes"]) for row in rows.values()):
        raise RuntimeError("Goal5790 v8 outer manifest mismatch")
    for name, data in outer.items():
        row = rows[name]
        if int(row["size_bytes"]) != len(data) or row["sha256"] != _sha(data):
            raise RuntimeError(f"Goal5790 v8 outer payload drift: {name}")
    if manifest.get("bundle_version") != 8 \
            or manifest.get("source_archive_sha256") != EXPECTED_SOURCE_SHA256 \
            or manifest.get("source_tree_sha256") != EXPECTED_SOURCE_TREE_SHA256 \
            or manifest.get("source_manifest_sha256") \
                != EXPECTED_SOURCE_MANIFEST_SHA256 \
            or outer.get("SOURCE.tar.gz") != source_bytes:
        raise RuntimeError("Goal5790 v8 candidate authority mismatch")
    source_payloads = _read_archive(source_bytes)
    source_manifest_bytes = source_payloads.pop(
        "history/internal_docs/goal5790_portable_source_manifest.json")
    source_manifest = json.loads(source_manifest_bytes)
    source_rows = {
        str(row["path"]): row for row in source_manifest["files"]
    }
    if set(source_rows) != set(source_payloads) \
            or source_manifest.get("source_tree_sha256") \
                != EXPECTED_SOURCE_TREE_SHA256 \
            or _sha(source_manifest_bytes) != EXPECTED_SOURCE_MANIFEST_SHA256:
        raise RuntimeError("Goal5790 v8 source manifest mismatch")
    for name, data in source_payloads.items():
        row = source_rows[name]
        if int(row["size_bytes"]) != len(data) or row["sha256"] != _sha(data):
            raise RuntimeError(f"Goal5790 v8 source payload drift: {name}")
    return {
        "outer_manifest": manifest,
        "outer_manifest_bytes": manifest_bytes,
        "source_manifest": source_manifest,
        "source_manifest_bytes": source_manifest_bytes,
    }


def _lineage_pins(manifest: dict[str, object]) -> dict[str, object]:
    rows = []
    for version in range(1, 8):
        row: dict[str, object] = {
            "version": version,
            "bundle_sha256": manifest[f"superseded_candidate_v{version}_sha256"],
            "executable": manifest[f"superseded_candidate_v{version}_executable"],
        }
        source_key = f"superseded_candidate_v{version}_source_archive_sha256"
        if source_key in manifest:
            row["source_archive_sha256"] = manifest[source_key]
        for suffix in (
            "zero_worker_failure", "prefreeze_rejection",
            "rejection_result_sha256", "rejection_report_sha256",
        ):
            key = f"candidate_v{version}_{suffix}"
            if key in manifest:
                row[suffix] = manifest[key]
        rows.append(row)
    return {
        "schema": "rtdl.goal5790.failure_lineage_pins.v1",
        "goal": 5790,
        "all_superseded_candidates_executable": False,
        "formal_workers_across_superseded_lineages": 0,
        "registered_timings_across_superseded_lineages": 0,
        "lineages": rows,
        "successful_candidate": {
            "version": 8,
            "bundle_sha256": EXPECTED_BUNDLE_SHA256,
            "source_archive_sha256": EXPECTED_SOURCE_SHA256,
            "source_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
        },
    }


def _verify_closure(closure: Path, candidate: dict[str, object]) -> dict[str, object]:
    files = sorted(path for path in closure.rglob("*") if path.is_file())
    inventory = [{
        "path": path.relative_to(closure).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    } for path in files]
    home_result = json.loads((closure / "RESULT.json").read_text(encoding="utf-8"))
    linux_recount_bytes = (closure / "FUNCTIONAL_RECOUNT.json").read_bytes()
    windows_recount_bytes = (
        closure / "FUNCTIONAL_RECOUNT_WINDOWS_INDEPENDENT.json").read_bytes()
    if _sha_file(closure / "RESULT.json") != EXPECTED_HOME_RESULT_SHA256 \
            or _sha(linux_recount_bytes) != EXPECTED_RECOUNT_SHA256 \
            or linux_recount_bytes != windows_recount_bytes:
        raise RuntimeError("Goal5790 Home result/recount identity drift")
    recount = json.loads(linux_recount_bytes)
    required_counts = {
        "exact_lane_count": 10,
        "behavioral_true_optix_lane_count": 10,
        "fresh_parent_pid_count": 10,
        "traversal_receipt_count": 10,
        "operation_receipt_count": 10,
        "successful_operation_event_count": 45,
        "invalid_traversal_or_operation_receipt_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    if any(recount.get(key) != value for key, value in required_counts.items()) \
            or recount.get("successful_operation_event_count_by_variant") \
                != {"fusion_off": 35, "fusion_on": 10} \
            or recount.get("operation_receipt_count_by_variant") \
                != {"fusion_off": 5, "fusion_on": 5} \
            or recount.get("performance_or_compiler_fusion_claimed") is not False:
        raise RuntimeError("Goal5790 Home recount claim/count drift")
    raw_root = closure / "functional_raw"
    raw_paths = sorted(raw_root.glob("*.json"))
    raw_rows = [{
        "path": path.name, "size_bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    } for path in raw_paths]
    if raw_rows != recount.get("raw_manifest") or len(raw_paths) != 10:
        raise RuntimeError("Goal5790 raw-lane manifest drift")
    event_counts = {"fusion_on": 0, "fusion_off": 0}
    receipt_counts = {"fusion_on": 0, "fusion_off": 0}
    pids = set()
    traversal_count = 0
    for path in raw_paths:
        lane = json.loads(path.read_text(encoding="utf-8"))
        variant = lane.get("variant")
        if variant not in event_counts or lane.get("matched") is not True \
                or lane.get("output") != lane.get("expected") \
                or lane.get("performance_claimed") is not False \
                or lane.get("compiler_fusion_claimed") is not False \
                or lane.get("registered_performance_timing_created") is not False \
                or lane.get("elapsed_values_recorded") is not False \
                or lane.get("pod_used") is not False \
                or lane.get("particle_included") is not False:
            raise RuntimeError(f"Goal5790 raw lane boundary drift: {path.name}")
        pids.add(int(lane["parent_pid"]))
        segments = lane.get("segments")
        if not isinstance(segments, list) or len(segments) != 1:
            raise RuntimeError(f"Goal5790 lane segment shape drift: {path.name}")
        receipt = segments[0]["operation_evidence_receipt"]
        events = receipt.get("events")
        if receipt.get("variant") != variant or not isinstance(events, list) \
                or int(receipt.get("successful_event_count", -1)) != len(events) \
                or any(event.get("recorded_after_callable_success") is not True
                       for event in events):
            raise RuntimeError(f"Goal5790 operation event drift: {path.name}")
        event_counts[variant] += len(events)
        receipt_counts[variant] += 1
        traversal = segments[0]["traversal_receipt"]
        native = traversal.get("native_snapshot", {})
        if traversal.get("physical_executor_classification") \
                != "optix_traversal_observed" \
                or int(native.get("successful_launch_count", 0)) <= 0 \
                or native.get("successful_launch_count") \
                    != native.get("complete_context_launch_count") \
                or any(int(native.get(key, 0)) != 0 for key in (
                    "failed_launch_count", "incomplete_context_launch_count",
                    "pending_context_at_finish", "session_error",
                    "incomplete_callsite_record_count",
                )):
            raise RuntimeError(f"Goal5790 traversal receipt drift: {path.name}")
        traversal_count += 1
    if len(pids) != 10 or traversal_count != 10 \
            or event_counts != {"fusion_on": 10, "fusion_off": 35} \
            or receipt_counts != {"fusion_on": 5, "fusion_off": 5}:
        raise RuntimeError("Goal5790 raw-derived totals drift")
    authority_path = closure / "TARGET_MATERIALIZATION_AUTHORITY.json"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    unsigned = dict(authority)
    receipt_sha = unsigned.pop("receipt_sha256")
    if _sha(_canonical(unsigned)) != receipt_sha \
            or authority.get("native_library_sha256") != EXPECTED_NATIVE_SHA256 \
            or authority.get("execution_source_archive_sha256") \
                != EXPECTED_SOURCE_SHA256 \
            or authority.get("execution_source_tree_sha256") \
                != EXPECTED_SOURCE_TREE_SHA256:
        raise RuntimeError("Goal5790 target authority drift")
    target_evidence_path = closure / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
    if _sha_file(target_evidence_path) != authority.get("evidence_archive_sha256"):
        raise RuntimeError("Goal5790 target-evidence identity drift")
    target_evidence = _read_archive(target_evidence_path.read_bytes())
    if _sha(target_evidence["EXECUTION_SOURCE.tar.gz"]) \
            != EXPECTED_SOURCE_SHA256 \
            or _sha(target_evidence["TARGET_NATIVE/librtdl_optix.so"]) \
                != EXPECTED_NATIVE_SHA256 \
            or target_evidence["EXECUTION_SOURCE.tar.gz"] \
                != (closure / "EXECUTION_SOURCE.tar.gz").read_bytes() \
            or target_evidence["TARGET_NATIVE/librtdl_optix.so"] \
                != (closure / "librtdl_optix.so").read_bytes():
        raise RuntimeError("Goal5790 nested preserved source/native drift")
    if home_result.get("bundle_sha256") != EXPECTED_BUNDLE_SHA256 \
            or home_result.get("execution_source_archive_sha256") \
                != EXPECTED_SOURCE_SHA256 \
            or home_result.get("execution_source_tree_sha256") \
                != EXPECTED_SOURCE_TREE_SHA256 \
            or home_result.get("source_manifest_sha256") \
                != EXPECTED_SOURCE_MANIFEST_SHA256 \
            or home_result.get("native_library_sha256") != EXPECTED_NATIVE_SHA256 \
            or home_result.get("target_materialization_receipt_sha256") \
                != receipt_sha:
        raise RuntimeError("Goal5790 Home result authority drift")
    cache_paths = sorted((closure / "fresh_cupy_probe_cache").glob("*.cubin"))
    cache_rows = [{
        "path": path.relative_to(closure).as_posix(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    } for path in cache_paths]
    return {
        "inventory": inventory,
        "home_result": home_result,
        "recount": recount,
        "raw_rows": raw_rows,
        "event_counts": event_counts,
        "receipt_counts": receipt_counts,
        "target_authority": authority,
        "target_evidence_sha256": _sha_file(target_evidence_path),
        "target_program_inspection_sha256": _sha_file(
            closure / "TARGET_PROGRAM_INSPECTION.json"),
        "cache_rows": cache_rows,
        "candidate": candidate,
    }


def _selected_home_payloads(closure: Path) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    exact_top = (
        "RESULT.json", "FUNCTIONAL_RECOUNT.json",
        "FUNCTIONAL_RECOUNT_WINDOWS_INDEPENDENT.json",
        "TARGET_MATERIALIZATION_AUTHORITY.json",
        "TARGET_MATERIALIZATION_EVIDENCE.tar.gz",
        "TARGET_PROGRAM_INSPECTION.json",
    )
    for name in exact_top:
        payloads[f"HOME/{name}"] = (closure / name).read_bytes()
    for directory in ("bounded_inputs", "functional_raw", "logs"):
        for path in sorted((closure / directory).rglob("*")):
            if path.is_file():
                payloads[f"HOME/{path.relative_to(closure).as_posix()}"] = \
                    path.read_bytes()
    return payloads


def build(
    *, closure: Path, bundle: Path, source: Path,
    output: Path, twin: Path, result_path: Path,
) -> dict[str, object]:
    outputs = (output, twin, result_path)
    if len({path.resolve() for path in outputs}) != 3:
        raise ValueError("Goal5790 evidence outputs must be distinct")
    for path in outputs:
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    candidate = _verified_candidate(bundle.resolve(), source.resolve())
    closure_state = _verify_closure(closure.resolve(), candidate)
    outer_manifest = candidate["outer_manifest"]
    lineage = _lineage_pins(outer_manifest)
    cache_label = {
        "schema": "rtdl.goal5790.cache_cubin_non_authority.v1",
        "goal": 5790,
        "cache_file_count": len(closure_state["cache_rows"]),
        "cache_file_bytes": sum(
            int(row["size_bytes"]) for row in closure_state["cache_rows"]),
        "observed_cache_files": closure_state["cache_rows"],
        "included_in_evidence_archive": False,
        "scientific_program_authority": False,
        "opaque_partner_kernel_binary_attestation_claimed": False,
        "meaning": (
            "transient CuPy compile-cache outputs observed during the isolated "
            "Home diagnostic and functional closure; recipe/source, exact "
            "producer paths, PTX digests/directives, and target receipts are "
            "the declared authority, not these cache cubins"
        ),
    }
    scope = {
        "schema": "rtdl.goal5790.home_evidence_scope.v1",
        "goal": 5790,
        "bundle_v8_sha256": EXPECTED_BUNDLE_SHA256,
        "source_v8_sha256": EXPECTED_SOURCE_SHA256,
        "source_v8_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
        "source_v8_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
        "duplicate_top_level_source_and_native_omitted": True,
        "source_and_native_preserved_inside_target_materialization_evidence": True,
        "cache_cubins_excluded_and_non_authoritative": True,
        "raw_generated_ptx_bytes_preserved": False,
        "ptx_evidence_scope": (
            "wrapper_leaf_composed_sha256_and_directive_tuple_plus_composer_"
            "binding__not_raw_ptx_or_compiled_cubin_attestation"
        ),
        "authoritative_goal_result_is_outside_archive_to_avoid_self_reference": True,
        "performance_evidence_included": False,
    }
    inventory = {
        "schema": "rtdl.goal5790.local_closure_inventory.v1",
        "goal": 5790,
        "all_local_closure_files_rehashed": True,
        "file_count": len(closure_state["inventory"]),
        "file_bytes": sum(
            int(row["size_bytes"]) for row in closure_state["inventory"]),
        "files": closure_state["inventory"],
    }
    payloads = _selected_home_payloads(closure.resolve())
    payloads.update({
        "IDENTITIES/V8_PORTABLE_MANIFEST.json": candidate[
            "outer_manifest_bytes"],
        "IDENTITIES/V8_SOURCE_MANIFEST.json": candidate[
            "source_manifest_bytes"],
        "IDENTITIES/FAILURE_LINEAGE_PINS.json": _json_bytes(lineage),
        "IDENTITIES/CACHE_CUBIN_NON_AUTHORITY.json": _json_bytes(cache_label),
        "IDENTITIES/EVIDENCE_SCOPE.json": _json_bytes(scope),
        "IDENTITIES/LOCAL_CLOSURE_INVENTORY.json": _json_bytes(inventory),
    })
    rows = [{
        "path": name, "size_bytes": len(data), "sha256": _sha(data),
    } for name, data in sorted(payloads.items())]
    manifest = {
        "schema": "rtdl.goal5790.home_evidence_manifest.v1",
        "goal": 5790,
        "manifest_self_referential": False,
        "manifest_member_listed_in_payloads": False,
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_bytes = _json_bytes(manifest)
    archive_payloads = dict(payloads)
    archive_payloads["MANIFEST.json"] = manifest_bytes
    evidence_bytes = _archive(archive_payloads)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(evidence_bytes)
    twin.write_bytes(evidence_bytes)
    if output.read_bytes() != twin.read_bytes():
        raise RuntimeError("Goal5790 evidence twin differs")
    recount = closure_state["recount"]
    home_result = closure_state["home_result"]
    result = {
        "schema": "rtdl.goal5790.home_functional_closure_result.v1",
        "goal": 5790,
        "status": "PASS__LOCAL_IMPLEMENTATION_AND_HOME_FUNCTIONAL_CLOSURE",
        "t0_scope": {
            "t0_result_sha256": (
                "65156de60922566648fb84bda8cc94d93885ea39e533e626d28a6a4b4cb2f420"),
            "triangle_weighted_rt_2a1_retained": True,
            "particle_excluded_by_kill_gate": True,
            "retained_mechanism": "compiler_fused_checked_u64_device_reduction",
        },
        "goal5789_contract_authority": {
            "result_sha256": (
                "58db251b0b676caee75b8bb70cfca08fb589d570947c22e389caa242239128a2"),
            "shared_contract_freeze_file_sha256": home_result[
                "shared_contract_freeze_file_sha256"],
            "shared_contract_freeze_sha256": closure_state[
                "target_authority"]["shared_contract_freeze_sha256"],
        },
        "candidate_v8": {
            "bundle_sha256": EXPECTED_BUNDLE_SHA256,
            "source_archive_sha256": EXPECTED_SOURCE_SHA256,
            "source_tree_sha256": EXPECTED_SOURCE_TREE_SHA256,
            "source_manifest_sha256": EXPECTED_SOURCE_MANIFEST_SHA256,
            "executing_harness_sha256": home_result[
                "executing_harness_sha256"],
            "focused_test_count": 76,
            "focused_tests_passed": True,
        },
        "home_closure": {
            "environment_class": "HOME_PASCAL_FUNCTIONAL_ONLY",
            "gpu": home_result["gpu"],
            "home_machine_authority_sha256": home_result[
                "home_machine_authority_sha256"],
            "native_library_sha256": EXPECTED_NATIVE_SHA256,
            "target_materialization_receipt_sha256": closure_state[
                "target_authority"]["receipt_sha256"],
            "target_materialization_evidence_sha256": closure_state[
                "target_evidence_sha256"],
            "target_program_inspection_sha256": closure_state[
                "target_program_inspection_sha256"],
            "ptx_program_identity_sha256": recount[
                "ptx_program_identity_sha256"],
            **{key: recount[key] for key in (
                "exact_lane_count", "behavioral_true_optix_lane_count",
                "fresh_parent_pid_count", "traversal_receipt_count",
                "operation_receipt_count", "successful_operation_event_count",
                "invalid_traversal_or_operation_receipt_count",
                "formal_worker_count", "registered_performance_timing_count",
            )},
            "operation_receipt_count_by_variant": closure_state[
                "receipt_counts"],
            "successful_operation_event_count_by_variant": closure_state[
                "event_counts"],
            "small_fixture_lane_count": recount["small_fixture_lane_count"],
            "bounded_real_smoke_lane_count": recount[
                "bounded_real_smoke_lane_count"],
            "bounded_real_dataset_count": recount[
                "bounded_real_dataset_count"],
            "bounded_view_triangle_oracles": recount[
                "bounded_view_triangle_oracles"],
            "linux_and_windows_recount_byte_identical": True,
            "linux_and_windows_recount_sha256": EXPECTED_RECOUNT_SHA256,
            "raw_lane_manifest": closure_state["raw_rows"],
        },
        "failure_lineage": lineage,
        "cache_cubin_boundary": {
            "record_sha256": _sha(_json_bytes(cache_label)),
            "cache_file_count": cache_label["cache_file_count"],
            "cache_file_bytes": cache_label["cache_file_bytes"],
            "scientific_program_authority": False,
            "included_in_evidence_archive": False,
        },
        "evidence": {
            "archive_sha256": _sha(evidence_bytes),
            "twin_byte_identical": True,
            "manifest_sha256": _sha(manifest_bytes),
            "payload_count": manifest["payload_count"],
            "payload_bytes": manifest["payload_bytes"],
            "local_closure_file_count_rehashed": inventory["file_count"],
            "local_closure_file_bytes_rehashed": inventory["file_bytes"],
            "manifest_self_referential": False,
            "authoritative_result_in_archive": False,
        },
        "claim_boundary": {
            "home_functional_only": True,
            "correctness_and_behavioral_optix_claimed": True,
            "compiler_fusion_mechanism_implemented": True,
            "compiler_fusion_performance_demonstrated": False,
            "registered_performance_result_created": False,
            "home_timing_used_for_claim": False,
            "pod_used": False,
            "modern_rtx_execution_authorized": False,
            "goal5791_authorized_or_executed": False,
            "raw_generated_ptx_preserved": False,
            "opaque_compiled_binary_attestation_claimed": False,
            "public_production_or_submission_claimed": False,
        },
    }
    result_path.write_bytes(_json_bytes(result))
    return {
        "evidence_archive_sha256": _sha(evidence_bytes),
        "evidence_manifest_sha256": _sha(manifest_bytes),
        "evidence_payload_count": manifest["payload_count"],
        "evidence_payload_bytes": manifest["payload_bytes"],
        "result_sha256": _sha_file(result_path),
        "result_path": str(result_path),
        "twin_byte_identical": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--closure", type=Path, default=DEFAULT_CLOSURE)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(
        closure=args.closure, bundle=args.bundle, source=args.source,
        output=args.output, twin=args.twin, result_path=args.result,
    ), sort_keys=True))


if __name__ == "__main__":
    main()
