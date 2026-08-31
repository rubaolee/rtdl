#!/usr/bin/env python3
"""Standalone verifier for Goal5801 A3 clean-install evidence v3."""

from __future__ import annotations

import argparse
import ast
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import struct
import tomllib
from typing import Mapping, NoReturn
import zipfile


RUN_SCHEMA = "rtdl.goal5801.a3.clean_install_run.v3"
RESULT_SCHEMA = "rtdl.goal5801.a3.clean_install_public_api_result.v5"
AUTHORITY_SCHEMA = "rtdl.v4.rtdlexe.detached_authority.v1"
ARTIFACT_SCHEMA = "rtdl.v4.rtdlexe.v1"
TRUST_ROOT_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_root.v1"
TRUST_PACKAGE_SCHEMA = "rtdl.v4.rtdlexe.deployment_trust_package.v1"
TRUST_HEAD_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_head.v1"
AUTHORITY_DOMAIN = b"RTDL-V4-RTDLEXE-DETACHED-AUTHORITY-V1\x00"
TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
TRUST_PACKAGE_DOMAIN = b"RTDL-V4-RTDLEXE-DEPLOYMENT-TRUST-PACKAGE-V1\x00"
TRUST_HEAD_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-HEAD-V1\x00"
DIGEST_INFO = bytes.fromhex("3031300d060960864801650304020105000420")
SHA256 = re.compile(r"[0-9a-f]{64}")
RETIRED_PREDECESSOR_ROOT_SHA256 = (
    "68aaf930e9545aa51a6c2d4ec7e102ccfeee7fb77ab0545ace1adcf0140ff419"
)
RETIRED_UNMATERIALIZED_SEQUENCE_ROOT_SHA256 = (
    "a9b1997694bf1892986518c943070571eb5cfd6b32c01f63becad9a1146bd927"
)
RETIRED_TEST_TRUST_ROOT_DISCLOSURE = {
    RETIRED_PREDECESSOR_ROOT_SHA256: {
        "maximum_preserved_sequence": 4,
        "unmaterialized_sequence_range": None,
    },
    RETIRED_UNMATERIALIZED_SEQUENCE_ROOT_SHA256: {
        "maximum_preserved_sequence": 4,
        "unmaterialized_sequence_range": [5, 16],
    },
    "e379bd6405187b94258533b12a12b459803ac298dd030e18cd1d73c308caf60c": {
        "maximum_preserved_sequence": 2,
        "unmaterialized_sequence_range": None,
    },
    "e1c419ea12fa997b1956254cf04e03b9a7182fe8f35a63ad4639f21fc4152967": {
        "maximum_preserved_sequence": 2,
        "unmaterialized_sequence_range": None,
    },
    "6dc886fbaa003f14f41f273d6a70f3ff168e935cdc1fcd1fbac0a8988f17e91c": {
        "maximum_preserved_sequence": 2,
        "unmaterialized_sequence_range": None,
    },
}
CONTROLLING_TRUST_ROOT_FILE_SHA256 = (
    "3364f744a637e27710319001c2fa505bd6c54f75904b51429de253bcd4da8dc4"
)
CONTROLLING_TRUST_SEQUENCE = 2
QUALIFICATION_ONLY_KEY_PREFIX = (
    "TEST_ONLY_goal5802_final_home_qualification_"
)
# The first owner-provided modern-RTX target will consume exactly two slots:
# sequence-1 relation genesis plus sequence-2 triangle append under this
# unused test-only root.  No deployment from any retired test root is copied
# forward.  The private key stays outside the repository and is not an input
# to a clean install or formal worker.
RETAINED_PREDECESSOR_DEPLOYMENTS: dict[str, str] = {}


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _require(condition: object, message: str) -> None:
    if not condition:
        _fail(message)


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _verify_controlling_trust_root_sha256(observed: object) -> None:
    _require(
        isinstance(observed, str)
        and observed == CONTROLLING_TRUST_ROOT_FILE_SHA256
        and observed not in RETIRED_TEST_TRUST_ROOT_DISCLOSURE,
        "controlling trust-root file identity",
    )


def _verify_trust_root_file_identity(
        trust_root_path: Path, *,
        qualification_only_expected_sha256: str | None = None,
) -> tuple[str, str]:
    """Verify either the pinned formal root or an explicit S0-only root.

    The default remains the exact formal-measurement pin.  A caller may name a
    different root only through the conspicuous qualification-only argument;
    that root must carry the fresh Home-qualification key-id prefix and is
    reported as ineligible for formal measurement.  This keeps a successful
    S0 rehearsal from silently weakening the production verifier.
    """

    observed = _sha(trust_root_path)
    if qualification_only_expected_sha256 is None:
        _verify_controlling_trust_root_sha256(observed)
        return "CONTROLLING_FORMAL_MEASUREMENT_ROOT", observed
    expected = qualification_only_expected_sha256
    _require(
        isinstance(expected, str)
        and SHA256.fullmatch(expected) is not None,
        "qualification-only expected trust-root SHA-256",
    )
    _require(
        expected != CONTROLLING_TRUST_ROOT_FILE_SHA256
        and expected not in RETIRED_TEST_TRUST_ROOT_DISCLOSURE,
        "qualification-only root must differ from formal and retired roots",
    )
    _require(observed == expected, "qualification-only trust-root file identity")
    root, _ = _read_json(trust_root_path, canonical_lf=True)
    key_id = root.get("key_id") if isinstance(root, dict) else None
    _require(
        isinstance(key_id, str)
        and key_id.startswith(QUALIFICATION_ONLY_KEY_PREFIX),
        "qualification-only trust-root key-id boundary",
    )
    return "QUALIFICATION_ONLY__NOT_FORMAL_MEASUREMENT_ROOT", observed


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _mapping(value: object, label: str) -> Mapping[str, object]:
    _require(isinstance(value, dict), f"{label}: mapping required")
    return value  # type: ignore[return-value]


def _command_has_saved_path(
    tokens: list[object], *, packet_root: Path, saved_path: Path,
) -> bool:
    """Match a saved input after packet relocation without trusting basename."""

    try:
        relative = saved_path.relative_to(packet_root).as_posix()
    except ValueError as error:
        raise RuntimeError("saved command input is outside packet") from error
    suffix = "/" + relative
    for token in tokens:
        normalized = str(token).replace("\\", "/")
        if normalized == relative or normalized.endswith(suffix):
            return True
    return False


def _normalized_token(value: object) -> str:
    return str(value).replace("\\", "/")


def _verify_actual_prepared_native_dsos(
    result: Mapping[str, object], *, native_sha256: str, native_bytes: int,
    expected_loaded_path: str,
) -> None:
    """Verify counters and identity for each DSO that actually executed."""

    boundary = _mapping(
        result.get("prepared_native_dso_evidence_boundary"),
        "prepared_native_dso_evidence_boundary")
    expected_boundary = {
        "application_lifecycle_calls_use_public_api_only": True,
        "cross_owner_dso_cache_or_reuse_claimed": True,
        "evidence_method": (
            "EVIDENCE_ONLY_PRIVATE_PREPARED_OWNER_LIBRARY_INTROSPECTION"),
        "product_api_expanded_for_evidence": False,
        "relation_and_triangle_share_one_dso_handle": True,
        "relation_and_triangle_share_one_memfd_descriptor": True,
        "relation_and_triangle_share_one_loader_alias": True,
        "relation_and_triangle_same_native_sha256": True,
        "relation_and_triangle_use_distinct_native_leases": True,
        "same_sha_process_cache_is_bounded_to_one_loader_image": True,
    }
    _require(set(boundary) == set(expected_boundary)
             and all(type(boundary[key]) is type(expected)
                     and boundary[key] == expected
                     for key, expected in expected_boundary.items()),
             "prepared native DSO evidence boundary")
    expected_keys = {
        "compiler_attempt_count_after", "compiler_attempt_count_before",
        "ctypes_handle",
        "lease_abandon_finalizer_alive_after_execute_before_close",
        "lease_abandon_finalizer_alive_before_execute",
        "loaded_library_path", "loaded_library_sha256", "native_image_bytes",
        "native_image_fd", "native_image_seals_after",
        "native_image_seals_before", "native_loader_alias",
        "native_cache_entry_identity", "native_cache_lease_id",
        "native_cache_active_lease_count_before_execute",
        "native_cache_active_lease_count_after_execute",
        "native_cache_acquisition_count_before_execute",
        "native_cache_acquisition_count_after_execute",
        "native_loader_alias_parent_removed_before_execute",
        "native_loader_alias_removed_before_execute",
        "required_native_image_seals", "same_owner_library_object_after_execute",
        "sealed_image_sha256_after", "sealed_image_sha256_before",
    }
    rows: dict[str, Mapping[str, object]] = {}
    for family in ("relation", "triangle"):
        family_result = _mapping(result.get(family), family)
        row = _mapping(
            family_result.get("actual_loaded_native_dso"),
            f"{family}.actual_loaded_native_dso")
        _require(set(row) == expected_keys,
                 f"{family} actual loaded native DSO fields")
        alias = row.get("native_loader_alias")
        alias_posix = PurePosixPath(_normalized_token(alias)) \
            if isinstance(alias, str) else None
        _require(
            type(row.get("compiler_attempt_count_before")) is int
            and row.get("compiler_attempt_count_before") == 0
            and type(row.get("compiler_attempt_count_after")) is int
            and row.get("compiler_attempt_count_after") == 0
            and type(row.get("ctypes_handle")) is int
            and int(row["ctypes_handle"]) > 0
            and type(row.get("native_image_fd")) is int
            and int(row["native_image_fd"]) >= 0
            and isinstance(row.get("native_cache_entry_identity"), str)
            and str(row["native_cache_entry_identity"]).endswith(native_sha256)
            and type(row.get("native_cache_lease_id")) is int
            and int(row["native_cache_lease_id"]) > 0
            and type(row.get("native_cache_active_lease_count_before_execute")) is int
            and int(row["native_cache_active_lease_count_before_execute"]) > 0
            and type(row.get("native_cache_active_lease_count_after_execute")) is int
            and int(row["native_cache_active_lease_count_after_execute"]) > 0
            and type(row.get("native_cache_acquisition_count_before_execute")) is int
            and int(row["native_cache_acquisition_count_before_execute"]) > 0
            and type(row.get("native_cache_acquisition_count_after_execute")) is int
            and int(row["native_cache_acquisition_count_after_execute"])
                >= int(row["native_cache_acquisition_count_before_execute"])
            and row.get("loaded_library_sha256") == native_sha256
            and row.get("sealed_image_sha256_before") == native_sha256
            and row.get("sealed_image_sha256_after") == native_sha256
            and type(row.get("native_image_bytes")) is int
            and row.get("native_image_bytes") == native_bytes
            and type(row.get("native_image_seals_before")) is int
            and row.get("native_image_seals_before") == 15
            and type(row.get("native_image_seals_after")) is int
            and row.get("native_image_seals_after") == 15
            and type(row.get("required_native_image_seals")) is int
            and row.get("required_native_image_seals") == 15
            and row.get("native_loader_alias_removed_before_execute") is True
            and row.get("native_loader_alias_parent_removed_before_execute") is True
            and row.get("same_owner_library_object_after_execute") is True
            and row.get("lease_abandon_finalizer_alive_before_execute") is True
            and row.get(
                "lease_abandon_finalizer_alive_after_execute_before_close") is True
            and _normalized_token(row.get("loaded_library_path"))
            == _normalized_token(expected_loaded_path)
            and alias_posix is not None and alias_posix.is_absolute()
            and alias_posix.name == f"image-{native_sha256}.so"
            and alias_posix.parent.name.startswith("rtdl-native-"),
            f"{family} actual executing DSO identity/counter")
        rows[family] = row
    _require(
        rows["relation"]["ctypes_handle"] == rows["triangle"]["ctypes_handle"]
        and rows["relation"]["native_image_fd"]
        == rows["triangle"]["native_image_fd"]
        and rows["relation"]["native_loader_alias"]
        == rows["triangle"]["native_loader_alias"]
        and rows["relation"]["native_cache_entry_identity"]
        == rows["triangle"]["native_cache_entry_identity"]
        and rows["relation"]["native_cache_lease_id"]
        != rows["triangle"]["native_cache_lease_id"],
        "relation/triangle same-SHA owners do not share one image via distinct leases")


def _verify_native_mapping_lifetime_kat(
    result: Mapping[str, object], *, native_sha256: str, native_bytes: int,
    expected_loaded_path: str,
) -> None:
    kat = _mapping(
        result.get("native_mapping_lifetime_kat"),
        "native_mapping_lifetime_kat")
    expected_kat_keys = {
        "fork_child_prepare_code", "map_identity_marker",
        "maximum_live_map_count", "prepared_owner_count_per_round",
        "round_count", "rounds", "schema", "warm_process_cache_map_count",
    }
    marker = f"/memfd:rtdl-native-{native_sha256[:16]} (deleted)"
    rounds = kat.get("rounds")
    _require(
        set(kat) == expected_kat_keys
        and kat.get("schema") == "rtdl.goal5801.native_mapping_lifetime_kat.v2"
        and kat.get("fork_child_prepare_code")
            == "RX047_NATIVE_CACHE_FORK_POISONED"
        and type(kat.get("warm_process_cache_map_count")) is int
        and 0 < int(kat["warm_process_cache_map_count"]) <= 32
        and kat.get("map_identity_marker") == marker
        and type(kat.get("maximum_live_map_count")) is int
        and kat.get("maximum_live_map_count") == 32
        and type(kat.get("prepared_owner_count_per_round")) is int
        and kat.get("prepared_owner_count_per_round") == 2
        and type(kat.get("round_count")) is int
        and kat.get("round_count") == 3
        and isinstance(rounds, list) and len(rounds) == 3,
        "native mapping lifetime KAT envelope",
    )
    expected_round_keys = {
        "after_close_map_count", "after_idempotent_close_map_count",
        "before_prepare_map_count", "live_map_count",
        "relation_closed_state", "relation_live_dso", "relation_output",
        "round_index", "triangle_closed_state", "triangle_live_dso",
        "triangle_output",
    }
    expected_closed = {
        "cache_image_fd_open_after_close": True,
        "cache_loader_handle_live_after_close": True,
        "lease_abandon_finalizer_alive_after_close": False,
        "lease_image_fd_value_after_close": -1,
        "lease_library_handle_after_close": 0,
        "lease_release_phase_after_close": "COMPLETE",
        "lease_released_after_close": True,
        "owner_library_released_after_close": True,
        "owner_release_complete_after_close": True,
        "prepared_closed_after_close": True,
    }
    live_counts: list[int] = []
    boundary = result.get("prepared_native_dso_evidence_boundary")
    for index, raw_round in enumerate(rounds):
        row = _mapping(raw_round, f"native mapping lifetime KAT round {index}")
        relation_closed = _mapping(
            row.get("relation_closed_state"),
            f"native mapping lifetime KAT round {index} relation close")
        triangle_closed = _mapping(
            row.get("triangle_closed_state"),
            f"native mapping lifetime KAT round {index} triangle close")
        live_count = row.get("live_map_count")
        _require(
            set(row) == expected_round_keys
            and type(row.get("round_index")) is int
            and row.get("round_index") == index
            and type(row.get("before_prepare_map_count")) is int
            and row.get("before_prepare_map_count")
                == kat.get("warm_process_cache_map_count")
            and type(live_count) is int
            and live_count == kat.get("warm_process_cache_map_count")
            and type(row.get("after_close_map_count")) is int
            and row.get("after_close_map_count")
                == kat.get("warm_process_cache_map_count")
            and type(row.get("after_idempotent_close_map_count")) is int
            and row.get("after_idempotent_close_map_count")
                == kat.get("warm_process_cache_map_count")
            and set(relation_closed) == set(expected_closed) | {
                "cache_active_lease_count_after_close"}
            and set(triangle_closed) == set(expected_closed) | {
                "cache_active_lease_count_after_close"}
            and relation_closed.get(
                "cache_active_lease_count_after_close") == 1
            and triangle_closed.get(
                "cache_active_lease_count_after_close") == 0
            and all(type(relation_closed[key]) is type(expected)
                    and relation_closed[key] == expected
                    for key, expected in expected_closed.items())
            and all(type(triangle_closed[key]) is type(expected)
                    and triangle_closed[key] == expected
                    for key, expected in expected_closed.items())
            and row.get("relation_output") == [[10, 100]]
            and row.get("triangle_output") == 7,
            f"native mapping lifetime KAT round {index}",
        )
        live_counts.append(live_count)
        _verify_actual_prepared_native_dsos({
            "prepared_native_dso_evidence_boundary": boundary,
            "relation": {"actual_loaded_native_dso": row.get("relation_live_dso")},
            "triangle": {"actual_loaded_native_dso": row.get("triangle_live_dso")},
        }, native_sha256=native_sha256, native_bytes=native_bytes,
            expected_loaded_path=expected_loaded_path)
    _require(len(set(live_counts)) == 1,
             "native mapping lifetime KAT live count drift")


def _verify_fast_path_operation_kat(result: Mapping[str, object]) -> None:
    kat = _mapping(
        result.get("fast_path_operation_kat"), "fast_path_operation_kat")
    _require(
        set(kat) == {"registered_performance_timing_count", "relation",
                     "schema", "triangle"}
        and kat.get("schema") == "rtdl.goal5801.fast_path_operation_kat.v1"
        and kat.get("registered_performance_timing_count") == 0,
        "fast path operation KAT envelope")

    def verify_family(
        family: str, *, launches: int, control_bytes: int,
        output_bytes: int, calls: list[int], builds: list[int],
    ) -> None:
        row = _mapping(kat.get(family), f"fast path operation KAT {family}")
        expected_envelope = {
            "failure_code": "RX035_DEVICE_STATUS_INVALID",
            "receipt_sha256": None,
            "receipts": None,
            "success_control_d2h_bytes": control_bytes,
            "success_output_d2h_bytes": output_bytes,
            "success_total_d2h_bytes": control_bytes + output_bytes,
        }
        if family == "relation":
            expected_envelope.update({
                "output_row_count": 4096,
                "raw_event_count": 8192,
                "unique_event_count": 4096,
                "semantic_compaction_hostile": None,
            })
        _require(set(row) == set(expected_envelope),
                 f"fast path operation KAT {family} fields")
        for key, expected in expected_envelope.items():
            if expected is not None:
                _require(type(row.get(key)) is type(expected)
                         and row.get(key) == expected,
                         f"fast path operation KAT {family}.{key}")
        receipts = row.get("receipts")
        receipt_hashes = row.get("receipt_sha256")
        _require(isinstance(receipts, list) and len(receipts) == 4
                 and isinstance(receipt_hashes, list)
                 and len(receipt_hashes) == 4,
                 f"fast path operation KAT {family} receipt arrays")
        generations: list[int] = []
        for index, raw_receipt in enumerate(receipts):
            receipt = _mapping(
                raw_receipt, f"fast path operation KAT {family}[{index}]")
            success = index < 3
            reused = index == 1
            expected = {
                "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
                "optix_launch_count": launches,
                "host_blocking_boundary_count": 2 if success else 1,
                "control_d2h_bytes": control_bytes,
                "output_d2h_bytes": output_bytes if success else 0,
                "status_before_output": True,
                "output_d2h_after_status_failure": 0,
                "role_counters_materialized": False,
                "prepared_input_reused": reused,
                "dynamic_device_upload_call_count": calls[index],
                "dynamic_accel_build_count": builds[index],
                "dynamic_explicit_sync_count": 0,
                "dynamic_blocking_upload_call_count": 0,
                "callback_status_kernel_launch_count": 5 if family == "relation" else 3,
                "checked_product_kernel_launch_count": 0 if family == "relation" else 2,
                "compact_control_finalizer_kernel_launch_count": 1,
                "total_auxiliary_cuda_kernel_launch_count": 7 if family == "relation" else 6,
                "execution_parameter_h2d_bytes": 224 if family == "relation" else 200,
                "execution_parameter_h2d_copy_call_count": 2 if family == "relation" else 1,
                "stream_ordered_memset_call_count": 9 if family == "relation" else 4,
                "status_d2h_copy_call_count": 1,
                "output_d2h_copy_call_count": 1 if success else 0,
                "semantic_compaction_launch_count": 1 if family == "relation" else 0,
                "semantic_compaction_key_capacity": 8192 if family == "relation" else 0,
                "semantic_compaction_scratch_bytes": 98_312 if family == "relation" else 0,
            }
            _require(set(receipt) == set(expected) | {
                         "dynamic_device_upload_bytes", "dynamic_input_generation"},
                     f"fast path operation KAT {family}[{index}] receipt fields")
            _require(all(type(receipt.get(key)) is type(value)
                         and receipt.get(key) == value
                         for key, value in expected.items()),
                     f"fast path operation KAT {family}[{index}] facts")
            upload_bytes = receipt.get("dynamic_device_upload_bytes")
            generation = receipt.get("dynamic_input_generation")
            _require(type(upload_bytes) is int
                     and (upload_bytes == 0 if reused else upload_bytes > 0)
                     and type(generation) is int and generation > 0,
                     f"fast path operation KAT {family}[{index}] dynamic facts")
            generations.append(generation)
            expected_hash = _sha_bytes(_canonical(dict(receipt)))
            _require(receipt_hashes[index] == expected_hash
                     and isinstance(receipt_hashes[index], str)
                     and SHA256.fullmatch(receipt_hashes[index]) is not None,
                     f"fast path operation KAT {family}[{index}] receipt seal")
        _require(generations == [1, 1, 2, 3],
                 f"fast path operation KAT {family} generation sequence")

    verify_family(
        "relation", launches=2, control_bytes=16, output_bytes=32_768,
        calls=[2, 0, 2, 2], builds=[1, 0, 1, 1])
    verify_family(
        "triangle", launches=1, control_bytes=4, output_bytes=8,
        calls=[8, 0, 8, 8], builds=[0, 0, 0, 0])

    relation = _mapping(kat["relation"], "fast path operation KAT relation")
    hostile = _mapping(
        relation.get("semantic_compaction_hostile"),
        "fast path operation KAT relation semantic hostile")
    expected_hostile_keys = {
        "k_plus_one_compact_control", "k_plus_one_failure_code",
        "k_plus_one_receipt", "max_u64_key_output",
        "max_u64_key_receipts", "raw_capacity",
        "raw_count_below_raw_capacity",
        "registered_performance_timing_count",
        "same_input_reuse_clears_compaction_scratch",
    }
    _require(set(hostile) == expected_hostile_keys
             and hostile["k_plus_one_failure_code"]
             == "RX035_DEVICE_STATUS_INVALID"
             and hostile["max_u64_key_output"]
             == [[(1 << 32) - 1, (1 << 32) - 1]]
             and hostile["raw_capacity"] == 8192
             and hostile["raw_count_below_raw_capacity"] is True
             and hostile["registered_performance_timing_count"] == 0
             and hostile["same_input_reuse_clears_compaction_scratch"] is True,
             "fast path relation semantic-hostile envelope")
    control = _mapping(
        hostile["k_plus_one_compact_control"],
        "fast path relation K+1 compact control")
    _require(control == {
        "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
        "raw_event_count": 4097,
        "unique_event_count": 4097,
        "overflowed": 1,
        "status": 0xffff5102,
        "semantic_capacity": 4096,
        "control_d2h_bytes": 16,
    } and control["raw_event_count"] < hostile["raw_capacity"],
             "fast path relation K+1 device unique gate")

    def verify_semantic_receipt(
        raw: object, *, reused: bool, success: bool, generation: int,
        upload_bytes: int,
    ) -> None:
        receipt = _mapping(raw, "fast path relation semantic receipt")
        expected = {
            "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
            "optix_launch_count": 2,
            "host_blocking_boundary_count": 2 if success else 1,
            "control_d2h_bytes": 16,
            "output_d2h_bytes": 8 if success else 0,
            "status_before_output": True,
            "output_d2h_after_status_failure": 0,
            "role_counters_materialized": False,
            "prepared_input_reused": reused,
            "dynamic_device_upload_call_count": 0 if reused else 2,
            "dynamic_device_upload_bytes": upload_bytes,
            "dynamic_accel_build_count": 0 if reused else 1,
            "dynamic_explicit_sync_count": 0,
            "dynamic_blocking_upload_call_count": 0,
            "dynamic_input_generation": generation,
            "semantic_compaction_launch_count": 1,
            "semantic_compaction_key_capacity": 8192,
            "semantic_compaction_scratch_bytes": 98_312,
            "callback_status_kernel_launch_count": 5,
            "checked_product_kernel_launch_count": 0,
            "compact_control_finalizer_kernel_launch_count": 1,
            "total_auxiliary_cuda_kernel_launch_count": 7,
            "execution_parameter_h2d_bytes": 224,
            "execution_parameter_h2d_copy_call_count": 2,
            "stream_ordered_memset_call_count": 9,
            "status_d2h_copy_call_count": 1,
            "output_d2h_copy_call_count": 1 if success else 0,
        }
        _require(receipt == expected,
                 "fast path relation semantic receipt facts")

    max_receipts = hostile["max_u64_key_receipts"]
    _require(isinstance(max_receipts, list) and len(max_receipts) == 2,
             "fast path relation max-key receipt count")
    verify_semantic_receipt(
        max_receipts[0], reused=False, success=True, generation=1,
        upload_bytes=52)
    verify_semantic_receipt(
        max_receipts[1], reused=True, success=True, generation=1,
        upload_bytes=0)
    verify_semantic_receipt(
        hostile["k_plus_one_receipt"], reused=False, success=False,
        generation=2, upload_bytes=52 * 4097)


def _read_command(path: Path, label: str) -> list[object]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{label}: invalid command JSON: {error}") from error
    _require(isinstance(value, list) and all(isinstance(token, str)
             for token in value), f"{label}: string token list required")
    _require(raw == _canonical(value) + b"\n",
             f"{label}: canonical JSON plus LF required")
    return value


def _root_before_suffix(value: object, suffix: str, label: str) -> str:
    normalized = _normalized_token(value).rstrip("/")
    canonical_suffix = "/" + suffix.strip("/")
    _require(normalized.endswith(canonical_suffix),
             f"{label}: expected path suffix {canonical_suffix}")
    root = normalized[:-len(canonical_suffix)].rstrip("/")
    _require(bool(root), f"{label}: absolute packet root required")
    return root


def _saved_relative(packet_root: Path, saved_path: Path, label: str) -> str:
    try:
        relative = saved_path.relative_to(packet_root).as_posix()
    except ValueError as error:
        raise RuntimeError(f"{label}: saved input is outside packet") from error
    _require(relative and not relative.startswith("../"),
             f"{label}: nonempty saved path required")
    return relative


def _external_projection_root(
    records: Mapping[str, Mapping[str, object]], prefix: str,
) -> str:
    roots: set[str] = set()
    count = 0
    for role, row in records.items():
        if not role.startswith(prefix):
            continue
        count += 1
        relative = role.removeprefix(prefix)
        _require(bool(relative), f"{prefix}: empty projection member")
        source = _normalized_token(row.get("source_path"))
        suffix = "/" + relative
        _require(source.endswith(suffix),
                 f"{role}: source path does not bind projection member")
        roots.add(source[:-len(suffix)].rstrip("/"))
    _require(count > 0 and len(roots) == 1,
             f"{prefix}: one external projection root required")
    return next(iter(roots))


def _verify_execution_commands(
    root: Path, inputs: Mapping[str, Path],
    records: Mapping[str, Mapping[str, object]],
) -> str:
    """Verify the exact clean-install command protocol after relocation.

    Receipt paths necessarily name the packet's execution-time root.  The
    verifier may itself run from a copied packet, so it derives that old root
    once and then requires every packet-owned token to share it.
    """

    venv_command = _read_command(root / "receipts/venv.command.json", "venv")
    _require(len(venv_command) == 4
             and _normalized_token(venv_command[0])
             == _normalized_token(records["base_python"]["source_path"])
             and venv_command[1:3] == ["-I", "-c"],
             "venv command prefix")
    bootstrap_source = _external_projection_root(
        records, "virtualenv_bootstrap/")
    code = str(venv_command[3])
    code_prefix = (
        "import runpy,sys;sys.dont_write_bytecode=True;"
        f"sys.path.insert(0,{bootstrap_source!r});"
        "sys.argv=['virtualenv','--no-download','--copies','--app-data',"
    )
    code_suffix = (
        "];runpy.run_module('virtualenv',run_name='__main__')"
    )
    _require(code.startswith(code_prefix) and code.endswith(code_suffix),
             "venv command exact bootstrap/no-download framing")
    literal = code[len(code_prefix):-len(code_suffix)]
    try:
        app_data_path, venv_path = ast.literal_eval(f"({literal})")
    except (SyntaxError, ValueError) as error:
        raise RuntimeError("venv command output paths literal") from error
    _require(
        isinstance(app_data_path, str) and isinstance(venv_path, str),
        "venv command output path strings")
    app_data_root = _root_before_suffix(
        app_data_path, "virtualenv_app_data", "venv app-data command")
    execution_root = _root_before_suffix(venv_path, "venv", "venv command")
    _require(app_data_root == execution_root,
             "venv app-data/output roots differ")

    wheel_relative = _saved_relative(root, inputs["wheel"], "wheel")
    install_command = _read_command(
        root / "receipts/install.command.json", "install")
    expected_install = [
        f"{execution_root}/venv/bin/python", "-I", "-m", "pip", "install",
        "--isolated", "--no-index", "--no-deps", "--no-cache-dir",
        "--no-compile",
        f"{execution_root}/{wheel_relative}",
    ]
    _require([_normalized_token(token) for token in install_command]
             == expected_install, "install command exact isolated local wheel")

    probe_command = _read_command(root / "receipts/probe.command.json", "probe")
    source_path = _normalized_token(records["source_pyproject"]["source_path"])
    _require(source_path.endswith("/pyproject.toml"),
             "source pyproject external path")
    source_root = source_path.removesuffix("/pyproject.toml")
    saved_arguments = (
        ("--relation", "relation_descriptor"),
        ("--triangle", "triangle_descriptor"),
        ("--candidate-manifest", "candidate_manifest"),
        ("--trust-root", "trust_root"),
        ("--trust-head", "trust_head"),
        ("--trust-package", "trust_package"),
        ("--native", "native"),
        ("--wheel", "wheel"),
    )
    expected_probe = [
        f"{execution_root}/venv/bin/python", "-I", "-B",
        f"{execution_root}/{_saved_relative(root, inputs['probe_source'], 'probe')}",
    ]
    for option, role in saved_arguments:
        expected_probe.extend((
            option,
            f"{execution_root}/{_saved_relative(root, inputs[role], role)}",
        ))
    expected_probe.extend((
        "--forbid-source-root", source_root,
        "--nvrtc-trap-library",
        f"{execution_root}/build/goal5801_nvrtc_forbidden_preload.so",
        "--nvrtc-trap-log", f"{execution_root}/build/nvrtc_lifecycle.log",
        "--output", f"{execution_root}/result.json",
    ))
    _require([_normalized_token(token) for token in probe_command]
             == expected_probe, "probe command exact public lifecycle inputs")

    host_cc = _normalized_token(records["host_cc"]["source_path"])
    header_parent = inputs["nvrtc_header"].parent
    trap_build = _read_command(
        root / "receipts/trap_build.command.json", "trap_build")
    expected_trap_build = [
        host_cc, "-shared", "-fPIC", "-I",
        f"{execution_root}/{_saved_relative(root, header_parent, 'nvrtc header root')}",
        f"{execution_root}/{_saved_relative(root, inputs['nvrtc_trap_source'], 'trap source')}",
        "-o", f"{execution_root}/build/goal5801_nvrtc_forbidden_preload.so",
    ]
    _require([_normalized_token(token) for token in trap_build]
             == expected_trap_build, "trap build exact command")
    kat_build = _read_command(
        root / "receipts/kat_build.command.json", "kat_build")
    expected_kat_build = [
        host_cc, "-I",
        f"{execution_root}/{_saved_relative(root, header_parent, 'nvrtc header root')}",
        f"{execution_root}/{_saved_relative(root, inputs['nvrtc_kat_source'], 'KAT source')}",
        f"{execution_root}/{_saved_relative(root, inputs['nvrtc_library'], 'NVRTC library')}",
        "-o", f"{execution_root}/build/goal5801_nvrtc_positive_kat",
    ]
    _require([_normalized_token(token) for token in kat_build]
             == expected_kat_build, "KAT build exact command")
    kat_command = _read_command(root / "receipts/kat.command.json", "kat")
    _require([_normalized_token(token) for token in kat_command] == [
        f"{execution_root}/build/goal5801_nvrtc_positive_kat",
    ], "KAT exact execution command")
    return execution_root


def _read_json(path: Path, *, canonical_lf: bool = False) \
        -> tuple[Mapping[str, object], bytes]:
    raw = path.read_bytes()
    try:
        value = _mapping(json.loads(raw.decode("utf-8")), str(path))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{path}: invalid JSON: {error}") from error
    if canonical_lf and raw != _canonical(value) + b"\n":
        _fail(f"{path}: canonical JSON plus LF required")
    return value, raw


def _safe_path(root: Path, relative: object, label: str) -> Path:
    _require(isinstance(relative, str), f"{label}: string path required")
    posix = PurePosixPath(relative)
    _require(not posix.is_absolute() and relative == posix.as_posix()
             and ".." not in posix.parts and "." not in posix.parts,
             f"{label}: unsafe/noncanonical path")
    path = root.joinpath(*posix.parts)
    cursor = root
    for part in posix.parts:
        cursor = cursor / part
        _require(not cursor.is_symlink(),
                 f"{label}: symlink component is forbidden")
    _require(path.is_file() and not path.is_symlink(), f"{label}: file absent/symlink")
    return path


def _strict_b64(value: object, label: str) -> bytes:
    _require(isinstance(value, str), f"{label}: base64 string required")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise RuntimeError(f"{label}: invalid base64") from error
    _require(bool(raw), f"{label}: empty base64")
    return raw


def _verify_rsa(signature: object, message: bytes, *, modulus: int,
                exponent: int, label: str) -> None:
    raw = _strict_b64(signature, f"{label}.signature")
    width = (modulus.bit_length() + 7) // 8
    _require(len(raw) == width, f"{label}: signature width")
    encoded = pow(int.from_bytes(raw, "big"), exponent, modulus).to_bytes(width, "big")
    tail = DIGEST_INFO + hashlib.sha256(message).digest()
    padding = width - len(tail) - 3
    _require(padding >= 8, f"{label}: RSA modulus too small")
    _require(encoded == b"\x00\x01" + b"\xff" * padding + b"\x00" + tail,
             f"{label}: RSA signature invalid")


def _input_identities(root: Path, run: Mapping[str, object]) \
        -> tuple[dict[str, Path], dict[str, Mapping[str, object]]]:
    rows = run.get("input_identities")
    _require(isinstance(rows, list) and rows, "run.input_identities absent")
    paths: dict[str, Path] = {}
    records: dict[str, Mapping[str, object]] = {}
    for index, raw_row in enumerate(rows):
        row = _mapping(raw_row, f"input_identities[{index}]")
        _require(set(row) == {"role", "source_path", "saved_path", "bytes", "sha256"},
                 f"input_identities[{index}]: exact keys")
        role = row["role"]
        _require(isinstance(role, str) and role and role not in paths,
                 f"input_identities[{index}].role")
        path = _safe_path(root, row["saved_path"], f"input:{role}")
        _require(type(row["bytes"]) is int and row["bytes"] >= 0
                 and len(path.read_bytes()) == row["bytes"]
                 and isinstance(row["sha256"], str)
                 and SHA256.fullmatch(row["sha256"]) is not None
                 and _sha(path) == row["sha256"], f"input:{role}: identity")
        paths[role] = path
        records[role] = row
    _require(list(paths) == sorted(paths), "input identities are not role-sorted")
    return paths, records


def _verify_wheel(wheel: Path, source_root: Path) -> tuple[int, str]:
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    allowed_dist = {
        f"{dist}/METADATA", f"{dist}/WHEEL", f"{dist}/top_level.txt",
        f"{dist}/RECORD",
    }
    with zipfile.ZipFile(wheel) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        _require(len(names) == len(set(names)) and not any(
            info.is_dir() for info in infos), "wheel duplicate/directory members")
        for name in names:
            posix = PurePosixPath(name)
            _require(not posix.is_absolute() and name == posix.as_posix()
                     and ".." not in posix.parts and "." not in posix.parts
                     and not name.endswith(".pth")
                     and not any(part.endswith(".data") for part in posix.parts)
                     and (name.startswith("rtdsl/") or name in allowed_dist),
                     f"wheel member outside boundary: {name}")
        _require({name for name in names if name.startswith(f"{dist}/")} == allowed_dist,
                 "wheel dist-info members differ")
        record_name = f"{dist}/RECORD"
        record_rows = list(csv.reader(io.StringIO(
            archive.read(record_name).decode("utf-8"), newline="")))
        _require(all(len(row) == 3 for row in record_rows)
                 and len({row[0] for row in record_rows}) == len(record_rows)
                 and {row[0] for row in record_rows} == set(names),
                 "wheel RECORD coverage/shape")
        for member, encoded_hash, encoded_size in record_rows:
            payload = archive.read(member)
            if member == record_name:
                _require(not encoded_hash and not encoded_size, "RECORD self identity")
            else:
                expected = base64.urlsafe_b64encode(
                    hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
                _require(encoded_hash == f"sha256={expected}"
                         and encoded_size == str(len(payload)),
                         f"RECORD identity: {member}")
        metadata = BytesParser().parsebytes(archive.read(f"{dist}/METADATA"))
        _require(metadata.get("Name") == "rtdl-source-tree"
                 and metadata.get("Version") == "4.0.0rc1"
                 and metadata.get("Requires-Python") == ">=3.10"
                 and [value.replace(" ", "")
                      for value in metadata.get_all("Requires-Dist", [])]
                 == ["numpy>=1.26"], "wheel METADATA differs")
        package = {
            name.removeprefix("rtdsl/"): archive.read(name)
            for name in names if name.startswith("rtdsl/")
        }
    source = {
        path.relative_to(source_root).as_posix(): path.read_bytes()
        for path in source_root.rglob("*") if path.is_file()
    }
    _require(package == source, "wheel package differs from frozen source")
    rows = [{"path": f"rtdsl/{name}", "bytes": len(payload),
             "sha256": _sha_bytes(payload)} for name, payload in sorted(package.items())]
    tree = _sha_bytes(_canonical(rows))
    return len(rows), tree


def _verify_signed_trust_package(
        package_path: Path, *, root: Mapping[str, object], modulus: int,
        exponent: int, expected_sequence: int,
        expected_previous_sha256: str | None,
) -> tuple[Mapping[str, object], bytes, list[Mapping[str, object]]]:
    package, package_raw = _read_json(package_path, canonical_lf=True)
    _require(set(package) == {"schema", "key_id", "sequence",
                              "previous_package_sha256", "authorities",
                              "signature_algorithm", "signature_base64"}
             and package["schema"] == TRUST_PACKAGE_SCHEMA
             and package["key_id"] == root["key_id"]
             and type(package["sequence"]) is int
             and package["sequence"] == expected_sequence
             and package["previous_package_sha256"]
             == expected_previous_sha256
             and package["signature_algorithm"]
             == "rsa-pkcs1-v1_5-sha256",
             f"trust package sequence {expected_sequence} envelope")
    signed = dict(package); signature = signed.pop("signature_base64")
    _verify_rsa(signature, TRUST_PACKAGE_DOMAIN + _canonical(signed),
                modulus=modulus, exponent=exponent,
                label=f"trust package sequence {expected_sequence}")
    raw_entries = package["authorities"]
    _require(isinstance(raw_entries, list)
             and len(raw_entries) == expected_sequence,
             f"trust package sequence {expected_sequence} authority count")
    expected_entry_keys = {
        "deployment_id", "family", "task_semantics_sha256",
        "authority_sha256", "artifact_sha256",
        "executable_identity_sha256", "target_sha256",
        "native_library_sha256", "compute_capability",
    }
    entries: list[Mapping[str, object]] = []
    for index, raw_entry in enumerate(raw_entries):
        entry = _mapping(
            raw_entry,
            f"trust package sequence {expected_sequence} authority {index}")
        _require(set(entry) == expected_entry_keys
                 and isinstance(entry.get("deployment_id"), str)
                 and bool(entry.get("deployment_id"))
                 and isinstance(entry.get("family"), str)
                 and bool(entry.get("family")),
                 f"trust package sequence {expected_sequence} authority envelope")
        for key in (
                "task_semantics_sha256", "authority_sha256",
                "artifact_sha256", "executable_identity_sha256",
                "target_sha256", "native_library_sha256"):
            _require(isinstance(entry.get(key), str)
                     and SHA256.fullmatch(str(entry[key])) is not None,
                     f"trust package sequence {expected_sequence} {key}")
        capability = entry.get("compute_capability")
        _require(isinstance(capability, list) and len(capability) == 2
                 and all(type(item) is int and item >= 0
                         for item in capability),
                 f"trust package sequence {expected_sequence} capability")
        entries.append(entry)
    deployment_ids = [str(entry["deployment_id"]) for entry in entries]
    _require(deployment_ids == sorted(deployment_ids)
             and len(deployment_ids) == len(set(deployment_ids)),
             f"trust package sequence {expected_sequence} ordering")
    return package, package_raw, entries


def _verify_trust(root_path: Path, head_path: Path,
                  predecessor_package_path: Path, package_path: Path) \
        -> tuple[list[Mapping[str, object]], list[Mapping[str, object]]]:
    root, root_raw = _read_json(root_path, canonical_lf=True)
    _require(set(root) == {"schema", "key_id", "rsa_modulus_base64",
                           "rsa_exponent", "trust_root_sha256"}
             and root["schema"] == TRUST_ROOT_SCHEMA, "trust root envelope")
    body = dict(root); seal = body.pop("trust_root_sha256")
    _require(seal == _sha_bytes(TRUST_ROOT_DOMAIN + _canonical(body)),
             "trust root domain seal")
    modulus = int.from_bytes(_strict_b64(
        root["rsa_modulus_base64"], "trust_root.modulus"), "big")
    exponent = root["rsa_exponent"]
    _require(type(exponent) is int and exponent >= 3 and exponent % 2 == 1
             and modulus.bit_length() >= 2048, "trust root RSA key")

    predecessor, predecessor_raw, predecessor_entries = (
        _verify_signed_trust_package(
            predecessor_package_path, root=root, modulus=modulus,
            exponent=exponent, expected_sequence=1,
            expected_previous_sha256=None))
    package, package_raw, entries = _verify_signed_trust_package(
        package_path, root=root, modulus=modulus, exponent=exponent,
        expected_sequence=CONTROLLING_TRUST_SEQUENCE,
        expected_previous_sha256=_sha_bytes(predecessor_raw))
    predecessor_by_id = {
        str(entry["deployment_id"]): entry for entry in predecessor_entries}
    current_by_id = {str(entry["deployment_id"]): entry for entry in entries}
    _require(len(predecessor_by_id) == len(predecessor_entries)
             and len(current_by_id) == len(entries)
             and len(current_by_id) == len(predecessor_by_id) + 1
             and all(current_by_id.get(key) == value
                     for key, value in predecessor_by_id.items()),
             "trust package sequence 2 is not an exact append of sequence 1")

    head, _ = _read_json(head_path, canonical_lf=True)
    _require(set(head) == {"schema", "key_id", "current_package_sha256",
                           "current_sequence", "signature_algorithm",
                           "signature_base64"}
             and head["schema"] == TRUST_HEAD_SCHEMA
             and head["key_id"] == root["key_id"]
             and head["current_package_sha256"] == _sha_bytes(package_raw)
             and type(head["current_sequence"]) is int
             and head["current_sequence"] == package["sequence"]
             and head["signature_algorithm"] == "rsa-pkcs1-v1_5-sha256",
             "trust head envelope/binding")
    head_body = dict(head); head_signature = head_body.pop("signature_base64")
    _verify_rsa(head_signature, TRUST_HEAD_DOMAIN + _canonical(head_body),
                modulus=modulus, exponent=exponent, label="trust head")
    _require(predecessor["key_id"] == package["key_id"],
             "trust predecessor/current key differs")
    return entries, predecessor_entries


def _authority_entry(authority: Mapping[str, object], authority_sha: str) \
        -> dict[str, object]:
    return {
        "deployment_id": authority["deployment_id"],
        "family": authority["family"],
        "task_semantics_sha256": authority["task_semantics_sha256"],
        "authority_sha256": authority_sha,
        "artifact_sha256": authority["artifact_sha256"],
        "executable_identity_sha256": authority["executable_identity_sha256"],
        "target_sha256": authority["target_sha256"],
        "native_library_sha256": authority["native_library_sha256"],
        "compute_capability": authority["target_compute_capability"],
    }


def _verify_candidate(root: Path, family: str, inputs: Mapping[str, Path],
                      native_sha: str) -> dict[str, object]:
    descriptor, descriptor_raw = _read_json(
        inputs[f"{family}_descriptor"], canonical_lf=True)
    _require(set(descriptor) == {"deployment_id", "artifact_path", "authority_path"},
             f"{family} descriptor envelope")
    artifact = inputs[f"{family}_artifact"]
    authority_path = inputs[f"{family}_authority"]
    _require(descriptor["artifact_path"] == artifact.relative_to(root).as_posix()
             and descriptor["authority_path"] == authority_path.relative_to(root).as_posix(),
             f"{family} descriptor saved paths")
    authority, authority_raw = _read_json(authority_path, canonical_lf=True)
    expected_keys = {
        "schema", "authority_version", "artifact_sha256", "artifact_bytes",
        "product_projection_sha256", "protocol_decision_sha256",
        "executable_identity_sha256", "native_library_sha256", "target_sha256",
        "deployment_id", "family", "task_semantics_sha256",
        "target_compute_capability", "authority_seal",
    }
    _require(set(authority) == expected_keys and authority["schema"] == AUTHORITY_SCHEMA
             and type(authority["authority_version"]) is int
             and authority["authority_version"] == 1
             and type(authority["artifact_bytes"]) is int
             and authority["artifact_bytes"] > 0, f"{family} authority envelope")
    body = dict(authority); seal = body.pop("authority_seal")
    _require(seal == _sha_bytes(AUTHORITY_DOMAIN + _canonical(body)),
             f"{family} authority seal")
    artifact_raw = artifact.read_bytes()
    artifact_sha = _sha_bytes(artifact_raw)
    _require(artifact_sha == authority["artifact_sha256"]
             and len(artifact_raw) == authority["artifact_bytes"]
             and artifact.name == f"{artifact_sha}.rtdlexe"
             and authority["native_library_sha256"] == native_sha
             and authority["deployment_id"] == descriptor["deployment_id"],
             f"{family} artifact/authority/native binding")
    artifact_value = _mapping(json.loads(artifact_raw.decode("utf-8")), "artifact")
    _require(artifact_raw == _canonical(artifact_value) + b"\n"
             and artifact_value.get("schema") == ARTIFACT_SCHEMA
             and type(artifact_value.get("format_version")) is int
             and artifact_value.get("format_version") == 1,
             f"{family} artifact canonical envelope")
    return _authority_entry(authority, _sha_bytes(authority_raw))


def _verify_candidate_relation_protocol(
        candidate_manifest: Mapping[str, object],
        relation_artifact: Mapping[str, object]) -> None:
    """Cross-bind the v2 task parameters to the identity-bearing artifact."""

    schema = candidate_manifest.get("schema")
    if schema == "rtdl.goal5801.lx1_untimed_candidate_manifest.v1":
        # Historical Goal5801 packets remain independently verifiable.  The
        # Goal5802 binder separately forbids this legacy schema.
        return
    _require(schema == "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
             "unsupported candidate manifest schema")
    relation_protocol = _mapping(
        candidate_manifest.get("relation_protocol"),
        "candidate manifest relation_protocol")
    _require(set(relation_protocol) == {
                 "capacity", "minimum_overlap_boundary",
                 "minimum_overlap_f32", "minimum_overlap_f32_bits",
             }
             and type(relation_protocol.get("capacity")) is int
             and relation_protocol.get("capacity") == 4096
             and relation_protocol.get("minimum_overlap_boundary")
             == "inclusive"
             and type(relation_protocol.get("minimum_overlap_f32")) is float
             and type(relation_protocol.get("minimum_overlap_f32_bits")) is int,
             "candidate manifest relation protocol envelope")
    relation_threshold = float(relation_protocol["minimum_overlap_f32"])
    try:
        relation_threshold_bytes = struct.pack("<f", relation_threshold)
    except (OverflowError, struct.error) as error:
        raise RuntimeError(
            "candidate manifest relation threshold is outside f32") from error
    _require(math.isfinite(relation_threshold)
             and relation_threshold >= 0.0
             and struct.unpack("<f", relation_threshold_bytes)[0]
             == relation_threshold
             and relation_protocol.get("minimum_overlap_f32_bits")
             == struct.unpack("<I", relation_threshold_bytes)[0],
             "candidate manifest exact relation threshold")
    relation_product = _mapping(
        relation_artifact.get("product_projection"),
        "relation artifact product_projection")
    relation_runtime = _mapping(
        relation_product.get("runtime"),
        "relation artifact product_projection.runtime")
    _require(type(relation_runtime.get("capacity")) is int
             and type(relation_runtime.get("minimum_overlap_f32")) is float
             and relation_runtime.get("capacity")
             == relation_protocol["capacity"]
             and relation_runtime.get("minimum_overlap_f32")
             == relation_threshold,
             "candidate manifest/artifact relation protocol binding")


def _verify_trusted_candidate_entries(
        candidate_entries: Mapping[str, Mapping[str, object]],
        trusted: list[Mapping[str, object]], *,
        retained_predecessors: Mapping[str, str] | None = None) -> None:
    """Bind exact candidate authorities to the signed deployment slots.

    Keeping this as a separately hostile-testable operation is important: a
    coherent artifact+detached-authority rewrite still has to fail unless the
    independently signed trust package is rewritten and re-signed too.
    """
    trusted_by_id = {str(row.get("deployment_id")): row for row in trusted}
    _require(len(trusted_by_id) == len(trusted),
             "duplicate deployment id in signed trust package")
    current_ids = {
        str(entry["deployment_id"]) for entry in candidate_entries.values()}
    retained = dict(retained_predecessors or {})
    _require(not current_ids.intersection(retained)
             and set(trusted_by_id) == current_ids.union(retained),
             "signed trust package retained/current deployment set differs")
    for deployment_id, native_sha256 in retained.items():
        _require(trusted_by_id[deployment_id].get("native_library_sha256")
                 == native_sha256,
                 "retained predecessor native identity differs")
    for entry in candidate_entries.values():
        _require(trusted_by_id[str(entry["deployment_id"])] == entry,
                 "trust slot differs from candidate authority")


def verify(
        root: Path, *,
        qualification_only_expected_trust_root_file_sha256: str | None = None,
) -> dict[str, object]:
    supplied_root = root.expanduser()
    _require(not supplied_root.is_symlink(), "clean-install root must not be a symlink")
    root = supplied_root.resolve(strict=True)
    _require(root.is_dir(), "clean-install root must be a directory")
    ephemeral_venv = root / "venv"
    if ephemeral_venv.exists() or ephemeral_venv.is_symlink():
        _require(not ephemeral_venv.is_symlink() and ephemeral_venv.is_dir(),
                 "top-level ephemeral venv must be a real directory")
    for path in root.rglob("*"):
        if path.relative_to(root).parts[:1] == ("venv",):
            continue
        _require(not path.is_symlink(),
                 f"clean-install evidence contains a symlink: {path}")
        _require(path.is_file() or path.is_dir(),
                 f"clean-install evidence contains a special file: {path}")
    run, run_raw = _read_json(root / "run.json", canonical_lf=True)
    _require(run.get("schema") == RUN_SCHEMA
             and run.get("status") == "PASS__FRESH_VENV__ISOLATED_LOCAL_WHEEL__PUBLIC_API"
             and run.get("registered_performance_timing_count") == 0
             and run.get("claim_boundary") == "install_and_execution_receipt__not_performance",
             "clean-install run envelope")
    inputs, input_records = _input_identities(root, run)
    required_roles = {
        "candidate_manifest", "relation_descriptor", "relation_artifact",
        "relation_authority", "triangle_descriptor", "triangle_artifact",
        "triangle_authority", "trust_root", "trust_head",
        "trust_predecessor_package", "trust_package",
        "native", "wheel", "probe_source", "host_cc", "base_python",
        "runner_source",
        "nvrtc_header", "nvrtc_library", "nvrtc_trap_source",
        "nvrtc_kat_source", "nvrtc_trap_library", "nvrtc_kat_binary",
        "source_pyproject", "source_readme",
    }
    _require(required_roles <= set(inputs), "required saved input roles absent")
    bootstrap_roles = {
        role.removeprefix("virtualenv_bootstrap/"): path
        for role, path in inputs.items() if role.startswith("virtualenv_bootstrap/")
    }
    source_roles = {
        role.removeprefix("source_package/"): path
        for role, path in inputs.items() if role.startswith("source_package/")
    }
    _require(bootstrap_roles and source_roles, "bootstrap/source projections absent")
    allowed_roles = required_roles.union(
        {f"virtualenv_bootstrap/{name}" for name in bootstrap_roles},
        {f"source_package/{name}" for name in source_roles})
    _require(set(inputs) == allowed_roles,
             "clean-install input role grammar differs")
    bootstrap_rows = [{
        "path": name, "bytes": path.stat().st_size, "sha256": _sha(path),
    } for name, path in sorted(bootstrap_roles.items())]
    _require(run.get("virtualenv_bootstrap_files") == bootstrap_rows
             and run.get("virtualenv_bootstrap_file_count") == len(bootstrap_rows)
             and run.get("virtualenv_creation_uses_network") is False,
             "virtualenv bootstrap binding")

    actual_payloads = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path != root / "run.json"
        and path.relative_to(root).parts[:1] != ("venv",)
    }
    receipt_rows = run.get("receipts")
    _require(isinstance(receipt_rows, list)
             and run.get("receipt_file_count") == len(receipt_rows),
             "run receipt inventory")
    recorded: dict[str, tuple[int, str]] = {}
    for raw_row in receipt_rows:
        row = _mapping(raw_row, "receipt row")
        _require(set(row) == {"path", "bytes", "sha256"}, "receipt row keys")
        path = row["path"]
        _require(isinstance(path, str) and path not in recorded
                 and type(row["bytes"]) is int and row["bytes"] >= 0
                 and isinstance(row["sha256"], str), "receipt row values")
        recorded[path] = (row["bytes"], row["sha256"])
    _require(set(recorded) == set(actual_payloads), "run payload inventory differs")
    for name, path in actual_payloads.items():
        size, digest = recorded[name]
        _require(path.stat().st_size == size and _sha(path) == digest,
                 f"run payload differs: {name}")

    for label, expected in (
            ("trap_build", b"0\n"), ("kat_build", b"0\n"),
            ("kat", b"97\n"), ("venv", b"0\n"),
            ("install", b"0\n"), ("probe", b"0\n")):
        _require((root / f"receipts/{label}.exit_code").read_bytes() == expected,
                 f"{label} exit receipt")
    _require((root / "build/nvrtc_kat.log").read_bytes() == b"nvrtcCreateProgram\n"
             and (root / "build/nvrtc_lifecycle.log").read_bytes() == b"",
             "NVRTC KAT/lifecycle logs")
    _require(inputs["nvrtc_trap_library"].read_bytes()
             == (root / "build/goal5801_nvrtc_forbidden_preload.so").read_bytes()
             and inputs["nvrtc_kat_binary"].read_bytes()
             == (root / "build/goal5801_nvrtc_positive_kat").read_bytes(),
             "built trap/KAT saved copies")

    execution_root = _verify_execution_commands(root, inputs, input_records)

    build_environment, build_environment_raw = _read_json(
        root / "receipts/build_environment.json")
    kat_environment, kat_environment_raw = _read_json(
        root / "receipts/kat_environment.json")
    expected_kat_environment = dict(build_environment)
    expected_kat_environment.update({
        "LD_PRELOAD": (
            f"{execution_root}/build/goal5801_nvrtc_forbidden_preload.so"),
        "RTDL_GOAL5801_NVRTC_TRAP_LOG": (
            f"{execution_root}/build/nvrtc_kat.log"),
    })
    _require(build_environment_raw == _canonical(build_environment) + b"\n"
             and kat_environment_raw == _canonical(kat_environment) + b"\n"
             and "PYTHONPATH" not in build_environment
             and "LD_PRELOAD" not in build_environment
             and "RTDL_GOAL5801_NVRTC_TRAP_LOG" not in build_environment
             and build_environment.get("PIP_CONFIG_FILE") == "/dev/null"
             and build_environment.get("PIP_DISABLE_PIP_VERSION_CHECK") == "1"
             and build_environment.get("PIP_NO_INDEX") == "1"
             and build_environment.get("PYTHONNOUSERSITE") == "1"
             and build_environment.get("PYTHONDONTWRITEBYTECODE") == "1"
             and kat_environment == expected_kat_environment,
             "build/KAT environments")

    result, _ = _read_json(root / "result.json")
    _require(result.get("schema") == RESULT_SCHEMA
             and result.get("status")
             == "PASS__CLEAN_WHEEL__TOP_LEVEL_ALIASES__TWO_FAMILY_LIFECYCLE"
             and result.get("registered_performance_timing_count") == 0
             and result.get("nvrtc_lifecycle_log_bytes") == 0
             and result.get("forbidden_compiler_modules") == [],
             "clean-install result envelope")
    _require(run.get("result_sha256") == _sha(root / "result.json")
             and run.get("wheel_sha256") == _sha(inputs["wheel"])
             and run.get("native_sha256") == _sha(inputs["native"])
             and run.get("base_python_sha256") == _sha(inputs["base_python"])
             and run.get("nvrtc_trap_library_sha256")
             == _sha(inputs["nvrtc_trap_library"])
             and run.get("nvrtc_positive_kat_log_sha256")
             == _sha(root / "build/nvrtc_kat.log")
             and run.get("nvrtc_positive_kat_exit_code") == 97
             and run.get("nvrtc_lifecycle_log_bytes") == 0,
             "run/result/input hashes")

    source_root = root / "inputs/source/src/rtdsl"
    try:
        pyproject = tomllib.loads(inputs["source_pyproject"].read_text(
            encoding="utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError(f"frozen pyproject invalid: {error}") from error
    project = _mapping(pyproject.get("project"), "pyproject.project")
    _require(project.get("name") == "rtdl-source-tree"
             and project.get("version") == "4.0.0rc1"
             and project.get("requires-python") == ">=3.10"
             and project.get("dependencies") == ["numpy>=1.26"],
             "frozen pyproject metadata boundary")
    wheel_count, wheel_tree = _verify_wheel(inputs["wheel"], source_root)
    _require(result.get("wheel_sha256") == _sha(inputs["wheel"])
             and result.get("wheel_rtdsl_file_count") == wheel_count
             and result.get("wheel_rtdsl_tree_sha256") == wheel_tree
             and result.get("native_sha256") == _sha(inputs["native"]),
             "result wheel/native binding")

    candidate_manifest, _ = _read_json(inputs["candidate_manifest"])
    candidates = candidate_manifest.get("candidates")
    candidate_schema = candidate_manifest.get("schema")
    _require(candidate_schema in {
                 "rtdl.goal5801.lx1_untimed_candidate_manifest.v1",
                 "rtdl.goal5801.lx1_untimed_candidate_manifest.v2",
             }
             and candidate_manifest.get("status")
             == "UNTRUSTED_CANDIDATES__NOT_AUTHORIZED"
             and candidate_manifest.get("registered_timing_count") == 0
             and isinstance(candidates, dict)
             and set(candidates) == {"relation", "triangle"},
             "candidate manifest envelope/families")
    native_sha = _sha(inputs["native"])
    native_relative = inputs["native"].relative_to(root).as_posix()
    expected_loaded_path = (
        f"{_normalized_token(execution_root).rstrip('/')}/"
        f"{native_relative}")
    _verify_actual_prepared_native_dsos(
        result, native_sha256=native_sha,
        native_bytes=inputs["native"].stat().st_size,
        expected_loaded_path=expected_loaded_path)
    _verify_native_mapping_lifetime_kat(
        result, native_sha256=native_sha,
        native_bytes=inputs["native"].stat().st_size,
        expected_loaded_path=expected_loaded_path)
    _verify_fast_path_operation_kat(result)
    _require(candidate_manifest.get("native_sha256") == native_sha,
             "candidate manifest native binding")
    relation_artifact, _ = _read_json(
        inputs["relation_artifact"], canonical_lf=True)
    _verify_candidate_relation_protocol(candidate_manifest, relation_artifact)
    candidate_entries = {
        family: _verify_candidate(root, family, inputs, native_sha)
        for family in ("relation", "triangle")
    }
    for family, entry in candidate_entries.items():
        manifest_row = _mapping(candidates[family], f"candidate manifest {family}")
        _require(manifest_row.get("deployment_id") == entry["deployment_id"]
                 and manifest_row.get("artifact_sha256") == entry["artifact_sha256"]
                 and manifest_row.get("authority_sha256") == entry["authority_sha256"]
                 and manifest_row.get("executable_identity_sha256")
                 == entry["executable_identity_sha256"],
                 f"candidate manifest {family} binding")
    trusted, predecessor_trusted = _verify_trust(
        inputs["trust_root"], inputs["trust_head"],
        inputs["trust_predecessor_package"], inputs["trust_package"])
    trust_root_verification_scope, trust_root_file_sha256 = (
        _verify_trust_root_file_identity(
            inputs["trust_root"],
            qualification_only_expected_sha256=(
                qualification_only_expected_trust_root_file_sha256)))
    _require(predecessor_trusted == [candidate_entries["relation"]],
             "sequence-1 predecessor is not the exact current relation authority")
    _verify_trusted_candidate_entries(
        candidate_entries, trusted,
        retained_predecessors=RETAINED_PREDECESSOR_DEPLOYMENTS)

    expected_execution = {
        "candidate_manifest": _sha(inputs["candidate_manifest"]),
        "relation_descriptor": _sha(inputs["relation_descriptor"]),
        "relation_artifact": _sha(inputs["relation_artifact"]),
        "relation_authority": _sha(inputs["relation_authority"]),
        "triangle_descriptor": _sha(inputs["triangle_descriptor"]),
        "triangle_artifact": _sha(inputs["triangle_artifact"]),
        "triangle_authority": _sha(inputs["triangle_authority"]),
        "trust_root": _sha(inputs["trust_root"]),
        "trust_head": _sha(inputs["trust_head"]),
        "trust_package": _sha(inputs["trust_package"]),
        "native": native_sha,
        "wheel": _sha(inputs["wheel"]),
        "probe_source": _sha(inputs["probe_source"]),
        "nvrtc_trap_library": _sha(inputs["nvrtc_trap_library"]),
        "nvrtc_lifecycle_log": _sha(root / "build/nvrtc_lifecycle.log"),
    }
    _require(result.get("execution_input_sha256") == expected_execution,
             "probe execution input identities")
    environment, env_raw = _read_json(root / "receipts/environment.json")
    expected_environment = dict(build_environment)
    expected_environment.update({
        "LD_PRELOAD": (
            f"{execution_root}/build/goal5801_nvrtc_forbidden_preload.so"),
        "RTDL_GOAL5801_NVRTC_TRAP_LOG": (
            f"{execution_root}/build/nvrtc_lifecycle.log"),
    })
    _require(env_raw == _canonical(environment) + b"\n"
             and "PYTHONPATH" not in environment
             and environment.get("PIP_NO_INDEX") == "1"
             and environment.get("PYTHONNOUSERSITE") == "1"
             and environment == expected_environment,
             "clean-install environment")

    _require(result.get("relation", {}).get("output") == [[10, 100]]
             and result.get("relation", {}).get("status_d2h_bytes") == 112
             and result.get("triangle", {}).get("output") == 7
             and result.get("triangle", {}).get("total_product_d2h_bytes") == 152,
             "exact public lifecycle outputs/status bytes")
    for family in ("relation", "triangle"):
        traversal = _mapping(
            _mapping(result.get(family), family).get("traversal_receipt"),
            f"{family}.traversal_receipt")
        _require(traversal.get("physical_executor_classification")
                 == "optix_traversal_observed"
                 and traversal.get("provider_library_sha256") == native_sha,
                 f"{family} traversal/native binding")
    rtdsl_file = result.get("rtdsl_file")
    prefix = result.get("python_prefix")
    base_prefix = result.get("python_base_prefix")
    _require(result.get("fresh_virtual_environment") is True
             and result.get("source_tree_on_sys_path") is False
             and all(isinstance(value, str) and value
                     for value in (rtdsl_file, prefix, base_prefix))
             and str(prefix) != str(base_prefix)
             and str(rtdsl_file).replace("\\", "/").startswith(
                 str(prefix).replace("\\", "/").rstrip("/") + "/"),
             "fresh environment/import provenance")
    return {
        "status": "PASS__INDEPENDENT_CLEAN_INSTALL_V3_VERIFICATION",
        "run_sha256": _sha_bytes(run_raw),
        "wheel_sha256": _sha(inputs["wheel"]),
        "native_sha256": native_sha,
        "saved_input_count": len(inputs),
        "source_file_count": len(source_roles),
        "bootstrap_file_count": len(bootstrap_roles),
        "current_trusted_deployment_count": len(candidate_entries),
        "retained_predecessor_deployment_count": len(
            RETAINED_PREDECESSOR_DEPLOYMENTS),
        "signed_trust_package_deployment_count": len(trusted),
        "signed_trust_predecessor_deployment_count": len(
            predecessor_trusted),
        "signed_trust_predecessor_package_sha256": _sha(
            inputs["trust_predecessor_package"]),
        "trust_root_file_sha256": trust_root_file_sha256,
        "trust_root_verification_scope": trust_root_verification_scope,
        "formal_measurement_trust_root_accepted": (
            trust_root_verification_scope
            == "CONTROLLING_FORMAL_MEASUREMENT_ROOT"),
        "retired_test_trust_root_disclosure": (
            RETIRED_TEST_TRUST_ROOT_DISCLOSURE),
        "unmaterialized_retired_sequences_reconstructed": False,
        "registered_performance_timing_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_directory", type=Path)
    parser.add_argument(
        "--qualification-only-expected-trust-root-file-sha256")
    args = parser.parse_args()
    print(json.dumps(verify(
        args.run_directory,
        qualification_only_expected_trust_root_file_sha256=(
            args.qualification_only_expected_trust_root_file_sha256)),
        sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
