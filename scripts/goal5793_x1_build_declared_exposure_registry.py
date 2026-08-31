#!/usr/bin/env python3
"""Build a fail-closed Goal5793 X1 declared-exposure successor authority.

The authority deliberately does *not* pretend that today's worktree is the
missing S0 worktree snapshot.  It records a post-S0 successor observation,
scans every reachable Git commit through a reconstructable tree DAG, walks the
local S0 evidence DAG and supported archive members, and binds the frozen
Goal5753/survey components.  Missing historical workspace and owner disclosure
authorities are blocking gaps, so this tool cannot authorize X2.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import zipfile
from collections import Counter, deque
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

try:
    from scripts.goal5793_x1_canonical import (
        CANONICALIZATION_NAME,
        canonical_digest,
        canonical_json_bytes,
        seal_document,
        sha256_bytes,
    )
    from scripts import goal5793_x1_build_exposure_registry as survey_registry
except ModuleNotFoundError:  # direct execution from scripts/
    from goal5793_x1_canonical import (  # type: ignore[no-redef]
        CANONICALIZATION_NAME,
        canonical_digest,
        canonical_json_bytes,
        seal_document,
        sha256_bytes,
    )
    import goal5793_x1_build_exposure_registry as survey_registry  # type: ignore[no-redef]


SCHEMA = "rtdl.goal5793.x1.declared_exposure_successor_authority.v2"
PHASE_CACHE_SCHEMA = "rtdl.goal5793.x1.declared_exposure_phase_cache.v1"
DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path(
    "history/internal_docs/goal5793_x1_declared_project_exposure_registry_blocker_20260822.json"
)
S0_CLOSURE_PATH = Path(
    "history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json"
)
S0_CLOSURE_FILE_SHA256 = "4d6e37bc19c0f541537e2f9fc36a31b4d35a20bc0fb080ba495629c0d9fd1f41"
S0_CLOSURE_INTERNAL_SHA256 = "cc118989e6f7462eb236c414c08b7058ea4feacc8e4bac27898f9254bcb90a1a"
SURVEY_COMPONENT_PATH = Path(
    "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"
)
SURVEY_COMPONENT_SHA256 = "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"
OWNER_DISCLOSURE_PATH = Path(
    "history/internal_docs/goal5793_x1_owner_off_repository_exposure_disclosure_20260822.json"
)

ROOT_TRANSIENT_DIRECTORY_NAMES = {"build", "scratch", "tmp"}
ROOT_TRANSIENT_DIRECTORY_PREFIXES = (".goal", ".tmp_goal")
CACHE_DIRECTORY_NAMES = {
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
# ``history`` is a workspace-owned relocated junction in this checkout.  It is
# the sole reparse directory deliberately traversed from the repository root;
# its exact logical and resolved identities are recorded in the observation.
FOLLOWED_ROOT_REPARSE_DIRECTORIES = {"history"}
ARCHIVE_SUFFIXES = (".tar.gz", ".tgz", ".tar", ".zip", ".gz")
MAX_WORKSPACE_FILE_BYTES = 16 * 1024 * 1024
MAX_GIT_TEXT_BLOB_BYTES = 16 * 1024 * 1024
MAX_DAG_LOCAL_FILE_BYTES = 512 * 1024 * 1024
MAX_ARCHIVE_MEMBER_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_TOTAL_MEMBER_BYTES = 1024 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 100_000
MAX_ARCHIVE_DEPTH = 3
MAX_DAG_LOCAL_NODES = 50_000
MAX_DAG_TOTAL_SCANNED_BYTES = 8 * 1024 * 1024 * 1024

OUTPUT_NAME_PREFIX = "goal5793_x1_declared_project_exposure_registry"


class DeclaredExposureError(RuntimeError):
    """Stable fail-closed error for scanner or authority inconsistencies."""


def _progress(event: str, **facts: Any) -> None:
    """Emit non-authoritative progress telemetry to stderr.

    Progress records are deliberately excluded from every scientific digest.
    They exist only so a long local scan is observable and can be stopped at a
    phase boundary instead of appearing hung.
    """

    print(
        json.dumps({"event": event, **facts}, sort_keys=True),
        file=sys.stderr,
        flush=True,
    )


def _filesystem_path(path: Path) -> Path:
    """Return an extended Windows path without changing the logical identity."""

    if os.name != "nt":
        return path
    raw = str(path.absolute())
    if raw.startswith("\\\\?\\"):
        return Path(raw)
    if raw.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + raw[2:])
    return Path("\\\\?\\" + raw)


def _path_stat(path: Path) -> os.stat_result:
    return _filesystem_path(path).stat()


def _path_is_file(path: Path) -> bool:
    return _filesystem_path(path).is_file()


def _read_path_bytes(path: Path) -> bytes:
    return _filesystem_path(path).read_bytes()


def utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with _filesystem_path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_strict_text(payload: bytes) -> tuple[bool, str | None]:
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False, None
    if "\x00" in text:
        return False, None
    forbidden_controls = [
        char for char in text
        if (ord(char) < 32 and char not in "\t\n\r\f") or 0x7F <= ord(char) <= 0x9F
    ]
    if forbidden_controls:
        return False, None
    return True, text


def _fallback_alias(title: str, author: str, year: str) -> str | None:
    normalized_title = survey_registry.normalize_words(title)
    normalized_author = survey_registry.normalize_first_author(author)
    year_match = re.search(r"\d{4}", year)
    if not (normalized_title and normalized_author and year_match):
        return None
    digest = canonical_digest(
        {
            "first_author_family": normalized_author,
            "title": normalized_title,
            "year": year_match.group(0),
        },
        domain="rtdl.goal5793.x1.declared_exposure.fallback_identity",
        version=1,
        projection="normalized_title_first_author_family_year",
    )["sha256"]
    return f"fallback_sha256:{digest}"


DOI_CANDIDATE_RE = re.compile(r"(?i)(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.\d{4,9}/[^\s\"<>`]+)")
CITATION_KEY_FIELD_RE = re.compile(
    r"(?i)[\"']?citation_key[\"']?\s*[:=]\s*[\"']([^\"'\s,}\]]+)[\"']"
)


def _walk_json_records(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_json_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_json_records(child)


def extract_aliases(text: str, path_hint: str) -> tuple[list[str], list[str]]:
    """Extract only frozen identifier/fallback/citation-key aliases."""

    aliases: set[str] = set()
    gaps: list[str] = []
    for match in DOI_CANDIDATE_RE.finditer(text):
        doi = survey_registry.normalize_doi(match.group(1))
        if doi:
            aliases.add(f"doi:{doi}")
    aliases.update(f"arxiv:{value}" for value in survey_registry.extract_arxiv_ids(text))
    aliases.update(f"openalex:{value}" for value in survey_registry.extract_openalex_ids(text))
    for occurrence in survey_registry.extract_citations(path_hint, text):
        aliases.update(
            f"citation_key:{key}" for key in occurrence["keys"] if key != "*"
        )
    aliases.update(f"citation_key:{match.group(1)}" for match in CITATION_KEY_FIELD_RE.finditer(text))

    if path_hint.lower().endswith(".bib"):
        try:
            entries = survey_registry.parse_bibtex(text)
        except Exception as exc:  # preserve failure, never invent partial BibTeX rows
            gaps.append(f"BIBTEX_PARSE_FAILED:{type(exc).__name__}")
        else:
            for entry in entries:
                entry_aliases, _ = survey_registry._entry_aliases(entry)
                aliases.update(str(row["value"]) for row in entry_aliases)

    if path_hint.lower().endswith(".json"):
        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, RecursionError):
            gaps.append("JSON_PARSE_FAILED__REGEX_IDENTIFIERS_RETAINED")
        else:
            for record in _walk_json_records(payload):
                title = record.get("title")
                author = record.get("author") or record.get("first_author")
                year = record.get("year")
                if isinstance(author, list) and author:
                    author = author[0]
                if isinstance(title, str) and isinstance(author, str) and year is not None:
                    fallback = _fallback_alias(title, author, str(year))
                    if fallback:
                        aliases.add(fallback)
    return sorted(aliases, key=utf8_key), sorted(set(gaps), key=utf8_key)


def canonical_rows_digest(rows: Any, domain: str, projection: str) -> dict[str, Any]:
    return canonical_digest(rows, domain=domain, version=1, projection=projection)


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_output_path(relative_path: str) -> bool:
    return (
        relative_path.startswith("history/internal_docs/" + OUTPUT_NAME_PREFIX)
        or relative_path == DEFAULT_OUTPUT.as_posix()
    )


def _is_reparse_point(path: Path) -> bool:
    filesystem_path = _filesystem_path(path)
    attributes = getattr(filesystem_path.lstat(), "st_file_attributes", 0)
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    return filesystem_path.is_symlink() or bool(attributes & reparse_flag)


def _directory_exclusion_reason(path: Path, *, at_repository_root: bool) -> str | None:
    lowered = path.name.lower()
    if lowered == ".git":
        return "GIT_METADATA_DIRECTORY_EXCLUDED__REACHABLE_OBJECTS_SCANNED_SEPARATELY"
    if lowered in CACHE_DIRECTORY_NAMES:
        return "EXPLICIT_CACHE_DIRECTORY_EXCLUDED"
    if at_repository_root and (
        lowered in ROOT_TRANSIENT_DIRECTORY_NAMES
        or any(lowered.startswith(prefix) for prefix in ROOT_TRANSIENT_DIRECTORY_PREFIXES)
    ):
        return "EXPLICIT_POST_S0_TRANSIENT_OR_BUILD_ROOT_DIRECTORY_EXCLUDED"
    return None


def enumerate_successor_workspace_paths(
    root: Path,
) -> tuple[list[Path], list[dict[str, Any]], list[dict[str, Any]]]:
    """Enumerate the repo root, omitting only explicit, recorded boundaries."""

    files: set[Path] = set()
    exclusions: list[dict[str, Any]] = []
    followed_reparse_mounts: list[dict[str, Any]] = []
    walk_roots: list[Path] = []

    for entry in sorted(root.iterdir(), key=lambda path: utf8_key(path.name)):
        relative = entry.name
        if _is_output_path(relative):
            exclusions.append(
                {
                    "path": relative,
                    "reason": "SELF_REFERENTIAL_SUCCESSOR_AUTHORITY_OUTPUT_EXCLUDED",
                    "scope_effect": "NO_EXPOSURE_COVERAGE_LOSS__OUTPUT_DOES_NOT_PREEXIST_ITS_OWN_BUILD",
                }
            )
            continue
        if entry.is_file() and not _is_reparse_point(entry):
            if entry.name == ".git":
                exclusions.append(
                    {
                        "path": relative,
                        "reason": "GIT_CONTROL_FILE_EXCLUDED__REACHABLE_OBJECTS_SCANNED_SEPARATELY",
                        "scope_effect": "NO_REGULAR_REPOSITORY_TEXT_COVERAGE_CLAIM_FOR_GIT_CONTROL_BYTES",
                    }
                )
            else:
                # A root *file* is never discarded because its name begins
                # with build/tmp/.goal.  Prefix exclusions apply to explicit
                # transient root directories only.
                files.add(entry)
            continue
        if entry.is_dir():
            reason = _directory_exclusion_reason(entry, at_repository_root=True)
            if reason is not None:
                exclusions.append(
                    {
                        "path": relative,
                        "reason": reason,
                        "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_DIRECTORY_COVERAGE_GAP",
                    }
                )
                continue
            if _is_reparse_point(entry):
                if entry.name not in FOLLOWED_ROOT_REPARSE_DIRECTORIES:
                    exclusions.append(
                        {
                            "path": relative,
                            "reason": "UNAPPROVED_REPARSE_OR_LINKED_ROOT_DIRECTORY_EXCLUDED",
                            "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_DIRECTORY_COVERAGE_GAP",
                        }
                    )
                    continue
                followed_reparse_mounts.append(
                    {
                        "logical_path": relative,
                        "reason": "WORKSPACE_OWNED_RELOCATED_HISTORY_MOUNT_EXPLICITLY_FOLLOWED",
                        "resolved_target": str(entry.resolve(strict=True)),
                    }
                )
            walk_roots.append(entry)
            continue
        exclusions.append(
            {
                "path": relative,
                "reason": "NONREGULAR_ROOT_ENTRY_EXCLUDED",
                "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_PATH_COVERAGE_GAP",
            }
        )

    filesystem_root = _filesystem_path(root)

    def walk_error(error: OSError) -> None:
        raise DeclaredExposureError(
            f"SUCCESSOR_WORKSPACE_ENUMERATION_ERROR:{error.errno}:{error.filename}"
        )

    for base in walk_roots:
        filesystem_base = _filesystem_path(base)
        for directory, dirnames, filenames in os.walk(
            filesystem_base,
            topdown=True,
            followlinks=False,
            onerror=walk_error,
        ):
            filesystem_current = Path(directory)
            logical_relative_current = filesystem_current.relative_to(filesystem_root)
            current = root / logical_relative_current
            retained_dirs: list[str] = []
            for dirname in sorted(dirnames, key=utf8_key):
                child = current / dirname
                relative_child = _relative(root, child)
                reason = _directory_exclusion_reason(child, at_repository_root=False)
                if reason is not None:
                    exclusions.append(
                        {
                            "path": relative_child,
                            "reason": reason,
                            "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_DIRECTORY_COVERAGE_GAP",
                        }
                    )
                elif _is_reparse_point(child):
                    exclusions.append(
                        {
                            "path": relative_child,
                            "reason": "NESTED_REPARSE_OR_LINKED_DIRECTORY_EXCLUDED",
                            "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_DIRECTORY_COVERAGE_GAP",
                        }
                    )
                else:
                    retained_dirs.append(dirname)
            dirnames[:] = retained_dirs
            for filename in sorted(filenames, key=utf8_key):
                path = current / filename
                relative_path = _relative(root, path)
                if _is_output_path(relative_path):
                    exclusions.append(
                        {
                            "path": relative_path,
                            "reason": "SELF_REFERENTIAL_SUCCESSOR_AUTHORITY_OUTPUT_EXCLUDED",
                            "scope_effect": "NO_EXPOSURE_COVERAGE_LOSS__OUTPUT_DOES_NOT_PREEXIST_ITS_OWN_BUILD",
                        }
                    )
                    continue
                if _is_reparse_point(path) or not _path_is_file(path):
                    exclusions.append(
                        {
                            "path": relative_path,
                            "reason": "NONREGULAR_OR_LINKED_FILE_EXCLUDED",
                            "scope_effect": "SUCCESSOR_OBSERVATION_HAS_EXPLICIT_PATH_COVERAGE_GAP",
                        }
                    )
                    continue
                files.add(path)

    return (
        sorted(files, key=lambda path: utf8_key(_relative(root, path))),
        sorted(exclusions, key=lambda row: utf8_key(str(row["path"]))),
        sorted(followed_reparse_mounts, key=lambda row: utf8_key(str(row["logical_path"]))),
    )


def scan_successor_workspace(root: Path) -> dict[str, Any]:
    initial_paths, exclusions, followed_reparse_mounts = enumerate_successor_workspace_paths(root)
    initial_relatives = [_relative(root, path) for path in initial_paths]
    rows: list[dict[str, Any]] = []
    non_text_rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    observed_stats: dict[str, tuple[int, int]] = {}

    for path, relative_path in zip(initial_paths, initial_relatives):
        before = _path_stat(path)
        observed_stats[relative_path] = (before.st_size, before.st_mtime_ns)
        if before.st_size > MAX_WORKSPACE_FILE_BYTES:
            gaps.append(
                {
                    "bytes": before.st_size,
                    "path": relative_path,
                    "reason": "SUCCESSOR_FILE_EXCEEDS_TEXT_SCAN_LIMIT",
                }
            )
            continue
        payload = _read_path_bytes(path)
        after = _path_stat(path)
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise DeclaredExposureError("SUCCESSOR_WORKSPACE_FILE_CHANGED_DURING_SCAN")
        text_ok, text = is_strict_text(payload)
        if not text_ok or text is None:
            non_text_rows.append(
                {
                    "bytes": len(payload),
                    "classification": "NOT_STRICT_UTF8_TEXT",
                    "path": relative_path,
                    "sha256": sha256_bytes(payload),
                }
            )
            continue
        aliases, alias_gaps = extract_aliases(text, relative_path)
        rows.append(
            {
                "aliases": aliases,
                "alias_extraction_gaps": alias_gaps,
                "bytes": len(payload),
                "path": relative_path,
                "sha256": sha256_bytes(payload),
            }
        )

    final_paths, final_exclusions, final_followed_reparse_mounts = (
        enumerate_successor_workspace_paths(root)
    )
    final_relatives = [_relative(root, path) for path in final_paths]
    if (
        final_relatives != initial_relatives
        or final_exclusions != exclusions
        or final_followed_reparse_mounts != followed_reparse_mounts
    ):
        raise DeclaredExposureError("SUCCESSOR_WORKSPACE_PATH_SET_CHANGED_DURING_SCAN")
    for path, relative_path in zip(final_paths, final_relatives):
        final_stat = _path_stat(path)
        if observed_stats[relative_path] != (final_stat.st_size, final_stat.st_mtime_ns):
            raise DeclaredExposureError("SUCCESSOR_WORKSPACE_FILE_CHANGED_AFTER_SCAN")

    rows.sort(key=lambda row: utf8_key(str(row["path"])))
    non_text_rows.sort(key=lambda row: utf8_key(str(row["path"])))
    gaps.sort(key=lambda row: utf8_key(str(row["path"])))
    return {
        "classification": "EXACT_CURRENT_POST_S0_X1_SUCCESSOR_OBSERVATION__NOT_THE_MISSING_S0_WORKSPACE_SNAPSHOT",
        "enumeration_scope": "REPOSITORY_ROOT_RECURSIVE_EXCEPT_EACH_EXPLICITLY_RECORDED_EXCLUSION",
        "root_regular_files_are_not_excluded_by_filename_prefix": True,
        "path_enumeration_count": len(initial_paths),
        "strict_utf8_text_rows": rows,
        "strict_utf8_text_rows_digest": canonical_rows_digest(
            rows,
            "rtdl.goal5793.x1.declared_exposure.successor_workspace_text_rows",
            "path_bytes_sha256_aliases_sorted_by_path_utf8",
        ),
        "non_strict_text_rows": non_text_rows,
        "non_strict_text_rows_digest": canonical_rows_digest(
            non_text_rows,
            "rtdl.goal5793.x1.declared_exposure.successor_workspace_non_text_rows",
            "path_bytes_sha256_classification_sorted_by_path_utf8",
        ),
        "excluded_roots_or_directories": exclusions,
        "followed_reparse_mounts": followed_reparse_mounts,
        "limit_gaps": gaps,
        "complete_for_current_successor_repo_regular_text_under_limits_and_explicit_exclusions": not gaps,
        "complete_current_successor_workspace_without_coverage_gaps": not exclusions and not gaps,
        "complete_historical_s0_workspace_snapshot": False,
        "post_s0_or_x1_contamination_present": True,
    }


def run_git(root: Path, args: Sequence[str], input_bytes: bytes | None = None) -> bytes:
    environment = os.environ.copy()
    environment.update(
        {
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        env=environment,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise DeclaredExposureError(
            f"GIT_COMMAND_FAILED:{' '.join(args)}:{completed.stderr.decode('utf-8', errors='replace')[:500]}"
        )
    return completed.stdout


def git_refs(root: Path) -> list[dict[str, str]]:
    output = run_git(root, ["for-each-ref", "--format=%(refname)%00%(objectname)"])
    rows: list[dict[str, str]] = []
    for line in output.decode("utf-8", errors="strict").splitlines():
        refname, oid = line.split("\x00", 1)
        rows.append({"object_id": oid, "refname": refname})
    rows.sort(key=lambda row: utf8_key(row["refname"]))
    return rows


def git_batch_check(root: Path, object_ids: Sequence[str]) -> dict[str, tuple[str, int]]:
    if not object_ids:
        return {}
    payload = "".join(f"{oid}\n" for oid in object_ids).encode("ascii")
    output = run_git(
        root,
        ["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        payload,
    )
    lines = output.decode("ascii", errors="strict").splitlines()
    if len(lines) != len(object_ids):
        raise DeclaredExposureError("GIT_BATCH_CHECK_ROW_COUNT_MISMATCH")
    result: dict[str, tuple[str, int]] = {}
    for expected, line in zip(object_ids, lines):
        parts = line.split(" ")
        if len(parts) != 3 or parts[0] != expected or parts[1] == "missing":
            raise DeclaredExposureError("GIT_BATCH_CHECK_IDENTITY_MISMATCH")
        result[expected] = (parts[1], int(parts[2]))
    return result


def git_batch_read(root: Path, object_ids: Sequence[str]) -> dict[str, bytes]:
    if not object_ids:
        return {}
    payload = "".join(f"{oid}\n" for oid in object_ids).encode("ascii")
    output = run_git(root, ["cat-file", "--batch"], payload)
    cursor = 0
    result: dict[str, bytes] = {}
    for expected in object_ids:
        line_end = output.find(b"\n", cursor)
        if line_end < 0:
            raise DeclaredExposureError("GIT_BATCH_OBJECT_HEADER_TRUNCATED")
        header = output[cursor:line_end].decode("ascii", errors="strict")
        cursor = line_end + 1
        parts = header.split(" ")
        if len(parts) != 3 or parts[0] != expected or parts[1] == "missing":
            raise DeclaredExposureError("GIT_BATCH_OBJECT_IDENTITY_MISMATCH")
        size = int(parts[2])
        end = cursor + size
        if end >= len(output) or output[end:end + 1] != b"\n":
            raise DeclaredExposureError("GIT_BATCH_OBJECT_BODY_TRUNCATED")
        result[expected] = output[cursor:end]
        cursor = end + 1
    if cursor != len(output):
        raise DeclaredExposureError("GIT_BATCH_OBJECT_TRAILING_BYTES")
    return result


def _chunks_by_size(
    object_ids: Sequence[str], inventory: Mapping[str, tuple[str, int]], max_bytes: int = 64 * 1024 * 1024
) -> Iterable[list[str]]:
    chunk: list[str] = []
    total = 0
    for oid in object_ids:
        size = inventory[oid][1]
        if chunk and total + size > max_bytes:
            yield chunk
            chunk = []
            total = 0
        chunk.append(oid)
        total += size
    if chunk:
        yield chunk


def parse_git_tree(payload: bytes, oid_bytes: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(payload):
        space = payload.find(b" ", cursor)
        nul = payload.find(b"\x00", space + 1)
        if space < 0 or nul < 0 or nul + 1 + oid_bytes > len(payload):
            raise DeclaredExposureError("GIT_TREE_OBJECT_MALFORMED")
        mode = payload[cursor:space].decode("ascii", errors="strict")
        name_bytes = payload[space + 1:nul]
        object_id = payload[nul + 1:nul + 1 + oid_bytes].hex()
        cursor = nul + 1 + oid_bytes
        if b"/" in name_bytes or b"\x00" in name_bytes:
            raise DeclaredExposureError("GIT_TREE_ENTRY_NAME_INVALID")
        try:
            name = name_bytes.decode("utf-8", errors="strict")
            name_encoding = "UTF8"
            name_b64 = None
        except UnicodeDecodeError:
            name = None
            name_encoding = "BASE64_RAW_BYTES"
            name_b64 = base64.b64encode(name_bytes).decode("ascii")
        normalized_mode = mode.lstrip("0") or "0"
        if normalized_mode == "40000":
            object_type = "tree"
        elif normalized_mode in {"100644", "100755"}:
            object_type = "regular_blob"
        elif normalized_mode == "120000":
            object_type = "symlink_blob"
        elif normalized_mode == "160000":
            object_type = "gitlink_commit"
        else:
            object_type = "unknown_mode"
        rows.append(
            {
                "mode": mode,
                "name": name,
                "name_base64": name_b64,
                "name_encoding": name_encoding,
                "object_id": object_id,
                "object_type": object_type,
            }
        )
    return rows


def scan_git_history(root: Path) -> dict[str, Any]:
    started = time.monotonic()
    _progress("git_scan_started")
    refs_before = git_refs(root)
    commit_ids = sorted(
        set(run_git(root, ["rev-list", "--all"]).decode("ascii", errors="strict").splitlines())
    )
    objects_output = run_git(root, ["rev-list", "--objects", "--all"])
    object_ids = sorted(
        {line.split(b" ", 1)[0].decode("ascii") for line in objects_output.splitlines() if line}
    )
    inventory = git_batch_check(root, object_ids)
    _progress(
        "git_inventory_complete",
        elapsed_seconds=round(time.monotonic() - started, 3),
        reachable_commits=len(commit_ids),
        reachable_objects=len(object_ids),
    )
    object_rows = [
        {"bytes": inventory[oid][1], "object_id": oid, "type": inventory[oid][0]}
        for oid in object_ids
    ]
    type_counts = Counter(row["type"] for row in object_rows)
    object_format = run_git(root, ["rev-parse", "--show-object-format"]).decode("ascii").strip()
    oid_bytes = {"sha1": 20, "sha256": 32}.get(object_format)
    if oid_bytes is None:
        raise DeclaredExposureError("UNSUPPORTED_GIT_OBJECT_FORMAT")

    commit_bodies: dict[str, bytes] = {}
    for chunk in _chunks_by_size(commit_ids, inventory):
        commit_bodies.update(git_batch_read(root, chunk))
    commit_roots: list[dict[str, str]] = []
    for oid in commit_ids:
        if inventory[oid][0] != "commit":
            raise DeclaredExposureError("REV_LIST_NONCOMMIT")
        first_line = commit_bodies[oid].split(b"\n", 1)[0]
        if not first_line.startswith(b"tree "):
            raise DeclaredExposureError("COMMIT_TREE_HEADER_MISSING")
        commit_roots.append(
            {"commit_id": oid, "root_tree_id": first_line[5:].decode("ascii", errors="strict")}
        )
    _progress(
        "git_commit_roots_complete",
        elapsed_seconds=round(time.monotonic() - started, 3),
        commit_roots=len(commit_roots),
    )

    tree_ids = [oid for oid in object_ids if inventory[oid][0] == "tree"]
    tree_rows: list[dict[str, Any]] = []
    regular_ref_counts: Counter[str] = Counter()
    regular_names: dict[str, set[str]] = {}
    non_utf8_tree_name_count = 0
    unknown_mode_count = 0
    for chunk in _chunks_by_size(tree_ids, inventory):
        bodies = git_batch_read(root, chunk)
        for tree_id in chunk:
            tree_payload = bodies[tree_id]
            entries = parse_git_tree(tree_payload, oid_bytes)
            tree_non_utf8 = sum(row["name_encoding"] != "UTF8" for row in entries)
            tree_unknown = sum(row["object_type"] == "unknown_mode" for row in entries)
            tree_regular = sum(row["object_type"] == "regular_blob" for row in entries)
            non_utf8_tree_name_count += tree_non_utf8
            unknown_mode_count += tree_unknown
            for row in entries:
                if row["object_type"] == "regular_blob":
                    blob_id = str(row["object_id"])
                    regular_ref_counts[blob_id] += 1
                    if row["name"] is not None:
                        regular_names.setdefault(blob_id, set()).add(str(row["name"]))
            tree_rows.append(
                {
                    "bytes": len(tree_payload),
                    "entry_count": len(entries),
                    "non_utf8_entry_name_count": tree_non_utf8,
                    "raw_tree_sha256": sha256_bytes(tree_payload),
                    "regular_blob_entry_count": tree_regular,
                    "tree_id": tree_id,
                    "unknown_mode_entry_count": tree_unknown,
                }
            )
        del bodies
    _progress(
        "git_tree_dag_complete",
        elapsed_seconds=round(time.monotonic() - started, 3),
        tree_rows=len(tree_rows),
        unique_regular_blobs=len(regular_ref_counts),
    )

    candidate_blob_ids = sorted(regular_ref_counts)
    missing_inventory = [oid for oid in candidate_blob_ids if oid not in inventory]
    if missing_inventory:
        raise DeclaredExposureError("TREE_REFERENCED_OBJECT_NOT_IN_REACHABLE_INVENTORY")
    bounded_ids = [oid for oid in candidate_blob_ids if inventory[oid][1] <= MAX_GIT_TEXT_BLOB_BYTES]
    oversize_ids = [oid for oid in candidate_blob_ids if inventory[oid][1] > MAX_GIT_TEXT_BLOB_BYTES]
    text_rows: list[dict[str, Any]] = []
    binary_blob_count = 0
    for chunk in _chunks_by_size(bounded_ids, inventory):
        bodies = git_batch_read(root, chunk)
        for oid in chunk:
            payload = bodies[oid]
            text_ok, text = is_strict_text(payload)
            if not text_ok or text is None:
                binary_blob_count += 1
                continue
            names = sorted(regular_names.get(oid, set()), key=utf8_key)
            bib_names = [name for name in names if name.lower().endswith(".bib")]
            path_hint = bib_names[0] if bib_names else (names[0] if names else "git_blob.txt")
            aliases, alias_gaps = extract_aliases(text, path_hint)
            text_rows.append(
                {
                    "aliases": aliases,
                    "alias_extraction_gaps": alias_gaps,
                    "bytes": len(payload),
                    "direct_regular_tree_reference_count": regular_ref_counts[oid],
                    "git_blob_id": oid,
                    "observed_direct_names": names,
                    "sha256": sha256_bytes(payload),
                }
            )
    _progress(
        "git_text_blob_scan_complete",
        elapsed_seconds=round(time.monotonic() - started, 3),
        strict_utf8_text_blobs=len(text_rows),
        binary_blobs=binary_blob_count,
        oversize_blobs=len(oversize_ids),
    )
    text_rows.sort(key=lambda row: row["git_blob_id"])
    oversize_rows = [
        {
            "bytes": inventory[oid][1],
            "direct_regular_tree_reference_count": regular_ref_counts[oid],
            "git_blob_id": oid,
            "reason": "REACHABLE_REGULAR_BLOB_EXCEEDS_FROZEN_TEXT_SCAN_LIMIT",
        }
        for oid in oversize_ids
    ]

    refs_after = git_refs(root)
    commits_after = sorted(
        set(run_git(root, ["rev-list", "--all"]).decode("ascii", errors="strict").splitlines())
    )
    if refs_before != refs_after or commit_ids != commits_after:
        raise DeclaredExposureError("GIT_REACHABILITY_CHANGED_DURING_SCAN")
    root_tree_ids = {row["root_tree_id"] for row in commit_roots}
    if not root_tree_ids.issubset(set(tree_ids)):
        raise DeclaredExposureError("COMMIT_ROOT_TREE_NOT_IN_REACHABLE_TREE_SET")

    result = {
        "object_format": object_format,
        "git_version": run_git(root, ["--version"]).decode("utf-8", errors="strict").strip(),
        "refs": refs_before,
        "reachable_commit_roots": commit_roots,
        "reachable_object_inventory": object_rows,
        "reachable_object_inventory_digest": canonical_rows_digest(
            object_rows,
            "rtdl.goal5793.x1.declared_exposure.git_object_inventory",
            "object_id_type_bytes_sorted_by_object_id",
        ),
        "tree_dag": tree_rows,
        "tree_dag_digest": canonical_rows_digest(
            tree_rows,
            "rtdl.goal5793.x1.declared_exposure.git_tree_dag",
            "tree_object_identity_summaries_sorted_by_tree_id",
        ),
        "strict_utf8_regular_text_blobs": text_rows,
        "strict_utf8_regular_text_blobs_digest": canonical_rows_digest(
            text_rows,
            "rtdl.goal5793.x1.declared_exposure.git_text_blobs",
            "git_blob_sha256_aliases_sorted_by_git_blob_id",
        ),
        "oversize_regular_blob_gaps": oversize_rows,
        "counts": {
            "reachable_commits": len(commit_ids),
            "reachable_objects": len(object_rows),
            "reachable_object_types": dict(sorted(type_counts.items())),
            "reachable_trees": len(tree_rows),
            "unique_regular_referenced_blobs": len(candidate_blob_ids),
            "strict_utf8_regular_text_blobs": len(text_rows),
            "binary_or_control_regular_blobs_under_limit": binary_blob_count,
            "oversize_regular_blob_gaps": len(oversize_rows),
            "non_utf8_tree_entry_names": non_utf8_tree_name_count,
            "unknown_tree_entry_modes": unknown_mode_count,
        },
        "provenance_model": {
            "commit_path_reconstruction": "join reachable_commit_roots commit->root tree with exact Git tree objects; tree_dag binds every raw tree object by Git id plus independent sha256/count summary; each text row is keyed by exact Git blob id plus independent content sha256",
            "unchanged_file_occurrences_are_not_dropped": True,
            "raw_git_object_bytes_embedded_in_this_json": False,
            "exact_local_git_object_database_required_for_path_reconstruction": True,
            "tree_dag_rows_are_content_identity_summaries_not_expanded_entry_copies": True,
            "deduplication_unit": "git_blob_id_plus_sha256",
        },
        "complete_under_frozen_blob_size_limit": not oversize_rows and unknown_mode_count == 0,
    }
    _progress(
        "git_scan_complete",
        elapsed_seconds=round(time.monotonic() - started, 3),
        reachable_objects=len(object_rows),
    )
    return result


def safe_virtual_member_path(name: str) -> str:
    if not name or "\\" in name or "\x00" in name or re.match(r"^[A-Za-z]:", name):
        raise DeclaredExposureError("UNSAFE_ARCHIVE_MEMBER_PATH")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise DeclaredExposureError("UNSAFE_ARCHIVE_MEMBER_PATH")
    normalized = path.as_posix()
    if normalized != name.rstrip("/"):
        raise DeclaredExposureError("NONCANONICAL_ARCHIVE_MEMBER_PATH")
    return normalized


REPO_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:history/internal_docs|scripts|tests|src|docs|memory|examples|Paper-reproduction-apps)/[^\s`\"'<>|;,(){}\[\]]+)"
)
BARE_HISTORY_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:call_for_review_|review_|self_review_|goal|v4_)[A-Za-z0-9_.-]+\.(?:json|md|py|tar\.gz|tgz|tar|zip|gz|pdf))"
)


def _json_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                yield key
            yield from _json_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _json_strings(child)


def extract_repository_references(text: str, path_hint: str) -> list[str]:
    candidates: set[str] = set(match.group(1) for match in REPO_PATH_RE.finditer(text))
    if path_hint.lower().endswith(".json"):
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, RecursionError):
            parsed = None
        if parsed is not None:
            for value in _json_strings(parsed):
                normalized = value.replace("\\", "/").strip()
                if any(normalized.startswith(prefix + "/") for prefix in (
                    "history/internal_docs", "scripts", "tests", "src", "docs", "memory", "examples", "Paper-reproduction-apps"
                )):
                    candidates.add(normalized)
    for match in re.finditer(r"`([^`\r\n]+)`", text):
        value = match.group(1).replace("\\", "/").strip()
        if any(value.startswith(prefix + "/") for prefix in (
            "history/internal_docs", "scripts", "tests", "src", "docs", "memory", "examples", "Paper-reproduction-apps"
        )):
            candidates.add(value)
    candidates.update(f"history/internal_docs/{match.group(1)}" for match in BARE_HISTORY_RE.finditer(text))
    cleaned: set[str] = set()
    for candidate in candidates:
        value = candidate.rstrip(".:")
        value = re.sub(r":\d+(?::\d+)?$", "", value)
        if "*" in value or "?" in value or ".." in PurePosixPath(value).parts:
            continue
        cleaned.add(PurePosixPath(value).as_posix())
    return sorted(cleaned, key=utf8_key)


def pdf_parser_authority() -> dict[str, Any]:
    executable = shutil.which("pdftotext")
    if executable is None:
        return {"available": False, "reason": "PDFTOTEXT_NOT_FOUND"}
    path = Path(executable)
    completed = subprocess.run(
        [executable, "-v"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    version = completed.stdout.decode("utf-8", errors="replace").splitlines()[0].strip()
    return {
        "available": completed.returncode == 0,
        "binary_bytes": path.stat().st_size,
        "binary_sha256": file_sha256(path),
        "command": ["pdftotext", "-enc", "UTF-8", "-nopgbrk", "INPUT.pdf", "-"],
        "executable_basename": path.name,
        "version_line": version,
    }


def parse_pdf_bytes(payload: bytes, parser: Mapping[str, Any]) -> tuple[str | None, str | None]:
    if not parser.get("available"):
        return None, "PDF_PARSER_UNAVAILABLE"
    executable = shutil.which("pdftotext")
    if executable is None or file_sha256(Path(executable)) != parser["binary_sha256"]:
        return None, "PDF_PARSER_IDENTITY_CHANGED"
    with tempfile.TemporaryDirectory() as temporary:
        input_path = Path(temporary) / "input.pdf"
        input_path.write_bytes(payload)
        completed = subprocess.run(
            [executable, "-enc", "UTF-8", "-nopgbrk", str(input_path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if completed.returncode != 0:
        return None, "PDFTOTEXT_FAILED"
    try:
        return completed.stdout.decode("utf-8", errors="strict"), None
    except UnicodeDecodeError:
        return None, "PDFTOTEXT_OUTPUT_NOT_STRICT_UTF8"


def _looks_like_archive(path_hint: str) -> bool:
    lowered = path_hint.lower()
    return lowered.endswith(ARCHIVE_SUFFIXES)


def _scan_member_payload(
    payload: bytes,
    virtual_path: str,
    depth: int,
    pdf_parser: Mapping[str, Any],
    rows: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    references: set[str],
) -> None:
    identity = {"bytes": len(payload), "path": virtual_path, "sha256": sha256_bytes(payload)}
    if len(payload) > MAX_ARCHIVE_MEMBER_BYTES:
        gaps.append({**identity, "reason": "ARCHIVE_MEMBER_EXCEEDS_FROZEN_MEMBER_LIMIT"})
        rows.append({**identity, "classification": "LIMIT_GAP", "aliases": []})
        return
    if _looks_like_archive(virtual_path):
        if depth >= MAX_ARCHIVE_DEPTH:
            gaps.append({**identity, "reason": "NESTED_ARCHIVE_DEPTH_LIMIT_REACHED"})
            rows.append({**identity, "classification": "NESTED_ARCHIVE_LIMIT_GAP", "aliases": []})
            return
        rows.append({**identity, "classification": "NESTED_ARCHIVE_CONTAINER", "aliases": []})
        _scan_archive_payload(payload, virtual_path, depth + 1, pdf_parser, rows, gaps, references)
        return
    if virtual_path.lower().endswith(".pdf"):
        text, error = parse_pdf_bytes(payload, pdf_parser)
        if error:
            gaps.append({**identity, "reason": error})
            rows.append({**identity, "classification": "PDF_PARSE_GAP", "aliases": []})
            return
        assert text is not None
        aliases, alias_gaps = extract_aliases(text, virtual_path + ".txt")
        references.update(extract_repository_references(text, virtual_path + ".txt"))
        rows.append(
            {**identity, "classification": "PDF_PARSED_TEXT", "aliases": aliases, "alias_extraction_gaps": alias_gaps}
        )
        return
    text_ok, text = is_strict_text(payload)
    if text_ok and text is not None:
        aliases, alias_gaps = extract_aliases(text, virtual_path)
        references.update(extract_repository_references(text, virtual_path))
        rows.append(
            {**identity, "classification": "STRICT_UTF8_TEXT", "aliases": aliases, "alias_extraction_gaps": alias_gaps}
        )
    else:
        rows.append({**identity, "classification": "BINARY_NON_PDF", "aliases": []})


def _scan_archive_payload(
    payload: bytes,
    virtual_path: str,
    depth: int,
    pdf_parser: Mapping[str, Any],
    rows: list[dict[str, Any]],
    gaps: list[dict[str, Any]],
    references: set[str],
) -> None:
    seen: set[str] = set()
    total_bytes = 0
    member_count = 0
    try:
        if tarfile.is_tarfile(io.BytesIO(payload)):
            with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as archive:
                members = archive.getmembers()
                if len(members) > MAX_ARCHIVE_MEMBERS:
                    raise DeclaredExposureError("ARCHIVE_MEMBER_COUNT_LIMIT_EXCEEDED")
                for member in members:
                    path = safe_virtual_member_path(member.name)
                    if path in seen:
                        raise DeclaredExposureError("DUPLICATE_ARCHIVE_MEMBER_PATH")
                    seen.add(path)
                    if member.issym() or member.islnk():
                        raise DeclaredExposureError("LINKED_ARCHIVE_MEMBER_FORBIDDEN")
                    if member.isdir():
                        continue
                    if not member.isfile():
                        raise DeclaredExposureError("SPECIAL_ARCHIVE_MEMBER_FORBIDDEN")
                    if member.size > MAX_ARCHIVE_MEMBER_BYTES:
                        gaps.append(
                            {
                                "bytes": member.size,
                                "path": f"{virtual_path}!/{path}",
                                "reason": "ARCHIVE_MEMBER_EXCEEDS_FROZEN_MEMBER_LIMIT",
                            }
                        )
                        continue
                    total_bytes += member.size
                    member_count += 1
                    if total_bytes > MAX_ARCHIVE_TOTAL_MEMBER_BYTES:
                        raise DeclaredExposureError("ARCHIVE_TOTAL_MEMBER_BYTES_LIMIT_EXCEEDED")
                    stream = archive.extractfile(member)
                    if stream is None:
                        raise DeclaredExposureError("ARCHIVE_REGULAR_MEMBER_UNREADABLE")
                    member_payload = stream.read(MAX_ARCHIVE_MEMBER_BYTES + 1)
                    if len(member_payload) != member.size:
                        raise DeclaredExposureError("ARCHIVE_MEMBER_SIZE_MISMATCH")
                    _scan_member_payload(
                        member_payload,
                        f"{virtual_path}!/{path}",
                        depth,
                        pdf_parser,
                        rows,
                        gaps,
                        references,
                    )
            return
        if zipfile.is_zipfile(io.BytesIO(payload)):
            with zipfile.ZipFile(io.BytesIO(payload), mode="r") as archive:
                infos = archive.infolist()
                if len(infos) > MAX_ARCHIVE_MEMBERS:
                    raise DeclaredExposureError("ARCHIVE_MEMBER_COUNT_LIMIT_EXCEEDED")
                for info in infos:
                    path = safe_virtual_member_path(info.filename)
                    if path in seen:
                        raise DeclaredExposureError("DUPLICATE_ARCHIVE_MEMBER_PATH")
                    seen.add(path)
                    if info.is_dir():
                        continue
                    unix_mode = (info.external_attr >> 16) & 0xFFFF
                    if unix_mode and (unix_mode & 0o170000) not in (0, 0o100000):
                        raise DeclaredExposureError("ZIP_NONREGULAR_MEMBER_FORBIDDEN")
                    if info.file_size > MAX_ARCHIVE_MEMBER_BYTES:
                        gaps.append(
                            {
                                "bytes": info.file_size,
                                "path": f"{virtual_path}!/{path}",
                                "reason": "ARCHIVE_MEMBER_EXCEEDS_FROZEN_MEMBER_LIMIT",
                            }
                        )
                        continue
                    total_bytes += info.file_size
                    member_count += 1
                    if total_bytes > MAX_ARCHIVE_TOTAL_MEMBER_BYTES:
                        raise DeclaredExposureError("ARCHIVE_TOTAL_MEMBER_BYTES_LIMIT_EXCEEDED")
                    member_payload = archive.read(info)
                    _scan_member_payload(
                        member_payload,
                        f"{virtual_path}!/{path}",
                        depth,
                        pdf_parser,
                        rows,
                        gaps,
                        references,
                    )
            return
        if virtual_path.lower().endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(payload), mode="rb") as stream:
                member_payload = stream.read(MAX_ARCHIVE_MEMBER_BYTES + 1)
            if len(member_payload) > MAX_ARCHIVE_MEMBER_BYTES:
                raise DeclaredExposureError("GZIP_MEMBER_EXCEEDS_FROZEN_MEMBER_LIMIT")
            inner_name = virtual_path[:-3]
            _scan_member_payload(
                member_payload, f"{virtual_path}!/{PurePosixPath(inner_name).name}", depth,
                pdf_parser, rows, gaps, references
            )
            return
        raise DeclaredExposureError("UNSUPPORTED_ARCHIVE_FORMAT")
    except (tarfile.TarError, zipfile.BadZipFile, gzip.BadGzipFile, OSError, EOFError, DeclaredExposureError) as exc:
        gaps.append(
            {
                "bytes": len(payload),
                "path": virtual_path,
                "reason": f"ARCHIVE_REJECTED:{str(exc)}",
            }
        )


def verify_s0_closure_seed(root: Path) -> dict[str, Any]:
    seed = root / S0_CLOSURE_PATH
    if not _path_is_file(seed):
        raise DeclaredExposureError("S0_CLOSURE_SEED_MISSING")
    payload = _read_path_bytes(seed)
    file_digest = sha256_bytes(payload)
    if file_digest != S0_CLOSURE_FILE_SHA256:
        raise DeclaredExposureError("S0_CLOSURE_SEED_FILE_IDENTITY_MISMATCH")
    try:
        document = json.loads(payload.decode("utf-8", errors="strict"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeclaredExposureError("S0_CLOSURE_SEED_JSON_INVALID") from exc
    if not isinstance(document, dict):
        raise DeclaredExposureError("S0_CLOSURE_SEED_JSON_ROOT_INVALID")
    claimed = document.get("closure_sha256")
    body = dict(document)
    body.pop("closure_sha256", None)
    computed = sha256_bytes(canonical_json_bytes(body))
    if claimed != S0_CLOSURE_INTERNAL_SHA256 or computed != S0_CLOSURE_INTERNAL_SHA256:
        raise DeclaredExposureError("S0_CLOSURE_SEED_INTERNAL_SEAL_MISMATCH")
    return {
        "bytes": len(payload),
        "file_sha256": file_digest,
        "internal_seal_field": "closure_sha256",
        "internal_seal_sha256": computed,
        "path": S0_CLOSURE_PATH.as_posix(),
    }


def scan_s0_dag(root: Path) -> dict[str, Any]:
    started = time.monotonic()
    _progress("s0_dag_scan_started")
    seed = root / S0_CLOSURE_PATH
    seed_identity = verify_s0_closure_seed(root)
    parser = pdf_parser_authority()
    queue: deque[str] = deque([S0_CLOSURE_PATH.as_posix()])
    queued = {S0_CLOSURE_PATH.as_posix()}
    visited: set[str] = set()
    local_rows: list[dict[str, Any]] = []
    member_rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    unresolved_references: set[str] = set()
    total_scanned_bytes = 0

    while queue:
        relative_path = queue.popleft()
        if relative_path in visited:
            continue
        if len(visited) >= MAX_DAG_LOCAL_NODES:
            gaps.append({"path": relative_path, "reason": "S0_DAG_LOCAL_NODE_LIMIT_REACHED"})
            break
        visited.add(relative_path)
        path = root / PurePosixPath(relative_path)
        if not path.is_file() or path.is_symlink():
            unresolved_references.add(relative_path)
            continue
        size = path.stat().st_size
        if size > MAX_DAG_LOCAL_FILE_BYTES:
            gaps.append({"bytes": size, "path": relative_path, "reason": "S0_DAG_LOCAL_FILE_LIMIT_EXCEEDED"})
            continue
        total_scanned_bytes += size
        if total_scanned_bytes > MAX_DAG_TOTAL_SCANNED_BYTES:
            gaps.append({"path": relative_path, "reason": "S0_DAG_TOTAL_SCANNED_BYTES_LIMIT_REACHED"})
            break
        payload = path.read_bytes()
        identity = {"aliases": [], "bytes": len(payload), "path": relative_path, "sha256": sha256_bytes(payload)}
        discovered: set[str] = set()
        if _looks_like_archive(relative_path):
            identity["classification"] = "ARCHIVE_CONTAINER"
            _progress(
                "s0_dag_archive_started",
                bytes=len(payload),
                elapsed_seconds=round(time.monotonic() - started, 3),
                path=relative_path,
                visited_nodes=len(visited),
            )
            _scan_archive_payload(payload, relative_path, 0, parser, member_rows, gaps, discovered)
            _progress(
                "s0_dag_archive_complete",
                elapsed_seconds=round(time.monotonic() - started, 3),
                member_rows=len(member_rows),
                path=relative_path,
            )
        elif relative_path.lower().endswith(".pdf"):
            text, error = parse_pdf_bytes(payload, parser)
            if error:
                identity["classification"] = "PDF_PARSE_GAP"
                gaps.append({**identity, "reason": error})
            else:
                assert text is not None
                aliases, alias_gaps = extract_aliases(text, relative_path + ".txt")
                identity.update({"aliases": aliases, "alias_extraction_gaps": alias_gaps, "classification": "PDF_PARSED_TEXT"})
                discovered.update(extract_repository_references(text, relative_path + ".txt"))
        else:
            text_ok, text = is_strict_text(payload)
            if text_ok and text is not None:
                aliases, alias_gaps = extract_aliases(text, relative_path)
                identity.update({"aliases": aliases, "alias_extraction_gaps": alias_gaps, "classification": "STRICT_UTF8_TEXT"})
                discovered.update(extract_repository_references(text, relative_path))
            else:
                identity["classification"] = "BINARY_NONARCHIVE_NONPDF"
        local_rows.append(identity)
        if len(local_rows) % 25 == 0:
            _progress(
                "s0_dag_local_progress",
                elapsed_seconds=round(time.monotonic() - started, 3),
                local_rows=len(local_rows),
                member_rows=len(member_rows),
                queued=len(queue),
            )
        for reference in sorted(discovered, key=utf8_key):
            if _is_output_path(reference):
                continue
            candidate = root / PurePosixPath(reference)
            if candidate.is_file() and not candidate.is_symlink():
                if reference not in queued:
                    queue.append(reference)
                    queued.add(reference)
            else:
                unresolved_references.add(reference)

    local_rows.sort(key=lambda row: utf8_key(str(row["path"])))
    member_rows.sort(key=lambda row: utf8_key(str(row["path"])))
    gaps.sort(key=lambda row: (utf8_key(str(row.get("path", ""))), utf8_key(str(row["reason"]))))
    result = {
        "seed_identity": seed_identity,
        "seed": {
            "path": S0_CLOSURE_PATH.as_posix(),
            "file_sha256": S0_CLOSURE_FILE_SHA256,
            "internal_closure_sha256": S0_CLOSURE_INTERNAL_SHA256,
        },
        "pdf_parser": parser,
        "limits": {
            "max_archive_depth": MAX_ARCHIVE_DEPTH,
            "max_archive_member_bytes": MAX_ARCHIVE_MEMBER_BYTES,
            "max_archive_members": MAX_ARCHIVE_MEMBERS,
            "max_archive_total_member_bytes": MAX_ARCHIVE_TOTAL_MEMBER_BYTES,
            "max_dag_local_file_bytes": MAX_DAG_LOCAL_FILE_BYTES,
            "max_dag_local_nodes": MAX_DAG_LOCAL_NODES,
            "max_dag_total_scanned_bytes": MAX_DAG_TOTAL_SCANNED_BYTES,
        },
        "local_nodes": local_rows,
        "local_nodes_digest": canonical_rows_digest(
            local_rows,
            "rtdl.goal5793.x1.declared_exposure.s0_dag_local_nodes",
            "reachable_local_nodes_sorted_by_path_utf8",
        ),
        "archive_members": member_rows,
        "archive_members_digest": canonical_rows_digest(
            member_rows,
            "rtdl.goal5793.x1.declared_exposure.s0_dag_archive_members",
            "safe_archive_member_rows_sorted_by_virtual_path_utf8",
        ),
        "coverage_gaps": gaps,
        "unresolved_references": sorted(unresolved_references, key=utf8_key),
        "counts": {
            "local_nodes": len(local_rows),
            "archive_member_rows": len(member_rows),
            "coverage_gaps": len(gaps),
            "unresolved_references": len(unresolved_references),
            "total_local_bytes_scanned": sum(int(row["bytes"]) for row in local_rows),
            "total_archive_member_bytes_scanned": sum(int(row["bytes"]) for row in member_rows),
        },
        "complete_under_frozen_limits": not gaps and not unresolved_references,
    }
    _progress(
        "s0_dag_scan_complete",
        coverage_gaps=len(gaps),
        elapsed_seconds=round(time.monotonic() - started, 3),
        local_nodes=len(local_rows),
        member_rows=len(member_rows),
        unresolved_references=len(unresolved_references),
    )
    return result


def _phase_limits() -> dict[str, int]:
    return {
        "max_archive_depth": MAX_ARCHIVE_DEPTH,
        "max_archive_member_bytes": MAX_ARCHIVE_MEMBER_BYTES,
        "max_archive_members": MAX_ARCHIVE_MEMBERS,
        "max_archive_total_member_bytes": MAX_ARCHIVE_TOTAL_MEMBER_BYTES,
        "max_dag_local_file_bytes": MAX_DAG_LOCAL_FILE_BYTES,
        "max_dag_local_nodes": MAX_DAG_LOCAL_NODES,
        "max_dag_total_scanned_bytes": MAX_DAG_TOTAL_SCANNED_BYTES,
        "max_git_text_blob_bytes": MAX_GIT_TEXT_BLOB_BYTES,
    }


def _scanner_file_identity() -> dict[str, Any]:
    path = Path(__file__).resolve()
    return {
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def build_phase_cache(root: Path, phase: str) -> dict[str, Any]:
    root = root.resolve()
    if phase == "git":
        data = scan_git_history(root)
    elif phase == "s0_dag":
        data = scan_s0_dag(root)
    else:
        raise DeclaredExposureError("UNKNOWN_PHASE_CACHE_KIND")
    cache: dict[str, Any] = {
        "schema": PHASE_CACHE_SCHEMA,
        "phase": phase,
        "scanner_file_identity": _scanner_file_identity(),
        "frozen_limits": _phase_limits(),
        "data": data,
        "phase_cache_sha256": "",
    }
    cache["phase_cache_sha256"] = seal_document(
        cache,
        seal_field="phase_cache_sha256",
        domain="rtdl.goal5793.x1.declared_exposure.phase_cache",
        version=1,
    )
    return cache


def _read_phase_cache(path: Path, expected_phase: str) -> dict[str, Any]:
    try:
        cache = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeclaredExposureError("PHASE_CACHE_UNREADABLE") from exc
    if not isinstance(cache, dict) or set(cache) != {
        "schema", "phase", "scanner_file_identity", "frozen_limits", "data",
        "phase_cache_sha256",
    }:
        raise DeclaredExposureError("PHASE_CACHE_KEYSET_MISMATCH")
    if cache.get("schema") != PHASE_CACHE_SCHEMA or cache.get("phase") != expected_phase:
        raise DeclaredExposureError("PHASE_CACHE_SCHEMA_OR_KIND_MISMATCH")
    claimed = cache.get("phase_cache_sha256")
    expected = seal_document(
        cache,
        seal_field="phase_cache_sha256",
        domain="rtdl.goal5793.x1.declared_exposure.phase_cache",
        version=1,
    )
    if claimed != expected:
        raise DeclaredExposureError("PHASE_CACHE_SEAL_MISMATCH")
    if cache.get("scanner_file_identity") != _scanner_file_identity():
        raise DeclaredExposureError("PHASE_CACHE_SCANNER_IDENTITY_MISMATCH")
    if cache.get("frozen_limits") != _phase_limits():
        raise DeclaredExposureError("PHASE_CACHE_LIMITS_MISMATCH")
    if not isinstance(cache.get("data"), dict):
        raise DeclaredExposureError("PHASE_CACHE_DATA_INVALID")
    return cache


def _current_git_inventory_identity(root: Path) -> dict[str, Any]:
    refs = git_refs(root)
    object_lines = run_git(root, ["rev-list", "--objects", "--all"]).splitlines()
    object_ids = sorted(
        {line.split(b" ", 1)[0].decode("ascii", errors="strict") for line in object_lines if line}
    )
    inventory = git_batch_check(root, object_ids)
    rows = [
        {"bytes": inventory[oid][1], "object_id": oid, "type": inventory[oid][0]}
        for oid in object_ids
    ]
    return {
        "refs": refs,
        "reachable_object_inventory_digest": canonical_rows_digest(
            rows,
            "rtdl.goal5793.x1.declared_exposure.git_object_inventory",
            "object_id_type_bytes_sorted_by_object_id",
        ),
    }


def load_validated_phase_cache(
    root: Path,
    path: Path,
    phase: str,
    trusted_file_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not re.fullmatch(r"[0-9a-f]{64}", trusted_file_sha256):
        raise DeclaredExposureError("PHASE_CACHE_TRUSTED_FILE_SHA256_INVALID")
    actual_file_sha256 = file_sha256(path)
    if actual_file_sha256 != trusted_file_sha256:
        raise DeclaredExposureError("PHASE_CACHE_OUT_OF_BAND_FILE_IDENTITY_MISMATCH")
    cache = _read_phase_cache(path, phase)
    data = cache["data"]
    if phase == "git":
        current = _current_git_inventory_identity(root)
        if data.get("refs") != current["refs"]:
            raise DeclaredExposureError("GIT_PHASE_CACHE_REFS_DRIFT")
        if data.get("reachable_object_inventory_digest") \
                != current["reachable_object_inventory_digest"]:
            raise DeclaredExposureError("GIT_PHASE_CACHE_OBJECT_INVENTORY_DRIFT")
    elif phase == "s0_dag":
        if data.get("seed_identity") != verify_s0_closure_seed(root):
            raise DeclaredExposureError("S0_PHASE_CACHE_SEED_DRIFT")
        if data.get("pdf_parser") != pdf_parser_authority():
            raise DeclaredExposureError("S0_PHASE_CACHE_PDF_PARSER_DRIFT")
        if data.get("limits") != {
            key: value for key, value in _phase_limits().items()
            if key != "max_git_text_blob_bytes"
        }:
            raise DeclaredExposureError("S0_PHASE_CACHE_LIMITS_DRIFT")
        for row in data.get("local_nodes", []):
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                raise DeclaredExposureError("S0_PHASE_CACHE_LOCAL_ROW_INVALID")
            local = root / PurePosixPath(row["path"])
            if not local.is_file() or local.is_symlink() \
                    or file_sha256(local) != row.get("sha256"):
                raise DeclaredExposureError("S0_PHASE_CACHE_LOCAL_NODE_DRIFT")
    else:
        raise DeclaredExposureError("UNKNOWN_PHASE_CACHE_KIND")
    _progress(
        "phase_cache_validated",
        path=path.as_posix(),
        phase=phase,
        phase_cache_sha256=cache["phase_cache_sha256"],
    )
    return data, {
        "phase": phase,
        "bytes": path.stat().st_size,
        "file_sha256": actual_file_sha256,
        "phase_cache_sha256": cache["phase_cache_sha256"],
        "trust_source": "OUT_OF_BAND_EXACT_FILE_SHA256_REQUIRED_BY_FINAL_ASSEMBLY",
    }


def load_survey_component(root: Path) -> dict[str, Any]:
    path = root / SURVEY_COMPONENT_PATH
    if not path.is_file() or file_sha256(path) != SURVEY_COMPONENT_SHA256:
        raise DeclaredExposureError("SURVEY_COMPONENT_IDENTITY_MISMATCH")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "rtdl.goal5793.x1.survey_exposure_registry.v2":
        raise DeclaredExposureError("SURVEY_COMPONENT_SCHEMA_MISMATCH")
    counts = payload.get("counts", {})
    if counts.get("bibliography_entries") != 186 or counts.get("selection_eligible_entries") != 0:
        raise DeclaredExposureError("SURVEY_COMPONENT_COUNT_MISMATCH")
    entries = payload.get("bibliography_entries")
    if not isinstance(entries, list) or len(entries) != 186:
        raise DeclaredExposureError("SURVEY_COMPONENT_ROWS_MISMATCH")
    if any(row.get("selection_eligible") is not False for row in entries):
        raise DeclaredExposureError("SURVEY_COMPONENT_ELIGIBILITY_MISMATCH")
    return {
        "authority": {
            "bytes": path.stat().st_size,
            "file_sha256": SURVEY_COMPONENT_SHA256,
            "internal_registry_sha256": payload["registry_sha256"],
            "path": SURVEY_COMPONENT_PATH.as_posix(),
        },
        "entries": entries,
        "counts": {
            "bibliography_entries": 186,
            "old_goal5753_crosslinked_candidate_rows": counts[
                "old_goal5753_crosslinked_candidate_rows"
            ],
            "selection_eligible_entries": 0,
        },
        "scope_boundary": payload["scope_boundary"],
    }


def load_owner_disclosure(root: Path) -> dict[str, Any]:
    path = root / OWNER_DISCLOSURE_PATH
    if not path.exists():
        return {
            "status": "BLOCKING_GAP__OWNER_OFF_REPOSITORY_DISCLOSURE_NOT_PROVIDED__NOT_ASSUMED_EMPTY",
            "expected_path": OWNER_DISCLOSURE_PATH.as_posix(),
            "provided": False,
            "disclosures": [],
            "aliases": [],
            "complete_or_empty_claimed": False,
        }
    if not path.is_file() or path.is_symlink():
        raise DeclaredExposureError("OWNER_DISCLOSURE_PATH_NOT_REGULAR_FILE")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "rtdl.goal5793.x1.owner_off_repository_exposure_disclosure.v1":
        raise DeclaredExposureError("OWNER_DISCLOSURE_SCHEMA_MISMATCH")
    disclosures = payload.get("disclosures")
    if not isinstance(disclosures, list):
        raise DeclaredExposureError("OWNER_DISCLOSURE_ROWS_MISSING")
    aliases: set[str] = set()
    for row in disclosures:
        if not isinstance(row, dict):
            raise DeclaredExposureError("OWNER_DISCLOSURE_ROW_INVALID")
        text = json.dumps(row, sort_keys=True, ensure_ascii=False)
        extracted, _ = extract_aliases(text, "owner_disclosure.json")
        aliases.update(extracted)
        if all(isinstance(row.get(key), str) for key in ("title", "author", "year")):
            fallback = _fallback_alias(row["title"], row["author"], row["year"])
            if fallback:
                aliases.add(fallback)
    return {
        "status": "PROVIDED__EXTERNAL_REVIEW_STILL_REQUIRED",
        "provided": True,
        "authority": {
            "bytes": path.stat().st_size,
            "file_sha256": file_sha256(path),
            "path": OWNER_DISCLOSURE_PATH.as_posix(),
        },
        "disclosures": disclosures,
        "aliases": sorted(aliases, key=utf8_key),
        "complete_or_empty_claimed": bool(payload.get("owner_attests_complete_for_declared_scope")),
    }


def build_alias_index(
    workspace: Mapping[str, Any],
    git_history: Mapping[str, Any],
    s0_dag: Mapping[str, Any],
    survey: Mapping[str, Any],
    owner: Mapping[str, Any],
) -> list[dict[str, Any]]:
    index: dict[str, set[str]] = {}

    def add(alias: str, source: str) -> None:
        index.setdefault(alias, set()).add(source)

    for row in workspace["strict_utf8_text_rows"]:
        source = f"successor_workspace:{row['path']}:{row['sha256']}"
        for alias in row["aliases"]:
            add(str(alias), source)
    for row in git_history["strict_utf8_regular_text_blobs"]:
        source = f"git_blob:{row['git_blob_id']}:{row['sha256']}"
        for alias in row["aliases"]:
            add(str(alias), source)
    for row in s0_dag["local_nodes"]:
        source = f"s0_dag_local:{row['path']}:{row['sha256']}"
        for alias in row["aliases"]:
            add(str(alias), source)
    for row in s0_dag["archive_members"]:
        source = f"s0_dag_member:{row['path']}:{row['sha256']}"
        for alias in row["aliases"]:
            add(str(alias), source)
    for row in survey["entries"]:
        source = f"survey_bib:{row['node_id']}"
        for alias in row["aliases"]:
            add(str(alias["value"]), source)
    for alias in owner["aliases"]:
        add(str(alias), "owner_off_repository_disclosure")

    rows = [
        {
            "alias": alias,
            "matched_query_row_selection_eligible": False,
            "source_count": len(sources),
            "sources": sorted(sources, key=utf8_key),
        }
        for alias, sources in index.items()
    ]
    rows.sort(key=lambda row: utf8_key(str(row["alias"])))
    return rows


def _verify_final_identities(
    root: Path,
    git_history: Mapping[str, Any],
    s0_dag: Mapping[str, Any],
) -> None:
    if git_refs(root) != git_history["refs"]:
        raise DeclaredExposureError("GIT_REFS_CHANGED_BEFORE_AUTHORITY_SEAL")
    for row in s0_dag["local_nodes"]:
        path = root / PurePosixPath(str(row["path"]))
        if not path.is_file() or file_sha256(path) != row["sha256"]:
            raise DeclaredExposureError("S0_DAG_LOCAL_NODE_CHANGED_BEFORE_AUTHORITY_SEAL")
    survey_path = root / SURVEY_COMPONENT_PATH
    if file_sha256(survey_path) != SURVEY_COMPONENT_SHA256:
        raise DeclaredExposureError("SURVEY_COMPONENT_CHANGED_BEFORE_AUTHORITY_SEAL")


def build_authority(
    root: Path,
    *,
    git_phase_cache: Path | None = None,
    git_phase_cache_sha256: str | None = None,
    s0_phase_cache: Path | None = None,
    s0_phase_cache_sha256: str | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    if not (root / ".git").exists():
        raise DeclaredExposureError("ROOT_IS_NOT_GIT_WORKTREE")

    # Scan immutable/reconstructable history first and the mutable successor
    # workspace last, minimizing the seal window for current bytes.
    if (git_phase_cache is None) != (git_phase_cache_sha256 is None):
        raise DeclaredExposureError("GIT_PHASE_CACHE_AND_TRUSTED_SHA_REQUIRED_TOGETHER")
    if (s0_phase_cache is None) != (s0_phase_cache_sha256 is None):
        raise DeclaredExposureError("S0_PHASE_CACHE_AND_TRUSTED_SHA_REQUIRED_TOGETHER")
    phase_cache_inputs: list[dict[str, Any]] = []
    if git_phase_cache is not None:
        assert git_phase_cache_sha256 is not None
        git_history, git_cache_identity = load_validated_phase_cache(
            root, git_phase_cache, "git", git_phase_cache_sha256
        )
        phase_cache_inputs.append(git_cache_identity)
    else:
        git_history = scan_git_history(root)
    if s0_phase_cache is not None:
        assert s0_phase_cache_sha256 is not None
        s0_dag, s0_cache_identity = load_validated_phase_cache(
            root, s0_phase_cache, "s0_dag", s0_phase_cache_sha256
        )
        phase_cache_inputs.append(s0_cache_identity)
    else:
        s0_dag = scan_s0_dag(root)
    survey = load_survey_component(root)
    owner = load_owner_disclosure(root)
    _progress("workspace_scan_started")
    workspace = scan_successor_workspace(root)
    _progress(
        "workspace_scan_complete",
        path_enumeration_count=workspace["path_enumeration_count"],
        strict_utf8_text_rows=len(workspace["strict_utf8_text_rows"]),
    )
    _progress("alias_index_build_started")
    alias_index = build_alias_index(workspace, git_history, s0_dag, survey, owner)
    _progress("alias_index_build_complete", aliases=len(alias_index))
    _verify_final_identities(root, git_history, s0_dag)

    blocking_gaps: list[dict[str, Any]] = [
        {
            "id": "MISSING_EXACT_S0_FULL_REPOSITORY_UNTRACKED_TEXT_WORKSPACE_SNAPSHOT",
            "fact": "S0 froze 326 product/build rows but no complete all-repository regular-text path-and-byte manifest; today's successor tree contains post-S0/X1 changes and cannot be backdated",
            "outcome": "X1_NOT_CLOSABLE__X2_BLOCKED",
            "repair_boundary": "requires externally reviewed restart-style pre-X2 freeze; never retroactive reconstruction",
        }
    ]
    if not owner["provided"]:
        blocking_gaps.append(
            {
                "id": "OWNER_OFF_REPOSITORY_EXPOSURE_DISCLOSURE_NOT_PROVIDED",
                "fact": "absence is not an empty disclosure and cannot establish complete mental exposure",
                "outcome": "X1_NOT_CLOSABLE__X2_BLOCKED",
                "repair_boundary": "owner append-only disclosure plus external review",
            }
        )
    if workspace["limit_gaps"] or workspace["excluded_roots_or_directories"]:
        blocking_gaps.append(
            {
                "id": "CURRENT_SUCCESSOR_WORKSPACE_HAS_DECLARED_EXCLUSIONS_OR_LIMIT_GAPS",
                "excluded_directory_count": len(workspace["excluded_roots_or_directories"]),
                "limit_gap_count": len(workspace["limit_gaps"]),
                "outcome": "SUCCESSOR_OBSERVATION_ONLY__NEVER_S0_SNAPSHOT_AUTHORITY",
            }
        )
    if not git_history["complete_under_frozen_blob_size_limit"]:
        blocking_gaps.append(
            {
                "id": "REACHABLE_GIT_HISTORY_HAS_LIMIT_OR_TREE_MODE_GAPS",
                "oversize_blob_count": git_history["counts"]["oversize_regular_blob_gaps"],
                "unknown_tree_entry_mode_count": git_history["counts"]["unknown_tree_entry_modes"],
                "outcome": "X1_NOT_CLOSABLE__X2_BLOCKED",
            }
        )
    if not s0_dag["complete_under_frozen_limits"]:
        blocking_gaps.append(
            {
                "id": "S0_DAG_HAS_UNRESOLVED_REFERENCES_OR_ARCHIVE_LIMIT_PARSER_GAPS",
                "coverage_gap_count": s0_dag["counts"]["coverage_gaps"],
                "unresolved_reference_count": s0_dag["counts"]["unresolved_references"],
                "outcome": "X1_NOT_CLOSABLE__X2_BLOCKED",
            }
        )

    authority: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5793,
        "stage": "X1_DECLARED_EXPOSURE_SUCCESSOR_SCAN",
        "status": "X1_NOT_CLOSABLE__X2_BLOCKED__MISSING_HISTORICAL_S0_WORKSPACE_SNAPSHOT_AND_OWNER_DISCLOSURE",
        "canonicalization": {"name": CANONICALIZATION_NAME},
        "scope_definition": {
            "current_workspace_is_historical_s0_snapshot": False,
            "current_workspace_classification": "post-S0/X1 successor observation with contamination and explicit exclusions",
            "git_history_scope": "all objects reachable from every current local ref returned by git rev-list --all; exact refs frozen before/after",
            "s0_dag_scope": "recursive local references reachable from exact S0 postreview closure seed under frozen archive/PDF/byte/depth limits",
            "survey_scope": "all 186 entries in exact pinned survey source bibliography component",
            "goal5753_scope": "all 35 rows crosslinked through survey component",
            "owner_disclosure_absence_means_empty": False,
            "complete_author_mental_exposure_claimed": False,
            "complete_literature_universe_claimed": False,
        },
        "blocking_gaps": blocking_gaps,
        "phase_cache_inputs": sorted(phase_cache_inputs, key=lambda row: row["phase"]),
        "successor_workspace_observation": workspace,
        "reachable_git_history": git_history,
        "s0_evidence_dag": s0_dag,
        "survey_and_goal5753_component": survey,
        "owner_off_repository_disclosure": owner,
        "alias_index": alias_index,
        "alias_index_digest": canonical_rows_digest(
            alias_index,
            "rtdl.goal5793.x1.declared_exposure.alias_index",
            "all_alias_rows_sorted_by_alias_utf8_with_all_source_crosslinks",
        ),
        "counts": {
            "blocking_gaps": len(blocking_gaps),
            "global_aliases": len(alias_index),
            "survey_bibliography_entries": 186,
            "goal5753_crosslinked_rows": 35,
            "selection_eligible_registry_rows": 0,
        },
        "selection_policy": {
            "any_registry_alias_match_selection_eligible": False,
            "coverage_gap_allows_unseen_blind_or_held_out_claim": False,
            "absence_from_registry_means_only_not_matched_to_declared_registry": True,
            "later_discovered_preexisting_exposure": "PROTOCOL_CONTAMINATION__TERMINATE_SINGLE_EXPANSION__NO_REPLACEMENT_OR_REUSE",
        },
        "authorization": {
            "x1_complete": False,
            "x1_closure_authorized": False,
            "x2_implementation_or_live_search_authorized": False,
            "network_or_live_provider_call_count": 0,
            "entropy_anchor_or_draw_count": 0,
            "candidate_selection_count": 0,
            "candidate_implementation_or_execution_count": 0,
            "src_or_native_write_count": 0,
            "gpu_home_pod_or_ssh_count": 0,
            "registered_or_performance_timing_count": 0,
            "external_reviewer_contact_count": 0,
            "public_release_publication_or_submission_authorized": False,
        },
    }
    authority["authority_sha256"] = seal_document(
        authority,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x1.declared_exposure.successor_authority",
        version=1,
    )
    return authority


def serialized_document(document: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def write_create_only(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def summary(document: Mapping[str, Any]) -> dict[str, Any]:
    workspace = document["successor_workspace_observation"]
    git_history = document["reachable_git_history"]
    s0_dag = document["s0_evidence_dag"]

    def reason_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
        return dict(sorted(Counter(str(row["reason"]) for row in rows).items()))

    def rows_sha256(rows: Any, label: str) -> str:
        return str(
            canonical_digest(
                rows,
                domain="rtdl.goal5793.x1.declared_exposure.dry_summary",
                version=1,
                projection=label,
            )["sha256"]
        )

    return {
        "schema": document["schema"],
        "status": document["status"],
        "authority_sha256": document["authority_sha256"],
        "blocking_gap_count": document["counts"]["blocking_gaps"],
        "blocking_gap_rows": document["blocking_gaps"],
        "global_aliases": document["counts"]["global_aliases"],
        "workspace": {
            "classification": workspace["classification"],
            "path_enumeration_count": workspace["path_enumeration_count"],
            "strict_utf8_text_rows": len(workspace["strict_utf8_text_rows"]),
            "non_strict_text_rows": len(workspace["non_strict_text_rows"]),
            "excluded_path_count": len(workspace["excluded_roots_or_directories"]),
            "excluded_path_reason_counts": reason_counts(
                workspace["excluded_roots_or_directories"]
            ),
            "excluded_paths_digest_sha256": rows_sha256(
                workspace["excluded_roots_or_directories"], "workspace_excluded_paths"
            ),
            "limit_gap_count": len(workspace["limit_gaps"]),
            "limit_gap_reason_counts": reason_counts(workspace["limit_gaps"]),
            "limit_gaps_digest_sha256": rows_sha256(
                workspace["limit_gaps"], "workspace_limit_gaps"
            ),
            "followed_reparse_mount_count": len(workspace["followed_reparse_mounts"]),
        },
        "git_history": {
            "counts": git_history["counts"],
            "oversize_gap_rows": git_history["oversize_regular_blob_gaps"],
        },
        "s0_dag": {
            "counts": s0_dag["counts"],
            "seed_identity": s0_dag["seed_identity"],
            "coverage_gap_reason_counts": reason_counts(s0_dag["coverage_gaps"]),
            "coverage_gaps_digest_sha256": rows_sha256(
                s0_dag["coverage_gaps"], "s0_dag_coverage_gaps"
            ),
            "unresolved_references_digest_sha256": rows_sha256(
                s0_dag["unresolved_references"], "s0_dag_unresolved_references"
            ),
        },
        "survey": document["survey_and_goal5753_component"]["counts"],
        "owner_disclosure": {
            "provided": document["owner_off_repository_disclosure"]["provided"],
            "complete_or_empty_claimed": document["owner_off_repository_disclosure"][
                "complete_or_empty_claimed"
            ],
            "status": document["owner_off_repository_disclosure"]["status"],
        },
        "selection_eligible_registry_rows": document["counts"][
            "selection_eligible_registry_rows"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--phase", choices=("git", "s0_dag"))
    parser.add_argument("--phase-output", type=Path)
    parser.add_argument("--git-phase-cache", type=Path)
    parser.add_argument("--git-phase-cache-sha256")
    parser.add_argument("--s0-phase-cache", type=Path)
    parser.add_argument("--s0-phase-cache-sha256")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.phase is not None:
        if args.write_create_only:
            raise SystemExit("--write-create-only is for the final authority, not a phase cache")
        if args.phase_output is None:
            raise SystemExit("--phase-output is required with --phase")
        cache = build_phase_cache(root, args.phase)
        output = args.phase_output if args.phase_output.is_absolute() \
            else root / args.phase_output
        write_create_only(output, serialized_document(cache))
        print(json.dumps({
            "schema": cache["schema"],
            "phase": cache["phase"],
            "phase_cache_sha256": cache["phase_cache_sha256"],
            "serialized_bytes": output.stat().st_size,
            "serialized_sha256": file_sha256(output),
        }, sort_keys=True))
        return
    if args.phase_output is not None:
        raise SystemExit("--phase-output requires --phase")
    git_cache = None if args.git_phase_cache is None else (
        args.git_phase_cache if args.git_phase_cache.is_absolute()
        else root / args.git_phase_cache
    )
    s0_cache = None if args.s0_phase_cache is None else (
        args.s0_phase_cache if args.s0_phase_cache.is_absolute()
        else root / args.s0_phase_cache
    )
    document = build_authority(
        root,
        git_phase_cache=git_cache,
        git_phase_cache_sha256=args.git_phase_cache_sha256,
        s0_phase_cache=s0_cache,
        s0_phase_cache_sha256=args.s0_phase_cache_sha256,
    )
    payload = serialized_document(document)
    result = summary(document)
    result["serialized_bytes"] = len(payload)
    result["serialized_sha256"] = sha256_bytes(payload)
    if args.write_create_only:
        output = args.output if args.output.is_absolute() else root / args.output
        write_create_only(output, payload)
        result["output"] = args.output.as_posix()
    else:
        result["dry_run_no_authority_written"] = True
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
