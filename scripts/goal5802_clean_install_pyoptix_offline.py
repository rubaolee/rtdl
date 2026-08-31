#!/usr/bin/env python3
"""Plan, build, and verify the offline Goal5802 PyOptiX environment.

The implementation specializes the separately tested Goal5802 combined
runtime builder.  It admits exactly the reviewed PyOptiX/RTDL runtime wheel
set, an explicit local virtualenv bootstrap tree, and one exact base Python.
The install command always uses the selected Python interpreter to execute the
``pip`` module with ``--isolated``, ``--no-index``, and ``--no-deps``.  Every
build command uses ``-I -S -B -P``: site initialisation is disabled, bytecode
is suppressed, unsafe path prepending is disabled, and ``pip`` is loaded
explicitly through ``runpy`` so an installed ``.pth`` file cannot execute
during construction.
No installed measured-runtime distribution is imported, no device is queried,
no GPU kernel is launched, and no measurement clock or performance worker is
used.
"""

from __future__ import annotations

import argparse
import configparser
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
from typing import Any, Mapping, NoReturn
import zipfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import goal5802_build_combined_runtime_untimed as combined
from scripts import goal5802_build_offline_python_wheelhouse as wheelhouse


SPECIALIZATION_SCHEMA = (
    "rtdl.goal5802.offline_pyoptix_clean_install_specialization.v1")
RECEIPT_SCHEMA = "rtdl.goal5802.offline_pyoptix_clean_install_receipt.v1"
FAILURE_SCHEMA = "rtdl.goal5802.offline_pyoptix_clean_install_failure.v1"
SPECIALIZATION_KEY = "offline_pyoptix_specialization"
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FORBIDDEN_NETWORK_TOKENS = (
    "--index-url", "--extra-index-url", "--trusted-host", "--proxy",
    "http://", "https://", "ftp://", "git+http", "git+ssh",
)
BOOTSTRAP_DISTRIBUTIONS: tuple[tuple[str, str], ...] = (
    ("virtualenv", "20.35.4"),
    ("distlib", "0.4.3"),
    ("filelock", "3.32.4"),
    ("platformdirs", "4.11.4"),
)
BOOTSTRAP_VERSION_MAP = dict(BOOTSTRAP_DISTRIBUTIONS)
BASE_PROBE_CODE = (
    "import json,platform,struct,sys,sysconfig;"
    "value={'cache_tag':sys.implementation.cache_tag,"
    "'implementation':sys.implementation.name,"
    "'platform':sysconfig.get_platform(),"
    "'pointer_bits':struct.calcsize('P')*8,"
    "'python_version':platform.python_version(),"
    "'version_info':[sys.version_info.major,sys.version_info.minor,"
    "sys.version_info.micro]};"
    "sys.stdout.buffer.write(json.dumps(value,allow_nan=False,"
    "separators=(',',':'),sort_keys=True).encode('utf-8')+b'\\n')"
)


class OfflinePyOptiXInstallError(RuntimeError):
    """Fail-closed offline PyOptiX installation error."""


def _fail(message: str) -> NoReturn:
    raise OfflinePyOptiXInstallError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _strict_json_with_file_sha(path: Path, label: str) -> tuple[Any, str]:
    if path.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        metadata = path.stat()
        payload = path.read_bytes()
    except OSError as error:
        raise OfflinePyOptiXInstallError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfflinePyOptiXInstallError(f"{label} is not UTF-8 JSON") from error
    if payload != _canonical(value) + b"\n":
        _fail(f"{label} is not exact canonical JSON plus LF")
    return value, hashlib.sha256(payload).hexdigest()


def _strict_json(path: Path, label: str) -> Any:
    return _strict_json_with_file_sha(path, label)[0]


def _record(path: Path, root: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        _fail(f"evidence file is absent or symbolic: {path}")
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha_file(path),
    }


def _current_file_record(path: Path) -> dict[str, object]:
    try:
        return combined._file_record(path, allow_symlink=False)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error


def _source_records() -> dict[str, dict[str, object]]:
    return {
        "offline_installer": _current_file_record(Path(__file__)),
        "wheelhouse_builder": _current_file_record(Path(wheelhouse.__file__)),
        "combined_runtime_builder": _current_file_record(Path(combined.__file__)),
    }


def _probe_base_python(path: Path) -> dict[str, object]:
    base = _current_file_record(path)
    environment = dict(os.environ)
    environment.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_NO_INDEX": "1",
    })
    try:
        completed = subprocess.run(
            [str(base["invocation_path"]), "-I", "-S", "-B", "-P", "-c",
             BASE_PROBE_CODE],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment)
    except OSError as error:
        raise OfflinePyOptiXInstallError(
            "declared base Python is not executable") from error
    if completed.returncode != 0 or completed.stderr:
        _fail("declared base Python safe probe failed")
    try:
        value = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfflinePyOptiXInstallError(
            "declared base Python safe probe is not JSON") from error
    if completed.stdout != _canonical(value) + b"\n" \
            or not isinstance(value, dict) or set(value) != {
                "cache_tag", "implementation", "platform", "pointer_bits",
                "python_version", "version_info"}:
        _fail("declared base Python safe probe envelope differs")
    if value["implementation"] != "cpython" or value["cache_tag"] != "cpython-312" \
            or value["pointer_bits"] != 64 \
            or not isinstance(value["version_info"], list) \
            or len(value["version_info"]) != 3 \
            or value["version_info"][:2] != [3, 12] \
            or any(type(item) is not int for item in value["version_info"]):
        _fail("base Python is not 64-bit CPython 3.12/cp312")
    body: dict[str, object] = {
        "schema": "rtdl.goal5802.base_python_safe_probe.v1",
        "status": "PASS__CPYTHON_312_64BIT__SITE_DISABLED",
        "base_python": base,
        "argv_suffix": ["-I", "-S", "-B", "-P", "-c", BASE_PROBE_CODE],
        "observed": value,
        "site_module_enabled": False,
        "safe_path_enabled": True,
        "installed_runtime_distribution_import_count": 0,
        "gpu_kernel_launch_count": 0,
        "registered_performance_timing_count": 0,
    }
    return {**body, "probe_sha256": _digest(body)}


def _bootstrap_profile(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve(strict=True)
    if root.is_symlink() or not root.is_dir():
        _fail("virtualenv bootstrap root is not a real directory")
    metadata_paths = sorted(root.glob("*.dist-info/METADATA"))
    observed: dict[str, dict[str, object]] = {}
    for metadata_path in metadata_paths:
        if metadata_path.is_symlink() or not metadata_path.is_file():
            _fail("virtualenv bootstrap METADATA is absent or symbolic")
        metadata = BytesParser().parsebytes(metadata_path.read_bytes())
        raw_name = metadata.get("Name")
        version = metadata.get("Version")
        if not raw_name or not version:
            _fail("virtualenv bootstrap METADATA has no Name/Version")
        try:
            name = combined._normalize_distribution(str(raw_name))
        except combined.CombinedRuntimeError as error:
            raise OfflinePyOptiXInstallError(str(error)) from error
        if name in observed:
            _fail(f"duplicate virtualenv bootstrap distribution: {name}")
        observed[name] = {
            "distribution": name,
            "metadata_name": str(raw_name),
            "version": str(version),
            "metadata_path": metadata_path.relative_to(root).as_posix(),
            "metadata_bytes": metadata_path.stat().st_size,
            "metadata_sha256": _sha_file(metadata_path),
        }
    if set(observed) != set(BOOTSTRAP_VERSION_MAP):
        _fail("virtualenv bootstrap distribution set differs")
    rows = []
    for name, version in BOOTSTRAP_DISTRIBUTIONS:
        row = observed[name]
        if row["version"] != version:
            _fail(f"virtualenv bootstrap version differs: {name}")
        rows.append(row)
    body: dict[str, object] = {
        "schema": "rtdl.goal5802.virtualenv_bootstrap_profile.v1",
        "status": "PASS__EXACT_REVIEWED_VIRTUALENV_BOOTSTRAP_VERSIONS",
        "root": str(root),
        "required_distributions": BOOTSTRAP_VERSION_MAP,
        "distributions": rows,
    }
    return {**body, "profile_sha256": _digest(body)}


def _entrypoint_and_script_boundary(
        root: Path, manifest: Mapping[str, object]) -> dict[str, object]:
    """Inventory wheel entry points without importing or executing a wheel."""

    rows = []
    console_count = 0
    nonconsole_count = 0
    wheel_script_count = 0
    for manifest_row in manifest["wheels"]:
        path = root / str(manifest_row["saved_path"])
        entry_point_files = []
        wheel_scripts = []
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    if info.filename.endswith(".dist-info/entry_points.txt"):
                        payload = archive.read(info)
                        try:
                            text = payload.decode("utf-8")
                            parser = configparser.ConfigParser(
                                interpolation=None, strict=True)
                            parser.optionxform = str
                            parser.read_string(text)
                        except (UnicodeError, configparser.Error) as error:
                            raise OfflinePyOptiXInstallError(
                                f"wheel entry_points metadata differs: {path}"
                            ) from error
                        groups = []
                        for group in parser.sections():
                            entries = [
                                {"name": name, "target": target}
                                for name, target in parser.items(group)
                            ]
                            groups.append({"group": group, "entries": entries})
                            if group == "console_scripts":
                                console_count += len(entries)
                            else:
                                nonconsole_count += len(entries)
                        entry_point_files.append({
                            "path": info.filename,
                            "bytes": len(payload),
                            "sha256": hashlib.sha256(payload).hexdigest(),
                            "groups": groups,
                        })
                    if ".data/scripts/" in info.filename:
                        payload = archive.read(info)
                        wheel_scripts.append({
                            "path": info.filename,
                            "bytes": len(payload),
                            "sha256": hashlib.sha256(payload).hexdigest(),
                        })
                        wheel_script_count += 1
        except (OSError, zipfile.BadZipFile) as error:
            raise OfflinePyOptiXInstallError(
                f"wheel script inventory is unreadable: {path}") from error
        rows.append({
            "distribution": manifest_row["distribution"],
            "version": manifest_row["version"],
            "wheel_sha256": manifest_row["sha256"],
            "entry_point_files": entry_point_files,
            "wheel_data_scripts": wheel_scripts,
        })
    body: dict[str, object] = {
        "schema": "rtdl.goal5802.wheel_entrypoint_and_script_boundary.v1",
        "wheel_count": len(rows),
        "wheels": rows,
        "observed_console_entry_point_count": console_count,
        "observed_nonconsole_entry_point_count": nonconsole_count,
        "observed_wheel_data_script_count": wheel_script_count,
        "goal5802_required_console_entry_point_count": 0,
        "goal5802_required_wheel_data_script_count": 0,
        "goal5802_runtime_interface": "PYTHON_IMPORTS_ONLY",
        "script_absence_claimed": False,
        "observed_scripts_or_entry_points_authorize_invocation": False,
        "wheel_import_or_execution_count": 0,
    }
    return {**body, "inventory_sha256": _digest(body)}


def _specialization_body(
        *, manifest_root: Path, manifest: Mapping[str, object],
        base_probe: Mapping[str, object],
        bootstrap_profile: Mapping[str, object]) -> dict[str, object]:
    manifest_path = manifest_root / "wheelhouse_manifest.json"
    return {
        "schema": SPECIALIZATION_SCHEMA,
        "status": "PLANNED_EXACT_OFFLINE_PYOPTIX_CLEAN_INSTALL_PROFILE",
        "profile": wheelhouse.PROFILE,
        "required_distributions": wheelhouse.REQUIRED_VERSION_MAP,
        "wheelhouse_root": str(manifest_root),
        "wheelhouse_manifest": _current_file_record(manifest_path),
        "wheelhouse_manifest_sha256": manifest["manifest_sha256"],
        "wheel_set_sha256": manifest["wheel_set_sha256"],
        "wheel_count": manifest["wheel_count"],
        "base_python_safe_probe": base_probe,
        "virtualenv_bootstrap_profile": bootstrap_profile,
        "source_implementations": _source_records(),
        "entrypoint_and_script_boundary": _entrypoint_and_script_boundary(
            manifest_root, manifest),
        "pip_policy": {
            "python_interpreter_executes_pip_module_without_script_or_shebang": (
                True),
            "pip_loaded_via_runpy_with_site_disabled": True,
            "safe_path_enabled_for_every_build_command": True,
            "isolated": True,
            "no_index": True,
            "no_deps": True,
            "no_cache_dir": True,
            "no_compile": True,
            "exact_venv_site_packages_target": True,
            "prefix_mode_allowed": False,
            "implicit_download_allowed": False,
            "pip_script_or_shebang_invocation_allowed": False,
        },
        "validation_boundary": {
            "installed_measured_runtime_distribution_import_count": 0,
            "pyoptix_import_count": 0,
            "cupy_import_count": 0,
            "device_query_count": 0,
            "gpu_kernel_launch_count": 0,
            "registered_measurement_clock_read_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "execution_authority_consumed": False,
            "self_hash_is_execution_authority": False,
            "caller_must_bind_exact_plan_before_run": True,
        },
    }


def build_plan(
        *, output: Path, base_python: Path, bootstrap_root: Path,
        wheelhouse_root: Path) -> dict[str, object]:
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    manifest_root = wheelhouse_root.expanduser().resolve(strict=True)
    try:
        manifest = wheelhouse.verify(manifest_root)
    except (wheelhouse.OfflineWheelhouseError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error
    by_name = {
        str(row["distribution"]): row for row in manifest["wheels"]
    }
    wheel_specs = [
        f"{name.replace('-', '_')}={manifest_root / str(by_name[name]['saved_path'])}"
        for name, _ in wheelhouse.REQUIRED_DISTRIBUTIONS
    ]
    base_probe = _probe_base_python(base_python)
    bootstrap = _bootstrap_profile(bootstrap_root)
    try:
        plan = combined.build_plan(
            output=output, base_python=base_python,
            bootstrap_root=bootstrap_root, wheel_specs=wheel_specs)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error
    plan.pop("plan_sha256")
    specialization_body = _specialization_body(
        manifest_root=manifest_root, manifest=manifest,
        base_probe=base_probe, bootstrap_profile=bootstrap)
    plan[SPECIALIZATION_KEY] = {
        **specialization_body,
        "specialization_sha256": _digest(specialization_body),
    }
    plan["plan_sha256"] = combined._digest(plan)
    return _validate_plan(plan, require_live_inputs=True)


def _validate_install_command(plan: Mapping[str, object]) -> None:
    commands = plan.get("commands")
    if not isinstance(commands, list) or len(commands) != 4:
        _fail("offline PyOptiX command plan differs")
    output = Path(str(plan["output_directory"]))
    bootstrap = plan.get("virtualenv_bootstrap")
    runner = plan.get("runner_source")
    if not isinstance(bootstrap, dict) or not isinstance(runner, dict):
        _fail("offline PyOptiX generic input projection differs")
    expected_commands = combined._command_plan(
        output=output, base=plan["base_python"], wheels=plan["wheels"],
        bootstrap_saved_root=output / str(bootstrap["saved_root"]),
        runner_saved=output / str(runner["saved_path"]),
        platform_kind=str(plan["platform_kind"]),
    )
    if commands != expected_commands:
        _fail("offline PyOptiX command plan is not the exact frozen projection")
    install = commands[1].get("argv") if isinstance(commands[1], dict) else None
    if not isinstance(install, list) or len(install) < 13:
        _fail("offline PyOptiX install command differs")
    if install[1:6] != ["-I", "-S", "-B", "-P", "-c"] \
            or install[7:9] != ["--isolated", "install"] \
            or "runpy.run_module('pip',run_name='__main__')" not in install[6]:
        _fail("offline PyOptiX install is not site-disabled pip-module execution")
    required_flags = (
        "--no-index", "--no-deps", "--no-cache-dir",
        "--no-compile", "--disable-pip-version-check", "--target",
    )
    if any(install.count(flag) != 1 for flag in required_flags):
        _fail("offline PyOptiX install flags differ")
    target_index = install.index("--target")
    expected_target = Path(str(plan["output_directory"])) \
        / combined._venv_site_packages_relative(str(plan["platform_kind"]))
    if target_index + 1 >= len(install) \
            or install[target_index + 1] != str(expected_target) \
            or "--prefix" in install:
        _fail("offline PyOptiX pip target is not the exact venv site-packages")
    expected_wheels = [
        str(Path(str(plan["output_directory"])) / str(row["saved_path"]))
        for row in plan["wheels"]
    ]
    if install[-len(expected_wheels):] != expected_wheels:
        _fail("offline PyOptiX install wheel argv differs")
    for command in commands:
        if not isinstance(command, dict) or not isinstance(command.get("argv"), list):
            _fail("offline PyOptiX command row differs")
        if command["argv"][1:5] != ["-I", "-S", "-B", "-P"]:
            _fail(
                "offline PyOptiX build command does not disable "
                "site/bytecode/unsafe-path setup")
        lowered = "\n".join(str(item).lower() for item in command["argv"])
        if any(token in lowered for token in FORBIDDEN_NETWORK_TOKENS):
            _fail("offline PyOptiX command contains a network-capable token")
        if any(Path(str(item)).name.lower() in {"pip", "pip3", "pip3.12"}
               for item in command["argv"][:1]):
            _fail("offline PyOptiX command invokes a pip script/shebang")


def _match_live_inputs(
        plan: Mapping[str, object], specialization: Mapping[str, object]) -> None:
    root = Path(str(specialization["wheelhouse_root"]))
    try:
        manifest = wheelhouse.verify(root)
    except (wheelhouse.OfflineWheelhouseError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error
    manifest_record = _current_file_record(root / "wheelhouse_manifest.json")
    if manifest_record != specialization["wheelhouse_manifest"] \
            or manifest["manifest_sha256"] \
            != specialization["wheelhouse_manifest_sha256"] \
            or manifest["wheel_set_sha256"] != specialization["wheel_set_sha256"]:
        _fail("offline PyOptiX wheelhouse changed after planning")
    manifest_rows = manifest["wheels"]
    plan_rows = plan["wheels"]
    if len(plan_rows) != len(manifest_rows):
        _fail("offline PyOptiX generic/manifest wheel count differs")
    for (name, version), manifest_row, plan_row in zip(
            wheelhouse.REQUIRED_DISTRIBUTIONS, manifest_rows, plan_rows,
            strict=True):
        for key in (
                "distribution", "version", "bytes", "sha256", "member_count",
                "member_tree_sha256"):
            if plan_row.get(key) != manifest_row.get(key):
                _fail(f"offline PyOptiX wheel projection differs: {name}/{key}")
        expected_path = (root / str(manifest_row["saved_path"])).resolve(strict=True)
        if Path(str(plan_row["resolved_path"])) != expected_path \
                or plan_row["distribution"] != name or plan_row["version"] != version:
            _fail(f"offline PyOptiX wheel source differs: {name}")
    if _source_records() != specialization["source_implementations"]:
        _fail("offline PyOptiX helper source changed after planning")
    if _probe_base_python(Path(str(plan["base_python"]["invocation_path"]))) \
            != specialization["base_python_safe_probe"]:
        _fail("offline PyOptiX base Python probe changed after planning")
    if _bootstrap_profile(Path(str(
            plan["virtualenv_bootstrap"]["source_root"]))) \
            != specialization["virtualenv_bootstrap_profile"]:
        _fail("offline PyOptiX virtualenv bootstrap profile changed after planning")
    if _entrypoint_and_script_boundary(root, manifest) \
            != specialization["entrypoint_and_script_boundary"]:
        _fail("offline PyOptiX wheel entrypoint/script inventory changed")


def _validate_plan(
        value: Any, *, require_live_inputs: bool) -> dict[str, object]:
    try:
        plan = combined._validate_plan(value)
    except combined.CombinedRuntimeError as error:
        raise OfflinePyOptiXInstallError(str(error)) from error
    specialization = plan.get(SPECIALIZATION_KEY)
    if not isinstance(specialization, dict) or set(specialization) != {
            "schema", "status", "profile", "required_distributions",
            "wheelhouse_root", "wheelhouse_manifest",
            "wheelhouse_manifest_sha256", "wheel_set_sha256", "wheel_count",
            "base_python_safe_probe", "virtualenv_bootstrap_profile",
            "source_implementations", "entrypoint_and_script_boundary",
            "pip_policy", "validation_boundary",
            "specialization_sha256"}:
        _fail("offline PyOptiX specialization envelope differs")
    body = dict(specialization)
    seal = body.pop("specialization_sha256")
    if not isinstance(seal, str) or not SHA256_RE.fullmatch(seal) \
            or seal != _digest(body):
        _fail("offline PyOptiX specialization seal differs")
    if specialization["schema"] != SPECIALIZATION_SCHEMA \
            or specialization["status"] \
            != "PLANNED_EXACT_OFFLINE_PYOPTIX_CLEAN_INSTALL_PROFILE" \
            or specialization["profile"] != wheelhouse.PROFILE \
            or specialization["required_distributions"] \
            != wheelhouse.REQUIRED_VERSION_MAP \
            or specialization["wheel_count"] != len(wheelhouse.REQUIRED_DISTRIBUTIONS):
        _fail("offline PyOptiX specialization profile differs")
    if specialization["pip_policy"] != {
            "python_interpreter_executes_pip_module_without_script_or_shebang": (
                True),
            "pip_loaded_via_runpy_with_site_disabled": True,
            "safe_path_enabled_for_every_build_command": True,
            "isolated": True,
            "no_index": True,
            "no_deps": True,
            "no_cache_dir": True,
            "no_compile": True,
            "exact_venv_site_packages_target": True,
            "prefix_mode_allowed": False,
            "implicit_download_allowed": False,
            "pip_script_or_shebang_invocation_allowed": False,
    }:
        _fail("offline PyOptiX pip policy differs")
    script_boundary = specialization["entrypoint_and_script_boundary"]
    if not isinstance(script_boundary, dict) \
            or script_boundary.get("goal5802_required_console_entry_point_count") \
            != 0 \
            or script_boundary.get("goal5802_required_wheel_data_script_count") \
            != 0 \
            or script_boundary.get("goal5802_runtime_interface") \
            != "PYTHON_IMPORTS_ONLY" \
            or script_boundary.get("script_absence_claimed") is not False \
            or script_boundary.get(
                "observed_scripts_or_entry_points_authorize_invocation") \
            is not False \
            or script_boundary.get("wheel_import_or_execution_count") != 0 \
            or script_boundary.get("wheel_count") \
            != len(wheelhouse.REQUIRED_DISTRIBUTIONS):
        _fail("offline PyOptiX wheel script requirement boundary differs")
    script_body = dict(script_boundary)
    script_seal = script_body.pop("inventory_sha256", None)
    if script_seal != _digest(script_body):
        _fail("offline PyOptiX wheel script inventory seal differs")
    if specialization["validation_boundary"] != {
            "installed_measured_runtime_distribution_import_count": 0,
            "pyoptix_import_count": 0,
            "cupy_import_count": 0,
            "device_query_count": 0,
            "gpu_kernel_launch_count": 0,
            "registered_measurement_clock_read_count": 0,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "execution_authority_consumed": False,
            "self_hash_is_execution_authority": False,
            "caller_must_bind_exact_plan_before_run": True,
    }:
        _fail("offline PyOptiX no-execution boundary differs")
    expected_versions = list(wheelhouse.REQUIRED_DISTRIBUTIONS)
    observed_versions = [
        (str(row.get("distribution")), str(row.get("version")))
        for row in plan.get("wheels", []) if isinstance(row, dict)
    ]
    if observed_versions != expected_versions:
        _fail("offline PyOptiX plan distribution order/version differs")
    if plan.get("pip_invocation_policy") != {
            "python_interpreter_executes_pip_module_without_script_or_shebang": (
                True),
            "pip_loaded_via_runpy_with_site_disabled": True,
            "pip_script_or_shebang_invocation_forbidden": True,
            "network_index_access": False,
            "dependency_resolution": "NO_DEPS__EVERY_WHEEL_EXPLICIT",
            "only_unlisted_distributions_allowed": sorted(
                combined.VIRTUALENV_SEED_DISTRIBUTIONS),
            "virtualenv_app_data_confined_inside_output": True,
            "pip_install_target_exact_venv_site_packages": str(
                Path(str(plan["output_directory"]))
                / combined._venv_site_packages_relative(
                    str(plan["platform_kind"]))),
            "console_entrypoints_not_used_by_goal5802_runtime": True,
            "wheel_data_scripts_not_claimed_as_runtime_interfaces": True,
            "site_initialization_disabled_for_every_build_command": True,
            "pth_execution_during_build_forbidden": True,
            "pip_bytecode_compilation_during_install_forbidden": True,
    } or plan.get("execution_scope") != {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
            "measured_arm_import_count": 0,
            "execution_authority_consumed": False,
    }:
        _fail("offline PyOptiX generic no-network/no-execution policy differs")
    _validate_install_command(plan)
    if require_live_inputs:
        _match_live_inputs(plan, specialization)
    return plan


def write_plan(path: Path, plan: Mapping[str, object]) -> None:
    try:
        combined.write_plan(path, plan)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error


def _copy_provenance(
        source: Path, destination: Path, expected: Mapping[str, object]) -> None:
    try:
        combined._copy_exact(source, destination, expected)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflinePyOptiXInstallError(str(error)) from error


def _write_terminal_failure(
        output: Path, plan: Mapping[str, object], error: BaseException) -> None:
    if not output.exists() or not output.is_dir():
        return
    failure = {
        "schema": FAILURE_SCHEMA,
        "status": "TERMINAL_OFFLINE_PYOPTIX_CLEAN_INSTALL_FAILURE__NO_REUSE",
        "plan_sha256": plan.get("plan_sha256"),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "execution_authority_consumed": False,
        "retry_or_replacement_authorized": False,
    }
    failure["failure_receipt_sha256"] = _digest(failure)
    try:
        combined._write_create_only(
            output / "offline_pyoptix_terminal_failure_receipt.json",
            _canonical(failure) + b"\n")
    except (OSError, FileExistsError):
        pass


def run(plan_path: Path) -> dict[str, object]:
    plan_path = plan_path.expanduser().resolve(strict=True)
    raw_plan, plan_file_sha256 = _strict_json_with_file_sha(
        plan_path, "offline PyOptiX plan")
    plan = _validate_plan(
        raw_plan, require_live_inputs=True)
    output = Path(str(plan["output_directory"]))
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    try:
        generic_receipt = combined.run_plan(
            plan_path, expected_plan_file_sha256=plan_file_sha256)
        if generic_receipt.get("plan_file_sha256") != plan_file_sha256 \
                or generic_receipt.get("plan_sha256") != plan["plan_sha256"]:
            _fail("combined runtime executed a different plan identity")
        specialization = plan[SPECIALIZATION_KEY]
        provenance = output / "offline_pyoptix_provenance"
        source_records = specialization["source_implementations"]
        copies = (
            (Path(str(specialization["wheelhouse_manifest"]["resolved_path"])),
             provenance / "wheelhouse_manifest.json",
             specialization["wheelhouse_manifest"]),
            (Path(str(source_records["offline_installer"]["resolved_path"])),
             provenance / "goal5802_clean_install_pyoptix_offline.py",
             source_records["offline_installer"]),
            (Path(str(source_records["wheelhouse_builder"]["resolved_path"])),
             provenance / "goal5802_build_offline_python_wheelhouse.py",
             source_records["wheelhouse_builder"]),
            (Path(str(source_records["combined_runtime_builder"]["resolved_path"])),
             provenance / "goal5802_build_combined_runtime_untimed.py",
             source_records["combined_runtime_builder"]),
        )
        for source, destination, expected in copies:
            _copy_provenance(source, destination, expected)
        provenance_rows = [
            _record(path, output) for path in sorted(provenance.iterdir())
        ]
        generic_path = output / "combined_runtime_receipt.json"
        snapshot_path = output / "installed_packages.json"
        body: dict[str, object] = {
            "schema": RECEIPT_SCHEMA,
            "status": "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED",
            "plan_sha256": plan["plan_sha256"],
            "plan_file_sha256": plan_file_sha256,
            "specialization_sha256": specialization["specialization_sha256"],
            "wheelhouse_manifest_sha256": (
                specialization["wheelhouse_manifest_sha256"]),
            "wheel_set_sha256": specialization["wheel_set_sha256"],
            "required_distributions": wheelhouse.REQUIRED_VERSION_MAP,
            "generic_combined_runtime_receipt": _record(generic_path, output),
            "generic_combined_runtime_receipt_sha256": (
                generic_receipt["receipt_sha256"]),
            "installed_package_snapshot": _record(snapshot_path, output),
            "installed_package_snapshot_sha256": (
                generic_receipt["installed_package_snapshot_sha256"]),
            "generic_input_tree_sha256": generic_receipt["input_tree_sha256"],
            "generic_commands_sha256": generic_receipt["commands_sha256"],
            "generic_venv_member_count": generic_receipt["venv_member_count"],
            "generic_venv_member_tree_sha256": (
                generic_receipt["venv_member_tree_sha256"]),
            "generic_base_python_site_boundary": (
                generic_receipt["base_python_site_boundary"]),
            "install_command": plan["commands"][1]["argv"],
            "provenance_files": provenance_rows,
            "provenance_tree_sha256": _digest(provenance_rows),
            "pip_policy": specialization["pip_policy"],
            "validation_boundary": specialization["validation_boundary"],
            "create_only": True,
        }
        receipt = {**body, "receipt_sha256": _digest(body)}
        combined._write_create_only(
            output / "offline_pyoptix_clean_install_receipt.json",
            _canonical(receipt) + b"\n")
        return receipt
    except BaseException as error:
        _write_terminal_failure(output, plan, error)
        raise


def _verify_provenance_rows(
        output: Path, rows: Any) -> list[dict[str, object]]:
    if not isinstance(rows, list) or len(rows) != 4:
        _fail("offline PyOptiX provenance row count differs")
    observed = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            _fail("offline PyOptiX provenance row differs")
        relative = PurePosixPath(str(row["path"]))
        if relative.is_absolute() or ".." in relative.parts \
                or len(relative.parts) != 2 \
                or relative.parts[0] != "offline_pyoptix_provenance":
            _fail("offline PyOptiX provenance path is unsafe")
        path = output / Path(*relative.parts)
        rebuilt = _record(path, output)
        if rebuilt != row:
            _fail(f"offline PyOptiX provenance identity differs: {relative}")
        observed.append(rebuilt)
    if len({str(row["path"]) for row in observed}) != len(observed):
        _fail("offline PyOptiX provenance paths are duplicated")
    return observed


def verify(output: Path) -> dict[str, object]:
    output = output.expanduser().resolve(strict=True)
    if output.is_symlink() or not output.is_dir():
        _fail("offline PyOptiX output is not a real directory")
    if (output / "offline_pyoptix_terminal_failure_receipt.json").exists():
        _fail("offline PyOptiX output is terminal-failed")
    plan = _validate_plan(
        _strict_json(output / "plan.json", "saved offline PyOptiX plan"),
        require_live_inputs=True)
    try:
        generic = combined.verify_run(output)
    except combined.CombinedRuntimeError as error:
        raise OfflinePyOptiXInstallError(str(error)) from error
    receipt = _strict_json(
        output / "offline_pyoptix_clean_install_receipt.json",
        "offline PyOptiX clean-install receipt")
    if not isinstance(receipt, dict) or set(receipt) != {
            "schema", "status", "plan_sha256", "specialization_sha256",
            "plan_file_sha256",
            "wheelhouse_manifest_sha256", "wheel_set_sha256",
            "required_distributions", "generic_combined_runtime_receipt",
            "generic_combined_runtime_receipt_sha256",
            "installed_package_snapshot", "installed_package_snapshot_sha256",
            "generic_input_tree_sha256", "generic_commands_sha256",
            "generic_venv_member_count", "generic_venv_member_tree_sha256",
            "generic_base_python_site_boundary",
            "install_command", "provenance_files", "provenance_tree_sha256",
            "pip_policy", "validation_boundary", "create_only",
            "receipt_sha256"}:
        _fail("offline PyOptiX receipt envelope differs")
    body = dict(receipt)
    seal = body.pop("receipt_sha256")
    if not isinstance(seal, str) or not SHA256_RE.fullmatch(seal) \
            or seal != _digest(body):
        _fail("offline PyOptiX receipt seal differs")
    specialization = plan[SPECIALIZATION_KEY]
    if receipt["schema"] != RECEIPT_SCHEMA \
            or receipt["status"] \
            != "PASS__OFFLINE_CREATE_ONLY_PYOPTIX_RUNTIME_INSTALLED" \
            or receipt["plan_sha256"] != plan["plan_sha256"] \
            or receipt["plan_file_sha256"] \
            != _sha_file(output / "plan.json") \
            or receipt["plan_file_sha256"] != generic["plan_file_sha256"] \
            or receipt["specialization_sha256"] \
            != specialization["specialization_sha256"] \
            or receipt["wheelhouse_manifest_sha256"] \
            != specialization["wheelhouse_manifest_sha256"] \
            or receipt["wheel_set_sha256"] != specialization["wheel_set_sha256"] \
            or receipt["required_distributions"] \
            != wheelhouse.REQUIRED_VERSION_MAP \
            or receipt["pip_policy"] != specialization["pip_policy"] \
            or receipt["validation_boundary"] \
            != specialization["validation_boundary"] \
            or receipt["create_only"] is not True:
        _fail("offline PyOptiX receipt profile projection differs")
    if receipt["generic_combined_runtime_receipt"] \
            != _record(output / "combined_runtime_receipt.json", output) \
            or receipt["generic_combined_runtime_receipt_sha256"] \
            != generic["receipt_sha256"] \
            or receipt["installed_package_snapshot"] \
            != _record(output / "installed_packages.json", output) \
            or receipt["installed_package_snapshot_sha256"] \
            != generic["installed_package_snapshot_sha256"] \
            or receipt["generic_input_tree_sha256"] != generic["input_tree_sha256"] \
            or receipt["generic_commands_sha256"] != generic["commands_sha256"] \
            or receipt["generic_venv_member_count"] \
            != generic["venv_member_count"] \
            or receipt["generic_venv_member_tree_sha256"] \
            != generic["venv_member_tree_sha256"] \
            or receipt["generic_base_python_site_boundary"] \
            != generic["base_python_site_boundary"] \
            or receipt["install_command"] != plan["commands"][1]["argv"]:
        _fail("offline PyOptiX generic-runtime projection differs")
    rows = _verify_provenance_rows(output, receipt["provenance_files"])
    if rows != sorted(rows, key=lambda row: str(row["path"])) \
            or receipt["provenance_tree_sha256"] != _digest(rows):
        _fail("offline PyOptiX provenance tree differs")
    copied_manifest = output / "offline_pyoptix_provenance/wheelhouse_manifest.json"
    if copied_manifest.read_bytes() != Path(
            str(specialization["wheelhouse_manifest"]["resolved_path"])).read_bytes():
        _fail("offline PyOptiX copied wheelhouse manifest differs")
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan/build/verify an exact offline PyOptiX runtime")
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan")
    plan.add_argument("--output-directory", type=Path, required=True)
    plan.add_argument("--base-python", type=Path, required=True)
    plan.add_argument("--virtualenv-bootstrap-root", type=Path, required=True)
    plan.add_argument("--wheelhouse-root", type=Path, required=True)
    plan.add_argument("--plan-output", type=Path, required=True)
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--plan", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "plan":
        output = args.output_directory.expanduser().absolute()
        plan_output = args.plan_output.expanduser().absolute()
        try:
            plan_output.relative_to(output)
        except ValueError:
            pass
        else:
            _fail("plan output must be outside the future create-only runtime root")
        value = build_plan(
            output=args.output_directory, base_python=args.base_python,
            bootstrap_root=args.virtualenv_bootstrap_root,
            wheelhouse_root=args.wheelhouse_root)
        write_plan(args.plan_output, value)
        result = {
            "status": value[SPECIALIZATION_KEY]["status"],
            "plan_sha256": value["plan_sha256"],
        }
    elif args.command == "run":
        value = run(args.plan)
        result = {"status": value["status"],
                  "receipt_sha256": value["receipt_sha256"]}
    else:
        value = verify(args.output_directory)
        result = {"status": value["status"],
                  "receipt_sha256": value["receipt_sha256"]}
    result.update({
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    })
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
