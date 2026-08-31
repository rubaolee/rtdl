#!/usr/bin/env python3
"""Build and CPU-qualify Goal5790-A1 verification-source successor v4.

The immutable, actually executed Goal5790-A1 portable source v3 is the sole
base.  This append-only successor changes postrun verification bytes only: the
independent recount, its real-ABI regressions, this builder, and the preserved
s3 validator-failure lineage.  It does not replace or relabel the executed v3
source, controller, or workers.  The builder rehashes the v3 non-self manifest,
rejects recognized nested-container and executable/device-binary magic across
the complete successor projection, emits a deterministic source/twin pair,
extracts one copy into a new empty temporary directory, rehashes every member,
and runs the exact CPU-only A1 test set.

It never builds or ships a native, contacts Home, runs a GPU, registers a
performance timing, or authorizes a POD.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
from typing import Mapping


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = (
    ROOT / "history/internal_docs/goal5790_a1_portable_source_v3_20260816.tar.gz"
)
EXPECTED_BASE_SOURCE_SHA256 = (
    "091035a87884f8e48d1da068cfa196d238e92df364323d6253b427472ab1fa69"
)
OLD_SOURCE_MANIFEST = (
    "history/internal_docs/goal5790_a1_portable_source_manifest_v3_20260816.json"
)
NEW_SOURCE_MANIFEST = (
    "history/internal_docs/"
    "goal5790_a1_portable_source_manifest_v4_20260816.json"
)
REMOVED_NESTED_EVIDENCE = (
    "history/internal_docs/"
    "goal5753_held_out_particle_tracking_exam_evidence_20260811.tar.gz"
)
EXPECTED_REMOVED_NESTED_EVIDENCE_SHA256 = (
    "6cb96787812f5f5868af3399abbe019400f591d63bb9d587d2e626b2ff988761"
)
REMOVED_NESTED_ELF_MEMBER = (
    "goal5753/history/internal_docs/"
    "goal5752_home_partner_lifecycle_v4_20260811/librtdl_optix.so"
)
EXPECTED_REMOVED_NESTED_ELF_SHA256 = (
    "d790104ee042967d5e5dc73c4ddcf4f1af312170e7f701ff3a779bbb092e1154"
)
EXPECTED_REMOVED_NESTED_ELF_SIZE = 6_029_024

# Every non-builder overlay is frozen by exact byte identity.  The builder is
# also included in the output, but cannot list its own expected hash without a
# self-reference.  Its exact bytes are instead bound by the non-self source
# manifest and by the create-only receipt outside the source archive.
EXPECTED_OVERLAY_SHA256: Mapping[str, str] = {
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/independent_oracle.py": (
        "8fee67b7dcc34987e3ddf3947f6a6570f0267cfd7bbd3177d476a0478d37d6a2"
    ),
    "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py": (
        "0823fdf32e0ade592eebc577b1f43d5c81e4fb1134934f353bbd3e3586a3b0b1"
    ),
    "src/rtdsl/v4_semantic_physical_admission.py": (
        "eb8a4a33352b94ad18d95cabe1e9c89389427b09a2bf98dbae3028d8fa940267"
    ),
    "src/rtdsl/v4_semantically_admitted_compiler.py": (
        "e9dc82c883deaf5c2ca63fec29486bc844e7b2e9c9906af6cba853489c72caa0"
    ),
    "src/rtdsl/v4_builtin_triangle_standard_library.py": (
        "77c483f4bb4bdcc7900f4fc96e85d99db21274b87da639ba3d4a3aae788de4c5"
    ),
    "src/rtdsl/v4_triangle_standard_library.py": (
        "0855481f7737f8afe26eec2b86ce36a1a9708d8a0417afb483634c428d542359"
    ),
    "scripts/goal5790_a1_rejected_encoding_cases.py": (
        "2f49131ab6a6baa4358e1cb6afce886ef05ac991e6b4ef57ef3dad945501a55a"
    ),
    "scripts/goal5790_a1_home_worker.py": (
        "81e6cadb79b6b181acc0402ab12e9b2fa86fef35f31a57dcf58477972ea03a0a"
    ),
    "scripts/goal5790_a1_home_controller.py": (
        "60095c773a9827f4189cc854c632d6f7c18fe5cf5724e2f579602a7f54cec2ba"
    ),
    "scripts/goal5790_a1_independent_recount.py": (
        "dbc31d85c448e2a8db88ffcb7bdcb20bcb18da0d3f5d253fd27652d78a76e169"
    ),
    "scripts/goal5790_a1_build_evidence.py": (
        "77b47242aede68c9746d1e4a1782556d5e199a482cbcd6992155a1ced1e41f8b"
    ),
    "tests/goal5790_a1_semantic_physical_admission_test.py": (
        "2d577645f10a11b6af65df0dd4b37d71a49557ca2e4a4d047d709202805970e5"
    ),
    "tests/goal5790_a1_semantically_admitted_compiler_test.py": (
        "f11d5488431c61e39cb283e59bff0bf283f5e2a5e332a91ecd678e50f2cf3c0e"
    ),
    "tests/goal5790_a1_rejected_encoding_cases_test.py": (
        "c86392ae9a67a349bee798daee7a331eeae66c1399d47e94f078c0dbc7bd8529"
    ),
    "tests/goal5790_a1_home_worker_test.py": (
        "6508fad2e727071e73b8b6eb24b90cb0895f08aed3a111b80063b2fa27984800"
    ),
    "tests/goal5790_a1_recount_test.py": (
        "0ca9153ebfdd9443c5ac5c823a338e3b2b356832ec87c6100650176d663caa26"
    ),
    "history/internal_docs/goal5790_a1_rejected_program_suite_plan_20260816.md": (
        "66123ebf1d1b3a6c61b77ac89c2ada61dcb730c6291cd195d5fc2ed11b57ce37"
    ),
    "history/internal_docs/"
    "goal5790_a1_amendment_a1_particle_earliest_product_gate_20260816.md": (
        "84872fdb24f5d398644ec421b55a8a53c7f6cc19af4860ac4ad10f440d958625"
    ),
    "history/internal_docs/goal5790_frozen_home_machine_authority_20260816.json": (
        "bcfd6a99766621d474dc45aa1b8c896df725575fd1131b64471b5d3d75316314"
    ),
    "history/internal_docs/"
    "goal5783_home_functional_result_20260814/"
    "GOAL5783_FUNCTIONAL_RECEIPT.json": (
        "1f490e072476c43c3807ace165859e217133afcfc8caee601ba8d8f8d960235b"
    ),
    "history/internal_docs/"
    "goal5790_a1_portable_source_v1_build_receipt_20260816.json": (
        "94a134fc4d82403ea109d7076b8184fca17fec06bf1e3238e5d7f55ed24369de"
    ),
    "history/internal_docs/"
    "goal5790_a1_portable_source_v2_build_receipt_20260816.json": (
        "f7ef7a929b787c1fbc4f94e3e3bc7b588207335a09e2e6af068945431972761a"
    ),
    "history/internal_docs/"
    "goal5790_a1_portable_source_v3_build_receipt_20260816.json": (
        "189b33cd48941f235ce88c7dc46acdee579c90cd4ad06c34f5132c703f9307fe"
    ),
    "history/internal_docs/"
    "goal5790_a1_v3_s3_postrun_validator_failure_result_20260816.json": (
        "7ea28e154cd5bfdfa60fa97382c3e72559fa3b2271bbc199a54fe73fef487009"
    ),
    "history/internal_docs/"
    "goal5790_a1_v3_s3_postrun_validator_failure_report_20260816.md": (
        "48411736c45585f9f58b27e323f194c569e975f739a8fb5efcd439fa0d788a65"
    ),
    "history/internal_docs/"
    "goal5790_a1_real_native_snapshot_fixture_20260816.json": (
        "761a6a7b763ffa85198de48df43da733b97d61d8e6c3ba8b260af3dad0e2008b"
    ),
    "history/internal_docs/"
    "goal5790_a1_v1_home_s1_zero_worker_failure_result_20260816.json": (
        "f9d66d4240e0e93abd654a57310a32bcac548f156ed80bf9299344d047b96a41"
    ),
    "history/internal_docs/"
    "goal5790_a1_v1_home_s1_zero_worker_failure_report_20260816.md": (
        "e4d674d49feaf9c9c868b009a723d40f4e19490b9119bcabf62a2c7dda0262a3"
    ),
    "history/internal_docs/goal5790_a1_v1_zero_worker_failure_evidence_20260816/"
    "CPU_SUITE.json": (
        "97e17cee8794a6595e61ee48be4c8a26ee2da6aba29f8955d7b945e6aef65646"
    ),
    "history/internal_docs/goal5790_a1_v1_zero_worker_failure_evidence_20260816/"
    "HOME_EXECUTION_SPEC.json": (
        "f3d3c23c3258f3423a3b015f68c24046b64ed273214c6dd1d12448ebe6ade6ef"
    ),
    "history/internal_docs/goal5790_a1_v1_zero_worker_failure_evidence_20260816/"
    "PRE_RUN_RECEIPT.json": (
        "cb97612f9f3f66556a6629bbadf39fc9c05fdc3a52fd0689340934a5e57d4ae8"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_home_s2_partial_worker_failure_result_20260816.json": (
        "61527569743c17226d2be27298a407357ff51324b96b74b594f18747be7bf5d4"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_home_s2_partial_worker_failure_report_20260816.md": (
        "dd32d98c8c19f560e33201db108053314ea89a0f5ba12655ecac4ee29554c6a4"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_s2_partial_worker_failure_evidence_20260816/"
    "CPU_SUITE.json": (
        "97e17cee8794a6595e61ee48be4c8a26ee2da6aba29f8955d7b945e6aef65646"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_s2_partial_worker_failure_evidence_20260816/"
    "HOME_EXECUTION_SPEC.json": (
        "f905e7f4a39c22bdfc32850599bfa825ed09d674860faba56538b98210543585"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_s2_partial_worker_failure_evidence_20260816/"
    "PRE_RUN_RECEIPT.json": (
        "e95c91c4e3e9f0deaa06edbf4ff8f09307da23783533ed6f1c92214b732e389e"
    ),
    "history/internal_docs/"
    "goal5790_a1_v2_s2_partial_worker_failure_evidence_20260816/"
    "product_admission_reject.json": (
        "9fcc898ee6f3a12ed7f5a2e4563b5b66414764f7eddd5514170cfdc03b4a203d"
    ),
}
BUILDER_MEMBER = "scripts/goal5790_a1_build_portable_source.py"

CPU_TEST_MODULES = (
    "tests.goal5790_a1_semantic_physical_admission_test",
    "tests.goal5790_a1_semantically_admitted_compiler_test",
    "tests.goal5790_a1_rejected_encoding_cases_test",
    "tests.goal5790_a1_home_worker_test",
    "tests.goal5790_a1_recount_test",
)
EXPECTED_CPU_TEST_COUNT = 95

_FORBIDDEN_PARTS = frozenset((".codex", ".git", "__pycache__", "build"))
_FORBIDDEN_SUFFIXES = (
    ".pyc", ".pyo", ".so", ".dll", ".dylib", ".pyd", ".cubin",
    ".ptx", ".o", ".obj", ".a", ".lib", ".exe",
)
_NESTED_CONTAINER_SUFFIXES = (
    ".tar.gz", ".tgz", ".tar", ".zip", ".7z", ".rar", ".gz",
    ".bz2", ".xz",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_rows(payloads: Mapping[str, bytes]) -> list[dict[str, object]]:
    return [
        {"path": name, "size_bytes": len(data), "sha256": _sha(data)}
        for name, data in sorted(payloads.items())
    ]


def _tree_sha(rows: list[dict[str, object]]) -> str:
    return _sha(json.dumps(
        rows, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))


def _normalized_member(name: str) -> str:
    pure = PurePosixPath(name)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    normalized = "/".join(parts)
    if not parts or pure.is_absolute() or ".." in parts:
        raise RuntimeError(f"unsafe archive member: {name!r}")
    if normalized != name.rstrip("/"):
        raise RuntimeError(f"non-canonical archive member: {name!r}")
    if any(part in _FORBIDDEN_PARTS for part in parts):
        raise RuntimeError(f"private/cache archive member: {name!r}")
    if normalized.lower().endswith(_FORBIDDEN_SUFFIXES):
        raise RuntimeError(f"prebuilt/binary archive member: {name!r}")
    return normalized


def _read_regular_archive(data: bytes) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {}
    casefold_names: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = _normalized_member(member.name)
            if name in payloads:
                raise RuntimeError(f"duplicate archive member: {name}")
            folded = name.casefold()
            if folded in casefold_names:
                raise RuntimeError(f"case-colliding archive member: {name}")
            casefold_names.add(folded)
            if member.isdir():
                continue
            if not member.isfile() or member.issym() or member.islnk():
                raise RuntimeError(f"unsupported archive member: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(f"unreadable archive member: {name}")
            payloads[name] = stream.read()
    return payloads


def _recognized_blob_kind(data: bytes) -> str | None:
    """Identify container/native blobs even when a misleading suffix is used."""

    signatures = (
        (b"\x7fELF", "ELF"),
        (b"MZ", "PE"),
        (b"!<arch>\n", "AR"),
        (b"\x1f\x8b", "GZIP"),
        (b"PK\x03\x04", "ZIP"),
        (b"PK\x05\x06", "ZIP_EMPTY"),
        (b"PK\x07\x08", "ZIP_SPANNED"),
        (b"BZh", "BZIP2"),
        (b"\xfd7zXZ\x00", "XZ"),
        (b"P\xedU\xba", "CUDA_FATBIN_V1"),
        (b"\xb1CbF", "CUDA_FATBIN_V2"),
    )
    for signature, kind in signatures:
        if data.startswith(signature):
            return kind
    if len(data) >= 262 and data[257:262] == b"ustar":
        return "TAR"
    return None


def _verify_removed_nested_evidence(data: bytes) -> dict[str, object]:
    """Pin the exact inherited container and the ELF that made v1 ineligible."""

    if _sha(data) != EXPECTED_REMOVED_NESTED_EVIDENCE_SHA256:
        raise RuntimeError("Goal5753 nested evidence bytes drifted")
    if _recognized_blob_kind(data) != "GZIP":
        raise RuntimeError("Goal5753 nested evidence is not the pinned gzip")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        try:
            member = archive.getmember(REMOVED_NESTED_ELF_MEMBER)
        except KeyError as exc:
            raise RuntimeError("pinned nested Goal5753 ELF is absent") from exc
        if not member.isfile() or member.issym() or member.islnk() \
                or member.size != EXPECTED_REMOVED_NESTED_ELF_SIZE:
            raise RuntimeError("pinned nested Goal5753 ELF metadata drifted")
        stream = archive.extractfile(member)
        if stream is None:
            raise RuntimeError("pinned nested Goal5753 ELF is unreadable")
        nested_elf = stream.read()
    if _sha(nested_elf) != EXPECTED_REMOVED_NESTED_ELF_SHA256 \
            or _recognized_blob_kind(nested_elf) != "ELF":
        raise RuntimeError("pinned nested Goal5753 ELF bytes drifted")
    return {
        "removed_member": REMOVED_NESTED_EVIDENCE,
        "removed_member_sha256": EXPECTED_REMOVED_NESTED_EVIDENCE_SHA256,
        "nested_elf_member": REMOVED_NESTED_ELF_MEMBER,
        "nested_elf_size_bytes": EXPECTED_REMOVED_NESTED_ELF_SIZE,
        "nested_elf_sha256": EXPECTED_REMOVED_NESTED_ELF_SHA256,
        "nested_elf_magic": "ELF",
        "removal_reason": "unrelated evidence container with prebuilt native",
    }


def _deep_successor_blob_audit(
    payloads: Mapping[str, bytes],
) -> dict[str, object]:
    """Make the nested-container/native count a complete projection audit."""

    for name, data in payloads.items():
        lower = name.lower()
        if lower.endswith(_NESTED_CONTAINER_SUFFIXES):
            raise RuntimeError(f"nested source container remains: {name}")
        kind = _recognized_blob_kind(data)
        if kind is not None:
            raise RuntimeError(f"recognized source blob remains: {name}: {kind}")
    return {
        "all_successor_payload_bytes_scanned": True,
        "scanned_payload_count": len(payloads),
        "recognized_nested_container_suffix_count": 0,
        "recognized_container_magic_count": 0,
        "recognized_executable_or_device_binary_magic_count": 0,
        "maximum_nested_container_depth": 0,
    }


def _verify_base_manifest(payloads: Mapping[str, bytes]) -> dict[str, object]:
    try:
        manifest_bytes = payloads[OLD_SOURCE_MANIFEST]
    except KeyError as exc:
        raise RuntimeError("Goal5790-A1 v3 base source manifest is absent") from exc
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema") \
            != "rtdl.goal5790_a1.portable_source_manifest.v3":
        raise RuntimeError("Goal5790-A1 v3 base source manifest schema drift")
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("Goal5790 v8 base manifest has no file rows")
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    actual = {
        name: (len(data), _sha(data))
        for name, data in payloads.items()
        if name != OLD_SOURCE_MANIFEST
    }
    if len(rows) != len(expected) \
            or expected != actual \
            or int(manifest.get("file_count_excluding_this_manifest", -1)) \
                != len(actual):
        raise RuntimeError("Goal5790-A1 v3 base source manifest does not rehash")
    if str(manifest.get("source_tree_sha256")) != _tree_sha(_canonical_rows({
        name: data for name, data in payloads.items()
        if name != OLD_SOURCE_MANIFEST
    })):
        raise RuntimeError(
            "Goal5790-A1 v3 base source tree identity does not rehash")
    return manifest


def _deterministic_archive(payloads: Mapping[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _extract_empty(payloads: Mapping[str, bytes], destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    for name, data in sorted(payloads.items()):
        path = destination.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def _write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def _receipt_path(path: Path) -> str:
    # The Windows workspace's history directory may be a junction into the
    # durable D: tree, so Path.resolve() is not a sound lexical-root test here.
    # Preserve the caller's relative create-only path when one was supplied.
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _run_cpu_tests(extracted_root: Path) -> dict[str, object]:
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": str(extracted_root / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "CUDA_VISIBLE_DEVICES": "-1",
        "NUMBA_DISABLE_CUDA": "1",
    })
    command = [
        sys.executable, "-m", "unittest", *CPU_TEST_MODULES, "-q",
    ]
    completed = subprocess.run(
        command,
        cwd=extracted_root,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=300,
        check=False,
    )
    combined = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(
            "Goal5790-A1 extracted CPU tests failed:\n" + combined[-12000:]
        )
    marker = f"Ran {EXPECTED_CPU_TEST_COUNT} tests"
    if marker not in combined:
        raise RuntimeError(
            f"Goal5790-A1 extracted test count drifted; expected {marker!r}:\n"
            + combined[-4000:]
        )
    return {
        "command": command,
        "module_count": len(CPU_TEST_MODULES),
        "test_count": EXPECTED_CPU_TEST_COUNT,
        "returncode": completed.returncode,
        "output_sha256": _sha(combined.encode("utf-8")),
        "gpu_disabled_by_environment": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    outputs = (args.output, args.twin, args.receipt)
    if len({path.resolve() for path in outputs}) != len(outputs):
        raise ValueError("output, twin, and receipt must be pairwise distinct")
    for path in outputs:
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)

    base_bytes = BASE_SOURCE.read_bytes()
    if _sha(base_bytes) != EXPECTED_BASE_SOURCE_SHA256:
        raise RuntimeError("immutable executed Goal5790-A1 v3 source drifted")
    base_payloads = _read_regular_archive(base_bytes)
    base_manifest = _verify_base_manifest(base_payloads)

    source_payloads = dict(base_payloads)
    del source_payloads[OLD_SOURCE_MANIFEST]
    for name, expected_sha in EXPECTED_OVERLAY_SHA256.items():
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise FileNotFoundError(f"missing regular A1 overlay: {name}")
        data = path.read_bytes()
        if _sha(data) != expected_sha:
            raise RuntimeError(f"frozen A1 overlay drifted: {name}")
        source_payloads[name] = data
    builder_bytes = (ROOT / BUILDER_MEMBER).read_bytes()
    source_payloads[BUILDER_MEMBER] = builder_bytes

    # Recheck the full successor name surface after overlay, not only the base.
    for name in source_payloads:
        if _normalized_member(name) != name:
            raise RuntimeError(f"noncanonical successor member: {name}")
    if NEW_SOURCE_MANIFEST in source_payloads:
        raise RuntimeError("new non-self manifest path collides with source")
    deep_blob_audit = _deep_successor_blob_audit(source_payloads)

    source_rows = _canonical_rows(source_payloads)
    source_tree_sha = _tree_sha(source_rows)
    source_manifest = (json.dumps({
        "schema": "rtdl.goal5790_a1.portable_source_manifest.v4",
        "run_goal_id": "5790-A1",
        "source_role": "postrun_verification_successor_only",
        "executed_source_version": 3,
        "executed_source_archive_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "worker_or_scientific_execution_bytes_replaced": False,
        "base_source_archive_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "base_source_manifest_sha256": _sha(base_payloads[OLD_SOURCE_MANIFEST]),
        "base_source_tree_sha256": base_manifest["source_tree_sha256"],
        "old_source_manifest_removed": OLD_SOURCE_MANIFEST,
        "successor_deep_blob_audit": deep_blob_audit,
        "manifest_is_non_self_referential": True,
        "file_count_excluding_this_manifest": len(source_rows),
        "overlay_file_count_including_builder": (
            len(EXPECTED_OVERLAY_SHA256) + 1
        ),
        "source_tree_sha256": source_tree_sha,
        "files": source_rows,
    }, indent=2, sort_keys=True) + "\n").encode("utf-8")
    archive_payloads = dict(source_payloads)
    archive_payloads[NEW_SOURCE_MANIFEST] = source_manifest
    archive_bytes = _deterministic_archive(archive_payloads)

    # Reopen and independently rehash the produced bytes before they reach disk.
    reopened = _read_regular_archive(archive_bytes)
    if reopened != archive_payloads:
        raise RuntimeError("in-memory successor archive reopen mismatch")

    with tempfile.TemporaryDirectory(prefix="goal5790_a1_portable_audit_") as tmp:
        extracted = Path(tmp) / "source"
        _extract_empty(reopened, extracted)
        extracted_payloads = {
            path.relative_to(extracted).as_posix(): path.read_bytes()
            for path in extracted.rglob("*") if path.is_file()
        }
        if extracted_payloads != archive_payloads:
            raise RuntimeError("empty-directory extraction rehash mismatch")
        cpu_test_result = _run_cpu_tests(extracted)

    archive_sha = _sha(archive_bytes)
    manifest_sha = _sha(source_manifest)
    builder_sha = _sha(builder_bytes)
    receipt = (json.dumps({
        "schema": "rtdl.goal5790_a1.portable_source_build_receipt.v4",
        "goal": "5790-A1",
        "source_role": "postrun_verification_successor_only",
        "executed_source_version": 3,
        "executed_source_archive_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "worker_or_scientific_execution_bytes_replaced": False,
        "base_source_archive_path": BASE_SOURCE.relative_to(ROOT).as_posix(),
        "base_source_archive_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "base_source_manifest_rehashed": True,
        "base_source_tree_sha256": base_manifest["source_tree_sha256"],
        "builder_path": BUILDER_MEMBER,
        "builder_sha256": builder_sha,
        "output_path": _receipt_path(args.output),
        "twin_path": _receipt_path(args.twin),
        "source_archive_sha256": archive_sha,
        "source_archive_bytes": len(archive_bytes),
        "source_twin_sha256": archive_sha,
        "source_twin_byte_identical": True,
        "source_manifest_member": NEW_SOURCE_MANIFEST,
        "source_manifest_sha256": manifest_sha,
        "source_manifest_non_self_referential": True,
        "source_tree_sha256": source_tree_sha,
        "source_file_count_excluding_manifest": len(source_payloads),
        "archive_payload_count_including_manifest": len(archive_payloads),
        "archive_payload_bytes": sum(map(len, archive_payloads.values())),
        "overlay_file_count_including_builder": (
            len(EXPECTED_OVERLAY_SHA256) + 1
        ),
        "overlay_sha256": {
            **dict(EXPECTED_OVERLAY_SHA256),
            BUILDER_MEMBER: builder_sha,
        },
        "old_source_manifest_removed": OLD_SOURCE_MANIFEST not in reopened,
        "successor_deep_blob_audit": deep_blob_audit,
        "unsafe_member_count": 0,
        "prebuilt_native_or_device_binary_count": 0,
        "nested_container_count": 0,
        "private_cache_member_count": 0,
        "empty_directory_extract_rehash_passed": True,
        "cpu_only_extracted_test_result": cpu_test_result,
        "home_or_remote_execution_count": 0,
        "gpu_execution_count": 0,
        "pod_execution_count": 0,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "claim_boundary": (
            "append-only postrun verification-source construction and CPU-only "
            "tests over preserved Home s3 bytes; executed source remains v3; no "
            "worker rerun, GPU, performance, universal compiler-correctness, "
            "public-release, or submission claim"
        ),
    }, indent=2, sort_keys=True) + "\n").encode("utf-8")

    _write_create_only(args.output, archive_bytes)
    _write_create_only(args.twin, archive_bytes)
    _write_create_only(args.receipt, receipt)
    if args.output.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("on-disk deterministic source twin differs")

    print(json.dumps({
        "source_archive_sha256": archive_sha,
        "source_tree_sha256": source_tree_sha,
        "source_manifest_sha256": manifest_sha,
        "source_file_count_excluding_manifest": len(source_payloads),
        "archive_payload_count_including_manifest": len(archive_payloads),
        "archive_payload_bytes": sum(map(len, archive_payloads.values())),
        "cpu_test_count": cpu_test_result["test_count"],
        "source_twin_byte_identical": True,
        "receipt_sha256": _sha(receipt),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
