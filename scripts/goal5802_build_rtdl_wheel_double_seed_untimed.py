#!/usr/bin/env python3
"""Build the exact Goal5802 RTDL wheel twice from Git blob bytes.

The two builds use independent materializations and PYTHONHASHSEED 1/777.
Source files are written from ``git cat-file`` rather than a Windows working
tree or ``git archive`` so checkout filters and CRLF conversion cannot enter
the wheel.  This transaction runs no RT program and records no timing.
"""

from __future__ import annotations

import argparse
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from typing import NoReturn


SCHEMA = "rtdl.goal5802.rtdl_wheel_double_seed.v2"
SEEDS = (1, 777)
BUILD_PIP_VERSION = "25.3"
BUILD_SETUPTOOLS_VERSION = "80.9.0"
BOOTSTRAP_DISTRIBUTIONS = {
    "distlib": "0.4.3",
    "filelock": "3.32.4",
    "platformdirs": "4.11.4",
    "virtualenv": "20.35.4",
}


class WheelBuildError(RuntimeError):
    """Fail-closed source or wheel build error."""


def _fail(message: str) -> NoReturn:
    raise WheelBuildError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _normalize_distribution(name: str) -> str:
    value = re.sub(r"[-_.]+", "-", name).lower()
    if not value or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        _fail(f"invalid bootstrap distribution name: {name!r}")
    return value


def _bootstrap_profile(root: Path) -> dict[str, object]:
    supplied = root.expanduser().absolute()
    if supplied.is_symlink():
        _fail("virtualenv bootstrap root may not be a symlink")
    root = supplied.resolve(strict=True)
    if not root.is_dir() or not (root / "virtualenv/__main__.py").is_file():
        _fail("virtualenv bootstrap root is incomplete")
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            _fail(f"virtualenv bootstrap contains a symlink: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha_file(path),
            })
    if not rows:
        _fail("virtualenv bootstrap root is empty")
    observed: dict[str, str] = {}
    for path in sorted(root.glob("*.dist-info/METADATA")):
        metadata = BytesParser().parsebytes(path.read_bytes())
        raw_name = metadata.get("Name")
        version = metadata.get("Version")
        if not raw_name or not version:
            _fail(f"bootstrap METADATA lacks Name/Version: {path}")
        name = _normalize_distribution(raw_name)
        if name in observed:
            _fail(f"bootstrap distribution is duplicated: {name}")
        observed[name] = version
    if observed != BOOTSTRAP_DISTRIBUTIONS:
        _fail("virtualenv bootstrap distribution profile differs")
    return {
        "root": str(root),
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": hashlib.sha256(_canonical(rows)).hexdigest(),
        "distributions": dict(sorted(observed.items())),
    }


def _build_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _probe_build_environment(python: Path) -> dict[str, object]:
    code = (
        "import importlib.metadata as m,json,sys;"
        "print(json.dumps({'implementation':sys.implementation.name,"
        "'python':[sys.version_info.major,sys.version_info.minor,"
        "sys.version_info.micro],'pip':m.version('pip'),"
        "'setuptools':m.version('setuptools')},sort_keys=True))"
    )
    completed = subprocess.run(
        [str(python), "-I", "-B", "-c", code], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        _fail("dedicated wheel-build environment probe failed")
    try:
        value = json.loads(completed.stdout.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WheelBuildError(
            "dedicated wheel-build environment probe is not JSON") from error
    if not isinstance(value, dict) or value.get("implementation") != "cpython" \
            or value.get("pip") != BUILD_PIP_VERSION \
            or value.get("setuptools") != BUILD_SETUPTOOLS_VERSION:
        _fail("dedicated wheel-build environment profile differs")
    return value


def _create_build_environment(
        invocation_python: Path, bootstrap_root: Path, output: Path,
        log_root: Path) -> tuple[Path, dict[str, object]]:
    bootstrap = _bootstrap_profile(bootstrap_root)
    environment_root = output / "build_environment"
    venv = environment_root / "venv"
    app_data = environment_root / "virtualenv_app_data"
    bootstrap_code = (
        "import runpy,sys;"
        "sys.dont_write_bytecode=True;"
        f"sys.path.insert(0,{str(bootstrap_root.resolve(strict=True))!r});"
        "sys.argv=['virtualenv','--no-download','--copies','--app-data',"
        f"{str(app_data)!r},'--pip',{BUILD_PIP_VERSION!r},'--setuptools',"
        f"{BUILD_SETUPTOOLS_VERSION!r},{str(venv)!r}];"
        "runpy.run_module('virtualenv',run_name='__main__')"
    )
    command = [
        str(invocation_python), "-I", "-S", "-B", "-P", "-c",
        bootstrap_code,
    ]
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment.pop("LD_PRELOAD", None)
    environment.update({
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    completed = subprocess.run(
        command, cwd=output, env=environment, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = log_root / "build_environment.stdout.bin"
    stderr = log_root / "build_environment.stderr.bin"
    exit_code = log_root / "build_environment.exit_code"
    stdout.write_bytes(completed.stdout)
    stderr.write_bytes(completed.stderr)
    exit_code.write_text(f"{completed.returncode}\n", encoding="ascii")
    python = _build_python(venv)
    if completed.returncode != 0 or python.is_symlink() or not python.is_file():
        _fail("dedicated offline wheel-build environment creation failed")
    profile = _probe_build_environment(python)
    if _bootstrap_profile(bootstrap_root) != bootstrap:
        _fail("virtualenv bootstrap changed during environment creation")
    return python, {
        "argv": command,
        "environment": {
            key: environment[key] for key in (
                "PIP_CONFIG_FILE", "PIP_DISABLE_PIP_VERSION_CHECK",
                "PIP_NO_INDEX", "PYTHONNOUSERSITE",
                "PYTHONDONTWRITEBYTECODE")},
        "exit_code": completed.returncode,
        "stdout_sha256": _sha_file(stdout),
        "stderr_sha256": _sha_file(stderr),
        "bootstrap": bootstrap,
        "profile": profile,
        "invocation_python": str(invocation_python),
        "build_python": str(python.resolve(strict=True)),
        "network_allowed": False,
    }


def _git(git: Path, source: Path, *args: str, input_bytes: bytes | None = None) \
        -> bytes:
    completed = subprocess.run(
        [str(git), "-C", str(source), *args], input=input_bytes, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        _fail(
            f"git {' '.join(args)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


def _inventory(git: Path, source: Path, commit: str) \
        -> tuple[list[tuple[str, str, int]], bytes, str]:
    head = _git(git, source, "rev-parse", "HEAD").decode("ascii").strip()
    tree = _git(git, source, "rev-parse", f"{commit}^{{tree}}").decode(
        "ascii").strip()
    if head != commit:
        _fail("source HEAD differs from requested commit")
    if _git(git, source, "status", "--porcelain=v1", "--untracked-files=all"):
        _fail("source checkout is dirty, including untracked files")
    raw = _git(git, source, "ls-tree", "-rz", "--full-tree", commit)
    rows: list[tuple[str, str, int]] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        header, separator, raw_path = item.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3 or fields[1] != b"blob" \
                or fields[0] not in {b"100644", b"100755"}:
            _fail("source tree contains a non-regular entry")
        try:
            path = raw_path.decode("utf-8")
        except UnicodeDecodeError as error:
            raise WheelBuildError("source path is not UTF-8") from error
        parts = path.split("/")
        if not path or path.startswith("/") or any(
                part in {"", ".", ".."} for part in parts):
            _fail("source tree contains an unsafe path")
        rows.append((
            path, fields[2].decode("ascii"),
            0o755 if fields[0] == b"100755" else 0o644))
    if not rows or len(rows) != len({row[0] for row in rows}):
        _fail("source inventory is empty or duplicates")
    return rows, raw, tree


def _blob_payloads(git: Path, source: Path,
                   rows: list[tuple[str, str, int]]) -> list[bytes]:
    request = "".join(f"{object_id}\n" for _, object_id, _ in rows).encode(
        "ascii")
    raw = _git(git, source, "cat-file", "--batch", input_bytes=request)
    payloads: list[bytes] = []
    cursor = 0
    for _path, object_id, _mode in rows:
        end = raw.find(b"\n", cursor)
        if end < 0:
            _fail("git cat-file header is truncated")
        header = raw[cursor:end].split()
        if len(header) != 3 or header[0].decode("ascii") != object_id \
                or header[1] != b"blob":
            _fail("git cat-file returned the wrong object")
        size = int(header[2])
        start = end + 1
        payload = raw[start:start + size]
        cursor = start + size
        if len(payload) != size or raw[cursor:cursor + 1] != b"\n" \
                or _git_blob_sha1(payload) != object_id:
            _fail("git cat-file payload is truncated or does not rehash")
        cursor += 1
        payloads.append(payload)
    if cursor != len(raw):
        _fail("git cat-file has trailing output")
    return payloads


def _materialize(root: Path, rows: list[tuple[str, str, int]],
                 payloads: list[bytes]) -> None:
    if root.exists() or root.is_symlink():
        raise FileExistsError(root)
    root.mkdir(parents=True)
    for (relative, object_id, mode), payload in zip(rows, payloads):
        if _git_blob_sha1(payload) != object_id:
            _fail("source blob changed before materialization")
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(
            target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
        os.chmod(target, mode)


def _run_build(python: Path, source: Path, wheel_dir: Path, seed: int,
               epoch: int, log_root: Path) -> tuple[Path, dict[str, object]]:
    wheel_dir.mkdir()
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    environment.pop("LD_PRELOAD", None)
    environment.update({
        "PIP_CONFIG_FILE": os.devnull,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_INDEX": "1",
        "PYTHONHASHSEED": str(seed),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "SOURCE_DATE_EPOCH": str(epoch),
    })
    command = [
        str(python), "-I", "-B", "-m", "pip", "wheel",
        "--no-build-isolation", "--no-deps", "--no-cache-dir",
        "--disable-pip-version-check", "--wheel-dir", str(wheel_dir),
        str(source),
    ]
    completed = subprocess.run(
        command, cwd=source, env=environment, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = log_root / f"seed{seed}.stdout.bin"
    stderr = log_root / f"seed{seed}.stderr.bin"
    exit_code = log_root / f"seed{seed}.exit_code"
    stdout.write_bytes(completed.stdout)
    stderr.write_bytes(completed.stderr)
    exit_code.write_text(f"{completed.returncode}\n", encoding="ascii")
    wheels = sorted(wheel_dir.glob("*.whl"))
    if completed.returncode != 0 or len(wheels) != 1 \
            or wheels[0].is_symlink() or not wheels[0].is_file():
        _fail(f"seed {seed} wheel build failed or emitted !=1 wheel")
    receipt = {
        "seed": seed,
        "argv": command,
        "environment": {
            key: environment[key] for key in (
                "PIP_CONFIG_FILE", "PIP_DISABLE_PIP_VERSION_CHECK",
                "PIP_NO_INDEX", "PYTHONHASHSEED", "PYTHONNOUSERSITE",
                "PYTHONDONTWRITEBYTECODE", "SOURCE_DATE_EPOCH")},
        "exit_code": completed.returncode,
        "stdout_sha256": _sha_file(stdout),
        "stderr_sha256": _sha_file(stderr),
        "wheel_name": wheels[0].name,
        "wheel_bytes": wheels[0].stat().st_size,
        "wheel_sha256": _sha_file(wheels[0]),
    }
    return wheels[0], receipt


def build(args: argparse.Namespace) -> dict[str, object]:
    source = args.source_root.expanduser().resolve(strict=True)
    git = args.git.expanduser().resolve(strict=True)
    python = args.python.expanduser().resolve(strict=True)
    bootstrap_root = args.virtualenv_bootstrap_root.expanduser().absolute()
    output = args.output.expanduser().absolute()
    if source.is_symlink() or not source.is_dir():
        _fail("source root must be a real directory")
    for label, path in (("git", git), ("python", python)):
        if not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
            _fail(f"{label} must resolve to a regular file")
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    try:
        output.relative_to(source)
    except ValueError:
        pass
    else:
        _fail("wheel output must be outside source checkout")
    if len(args.commit) != 40 or any(
            character not in "0123456789abcdef" for character in args.commit):
        _fail("commit must be a full lowercase Git SHA-1")
    observed_epoch = int(_git(
        git, source, "show", "-s", "--format=%ct", args.commit).decode(
            "ascii").strip())
    if args.source_date_epoch != observed_epoch:
        _fail("SOURCE_DATE_EPOCH differs from exact commit epoch")
    rows, inventory_raw, tree = _inventory(git, source, args.commit)
    if tree != args.tree:
        _fail("source tree differs from requested tree")
    payloads = _blob_payloads(git, source, rows)
    output.mkdir(parents=True)
    logs = output / "logs"
    logs.mkdir()
    build_python, build_environment = _create_build_environment(
        python, bootstrap_root, output, logs)
    builds: list[tuple[Path, dict[str, object]]] = []
    for seed in SEEDS:
        materialized = output / f"source_seed{seed}"
        _materialize(materialized, rows, payloads)
        builds.append(_run_build(
            build_python, materialized, output / f"wheel_seed{seed}", seed,
            observed_epoch, logs))
    first, first_receipt = builds[0]
    second, second_receipt = builds[1]
    if first.name != second.name or first.read_bytes() != second.read_bytes():
        _fail("RTDL wheel differs across PYTHONHASHSEED 1 and 777")
    published = output / first.name
    descriptor = os.open(
        published, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(first.read_bytes())
        stream.flush()
        os.fsync(stream.fileno())
    result: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS__EXACT_GIT_BLOBS__DOUBLE_SEED_BYTE_IDENTICAL_WHEEL",
        "source_commit": args.commit,
        "source_tree": tree,
        "source_date_epoch": observed_epoch,
        "source_file_count": len(rows),
        "source_payload_bytes": sum(len(payload) for payload in payloads),
        "source_inventory_sha256": hashlib.sha256(inventory_raw).hexdigest(),
        "build_environment": build_environment,
        "seeds": list(SEEDS),
        "builds": [first_receipt, second_receipt],
        "published_wheel": {
            "path": str(published.resolve()),
            "bytes": published.stat().st_size,
            "sha256": _sha_file(published),
        },
        "network_allowed": False,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
        "execution_authority_consumed": False,
    }
    result["receipt_sha256"] = hashlib.sha256(_canonical(result)).hexdigest()
    receipt = output / "receipt.json"
    receipt.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--git", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument(
        "--virtualenv-bootstrap-root", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--source-date-epoch", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> int:
    result = build(_parser().parse_args())
    print(json.dumps({
        "status": result["status"],
        "wheel_sha256": result["published_wheel"]["sha256"],
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
