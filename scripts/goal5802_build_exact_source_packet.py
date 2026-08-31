#!/usr/bin/env python3
"""Build a self-contained, one-commit Git source packet for Goal5802.

The builder reads Git objects, never work-tree bytes.  It materializes a bare
repository whose sole advertised history boundary is the requested commit,
sets ``core.autocrlf=false``, and archives only the files required to use that
repository.  The external manifest binds the packet bytes, root tree, and the
complete recursive path/mode/blob inventory.

This operation is create-only and records no application worker or timing.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
from typing import Iterable
import zipfile


SCHEMA = "rtdl.goal5802.exact_shallow_git_source_packet_manifest.v1"
PACKET_SCHEMA = "rtdl.goal5802.exact_shallow_git_source_packet.v1"
ALLOWED_MODES = {"100644", "100755"}
PRIVATE_COMPONENT_KEYS = {
    "d",
    "private_exponent",
    "private_exponent_base64",
    "private_key",
    "private_key_base64",
    "private_key_pem",
    "rsa_d",
    "rsa_private_exponent",
    "rsa_private_exponent_base64",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
ARCHIVE_SUFFIXES = (".tar.gz", ".tgz", ".tar", ".zip", ".whl", ".gz")
UNSUPPORTED_CONTAINER_SUFFIXES = (
    ".7z", ".rar", ".tar.bz2", ".tbz2", ".bz2", ".tar.xz", ".txz", ".xz", ".zst",
)
MAX_PRIVATE_SCAN_BYTES = 16 * 1024 * 1024 * 1024
MAX_PRIVATE_SCAN_PAYLOADS = 1_000_000
MAX_PRIVATE_SCAN_DEPTH = 8
BARE_CONFIG = (
    b"[core]\n"
    b"\trepositoryformatversion = 0\n"
    b"\tfilemode = true\n"
    b"\tbare = true\n"
    b"\tlogallrefupdates = false\n"
    b"\tautocrlf = false\n"
    b"\teol = lf\n"
    b"\tsafecrlf = true\n"
    b"[pack]\n"
    b"\twriteReverseIndex = false\n"
)


def _git_environment() -> dict[str, str]:
    environment = dict(os.environ)
    for key in tuple(environment):
        if key.startswith("GIT_"):
            environment.pop(key)
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    return environment


def _run_git(repository: Path, *arguments: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        [
            "git",
            "-c", "core.autocrlf=false",
            "-c", "core.safecrlf=true",
            "-C", str(repository),
            *arguments,
        ],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=_git_environment(),
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', errors='replace')}")
    return completed.stdout


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def _safe_source_path(raw_path: bytes) -> str:
    try:
        path = raw_path.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise RuntimeError("source path is not UTF-8") from error
    pure = PurePosixPath(path)
    parts = path.split("/")
    if (
        not path
        or path.startswith("/")
        or "\\" in path
        or "\r" in path
        or "\n" in path
        or pure.is_absolute()
        or any(part in {"", ".", "..", ".git"} for part in parts)
    ):
        raise RuntimeError(f"unsafe source path: {path!r}")
    return path


def _parse_leaf_inventory(payload: bytes) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for raw_row in payload.split(b"\0"):
        if not raw_row:
            continue
        try:
            left, raw_path = raw_row.split(b"\t", 1)
            raw_mode, raw_type, raw_object_id = left.split(b" ", 2)
            mode = raw_mode.decode("ascii")
            object_type = raw_type.decode("ascii")
            object_id = raw_object_id.decode("ascii")
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("malformed recursive ls-tree row") from error
        path = _safe_source_path(raw_path)
        if path in seen:
            raise RuntimeError(f"duplicate source path: {path}")
        seen.add(path)
        if mode not in ALLOWED_MODES or object_type != "blob":
            raise RuntimeError(
                f"unsupported non-regular source entry: {mode} {object_type} {path}")
        if not HEX40.fullmatch(object_id):
            raise RuntimeError(f"invalid Git object id for {path}")
        rows.append({
            "mode": mode,
            "object_id": object_id,
            "path": path,
            "type": object_type,
        })
    if not rows:
        raise RuntimeError("empty source inventory")
    if rows != sorted(rows, key=lambda row: str(row["path"]).encode("utf-8")):
        raise RuntimeError("recursive ls-tree inventory is not path ordered")
    return rows


def _parse_all_objects(payload: bytes) -> list[str]:
    objects: list[str] = []
    for raw_row in payload.split(b"\0"):
        if not raw_row:
            continue
        try:
            left, raw_path = raw_row.split(b"\t", 1)
            raw_mode, raw_type, raw_object_id = left.split(b" ", 2)
            object_id = raw_object_id.decode("ascii")
        except (ValueError, UnicodeDecodeError) as error:
            raise RuntimeError("malformed recursive object row") from error
        _safe_source_path(raw_path)
        if raw_type not in {b"tree", b"blob"} or not HEX40.fullmatch(object_id):
            raise RuntimeError("unsupported recursive Git object")
        objects.append(object_id)
    return objects


def _walk_private_components(value: object, parent_key: str | None = None) -> Iterable[bytes]:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                continue
            normalized = key.strip().lower().replace("-", "_")
            if normalized in PRIVATE_COMPONENT_KEYS:
                if isinstance(child, str):
                    yield child.encode("utf-8")
                elif isinstance(child, int) and not isinstance(child, bool):
                    yield str(child).encode("ascii")
            yield from _walk_private_components(child, normalized)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_private_components(child, parent_key)


def _private_material(path: Path) -> tuple[bytes, list[bytes]]:
    payload = path.resolve(strict=True).read_bytes()
    if not payload:
        raise RuntimeError(f"empty forbidden private-key file: {path}")
    tokens: set[bytes] = {payload}
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        document = None
    if document is not None:
        tokens.update(
            token for token in _walk_private_components(document) if len(token) >= 16)
    for match in re.finditer(
        rb"-----BEGIN [^-\r\n]*PRIVATE KEY-----.*?"
        rb"-----END [^-\r\n]*PRIVATE KEY-----",
        payload,
        flags=re.DOTALL,
    ):
        tokens.add(match.group(0))
    if len(tokens) == 1 and len(payload) < 32:
        raise RuntimeError(
            f"forbidden private-key file has no safely matchable material: {path}")
    return payload, sorted(tokens, key=lambda item: (_sha256(item), len(item)))


def _looks_like_container(label: str, prefix: bytes) -> bool:
    lowered = label.lower()
    return (
        lowered.endswith(ARCHIVE_SUFFIXES)
        or prefix.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08", b"\x1f\x8b"))
        or (len(prefix) >= 263 and prefix[257:263] in {b"ustar\x00", b"ustar "})
    )


def _reject_unsupported_container(label: str, prefix: bytes) -> None:
    lowered = label.lower()
    if (
        lowered.endswith(UNSUPPORTED_CONTAINER_SUFFIXES)
        or prefix.startswith((b"7z\xbc\xaf'\x1c", b"Rar!\x1a\x07", b"BZh", b"\xfd7zXZ\x00", b"(\xb5/\xfd"))
    ):
        raise RuntimeError(
            f"unsupported compressed container cannot be private-value scanned: {label}")


def _scan_private_stream(
    stream: object,
    label: str,
    private_file_hashes: set[str],
    private_tokens: list[bytes],
    statistics: dict[str, int],
    depth: int,
) -> None:
    if depth > MAX_PRIVATE_SCAN_DEPTH:
        raise RuntimeError(f"private-material archive nesting exceeds limit at {label}")
    statistics["payload_count"] += 1
    if statistics["payload_count"] > MAX_PRIVATE_SCAN_PAYLOADS:
        raise RuntimeError("private-material scan payload-count limit exceeded")
    digest = hashlib.sha256()
    nonempty = [token for token in private_tokens if token]
    overlap = max((len(token) for token in nonempty), default=1) - 1
    tail = b""
    spool: object | None = None
    first = True
    try:
        while True:
            chunk = stream.read(1024 * 1024)  # type: ignore[attr-defined]
            if not chunk:
                break
            if first:
                first = False
                _reject_unsupported_container(label, chunk)
                if _looks_like_container(label, chunk):
                    spool = tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024)
            if spool is not None:
                spool.write(chunk)  # type: ignore[attr-defined]
            statistics["bytes"] += len(chunk)
            if statistics["bytes"] > MAX_PRIVATE_SCAN_BYTES:
                raise RuntimeError("private-material expanded-byte scan limit exceeded")
            digest.update(chunk)
            window = tail + chunk
            if any(token in window for token in nonempty):
                raise RuntimeError(f"actual private-key value present in {label}")
            tail = window[-overlap:] if overlap else b""
        if digest.hexdigest() in private_file_hashes:
            raise RuntimeError(f"exact private-key file present in {label}")
        if spool is not None:
            spool.seek(0)  # type: ignore[attr-defined]
            _scan_private_container(
                spool, label, private_file_hashes, private_tokens, statistics, depth)
    finally:
        if spool is not None:
            spool.close()  # type: ignore[attr-defined]


def _scan_private_container(
    stream: object,
    label: str,
    private_file_hashes: set[str],
    private_tokens: list[bytes],
    statistics: dict[str, int],
    depth: int,
) -> None:
    statistics["container_count"] += 1
    stream.seek(0)  # type: ignore[attr-defined]
    if zipfile.is_zipfile(stream):
        stream.seek(0)  # type: ignore[attr-defined]
        with zipfile.ZipFile(stream) as archive:
            occurrences: dict[str, int] = {}
            for info in archive.infolist():
                occurrence = occurrences.get(info.filename, 0) + 1
                occurrences[info.filename] = occurrence
                if info.is_dir():
                    continue
                if info.flag_bits & 0x1:
                    raise RuntimeError(f"encrypted nested ZIP member in {label}")
                with archive.open(info, "r") as member_stream:
                    _scan_private_stream(
                        member_stream,
                        f"{label}!{info.filename}[occurrence={occurrence}]",
                        private_file_hashes,
                        private_tokens,
                        statistics,
                        depth + 1,
                    )
        return
    stream.seek(0)  # type: ignore[attr-defined]
    try:
        archive = tarfile.open(fileobj=stream, mode="r:*")
    except tarfile.ReadError:
        archive = None
    if archive is not None:
        with archive:
            occurrences = {}
            for member in archive:
                occurrence = occurrences.get(member.name, 0) + 1
                occurrences[member.name] = occurrence
                if not member.isfile():
                    continue
                member_stream = archive.extractfile(member)
                if member_stream is None:
                    raise RuntimeError(f"unreadable nested TAR member in {label}")
                with member_stream:
                    _scan_private_stream(
                        member_stream,
                        f"{label}!{member.name}[occurrence={occurrence}]",
                        private_file_hashes,
                        private_tokens,
                        statistics,
                        depth + 1,
                    )
        return
    stream.seek(0)  # type: ignore[attr-defined]
    prefix = stream.read(2)  # type: ignore[attr-defined]
    stream.seek(0)  # type: ignore[attr-defined]
    if prefix == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=stream, mode="rb") as uncompressed:
            _scan_private_stream(
                uncompressed,
                f"{label}!gzip-payload",
                private_file_hashes,
                private_tokens,
                statistics,
                depth + 1,
            )
        return
    raise RuntimeError(f"recognized archive payload is malformed or unsupported: {label}")


def _scan_unique_blobs(
    repository: Path,
    rows: list[dict[str, object]],
    private_files: list[bytes],
    private_tokens: list[bytes],
) -> dict[str, int]:
    object_to_paths: dict[str, list[str]] = {}
    for row in rows:
        object_to_paths.setdefault(str(row["object_id"]), []).append(str(row["path"]))
    statistics = {"bytes": 0, "container_count": 0, "payload_count": 0}
    private_file_hashes = {_sha256(payload) for payload in private_files}
    process = subprocess.Popen(
        ["git", "-c", "core.autocrlf=false", "-C", str(repository), "cat-file", "--batch"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=_git_environment(),
    )
    assert process.stdin is not None and process.stdout is not None
    try:
        for object_id in sorted(object_to_paths):
            process.stdin.write(object_id.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline()
            parts = header.rstrip(b"\n").split(b" ")
            if len(parts) != 3 or parts[0].decode("ascii") != object_id or parts[1] != b"blob":
                raise RuntimeError(f"unexpected cat-file response for {object_id}")
            size = int(parts[2])
            payload = process.stdout.read(size)
            trailer = process.stdout.read(1)
            if len(payload) != size or trailer != b"\n":
                raise RuntimeError(f"truncated cat-file response for {object_id}")
            if _git_blob_sha1(payload) != object_id:
                raise RuntimeError(f"Git blob identity mismatch for {object_id}")
            paths = object_to_paths[object_id]
            _scan_private_stream(
                io.BytesIO(payload),
                paths[0],
                private_file_hashes,
                private_tokens,
                statistics,
                0,
            )
        process.stdin.close()
        return_code = process.wait()
        if return_code != 0:
            error = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
            raise RuntimeError(f"git cat-file failed: {error}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()
    return statistics


def _make_bare_repository(
    source: Path,
    commit: str,
    tree: str,
    object_ids: list[str],
    output: Path,
) -> None:
    completed = subprocess.run(
        ["git", "init", "--bare", "--quiet", "--object-format=sha1", str(output)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=_git_environment(),
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    (output / "config").write_bytes(BARE_CONFIG)

    pack_path = output.parent / "objects.pack.tmp"
    unique_ids = sorted(set([commit, tree, *object_ids]))
    with pack_path.open("wb") as pack_stream:
        packer = subprocess.Popen(
            [
                "git", "-c", "core.autocrlf=false", "-C", str(source),
                "pack-objects", "--stdout", "--compression=9", "--threads=1",
                "--no-reuse-delta", "--no-reuse-object",
            ],
            stdin=subprocess.PIPE,
            stdout=pack_stream,
            stderr=subprocess.PIPE,
            env=_git_environment(),
        )
        assert packer.stdin is not None
        packer.stdin.write(("\n".join(unique_ids) + "\n").encode("ascii"))
        packer.stdin.close()
        return_code = packer.wait()
        error = packer.stderr.read().decode("utf-8", errors="replace") if packer.stderr else ""
        if packer.stderr is not None:
            packer.stderr.close()
        if return_code != 0:
            raise RuntimeError(f"git pack-objects failed: {error}")
    with pack_path.open("rb") as pack_stream:
        indexed = subprocess.run(
            ["git", "-C", str(output), "index-pack", "--stdin"],
            stdin=pack_stream,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=_git_environment(),
        )
    pack_path.unlink()
    if indexed.returncode != 0:
        raise RuntimeError(
            f"git index-pack failed: {indexed.stderr.decode('utf-8', errors='replace')}")
    _run_git(output, "update-ref", "refs/heads/packet", commit)
    _run_git(output, "symbolic-ref", "HEAD", "refs/heads/packet")
    (output / "shallow").write_bytes(commit.encode("ascii") + b"\n")

    if _run_git(output, "rev-parse", "HEAD").decode("ascii").strip() != commit:
        raise RuntimeError("packet bare repository HEAD mismatch")
    if _run_git(output, "rev-parse", "HEAD^{tree}").decode("ascii").strip() != tree:
        raise RuntimeError("packet bare repository tree mismatch")
    if _run_git(output, "rev-parse", "--is-shallow-repository").strip() != b"true":
        raise RuntimeError("packet bare repository is not shallow")
    if _run_git(output, "rev-list", "--count", "HEAD").strip() != b"1":
        raise RuntimeError("packet exposes more than one commit")
    _run_git(output, "fsck", "--full", "--strict", "--no-reflogs")
    if (output / "config").read_bytes() != BARE_CONFIG:
        raise RuntimeError("packet bare repository configuration drift")


def _packet_files(repository: Path) -> list[Path]:
    fixed = [
        repository / "HEAD",
        repository / "config",
        repository / "shallow",
        repository / "refs" / "heads" / "packet",
    ]
    packs = sorted((repository / "objects" / "pack").glob("pack-*.*"))
    if len([path for path in packs if path.suffix == ".pack"]) != 1:
        raise RuntimeError("packet repository must contain exactly one pack")
    if len([path for path in packs if path.suffix == ".idx"]) != 1:
        raise RuntimeError("packet repository must contain exactly one pack index")
    if any(path.suffix not in {".pack", ".idx"} for path in packs):
        raise RuntimeError("unexpected pack-side file")
    files = [*fixed, *packs]
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"missing or unsafe packet Git file: {path}")
    return files


def _tar_info(name: str, *, directory: bool, size: int = 0, mode: int = 0o644) -> tarfile.TarInfo:
    info = tarfile.TarInfo(name + ("/" if directory and not name.endswith("/") else ""))
    info.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
    info.size = 0 if directory else size
    info.mode = 0o755 if directory else mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    return info


def _build_packet(repository: Path, commit: str, destination: Path) -> list[dict[str, object]]:
    members: list[dict[str, object]] = []
    files = _packet_files(repository)
    directory_names = (
        "repository",
        "repository/objects",
        "repository/objects/pack",
        "repository/refs",
        "repository/refs/heads",
    )
    with destination.open("wb") as raw_stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw_stream, mtime=0, compresslevel=9) as gzip_stream:
            with tarfile.open(
                fileobj=gzip_stream,
                mode="w",
                format=tarfile.PAX_FORMAT,
                pax_headers={"comment": commit, "rtdl.goal5802.schema": PACKET_SCHEMA},
            ) as archive:
                for name in directory_names:
                    archive.addfile(_tar_info(name, directory=True))
                for path in files:
                    relative = path.relative_to(repository).as_posix()
                    name = f"repository/{relative}"
                    payload = path.read_bytes()
                    mode = 0o444 if path.suffix in {".pack", ".idx"} else 0o644
                    archive.addfile(
                        _tar_info(name, directory=False, size=len(payload), mode=mode),
                        io.BytesIO(payload),
                    )
                    members.append({
                        "bytes": len(payload),
                        "mode": f"{mode:04o}",
                        "path": name,
                        "sha256": _sha256(payload),
                    })
    return members


def _copy_create_only(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output, length=1024 * 1024)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            destination.unlink()
        except FileNotFoundError:
            pass
        raise


def _write_create_only(destination: Path, payload: bytes) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        try:
            destination.unlink()
        except FileNotFoundError:
            pass
        raise


def build(
    repository: Path,
    requested_commit: str,
    packet_path: Path,
    manifest_path: Path,
    forbidden_private_key_paths: list[Path],
) -> dict[str, object]:
    repository = repository.resolve(strict=True)
    packet_path = packet_path.resolve()
    manifest_path = manifest_path.resolve()
    if packet_path == manifest_path:
        raise RuntimeError("packet and manifest paths must differ")
    if packet_path.exists() or packet_path.is_symlink():
        raise FileExistsError(packet_path)
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError(manifest_path)
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if not forbidden_private_key_paths:
        raise RuntimeError("at least one exact forbidden private-key file is required")

    commit = _run_git(repository, "rev-parse", f"{requested_commit}^{{commit}}") \
        .decode("ascii").strip()
    tree = _run_git(repository, "rev-parse", f"{commit}^{{tree}}") \
        .decode("ascii").strip()
    if not HEX40.fullmatch(commit) or not HEX40.fullmatch(tree):
        raise RuntimeError("Goal5802 source packet currently requires Git SHA-1 objects")
    leaf_inventory_bytes = _run_git(
        repository, "ls-tree", "-r", "-z", "--full-tree", commit)
    rows = _parse_leaf_inventory(leaf_inventory_bytes)
    all_object_bytes = _run_git(
        repository, "ls-tree", "-r", "-t", "-z", "--full-tree", commit)
    recursive_objects = _parse_all_objects(all_object_bytes)

    private_files: list[bytes] = []
    private_tokens: list[bytes] = []
    private_file_hashes: list[str] = []
    resolved_key_paths = [path.resolve(strict=True) for path in forbidden_private_key_paths]
    if len(set(resolved_key_paths)) != len(resolved_key_paths):
        raise RuntimeError("duplicate forbidden private-key path")
    for key_path in resolved_key_paths:
        file_payload, tokens = _private_material(key_path)
        private_files.append(file_payload)
        private_tokens.extend(tokens)
        private_file_hashes.append(_sha256(file_payload))
    if len(set(private_file_hashes)) != len(private_file_hashes):
        raise RuntimeError("duplicate forbidden private-key identity")
    private_tokens = sorted(set(private_tokens), key=lambda item: (_sha256(item), len(item)))
    commit_payload = _run_git(repository, "cat-file", "commit", commit)
    if any(commit_payload == forbidden for forbidden in private_files):
        raise RuntimeError("exact private-key file used as Git commit object")
    if any(token and token in commit_payload for token in private_tokens):
        raise RuntimeError("actual private-key value present in Git commit object")
    for row in rows:
        encoded_path = str(row["path"]).encode("utf-8")
        if any(token and token in encoded_path for token in private_tokens):
            raise RuntimeError("actual private-key value present in Git path")
    private_scan = _scan_unique_blobs(
        repository, rows, private_files, private_tokens)

    inventory_digest = _sha256(_canonical(rows))
    private_token_hashes = sorted(_sha256(token) for token in private_tokens)
    with tempfile.TemporaryDirectory(
        prefix="goal5802-source-packet-", dir=str(packet_path.parent),
    ) as temporary:
        temporary_root = Path(temporary)
        bare = temporary_root / "repository.git"
        _make_bare_repository(
            repository, commit, tree, recursive_objects, bare)
        packet_temporary = temporary_root / "packet.tar.gz"
        members = _build_packet(bare, commit, packet_temporary)
        packet_bytes = packet_temporary.stat().st_size
        packet_sha256 = hashlib.sha256()
        with packet_temporary.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                packet_sha256.update(chunk)

        manifest: dict[str, object] = {
            "forbidden_private_key_file_count": len(private_file_hashes),
            "forbidden_private_key_file_sha256": sorted(private_file_hashes),
            "forbidden_private_value_sha256": private_token_hashes,
            "packet_bytes": packet_bytes,
            "packet_member_count": len(members),
            "packet_members": members,
            "packet_pax_comment": commit,
            "packet_schema": PACKET_SCHEMA,
            "packet_sha256": packet_sha256.hexdigest(),
            "private_material_scan_container_count": private_scan["container_count"],
            "private_material_scan_expanded_bytes": private_scan["bytes"],
            "private_material_scan_payload_count": private_scan["payload_count"],
            "registered_performance_timing_count": 0,
            "schema": SCHEMA,
            "source_commit": commit,
            "source_entry_count": len(rows),
            "source_full_ls_tree_z_bytes": len(leaf_inventory_bytes),
            "source_full_ls_tree_z_sha256": _sha256(leaf_inventory_bytes),
            "source_inventory": rows,
            "source_inventory_sha256": inventory_digest,
            "source_object_format": "sha1",
            "source_tree": tree,
            "status": "PASS__EXACT_SELF_CONTAINED_DEPTH_ONE_GIT_SOURCE_PACKET",
            "unregistered_timing_count": 0,
            "worker_count": 0,
        }
        manifest_payload = _canonical(manifest) + b"\n"
        _copy_create_only(packet_temporary, packet_path)
        try:
            _write_create_only(manifest_path, manifest_payload)
        except BaseException:
            packet_path.unlink()
            raise
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--forbidden-private-key-file",
        type=Path,
        action="append",
        required=True,
        dest="forbidden_private_key_files",
    )
    args = parser.parse_args()
    manifest = build(
        args.repository,
        args.commit,
        args.packet,
        args.manifest,
        args.forbidden_private_key_files,
    )
    print(json.dumps(manifest, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
