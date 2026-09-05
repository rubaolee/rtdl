#!/usr/bin/env python3
"""Independently recount the retained Goal5847 AOT startup evidence.

The verifier intentionally imports neither RTDL nor a GPU package.  It reads
the immutable pod capture directly from its tar archive and validates custody,
Git identities, AOT/native identities, installed trust signatures, traversal
receipts, worker transport, all timing samples, preregistered gates, and the
derived authority with the Python standard library only.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import statistics
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = ROOT / "history/internal_docs/goal5847_aot_startup_20260905"
EVIDENCE_PATH = GOAL_ROOT / "FORMAL_V2_EVIDENCE.tar.gz"
PREREGISTRATION_PATH = GOAL_ROOT / "PREREGISTRATION_V2.json"
AUTHORITY_PATH = GOAL_ROOT / "GOAL5847_INTERNAL_AUTHORITY.json"

SOURCE_COMMIT = "f5e337feef6829e063c6aff06f4e8bd6d5466b3b"
SOURCE_TREE = "c276d64342bf17fee77b7ab0cf66ef5060c73341"
PREREGISTRATION_COMMIT = "7eaad7e52656c7521e7763fba132a72186583d6d"
ARCHIVE_ROOT = "goal5847-f5e337fee-evidence-v2"
EVIDENCE_FILE_SHA256 = (
    "65ee646c36e801fbf957de6eeb0c8b03106a48fa01bb2008d3aed0761fd037e8"
)
CAPTURE_MANIFEST_FILE_SHA256 = (
    "9ef688b64a3b8913ae2cf428e766706f152bb88b102bf1d85947ed25a6c25923"
)
CAPTURE_MANIFEST_SHA256 = (
    "70cca6e698e76b1efe80da058c324d952ec39f91912ca8963e75563824404d52"
)
CAPTURE_FILES_SHA256 = (
    "74cc18b2835c67146885243bb810bd41b4be1778bf27d423d3bee665a5a501b7"
)
PREREGISTRATION_FILE_SHA256 = (
    "d72f38459bcfa283373a43258a000498c574cb37a428334485b86cf36ae93975"
)
PREREGISTRATION_SHA256 = (
    "34b977a163a21090d0820b1f6b2dafc6e9723ff9d7635d75bd0afa85bdd8d433"
)
NATIVE_BUILD_MANIFEST_SHA256 = (
    "a394fe81fc61eedcb63e72c78f63f8284ba8f47fead4653cb37ac2a571d5f8bb"
)
NATIVE_SHA256 = (
    "6f695bc006114087aa85303f1faeb3f8d1dd2ffb8fab2256206ce6b3e42ec6a4"
)
CANDIDATE_MANIFEST_FILE_SHA256 = (
    "b002957fe9405ee97ab76a05656ceeea594514e0c8adcc59a16fc83d0923233d"
)
CANDIDATE_MANIFEST_SHA256 = (
    "6198d9dd8534bf16d90636e390c3aef7015f7b7f71e752324be96f2324001508"
)
GPU_VALIDATION_FILE_SHA256 = (
    "0f6fa8fe2a0fca5d5dccaf6bae70fe20e9d13936c1370bebb52badb2d07e5db4"
)
CONTROLLER_FILE_SHA256 = (
    "3512eeee67dbb21d8926a6bee7514c377941c79a488372b618c6daca90653e7f"
)
CONTROLLER_SHA256 = (
    "9c06a160c5ec9fbc97dda15581627f6d1c03bcc80ccc3c8e13882ff24f9a855b"
)
PRECOMPILED_PTX_SHA256 = (
    "7f79eb31ff6eedaf25c24e0910bf2989b576b13a883a4a2e5c840f72b6203b2d"
)
PYOPTIX_RECEIPT_FILE_SHA256 = (
    "a05317ef879630fe9de3aced08fe2ce35ee9416e684799e1f571e64c4c9abfd4"
)
PYOPTIX_RECEIPT_SHA256 = (
    "06e8ea1d7ea3894972b5a4d6ca8b8860e526be0d6c5cf5a19c8b19aafd88a30e"
)
PYOPTIX_SOURCE_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_SOURCE_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
PYOPTIX_EXTENSION_SHA256 = (
    "7a7c555635062180e8f5d6246e41e8c7033e287218e963668eb34365f3e1b927"
)

RTDL_ARM = "RTDL_FAMILY_RTDLEXE_AOT"
PYOPTIX_ARM = "PYOPTIX_PRECOMPILED_PTX_VALIDATION_OFF"
ARMS = (RTDL_ARM, PYOPTIX_ARM)
TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
INPUT_SHA256 = "8606dd3c22d424a7ee2d64b61918f6185d39d8090d1a0a64001de65054d25e0e"
OUTPUT_SHA256 = "2fb668490480cbb5d4d9bbf5a8d357435eff5fc6bb3532427ac2726cdaa88c77"
TRIANGLE_OUTPUT_SHA256 = (
    "2df49102543561c678ce39e05cc6c79ce92c0ea919ad45134d53d19bb67174ef"
)
RELATION_ARTIFACT_SHA256 = (
    "7ee22c3baeb3f253e47b0fc58323c259b38ba11d1d79e031101e27eddb05ef47"
)
TRIANGLE_ARTIFACT_SHA256 = (
    "e945c9d65c1ff4ecf95e3a189af7170c287aa6b07d4919ab1435b6a7abe54e4f"
)
BLOCKS = 8
WARMUPS = 16
SAMPLES_PER_WORKER = 128
SAMPLES_PER_ARM = BLOCKS * SAMPLES_PER_WORKER
GOAL5845_REFERENCE_NS = 366_340

EXPECTED_HARDWARE = {
    "compute_capability": "8.9",
    "driver_version": "580.159.04",
    "gpu_name": "NVIDIA RTX 2000 Ada Generation",
    "gpu_uuid": "GPU-4b436f5f-bf8f-1d8c-0202-98e6e7b387e9",
    "memory_mib": 16_380,
}
CLAIM = {
    "external_review_complete": False,
    "internal_engineering_evidence_only": True,
    "public_or_manuscript_claim_authorized": False,
}
CONTROLLER_CLAIM = {
    **CLAIM,
    "arbitrary_workload_claim_authorized": False,
    "cross_hardware_generalization_authorized": False,
}

REQUIRED_SYMBOLS = (
    "rtdl_optix_v4_warm_runtime_v1",
    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
    "rtdl_optix_v4_rtdlexe_producer_descriptor_v1",
    "rtdl_optix_traversal_audit_begin",
    "rtdl_optix_traversal_audit_finish",
    "rtdl_optix_traversal_audit_abort",
    "rtdl_optix_v4_prepare_bounded_relation_callback_v1",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v4",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v5",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v6",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v7",
    "rtdl_optix_v4_prepared_bounded_relation_source_cache_build_count_v1",
    "rtdl_optix_v4_commit_prepared_bounded_relation_source_cache_v2",
    "rtdl_optix_v4_prepared_bounded_relation_source_cache_digest_v1",
    "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v2",
    "rtdl_optix_v4_prepare_triangle_reduction_callback_v1",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v4",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v5",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v6",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v7",
    "rtdl_optix_v4_commit_prepared_triangle_reduction_cache_v1",
    "rtdl_optix_v4_prepared_triangle_reduction_cache_digest_v1",
    "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v2",
)

SOURCE_FILE_SHA256 = {
    "scripts/build_v4_optix_native_snapshot.py": (
        "e86c06a76f7c74e6471f32d39778d6ae9a853bfba3b430f25029d5aa4a5ffe7e"
    ),
    "scripts/goal5847_build_aot_candidates.py": (
        "44d7d399174448b6574adde23c166a62334cac62a2c7a5b0f25231325b7229c5"
    ),
    "scripts/goal5847_run_aot_startup_comparison.py": (
        "4f8847a1984c0e8649e373b455a4028902d4479f1bf250da0af56da56825caec"
    ),
    "scripts/goal5847_validate_aot_gpu.py": (
        "2093595ed19768b8b533d51aad7e62fcab9596fc18512554719a8909acf6e486"
    ),
    "experiments/goal5847_aot_startup/worker.py": (
        "834bca5e31c005a9e5c3da34d2146f6787efa0b9de1a7c5ef0e45e608874a969"
    ),
    "src/rtdsl/v4_rtdlexe.py": (
        "2dd6b4981a0da66a01006e33d44c8a4c4f9777052c98a0b6f2f622b52026343e"
    ),
}

_AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V2\x00"
_TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
_TRUST_PACKAGE_DOMAIN = b"RTDL-V4-RTDLEXE-DEPLOYMENT-TRUST-PACKAGE-V1\x00"
_TRUST_HEAD_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-HEAD-V1\x00"
_SHA256_DIGEST_INFO_PREFIX = bytes.fromhex(
    "3031300d060960864801650304020105000420"
)


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


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def _load_json_bytes(raw: bytes, *, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Goal5847 {label} is not valid UTF-8 JSON") from error
    if not isinstance(value, dict):
        raise TypeError(f"Goal5847 {label} must be a JSON object")
    return value


def _verify_removed_seal(
    value: dict[str, object], field: str, expected: str | None = None, *, label: str
) -> str:
    body = dict(value)
    observed = body.pop(field, None)
    if type(observed) is not str or observed != _digest(body):
        raise RuntimeError(f"Goal5847 {label} seal differs")
    if expected is not None and observed != expected:
        raise RuntimeError(f"Goal5847 {label} frozen seal differs")
    return observed


def _require_exact_keys(
    value: object, keys: set[str], *, label: str
) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise RuntimeError(f"Goal5847 {label} field set differs")
    return value


def _git(*arguments: str) -> bytes:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True
    ).stdout


def _git_text(*arguments: str) -> str:
    return _git(*arguments).decode("utf-8").strip()


class EvidenceArchive:
    """Safely retain every regular archive member in memory."""

    def __init__(
        self,
        path: Path = EVIDENCE_PATH,
        *,
        expected_sha256: str = EVIDENCE_FILE_SHA256,
    ) -> None:
        if _sha256_file(path) != expected_sha256:
            raise RuntimeError("Goal5847 evidence archive hash differs")
        members: dict[str, bytes] = {}
        names: set[str] = set()
        directory_count = 0
        with tarfile.open(path, "r:gz") as archive:
            for member in archive.getmembers():
                if member.name in names:
                    raise RuntimeError("Goal5847 archive has a duplicate member")
                names.add(member.name)
                pure = PurePosixPath(member.name)
                if pure.is_absolute() or ".." in pure.parts:
                    raise RuntimeError("Goal5847 archive path escapes its root")
                if not pure.parts or pure.parts[0] != ARCHIVE_ROOT:
                    raise RuntimeError("Goal5847 archive root differs")
                if member.isdir():
                    directory_count += 1
                    continue
                if not member.isfile() or member.issym() or member.islnk():
                    raise RuntimeError("Goal5847 archive has a special member")
                stream = archive.extractfile(member)
                if stream is None:
                    raise RuntimeError("Goal5847 archive member is unreadable")
                raw = stream.read()
                if len(raw) != member.size:
                    raise RuntimeError("Goal5847 archive member size differs")
                short = PurePosixPath(*pure.parts[1:]).as_posix()
                if not short or short in members:
                    raise RuntimeError("Goal5847 archive member name differs")
                members[short] = raw
        if len(members) != 81 or directory_count != 7:
            raise RuntimeError("Goal5847 archive member count differs")
        self.path = path
        self.members = members

    def raw(self, name: str) -> bytes:
        try:
            return self.members[name]
        except KeyError as error:
            raise RuntimeError(f"Goal5847 archive member is absent: {name}") from error

    def json(self, name: str) -> dict[str, object]:
        return _load_json_bytes(self.raw(name), label=name)


def _validate_capture(archive: EvidenceArchive) -> dict[str, object]:
    raw = archive.raw("CAPTURE_MANIFEST.json")
    if _sha256_bytes(raw) != CAPTURE_MANIFEST_FILE_SHA256:
        raise RuntimeError("Goal5847 capture manifest file hash differs")
    value = _load_json_bytes(raw, label="capture manifest")
    _require_exact_keys(
        value,
        {
            "schema", "status", "captured_at_utc", "pod_endpoint",
            "source_commit", "source_tree", "file_count", "files",
            "files_sha256", "claim_boundary", "capture_manifest_sha256",
        },
        label="capture manifest",
    )
    _verify_removed_seal(
        value,
        "capture_manifest_sha256",
        CAPTURE_MANIFEST_SHA256,
        label="capture manifest",
    )
    rows = value.get("files")
    if (
        value.get("schema")
        != "rtdl.goal5847.aot_startup.capture_manifest.v1"
        or value.get("status") != "COMPLETE_POD_CAPTURE"
        or value.get("captured_at_utc") != "2026-09-05T14:46:13.488233Z"
        or value.get("pod_endpoint") != "root@213.173.108.40:37784"
        or value.get("source_commit") != SOURCE_COMMIT
        or value.get("source_tree") != SOURCE_TREE
        or value.get("file_count") != 80
        or value.get("claim_boundary") != CLAIM
        or not isinstance(rows, list)
        or len(rows) != 80
        or value.get("files_sha256") != _digest(rows)
        or value.get("files_sha256") != CAPTURE_FILES_SHA256
    ):
        raise RuntimeError("Goal5847 capture manifest contract differs")
    expected_names = set(archive.members) - {"CAPTURE_MANIFEST.json"}
    observed_names: set[str] = set()
    for row in rows:
        row = _require_exact_keys(
            row, {"path", "bytes", "sha256"}, label="capture file row"
        )
        name = row.get("path")
        if type(name) is not str or name in observed_names:
            raise RuntimeError("Goal5847 capture file path differs")
        observed_names.add(name)
        raw_member = archive.raw(name)
        if (
            row.get("bytes") != len(raw_member)
            or row.get("sha256") != _sha256_bytes(raw_member)
        ):
            raise RuntimeError(f"Goal5847 captured bytes differ: {name}")
    if observed_names != expected_names:
        raise RuntimeError("Goal5847 capture inventory membership differs")
    if rows != sorted(rows, key=lambda row: row["path"]):
        raise RuntimeError("Goal5847 capture inventory order differs")
    return value


def _expected_schedule() -> list[list[object]]:
    result: list[list[object]] = []
    for block in range(BLOCKS):
        first, second = (
            (RTDL_ARM, PYOPTIX_ARM)
            if block % 2 == 0
            else (PYOPTIX_ARM, RTDL_ARM)
        )
        result.extend(([block, 0, first], [block, 1, second]))
    return result


def _validate_preregistration(archive: EvidenceArchive) -> dict[str, object]:
    local = PREREGISTRATION_PATH.read_bytes()
    retained = archive.raw("PREREGISTRATION_V2.json")
    if (
        local != retained
        or _sha256_bytes(local) != PREREGISTRATION_FILE_SHA256
        or _git(
            "show",
            f"{PREREGISTRATION_COMMIT}:history/internal_docs/"
            "goal5847_aot_startup_20260905/PREREGISTRATION_V2.json",
        )
        != local
    ):
        raise RuntimeError("Goal5847 preregistration custody differs")
    value = _load_json_bytes(local, label="preregistration")
    _verify_removed_seal(
        value,
        "preregistration_sha256",
        PREREGISTRATION_SHA256,
        label="preregistration",
    )
    expected_design = {
        "balanced_alternating_order": True,
        "blocks": 8,
        "fresh_process_per_arm_per_block": True,
        "primary_estimand": "parent_pre_spawn_to_first_correct_result_ns",
        "sample_discard_count": 0,
        "samples_per_arm": 1024,
        "samples_per_worker": 128,
        "secondary_estimand": "implementation_import_end_to_first_correct_result_ns",
        "steady_estimand": "complete_same_contract_execution_ns",
        "warmups_per_worker": 16,
    }
    expected_gates = {
        "all_registered_samples_retained": True,
        "all_workers_and_exact_oracles_pass": True,
        "goal5845_rtdl_steady_reference_ns": GOAL5845_REFERENCE_NS,
        "pooled_rtdl_steady_regression_at_most": 1.25,
        "pooled_steady_rtdl_to_pyoptix_ratio_at_most": 0.2,
        "post_import_median_within_block_ratio_at_most": 3.0,
        "post_import_worst_block_ratio_at_most": 4.0,
        "primary_median_within_block_ratio_at_most": 0.5,
        "primary_worst_block_ratio_at_most": 0.75,
    }
    expected_bindings = {
        "candidate_manifest_seal": CANDIDATE_MANIFEST_SHA256,
        "candidate_manifest_sha256": CANDIDATE_MANIFEST_FILE_SHA256,
        "native_library_sha256": NATIVE_SHA256,
        "precompiled_ptx_sha256": PRECOMPILED_PTX_SHA256,
        "pyoptix_build_receipt_internal_seal": PYOPTIX_RECEIPT_SHA256,
        "pyoptix_build_receipt_sha256": PYOPTIX_RECEIPT_FILE_SHA256,
        "pyoptix_commit": PYOPTIX_SOURCE_COMMIT,
        "pyoptix_tree": PYOPTIX_SOURCE_TREE,
        "relation_artifact_sha256": RELATION_ARTIFACT_SHA256,
        "triangle_artifact_sha256": TRIANGLE_ARTIFACT_SHA256,
    }
    expected_claim = {
        **CONTROLLER_CLAIM,
        "production_signing_claim_authorized": False,
    }
    if (
        value.get("schema")
        != "rtdl.goal5847.aot_startup_preregistration.v1"
        or value.get("status") != "FROZEN_BEFORE_FORMAL_GPU_TRANSACTION"
        or value.get("implementation_source_commit") != SOURCE_COMMIT
        or value.get("implementation_source_tree") != SOURCE_TREE
        or value.get("arms") != list(ARMS)
        or value.get("task")
        != {
            "canonical_row_count": 4096,
            "id": TASK,
            "indexed_count": 4096,
            "input_sha256": INPUT_SHA256,
            "output_contract": "canonical_u32_relation_rows",
            "output_sha256": OUTPUT_SHA256,
            "query_count": 4096,
        }
        or value.get("design") != expected_design
        or value.get("pass_gates") != expected_gates
        or value.get("frozen_bindings") != expected_bindings
        or value.get("claim_boundary") != expected_claim
    ):
        raise RuntimeError("Goal5847 preregistration contract differs")
    comparison = value.get("comparison_boundary")
    required = value.get("required_rtdl_facts")
    prior = value.get("prior_exploration")
    if (
        not isinstance(comparison, dict)
        or comparison.get("both_arms_consume_precompiled_device_programs")
        is not True
        or comparison.get("primary_includes_interpreter_and_dependency_import")
        is not True
        or comparison.get("secondary_excludes_implementation_import") is not True
        or comparison.get("pyoptix_harness_calls_source_compiler") is not False
        or comparison.get("pyoptix_dependency_stack_may_map_nvrtc") is not True
        or comparison.get("storage_page_cache_state_not_controlled") is not True
        or comparison.get("block_device_cold_io_claimed") is not False
        or not isinstance(required, dict)
        or any(required.get(key) is not True for key in (
            "runtime_compiler_attempt_count_before_and_after_zero",
            "nvrtc_mapping_absent",
            "compiler_modules_absent",
            "full_generic_family_identity_match",
            "exact_output_required",
            "prepared_steady_regression_forbidden",
            "optional_batch_oracle_disabled_in_timed_path",
            "diagnostic_execution_occurs_after_steady_samples",
        ))
        or required.get("actual_optix_launch_count_per_execution") != 2
        or required.get("application_specific_native_logic_added") is not False
        or not isinstance(prior, dict)
        or prior.get("disclosed") is not True
        or prior.get("pooled_into_formal_transaction") is not False
        or prior.get("used_to_select_metrics_or_thresholds") is not True
    ):
        raise RuntimeError("Goal5847 preregistration boundary differs")
    return value


def _validate_source_bindings(build: dict[str, object]) -> None:
    if _git_text("rev-parse", f"{SOURCE_COMMIT}^{{tree}}") != SOURCE_TREE:
        raise RuntimeError("Goal5847 implementation Git tree differs")
    for path, expected in SOURCE_FILE_SHA256.items():
        if _sha256_bytes(_git("show", f"{SOURCE_COMMIT}:{path}")) != expected:
            raise RuntimeError(f"Goal5847 source binding differs: {path}")
    build_input = build.get("build_input")
    if not isinstance(build_input, dict):
        raise TypeError("Goal5847 native build input is absent")
    inventory = build_input.get("source_inventory")
    if not isinstance(inventory, list) or len(inventory) != 12:
        raise RuntimeError("Goal5847 native source inventory differs")
    seen: set[str] = set()
    for row in inventory:
        row = _require_exact_keys(
            row, {"path", "bytes", "sha256"}, label="native source row"
        )
        path = row.get("path")
        if type(path) is not str or path in seen:
            raise RuntimeError("Goal5847 native source path differs")
        seen.add(path)
        raw = _git("show", f"{SOURCE_COMMIT}:{path}")
        if len(raw) != row.get("bytes") or _sha256_bytes(raw) != row.get("sha256"):
            raise RuntimeError(f"Goal5847 native source bytes differ: {path}")
    builder = _git(
        "show", f"{SOURCE_COMMIT}:scripts/build_v4_optix_native_snapshot.py"
    )
    if _sha256_bytes(builder) != build_input.get("builder_sha256"):
        raise RuntimeError("Goal5847 native builder binding differs")


def _validate_native(archive: EvidenceArchive) -> dict[str, object]:
    raw = archive.raw("native/build_manifest.json")
    native = archive.raw("native/librtdl_optix_rtdlexe.so")
    log = archive.raw("native/build.log")
    if (
        _sha256_bytes(raw) != NATIVE_BUILD_MANIFEST_SHA256
        or _sha256_bytes(native) != NATIVE_SHA256
    ):
        raise RuntimeError("Goal5847 native custody differs")
    value = _load_json_bytes(raw, label="native build manifest")
    build_input = value.get("build_input")
    if not isinstance(build_input, dict):
        raise TypeError("Goal5847 native build input differs")
    if (
        value.get("schema") != "rtdl.v4.optix_native_snapshot_build.v3"
        or value.get("status") != "PASS__MINIMAL_RTDLEXE_AOT_NATIVE"
        or value.get("deployment_profile") != "rtdlexe_aot_runtime_v1"
        or value.get("git_commit") != SOURCE_COMMIT
        or value.get("git_commit_after_build") != SOURCE_COMMIT
        or value.get("git_status_before_build") != []
        or value.get("git_status_after_build") != []
        or value.get("dirty_build_authorized") is not False
        or value.get("build_id") != _digest(build_input)
        or value.get("native_bytes") != len(native)
        or value.get("native_sha256") != NATIVE_SHA256
        or value.get("log_sha256") != _sha256_bytes(log)
        or value.get("required_symbols") != list(REQUIRED_SYMBOLS)
        or value.get("all_required_symbols_exported") is not True
        or value.get("unexpected_exported_symbols") != []
        or value.get("all_exports_allowlisted") is not True
        or value.get("exported_symbol_match_mode")
        != "exact_nm_dynamic_defined_name"
        or value.get("runtime_compiler_linkage") != "lazy_dlopen_build_pinned"
        or value.get("eager_nvrtc_dependency") is not False
        or "nvrtc" in str(value.get("dynamic_dependencies", "")).lower()
        or value.get("optix_version") != 90000
        or build_input.get("schema") != "rtdl.v4.optix_native_build_input.v3"
        or build_input.get("git_commit") != SOURCE_COMMIT
        or build_input.get("deployment_profile") != "rtdlexe_aot_runtime_v1"
        or build_input.get("runtime_compiler_linkage")
        != "lazy_dlopen_build_pinned"
        or build_input.get("source_compiler_entry_points_exported") is not False
        or build_input.get("section_garbage_collection") is not True
        or build_input.get("compute_capability") != [8, 9]
        or build_input.get("expected_optix_sdk") != "9.0.0"
        or build_input.get("optix_version") != 90000
        or build_input.get("exported_symbol_allowlist") != list(REQUIRED_SYMBOLS)
    ):
        raise RuntimeError("Goal5847 native build contract differs")
    exports = {
        line.split()[-1]
        for line in archive.raw("environment/native-exports.txt")
        .decode("utf-8")
        .splitlines()
        if line.split()
    }
    dynamic = archive.raw("environment/native-readelf-dynamic.txt").decode(
        "utf-8", errors="strict"
    )
    ldd = archive.raw("environment/native-ldd.txt").decode(
        "utf-8", errors="strict"
    )
    if (
        exports != set(REQUIRED_SYMBOLS)
        or "Shared library: [libcuda.so.1]" not in dynamic
        or "libnvrtc" in dynamic.lower()
        or "libnvrtc" in ldd.lower()
    ):
        raise RuntimeError("Goal5847 native exported/dependency surface differs")
    _validate_source_bindings(value)
    return value


def _rsa_pkcs1_v15_sha256_verify(
    signature: bytes, message: bytes, *, modulus: int, exponent: int
) -> bool:
    width = (modulus.bit_length() + 7) // 8
    if len(signature) != width:
        return False
    encoded = pow(int.from_bytes(signature, "big"), exponent, modulus).to_bytes(
        width, "big"
    )
    digest_info = _SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(message).digest()
    padding_length = width - len(digest_info) - 3
    if padding_length < 8:
        return False
    expected = b"\x00\x01" + b"\xff" * padding_length + b"\x00" + digest_info
    return encoded == expected


def _verify_canonical_json(raw: bytes, value: dict[str, object], *, label: str) -> None:
    if raw != _canonical_bytes(value) + b"\n":
        raise RuntimeError(f"Goal5847 {label} is not canonical JSON")


def _verify_embedded_seal(
    value: object, field: str, *, label: str
) -> dict[str, object]:
    if not isinstance(value, dict):
        raise TypeError(f"Goal5847 {label} must be an object")
    _verify_removed_seal(value, field, label=label)
    return value


def _validate_artifact(
    archive: EvidenceArchive,
    *,
    label: str,
    row: dict[str, object],
) -> dict[str, object]:
    artifact_sha = str(row["artifact_sha256"])
    artifact_name = f"candidates/artifacts/{artifact_sha}.rtdlexe"
    artifact_raw = archive.raw(artifact_name)
    authority_raw = archive.raw(f"candidates/{label}.authority.json")
    artifact = _load_json_bytes(artifact_raw, label=f"{label} artifact")
    authority = _load_json_bytes(authority_raw, label=f"{label} authority")
    _verify_canonical_json(artifact_raw, artifact, label=f"{label} artifact")
    _verify_canonical_json(authority_raw, authority, label=f"{label} authority")
    authority_body = dict(authority)
    authority_seal = authority_body.pop("authority_seal", None)
    if (
        _sha256_bytes(artifact_raw) != artifact_sha
        or _sha256_bytes(authority_raw) != row.get("authority_sha256")
        or authority_seal
        != _sha256_bytes(_AUTHORITY_DOMAIN + _canonical_bytes(authority_body))
        or authority.get("schema") != "rtdl.v4.rtdlexe.detached_authority.v2"
        or authority.get("authority_version") != 2
        or authority.get("artifact_sha256") != artifact_sha
        or authority.get("artifact_bytes") != len(artifact_raw)
        or authority.get("native_library_sha256") != NATIVE_SHA256
        or authority.get("target_compute_capability") != [8, 9]
        or authority.get("deployment_id") != row.get("deployment_id")
        or authority.get("executable_identity_sha256")
        != row.get("executable_identity_sha256")
        or authority.get("family_executable_identity_sha256")
        != row.get("family_executable_identity_sha256")
        or artifact.get("schema") != "rtdl.v4.rtdlexe.v2"
        or artifact.get("format_version") != 2
    ):
        raise RuntimeError(f"Goal5847 {label} artifact authority differs")
    declaration = _verify_embedded_seal(
        artifact.get("protocol_declaration"),
        "contract_sha256",
        label=f"{label} declaration",
    )
    projection = _verify_embedded_seal(
        artifact.get("compiler_projection"),
        "projection_sha256",
        label=f"{label} compiler projection",
    )
    decision = _verify_embedded_seal(
        artifact.get("protocol_decision"),
        "decision_sha256",
        label=f"{label} protocol decision",
    )
    product = artifact.get("product_projection")
    if not isinstance(product, dict):
        raise TypeError(f"Goal5847 {label} product projection differs")
    binding = _verify_embedded_seal(
        product.get("generic_family_binding"),
        "binding_sha256",
        label=f"{label} generic family binding",
    )
    family_identity = _verify_embedded_seal(
        binding.get("family_executable_identity"),
        "identity_sha256",
        label=f"{label} family executable identity",
    )
    provider_key = _verify_embedded_seal(
        product.get("provider_key"),
        "provider_key_sha256",
        label=f"{label} provider key",
    )
    execution_schema = _verify_embedded_seal(
        product.get("execution_schema"),
        "execution_schema_sha256",
        label=f"{label} execution schema",
    )
    identity = product.get("executable_identity")
    target = product.get("target_toolchain")
    if not isinstance(identity, dict) or not isinstance(target, dict):
        raise TypeError(f"Goal5847 {label} product identity differs")
    try:
        ptx = base64.b64decode(artifact.get("composed_ptx_base64"), validate=True)
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Goal5847 {label} composed PTX differs") from error
    ptx_sha = _sha256_bytes(ptx)
    if (
        _digest(product) != authority.get("product_projection_sha256")
        or _digest(identity) != authority.get("executable_identity_sha256")
        or decision.get("decision_sha256")
        != authority.get("protocol_decision_sha256")
        or binding.get("binding_sha256")
        != authority.get("generic_family_binding_sha256")
        or family_identity.get("identity_sha256")
        != authority.get("family_executable_identity_sha256")
        or decision.get("verdict") != "ACCEPT"
        or decision.get("findings") != []
        or decision.get("executable_capability_issued") is not False
        or decision.get("contract_sha256") != declaration.get("contract_sha256")
        or decision.get("projection_sha256") != projection.get("projection_sha256")
        or declaration.get("family") != projection.get("family")
        or declaration.get("family") != product.get("family")
        or declaration.get("task_semantics_sha256")
        != projection.get("task_semantics_sha256")
        or declaration.get("task_semantics_sha256")
        != authority.get("task_semantics_sha256")
        or product.get("deployment_id") != authority.get("deployment_id")
        or product.get("protocol_contract_sha256")
        != declaration.get("contract_sha256")
        or product.get("compiler_projection_sha256")
        != projection.get("projection_sha256")
        or product.get("protocol_decision_sha256") != decision.get("decision_sha256")
        or target.get("native_library_sha256") != NATIVE_SHA256
        or target.get("target_sha256") != authority.get("target_sha256")
        or target.get("compute_capability") != [8, 9]
        or target.get("provider") != "optix"
        or target.get("optix_sdk") != "9.0.0"
        or provider_key.get("native_provider_sha256") != NATIVE_SHA256
        or provider_key.get("target_compute_capability") != [8, 9]
        or product.get("composed_ptx_sha256") != ptx_sha
        or projection.get("generated_device_source_sha256") != ptx_sha
        or identity.get("composed_ptx_sha256") != ptx_sha
        or family_identity.get("provider_artifact_sha256") != NATIVE_SHA256
        or family_identity.get("generated_artifact_sha256") != ptx_sha
        or family_identity.get("identity_sha256")
        != row.get("family_executable_identity_sha256")
        or execution_schema.get("native_program_bundle")
        not in {
            "v4_custom_aabb_bounded_relation_composed",
            "v4_builtin_triangle_checked_reduction_composed",
        }
    ):
        raise RuntimeError(f"Goal5847 {label} artifact chain differs")
    return authority


def _validate_trust_family(
    archive: EvidenceArchive,
    *,
    label: str,
    row: dict[str, object],
    authority: dict[str, object],
) -> dict[str, object]:
    documents: dict[str, tuple[bytes, dict[str, object]]] = {}
    for suffix in ("public", "package", "head"):
        raw = archive.raw(f"candidates/{label}.{suffix}.json")
        value = _load_json_bytes(raw, label=f"{label} {suffix}")
        _verify_canonical_json(raw, value, label=f"{label} {suffix}")
        if _sha256_bytes(raw) != row.get(f"{suffix}_sha256"):
            raise RuntimeError(f"Goal5847 {label} {suffix} hash differs")
        documents[suffix] = (raw, value)
    _root_raw, root = documents["public"]
    package_raw, package = documents["package"]
    _head_raw, head = documents["head"]
    root_body = dict(root)
    root_seal = root_body.pop("trust_root_sha256", None)
    try:
        modulus_bytes = base64.b64decode(
            root.get("rsa_modulus_base64"), validate=True
        )
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Goal5847 {label} trust modulus differs") from error
    modulus = int.from_bytes(modulus_bytes, "big")
    exponent = root.get("rsa_exponent")
    if (
        root.get("schema") != "rtdl.v4.rtdlexe.installed_trust_root.v1"
        or root.get("key_id") != f"TEST_ONLY_goal5847_{label}"
        or type(exponent) is not int
        or exponent != 65537
        or len(modulus_bytes) < 256
        or modulus.bit_length() < 2040
        or modulus % 2 == 0
        or root_seal
        != _sha256_bytes(_TRUST_ROOT_DOMAIN + _canonical_bytes(root_body))
    ):
        raise RuntimeError(f"Goal5847 {label} trust root differs")
    package_body = dict(package)
    package_signature_b64 = package_body.pop("signature_base64", None)
    head_body = dict(head)
    head_signature_b64 = head_body.pop("signature_base64", None)
    try:
        package_signature = base64.b64decode(
            package_signature_b64, validate=True
        )
        head_signature = base64.b64decode(head_signature_b64, validate=True)
    except (TypeError, ValueError) as error:
        raise RuntimeError(f"Goal5847 {label} trust signature differs") from error
    if (
        package.get("schema")
        != "rtdl.v4.rtdlexe.deployment_trust_package.v1"
        or package.get("key_id") != root.get("key_id")
        or package.get("sequence") != 1
        or package.get("previous_package_sha256") is not None
        or package.get("signature_algorithm") != "rsa-pkcs1-v1_5-sha256"
        or not _rsa_pkcs1_v15_sha256_verify(
            package_signature,
            _TRUST_PACKAGE_DOMAIN + _canonical_bytes(package_body),
            modulus=modulus,
            exponent=exponent,
        )
        or head.get("schema") != "rtdl.v4.rtdlexe.installed_trust_head.v1"
        or head.get("key_id") != root.get("key_id")
        or head.get("current_sequence") != 1
        or head.get("current_package_sha256") != _sha256_bytes(package_raw)
        or head.get("signature_algorithm") != "rsa-pkcs1-v1_5-sha256"
        or not _rsa_pkcs1_v15_sha256_verify(
            head_signature,
            _TRUST_HEAD_DOMAIN + _canonical_bytes(head_body),
            modulus=modulus,
            exponent=exponent,
        )
    ):
        raise RuntimeError(f"Goal5847 {label} trust signatures differ")
    expected_entry = {
        "artifact_sha256": authority["artifact_sha256"],
        "authority_sha256": row["authority_sha256"],
        "compute_capability": authority["target_compute_capability"],
        "deployment_id": authority["deployment_id"],
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "family": authority["family"],
        "native_library_sha256": authority["native_library_sha256"],
        "target_sha256": authority["target_sha256"],
        "task_semantics_sha256": authority["task_semantics_sha256"],
    }
    if package.get("authorities") != [expected_entry]:
        raise RuntimeError(f"Goal5847 {label} installed trust entry differs")
    return {
        "key_id": root["key_id"],
        "trust_root_sha256": root_seal,
        "package_sha256": _sha256_bytes(package_raw),
        "head_sha256": row["head_sha256"],
        "rsa_signature_chain_verified": True,
        "test_only_signing": True,
    }


def _validate_candidates(
    archive: EvidenceArchive, native_build: dict[str, object]
) -> tuple[dict[str, object], dict[str, object]]:
    raw = archive.raw("candidates/manifest.json")
    if _sha256_bytes(raw) != CANDIDATE_MANIFEST_FILE_SHA256:
        raise RuntimeError("Goal5847 candidate manifest file hash differs")
    value = _load_json_bytes(raw, label="candidate manifest")
    _verify_removed_seal(
        value,
        "manifest_sha256",
        CANDIDATE_MANIFEST_SHA256,
        label="candidate manifest",
    )
    rows = value.get("rows")
    if (
        value.get("schema") != "rtdl.goal5847.aot_candidates.v1"
        or value.get("status") != "PASS__DEPLOY_ONLY_FAMILY_CANDIDATES_BUILT"
        or value.get("source_commit") != SOURCE_COMMIT
        or value.get("source_tree") != SOURCE_TREE
        or value.get("native_sha256") != NATIVE_SHA256
        or value.get("native_bytes")
        != len(archive.raw("native/librtdl_optix_rtdlexe.so"))
        or value.get("native_build_manifest_sha256")
        != NATIVE_BUILD_MANIFEST_SHA256
        or value.get("native_build_id") != native_build.get("build_id")
        or value.get("optix_sdk") != "9.0.0"
        or value.get("compute_capability") != [8, 9]
        or value.get("build_roots")
        != {
            "cuda_toolkit_version": "12.8",
            "link_options": ["max_trace_depth=1", "debug=none"],
            "llvmlite_version": "0.47.0",
        }
        or value.get("claim_boundary")
        != {
            "gpu_execution_performed": False,
            "production_key_custody_attested": False,
            "public_or_manuscript_claim_authorized": False,
            "test_only_signing": True,
        }
        or not isinstance(rows, dict)
        or set(rows) != {"relation", "triangle"}
    ):
        raise RuntimeError("Goal5847 candidate manifest contract differs")
    expected_rows = {
        "relation": (
            TASK,
            RELATION_ARTIFACT_SHA256,
            "goal5847-relation-slot",
            "custom_aabb_bounded_relation_v1",
        ),
        "triangle": (
            "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
            TRIANGLE_ARTIFACT_SHA256,
            "goal5847-triangle-slot",
            "builtin_triangle_reduction_v1",
        ),
    }
    trust: dict[str, object] = {}
    for label, (task, artifact_sha, deployment, family) in expected_rows.items():
        row = rows[label]
        if (
            not isinstance(row, dict)
            or set(row)
            != {
                "task", "deployment_id", "artifact", "artifact_sha256",
                "authority", "authority_sha256", "public", "public_sha256",
                "package", "package_sha256", "head", "head_sha256",
                "executable_identity_sha256",
                "family_executable_identity_sha256",
                "materialize_build_and_sign_ns",
                "test_only_signing_key_destroyed_after_freeze",
            }
            or row.get("task") != task
            or row.get("artifact_sha256") != artifact_sha
            or row.get("deployment_id") != deployment
            or not str(row.get("artifact", "")).endswith(
                f"/artifacts/{artifact_sha}.rtdlexe"
            )
            or not str(row.get("authority", "")).endswith(
                f"/{label}.authority.json"
            )
            or not str(row.get("public", "")).endswith(f"/{label}.public.json")
            or not str(row.get("package", "")).endswith(
                f"/{label}.package.json"
            )
            or not str(row.get("head", "")).endswith(f"/{label}.head.json")
            or row.get("test_only_signing_key_destroyed_after_freeze") is not True
            or type(row.get("materialize_build_and_sign_ns")) is not int
            or row["materialize_build_and_sign_ns"] <= 0
        ):
            raise RuntimeError(f"Goal5847 {label} candidate row differs")
        authority = _validate_artifact(archive, label=label, row=row)
        if authority.get("family") != family:
            raise RuntimeError(f"Goal5847 {label} family differs")
        trust[label] = _validate_trust_family(
            archive, label=label, row=row, authority=authority
        )
    if (
        type(value.get("total_build_ns")) is not int
        or value["total_build_ns"]
        < sum(int(rows[label]["materialize_build_and_sign_ns"]) for label in rows)
    ):
        raise RuntimeError("Goal5847 candidate build timing differs")
    return value, trust


def _program_bundle_id(name: str) -> int:
    value = 1469598103934665603
    for byte in name.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _mix(state: int, value: int) -> int:
    mask = (1 << 64) - 1
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    value = (value ^ (value >> 31)) & mask
    return (
        state
        ^ (value + 0x9E3779B97F4A7C15 + ((state << 6) & mask) + (state >> 2))
    ) & mask


def _validate_traversal_receipt(
    receipt: object,
    *,
    route: str,
    output_sha256: str,
    bundle: str,
    launches: int,
    raygen: int,
) -> None:
    top = {
        "schema", "provider_library", "provider_library_path",
        "provider_library_sha256", "route_identity", "semantic_digest",
        "output_digest", "nonce", "physical_executor_classification",
        "expected_program_bundles", "expected_program_bundle_ids",
        "expected_program_observed_at_receipt_edge", "native_snapshot",
        "claim_rules", "receipt_sha256",
    }
    if not isinstance(receipt, dict) or set(receipt) != top:
        raise RuntimeError("Goal5847 traversal receipt field set differs")
    _verify_removed_seal(receipt, "receipt_sha256", label="traversal receipt")
    bundle_id = _program_bundle_id(bundle)
    nonce = receipt.get("nonce")
    snapshot = receipt.get("native_snapshot")
    rules = {
        "nonzero_traversable_binding_required": True,
        "output_digest_bound": True,
        "program_bundle_binding_required": True,
        "provider_name_alone_proves_traversal": False,
        "selected_template_alone_proves_traversal": False,
        "successful_optix_launch_required": True,
    }
    u64_fields = {
        "attempted_launch_count", "callsite_mix", "complete_context_launch_count",
        "context_bind_count", "failed_launch_count", "first_program_bundle_id",
        "first_traversable",
        "incomplete_context_launch_count", "last_program_bundle_id",
        "last_traversable", "nonce_hi", "nonce_lo", "params_mix",
        "pipeline_mix", "program_bundle_mix", "raygen_invocation_count",
        "sbt_mix", "stream_mix",
        "successful_launch_count", "traversable_mix",
    }
    u32_fields = {
        "pending_context_at_finish", "session_error",
        "incomplete_callsite_record_count",
    }
    if (
        receipt.get("schema") != "rtdl.physical_execution.traversal_receipt.v1"
        or receipt.get("provider_library") != "librtdl_optix"
        or type(receipt.get("provider_library_path")) is not str
        or not receipt.get("provider_library_path")
        or receipt.get("provider_library_sha256") != NATIVE_SHA256
        or receipt.get("route_identity") != route
        or type(receipt.get("semantic_digest")) is not str
        or len(str(receipt.get("semantic_digest"))) != 64
        or receipt.get("output_digest") != output_sha256
        or receipt.get("physical_executor_classification")
        != "optix_traversal_observed"
        or receipt.get("expected_program_bundles") != [bundle]
        or receipt.get("expected_program_bundle_ids") != [bundle_id]
        or receipt.get("expected_program_observed_at_receipt_edge") is not True
        or receipt.get("claim_rules") != rules
        or not isinstance(nonce, dict)
        or set(nonce) != {"hi", "lo"}
        or any(type(nonce.get(key)) is not int or not 0 <= nonce[key] < 1 << 64
               for key in ("hi", "lo"))
        or (nonce["hi"], nonce["lo"]) == (0, 0)
        or not isinstance(snapshot, dict)
        or set(snapshot)
        != u64_fields | u32_fields | {"incomplete_callsite_lines"}
    ):
        raise RuntimeError("Goal5847 traversal receipt envelope differs")
    lines = snapshot["incomplete_callsite_lines"]
    if (
        any(
            type(snapshot[key]) is not int or not 0 <= snapshot[key] < 1 << 64
            for key in u64_fields
        )
        or any(
            type(snapshot[key]) is not int or not 0 <= snapshot[key] < 1 << 32
            for key in u32_fields
        )
        or not isinstance(lines, list)
        or len(lines) != 32
        or any(type(item) is not int or not 0 <= item < 1 << 32 for item in lines)
        or snapshot["nonce_hi"] != nonce["hi"]
        or snapshot["nonce_lo"] != nonce["lo"]
        or snapshot["attempted_launch_count"] != launches
        or snapshot["successful_launch_count"] != launches
        or snapshot["failed_launch_count"] != 0
        or snapshot["complete_context_launch_count"] != launches
        or snapshot["incomplete_context_launch_count"] != 0
        or snapshot["context_bind_count"] != launches
        or snapshot["raygen_invocation_count"] != raygen
        or snapshot["pending_context_at_finish"] != 0
        or snapshot["session_error"] != 0
        or snapshot["incomplete_callsite_record_count"] != 0
        or any(lines)
        or snapshot["first_program_bundle_id"] != bundle_id
        or snapshot["last_program_bundle_id"] != bundle_id
        or snapshot["first_traversable"] == 0
        or snapshot["last_traversable"] == 0
    ):
        raise RuntimeError("Goal5847 traversal receipt native counters differ")
    expected_bundle_mix = 0
    for _ in range(launches):
        expected_bundle_mix = _mix(expected_bundle_mix, bundle_id)
    expected_traversable_mix = _mix(0, snapshot["first_traversable"])
    if launches == 2:
        expected_traversable_mix = _mix(
            expected_traversable_mix, snapshot["last_traversable"]
        )
    if (
        (
            launches == 1
            and snapshot["first_traversable"] != snapshot["last_traversable"]
        )
        or snapshot["program_bundle_mix"] != expected_bundle_mix
        or snapshot["traversable_mix"] != expected_traversable_mix
    ):
        raise RuntimeError("Goal5847 traversal receipt native mixes differ")


def _validate_pyoptix(archive: EvidenceArchive) -> dict[str, object]:
    raw = archive.raw("baseline/pyoptix-build-receipt.json")
    extension = archive.raw("baseline/pyoptix-extension.so")
    ptx = archive.raw("baseline/pyoptix-relation-precompiled.ptx")
    if (
        _sha256_bytes(raw) != PYOPTIX_RECEIPT_FILE_SHA256
        or _sha256_bytes(extension) != PYOPTIX_EXTENSION_SHA256
        or _sha256_bytes(ptx) != PRECOMPILED_PTX_SHA256
    ):
        raise RuntimeError("Goal5847 PyOptix baseline custody differs")
    value = _load_json_bytes(raw, label="PyOptix build receipt")
    _verify_removed_seal(
        value,
        "receipt_sha256",
        PYOPTIX_RECEIPT_SHA256,
        label="PyOptix build receipt",
    )
    source = value.get("pyoptix_source")
    installed = value.get("installed")
    wheel = value.get("wheel")
    if (
        value.get("schema") != "rtdl.goal5844.pyoptix_clean_build_install.v1"
        or value.get("status")
        != "PASS__CLEAN_SOURCE_WHEEL_AND_LOADED_EXTENSION_BOUND"
        or value.get("transaction_kind")
        != "build_install_provenance_not_performance"
        or value.get("registered_performance_timing_count") != 0
        or value.get("claim_boundary")
        != {
            "clean_source_build_bound": True,
            "loaded_extension_bound_to_wheel_member": True,
            "performance_measurement_in_receipt": False,
            "public_or_manuscript_claim_authorized": False,
        }
        or not isinstance(source, dict)
        or source.get("commit") != PYOPTIX_SOURCE_COMMIT
        or source.get("tree") != PYOPTIX_SOURCE_TREE
        or source.get("clean") is not True
        or not isinstance(installed, dict)
        or installed.get("distribution_name") != "pyoptix"
        or installed.get("distribution_version") != "9.1.0"
        or installed.get("optix_api_version") != "9.0.0"
        or not isinstance(installed.get("loaded_extension"), dict)
        or installed["loaded_extension"].get("sha256")
        != PYOPTIX_EXTENSION_SHA256
        or installed["loaded_extension"].get("bytes") != len(extension)
        or not isinstance(wheel, dict)
        or wheel.get("extension_sha256") != PYOPTIX_EXTENSION_SHA256
        or wheel.get("extension_bytes") != len(extension)
    ):
        raise RuntimeError("Goal5847 PyOptix baseline receipt differs")
    return value


def _validate_initialization_phases(value: object, *, label: str) -> None:
    phases = _require_exact_keys(
        value,
        {"cuda_primary_context", "native_runtime_warm", "sealed_native_image", "total"},
        label=label,
    )
    if any(type(item) is not int or item <= 0 for item in phases.values()):
        raise RuntimeError(f"Goal5847 {label} values differ")
    subtotal = sum(phases[key] for key in phases if key != "total")
    if not subtotal <= phases["total"] <= subtotal + 1_000_000:
        raise RuntimeError(f"Goal5847 {label} total differs")


def _validate_gpu_validation(
    archive: EvidenceArchive, candidate: dict[str, object]
) -> dict[str, object]:
    raw = archive.raw("gpu_validation.json")
    if _sha256_bytes(raw) != GPU_VALIDATION_FILE_SHA256:
        raise RuntimeError("Goal5847 GPU validation file hash differs")
    value = _load_json_bytes(raw, label="GPU validation")
    _verify_removed_seal(value, "result_sha256", label="GPU validation")
    relation = value.get("relation")
    triangle = value.get("triangle")
    if (
        value.get("schema") != "rtdl.goal5847.aot_gpu_validation.v1"
        or value.get("status") != "PASS__AOT_RELATION_TRIANGLE_AND_MUTATIONS"
        or value.get("source_commit") != SOURCE_COMMIT
        or value.get("source_tree") != SOURCE_TREE
        or value.get("candidate_manifest_sha256")
        != CANDIDATE_MANIFEST_FILE_SHA256
        or value.get("runtime_compiler_modules") != []
        or value.get("nvrtc_mappings") != []
        or value.get("claim_boundary") != CLAIM
        or value.get("mutation_rejections")
        != {
            "artifact_byte_append": "RX023_ARTIFACT_INVALID",
            "authority_byte_append": "RX018_AUTHORITY_INVALID",
            "cross_family_bind": "RX050_DEPLOYMENT_INTENT_MISMATCH",
            "native_byte_append": "RX032_NATIVE_IDENTITY_MISMATCH",
            "unknown_deployment_slot": "RX049_DEPLOYMENT_SLOT_NOT_FROZEN",
        }
        or type(value.get("elapsed_ns")) is not int
        or value["elapsed_ns"] <= 0
        or not isinstance(relation, dict)
        or not isinstance(triangle, dict)
        or relation.get("compiler_attempt_count") != 0
        or relation.get("output_sha256") != OUTPUT_SHA256
        or relation.get("row_count") != 4096
        or relation.get("family_executable_identity_sha256")
        != candidate["rows"]["relation"]["family_executable_identity_sha256"]
        or triangle.get("compiler_attempt_count") != 0
        or triangle.get("output_sha256") != TRIANGLE_OUTPUT_SHA256
        or triangle.get("checked_u64_output") != 65530
        or triangle.get("family_executable_identity_sha256")
        != candidate["rows"]["triangle"]["family_executable_identity_sha256"]
    ):
        raise RuntimeError("Goal5847 GPU validation contract differs")
    _validate_initialization_phases(
        relation.get("initialization_phases_ns"), label="relation initialization"
    )
    _validate_initialization_phases(
        triangle.get("initialization_phases_ns"), label="triangle initialization"
    )
    _validate_traversal_receipt(
        relation.get("traversal_receipt"),
        route="v4_callback_ir:custom_aabb_bounded_relation_v1",
        output_sha256=OUTPUT_SHA256,
        bundle="v4_custom_aabb_bounded_relation_composed",
        launches=2,
        raygen=8192,
    )
    _validate_traversal_receipt(
        triangle.get("traversal_receipt"),
        route="v4_builtin_triangle_callback_ir:checked_reduction_v1",
        output_sha256=TRIANGLE_OUTPUT_SHA256,
        bundle="v4_builtin_triangle_checked_reduction_composed",
        launches=1,
        raygen=16384,
    )
    return value


def _timing(value: object, expected_count: int, *, label: str) -> list[int]:
    value = _require_exact_keys(
        value,
        {"sample_count", "samples_ns", "minimum_ns", "median_ns", "maximum_ns"},
        label=label,
    )
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
        raise RuntimeError(f"Goal5847 {label} timing differs")
    return [int(item) for item in samples]


def _validate_worker(
    value: dict[str, object],
    *,
    arm: str,
    block: int,
    candidate: dict[str, object],
    pyoptix: dict[str, object],
) -> list[int]:
    _require_exact_keys(
        value,
        {
            "schema", "status", "source_commit", "source_tree", "arm",
            "block", "python", "hardware", "task", "query_count",
            "row_count", "warmups", "repetitions", "measurements",
            "claim_boundary", "result_sha256",
        },
        label=f"worker {block} {arm}",
    )
    _verify_removed_seal(value, "result_sha256", label=f"worker {block} {arm}")
    if (
        value.get("schema") != "rtdl.goal5847.aot_startup.worker.v1"
        or value.get("status") != "PASS__INTERNAL_ENGINEERING_WORKER"
        or value.get("source_commit") != SOURCE_COMMIT
        or value.get("source_tree") != SOURCE_TREE
        or value.get("arm") != arm
        or value.get("block") != block
        or value.get("task") != TASK
        or value.get("query_count") != 4096
        or value.get("row_count") != 4096
        or value.get("warmups") != WARMUPS
        or value.get("repetitions") != SAMPLES_PER_WORKER
        or value.get("python") != "3.12.3"
        or value.get("hardware") != EXPECTED_HARDWARE
        or value.get("claim_boundary") != CLAIM
    ):
        raise RuntimeError(f"Goal5847 worker contract differs: {block} {arm}")
    measurements = value.get("measurements")
    if not isinstance(measurements, dict):
        raise TypeError("Goal5847 worker measurements are absent")
    _require_exact_keys(
        measurements,
        {
            "process_spawn_to_correct_result_ns",
            "post_import_to_correct_result_ns", "phases_ns",
            "steady_complete_execution", "identity", "evidence",
        },
        label=f"worker {block} {arm} measurements",
    )
    process_ns = measurements.get("process_spawn_to_correct_result_ns")
    post_ns = measurements.get("post_import_to_correct_result_ns")
    phases = measurements.get("phases_ns")
    identity = measurements.get("identity")
    evidence = measurements.get("evidence")
    if (
        type(process_ns) is not int
        or type(post_ns) is not int
        or process_ns <= post_ns
        or post_ns <= 0
        or not isinstance(phases, dict)
        or not isinstance(identity, dict)
        or not isinstance(evidence, dict)
        or any(type(item) is not int or item <= 0 for item in phases.values())
        or post_ns < sum(
            item for name, item in phases.items() if name != "implementation_import"
        )
        or evidence.get("output_sha256") != OUTPUT_SHA256
        or evidence.get("row_count") != 4096
    ):
        raise RuntimeError(f"Goal5847 worker measurements differ: {block} {arm}")
    samples = _timing(
        measurements.get("steady_complete_execution"),
        SAMPLES_PER_WORKER,
        label=f"worker {block} {arm} steady",
    )
    if arm == RTDL_ARM:
        relation = candidate["rows"]["relation"]
        if (
            set(identity)
            != {
                "artifact_sha256", "authority_sha256",
                "family_executable_identity_sha256", "native_library_sha256",
            }
            or set(evidence)
            != {
                "diagnostic_traversal_receipt",
                "full_generic_family_identity_matched", "nvrtc_mappings",
                "output_sha256", "provider_initialization_phases_ns",
                "row_count", "runtime_compiler_attempt_count_after",
                "runtime_compiler_attempt_count_before",
                "runtime_compiler_modules",
            }
            or
            set(phases)
            != {
                "implementation_import", "deterministic_input_materialization",
                "signed_deployment_install", "provider_initialization_start",
                "artifact_authority_load", "provider_bind_and_initialization_join",
                "deploy_static_input", "deploy_dynamic_input", "native_prepare",
                "first_complete_execution",
            }
            or evidence.get("runtime_compiler_attempt_count_before") != 0
            or evidence.get("runtime_compiler_attempt_count_after") != 0
            or evidence.get("runtime_compiler_modules") != []
            or evidence.get("nvrtc_mappings") != []
            or evidence.get("full_generic_family_identity_matched") is not True
            or identity.get("artifact_sha256") != relation["artifact_sha256"]
            or identity.get("authority_sha256") != relation["authority_sha256"]
            or identity.get("native_library_sha256") != NATIVE_SHA256
            or identity.get("family_executable_identity_sha256")
            != relation["family_executable_identity_sha256"]
        ):
            raise RuntimeError("Goal5847 RTDL worker evidence differs")
        _validate_initialization_phases(
            evidence.get("provider_initialization_phases_ns"),
            label="worker provider initialization",
        )
        _validate_traversal_receipt(
            evidence.get("diagnostic_traversal_receipt"),
            route="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_sha256=OUTPUT_SHA256,
            bundle="v4_custom_aabb_bounded_relation_composed",
            launches=2,
            raygen=8192,
        )
    else:
        source = identity.get("pyoptix_repository")
        nvrtc = evidence.get("nvrtc_mappings")
        installed = pyoptix["installed"]
        if (
            set(identity)
            != {
                "loaded_extension", "optix_api_version",
                "precompiled_ptx_sha256", "pyoptix_build_receipt_file_sha256",
                "pyoptix_build_receipt_internal_seal", "pyoptix_distribution",
                "pyoptix_distribution_version", "pyoptix_repository",
            }
            or set(evidence)
            != {
                "device_overflow", "device_status", "nvrtc_mappings",
                "output_sha256",
                "precompiled_ptx_means_harness_did_not_compile_source",
                "raw_event_count", "row_count",
                "stack_wide_no_runtime_compiler_claimed",
            }
            or
            set(phases)
            != {
                "implementation_import", "deterministic_input_materialization",
                "precompiled_ptx_load", "cuda_optix_context",
                "module_program_pipeline_sbt", "native_prepare",
                "first_complete_execution",
            }
            or not isinstance(source, dict)
            or set(source) != {"clean", "commit", "status", "tree"}
            or source.get("commit") != PYOPTIX_SOURCE_COMMIT
            or source.get("tree") != PYOPTIX_SOURCE_TREE
            or source.get("clean") is not True
            or identity.get("precompiled_ptx_sha256") != PRECOMPILED_PTX_SHA256
            or identity.get("pyoptix_build_receipt_file_sha256")
            != PYOPTIX_RECEIPT_FILE_SHA256
            or identity.get("pyoptix_build_receipt_internal_seal")
            != PYOPTIX_RECEIPT_SHA256
            or identity.get("pyoptix_distribution") != "pyoptix"
            or identity.get("pyoptix_distribution_version") != "9.1.0"
            or identity.get("optix_api_version") != "9.0.0"
            or not isinstance(identity.get("loaded_extension"), dict)
            or set(identity["loaded_extension"]) != {"bytes", "path", "sha256"}
            or identity["loaded_extension"].get("sha256")
            != installed["loaded_extension"]["sha256"]
            or evidence.get("device_status") != 0
            or evidence.get("device_overflow") != 0
            or evidence.get("raw_event_count") != 8192
            or evidence.get("precompiled_ptx_means_harness_did_not_compile_source")
            is not True
            or evidence.get("stack_wide_no_runtime_compiler_claimed") is not False
            or not isinstance(nvrtc, list)
            or not nvrtc
            or not all("nvrtc" in str(item).lower() for item in nvrtc)
        ):
            raise RuntimeError("Goal5847 PyOptix worker evidence differs")
    return samples


def _median_int(values: list[int]) -> int:
    return int(statistics.median(values))


def _validate_formal(
    archive: EvidenceArchive,
    *,
    candidate: dict[str, object],
    pyoptix: dict[str, object],
    preregistration: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    raw = archive.raw("formal/controller.json")
    if _sha256_bytes(raw) != CONTROLLER_FILE_SHA256:
        raise RuntimeError("Goal5847 controller file hash differs")
    controller = _load_json_bytes(raw, label="controller")
    _verify_removed_seal(
        controller,
        "result_sha256",
        CONTROLLER_SHA256,
        label="controller",
    )
    schedule = _expected_schedule()
    worker_rows = controller.get("workers")
    if (
        controller.get("schema") != "rtdl.goal5847.aot_startup.controller.v1"
        or controller.get("status")
        != "PASS__GOAL5847_PREREGISTERED_AOT_PERFORMANCE_GATES"
        or controller.get("source_commit") != SOURCE_COMMIT
        or controller.get("source_tree") != SOURCE_TREE
        or controller.get("candidate_manifest_sha256")
        != CANDIDATE_MANIFEST_FILE_SHA256
        or controller.get("precompiled_ptx_sha256") != PRECOMPILED_PTX_SHA256
        or controller.get("hardware") != EXPECTED_HARDWARE
        or controller.get("claim_boundary") != CONTROLLER_CLAIM
        or controller.get("preregistration")
        != {
            "path": "/workspace/goal5847-f5e337fee-PREREGISTRATION_V2.json",
            "preregistration_sha256": PREREGISTRATION_SHA256,
            "sha256": PREREGISTRATION_FILE_SHA256,
        }
        or controller.get("design")
        != {
            "blocks": BLOCKS,
            "discarded_samples": 0,
            "samples_per_arm": SAMPLES_PER_ARM,
            "samples_per_worker": SAMPLES_PER_WORKER,
            "schedule": schedule,
            "warmups_per_worker": WARMUPS,
        }
        or not isinstance(worker_rows, list)
        or len(worker_rows) != 16
    ):
        raise RuntimeError("Goal5847 controller contract differs")
    workers: dict[tuple[int, str], dict[str, object]] = {}
    steady: dict[str, list[int]] = {arm: [] for arm in ARMS}
    process_times: dict[str, list[int]] = {arm: [] for arm in ARMS}
    post_import_times: dict[str, list[int]] = {arm: [] for arm in ARMS}
    phase_times: dict[str, dict[str, list[int]]] = {arm: {} for arm in ARMS}
    for expected, row in zip(schedule, worker_rows, strict=True):
        block, position, arm = expected
        name = f"block-{block:02d}-position-{position}-{arm}.json"
        row = _require_exact_keys(
            row,
            {"block", "position", "arm", "path", "sha256", "result_sha256"},
            label="controller worker row",
        )
        worker_raw = archive.raw(f"formal/{name}")
        worker = _load_json_bytes(worker_raw, label=name)
        stdout = archive.raw(f"formal/{name.removesuffix('.json')}.stdout")
        stderr = archive.raw(f"formal/{name.removesuffix('.json')}.stderr")
        if (
            row.get("block") != block
            or row.get("position") != position
            or row.get("arm") != arm
            or row.get("path") != name
            or row.get("sha256") != _sha256_bytes(worker_raw)
            or row.get("result_sha256") != worker.get("result_sha256")
            or stderr != b""
            or _load_json_bytes(stdout, label=f"{name} stdout") != worker
        ):
            raise RuntimeError(f"Goal5847 worker transport differs: {name}")
        samples = _validate_worker(
            worker,
            arm=str(arm),
            block=int(block),
            candidate=candidate,
            pyoptix=pyoptix,
        )
        workers[(int(block), str(arm))] = worker
        steady[str(arm)].extend(samples)
        measurements = worker["measurements"]
        process_times[str(arm)].append(
            measurements["process_spawn_to_correct_result_ns"]
        )
        post_import_times[str(arm)].append(
            measurements["post_import_to_correct_result_ns"]
        )
        for phase, elapsed in measurements["phases_ns"].items():
            phase_times[str(arm)].setdefault(phase, []).append(elapsed)
    primary: list[float] = []
    post_import: list[float] = []
    block_rows: list[dict[str, object]] = []
    for block in range(BLOCKS):
        rtdl = workers[(block, RTDL_ARM)]["measurements"]
        baseline = workers[(block, PYOPTIX_ARM)]["measurements"]
        rtdl_primary = rtdl["process_spawn_to_correct_result_ns"]
        baseline_primary = baseline["process_spawn_to_correct_result_ns"]
        rtdl_post = rtdl["post_import_to_correct_result_ns"]
        baseline_post = baseline["post_import_to_correct_result_ns"]
        primary_ratio = rtdl_primary / baseline_primary
        post_ratio = rtdl_post / baseline_post
        primary.append(primary_ratio)
        post_import.append(post_ratio)
        block_rows.append({
            "block": block,
            "first_arm": schedule[2 * block][2],
            "rtdl_process_spawn_to_correct_result_ns": rtdl_primary,
            "pyoptix_process_spawn_to_correct_result_ns": baseline_primary,
            "primary_rtdl_to_pyoptix_ratio": primary_ratio,
            "rtdl_post_import_to_correct_result_ns": rtdl_post,
            "pyoptix_post_import_to_correct_result_ns": baseline_post,
            "post_import_rtdl_to_pyoptix_ratio": post_ratio,
        })
    medians = {arm: _median_int(steady[arm]) for arm in ARMS}
    summary = {
        "median_within_block_primary_ratio": statistics.median(primary),
        "worst_block_primary_ratio": max(primary),
        "median_within_block_post_import_ratio": statistics.median(post_import),
        "worst_block_post_import_ratio": max(post_import),
        "pooled_steady_median_ns": medians,
        "pooled_steady_rtdl_to_pyoptix_ratio": (
            medians[RTDL_ARM] / medians[PYOPTIX_ARM]
        ),
        "rtdl_steady_vs_goal5845_reference_ratio": (
            medians[RTDL_ARM] / GOAL5845_REFERENCE_NS
        ),
    }
    gates = {
        "worker_count_exact": len(workers) == 16,
        "all_registered_samples_retained": all(
            len(steady[arm]) == SAMPLES_PER_ARM for arm in ARMS
        ),
        "primary_median_ratio_pass": summary[
            "median_within_block_primary_ratio"
        ] <= preregistration["pass_gates"][
            "primary_median_within_block_ratio_at_most"
        ],
        "primary_worst_ratio_pass": summary["worst_block_primary_ratio"]
        <= preregistration["pass_gates"]["primary_worst_block_ratio_at_most"],
        "post_import_median_ratio_pass": summary[
            "median_within_block_post_import_ratio"
        ] <= preregistration["pass_gates"][
            "post_import_median_within_block_ratio_at_most"
        ],
        "post_import_worst_ratio_pass": summary[
            "worst_block_post_import_ratio"
        ] <= preregistration["pass_gates"][
            "post_import_worst_block_ratio_at_most"
        ],
        "steady_ratio_pass": summary["pooled_steady_rtdl_to_pyoptix_ratio"]
        <= preregistration["pass_gates"][
            "pooled_steady_rtdl_to_pyoptix_ratio_at_most"
        ],
        "rtdl_steady_regression_pass": summary[
            "rtdl_steady_vs_goal5845_reference_ratio"
        ] <= preregistration["pass_gates"][
            "pooled_rtdl_steady_regression_at_most"
        ],
    }
    if (
        controller.get("block_comparisons") != block_rows
        or controller.get("summary") != summary
        or controller.get("gates") != gates
        or not all(gates.values())
    ):
        raise RuntimeError("Goal5847 formal recount differs")
    return controller, {
        "block_comparisons": block_rows,
        "summary": summary,
        "gates": gates,
        "retained_samples_per_arm": {arm: len(steady[arm]) for arm in ARMS},
        "median_process_ns": {
            arm: _median_int(process_times[arm]) for arm in ARMS
        },
        "median_post_import_ns": {
            arm: _median_int(post_import_times[arm]) for arm in ARMS
        },
        "median_phase_ns": {
            arm: {
                phase: _median_int(values)
                for phase, values in sorted(phase_times[arm].items())
            }
            for arm in ARMS
        },
    }


def build() -> dict[str, object]:
    archive = EvidenceArchive()
    capture = _validate_capture(archive)
    preregistration = _validate_preregistration(archive)
    native = _validate_native(archive)
    candidate, trust = _validate_candidates(archive, native)
    pyoptix = _validate_pyoptix(archive)
    gpu_validation = _validate_gpu_validation(archive, candidate)
    controller, recount = _validate_formal(
        archive,
        candidate=candidate,
        pyoptix=pyoptix,
        preregistration=preregistration,
    )
    summary = recount["summary"]
    value: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_startup.internal_authority.v1",
        "status": (
            "PASS__GOAL5847_INTERNAL_TECHNICAL_COMPLETE__"
            "EXTERNAL_REVIEW_PENDING"
        ),
        "source": {
            "implementation_commit": SOURCE_COMMIT,
            "implementation_tree": SOURCE_TREE,
            "preregistration_commit": PREREGISTRATION_COMMIT,
            "source_file_bindings": SOURCE_FILE_SHA256,
        },
        "custody": {
            "evidence_archive": str(EVIDENCE_PATH.relative_to(ROOT)),
            "evidence_archive_sha256": EVIDENCE_FILE_SHA256,
            "capture_manifest_file_sha256": CAPTURE_MANIFEST_FILE_SHA256,
            "capture_manifest_sha256": capture["capture_manifest_sha256"],
            "capture_files_sha256": capture["files_sha256"],
            "capture_file_count": capture["file_count"],
            "pod_endpoint": capture["pod_endpoint"],
            "controller_file_sha256": CONTROLLER_FILE_SHA256,
            "controller_sha256": controller["result_sha256"],
        },
        "frozen_experiment": {
            "preregistration_file_sha256": PREREGISTRATION_FILE_SHA256,
            "preregistration_sha256": preregistration["preregistration_sha256"],
            "task": preregistration["task"],
            "arms": list(ARMS),
            "design": preregistration["design"],
            "all_preregistered_gates_pass": all(recount["gates"].values()),
            "discarded_samples": 0,
        },
        "aot_runtime": {
            "native_sha256": NATIVE_SHA256,
            "native_bytes": native["native_bytes"],
            "native_build_manifest_sha256": NATIVE_BUILD_MANIFEST_SHA256,
            "native_build_id": native["build_id"],
            "deployment_profile": native["deployment_profile"],
            "runtime_compiler_linkage": native["runtime_compiler_linkage"],
            "eager_nvrtc_dependency": native["eager_nvrtc_dependency"],
            "required_export_count": len(REQUIRED_SYMBOLS),
            "unexpected_export_count": len(native["unexpected_exported_symbols"]),
            "relation_artifact_sha256": RELATION_ARTIFACT_SHA256,
            "triangle_artifact_sha256": TRIANGLE_ARTIFACT_SHA256,
            "installed_trust": trust,
            "test_only_signing": True,
            "production_key_custody_attested": False,
        },
        "correctness_and_security": {
            "relation_canonical_row_count": 4096,
            "relation_output_sha256": OUTPUT_SHA256,
            "triangle_checked_u64_output": 65530,
            "triangle_output_sha256": TRIANGLE_OUTPUT_SHA256,
            "true_optix_receipts_recounted": 10,
            "relation_launches_per_execution": 2,
            "triangle_validation_launches": 1,
            "runtime_compiler_attempt_count": 0,
            "rtdl_runtime_compiler_modules": [],
            "rtdl_nvrtc_mappings": [],
            "mutation_rejections": gpu_validation["mutation_rejections"],
            "rsa_trust_chains_verified": 2,
        },
        "performance": {
            **summary,
            "complete_process_primary_reciprocal": (
                1.0 / summary["median_within_block_primary_ratio"]
            ),
            "pooled_steady_reciprocal": (
                1.0 / summary["pooled_steady_rtdl_to_pyoptix_ratio"]
            ),
            "retained_samples_per_arm": recount["retained_samples_per_arm"],
            "median_process_ns": recount["median_process_ns"],
            "median_post_import_ns": recount["median_post_import_ns"],
            "median_phase_ns": recount["median_phase_ns"],
            "worker_count": 16,
            "block_count": 8,
        },
        "scientific_boundary": {
            "exact_task_precompiled_aot_only": True,
            "primary_includes_interpreter_and_dependency_import": True,
            "secondary_excludes_implementation_import": True,
            "pyoptix_harness_source_compilation_performed": False,
            "pyoptix_dependency_stack_mapped_nvrtc": True,
            "storage_page_cache_controlled": False,
            "first_ever_aot_build_in_performance_endpoint": False,
            "single_gpu_generation_only": True,
            "arbitrary_workload_claim_authorized": False,
            "intrinsic_language_speedup_claim_authorized": False,
            "external_review_complete": False,
            "public_or_manuscript_claim_authorized": False,
        },
        "claim_boundary": {
            "internal_engineering_evidence_only": True,
            "external_review_complete": False,
            "external_consensus_complete": False,
            "public_or_manuscript_claim_authorized": False,
            "cross_hardware_generalization_authorized": False,
            "production_signing_claim_authorized": False,
        },
    }
    value["authority_sha256"] = _digest(value)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.verify_stored:
        stored = _load_json_bytes(
            AUTHORITY_PATH.read_bytes(), label="stored internal authority"
        )
        if stored != value:
            raise RuntimeError("Goal5847 stored authority differs from recount")
    else:
        if AUTHORITY_PATH.exists() or AUTHORITY_PATH.is_symlink():
            raise FileExistsError(AUTHORITY_PATH)
        AUTHORITY_PATH.write_bytes(_json_bytes(value))
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
