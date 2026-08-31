#!/usr/bin/env python3
"""Validate the non-formal Goal5809 successor execution identity.

The identity is deliberately separate from the frozen Goal5802 runtime
manifest.  Goal5802 supplies byte authorities for retained dependencies; this
document additionally binds the current Goal5809 workers, controller, public
runtime implementation, and any Goal5809 bulk helper shipped in the portable
pilot bundle.

Static admission rehashes files without importing PyOptiX, so an RTDL child
does not accidentally pay (or hide) the other arm's runtime preload.  A
PyOptiX child calls ``verify_loaded_pyoptix`` after its normal preload to bind
the actually loaded initializer, extension, distribution, and OptiX API.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import stat
import sys
from typing import Any, Iterable, Mapping


SCHEMA = "rtdl.goal5809.successor_execution_identity.v1"
STATUS = "BOUND__NONFORMAL_GOAL5809_SUCCESSOR_EXECUTION_IDENTITY"
REQUIRED_BASE_FILE_ROLES = frozenset({
    "goal5809_execution_identity_helper",
    "goal5809_portable_bundle_tool",
    "goal5809_pyoptix_bulk_input_source",
    "goal5809_pyoptix_worker",
    "goal5809_rtdl_worker",
    "goal5809_two_app_controller",
    "goal5800_pyoptix_idiomatic_arm_source",
    "goal5805_protocol_source",
    "matched_ptx",
    "native_library",
    "callback_proof",
    "pyoptix_baseline_source",
    "pyoptix_extension",
    "pyoptix_initializer",
    "pyoptix_scalar_arm_source",
    "relation_artifact",
    "relation_authority",
    "relation_compaction_cubin",
    "rtdl_init",
    "rtdlexe_arm_source",
    "rtdlexe_module",
    "physical_execution_provenance_module",
    "runtime_manifest_dependency_source",
    "staged_candidate_manifest",
    "staged_target_manifest",
    "triangle_artifact",
    "triangle_authority",
    "trust_head",
    "trust_package",
    "trust_root",
    "workload_source",
})
_SHA256_HEX = frozenset("0123456789abcdef")
_RUNTIME_MANIFEST_SCHEMA = "rtdl.goal5802.target_runtime_manifest.v2"
_RUNTIME_MANIFEST_STATUS = "PREPARED_UNTIMED__FORMAL_EXECUTION_LOCKED"
_RUNTIME_DEPENDENCY_ROOTS = frozenset({
    "cuda", "cupy", "cupy_backends", "numpy", "optix",
})
CONTROLLED_PYTHON_FLAGS = ("-I", "-S", "-B", "-P", "-c")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 \
            or any(character not in _SHA256_HEX for character in value):
        raise RuntimeError(f"{label} is not a lowercase SHA-256")
    return value


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Goal5809 execution identity is not an object")
    return value


def _runtime_member_tree(combined_root: Path) \
        -> list[dict[str, object]]:
    """Rebuild the combined-runtime builder's complete venv framing."""

    venv = combined_root / "venv"
    if combined_root.is_symlink() or venv.is_symlink() or not venv.is_dir():
        raise RuntimeError("Goal5809 admitted combined runtime is absent")
    rows: list[dict[str, object]] = []
    for path in sorted(venv.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(
                f"Goal5809 combined runtime contains a symlink: {path}")
        metadata = path.stat()
        row: dict[str, object] = {
            "path": path.relative_to(combined_root).as_posix(),
            "mode": stat.S_IMODE(metadata.st_mode),
        }
        if stat.S_ISDIR(metadata.st_mode):
            row["kind"] = "DIRECTORY"
        elif stat.S_ISREG(metadata.st_mode):
            row.update({
                "kind": "REGULAR_FILE",
                "bytes": metadata.st_size,
                "sha256": sha256_file(path),
            })
        else:
            raise RuntimeError(
                f"Goal5809 combined runtime has a special member: {path}")
        rows.append(row)
    if not rows:
        raise RuntimeError("Goal5809 admitted combined runtime is empty")
    return rows


def controlled_python_command(
    runtime_environment: Mapping[str, Any], *, script: Path,
) -> list[str]:
    """Build the same site-disabled runpy command frozen by Goal5802."""

    interpreter = Path(str(
        runtime_environment["admitted_interpreter_path"])).resolve(
            strict=True)
    source_package = Path(str(
        runtime_environment["source_package_import_root"])).resolve(
            strict=True)
    source = Path(str(runtime_environment["source_import_root"])).resolve(
        strict=True)
    site = Path(str(
        runtime_environment["site_packages_import_root"])).resolve(
            strict=True)
    target = script.resolve(strict=True)
    bootstrap = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path[:0]=[{str(source_package)!r},{str(source)!r},"
        f"{str(site)!r}];"
        f"p={str(target)!r};"
        "sys.argv=[p,*sys.argv[1:]];"
        "runpy.run_path(p,run_name='__main__')"
    )
    return [
        str(interpreter), *CONTROLLED_PYTHON_FLAGS, bootstrap,
    ]


def controlled_python_environment(
    runtime_environment: Mapping[str, Any], *, base: Mapping[str, str],
) -> dict[str, str]:
    """Remove Python/loader injection sources and replay frozen loader state."""

    result = dict(base)
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_PRELOAD"):
        result.pop(key, None)
    # -I implies -E, so PYTHONHASHSEED would be ignored.  Remove it instead of
    # publishing a false deterministic-hash control.
    result.pop("PYTHONHASHSEED", None)
    expected_loader = runtime_environment.get("loader_environment")
    if not isinstance(expected_loader, Mapping) \
            or set(expected_loader) != {"LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or expected_loader.get("LD_PRELOAD") is not None:
        raise RuntimeError("Goal5809 loader environment authority differs")
    ld_library_path = expected_loader.get("LD_LIBRARY_PATH")
    if ld_library_path is None:
        result.pop("LD_LIBRARY_PATH", None)
    elif isinstance(ld_library_path, str) and ld_library_path:
        result["LD_LIBRARY_PATH"] = ld_library_path
    else:
        raise RuntimeError("Goal5809 LD_LIBRARY_PATH authority differs")
    result.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
    })
    return result


def _startup_observation() -> dict[str, Any]:
    return {
        "flags": {
            "isolated": int(sys.flags.isolated),
            "no_site": int(sys.flags.no_site),
            "dont_write_bytecode": int(sys.flags.dont_write_bytecode),
            "safe_path": int(sys.flags.safe_path),
            "ignore_environment": int(sys.flags.ignore_environment),
            "no_user_site": int(sys.flags.no_user_site),
        },
        "sys_path_prefix": list(sys.path[:3]),
        "environment": {
            key: os.environ.get(key) for key in (
                "PYTHONPATH", "PYTHONHOME", "PYTHONDONTWRITEBYTECODE",
                "PYTHONNOUSERSITE", "PYTHONHASHSEED", "LD_LIBRARY_PATH",
                "LD_PRELOAD")
        },
    }


def _validate_controlled_startup(
    observed: Mapping[str, Any], *, expected_import_roots: list[str],
    expected_loader_environment: Mapping[str, Any],
) -> dict[str, Any]:
    expected_flags = {
        "isolated": 1,
        "no_site": 1,
        "dont_write_bytecode": 1,
        "safe_path": 1,
        "ignore_environment": 1,
        "no_user_site": 1,
    }
    expected_environment = {
        "PYTHONPATH": None,
        "PYTHONHOME": None,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONHASHSEED": None,
        "LD_LIBRARY_PATH": expected_loader_environment.get(
            "LD_LIBRARY_PATH"),
        "LD_PRELOAD": None,
    }
    raw_paths = observed.get("sys_path_prefix")
    try:
        observed_paths = [
            str(Path(str(item)).resolve(strict=True)) for item in raw_paths]
    except (OSError, TypeError) as error:
        raise RuntimeError("Goal5809 controlled import roots differ") from error
    if observed.get("flags") != expected_flags \
            or observed_paths != expected_import_roots \
            or observed.get("environment") != expected_environment:
        raise RuntimeError("Goal5809 controlled Python startup differs")
    return {
        "python_startup_flags_exact": list(CONTROLLED_PYTHON_FLAGS),
        "observed_sys_flags": expected_flags,
        "controlled_import_roots": expected_import_roots,
        "environment": expected_environment,
        "python_environment_injection_sources_absent": True,
        "loader_environment_exactly_replayed": True,
        "pythonhashseed_control_claimed": False,
        "hash_order_determinism_reliance": False,
    }


def _admit_runtime_environment(
    identity: Mapping[str, Any], *, observed_files: Mapping[str, Any],
) -> dict[str, Any]:
    """Admit the exact interpreter and live-rehash the complete frozen venv."""

    runtime_row = observed_files.get("runtime_manifest_dependency_source")
    if not isinstance(runtime_row, Mapping):
        raise RuntimeError("Goal5809 runtime-manifest dependency is absent")
    runtime_path = Path(str(runtime_row["path"]))
    runtime = _read_object(runtime_path)
    unsigned_runtime = dict(runtime)
    runtime_semantic_sha256 = unsigned_runtime.pop("manifest_sha256", None)
    predecessor = identity.get("predecessor_runtime_manifest")
    if runtime.get("schema") != _RUNTIME_MANIFEST_SCHEMA \
            or runtime.get("status") != _RUNTIME_MANIFEST_STATUS \
            or runtime_semantic_sha256 != digest(unsigned_runtime) \
            or not isinstance(predecessor, Mapping) \
            or predecessor.get("semantic_sha256") \
            != runtime_semantic_sha256:
        raise RuntimeError("Goal5809 predecessor runtime semantic seal differs")

    provenance = runtime.get("build_provenance")
    runtime_files = runtime.get("files")
    if not isinstance(provenance, Mapping) \
            or not isinstance(runtime_files, Mapping):
        raise RuntimeError("Goal5809 runtime environment authority is absent")
    projection = provenance.get("combined_runtime_path_projection")
    expected_tree_sha256 = _require_sha256(
        provenance.get("combined_runtime_full_venv_member_tree_sha256"),
        "Goal5809 combined runtime member-tree SHA-256")
    if not isinstance(projection, Mapping) \
            or projection.get("all_runtime_paths_inside_receipted_combined_root") \
            is not True \
            or not isinstance(projection.get("root_path"), str) \
            or not isinstance(projection.get("clean_python_relative"), str):
        raise RuntimeError("Goal5809 combined runtime path projection differs")
    combined_root = Path(str(projection["root_path"]))
    if not combined_root.is_absolute():
        raise RuntimeError("Goal5809 combined runtime root is not absolute")
    combined_root = combined_root.resolve(strict=True)
    venv_root = (combined_root / "venv").resolve(strict=True)
    site_packages = (
        combined_root / str(projection.get("site_packages_relative", ""))
    ).resolve(strict=True)
    expected_interpreter_path = (
        combined_root / str(projection["clean_python_relative"])).absolute()
    expected_interpreter = expected_interpreter_path.resolve(strict=True)
    clean_python = runtime_files.get("clean_python")
    if not isinstance(clean_python, Mapping) \
            or type(clean_python.get("bytes")) is not int \
            or clean_python["bytes"] <= 0:
        raise RuntimeError("Goal5809 clean interpreter authority differs")
    clean_python_sha256 = _require_sha256(
        clean_python.get("sha256"), "Goal5809 clean interpreter SHA-256")
    clean_authority_path = Path(str(clean_python.get(
        "resolved_path", clean_python.get("path", "")))).resolve(strict=True)
    if clean_authority_path != expected_interpreter \
            or expected_interpreter.stat().st_size != clean_python["bytes"] \
            or sha256_file(expected_interpreter) != clean_python_sha256:
        raise RuntimeError("Goal5809 clean interpreter bytes differ")

    actual_interpreter_path = Path(sys.executable).absolute()
    actual_interpreter = actual_interpreter_path.resolve(strict=True)
    actual_prefix = Path(sys.prefix).resolve(strict=True)
    actual_base_prefix = Path(sys.base_prefix).resolve(strict=True)
    if os.path.normcase(str(actual_interpreter_path)) \
            != os.path.normcase(str(expected_interpreter_path)):
        raise RuntimeError(
            "Goal5809 process did not use the admitted clean interpreter")
    if actual_interpreter.stat().st_size != clean_python["bytes"] \
            or sha256_file(actual_interpreter) != clean_python_sha256:
        raise RuntimeError("Goal5809 live interpreter bytes differ")

    member_rows = _runtime_member_tree(combined_root)
    observed_tree_sha256 = digest(member_rows)
    if observed_tree_sha256 != expected_tree_sha256:
        raise RuntimeError("Goal5809 live combined runtime tree differs")
    pyvenv_cfg = venv_root / "pyvenv.cfg"
    if pyvenv_cfg.is_symlink() or not pyvenv_cfg.is_file():
        raise RuntimeError("Goal5809 frozen pyvenv.cfg is absent")
    cfg_rows: dict[str, str] = {}
    for line in pyvenv_cfg.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator:
            cfg_rows[key.strip().lower()] = value.strip()
    home = cfg_rows.get("home")
    if not home or not Path(home).is_absolute():
        raise RuntimeError("Goal5809 frozen pyvenv.cfg home differs")
    home_path = Path(home).resolve(strict=True)
    expected_base_prefix = (
        home_path.parent if home_path.name.lower() in {"bin", "scripts"}
        else home_path)
    # With -S, CPython intentionally does not activate the venv prefix even
    # though sys.executable is the exact venv binary.  Bind that real startup
    # shape to the frozen pyvenv.cfg instead of falsely requiring sys.prefix
    # to equal the venv root.
    if actual_prefix != expected_base_prefix \
            or actual_base_prefix != expected_base_prefix:
        raise RuntimeError("Goal5809 frozen base Python prefix differs")
    identity_files = identity.get("files")
    worker_row = (identity_files.get("goal5809_rtdl_worker")
                  if isinstance(identity_files, Mapping) else None)
    if not isinstance(worker_row, Mapping):
        raise RuntimeError("Goal5809 worker source authority is absent")
    worker_path = Path(str(worker_row["path"])).resolve(strict=True)
    source_root = worker_path.parent.parent
    source_package_root = source_root / "src"
    if not source_package_root.is_dir():
        raise RuntimeError("Goal5809 controlled source root is absent")
    target_observation = runtime.get("target_observation")
    loader_environment = (
        target_observation.get("loader_environment")
        if isinstance(target_observation, Mapping) else None)
    if not isinstance(loader_environment, Mapping) \
            or set(loader_environment) != {"LD_LIBRARY_PATH", "LD_PRELOAD"} \
            or loader_environment.get("LD_PRELOAD") is not None:
        raise RuntimeError("Goal5809 frozen loader environment differs")
    expected_import_roots = [
        str(source_package_root.resolve(strict=True)),
        str(source_root.resolve(strict=True)),
        str(site_packages),
    ]
    startup = _validate_controlled_startup(
        _startup_observation(), expected_import_roots=expected_import_roots,
        expected_loader_environment=loader_environment)
    body: dict[str, Any] = {
        "admitted_interpreter_path": str(actual_interpreter_path),
        "admitted_interpreter_bytes": clean_python["bytes"],
        "admitted_interpreter_sha256": clean_python_sha256,
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "sys_prefix": str(actual_prefix),
        "sys_base_prefix": str(actual_base_prefix),
        "frozen_base_prefix": str(expected_base_prefix),
        "pyvenv_cfg_path": str(pyvenv_cfg),
        "pyvenv_cfg_sha256": sha256_file(pyvenv_cfg),
        "combined_runtime_root": str(combined_root),
        "venv_root": str(venv_root),
        "venv_member_count": len(member_rows),
        "venv_member_tree_sha256": observed_tree_sha256,
        "source_package_import_root": expected_import_roots[0],
        "source_import_root": expected_import_roots[1],
        "site_packages_import_root": expected_import_roots[2],
        "loader_environment": dict(loader_environment),
        "controlled_python_startup": startup,
        "interpreter_live_rehashed": True,
        "complete_venv_member_tree_live_rehashed": True,
    }
    return {
        **body,
        "environment_identity_sha256": digest(body),
        # Internal authority only.  Workers publish the compact tree digest,
        # not this potentially large projection, but loaded-file verification
        # must compare against the exact rows observed at admission rather
        # than merely hashing whatever bytes happen to exist later.
        "_admitted_venv_member_rows": member_rows,
    }


def admit_execution_identity(
    path: Path, *, expected_file_sha256: str,
    require_runtime_environment: bool = False,
) -> dict[str, Any]:
    """Rehash the manifest and every bound file without importing PyOptiX."""

    resolved_manifest = path.resolve(strict=True)
    file_sha256 = sha256_file(resolved_manifest)
    if file_sha256 != _require_sha256(
            expected_file_sha256,
            "expected Goal5809 execution identity file SHA-256"):
        raise RuntimeError("Goal5809 execution identity file SHA-256 differs")
    value = _read_object(resolved_manifest)
    unsigned = dict(value)
    semantic_sha256 = unsigned.pop("execution_identity_sha256", None)
    if value.get("schema") != SCHEMA or value.get("status") != STATUS \
            or semantic_sha256 != digest(unsigned):
        raise RuntimeError("Goal5809 execution identity semantic seal differs")
    scope = value.get("scope")
    if scope != {
        "claim_authorized": False,
        "formal_worker_count": 0,
        "nonformal_pilot_only": True,
        "registered_performance_timing_count": 0,
    }:
        raise RuntimeError("Goal5809 execution identity scope differs")
    predecessor = value.get("predecessor_runtime_manifest")
    if not isinstance(predecessor, Mapping) \
            or predecessor.get("dependency_source_only") is not True \
            or predecessor.get("is_goal5809_execution_identity") is not False:
        raise RuntimeError("Goal5802 predecessor role is not quarantined")

    files = value.get("files")
    required_roles = value.get("required_file_roles")
    if not isinstance(files, Mapping) \
            or not isinstance(required_roles, list) \
            or required_roles != sorted(files) \
            or not REQUIRED_BASE_FILE_ROLES.issubset(files) \
            or any(role.startswith("bulk_helper_") is False
                   for role in set(files) - REQUIRED_BASE_FILE_ROLES):
        raise RuntimeError("Goal5809 execution identity file role set differs")
    observed_files: dict[str, dict[str, object]] = {}
    for role in required_roles:
        row = files[role]
        if not isinstance(row, Mapping) or set(row) != {
                "bytes", "path", "provenance", "sha256"}:
            raise RuntimeError(f"Goal5809 execution identity row differs: {role}")
        if not isinstance(row.get("provenance"), str) \
                or not row["provenance"]:
            raise RuntimeError(
                f"Goal5809 execution provenance differs: {role}")
        file_path = Path(str(row["path"]))
        if not file_path.is_absolute():
            raise RuntimeError(f"Goal5809 execution path is not absolute: {role}")
        resolved = file_path.resolve(strict=True)
        expected_bytes = row.get("bytes")
        expected_sha256 = _require_sha256(
            row.get("sha256"), f"Goal5809 {role} SHA-256")
        if type(expected_bytes) is not int or expected_bytes < 0 \
                or not resolved.is_file() \
                or resolved.stat().st_size != expected_bytes \
                or sha256_file(resolved) != expected_sha256:
            raise RuntimeError(f"Goal5809 execution file differs: {role}")
        observed_files[role] = {
            "path": str(resolved),
            "bytes": expected_bytes,
            "sha256": expected_sha256,
        }

    pyoptix = value.get("pyoptix")
    if not isinstance(pyoptix, Mapping) or set(pyoptix) != {
            "api_version", "distribution_name", "distribution_version",
            "extension_module", "extension_role", "initializer_module",
            "initializer_role"} \
            or pyoptix.get("distribution_name") != "pyoptix" \
            or pyoptix.get("initializer_module") != "optix" \
            or pyoptix.get("extension_module") != "optix._optix" \
            or pyoptix.get("initializer_role") != "pyoptix_initializer" \
            or pyoptix.get("extension_role") != "pyoptix_extension" \
            or not isinstance(pyoptix.get("distribution_version"), str) \
            or not pyoptix["distribution_version"] \
            or not isinstance(pyoptix.get("api_version"), str) \
            or not pyoptix["api_version"]:
        raise RuntimeError("Goal5809 PyOptiX identity declaration differs")
    observed_distribution = importlib.metadata.version("pyoptix")
    if observed_distribution != pyoptix["distribution_version"]:
        raise RuntimeError("Goal5809 PyOptiX distribution version differs")
    runtime_environment_internal = (
        _admit_runtime_environment(value, observed_files=observed_files)
        if require_runtime_environment else None)
    admitted_member_rows = None
    runtime_environment = runtime_environment_internal
    if isinstance(runtime_environment_internal, dict):
        runtime_environment = dict(runtime_environment_internal)
        admitted_member_rows = runtime_environment.pop(
            "_admitted_venv_member_rows")
    return {
        "manifest_path": str(resolved_manifest),
        "manifest_file_sha256": file_sha256,
        "execution_identity_sha256": semantic_sha256,
        "file_count": len(observed_files),
        "files_rehashed": True,
        "pyoptix_distribution_version": observed_distribution,
        "pyoptix_loaded_identity_verified": False,
        "runtime_environment_required": require_runtime_environment,
        "runtime_environment_admission": runtime_environment,
        "runtime_environment_admitted_member_rows": admitted_member_rows,
        "manifest": value,
    }


def verify_loaded_runtime_dependencies(
    admitted: Mapping[str, Any], *, required_module_roots: Iterable[str],
    observed_versions: Mapping[str, object],
) -> dict[str, Any]:
    """Rehash every loaded file under selected runtime dependency roots.

    The complete venv tree is already checked at admission.  This second pass
    records which NumPy/CuPy/cuda-python/PyOptiX bytes were actually loaded by
    this arm, without importing an otherwise-unused dependency into that arm.
    """

    environment = admitted.get("runtime_environment_admission")
    if not isinstance(environment, Mapping) \
            or environment.get("complete_venv_member_tree_live_rehashed") \
            is not True:
        raise RuntimeError("Goal5809 exact runtime environment was not admitted")
    required = set(required_module_roots)
    if not required or not required.issubset(_RUNTIME_DEPENDENCY_ROOTS):
        raise RuntimeError("Goal5809 required dependency root set differs")
    if not isinstance(observed_versions, Mapping) or not observed_versions:
        raise RuntimeError("Goal5809 runtime dependency versions are absent")
    if any(not isinstance(key, str) or not key \
           or value is None or isinstance(value, (dict, set))
           for key, value in observed_versions.items()):
        raise RuntimeError("Goal5809 runtime dependency version differs")

    venv_root = Path(str(environment["venv_root"])).resolve(strict=True)
    combined_root = Path(str(environment["combined_runtime_root"])).resolve(
        strict=True)
    admitted_rows = admitted.get("runtime_environment_admitted_member_rows")
    if not isinstance(admitted_rows, list) or not admitted_rows:
        raise RuntimeError("Goal5809 admitted runtime member rows are absent")
    admitted_by_path = {
        str(row.get("path")): dict(row)
        for row in admitted_rows if isinstance(row, Mapping)
    }
    if len(admitted_by_path) != len(admitted_rows) \
            or digest(admitted_rows) != environment.get(
                "venv_member_tree_sha256"):
        raise RuntimeError("Goal5809 admitted runtime member rows differ")
    observed: dict[str, dict[str, object]] = {}
    root_counts = {root: 0 for root in sorted(_RUNTIME_DEPENDENCY_ROOTS)}
    for name, module in sorted(sys.modules.items()):
        root = name.partition(".")[0]
        if root not in _RUNTIME_DEPENDENCY_ROOTS:
            continue
        raw_path = getattr(module, "__file__", None)
        if not isinstance(raw_path, str) or not raw_path:
            continue
        module_path = Path(raw_path).resolve(strict=True)
        try:
            relative = module_path.relative_to(venv_root)
        except ValueError as error:
            raise RuntimeError(
                f"Goal5809 loaded dependency escapes admitted venv: {name}"
            ) from error
        if module_path.is_symlink() or not module_path.is_file():
            raise RuntimeError(
                f"Goal5809 loaded dependency is not a regular file: {name}")
        combined_relative = module_path.relative_to(combined_root).as_posix()
        current_row = {
            "path": combined_relative,
            "mode": stat.S_IMODE(module_path.stat().st_mode),
            "kind": "REGULAR_FILE",
            "bytes": module_path.stat().st_size,
            "sha256": sha256_file(module_path),
        }
        if admitted_by_path.get(combined_relative) != current_row:
            raise RuntimeError(
                f"Goal5809 loaded dependency differs from admission: {name}")
        observed[name] = {
            "root": root,
            "path": str(module_path),
            "venv_relative_path": relative.as_posix(),
            "bytes": current_row["bytes"],
            "sha256": current_row["sha256"],
        }
        root_counts[root] += 1
    missing = sorted(root for root in required if root_counts[root] == 0)
    if missing:
        raise RuntimeError({
            "Goal5809_loaded_runtime_dependency_roots_absent": missing,
        })
    actual_versions: dict[str, object] = {}
    if root_counts["numpy"]:
        actual_versions["numpy"] = str(getattr(sys.modules.get("numpy"),
                                               "__version__", ""))
    if root_counts["cupy"]:
        actual_versions["cupy"] = str(getattr(sys.modules.get("cupy"),
                                              "__version__", ""))
    if root_counts["cuda"]:
        actual_versions["cuda-python"] = importlib.metadata.version(
            "cuda-python")
    if root_counts["optix"]:
        optix = sys.modules.get("optix")
        actual_versions["pyoptix"] = importlib.metadata.version("pyoptix")
        version = getattr(optix, "version", None)
        if not callable(version):
            raise RuntimeError("Goal5809 loaded OptiX API version is absent")
        actual_versions["optix-api"] = ".".join(
            str(int(item)) for item in version())
    if any(not value for value in actual_versions.values()) \
            or dict(observed_versions) != actual_versions:
        raise RuntimeError("Goal5809 runtime dependency version differs")

    closing_rows = _runtime_member_tree(combined_root)
    if closing_rows != admitted_rows \
            or digest(closing_rows) != environment.get(
                "venv_member_tree_sha256"):
        raise RuntimeError("Goal5809 runtime tree changed after admission")
    body: dict[str, Any] = {
        "required_module_roots": sorted(required),
        "loaded_root_file_counts": root_counts,
        "loaded_module_files": observed,
        "observed_versions": dict(sorted(actual_versions.items())),
        "loaded_dependency_file_count": len(observed),
        "all_loaded_selected_dependency_files_live_rehashed": True,
        "all_loaded_selected_dependency_files_inside_admitted_venv": True,
        "unloaded_dependency_imported_for_identity_only": False,
        "complete_venv_member_tree_rehashed_at_closing_endpoint": True,
        "admission_and_closing_runtime_tree_snapshots_equal": True,
        "continuous_runtime_tree_immutability_claimed": False,
    }
    return {**body, "loaded_dependency_identity_sha256": digest(body)}


def verify_loaded_modules(
    admitted: Mapping[str, Any], *, modules_by_role: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind actually imported modules to exact role paths and bytes."""

    value = admitted.get("manifest")
    if not isinstance(value, Mapping):
        raise RuntimeError("Goal5809 admitted execution identity is absent")
    files = value["files"]
    observed: dict[str, dict[str, object]] = {}
    if not modules_by_role:
        raise RuntimeError("Goal5809 loaded module binding set is empty")
    for role, module in modules_by_role.items():
        if role not in files:
            raise RuntimeError(
                f"Goal5809 loaded module role is not bound: {role}")
        expected = files[role]
        module_path = Path(str(getattr(module, "__file__", ""))).resolve(
            strict=True)
        if str(module_path) != expected["path"] \
                or module_path.stat().st_size != expected["bytes"] \
                or sha256_file(module_path) != expected["sha256"]:
            raise RuntimeError(f"Goal5809 loaded module differs: {role}")
        observed[role] = {
            "path": str(module_path),
            "bytes": expected["bytes"],
            "sha256": expected["sha256"],
        }
    return {
        "loaded_modules": observed,
        "loaded_module_identity_verified": True,
    }


def verify_loaded_rtdl(
    admitted: Mapping[str, Any], *, rtdl_module: Any,
    implementation_module: Any,
) -> dict[str, Any]:
    """Bind the actually imported public package and runtime implementation."""

    observed = verify_loaded_modules(
        admitted,
        modules_by_role={
            "rtdl_init": rtdl_module,
            "rtdlexe_module": implementation_module,
        })
    return {**observed, "rtdl_loaded_identity_verified": True}


def verify_loaded_pyoptix(
    admitted: Mapping[str, Any], *, optix_module: Any,
) -> dict[str, Any]:
    """Bind the already normally loaded PyOptiX modules to the manifest."""

    value = admitted.get("manifest")
    if not isinstance(value, Mapping):
        raise RuntimeError("Goal5809 admitted execution identity is absent")
    files = value["files"]
    pyoptix = value["pyoptix"]
    extension_module = sys.modules.get(str(pyoptix["extension_module"]))
    if extension_module is None:
        raise RuntimeError("Goal5809 loaded PyOptiX extension is absent")
    initializer_path = Path(str(getattr(optix_module, "__file__", ""))).resolve(
        strict=True)
    extension_path = Path(str(
        getattr(extension_module, "__file__", ""))).resolve(strict=True)
    expected_initializer = files[str(pyoptix["initializer_role"])]
    expected_extension = files[str(pyoptix["extension_role"])]
    for label, observed_path, expected in (
            ("initializer", initializer_path, expected_initializer),
            ("extension", extension_path, expected_extension)):
        if str(observed_path) != expected["path"] \
                or observed_path.stat().st_size != expected["bytes"] \
                or sha256_file(observed_path) != expected["sha256"]:
            raise RuntimeError(f"Goal5809 loaded PyOptiX {label} differs")
    version = getattr(optix_module, "version", None)
    if not callable(version):
        raise RuntimeError("Goal5809 loaded PyOptiX API version unavailable")
    observed_api = ".".join(str(int(item)) for item in version())
    if observed_api != pyoptix["api_version"]:
        raise RuntimeError("Goal5809 loaded OptiX API version differs")
    return {
        "initializer_path": str(initializer_path),
        "initializer_sha256": expected_initializer["sha256"],
        "extension_path": str(extension_path),
        "extension_sha256": expected_extension["sha256"],
        "distribution_version": pyoptix["distribution_version"],
        "api_version": observed_api,
        "pyoptix_loaded_identity_verified": True,
    }
