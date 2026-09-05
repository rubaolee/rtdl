#!/usr/bin/env python3
"""Independently recount the downloaded Goal5845 GPU evidence.

This verifier intentionally imports neither RTDL nor a GPU package.  It
recomputes worker seals, timing summaries, traversal stamp invariants, block
estimands, build/source bindings, and the final authority from retained files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = ROOT / "history/internal_docs/goal5845_relation_public_parity_20260904"
EVIDENCE_ROOT = GOAL_ROOT / "evidence"
PREREGISTRATION_PATH = GOAL_ROOT / "PREREGISTRATION.json"
AUTHORITY_PATH = GOAL_ROOT / "GOAL5845_INTERNAL_AUTHORITY.json"

RTDL_ARM = "RTDL_PUBLIC_RELATION_V8_COMPACT_STAMP"
PYOPTIX_ARM = "PINNED_PYOPTIX_COMPATIBLE_API"
ARMS = (RTDL_ARM, PYOPTIX_ARM)
SOURCE_COMMIT = "22c6a45020e3da6894fa108fe92d50fbd2c5aa27"
SOURCE_TREE = "d3efda68c1a1b7f70c6538e9f97daf73b3648731"
TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
INPUT_SHA256 = "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e"
OUTPUT_SHA256 = "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77"
PREREGISTRATION_SHA256 = (
    "2f246a54e172ec83e32ad93fa3c796c3c73ef9c2de54ded3b3fea63daf4d00db"
)
PREREGISTRATION_FILE_SHA256 = (
    "7b83ec092503e902590bad66b6a674b0c1216e62bfa433a75c943c8785334fb2"
)
SUMMARY_SHA256 = "7c5f47b6e8cf47968cf12b2db9b1982dd5f46493323b300413c73f9082ef031d"
SUMMARY_FILE_SHA256 = "c323577659896e3ec4298efab18f18eecc52b1ef9a2ad7334b699e2a90470046"
BUILD_MANIFEST_FILE_SHA256 = (
    "5cb4b9c5bc2bb6416ecbab71ae3e67c72ebd1c9fd7ed77264f8703e741b2e341"
)
BUILD_MANIFEST_RESULT_SHA256 = (
    "4e6bb20ee58f8299c01f736dffc35cebe2e5f559e7aa9b0d73352a46681ec32b"
)
NATIVE_SHA256 = "2383cc988ca7b5c99112c1b360a1c36380de88e750959fb4b17d9012d4e8efb8"
NATIVE_BYTES = 7_187_784
NATIVE_SYMBOL = "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v8"
DEVICE_SOURCE_SHA256 = (
    "dcfb335a2a63ab609d21ce0361d0d530f148d157bd98b122989df0dab51f17a8"
)
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
PYOPTIX_BUILD_RECEIPT_FILE_SHA256 = (
    "a05317ef879630fe9de3aced08fe2ce35ee9416e684799e1f571e64c4c9abfd4"
)
PYOPTIX_BUILD_RECEIPT_SHA256 = (
    "06e8ea1d7ea3894972b5a4d6ca8b8860e526be0d6c5cf5a19c8b19aafd88a30e"
)
PYOPTIX_EXTENSION_SHA256 = (
    "7a7c555635062180e8f5d6246e41e8c7033e287218e963668eb34365f3e1b927"
)
PROGRAM_BUNDLE = "v4_custom_aabb_bounded_relation_composed"
ROUTE_IDENTITY = "v4_callback_ir:custom_aabb_bounded_relation_v1"
SEMANTIC_SHA256 = "c5c31b1aa1d7b69db60e41e4dd9a510f2a453fe69373f900b019fb4eb1f2c8fa"
PRIMARY_LIMIT = 1.25
WORST_BLOCK_LIMIT = 1.50
PUBLIC_OVER_DIRECT_LIMIT = 1.75
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
    "public_or_manuscript_claim_authorized": False,
}
BUILD_SOURCE_PATHS = {
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
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
        raise TypeError(f"Goal5845 JSON object required: {path}")
    return value


def _verify_removed_field_seal(
    value: dict[str, object], field: str, *, label: str
) -> None:
    body = dict(value)
    observed = body.pop(field, None)
    if type(observed) is not str or observed != _digest(body):
        raise RuntimeError(f"Goal5845 {label} seal differs")


def _verify_build_seal(value: dict[str, object]) -> None:
    body = dict(value)
    body["result_sha256"] = ""
    schema = value.get("schema")
    if type(schema) is not str:
        raise RuntimeError("Goal5845 build schema differs")
    expected = hashlib.sha256(
        schema.encode("ascii") + b"\0" + _canonical_bytes(body)
    ).hexdigest()
    if value.get("result_sha256") != expected:
        raise RuntimeError("Goal5845 build result seal differs")


def _git_blob(path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def _timing(value: object, expected_count: int, *, label: str) -> list[int]:
    expected_fields = {
        "sample_count",
        "samples_ns",
        "minimum_ns",
        "median_ns",
        "maximum_ns",
    }
    if not isinstance(value, dict) or set(value) != expected_fields:
        raise RuntimeError(f"Goal5845 {label} timing schema differs")
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
        raise RuntimeError(f"Goal5845 {label} timing values differ")
    return samples


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
        state ^ (value + 0x9E3779B97F4A7C15 + ((state << 6) & mask) + (state >> 2))
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
        raise RuntimeError("Goal5845 compact receipt schema differs")
    _verify_removed_field_seal(receipt, "receipt_sha256", label="compact receipt")
    bundle_id = _program_bundle_id(PROGRAM_BUNDLE)
    if (
        receipt.get("schema") != "rtdl.physical_execution.compact_traversal_receipt.v1"
        or receipt.get("provider_library_sha256") != NATIVE_SHA256
        or receipt.get("route_identity") != ROUTE_IDENTITY
        or receipt.get("semantic_digest") != SEMANTIC_SHA256
        or receipt.get("output_digest") != OUTPUT_SHA256
        or receipt.get("physical_executor_classification") != "optix_traversal_observed"
        or receipt.get("expected_program_bundle") != PROGRAM_BUNDLE
        or receipt.get("expected_program_bundle_id") != bundle_id
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
    ):
        raise RuntimeError("Goal5845 compact receipt envelope differs")
    stamp = receipt.get("native_stamp")
    if (
        not isinstance(stamp, list)
        or len(stamp) != 19
        or any(type(item) is not int or not 0 <= item < 1 << 64 for item in stamp)
    ):
        raise RuntimeError("Goal5845 compact native stamp schema differs")
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
        raise RuntimeError("Goal5845 compact native stamp semantics differ")
    return stamp[0]


def _validate_fast_receipt(value: object) -> None:
    expected = {
        "schema_version": 2,
        "optix_launch_count": 2,
        "host_blocking_boundary_count": 2,
        "control_d2h_bytes": 28,
        "output_d2h_bytes": 32768,
        "status_before_output": True,
        "output_d2h_after_status_failure": 0,
        "role_counters_materialized": False,
        "prepared_input_reused": True,
        "dynamic_device_upload_call_count": 0,
        "dynamic_accel_build_count": 0,
        "dynamic_explicit_sync_count": 0,
        "dynamic_blocking_upload_call_count": 0,
        "dynamic_device_upload_bytes": 0,
        "semantic_compaction_launch_count": 1,
        "semantic_compaction_key_capacity": 8192,
        "semantic_compaction_scratch_bytes": 98312,
        "callback_status_kernel_launch_count": 0,
        "checked_product_kernel_launch_count": 0,
        "compact_control_finalizer_kernel_launch_count": 0,
        "total_auxiliary_cuda_kernel_launch_count": 1,
        "execution_parameter_h2d_bytes": 240,
        "execution_parameter_h2d_copy_call_count": 2,
        "stream_ordered_memset_call_count": 4,
        "status_d2h_copy_call_count": 1,
        "output_d2h_copy_call_count": 1,
    }
    if (
        not isinstance(value, dict)
        or set(value) != set(expected) | {"dynamic_input_generation"}
        or any(
            value.get(key) != expected_value for key, expected_value in expected.items()
        )
        or value.get("dynamic_input_generation") != 1
    ):
        raise RuntimeError("Goal5845 fast operation receipt differs")


def _validate_worker(
    worker: dict[str, object], *, arm: str, block: int
) -> dict[str, object]:
    _verify_removed_field_seal(worker, "result_sha256", label="worker")
    expected = {
        "schema": "rtdl.goal5845.relation_compact_execution.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": SOURCE_COMMIT,
        "source_tree": SOURCE_TREE,
        "arm": arm,
        "block": block,
        "task": TASK,
        "query_count": 4096,
        "row_count": 4096,
        "warmups": 16,
        "repetitions": 128,
        "python": "3.12.3",
        "output_sha256": OUTPUT_SHA256,
        "hardware": EXPECTED_HARDWARE,
        "claim_boundary": WORKER_CLAIM,
    }
    if any(worker.get(key) != value for key, value in expected.items()):
        raise RuntimeError(f"Goal5845 {arm} worker identity differs")
    measurements = worker.get("measurements")
    if not isinstance(measurements, dict) or set(measurements) != {
        "first_execution_ns",
        "steady_public",
        "attribution",
        "setup_ns",
        "identity",
        "evidence",
    }:
        raise RuntimeError("Goal5845 worker measurement schema differs")
    if (
        type(measurements.get("first_execution_ns")) is not int
        or measurements["first_execution_ns"] <= 0
    ):
        raise RuntimeError("Goal5845 first execution timing differs")
    _timing(measurements["steady_public"], 128, label=f"{arm}.steady")
    setup = measurements.get("setup_ns")
    if not isinstance(setup, dict) or any(
        type(item) is not int or item <= 0 for item in setup.values()
    ):
        raise RuntimeError("Goal5845 setup timing differs")
    evidence = measurements.get("evidence")
    identity = measurements.get("identity")
    if not isinstance(evidence, dict) or not isinstance(identity, dict):
        raise TypeError("Goal5845 worker evidence must be mappings")
    if (
        evidence.get("public_output_sha256") != OUTPUT_SHA256
        or evidence.get("public_row_count") != 4096
    ):
        raise RuntimeError("Goal5845 public output evidence differs")

    if arm == RTDL_ARM:
        if set(setup) != {
            "route_declaration",
            "generic_admission",
            "materialize",
            "prepare",
            "close",
        }:
            raise RuntimeError("Goal5845 RTDL setup schema differs")
        attribution = measurements.get("attribution")
        if not isinstance(attribution, dict) or set(attribution) != {
            "family_bridge",
            "protocol_lifecycle",
            "prepared_owner",
            "direct_native_v8",
            "explicit_full_diagnostic_ns",
        }:
            raise RuntimeError("Goal5845 RTDL attribution schema differs")
        for layer in (
            "family_bridge",
            "protocol_lifecycle",
            "prepared_owner",
            "direct_native_v8",
        ):
            _timing(attribution[layer], 64, label=f"RTDL.{layer}")
        if (
            type(attribution.get("explicit_full_diagnostic_ns")) is not int
            or attribution["explicit_full_diagnostic_ns"] <= 0
        ):
            raise RuntimeError("Goal5845 full diagnostic timing differs")
        if set(evidence) != {
            "public_output_sha256",
            "public_row_count",
            "latest_compact_receipt",
            "latest_fast_operation_receipt",
            "immutable_output_reused",
            "two_actual_optix_launches",
        }:
            raise RuntimeError("Goal5845 RTDL evidence schema differs")
        if (
            evidence.get("immutable_output_reused") is not True
            or evidence.get("two_actual_optix_launches") is not True
        ):
            raise RuntimeError("Goal5845 RTDL execution facts differ")
        _validate_fast_receipt(evidence.get("latest_fast_operation_receipt"))
        nonce = _validate_compact_receipt(evidence.get("latest_compact_receipt"))
        executable = identity.get("generic_executable_identity")
        if (
            set(identity) != {"native_library_sha256", "generic_executable_identity"}
            or identity.get("native_library_sha256") != NATIVE_SHA256
            or not isinstance(executable, dict)
            or executable.get("provider_artifact_sha256") != NATIVE_SHA256
            or executable.get("schema") != "rtdl.family_executable_identity.v1"
        ):
            raise RuntimeError("Goal5845 RTDL executable identity differs")
        _verify_removed_field_seal(
            executable, "identity_sha256", label="generic executable identity"
        )
        return {"nonce": nonce}

    if measurements.get("attribution") is not None:
        raise RuntimeError("Goal5845 PyOptiX attribution must be absent")
    if set(setup) != {"device_compile", "pipeline", "prepare", "close"}:
        raise RuntimeError("Goal5845 PyOptiX setup schema differs")
    repository = identity.get("pyoptix_repository")
    extension = identity.get("loaded_extension")
    if (
        set(evidence)
        != {
            "public_output_sha256",
            "public_row_count",
            "device_status",
            "device_overflow",
            "raw_event_count",
            "duplicate_count",
        }
        or evidence.get("device_status") != 0
        or evidence.get("device_overflow") != 0
        or evidence.get("raw_event_count") != 8192
        or evidence.get("duplicate_count") != 4096
        or not isinstance(repository, dict)
        or repository.get("commit") != PYOPTIX_COMMIT
        or repository.get("tree") != PYOPTIX_TREE
        or repository.get("clean") is not True
        or repository.get("status") != ""
        or identity.get("optix_api_version") != "9.0.0"
        or identity.get("pyoptix_distribution") != "pyoptix"
        or identity.get("pyoptix_distribution_version") != "9.1.0"
        or identity.get("pyoptix_build_receipt_sha256") != PYOPTIX_BUILD_RECEIPT_SHA256
        or identity.get("device_source_sha256") != DEVICE_SOURCE_SHA256
        or not isinstance(extension, dict)
        or extension.get("sha256") != PYOPTIX_EXTENSION_SHA256
        or extension.get("bytes") != 2_630_616
    ):
        raise RuntimeError("Goal5845 PyOptiX evidence differs")
    return {}


def _expected_schedule() -> list[dict[str, object]]:
    schedule = []
    for block in range(8):
        order = (
            (RTDL_ARM, PYOPTIX_ARM)
            if block % 2 == 0
            else (
                PYOPTIX_ARM,
                RTDL_ARM,
            )
        )
        for position, arm in enumerate(order):
            schedule.append({"block": block, "position": position, "arm": arm})
    return schedule


def _load_workers(summary: dict[str, object]) -> list[dict[str, object]]:
    root = EVIDENCE_ROOT / "formal_comparison/workers"
    paths = sorted(root.glob("block_*_*.json"))
    if len(paths) != 16:
        raise RuntimeError("Goal5845 retained worker count differs")
    workers = []
    keys = set()
    nonces = set()
    for path in paths:
        worker = _load(path)
        block = worker.get("block")
        arm = worker.get("arm")
        if type(block) is not int or arm not in ARMS:
            raise RuntimeError("Goal5845 retained worker key differs")
        expected_name = (
            f"block_{block:02d}_{'rtdl' if arm == RTDL_ARM else 'pyoptix'}.json"
        )
        if path.name != expected_name or (block, arm) in keys:
            raise RuntimeError(
                "Goal5845 retained worker filename or uniqueness differs"
            )
        keys.add((block, arm))
        stdout = path.with_name(f"{path.stem}.stdout.txt")
        stderr = path.with_name(f"{path.stem}.stderr.txt")
        if (
            not stdout.is_file()
            or not stderr.is_file()
            or stderr.read_bytes() != b""
            or json.loads(stdout.read_text(encoding="utf-8")) != worker
        ):
            raise RuntimeError("Goal5845 retained worker transport differs")
        details = _validate_worker(worker, arm=str(arm), block=block)
        if arm == RTDL_ARM:
            nonces.add(details["nonce"])
        workers.append(worker)
    if keys != {(block, arm) for block in range(8) for arm in ARMS}:
        raise RuntimeError("Goal5845 worker matrix differs")
    if len(nonces) != 8:
        raise RuntimeError("Goal5845 RTDL worker nonce isolation differs")
    embedded = summary.get("workers")
    if not isinstance(embedded, list) or len(embedded) != 16:
        raise RuntimeError("Goal5845 embedded workers differ")
    by_key = {(worker["block"], worker["arm"]): worker for worker in workers}
    embedded_keys = {
        (worker.get("block"), worker.get("arm"))
        for worker in embedded
        if isinstance(worker, dict)
    }
    if (
        embedded_keys != set(by_key)
        or any(
            worker != by_key.get((worker.get("block"), worker.get("arm")))
            for worker in embedded
            if isinstance(worker, dict)
        )
        or any(not isinstance(worker, dict) for worker in embedded)
    ):
        raise RuntimeError("Goal5845 embedded and retained workers differ")
    return [by_key[(item["block"], item["arm"])] for item in _expected_schedule()]


def _validate_preregistration() -> dict[str, object]:
    if _sha256_file(PREREGISTRATION_PATH) != PREREGISTRATION_FILE_SHA256:
        raise RuntimeError("Goal5845 preregistration file hash differs")
    value = _load(PREREGISTRATION_PATH)
    _verify_removed_field_seal(value, "preregistration_sha256", label="preregistration")
    if (
        value.get("preregistration_sha256") != PREREGISTRATION_SHA256
        or value.get("schema")
        != "rtdl.goal5845.relation_public_parity_preregistration.v1"
        or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION"
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
        or value.get("design")
        != {
            "blocks": 8,
            "balanced_alternating_order": True,
            "fresh_process_per_arm_per_block": True,
            "warmups_per_worker": 16,
            "samples_per_worker": 128,
            "samples_per_arm": 1024,
            "sample_discard_count": 0,
        }
    ):
        raise RuntimeError("Goal5845 preregistration contract differs")
    blob = _git_blob(
        "history/internal_docs/goal5845_relation_public_parity_20260904/PREREGISTRATION.json"
    )
    if hashlib.sha256(blob).hexdigest() != PREREGISTRATION_FILE_SHA256:
        raise RuntimeError("Goal5845 preregistration Git binding differs")
    return value


def _validate_build_manifest() -> dict[str, object]:
    path = EVIDENCE_ROOT / "native/build_manifest.json"
    if _sha256_file(path) != BUILD_MANIFEST_FILE_SHA256:
        raise RuntimeError("Goal5845 build manifest file hash differs")
    value = _load(path)
    _verify_build_seal(value)
    repository = value.get("repository")
    build_input = value.get("build_input")
    native = value.get("native_output")
    if (
        value.get("result_sha256") != BUILD_MANIFEST_RESULT_SHA256
        or value.get("status") != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
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
        raise RuntimeError("Goal5845 native build identity differs")
    source_rows = repository.get("source_files")
    if (
        not isinstance(source_rows, list)
        or {row.get("path") for row in source_rows if isinstance(row, dict)}
        != BUILD_SOURCE_PATHS
        or len(source_rows) != len(BUILD_SOURCE_PATHS)
    ):
        raise RuntimeError("Goal5845 native build source set differs")
    for row in source_rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise RuntimeError("Goal5845 native source record differs")
        blob = _git_blob(str(row["path"]))
        if (
            len(blob) != row["bytes"]
            or hashlib.sha256(blob).hexdigest() != row["sha256"]
        ):
            raise RuntimeError("Goal5845 native source Git binding differs")
    post = EVIDENCE_ROOT / "post_formal"
    if (
        (post / "source_status.txt").read_bytes() != b""
        or (post / "gpu_processes.txt").read_bytes() != b""
        or (post / "native_sha256.txt").read_text(encoding="utf-8").split()[0]
        != NATIVE_SHA256
        or (post / "native_size.txt").read_text(encoding="utf-8").strip()
        != f"{NATIVE_BYTES} bytes"
    ):
        raise RuntimeError("Goal5845 post-formal identity record differs")
    symbols = {
        line.split()[-1]
        for line in (post / "native_defined_symbols.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.split()
    }
    if NATIVE_SYMBOL not in symbols:
        raise RuntimeError("Goal5845 native v8 symbol evidence differs")
    tests = (post / "focused_tests.stderr.txt").read_text(encoding="utf-8")
    if "Ran 55 tests" not in tests or not tests.rstrip().endswith("OK"):
        raise RuntimeError("Goal5845 post-formal focused tests differ")
    return value


def _validate_preflight() -> None:
    root = EVIDENCE_ROOT / "preflight"
    for label, arm in (("rtdl", RTDL_ARM), ("pyoptix", PYOPTIX_ARM)):
        path = root / f"{label}.json"
        value = _load(path)
        stdout = json.loads((root / f"{label}.stdout").read_text(encoding="utf-8"))
        stderr = (root / f"{label}.stderr").read_bytes()
        _verify_removed_field_seal(value, "result_sha256", label="preflight")
        if (
            value != stdout
            or stderr != b""
            or value.get("arm") != arm
            or value.get("source_commit") != SOURCE_COMMIT
            or value.get("source_tree") != SOURCE_TREE
            or value.get("status") != "PASS__INTERNAL_ENGINEERING_WORKER"
            or value.get("output_sha256") != OUTPUT_SHA256
            or value.get("warmups") != 1
            or value.get("repetitions") != 1
        ):
            raise RuntimeError("Goal5845 preflight differs")


def _validate_transaction() -> dict[str, object]:
    value = _load(EVIDENCE_ROOT / "POD_TRANSACTION.json")
    _verify_removed_field_seal(value, "transaction_sha256", label="pod transaction")
    formal = value.get("formal_run")
    provider = value.get("native_provider")
    source = value.get("source")
    claim = value.get("claim_boundary")
    if (
        value.get("status") != "PASS__FORMAL_GPU_TRANSACTION_COMPLETE"
        or not isinstance(formal, dict)
        or formal.get("summary_file_sha256") != SUMMARY_FILE_SHA256
        or formal.get("summary_semantic_sha256") != SUMMARY_SHA256
        or formal.get("samples_per_arm") != 1024
        or formal.get("sample_discard_count") != 0
        or not isinstance(provider, dict)
        or provider.get("sha256") != NATIVE_SHA256
        or provider.get("required_symbol") != NATIVE_SYMBOL
        or not isinstance(source, dict)
        or source.get("commit") != SOURCE_COMMIT
        or source.get("tree") != SOURCE_TREE
        or source.get("clean_before_formal_run") is not True
        or source.get("clean_after_formal_run") is not True
        or not isinstance(claim, dict)
        or claim.get("internal_engineering_evidence_only") is not True
        or claim.get("public_or_manuscript_claim_authorized") is not False
        or claim.get("external_review_complete") is not False
    ):
        raise RuntimeError("Goal5845 pod transaction fields differ")
    return value


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
        summary.get("schema") != "rtdl.goal5845.relation_compact_execution.summary.v1"
        or summary.get("status") != "PASS__GOAL5845_INTERNAL_PERFORMANCE_TARGET_MET"
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
        raise RuntimeError("Goal5845 summary identity differs")

    by_key = {(worker["block"], worker["arm"]): worker for worker in workers}
    blocks = []
    rtdl_samples = []
    pyoptix_samples = []
    public_over_direct = []
    layer_samples = {
        "family_bridge": [],
        "protocol_lifecycle": [],
        "prepared_owner": [],
        "direct_native_v8": [],
    }
    diagnostics = []
    for worker in workers:
        values = worker["measurements"]["steady_public"]["samples_ns"]
        (rtdl_samples if worker["arm"] == RTDL_ARM else pyoptix_samples).extend(values)
        if worker["arm"] == RTDL_ARM:
            attribution = worker["measurements"]["attribution"]
            for layer, collected in layer_samples.items():
                collected.extend(attribution[layer]["samples_ns"])
            diagnostics.append(attribution["explicit_full_diagnostic_ns"])
    for block in range(8):
        rtdl = by_key[(block, RTDL_ARM)]
        pyoptix = by_key[(block, PYOPTIX_ARM)]
        rtdl_ns = rtdl["measurements"]["steady_public"]["median_ns"]
        pyoptix_ns = pyoptix["measurements"]["steady_public"]["median_ns"]
        direct_ns = rtdl["measurements"]["attribution"]["direct_native_v8"]["median_ns"]
        ratio = rtdl_ns / pyoptix_ns
        overhead = rtdl_ns / direct_ns
        public_over_direct.append(overhead)
        blocks.append(
            {
                "block": block,
                "rtdl_median_ns": rtdl_ns,
                "pyoptix_median_ns": pyoptix_ns,
                "direct_native_v8_median_ns": direct_ns,
                "rtdl_over_pyoptix": ratio,
                "rtdl_public_over_direct_native": overhead,
                "order": [item["arm"] for item in schedule if item["block"] == block],
            }
        )
    ratios = [row["rtdl_over_pyoptix"] for row in blocks]
    primary = float(statistics.median(ratios))
    worst = max(ratios)
    public_direct = float(statistics.median(public_over_direct))
    gates = {
        "all_workers_passed": len(workers) == 16,
        "all_samples_retained": len(rtdl_samples) == len(pyoptix_samples) == 1024,
        "median_within_block_ratio_at_most_1_25": primary <= PRIMARY_LIMIT,
        "worst_block_ratio_at_most_1_50": worst <= WORST_BLOCK_LIMIT,
        "median_public_over_direct_at_most_1_75": (
            public_direct <= PUBLIC_OVER_DIRECT_LIMIT
        ),
    }
    primary_row = {
        "name": "median_within_block_rtdl_over_pyoptix",
        "value": primary,
        "pass_limit": PRIMARY_LIMIT,
    }
    secondary = {
        "worst_block_rtdl_over_pyoptix": worst,
        "worst_block_pass_limit": WORST_BLOCK_LIMIT,
        "median_rtdl_public_over_direct_native": public_direct,
        "public_over_direct_pass_limit": PUBLIC_OVER_DIRECT_LIMIT,
        "pooled_rtdl_median_ns": int(statistics.median(rtdl_samples)),
        "pooled_pyoptix_median_ns": int(statistics.median(pyoptix_samples)),
    }
    if (
        summary.get("blocks") != blocks
        or summary.get("primary_estimand") != primary_row
        or summary.get("secondary_estimands") != secondary
        or summary.get("gates") != gates
        or not all(gates.values())
    ):
        raise RuntimeError("Goal5845 summary estimands do not reproduce")
    return {
        "block_rows": blocks,
        "median_within_block_rtdl_over_pyoptix": primary,
        "rtdl_over_pyoptix_speedup": 1.0 / primary,
        "worst_block_rtdl_over_pyoptix": worst,
        "pooled_rtdl_median_ns": secondary["pooled_rtdl_median_ns"],
        "pooled_pyoptix_median_ns": secondary["pooled_pyoptix_median_ns"],
        "median_rtdl_public_over_direct_native": public_direct,
        "pooled_attribution_median_ns": {
            layer: int(statistics.median(values))
            for layer, values in layer_samples.items()
        },
        "diagnostic_path_median_ns": int(statistics.median(diagnostics)),
        "public_samples_per_arm": 1024,
        "attribution_samples_per_layer": 512,
        "workers": 16,
        "all_samples_retained": True,
    }


def _validate_summary_provenance(summary: dict[str, object]) -> None:
    provenance = summary.get("provenance")
    if not isinstance(provenance, dict):
        raise TypeError("Goal5845 summary provenance must be a mapping")
    if provenance != {
        "preregistration": {
            "path": (
                "/workspace/goal5845-22c6a450-source/history/internal_docs/"
                "goal5845_relation_public_parity_20260904/PREREGISTRATION.json"
            ),
            "sha256": PREREGISTRATION_FILE_SHA256,
            "preregistration_sha256": PREREGISTRATION_SHA256,
        },
        "native_library": {
            "path": "/workspace/goal5845-22c6a450-run/native/librtdl_optix.so",
            "bytes": NATIVE_BYTES,
            "sha256": NATIVE_SHA256,
            "required_symbol": NATIVE_SYMBOL,
        },
        "native_build_manifest": {
            "path": "/workspace/goal5845-22c6a450-run/native/build_manifest.json",
            "sha256": BUILD_MANIFEST_FILE_SHA256,
        },
        "device_source": {
            "path": (
                "/workspace/goal5845-22c6a450-source/experiments/"
                "goal5796_matched/matched_device.cu"
            ),
            "sha256": DEVICE_SOURCE_SHA256,
        },
        "pyoptix_source": {
            "path": (
                "/workspace/goal5844-ee0237963bcd-20260905T020218Z-run/"
                "upstream/otk-pyoptix"
            ),
            "commit": PYOPTIX_COMMIT,
            "tree": PYOPTIX_TREE,
        },
        "pyoptix_build_receipt": {
            "path": (
                "/workspace/goal5844-ee0237963bcd-20260905T020218Z-run/"
                "pyoptix-build/build_receipt.json"
            ),
            "sha256": PYOPTIX_BUILD_RECEIPT_FILE_SHA256,
        },
    }:
        raise RuntimeError("Goal5845 summary provenance differs")
    blob = _git_blob("experiments/goal5796_matched/matched_device.cu")
    if hashlib.sha256(blob).hexdigest() != DEVICE_SOURCE_SHA256:
        raise RuntimeError("Goal5845 device source Git binding differs")


def _stored_files() -> list[dict[str, object]]:
    rows = []
    for path in sorted(EVIDENCE_ROOT.rglob("*")):
        if path.is_file():
            try:
                label = path.relative_to(ROOT).as_posix()
            except ValueError:
                label = path.as_posix()
            rows.append(
                {
                    "path": label,
                    "bytes": path.stat().st_size,
                    "sha256": _sha256_file(path),
                }
            )
    return rows


def build() -> dict[str, object]:
    preregistration = _validate_preregistration()
    build_manifest = _validate_build_manifest()
    _validate_preflight()
    transaction = _validate_transaction()
    summary_path = EVIDENCE_ROOT / "formal_comparison/SUMMARY.json"
    if _sha256_file(summary_path) != SUMMARY_FILE_SHA256:
        raise RuntimeError("Goal5845 summary file hash differs")
    summary = _load(summary_path)
    if summary.get("summary_sha256") != SUMMARY_SHA256:
        raise RuntimeError("Goal5845 summary frozen seal differs")
    result = _recount_summary(summary)
    _validate_summary_provenance(summary)

    authority: dict[str, object] = {
        "schema": "rtdl.goal5845.relation_public_parity.internal_authority.v1",
        "status": (
            "PASS__GOAL5845_RELATION_PUBLIC_STEADY_PERFORMANCE_DEBT_CLOSED__"
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
        "evidence_identity": {
            "preregistration_sha256": PREREGISTRATION_SHA256,
            "preregistration_file_sha256": PREREGISTRATION_FILE_SHA256,
            "summary_sha256": SUMMARY_SHA256,
            "summary_file_sha256": SUMMARY_FILE_SHA256,
            "native_provider_sha256": NATIVE_SHA256,
            "native_provider_bytes": NATIVE_BYTES,
            "native_build_manifest_sha256": BUILD_MANIFEST_FILE_SHA256,
            "native_build_result_sha256": build_manifest["result_sha256"],
            "pod_transaction_sha256": transaction["transaction_sha256"],
            "pyoptix_source_commit": PYOPTIX_COMMIT,
            "pyoptix_source_tree": PYOPTIX_TREE,
        },
        "architecture_boundary": {
            "native_abi_app_neutral": True,
            "application_dispatch_added": False,
            "ordinary_path_uses_device_semantic_compaction": True,
            "ordinary_path_materializes_role_counters": False,
            "ordinary_path_returns_canonical_rows_once": True,
            "full_diagnostics_remain_explicitly_available": True,
            "two_actual_optix_launches_per_execution": True,
        },
        "historical_boundary": {
            "goal5843_adverse_relation_result_preserved": True,
            "goal5843_samples_reused_or_pooled": False,
            "unregistered_preflight_or_diagnostics_pooled": False,
            "formal_transaction_is_new_and_preregistered": True,
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "exact_task_and_prepared_steady_path_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
            "consensus_claimed": False,
            "cross_hardware_generalization_authorized": False,
            "cold_start_parity_claim_authorized": False,
            "intrinsic_language_or_api_speedup_claim_authorized": False,
            "arbitrary_workload_claim_authorized": False,
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
    else:
        if _load(AUTHORITY_PATH) != value:
            raise RuntimeError("stored Goal5845 internal authority differs")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
