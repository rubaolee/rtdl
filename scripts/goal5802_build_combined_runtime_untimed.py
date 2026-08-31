#!/usr/bin/env python3
"""Plan, build, and verify the combined Goal5802 Python runtime.

The builder is offline and create-only.  Every wheel is supplied explicitly,
validated, copied, and installed by the target interpreter loading pip through
``runpy`` with site initialization disabled and an exact venv site-packages
target; the
generated ``pip`` launcher is never invoked.  The
tool records every command and every installed distribution file.  It neither
imports the measured arms nor runs GPU work or performance workers.
"""

from __future__ import annotations

import argparse
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from typing import Any, Iterable, Mapping, NoReturn
import zipfile


PLAN_SCHEMA = "rtdl.goal5802.combined_runtime_plan.v1"
RUN_SCHEMA = "rtdl.goal5802.combined_runtime_build_receipt.v1"
FAILURE_SCHEMA = "rtdl.goal5802.combined_runtime_terminal_failure.v1"
SNAPSHOT_SCHEMA = "rtdl.goal5802.combined_runtime_package_snapshot.v1"
ROLE_RE = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")
VIRTUALENV_SEED_DISTRIBUTIONS = frozenset({"pip", "setuptools", "wheel"})
BOOTSTRAP_DISTRIBUTIONS = {
    "distlib": "0.4.3",
    "filelock": "3.32.4",
    "platformdirs": "4.11.4",
    "virtualenv": "20.35.4",
}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class CombinedRuntimeError(RuntimeError):
    """Fail-closed combined-runtime error."""


def _fail(message: str) -> NoReturn:
    raise CombinedRuntimeError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _normalize_distribution(name: str) -> str:
    normalized = re.sub(r"[-_.]+", "-", name).lower()
    if not normalized or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        _fail(f"invalid distribution name: {name!r}")
    return normalized


def _write_create_only(path: Path, payload: bytes, *, mode: int = 0o644) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _strict_json_bytes(payload: bytes, label: str) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                _fail(f"{label} has duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=no_duplicates,
            parse_constant=lambda value: _fail(
                f"{label} has non-finite JSON value: {value}"),
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise CombinedRuntimeError(f"{label} is not UTF-8 JSON") from error
    if payload != _canonical(value) + b"\n":
        _fail(f"{label} is not exact canonical JSON plus LF")
    return value


def _strict_json(path: Path, label: str) -> Any:
    if path.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        metadata = path.stat()
        payload = path.read_bytes()
    except OSError as error:
        raise CombinedRuntimeError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    return _strict_json_bytes(payload, label)


def _file_record(path: Path, *, allow_symlink: bool) -> dict[str, object]:
    supplied = path.expanduser().absolute()
    if supplied.is_symlink() and not allow_symlink:
        _fail(f"input may not be a symlink: {supplied}")
    try:
        resolved = supplied.resolve(strict=True)
        metadata = resolved.stat()
    except OSError as error:
        raise CombinedRuntimeError(f"input is unreadable: {supplied}") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"input is not a regular file: {supplied}")
    record: dict[str, object] = {
        "invocation_path": str(supplied),
        "resolved_path": str(resolved),
        "path_kind": ("SYMLINK_TO_REGULAR_FILE"
                      if supplied.is_symlink() else "REGULAR_FILE"),
        "bytes": metadata.st_size,
        "sha256": _sha_file(resolved),
    }
    if supplied.is_symlink():
        record["symlink_target"] = str(supplied.readlink())
    return record


def _tree_manifest(root: Path) -> list[dict[str, object]]:
    supplied = root.expanduser().absolute()
    if supplied.is_symlink():
        _fail("virtualenv bootstrap root may not be a symlink")
    root = supplied.resolve(strict=True)
    if not root.is_dir():
        _fail("virtualenv bootstrap root is not a directory")
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"virtualenv bootstrap contains a symlink: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha_file(path),
            })
    if not rows or not (root / "virtualenv" / "__main__.py").is_file():
        _fail("virtualenv bootstrap has no virtualenv/__main__.py")
    return rows


def _bootstrap_profile(root: Path, rows: list[dict[str, object]]) \
        -> dict[str, object]:
    """Bind the exact reviewed virtualenv bootstrap dependency profile."""

    root = root.expanduser().resolve(strict=True)
    observed: dict[str, dict[str, object]] = {}
    for path in sorted(root.glob("*.dist-info/METADATA")):
        payload = path.read_bytes()
        metadata = BytesParser().parsebytes(payload)
        raw_name = metadata.get("Name")
        version = metadata.get("Version")
        if not raw_name or not version:
            _fail(f"bootstrap METADATA has no Name/Version: {path}")
        name = _normalize_distribution(raw_name)
        if name in observed:
            _fail(f"bootstrap distribution is duplicated: {name}")
        observed[name] = {
            "distribution": name,
            "metadata_name": raw_name,
            "version": version,
            "metadata_path": path.relative_to(root).as_posix(),
            "metadata_bytes": len(payload),
            "metadata_sha256": _sha(payload),
        }
    if {name: row["version"] for name, row in observed.items()} \
            != BOOTSTRAP_DISTRIBUTIONS:
        _fail("virtualenv bootstrap distribution profile differs")
    return {
        "required_distributions": dict(sorted(BOOTSTRAP_DISTRIBUTIONS.items())),
        "observed_distributions": [observed[name] for name in sorted(observed)],
        "tree_file_count": len(rows),
        "tree_sha256": _digest(rows),
    }


def _base_python_profile(path: Path) -> dict[str, object]:
    """Probe the interpreter without site initialization or third-party imports."""

    code = (
        "import json,platform,struct,sys,sysconfig;"
        "v={'implementation':sys.implementation.name,"
        "'version':[sys.version_info.major,sys.version_info.minor,"
        "sys.version_info.micro],"
        "'cache_tag':sys.implementation.cache_tag,"
        "'pointer_bits':struct.calcsize('P')*8,"
        "'sys_platform':sys.platform,'machine':platform.machine(),"
        "'soabi':sysconfig.get_config_var('SOABI'),"
        "'purelib':sysconfig.get_path('purelib'),"
        "'platlib':sysconfig.get_path('platlib'),"
        "'site_imported':('site' in sys.modules)};"
        "sys.stdout.buffer.write(json.dumps(v,allow_nan=False,"
        "separators=(',',':'),sort_keys=True).encode('utf-8')+b'\\n')"
    )
    command = [str(path), "-I", "-S", "-B", "-P", "-c", code]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1"},
    )
    if completed.returncode != 0 or completed.stderr:
        _fail("base Python isolated ABI probe failed")
    value = _strict_json_bytes(completed.stdout, "base Python ABI probe")
    if not isinstance(value, dict) \
            or value.get("implementation") != "cpython" \
            or value.get("version", [])[:2] != [3, 12] \
            or value.get("cache_tag") != "cpython-312" \
            or value.get("pointer_bits") != 64 \
            or value.get("site_imported") is not False \
            or value.get("sys_platform") not in {"linux", "win32"} \
            or not isinstance(value.get("machine"), str) \
            or not value["machine"] \
            or not all(isinstance(value.get(key), str)
                       and Path(value[key]).is_absolute()
                       for key in ("purelib", "platlib")):
        _fail("base Python is not the required isolated 64-bit CPython 3.12 ABI")
    if value["sys_platform"] == "linux" \
            and (not isinstance(value.get("soabi"), str)
                 or not value["soabi"].startswith("cpython-312-")):
        _fail("Linux base Python SOABI differs from CPython 3.12")
    if value["sys_platform"] == "win32" and value.get("soabi") is not None:
        _fail("Windows base Python SOABI projection differs")
    return {"argv": command, "result": value}


def _wheel_record(role: str, path: Path, ordinal: int) -> dict[str, object]:
    if not ROLE_RE.fullmatch(role):
        _fail(f"wheel role is invalid: {role!r}")
    file_record = _file_record(path, allow_symlink=False)
    resolved = Path(str(file_record["resolved_path"]))
    if resolved.suffix != ".whl":
        _fail(f"wheel input does not end in .whl: {resolved}")
    try:
        with zipfile.ZipFile(resolved) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                _fail(f"wheel contains duplicate members: {resolved.name}")
            files = [info for info in infos if not info.is_dir()]
            for info in infos:
                pure = PurePosixPath(info.filename)
                canonical_name = pure.as_posix() + ("/" if info.is_dir() else "")
                if pure.is_absolute() or ".." in pure.parts \
                        or info.filename != canonical_name:
                    _fail(f"wheel contains an unsafe member: {info.filename}")
            metadata_names = [
                info.filename for info in files
                if info.filename.endswith(".dist-info/METADATA")
            ]
            record_names = [
                info.filename for info in files
                if info.filename.endswith(".dist-info/RECORD")
            ]
            if len(metadata_names) != 1 or len(record_names) != 1 \
                    or metadata_names[0].rsplit("/", 1)[0] \
                    != record_names[0].rsplit("/", 1)[0]:
                _fail(f"wheel has no unique matching METADATA/RECORD: {resolved.name}")
            metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))
            name = metadata.get("Name")
            version = metadata.get("Version")
            if not name or not version or "\n" in version or "\r" in version:
                _fail(f"wheel METADATA name/version is invalid: {resolved.name}")
            rows = list(csv.reader(io.StringIO(
                archive.read(record_names[0]).decode("utf-8"), newline="")))
            if any(len(row) != 3 for row in rows) \
                    or len({row[0] for row in rows}) != len(rows):
                _fail(f"wheel RECORD shape differs: {resolved.name}")
            file_names = {info.filename for info in files}
            if {row[0] for row in rows} != file_names:
                _fail(f"wheel RECORD coverage differs: {resolved.name}")
            for member, encoded_hash, encoded_size in rows:
                payload = archive.read(member)
                if member == record_names[0]:
                    if encoded_hash or encoded_size:
                        _fail(f"wheel RECORD self-row differs: {resolved.name}")
                    continue
                expected = base64.urlsafe_b64encode(
                    hashlib.sha256(payload).digest()).rstrip(b"=").decode("ascii")
                if encoded_hash != f"sha256={expected}" \
                        or encoded_size != str(len(payload)):
                    _fail(f"wheel RECORD identity differs: {resolved.name}/{member}")
            tree_rows = [{
                "path": info.filename,
                "bytes": info.file_size,
                "sha256": _sha(archive.read(info.filename)),
            } for info in files]
    except (OSError, zipfile.BadZipFile, UnicodeError, csv.Error) as error:
        raise CombinedRuntimeError(f"invalid wheel: {resolved}") from error
    # pip parses the wheel filename before it opens METADATA.  Prefixing an
    # ordinal or digest changes the apparent distribution name and makes an
    # otherwise valid wheel uninstallable.  Preserve the exact PEP 427
    # basename; ordinal and digest remain separately sealed in this record.
    saved_name = resolved.name
    return {
        "ordinal": ordinal,
        "role": role,
        "distribution": _normalize_distribution(str(name)),
        "metadata_name": str(name),
        "version": str(version),
        "saved_path": f"inputs/wheels/{saved_name}",
        "member_count": len(tree_rows),
        "member_tree_sha256": _digest(tree_rows),
        **file_record,
    }


def _parse_wheel_spec(value: str) -> tuple[str, Path]:
    role, separator, path = value.partition("=")
    if not separator or not role or not path:
        _fail("--wheel must be ROLE=PATH")
    return role, Path(path)


def _venv_python_relative(platform_kind: str) -> str:
    if platform_kind == "nt":
        return "venv/Scripts/python.exe"
    if platform_kind == "posix":
        return "venv/bin/python"
    _fail("unsupported platform kind")


def _venv_site_packages_relative(platform_kind: str) -> str:
    if platform_kind == "nt":
        return "venv/Lib/site-packages"
    if platform_kind == "posix":
        return "venv/lib/python3.12/site-packages"
    _fail("unsupported platform kind")


def _command_plan(
        *, output: Path, base: Mapping[str, object], wheels: list[Mapping[str, object]],
        bootstrap_saved_root: Path, runner_saved: Path,
        platform_kind: str) -> list[dict[str, object]]:
    venv = output / "venv"
    app_data = output / "virtualenv_app_data"
    venv_python = output / _venv_python_relative(platform_kind)
    site_packages = output / _venv_site_packages_relative(platform_kind)
    bootstrap_code = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path.insert(0,{str(bootstrap_saved_root)!r});"
        f"sys.argv=['virtualenv','--no-download','--copies','--app-data',"
        f"{str(app_data)!r},{str(venv)!r}];"
        "runpy.run_module('virtualenv',run_name='__main__')"
    )
    wheel_paths = [str(output / str(row["saved_path"])) for row in wheels]
    return [
        {
            "label": "01_create_virtualenv",
            "argv": [
                str(base["invocation_path"]), "-I", "-S", "-B", "-P", "-c",
                bootstrap_code,
            ],
        },
        {
            "label": "02_install_explicit_wheels",
            "argv": [
                str(venv_python), "-I", "-S", "-B", "-P", "-c",
                "import runpy,sys;sys.dont_write_bytecode=True;"
                f"sys.path.insert(0,{str(site_packages)!r});"
                "sys.argv=['pip',*sys.argv[1:]];"
                "runpy.run_module('pip',run_name='__main__')",
                "--isolated",
                "install", "--no-index", "--no-deps", "--no-cache-dir",
                "--no-compile", "--disable-pip-version-check",
                "--target", str(site_packages),
                *wheel_paths,
            ],
        },
        {
            "label": "03_pip_check",
            "argv": [
                str(venv_python), "-I", "-S", "-B", "-P", "-c",
                "import runpy,sys;sys.dont_write_bytecode=True;"
                f"sys.path.insert(0,{str(site_packages)!r});"
                "sys.argv=['pip',*sys.argv[1:]];"
                "runpy.run_module('pip',run_name='__main__')",
                "--isolated", "check",
            ],
        },
        {
            "label": "04_snapshot_installed_packages",
            "argv": [
                str(venv_python), "-I", "-S", "-B", "-P", str(runner_saved),
                "_snapshot", "--venv-root", str(venv),
                "--site-packages", str(site_packages),
            ],
        },
    ]


def build_plan(
        *, output: Path, base_python: Path, bootstrap_root: Path,
        wheel_specs: Iterable[str]) -> dict[str, object]:
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    base = _file_record(base_python, allow_symlink=True)
    base_profile = _base_python_profile(
        Path(str(base["invocation_path"])))
    for role in ("purelib", "platlib"):
        try:
            Path(str(base_profile["result"][role])).absolute().relative_to(output)
        except ValueError:
            pass
        else:
            _fail("base Python installation boundary overlaps runtime output")
    bootstrap = bootstrap_root.expanduser().resolve(strict=True)
    bootstrap_rows = _tree_manifest(bootstrap)
    bootstrap_profile = _bootstrap_profile(bootstrap, bootstrap_rows)
    parsed = [_parse_wheel_spec(value) for value in wheel_specs]
    if not parsed:
        _fail("at least one explicit wheel is required")
    if len({role for role, _ in parsed}) != len(parsed):
        _fail("wheel roles must be unique")
    wheels = [_wheel_record(role, path, index)
              for index, (role, path) in enumerate(parsed, 1)]
    distributions = [str(row["distribution"]) for row in wheels]
    if len(distributions) != len(set(distributions)):
        _fail("each installed distribution must have exactly one wheel")
    saved_paths = [str(row["saved_path"]) for row in wheels]
    if len(saved_paths) != len(set(saved_paths)):
        _fail("wheel inputs must have distinct installable basenames")
    runner = _file_record(Path(__file__), allow_symlink=False)
    platform_kind = os.name
    planned_site_packages = (
        output / _venv_site_packages_relative(platform_kind))
    commands = _command_plan(
        output=output, base=base, wheels=wheels,
        bootstrap_saved_root=output / "inputs" / "virtualenv_bootstrap",
        runner_saved=output / "inputs" / "runner" / Path(__file__).name,
        platform_kind=platform_kind,
    )
    body: dict[str, object] = {
        "schema": PLAN_SCHEMA,
        "status": (
            "FROZEN_LOCAL_INTEGRITY_PLAN__EXTERNAL_INPUT_AUTHORITY_REQUIRED"),
        "output_directory": str(output),
        "platform_kind": platform_kind,
        "base_python": base,
        "base_python_abi_profile": base_profile,
        "virtualenv_bootstrap": {
            "source_root": str(bootstrap),
            "saved_root": "inputs/virtualenv_bootstrap",
            "file_count": len(bootstrap_rows),
            "payload_bytes": sum(int(row["bytes"]) for row in bootstrap_rows),
            "tree_sha256": _digest(bootstrap_rows),
            "files": bootstrap_rows,
            "reviewed_distribution_profile": bootstrap_profile,
        },
        "runner_source": {
            **runner,
            "saved_path": f"inputs/runner/{Path(__file__).name}",
        },
        "wheels": wheels,
        "commands": commands,
        "pip_invocation_policy": {
            "python_interpreter_executes_pip_module_without_script_or_shebang": True,
            "pip_loaded_via_runpy_with_site_disabled": True,
            "pip_script_or_shebang_invocation_forbidden": True,
            "network_index_access": False,
            "dependency_resolution": "NO_DEPS__EVERY_WHEEL_EXPLICIT",
            "only_unlisted_distributions_allowed": sorted(
                VIRTUALENV_SEED_DISTRIBUTIONS),
            "virtualenv_app_data_confined_inside_output": True,
            "pip_install_target_exact_venv_site_packages": str(
                planned_site_packages),
            "console_entrypoints_not_used_by_goal5802_runtime": True,
            "wheel_data_scripts_not_claimed_as_runtime_interfaces": True,
            "site_initialization_disabled_for_every_build_command": True,
            "pth_execution_during_build_forbidden": True,
            "pip_bytecode_compilation_during_install_forbidden": True,
        },
        "authority_boundary": {
            "plan_sha256_is_integrity_not_input_authority": True,
            "caller_must_supply_external_base_python_authority": True,
            "caller_must_supply_external_bootstrap_authority": True,
            "caller_must_supply_external_wheel_authorities": True,
            "coordinated_malicious_inputs_not_excluded_by_self_seal": True,
            "base_python_site_tree_unchanged_across_build": True,
        },
        "execution_scope": {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
            "measured_arm_import_count": 0,
            "execution_authority_consumed": False,
        },
    }
    return {**body, "plan_sha256": _digest(body)}


def _validate_plan(value: Any) -> dict[str, object]:
    if not isinstance(value, dict) or value.get("schema") != PLAN_SCHEMA \
            or value.get("status") != (
                "FROZEN_LOCAL_INTEGRITY_PLAN__EXTERNAL_INPUT_AUTHORITY_REQUIRED"):
        _fail("combined-runtime plan envelope differs")
    body = dict(value)
    seal = body.pop("plan_sha256", None)
    if seal != _digest(body):
        _fail("combined-runtime plan seal differs")
    commands = value.get("commands")
    if not isinstance(commands, list) or len(commands) != 4:
        _fail("combined-runtime command plan differs")
    for row in commands:
        if not isinstance(row, dict) or set(row) != {"label", "argv"} \
                or not isinstance(row["argv"], list) \
                or not all(isinstance(item, str) and item for item in row["argv"]):
            _fail("combined-runtime command row differs")
    try:
        rebuilt_commands = _command_plan(
            output=Path(str(value["output_directory"])),
            base=value["base_python"], wheels=value["wheels"],
            bootstrap_saved_root=(
                Path(str(value["output_directory"]))
                / str(value["virtualenv_bootstrap"]["saved_root"])),
            runner_saved=(
                Path(str(value["output_directory"]))
                / str(value["runner_source"]["saved_path"])),
            platform_kind=str(value["platform_kind"]),
        )
    except (KeyError, TypeError) as error:
        raise CombinedRuntimeError("combined-runtime plan projection differs") from error
    if commands != rebuilt_commands:
        _fail("combined-runtime command plan is not the fixed offline recipe")
    policy = value.get("pip_invocation_policy")
    if not isinstance(policy, dict) \
            or policy.get("site_initialization_disabled_for_every_build_command") \
            is not True \
            or policy.get("pth_execution_during_build_forbidden") is not True \
            or policy.get(
                "pip_bytecode_compilation_during_install_forbidden") is not True:
        _fail("combined-runtime site/.pth execution policy differs")
    boundary = value.get("authority_boundary")
    if not isinstance(boundary, dict) or any(
            boundary.get(key) is not True for key in (
                "plan_sha256_is_integrity_not_input_authority",
                "caller_must_supply_external_base_python_authority",
                "caller_must_supply_external_bootstrap_authority",
                "caller_must_supply_external_wheel_authorities",
                "coordinated_malicious_inputs_not_excluded_by_self_seal",
                "base_python_site_tree_unchanged_across_build")):
        _fail("combined-runtime external authority boundary differs")
    return value


def write_plan(path: Path, plan: Mapping[str, object]) -> None:
    _write_create_only(path.expanduser().absolute(), _canonical(plan) + b"\n")


def _read_regular_file_once(source: Path) -> bytes:
    """Read one opened regular-file identity without a check/reopen window."""

    supplied = source.expanduser().absolute()
    if supplied.is_symlink():
        _fail(f"input may not be a symlink: {supplied}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) \
        | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(supplied, flags)
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                _fail(f"input is not a regular file: {supplied}")
            payload = stream.read()
            after = os.fstat(stream.fileno())
    except OSError as error:
        raise CombinedRuntimeError(f"input is unreadable: {supplied}") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if (before.st_dev, before.st_ino, before.st_size) \
            != (after.st_dev, after.st_ino, after.st_size) \
            or len(payload) != after.st_size:
        _fail(f"input changed while being read: {supplied}")
    return payload


def _copy_exact(source: Path, destination: Path, expected: Mapping[str, object]) -> None:
    payload = _read_regular_file_once(source)
    if len(payload) != expected.get("bytes") \
            or _sha(payload) != expected.get("sha256"):
        _fail(f"input changed before combined-runtime build: {source}")
    _write_create_only(destination, payload)


def _validate_plan_inputs(plan: Mapping[str, object]) -> None:
    base = _file_record(Path(str(plan["base_python"]["invocation_path"])),
                        allow_symlink=True)
    for key in ("resolved_path", "path_kind", "bytes", "sha256"):
        if base.get(key) != plan["base_python"].get(key):
            _fail("base Python changed after planning")
    if _base_python_profile(
            Path(str(plan["base_python"]["invocation_path"]))) \
            != plan.get("base_python_abi_profile"):
        _fail("base Python ABI profile changed after planning")
    bootstrap = plan["virtualenv_bootstrap"]
    rows = _tree_manifest(Path(str(bootstrap["source_root"])))
    if rows != bootstrap["files"] or _digest(rows) != bootstrap["tree_sha256"]:
        _fail("virtualenv bootstrap changed after planning")
    if _bootstrap_profile(Path(str(bootstrap["source_root"])), rows) \
            != bootstrap.get("reviewed_distribution_profile"):
        _fail("virtualenv bootstrap distribution profile changed after planning")
    wheels = plan["wheels"]
    if not isinstance(wheels, list):
        _fail("combined-runtime wheel plan is not a list")
    for expected_ordinal, wheel in enumerate(wheels, 1):
        if not isinstance(wheel, Mapping) \
                or type(wheel.get("ordinal")) is not int \
                or wheel["ordinal"] != expected_ordinal:
            _fail("combined-runtime wheel ordinal/order differs")
        rebuilt = _wheel_record(
            str(wheel["role"]), Path(str(wheel["resolved_path"])),
            expected_ordinal,
        )
        if rebuilt != wheel:
            _fail(f"wheel changed after planning: {wheel['role']}")
    runner = _file_record(Path(str(plan["runner_source"]["resolved_path"])),
                          allow_symlink=False)
    for key in ("resolved_path", "path_kind", "bytes", "sha256"):
        if runner.get(key) != plan["runner_source"].get(key):
            _fail("combined-runtime runner changed after planning")


def _command_environment() -> dict[str, str]:
    environment = {
        key: value for key, value in os.environ.items()
        if not key.upper().startswith("PYTHON")
        and not key.upper().startswith("PIP_")
    }
    environment.update({
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
    })
    return environment


def _record(path: Path, root: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        _fail(f"evidence file is absent or symbolic: {path}")
    payload = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": len(payload), "sha256": _sha(payload),
    }


def _run_command(
        row: Mapping[str, object], *, output: Path,
        environment: Mapping[str, str]) -> subprocess.CompletedProcess[bytes]:
    label = str(row["label"])
    command = [str(item) for item in row["argv"]]
    completed = subprocess.run(
        command, cwd=output, env=dict(environment), check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    receipt_dir = output / "command_receipts" / label
    _write_create_only(receipt_dir / "argv.json", _canonical(command) + b"\n")
    _write_create_only(receipt_dir / "stdout", completed.stdout)
    _write_create_only(receipt_dir / "stderr", completed.stderr)
    _write_create_only(
        receipt_dir / "exit_code", f"{completed.returncode}\n".encode("ascii"))
    environment_projection = {
        key: environment.get(key) for key in (
            "PATH", "LD_LIBRARY_PATH", "LD_PRELOAD", "CUDA_VISIBLE_DEVICES",
            "PIP_CONFIG_FILE", "PIP_DISABLE_PIP_VERSION_CHECK", "PIP_NO_INDEX",
            "PYTHONDONTWRITEBYTECODE", "PYTHONNOUSERSITE",
        )
    }
    _write_create_only(
        receipt_dir / "environment.json",
        _canonical(environment_projection) + b"\n")
    if completed.returncode != 0:
        _fail(f"combined-runtime command failed: {label}")
    return completed


def _package_snapshot(
        venv_root: Path, site_packages: Path) -> dict[str, object]:
    """Executed only by the new venv Python; imports standard library only."""

    import importlib.metadata

    expected_root = venv_root.expanduser().resolve(strict=True)
    expected_site = site_packages.expanduser().resolve(strict=True)
    try:
        expected_site.relative_to(expected_root)
        Path(sys.executable).resolve(strict=True).relative_to(expected_root)
    except ValueError:
        _fail("package snapshot interpreter/site-packages escapes virtualenv")
    if expected_site.is_symlink() or not expected_site.is_dir() \
            or "site" in sys.modules:
        _fail("package snapshot site boundary differs")
    packages = []
    names: set[str] = set()
    for distribution in importlib.metadata.distributions(path=[str(expected_site)]):
        raw_name = distribution.metadata.get("Name")
        if not raw_name:
            _fail("installed distribution has no Name metadata")
        name = _normalize_distribution(raw_name)
        if name in names:
            _fail(f"installed distribution is duplicated: {name}")
        names.add(name)
        rows = []
        for item in sorted(distribution.files or (), key=lambda value: str(value)):
            lexical = Path(distribution.locate_file(item)).absolute()
            if lexical.is_symlink():
                _fail(f"installed distribution file is symbolic: {lexical}")
            resolved = lexical.resolve(strict=True)
            try:
                relative = resolved.relative_to(expected_root).as_posix()
            except ValueError:
                _fail(f"installed distribution file escapes virtualenv: {resolved}")
            if not resolved.is_file():
                continue
            rows.append({
                "path": relative,
                "bytes": resolved.stat().st_size,
                "sha256": _sha_file(resolved),
            })
        packages.append({
            "distribution": name,
            "metadata_name": raw_name,
            "version": distribution.version,
            "file_count": len(rows),
            "payload_bytes": sum(int(row["bytes"]) for row in rows),
            "tree_sha256": _digest(rows),
            "files": rows,
        })
    packages.sort(key=lambda row: str(row["distribution"]))
    executable = _file_record(Path(sys.executable), allow_symlink=True)
    body: dict[str, object] = {
        "schema": SNAPSHOT_SCHEMA,
        "status": "PASS__COMPLETE_INSTALLED_DISTRIBUTION_SNAPSHOT",
        "venv_root": str(expected_root),
        "site_packages": str(expected_site),
        "site_module_imported": False,
        "python_executable": executable,
        "package_count": len(packages),
        "packages": packages,
    }
    return {**body, "snapshot_sha256": _digest(body)}


def _input_copy_manifest(output: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted((output / "inputs").rglob("*")):
        if path.is_symlink():
            _fail(f"combined-runtime copied input is symbolic: {path}")
        if path.is_file():
            rows.append(_record(path, output))
    rows.sort(key=lambda row: str(row["path"]))
    return rows


def _expected_input_copy_manifest(
        output: Path, plan: Mapping[str, object]) -> list[dict[str, object]]:
    """Project the exact copied-input member set directly from the plan."""

    rows: list[dict[str, object]] = []
    bootstrap = plan["virtualenv_bootstrap"]
    bootstrap_root = Path(str(bootstrap["saved_root"]))
    for row in bootstrap["files"]:
        rows.append({
            "path": (bootstrap_root / str(row["path"])).as_posix(),
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        })
    for wheel in plan["wheels"]:
        rows.append({
            "path": str(wheel["saved_path"]),
            "bytes": wheel["bytes"],
            "sha256": wheel["sha256"],
        })
    runner = plan["runner_source"]
    rows.append({
        "path": str(runner["saved_path"]),
        "bytes": runner["bytes"],
        "sha256": runner["sha256"],
    })
    expected = sorted(rows, key=lambda row: str(row["path"]))
    for row in expected:
        try:
            (output / str(row["path"])).relative_to(output)
        except ValueError as error:
            raise CombinedRuntimeError(
                "planned copied input escapes runtime output") from error
    return expected


def _generated_tree_manifest(output: Path, relative: str) -> list[dict[str, object]]:
    root = output / relative
    if root.is_symlink() or not root.is_dir():
        _fail(f"generated tree is absent or symbolic: {relative}")
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"generated tree contains a symlink: {path}")
        if path.is_file():
            rows.append(_record(path, output))
    return rows


def _generated_member_tree_manifest(
        output: Path, relative: str) -> list[dict[str, object]]:
    """Record the complete file *and directory* set of a generated tree."""

    root = output / relative
    if root.is_symlink() or not root.is_dir():
        _fail(f"generated member tree is absent or symbolic: {relative}")
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"generated member tree contains a symlink: {path}")
        metadata = path.stat()
        row: dict[str, object] = {
            "path": path.relative_to(output).as_posix(),
            "mode": stat.S_IMODE(metadata.st_mode),
        }
        if stat.S_ISDIR(metadata.st_mode):
            row["kind"] = "DIRECTORY"
        elif stat.S_ISREG(metadata.st_mode):
            row.update({
                "kind": "REGULAR_FILE",
                "bytes": metadata.st_size,
                "sha256": _sha_file(path),
            })
        else:
            _fail(f"generated member tree has a special member: {path}")
        rows.append(row)
    if not rows:
        _fail(f"generated member tree is empty: {relative}")
    return rows


def _external_tree_projection(path: Path) -> dict[str, object]:
    """Hash an external tree without following symbolic members."""

    lexical = path.expanduser().absolute()
    if lexical.is_symlink():
        _fail(f"base Python site root may not be symbolic: {lexical}")
    if not lexical.exists():
        return {
            "path": str(lexical), "state": "ABSENT",
            "member_count": 0, "payload_bytes": 0,
            "tree_sha256": _digest([]),
        }
    root = lexical.resolve(strict=True)
    if not root.is_dir():
        _fail(f"base Python site root is not a directory: {root}")
    rows: list[dict[str, object]] = []
    for member in sorted(root.rglob("*")):
        metadata = member.lstat()
        row: dict[str, object] = {
            "path": member.relative_to(root).as_posix(),
            "mode": stat.S_IMODE(metadata.st_mode),
        }
        if stat.S_ISLNK(metadata.st_mode):
            row.update({"kind": "SYMLINK", "target": os.readlink(member)})
        elif stat.S_ISDIR(metadata.st_mode):
            row["kind"] = "DIRECTORY"
        elif stat.S_ISREG(metadata.st_mode):
            row.update({
                "kind": "REGULAR_FILE", "bytes": metadata.st_size,
                "sha256": _sha_file(member),
            })
        else:
            _fail(f"base Python site root has a special member: {member}")
        rows.append(row)
    return {
        "path": str(root), "state": "PRESENT",
        "member_count": len(rows),
        "payload_bytes": sum(
            int(row.get("bytes", 0)) for row in rows),
        "tree_sha256": _digest(rows),
    }


def _base_site_boundary(plan: Mapping[str, object]) -> dict[str, object]:
    result = plan["base_python_abi_profile"]["result"]
    grouped: dict[str, dict[str, object]] = {}
    for role in ("purelib", "platlib"):
        path = Path(str(result[role])).expanduser().absolute()
        key = str(path)
        grouped.setdefault(key, {"path": path, "roles": []})["roles"].append(role)
    rows = []
    for key in sorted(grouped):
        item = grouped[key]
        rows.append({
            "roles": sorted(item["roles"]),
            **_external_tree_projection(item["path"]),
        })
    return {
        "roots": rows,
        "root_count": len(rows),
        "projection_sha256": _digest(rows),
    }


def _write_failure(
        output: Path, plan: Mapping[str, object], error: BaseException,
        *, plan_file_sha256: str) -> None:
    failure = {
        "schema": FAILURE_SCHEMA,
        "status": "TERMINAL_CREATE_ONLY_COMBINED_RUNTIME_FAILURE__NO_REUSE",
        "plan_sha256": plan.get("plan_sha256"),
        "plan_file_sha256": plan_file_sha256,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "execution_authority_consumed": False,
        "retry_or_replacement_authorized": False,
    }
    failure["failure_receipt_sha256"] = _digest(failure)
    try:
        _write_create_only(
            output / "terminal_failure_receipt.json", _canonical(failure) + b"\n")
    except (OSError, FileExistsError):
        pass


def _capture_current_snapshot(
        output: Path, plan: Mapping[str, object]) -> dict[str, object]:
    """Recount the installed packages before publishing a PASS receipt."""

    runner = output / str(plan["runner_source"]["saved_path"])
    venv_python = output / _venv_python_relative(str(plan["platform_kind"]))
    site_packages = output / _venv_site_packages_relative(
        str(plan["platform_kind"]))
    completed = subprocess.run(
        [str(venv_python), "-I", "-S", "-B", "-P", str(runner), "_snapshot",
         "--venv-root", str(output / "venv"),
         "--site-packages", str(site_packages)],
        cwd=output, env=_command_environment(), check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        _fail("current installed package recount failed")
    observed = _strict_json_bytes(completed.stdout, "current package recount")
    if not isinstance(observed, dict) or observed.get("schema") != SNAPSHOT_SCHEMA:
        _fail("current installed package recount envelope differs")
    body = dict(observed)
    seal = body.pop("snapshot_sha256", None)
    if seal != _digest(body):
        _fail("current installed package recount seal differs")
    return observed


def run_plan(
        plan_path: Path, *, expected_plan_file_sha256: str) \
        -> dict[str, object]:
    supplied_plan = plan_path.expanduser().absolute()
    if HEX64.fullmatch(expected_plan_file_sha256) is None \
            or supplied_plan.is_symlink():
        _fail("expected plan file SHA-256 or plan path differs")
    try:
        metadata = supplied_plan.stat()
        plan_payload = supplied_plan.read_bytes()
    except OSError as error:
        raise CombinedRuntimeError("combined-runtime plan is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode) \
            or _sha(plan_payload) != expected_plan_file_sha256:
        _fail("combined-runtime plan differs from caller-pinned exact bytes")
    plan = _validate_plan(_strict_json_bytes(
        plan_payload, "combined-runtime plan"))
    output = Path(str(plan["output_directory"]))
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    _validate_plan_inputs(plan)
    base_site_boundary = _base_site_boundary(plan)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    try:
        _write_create_only(output / "plan.json", _canonical(plan) + b"\n")
        bootstrap = plan["virtualenv_bootstrap"]
        bootstrap_source = Path(str(bootstrap["source_root"]))
        for row in bootstrap["files"]:
            _copy_exact(
                bootstrap_source / str(row["path"]),
                output / str(bootstrap["saved_root"]) / str(row["path"]), row)
        for wheel in plan["wheels"]:
            _copy_exact(
                Path(str(wheel["resolved_path"])),
                output / str(wheel["saved_path"]), wheel)
        runner = plan["runner_source"]
        _copy_exact(
            Path(str(runner["resolved_path"])),
            output / str(runner["saved_path"]), runner)
        expected_input_rows = _expected_input_copy_manifest(output, plan)
        input_rows = _input_copy_manifest(output)
        if input_rows != expected_input_rows:
            _fail("copied combined-runtime inputs differ from frozen plan")
        environment = _command_environment()
        command_outputs = []
        for row in plan["commands"]:
            command_outputs.append(_run_command(
                row, output=output, environment=environment))
        snapshot_payload = command_outputs[-1].stdout
        snapshot = _strict_json_bytes(snapshot_payload, "package snapshot stdout")
        if not isinstance(snapshot, dict) or snapshot.get("schema") != SNAPSHOT_SCHEMA:
            _fail("package snapshot envelope differs")
        snapshot_body = dict(snapshot)
        snapshot_seal = snapshot_body.pop("snapshot_sha256", None)
        if snapshot_seal != _digest(snapshot_body):
            _fail("package snapshot seal differs")
        installed = {
            str(row["distribution"]): str(row["version"])
            for row in snapshot["packages"]
        }
        expected = {
            str(row["distribution"]): str(row["version"])
            for row in plan["wheels"]
        }
        if any(installed.get(name) != version for name, version in expected.items()):
            _fail("one or more explicit wheel distributions are not installed exactly")
        unexpected = set(installed) - set(expected) - VIRTUALENV_SEED_DISTRIBUTIONS
        if unexpected:
            _fail(f"unexpected installed distributions: {sorted(unexpected)}")
        if any(int(row["file_count"]) <= 0 for row in snapshot["packages"]):
            _fail("an installed distribution has no receipted files")
        _write_create_only(
            output / "installed_packages.json", _canonical(snapshot) + b"\n")
        if _capture_current_snapshot(output, plan) != snapshot:
            _fail("independent current package recount differs before publication")
        if _base_site_boundary(plan) != base_site_boundary:
            _fail("base Python site tree changed during combined-runtime build")
        venv_rows = _generated_member_tree_manifest(output, "venv")
        input_rows = _input_copy_manifest(output)
        if input_rows != expected_input_rows:
            _fail("combined-runtime commands changed their frozen inputs")
        app_data_rows = _generated_tree_manifest(output, "virtualenv_app_data")
        evidence_rows = [_record(output / "plan.json", output)]
        evidence_rows.append(_record(output / "installed_packages.json", output))
        for path in sorted((output / "command_receipts").rglob("*")):
            if path.is_file():
                evidence_rows.append(_record(path, output))
        body: dict[str, object] = {
            "schema": RUN_SCHEMA,
            "status": "PASS__OFFLINE_CREATE_ONLY_COMBINED_RUNTIME_BUILT",
            "plan_sha256": plan["plan_sha256"],
            "plan_file_sha256": expected_plan_file_sha256,
            "input_file_count": len(input_rows),
            "input_tree_sha256": _digest(input_rows),
            "input_files": input_rows,
            "virtualenv_app_data_file_count": len(app_data_rows),
            "virtualenv_app_data_tree_sha256": _digest(app_data_rows),
            "virtualenv_app_data_files": app_data_rows,
            "command_count": len(plan["commands"]),
            "commands_sha256": _digest(plan["commands"]),
            "installed_package_snapshot_sha256": snapshot["snapshot_sha256"],
            "venv_member_count": len(venv_rows),
            "venv_member_tree_sha256": _digest(venv_rows),
            "venv_members": venv_rows,
            "expected_explicit_distributions": expected,
            "unexpected_installed_distribution_count": 0,
            "evidence_files": evidence_rows,
            "pip_invocation_policy": plan["pip_invocation_policy"],
            "authority_boundary": plan["authority_boundary"],
            "base_python_site_boundary": base_site_boundary,
            "execution_scope": {
                "formal_worker_count": 0,
                "registered_performance_timing_count": 0,
                "gpu_kernel_launch_count": 0,
                "clock_read_count": 0,
                "measured_arm_import_count": 0,
                "execution_authority_consumed": False,
            },
            "create_only": True,
        }
        receipt = {**body, "receipt_sha256": _digest(body)}
        _write_create_only(
            output / "combined_runtime_receipt.json", _canonical(receipt) + b"\n")
        return receipt
    except BaseException as error:
        _write_failure(
            output, plan, error,
            plan_file_sha256=expected_plan_file_sha256)
        raise


def _verify_file_rows(output: Path, rows: Any, label: str) -> None:
    if not isinstance(rows, list):
        _fail(f"{label} is not a list")
    paths = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            _fail(f"{label} row differs")
        relative = PurePosixPath(str(row["path"]))
        if relative.is_absolute() or ".." in relative.parts:
            _fail(f"{label} path is unsafe")
        path = output / Path(*relative.parts)
        if _record(path, output) != row:
            _fail(f"{label} file identity differs: {relative}")
        paths.append(str(relative))
    if len(paths) != len(set(paths)):
        _fail(f"{label} has duplicate paths")


def verify_run(output: Path) -> dict[str, object]:
    output = output.expanduser().resolve(strict=True)
    if output.is_symlink() or not output.is_dir():
        _fail("combined-runtime output is not a real directory")
    if (output / "terminal_failure_receipt.json").exists():
        _fail("combined-runtime output is terminal-failed")
    plan = _validate_plan(_strict_json(output / "plan.json", "saved plan"))
    receipt = _strict_json(
        output / "combined_runtime_receipt.json", "combined-runtime receipt")
    if not isinstance(receipt, dict) or receipt.get("schema") != RUN_SCHEMA:
        _fail("combined-runtime receipt envelope differs")
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    saved_plan_file_sha256 = _sha((output / "plan.json").read_bytes())
    if seal != _digest(body) \
            or receipt.get("plan_sha256") != plan["plan_sha256"] \
            or receipt.get("plan_file_sha256") != saved_plan_file_sha256:
        _fail("combined-runtime receipt seal or plan binding differs")
    expected = {
        str(row["distribution"]): str(row["version"])
        for row in plan["wheels"]
    }
    if receipt.get("command_count") != len(plan["commands"]) \
            or receipt.get("commands_sha256") != _digest(plan["commands"]) \
            or receipt.get("expected_explicit_distributions") != expected \
            or receipt.get("unexpected_installed_distribution_count") != 0 \
            or receipt.get("pip_invocation_policy") != plan["pip_invocation_policy"] \
            or receipt.get("authority_boundary") != plan["authority_boundary"]:
        _fail("combined-runtime receipt command/package projection differs")
    if receipt.get("base_python_site_boundary") != _base_site_boundary(plan):
        _fail("base Python site tree differs from build receipt")
    _verify_file_rows(output, receipt.get("input_files"), "input manifest")
    if receipt["input_file_count"] != len(receipt["input_files"]) \
            or receipt["input_tree_sha256"] != _digest(receipt["input_files"]):
        _fail("combined-runtime input tree binding differs")
    if _input_copy_manifest(output) != receipt["input_files"]:
        _fail("combined-runtime copied input member set differs")
    if receipt["input_files"] != _expected_input_copy_manifest(output, plan):
        _fail("combined-runtime copied inputs differ from frozen plan")
    app_data_rows = _generated_tree_manifest(output, "virtualenv_app_data")
    if receipt.get("virtualenv_app_data_file_count") != len(app_data_rows) \
            or receipt.get("virtualenv_app_data_tree_sha256") \
            != _digest(app_data_rows) \
            or receipt.get("virtualenv_app_data_files") != app_data_rows:
        _fail("virtualenv app-data tree binding differs")
    _verify_file_rows(output, receipt.get("evidence_files"), "evidence manifest")
    observed_evidence = [_record(output / "plan.json", output)]
    observed_evidence.append(_record(output / "installed_packages.json", output))
    for path in sorted((output / "command_receipts").rglob("*")):
        if path.is_symlink():
            _fail(f"combined-runtime command receipt is symbolic: {path}")
        if path.is_file():
            observed_evidence.append(_record(path, output))
    if observed_evidence != receipt["evidence_files"]:
        _fail("combined-runtime evidence member set differs")
    venv_rows = _generated_member_tree_manifest(output, "venv")
    if receipt.get("venv_member_count") != len(venv_rows) \
            or receipt.get("venv_member_tree_sha256") != _digest(venv_rows) \
            or receipt.get("venv_members") != venv_rows:
        _fail("combined-runtime complete virtualenv member tree differs")
    snapshot = _strict_json(
        output / "installed_packages.json", "installed package snapshot")
    snapshot_body = dict(snapshot)
    snapshot_seal = snapshot_body.pop("snapshot_sha256", None)
    if snapshot_seal != _digest(snapshot_body) \
            or snapshot_seal != receipt["installed_package_snapshot_sha256"]:
        _fail("installed package snapshot seal differs")
    installed = {
        str(row["distribution"]): str(row["version"])
        for row in snapshot.get("packages", [])
    }
    if any(installed.get(name) != version for name, version in expected.items()) \
            or set(installed) - set(expected) - VIRTUALENV_SEED_DISTRIBUTIONS:
        _fail("installed distribution set differs from plan")
    if _capture_current_snapshot(output, plan) != snapshot:
        _fail("current installed package snapshot differs from build receipt")
    if _generated_member_tree_manifest(output, "venv") != venv_rows:
        _fail("virtualenv changed while independently recounting packages")
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan/build/verify an offline combined Goal5802 runtime")
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--output-directory", type=Path, required=True)
    plan.add_argument("--base-python", type=Path, required=True)
    plan.add_argument("--virtualenv-bootstrap-root", type=Path, required=True)
    plan.add_argument("--wheel", action="append", required=True,
                      help="one explicit ROLE=PATH wheel; repeat for every package")
    plan.add_argument("--plan-output", type=Path, required=True)
    run = commands.add_parser("run")
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--expected-plan-file-sha256", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--output-directory", type=Path, required=True)
    snapshot = commands.add_parser("_snapshot")
    snapshot.add_argument("--venv-root", type=Path, required=True)
    snapshot.add_argument("--site-packages", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "plan":
        output_absolute = args.output_directory.expanduser().absolute()
        plan_absolute = args.plan_output.expanduser().absolute()
        try:
            plan_absolute.relative_to(output_absolute)
        except ValueError:
            pass
        else:
            _fail("plan output must be outside the future create-only runtime root")
        plan = build_plan(
            output=args.output_directory, base_python=args.base_python,
            bootstrap_root=args.virtualenv_bootstrap_root,
            wheel_specs=args.wheel,
        )
        write_plan(args.plan_output, plan)
        result = {"status": plan["status"], "plan_sha256": plan["plan_sha256"]}
    elif args.command == "run":
        receipt = run_plan(
            args.plan,
            expected_plan_file_sha256=args.expected_plan_file_sha256)
        result = {"status": receipt["status"],
                  "receipt_sha256": receipt["receipt_sha256"]}
    elif args.command == "verify":
        receipt = verify_run(args.output_directory)
        result = {"status": receipt["status"],
                  "receipt_sha256": receipt["receipt_sha256"]}
    else:
        snapshot = _package_snapshot(args.venv_root, args.site_packages)
        sys.stdout.buffer.write(_canonical(snapshot) + b"\n")
        return 0
    result.update({
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    })
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
