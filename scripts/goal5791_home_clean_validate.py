#!/usr/bin/env python3
"""Fresh Home-Linux token-path qualification for a Goal5791 source.

The input is a deterministic, native-free source archive.  This create-only
harness rehashes and extracts it into an empty root, admits the frozen lx1
machine and exact PTX producers, builds a fresh native, materializes a new
target authority, and launches ten fresh functional processes.  Four K4 lanes
cover ON/OFF x cold/prepared; six bounded-prefix lanes cover ON/OFF across the
three frozen Triangle datasets.  Every lane uses the Goal5791 execution token
API, and an independent stdlib recount closes the evidence.

No functional clock is sampled and no elapsed/performance observation is
created.  Subprocess timeouts are operational kill guards only and their
durations are not recorded.  No registered performance timing, formal worker,
POD action, or compiler-fusion performance claim is created.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import secrets
import shutil
import stat
import subprocess
import sys
import tarfile


SOURCE_MANIFEST_MEMBER = (
    "history/internal_docs/goal5791_portable_source_manifest_v1_20260817.json"
)
SHARED_FREEZE_MEMBER = (
    "history/internal_docs/goal5789_contract_evidence_20260816/"
    "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)
HOME_AUTHORITY_MEMBER = (
    "history/internal_docs/goal5790_frozen_home_machine_authority_20260816.json"
)
PREFIX_EDGE_RECORD_COUNT = 262_144
PREFIX_RULE = "first_262144_little_endian_i32_pair_records_preserve_order"
HOME_QUALIFICATION_DEPENDENCY_IDENTITY = {
    "python": "3.12.3",
    "numba": "0.65.1",
    "numpy": "2.4.4",
    "cupy": "14.0.1",
    "llvmlite": "0.47.0",
}
_HOME_ZERO_COUNT_KEYS = frozenset((
    "elapsed_value_count",
    "clock_sample_count",
    "registered_performance_timing_count",
))
_HOME_FALSE_OBSERVATION_KEYS = frozenset((
    "elapsed_values_recorded",
    "home_performance_observation_created",
    "home_performance_diagnostic_used",
    "registered_performance_timing_created",
    "performance_or_compiler_fusion_claimed",
    "performance_or_timing_claimed",
    "variant_selected_from_app_dataset_result_or_timing",
    "timing_or_duration_recorded",
    "performance_claimed",
    "performance_observation_created",
    "compiler_fusion_performance_demonstrated",
    "registered_performance_result_created",
    "home_timing_used_for_claim",
    "performance_evidence_included",
    "target_performance_observation",
    "evidence_hashing_or_serialization_inside_registered_timer",
    "registered_timing",
))
_HOME_TIMER_CONTRACT = {
    "schema": "rtdl.goal5791.home_zero_elapsed_observation.v1",
    "elapsed_value_count": 0,
    "clock_sample_count": 0,
    "home_performance_observation_created": False,
    "home_performance_diagnostic_used": False,
    "token_admission_before_device_geometry": True,
    "device_iterator_closed_before_evidence_seal": True,
}
_HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS = (
    "elapsed", "clock", "duration", "timing", "timer", "timestamp",
    "monotonic", "perf_counter", "process_time", "wall_time", "latency",
    "throughput", "benchmark", "performance",
)
_HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES = (
    "_started_ns", "_ended_ns", "_start_ns", "_end_ns",
    "_seconds", "_milliseconds", "_microseconds", "_nanoseconds",
)
HOME_FUNCTIONAL_CLOSURE_KEYS = frozenset({
    "schema", "status", "execution_source_archive_sha256",
    "execution_source_tree_sha256", "source_manifest_sha256",
    "native_library_sha256", "target_materialization_receipt_sha256",
    "target_materialization_evidence_sha256", "home_evidence_sha256",
    "home_evidence_twin_sha256", "home_evidence_twin_byte_identical",
    "home_evidence_manifest_sha256",
    "home_evidence_independent_audit_sha256", "home_evidence_payload_count",
    "gpu", "home_machine_authority", "ptx_producer_toolchain_files",
    "ptx_producer_observation", "home_qualification_dependency_identity",
    "home_qualification_identity_is_not_cross_environment_reproducibility",
    "ptx_producer_open_audit", "ptx_program_identity_sha256",
    "home_functional_lane_count", "small_lane_count",
    "bounded_real_lane_count", "exact_lane_count",
    "behavioral_true_optix_lane_count", "token_only_lane_count",
    "fresh_parent_pid_count", "operation_receipt_count",
    "successful_operation_event_count_by_variant", "event_count_per_receipt",
    "all_tokens_admitted_in_preparation", "fresh_private_cupy_cache_per_lane",
    "cache_policy", "cache_policy_sha256", "cold_definition",
    "cold_claim_excludes", "operating_system_page_cache_controlled_or_dropped",
    "operating_system_page_cache_scope",
    "cuda_driver_jit_cache_controlled_or_isolated",
    "optix_disk_cache_controlled_or_isolated",
    "round_major_abba_is_uncontrolled_cache_mitigation_not_control",
    "independent_simple_undirected_oracle_recomputed_from_raw_edges",
    "independently_recounted_inputs", "legacy_execution_path_used",
    "exact_source_and_native_preserved_before_first_lane",
    "source_manifest_payloads_read_only_before_first_lane",
    "source_manifest_fully_rehashed_after_functional_lanes",
    "source_exact_set_before_first_lane",
    "source_exact_set_and_all_tree_paths_read_only_after_lanes",
    "formal_worker_count", "registered_performance_timing_count",
    "elapsed_value_count", "clock_sample_count",
    "home_performance_observation_created", "home_performance_diagnostic_used",
    "performance_or_compiler_fusion_claimed", "pod_used",
    "prebuilt_target_native_used", "private_codex_dependency_used",
    "formal_worker_environment_contract_sha256",
    "home_locale_matches_formal_environment_contract",
    "source_admission_policy_sha256",
})
HOME_EXTERNAL_EVIDENCE_HASH_KEYS = frozenset({
    "home_evidence_sha256", "home_evidence_twin_sha256",
    "home_evidence_twin_byte_identical", "home_evidence_manifest_sha256",
    "home_evidence_independent_audit_sha256",
})
HOME_EVIDENCE_BOUND_CLOSURE_KEYS = (
    HOME_FUNCTIONAL_CLOSURE_KEYS - HOME_EXTERNAL_EVIDENCE_HASH_KEYS
)
REAL_DATASETS = {
    "com-dblp": {
        "filename": "com-dblp.edge",
        "sha256": "e9647564c1ca96589cc52314cabf5569ec80b9f5d697578a55d47fbe7aafca67",
        "size_bytes": 8_398_928,
        "prefix_sha256": "0a6d9608bd843e12ca1bac1d93a49e06cd40d76ab0526735dbf7204e6586be14",
        "prefix_triangle_count": 159_861,
    },
    "cit-Patents": {
        "filename": "cit-Patents.edge",
        "sha256": "c5b2c9203eeabb46414965755c33befdb1810e71cb51155eb940a68a6179d855",
        "size_bytes": 132_151_584,
        "prefix_sha256": "4b2b992c8efc9b67d6695245eb5d4647e39a9a1d996d4b05078f870dd1847ba0",
        "prefix_triangle_count": 97,
    },
    "soc-LiveJournal1": {
        "filename": "soc-LiveJournal1.edge",
        "sha256": "80199ecebb7ebdf3b4861748e009d16b1c5f93c35eba837a7ce37f94ada35f83",
        "size_bytes": 551_950_184,
        "prefix_sha256": "86c12ecc87289f9fec53bf6f11f8607fde3d8b8380917a45dd6609fd26b4e8d1",
        "prefix_triangle_count": 70_758,
    },
}


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def _reject_home_performance_observations(
    value: object, *, label: str,
) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            folded = key.casefold()
            if key in _HOME_ZERO_COUNT_KEYS:
                if type(item) is not int or item != 0:
                    raise RuntimeError(
                        f"Home observation count is not exact zero: "
                        f"{label}.{key}")
            elif key in _HOME_FALSE_OBSERVATION_KEYS:
                if item is not False:
                    raise RuntimeError(
                        f"Home observation marker is not false: "
                        f"{label}.{key}")
            elif key == "timer_contract_sha256":
                if item != _digest(_HOME_TIMER_CONTRACT):
                    raise RuntimeError(
                        f"Home zero-observation contract digest drifted: "
                        f"{label}.{key}")
            elif any(token in folded
                     for token in _HOME_FORBIDDEN_OBSERVATION_KEY_TOKENS) \
                    or folded.endswith(
                        _HOME_FORBIDDEN_OBSERVATION_KEY_SUFFIXES):
                raise RuntimeError(
                    f"Home performance/clock field is forbidden: "
                    f"{label}.{key}")
            _reject_home_performance_observations(
                item, label=f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_home_performance_observations(
                item, label=f"{label}[{index}]")


def _run(
    command: list[str], *, cwd: Path, env: dict[str, str], log: Path,
    timeout: int = 1800,
) -> str:
    completed = subprocess.run(
        command, cwd=cwd, env=env, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        check=False, timeout=timeout,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode:
        raise RuntimeError(f"command failed: {command!r}; see {log}")
    return completed.stdout


def _safe_extract_source(archive_path: Path, destination: Path) -> list[str]:
    """Extract only canonical regular files into one absent directory."""

    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    payloads: dict[str, bytes] = {}
    folded: set[str] = set()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            spelling = member.name
            pure = PurePosixPath(spelling)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            normalized = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts \
                    or "\\" in spelling or normalized != spelling:
                raise RuntimeError(
                    f"Goal5791 source archive member is unsafe: {spelling!r}")
            if member.isdir():
                # The deterministic source archive contains no explicit
                # directory members; directories are implied by file paths.
                raise RuntimeError(
                    f"Goal5791 source archive has an extra directory member: "
                    f"{spelling!r}")
            if not member.isfile() or member.issym() or member.islnk():
                raise RuntimeError(
                    f"Goal5791 source archive member is not regular: {spelling!r}")
            if normalized in payloads or normalized.casefold() in folded:
                raise RuntimeError(
                    f"Goal5791 source archive member collides: {spelling!r}")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError(
                    f"Goal5791 source archive member is unreadable: {spelling!r}")
            payloads[normalized] = stream.read()
            folded.add(normalized.casefold())
    destination.mkdir(parents=True)
    for name, data in sorted(payloads.items()):
        path = destination.joinpath(*PurePosixPath(name).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return sorted(payloads)


def _verify_source(source: Path, names: list[str]) -> dict[str, object]:
    manifest_path = source / SOURCE_MANIFEST_MEMBER
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if value.get("schema") != "rtdl.goal5791.portable_source_manifest.v1" \
            or value.get("goal") != 5791:
        raise RuntimeError("Goal5791 source manifest header drifted")
    rows = value.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("Goal5791 source manifest has no file rows")
    expected = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    if len(expected) != len(rows) \
            or set(names) != set(expected) | {SOURCE_MANIFEST_MEMBER} \
            or value.get("file_count_excluding_this_manifest") != len(rows):
        raise RuntimeError("Goal5791 source membership/count drifted")
    for name, (size, sha) in expected.items():
        path = source.joinpath(*PurePosixPath(name).parts)
        if path.stat().st_size != size or _sha(path) != sha:
            raise RuntimeError(f"Goal5791 source member drifted: {name}")
    reconstructed = _digest(rows)
    if reconstructed != value.get("source_tree_sha256"):
        raise RuntimeError("Goal5791 source tree digest drifted")
    forbidden = [
        name for name in names
        if any(part in {".codex", ".git", "__pycache__", "build"}
               for part in PurePosixPath(name).parts)
        or name.lower().endswith((
            ".pyc", ".pyo", ".so", ".dll", ".dylib", ".pyd", ".ptx",
            ".cubin", ".o", ".obj", ".a", ".lib", ".exe", ".tar",
            ".tar.gz", ".tgz", ".zip", ".7z", ".gz", ".bz2", ".xz",
        ))
    ]
    if forbidden:
        raise RuntimeError(
            f"Goal5791 source contains private/binary/container bytes: {forbidden[:3]}")
    if value.get("product_delta_paths") != [
        "src/rtdsl/v4_operation_evidence.py",
        "src/rtdsl/v4_triangle_reduction_device_runtime.py",
    ]:
        raise RuntimeError("Goal5791 source product delta set drifted")
    return value


def _seal_manifest_payloads(
    source: Path, manifest: dict[str, object],
) -> None:
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("Goal5791 source manifest rows disappeared")
    for row in rows:
        path = source.joinpath(*PurePosixPath(str(row["path"])).parts)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Goal5791 source payload disappeared: {path}")
        path.chmod(path.stat().st_mode & ~0o222)
    manifest_path = source / SOURCE_MANIFEST_MEMBER
    manifest_path.chmod(manifest_path.stat().st_mode & ~0o222)


def _audit_exact_source_set(
    source: Path, manifest: dict[str, object], *,
    manifest_file_sha256: str, require_read_only: bool,
) -> dict[str, object]:
    rows = manifest.get("files")
    if not isinstance(rows, list):
        raise RuntimeError("Goal5791 source manifest rows disappeared")
    expected_files = {
        str(row["path"]): (int(row["size_bytes"]), str(row["sha256"]))
        for row in rows
    }
    manifest_path = source / SOURCE_MANIFEST_MEMBER
    expected_files[SOURCE_MANIFEST_MEMBER] = (
        manifest_path.stat().st_size, manifest_file_sha256)
    expected_dirs: set[str] = set()
    for name in expected_files:
        parent = PurePosixPath(name).parent
        while str(parent) not in ("", "."):
            expected_dirs.add(parent.as_posix())
            parent = parent.parent
    observed_files: dict[str, tuple[int, str]] = {}
    observed_dirs: set[str] = set()
    for path in [source, *source.rglob("*")]:
        relative = "." if path == source else path.relative_to(source).as_posix()
        lstat = path.lstat()
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        if path.is_symlink() or (
            reparse_flag
            and getattr(lstat, "st_file_attributes", 0) & reparse_flag
        ):
            raise RuntimeError(
                f"Goal5791 source link/reparse remains: {relative}")
        if require_read_only and lstat.st_mode & 0o222:
            raise RuntimeError(f"Goal5791 source path is writable: {relative}")
        if path.is_dir():
            if path != source:
                observed_dirs.add(relative)
        elif path.is_file():
            observed_files[relative] = (path.stat().st_size, _sha(path))
        else:
            raise RuntimeError(f"Goal5791 source special node remains: {relative}")
    if observed_dirs != expected_dirs or observed_files != expected_files:
        raise RuntimeError(
            "Goal5791 source exact-set drifted: "
            + repr({
                "files": sorted(set(observed_files) ^ set(expected_files))[:16],
                "directories": sorted(observed_dirs ^ expected_dirs)[:16],
            }))
    return {
        "regular_file_count": len(observed_files),
        "directory_count_excluding_root": len(observed_dirs),
        "regular_file_set_exact": True,
        "directory_set_exact": True,
        "extra_regular_file_count": 0,
        "extra_directory_count": 0,
        "link_count": 0,
        "reparse_point_count": 0,
        "special_file_count": 0,
        "all_tree_paths_without_write_bits": require_read_only,
    }


def _remove_write_bits(path: Path) -> None:
    for item in sorted(path.rglob("*"), reverse=True):
        if item.is_symlink():
            raise RuntimeError(f"Goal5791 refuses to seal source link: {item}")
        item.chmod(item.stat().st_mode & ~0o222)
    path.chmod(path.stat().st_mode & ~0o222)


def _target_authority(
    *, source_archive: Path, source_manifest: dict[str, object], source: Path,
    native: Path, inspection: dict[str, object], target_evidence: Path,
) -> dict[str, object]:
    freeze = json.loads((source / SHARED_FREEZE_MEMBER).read_text(encoding="utf-8"))
    value = {
        "schema": "rtdl.v4.target_materialization_authority.v2",
        "shared_contract_freeze_sha256": freeze["shared_contract_freeze_sha256"],
        "execution_source_archive_sha256": _sha(source_archive),
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "callback_ir_sha256": inspection["callback_ir_sha256"],
        "callback_authority_nonce": inspection["callback_authority_nonce"],
        "contract_sha256": inspection["contract_sha256"],
        "abi_sha256": inspection["abi_sha256"],
        "provider_identity": "optix",
        "program_bundle_identity": inspection["program_bundle_identity"],
        "composed_program_sha256": inspection["composed_program_sha256"],
        "cupy_version": inspection["cupy_version"],
        "fusion_on_downstream_operation_recipe": inspection[
            "fusion_on_downstream_operation_recipe"],
        "fusion_off_downstream_operation_recipe": inspection[
            "fusion_off_downstream_operation_recipe"],
        "fusion_on_downstream_operation_recipe_sha256": inspection[
            "fusion_on_downstream_operation_recipe_sha256"],
        "fusion_off_downstream_operation_recipe_sha256": inspection[
            "fusion_off_downstream_operation_recipe_sha256"],
        "native_library_sha256": _sha(native),
        "native_payload_sha256": _sha(native),
        "target_identity_sha256": inspection["target_identity_sha256"],
        "materializer_source_sha256": _sha(
            source / "scripts/goal5791_home_clean_validate.py"),
        "source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "evidence_archive_sha256": _sha(target_evidence),
        # A fresh hex nonce hardens evidence uniqueness.  It is not a claim
        # that the preexisting product verifier requires 256-bit nonce bytes;
        # that verifier also admits bounded descriptive nonce strings.
        "materialization_nonce": secrets.token_hex(32),
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
    }
    value["receipt_sha256"] = _digest(value)
    return value


_FRESH_PRODUCER_OBSERVATION_FIELDS = frozenset((
    "numba_probe_ptx_sha256",
    "nvrtc_probe_source_sha256",
))


def _target_bound_producer_observation(
    preflight: dict[str, object], inspection: dict[str, object],
) -> dict[str, object]:
    """Bind evidence to the actual target-inspection producer process.

    The producer probe deliberately runs in fresh processes.  Its NVRTC
    source contains the PID, and Numba's line-info PTX is likewise a
    fresh-process payload.  Every stable identity field must match the
    earlier preflight, while the evidence carries the observation that is
    actually embedded in and bound by the target inspection.
    """

    observed = inspection.get("ptx_producer_observation")
    if not isinstance(observed, dict) or set(observed) != set(preflight):
        raise RuntimeError(
            "Goal5791 target producer observation shape drifted")
    stable_fields = set(preflight) - _FRESH_PRODUCER_OBSERVATION_FIELDS
    if any(preflight[name] != observed[name] for name in stable_fields):
        raise RuntimeError(
            "Goal5791 target producer stable identity drifted")
    return dict(observed)


def main() -> None:
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--optix-prefix", type=Path, required=True)
    parser.add_argument("--triangle-data-root", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("61",), default="61")
    parser.add_argument("--max-relation-rows", type=int, default=1_000_000)
    args = parser.parse_args()
    source_archive = args.source.resolve()
    root = args.work_root.resolve()
    home_python = args.python.resolve()
    if root.exists() or root.is_symlink():
        raise FileExistsError(root)
    if _sha(source_archive) != args.expected_source_sha256.lower():
        raise RuntimeError("Goal5791 source archive bytes drifted")
    for path in (home_python, args.cuda_prefix, args.optix_prefix,
                 args.triangle_data_root):
        if not path.exists():
            raise FileNotFoundError(path)
    root.mkdir(parents=True)
    logs = root / "logs"
    logs.mkdir()
    source = root / "source"

    names = _safe_extract_source(source_archive, source)
    executing_harness_sha = _sha(Path(__file__).resolve())
    source_harness = source / "scripts/goal5791_home_clean_validate.py"
    if _sha(source_harness) != executing_harness_sha:
        raise RuntimeError(
            "executing Goal5791 Home validator differs from frozen source")
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "src"))
    from scripts import goal5790_home_clean_validate as legacy
    from scripts import goal5791_formal_contract as formal_contract
    if not Path(legacy.__file__).resolve().is_relative_to(source) \
            or not Path(formal_contract.__file__).resolve().is_relative_to(source):
        raise RuntimeError("Goal5791 Home validator imported outside frozen source")

    source_manifest = _verify_source(source, names)
    source_manifest_file_sha = _sha(source / SOURCE_MANIFEST_MEMBER)
    _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=False,
    )
    home_authority_path = source / HOME_AUTHORITY_MEMBER
    cuda = args.cuda_prefix.resolve()
    optix = args.optix_prefix.resolve()

    env = os.environ.copy()
    for name in tuple(env):
        if name in {
            "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES",
            "NUMBA_DISABLE_CUDA", "NUMBA_ENABLE_CUDASIM",
            "NUMBA_FORCE_CUDA_CC", "NUMBA_CUDA_DEFAULT_PTX_CC",
            "NUMBA_CUDA_NVVM", "NUMBA_CUDA_LIBDEVICE",
            "NUMBA_CACHE_DIR",
            "CUPY_CACHE_DIR", "CUPY_ACCELERATORS",
            "CUDA_CACHE_PATH", "CUDA_CACHE_DISABLE",
            "OPTIX_CACHE_PATH", "OPTIX_CACHE_MAXSIZE",
            "OPTIX_CACHE_ENABLED",
        } or name.startswith("RTDL_V4_FORMAL_LEAF_CACHE"):
            env.pop(name)
    env["PYTHONPATH"] = os.pathsep.join((
        str(source / "src"), str(source), str(source / "scripts")))
    env["PATH"] = os.pathsep.join((str(cuda / "bin"), env.get("PATH", "")))
    env["CUDA_HOME"] = env["CUDA_PATH"] = str(cuda)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONHASHSEED"] = "0"
    # Numba's cache=True machinery may create an empty __pycache__ directory
    # even when PYTHONDONTWRITEBYTECODE=1.  Keep every such cache outside the
    # immutable source tree so the exact-set gate remains a real admission
    # check rather than deleting evidence after the fact.
    numba_cache_root = root / "numba_cache"
    numba_cache_root.mkdir()
    env["NUMBA_CACHE_DIR"] = str(numba_cache_root)
    environment_contract = formal_contract.FORMAL_WORKER_ENVIRONMENT_CONTRACT
    if environment_contract["frozen_keys"] != [
        "PYTHONPATH", "PATH", "PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE",
        "PYTHONNOUSERSITE", "LC_ALL", "CUDA_HOME", "CUDA_PATH",
        "LD_LIBRARY_PATH", "LD_PRELOAD", "RTDL_OPTIX_LIB",
        "RTDL_OPTIX_LIBRARY", "RTDL_V4_CUDA_PREFIX", "RTDL_V4_OPTIX_PREFIX",
    ] or environment_contract["dynamic_keys"] != [
        "CUPY_CACHE_DIR", "NUMBA_CACHE_DIR",
    ]:
        raise RuntimeError("Goal5791 formal environment contract drifted")
    source_admission_policy = formal_contract.SOURCE_ADMISSION_POLICY
    if source_admission_policy[
            "expected_regular_file_set"] \
            != "manifest_rows_plus_manifest_itself" \
            or source_admission_policy["expected_directory_set"] \
                != "root_plus_parents_implied_by_expected_files" \
            or source_admission_policy[
                "extra_missing_symlink_reparse_or_special_paths_allowed"] \
                is not False \
            or source_admission_policy[
                "all_source_paths_without_write_bits_required"] is not True:
        raise RuntimeError("Goal5791 source admission policy drifted")
    env["LC_ALL"] = str(environment_contract["lc_all"])
    env.pop("LC_CTYPE", None)
    home_unsigned = dict(legacy.HOME_MACHINE_AUTHORITY)
    home_expected = {**home_unsigned, "receipt_sha256": _digest(home_unsigned)}
    if json.loads(home_authority_path.read_text(encoding="utf-8")) != home_expected \
            or str(cuda) != home_expected["cuda_toolkit_resolved_path"]:
        raise RuntimeError("Goal5791 frozen Home authority/toolkit drifted")
    ptx_files = legacy._verify_home_ptx_toolchain_files(home_expected)
    env["LD_LIBRARY_PATH"] = os.pathsep.join((
        str(Path(str(home_expected["cuda_nvvm_resolved_path"])).parent),
        str(Path(str(home_expected["cuda_nvrtc_resolved_path"])).parent),
        "/usr/lib/x86_64-linux-gnu",
    ))
    env["LD_PRELOAD"] = str(home_expected["cuda_nvrtc_resolved_path"])
    env["CUPY_CACHE_DIR"] = str(root / "fresh_cupy_probe_cache")
    env["RTDL_V4_CUDA_PREFIX"] = str(cuda)
    env["RTDL_V4_OPTIX_PREFIX"] = str(optix)

    versions = json.loads(_run([
        str(home_python), str(source / "scripts/goal5790_home_ptx_producer_probe.py"),
    ], cwd=source, env=env, log=logs / "ptx_producer_probe.log").strip())
    legacy._verify_home_nvrtc_runtime(home_expected, versions)
    observed_home_dependencies = {
        name: versions.get(name)
        for name in HOME_QUALIFICATION_DEPENDENCY_IDENTITY
    }
    if observed_home_dependencies != HOME_QUALIFICATION_DEPENDENCY_IDENTITY:
        raise RuntimeError(
            "Goal5791 Home qualification dependency identity drifted: "
            + repr(observed_home_dependencies))
    nvidia_smi = Path("/usr/bin/nvidia-smi")
    if not nvidia_smi.is_file() or not os.access(nvidia_smi, os.X_OK):
        raise RuntimeError(
            "Goal5791 Home identity requires exact /usr/bin/nvidia-smi")
    gpu = _run([
        str(nvidia_smi),
        "--query-gpu=name,uuid,driver_version,compute_cap",
        "--format=csv,noheader",
    ], cwd=source, env=env, log=logs / "gpu.log").strip()
    home_authority = legacy._verify_home_authority(home_authority_path, gpu)

    host_compiler = Path(str(home_authority["cuda_host_compiler_path"]))
    compiler_line = _run(
        [str(host_compiler), "--version"], cwd=source, env=env,
        log=logs / "cuda_host_compiler.log",
    ).splitlines()[0].strip()
    if compiler_line != home_authority["cuda_host_compiler_version"]:
        raise RuntimeError("Goal5791 Home host compiler drifted")
    nvcc = cuda / "bin/nvcc"
    nvcc_lines = _run(
        [str(nvcc), "--version"], cwd=source, env=env,
        log=logs / "nvcc.log",
    ).splitlines()
    if not nvcc_lines or nvcc_lines[-1].strip() \
            != home_authority["cuda_nvcc_version"]:
        raise RuntimeError("Goal5791 Home nvcc drifted")
    _run([
        "make", "build-optix", f"OPTIX_PREFIX={optix}",
        f"CUDA_PREFIX={cuda}", f"OPTIX_CUDA_ARCH=sm_{args.compute_capability}",
        f"CXX_OPTIX={nvcc} -ccbin {host_compiler}",
    ], cwd=source, env=env, log=logs / "build.log", timeout=3600)
    built_native = source / "build/librtdl_optix.so"
    if not built_native.is_file():
        raise RuntimeError("fresh Goal5791 Home native is absent")
    native_root = root / "native"
    native_root.mkdir()
    native = native_root / "librtdl_optix.so"
    shutil.copy2(built_native, native)
    build_root = source / "build"
    if build_root.is_symlink() \
            or build_root.resolve().parent != source.resolve():
        raise RuntimeError("Goal5791 Home build cleanup target escaped source")
    shutil.rmtree(build_root.resolve())
    env["RTDL_OPTIX_LIB"] = env["RTDL_OPTIX_LIBRARY"] = str(native)

    test_modules = (
        "tests.goal5790_deferred_traversal_evidence_test",
        "tests.goal5790_deferred_triangle_segment_evidence_test",
        "tests.goal5790_fusion_ablation_contract_test",
        "tests.goal5790_operation_evidence_test",
        "tests.goal5790_triangle_runtime_integration_test",
        "tests.goal5791_verified_fusion_execution_token_test",
        "tests.goal5791_segment_descriptors_test",
    )
    test_output = _run(
        [str(home_python), "-m", "unittest", *test_modules],
        cwd=source, env=env, log=logs / "focused_tests.log", timeout=1800,
    )

    runner = source / "scripts/goal5791_home_token_validation.py"
    common = [
        str(home_python), str(runner), "--source-root", str(source),
        "--native", str(native), "--optix-include", str(optix / "include"),
        "--cuda-include", str(cuda / "include"),
        "--compute-capability", args.compute_capability,
        "--home-machine-authority", str(home_authority_path),
    ]
    inspection_path = root / "TARGET_PROGRAM_INSPECTION.json"
    trace_path = logs / "inspect_target_producer_openat.log"
    strace = Path("/usr/bin/strace")
    if not strace.is_file() or not os.access(strace, os.X_OK):
        raise RuntimeError("Goal5791 Home requires /usr/bin/strace")
    _run([
        str(strace), "-f", "-s", "4096", "-e", "trace=openat", "-o",
        str(trace_path), *common, "--mode", "inspect-target", "--output",
        str(inspection_path),
    ], cwd=source, env=env, log=logs / "inspect_target.log", timeout=1800)
    producer_open_audit = legacy._verify_strace_producer_opens(
        trace_path, home_authority)
    inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
    _reject_home_performance_observations(
        inspection, label="TARGET_PROGRAM_INSPECTION.json")
    _reject_home_performance_observations(
        versions, label="PTX_PRODUCER_OBSERVATION.json")
    _reject_home_performance_observations(
        producer_open_audit, label="PTX_PRODUCER_OPEN_AUDIT")
    ptx_identity_sha = legacy._verify_ptx_program_inspection(inspection)
    if inspection.get("schema") \
            != "rtdl.goal5791.home_target_program_inspection.v1" \
            or inspection.get("goal5791_token_api_present") is not True \
            or inspection.get("native_library_sha256") != _sha(native) \
            or inspection.get("provider_identity") != "optix" \
            or inspection.get("application_worker_executed") is not False:
        raise RuntimeError("Goal5791 Home target inspection drifted")
    target_producer_observation = _target_bound_producer_observation(
        versions, inspection)
    _reject_home_performance_observations(
        target_producer_observation,
        label="TARGET_PROGRAM_INSPECTION.ptx_producer_observation",
    )

    # Preserve exact source/native before the first functional lane.
    shutil.copy2(source_archive, root / "EXECUTION_SOURCE.tar.gz")
    shutil.copy2(native, root / "librtdl_optix.so")
    target_evidence = root / "TARGET_MATERIALIZATION_EVIDENCE.tar.gz"
    target_evidence.write_bytes(legacy._archive({
        "EXECUTION_SOURCE.tar.gz": source_archive.read_bytes(),
        "TARGET_NATIVE/librtdl_optix.so": native.read_bytes(),
        "TARGET_PROGRAM_INSPECTION.json": inspection_path.read_bytes(),
        "SOURCE_MANIFEST.json": (source / SOURCE_MANIFEST_MEMBER).read_bytes(),
        "SHARED_CONTRACT_FREEZE.json": (source / SHARED_FREEZE_MEMBER).read_bytes(),
        "HOME_MACHINE_AUTHORITY.json": home_authority_path.read_bytes(),
        "PTX_PRODUCER_OPENAT_TRACE.log": trace_path.read_bytes(),
        "PTX_PRODUCER_OBSERVATION.json": (
            json.dumps(
                target_producer_observation, indent=2, sort_keys=True,
            ) + "\n").encode(),
    }))
    authority = _target_authority(
        source_archive=source_archive, source_manifest=source_manifest,
        source=source, native=native, inspection=inspection,
        target_evidence=target_evidence,
    )
    _reject_home_performance_observations(
        authority, label="TARGET_MATERIALIZATION_AUTHORITY.json")
    authority_path = root / "TARGET_MATERIALIZATION_AUTHORITY.json"
    authority_path.write_text(
        json.dumps(authority, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )

    # No authoritative source byte may change after materialization and
    # before the ten fresh functional processes.  Build products remain
    # outside the non-self source manifest and are separately preserved.
    source_set_before_lanes = _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=False,
    )
    _seal_manifest_payloads(source, source_manifest)

    small = root / "small_k4.edge"
    legacy._write_k4(small)
    bounded_root = root / "bounded_inputs"
    bounded_root.mkdir()
    bounded: dict[str, dict[str, object]] = {}
    for dataset, identity in REAL_DATASETS.items():
        full = args.triangle_data_root.resolve() / str(identity["filename"])
        if not full.is_file() or full.stat().st_size != identity["size_bytes"] \
                or _sha(full) != identity["sha256"]:
            raise RuntimeError(f"Goal5791 full Home input drifted: {dataset}")
        view = bounded_root / f"{dataset}__first262144.edge"
        payload = legacy._write_bounded_prefix(full, view)
        count = legacy._triangle_count(payload)
        if hashlib.sha256(payload).hexdigest() != identity["prefix_sha256"] \
                or count != identity["prefix_triangle_count"]:
            raise RuntimeError(f"Goal5791 bounded Home input/oracle drifted: {dataset}")
        bounded[dataset] = {"path": view, "count": count}

    raw = root / "functional_raw"
    raw.mkdir()
    recount_inputs = root / "recount_inputs"
    recount_inputs.mkdir()
    shutil.copy2(small, recount_inputs / "small__four_vertex_clique.edge")
    for dataset, record in bounded.items():
        shutil.copy2(
            Path(record["path"]),
            recount_inputs / f"bounded_real__{dataset}.edge",
        )
    lane_cache_root = root / "functional_lane_caches"
    lane_cache_root.mkdir()
    lane_specs: list[tuple[str, str, str, Path, int]] = []
    for lifecycle in ("cold", "prepared"):
        lane_specs.append(("small", "four_vertex_clique", lifecycle, small, 4))
    for dataset, record in bounded.items():
        lane_specs.append((
            "bounded_real", dataset, "bounded_smoke",
            Path(record["path"]), int(record["count"]),
        ))
    lane_names: list[str] = []
    for input_kind, dataset, lifecycle, edge, expected in lane_specs:
        for variant in ("fusion_on", "fusion_off"):
            name = f"{input_kind}__{dataset}__{lifecycle}__{variant}.json"
            output = raw / name
            command = [
                *common, "--mode", "functional", "--shared-freeze",
                str(source / SHARED_FREEZE_MEMBER), "--target-materialization",
                str(authority_path), "--input-kind", input_kind,
                "--dataset", dataset, "--edge-file", str(edge),
                "--expected-triangle-count", str(expected),
                "--max-relation-rows", str(args.max_relation_rows),
                "--variant", variant, "--lifecycle", lifecycle,
                "--output", str(output),
            ]
            if lifecycle == "prepared":
                command.extend(["--neutral-prewarm-edge", str(small)])
            # Every Home lane starts in a fresh PID with its own initially
            # empty recipe cache.  No functional clock is sampled; the timeout
            # passed to _run is only a kill guard and is not recorded.
            lane_env = dict(env)
            lane_cache = lane_cache_root / name.removesuffix(".json")
            lane_cache.mkdir()
            lane_env["CUPY_CACHE_DIR"] = str(lane_cache)
            _run(
                command, cwd=source, env=lane_env,
                log=logs / (name + ".log"),
                timeout=1800,
            )
            lane = json.loads(output.read_text(encoding="utf-8"))
            _reject_home_performance_observations(lane, label=name)
            if lane.get("ptx_program_identity") \
                    != inspection["ptx_program_identity"]:
                raise RuntimeError("Goal5791 Home lane PTX identity drifted")
            lane_names.append(name)
    if len(lane_names) != 10:
        raise RuntimeError("Goal5791 Home lane cardinality drifted")

    recount_path = root / "FUNCTIONAL_RECOUNT.json"
    _run([
        str(home_python), str(source / "scripts/goal5791_independent_home_recount.py"),
        "--raw", str(raw), "--inputs", str(recount_inputs),
        "--expected-source-archive-sha256",
        _sha(source_archive), "--expected-source-tree-sha256",
        str(source_manifest["source_tree_sha256"]), "--expected-native-sha256",
        _sha(native), "--output", str(recount_path),
    ], cwd=source, env=env, log=logs / "functional_recount.log", timeout=600)
    recount = json.loads(recount_path.read_text(encoding="utf-8"))
    _reject_home_performance_observations(
        recount, label="FUNCTIONAL_RECOUNT.json")
    if recount.get("exact_lane_count") != 10 \
            or recount.get("behavioral_true_optix_lane_count") != 10 \
            or recount.get("token_only_lane_count") != 10 \
            or recount.get("elapsed_value_count") != 0 \
            or recount.get("clock_sample_count") != 0 \
            or recount.get("home_performance_observation_created") is not False \
            or recount.get("home_performance_diagnostic_used") is not False:
        raise RuntimeError("Goal5791 independent Home recount did not close")
    post_functional_source = _verify_source(source, names)
    if post_functional_source["source_tree_sha256"] \
            != source_manifest["source_tree_sha256"]:
        raise RuntimeError("Goal5791 source changed during Home functional lanes")
    _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=False,
    )
    _remove_write_bits(source)
    source_set_after_lanes = _audit_exact_source_set(
        source, source_manifest,
        manifest_file_sha256=source_manifest_file_sha,
        require_read_only=True,
    )

    evidence_payloads = {
        "EXECUTION_SOURCE.tar.gz": source_archive.read_bytes(),
        "TARGET_NATIVE/librtdl_optix.so": native.read_bytes(),
        "TARGET_MATERIALIZATION_AUTHORITY.json": authority_path.read_bytes(),
        "TARGET_MATERIALIZATION_EVIDENCE.tar.gz": target_evidence.read_bytes(),
        "TARGET_PROGRAM_INSPECTION.json": inspection_path.read_bytes(),
        "SOURCE_MANIFEST.json": (source / SOURCE_MANIFEST_MEMBER).read_bytes(),
        "FUNCTIONAL_RECOUNT.json": recount_path.read_bytes(),
        **{
            f"INPUTS/{path.name}": path.read_bytes()
            for path in sorted(recount_inputs.iterdir())
        },
        **{
            f"RAW/{name}": (raw / name).read_bytes()
            for name in sorted(lane_names)
        },
    }
    home_functional_facts = {
        "schema": "rtdl.goal5791.home_token_functional_closure.v1",
        "status": "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX",
        "execution_source_archive_sha256": _sha(source_archive),
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "native_library_sha256": _sha(native),
        "target_materialization_receipt_sha256": authority["receipt_sha256"],
        "target_materialization_evidence_sha256": _sha(target_evidence),
        "home_evidence_payload_count": len(evidence_payloads) + 1,
        "gpu": gpu,
        "home_machine_authority": home_authority,
        "ptx_producer_toolchain_files": ptx_files,
        "ptx_producer_observation": target_producer_observation,
        "home_qualification_dependency_identity": observed_home_dependencies,
        "home_qualification_identity_is_not_cross_environment_reproducibility": True,
        "ptx_producer_open_audit": producer_open_audit,
        "ptx_program_identity_sha256": ptx_identity_sha,
        "home_functional_lane_count": 10,
        "small_lane_count": 4,
        "bounded_real_lane_count": 6,
        "exact_lane_count": recount["exact_lane_count"],
        "behavioral_true_optix_lane_count": recount[
            "behavioral_true_optix_lane_count"],
        "token_only_lane_count": recount["token_only_lane_count"],
        "fresh_parent_pid_count": recount["fresh_parent_pid_count"],
        "operation_receipt_count": recount["operation_receipt_count"],
        "successful_operation_event_count_by_variant": recount[
            "successful_operation_event_count_by_variant"],
        "event_count_per_receipt": {"fusion_on": 2, "fusion_off": 7},
        "all_tokens_admitted_in_preparation": True,
        "fresh_private_cupy_cache_per_lane": True,
        "cache_policy": formal_contract.CACHE_POLICY,
        "cache_policy_sha256": _digest(formal_contract.CACHE_POLICY),
        "cold_definition": formal_contract.CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": formal_contract.CACHE_POLICY[
            "cold_claim_excludes"],
        "operating_system_page_cache_controlled_or_dropped": (
            formal_contract.CACHE_POLICY[
                "operating_system_page_cache_controlled_or_dropped"]),
        "operating_system_page_cache_scope": formal_contract.CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": (
            formal_contract.CACHE_POLICY[
                "cuda_driver_jit_cache_controlled_or_isolated"]),
        "optix_disk_cache_controlled_or_isolated": (
            formal_contract.CACHE_POLICY[
                "optix_disk_cache_controlled_or_isolated"]),
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            formal_contract.CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]),
        "independent_simple_undirected_oracle_recomputed_from_raw_edges": (
            recount[
                "independent_simple_undirected_oracle_recomputed_from_raw_edges"]),
        "independently_recounted_inputs": recount[
            "independently_recounted_inputs"],
        "legacy_execution_path_used": False,
        "exact_source_and_native_preserved_before_first_lane": True,
        "source_manifest_payloads_read_only_before_first_lane": True,
        "source_manifest_fully_rehashed_after_functional_lanes": True,
        "source_exact_set_before_first_lane": source_set_before_lanes,
        "source_exact_set_and_all_tree_paths_read_only_after_lanes": (
            source_set_after_lanes),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "performance_or_compiler_fusion_claimed": False,
        "pod_used": False,
        "prebuilt_target_native_used": False,
        "private_codex_dependency_used": False,
        "formal_worker_environment_contract_sha256": _digest(
            environment_contract),
        "home_locale_matches_formal_environment_contract": True,
        "source_admission_policy_sha256": _digest(source_admission_policy),
    }
    if set(home_functional_facts) != HOME_EVIDENCE_BOUND_CLOSURE_KEYS:
        raise RuntimeError(
            "Goal5791 evidence-bound Home functional facts key set drifted")
    _reject_home_performance_observations(
        home_functional_facts, label="home_functional_facts")
    evidence_rows = [
        {"path": name, "size_bytes": len(data),
         "sha256": hashlib.sha256(data).hexdigest()}
        for name, data in sorted(evidence_payloads.items())
    ]
    evidence_manifest_value = {
            "schema": "rtdl.goal5791.home_token_evidence_manifest.v1",
            "goal": 5791,
            "status": "PASS__10_OF_10_TOKEN_ONLY_HOME_EVIDENCE",
            "manifest_is_non_self_referential": True,
            "execution_source_archive_sha256": _sha(source_archive),
            "execution_source_tree_sha256": source_manifest[
                "source_tree_sha256"],
            "source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
            "native_library_sha256": _sha(native),
            "functional_recount_sha256": _sha(recount_path),
            "exact_lane_count": 10,
            "behavioral_true_optix_lane_count": 10,
            "token_only_lane_count": 10,
            "payload_count_excluding_manifest": len(evidence_rows),
            "payload_bytes_excluding_manifest": sum(
                len(data) for data in evidence_payloads.values()),
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "elapsed_value_count": 0,
            "clock_sample_count": 0,
            "home_performance_observation_created": False,
            "home_performance_diagnostic_used": False,
            "pod_used": False,
            "home_functional_facts": home_functional_facts,
            "files": evidence_rows,
    }
    _reject_home_performance_observations(
        evidence_manifest_value, label="EVIDENCE_MANIFEST.json")
    evidence_manifest = (
        json.dumps(evidence_manifest_value, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    evidence_payloads["EVIDENCE_MANIFEST.json"] = evidence_manifest
    evidence_bytes = legacy._archive(evidence_payloads)
    evidence = root / "GOAL5791_HOME_TOKEN_EVIDENCE.tar.gz"
    twin = root / "GOAL5791_HOME_TOKEN_EVIDENCE_TWIN.tar.gz"
    evidence.write_bytes(evidence_bytes)
    twin.write_bytes(legacy._archive(evidence_payloads))
    if evidence.read_bytes() != twin.read_bytes():
        raise RuntimeError("Goal5791 Home evidence twin is not byte-identical")
    independent_evidence_audit_path = (
        root / "HOME_EVIDENCE_INDEPENDENT_AUDIT.json")
    _run([
        str(home_python),
        str(source / "scripts/goal5791_independent_portable_audit.py"),
        "--kind", "home-evidence", "--archive", str(evidence),
        "--twin", str(twin), "--output",
        str(independent_evidence_audit_path),
    ], cwd=source, env=env,
        log=logs / "home_evidence_independent_audit.log", timeout=600)
    independent_evidence_audit = json.loads(
        independent_evidence_audit_path.read_text(encoding="utf-8"))
    _reject_home_performance_observations(
        independent_evidence_audit,
        label="HOME_EVIDENCE_INDEPENDENT_AUDIT.json",
    )
    if independent_evidence_audit.get("status") \
            != "PASS__INDEPENDENT_DEEP_ARCHIVE_AND_TWIN_AUDIT" \
            or independent_evidence_audit.get("kind") != "home-evidence" \
            or independent_evidence_audit.get("raw_lane_count") != 10:
        raise RuntimeError("Goal5791 independent Home evidence audit drifted")

    result = {
        "schema": "rtdl.goal5791.home_token_functional_closure.v1",
        "status": "PASS__10_OF_10_TOKEN_ONLY_EXACT_BEHAVIORAL_TRUE_OPTIX",
        "execution_source_archive_sha256": _sha(source_archive),
        "execution_source_tree_sha256": source_manifest["source_tree_sha256"],
        "source_manifest_sha256": _sha(source / SOURCE_MANIFEST_MEMBER),
        "native_library_sha256": _sha(native),
        "target_materialization_receipt_sha256": authority["receipt_sha256"],
        "target_materialization_evidence_sha256": _sha(target_evidence),
        "home_evidence_sha256": _sha(evidence),
        "home_evidence_twin_sha256": _sha(twin),
        "home_evidence_twin_byte_identical": True,
        "home_evidence_manifest_sha256": hashlib.sha256(
            evidence_manifest).hexdigest(),
        "home_evidence_independent_audit_sha256": _sha(
            independent_evidence_audit_path),
        "home_evidence_payload_count": len(evidence_payloads),
        "gpu": gpu,
        "home_machine_authority": home_authority,
        "ptx_producer_toolchain_files": ptx_files,
        "ptx_producer_observation": target_producer_observation,
        "home_qualification_dependency_identity": (
            observed_home_dependencies),
        "home_qualification_identity_is_not_cross_environment_reproducibility": (
            True),
        "ptx_producer_open_audit": producer_open_audit,
        "ptx_program_identity_sha256": ptx_identity_sha,
        "home_functional_lane_count": 10,
        "small_lane_count": 4,
        "bounded_real_lane_count": 6,
        "exact_lane_count": recount["exact_lane_count"],
        "behavioral_true_optix_lane_count": recount[
            "behavioral_true_optix_lane_count"],
        "token_only_lane_count": recount["token_only_lane_count"],
        "fresh_parent_pid_count": recount["fresh_parent_pid_count"],
        "operation_receipt_count": recount["operation_receipt_count"],
        "successful_operation_event_count_by_variant": recount[
            "successful_operation_event_count_by_variant"],
        "event_count_per_receipt": {"fusion_on": 2, "fusion_off": 7},
        "all_tokens_admitted_in_preparation": True,
        "fresh_private_cupy_cache_per_lane": True,
        "cache_policy": formal_contract.CACHE_POLICY,
        "cache_policy_sha256": _digest(formal_contract.CACHE_POLICY),
        "cold_definition": formal_contract.CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": formal_contract.CACHE_POLICY[
            "cold_claim_excludes"],
        "operating_system_page_cache_controlled_or_dropped": (
            formal_contract.CACHE_POLICY[
                "operating_system_page_cache_controlled_or_dropped"]),
        "operating_system_page_cache_scope": formal_contract.CACHE_POLICY[
            "operating_system_page_cache_scope"],
        "cuda_driver_jit_cache_controlled_or_isolated": (
            formal_contract.CACHE_POLICY[
                "cuda_driver_jit_cache_controlled_or_isolated"]),
        "optix_disk_cache_controlled_or_isolated": (
            formal_contract.CACHE_POLICY[
                "optix_disk_cache_controlled_or_isolated"]),
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            formal_contract.CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"]),
        "independent_simple_undirected_oracle_recomputed_from_raw_edges": (
            recount["independent_simple_undirected_oracle_recomputed_from_raw_edges"]),
        "independently_recounted_inputs": recount[
            "independently_recounted_inputs"],
        "legacy_execution_path_used": False,
        "exact_source_and_native_preserved_before_first_lane": True,
        "source_manifest_payloads_read_only_before_first_lane": True,
        "source_manifest_fully_rehashed_after_functional_lanes": True,
        "source_exact_set_before_first_lane": source_set_before_lanes,
        "source_exact_set_and_all_tree_paths_read_only_after_lanes": (
            source_set_after_lanes),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "elapsed_value_count": 0,
        "clock_sample_count": 0,
        "home_performance_observation_created": False,
        "home_performance_diagnostic_used": False,
        "performance_or_compiler_fusion_claimed": False,
        "pod_used": False,
        "prebuilt_target_native_used": False,
        "private_codex_dependency_used": False,
        "formal_worker_environment_contract_sha256": _digest(
            environment_contract),
        "home_locale_matches_formal_environment_contract": True,
        "source_admission_policy_sha256": _digest(
            source_admission_policy),
    }
    if {
        key: result[key] for key in HOME_EVIDENCE_BOUND_CLOSURE_KEYS
    } != home_functional_facts:
        raise RuntimeError(
            "Goal5791 Home result drifted from evidence-bound functional facts")
    _reject_home_performance_observations(result, label="RESULT.json")
    if set(result) != HOME_FUNCTIONAL_CLOSURE_KEYS:
        raise RuntimeError("Goal5791 Home closure exact key set drifted")
    (root / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
