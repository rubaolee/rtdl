#!/usr/bin/env python3
"""Build the exact Goal5802 POD-S0 orchestration configuration.

This helper is the only operator-facing bridge between target paths and the
low-level S0 state machine.  The operator supplies target identities and
immutable input roots; every intermediate path, dynamic token, interpreter
transition, argv vector, output declaration, and zero-authority boundary is
derived here.  It never runs an RT workload, signs a trust package, reads a
clock, or authorizes a formal worker.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
from typing import Any, Mapping, NoReturn, Sequence


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import goal5802_build_offline_python_wheelhouse as wheelhouse
from scripts import goal5802_run_pod_s0_untimed as s0


BUILDER_SCHEMA = "rtdl.goal5802.pod_s0_config_builder_receipt.v1"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
SHA1_RE = re.compile(r"[0-9a-f]{40}\Z")
RTDL_WHEEL_NAME = "rtdl_source_tree-4.0.0rc1-py3-none-any.whl"
OPTIX_SDK_VERSION = "9.0.0"
NATIVE_BUILD_ID = "goal5802-s0-final-v1"
TRUST_ROOT_SCHEMA = "rtdl.v4.rtdlexe.installed_trust_root.v1"
TRUST_ROOT_DOMAIN = b"RTDL-V4-RTDLEXE-INSTALLED-TRUST-ROOT-V1\x00"
QUALIFICATION_ONLY_KEY_PREFIX = (
    "TEST_ONLY_goal5802_final_home_qualification_"
)
FORMAL_MEASUREMENT_KEY_ID = (
    "TEST_ONLY_goal5802_rtx_measurement_root_v5_20260826"
)
FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256 = (
    "3364f744a637e27710319001c2fa505bd6c54f75904b51429de253bcd4da8dc4"
)
FORMAL_MEASUREMENT_TRUST_SCOPE = "CONTROLLING_FORMAL_MEASUREMENT_ROOT"
QUALIFICATION_ONLY_TRUST_SCOPE = (
    "QUALIFICATION_ONLY__NOT_FORMAL_MEASUREMENT_ROOT"
)

MANUAL_AUTHORITY_RELATIVE = (
    "history/internal_docs/"
    "goal5802_final_successor_forecast_manual_judgement_20260825.json")
ENGINEERING_LEDGER_RELATIVE = (
    "history/internal_docs/"
    "goal5802_per_arm_engineering_effort_ledger_20260825.json")
GOAL5799_BINDING_RELATIVE = (
    "history/internal_docs/"
    "goal5799_a1_repaired_performance_and_evidence_contract_20260824.json")

SOURCE_PATHS = {
    "callback_proof": "experiments/goal5796_matched/semantic_spec.json",
    "compaction_source": (
        "experiments/goal5802_premeasurement/"
        "relation_semantic_compaction.cu"),
    "device_source": (
        "experiments/goal5802_premeasurement/"
        "matched_device_semantic_capacity.cu"),
    "direct_source": (
        "experiments/goal5802_premeasurement/direct_scalar_worker.cpp"),
    "goal5800_source": (
        "experiments/goal5800_pyoptix_owl/pyoptix_idiomatic_arm.py"),
    "clean_probe": "scripts/goal5801_a3_clean_install_probe.py",
    "clean_verifier": "scripts/goal5801_a3_verify_clean_install.py",
    "native_verifier": "scripts/goal5801_a3_verify_native_custody.py",
    "nvrtc_trap_source": "scripts/goal5801_nvrtc_forbidden_preload.c",
    "nvrtc_kat_source": "scripts/goal5801_nvrtc_positive_kat.c",
}


class ConfigBuildError(RuntimeError):
    """Fail-closed semantic-input or generated-configuration error."""


def _fail(message: str) -> NoReturn:
    raise ConfigBuildError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _trust_root_identity(path: Path) -> tuple[str, str]:
    value = _strict_json(path, "public trust root", canonical=True)
    expected_keys = {
        "schema", "key_id", "rsa_modulus_base64", "rsa_exponent",
        "trust_root_sha256",
    }
    if not isinstance(value, dict) or set(value) != expected_keys \
            or value.get("schema") != TRUST_ROOT_SCHEMA \
            or not isinstance(value.get("key_id"), str) \
            or not isinstance(value.get("rsa_modulus_base64"), str) \
            or not value["rsa_modulus_base64"] \
            or type(value.get("rsa_exponent")) is not int:
        _fail("public trust-root envelope differs")
    body = dict(value)
    seal = body.pop("trust_root_sha256")
    if seal != hashlib.sha256(
            TRUST_ROOT_DOMAIN + _canonical(body)).hexdigest():
        _fail("public trust-root domain seal differs")
    file_sha256 = _sha_file(path)
    key_id = str(value["key_id"])
    if file_sha256 == FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256 \
            and key_id == FORMAL_MEASUREMENT_KEY_ID:
        return FORMAL_MEASUREMENT_TRUST_SCOPE, file_sha256
    if key_id.startswith(QUALIFICATION_ONLY_KEY_PREFIX) \
            and file_sha256 != FORMAL_MEASUREMENT_TRUST_ROOT_FILE_SHA256:
        return QUALIFICATION_ONLY_TRUST_SCOPE, file_sha256
    _fail("public trust-root scope or controlling identity differs")


def _strict_json(path: Path, label: str, *, canonical: bool = False) -> Any:
    if path.is_symlink() or not path.is_file():
        _fail(f"{label} is not a regular file: {path}")
    payload = path.read_bytes()
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ConfigBuildError(f"{label} is not UTF-8 JSON") from error
    if canonical and payload != _canonical(value) + b"\n":
        _fail(f"{label} is not canonical JSON plus LF")
    return value


def _absolute(value: Path, label: str, *, must_exist: bool = True) -> Path:
    path = value.expanduser().absolute()
    if not path.is_absolute() or "${" in str(path):
        _fail(f"{label} must be a literal absolute path")
    if must_exist:
        try:
            path.resolve(strict=True)
        except OSError as error:
            raise ConfigBuildError(f"{label} does not resolve: {path}") from error
    return path


def _regular(value: Path, label: str, *, executable: bool = False) -> Path:
    supplied = _absolute(value, label)
    resolved = supplied.resolve(strict=True)
    metadata = resolved.stat()
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file: {resolved}")
    if executable and not os.access(resolved, os.X_OK):
        _fail(f"{label} is not executable: {resolved}")
    # Native-custody capture rejects symlink tool inputs.  Canonicalize every
    # executable once at the configuration boundary so a normal distribution
    # alias such as /usr/bin/pkg-config -> pkgconf cannot pass the native build
    # and then fail in the adjacent custody step.  Evidence files retain their
    # supplied absolute spelling because registered source inputs are path-bound.
    return resolved if executable else supplied


def _directory(value: Path, label: str) -> Path:
    supplied = _absolute(value, label)
    if supplied.is_symlink() or not supplied.resolve(strict=True).is_dir():
        _fail(f"{label} is not a real directory: {supplied}")
    return supplied.resolve(strict=True)


def _git(source: Path, git: Path, *arguments: str) -> bytes:
    environment = dict(os.environ)
    for key in list(environment):
        if key in {
                "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"} \
                or key.startswith("GIT_CONFIG_"):
            environment.pop(key, None)
    environment.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
    })
    completed = subprocess.run(
        [str(git), "-C", str(source), *arguments], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment)
    if completed.returncode != 0:
        _fail(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _source_identity(source: Path, git: Path) -> tuple[str, str, int]:
    commit = _git(source, git, "rev-parse", "HEAD").decode("ascii").strip()
    tree = _git(source, git, "rev-parse", "HEAD^{tree}").decode(
        "ascii").strip()
    if not SHA1_RE.fullmatch(commit) or not SHA1_RE.fullmatch(tree):
        _fail("source checkout does not expose full SHA-1 HEAD/tree identities")
    if _git(source, git, "status", "--porcelain=v1", "--untracked-files=all"):
        _fail("source checkout is not exact-clean, including untracked files")
    autocrlf = _git(
        source, git, "config", "--local", "--get", "core.autocrlf",
    ).decode("utf-8", errors="strict").strip().lower()
    if autocrlf not in {"false", "input"}:
        _fail("source checkout core.autocrlf must be false or input")
    epoch_text = _git(source, git, "show", "-s", "--format=%ct", commit) \
        .decode("ascii").strip()
    if not epoch_text.isdigit() or int(epoch_text) <= 0:
        _fail("source commit timestamp is not a positive integer")
    return commit, tree, int(epoch_text)


def _source_file(source: Path, role: str) -> Path:
    relative = SOURCE_PATHS[role]
    path = source / Path(*PurePosixPath(relative).parts)
    if path.is_symlink() or not path.is_file():
        _fail(f"required source-controlled input is absent: {relative}")
    return path


def _registered_source_file(source: Path, supplied: Path, relative: str,
                            label: str) -> Path:
    expected_path = source / Path(*PurePosixPath(relative).parts)
    if expected_path.is_symlink() or not expected_path.is_file():
        _fail(f"registered {label} is absent or symbolic: {expected_path}")
    expected = expected_path.resolve(strict=True)
    observed_path = _regular(supplied, label)
    if observed_path.is_symlink() \
            or observed_path.absolute() != expected_path.absolute() \
            or observed_path.resolve(strict=True) != expected:
        _fail(f"{label} must be the registered source-controlled path: {expected}")
    return expected


def _packet_identity(packet: Path, manifest_path: Path,
                     commit: str, tree: str) -> None:
    manifest = _strict_json(manifest_path, "exact source packet manifest",
                            canonical=True)
    if not isinstance(manifest, dict) \
            or manifest.get("schema") \
            != "rtdl.goal5802.exact_shallow_git_source_packet_manifest.v1" \
            or manifest.get("status") \
            != "PASS__EXACT_SELF_CONTAINED_DEPTH_ONE_GIT_SOURCE_PACKET" \
            or manifest.get("source_commit") != commit \
            or manifest.get("source_tree") != tree \
            or manifest.get("packet_sha256") != _sha_file(packet) \
            or manifest.get("packet_bytes") != packet.stat().st_size \
            or manifest.get("worker_count") != 0 \
            or manifest.get("registered_performance_timing_count") != 0:
        _fail("source packet/manifest/checkout identity differs")


def _python_version(python: Path) -> tuple[int, int]:
    command = [
        str(python), "-I", "-S", "-B", "-c",
        "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')",
    ]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    text = completed.stdout.decode("ascii", errors="strict").strip()
    match = re.fullmatch(r"([0-9]+)\.([0-9]+)", text)
    if completed.returncode != 0 or match is None:
        _fail("base Python version probe failed")
    return int(match.group(1)), int(match.group(2))


def _find_cuda_runtime_library(cuda: Path, prefix: str) -> Path:
    candidates = []
    for path in cuda.rglob(f"{prefix}.so.*"):
        if path.is_symlink():
            continue
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            continue
        if resolved.is_file() and resolved not in candidates:
            candidates.append(resolved)
    candidates.sort(key=lambda item: str(item))
    if len(candidates) != 1:
        _fail(
            f"CUDA prefix must contain exactly one canonical regular {prefix} "
            f"runtime, observed {len(candidates)}")
    return candidates[0]


def _projected_root(projection: Path, original: Path) -> Path:
    # ``original`` is the future create-only checkout emitted by the earlier
    # provenance stage.  Projection is a pure absolute-path mapping here; the
    # header projection tool later requires and records the materialized tree.
    absolute = original.absolute()
    parts = list(absolute.parts)
    if not parts or not absolute.anchor:
        _fail("SDK include root has no absolute anchor")
    projected = projection / "rootfs"
    drive = absolute.drive.rstrip(":/\\")
    if drive:
        projected /= f"drive_{drive}"
    for part in parts[1:]:
        if part in {"", ".", ".."} or "/" in part or "\\" in part:
            _fail("SDK include root is not mechanically projectable")
        projected /= part
    return projected


def _wheelhouse_rows(root: Path) -> tuple[list[dict[str, Any]], Path]:
    value = wheelhouse.verify(root)
    manifest = root / "wheelhouse_manifest.json"
    rows = value.get("wheels")
    if not isinstance(rows, list) or len(rows) != len(
            wheelhouse.REQUIRED_DISTRIBUTIONS):
        _fail("offline wheelhouse has wrong package set")
    materialized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            _fail("offline wheelhouse row is not an object")
        relative = PurePosixPath(str(row["saved_path"]))
        path = root / Path(*relative.parts)
        materialized.append({**row, "path": path})
    return materialized, manifest


def _wheel_member_paths(pyoptix_wheel: Path, python_version: tuple[int, int],
                        runtime_root: Path) -> tuple[Path, Path]:
    import zipfile

    with zipfile.ZipFile(pyoptix_wheel, "r") as archive:
        names = archive.namelist()
    initializers = [name for name in names if name == "optix/__init__.py"]
    extensions = [
        name for name in names
        if re.fullmatch(r"optix/_optix\.[^/]+\.so", name)]
    if len(initializers) != 1 or len(extensions) != 1:
        _fail("PyOptiX wheel must contain one initializer and one extension")
    major, minor = python_version
    site = runtime_root / "venv" / "lib" / f"python{major}.{minor}" \
        / "site-packages"
    return site / initializers[0], site / extensions[0]


def _venv_python(root: Path) -> Path:
    return root / "venv" / "bin" / "python"


def _step(name: str, *, runner: str, target: str,
          interpreter: Path | None, args: Sequence[str],
          environment: Mapping[str, str],
          outputs: Sequence[tuple[Path, str]]) -> dict[str, object]:
    return {
        "schema": s0.STEP_SCHEMA,
        "name": name,
        "runner": runner,
        "target": target,
        "interpreter": None if interpreter is None else str(interpreter),
        "args": list(args),
        "environment": dict(environment),
        "outputs": [
            {"path": str(path), "kind": kind} for path, kind in outputs],
    }


def _python_step(name: str, interpreter: Path, args: Sequence[str],
                 environment: Mapping[str, str],
                 outputs: Sequence[tuple[Path, str]]) -> dict[str, object]:
    return _step(
        name, runner="python_script", target=s0.SCRIPT_TARGETS[name],
        interpreter=interpreter, args=args, environment=environment,
        outputs=outputs)


def _journal_stdout(run: Path, phase: str, name: str) -> Path:
    names = s0.PREPARE_STEPS if phase == "prepare" else s0.FINISH_STEPS
    if phase not in {"prepare", "finish"} or name not in names:
        _fail(f"journal stdout stage is absent: {phase}/{name}")
    ordinal = names.index(name) + 1
    return run / f"{phase}_journal" / f"{ordinal:02d}_{name}.stdout.bin"


def _common_environment(args: argparse.Namespace) -> dict[str, str]:
    path_candidates = [
        args.base_python.parent, args.nvidia_smi.parent, args.nvcc.parent,
        args.make.parent, args.cxx.parent, args.git.parent, args.uname.parent,
        args.ldd.parent, args.pkg_config.parent, args.strace.parent,
        args.cuda_prefix / "bin",
    ]
    path_rows: list[str] = []
    for path in path_candidates:
        resolved = path.resolve(strict=True)
        if not resolved.is_dir():
            _fail(f"derived PATH member is not a directory: {resolved}")
        if str(resolved) not in path_rows:
            path_rows.append(str(resolved))
    value = {
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PATH": os.pathsep.join(path_rows),
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }
    if args.runtime_library_directory:
        value["LD_LIBRARY_PATH"] = os.pathsep.join(
            str(path) for path in args.runtime_library_directory)
    return value


def _output_path_set(config: Mapping[str, Any]) -> set[str]:
    paths: set[str] = set()
    for phase in ("prepare_steps", "finish_steps"):
        for step in config[phase]:
            for row in step["outputs"]:
                path = str(row["path"])
                if path in paths:
                    _fail(f"generated output path is duplicated: {path}")
                paths.add(path)
    return paths


def _assert_no_embedded_or_manual_dynamic(config: Mapping[str, Any]) -> None:
    allowed = set(s0.DYNAMIC_TOKENS)
    named_link_inputs = {
        "cuda=${LDD_CUDA}": "${LDD_CUDA}",
        "nvrtc=${LDD_NVRTC}": "${LDD_NVRTC}",
        "geos_c=${LDD_GEOS_C}": "${LDD_GEOS_C}",
    }
    observed: list[str] = []
    observed_by_stage: dict[str, set[str]] = {}
    for phase in ("prepare_steps", "finish_steps"):
        for step in config[phase]:
            stage_tokens: set[str] = set()
            for argument in step["args"]:
                if "${" in argument:
                    if argument in allowed:
                        token = argument
                    elif argument in named_link_inputs:
                        token = named_link_inputs[argument]
                    else:
                        _fail(f"unsupported or embedded dynamic input: {argument}")
                    observed.append(token)
                    stage_tokens.add(token)
            observed_by_stage[str(step["name"])] = stage_tokens
    required = {
        "${OBSERVED_CC}", "${OBSERVED_SM}",
        "${LDD_CUDA}", "${LDD_NVRTC}", "${LDD_GEOS_C}",
        "${COMBINED_PLAN_FILE_SHA256}",
        "${RELATION_ARTIFACT}", "${RELATION_AUTHORITY}",
        "${RELATION_DEPLOYMENT_ID}", "${RELATION_EXECUTABLE_IDENTITY}",
        "${TRIANGLE_ARTIFACT}", "${TRIANGLE_AUTHORITY}",
        "${TRIANGLE_DEPLOYMENT_ID}", "${TRIANGLE_EXECUTABLE_IDENTITY}",
        "${TRUST_PACKAGE_SEQ1}", "${TRUST_PACKAGE_SEQ2}",
        "${TRUST_HEAD_SEQ2}",
    }
    if not required <= set(observed):
        _fail(f"generated config omits dynamic authorities: {sorted(required-set(observed))}")
    required_by_stage = {
        "native_build": {"${OBSERVED_SM}"},
        "native_custody_capture": {
            "${LDD_CUDA}", "${LDD_NVRTC}", "${LDD_GEOS_C}"},
        "candidate_seed1": {"${OBSERVED_CC}"},
        "candidate_seed777": {"${OBSERVED_CC}"},
        "rtdl_clean_install": {
            "${TRUST_PACKAGE_SEQ1}", "${TRUST_PACKAGE_SEQ2}",
            "${TRUST_HEAD_SEQ2}"},
        "combined_runtime_run": {"${COMBINED_PLAN_FILE_SHA256}"},
        "header_projection": {"${OBSERVED_SM}"},
        "matched_ptx": {"${OBSERVED_CC}"},
        "rtdl_kat": {
            "${RELATION_ARTIFACT}", "${RELATION_AUTHORITY}",
            "${RELATION_DEPLOYMENT_ID}", "${RELATION_EXECUTABLE_IDENTITY}",
            "${TRIANGLE_ARTIFACT}", "${TRIANGLE_AUTHORITY}",
            "${TRIANGLE_DEPLOYMENT_ID}", "${TRIANGLE_EXECUTABLE_IDENTITY}",
            "${TRUST_PACKAGE_SEQ2}", "${TRUST_HEAD_SEQ2}"},
        "target_runtime_manifest": {
            "${RELATION_ARTIFACT}", "${RELATION_AUTHORITY}",
            "${RELATION_DEPLOYMENT_ID}", "${TRIANGLE_ARTIFACT}",
            "${TRIANGLE_AUTHORITY}", "${TRIANGLE_DEPLOYMENT_ID}",
            "${TRUST_PACKAGE_SEQ2}", "${TRUST_HEAD_SEQ2}"},
    }
    for name, stage_required in required_by_stage.items():
        missing = stage_required - observed_by_stage.get(name, set())
        if missing:
            _fail(f"stage {name} omits dynamic inputs: {sorted(missing)}")


def _normalize_inputs(args: argparse.Namespace) -> argparse.Namespace:
    for name in (
            "source_root", "offline_wheelhouse_root",
            "virtualenv_bootstrap_root", "cuda_prefix"):
        setattr(args, name, _directory(getattr(args, name), name))
    for name in (
            "source_packet", "source_packet_manifest",
            "private_scan_authority", "public_trust_root", "base_python",
            "optix_headers_bundle", "pyoptix_wheel_build_receipt",
            "nvidia_smi", "nvcc", "make",
            "cxx", "git", "uname", "ldd", "pkg_config", "strace",
            "manual_judgement", "engineering_effort_ledger"):
        executable = name in {
            "base_python", "nvidia_smi", "nvcc", "make", "cxx", "git",
            "uname", "ldd", "pkg_config", "strace"}
        setattr(args, name, _regular(
            getattr(args, name), name, executable=executable))
    args.run_root = _absolute(args.run_root, "run_root", must_exist=False)
    args.output = _absolute(args.output, "output", must_exist=False)
    source_root = args.source_root.resolve(strict=True)
    try:
        args.run_root.relative_to(source_root)
    except ValueError:
        pass
    else:
        _fail("run root must be outside the exact source checkout")
    try:
        args.output.relative_to(source_root)
    except ValueError:
        pass
    else:
        _fail("configuration output must be outside the exact source checkout")
    try:
        args.output.relative_to(args.run_root)
    except ValueError:
        pass
    else:
        _fail("configuration output must be outside the create-only run root")
    if args.run_root.exists() or args.run_root.is_symlink():
        _fail("run root is create-only and must not exist")
    if args.output.exists() or args.output.is_symlink():
        _fail("configuration output is create-only")
    for name in ("runtime_library_directory", "direct_library_directory"):
        rows = [_directory(path, name) for path in getattr(args, name)]
        if len({str(path) for path in rows}) != len(rows):
            _fail(f"{name} contains a duplicate")
        setattr(args, name, rows)
    if not args.direct_library_directory:
        args.direct_library_directory = list(args.runtime_library_directory)
    if not SHA256_RE.fullmatch(args.private_key_sha256):
        _fail("private-key SHA-256 is not lowercase 256-bit hex")
    if not SHA256_RE.fullmatch(args.private_scan_authority_sha256) \
            or _sha_file(args.private_scan_authority) \
            != args.private_scan_authority_sha256:
        _fail("private-scan authority SHA-256 differs")
    return args


def build_config(args: argparse.Namespace) -> dict[str, object]:
    args = _normalize_inputs(args)
    source = args.source_root
    run = args.run_root
    trust_root_scope, trust_root_file_sha256 = _trust_root_identity(
        args.public_trust_root)
    qualification_verifier_args = [] if (
        trust_root_scope == FORMAL_MEASUREMENT_TRUST_SCOPE
    ) else [
        "--qualification-only-expected-trust-root-file-sha256",
        trust_root_file_sha256,
    ]
    commit, tree, epoch = _source_identity(source, args.git)
    _packet_identity(
        args.source_packet, args.source_packet_manifest, commit, tree)
    manual = _registered_source_file(
        source, args.manual_judgement, MANUAL_AUTHORITY_RELATIVE,
        "manual judgement")
    engineering = _registered_source_file(
        source, args.engineering_effort_ledger, ENGINEERING_LEDGER_RELATIVE,
        "engineering-effort ledger")
    goal5799 = source / Path(*PurePosixPath(GOAL5799_BINDING_RELATIVE).parts)
    if goal5799.is_symlink() or not goal5799.is_file():
        _fail("registered Goal5799 binding is absent")
    source_files = {role: _source_file(source, role) for role in SOURCE_PATHS}
    wheel_rows, wheelhouse_manifest = _wheelhouse_rows(
        args.offline_wheelhouse_root)
    pyoptix_rows = [
        row for row in wheel_rows if row["distribution"] == "pyoptix"]
    if len(pyoptix_rows) != 1:
        _fail("wheelhouse must contain exactly one PyOptiX wheel")
    pyoptix_wheel = Path(pyoptix_rows[0]["path"])
    python_version = _python_version(args.base_python)
    if python_version != (3, 12):
        _fail("Goal5802 target runtime requires exact CPython 3.12")

    pyoptix_provenance = run / "prepare/pyoptix_build_provenance"
    pyoptix_provenance_receipt = pyoptix_provenance / "receipt.json"
    optix_sdk = pyoptix_provenance / "optix_headers"
    optix_include = optix_sdk / "include"
    cuda_include = (args.cuda_prefix / "include").resolve(strict=True)
    if not cuda_include.is_dir():
        _fail("CUDA prefix must expose an include directory")
    nvrtc_library = _find_cuda_runtime_library(args.cuda_prefix, "libnvrtc")
    nvrtc_builtins = _find_cuda_runtime_library(
        args.cuda_prefix, "libnvrtc-builtins")
    for directory in (nvrtc_library.parent, nvrtc_builtins.parent):
        resolved = directory.resolve(strict=True)
        if resolved not in args.runtime_library_directory:
            args.runtime_library_directory.insert(0, resolved)
        if resolved not in args.direct_library_directory:
            args.direct_library_directory.insert(0, resolved)

    environment = _common_environment(args)
    prepare: dict[str, dict[str, object]] = {}
    finish: dict[str, dict[str, object]] = {}

    source_verify_receipt = run / "prepare/source_packet_verify/receipt.json"
    prepare["source_packet_verify"] = _python_step(
        "source_packet_verify", args.base_python,
        [
            "--packet", str(args.source_packet),
            "--manifest", str(args.source_packet_manifest),
            "--receipt", str(source_verify_receipt),
            "--private-scan-authority", str(args.private_scan_authority),
            "--private-scan-authority-sha256",
            args.private_scan_authority_sha256,
        ], environment, [(source_verify_receipt, "file")])

    # Preserve the historical build receipt byte-for-byte and make its exact
    # pinned OptiX header checkout available on this target.  The successor
    # receipt records target materialization; it never rewrites where the old
    # wheel was built.
    prepare["pyoptix_build_provenance_materialize"] = _python_step(
        "pyoptix_build_provenance_materialize", args.base_python,
        [
            "materialize", "--git", str(args.git),
            "--headers-bundle", str(args.optix_headers_bundle),
            "--original-build-receipt",
            str(args.pyoptix_wheel_build_receipt),
            "--pyoptix-wheel", str(pyoptix_wheel),
            "--output-directory", str(pyoptix_provenance),
        ], environment, [(pyoptix_provenance, "directory")])
    prepare["pyoptix_build_provenance_verify"] = _python_step(
        "pyoptix_build_provenance_verify", args.base_python,
        ["verify", "--receipt", str(pyoptix_provenance_receipt)],
        environment,
        [(_journal_stdout(
            run, "prepare", "pyoptix_build_provenance_verify"), "file")])

    # The exact offline PyOptiX stage names are checked against the
    # orchestrator below.  The old network helper is never emitted.
    pyoptix_root = run / "prepare/pyoptix_runtime"
    pyoptix_plan = run / "prepare/pyoptix_runtime_plan.json"
    pyoptix_python = _venv_python(pyoptix_root)
    prepare["pyoptix_offline_plan"] = _python_step(
        "pyoptix_offline_plan", args.base_python,
        [
            "plan", "--output-directory", str(pyoptix_root),
            "--base-python", str(args.base_python),
            "--virtualenv-bootstrap-root", str(args.virtualenv_bootstrap_root),
            "--wheelhouse-root", str(args.offline_wheelhouse_root),
            "--plan-output", str(pyoptix_plan),
        ], environment, [(pyoptix_plan, "file")])
    prepare["pyoptix_offline_run"] = _python_step(
        "pyoptix_offline_run", args.base_python,
        ["run", "--plan", str(pyoptix_plan)], environment,
        [(pyoptix_root, "directory")])
    # Verification uses the runtime it has just installed, never the base
    # interpreter.  Its declared output is the orchestrator-owned stdout.
    prepare["pyoptix_offline_verify"] = _python_step(
        "pyoptix_offline_verify", pyoptix_python,
        ["verify", "--output-directory", str(pyoptix_root)], environment,
        [(_journal_stdout(
            run, "prepare", "pyoptix_offline_verify"), "file")])

    target_observation = run / "prepare/target_observation.json"
    prepare["target_observation"] = _python_step(
        "target_observation", pyoptix_python,
        ["--nvidia-smi", str(args.nvidia_smi), "--nvcc", str(args.nvcc),
         "--output", str(target_observation)], environment,
        [(target_observation, "file")])

    origin = run / "prepare/origin_authority"
    prepare["origin_authority"] = _python_step(
        "origin_authority", pyoptix_python,
        ["--repository", str(source), "--commit", commit,
         "--output-directory", str(origin)], environment,
        [(origin, "directory")])

    native_root = run / "prepare/native_build"
    native = native_root / "native/librtdl_optix.so"
    prepare["native_build"] = _python_step(
        "native_build", pyoptix_python,
        [
            "--source-root", str(source), "--output-root", str(native_root),
            "--optix-prefix", str(optix_sdk),
            "--cuda-prefix", str(args.cuda_prefix),
            "--build-id", NATIVE_BUILD_ID, "--cuda-arch", "${OBSERVED_SM}",
            "--make", str(args.make), "--nvcc", str(args.nvcc),
            "--host-cxx", str(args.cxx), "--git", str(args.git),
            "--uname", str(args.uname), "--ldd", str(args.ldd),
            "--pkg-config", str(args.pkg_config),
        ], environment, [(native_root, "directory")])

    custody = run / "prepare/native_custody"
    tool_args: list[str] = []
    for name, path in (
            ("nvcc", args.nvcc), ("make", args.make),
            ("host_cxx", args.cxx), ("git", args.git),
            ("uname", args.uname), ("ldd", args.ldd),
            ("pkg_config", args.pkg_config)):
        tool_args.extend(["--tool", f"{name}={path}"])
    link_args = [
        "--link-input", "cuda=${LDD_CUDA}",
        "--link-input", "nvrtc=${LDD_NVRTC}",
        "--link-input", "geos_c=${LDD_GEOS_C}",
    ]
    receipt_args: list[str] = []
    for name, filename in (
            ("nvcc_version", "nvcc_version.txt"),
            ("make_version", "make_version.txt"),
            ("host_cxx_version", "host_cxx_version.txt"),
            ("git_version", "git_version.txt"),
            ("pkg_config_version", "pkg_config_version.txt"),
            ("uname", "uname.txt"), ("native_ldd", "native_ldd.txt")):
        receipt_args.extend([
            "--tool-receipt",
            f"{name}={native_root / 'tool_receipts' / filename}"])
    prepare["native_custody_capture"] = _python_step(
        "native_custody_capture", pyoptix_python,
        [
            "--output", str(custody), "--source-root", str(source),
            "--source-commit", commit, "--origin-commit", commit,
            "--origin-tree", tree,
            "--origin-commit-object", str(origin / "origin_commit_object.bin"),
            "--origin-inventory", str(origin / "origin_full_git_ls_tree_z.bin"),
            "--native", str(native), "--build-cwd", str(source),
            "--build-source-root", str(source),
            "--build-command", str(native_root / "build_command.txt"),
            "--build-stdout", str(native_root / "build_stdout.txt"),
            "--build-stderr", str(native_root / "build_stderr.txt"),
            "--build-exit-code", str(native_root / "build_exit_code.txt"),
            "--dependency-file", str(native_root / "rtdl_optix_dependencies.d"),
            "--build-environment", str(native_root / "build_environment.json"),
            *tool_args, *link_args, *receipt_args,
        ], environment, [(custody, "directory")])
    prepare["native_custody_verify"] = _python_step(
        "native_custody_verify", pyoptix_python, [str(custody)], environment,
        [(_journal_stdout(
            run, "prepare", "native_custody_verify"), "file")])

    candidates: dict[int, Path] = {
        1: run / "prepare/candidates/seed1",
        777: run / "prepare/candidates/seed777",
    }
    for seed, name in ((1, "candidate_seed1"), (777, "candidate_seed777")):
        seed_environment = {**environment, "PYTHONHASHSEED": str(seed)}
        prepare[name] = _python_step(
            name, pyoptix_python,
            [
                "build", "--native", str(native),
                "--optix-include", str(optix_include),
                "--cuda-include", str(cuda_include),
                "--optix-sdk", OPTIX_SDK_VERSION,
                "--compute-capability", "${OBSERVED_CC}",
                "--deployment-generation", "v3",
                "--relation-minimum-overlap-f32", "1.0",
                "--proof", str(source_files["callback_proof"]),
                "--output", str(candidates[seed]),
            ], seed_environment, [(candidates[seed], "directory")])

    wheel_root = run / "finish/rtdl_wheel"
    rtdl_wheel = wheel_root / RTDL_WHEEL_NAME
    finish["rtdl_wheel_double_seed"] = _python_step(
        "rtdl_wheel_double_seed", pyoptix_python,
        [
            "--source-root", str(source), "--git", str(args.git),
            "--python", str(pyoptix_python), "--commit", commit,
            "--virtualenv-bootstrap-root", str(args.virtualenv_bootstrap_root),
            "--tree", tree, "--source-date-epoch", str(epoch),
            "--output", str(wheel_root),
        ], {**environment, "SOURCE_DATE_EPOCH": str(epoch)},
        [(wheel_root, "directory")])

    clean_root = run / "finish/rtdl_clean_install"
    finish["rtdl_clean_install"] = _python_step(
        "rtdl_clean_install", pyoptix_python,
        [
            "--output-directory", str(clean_root),
            "--base-python", str(args.base_python),
            "--virtualenv-bootstrap-root", str(args.virtualenv_bootstrap_root),
            "--probe", str(source_files["clean_probe"]),
            "--wheel", str(rtdl_wheel), "--source-root", str(source),
            "--candidate-manifest", str(
                candidates[1] / "candidate_manifest.json"),
            "--trust-root", str(args.public_trust_root),
            "--trust-head", "${TRUST_HEAD_SEQ2}",
            "--trust-predecessor-package", "${TRUST_PACKAGE_SEQ1}",
            "--trust-package", "${TRUST_PACKAGE_SEQ2}",
            "--native", str(native), "--host-cc", str(args.cxx),
            "--cuda-include", str(cuda_include),
            "--nvrtc-library", str(nvrtc_library),
            "--nvrtc-trap-source", str(source_files["nvrtc_trap_source"]),
            "--nvrtc-kat-source", str(source_files["nvrtc_kat_source"]),
        ], environment, [(clean_root, "directory")])
    finish["rtdl_clean_install_verify"] = _python_step(
        "rtdl_clean_install_verify", pyoptix_python, [
            str(clean_root),
            *qualification_verifier_args,
        ],
        environment,
        [(_journal_stdout(
            run, "finish", "rtdl_clean_install_verify"), "file")])

    combined_plan = run / "finish/combined_runtime_plan.json"
    combined_root = run / "finish/combined_runtime"
    combined_python = _venv_python(combined_root)
    combined_wheels: list[str] = []
    for row in wheel_rows:
        role = str(row["distribution"]).replace("-", "_")
        combined_wheels.extend(["--wheel", f"{role}={row['path']}"])
    combined_wheels.extend(["--wheel", f"rtdl={rtdl_wheel}"])
    finish["combined_runtime_plan"] = _python_step(
        "combined_runtime_plan", pyoptix_python,
        [
            "plan", "--output-directory", str(combined_root),
            "--base-python", str(args.base_python),
            "--virtualenv-bootstrap-root", str(args.virtualenv_bootstrap_root),
            *combined_wheels, "--plan-output", str(combined_plan),
        ], environment, [(combined_plan, "file")])
    finish["combined_runtime_run"] = _python_step(
        "combined_runtime_run", pyoptix_python,
        ["run", "--plan", str(combined_plan),
         "--expected-plan-file-sha256", "${COMBINED_PLAN_FILE_SHA256}"],
        environment,
        [(combined_root, "directory")])
    finish["combined_runtime_verify"] = _python_step(
        "combined_runtime_verify", combined_python,
        ["verify", "--output-directory", str(combined_root)], environment,
        [(_journal_stdout(
            run, "finish", "combined_runtime_verify"), "file")])

    product_binding = run / "finish/product_binding.json"
    finish["product_binding"] = _python_step(
        "product_binding", combined_python,
        [
            "--clean-root", str(clean_root), "--source-commit", commit,
            "--source-tree", tree, "--repository-root", str(source),
            "--standalone-verifier", str(source_files["clean_verifier"]),
            *qualification_verifier_args,
            "--native-custody-root", str(custody),
            "--standalone-native-custody-verifier",
            str(source_files["native_verifier"]),
            "--output", str(product_binding),
        ], environment, [(product_binding, "file")])

    freeze_inputs = run / "finish/freeze_inputs"
    finish["freeze_inputs"] = _python_step(
        "freeze_inputs", combined_python,
        ["export", "--root", str(source),
         "--output-directory", str(freeze_inputs)], environment,
        [(freeze_inputs, "directory")])

    forecast = run / "finish/successor_forecast.json"
    finish["successor_forecast"] = _python_step(
        "successor_forecast", combined_python,
        [
            "--root", str(source), "--product-binding", str(product_binding),
            "--clean-install-root", str(clean_root),
            "--native-custody-root", str(custody),
            "--standalone-clean-verifier", str(source_files["clean_verifier"]),
            *qualification_verifier_args,
            "--standalone-native-custody-verifier",
            str(source_files["native_verifier"]),
            "--workload-authority", str(freeze_inputs / "workload_authority.json"),
            "--operation-contract", str(freeze_inputs / "operation_contract.json"),
            "--comparative-schedule", str(
                freeze_inputs / "comparative_schedule_432.json"),
            "--build-cold-schedule", str(
                freeze_inputs / "build_cold_schedule_72.json"),
            "--instrument-source-manifest", str(
                freeze_inputs / "instrument_source_manifest.json"),
            "--goal5799-binding", str(goal5799),
            "--manual-judgement", str(manual), "--output", str(forecast),
        ], environment, [(forecast, "file")])

    freeze = run / "final/freeze.json"
    finish["local_freeze"] = _python_step(
        "local_freeze", combined_python,
        [
            "--root", str(source), "--product-binding", str(product_binding),
            "--engineering-effort-ledger", str(engineering),
            "--successor-forecast", str(forecast), "--output", str(freeze),
        ], environment, [(freeze, "file")])
    finish["local_freeze_verify"] = _python_step(
        "local_freeze_verify", combined_python,
        [
            "--root", str(source), "--freeze", str(freeze),
            "--clean-install-root", str(clean_root),
            "--standalone-clean-install-verifier",
            str(source_files["clean_verifier"]),
            *qualification_verifier_args,
            "--native-custody-root", str(custody),
            "--standalone-native-custody-verifier",
            str(source_files["native_verifier"]),
        ], environment,
        [(_journal_stdout(
            run, "finish", "local_freeze_verify"), "file")])

    projection = run / "finish/header_projection"
    projection_receipt = run / "finish/header_projection_receipt.json"
    projected_optix = _projected_root(projection, optix_include)
    projected_cuda = _projected_root(projection, cuda_include)
    finish["header_projection"] = _python_step(
        "header_projection", combined_python,
        [
            "--nvcc", str(args.nvcc), "--cxx", str(args.cxx),
            "--device-source", str(source_files["device_source"]),
            "--compaction-source", str(source_files["compaction_source"]),
            "--direct-source", str(source_files["direct_source"]),
            "--optix-include", str(optix_include),
            "--cuda-include", str(cuda_include),
            "--compute-capability", "${OBSERVED_SM}",
            "--projection-root", str(projection),
            "--receipt", str(projection_receipt),
        ], environment,
        [(projection, "directory"), (projection_receipt, "file")])
    finish["header_projection_verify"] = _python_step(
        "header_projection_verify", combined_python,
        ["--receipt", str(projection_receipt),
         "--projection-root", str(projection), "--mode", "full"],
        environment,
        [(_journal_stdout(
            run, "finish", "header_projection_verify"), "file")])

    direct_recipe = run / "finish/direct_recipe.json"
    recipe_args: list[str] = []
    for directory in args.direct_library_directory:
        recipe_args.extend(["--library-directory", str(directory)])
    finish["direct_recipe"] = _python_step(
        "direct_recipe", combined_python,
        [*recipe_args, "--output", str(direct_recipe)], environment,
        [(direct_recipe, "file")])

    direct_worker = run / "finish/direct_scalar_worker"
    direct_receipt = run / "finish/direct_worker_build_receipt.json"
    finish["direct_worker"] = _python_step(
        "direct_worker", combined_python,
        [
            "--recipe", str(direct_recipe), "--cxx", str(args.cxx),
            "--direct-source", str(source_files["direct_source"]),
            "--optix-include", str(projected_optix),
            "--cuda-include", str(projected_cuda),
            "--output", str(direct_worker), "--receipt", str(direct_receipt),
        ], environment, [(direct_worker, "file"), (direct_receipt, "file")])

    replay = run / "finish/matched_ptx_replay"
    matched_ptx = run / "finish/matched_device.ptx"
    compaction_cubin = run / "finish/relation_compaction.cubin"
    matched_receipt = run / "finish/matched_ptx_receipt.json"
    finish["matched_ptx"] = _python_step(
        "matched_ptx", combined_python,
        [
            "--device-source", str(source_files["device_source"]),
            "--compaction-source", str(source_files["compaction_source"]),
            "--optix-include", str(projected_optix),
            "--cuda-include", str(projected_cuda),
            "--original-optix-include", str(optix_include),
            "--original-cuda-include", str(cuda_include),
            "--header-projection-root", str(projection),
            "--header-projection-receipt", str(projection_receipt),
            "--strace", str(args.strace), "--replay-root", str(replay),
            "--compute-capability", "${OBSERVED_CC}",
            "--output", str(matched_ptx),
            "--compaction-output", str(compaction_cubin),
            "--receipt", str(matched_receipt),
        ], environment,
        [(replay, "directory"), (matched_ptx, "file"),
         (compaction_cubin, "file"), (matched_receipt, "file")])

    direct_kat = run / "finish/direct_operation_kat.json"
    finish["direct_kat"] = _python_step(
        "direct_kat", combined_python,
        ["--worker", str(direct_worker),
         "--direct-source", str(source_files["direct_source"]),
         "--ptx", str(matched_ptx),
         "--compaction-cubin", str(compaction_cubin),
         "--output", str(direct_kat)], environment,
        [(direct_kat, "file")])

    pyoptix_kat = run / "finish/pyoptix_operation_kat.json"
    finish["pyoptix_kat"] = _python_step(
        "pyoptix_kat", combined_python,
        ["--ptx", str(matched_ptx),
         "--compaction-cubin", str(compaction_cubin),
         "--output", str(pyoptix_kat)], environment,
        [(pyoptix_kat, "file")])

    rtdl_kat = run / "finish/rtdl_operation_kat.json"
    combined_site = combined_root / "venv" / "lib" \
        / f"python{python_version[0]}.{python_version[1]}" / "site-packages"
    rtdsl_init = combined_site / "rtdsl/__init__.py"
    rtdlexe_module = combined_site / "rtdsl/v4_rtdlexe.py"
    finish["rtdl_kat"] = _python_step(
        "rtdl_kat", combined_python,
        [
            "--relation-artifact", "${RELATION_ARTIFACT}",
            "--relation-authority", "${RELATION_AUTHORITY}",
            "--relation-deployment-id", "${RELATION_DEPLOYMENT_ID}",
            "--relation-executable-identity-sha256",
            "${RELATION_EXECUTABLE_IDENTITY}",
            "--triangle-artifact", "${TRIANGLE_ARTIFACT}",
            "--triangle-authority", "${TRIANGLE_AUTHORITY}",
            "--triangle-deployment-id", "${TRIANGLE_DEPLOYMENT_ID}",
            "--triangle-executable-identity-sha256",
            "${TRIANGLE_EXECUTABLE_IDENTITY}",
            "--trust-root", str(args.public_trust_root),
            "--trust-head", "${TRUST_HEAD_SEQ2}",
            "--trust-package", "${TRUST_PACKAGE_SEQ2}",
            "--native-library", str(native),
            "--rtdsl-init", str(rtdsl_init),
            "--rtdlexe-module", str(rtdlexe_module),
            "--output", str(rtdl_kat),
        ], environment, [(rtdl_kat, "file")])

    host_runtime = run / "finish/host_runtime_provenance.json"
    finish["host_runtime"] = _python_step(
        "host_runtime", combined_python, [str(host_runtime)], environment,
        [(host_runtime, "file")])

    # The operation KAT and every formal Python arm run from the combined
    # environment.  Bind the manifest's loaded-module paths to that same
    # interpreter; the earlier PyOptiX-only environment remains provenance
    # and clean-install evidence, not the final loaded-module authority.
    pyoptix_initializer, pyoptix_extension = _wheel_member_paths(
        pyoptix_wheel, python_version, combined_root)
    pyoptix_clean_receipt = (
        pyoptix_root / "offline_pyoptix_clean_install_receipt.json")
    runtime_manifest = run / "final/runtime_manifest.json"
    manifest_files: dict[str, str] = {
        "clean_python": str(combined_python),
        "direct_scalar_worker": str(direct_worker),
        "direct_scalar_source": str(source_files["direct_source"]),
        "direct_build_recipe": str(direct_recipe),
        "direct_worker_build_receipt": str(direct_receipt),
        "direct_operation_kat": str(direct_kat),
        "rtdl_operation_kat": str(rtdl_kat),
        "device_source": str(source_files["device_source"]),
        "compaction_source": str(source_files["compaction_source"]),
        "matched_ptx": str(matched_ptx),
        "compaction_cubin": str(compaction_cubin),
        "matched_ptx_prepare_receipt": str(matched_receipt),
        "callback_proof": str(source_files["callback_proof"]),
        "nvrtc_library": str(nvrtc_library),
        "nvrtc_builtins": str(nvrtc_builtins),
        "cxx_compiler": str(args.cxx), "nvcc": str(args.nvcc),
        "nvidia_smi": str(args.nvidia_smi),
        "target_observation_receipt": str(target_observation),
        "rtdl_wheel": str(rtdl_wheel),
        "pyoptix_wheel": str(pyoptix_wheel),
        "pyoptix_wheel_build_receipt": str(pyoptix_provenance_receipt),
        "pyoptix_clean_install_receipt": str(pyoptix_clean_receipt),
        "goal5800_v7_source": str(source_files["goal5800_source"]),
        "pyoptix_operation_kat": str(pyoptix_kat),
        "host_runtime_provenance": str(host_runtime),
        "header_projection_receipt": str(projection_receipt),
        "combined_runtime_receipt": str(
            combined_root / "combined_runtime_receipt.json"),
        "pyoptix_initializer": str(pyoptix_initializer),
        "pyoptix_extension": str(pyoptix_extension),
        "rtdsl_init": str(rtdsl_init), "rtdlexe_module": str(rtdlexe_module),
        "native_library": str(native), "trust_root": str(args.public_trust_root),
        "trust_head": "${TRUST_HEAD_SEQ2}",
        "trust_package": "${TRUST_PACKAGE_SEQ2}",
        "relation_artifact": "${RELATION_ARTIFACT}",
        "relation_authority": "${RELATION_AUTHORITY}",
        "triangle_artifact": "${TRIANGLE_ARTIFACT}",
        "triangle_authority": "${TRIANGLE_AUTHORITY}",
    }
    manifest_directories = {
        "optix_include": str(projected_optix),
        "cuda_include": str(projected_cuda),
        "optix_sdk": str(optix_sdk),
        "header_projection": str(projection),
    }
    manifest_args: list[str] = []
    for role in (
            "clean_python", "direct_scalar_worker", "direct_scalar_source",
            "direct_build_recipe", "direct_worker_build_receipt",
            "direct_operation_kat", "rtdl_operation_kat", "device_source",
            "compaction_source", "matched_ptx", "compaction_cubin",
            "matched_ptx_prepare_receipt", "callback_proof", "nvrtc_library",
            "nvrtc_builtins", "cxx_compiler", "nvcc", "nvidia_smi",
            "target_observation_receipt", "rtdl_wheel", "pyoptix_wheel",
            "pyoptix_wheel_build_receipt", "pyoptix_clean_install_receipt",
            "goal5800_v7_source", "pyoptix_operation_kat",
            "host_runtime_provenance", "header_projection_receipt",
            "combined_runtime_receipt",
            "pyoptix_initializer", "pyoptix_extension", "rtdsl_init",
            "rtdlexe_module", "native_library", "trust_root", "trust_head",
            "trust_package", "relation_artifact", "relation_authority",
            "triangle_artifact", "triangle_authority"):
        manifest_args.extend([f"--{role.replace('_', '-')}", manifest_files[role]])
    for role in ("optix_include", "cuda_include", "optix_sdk",
                 "header_projection"):
        manifest_args.extend([
            f"--{role.replace('_', '-')}", manifest_directories[role]])
    manifest_args.extend([
        "--relation-deployment-id", "${RELATION_DEPLOYMENT_ID}",
        "--triangle-deployment-id", "${TRIANGLE_DEPLOYMENT_ID}",
        "--output", str(runtime_manifest),
    ])
    finish["target_runtime_manifest"] = _python_step(
        "target_runtime_manifest", combined_python, manifest_args,
        environment, [(runtime_manifest, "file")])

    dual = run / "final/dual_validation.json"
    finish["dual_validation"] = _python_step(
        "dual_validation", combined_python,
        ["--root", str(source), "--freeze", str(freeze),
         "--runtime-manifest", str(runtime_manifest), "--output", str(dual)],
        environment, [(dual, "file")])

    plan = run / "final/plan.json"
    finish["plan_only"] = _step(
        "plan_only", runner="python_module", target=s0.PLAN_ONLY_MODULE,
        interpreter=combined_python,
        args=["--freeze", str(freeze), "--root", str(source),
              "--plan-output", str(plan)], environment=environment,
        outputs=[(plan, "file")])

    missing_prepare = [name for name in s0.PREPARE_STEPS if name not in prepare]
    missing_finish = [name for name in s0.FINISH_STEPS if name not in finish]
    if missing_prepare or missing_finish:
        _fail(
            "orchestrator stage set is not supported by this builder; "
            f"prepare={missing_prepare}, finish={missing_finish}")
    if any(name not in s0.PREPARE_STEPS for name in prepare) \
            or any(name not in s0.FINISH_STEPS for name in finish):
        extra_prepare = sorted(set(prepare) - set(s0.PREPARE_STEPS))
        extra_finish = sorted(set(finish) - set(s0.FINISH_STEPS))
        _fail(
            "builder/orchestrator exact stage set differs; "
            f"extra_prepare={extra_prepare}, extra_finish={extra_finish}")

    config: dict[str, object] = {
        "schema": s0.CONFIG_SCHEMA,
        "source_root": str(source), "source_commit": commit,
        "source_tree": tree, "git": str(args.git),
        "python": str(args.base_python), "run_root": str(run),
        "source_packet_manifest": str(args.source_packet_manifest),
        "public_trust_root": str(args.public_trust_root),
        "trust_root_scope": trust_root_scope,
        "trust_root_file_sha256": trust_root_file_sha256,
        "private_key_sha256": args.private_key_sha256,
        "deployment_generation": "v3", "candidate_seeds": [1, 777],
        "wheel_seeds": [1, 777], "relation_minimum_overlap_f32": 1.0,
        "prepare_steps": [prepare[name] for name in s0.PREPARE_STEPS],
        "finish_steps": [finish[name] for name in s0.FINISH_STEPS],
        "candidate_manifests": {
            "seed1": str(candidates[1] / "candidate_manifest.json"),
            "seed777": str(candidates[777] / "candidate_manifest.json"),
        },
        "final_outputs": {
            "freeze": str(freeze), "runtime_manifest": str(runtime_manifest),
            "dual_validation": str(dual), "plan": str(plan),
        },
        "claim_boundary": {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "execution_authority_consumed": False,
            "gpu_use": "UNTIMED_TARGET_OBSERVATION_AND_OPERATION_KATS_ONLY",
            "retry_resume_replacement_allowed": False,
            "target_selection_allowed": False,
        },
    }
    _output_path_set(config)
    _assert_no_embedded_or_manual_dynamic(config)
    return config


def write_config(args: argparse.Namespace) -> dict[str, object]:
    config = build_config(args)
    payload = _canonical(config) + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exercise the production path-based validator before publishing the
    # create-only destination.  A rejected graph leaves no misleading final
    # config byte behind; the private validation file is never an authority.
    descriptor, validation_name = tempfile.mkstemp(
        prefix=".goal5802-pod-s0-config-", suffix=".json",
        dir=args.output.parent)
    validation_path = Path(validation_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        s0._load_config(validation_path, args.run_root.absolute())
    finally:
        try:
            validation_path.unlink()
        except FileNotFoundError:
            pass
    descriptor = os.open(
        args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    receipt = {
        "schema": BUILDER_SCHEMA,
        "status": "PASS__EXACT_CREATE_ONLY_POD_S0_CONFIG",
        "config_path": str(args.output), "config_bytes": len(payload),
        "config_sha256": hashlib.sha256(payload).hexdigest(),
        "prepare_stage_count": len(s0.PREPARE_STEPS),
        "finish_stage_count": len(s0.FINISH_STEPS),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "execution_authority_consumed": False,
    }
    return {**receipt, "receipt_sha256": _digest(receipt)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an exact create-only Goal5802 POD-S0 config")
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--source-packet", type=Path, required=True)
    parser.add_argument("--source-packet-manifest", type=Path, required=True)
    parser.add_argument("--private-scan-authority", type=Path, required=True)
    parser.add_argument(
        "--private-scan-authority-sha256", required=True)
    parser.add_argument("--public-trust-root", type=Path, required=True)
    parser.add_argument("--private-key-sha256", required=True)
    parser.add_argument("--base-python", type=Path, required=True)
    parser.add_argument("--offline-wheelhouse-root", type=Path, required=True)
    parser.add_argument(
        "--virtualenv-bootstrap-root", type=Path, required=True)
    parser.add_argument("--optix-headers-bundle", type=Path, required=True)
    parser.add_argument(
        "--pyoptix-wheel-build-receipt", type=Path, required=True)
    parser.add_argument("--cuda-prefix", type=Path, required=True)
    parser.add_argument("--nvidia-smi", type=Path, required=True)
    parser.add_argument("--nvcc", type=Path, required=True)
    parser.add_argument("--make", type=Path, required=True)
    parser.add_argument("--cxx", type=Path, required=True)
    parser.add_argument("--git", type=Path, required=True)
    parser.add_argument("--uname", type=Path, required=True)
    parser.add_argument("--ldd", type=Path, required=True)
    parser.add_argument("--pkg-config", type=Path, required=True)
    parser.add_argument("--strace", type=Path, required=True)
    parser.add_argument(
        "--runtime-library-directory", action="append", type=Path,
        default=[])
    parser.add_argument(
        "--direct-library-directory", action="append", type=Path,
        default=[])
    parser.add_argument("--manual-judgement", type=Path, required=True)
    parser.add_argument(
        "--engineering-effort-ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    receipt = write_config(args)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigBuildError as error:
        print(f"GOAL5802_POD_S0_CONFIG_REJECTED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
