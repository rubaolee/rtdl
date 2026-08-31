#!/usr/bin/env python3
"""Create the one exact prebuilt PTX consumed by both comparative baselines."""

from __future__ import annotations

import argparse
import ast
import errno
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
import sys
from typing import Mapping, NoReturn, Sequence

from experiments.goal5802_premeasurement.runtime_manifest import (
    digest, sha256_file, tree_identity,
)
from scripts.goal5802_build_header_projection_untimed import (
    SDK_CLASS,
    validate_header_projection,
)


FINAL_PROJECTION_CLAIM = (
    "OBSERVED_NVCC_DEPENDENCY_SET_UNDER_MATCHED_ARCH_AND_EXACT_HOST_CXX__"
    "EMPIRICALLY_SUFFICIENT_FOR_FRESH_PROCESS_EXACT_NVRTC_REPLAY__"
    "NOT_A_GENERAL_NVRTC_SUPERSET")


def _plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def architecture_contract(compute_capability: str) -> tuple[str, str, str]:
    """Return canonical CC text plus the exact NVRTC PTX/CUBIN targets."""

    match = re.fullmatch(r"([0-9]+)\.([0-9]+)", compute_capability)
    if match is None:
        raise RuntimeError(
            "compute capability must be the observed <major>.<minor> value")
    major, minor = map(int, match.groups())
    if major <= 0 or minor < 0 or minor > 9:
        raise RuntimeError("unsupported CUDA compute capability")
    canonical = f"{major}.{minor}"
    digits = f"{major}{minor}"
    return canonical, f"compute_{digits}", f"sm_{digits}"


def _compile_exact_ptx(
        source_path: Path, optix_include: Path, cuda_include: Path,
        baseline: object, compute_capability: str,
        ) -> tuple[bytes, list[str], str]:
    """Compile PTX with one explicit target and verify its target directive."""

    from cuda.bindings import nvrtc

    _cc, compute_architecture, sm_architecture = architecture_contract(
        compute_capability)
    source = source_path.read_bytes()
    program = baseline.check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_path.name.encode(), 0, [], []))
    option_text = [
        "--std=c++17",
        "--device-as-default-execution-space",
        "--relocatable-device-code=true",
        f"--gpu-architecture={compute_architecture}",
        f"-I{optix_include}",
        f"-I{cuda_include}",
        f"-I{cuda_include / 'nv'}",
    ]
    options = [item.encode() for item in option_text]
    baseline.check_nvrtc(
        nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = baseline.check_nvrtc(nvrtc.nvrtcGetPTXSize(program))
    ptx = b" " * size
    baseline.check_nvrtc(nvrtc.nvrtcGetPTX(program, ptx))
    targets = re.findall(
        rb"(?m)^\.target[ \t]+(sm_[0-9]+)(?:[ \t,\r\n]|$)", ptx)
    observed = [item.decode("ascii") for item in targets]
    if observed != [sm_architecture]:
        raise RuntimeError(
            f"NVRTC PTX target differs: expected {sm_architecture}, "
            f"observed {observed}")
    return ptx, option_text, sm_architecture


def _compile_target_cubin(
        source_path: Path, baseline: object, compute_capability: str,
        ) -> tuple[bytes, str, list[str]]:
    from cuda.bindings import nvrtc
    _cc, _compute_architecture, architecture = architecture_contract(
        compute_capability)
    source = source_path.read_bytes()
    program = baseline.check_nvrtc(nvrtc.nvrtcCreateProgram(
        source, source_path.name.encode(), 0, [], []))
    option_text = [
        "--std=c++17",
        "--device-as-default-execution-space",
        f"--gpu-architecture={architecture}",
    ]
    options = [item.encode() for item in option_text]
    baseline.check_nvrtc(
        nvrtc.nvrtcCompileProgram(program, len(options), options), program)
    size = baseline.check_nvrtc(nvrtc.nvrtcGetCUBINSize(program))
    cubin = b" " * size
    baseline.check_nvrtc(nvrtc.nvrtcGetCUBIN(program, cubin))
    if not cubin or cubin[:4] != b"\x7fELF":
        raise RuntimeError("NVRTC did not produce an ELF CUDA cubin")
    return cubin, architecture, option_text


def _loaded_nvrtc_identity(nvrtc: object) -> dict[str, object]:
    """Bind the actual Linux libnvrtc DSO used by the target preparation."""

    version_result = nvrtc.nvrtcVersion()
    if not isinstance(version_result, tuple) or len(version_result) != 3 \
            or getattr(version_result[0], "value", version_result[0]) != 0:
        raise RuntimeError("NVRTC version query failed")
    maps = Path("/proc/self/maps")
    if not maps.is_file():
        raise RuntimeError("target preparation cannot bind loaded libnvrtc")
    candidates: set[Path] = set()
    for line in maps.read_text(encoding="utf-8").splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6 or not fields[5].startswith("/"):
            continue
        candidate = Path(fields[5]).resolve(strict=True)
        if candidate.name.startswith("libnvrtc.so"):
            candidates.add(candidate)
    if len(candidates) != 1:
        raise RuntimeError(
            f"loaded libnvrtc identity is ambiguous: {sorted(map(str, candidates))}")
    library = next(iter(candidates))
    return {
        "path": str(library),
        "bytes": library.stat().st_size,
        "sha256": sha256_file(library),
        "version": [int(version_result[1]), int(version_result[2])],
    }


def _fail(message: str) -> NoReturn:
    raise RuntimeError(message)


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _file_identity(path: Path) -> dict[str, object]:
    resolved = path.resolve(strict=True)
    if not resolved.is_file() or resolved.is_symlink():
        _fail(f"replay payload is not a canonical regular file: {path}")
    return {
        "path": str(resolved), "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def _python_invocation_path(executable: str) -> Path:
    """Preserve the active environment entrypoint while hashing its target.

    A POSIX virtual environment commonly exposes ``bin/python`` as a symlink
    to the base interpreter. Executing the resolved target discards the
    virtual environment's site-packages even though the binary bytes are the
    same. The command therefore retains the absolute invocation path; the
    receipt's ``_file_identity`` separately resolves and hashes the binary.
    """

    candidate = Path(executable)
    if not candidate.is_absolute():
        _fail("active Python invocation path is not absolute")
    candidate = candidate.absolute()
    if not candidate.is_file():
        _fail("active Python invocation path is not a file")
    return candidate


def _python_replay_identity(path: Path) -> dict[str, object]:
    invocation = _python_invocation_path(str(path))
    return {
        "invocation_path": str(invocation),
        **_file_identity(invocation),
    }


def _tree_rows(root: Path) -> list[dict[str, object]]:
    root = root.resolve(strict=True)
    rows = []
    # ``Path`` ordering compares path components, while the sealed manifests
    # order POSIX path strings.  Those orders differ when one sibling's name
    # is also another sibling directory's prefix (for example ``types.h`` and
    # ``types/FILE.h`` in real glibc headers).  Sort the exact manifest key so
    # a set-identical real SDK projection cannot fail only on enumeration
    # order.
    for path in sorted(
            root.rglob("*"),
            key=lambda item: item.relative_to(root).as_posix()):
        if path.is_symlink():
            _fail(f"fresh replay tree contains symlink: {path}")
        if path.is_file():
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
        elif not path.is_dir():
            _fail(f"fresh replay tree contains special file: {path}")
    return rows


def _materialize_subset(
        source_root: Path, destination_root: Path,
        relative_paths: Sequence[str]) -> dict[str, object]:
    if destination_root.exists() or destination_root.is_symlink():
        raise FileExistsError(destination_root)
    destination_root.mkdir(parents=True)
    for relative in sorted(set(relative_paths)):
        source = source_root / Path(relative)
        if not source.is_file() or source.is_symlink():
            _fail(f"projection subset source differs: {relative}")
        destination = destination_root / Path(relative)
        _write_create_only(destination, source.read_bytes())
    rows = _tree_rows(destination_root)
    if [str(row["path"]) for row in rows] != sorted(set(relative_paths)):
        _fail("projection subset exact file set differs")
    return {
        "file_count": len(rows),
        "payload_bytes": sum(int(row["bytes"]) for row in rows),
        "tree_sha256": digest(rows),
        "rows": rows,
    }


def _decode_trace_path(raw: str) -> str:
    try:
        value = ast.literal_eval(f'"{raw}"')
    except (SyntaxError, ValueError) as error:
        raise RuntimeError("strace path escaping is not parseable") from error
    if not isinstance(value, str) or "\x00" in value:
        _fail("strace path is not a valid string")
    return value


STABLE_PROC_OBSERVATIONS = {
    "/proc/self/maps", "/proc/thread-self/maps",
    "/proc/self/status", "/proc/thread-self/status",
}


def _normalize_kernel_absolute_path(target: str) -> str:
    if target.startswith("/"):
        return posixpath.normpath("/" + target.lstrip("/"))
    if os.name == "nt" and Path(target).is_absolute():
        # Cross-platform hostile unit fixtures; formal strace execution is
        # Linux and therefore always takes the POSIX branch above.
        return str(Path(target).resolve(strict=False))
    _fail("successful open kernel target is not absolute")


def _normalize_kernel_open_target(
        raw_target: str, *, decoded_path: str,
        trace_pid: int | None) -> str:
    """Validate the ``strace -y`` FD target captured at syscall exit."""

    target = _decode_trace_path(raw_target)
    normalized = _normalize_kernel_absolute_path(target)
    if decoded_path in STABLE_PROC_OBSERVATIONS:
        if decoded_path.startswith("/proc/thread-self/"):
            match = re.fullmatch(
                r"/proc/[0-9]+/task/([0-9]+)/(maps|status)", normalized)
            if match is None or trace_pid is None \
                    or int(match.group(1)) != trace_pid \
                    or match.group(2) != decoded_path.rsplit("/", 1)[-1]:
                _fail("thread-self kernel target does not bind trace PID")
        else:
            match = re.fullmatch(
                r"/proc/[0-9]+/(maps|status)", normalized)
            if match is None \
                    or match.group(1) != decoded_path.rsplit("/", 1)[-1]:
                _fail("self kernel target is not the declared observation")
        return normalized
    _reject_dynamic_procfs_spelling(
        normalized, context="successful open kernel target")
    return normalized


def _normalize_traced_path(path: Path, *, decoded: str) -> str:
    """Normalize one traced path without dereferencing procfs magic links.

    ``/proc/self`` and ``/proc/thread-self`` refer to the process performing
    the *open*.  Resolving either while recounting a preserved trace instead
    points at the verifier process, so identical raw bytes acquire a different
    digest on every replay.  Their read-only maps/status observation files use
    a stable lexical POSIX identity; other procfs magic paths fail closed.
    Ordinary paths retain realpath-style resolution so SDK-root containment
    cannot be forged through a symlink.
    """

    # Whitelist only the exact raw strace spelling.  Applying normpath before
    # this decision is unsound for procfs magic links: Linux follows e.g.
    # /proc/self/fd/<n> before interpreting subsequent ``..`` components.
    if decoded in STABLE_PROC_OBSERVATIONS:
        return decoded
    _reject_dynamic_procfs_spelling(decoded, context="strace")
    _reject_dynamic_procfs_symlink_hops(path)
    resolved = str(path.resolve(strict=False))
    _reject_dynamic_procfs_spelling(resolved, context="resolved strace path")
    return resolved


def _reject_dynamic_procfs_spelling(value: str, *, context: str) -> None:
    """Reject Linux process-relative namespaces under every slash spelling."""

    if not value.startswith("/"):
        return
    # Linux treats two or more leading slashes as the same root. Collapse them
    # even though POSIX normpath deliberately preserves exactly two.
    lexical = posixpath.normpath("/" + value.lstrip("/"))
    if re.match(r"^/proc/[0-9]+(?:/|$)", lexical):
        _fail(f"{context} uses numeric-PID procfs")
    if (lexical == "/proc/self" or lexical.startswith("/proc/self/")
            or lexical == "/proc/thread-self"
            or lexical.startswith("/proc/thread-self/")):
        _fail(f"{context} uses a procfs magic path")
    if (lexical == "/dev/fd" or lexical.startswith("/dev/fd/")
            or lexical in {
                "/dev/stdin", "/dev/stdout", "/dev/stderr",
            }):
        _fail(f"{context} uses a dynamic /dev fd alias")


def _reject_dynamic_procfs_symlink_hops(path: Path) -> None:
    """Inspect each POSIX symlink hop before ordinary realpath resolution.

    A stable-looking alias can target ``/proc/self/fd/N``. Resolving it after
    the traced child exits follows the verifier's descriptor N instead and can
    erase the procfs component completely. This bounded lexical walker rejects
    that namespace at the hop where it first appears.
    """

    if os.name != "posix":
        return
    text = str(path)
    if not text.startswith("/"):
        _fail("strace normalization received a non-absolute path")
    pending = [part for part in text.split("/") if part]
    current = "/"
    symlink_hops = 0
    while pending:
        component = pending.pop(0)
        if component == ".":
            continue
        if component == "..":
            current = posixpath.dirname(current.rstrip("/")) or "/"
            continue
        candidate = posixpath.join(current, component)
        _reject_dynamic_procfs_spelling(
            candidate, context="strace symlink hop")
        try:
            target = os.readlink(candidate)
        except OSError as error:
            if error.errno in {errno.EINVAL, errno.ENOENT, errno.ENOTDIR}:
                current = candidate
                continue
            raise RuntimeError(
                f"cannot inspect strace symlink hop: {candidate}") from error
        symlink_hops += 1
        if symlink_hops > 40:
            _fail("strace path exceeds the 40-symlink inspection bound")
        if target.startswith("/"):
            current = "/"
        pending = [part for part in target.split("/") if part] + pending


def parse_strace_file_accesses(
        trace_payloads: Sequence[bytes], *, cwd: Path,
        trace_pids: Sequence[int] | None = None,
        require_kernel_targets: bool = False) \
        -> list[dict[str, object]]:
    """Fail-closed parser for the exact file-open syscalls used by the KAT."""

    rows: list[dict[str, object]] = []
    if trace_pids is not None and len(trace_pids) != len(trace_payloads):
        _fail("strace payload/PID cardinality differs")
    for payload_index, payload in enumerate(trace_payloads):
        trace_pid = trace_pids[payload_index] if trace_pids is not None else None
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise RuntimeError("strace output is not UTF-8") from error
        if "<unfinished ...>" in text or "resumed>" in text:
            _fail("strace contains unfinished/resumed syscalls")
        for line in text.splitlines():
            if re.match(r"^(?:\[pid\s+[0-9]+\]\s+)?(?:chdir|fchdir)\(", line) \
                    and re.search(r"=\s*0\s*$", line):
                _fail("traced compiler changed working directory")
            call = re.match(
                r"^(?:\[pid\s+[0-9]+\]\s+)?(open|openat|openat2)\(",
                line)
            if call is None:
                continue
            syscall = call.group(1)
            tail = line[call.start(1):]
            if syscall == "open":
                match = re.match(r'open\("((?:\\.|[^"\\])*)"', tail)
                dirfd = None
            else:
                match = re.match(
                    rf'{syscall}\(([^,]+),\s*"((?:\\.|[^"\\])*)"',
                    tail)
                dirfd = match.group(1).strip() if match is not None else None
            result = re.search(
                r"=\s*(-?[0-9]+)(?:<(.*)>)?"
                r"(?:\s+[A-Z][A-Z0-9_]*(?:\s+\([^)]*\))?)?\s*$",
                tail)
            if match is None or result is None:
                _fail(f"strace {syscall} line is not fully parseable")
            after_path = tail[match.end():].lstrip()
            if not after_path.startswith(","):
                _fail("strace quoted path is truncated or malformed")
            raw_path = match.group(1) if syscall == "open" else match.group(2)
            decoded = _decode_trace_path(raw_path)
            path = Path(decoded)
            if not path.is_absolute():
                if syscall != "open":
                    at_cwd = re.fullmatch(
                        r"AT_FDCWD(?:<(.*)>)?", str(dirfd))
                    if at_cwd is None:
                        _fail("relative open uses an unresolved numeric dirfd")
                    if require_kernel_targets and at_cwd.group(1) is None:
                        _fail("strace -y AT_FDCWD annotation is absent")
                    if at_cwd.group(1) is not None:
                        annotated_cwd = _decode_trace_path(at_cwd.group(1))
                        if _normalize_kernel_absolute_path(annotated_cwd) \
                                != str(cwd.resolve(strict=True)):
                            _fail("strace AT_FDCWD annotation differs")
                path = cwd / path
            result_code = int(result.group(1))
            kernel_target = result.group(2)
            if result_code >= 0:
                if require_kernel_targets and kernel_target is None:
                    _fail("successful open lacks strace -y kernel target")
                normalized = (
                    _normalize_kernel_open_target(
                        kernel_target, decoded_path=decoded,
                        trace_pid=trace_pid)
                    if kernel_target is not None
                    else _normalize_traced_path(path, decoded=decoded))
            else:
                if kernel_target is not None:
                    _fail("failed open unexpectedly has a kernel target")
                normalized = _normalize_traced_path(path, decoded=decoded)
            rows.append({
                "syscall": syscall,
                "path": decoded,
                "normalized_path": normalized,
                "kernel_target_path": (
                    normalized if kernel_target is not None else None),
                "success": result_code >= 0,
                "result": result_code,
                "trace_pid": trace_pid,
            })
    if not rows:
        _fail("strace contains no parseable file-open evidence")
    return rows


def _trace_identity_and_accesses(
        prefix: Path, *, cwd: Path, original_roots: Sequence[Path],
        projected_roots: Sequence[Path], required_projected: Sequence[Path],
        require_no_original_attempt: bool,
        authority_pid: int | None) -> dict[str, object]:
    traces = sorted(path for path in prefix.parent.glob(prefix.name + ".*")
                    if path.is_file() and not path.is_symlink())
    if not traces:
        _fail(f"strace emitted no per-PID files: {prefix}")
    identities = [_file_identity(path) for path in traces]
    return _recount_trace_document(
        identities, cwd=cwd, original_roots=original_roots,
        projected_roots=projected_roots,
        required_projected=required_projected,
        require_no_original_attempt=require_no_original_attempt,
        authority_pid=authority_pid)


def _recount_trace_document(
        identities: Sequence[Mapping[str, object]], *, cwd: Path,
        original_roots: Sequence[Path], projected_roots: Sequence[Path],
        required_projected: Sequence[Path],
        require_no_original_attempt: bool,
        authority_pid: int | None) -> dict[str, object]:
    traces = []
    exact_identities = []
    for identity in identities:
        if not isinstance(identity, Mapping) or "path" not in identity:
            _fail("strace identity record is malformed")
        path = Path(str(identity["path"]))
        exact = _file_identity(path)
        if dict(identity) != exact:
            _fail("strace file identity differs")
        traces.append(path)
        exact_identities.append(exact)
    traced_pids = []
    for path in traces:
        suffix = path.name.rsplit(".", 1)[-1]
        if not suffix.isdigit():
            _fail("strace per-PID filename is not canonical")
        traced_pids.append(int(suffix))
    accesses = parse_strace_file_accesses(
        [path.read_bytes() for path in traces], cwd=cwd,
        trace_pids=traced_pids, require_kernel_targets=True)
    originals = [root.resolve(strict=True) for root in original_roots]
    projected = [root.resolve(strict=True) for root in projected_roots]
    original_rows = [
        row for row in accesses
        if any(Path(str(row["normalized_path"])).is_relative_to(root)
               for root in originals)]
    projected_rows = [
        row for row in accesses
        if any(Path(str(row["normalized_path"])).is_relative_to(root)
               for root in projected)]
    required = {str(path.resolve(strict=True)) for path in required_projected}
    observed_success = {
        str(row["normalized_path"]) for row in projected_rows
        if row["success"] is True
        and (authority_pid is None or row["trace_pid"] == authority_pid)}
    if authority_pid is not None and authority_pid not in traced_pids:
        _fail("receipt authority PID is absent from strace evidence")
    if require_no_original_attempt and original_rows:
        _fail("projected NVRTC process attempted access to original SDK root")
    if required - observed_success:
        _fail("projected NVRTC trace lacks required header opens")
    return {
        "trace_files": exact_identities,
        "trace_file_count": len(exact_identities),
        "traced_pids": traced_pids,
        "authority_pid": authority_pid,
        "file_open_attempt_count": len(accesses),
        "file_open_success_count": sum(
            row["success"] is True for row in accesses),
        "successful_kernel_target_count": sum(
            row["kernel_target_path"] is not None for row in accesses),
        "all_successful_opens_kernel_resolved": all(
            row["success"] is not True
            or row["kernel_target_path"] is not None for row in accesses),
        "original_sdk_attempt_count": len(original_rows),
        "original_sdk_success_count": sum(
            row["success"] is True for row in original_rows),
        "projected_sdk_attempt_count": len(projected_rows),
        "projected_sdk_success_count": sum(
            row["success"] is True for row in projected_rows),
        "required_projected_header_paths": sorted(required),
        "required_projected_headers_observed_successfully": (
            not bool(required - observed_success)),
        "normalized_access_sha256": digest(accesses),
    }


def _run_fresh_child(
        *, label: str, python: Path, strace: Path, child: Path,
        source: Path, optix_include: Path | None, cuda_include: Path | None,
        compute_capability: str, replay_root: Path,
        original_roots: Sequence[Path], projected_roots: Sequence[Path],
        required_projected: Sequence[Path], expect_success: bool,
        mode: str = "ptx") -> dict[str, object]:
    products = replay_root / "products"
    receipts = replay_root / "child_receipts"
    traces = replay_root / "traces"
    for directory in (products, receipts, traces):
        directory.mkdir(parents=True, exist_ok=True)
    output = products / f"{label}.{'ptx' if mode == 'ptx' else 'cubin'}"
    receipt = receipts / f"{label}.json"
    prefix = traces / label
    child_argv = [
        str(python), str(child), "--mode", mode, "--source", str(source),
        "--compute-capability", compute_capability,
        "--output", str(output), "--receipt", str(receipt),
    ]
    if optix_include is not None:
        child_argv.extend(["--optix-include", str(optix_include)])
    if cuda_include is not None:
        child_argv.extend(["--cuda-include", str(cuda_include)])
    trace_selector = (
        "open,openat,openat2,chdir,fchdir,execve,clone,clone3,fork,vfork")
    command = [
        str(strace), "-ff", "-y", "-qq", "-s", "65535", "-e",
        f"trace={trace_selector}", "-o", str(prefix), "--", *child_argv,
    ]
    completed = subprocess.run(
        command, cwd=Path.cwd(), capture_output=True, check=False)
    stdout = completed.stdout.decode("utf-8", errors="strict")
    stderr = completed.stderr.decode("utf-8", errors="strict")
    process = {
        "label": label,
        "cwd": str(Path.cwd().resolve(strict=True)),
        "command": command,
        "child_argv": child_argv,
        "exit_code": completed.returncode,
        "stdout_utf8": stdout,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stderr_utf8": stderr,
        "stderr_sha256": hashlib.sha256(stderr.encode()).hexdigest(),
    }
    if expect_success:
        if completed.returncode != 0 or not output.is_file() \
                or not receipt.is_file():
            _fail(f"fresh NVRTC child failed: {label}")
        value = json.loads(receipt.read_text(encoding="utf-8"))
        if not isinstance(value, Mapping):
            _fail("fresh NVRTC child receipt is not an object")
        unsigned = dict(value)
        seal = unsigned.pop("receipt_sha256", None)
        authority_pid = value.get("pid")
        if not isinstance(authority_pid, int):
            _fail("fresh NVRTC child PID is invalid")
        trace = _trace_identity_and_accesses(
            prefix, cwd=Path.cwd(), original_roots=original_roots,
            projected_roots=projected_roots,
            required_projected=required_projected,
            require_no_original_attempt=bool(projected_roots),
            authority_pid=authority_pid)
        if value.get("schema") \
                != "rtdl.goal5802.fresh_nvrtc_compile_child.v2" \
                or value.get("status") \
                != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE" \
                or value.get("argv") != child_argv[1:] \
                or value.get("pid") not in trace["traced_pids"] \
                or value.get("product") != _file_identity(output) \
                or seal != digest(unsigned) \
                or any(not _plain_int(value.get(key)) or value[key] != 0
                       for key in (
                    "clock_read_count", "gpu_kernel_launch_count",
                    "formal_worker_count",
                    "registered_performance_timing_count")):
            _fail("fresh NVRTC child receipt differs")
        return {
            "process": process,
            "trace": trace,
            "receipt": _file_identity(receipt),
            "child": dict(value),
            "product": _file_identity(output),
        }
    if completed.returncode == 0 or output.exists() or not receipt.is_file():
        _fail("negative missing-header NVRTC KAT did not fail closed")
    failure = json.loads(receipt.read_text(encoding="utf-8"))
    if not isinstance(failure, Mapping):
        _fail("negative NVRTC child failure receipt is invalid")
    failure_unsigned = dict(failure)
    failure_seal = failure_unsigned.pop("receipt_sha256", None)
    failure_pid = failure.get("pid")
    if not isinstance(failure_pid, int) \
            or failure.get("schema") \
            != "rtdl.goal5802.fresh_nvrtc_compile_failure.v2" \
            or failure.get("status") \
            != "FAIL__FRESH_PROCESS_NVRTC_COMPILE__NO_PRODUCT" \
            or failure.get("argv") != child_argv[1:] \
            or failure.get("product_created") is not False \
            or failure_seal != digest(failure_unsigned):
        _fail("negative NVRTC child failure receipt differs")
    removed_header = required_projected[0] if required_projected else None
    trace = _trace_identity_and_accesses(
        prefix, cwd=Path.cwd(), original_roots=original_roots,
        projected_roots=projected_roots, required_projected=[],
        require_no_original_attempt=bool(projected_roots),
        authority_pid=failure_pid)
    if removed_header is not None:
        removed_text = str(removed_header.resolve(strict=False))
        accesses = parse_strace_file_accesses(
            [Path(str(row["path"])).read_bytes()
             for row in trace["trace_files"]], cwd=Path.cwd(),
            trace_pids=trace["traced_pids"])
        missing_attempts = [
            row for row in accesses
            if row["trace_pid"] == failure_pid
            and row["normalized_path"] == removed_text
            and row["success"] is False]
        if not missing_attempts \
                or "optix.h" not in str(failure.get("error_message", "")) \
                or "optix.h" not in stderr:
            _fail("negative KAT is not causally bound to missing optix.h")
    return {
        "process": process,
        "trace": trace,
        "receipt": _file_identity(receipt),
        "failure": dict(failure),
        "receipt_created": True,
        "product_created": False,
        "missing_header_unsuccessful_open_count": len(missing_attempts)
            if removed_header is not None else 0,
    }


def validate_matched_ptx_prepare_receipt(
        value: Mapping[str, object], *,
        projection_receipt: Mapping[str, object],
        projection_root: Path) -> None:
    """Rehash every fresh child/product/raw trace and replay the verdict."""

    required_top = {
        "schema", "status", "projection_claim", "device_source_sha256",
        "compaction_source_sha256", "optix_include_tree",
        "cuda_include_tree", "header_projection_receipt_sha256",
        "header_projection_tree_sha256", "original_optix_include_path",
        "original_cuda_include_path", "original_ptx_compile_options",
        "original_ptx_sha256", "projected_ptx_byte_identical_to_original",
        "nvcc_only_ptx_byte_identical_to_original",
        "union_ptx_byte_identical_to_original", "nvrtc_library",
        "nvrtc_builtins", "fresh_process_replay", "compute_capability",
        "ptx_compile_options", "ptx_target", "ptx_bytes", "ptx_sha256",
        "compaction_cubin_architecture", "compaction_compile_options",
        "compaction_cubin_bytes", "compaction_cubin_sha256",
        "registered_performance_timing_count", "clock_read_count",
        "gpu_kernel_launch_count", "formal_worker_count", "receipt_sha256",
    }
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    if set(value) != required_top \
            or value.get("schema") \
            != "rtdl.goal5802.matched_ptx_untimed_prepare.v3" \
            or value.get("status") \
            != "PASS__FRESH_PROCESS_TRACED_UNTIMED_PREPARE" \
            or value.get("projection_claim") != FINAL_PROJECTION_CLAIM \
            or any(not _plain_int(value.get(key)) or value[key] != 0
                   for key in (
                "registered_performance_timing_count", "clock_read_count",
                "gpu_kernel_launch_count", "formal_worker_count")) \
            or seal != digest(unsigned):
        _fail("fresh matched PTX prepare envelope differs")
    replay = value.get("fresh_process_replay")
    if not isinstance(replay, Mapping) or set(replay) != {
            "python", "strace", "child", "canonical_projection_root",
            "nvcc_only_projection_root", "negative_projection_root",
            "nvcc_only_sdk_paths", "direct_sdk_paths", "union_sdk_paths",
            "nvcc_only_tree", "negative_tree_rows", "negative_removed_path",
            "runs", "successful_child_pids", "all_successful_pids_distinct",
            "negative_pid_disjoint",
            "original_sdk_attempts_in_projected_runs",
            "negative_compile_failed_without_product"}:
        _fail("fresh replay schema differs")
    python_record = replay["python"]
    if not isinstance(python_record, Mapping) \
            or dict(python_record) != _python_replay_identity(Path(str(
                python_record.get("invocation_path")))):
        _fail("fresh replay Python invocation/binary identity differs")
    for role in ("strace", "child"):
        record = replay[role]
        if not isinstance(record, Mapping) \
                or dict(record) != _file_identity(Path(str(record["path"]))):
            _fail(f"fresh replay tool identity differs: {role}")
    root = projection_root.resolve(strict=True)
    if replay.get("canonical_projection_root") != str(root):
        _fail("fresh replay canonical projection root differs")
    runs = projection_receipt.get("runs")
    if not isinstance(runs, list) or len(runs) != 3:
        _fail("fresh replay header projection runs differ")
    nvcc_paths = sorted({
        str(row["projection_path"]) for run in runs[:2]
        for row in run["load_bearing_sdk_dependencies"]})
    direct_paths = sorted({
        str(row["projection_path"])
        for row in runs[2]["load_bearing_sdk_dependencies"]})
    union_paths = sorted(set(nvcc_paths) | set(direct_paths))
    if replay.get("nvcc_only_sdk_paths") != nvcc_paths \
            or replay.get("direct_sdk_paths") != direct_paths \
            or replay.get("union_sdk_paths") != union_paths:
        _fail("fresh replay SDK file-set partition differs")
    nvcc_root = Path(str(replay["nvcc_only_projection_root"])).resolve(
        strict=True)
    negative_root = Path(str(replay["negative_projection_root"])).resolve(
        strict=True)
    replay_root = nvcc_root.parent
    if negative_root.parent != replay_root \
            or nvcc_root.name != "nvcc_only_projection" \
            or negative_root.name != "negative_projection":
        _fail("fresh replay root layout differs")
    observed_nvcc_rows = _tree_rows(nvcc_root)
    nvcc_tree = replay.get("nvcc_only_tree")
    if not isinstance(nvcc_tree, Mapping) or set(nvcc_tree) != {
            "file_count", "payload_bytes", "tree_sha256", "rows"} \
            or nvcc_tree.get("rows") != observed_nvcc_rows \
            or nvcc_tree.get("file_count") != len(observed_nvcc_rows) \
            or nvcc_tree.get("payload_bytes") \
            != sum(int(row["bytes"]) for row in observed_nvcc_rows) \
            or nvcc_tree.get("tree_sha256") != digest(observed_nvcc_rows):
        _fail("fresh replay NVCC-only tree differs")
    negative_rows = _tree_rows(negative_root)
    removed = replay.get("negative_removed_path")
    if replay.get("negative_tree_rows") != negative_rows \
            or not isinstance(removed, str) \
            or set(str(row["path"]) for row in observed_nvcc_rows) \
            - set(str(row["path"]) for row in negative_rows) != {removed} \
            or len(negative_rows) + 1 != len(observed_nvcc_rows) \
            or Path(removed).name != "optix.h":
        _fail("fresh replay exact-one-header negative tree differs")
    mappings = projection_receipt.get("root_mappings")
    if not isinstance(mappings, list):
        _fail("fresh replay root mappings absent")
    mapping = {str(row["role"]): row for row in mappings}
    authority = projection_receipt.get("command_authority")
    authority_sources = authority.get("sources") \
        if isinstance(authority, Mapping) else None
    if not isinstance(authority_sources, Mapping):
        _fail("fresh replay source authority is absent")
    matched_source = authority_sources.get("matched_device_source")
    compaction_source = authority_sources.get("relation_compaction_source")
    if not isinstance(matched_source, Mapping) \
            or not isinstance(compaction_source, Mapping) \
            or value.get("device_source_sha256") \
            != matched_source.get("sha256") \
            or value.get("compaction_source_sha256") \
            != compaction_source.get("sha256"):
        _fail("fresh replay outer/source authority differs")
    original_roots = [Path(str(value["original_optix_include_path"])),
                      Path(str(value["original_cuda_include_path"]))]
    canonical_projected = [
        Path(str(mapping["optix_include"]["projected_root"])),
        Path(str(mapping["cuda_include"]["projected_root"]))]
    relative_roots = [path.relative_to(root) for path in canonical_projected]
    nvcc_projected = [nvcc_root / rel for rel in relative_roots]
    negative_projected = [negative_root / rel for rel in relative_roots]

    replay_runs = replay.get("runs")
    if not isinstance(replay_runs, Mapping) or set(replay_runs) != {
            "original", "nvcc_only", "union", "compaction",
            "negative_missing_optix_h"}:
        _fail("fresh replay run roles differ")
    loaded = []
    ptx_products = []
    successful_pids = []

    def validate_process_layout(
            label: str, process: Mapping[str, object],
            child_value: Mapping[str, object], *, extension: str,
            receipt_record: Mapping[str, object]) -> None:
        output_path = replay_root / "products" / f"{label}.{extension}"
        receipt_path = replay_root / "child_receipts" / f"{label}.json"
        trace_prefix = replay_root / "traces" / label
        include_roots = child_value.get("include_roots")
        source = child_value.get("source")
        if not isinstance(include_roots, Mapping) \
                or not isinstance(source, Mapping):
            _fail(f"fresh replay child inputs differ: {label}")
        expected_child_argv = [
            str(replay["python"]["invocation_path"]),
            str(replay["child"]["path"]),
            "--mode", str(child_value["mode"]), "--source",
            str(source["path"]), "--compute-capability",
            str(child_value["compute_capability"]), "--output",
            str(output_path), "--receipt", str(receipt_path),
        ]
        if include_roots.get("optix") is not None:
            expected_child_argv.extend([
                "--optix-include", str(include_roots["optix"])])
        if include_roots.get("cuda") is not None:
            expected_child_argv.extend([
                "--cuda-include", str(include_roots["cuda"])])
        selector = (
            "open,openat,openat2,chdir,fchdir,execve,clone,clone3,fork,vfork")
        expected_command = [
            str(replay["strace"]["path"]), "-ff", "-y", "-qq", "-s", "65535",
            "-e", f"trace={selector}", "-o", str(trace_prefix), "--",
            *expected_child_argv,
        ]
        trace = replay_runs[label]["trace"]
        if process.get("cwd") != child_value.get("cwd") \
                or process.get("child_argv") != expected_child_argv \
                or process.get("command") != expected_command \
                or receipt_record.get("path") != str(receipt_path) \
                or replay_runs[label]["product"].get("path") \
                != str(output_path) \
                or any(Path(str(row["path"])).parent \
                       != trace_prefix.parent
                       or not Path(str(row["path"])).name.startswith(
                           trace_prefix.name + ".")
                       for row in trace["trace_files"]):
            _fail(f"fresh replay process/trace path binding differs: {label}")

    success_specs = {
        "original": (
            [], [], matched_source, original_roots, "ptx"),
        "nvcc_only": (
            nvcc_projected,
            [nvcc_projected[0] / name
             for name in ("optix.h", "optix_device.h")],
            matched_source, nvcc_projected, "ptx"),
        "union": (
            canonical_projected,
            [canonical_projected[0] / name
             for name in ("optix.h", "optix_device.h")],
            matched_source, canonical_projected, "ptx"),
        "compaction": ([], [], compaction_source, [], "cubin"),
    }
    for label, (projected_roots, required_headers, expected_source,
                expected_includes, expected_mode) in success_specs.items():
        row = replay_runs[label]
        if not isinstance(row, Mapping) or set(row) != {
                "process", "trace", "receipt", "child", "product"}:
            _fail(f"fresh replay success row differs: {label}")
        process = row["process"]
        child_value = row["child"]
        if not isinstance(process, Mapping) or set(process) != {
                "label", "cwd", "command", "child_argv", "exit_code",
                "stdout_utf8", "stdout_sha256", "stderr_utf8",
                "stderr_sha256"} \
                or process.get("label") != label \
                or process.get("exit_code") != 0 \
                or process.get("stdout_sha256") != hashlib.sha256(
                    str(process.get("stdout_utf8")).encode()).hexdigest() \
                or process.get("stderr_sha256") != hashlib.sha256(
                    str(process.get("stderr_utf8")).encode()).hexdigest() \
                or not isinstance(child_value, Mapping):
            _fail(f"fresh replay process differs: {label}")
        child_unsigned = dict(child_value)
        child_seal = child_unsigned.pop("receipt_sha256", None)
        receipt_record = row["receipt"]
        product_record = row["product"]
        child_source = child_value.get("source")
        child_includes = child_value.get("include_roots")
        expected_source_projection = {
            "path": expected_source["resolved_path"],
            "bytes": expected_source["bytes"],
            "sha256": expected_source["sha256"],
        }
        _canonical_cc, expected_compute, expected_sm = architecture_contract(
            str(value["compute_capability"]))
        expected_options = ([
            "--std=c++17", "--device-as-default-execution-space",
            "--relocatable-device-code=true",
            f"--gpu-architecture={expected_compute}",
            f"-I{expected_includes[0]}", f"-I{expected_includes[1]}",
            f"-I{expected_includes[1] / 'nv'}",
        ] if expected_mode == "ptx" else [
            "--std=c++17", "--device-as-default-execution-space",
            f"--gpu-architecture={expected_sm}",
        ])
        if set(child_value) != {
                "schema", "status", "pid", "parent_pid", "argv", "cwd",
                "mode", "source", "include_roots", "compute_capability",
                "compile_options", "target", "product", "loaded_nvrtc",
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count",
                "receipt_sha256"} \
                or child_value.get("schema") \
                != "rtdl.goal5802.fresh_nvrtc_compile_child.v2" \
                or child_value.get("status") \
                != "PASS__FRESH_PROCESS_UNTIMED_NVRTC_COMPILE" \
                or child_value.get("mode") != expected_mode \
                or child_value.get("compute_capability") \
                != value.get("compute_capability") \
                or child_value.get("target") != expected_sm \
                or child_value.get("compile_options") != expected_options \
                or child_source != expected_source_projection \
                or not isinstance(child_source, Mapping) \
                or child_source != _file_identity(Path(str(
                    child_source["path"]))) \
                or child_includes != {
                    "optix": str(expected_includes[0])
                        if expected_includes else None,
                    "cuda": str(expected_includes[1])
                        if expected_includes else None,
                } \
                or any(not _plain_int(child_value.get(key))
                       or child_value[key] != 0 for key in (
                    "clock_read_count", "gpu_kernel_launch_count",
                    "formal_worker_count",
                    "registered_performance_timing_count")):
            _fail(f"fresh replay role source/root/options differ: {label}")
        if not isinstance(receipt_record, Mapping) \
                or dict(receipt_record) != _file_identity(Path(str(
                    receipt_record["path"]))) \
                or json.loads(Path(str(receipt_record["path"])).read_text(
                    encoding="utf-8")) != child_value \
                or child_seal != digest(child_unsigned) \
                or not isinstance(process.get("child_argv"), list) \
                or child_value.get("argv") != process["child_argv"][1:] \
                or child_value.get("pid") not in row["trace"]["traced_pids"] \
                or not isinstance(product_record, Mapping) \
                or dict(product_record) != _file_identity(Path(str(
                    product_record["path"]))) \
                or child_value.get("product") != product_record:
            _fail(f"fresh replay child/product binding differs: {label}")
        validate_process_layout(
            label, process, child_value,
            extension="cubin" if label == "compaction" else "ptx",
            receipt_record=receipt_record)
        expected_trace = _recount_trace_document(
            row["trace"]["trace_files"], cwd=Path(str(child_value["cwd"])),
            original_roots=original_roots,
            projected_roots=projected_roots,
            required_projected=required_headers,
            require_no_original_attempt=bool(projected_roots),
            authority_pid=int(child_value["pid"]))
        if row.get("trace") != expected_trace:
            _fail(f"fresh replay raw trace recount differs: {label}")
        loaded.append(child_value.get("loaded_nvrtc"))
        successful_pids.append(int(child_value["pid"]))
        if label != "compaction":
            ptx_products.append(Path(str(product_record["path"])).read_bytes())
    if any(item != loaded[0] for item in loaded[1:]) \
            or any(item != ptx_products[0] for item in ptx_products[1:]) \
            or len(set(successful_pids)) != len(successful_pids) \
            or replay.get("successful_child_pids") != successful_pids \
            or replay.get("all_successful_pids_distinct") is not True:
        _fail("fresh replay cross-process identity/equality differs")
    loaded_identity = loaded[0]
    if not isinstance(loaded_identity, Mapping) or set(loaded_identity) != {
            "library", "builtins", "version"} \
            or not isinstance(loaded_identity.get("version"), list) \
            or len(loaded_identity["version"]) != 2:
        _fail("fresh replay loaded NVRTC envelope differs")
    for role in ("library", "builtins"):
        record = loaded_identity.get(role)
        if not isinstance(record, Mapping) or set(record) != {
                "path", "bytes", "sha256", "canonical_regular_file",
                "symlink"} \
                or record.get("canonical_regular_file") is not True \
                or record.get("symlink") is not False \
                or {key: record[key] for key in ("path", "bytes", "sha256")} \
                != _file_identity(Path(str(record["path"]))):
            _fail(f"fresh replay loaded NVRTC identity differs: {role}")
    if value.get("nvrtc_library") != {
            **loaded_identity["library"],
            "version": loaded_identity["version"]} \
            or value.get("nvrtc_builtins") != loaded_identity["builtins"]:
        _fail("fresh replay outer NVRTC identities differ")
    negative = replay_runs["negative_missing_optix_h"]
    if not isinstance(negative, Mapping) or set(negative) != {
            "process", "trace", "receipt", "failure", "receipt_created",
            "product_created", "missing_header_unsuccessful_open_count"} \
            or negative.get("receipt_created") is not True \
            or negative.get("product_created") is not False \
            or negative["process"].get("exit_code") == 0:
        _fail("fresh replay negative result differs")
    failure = negative.get("failure")
    failure_receipt = negative.get("receipt")
    if not isinstance(failure, Mapping) \
            or not isinstance(failure_receipt, Mapping) \
            or dict(failure_receipt) != _file_identity(Path(str(
                failure_receipt["path"]))) \
            or json.loads(Path(str(failure_receipt["path"])).read_text(
                encoding="utf-8")) != failure:
        _fail("fresh replay negative failure receipt differs")
    failure_unsigned = dict(failure)
    failure_seal = failure_unsigned.pop("receipt_sha256", None)
    if set(failure) != {
            "schema", "status", "pid", "parent_pid", "argv", "cwd",
            "mode", "source", "include_roots", "compute_capability",
            "error_type", "error_message", "loaded_nvrtc",
            "product_created", "clock_read_count",
            "gpu_kernel_launch_count", "formal_worker_count",
            "registered_performance_timing_count", "receipt_sha256"} \
            or failure.get("schema") \
            != "rtdl.goal5802.fresh_nvrtc_compile_failure.v2" \
            or failure.get("status") \
            != "FAIL__FRESH_PROCESS_NVRTC_COMPILE__NO_PRODUCT" \
            or failure.get("product_created") is not False \
            or any(not _plain_int(failure.get(key)) or failure[key] != 0
                   for key in (
                "clock_read_count", "gpu_kernel_launch_count",
                "formal_worker_count", "registered_performance_timing_count")) \
            or failure_seal != digest(failure_unsigned):
        _fail("fresh replay negative child seal differs")
    negative_label = "negative_missing_optix_h"
    negative_output = replay_root / "products" / f"{negative_label}.ptx"
    negative_receipt_path = (
        replay_root / "child_receipts" / f"{negative_label}.json")
    negative_trace_prefix = replay_root / "traces" / negative_label
    failure_source = failure.get("source")
    failure_includes = failure.get("include_roots")
    expected_failure_source = {
        "path": matched_source["resolved_path"],
        "bytes": matched_source["bytes"],
        "sha256": matched_source["sha256"],
    }
    if not isinstance(failure_source, Mapping) \
            or not isinstance(failure_includes, Mapping) \
            or failure_source != expected_failure_source \
            or failure_source != _file_identity(Path(str(
                failure_source["path"]))) \
            or failure_includes != {
                "optix": str(negative_projected[0]),
                "cuda": str(negative_projected[1]),
            } \
            or failure.get("mode") != "ptx" \
            or failure.get("compute_capability") \
            != value.get("compute_capability") \
            or failure.get("loaded_nvrtc") != loaded_identity \
            or not isinstance(failure.get("pid"), int) \
            or not isinstance(failure.get("parent_pid"), int) \
            or not isinstance(failure.get("error_type"), str) \
            or not failure.get("error_type") \
            or not isinstance(failure.get("error_message"), str) \
            or not failure.get("error_message"):
        _fail("fresh replay negative child inputs differ")
    negative_argv = [
        str(replay["python"]["invocation_path"]),
        str(replay["child"]["path"]),
        "--mode", str(failure["mode"]), "--source",
        str(failure_source["path"]), "--compute-capability",
        str(failure["compute_capability"]), "--output", str(negative_output),
        "--receipt", str(negative_receipt_path), "--optix-include",
        str(failure_includes["optix"]), "--cuda-include",
        str(failure_includes["cuda"]),
    ]
    selector = (
        "open,openat,openat2,chdir,fchdir,execve,clone,clone3,fork,vfork")
    negative_command = [
        str(replay["strace"]["path"]), "-ff", "-y", "-qq", "-s", "65535",
        "-e", f"trace={selector}", "-o", str(negative_trace_prefix), "--",
        *negative_argv,
    ]
    if negative["process"].get("cwd") != failure.get("cwd") \
            or negative["process"].get("child_argv") != negative_argv \
            or negative["process"].get("command") != negative_command \
            or failure.get("argv") != negative_argv[1:] \
            or failure_receipt.get("path") != str(negative_receipt_path) \
            or any(Path(str(row["path"])).parent \
                   != negative_trace_prefix.parent
                   or not Path(str(row["path"])).name.startswith(
                       negative_trace_prefix.name + ".")
                   for row in negative["trace"]["trace_files"]):
        _fail("fresh replay negative process/trace path binding differs")
    negative_trace = _recount_trace_document(
        negative["trace"]["trace_files"],
        cwd=Path(str(negative["process"]["cwd"])),
        original_roots=original_roots, projected_roots=negative_projected,
        required_projected=[], require_no_original_attempt=True,
        authority_pid=int(negative["failure"]["pid"]))
    if negative.get("trace") != negative_trace \
            or set(successful_pids) & set(negative_trace["traced_pids"]) \
            or replay.get("negative_pid_disjoint") is not True \
            or replay.get("original_sdk_attempts_in_projected_runs") != 0 \
            or replay.get("negative_compile_failed_without_product") is not True:
        _fail("fresh replay negative trace/process binding differs")
    negative_accesses = parse_strace_file_accesses(
        [Path(str(row["path"])).read_bytes()
         for row in negative_trace["trace_files"]],
        cwd=Path(str(negative["process"]["cwd"])),
        trace_pids=negative_trace["traced_pids"])
    removed_absolute = str((negative_root / Path(str(removed))).resolve(
        strict=False))
    missing_count = sum(
        row["trace_pid"] == failure["pid"]
        and row["normalized_path"] == removed_absolute
        and row["success"] is False
        for row in negative_accesses)
    if missing_count <= 0 \
            or negative.get("missing_header_unsuccessful_open_count") \
            != missing_count \
            or "optix.h" not in str(failure.get("error_message", "")) \
            or "optix.h" not in str(
                negative["process"].get("stderr_utf8", "")):
        _fail("fresh replay negative cause is not exact missing optix.h")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--compaction-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--original-optix-include", type=Path, required=True)
    parser.add_argument("--original-cuda-include", type=Path, required=True)
    parser.add_argument("--header-projection-root", type=Path, required=True)
    parser.add_argument("--header-projection-receipt", type=Path, required=True)
    parser.add_argument("--strace", type=Path, required=True)
    parser.add_argument("--replay-root", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compaction-output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    for path in (
            args.output, args.compaction_output, args.receipt,
            args.replay_root):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    device_source = args.device_source.resolve(strict=True)
    compaction_source = args.compaction_source.resolve(strict=True)
    optix_include = args.optix_include.resolve(strict=True)
    cuda_include = args.cuda_include.resolve(strict=True)
    original_optix_include = args.original_optix_include.resolve(strict=True)
    original_cuda_include = args.original_cuda_include.resolve(strict=True)
    projection_root = args.header_projection_root.resolve(strict=True)
    projection_receipt_path = args.header_projection_receipt.resolve(
        strict=True)
    strace = args.strace.resolve(strict=True)
    python = _python_invocation_path(sys.executable)
    child = Path(__file__).with_name(
        "goal5802_nvrtc_compile_child.py").resolve(strict=True)
    if not strace.is_file() or not os.access(strace, os.X_OK) \
            or not python.is_file() or not child.is_file():
        _fail("fresh replay tool identity is invalid")
    projection_resolved_future = projection_root.resolve(strict=True)
    replay_resolved_future = args.replay_root.resolve(strict=False)
    for path in (args.replay_root, args.output, args.compaction_output,
                 args.receipt):
        candidate = path.resolve(strict=False)
        if candidate == projection_resolved_future \
                or candidate.is_relative_to(projection_resolved_future):
            _fail("fresh replay outputs must be outside canonical projection")
    if projection_resolved_future.is_relative_to(replay_resolved_future):
        _fail("canonical projection must not be nested in replay root")
    projection_receipt = json.loads(
        projection_receipt_path.read_text(encoding="utf-8"))
    if not isinstance(projection_receipt, dict):
        raise RuntimeError("header projection receipt is not an object")
    validate_header_projection(projection_receipt, projection_root)
    if not optix_include.is_relative_to(projection_root) \
            or not cuda_include.is_relative_to(projection_root):
        raise RuntimeError("NVRTC replay include root escapes projection")
    mapping_by_role = {
        str(row["role"]): row for row in projection_receipt["root_mappings"]}
    if mapping_by_role["optix_include"]["original_root"] \
            != str(original_optix_include) \
            or mapping_by_role["cuda_include"]["original_root"] \
            != str(original_cuda_include) \
            or mapping_by_role["optix_include"]["projected_root"] \
            != str(optix_include) \
            or mapping_by_role["cuda_include"]["projected_root"] \
            != str(cuda_include):
        _fail("header projection original/projected root mapping differs")
    canonical_cc, compute_architecture, expected_sm = architecture_contract(
        args.compute_capability)
    if projection_receipt["command_authority"]["compute_capability"] \
            != expected_sm:
        _fail("projection dependency architecture differs from observed target")
    runs = projection_receipt["runs"]
    nvcc_paths = sorted({
        str(row["projection_path"])
        for run in runs[:2]
        for row in run["load_bearing_sdk_dependencies"]
        if row["classification"] == SDK_CLASS})
    direct_paths = sorted({
        str(row["projection_path"])
        for row in runs[2]["load_bearing_sdk_dependencies"]
        if row["classification"] == SDK_CLASS})
    union_paths = sorted(set(nvcc_paths) | set(direct_paths))
    canonical_rows = _tree_rows(projection_root)
    if [str(row["path"]) for row in canonical_rows] != union_paths:
        _fail("canonical projection is not exact NVCC+CXX SDK union")
    args.replay_root.mkdir(parents=True)
    replay_root = args.replay_root.resolve(strict=True)
    nvcc_root = replay_root / "nvcc_only_projection"
    negative_root = replay_root / "negative_projection"
    nvcc_tree = _materialize_subset(projection_root, nvcc_root, nvcc_paths)
    _materialize_subset(projection_root, negative_root, nvcc_paths)
    optix_relative = optix_include.relative_to(projection_root)
    cuda_relative = cuda_include.relative_to(projection_root)
    nvcc_optix = nvcc_root / optix_relative
    nvcc_cuda = nvcc_root / cuda_relative
    negative_optix = negative_root / optix_relative
    negative_cuda = negative_root / cuda_relative
    required_names = ("optix.h", "optix_device.h")
    required_nvcc = [nvcc_optix / name for name in required_names]
    if not all(path.is_file() and not path.is_symlink()
               for path in required_nvcc):
        _fail("NVCC-only projection lacks required OptiX header")
    negative_removed = negative_optix / "optix.h"
    negative_removed_relative = negative_removed.relative_to(
        negative_root).as_posix()
    negative_removed.unlink()
    negative_rows = _tree_rows(negative_root)
    if set(str(row["path"]) for row in nvcc_tree["rows"]) \
            - set(str(row["path"]) for row in negative_rows) \
            != {negative_removed_relative} \
            or len(negative_rows) + 1 != len(nvcc_tree["rows"]):
        _fail("negative projection differs by more than exact optix.h")

    common = {
        "python": python, "strace": strace, "child": child,
        "compute_capability": canonical_cc,
        "replay_root": replay_root,
        "original_roots": [original_optix_include, original_cuda_include],
    }
    original = _run_fresh_child(
        label="original", source=device_source,
        optix_include=original_optix_include,
        cuda_include=original_cuda_include, projected_roots=[],
        required_projected=[], expect_success=True, **common)
    nvcc_only = _run_fresh_child(
        label="nvcc_only", source=device_source,
        optix_include=nvcc_optix, cuda_include=nvcc_cuda,
        projected_roots=[nvcc_optix, nvcc_cuda],
        required_projected=required_nvcc, expect_success=True, **common)
    union = _run_fresh_child(
        label="union", source=device_source, optix_include=optix_include,
        cuda_include=cuda_include,
        projected_roots=[optix_include, cuda_include],
        required_projected=[optix_include / name for name in required_names],
        expect_success=True, **common)
    compaction = _run_fresh_child(
        label="compaction", source=compaction_source,
        optix_include=None, cuda_include=None, projected_roots=[],
        required_projected=[], expect_success=True, mode="cubin", **common)
    negative = _run_fresh_child(
        label="negative_missing_optix_h", source=device_source,
        optix_include=negative_optix, cuda_include=negative_cuda,
        projected_roots=[negative_optix, negative_cuda],
        required_projected=[negative_removed], expect_success=False, **common)

    ptx_products = [Path(str(row["product"]["path"]))
                    for row in (original, nvcc_only, union)]
    ptx_payloads = [path.read_bytes() for path in ptx_products]
    if not ptx_payloads[0] or any(payload != ptx_payloads[0]
                                  for payload in ptx_payloads[1:]):
        _fail("fresh original/NVCC-only/union PTX bytes differ")
    successful = (original, nvcc_only, union, compaction)
    loaded_identities = [row["child"]["loaded_nvrtc"]
                         for row in successful]
    if any(identity != loaded_identities[0]
           for identity in loaded_identities[1:]):
        _fail("fresh children loaded different NVRTC/builtins identities")
    child_pids = [int(row["child"]["pid"]) for row in successful]
    negative_pids = [int(pid) for pid in negative["trace"]["traced_pids"]]
    if len(set(child_pids)) != len(child_pids) \
            or set(child_pids) & set(negative_pids):
        _fail("fresh replay process identities are not disjoint")
    ptx = ptx_payloads[2]
    compaction_cubin = Path(str(
        compaction["product"]["path"])).read_bytes()
    ptx_options = list(union["child"]["compile_options"])
    original_ptx_options = list(original["child"]["compile_options"])
    ptx_target = str(union["child"]["target"])
    compaction_architecture = str(compaction["child"]["target"])
    compaction_options = list(compaction["child"]["compile_options"])
    if ptx_target != expected_sm or compaction_architecture != expected_sm \
            or f"--gpu-architecture={compute_architecture}" not in ptx_options:
        _fail("Goal5802 exact target architecture contract drift")
    if not ptx or b".version" not in ptx[:4096]:
        raise RuntimeError("Goal5802 matched PTX is invalid")
    if not compaction_cubin or compaction_cubin[:4] != b"\x7fELF":
        raise RuntimeError("Goal5802 compaction cubin is invalid")
    _write_create_only(args.output, ptx)
    _write_create_only(args.compaction_output, compaction_cubin)
    nvrtc_loaded = loaded_identities[0]
    nvrtc_library = {
        **nvrtc_loaded["library"], "version": nvrtc_loaded["version"]}
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.matched_ptx_untimed_prepare.v3",
        "status": "PASS__FRESH_PROCESS_TRACED_UNTIMED_PREPARE",
        "projection_claim": FINAL_PROJECTION_CLAIM,
        "device_source_sha256": sha256_file(device_source),
        "compaction_source_sha256": sha256_file(compaction_source),
        "optix_include_tree": tree_identity(optix_include),
        "cuda_include_tree": tree_identity(cuda_include),
        "header_projection_receipt_sha256": sha256_file(
            projection_receipt_path),
        "header_projection_tree_sha256": projection_receipt[
            "projection_tree_sha256"],
        "original_optix_include_path": str(original_optix_include),
        "original_cuda_include_path": str(original_cuda_include),
        "original_ptx_compile_options": original_ptx_options,
        "original_ptx_sha256": hashlib.sha256(ptx_payloads[0]).hexdigest(),
        "projected_ptx_byte_identical_to_original": True,
        "nvcc_only_ptx_byte_identical_to_original": True,
        "union_ptx_byte_identical_to_original": True,
        "nvrtc_library": nvrtc_library,
        "nvrtc_builtins": nvrtc_loaded["builtins"],
        "fresh_process_replay": {
            "python": _python_replay_identity(python),
            "strace": _file_identity(strace),
            "child": _file_identity(child),
            "canonical_projection_root": str(projection_root),
            "nvcc_only_projection_root": str(nvcc_root.resolve(strict=True)),
            "negative_projection_root": str(negative_root.resolve(strict=True)),
            "nvcc_only_sdk_paths": nvcc_paths,
            "direct_sdk_paths": direct_paths,
            "union_sdk_paths": union_paths,
            "nvcc_only_tree": nvcc_tree,
            "negative_tree_rows": negative_rows,
            "negative_removed_path": negative_removed_relative,
            "runs": {
                "original": original,
                "nvcc_only": nvcc_only,
                "union": union,
                "compaction": compaction,
                "negative_missing_optix_h": negative,
            },
            "successful_child_pids": child_pids,
            "all_successful_pids_distinct": True,
            "negative_pid_disjoint": True,
            "original_sdk_attempts_in_projected_runs": 0,
            "negative_compile_failed_without_product": True,
        },
        "compute_capability": canonical_cc,
        "ptx_compile_options": ptx_options,
        "ptx_target": ptx_target,
        "ptx_bytes": len(ptx),
        "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "compaction_cubin_architecture": compaction_architecture,
        "compaction_compile_options": compaction_options,
        "compaction_cubin_bytes": len(compaction_cubin),
        "compaction_cubin_sha256": hashlib.sha256(
            compaction_cubin).hexdigest(),
        "registered_performance_timing_count": 0,
        "clock_read_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
    }
    value["receipt_sha256"] = digest(value)
    _write_create_only(
        args.receipt,
        json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
