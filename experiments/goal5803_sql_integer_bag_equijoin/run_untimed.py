#!/usr/bin/env python3
"""Execute the frozen SQL integer-bag equijoin through public RTDL only.

This runner reads no clock.  It imports RTDL only from an isolated site that
was installed from the exact repaired-v14 successor wheel.  Neither the SQL
oracle nor any expected row is passed to ``execute``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import struct
import sys
from types import ModuleType
from typing import Mapping
import zipfile

import _sqlite3  # type: ignore[import-not-found]
import sqlite3

from .build_successor_wheel import (
    EXPECTED_REPAIRED_CORE_SHA256,
    EXPECTED_RTDSL_INIT_SHA256,
    canonical_bytes,
    sha_bytes,
    sha_file,
    wheel_rtdsl_projection,
)
from .integer_bag_equijoin import (
    DEFAULT_A,
    DEFAULT_B,
    DEFAULT_EXPECTED_PAIRS,
    MINIMUM_OVERLAP_F32,
    REUSE_A,
    REUSE_EXPECTED_PAIRS,
    build_public_inputs,
)
from .sqlite_oracle import sqlite_integer_bag_equijoin_oracle


EXPECTED_CAPACITY = 4096
EXPECTED_FAMILY = "custom_aabb_bounded_relation_v1"
EXPECTED_NATIVE_ABI = "rtdl.v4.prepared_bounded_relation_callback.v7"
EXPECTED_DYNAMIC_STATUS = "static_protocol_checked_compact_device_status_v5"
EXPECTED_MANIFEST_SHA256 = (
    "47891b4c889e45da1840288311d375a429475a73eb24da8518fde341575c5131")
EXPECTED_ARTIFACT_SHA256 = (
    "71a9a9f1b99612373f67f11dd70b613b13493776f0916ccf007a25cdc14924d6")
EXPECTED_AUTHORITY_SHA256 = (
    "08ab3773e4978bedf42ee0c0854b646534a39dba7b2a47e99a3690b85017d91c")
EXPECTED_NATIVE_SHA256 = (
    "912ad474868c72c9ba24b1ab98d005f0279c0d205abe884cca692c5e721a23bd")
EXPECTED_EXECUTABLE_IDENTITY_SHA256 = (
    "d36254612eb27776de3ee1a518011babdc8e2667d82d494feb33462b2f1c0010")
EXPECTED_DEPLOYMENT_ID = "goal5801/lx1/relation/v14"
EXPECTED_TRUST_SHA256 = {
    "root": "e2a826536871c7a254ee86dd87e5bafa85aca83d0f3c2aa6e6dafe988cd8e3dc",
    "head": "2fc6540474aaa579728f9f9b52c872913e30847ecb4b55dcde3b4f502356b706",
    "package": "c1a2c85356cc6f31df78e0b7760e97c18ba573e793008fa2fe85dec9b544c1fe",
}
EXPECTED_BED_REGRESSION_SHA256 = (
    "0c2688b1b449de9ce785ae196abb356e8e88b4624ea633899147e7868aa8cc43")
EXPECTED_WHEEL_SHA256 = (
    "174dc33936507941bbedfa51436aafc5de7e2aa4ce490bffb3596815c35c1624")
EXPECTED_WHEEL_BYTES = 1_959_508
EXPECTED_WHEEL_RECEIPT_FILE_SHA256 = (
    "b29eeeab9d1fc6c365050306b015ec0b9f98959b8f6a43527b2c94db11dff8a5")
EXPECTED_WHEEL_RECEIPT_SELF_SHA256 = (
    "3482df37178d3ed40ff0a8bb1dcb3698a7db6dfd5fb6eaeba0894aecac84424e")
EXPECTED_WHEEL_RECEIPT_SCHEMA = (
    "rtdl.goal5803.repaired_v14_exact_offline_wheel.v1")
EXPECTED_WHEEL_RECEIPT_STATUS = (
    "PASS__EXACT_SOURCE__DOUBLE_SEED_WHEEL__OFFLINE_ISOLATED_IMPORT")
EXPECTED_WHEEL_EVIDENCE_FILE_SHA256 = (
    "b2cc519d19aa601cec2deed32806affeca7feed53ee386ceebff7fb7c0d8a3e2")
EXPECTED_WHEEL_EVIDENCE_SELF_SHA256 = (
    "b2c6487279698a860ce12d10651d7e27083d72d1a4a9204449b25a6bdf8c4bb2")
EXPECTED_WHEEL_EVIDENCE_SCHEMA = (
    "rtdl.goal5803.repaired_v14_exact_offline_wheel.evidence.v1")
EXPECTED_INSTALL_RECEIPT_FILE_SHA256 = (
    "7c695794ec1f8dffcdd2d97d5ed3dd77b6fb892e592d410ecdb23a76070e8d97")
EXPECTED_INDEPENDENT_PROJECTION_FILE_SHA256 = (
    "97190bb3618db164ec0fcdec7f669d34725c3b7a522803b56e8f34de58f86c3c")
EXPECTED_INDEPENDENT_PROJECTION_SHA256 = (
    "76bb1769b231f8571000eb2849cf968dec19844a5d17d47b76bc1633bc575b8f")
EXPECTED_RTDSL_MEMBER_COUNT = 294
EXPECTED_WHEEL_REGULAR_MEMBER_COUNT = 298
EXPECTED_WHEEL_DIST_INFO_MEMBERS = (
    "rtdl_source_tree-4.0.0rc1.dist-info/METADATA",
    "rtdl_source_tree-4.0.0rc1.dist-info/RECORD",
    "rtdl_source_tree-4.0.0rc1.dist-info/WHEEL",
    "rtdl_source_tree-4.0.0rc1.dist-info/top_level.txt",
)
EXPECTED_DRIVER_LIBRARIES = (
    ("libcuda.so.580.126.09", 96284520,
     "e8e541166449da5a1278f40b27a28d072174b31f2941b101a9609b6d1d3aed32"),
    ("libnvoptix.so.580.126.09", 105212368,
     "36f9ee5a05e56e3f8522251f6e8bbd8f3c7d5414dda0699311fb2079f31c6638"),
    ("libnvidia-ptxjitcompiler.so.580.126.09", 39422584,
     "afc319751643a76395d728ea1c4471085bfe5fde02d3c6a7bc27a6b005d463c8"),
)
F32_NEXT_DOWN_FROM_ONE_BITS = 0x3F7FFFFF
F32_NEXT_DOWN_FROM_ONE = struct.unpack(
    "<f", struct.pack("<I", F32_NEXT_DOWN_FROM_ONE_BITS))[0]
CAPACITY_KAT_INDEXED_ID = 9000
CAPACITY_KAT_SOURCE_ID_BASE = 10000


def _fail(message: str) -> None:
    raise RuntimeError(message)


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


def _file_row(path: Path, *, display_path: str | None = None) -> dict[str, object]:
    path = path.resolve()
    if not path.is_file() or path.is_symlink():
        _fail(f"expected a regular file: {path}")
    return {
        "path": display_path if display_path is not None else str(path),
        "bytes": path.stat().st_size,
        "sha256": sha_file(path),
    }


def _require_file_row(path: Path, expected: Mapping[str, object]) -> dict[str, object]:
    observed = _file_row(path, display_path=str(expected["path"]))
    if observed != dict(expected):
        _fail(f"frozen file identity mismatch: {observed!r}")
    return observed


def _verify_embedded_self_seal(
    payload: Mapping[str, object], *, field: str, expected: str,
) -> str:
    observed = payload.get(field)
    if observed != expected:
        _fail(f"wrong embedded {field}: {observed!r}")
    body = dict(payload)
    body.pop(field, None)
    recomputed = sha_bytes(canonical_bytes(body))
    if recomputed != observed:
        _fail(f"embedded {field} does not reproduce: {recomputed}")
    return recomputed


def _verify_independent_wheel_receipt(
    receipt_path: Path, wheel_path: Path,
) -> dict[str, object]:
    """Verify the independent Home double-seed/offline wheel transaction."""

    receipt_identity = _file_row(receipt_path)
    if receipt_identity["sha256"] != EXPECTED_WHEEL_RECEIPT_FILE_SHA256:
        _fail("independent wheel receipt bytes differ from reviewed v3")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        _fail("independent wheel receipt is not an object")
    self_sha = _verify_embedded_self_seal(
        receipt, field="receipt_sha256",
        expected=EXPECTED_WHEEL_RECEIPT_SELF_SHA256)
    wheel = wheel_path.resolve()
    wheel_identity = _file_row(wheel)
    required_zero = (
        "gpu_kernel_launch_count", "sql_task_execution_count",
        "formal_worker_count", "registered_performance_timing_count",
        "source_native_artifact_mutation_count",
    )
    source = receipt.get("source")
    validation = receipt.get("wheel_validation")
    published = receipt.get("published_wheel")
    isolated = receipt.get("isolated_import")
    builds = receipt.get("builds")
    if receipt.get("schema") != EXPECTED_WHEEL_RECEIPT_SCHEMA \
            or receipt.get("status") != EXPECTED_WHEEL_RECEIPT_STATUS \
            or receipt.get("double_seed_byte_identical") is not True \
            or receipt.get("network_allowed") is not False \
            or receipt.get("dependency_resolution") is not False \
            or receipt.get("build_isolation") is not False \
            or any(receipt.get(name) != 0 for name in required_zero) \
            or not isinstance(source, dict) \
            or source.get("unchanged") is not True \
            or source.get("inventory_sha256_before") != source.get(
                "inventory_sha256_after") \
            or source.get("v4_rtdlexe_sha256") != EXPECTED_REPAIRED_CORE_SHA256 \
            or not isinstance(published, dict) \
            or published.get("path") != str(wheel) \
            or published.get("bytes") != EXPECTED_WHEEL_BYTES \
            or published.get("sha256") != EXPECTED_WHEEL_SHA256 \
            or wheel_identity["bytes"] != EXPECTED_WHEEL_BYTES \
            or wheel_identity["sha256"] != EXPECTED_WHEEL_SHA256 \
            or not isinstance(validation, dict) \
            or validation.get("wheel_sha256") != EXPECTED_WHEEL_SHA256 \
            or validation.get("wheel_bytes") != EXPECTED_WHEEL_BYTES \
            or validation.get("rtdlexe_sha256") != EXPECTED_REPAIRED_CORE_SHA256 \
            or validation.get("rtdsl_member_count") != EXPECTED_RTDSL_MEMBER_COUNT \
            or validation.get("rtdsl_projection_sha256") != (
                EXPECTED_INDEPENDENT_PROJECTION_SHA256) \
            or validation.get("rtdsl_projection_set_exact") is not True \
            or validation.get("rtdsl_projection_bytes_exact") is not True \
            or validation.get("record_integrity_exact") is not True \
            or not isinstance(isolated, dict) \
            or isolated.get("module_sha256") != EXPECTED_REPAIRED_CORE_SHA256 \
            or isolated.get("origin_inside_isolated_venv") is not True \
            or isolated.get("source_hash_exact") is not True \
            or isolated.get("source_tree_on_sys_path") is not False \
            or not isinstance(builds, list) or len(builds) != 2 \
            or [row.get("seed") for row in builds] != [1, 777] \
            or any(row.get("exit_code") != 0 for row in builds) \
            or any(row.get("wheel_sha256") != EXPECTED_WHEEL_SHA256
                   for row in builds):
        _fail("independent wheel receipt is not the exact reviewed v3 authority")
    return {
        "identity": receipt_identity,
        "receipt_self_sha256": self_sha,
        "source_inventory_sha256": source["inventory_sha256_before"],
        "independent_projection_sha256": validation[
            "rtdsl_projection_sha256"],
        "double_seed_byte_identical": True,
        "offline_isolated_import": True,
    }


def _verify_independent_evidence_manifest(
    manifest_path: Path, *, verify_payloads: bool = True,
) -> dict[str, object]:
    manifest_identity = _file_row(manifest_path)
    if manifest_identity["sha256"] != EXPECTED_WHEEL_EVIDENCE_FILE_SHA256:
        _fail("independent wheel evidence-manifest bytes differ from reviewed v3")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _fail("independent wheel evidence manifest is not an object")
    self_sha = _verify_embedded_self_seal(
        payload, field="manifest_sha256",
        expected=EXPECTED_WHEEL_EVIDENCE_SELF_SHA256)
    rows = payload.get("rows")
    if payload.get("schema") != EXPECTED_WHEEL_EVIDENCE_SCHEMA \
            or payload.get("file_count") != 37 \
            or payload.get("payload_bytes") != 4_145_025 \
            or not isinstance(rows, list) or len(rows) != 37:
        _fail("independent wheel evidence manifest summary drift")
    by_path: dict[str, Mapping[str, object]] = {}
    base = manifest_path.resolve().parent
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            _fail("malformed independent wheel evidence row")
        relative = Path(row["path"])
        if relative.is_absolute() or ".." in relative.parts \
                or row["path"] in by_path:
            _fail("unsafe or duplicate independent wheel evidence path")
        by_path[row["path"]] = row
        if verify_payloads:
            _require_file_row(base / relative, row)
    required = {
        "rtdl_source_tree-4.0.0rc1-py3-none-any.whl": EXPECTED_WHEEL_SHA256,
        "receipt.json": EXPECTED_WHEEL_RECEIPT_FILE_SHA256,
        "isolated_install_and_import.json": EXPECTED_INSTALL_RECEIPT_FILE_SHA256,
        "rtdsl_projection_comparison.json": (
            EXPECTED_INDEPENDENT_PROJECTION_FILE_SHA256),
    }
    if any(path not in by_path or by_path[path].get("sha256") != digest
           for path, digest in required.items()):
        _fail("independent wheel evidence manifest lacks a required exact payload")
    return {
        "identity": manifest_identity,
        "manifest_self_sha256": self_sha,
        "file_count": len(rows),
        "payload_bytes": payload["payload_bytes"],
        "all_payloads_rehashed": verify_payloads,
    }


def _verify_independent_install_receipt(
    install_receipt_path: Path, *, installed_site: Path, wheel_path: Path,
) -> dict[str, object]:
    identity = _file_row(install_receipt_path)
    if identity["sha256"] != EXPECTED_INSTALL_RECEIPT_FILE_SHA256:
        _fail("independent isolated-install receipt differs from reviewed v3")
    payload = json.loads(install_receipt_path.read_text(encoding="utf-8"))
    install = payload.get("install") if isinstance(payload, dict) else None
    probe = payload.get("import_probe") if isinstance(payload, dict) else None
    command = probe.get("command") if isinstance(probe, dict) else None
    result = probe.get("result") if isinstance(probe, dict) else None
    site = installed_site.resolve()
    wheel = wheel_path.resolve()
    expected_module = site / "rtdsl/v4_rtdlexe.py"
    expected_init = site / "rtdsl/__init__.py"
    if not isinstance(install, dict) or install.get("exit_code") != 0 \
            or not isinstance(install.get("argv"), list) \
            or str(wheel) not in install["argv"] \
            or "--no-index" not in install["argv"] \
            or "--no-deps" not in install["argv"] \
            or not isinstance(command, dict) or command.get("exit_code") != 0 \
            or not isinstance(result, dict) \
            or result.get("module_file") != str(expected_module) \
            or result.get("rtdsl_file") != str(expected_init) \
            or result.get("module_sha256") != EXPECTED_REPAIRED_CORE_SHA256 \
            or result.get("origin_inside_isolated_venv") is not True \
            or result.get("source_hash_exact") is not True \
            or result.get("source_tree_on_sys_path") is not False \
            or str(site) not in result.get("sys_path", []):
        _fail("independent isolated-install receipt does not bind this site/wheel")
    return {
        "identity": identity,
        "recorded_python": result["python"],
        "recorded_prefix": result["prefix"],
        "recorded_site": str(site),
        "module_sha256": result["module_sha256"],
        "origin_inside_isolated_venv": True,
        "source_tree_on_sys_path": False,
    }


def _verify_independent_projection(
    projection_path: Path, wheel_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    identity = _file_row(projection_path)
    if identity["sha256"] != EXPECTED_INDEPENDENT_PROJECTION_FILE_SHA256:
        _fail("independent source/wheel projection bytes drift")
    payload = json.loads(projection_path.read_text(encoding="utf-8"))
    expected_rows = [{
        "path": row["path"], "bytes": row["bytes"],
        "source_sha256": row["sha256"], "wheel_sha256": row["sha256"],
        "byte_exact": True,
    } for row in wheel_rows]
    expected_by_path = {row["path"]: row for row in expected_rows}
    recorded_rows = payload.get("rows")
    recorded_paths = tuple(
        row.get("path") if isinstance(row, dict) else None
        for row in recorded_rows) if isinstance(recorded_rows, list) else ()
    if payload.get("expected_v4_rtdlexe_sha256") != EXPECTED_REPAIRED_CORE_SHA256 \
            or payload.get("member_count") != EXPECTED_RTDSL_MEMBER_COUNT \
            or payload.get("projection_sha256") != (
                EXPECTED_INDEPENDENT_PROJECTION_SHA256) \
            or len(recorded_paths) != len(expected_by_path) \
            or len(recorded_paths) != len(set(recorded_paths)) \
            or set(recorded_paths) != set(expected_by_path) \
            or any(row != expected_by_path.get(row.get("path"))
                   for row in recorded_rows if isinstance(row, dict)) \
            or any(not isinstance(row, dict) for row in recorded_rows) \
            or sha_bytes(canonical_bytes(recorded_rows)) != (
                EXPECTED_INDEPENDENT_PROJECTION_SHA256):
        _fail("independent source/wheel projection does not reproduce from wheel")
    return {
        "identity": identity,
        "member_count": len(expected_rows),
        "projection_sha256": EXPECTED_INDEPENDENT_PROJECTION_SHA256,
        "all_source_and_wheel_bytes_identical": True,
    }


def _complete_wheel_projection(
    wheel_path: Path,
) -> tuple[dict[str, object], ...]:
    """Project every regular wheel member and reject any unowned code."""

    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(wheel_path.resolve(), "r") as archive:
        infos = archive.infolist()
        if len(infos) != len({info.filename for info in infos}):
            _fail("wheel contains duplicate member names")
        for info in sorted(infos, key=lambda item: item.filename):
            name = info.filename
            relative = Path(name)
            mode = (info.external_attr >> 16) & 0o170000
            if relative.is_absolute() or ".." in relative.parts:
                _fail("wheel contains an unsafe member path")
            if info.is_dir():
                continue
            if mode == 0o120000:
                _fail("wheel contains a symbolic-link member")
            if not name.startswith("rtdsl/") \
                    and name not in EXPECTED_WHEEL_DIST_INFO_MEMBERS:
                _fail(f"wheel contains unowned top-level member: {name}")
            payload = archive.read(info)
            rows.append({
                "path": name, "bytes": len(payload),
                "sha256": sha_bytes(payload),
            })
    if len(rows) != EXPECTED_WHEEL_REGULAR_MEMBER_COUNT \
            or sum(str(row["path"]).startswith("rtdsl/") for row in rows) != (
                EXPECTED_RTDSL_MEMBER_COUNT) \
            or tuple(row["path"] for row in rows
                     if not str(row["path"]).startswith("rtdsl/")) != (
                         EXPECTED_WHEEL_DIST_INFO_MEMBERS):
        _fail("wheel complete member set differs from exact reviewed v3")
    return tuple(rows)


def _installed_site_regular_projection(
    site: Path,
) -> tuple[dict[str, object], ...]:
    """Bind every regular installed-site byte before importing RTDL."""

    root = site.resolve()
    rows: list[dict[str, object]] = []
    forbidden_names = {
        "sitecustomize.py", "sitecustomize.pyc",
        "usercustomize.py", "usercustomize.pyc",
    }
    for path in root.rglob("*"):
        if path.is_symlink():
            _fail(f"isolated site contains a symbolic link: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.name in forbidden_names:
            _fail(f"isolated site contains startup hook: {relative}")
        if relative.startswith("rtdsl/") and path.suffix.lower() == ".pyc":
            _fail(f"isolated rtdsl install contains bytecode: {relative}")
        rows.append(_file_row(path, display_path=relative))
    return tuple(sorted(rows, key=lambda row: str(row["path"])))


def _require_isolated_interpreter_flags() -> dict[str, object]:
    flags = {
        "isolated": sys.flags.isolated,
        "no_site": sys.flags.no_site,
        "dont_write_bytecode": sys.flags.dont_write_bytecode,
        "safe_path": sys.flags.safe_path,
    }
    if flags != {
            "isolated": 1, "no_site": 1,
            "dont_write_bytecode": 1, "safe_path": True} \
            or os.environ.get("PYTHONDONTWRITEBYTECODE") != "1":
        _fail("formal runner requires -I -S -B and PYTHONDONTWRITEBYTECODE=1")
    return flags


def _verify_execution_freeze(
    project_root: Path, freeze_path: Path,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("schema") != (
            "rtdl.goal5803.sql_integer_bag_equijoin.execution_freeze.v1"):
        _fail("wrong SQL execution-freeze schema")
    if freeze.get("status") != (
            "FROZEN_BEFORE_FIRST_SQL_GPU_CALL__NO_SCIENTIFIC_RESULT_YET"):
        _fail("SQL execution bytes are not frozen before first GPU call")
    creation = freeze.get("creation_rule")
    if not isinstance(creation, dict) \
            or creation.get("create_only") is not True \
            or creation.get("existing_output_refused") is not True \
            or creation.get("reseal_or_update_allowed") is not False:
        _fail("execution freeze lacks a create-only self-governance rule")
    execution = freeze.get("execution")
    if not isinstance(execution, dict) \
            or execution.get("wheel_execution_mode") is not True \
            or execution.get("source_tree_import_allowed") is not False \
            or execution.get("private_execution_api_allowed") is not False \
            or execution.get("performance_timing_allowed") is not False:
        _fail("execution freeze does not require the public wheel lifecycle")
    from .freeze_execution import PROJECT_FILE_PATHS

    frozen_rows = freeze.get("project_files", ())
    if not isinstance(frozen_rows, list):
        _fail("execution freeze project_files is not a list")
    frozen_paths = tuple(
        row.get("path") if isinstance(row, dict) else None
        for row in frozen_rows)
    if frozen_paths != PROJECT_FILE_PATHS \
            or len(frozen_paths) != len(set(frozen_paths)):
        _fail("execution freeze project file set/order is not exact")
    observed: list[dict[str, object]] = []
    for row in frozen_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            _fail("malformed project-file freeze row")
        observed.append(_require_file_row(project_root / row["path"], row))
    return freeze, observed


def _verify_bed_regression(project_root: Path, freeze: dict[str, object]) -> dict[str, object]:
    row = freeze["bed_generic_repair_regression"]
    if not isinstance(row, dict):
        _fail("BED regression binding is malformed")
    path = project_root / str(row["path"])
    observed = _require_file_row(path, {
        "path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"],
    })
    if observed["sha256"] != EXPECTED_BED_REGRESSION_SHA256:
        _fail("wrong BED generic repair regression result")
    payload = json.loads(path.read_text(encoding="utf-8"))
    operation = payload["capacity_overflow"]["operation_receipt"]
    if payload.get("status") != "PASS__POST_CORE_CHANGE_REGRESSION" \
            or payload.get("fresh_transfer_count") != 0 \
            or payload.get("generality_exam_count_increment") != 0 \
            or payload["capacity_overflow"].get("failure_code") != (
                "RX041_OUTPUT_OVERFLOW") \
            or operation.get("status_before_output") is not True \
            or operation.get("output_d2h_bytes") != 0 \
            or operation.get("output_d2h_after_status_failure") != 0:
        _fail("BED regression no longer proves the separate generic repair")
    return {
        **observed,
        "status": payload["status"],
        "counts_only_as_generic_repair_regression": True,
        "counts_as_sql_transfer_evidence": False,
        "private_fields_were_read_in_separate_bed_regression": payload.get(
            "private_fields_read_after_public_failure_for_regression_evidence"),
        "sql_runner_repeats_private_read": False,
    }


def _verify_driver_compat(
    driver_root: Path, freeze: dict[str, object],
) -> list[dict[str, object]]:
    root = driver_root.resolve()
    frozen = freeze["driver_compatibility_bridge"]
    if str(root) != frozen.get("root"):
        _fail("driver compatibility root differs from execution freeze")
    search = tuple(
        Path(part).resolve() for part in os.environ.get("LD_LIBRARY_PATH", "").split(
            os.pathsep) if part)
    if root not in search:
        _fail("driver compatibility root is absent from LD_LIBRARY_PATH")
    observed: list[dict[str, object]] = []
    expected_rows = tuple(frozen.get("libraries", ()))
    if tuple(
            (row.get("name"), row.get("bytes"), row.get("sha256"))
            for row in expected_rows) != EXPECTED_DRIVER_LIBRARIES:
        _fail("driver compatibility freeze differs from repaired BED execution")
    for row in expected_rows:
        path = root / str(row["name"])
        actual = {
            "name": row["name"],
            "bytes": path.stat().st_size,
            "sha256": sha_file(path),
        }
        if actual != row:
            _fail(f"driver compatibility library drift: {actual!r}")
        observed.append(actual)
    return observed


def _verify_isolated_wheel_install(
    *, installed_site: Path, wheel_path: Path, freeze: dict[str, object],
) -> tuple[ModuleType, dict[str, object]]:
    site = installed_site.resolve()
    wheel = wheel_path.resolve()
    installed_freeze = freeze["isolated_installed_site"]
    if not isinstance(installed_freeze, dict) \
            or str(site) != installed_freeze.get("path"):
        _fail("isolated installed-site path differs from execution freeze")
    wheel_freeze = freeze["successor_wheel"]
    if not isinstance(wheel_freeze, dict):
        _fail("successor wheel freeze is malformed")
    if str(wheel) != wheel_freeze.get("path") \
            or wheel.stat().st_size != wheel_freeze.get("bytes") \
            or sha_file(wheel) != wheel_freeze.get("sha256"):
        _fail("successor wheel identity differs from execution freeze")
    receipt_row = wheel_freeze.get("independent_build_receipt")
    evidence_row = wheel_freeze.get("independent_evidence_manifest")
    install_row = wheel_freeze.get("independent_install_receipt")
    if not all(isinstance(row, dict) for row in (
            receipt_row, evidence_row, install_row)):
        _fail("independent wheel/build/install evidence is absent")
    receipt_path = Path(str(receipt_row["path"])).resolve()
    evidence_path = Path(str(evidence_row["path"])).resolve()
    install_path = Path(str(install_row["path"])).resolve()
    _require_file_row(receipt_path, receipt_row)
    _require_file_row(evidence_path, evidence_row)
    _require_file_row(install_path, install_row)
    independent_receipt = _verify_independent_wheel_receipt(
        receipt_path, wheel)
    independent_evidence = _verify_independent_evidence_manifest(
        evidence_path, verify_payloads=True)
    independent_install = _verify_independent_install_receipt(
        install_path, installed_site=site, wheel_path=wheel)
    wheel_rows = wheel_rtdsl_projection(wheel)
    local_projection_sha = sha_bytes(canonical_bytes(list(wheel_rows)))
    if len(wheel_rows) != EXPECTED_RTDSL_MEMBER_COUNT \
            or local_projection_sha != wheel_freeze.get(
                "installed_projection_sha256"):
        _fail("wheel rtdsl projection differs from the execution freeze")
    independent_projection = _verify_independent_projection(
        evidence_path.parent / "rtdsl_projection_comparison.json", wheel_rows)
    complete_wheel_rows = _complete_wheel_projection(wheel)
    complete_wheel_sha = sha_bytes(canonical_bytes(list(complete_wheel_rows)))
    if len(complete_wheel_rows) != wheel_freeze.get("regular_member_count") \
            or complete_wheel_sha != wheel_freeze.get(
                "complete_wheel_projection_sha256"):
        _fail("complete wheel member set differs from execution freeze")
    installed_rows: list[dict[str, object]] = []
    for row in wheel_rows:
        path = site / str(row["path"])
        installed_rows.append(_require_file_row(path, row))
    extras = []
    package_root = site / "rtdsl"
    for path in package_root.rglob("*"):
        if not path.is_file() or path.is_symlink() \
                or path.suffix == ".pyc" or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(site).as_posix()
        if path.suffix == ".py" or (
                relative.startswith("rtdsl/schemas/") and path.suffix == ".json"):
            if relative not in {str(row["path"]) for row in wheel_rows}:
                extras.append(relative)
    if extras:
        _fail(f"isolated install contains extra rtdsl members: {sorted(extras)!r}")
    installed_projection_sha = sha_bytes(canonical_bytes(installed_rows))
    if len(installed_rows) != installed_freeze.get("rtdsl_member_count") \
            or installed_projection_sha != installed_freeze.get(
                "rtdsl_projection_sha256") \
            or installed_projection_sha != local_projection_sha:
        _fail("installed rtdsl projection differs from execution freeze")
    whole_site_rows = _installed_site_regular_projection(site)
    whole_site_sha = sha_bytes(canonical_bytes(list(whole_site_rows)))
    if len(whole_site_rows) != installed_freeze.get(
            "whole_regular_file_count") \
            or whole_site_sha != installed_freeze.get(
                "whole_regular_file_projection_sha256"):
        _fail("complete isolated installed-site inventory differs from freeze")
    if any(name == "rtdsl" or name.startswith("rtdsl.") for name in sys.modules):
        _fail("rtdsl was imported before isolated wheel validation")
    sys.path.insert(0, str(site))
    module = importlib.import_module("rtdsl")
    runtime = importlib.import_module("rtdsl.v4_rtdlexe")
    module_path = Path(str(module.__file__)).resolve()
    runtime_path = Path(str(runtime.__file__)).resolve()
    if not module_path.is_relative_to(site) or not runtime_path.is_relative_to(site):
        _fail("rtdsl import escaped the isolated installed site")
    if sha_file(module_path) != EXPECTED_RTDSL_INIT_SHA256 \
            or sha_file(runtime_path) != EXPECTED_REPAIRED_CORE_SHA256:
        _fail("imported RTDL is not the repaired-v14 wheel")
    return module, {
        "wheel": _file_row(wheel),
        "independent_build_receipt": independent_receipt,
        "independent_evidence_manifest": independent_evidence,
        "independent_install_receipt": independent_install,
        "independent_source_wheel_projection": independent_projection,
        "complete_wheel_regular_member_count": len(complete_wheel_rows),
        "complete_wheel_projection_sha256": complete_wheel_sha,
        "installed_site": str(site),
        "installed_rtdsl_member_count": len(installed_rows),
        "installed_rtdsl_projection_sha256": installed_projection_sha,
        "installed_site_whole_regular_file_count": len(whole_site_rows),
        "installed_site_whole_regular_file_projection_sha256": whole_site_sha,
        "rtdsl_init_path": str(module_path),
        "rtdsl_init_sha256": sha_file(module_path),
        "rtdlexe_module_path": str(runtime_path),
        "rtdlexe_module_sha256": sha_file(runtime_path),
        "source_tree_imported": False,
        "wheel_execution_mode": True,
    }


def _verify_execution_environment(freeze: dict[str, object]) -> dict[str, object]:
    frozen = freeze["execution_environment"]
    if not isinstance(frozen, dict):
        _fail("execution environment freeze is malformed")
    interpreter_flags = _require_isolated_interpreter_flags()
    if frozen.get("interpreter_flags") != interpreter_flags:
        _fail("isolated interpreter flags differ from execution freeze")
    python_row = frozen["python"]
    python_identity = _require_file_row(
        Path(sys.executable).resolve(), python_row)
    sqlite_row = frozen["sqlite_extension"]
    sqlite_path = Path(_sqlite3.__file__).resolve()
    sqlite_identity = _require_file_row(sqlite_path, sqlite_row)
    connection = sqlite3.connect(":memory:")
    try:
        source_id = connection.execute("SELECT sqlite_source_id()").fetchone()[0]
    finally:
        connection.close()
    if sqlite3.sqlite_version != frozen.get("sqlite_version") \
            or source_id != frozen.get("sqlite_source_id"):
        _fail("SQLite oracle runtime differs from execution freeze")
    return {
        "python": python_identity,
        "python_version": sys.version,
        "interpreter_flags": interpreter_flags,
        "sqlite_extension": sqlite_identity,
        "sqlite_version": sqlite3.sqlite_version,
        "sqlite_source_id": source_id,
    }


def _verify_public_product_projection(loaded: object) -> dict[str, object]:
    """Bind the complete public application/runtime identity used by SQL."""

    projection = getattr(loaded, "product_projection", None)
    if not isinstance(projection, Mapping):
        _fail("loaded executable lacks a public product projection")
    runtime = projection.get("runtime")
    identity = projection.get("executable_identity")
    if not isinstance(runtime, Mapping) or not isinstance(identity, Mapping):
        _fail("public product projection has malformed runtime/identity")
    minimum = runtime.get("minimum_overlap_f32")
    capacity = runtime.get("capacity")
    identity_sha = sha_bytes(canonical_bytes(_plain(identity)))
    if getattr(loaded, "family", None) != EXPECTED_FAMILY \
            or getattr(loaded, "deployment_id", None) != EXPECTED_DEPLOYMENT_ID \
            or getattr(loaded, "executable_identity_sha256", None) != (
                EXPECTED_EXECUTABLE_IDENTITY_SHA256) \
            or projection.get("family") != EXPECTED_FAMILY \
            or projection.get("deployment_id") != EXPECTED_DEPLOYMENT_ID \
            or identity_sha != EXPECTED_EXECUTABLE_IDENTITY_SHA256 \
            or runtime.get("family") != EXPECTED_FAMILY \
            or runtime.get("native_abi") != EXPECTED_NATIVE_ABI \
            or runtime.get("dynamic_status") != EXPECTED_DYNAMIC_STATUS \
            or runtime.get("triangle_mode") is not None \
            or type(minimum) is not float or not math.isfinite(minimum) \
            or minimum != MINIMUM_OVERLAP_F32 \
            or type(capacity) is not int or capacity != EXPECTED_CAPACITY:
        _fail("public product/runtime projection differs from exact v14 relation")
    return {
        "projection": _plain(projection),
        "top_level_family": projection["family"],
        "top_level_deployment_id": projection["deployment_id"],
        "executable_identity_sha256": identity_sha,
        "runtime": _plain(runtime),
        "runtime_family": runtime["family"],
        "runtime_native_abi": runtime["native_abi"],
        "runtime_dynamic_status": runtime["dynamic_status"],
        "runtime_triangle_mode": None,
        "minimum_overlap_f32": minimum,
        "capacity": capacity,
        "all_required_public_fields_exact": True,
    }


def build_public_threshold_kat_inputs(module: ModuleType) -> tuple[object, object]:
    """Create a same-artifact effective-boundary KAT using public types."""

    static = module.BoundedRelationStaticInput(indexed_boxes=(
        (0.0, 0.0, 1.0, 1.0, 900),
    ))
    batch = module.BoundedRelationBatch(source_boxes=(
        (0.0, 0.0, 1.0, 1.0, 800),
        (0.0, 0.0, F32_NEXT_DOWN_FROM_ONE, 1.0, 801),
    ), expected_rows=None)
    return static, batch


def build_public_capacity_kat_inputs(
    module: ModuleType, *, source_count: int,
) -> tuple[object, object, tuple[tuple[int, int], ...]]:
    """Build a one-key public relation of exactly ``source_count`` pairs."""

    if isinstance(source_count, bool) or not isinstance(source_count, int) \
            or source_count <= 0:
        raise ValueError("capacity KAT source_count must be a positive integer")
    static = module.BoundedRelationStaticInput(indexed_boxes=(
        (0.0, 0.0, 1.0, 1.0, CAPACITY_KAT_INDEXED_ID),
    ))
    sources = tuple(
        (0.0, 0.0, 1.0, 1.0, CAPACITY_KAT_SOURCE_ID_BASE + index)
        for index in range(source_count)
    )
    batch = module.BoundedRelationBatch(
        source_boxes=sources, expected_rows=None)
    expected = tuple(
        (CAPACITY_KAT_SOURCE_ID_BASE + index, CAPACITY_KAT_INDEXED_ID)
        for index in range(source_count)
    )
    return static, batch, expected


def _execute_public_exact(
    *, prepared: object, batch: object,
    expected: tuple[tuple[int, int], ...], label: str,
    executable_identity_sha256: str = EXPECTED_EXECUTABLE_IDENTITY_SHA256,
) -> tuple[object, dict[str, object]]:
    result = prepared.execute(batch, include_diagnostics=True)
    # The result is accepted only after the public status is checked.  The
    # runner never inspects the prepared owner's private state.
    status = dict(result.device_status)
    if status.get("ok") is not True:
        _fail(f"{label} public device status is not success: {status!r}")
    receipt = dict(result.traversal_receipt or {})
    if receipt.get("physical_executor_classification") != "optix_traversal_observed":
        _fail(f"{label} lacks a public behavioral OptiX receipt")
    output = tuple(tuple(int(item) for item in row) for row in result.output)
    if output != expected:
        _fail(f"{label} output differs from the independent oracle: {output!r}")
    if not isinstance(result.output_sha256, str) \
            or len(result.output_sha256) != 64:
        _fail(f"{label} diagnostic output identity is absent")
    if result.executable_identity_sha256 != executable_identity_sha256:
        _fail(f"{label} diagnostic executable identity drift")
    return result, {
        "label": label,
        "expected_pairs": [list(row) for row in expected],
        "output_pairs": [list(row) for row in output],
        "exact": True,
        "output_sha256": result.output_sha256,
        "public_device_status": _plain(status),
        "public_traversal_receipt": _plain(receipt),
        "executable_identity_sha256": result.executable_identity_sha256,
        "include_diagnostics": True,
        "public_status_checked_before_output_acceptance": True,
        "private_prepared_state_read": False,
    }


def _execute_public_fast_exact(
    *, prepared: object, batch: object,
    expected: tuple[tuple[int, int], ...], label: str,
    executable_identity_sha256: str = EXPECTED_EXECUTABLE_IDENTITY_SHA256,
) -> tuple[object, dict[str, object]]:
    """Observe public fast-path status/transfer order before output acceptance."""

    result = prepared.execute(batch, include_diagnostics=False)
    status = dict(result.device_status)
    operation = status.get("operation_receipt")
    if status.get("ok") is not True or not isinstance(operation, Mapping):
        _fail(f"{label} fast public device status is malformed: {status!r}")
    expected_output_bytes = len(expected) * 8
    if operation.get("schema") != (
            "rtdl.v4.rtdlexe.fast_path_operation_receipt.v2") \
            or operation.get("status_before_output") is not True \
            or operation.get("output_d2h_bytes") != expected_output_bytes \
            or operation.get("output_d2h_after_status_failure") != 0:
        _fail(f"{label} fast operation receipt lacks status-before-output")
    if result.traversal_receipt is not None or result.output_sha256 is not None:
        _fail(f"{label} fast result unexpectedly materialized diagnostics")
    if result.executable_identity_sha256 != executable_identity_sha256:
        _fail(f"{label} fast executable identity drift")
    # Deliberately read/accept output only after the public status and operation
    # receipt above have been materialized and checked.
    output = tuple(tuple(int(item) for item in row) for row in result.output)
    if output != expected:
        _fail(f"{label} fast output differs from the independent oracle")
    return result, {
        "label": label,
        "expected_pairs": [list(row) for row in expected],
        "output_pairs": [list(row) for row in output],
        "exact": True,
        "output_sha256": None,
        "executable_identity_sha256": result.executable_identity_sha256,
        "public_device_status": _plain(status),
        "public_fast_operation_receipt": _plain(operation),
        "include_diagnostics": False,
        "public_status_checked_before_output_acceptance": True,
        "status_before_output": True,
        "private_prepared_state_read": False,
    }


def _execute_public_paired_exact(
    *, prepared: object, batch: object,
    expected: tuple[tuple[int, int], ...], label: str,
    executable_identity_sha256: str = EXPECTED_EXECUTABLE_IDENTITY_SHA256,
) -> tuple[object, object, dict[str, object]]:
    """Pair public fast ordering evidence with public diagnostic OptiX evidence."""

    fast_result, fast = _execute_public_fast_exact(
        prepared=prepared, batch=batch, expected=expected,
        label=f"{label}.fast",
        executable_identity_sha256=executable_identity_sha256)
    diagnostic_result, diagnostic = _execute_public_exact(
        prepared=prepared, batch=batch, expected=expected,
        label=f"{label}.diagnostic",
        executable_identity_sha256=executable_identity_sha256)
    fast_output = tuple(tuple(row) for row in fast["output_pairs"])
    diagnostic_output = tuple(tuple(row) for row in diagnostic["output_pairs"])
    if fast_output != diagnostic_output \
            or fast_result.executable_identity_sha256 != (
                diagnostic_result.executable_identity_sha256):
        _fail(f"{label} paired public observations disagree")
    return fast_result, diagnostic_result, {
        "label": label,
        "expected_pairs": [list(row) for row in expected],
        "output_pairs": [list(row) for row in fast_output],
        "exact": True,
        "executable_identity_sha256": executable_identity_sha256,
        "paired_public_observation": True,
        "paired_outputs_and_executable_identity_equal": True,
        "evidence_split_disclosed": (
            "fast public result carries operation_receipt/status-before-output; "
            "diagnostic public result carries behavioral OptiX traversal receipt; "
            "no single API result is claimed to carry both"),
        "fast_status_before_output_observation": fast,
        "diagnostic_behavioral_optix_observation": diagnostic,
        "private_prepared_state_read": False,
    }


def _execute_public_capacity_overflow(
    *, prepared: object, batch: object, executable_error_type: type[Exception],
) -> dict[str, object]:
    """Require the public K+1 failure without inspecting private state."""

    returned_result = None
    failure = None
    try:
        returned_result = prepared.execute(batch, include_diagnostics=False)
    except executable_error_type as error:
        if getattr(error, "code", None) != "RX041_OUTPUT_OVERFLOW":
            _fail(f"public K+1 failed for a non-capacity reason: {error}")
        failure = error
    if returned_result is not None:
        _fail("public K+1 capacity case returned an application result")
    if failure is None:
        _fail("public K+1 capacity case did not fail")
    return {
        "expected_unique_pair_count": EXPECTED_CAPACITY + 1,
        "public_failure_code": "RX041_OUTPUT_OVERFLOW",
        "public_failure_text": str(failure),
        "result_object_returned": False,
        "partial_application_result_published": False,
        "private_prepared_state_read": False,
        "include_diagnostics": False,
    }


def _plain_rows(rows: object) -> tuple[tuple[int, int], ...]:
    return tuple(row.as_pair() for row in rows)


def _verify_frozen_oracles() -> tuple[object, object]:
    normal = sqlite_integer_bag_equijoin_oracle(
        _plain_rows(DEFAULT_A), _plain_rows(DEFAULT_B))
    reuse = sqlite_integer_bag_equijoin_oracle(
        _plain_rows(REUSE_A), _plain_rows(DEFAULT_B))
    if normal.pairs != DEFAULT_EXPECTED_PAIRS \
            or reuse.pairs != REUSE_EXPECTED_PAIRS:
        _fail("SQLite oracle differs from frozen task semantics")
    return normal, reuse


def _require_exact_input(
    path: Path, *, expected_path: str, expected_sha256: str,
) -> dict[str, object]:
    resolved = path.resolve()
    if str(resolved) != expected_path or sha_file(resolved) != expected_sha256:
        _fail(f"executed input differs from freeze: {resolved}")
    return _file_row(resolved)


def _append_attempt_event(
    path: Path, payload: Mapping[str, object], *, create: bool,
) -> None:
    mode = "xb" if create else "ab"
    encoded = canonical_bytes(dict(payload)) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode) as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execution-freeze", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--installed-site", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--driver-compat-root", type=Path, required=True)
    parser.add_argument("--attempt-journal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for future_output in (args.attempt_journal, args.output):
        if future_output.exists() or future_output.is_symlink():
            raise FileExistsError(future_output)

    project_root = Path(__file__).resolve().parents[2]
    freeze_path = args.execution_freeze.resolve()
    freeze, project_files = _verify_execution_freeze(project_root, freeze_path)
    frozen_execution = freeze["execution"]
    if frozen_execution.get("attempt_journal_required") is not True \
            or frozen_execution.get("attempt_journal_create_only") is not True \
            or frozen_execution.get(
                "silent_retry_with_new_journal_or_output_allowed") is not False \
            or str(args.attempt_journal.resolve()) != frozen_execution.get(
                "attempt_journal_path") \
            or str(args.output.resolve()) != frozen_execution.get(
                "result_output_path"):
        _fail("attempt journal or result output differs from execution freeze")
    execution_environment = _verify_execution_environment(freeze)
    bed_regression = _verify_bed_regression(project_root, freeze)
    driver_compat = _verify_driver_compat(args.driver_compat_root, freeze)
    module, wheel_runtime = _verify_isolated_wheel_install(
        installed_site=args.installed_site,
        wheel_path=args.wheel,
        freeze=freeze,
    )

    executed = freeze["executed_inputs"]
    manifest_row = executed["manifest"]
    if manifest_row.get("sha256") != EXPECTED_MANIFEST_SHA256:
        _fail("freeze selected a non-v14 manifest")
    manifest_identity = _require_exact_input(
        args.manifest,
        expected_path=str(manifest_row["path"]),
        expected_sha256=EXPECTED_MANIFEST_SHA256,
    )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    candidate = manifest["candidates"]["relation"]
    expected_candidate = {
        "deployment_id": EXPECTED_DEPLOYMENT_ID,
        "artifact_sha256": EXPECTED_ARTIFACT_SHA256,
        "authority_sha256": EXPECTED_AUTHORITY_SHA256,
        "executable_identity_sha256": EXPECTED_EXECUTABLE_IDENTITY_SHA256,
    }
    for key, value in expected_candidate.items():
        if candidate.get(key) != value:
            _fail(f"v14 candidate drift: {key}")
    if manifest.get("native_sha256") != EXPECTED_NATIVE_SHA256:
        _fail("v14 manifest native identity drift")
    artifact = Path(candidate["artifact_path"]).resolve()
    authority = Path(candidate["authority_path"]).resolve()
    artifact_identity = _require_exact_input(
        artifact,
        expected_path=str(executed["artifact"]["path"]),
        expected_sha256=EXPECTED_ARTIFACT_SHA256,
    )
    authority_identity = _require_exact_input(
        authority,
        expected_path=str(executed["authority"]["path"]),
        expected_sha256=EXPECTED_AUTHORITY_SHA256,
    )
    native_identity = _require_exact_input(
        args.native,
        expected_path=str(executed["native"]["path"]),
        expected_sha256=EXPECTED_NATIVE_SHA256,
    )
    trust_paths = {
        "root": args.trust_root,
        "head": args.trust_head,
        "package": args.trust_package,
    }
    trust_identity: dict[str, object] = {}
    for name, path in trust_paths.items():
        row = executed["trust"][name]
        trust_identity[name] = _require_exact_input(
            path,
            expected_path=str(row["path"]),
            expected_sha256=EXPECTED_TRUST_SHA256[name],
        )

    deployment = module.install_rtdlexe_deployment(
        trust_root_path=args.trust_root,
        trust_head_path=args.trust_head,
        trust_package_path=args.trust_package,
        deployment_id=EXPECTED_DEPLOYMENT_ID,
    )
    loaded = module.load_rtdlexe(
        artifact_path=artifact,
        authority_path=authority,
        deployment=deployment,
    )
    projection_gate = _verify_public_product_projection(loaded)
    runtime = projection_gate["runtime"]
    minimum = projection_gate["minimum_overlap_f32"]
    capacity = projection_gate["capacity"]

    normal_oracle, reuse_oracle = _verify_frozen_oracles()
    normal_static, normal_batch = build_public_inputs(
        module, DEFAULT_A, DEFAULT_B)
    reuse_static, reuse_batch = build_public_inputs(
        module, REUSE_A, DEFAULT_B)
    if normal_batch.expected_rows is not None \
            or reuse_batch.expected_rows is not None \
            or normal_static.indexed_boxes != reuse_static.indexed_boxes:
        _fail("oracle leakage or prepared-static drift in SQL inputs")
    _append_attempt_event(args.attempt_journal.resolve(), {
        "schema": "rtdl.goal5803.sql_integer_bag_equijoin.attempt_event.v1",
        "event": "ATTEMPT_STARTED_BEFORE_FIRST_PREPARE_OR_GPU_EXECUTE",
        "attempt_ordinal": 1,
        "execution_freeze_path": str(freeze_path),
        "execution_freeze_sha256": sha_file(freeze_path),
        "runner_path": str(Path(__file__).resolve()),
        "runner_sha256": sha_file(Path(__file__).resolve()),
        "result_output_path": str(args.output.resolve()),
        "gpu_call_count_before_event": 0,
        "scientific_result_count_before_event": 0,
        "rerun_allowed": False,
    }, create=True)
    prepared = loaded.prepare(
        normal_static, native_library_path=args.native.resolve())
    try:
        normal_fast_result, normal_result, normal_payload = (
            _execute_public_paired_exact(
            prepared=prepared, batch=normal_batch,
            expected=normal_oracle.pairs, label="normal"))
        reuse_fast_result, reuse_result, reuse_payload = (
            _execute_public_paired_exact(
            prepared=prepared, batch=reuse_batch,
            expected=reuse_oracle.pairs, label="prepared_reuse"))
    finally:
        prepared.close()
    if prepared.closed is not True:
        _fail("public prepared SQL handle did not close")

    threshold_static, threshold_batch = build_public_threshold_kat_inputs(module)
    if threshold_batch.expected_rows is not None:
        _fail("threshold KAT received an expected row through the public input")
    threshold_prepared = loaded.prepare(
        threshold_static, native_library_path=args.native.resolve())
    try:
        threshold_result, threshold_payload = _execute_public_exact(
            prepared=threshold_prepared,
            batch=threshold_batch,
            expected=((800, 900),), label="public_threshold_kat")
    finally:
        threshold_prepared.close()
    if threshold_prepared.closed is not True:
        _fail("public threshold KAT handle did not close")

    capacity_static, capacity_batch, capacity_expected = (
        build_public_capacity_kat_inputs(
            module, source_count=EXPECTED_CAPACITY))
    if capacity_batch.expected_rows is not None:
        _fail("K capacity KAT received expected rows through the public input")
    capacity_prepared = loaded.prepare(
        capacity_static, native_library_path=args.native.resolve())
    try:
        capacity_result, capacity_payload = _execute_public_exact(
            prepared=capacity_prepared,
            batch=capacity_batch,
            expected=capacity_expected, label="public_capacity_K")
    finally:
        capacity_prepared.close()
    if capacity_prepared.closed is not True:
        _fail("public K capacity handle did not close")

    overflow_static, overflow_batch, overflow_expected = (
        build_public_capacity_kat_inputs(
            module, source_count=EXPECTED_CAPACITY + 1))
    if len(overflow_expected) != EXPECTED_CAPACITY + 1 \
            or overflow_batch.expected_rows is not None:
        _fail("K+1 capacity KAT fixture is malformed")
    # A fresh public prepared handle prevents K success state from becoming
    # the K+1 continuation.  No private owner/cache field is observed.
    overflow_prepared = loaded.prepare(
        overflow_static, native_library_path=args.native.resolve())
    try:
        overflow_payload = _execute_public_capacity_overflow(
            prepared=overflow_prepared,
            batch=overflow_batch,
            executable_error_type=module.RTDLExecutableError,
        )
    finally:
        overflow_prepared.close()
    if overflow_prepared.closed is not True:
        _fail("public K+1 capacity handle did not close")

    result_payload = {
        "schema": "rtdl.goal5803.sql_integer_bag_equijoin.untimed_result.v1",
        "status": "PASS__POST_FAILURE_PROJECT_SELECTED_SQL_APPLICATION_REUSE",
        "lineage": {
            "selected_after_bed_failure": True,
            "selected_by_project": True,
            "blind_unseen_held_out_or_unbiased_exam": False,
            "fresh_generality_exam_count_increment": 0,
            "post_failure_project_selected_successor_pass_count_increment": 1,
            "bed_failure_preserved": True,
            "bed_repair_counts_only_as_regression": True,
        },
        "claim_ceiling": {
            "allowed": (
                "one constructive application-level reuse witness for SQLite "
                "INTEGER bag equijoin semantics on the pre-existing sealed "
                "custom-AABB relation artifact"),
            "new_geometry_or_protocol_family": False,
            "unit_box_geometry_new": False,
            "broad_generalization_or_transfer_rate": False,
            "third_party_user_or_author": False,
            "usability_productivity_or_performance": False,
        },
        "execution_freeze": {
            "path": str(freeze_path),
            "bytes": freeze_path.stat().st_size,
            "sha256": sha_file(freeze_path),
            "project_files": project_files,
        },
        "attempt_journal_start_identity": _file_row(
            args.attempt_journal.resolve()),
        "wheel_runtime": wheel_runtime,
        "execution_environment": execution_environment,
        "public_product_projection": projection_gate,
        "projection_gate": {
            **{key: projection_gate[key] for key in (
                "top_level_family", "top_level_deployment_id",
                "executable_identity_sha256", "runtime_family",
                "runtime_native_abi", "runtime_dynamic_status",
                "runtime_triangle_mode", "minimum_overlap_f32", "capacity",
            )},
            "minimum_overlap_f32_exactly_one": True,
            "capacity_exactly_4096": True,
            "all_required_public_fields_exact": True,
        },
        "executed_inputs": {
            "manifest": manifest_identity,
            "artifact": artifact_identity,
            "authority": authority_identity,
            "native": native_identity,
            "trust": trust_identity,
            "driver_compatibility_bridge": {
                "root": str(args.driver_compat_root.resolve()),
                "libraries": driver_compat,
                "system_packages_installed_or_changed": False,
                "host_rebooted": False,
            },
        },
        "oracles": {
            "normal": normal_oracle.to_payload(),
            "prepared_reuse": reuse_oracle.to_payload(),
            "sqlite_and_independent_python_agree": True,
            "oracle_passed_into_execute": False,
        },
        "normal": normal_payload,
        "prepared_reuse": {
            **reuse_payload,
            "same_public_prepared_handle_as_normal": True,
            "same_sealed_indexed_B_as_normal": True,
        },
        "public_behavioral_threshold_kat": {
            **threshold_payload,
            "same_loaded_artifact_as_sql_cases": True,
            "indexed_box": [0.0, 0.0, 1.0, 1.0, 900],
            "area_exactly_one_source": [0.0, 0.0, 1.0, 1.0, 800],
            "binary32_next_down_source": [
                0.0, 0.0, F32_NEXT_DOWN_FROM_ONE, 1.0, 801],
            "binary32_next_down_bits_hex": "0x3f7fffff",
            "binary32_next_down_decimal": F32_NEXT_DOWN_FROM_ONE,
            "area_exactly_one_accepted": True,
            "binary32_next_down_area_rejected": True,
            "effective_minimum_overlap_boundary_observed": True,
        },
        "public_capacity_bracket_kat": {
            "classification": (
                "GENERIC_CONTRACT_EVIDENCE__NOT_SQL_TRANSFER_EVIDENCE"),
            "public_projection_capacity": capacity,
            "K_exact_success": {
                **capacity_payload,
                "expected_unique_pair_count": EXPECTED_CAPACITY,
                "observed_unique_pair_count": len(capacity_result.output),
                "fresh_public_prepared_handle": True,
            },
            "K_plus_one_public_failure": {
                **overflow_payload,
                "fresh_public_prepared_handle_after_K_close": True,
            },
            "private_prepared_state_read": False,
            "counts_as_sql_transfer_evidence": False,
            "registered_performance_timing_count": 0,
        },
        "separate_bed_generic_repair_evidence": bed_regression,
        "public_lifecycle": [
            "install", "load", "LoadedRTDLExecutable.product_projection",
            "prepare", "execute", "close",
        ],
        "public_prepare_call_count": 4,
        "public_execute_attempt_count": 7,
        "public_execute_success_count": 6,
        "public_execute_expected_failure_count": 1,
        "public_close_call_count": 4,
        "private_execution_api_used": False,
        "private_prepared_state_read": False,
        "handwritten_ptx_sbt_or_pipeline_used": False,
        "registered_performance_timing_count": 0,
        "formal_performance_worker_count": 0,
        "clock_read_or_timing_performed": False,
        "network_call_count": 0,
        "normal_result_identity": normal_result.output_sha256,
        "reuse_result_identity": reuse_result.output_sha256,
        "normal_fast_executable_identity": (
            normal_fast_result.executable_identity_sha256),
        "reuse_fast_executable_identity": (
            reuse_fast_result.executable_identity_sha256),
        "threshold_result_identity": threshold_result.output_sha256,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(
            json.dumps(result_payload, indent=2, sort_keys=True).encode("utf-8")
            + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    _append_attempt_event(args.attempt_journal.resolve(), {
        "schema": "rtdl.goal5803.sql_integer_bag_equijoin.attempt_event.v1",
        "event": "ATTEMPT_COMPLETED_WITH_CREATE_ONLY_RESULT",
        "attempt_ordinal": 1,
        "result_output_path": str(args.output.resolve()),
        "result_output_bytes": args.output.stat().st_size,
        "result_output_sha256": sha_file(args.output),
        "status": result_payload["status"],
        "rerun_allowed": False,
    }, create=False)
    print(json.dumps(result_payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "EXPECTED_CAPACITY",
    "F32_NEXT_DOWN_FROM_ONE",
    "F32_NEXT_DOWN_FROM_ONE_BITS",
    "build_public_capacity_kat_inputs",
    "build_public_threshold_kat_inputs",
]
