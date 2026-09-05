#!/usr/bin/env python3
"""Independently recount the retained Goal5846 startup evidence.

This verifier intentionally imports neither RTDL nor any GPU package. It
recomputes seals, cache identities, worker transport, traversal-stamp
invariants, timing estimands, source bindings, and the final authority using
only the Python standard library and retained evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = ROOT / "history/internal_docs/goal5846_relation_startup_20260905"
EVIDENCE_ROOT = GOAL_ROOT / "evidence/pod_capture"
PROVENANCE_ROOT = GOAL_ROOT / "evidence/provenance"
PREREGISTRATION_PATH = GOAL_ROOT / "PREREGISTRATION.json"
AUTHORITY_PATH = GOAL_ROOT / "GOAL5846_INTERNAL_AUTHORITY.json"

SOURCE_COMMIT = "a6f395cc9411cbed3045c11145d92eda3bc2f502"
SOURCE_TREE = "19546ddeaee191de3e756cd1c14d979a8387fec7"
RTDL_ARM = "RTDL_PUBLIC_RELATION_OVERLAPPED_WARM_CACHE_V1"
PYOPTIX_ARM = "PINNED_PYOPTIX_COMPATIBLE_API"
ARMS = (RTDL_ARM, PYOPTIX_ARM)
TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
INPUT_SHA256 = "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e"
OUTPUT_SHA256 = "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77"
PREREGISTRATION_FILE_SHA256 = (
    "aff9abe35ec9a01b8bb9b41695b29c975c6ca4a74e66b77050fbc5798ca1ced2"
)
PREREGISTRATION_SHA256 = (
    "53111d83efc13497edae9f2721edaad5255b0bc8f268f721289f2752183d541b"
)
CACHE_PREPARATION_FILE_SHA256 = (
    "3fd9927ee1c605f97a9bd1800220007f165bbd26af369fa24aa256d84aa13d16"
)
CACHE_PREPARATION_SHA256 = (
    "c09edd09bd10e0c88c473376bbc3b37d0a7ab1c091acd75c88dc016e229618d8"
)
SUMMARY_FILE_SHA256 = (
    "6ee6a95e932daf8bf473e5c18fbbeba6e784126004eb608c6bbe8439b7f92207"
)
SUMMARY_SHA256 = "12f35f8a8665272274189c6d077d977f771d5610de22fd362ae6ee094c19e171"
BUILD_MANIFEST_FILE_SHA256 = (
    "b18cb198aedda56a08e95edb372d86d57a027119c63474fc4e83c09a566acc47"
)
BUILD_MANIFEST_RESULT_SHA256 = (
    "c63f9d9f3694fd7d04347e6ca79ca1d3bc286df0b60c3757e60c6cb2bc055d06"
)
LEAF_MANIFEST_SHA256 = (
    "2db7c1aeb6f80a77646a7eda4878244769459c138898f28b27c8666e9a5554f9"
)
EXECUTABLE_MANIFEST_SHA256 = (
    "6a6d06deb8a760f1e5b7e58146f600b2494b971278f170cb1b5809e563328236"
)
DEVICE_SOURCE_SHA256 = (
    "dcfb335a2a63ab609d21ce0361d0d530f148d157bd98b122989df0dab51f17a8"
)
PYOPTIX_BUILD_RECEIPT_FILE_SHA256 = (
    "a05317ef879630fe9de3aced08fe2ce35ee9416e684799e1f571e64c4c9abfd4"
)
PYOPTIX_BUILD_RECEIPT_SHA256 = (
    "06e8ea1d7ea3894972b5a4d6ca8b8860e526be0d6c5cf5a19c8b19aafd88a30e"
)
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
PYOPTIX_EXTENSION_SHA256 = (
    "7a7c555635062180e8f5d6246e41e8c7033e287218e963668eb34365f3e1b927"
)
NATIVE_SHA256 = "c56343fad27b4084566febbafeddca19f89c04fc66a0b878ca94417b64d2163e"
NATIVE_BYTES = 7_191_992
WARM_SYMBOL = "rtdl_optix_v4_warm_runtime_v1"
RELATION_SYMBOL = "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8"
PROGRAM_BUNDLE = "v4_custom_aabb_bounded_relation_composed"
ROUTE_IDENTITY = "v4_callback_ir:custom_aabb_bounded_relation_v1"
SEMANTIC_SHA256 = "bf11f78f35ae8fc59cdcdc453c6e7ad479112b54a3556d5d21be3418be327d4b"
STARTUP_RATIO_LIMIT = 1.25
WORST_STARTUP_RATIO_LIMIT = 2.0
GOAL5845_STEADY_REFERENCE_NS = 366_340
STEADY_MEDIAN_REGRESSION_LIMIT = 1.15
STEADY_WORST_WORKER_REGRESSION_LIMIT = 1.25

EXPECTED_HARDWARE = {
    "compute_capability": "8.9",
    "driver_version": "580.159.04",
    "gpu_name": "NVIDIA RTX 2000 Ada Generation",
    "gpu_uuid": "GPU-4b436f5f-bf8f-1d8c-0202-98e6e7b387e9",
    "memory_mib": 16_380,
}
WORKER_CLAIM = {
    "engineering_evidence_only": True,
    "external_review_complete": False,
    "public_or_manuscript_claim_authorized": False,
}
SUMMARY_CLAIM = {
    "cross_hardware_generalization_authorized": False,
    "external_review_complete": False,
    "internal_engineering_evidence_only": True,
    "precompiled_pyoptix_sensitivity_is_separate": True,
    "public_or_manuscript_claim_authorized": False,
}


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Goal5846 JSON object required: {path}")
    return value


def _verify_removed_field_seal(
    value: dict[str, object], field: str, *, label: str
) -> None:
    body = dict(value)
    observed = body.pop(field, None)
    if type(observed) is not str or observed != _digest(body):
        raise RuntimeError(f"Goal5846 {label} seal differs")


def _verify_build_seal(value: dict[str, object]) -> None:
    body = dict(value)
    body["result_sha256"] = ""
    schema = value.get("schema")
    if type(schema) is not str:
        raise RuntimeError("Goal5846 build schema differs")
    expected = hashlib.sha256(
        schema.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()
    if value.get("result_sha256") != expected:
        raise RuntimeError("Goal5846 build result seal differs")


def _git_blob(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _timing(value: object, expected_count: int, *, label: str) -> list[int]:
    expected_fields = {
        "sample_count",
        "samples_ns",
        "minimum_ns",
        "median_ns",
        "maximum_ns",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise RuntimeError(f"Goal5846 {label} timing schema differs")
    samples = value.get("samples_ns")
    if (
        value.get("sample_count") != expected_count
        or not isinstance(samples, list)
        or len(samples) != expected_count
        or any(type(item) is not int or item <= 0 for item in samples)
        or value.get("minimum_ns") != min(samples)
        or value.get("median_ns") != int(statistics.median(samples))
        or value.get("maximum_ns") != max(samples)
    ):
        raise RuntimeError(f"Goal5846 {label} timing values differ")
    return [int(item) for item in samples]


def _program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _mix(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    state &= mask
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value = (value ^ (value >> 31)) & mask
    return (
        state
        ^ (value + 0x9E3779B97F4A7C15 + ((state << 6) & mask) + (state >> 2))
    ) & mask


def _validate_compact_receipt(receipt: object) -> int:
    expected_fields = {
        "schema",
        "provider_library_sha256",
        "route_identity",
        "semantic_digest",
        "output_digest",
        "physical_executor_classification",
        "expected_program_bundle",
        "expected_program_bundle_id",
        "expected_program_observed_at_receipt_edge",
        "native_stamp",
        "receipt_sha256",
    }
    if not isinstance(receipt, dict) or set(receipt) != expected_fields:
        raise RuntimeError("Goal5846 compact receipt schema differs")
    _verify_removed_field_seal(receipt, "receipt_sha256", label="compact receipt")
    bundle_id = _program_bundle_id(PROGRAM_BUNDLE)
    if (
        receipt.get("schema")
        != "rtdl.physical_execution.compact_traversal_receipt.v1"
        or receipt.get("provider_library_sha256") != NATIVE_SHA256
        or receipt.get("route_identity") != ROUTE_IDENTITY
        or receipt.get("semantic_digest") != SEMANTIC_SHA256
        or receipt.get("output_digest") != OUTPUT_SHA256
        or receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or receipt.get("expected_program_bundle") != PROGRAM_BUNDLE
        or receipt.get("expected_program_bundle_id") != bundle_id
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
    ):
        raise RuntimeError("Goal5846 compact receipt envelope differs")
    stamp = receipt.get("native_stamp")
    if (
        not isinstance(stamp, list)
        or len(stamp) != 19
        or any(type(item) is not int or not 0 <= item < 1 << 64 for item in stamp)
    ):
        raise RuntimeError("Goal5846 compact native stamp schema differs")
    if (
        stamp[0] == 0
        or stamp[1] == 0
        or stamp[1] != stamp[2]
        or stamp[3:10] != [2, 2, 0, 2, 0, 2, 8192]
        or stamp[10] != bundle_id
        or stamp[11] != bundle_id
        or stamp[12] == 0
        or stamp[13] == 0
        or stamp[14:17] != [0, 0, 0]
        or stamp[17] != _mix(_mix(0, bundle_id), bundle_id)
        or stamp[18] != _mix(_mix(0, stamp[12]), stamp[13])
    ):
        raise RuntimeError("Goal5846 compact native stamp semantics differ")
    return int(stamp[0])


def _validate_preregistration() -> dict[str, object]:
    if _sha256_file(PREREGISTRATION_PATH) != PREREGISTRATION_FILE_SHA256:
        raise RuntimeError("Goal5846 preregistration file hash differs")
    value = _load(PREREGISTRATION_PATH)
    _verify_removed_field_seal(
        value, "preregistration_sha256", label="preregistration"
    )
    design = value.get("design")
    gates = value.get("pass_gates")
    claim = value.get("claim_boundary")
    if (
        value.get("schema")
        != "rtdl.goal5846.relation_startup_preregistration.v1"
        or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION"
        or value.get("preregistration_sha256") != PREREGISTRATION_SHA256
        or value.get("arms") != list(ARMS)
        or value.get("task")
        != {
            "id": TASK,
            "input_sha256": INPUT_SHA256,
            "output_sha256": OUTPUT_SHA256,
            "source_count": 4096,
            "indexed_count": 4096,
            "canonical_row_count": 4096,
            "public_contract": "canonical_u32_relation_rows",
        }
        or not isinstance(design, dict)
        or design.get("blocks") != 8
        or design.get("warmups_per_worker") != 16
        or design.get("samples_per_worker") != 128
        or design.get("samples_per_arm") != 1024
        or design.get("sample_discard_count") != 0
        or design.get("balanced_alternating_order") is not True
        or design.get("fresh_process_per_arm_per_block") is not True
        or not isinstance(gates, dict)
        or gates.get("median_within_block_setup_ratio_at_most")
        != STARTUP_RATIO_LIMIT
        or gates.get("worst_block_setup_ratio_at_most")
        != WORST_STARTUP_RATIO_LIMIT
        or gates.get("goal5845_steady_reference_ns")
        != GOAL5845_STEADY_REFERENCE_NS
        or gates.get("pooled_rtdl_steady_regression_at_most")
        != STEADY_MEDIAN_REGRESSION_LIMIT
        or gates.get("worst_worker_rtdl_steady_regression_at_most")
        != STEADY_WORST_WORKER_REGRESSION_LIMIT
        or not isinstance(claim, dict)
        or claim.get("internal_engineering_evidence_only") is not True
        or claim.get("public_or_manuscript_claim_authorized") is not False
        or claim.get("external_review_complete") is not False
        or claim.get("precompiled_pyoptix_parity_claim_authorized") is not False
        or claim.get("all_setup_performance_debt_closed_claim_authorized")
        is not False
    ):
        raise RuntimeError("Goal5846 preregistration contract differs")
    blob = _git_blob(
        "history/internal_docs/goal5846_relation_startup_20260905/"
        "PREREGISTRATION.json"
    )
    if hashlib.sha256(blob).hexdigest() != PREREGISTRATION_FILE_SHA256:
        raise RuntimeError("Goal5846 preregistration Git binding differs")
    return value


def _validate_cache_manifest(
    *, name: str, file_sha256: str, schema: str, expected_count: int
) -> tuple[dict[str, object], list[list[object]]]:
    path = EVIDENCE_ROOT / f"{name}-cache-manifest.json"
    if _sha256_file(path) != file_sha256:
        raise RuntimeError(f"Goal5846 {name} cache manifest hash differs")
    value = _load(path)
    rows = value.get("entries")
    expected_root = f"/workspace/goal5846-a6f395cc9-formal/{name}-cache"
    if (
        set(value)
        != {"schema", "cache_root", "entry_count", "entries_sha256", "entries"}
        or value.get("schema") != schema
        or value.get("cache_root") != expected_root
        or not isinstance(rows, list)
        or value.get("entry_count") != expected_count
        or len(rows) != expected_count
        or value.get("entries_sha256") != _digest(rows)
    ):
        raise RuntimeError(f"Goal5846 {name} cache manifest differs")
    snapshot: list[list[object]] = []
    observed = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "key_sha256",
            "artifact_json_sha256",
            "artifact_json_size_bytes",
        }:
            raise RuntimeError(f"Goal5846 {name} cache row differs")
        key = row["key_sha256"]
        if type(key) is not str or len(key) != 64 or key in observed:
            raise RuntimeError(f"Goal5846 {name} cache key differs")
        observed.add(key)
        artifact = EVIDENCE_ROOT / f"{name}-cache/{key}/artifact.json"
        if (
            not artifact.is_file()
            or artifact.stat().st_size != row["artifact_json_size_bytes"]
            or _sha256_file(artifact) != row["artifact_json_sha256"]
        ):
            raise RuntimeError(f"Goal5846 {name} cache artifact differs")
        document = _load(artifact)
        if document.get("key_sha256") != key or _digest(document.get("key")) != key:
            raise RuntimeError(f"Goal5846 {name} cache artifact key differs")
        if name == "executable":
            if (
                document.get("schema") != "rtdl.v4.executable_cache_entry.v1"
                or document.get("payload_sha256")
                != _digest(document.get("payload"))
            ):
                raise RuntimeError("Goal5846 executable cache payload differs")
        elif document.get("schema") != "rtdl.v4.formal_numba_leaf_cache.v1":
            raise RuntimeError("Goal5846 leaf cache payload differs")
        snapshot.append(
            [f"{key}/artifact.json", artifact.stat().st_size, _sha256_file(artifact)]
        )
    files = sorted((EVIDENCE_ROOT / f"{name}-cache").rglob("*"))
    if [path for path in files if path.is_file()] != [
        EVIDENCE_ROOT / f"{name}-cache/{row[0]}" for row in snapshot
    ]:
        raise RuntimeError(f"Goal5846 {name} cache membership differs")
    return value, snapshot


def _validate_cache_preparation() -> dict[str, object]:
    path = EVIDENCE_ROOT / "CACHE_PREPARATION.json"
    if _sha256_file(path) != CACHE_PREPARATION_FILE_SHA256:
        raise RuntimeError("Goal5846 cache preparation file hash differs")
    value = _load(path)
    _verify_removed_field_seal(value, "preparation_sha256", label="cache preparation")
    leaf, leaf_snapshot = _validate_cache_manifest(
        name="leaf",
        file_sha256=LEAF_MANIFEST_SHA256,
        schema="rtdl.v4.formal_numba_leaf_cache_manifest.v1",
        expected_count=7,
    )
    executable, executable_snapshot = _validate_cache_manifest(
        name="executable",
        file_sha256=EXECUTABLE_MANIFEST_SHA256,
        schema="rtdl.v4.executable_cache_manifest.v1",
        expected_count=1,
    )
    first = value.get("first_ever_cache_fill")
    leaf_record = value.get("leaf_cache")
    executable_record = value.get("executable_cache")
    native = value.get("native_library")
    native_manifest = value.get("native_build_manifest")
    if (
        value.get("schema")
        != "rtdl.goal5846.relation_startup_cache_preparation.v1"
        or value.get("status") != "PASS__FIRST_FILL_SEALED_AND_HIT_ONLY_REPLAY"
        or value.get("preparation_sha256") != CACHE_PREPARATION_SHA256
        or value.get("source_commit") != SOURCE_COMMIT
        or value.get("source_tree") != SOURCE_TREE
        or value.get("task") != TASK
        or value.get("claim_boundary")
        != {
            "cache_fill_excluded_from_formal_estimand": True,
            "gpu_execution_performed": False,
            "public_or_manuscript_claim_authorized": False,
        }
        or not isinstance(first, dict)
        or first.get("registered_performance_sample") is not False
        or any(
            type(first.get(key)) is not int or first[key] <= 0
            for key in (
                "route_declaration_ns",
                "generic_admission_ns",
                "materialize_and_compile_ns",
            )
        )
        or not (
            first["route_declaration_ns"]
            + first["generic_admission_ns"]
            + first["materialize_and_compile_ns"]
            <= first.get("total_ns", 0)
            <= first["route_declaration_ns"]
            + first["generic_admission_ns"]
            + first["materialize_and_compile_ns"]
            + 1_000_000
        )
        or type(value.get("sealed_replay_ns")) is not int
        or value["sealed_replay_ns"] <= 0
        or not isinstance(leaf_record, dict)
        or leaf_record.get("entry_count") != 7
        or leaf_record.get("manifest_sha256") != LEAF_MANIFEST_SHA256
        or leaf_record.get("entries_sha256") != leaf["entries_sha256"]
        or leaf_record.get("snapshot") != leaf_snapshot
        or not isinstance(executable_record, dict)
        or executable_record.get("entry_count") != 1
        or executable_record.get("manifest_sha256")
        != EXECUTABLE_MANIFEST_SHA256
        or executable_record.get("entries_sha256")
        != executable["entries_sha256"]
        or executable_record.get("snapshot") != executable_snapshot
        or not isinstance(native, dict)
        or native.get("sha256") != NATIVE_SHA256
        or native.get("bytes") != NATIVE_BYTES
        or not isinstance(native_manifest, dict)
        or native_manifest.get("sha256") != BUILD_MANIFEST_FILE_SHA256
    ):
        raise RuntimeError("Goal5846 cache preparation differs")
    identity = value.get("executable_identity")
    if not isinstance(identity, dict):
        raise RuntimeError("Goal5846 executable identity is absent")
    _verify_removed_field_seal(identity, "identity_sha256", label="executable identity")
    if identity.get("provider_artifact_sha256") != NATIVE_SHA256:
        raise RuntimeError("Goal5846 executable provider identity differs")
    return value


def _validate_build_manifest() -> dict[str, object]:
    path = EVIDENCE_ROOT / "native/BUILD_MANIFEST.json"
    if _sha256_file(path) != BUILD_MANIFEST_FILE_SHA256:
        raise RuntimeError("Goal5846 build manifest file hash differs")
    value = _load(path)
    _verify_build_seal(value)
    repository = value.get("repository")
    build_input = value.get("build_input")
    native = value.get("native_output")
    if (
        value.get("result_sha256") != BUILD_MANIFEST_RESULT_SHA256
        or value.get("status")
        != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        or value.get("all_required_symbols_exported") is not True
        or not isinstance(repository, dict)
        or repository.get("expected_commit") != SOURCE_COMMIT
        or repository.get("head_before") != SOURCE_COMMIT
        or repository.get("head_after") != SOURCE_COMMIT
        or repository.get("clean_before") is not True
        or repository.get("clean_after") is not True
        or repository.get("origin_url") != "https://github.com/rubaolee/rtdl"
        or not isinstance(build_input, dict)
        or value.get("build_input_sha256") != _digest(build_input)
        or build_input.get("compute_capability") != "8.9"
        or build_input.get("cuda_visible_devices") != "0"
        or build_input.get("expected_optix_sdk") != "9.0.0"
        or build_input.get("optix_version") != 90000
        or build_input.get("optimization") != "O3"
        or build_input.get("language_standard") != "c++17"
        or build_input.get("gpu")
        != {
            "compute_capability": "8.9",
            "driver_version": "580.159.04",
            "name": "NVIDIA RTX 2000 Ada Generation",
            "uuid": EXPECTED_HARDWARE["gpu_uuid"],
        }
        or not isinstance(native, dict)
        or native.get("sha256") != NATIVE_SHA256
        or native.get("bytes") != NATIVE_BYTES
    ):
        raise RuntimeError("Goal5846 native build identity differs")
    source_rows = repository.get("source_files")
    if not isinstance(source_rows, list) or len(source_rows) != 10:
        raise RuntimeError("Goal5846 native build source set differs")
    observed = set()
    for row in source_rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise RuntimeError("Goal5846 native source record differs")
        source_path = row["path"]
        if type(source_path) is not str or source_path in observed:
            raise RuntimeError("Goal5846 native source membership differs")
        observed.add(source_path)
        blob = _git_blob(source_path)
        if len(blob) != row["bytes"] or hashlib.sha256(blob).hexdigest() != row["sha256"]:
            raise RuntimeError("Goal5846 native source Git binding differs")
    if not {
        "src/native/optix/rtdl_optix_api.cpp",
        "src/native/optix/rtdl_optix_core.cpp",
        "src/native/optix/rtdl_optix_workloads.cpp",
        "src/native/optix/rtdl_optix_cuda_helpers.cu",
    }.issubset(observed):
        raise RuntimeError("Goal5846 native source closure differs")
    return value


def _validate_pyoptix_build_receipt() -> dict[str, object]:
    path = PROVENANCE_ROOT / "pyoptix_build_receipt.json"
    if _sha256_file(path) != PYOPTIX_BUILD_RECEIPT_FILE_SHA256:
        raise RuntimeError("Goal5846 PyOptiX build receipt file hash differs")
    value = _load(path)
    _verify_removed_field_seal(value, "receipt_sha256", label="PyOptiX build receipt")
    source = value.get("pyoptix_source")
    installed = value.get("installed")
    extension = installed.get("loaded_extension") if isinstance(installed, dict) else None
    if (
        value.get("receipt_sha256") != PYOPTIX_BUILD_RECEIPT_SHA256
        or value.get("status")
        != "PASS__CLEAN_SOURCE_WHEEL_AND_LOADED_EXTENSION_BOUND"
        or value.get("registered_performance_timing_count") != 0
        or not isinstance(source, dict)
        or source.get("commit") != PYOPTIX_COMMIT
        or source.get("tree") != PYOPTIX_TREE
        or source.get("clean") is not True
        or not isinstance(extension, dict)
        or extension.get("sha256") != PYOPTIX_EXTENSION_SHA256
        or extension.get("bytes") != 2_630_616
    ):
        raise RuntimeError("Goal5846 PyOptiX build receipt differs")
    return value


def _validate_worker(
    worker: dict[str, object], *, arm: str, block: int, warmups: int, repetitions: int
) -> dict[str, object]:
    _verify_removed_field_seal(worker, "result_sha256", label="worker")
    expected = {
        "schema": "rtdl.goal5846.relation_startup.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "arm": arm,
        "block": block,
        "task": TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": warmups,
        "repetitions": repetitions,
        "python": "3.12.3",
        "output_sha256": OUTPUT_SHA256,
        "hardware": EXPECTED_HARDWARE,
        "claim_boundary": WORKER_CLAIM,
    }
    if any(worker.get(key) != item for key, item in expected.items()):
        raise RuntimeError(f"Goal5846 {arm} worker identity differs")
    measurements = worker.get("measurements")
    if not isinstance(measurements, dict):
        raise RuntimeError("Goal5846 worker measurements differ")
    samples = _timing(
        measurements.get("steady_public"), repetitions, label=f"{arm}.steady"
    )
    setup = measurements.get("setup_ns")
    identity = measurements.get("identity")
    evidence = measurements.get("evidence")
    first_ns = measurements.get("first_execution_ns")
    total_ns = measurements.get("setup_plus_first_ns")
    if (
        not isinstance(setup, dict)
        or not isinstance(identity, dict)
        or not isinstance(evidence, dict)
        or type(first_ns) is not int
        or first_ns <= 0
        or type(total_ns) is not int
        or total_ns <= 0
        or any(type(item) is not int or item <= 0 for item in setup.values())
        or evidence.get("public_output_sha256") != OUTPUT_SHA256
        or evidence.get("public_row_count") != 4096
    ):
        raise RuntimeError("Goal5846 worker measurement envelope differs")
    if arm == RTDL_ARM:
        if set(measurements) != {
            "first_execution_ns",
            "setup_plus_first_ns",
            "setup_ns",
            "steady_public",
            "identity",
            "evidence",
        }:
            raise RuntimeError("Goal5846 RTDL measurement schema differs")
        phases = {
            "native_initialization_start",
            "route_declaration",
            "generic_admission",
            "materialize",
            "prepare",
            "first_public_execution",
        }
        if (
            set(setup) != phases
            or sum(setup.values()) != total_ns
            or setup["first_public_execution"] != first_ns
            or set(evidence)
            != {
                "public_output_sha256",
                "public_row_count",
                "latest_compact_receipt",
                "immutable_output_reused",
                "two_actual_optix_launches",
                "sealed_caches_unchanged",
            }
            or evidence.get("immutable_output_reused") is not True
            or evidence.get("two_actual_optix_launches") is not True
            or evidence.get("sealed_caches_unchanged") is not True
            or identity.get("native_library_sha256") != NATIVE_SHA256
            or identity.get("native_build_manifest_sha256")
            != BUILD_MANIFEST_FILE_SHA256
            or identity.get("leaf_cache_manifest_sha256")
            != LEAF_MANIFEST_SHA256
            or identity.get("executable_cache_manifest_sha256")
            != EXECUTABLE_MANIFEST_SHA256
        ):
            raise RuntimeError("Goal5846 RTDL phases or evidence differ")
        executable = identity.get("generic_executable_identity")
        if not isinstance(executable, dict):
            raise RuntimeError("Goal5846 RTDL executable identity differs")
        _verify_removed_field_seal(
            executable, "identity_sha256", label="worker executable identity"
        )
        if executable.get("provider_artifact_sha256") != NATIVE_SHA256:
            raise RuntimeError("Goal5846 RTDL provider identity differs")
        return {
            "samples": samples,
            "nonce": _validate_compact_receipt(
                evidence.get("latest_compact_receipt")
            ),
        }
    if arm != PYOPTIX_ARM:
        raise RuntimeError("Goal5846 unknown worker arm")
    if (
        set(measurements)
        != {
            "first_execution_ns",
            "setup_plus_first_ns",
            "setup_ns",
            "steady_public",
            "attribution",
            "identity",
            "evidence",
        }
        or measurements.get("attribution") is not None
        or set(setup) != {"device_compile", "pipeline", "prepare", "close"}
        or setup["device_compile"] + setup["pipeline"] + setup["prepare"] + first_ns
        != total_ns
        or evidence.get("device_status") != 0
        or evidence.get("device_overflow") != 0
        or evidence.get("raw_event_count") != 8192
        or evidence.get("duplicate_count") != 4096
    ):
        raise RuntimeError("Goal5846 PyOptiX phases or evidence differ")
    source = identity.get("pyoptix_repository")
    extension = identity.get("loaded_extension")
    if (
        not isinstance(source, dict)
        or source.get("commit") != PYOPTIX_COMMIT
        or source.get("tree") != PYOPTIX_TREE
        or source.get("clean") is not True
        or source.get("status") != ""
        or identity.get("optix_api_version") != "9.0.0"
        or identity.get("pyoptix_distribution") != "pyoptix"
        or identity.get("pyoptix_distribution_version") != "9.1.0"
        or identity.get("pyoptix_build_receipt_sha256")
        != PYOPTIX_BUILD_RECEIPT_SHA256
        or identity.get("device_source_sha256") != DEVICE_SOURCE_SHA256
        or not isinstance(extension, dict)
        or extension.get("sha256") != PYOPTIX_EXTENSION_SHA256
        or extension.get("bytes") != 2_630_616
    ):
        raise RuntimeError("Goal5846 PyOptiX identity differs")
    return {"samples": samples}


def _expected_schedule() -> list[dict[str, object]]:
    rows = []
    for block in range(8):
        order = ARMS if block % 2 == 0 else (PYOPTIX_ARM, RTDL_ARM)
        for position, arm in enumerate(order):
            rows.append({"block": block, "position": position, "arm": arm})
    return rows


def _load_workers(summary: dict[str, object]) -> list[dict[str, object]]:
    root = EVIDENCE_ROOT / "registered-transaction/workers"
    paths = sorted(root.glob("block_*_*.json"))
    if len(paths) != 16:
        raise RuntimeError("Goal5846 retained worker count differs")
    by_key = {}
    nonces = set()
    for path in paths:
        worker = _load(path)
        block = worker.get("block")
        arm = worker.get("arm")
        if type(block) is not int or arm not in ARMS:
            raise RuntimeError("Goal5846 retained worker key differs")
        label = "rtdl" if arm == RTDL_ARM else "pyoptix"
        if path.name != f"block_{block:02d}_{label}.json" or (block, arm) in by_key:
            raise RuntimeError("Goal5846 worker filename or uniqueness differs")
        stdout = path.with_name(f"{path.stem}.stdout.txt")
        stderr = path.with_name(f"{path.stem}.stderr.txt")
        if (
            not stdout.is_file()
            or not stderr.is_file()
            or stderr.read_bytes() != b""
            or json.loads(stdout.read_text(encoding="utf-8")) != worker
        ):
            raise RuntimeError("Goal5846 retained worker transport differs")
        details = _validate_worker(
            worker, arm=str(arm), block=block, warmups=16, repetitions=128
        )
        if arm == RTDL_ARM:
            nonces.add(details["nonce"])
        by_key[(block, arm)] = worker
    if set(by_key) != {(block, arm) for block in range(8) for arm in ARMS}:
        raise RuntimeError("Goal5846 worker matrix differs")
    if len(nonces) != 8:
        raise RuntimeError("Goal5846 RTDL process nonce isolation differs")
    embedded = summary.get("workers")
    if not isinstance(embedded, list) or len(embedded) != 16:
        raise RuntimeError("Goal5846 embedded worker count differs")
    embedded_by_key = {
        (row.get("block"), row.get("arm")): row
        for row in embedded
        if isinstance(row, dict)
    }
    if embedded_by_key != by_key:
        raise RuntimeError("Goal5846 embedded and retained workers differ")
    return [by_key[(row["block"], row["arm"])] for row in _expected_schedule()]


def _validate_preflight() -> None:
    root = EVIDENCE_ROOT / "preflight-v3"
    for label, arm in (("rtdl", RTDL_ARM), ("pyoptix", PYOPTIX_ARM)):
        value = _load(root / f"{label}.json")
        _validate_worker(
            value, arm=arm, block=999, warmups=2, repetitions=4
        )


def _validate_post_formal() -> None:
    first = EVIDENCE_ROOT / "post-formal"
    second = EVIDENCE_ROOT / "post-formal-v2"
    first_tests = (first / "focused_tests.stderr.txt").read_text(encoding="utf-8")
    second_tests = (second / "focused_tests.stderr.txt").read_text(encoding="utf-8")
    if (
        "Ran 232 tests" not in first_tests
        or "FAILED (errors=2)" not in first_tests
        or "test_preregistration_is_bound_to_frozen_source_without_timing"
        not in first_tests
        or "test_v12_binds_v11_terminal_failure_and_recounts_frozen_rows"
        not in first_tests
        or "git', 'cat-file', '-e'" not in first_tests
        or "not in '04305fc820290cc183a599376f13d2fb48175233'" not in first_tests
    ):
        raise RuntimeError("Goal5846 retained shallow-clone failure differs")
    if "Ran 232 tests" not in second_tests or not second_tests.rstrip().endswith("OK"):
        raise RuntimeError("Goal5846 post-fetch focused tests differ")
    for root in (first, second):
        if (
            (root / "source_status.txt").read_bytes() != b""
            or (root / "gpu_processes.txt").read_bytes() != b""
            or (root / "source_commit.txt").read_text(encoding="utf-8").strip()
            != SOURCE_COMMIT
            or (root / "source_tree.txt").read_text(encoding="utf-8").strip()
            != SOURCE_TREE
            or (root / "native_sha256.txt").read_text(encoding="utf-8").split()[0]
            != NATIVE_SHA256
            or (root / "native_size.txt").read_text(encoding="utf-8").strip()
            != f"{NATIVE_BYTES} bytes"
        ):
            raise RuntimeError("Goal5846 post-formal identity differs")
        cache_hashes = (root / "cache_manifest_sha256.txt").read_text(
            encoding="utf-8"
        )
        if LEAF_MANIFEST_SHA256 not in cache_hashes or EXECUTABLE_MANIFEST_SHA256 not in cache_hashes:
            raise RuntimeError("Goal5846 post-formal cache hashes differ")
    symbols = {
        line.split()[-1]
        for line in (second / "native_defined_symbols.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.split()
    }
    if not {WARM_SYMBOL, RELATION_SYMBOL}.issubset(symbols):
        raise RuntimeError("Goal5846 post-formal native symbols differ")
    host = (second / "host_toolchain.txt").read_text(encoding="utf-8")
    for expected in (
        "Ubuntu 24.04",
        "NVIDIA RTX 2000 Ada Generation",
        EXPECTED_HARDWARE["gpu_uuid"],
        "release 12.8, V12.8.93",
        "Python 3.12.3",
    ):
        if str(expected) not in host:
            raise RuntimeError("Goal5846 host/toolchain record differs")


def _recount_summary(summary: dict[str, object]) -> dict[str, object]:
    _verify_removed_field_seal(summary, "summary_sha256", label="summary")
    workers = _load_workers(summary)
    schedule = _expected_schedule()
    design = {
        "blocks": 8,
        "warmups_per_worker": 16,
        "samples_per_worker": 128,
        "samples_per_arm": 1024,
        "balanced_alternating_order": True,
        "fresh_process_per_arm_per_block": True,
        "sample_discard_count": 0,
        "schedule": schedule,
    }
    if (
        summary.get("schema") != "rtdl.goal5846.relation_startup.summary.v1"
        or summary.get("status") != "PASS__GOAL5846_INTERNAL_STARTUP_TARGET_MET"
        or summary.get("source_commit") != SOURCE_COMMIT
        or summary.get("source_tree") != SOURCE_TREE
        or summary.get("hardware") != EXPECTED_HARDWARE
        or summary.get("design") != design
        or summary.get("claim_boundary") != SUMMARY_CLAIM
        or summary.get("task")
        != {
            "id": TASK,
            "query_count": 4096,
            "row_count": 4096,
            "public_contract": "canonical_u32_relation_rows",
            "same_input_and_output_contract": True,
        }
    ):
        raise RuntimeError("Goal5846 summary identity differs")
    by_key = {(row["block"], row["arm"]): row for row in workers}
    blocks = []
    all_samples = {RTDL_ARM: [], PYOPTIX_ARM: []}
    phase_values: dict[str, list[int]] = {}
    for row in workers:
        all_samples[row["arm"]].extend(
            row["measurements"]["steady_public"]["samples_ns"]
        )
        if row["arm"] == RTDL_ARM:
            for name, value in row["measurements"]["setup_ns"].items():
                phase_values.setdefault(name, []).append(value)
    for block in range(8):
        rtdl = by_key[(block, RTDL_ARM)]
        pyoptix = by_key[(block, PYOPTIX_ARM)]
        rtdl_setup = rtdl["measurements"]["setup_plus_first_ns"]
        pyoptix_setup = pyoptix["measurements"]["setup_plus_first_ns"]
        rtdl_steady = rtdl["measurements"]["steady_public"]["median_ns"]
        blocks.append(
            {
                "block": block,
                "order": [
                    row["arm"] for row in schedule if row["block"] == block
                ],
                "rtdl_setup_plus_first_ns": rtdl_setup,
                "pyoptix_setup_plus_first_ns": pyoptix_setup,
                "rtdl_over_pyoptix_setup_plus_first": rtdl_setup / pyoptix_setup,
                "rtdl_steady_median_ns": rtdl_steady,
                "rtdl_steady_over_goal5845_reference": (
                    rtdl_steady / GOAL5845_STEADY_REFERENCE_NS
                ),
            }
        )
    setup_ratios = [row["rtdl_over_pyoptix_setup_plus_first"] for row in blocks]
    rtdl_samples = all_samples[RTDL_ARM]
    pyoptix_samples = all_samples[PYOPTIX_ARM]
    primary = float(statistics.median(setup_ratios))
    worst_setup = max(setup_ratios)
    pooled_rtdl = int(statistics.median(rtdl_samples))
    pooled_pyoptix = int(statistics.median(pyoptix_samples))
    worst_steady = max(
        row["rtdl_steady_over_goal5845_reference"] for row in blocks
    )
    gates = {
        "all_workers_passed": len(workers) == 16,
        "all_registered_samples_retained": (
            len(rtdl_samples) == 1024 and len(pyoptix_samples) == 1024
        ),
        "median_setup_ratio_at_most_1_25": primary <= STARTUP_RATIO_LIMIT,
        "worst_setup_ratio_at_most_2_0": worst_setup <= WORST_STARTUP_RATIO_LIMIT,
        "pooled_rtdl_steady_regression_at_most_1_15": (
            pooled_rtdl / GOAL5845_STEADY_REFERENCE_NS
            <= STEADY_MEDIAN_REGRESSION_LIMIT
        ),
        "worst_worker_rtdl_steady_regression_at_most_1_25": (
            worst_steady <= STEADY_WORST_WORKER_REGRESSION_LIMIT
        ),
    }
    secondary = {
        "worst_block_setup_ratio": worst_setup,
        "worst_block_setup_ratio_limit": WORST_STARTUP_RATIO_LIMIT,
        "pooled_rtdl_steady_median_ns": pooled_rtdl,
        "pooled_pyoptix_steady_median_ns": pooled_pyoptix,
        "goal5845_rtdl_steady_reference_ns": GOAL5845_STEADY_REFERENCE_NS,
        "pooled_rtdl_steady_regression": (
            pooled_rtdl / GOAL5845_STEADY_REFERENCE_NS
        ),
        "worst_worker_rtdl_steady_regression": worst_steady,
    }
    if (
        summary.get("blocks") != blocks
        or summary.get("gates") != gates
        or summary.get("primary_estimand")
        != {
            "name": "median_within_block_rtdl_over_pyoptix_setup_plus_first",
            "value": primary,
            "pass_limit": STARTUP_RATIO_LIMIT,
        }
        or summary.get("secondary_estimands") != secondary
        or not all(gates.values())
    ):
        raise RuntimeError("Goal5846 summary recount differs")
    return {
        "median_within_block_rtdl_over_pyoptix_setup_plus_first": primary,
        "reciprocal_pyoptix_over_rtdl": 1.0 / primary,
        "worst_block_rtdl_over_pyoptix_setup_plus_first": worst_setup,
        "rtdl_first_block_ratio_median": statistics.median(setup_ratios[0::2]),
        "pyoptix_first_block_ratio_median": statistics.median(setup_ratios[1::2]),
        "median_rtdl_setup_plus_first_ns": statistics.median(
            [row["rtdl_setup_plus_first_ns"] for row in blocks]
        ),
        "median_pyoptix_setup_plus_first_ns": statistics.median(
            [row["pyoptix_setup_plus_first_ns"] for row in blocks]
        ),
        "pooled_rtdl_steady_median_ns": pooled_rtdl,
        "pooled_pyoptix_steady_median_ns": pooled_pyoptix,
        "rtdl_steady_over_pyoptix": pooled_rtdl / pooled_pyoptix,
        "rtdl_steady_over_goal5845_reference": (
            pooled_rtdl / GOAL5845_STEADY_REFERENCE_NS
        ),
        "registered_samples_per_arm": 1024,
        "sample_discard_count": 0,
        "block_rows": blocks,
        "median_rtdl_phase_ns": {
            name: statistics.median(values)
            for name, values in sorted(phase_values.items())
        },
    }


def _validate_summary_provenance(summary: dict[str, object]) -> None:
    provenance = summary.get("provenance")
    if not isinstance(provenance, dict):
        raise RuntimeError("Goal5846 summary provenance is absent")
    expected = {
        "preregistration": (PREREGISTRATION_FILE_SHA256, "preregistration_sha256", PREREGISTRATION_SHA256),
        "cache_preparation": (CACHE_PREPARATION_FILE_SHA256, "preparation_sha256", CACHE_PREPARATION_SHA256),
        "native_build_manifest": (BUILD_MANIFEST_FILE_SHA256, None, None),
        "leaf_cache_manifest": (LEAF_MANIFEST_SHA256, None, None),
        "executable_cache_manifest": (EXECUTABLE_MANIFEST_SHA256, None, None),
        "device_source": (DEVICE_SOURCE_SHA256, None, None),
        "pyoptix_build_receipt": (PYOPTIX_BUILD_RECEIPT_FILE_SHA256, None, None),
    }
    for name, (file_sha, semantic_name, semantic_sha) in expected.items():
        row = provenance.get(name)
        if not isinstance(row, dict) or row.get("sha256") != file_sha:
            raise RuntimeError(f"Goal5846 summary {name} provenance differs")
        if semantic_name is not None and row.get(semantic_name) != semantic_sha:
            raise RuntimeError(f"Goal5846 summary {name} semantic seal differs")
    native = provenance.get("native_library")
    if (
        not isinstance(native, dict)
        or native.get("sha256") != NATIVE_SHA256
        or native.get("bytes") != NATIVE_BYTES
        or native.get("required_symbols") != [WARM_SYMBOL, RELATION_SYMBOL]
    ):
        raise RuntimeError("Goal5846 summary native provenance differs")


def _validate_formal_transport(summary: dict[str, object]) -> None:
    if (EVIDENCE_ROOT / "FORMAL_CONTROLLER_STDERR.log").read_bytes() != b"":
        raise RuntimeError("Goal5846 formal controller stderr is non-empty")
    stdout = json.loads(
        (EVIDENCE_ROOT / "FORMAL_CONTROLLER_STDOUT.log").read_text(encoding="utf-8")
    )
    if stdout != summary:
        raise RuntimeError("Goal5846 formal controller stdout differs")


def _stored_files() -> list[dict[str, object]]:
    rows = []
    for base in (EVIDENCE_ROOT, PROVENANCE_ROOT):
        for path in sorted(base.rglob("*")):
            if path.is_file():
                rows.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "bytes": path.stat().st_size,
                        "sha256": _sha256_file(path),
                    }
                )
    return sorted(rows, key=lambda row: row["path"])


def build() -> dict[str, object]:
    preregistration = _validate_preregistration()
    cache = _validate_cache_preparation()
    build_manifest = _validate_build_manifest()
    pyoptix = _validate_pyoptix_build_receipt()
    if _sha256_file(PROVENANCE_ROOT / "matched_device.cu") != DEVICE_SOURCE_SHA256:
        raise RuntimeError("Goal5846 matched device source differs")
    _validate_preflight()
    _validate_post_formal()
    summary_path = EVIDENCE_ROOT / "registered-transaction/SUMMARY.json"
    if _sha256_file(summary_path) != SUMMARY_FILE_SHA256:
        raise RuntimeError("Goal5846 summary file hash differs")
    summary = _load(summary_path)
    if summary.get("summary_sha256") != SUMMARY_SHA256:
        raise RuntimeError("Goal5846 summary frozen seal differs")
    _validate_formal_transport(summary)
    result = _recount_summary(summary)
    _validate_summary_provenance(summary)

    authority: dict[str, object] = {
        "schema": "rtdl.goal5846.relation_startup.internal_authority.v1",
        "status": (
            "PASS__GOAL5846_EXACT_WARM_CACHE_FRESH_PROCESS_STARTUP_TARGET_MET__"
            "EXTERNAL_REVIEW_PENDING"
        ),
        "source": {
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
            "origin": "https://github.com/rubaolee/rtdl",
        },
        "task": preregistration["task"],
        "hardware": EXPECTED_HARDWARE,
        "result": result,
        "first_ever_cache_fill": cache["first_ever_cache_fill"],
        "evidence_identity": {
            "preregistration_file_sha256": PREREGISTRATION_FILE_SHA256,
            "preregistration_sha256": PREREGISTRATION_SHA256,
            "cache_preparation_file_sha256": CACHE_PREPARATION_FILE_SHA256,
            "cache_preparation_sha256": CACHE_PREPARATION_SHA256,
            "summary_file_sha256": SUMMARY_FILE_SHA256,
            "summary_sha256": SUMMARY_SHA256,
            "native_provider_sha256": NATIVE_SHA256,
            "native_provider_bytes": NATIVE_BYTES,
            "native_build_manifest_sha256": BUILD_MANIFEST_FILE_SHA256,
            "native_build_result_sha256": build_manifest["result_sha256"],
            "leaf_cache_manifest_sha256": LEAF_MANIFEST_SHA256,
            "executable_cache_manifest_sha256": EXECUTABLE_MANIFEST_SHA256,
            "device_source_sha256": DEVICE_SOURCE_SHA256,
            "pyoptix_build_receipt_file_sha256": (
                PYOPTIX_BUILD_RECEIPT_FILE_SHA256
            ),
            "pyoptix_build_receipt_sha256": pyoptix["receipt_sha256"],
            "pyoptix_source_commit": PYOPTIX_COMMIT,
            "pyoptix_source_tree": PYOPTIX_TREE,
        },
        "architecture_boundary": {
            "native_abi_app_neutral": True,
            "application_dispatch_added": False,
            "sealed_cache_policy_is_logical_hit_only_not_os_permission": True,
            "cache_bytes_unchanged_in_every_formal_worker": True,
            "generic_executable_identity_bound_to_provider": True,
            "prepared_target_reused": True,
            "two_actual_optix_launches_per_execution": True,
            "public_canonical_rows_returned": True,
        },
        "closure_boundary": {
            "exact_pinned_warm_cache_startup_debt_closed": True,
            "goal5845_prepared_steady_path_not_regressed": True,
            "first_ever_cache_fill_debt_closed": False,
            "precompiled_pyoptix_aot_parity_closed": False,
            "all_startup_performance_debt_closed": False,
            "native_dso_bytes_stored_in_git": False,
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "exact_task_hardware_and_comparison_contract_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "consensus_claimed": False,
            "cross_hardware_generalization_authorized": False,
            "precompiled_pyoptix_parity_claim_authorized": False,
            "intrinsic_language_or_api_speedup_claim_authorized": False,
            "arbitrary_workload_claim_authorized": False,
        },
        "post_formal": {
            "first_run_shallow_clone_history_error_count": 2,
            "source_change_between_test_runs": False,
            "historical_commit_fetched_before_second_run": (
                "04305fc820290cc183a599376f13d2fb48175233"
            ),
            "second_run_test_count": 232,
            "second_run_passed": True,
        },
        "stored_evidence_files": _stored_files(),
        "producer": {
            "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "sha256": _sha256_file(Path(__file__).resolve()),
            "imports_rtdl_or_gpu_package": False,
        },
    }
    authority["authority_sha256"] = _digest(authority)
    return authority


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        if AUTHORITY_PATH.exists() or AUTHORITY_PATH.is_symlink():
            raise FileExistsError(AUTHORITY_PATH)
        AUTHORITY_PATH.write_text(
            json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif _load(AUTHORITY_PATH) != value:
        raise RuntimeError("stored Goal5846 internal authority differs")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
