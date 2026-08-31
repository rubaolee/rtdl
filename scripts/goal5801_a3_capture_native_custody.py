#!/usr/bin/env python3
"""Create-only native source-to-binary custody packet for Goal5801 A4.

The capture is deliberately post-build and untimed.  The native build must
emit an nvcc dependency file (``-MD -MF ...``) from the same compile command.
This tool preserves a clean, origin-bound projection containing every
first-party source consumed by the registered native target, every compiler
dependency byte named by that depfile, exact compiler/link inputs, build
receipts, tool versions, and the native binary.  It explicitly does not claim
custody of the entire product tree, CUDA/OptiX redistribution, or a hermetic
byte-reproducible toolchain image.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import subprocess
import tarfile
from typing import Iterable, NoReturn


SCHEMA = "rtdl.goal5801.a4.native_custody.v3"
MANIFEST_SCHEMA = "rtdl.goal5801.a4.native_custody_manifest.v3"


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _write_create_only(path: Path, payload: bytes, mode: int = 0o644) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        _fail(f"unsafe archive path: {value}")
    return path


def _tar_gz(entries: Iterable[tuple[str, bytes, int]]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, payload, mode in sorted(entries, key=lambda row: row[0]):
            _safe_relative(name)
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            info.mode = mode
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(payload))
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    return output.getvalue()


def _git_inventory(root: Path, git: Path, commit: str) \
        -> tuple[list[tuple[str, bytes, int]], bytes, str]:
    def run(*arguments: str) -> bytes:
        completed = subprocess.run(
            [str(git), "-C", str(root), *arguments], check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed.returncode != 0:
            _fail(f"git {' '.join(arguments)} failed: "
                  f"{completed.stderr.decode('utf-8', errors='replace')}")
        return completed.stdout

    observed_head = run("rev-parse", "HEAD").decode("ascii").strip()
    if observed_head != commit:
        _fail(f"source checkout HEAD differs from frozen commit: {observed_head}")
    if run("status", "--porcelain=v1", "--untracked-files=all"):
        _fail("source checkout is not clean, including untracked files")
    inventory_raw = run("ls-tree", "-rz", "--full-tree", commit)
    metadata: list[tuple[str, str, int]] = []
    for raw_row in inventory_raw.split(b"\0"):
        if not raw_row:
            continue
        header, separator, raw_path = raw_row.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3 or fields[1] != b"blob" \
                or fields[0] not in {b"100644", b"100755"}:
            _fail("Git tree contains a non-regular or malformed entry")
        relative = raw_path.decode("utf-8")
        _safe_relative(relative)
        metadata.append((relative, fields[2].decode("ascii"),
                         0o755 if fields[0] == b"100755" else 0o644))
    if not metadata or len(metadata) != len({row[0] for row in metadata}):
        _fail("Git commit inventory is empty or contains duplicates")

    request = "".join(f"{object_id}\n" for _, object_id, _ in metadata).encode("ascii")
    completed = subprocess.run(
        [str(git), "-C", str(root), "cat-file", "--batch"], input=request,
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        _fail("git cat-file --batch failed")
    cursor = 0
    entries: list[tuple[str, bytes, int]] = []
    for relative, object_id, mode in metadata:
        line_end = completed.stdout.find(b"\n", cursor)
        if line_end < 0:
            _fail("truncated git cat-file header")
        header = completed.stdout[cursor:line_end].split()
        if len(header) != 3 or header[0].decode("ascii") != object_id \
                or header[1] != b"blob":
            _fail("git cat-file returned the wrong object")
        size = int(header[2])
        start = line_end + 1
        payload = completed.stdout[start:start + size]
        cursor = start + size
        if len(payload) != size or completed.stdout[cursor:cursor + 1] != b"\n":
            _fail("truncated git cat-file payload")
        cursor += 1
        working = root / relative
        if working.is_symlink() or not working.is_file() \
                or working.read_bytes() != payload:
            _fail(f"source checkout byte differs from frozen commit: {relative}")
        entries.append((relative, payload, mode))
    if cursor != len(completed.stdout):
        _fail("unexpected trailing git cat-file output")
    tree = run("rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
    return sorted(entries), inventory_raw, tree


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _git_object_sha1(kind: str, payload: bytes) -> str:
    header = f"{kind} {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _parse_full_inventory(
        raw: bytes) -> dict[bytes, tuple[bytes, bytes, str]]:
    observed: dict[bytes, tuple[bytes, bytes, str]] = {}
    allowed = {
        (b"100644", b"blob"), (b"100755", b"blob"),
        (b"120000", b"blob"), (b"160000", b"commit"),
    }
    if not raw or not raw.endswith(b"\0"):
        _fail("origin full inventory is not nonempty NUL-terminated data")
    for row in raw.split(b"\0")[:-1]:
        header, separator, raw_path = row.partition(b"\t")
        fields = header.split()
        if not separator or not raw_path or len(fields) != 3 \
                or (fields[0], fields[1]) not in allowed \
                or len(fields[2]) != 40:
            _fail("origin full inventory row invalid")
        try:
            object_id = fields[2].decode("ascii")
            bytes.fromhex(object_id)
        except (UnicodeDecodeError, ValueError):
            _fail("origin full inventory object id invalid")
        if raw_path.startswith(b"/") or b"\0" in raw_path \
                or any(part in {b"", b".", b".."}
                       for part in raw_path.split(b"/")):
            _fail("origin full inventory path invalid")
        if raw_path in observed:
            _fail("origin full inventory contains duplicate path")
        observed[raw_path] = (fields[0], fields[1], object_id)
    return observed


def _inventory_tree_sha1(
        observed: dict[bytes, tuple[bytes, bytes, str]]) -> str:
    root: dict[bytes, object] = {}
    for raw_path, (mode, _kind, object_id) in observed.items():
        parts = tuple(raw_path.split(b"/"))
        node = root
        for part in parts[:-1]:
            existing = node.setdefault(part, {})
            if not isinstance(existing, dict):
                _fail("origin inventory file/directory conflict")
            node = existing
        if parts[-1] in node:
            _fail("origin inventory duplicate/conflicting path")
        node[parts[-1]] = (mode, object_id)

    def tree_sha(node: dict[bytes, object]) -> str:
        rows: list[tuple[bytes, bytes]] = []
        for raw_name, value in node.items():
            if isinstance(value, dict):
                mode = b"40000"
                object_id = tree_sha(value)
                sort_key = raw_name + b"/"
            else:
                mode, object_id = value
                sort_key = raw_name
            row = mode + b" " + raw_name + b"\0" + bytes.fromhex(object_id)
            rows.append((sort_key, row))
        payload = b"".join(row for _, row in sorted(rows))
        return _git_object_sha1("tree", payload)

    return tree_sha(root)


def _verify_origin_authority(
        commit_payload: bytes, full_inventory: bytes,
        tracked_entries: list[tuple[str, bytes, int]],
        commit: str, tree: str) -> None:
    if _git_object_sha1("commit", commit_payload) != commit:
        _fail("origin commit object payload does not hash to origin commit")
    first_line = commit_payload.splitlines()[0] if commit_payload else b""
    if first_line != f"tree {tree}".encode("ascii"):
        _fail("origin commit object does not bind the declared origin tree")
    observed = _parse_full_inventory(full_inventory)
    if _inventory_tree_sha1(observed) != tree:
        _fail("origin full inventory does not reconstruct origin tree")
    for path, payload, tracked_mode in tracked_entries:
        raw_path = path.encode("utf-8")
        expected_mode = b"100755" if tracked_mode == 0o755 else b"100644"
        row = observed.get(raw_path)
        if row is None or row[0] != expected_mode or row[1] != b"blob" \
                or row[2] != _git_blob_sha1(payload):
            _fail(f"source projection is not an exact origin blob subset: {path}")


def _source_rows(tracked_entries: list[tuple[str, bytes, int]]) \
        -> tuple[list[dict[str, object]], bytes]:
    rows: list[dict[str, object]] = []
    entries: list[tuple[str, bytes, int]] = []
    for relative, payload, mode in tracked_entries:
        _safe_relative(relative)
        rows.append({"path": relative, "bytes": len(payload),
                     "sha256": _sha(payload), "mode": mode})
        entries.append((relative, payload, mode))
    if not rows:
        _fail("prebuild source tree is empty")
    return rows, _tar_gz(entries)


def _parse_depfile(path: Path, cwd: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8").replace("\\\n", " ")
    _, separator, dependencies = text.partition(":")
    if not separator:
        _fail("nvcc dependency file has no target separator")
    observed: dict[str, Path] = {}
    for token in shlex.split(dependencies, posix=True):
        candidate = Path(token)
        if not candidate.is_absolute():
            candidate = cwd / candidate
        candidate = candidate.resolve()
        if not candidate.is_file() or candidate.is_symlink():
            _fail(f"dependency is not a regular resolved file: {candidate}")
        observed[str(candidate)] = candidate
    if not observed:
        _fail("nvcc dependency closure is empty")
    return [observed[key] for key in sorted(observed)]


def _named_path(value: str) -> tuple[str, Path]:
    name, separator, raw_path = value.partition("=")
    if not separator or not name or "/" in name or "\\" in name:
        raise argparse.ArgumentTypeError("expected safe NAME=PATH")
    supplied = Path(raw_path).expanduser()
    if supplied.is_symlink():
        raise argparse.ArgumentTypeError(f"symlink forbidden: {supplied}")
    path = supplied.resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"not a regular resolved file: {path}")
    return name, path


def _named_rows(values: list[tuple[str, Path]], kind: str,
                entries: list[tuple[str, bytes, int]]) -> list[dict[str, object]]:
    if len({name for name, _ in values}) != len(values):
        _fail(f"duplicate {kind} label")
    rows = []
    for name, path in sorted(values):
        payload = path.read_bytes()
        archive_path = f"{kind}/{name}/{path.name}"
        entries.append((archive_path, payload,
                        0o755 if os.access(path, os.X_OK) else 0o644))
        rows.append({
            "name": name,
            "original_path": str(path),
            "archive_path": archive_path,
            "bytes": len(payload),
            "sha256": _sha(payload),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--origin-commit", required=True)
    parser.add_argument("--origin-tree", required=True)
    parser.add_argument("--origin-commit-object", type=Path, required=True)
    parser.add_argument("--origin-inventory", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--build-cwd", type=Path, required=True)
    parser.add_argument("--build-source-root", type=Path, required=True,
                        help="source tree used by the recorded build command")
    parser.add_argument("--build-command", type=Path, required=True)
    parser.add_argument("--build-stdout", type=Path, required=True)
    parser.add_argument("--build-stderr", type=Path, required=True)
    parser.add_argument("--build-exit-code", type=Path, required=True)
    parser.add_argument("--dependency-file", type=Path, required=True)
    parser.add_argument("--build-environment", type=Path, required=True,
                        help="canonical JSON containing the declared build env")
    parser.add_argument("--tool", action="append", type=_named_path, default=[])
    parser.add_argument("--link-input", action="append", type=_named_path,
                        default=[])
    parser.add_argument("--tool-receipt", action="append", type=_named_path,
                        default=[])
    args = parser.parse_args()

    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if args.source_root.expanduser().is_symlink() \
            or args.build_source_root.expanduser().is_symlink() \
            or args.build_cwd.expanduser().is_symlink():
        _fail("source/build roots must not be supplied as symlinks")
    source_root = args.source_root.expanduser().resolve(strict=True)
    native = args.native.resolve()
    build_cwd = args.build_cwd.expanduser().resolve(strict=True)
    build_source_root = args.build_source_root.expanduser().resolve(strict=True)
    for path in (native, args.build_command, args.build_stdout,
                 args.build_stderr, args.build_exit_code,
                 args.dependency_file, args.build_environment,
                 args.origin_commit_object, args.origin_inventory):
        supplied = path.expanduser()
        if supplied.is_symlink() or not supplied.resolve(strict=True).is_file():
            _fail(f"required custody input is not a regular file: {path}")
    if args.build_exit_code.read_text(encoding="ascii").strip() != "0":
        _fail("native build did not exit zero")
    for label, identity in (
            ("source commit", args.source_commit),
            ("origin commit", args.origin_commit),
            ("origin tree", args.origin_tree)):
        if len(identity) != 40 or any(
                character not in "0123456789abcdef" for character in identity):
            _fail(f"{label} must be a full lowercase Git SHA-1")
    if {name for name, _ in args.tool} < {"nvcc", "make", "host_cxx", "git"}:
        _fail("tool identities must include nvcc, make, host_cxx and git")
    if {name for name, _ in args.tool_receipt} < {
            "nvcc_version", "make_version", "host_cxx_version", "git_version",
            "uname", "native_ldd"}:
        _fail("tool receipts are incomplete")
    if {name for name, _ in args.link_input} < {
            "cuda", "nvrtc", "geos_c"}:
        _fail("link-input identities must include cuda, nvrtc and geos_c")

    environment_raw = args.build_environment.read_bytes()
    environment = json.loads(environment_raw.decode("utf-8"))
    if not isinstance(environment, dict) or not environment:
        _fail("build environment must be a nonempty JSON object")
    if environment_raw != _canonical(environment) + b"\n":
        _fail("build environment must be canonical JSON plus terminal LF")
    command_raw = args.build_command.read_bytes()
    if b"nvcc" not in command_raw or b"rtdl_optix" not in command_raw:
        _fail("build command does not identify the native nvcc target")

    tool_paths = {name: path for name, path in args.tool}
    tracked_entries, git_inventory_raw, source_tree = _git_inventory(
        source_root, tool_paths["git"], args.source_commit)
    source_rows, source_archive = _source_rows(tracked_entries)
    origin_commit_raw = args.origin_commit_object.read_bytes()
    origin_inventory_raw = args.origin_inventory.read_bytes()
    _verify_origin_authority(
        origin_commit_raw, origin_inventory_raw, tracked_entries,
        args.origin_commit, args.origin_tree)
    # The clean prebuild capsule may be stored outside the build tree.  Bind it
    # to the actual tree used by the command by rehashing every captured source
    # path there after the build.  Build outputs may exist in the latter and are
    # intentionally not admitted as prebuild source.
    for row in source_rows:
        used = build_source_root / str(row["path"])
        if not used.is_file() or used.is_symlink() \
                or used.stat().st_size != row["bytes"] \
                or _sha_file(used) != row["sha256"]:
            _fail(f"build tree differs from prebuild source: {row['path']}")
    dependencies = _parse_depfile(args.dependency_file.resolve(), build_cwd)
    first_party_dependency_paths = set()
    for path in dependencies:
        try:
            relative = path.relative_to(build_source_root).as_posix()
        except ValueError:
            continue
        first_party_dependency_paths.add(relative)
    source_path_set = {str(row["path"]) for row in source_rows}
    if not first_party_dependency_paths or not first_party_dependency_paths \
            <= source_path_set:
        _fail("depfile first-party paths are absent from source projection")
    dependency_entries: list[tuple[str, bytes, int]] = []
    dependency_rows = []
    for index, path in enumerate(dependencies):
        payload = path.read_bytes()
        archive_path = f"dependencies/{index:05d}-{path.name}"
        dependency_entries.append((archive_path, payload, 0o644))
        dependency_rows.append({
            "original_path": str(path), "archive_path": archive_path,
            "bytes": len(payload), "sha256": _sha(payload),
        })
    dependency_archive = _tar_gz(dependency_entries)

    toolchain_entries: list[tuple[str, bytes, int]] = []
    tools = _named_rows(args.tool, "tools", toolchain_entries)
    links = _named_rows(args.link_input, "link_inputs", toolchain_entries)
    receipts = _named_rows(args.tool_receipt, "receipts", toolchain_entries)
    toolchain_archive = _tar_gz(toolchain_entries)

    source_manifest = {
        "schema": "rtdl.goal5801.a4.prebuild_source_projection_manifest.v3",
        "source_commit": args.source_commit,
        "source_tree": source_tree,
        "origin_commit": args.origin_commit,
        "origin_tree": args.origin_tree,
        "origin_full_inventory_sha256": _sha(origin_inventory_raw),
        "origin_commit_object_sha256": _sha(origin_commit_raw),
        "scope": "REGISTERED_NATIVE_BUILD_TARGET__NOT_ENTIRE_PRODUCT_TREE",
        "file_count": len(source_rows),
        "files": source_rows,
    }
    dependency_manifest = {
        "schema": "rtdl.goal5801.a4.compile_dependency_manifest.v2",
        "file_count": len(dependency_rows),
        "files": dependency_rows,
        "depfile_sha256": _sha_file(args.dependency_file.resolve()),
    }
    toolchain_manifest = {
        "schema": "rtdl.goal5801.a4.toolchain_manifest.v2",
        "tools": tools, "link_inputs": links, "receipts": receipts,
    }
    custody = {
        "schema": SCHEMA,
        "status": "CAPTURED__UNTIMED__VERIFY_BEFORE_CLAIM",
        "registered_performance_timing_count": 0,
        "source_commit": args.source_commit,
        "source_tree": source_tree,
        "origin_commit": args.origin_commit,
        "origin_tree": args.origin_tree,
        "origin_full_inventory_sha256": _sha(origin_inventory_raw),
        "origin_commit_object_sha256": _sha(origin_commit_raw),
        "native_sha256": _sha_file(native),
        "native_bytes": native.stat().st_size,
        "source_archive_sha256": _sha(source_archive),
        "source_manifest_sha256": _sha(_canonical(source_manifest) + b"\n"),
        "git_commit_tree_inventory_sha256": _sha(git_inventory_raw),
        "dependency_archive_sha256": _sha(dependency_archive),
        "dependency_manifest_sha256": _sha(_canonical(dependency_manifest) + b"\n"),
        "toolchain_archive_sha256": _sha(toolchain_archive),
        "toolchain_manifest_sha256": _sha(_canonical(toolchain_manifest) + b"\n"),
        "build_command_sha256": _sha(command_raw),
        "build_stdout_sha256": _sha_file(args.build_stdout.resolve()),
        "build_stderr_sha256": _sha_file(args.build_stderr.resolve()),
        "build_exit_code": 0,
        "build_environment_sha256": _sha(environment_raw),
        "complete_registered_native_target_source_projection_custody": True,
        "entire_product_source_tree_custody_claimed": False,
        "all_depfile_first_party_paths_present_in_projection": True,
        "source_checkout_clean_and_commit_exact": True,
        "build_tree_matches_prebuild_source": True,
        "complete_compiler_dependency_byte_custody": True,
        "declared_tool_and_link_input_byte_custody": True,
        "hermetic_toolchain_or_native_byte_reproducibility_claimed": False,
    }

    payloads = {
        "custody.json": _canonical(custody) + b"\n",
        "source/manifest.json": _canonical(source_manifest) + b"\n",
        "source/git_ls_tree_z.bin": git_inventory_raw,
        "source/origin_full_git_ls_tree_z.bin": origin_inventory_raw,
        "source/origin_commit_object.bin": origin_commit_raw,
        "source/prebuild_source.tar.gz": source_archive,
        "dependencies/manifest.json": _canonical(dependency_manifest) + b"\n",
        "dependencies/dependency_bytes.tar.gz": dependency_archive,
        "toolchain/manifest.json": _canonical(toolchain_manifest) + b"\n",
        "toolchain/tool_and_link_bytes.tar.gz": toolchain_archive,
        "build/command.txt": command_raw,
        "build/stdout.txt": args.build_stdout.read_bytes(),
        "build/stderr.txt": args.build_stderr.read_bytes(),
        "build/exit_code.txt": b"0\n",
        "build/environment.json": environment_raw,
        "build/dependencies.d": args.dependency_file.read_bytes(),
        "native/librtdl_optix.so": native.read_bytes(),
    }
    manifest_rows = [{
        "path": path, "bytes": len(payload), "sha256": _sha(payload),
    } for path, payload in sorted(payloads.items())]
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "file_count": len(manifest_rows),
        "total_payload_bytes": sum(int(row["bytes"]) for row in manifest_rows),
        "files": manifest_rows,
    }
    output.mkdir(parents=True)
    for relative, payload in payloads.items():
        _write_create_only(output / relative, payload,
                           0o755 if relative.endswith(".so") else 0o644)
    _write_create_only(output / "manifest.json", _canonical(manifest) + b"\n")
    print(json.dumps({
        "status": "CAPTURED__RUN_INDEPENDENT_VERIFIER",
        "manifest_sha256": _sha(_canonical(manifest) + b"\n"),
        "native_sha256": custody["native_sha256"],
        "source_file_count": len(source_rows),
        "dependency_file_count": len(dependency_rows),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
