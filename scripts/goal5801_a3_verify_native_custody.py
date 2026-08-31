#!/usr/bin/env python3
"""Independent standard-library verifier for Goal5801 A3 native custody."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from typing import Mapping, NoReturn


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git_blob_sha1(value: bytes) -> str:
    return hashlib.sha1(
        f"blob {len(value)}\0".encode("ascii") + value).hexdigest()


def _git_object_sha1(kind: str, value: bytes) -> str:
    return hashlib.sha1(
        f"{kind} {len(value)}\0".encode("ascii") + value).hexdigest()


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
        if raw_path.startswith(b"/") or any(
                part in {b"", b".", b".."}
                for part in raw_path.split(b"/")):
            _fail("origin full inventory path invalid")
        if raw_path in observed:
            _fail("origin full inventory contains duplicate path")
        observed[raw_path] = (fields[0], fields[1], object_id)
    return observed


def _inventory_tree_sha1(
        observed: Mapping[bytes, tuple[bytes, bytes, str]]) -> str:
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

    def tree_sha(node: Mapping[bytes, object]) -> str:
        rows: list[tuple[bytes, bytes]] = []
        for raw_name, value in node.items():
            if isinstance(value, dict):
                mode = b"40000"
                object_id = tree_sha(value)
                sort_key = raw_name + b"/"
            else:
                mode, object_id = value
                sort_key = raw_name
            rows.append((
                sort_key,
                mode + b" " + raw_name + b"\0" + bytes.fromhex(object_id),
            ))
        payload = b"".join(row for _, row in sorted(rows))
        return _git_object_sha1("tree", payload)

    return tree_sha(root)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _read_json(path: Path) -> tuple[Mapping[str, object], bytes]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict) or raw != _canonical(value) + b"\n":
        _fail(f"noncanonical JSON object: {path}")
    return value, raw


def _safe_archive(raw: bytes, label: str) -> dict[str, bytes]:
    import io
    rows: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() \
                    or member.islnk() or not member.isfile() \
                    or member.name in rows or member.mtime != 0:
                _fail(f"{label}: unsafe/noncanonical member {member.name}")
            stream = archive.extractfile(member)
            if stream is None:
                _fail(f"{label}: unreadable member {member.name}")
            rows[member.name] = stream.read()
    return rows


def _verify_rows(rows: object, files: Mapping[str, bytes], label: str) -> None:
    if not isinstance(rows, list):
        _fail(f"{label}: list required")
    expected = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
                "path", "bytes", "sha256"}:
            _fail(f"{label}: invalid row")
        path = str(row["path"])
        expected.add(path)
        payload = files.get(path)
        if payload is None or len(payload) != row["bytes"] \
                or _sha(payload) != row["sha256"]:
            _fail(f"{label}: payload mismatch {path}")
    if expected != set(files):
        _fail(f"{label}: path set differs")


def _verify_member_manifest(value: Mapping[str, object], archive: bytes,
                            *, label: str, path_key: str) -> int:
    members = _safe_archive(archive, label)
    rows = value.get("files")
    if not isinstance(rows, list) or value.get("file_count") != len(rows):
        _fail(f"{label}: file count invalid")
    expected = set()
    for row in rows:
        if not isinstance(row, dict) or path_key not in row \
                or "bytes" not in row or "sha256" not in row:
            _fail(f"{label}: malformed manifest row")
        path = str(row[path_key])
        expected.add(path)
        payload = members.get(path)
        if payload is None or len(payload) != row["bytes"] \
                or _sha(payload) != row["sha256"]:
            _fail(f"{label}: member mismatch {path}")
    if expected != set(members):
        _fail(f"{label}: archive/manifest path set differs")
    return len(rows)


def verify(root: Path) -> dict[str, object]:
    supplied_root = root.expanduser()
    if supplied_root.is_symlink():
        _fail("native-custody root must not be a symlink")
    root = supplied_root.resolve(strict=True)
    if not root.is_dir():
        _fail("native-custody root must be a real directory")
    # The manifest authenticates bytes, not filesystem indirection.  Reject
    # every indirection/special node before opening even the outer manifest so
    # a packet cannot be made non-self-contained by pointing one recorded path
    # at bytes outside the custody directory.
    for path in root.rglob("*"):
        if path.is_symlink():
            _fail(f"native-custody evidence contains a symlink: {path}")
        if not path.is_file() and not path.is_dir():
            _fail(f"native-custody evidence contains a special file: {path}")
    manifest, _ = _read_json(root / "manifest.json")
    if manifest.get("schema") != \
            "rtdl.goal5801.a4.native_custody_manifest.v3":
        _fail("outer manifest schema invalid")
    actual = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and path != root / "manifest.json"
    }
    _verify_rows(manifest.get("files"), actual, "outer manifest")
    if manifest.get("file_count") != len(actual) \
            or manifest.get("total_payload_bytes") != sum(map(len, actual.values())):
        _fail("outer manifest totals invalid")

    custody, custody_raw = _read_json(root / "custody.json")
    if custody.get("schema") != "rtdl.goal5801.a4.native_custody.v3" \
            or custody.get("registered_performance_timing_count") != 0 \
            or custody.get(
                "complete_registered_native_target_source_projection_custody") \
            is not True \
            or custody.get("entire_product_source_tree_custody_claimed") \
            is not False \
            or custody.get(
                "all_depfile_first_party_paths_present_in_projection") \
            is not True \
            or custody.get("source_checkout_clean_and_commit_exact") is not True \
            or custody.get("build_tree_matches_prebuild_source") is not True \
            or custody.get("complete_compiler_dependency_byte_custody") is not True \
            or custody.get("declared_tool_and_link_input_byte_custody") is not True \
            or custody.get("hermetic_toolchain_or_native_byte_reproducibility_claimed") \
            is not False:
        _fail("custody claim boundary invalid")

    source, source_raw = _read_json(root / "source/manifest.json")
    if set(source) != {
            "schema", "source_commit", "source_tree", "origin_commit",
            "origin_tree", "origin_full_inventory_sha256",
            "origin_commit_object_sha256", "scope", "file_count", "files"} \
            or source.get("schema") \
            != "rtdl.goal5801.a4.prebuild_source_projection_manifest.v3" \
            or source.get("scope") \
            != "REGISTERED_NATIVE_BUILD_TARGET__NOT_ENTIRE_PRODUCT_TREE":
        _fail("source projection manifest boundary invalid")
    source_count = _verify_member_manifest(
        source, (root / "source/prebuild_source.tar.gz").read_bytes(),
        label="source", path_key="path")
    inventory_raw = (root / "source/git_ls_tree_z.bin").read_bytes()
    source_inventory_rows = _parse_full_inventory(inventory_raw)
    if _inventory_tree_sha1(source_inventory_rows) != source.get("source_tree"):
        _fail("source inventory does not reconstruct declared source tree")
    inventory = []
    inventory_modes = {}
    for raw_row in inventory_raw.split(b"\0"):
        if not raw_row:
            continue
        header, separator, raw_path = raw_row.partition(b"\t")
        fields = header.split()
        if not separator or len(fields) != 3 or fields[1] != b"blob" \
                or fields[0] not in {b"100644", b"100755"}:
            _fail("Git commit tree inventory row invalid")
        path = raw_path.decode("utf-8")
        inventory.append(path)
        inventory_modes[path] = 0o755 if fields[0] == b"100755" else 0o644
    source_paths = [str(row["path"]) for row in source["files"]]
    source_modes = {str(row["path"]): row.get("mode") for row in source["files"]}
    if sorted(inventory) != source_paths or len(inventory) != len(set(inventory)) \
            or inventory_modes != source_modes:
        _fail("Git commit tree inventory/source manifest differs")
    source_members = _safe_archive(
        (root / "source/prebuild_source.tar.gz").read_bytes(), "source")
    for path, payload in source_members.items():
        row = source_inventory_rows.get(path.encode("utf-8"))
        if row is None or row[1] != b"blob" \
                or row[2] != _git_blob_sha1(payload):
            _fail(f"source archive is not the declared Git blob: {path}")
    origin_raw = (root / "source/origin_full_git_ls_tree_z.bin").read_bytes()
    origin_rows = _parse_full_inventory(origin_raw)
    if _inventory_tree_sha1(origin_rows) != source.get("origin_tree"):
        _fail("origin full inventory does not reconstruct declared origin tree")
    origin_commit_raw = (root / "source/origin_commit_object.bin").read_bytes()
    if _git_object_sha1("commit", origin_commit_raw) != source.get("origin_commit"):
        _fail("origin commit object does not hash to declared origin commit")
    first_line = origin_commit_raw.splitlines()[0] if origin_commit_raw else b""
    if first_line != f"tree {source.get('origin_tree')}".encode("ascii"):
        _fail("origin commit object does not bind declared origin tree")
    for path in source_paths:
        payload = source_members[path]
        expected_mode = b"100755" if source_modes[path] == 0o755 \
            else b"100644"
        row = origin_rows.get(path.encode("utf-8"))
        if row is None or row[0] != expected_mode or row[1] != b"blob" \
                or row[2] != _git_blob_sha1(payload):
            _fail(f"source projection is not an exact origin blob subset: {path}")
    dependencies, dependencies_raw = _read_json(
        root / "dependencies/manifest.json")
    dependency_count = _verify_member_manifest(
        dependencies,
        (root / "dependencies/dependency_bytes.tar.gz").read_bytes(),
        label="dependencies", path_key="archive_path")

    toolchain, toolchain_raw = _read_json(root / "toolchain/manifest.json")
    tool_members = _safe_archive(
        (root / "toolchain/tool_and_link_bytes.tar.gz").read_bytes(),
        "toolchain")
    expected_tool_members = set()
    for category in ("tools", "link_inputs", "receipts"):
        rows = toolchain.get(category)
        if not isinstance(rows, list) or not rows:
            _fail(f"toolchain {category} absent")
        for row in rows:
            if not isinstance(row, dict) or set(row) != {
                    "name", "original_path", "archive_path", "bytes", "sha256"}:
                _fail(f"toolchain {category} row invalid")
            archive_path = str(row["archive_path"])
            expected_tool_members.add(archive_path)
            payload = tool_members.get(archive_path)
            if payload is None or len(payload) != row["bytes"] \
                    or _sha(payload) != row["sha256"]:
                _fail(f"toolchain member mismatch: {archive_path}")
    if expected_tool_members != set(tool_members):
        _fail("toolchain archive/manifest path set differs")
    names = {
        category: {str(row["name"]) for row in toolchain[category]}
        for category in ("tools", "link_inputs", "receipts")
    }
    if names["tools"] < {"nvcc", "make", "host_cxx", "git"} \
            or names["link_inputs"] < {"cuda", "nvrtc", "geos_c"} \
            or names["receipts"] < {
                "nvcc_version", "make_version", "host_cxx_version", "git_version",
                "uname", "native_ldd"}:
        _fail("required toolchain identities/receipts absent")

    checks = {
        "source_archive_sha256": _sha(
            (root / "source/prebuild_source.tar.gz").read_bytes()),
        "source_manifest_sha256": _sha(source_raw),
        "git_commit_tree_inventory_sha256": _sha(inventory_raw),
        "origin_full_inventory_sha256": _sha(origin_raw),
        "origin_commit_object_sha256": _sha(origin_commit_raw),
        "dependency_archive_sha256": _sha(
            (root / "dependencies/dependency_bytes.tar.gz").read_bytes()),
        "dependency_manifest_sha256": _sha(dependencies_raw),
        "toolchain_archive_sha256": _sha(
            (root / "toolchain/tool_and_link_bytes.tar.gz").read_bytes()),
        "toolchain_manifest_sha256": _sha(toolchain_raw),
        "build_command_sha256": _sha(
            (root / "build/command.txt").read_bytes()),
        "build_stdout_sha256": _sha(
            (root / "build/stdout.txt").read_bytes()),
        "build_stderr_sha256": _sha(
            (root / "build/stderr.txt").read_bytes()),
        "build_environment_sha256": _sha(
            (root / "build/environment.json").read_bytes()),
        "native_sha256": _sha(
            (root / "native/librtdl_optix.so").read_bytes()),
    }
    for key, observed in checks.items():
        if custody.get(key) != observed:
            _fail(f"custody binding mismatch: {key}")
    if (root / "build/exit_code.txt").read_bytes() != b"0\n" \
            or custody.get("build_exit_code") != 0:
        _fail("native build exit receipt invalid")
    for key in ("source_commit", "source_tree", "origin_commit", "origin_tree",
                "origin_full_inventory_sha256",
                "origin_commit_object_sha256"):
        if source.get(key) != custody.get(key):
            _fail(f"source authority binding mismatch: {key}")
    return {
        "status": "PASS__INDEPENDENT_NATIVE_CUSTODY_VERIFICATION",
        "custody_sha256": _sha(custody_raw),
        "native_sha256": checks["native_sha256"],
        "source_commit": custody["source_commit"],
        "source_tree": custody["source_tree"],
        "origin_commit": custody["origin_commit"],
        "origin_tree": custody["origin_tree"],
        "source_file_count": source_count,
        "dependency_file_count": dependency_count,
        "toolchain_payload_count": len(tool_members),
        "hermetic_native_rebuild_claimed": False,
        "registered_performance_timing_count": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("custody_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.custody_directory), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
