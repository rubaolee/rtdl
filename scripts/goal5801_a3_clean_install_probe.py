#!/usr/bin/env python3
"""Untimed clean-install proof for the public Goal5801 deployment API.

Run this file with the Python interpreter of a fresh virtual environment after
installing the candidate wheel.  The probe intentionally imports every runtime
type through the top-level :mod:`rtdsl` package.  It never adds a source tree to
``sys.path`` and fails if the imported package is not inside that environment.
"""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
from typing import NoReturn
import zipfile


SCHEMA = "rtdl.goal5801.a3.clean_install_public_api_result.v5"
NATIVE_MAPPING_LIFETIME_ROUNDS = 3
MAX_LIVE_NATIVE_MAPPING_ROWS_PER_TWO_OWNERS = 32


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _goal5802_relation_protocol(candidate_manifest: Path) -> dict[str, object]:
    """Read the exact relation task that this clean qualification exercises."""

    try:
        value = json.loads(candidate_manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _fail(f"candidate manifest is invalid: {error}")
    expected = {
        "capacity": 4096,
        "minimum_overlap_boundary": "inclusive",
        "minimum_overlap_f32": 1.0,
        "minimum_overlap_f32_bits": 0x3F800000,
    }
    relation = value.get("relation_protocol") if isinstance(value, dict) else None
    if not isinstance(value, dict) \
            or value.get("schema") \
            != "rtdl.goal5801.lx1_untimed_candidate_manifest.v2" \
            or not isinstance(relation, dict) \
            or set(relation) != set(expected) \
            or type(relation.get("capacity")) is not int \
            or type(relation.get("minimum_overlap_f32")) is not float \
            or type(relation.get("minimum_overlap_f32_bits")) is not int \
            or relation != expected:
        _fail("clean qualification requires the exact Goal5802 relation protocol")
    return relation


def _create_only_json(path: Path, value: object) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _load_candidate(path: Path, label: str) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("deployment_id") is None \
            or value.get("artifact_path") is None \
            or value.get("authority_path") is None:
        _fail(f"{label} candidate descriptor is incomplete")
    return value


def _descriptor_sha256(descriptor: int) -> tuple[str, int]:
    """Hash one already-open descriptor without changing its file offset."""

    try:
        metadata = os.fstat(descriptor)
    except OSError as error:
        _fail(f"prepared native image descriptor is unavailable: {error}")
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size <= 0:
        _fail("prepared native image descriptor is not a nonempty regular file")
    digest = hashlib.sha256()
    offset = 0
    while offset < metadata.st_size:
        try:
            block = os.pread(descriptor, min(1 << 20, metadata.st_size - offset), offset)
        except (AttributeError, OSError) as error:
            _fail(f"prepared native image descriptor cannot be read: {error}")
        if not block:
            _fail("prepared native image descriptor ended before its recorded size")
        digest.update(block)
        offset += len(block)
    return digest.hexdigest(), offset


def _native_image_seals(descriptor: int) -> tuple[int, int]:
    try:
        import fcntl  # pylint: disable=import-outside-toplevel
        required = (
            fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW |
            fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL)
        observed = int(fcntl.fcntl(descriptor, fcntl.F_GET_SEALS))
    except (AttributeError, ImportError, OSError) as error:
        _fail(f"prepared native image seals are unavailable: {error}")
    if observed & required != required:
        _fail("prepared native image lacks its required write/grow/shrink/seal seals")
    return observed, required


def _bind_actual_prepared_native_dso(
    prepared: object, *, label: str, expected_native_path: Path,
    expected_native_sha256: str,
) -> dict[str, object]:
    """Bind evidence to the private DSO that owns a public prepared value.

    This is deliberately evidence-harness-only private introspection.  It does
    not add a product API: application installation, load, prepare, execute and
    close remain calls through the public top-level ``rtdsl`` surface.
    """

    owner = getattr(prepared, "_owner", None)
    library = getattr(owner, "_library", None)
    if owner is None or library is None:
        _fail(f"{label} prepared owner has no live native library")
    loaded_path = getattr(library, "_rtdl_loaded_library_path", None)
    loaded_sha256 = getattr(library, "_rtdl_loaded_library_sha256", None)
    descriptor = getattr(library, "_rtdl_native_image_fd", None)
    recorded_seals = getattr(library, "_rtdl_native_image_seals", None)
    alias = getattr(library, "_rtdl_native_loader_alias", None)
    handle = getattr(library, "_handle", None)
    finalizer = getattr(library, "_rtdl_native_lease_abandon_finalizer", None)
    entry_identity = getattr(
        library, "_rtdl_native_cache_entry_identity", None)
    lease_id = getattr(library, "_rtdl_native_cache_lease_id", None)
    active_lease_count = getattr(
        library, "_rtdl_native_cache_active_lease_count", None)
    acquisition_count = getattr(
        library, "_rtdl_native_cache_acquisition_count", None)
    if loaded_path != str(expected_native_path) \
            or loaded_sha256 != expected_native_sha256:
        _fail(f"{label} prepared owner loaded an unexpected native identity")
    if type(descriptor) is not int or descriptor < 0 \
            or type(handle) is not int or handle <= 0:
        _fail(f"{label} prepared owner native descriptor/handle is invalid")
    if not isinstance(alias, str) or not Path(alias).is_absolute() \
            or Path(alias).exists() or Path(alias).parent.exists():
        _fail(f"{label} prepared owner loader alias was not removed after load")
    if finalizer is None or getattr(finalizer, "alive", None) is not True:
        _fail(f"{label} prepared owner native lease lifetime is not live")
    if not isinstance(entry_identity, str) or not entry_identity.endswith(
            expected_native_sha256) \
            or type(lease_id) is not int or lease_id <= 0 \
            or type(active_lease_count) is not int or active_lease_count <= 0 \
            or type(acquisition_count) is not int or acquisition_count <= 0:
        _fail(f"{label} prepared owner native cache lease is invalid")
    descriptor_sha256, descriptor_bytes = _descriptor_sha256(descriptor)
    observed_seals, required_seals = _native_image_seals(descriptor)
    if descriptor_sha256 != expected_native_sha256 \
            or recorded_seals != observed_seals:
        _fail(f"{label} prepared owner sealed image identity is inconsistent")
    compiler_attempts = getattr(
        library, "rtdl_optix_v4_runtime_compiler_attempt_count_v1", None)
    if compiler_attempts is None:
        _fail(f"{label} prepared owner lacks the native compiler counter")
    compiler_attempts.argtypes = []
    compiler_attempts.restype = ctypes.c_uint64
    compiler_before = int(compiler_attempts())
    if compiler_before != 0:
        _fail(f"{label} actual prepared DSO compiled during preparation")
    return {
        "prepared": prepared,
        "owner": owner,
        "library": library,
        "counter": compiler_attempts,
        "evidence": {
            "compiler_attempt_count_before": compiler_before,
            "ctypes_handle": handle,
            "lease_abandon_finalizer_alive_before_execute": True,
            "loaded_library_path": loaded_path,
            "loaded_library_sha256": loaded_sha256,
            "native_image_bytes": descriptor_bytes,
            "native_image_fd": descriptor,
            "native_image_seals_before": observed_seals,
            "native_cache_entry_identity": entry_identity,
            "native_cache_lease_id": lease_id,
            "native_cache_active_lease_count_before_execute":
                active_lease_count,
            "native_cache_acquisition_count_before_execute":
                acquisition_count,
            "native_loader_alias": alias,
            "native_loader_alias_parent_removed_before_execute": True,
            "native_loader_alias_removed_before_execute": True,
            "required_native_image_seals": required_seals,
            "sealed_image_sha256_before": descriptor_sha256,
        },
    }


def _finish_actual_prepared_native_dso(
    binding: dict[str, object], *, label: str,
) -> dict[str, object]:
    """Read the same prepared owner's same DSO after execute, before close."""

    prepared = binding["prepared"]
    owner = binding["owner"]
    library = binding["library"]
    counter = binding["counter"]
    if getattr(prepared, "_owner", None) is not owner \
            or getattr(owner, "_library", None) is not library:
        _fail(f"{label} prepared owner changed its execution DSO")
    descriptor = getattr(library, "_rtdl_native_image_fd", None)
    if type(descriptor) is not int or descriptor != binding["evidence"]["native_image_fd"]:
        _fail(f"{label} prepared owner changed its native descriptor")
    after_sha256, after_bytes = _descriptor_sha256(descriptor)
    after_seals, required_seals = _native_image_seals(descriptor)
    evidence = dict(binding["evidence"])
    compiler_after = int(counter())
    if compiler_after != 0 \
            or after_sha256 != evidence["sealed_image_sha256_before"] \
            or after_bytes != evidence["native_image_bytes"] \
            or after_seals != evidence["native_image_seals_before"] \
            or required_seals != evidence["required_native_image_seals"] \
            or getattr(library, "_rtdl_native_lease_abandon_finalizer", None) is None \
            or getattr(
                library._rtdl_native_lease_abandon_finalizer,
                "alive", None) is not True:
        _fail(f"{label} actual prepared DSO changed or attempted runtime compilation")
    active_lease_count = getattr(
        library, "_rtdl_native_cache_active_lease_count", None)
    acquisition_count = getattr(
        library, "_rtdl_native_cache_acquisition_count", None)
    if type(active_lease_count) is not int or active_lease_count <= 0 \
            or type(acquisition_count) is not int or acquisition_count <= 0:
        _fail(f"{label} actual prepared DSO lost its cache lease")
    evidence.update({
        "compiler_attempt_count_after": compiler_after,
        "lease_abandon_finalizer_alive_after_execute_before_close": True,
        "native_cache_active_lease_count_after_execute": active_lease_count,
        "native_cache_acquisition_count_after_execute": acquisition_count,
        "same_owner_library_object_after_execute": True,
        "native_image_seals_after": after_seals,
        "sealed_image_sha256_after": after_sha256,
    })
    return evidence


def _native_mapping_count(expected_native_sha256: str) -> tuple[int, str]:
    maps = Path("/proc/self/maps")
    if not maps.is_file() or maps.is_symlink():
        _fail("native mapping lifetime KAT requires regular Linux procfs maps")
    marker = f"/memfd:rtdl-native-{expected_native_sha256[:16]} (deleted)"
    try:
        rows = maps.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        _fail(f"native mapping lifetime KAT cannot read procfs maps: {error}")
    matching = [row for row in rows if marker in row]
    unexpected = [row for row in rows
                  if "/memfd:rtdl-native-" in row and marker not in row]
    if unexpected:
        _fail("native mapping lifetime KAT found a foreign RTDL native image")
    return len(matching), marker


def _closed_prepared_native_dso(
    binding: dict[str, object], *, label: str,
    expected_active_lease_count: int,
) -> dict[str, object]:
    """Prove close released one lease but retained one cache image."""

    prepared = binding["prepared"]
    owner = binding["owner"]
    library = binding["library"]
    descriptor = binding["evidence"]["native_image_fd"]
    finalizer = getattr(library, "_rtdl_native_lease_abandon_finalizer", None)
    handle_after_close = getattr(library, "_handle", None)
    descriptor_after_close = getattr(library, "_rtdl_native_image_fd", None)
    released = getattr(library, "_rtdl_native_image_released", None)
    release_phase = getattr(library, "_rtdl_native_image_release_phase", None)
    release_error = getattr(library, "_rtdl_native_image_release_error", None)
    entry = getattr(library, "_rtdl_native_cache_entry", None)
    entry_handle = int(getattr(getattr(entry, "library", None), "_handle", 0))
    entry_descriptor = getattr(entry, "image_descriptor", None)
    active_lease_count = len(getattr(entry, "active_lease_ids", ()))
    if getattr(prepared, "closed", None) is not True \
            or getattr(owner, "_library", object()) is not None \
            or getattr(owner, "_release_complete", None) is not True \
            or finalizer is None \
            or getattr(finalizer, "alive", None) is not False \
            or type(handle_after_close) is not int or handle_after_close != 0 \
            or type(descriptor_after_close) is not int or descriptor_after_close != -1 \
            or released is not True or release_phase != "COMPLETE" \
            or release_error is not None \
            or entry_handle <= 0 or entry_descriptor != descriptor \
            or active_lease_count != expected_active_lease_count:
        _fail(f"{label} public close retained its prepared native owner")
    try:
        os.fstat(descriptor)
    except OSError as error:
        _fail(f"{label} process-cache descriptor was closed: {error}")
    return {
        "cache_active_lease_count_after_close": active_lease_count,
        "cache_image_fd_open_after_close": True,
        "cache_loader_handle_live_after_close": True,
        "lease_abandon_finalizer_alive_after_close": False,
        "lease_image_fd_value_after_close": descriptor_after_close,
        "lease_library_handle_after_close": handle_after_close,
        "lease_release_phase_after_close": release_phase,
        "lease_released_after_close": released,
        "owner_library_released_after_close": True,
        "owner_release_complete_after_close": True,
        "prepared_closed_after_close": True,
    }


def _run_native_mapping_lifetime_kat(
    *, relation_loaded: object, triangle_loaded: object,
    relation_static_input: object, triangle_static_input: object,
    relation_batch: object, triangle_batch: object,
    native: Path, native_sha256: str,
) -> dict[str, object]:
    """Require one warm process image with bounded, independent leases."""

    warm_count, marker = _native_mapping_count(native_sha256)
    if warm_count <= 0 or warm_count > MAX_LIVE_NATIVE_MAPPING_ROWS_PER_TWO_OWNERS:
        _fail("native mapping lifetime KAT lacks one bounded warm image")

    read_fd, write_fd = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(read_fd)
        code = "UNEXPECTED_ACCEPT"
        prepared = None
        try:
            prepared = relation_loaded.prepare(
                relation_static_input, native_library_path=native)
        except Exception as error:  # exact public fail-closed code below
            code = str(getattr(error, "code", type(error).__name__))
        finally:
            if prepared is not None:
                prepared.close()
        os.write(write_fd, code.encode("ascii", errors="replace"))
        os.close(write_fd)
        os._exit(0)
    os.close(write_fd)
    fork_code = os.read(read_fd, 4096).decode("ascii")
    os.close(read_fd)
    waited, status = os.waitpid(child, 0)
    if waited != child or status != 0 \
            or fork_code != "RX047_NATIVE_CACHE_FORK_POISONED":
        _fail("warm native cache was not poisoned in a fork child")

    rounds = []
    for round_index in range(NATIVE_MAPPING_LIFETIME_ROUNDS):
        before_count, before_marker = _native_mapping_count(native_sha256)
        if before_marker != marker or before_count != warm_count:
            _fail("native mapping lifetime KAT grew before preparation")
        relation_prepared = None
        triangle_prepared = None
        relation_binding = None
        triangle_binding = None
        try:
            relation_prepared = relation_loaded.prepare(
                relation_static_input, native_library_path=native)
            relation_binding = _bind_actual_prepared_native_dso(
                relation_prepared, label=f"lifetime[{round_index}].relation",
                expected_native_path=native,
                expected_native_sha256=native_sha256)
            triangle_prepared = triangle_loaded.prepare(
                triangle_static_input, native_library_path=native)
            triangle_binding = _bind_actual_prepared_native_dso(
                triangle_prepared, label=f"lifetime[{round_index}].triangle",
                expected_native_path=native,
                expected_native_sha256=native_sha256)
            relation_initial = relation_binding["evidence"]
            triangle_initial = triangle_binding["evidence"]
            if relation_initial["ctypes_handle"] != triangle_initial["ctypes_handle"] \
                    or relation_initial["native_image_fd"] \
                    != triangle_initial["native_image_fd"] \
                    or relation_initial["native_loader_alias"] \
                    != triangle_initial["native_loader_alias"] \
                    or relation_initial["native_cache_entry_identity"] \
                    != triangle_initial["native_cache_entry_identity"] \
                    or relation_initial["native_cache_lease_id"] \
                    == triangle_initial["native_cache_lease_id"]:
                _fail("same-digest owners did not share one image via distinct leases")
            live_count, live_marker = _native_mapping_count(native_sha256)
            if live_marker != marker or live_count != warm_count:
                _fail("native mapping lifetime KAT live mapping count is unbounded")
            relation_result = relation_prepared.execute(
                relation_batch, include_diagnostics=True)
            relation_dso = _finish_actual_prepared_native_dso(
                relation_binding, label=f"lifetime[{round_index}].relation")
            relation_prepared.close()
            relation_closed = _closed_prepared_native_dso(
                relation_binding, label=f"lifetime[{round_index}].relation",
                expected_active_lease_count=1)
            # Closing one lease must not invalidate the other family's token,
            # DSO functions, CUDA state, or output contract.
            triangle_result = triangle_prepared.execute(
                triangle_batch, include_diagnostics=True)
            triangle_dso = _finish_actual_prepared_native_dso(
                triangle_binding, label=f"lifetime[{round_index}].triangle")
        finally:
            try:
                if relation_prepared is not None:
                    relation_prepared.close()
            finally:
                if triangle_prepared is not None:
                    triangle_prepared.close()
        if relation_binding is None or triangle_binding is None:
            _fail("native mapping lifetime KAT did not bind both prepared owners")
        triangle_closed = _closed_prepared_native_dso(
            triangle_binding, label=f"lifetime[{round_index}].triangle",
            expected_active_lease_count=0)
        after_count, after_marker = _native_mapping_count(native_sha256)
        if after_marker != marker or after_count != warm_count:
            _fail("native mapping lifetime KAT changed its warm image after close")
        relation_prepared.close()
        triangle_prepared.close()
        idempotent_count, idempotent_marker = _native_mapping_count(native_sha256)
        if idempotent_marker != marker or idempotent_count != warm_count:
            _fail("idempotent public close changed native mapping lifetime")
        if relation_result.output != ((10, 100),) \
                or triangle_result.output != 7 \
                or not relation_result.device_status["ok"] \
                or not triangle_result.device_status["ok"]:
            _fail("native mapping lifetime KAT output/status failed")
        rounds.append({
            "after_close_map_count": after_count,
            "after_idempotent_close_map_count": idempotent_count,
            "before_prepare_map_count": before_count,
            "live_map_count": live_count,
            "relation_closed_state": relation_closed,
            "relation_live_dso": relation_dso,
            "relation_output": [list(row) for row in relation_result.output],
            "round_index": round_index,
            "triangle_closed_state": triangle_closed,
            "triangle_live_dso": triangle_dso,
            "triangle_output": triangle_result.output,
        })
    return {
        "fork_child_prepare_code": fork_code,
        "map_identity_marker": marker,
        "maximum_live_map_count": MAX_LIVE_NATIVE_MAPPING_ROWS_PER_TWO_OWNERS,
        "prepared_owner_count_per_round": 2,
        "round_count": NATIVE_MAPPING_LIFETIME_ROUNDS,
        "rounds": rounds,
        "schema": "rtdl.goal5801.native_mapping_lifetime_kat.v2",
        "warm_process_cache_map_count": warm_count,
    }


def _run_fast_path_operation_kat(
    *, relation_loaded: object, triangle_loaded: object,
    bounded_static_type: object, bounded_batch_type: object,
    triangle_static_type: object, triangle_batch_type: object,
    native: Path,
) -> dict[str, object]:
    """Exercise the exact Goal5802 status/output shapes without timing."""

    def receipt(result: object) -> dict[str, object]:
        value = dict(dict(result.device_status).get("operation_receipt", {}))
        if not value:
            _fail("application fast result omitted its native operation receipt")
        return value

    def receipt_hash(value: dict[str, object]) -> str:
        return hashlib.sha256(json.dumps(
            value, separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")).hexdigest()

    def verify_receipt(
        value: dict[str, object], *, family: str, reused: bool,
        success: bool, output_bytes: int,
    ) -> None:
        expected = {
            "schema": "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2",
            "optix_launch_count": 2 if family == "relation" else 1,
            "host_blocking_boundary_count": 2 if success else 1,
            "control_d2h_bytes": 16 if family == "relation" else 4,
            "output_d2h_bytes": output_bytes if success else 0,
            "status_before_output": True,
            "output_d2h_after_status_failure": 0,
            "role_counters_materialized": False,
            "prepared_input_reused": reused,
            "dynamic_device_upload_call_count": (
                0 if reused else (2 if family == "relation" else 8)),
            "dynamic_accel_build_count": (
                0 if reused or family == "triangle" else 1),
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
        mismatches = {
            key: {"expected": expected_value, "observed": value.get(key)}
            for key, expected_value in expected.items()
            if value.get(key) != expected_value
        }
        if mismatches:
            _fail(f"{family} fast operation receipt mismatch: {mismatches}")
        if type(value.get("dynamic_input_generation")) is not int \
                or int(value["dynamic_input_generation"]) <= 0:
            _fail(f"{family} fast receipt input generation is invalid")
        upload_bytes = value.get("dynamic_device_upload_bytes")
        if type(upload_bytes) is not int \
                or (upload_bytes != 0 if reused else upload_bytes <= 0):
            _fail(f"{family} fast receipt upload-byte accounting is invalid")

    relation_static = bounded_static_type(tuple(
        (0.0, 0.0, 2.0, 2.0, 10_000 + index)
        for index in range(4096)))
    relation_first_batch = bounded_batch_type((
        (0.5, 0.5, 1.5, 1.5, 10),))
    relation_changed_batch = bounded_batch_type((
        (0.5, 0.5, 1.5, 1.5, 11),))
    relation_prepared = relation_loaded.prepare(
        relation_static, native_library_path=native)
    try:
        relation_first = relation_prepared.execute(
            relation_first_batch, include_diagnostics=False)
        relation_repeat = relation_prepared.execute(
            bounded_batch_type(tuple(relation_first_batch.source_boxes)),
            include_diagnostics=False)
        relation_changed = relation_prepared.execute(
            relation_changed_batch, include_diagnostics=False)
        relation_receipts = [receipt(item) for item in (
            relation_first, relation_repeat, relation_changed)]
        for row, reused in zip(relation_receipts, (False, True, False)):
            verify_receipt(
                row, family="relation", reused=reused, success=True,
                output_bytes=32_768)
        for item, source_id in (
                (relation_first, 10), (relation_repeat, 10),
                (relation_changed, 11)):
            if len(item.output) != 4096 \
                    or item.output[0] != (source_id, 10_000) \
                    or item.output[-1] != (source_id, 14_095) \
                    or item.output_sha256 is not None \
                    or item.role_counters \
                    or item.traversal_receipt is not None \
                    or item.device_status.get("validated_raw_event_count") != 8192 \
                    or item.device_status.get("validated_unique_event_count") != 4096 \
                    or item.device_status.get(
                        "status_output_host_blocking_boundary_count") != 2:
                _fail("relation fast application output/status contract failed")
        try:
            relation_prepared.execute(
                bounded_batch_type((
                    (0.5, 0.5, 1.5, 1.5, 20),
                    (0.5, 0.5, 1.5, 1.5, 21),
                )), include_diagnostics=False)
        except Exception as error:
            relation_failure_code = str(
                getattr(error, "code", type(error).__name__))
        else:
            _fail("relation fast status-failure KAT unexpectedly succeeded")
        relation_failure_receipt = dict(
            relation_prepared._owner._last_fast_operation_receipt or {})
        verify_receipt(
            relation_failure_receipt, family="relation", reused=False,
            success=False, output_bytes=0)
    finally:
        relation_prepared.close()

    # Exercise the two cases that a raw-event cap cannot prove.  The geometry
    # is inside the indexed box but off its rising diagonal: pass 0 emits each
    # semantic pair while pass 1 does not.  Therefore K+1 unique rows produce
    # exactly K+1 raw rows (< 2*K), and only the device unique-count gate can
    # stop the application-row transfer.  UINT64_MAX simultaneously exercises
    # the hash table's reserved-sentinel path.
    max_u32 = (1 << 32) - 1
    semantic_prepared = relation_loaded.prepare(
        bounded_static_type(((0.0, 0.0, 4.0, 4.0, max_u32),)),
        native_library_path=native)
    try:
        max_key_batch = bounded_batch_type(
            ((0.25, 2.0, 1.25, 3.0, max_u32),),
            expected_rows=((max_u32, max_u32),))
        max_key_first = semantic_prepared.execute(
            max_key_batch, include_diagnostics=False)
        max_key_repeat = semantic_prepared.execute(
            bounded_batch_type(
                tuple(max_key_batch.source_boxes),
                expected_rows=((max_u32, max_u32),)),
            include_diagnostics=False)
        max_key_receipts = [receipt(max_key_first), receipt(max_key_repeat)]
        for row, reused in zip(max_key_receipts, (False, True)):
            verify_receipt(
                row, family="relation", reused=reused, success=True,
                output_bytes=8)
        if max_key_first.output != ((max_u32, max_u32),) \
                or max_key_repeat.output != ((max_u32, max_u32),):
            _fail("relation max-U64-key compaction output changed")

        semantic_capacity = 4096
        k_plus_one_sources = tuple(
            (0.25, 2.0, 1.25, 3.0, index)
            for index in range(semantic_capacity + 1))
        try:
            semantic_prepared.execute(
                bounded_batch_type(k_plus_one_sources),
                include_diagnostics=False)
        except Exception as error:
            k_plus_one_failure_code = str(
                getattr(error, "code", type(error).__name__))
        else:
            _fail("relation real K+1 semantic overflow unexpectedly succeeded")
        k_plus_one_receipt = dict(
            semantic_prepared._owner._last_fast_operation_receipt or {})
        k_plus_one_control = dict(
            semantic_prepared._owner._last_fast_compact_control or {})
        verify_receipt(
            k_plus_one_receipt, family="relation", reused=False,
            success=False, output_bytes=0)
        expected_control = {
            "schema": "rtdl.v4.rtdlexe.relation_compact_control.v1",
            "raw_event_count": semantic_capacity + 1,
            "unique_event_count": semantic_capacity + 1,
            "overflowed": 1,
            "status": 0xffff5102,
            "semantic_capacity": semantic_capacity,
            "control_d2h_bytes": 16,
        }
        if k_plus_one_control != expected_control:
            _fail(f"relation real K+1 compact control mismatch: "
                  f"{k_plus_one_control!r}")
        semantic_compaction_hostile = {
            "k_plus_one_compact_control": k_plus_one_control,
            "k_plus_one_failure_code": k_plus_one_failure_code,
            "k_plus_one_receipt": k_plus_one_receipt,
            "max_u64_key_output": [[max_u32, max_u32]],
            "max_u64_key_receipts": max_key_receipts,
            "raw_capacity": 2 * semantic_capacity,
            "raw_count_below_raw_capacity": True,
            "registered_performance_timing_count": 0,
            "same_input_reuse_clears_compaction_scratch": True,
        }
    finally:
        semantic_prepared.close()

    triangle_static = triangle_static_type(
        vertices=((-1.0, -1.0, 1.0), (1.0, -1.0, 1.0),
                  (0.0, 1.0, 1.0)),
        triangles=((0, 1, 2),), event_capacity=1)
    query = (((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
    triangle_a = triangle_batch_type(
        query, query_weights=(7,), expected_reduced_u64=7)
    triangle_b = triangle_batch_type(
        query, query_weights=(9,), expected_reduced_u64=9)
    triangle_prepared = triangle_loaded.prepare(
        triangle_static, native_library_path=native)
    try:
        triangle_first = triangle_prepared.execute(
            triangle_a, include_diagnostics=False)
        triangle_repeat = triangle_prepared.execute(
            triangle_batch_type(
                tuple(query), query_weights=(7,), expected_reduced_u64=7),
            include_diagnostics=False)
        triangle_changed = triangle_prepared.execute(
            triangle_b, include_diagnostics=False)
        triangle_receipts = [receipt(item) for item in (
            triangle_first, triangle_repeat, triangle_changed)]
        for row, reused in zip(triangle_receipts, (False, True, False)):
            verify_receipt(
                row, family="triangle", reused=reused, success=True,
                output_bytes=8)
        if [triangle_first.output, triangle_repeat.output,
                triangle_changed.output] != [7, 7, 9] \
                or any(item.output_sha256 is not None or item.role_counters
                       or item.traversal_receipt is not None
                       for item in (triangle_first, triangle_repeat,
                                    triangle_changed)):
            _fail("triangle fast application output/status contract failed")
        two_queries = query + (
            ((0.1, 0.0, 0.0), (0.0, 0.0, 1.0), 2.0),)
        try:
            triangle_prepared.execute(
                triangle_batch_type(
                    two_queries,
                    query_weights=((1 << 64) - 1, (1 << 64) - 1)),
                include_diagnostics=False)
        except Exception as error:
            triangle_failure_code = str(
                getattr(error, "code", type(error).__name__))
        else:
            _fail("triangle fast status-failure KAT unexpectedly succeeded")
        triangle_failure_receipt = dict(
            triangle_prepared._owner._last_fast_operation_receipt or {})
        verify_receipt(
            triangle_failure_receipt, family="triangle", reused=False,
            success=False, output_bytes=0)
    finally:
        triangle_prepared.close()

    relation_all_receipts = [*relation_receipts, relation_failure_receipt]
    triangle_all_receipts = [*triangle_receipts, triangle_failure_receipt]
    return {
        "registered_performance_timing_count": 0,
        "relation": {
            "failure_code": relation_failure_code,
            "output_row_count": 4096,
            "raw_event_count": 8192,
            "unique_event_count": 4096,
            "receipt_sha256": [receipt_hash(row)
                               for row in relation_all_receipts],
            "receipts": relation_all_receipts,
            "semantic_compaction_hostile": semantic_compaction_hostile,
            "success_control_d2h_bytes": 16,
            "success_output_d2h_bytes": 32_768,
            "success_total_d2h_bytes": 32_784,
        },
        "schema": "rtdl.goal5801.fast_path_operation_kat.v1",
        "triangle": {
            "failure_code": triangle_failure_code,
            "receipt_sha256": [receipt_hash(row)
                               for row in triangle_all_receipts],
            "receipts": triangle_all_receipts,
            "success_control_d2h_bytes": 4,
            "success_output_d2h_bytes": 8,
            "success_total_d2h_bytes": 12,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relation", type=Path, required=True,
                        help="JSON with deployment_id/artifact_path/authority_path")
    parser.add_argument("--triangle", type=Path, required=True,
                        help="JSON with deployment_id/artifact_path/authority_path")
    parser.add_argument("--candidate-manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--forbid-source-root", type=Path, required=True)
    parser.add_argument("--nvrtc-trap-log", type=Path, required=True)
    parser.add_argument("--nvrtc-trap-library", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if os.environ.get("PYTHONPATH"):
        _fail("clean-install proof forbids PYTHONPATH")
    source_root = args.forbid_source_root.resolve()
    if _inside(Path.cwd().resolve(), source_root):
        _fail("clean-install proof cwd is inside the source tree")
    if not args.wheel.is_file() or not args.native.is_file():
        _fail("wheel and native library must be regular files")
    if not args.nvrtc_trap_log.is_file() \
            or args.nvrtc_trap_log.stat().st_size != 0:
        _fail("NVRTC lifecycle trap must be a pre-created empty file")
    _goal5802_relation_protocol(args.candidate_manifest.resolve())
    dist = "rtdl_source_tree-4.0.0rc1.dist-info"
    allowed_dist = {
        f"{dist}/METADATA", f"{dist}/WHEEL",
        f"{dist}/top_level.txt", f"{dist}/RECORD",
    }
    with zipfile.ZipFile(args.wheel.resolve()) as wheel:
        infos = wheel.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or any(info.is_dir() for info in infos):
            _fail("wheel contains duplicate or directory members")
        for name in names:
            posix = PurePosixPath(name)
            if posix.is_absolute() or ".." in posix.parts or "." in posix.parts \
                    or name != posix.as_posix() or name.endswith(".pth") \
                    or any(part.endswith(".data") for part in posix.parts) \
                    or not (name.startswith("rtdsl/") or name in allowed_dist):
                _fail(f"wheel member is outside the public package boundary: {name}")

    # All public deployment values come from the installed top-level package.
    import rtdsl  # pylint: disable=import-outside-toplevel
    from rtdsl import (  # pylint: disable=import-outside-toplevel
        RTDLExecutableBoundedRelationBatch,
        RTDLExecutableBoundedRelationStaticInput,
        RTDLExecutableTriangleReductionBatch,
        RTDLExecutableTriangleReductionStaticInput,
        install_rtdlexe_deployment,
        load_rtdlexe,
    )

    package_file = Path(rtdsl.__file__).resolve()
    package_root = package_file.parent
    environment_root = Path(sys.prefix).resolve()
    base_environment_root = Path(sys.base_prefix).resolve()
    if environment_root == base_environment_root:
        _fail("clean-install proof requires a fresh virtual environment")
    if not _inside(package_file, environment_root) or _inside(package_file, source_root):
        _fail(f"rtdsl was not imported from the clean environment: {package_file}")
    if any(_inside(Path(item or ".").resolve(), source_root) for item in sys.path):
        _fail("source tree is present on clean-install sys.path")
    installed_rows = []
    with zipfile.ZipFile(args.wheel.resolve()) as wheel:
        package_names = sorted(name for name in wheel.namelist()
                               if name.startswith("rtdsl/")
                               and not name.endswith("/"))
        if len(package_names) != len(set(package_names)):
            _fail("wheel contains duplicate rtdsl package members")
        for name in package_names:
            relative = name.removeprefix("rtdsl/")
            installed = package_root / relative
            wheel_bytes = wheel.read(name)
            if not installed.is_file() or installed.read_bytes() != wheel_bytes:
                _fail(f"installed package byte differs from wheel: {name}")
            installed_rows.append({
                "path": name, "bytes": len(wheel_bytes),
                "sha256": hashlib.sha256(wheel_bytes).hexdigest(),
            })
    if not installed_rows:
        _fail("wheel contains no rtdsl package files")
    installed_tree_sha256 = hashlib.sha256(json.dumps(
        installed_rows, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")).hexdigest()

    relation = _load_candidate(args.relation.resolve(), "relation")
    triangle = _load_candidate(args.triangle.resolve(), "triangle")
    native = args.native.resolve()
    native_sha256 = _sha_file(native)

    def loaded(candidate: dict[str, object]):
        deployment = install_rtdlexe_deployment(
            trust_root_path=args.trust_root,
            trust_head_path=args.trust_head,
            trust_package_path=args.trust_package,
            deployment_id=str(candidate["deployment_id"]),
        )
        return load_rtdlexe(
            candidate["artifact_path"],
            authority_path=candidate["authority_path"],
            deployment=deployment,
        )

    relation_loaded = loaded(relation)
    triangle_loaded = loaded(triangle)
    relation_static_input = RTDLExecutableBoundedRelationStaticInput((
        (0.0, 0.0, 2.0, 2.0, 100),
        (3.0, 3.0, 4.0, 4.0, 101),
    ))
    triangle_static_input = RTDLExecutableTriangleReductionStaticInput(
        vertices=((-1.0, -1.0, 1.0),
                  (1.0, -1.0, 1.0),
                  (0.0, 1.0, 1.0)),
        triangles=((0, 1, 2),),
        event_capacity=1,
    )
    relation_batch = RTDLExecutableBoundedRelationBatch((
        (0.5, 0.5, 1.5, 1.5, 10),
        (10.0, 10.0, 11.0, 11.0, 11),
    ), expected_rows=((10, 100),))
    triangle_batch = RTDLExecutableTriangleReductionBatch(
        queries=(((0.0, 0.0, 0.0),
                  (0.0, 0.0, 1.0), 2.0),),
        query_weights=(7,),
        expected_reduced_u64=7,
    )
    relation_prepared = None
    triangle_prepared = None
    try:
        relation_prepared = relation_loaded.prepare(
            relation_static_input, native_library_path=native)
        relation_native_binding = _bind_actual_prepared_native_dso(
            relation_prepared, label="relation", expected_native_path=native,
            expected_native_sha256=native_sha256)
        triangle_prepared = triangle_loaded.prepare(
            triangle_static_input, native_library_path=native)
        triangle_native_binding = _bind_actual_prepared_native_dso(
            triangle_prepared, label="triangle", expected_native_path=native,
            expected_native_sha256=native_sha256)
        relation_initial = relation_native_binding["evidence"]
        triangle_initial = triangle_native_binding["evidence"]
        if relation_initial["ctypes_handle"] != triangle_initial["ctypes_handle"] \
                or relation_initial["native_image_fd"] != triangle_initial["native_image_fd"] \
                or relation_initial["native_loader_alias"] != triangle_initial["native_loader_alias"] \
                or relation_initial["native_cache_entry_identity"] \
                != triangle_initial["native_cache_entry_identity"] \
                or relation_initial["native_cache_lease_id"] \
                == triangle_initial["native_cache_lease_id"]:
            _fail("same-digest prepared owners did not share one cached image")
        relation_result = relation_prepared.execute(
            relation_batch, include_diagnostics=True)
        triangle_result = triangle_prepared.execute(
            triangle_batch, include_diagnostics=True)
        relation_native_dso = _finish_actual_prepared_native_dso(
            relation_native_binding, label="relation")
        triangle_native_dso = _finish_actual_prepared_native_dso(
            triangle_native_binding, label="triangle")
    finally:
        try:
            if relation_prepared is not None:
                relation_prepared.close()
        finally:
            if triangle_prepared is not None:
                triangle_prepared.close()

    native_mapping_lifetime_kat = _run_native_mapping_lifetime_kat(
        relation_loaded=relation_loaded,
        triangle_loaded=triangle_loaded,
        relation_static_input=relation_static_input,
        triangle_static_input=triangle_static_input,
        relation_batch=relation_batch,
        triangle_batch=triangle_batch,
        native=native,
        native_sha256=native_sha256,
    )
    fast_path_operation_kat = _run_fast_path_operation_kat(
        relation_loaded=relation_loaded,
        triangle_loaded=triangle_loaded,
        bounded_static_type=RTDLExecutableBoundedRelationStaticInput,
        bounded_batch_type=RTDLExecutableBoundedRelationBatch,
        triangle_static_type=RTDLExecutableTriangleReductionStaticInput,
        triangle_batch_type=RTDLExecutableTriangleReductionBatch,
        native=native,
    )

    trap = args.nvrtc_trap_log.read_bytes()
    if relation_result.output != ((10, 100),) \
            or triangle_result.output != 7 \
            or not relation_result.device_status["ok"] \
            or not triangle_result.device_status["ok"] \
            or trap:
        _fail("clean-install public lifecycle contract failed")

    forbidden = sorted(name for name in sys.modules if name.startswith((
        "numba", "llvmlite", "rtdsl.v4_callback_lifecycle",
    )) or (name.startswith("rtdsl.") and any(marker in name for marker in (
        "_compiler", "_codegen", "_composer", "wrapper_codegen"))))
    if forbidden:
        _fail(f"clean-install lifecycle imported compiler graph: {forbidden}")

    execution_inputs = {
        "candidate_manifest": args.candidate_manifest.resolve(),
        "relation_descriptor": args.relation.resolve(),
        "relation_artifact": Path(str(relation["artifact_path"])).resolve(),
        "relation_authority": Path(str(relation["authority_path"])).resolve(),
        "triangle_descriptor": args.triangle.resolve(),
        "triangle_artifact": Path(str(triangle["artifact_path"])).resolve(),
        "triangle_authority": Path(str(triangle["authority_path"])).resolve(),
        "trust_root": args.trust_root.resolve(),
        "trust_head": args.trust_head.resolve(),
        "trust_package": args.trust_package.resolve(),
        "native": native,
        "wheel": args.wheel.resolve(),
        "probe_source": Path(__file__).resolve(),
        "nvrtc_trap_library": args.nvrtc_trap_library.resolve(),
        "nvrtc_lifecycle_log": args.nvrtc_trap_log.resolve(),
    }
    if any(not path.is_file() or path.is_symlink()
           for path in execution_inputs.values()):
        _fail("clean-install execution input disappeared or became a symlink")

    result = {
        "schema": SCHEMA,
        "status": "PASS__CLEAN_WHEEL__TOP_LEVEL_ALIASES__TWO_FAMILY_LIFECYCLE",
        "registered_performance_timing_count": 0,
        "python_executable": str(Path(sys.executable).resolve()),
        "python_prefix": str(environment_root),
        "python_base_prefix": str(base_environment_root),
        "fresh_virtual_environment": True,
        "rtdsl_file": str(package_file),
        "source_tree_on_sys_path": False,
        "wheel_sha256": _sha_file(args.wheel.resolve()),
        "wheel_rtdsl_file_count": len(installed_rows),
        "wheel_rtdsl_tree_sha256": installed_tree_sha256,
        "native_sha256": native_sha256,
        "prepared_native_dso_evidence_boundary": {
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
        },
        "fast_path_operation_kat": fast_path_operation_kat,
        "native_mapping_lifetime_kat": native_mapping_lifetime_kat,
        "nvrtc_lifecycle_log_bytes": len(trap),
        "forbidden_compiler_modules": forbidden,
        "execution_input_sha256": {
            role: _sha_file(path) for role, path in sorted(execution_inputs.items())
        },
        "relation": {
            "actual_loaded_native_dso": relation_native_dso,
            "output": [list(row) for row in relation_result.output],
            "output_sha256": relation_result.output_sha256,
            "status_d2h_bytes": relation_result.device_status[
                "success_status_d2h_bytes"],
            "traversal_receipt": relation_result.traversal_receipt,
        },
        "triangle": {
            "actual_loaded_native_dso": triangle_native_dso,
            "output": triangle_result.output,
            "output_sha256": triangle_result.output_sha256,
            "total_product_d2h_bytes": triangle_result.device_status[
                "success_total_product_d2h_bytes"],
            "traversal_receipt": triangle_result.traversal_receipt,
        },
    }
    _create_only_json(args.output.resolve(), result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
