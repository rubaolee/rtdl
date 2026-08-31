#!/usr/bin/env python3
"""Execute the Goal5752 typed CuPy/Numba prepared-lifecycle validation."""

from __future__ import annotations

import argparse
import ctypes
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import shutil

from rtdsl.v4_callback_artifact_cache import _key_from_dict
from rtdsl.v4_callback_frontend import compile_callback_source
from rtdsl.v4_callback_partner_runtime import (
    V4PartnerContractError,
    prepare_v4_partner_session,
)
from tests.goal5750_v4_callback_ir_test import manifest
from tests.goal5751_v4_optix_wrapper_codegen_test import FORMAL_SOURCE

from goal5751_formal_device_validation import _cpu_reference


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _provider_key(provider_root: Path):
    directories = sorted(
        item for item in provider_root.iterdir() if item.is_dir() and not item.is_symlink())
    if len(directories) != 1:
        raise RuntimeError("Goal5752 requires exactly one Goal5751 provider directory")
    manifest_path = directories[0] / "artifact.json"
    artifact = json.loads(manifest_path.read_text(encoding="utf-8"))
    return _key_from_dict(artifact["provider_key"]), artifact


def _execution_row(result) -> dict[str, object]:
    return {
        "partner": result.partner,
        "execution_index": result.execution_index,
        "prepared_session_identity": result.prepared_session_identity,
        "output_ids": list(result.output_ids),
        "output_distance": list(result.output_distance),
        "valid_hit_mask": list(result.valid_hit_mask),
        "masked_distance": list(result.masked_distance),
        "valid_hit_count": result.valid_hit_count,
        "role_counters": list(result.role_counters),
        "launch_status": list(result.launch_status),
        "traversal_receipt": dict(result.traversal_receipt),
        "buffer_receipt": dict(result.buffer_receipt),
        "output_sha256": result.output_sha256,
        "lifecycle_contract": dict(result.lifecycle_contract),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal5751-output", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    provider_root = args.goal5751_output / "PROVIDER_CACHE"
    provider_key, provider_manifest = _provider_key(provider_root)
    goal5751 = json.loads((args.goal5751_output / "RESULT.json").read_text())
    native_path = Path(os.environ["RTDL_OPTIX_LIB"]).resolve()
    source_archive = args.source_archive.resolve()
    if not source_archive.is_file():
        raise RuntimeError("Goal5752 exact source archive is unavailable")
    if _sha256(native_path) != provider_key.native_provider_sha256:
        raise RuntimeError("Goal5752 native differs from the exact Goal5751 provider key")

    verified = compile_callback_source(FORMAL_SOURCE, manifest())
    if verified.ir_sha256 != provider_key.callback_ir_sha256:
        raise RuntimeError("Goal5752 Callback IR differs from the cached provider")
    semantic_digest = hashlib.sha256(json.dumps({
        "callback_ir_sha256": goal5751["callback_ir_sha256"],
        "callback_abi_sha256": goal5751["callback_abi_sha256"],
        "composed_ptx_sha256": goal5751["composed_ptx_sha256"],
        "proof_sha256": goal5751["any_hit_proof_sha256"],
    }, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    spheres = (
        ((5.0, 0.0, 0.0), 1.0, 9),
        ((5.0, 0.0, 0.0), 1.0, 3),
        ((8.0, 0.0, 0.0), 1.0, 5),
    )
    query_batches = (
        (
            ((0.0, 0.0, 0.0), 100.0),
            ((0.0, 4.0, 0.0), 100.0),
        ),
        (
            ((0.0, 0.0, 0.0), 3.0),
            ((10.0, 0.0, 0.0), 100.0),
            ((4.0, 0.0, 0.0), 100.0),
        ),
    )
    expected = tuple(_cpu_reference(verified, spheres, batch)[0]
                     for batch in query_batches)
    rows = []
    session = prepare_v4_partner_session(
        provider_root, provider_key, spheres=spheres,
        semantic_digest=semantic_digest,
    )
    prepared_identity = session.session_identity
    native_token = session._token
    native_destroy = session._destroy
    try:
        for partner in ("cupy", "numba"):
            for batch_index, batch in enumerate(query_batches):
                result = (
                    session.execute_cupy(batch, expected_output=expected[batch_index])
                    if partner == "cupy"
                    else session.execute_numba(batch, expected_output=expected[batch_index])
                )
                row = _execution_row(result)
                row["query_batch_index"] = batch_index
                row["cpu_expected"] = [list(item) for item in expected[batch_index]]
                rows.append(row)
                raw = args.output / "RAW"
                raw.mkdir(exist_ok=True)
                (raw / f"{result.execution_index:02d}_{partner}_batch{batch_index}.json").write_text(
                    json.dumps(row, indent=2, sort_keys=True) + "\n")
        if session.execution_count != 4:
            raise RuntimeError("prepared session did not execute exactly four launches")
    finally:
        session.close()
    use_after_close_failed = False
    try:
        session.execute_cupy(query_batches[0], expected_output=expected[0])
    except V4PartnerContractError as error:
        use_after_close_failed = error.code == "session_closed"
    if not use_after_close_failed:
        raise RuntimeError("prepared session use-after-close did not fail closed")

    def _destroy_must_fail_closed(token: int) -> str:
        error = ctypes.create_string_buffer(16384)
        status = int(native_destroy(token, error, len(error)))
        message = error.value.decode("utf-8", errors="replace")
        if status == 0 or not message:
            raise RuntimeError("invalid prepared token was accepted by native destroy")
        return message

    native_double_destroy_error = _destroy_must_fail_closed(native_token)
    native_forged_token_error = _destroy_must_fail_closed(native_token ^ (1 << 63))

    if {row["partner"] for row in rows} != {"cupy", "numba"}:
        raise RuntimeError("both closed partner lanes were not executed")
    if any(row["prepared_session_identity"] != prepared_identity for row in rows):
        raise RuntimeError("partner executions did not share one prepared owner")
    if any(row["output_ids"] != [item[0] for item in row["cpu_expected"]]
           for row in rows):
        raise RuntimeError("partner execution output IDs disagree with CPU semantics")
    if any(row["traversal_receipt"]["physical_executor_classification"] !=
           "optix_traversal_observed" for row in rows):
        raise RuntimeError("partner execution lacks behavioral OptiX traversal")
    if any(row["buffer_receipt"]["native_boundary_host_staging"] for row in rows):
        raise RuntimeError("partner native boundary performed a host stage")
    if any(not row["buffer_receipt"]["same_device_pointer_passed_to_native_and_partner"]
           for row in rows):
        raise RuntimeError("partner continuation did not consume native output pointers")

    shutil.copy2(native_path, args.output / "librtdl_optix.so")
    shutil.copy2(source_archive, args.output / "EXECUTION_SOURCE.tar.gz")
    shutil.copy2(provider_root / provider_key.key_sha256 / "artifact.json",
                 args.output / "PROVIDER_ARTIFACT.json")
    shutil.copy2(provider_root / provider_key.key_sha256 / "composed.ptx",
                 args.output / "COMPOSED_FORMAL_CALLBACK.ptx")
    result = {
        "schema": "rtdl.goal5752.partner_lifecycle_validation.v1",
        "goal5751_result_sha256": _sha256(args.goal5751_output / "RESULT.json"),
        "provider_identity": provider_key.provider_identity,
        "provider_key_sha256": provider_key.key_sha256,
        "provider_artifact_manifest_sha256": hashlib.sha256(json.dumps(
            provider_manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
        "callback_ir_sha256": verified.ir_sha256,
        "semantic_digest": semantic_digest,
        "composed_ptx_sha256": goal5751["composed_ptx_sha256"],
        "native_library_sha256": _sha256(native_path),
        "execution_source_archive_sha256": _sha256(source_archive),
        "prepared_session_identity": prepared_identity,
        "prepare_count": 1,
        "execute_count": 4,
        "distinct_query_batch_count": 2,
        "partners": ["cupy", "numba"],
        "execution_rows": rows,
        "use_after_close_failed_closed": use_after_close_failed,
        "native_double_destroy_failed_closed": True,
        "native_double_destroy_error": native_double_destroy_error,
        "native_forged_token_failed_closed": True,
        "native_forged_token_error": native_forged_token_error,
        "claims": {
            "typed_cuda_array_interface_validated": True,
            "same_explicit_nondefault_stream_per_execution": True,
            "native_boundary_zero_host_staging_observed": True,
            "same_device_output_pointer_consumed_by_partner": True,
            "one_prepared_owner_reused_across_distinct_query_batches_and_partners": True,
            "native_token_registry_rejects_double_destroy_and_forged_token": True,
            "four_of_four_cpu_device_partner_exact": True,
            "four_of_four_behavioral_optix": True,
            "performance_claimed": False,
            "prepared_may_replace_cold": False,
            "application_claimed": False,
        },
    }
    (args.output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    manifest_rows = []
    for path in sorted(item for item in args.output.rglob("*") if item.is_file()):
        manifest_rows.append({
            "path": path.relative_to(args.output).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })
    (args.output / "MANIFEST.json").write_text(json.dumps({
        "schema": "rtdl.goal5752.partner_lifecycle_manifest.v1",
        "payload_count": len(manifest_rows),
        "payload_bytes": sum(item["size_bytes"] for item in manifest_rows),
        "payloads": manifest_rows,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
