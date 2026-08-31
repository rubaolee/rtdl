#!/usr/bin/env python3
"""Build the frozen-survey component of Goal5793's X1 exposure registry.

This is deliberately an offline, conservative registry builder.  It reads the
exact Goal5753 survey source tar without extracting it, inventories every safe
member, parses every BibTeX work in ``sample.bib``, and makes every such work
permanently selection-ineligible.  It does not claim that the survey
bibliography is the complete literature or the complete author's mental
exposure, and it preserves every coverage gap explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

try:
    from scripts.goal5793_x1_canonical import (
        CANONICALIZATION_NAME,
        canonical_digest,
        seal_document,
        sha256_bytes,
    )
except ModuleNotFoundError:  # direct ``py scripts/...`` execution
    from goal5793_x1_canonical import (  # type: ignore[no-redef]
        CANONICALIZATION_NAME,
        canonical_digest,
        seal_document,
        sha256_bytes,
    )


SCHEMA = "rtdl.goal5793.x1.survey_exposure_registry.v2"
SURVEY_ARCHIVE_SHA256 = "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857"
SURVEY_ARCHIVE_BYTES = 752_766
SAMPLE_BIB_SHA256 = "9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a"
GOAL5753_UNIVERSE_SHA256 = "fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05"

DEFAULT_ARCHIVE = Path(
    "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar"
)
DEFAULT_GOAL5753_UNIVERSE = Path(
    "history/internal_docs/goal5753_held_out_candidate_universe_20260811.json"
)
DEFAULT_OUTPUT = Path(
    "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"
)
REJECTED_CREATE_ONLY_V1 = {
    "bytes": 475_785,
    "file_sha256": "4e0c4f9458d7c17102ee3dcc53a32b8d5bf456798cc51a113190ddb3b2dd614b",
    "path": "history/internal_docs/goal5793_x1_project_exposure_registry_20260822.json",
    "reason": "NONCONTROLLING_PATH_SPELLING_DEPENDENT_PROVENANCE_FIELD__SCIENTIFIC_ROWS_PRESERVED__NEVER_OVERWRITTEN",
}

MAX_ARCHIVE_MEMBERS = 1_024
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_TOTAL_REGULAR_BYTES = 128 * 1024 * 1024
TEXT_SUFFIXES = {
    ".bib",
    ".bbl",
    ".cls",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".sty",
    ".tex",
    ".txt",
}
COMPONENT_EDGE_ALIAS_KINDS = ("doi", "arxiv", "openalex")


class RegistryInputError(ValueError):
    """A stable fail-closed input error."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def _safe_member_path(name: str) -> str:
    if not name or "\\" in name or "\x00" in name:
        raise RegistryInputError("UNSAFE_ARCHIVE_MEMBER_PATH")
    if re.match(r"^[A-Za-z]:", name):
        raise RegistryInputError("UNSAFE_ARCHIVE_MEMBER_PATH")
    path = PurePosixPath(name)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise RegistryInputError("UNSAFE_ARCHIVE_MEMBER_PATH")
    normalized = path.as_posix()
    if normalized != name.rstrip("/"):
        raise RegistryInputError("NONCANONICAL_ARCHIVE_MEMBER_PATH")
    return normalized


def read_safe_tar(archive_path: Path) -> dict[str, Any]:
    """Read a bounded tar without filesystem extraction."""

    if not archive_path.is_file():
        raise RegistryInputError("PINNED_SURVEY_ARCHIVE_MISSING")
    archive_bytes = archive_path.stat().st_size
    archive_sha = file_sha256(archive_path)
    if archive_bytes != SURVEY_ARCHIVE_BYTES:
        raise RegistryInputError("PINNED_SURVEY_ARCHIVE_BYTE_COUNT_MISMATCH")
    if archive_sha != SURVEY_ARCHIVE_SHA256:
        raise RegistryInputError("PINNED_SURVEY_ARCHIVE_SHA256_MISMATCH")

    records: list[dict[str, Any]] = []
    contents: dict[str, bytes] = {}
    seen_paths: set[str] = set()
    total_regular_bytes = 0
    with tarfile.open(archive_path, mode="r:*") as archive:
        members = archive.getmembers()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            raise RegistryInputError("ARCHIVE_MEMBER_COUNT_LIMIT_EXCEEDED")
        for ordinal, member in enumerate(members):
            path = _safe_member_path(member.name)
            if path in seen_paths:
                raise RegistryInputError("DUPLICATE_ARCHIVE_MEMBER_PATH")
            seen_paths.add(path)
            if member.issym() or member.islnk():
                raise RegistryInputError("LINKED_ARCHIVE_MEMBER_FORBIDDEN")
            if not (member.isdir() or member.isfile()):
                raise RegistryInputError("SPECIAL_ARCHIVE_MEMBER_FORBIDDEN")
            if member.isdir():
                records.append(
                    {
                        "archive_ordinal": ordinal,
                        "bytes": 0,
                        "path": path,
                        "sha256": None,
                        "type": "directory",
                    }
                )
                continue
            if member.size < 0 or member.size > MAX_MEMBER_BYTES:
                raise RegistryInputError("ARCHIVE_MEMBER_BYTE_LIMIT_EXCEEDED")
            total_regular_bytes += member.size
            if total_regular_bytes > MAX_TOTAL_REGULAR_BYTES:
                raise RegistryInputError("ARCHIVE_TOTAL_BYTE_LIMIT_EXCEEDED")
            stream = archive.extractfile(member)
            if stream is None:
                raise RegistryInputError("REGULAR_ARCHIVE_MEMBER_UNREADABLE")
            payload = stream.read(MAX_MEMBER_BYTES + 1)
            if len(payload) != member.size:
                raise RegistryInputError("ARCHIVE_MEMBER_DECLARED_SIZE_MISMATCH")
            contents[path] = payload
            records.append(
                {
                    "archive_ordinal": ordinal,
                    "bytes": len(payload),
                    "path": path,
                    "sha256": sha256_bytes(payload),
                    "type": "regular",
                }
            )

    records.sort(key=lambda row: _utf8_key(str(row["path"])))
    return {
        "archive": {
            "bytes": archive_bytes,
            "path_role": "caller_supplied_exact_pinned_archive",
            "sha256": archive_sha,
        },
        "member_manifest": records,
        "contents": contents,
    }


def _find_balanced_entry_end(text: str, opening: int, opener: str) -> int:
    closer = "}" if opener == "{" else ")"
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return index + 1
    raise RegistryInputError("UNTERMINATED_BIBTEX_ENTRY")


def _split_header(body: str) -> tuple[str, str]:
    depth = 0
    quoted = False
    escaped = False
    for index, char in enumerate(body):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
        elif not quoted and char == "{":
            depth += 1
        elif not quoted and char == "}":
            depth -= 1
        elif not quoted and depth == 0 and char == ",":
            return body[:index].strip(), body[index + 1 :]
    raise RegistryInputError("BIBTEX_ENTRY_MISSING_KEY_SEPARATOR")


def _parse_braced_value(text: str, start: int) -> tuple[str, int]:
    depth = 0
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
    raise RegistryInputError("UNTERMINATED_BIBTEX_FIELD_BRACE")


def _parse_quoted_value(text: str, start: int) -> tuple[str, int]:
    escaped = False
    brace_depth = 0
    for index in range(start + 1, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        elif char == '"' and brace_depth == 0:
            return text[start + 1 : index], index + 1
    raise RegistryInputError("UNTERMINATED_BIBTEX_FIELD_QUOTE")


def _parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0
    while index < len(body):
        while index < len(body) and (body[index].isspace() or body[index] == ","):
            index += 1
        if index >= len(body):
            break
        name_match = re.match(r"[A-Za-z][A-Za-z0-9_:-]*", body[index:])
        if name_match is None:
            raise RegistryInputError("UNPARSEABLE_BIBTEX_FIELD_NAME")
        name = name_match.group(0).lower()
        index += len(name_match.group(0))
        while index < len(body) and body[index].isspace():
            index += 1
        if index >= len(body) or body[index] != "=":
            raise RegistryInputError("BIBTEX_FIELD_MISSING_EQUALS")
        index += 1
        parts: list[str] = []
        while True:
            while index < len(body) and body[index].isspace():
                index += 1
            if index >= len(body):
                raise RegistryInputError("BIBTEX_FIELD_MISSING_VALUE")
            if body[index] == "{":
                part, index = _parse_braced_value(body, index)
            elif body[index] == '"':
                part, index = _parse_quoted_value(body, index)
            else:
                end = index
                while end < len(body) and body[end] not in ",#":
                    end += 1
                part = body[index:end].strip()
                index = end
                if not part:
                    raise RegistryInputError("EMPTY_BIBTEX_BARE_VALUE")
            parts.append(part)
            while index < len(body) and body[index].isspace():
                index += 1
            if index < len(body) and body[index] == "#":
                index += 1
                continue
            break
        if name in fields:
            raise RegistryInputError("DUPLICATE_BIBTEX_FIELD")
        fields[name] = "".join(parts)
        while index < len(body) and body[index].isspace():
            index += 1
        if index < len(body) and body[index] != ",":
            raise RegistryInputError("BIBTEX_FIELD_MISSING_COMMA")
    return fields


def parse_bibtex(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    cursor = 0
    while True:
        match = re.search(r"@([A-Za-z][A-Za-z0-9_-]*)\s*([\{(])", text[cursor:])
        if match is None:
            break
        start = cursor + match.start()
        opening = cursor + match.end() - 1
        end = _find_balanced_entry_end(text, opening, match.group(2))
        entry_type = match.group(1).lower()
        raw = text[start:end]
        key, field_body = _split_header(text[opening + 1 : end - 1])
        if entry_type in {"comment", "preamble", "string"}:
            raise RegistryInputError("NONWORK_BIBTEX_DIRECTIVE_FORBIDDEN_IN_PINNED_BIB")
        if not key or any(char.isspace() for char in key):
            raise RegistryInputError("INVALID_BIBTEX_CITATION_KEY")
        if key in seen_keys:
            raise RegistryInputError("DUPLICATE_BIBTEX_CITATION_KEY")
        seen_keys.add(key)
        fields = _parse_fields(field_body)
        raw_bytes = raw.encode("utf-8")
        entries.append(
            {
                "citation_key": key,
                "entry_type": entry_type,
                "fields": fields,
                "raw_bytes": len(raw_bytes),
                "raw_sha256": sha256_bytes(raw_bytes),
            }
        )
        cursor = end
    if not entries:
        raise RegistryInputError("NO_BIBTEX_ENTRIES")
    entries.sort(key=lambda row: _utf8_key(str(row["citation_key"])))
    return entries


def _flatten_tex(value: str) -> str:
    value = re.sub(r"\\(?:textsuperscript|textsubscript|textregistered|emph|textit|textbf)\s*", " ", value)
    value = re.sub(r"\\[A-Za-z]+\*?", " ", value)
    value = re.sub(r"\\([^A-Za-z])", r"\1", value)
    return value.replace("{", " ").replace("}", " ")


def normalize_words(value: str) -> str:
    flattened = _flatten_tex(value)
    decomposed = unicodedata.normalize("NFKD", flattened).casefold()
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[^\W_]+", without_marks, flags=re.UNICODE))


def _split_bib_authors(author: str) -> list[str]:
    # BibTeX's separator is the word "and" at brace depth zero.
    parts: list[str] = []
    depth = 0
    start = 0
    for match in re.finditer(r"\band\b", author, flags=re.IGNORECASE):
        depth = author[: match.start()].count("{") - author[: match.start()].count("}")
        if depth == 0:
            parts.append(author[start : match.start()].strip())
            start = match.end()
    parts.append(author[start:].strip())
    return [part for part in parts if part]


def normalize_first_author(author: str) -> str:
    authors = _split_bib_authors(author)
    if not authors:
        return ""
    first = _flatten_tex(authors[0]).strip()
    if "," in first:
        family = first.split(",", 1)[0]
    else:
        tokens = first.split()
        family = tokens[-1] if tokens else ""
    return normalize_words(family)


def normalize_doi(value: str) -> str | None:
    candidate = value.strip().lower()
    candidate = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", candidate)
    match = re.search(r"10\.\d{4,9}/[^\s\"<>]+", candidate, flags=re.IGNORECASE)
    if match is None:
        return None
    return match.group(0).rstrip(".,;)]}").lower()


def extract_arxiv_ids(value: str) -> list[str]:
    ids: set[str] = set()
    for match in re.finditer(
        r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?",
        value,
    ):
        ids.add(match.group(1).lower())
    for match in re.finditer(
        r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)([a-z][a-z0-9.\-]+/\d{7})(?:v\d+)?",
        value,
    ):
        ids.add(match.group(1).lower())
    return sorted(ids, key=_utf8_key)


def extract_openalex_ids(value: str) -> list[str]:
    return sorted(
        {match.group(1).upper() for match in re.finditer(r"(?i)(?:openalex\.org/)?(W\d{4,})", value)},
        key=_utf8_key,
    )


def _entry_aliases(entry: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    fields = dict(entry["fields"])
    joined_values = "\n".join(str(value) for value in fields.values())
    dois = {doi for value in fields.values() if (doi := normalize_doi(str(value))) is not None}
    arxiv_ids = set(extract_arxiv_ids(joined_values))
    if "eprint" in fields and re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", fields["eprint"].strip()):
        arxiv_ids.add(re.sub(r"v\d+$", "", fields["eprint"].strip().lower()))
    openalex_ids = set(extract_openalex_ids(joined_values))
    aliases: list[dict[str, Any]] = []
    strong: dict[str, str] = {}
    for kind, values in (
        ("doi", dois),
        ("arxiv", arxiv_ids),
        ("openalex", openalex_ids),
    ):
        for value in sorted(values, key=_utf8_key):
            aliases.append(
                {
                    "component_edge": True,
                    "controlling_for_exposure_match": True,
                    "kind": kind,
                    "value": f"{kind}:{value}",
                }
            )
        if len(values) == 1:
            strong[kind] = next(iter(values))
    title = normalize_words(fields.get("title", ""))
    first_author = normalize_first_author(fields.get("author", ""))
    year_match = re.search(r"\d{4}", fields.get("year", ""))
    year = year_match.group(0) if year_match else ""
    if title and first_author and year:
        fallback_projection = {"first_author_family": first_author, "title": title, "year": year}
        fallback = canonical_digest(
            fallback_projection,
            domain="rtdl.goal5793.x1.survey_exposure.fallback_identity",
            version=1,
            projection="normalized_title_first_author_family_year",
        )["sha256"]
        aliases.append(
            {
                "component_edge": False,
                "controlling_for_exposure_match": True,
                "kind": "fallback_identity_sha256",
                "value": f"fallback_sha256:{fallback}",
            }
        )
    aliases.append(
        {
            "component_edge": False,
            "controlling_for_exposure_match": False,
            "kind": "citation_key",
            "value": f"citation_key:{entry['citation_key']}",
        }
    )
    aliases.sort(key=lambda row: (_utf8_key(str(row["kind"])), _utf8_key(str(row["value"]))))
    normalized = {"first_author_family": first_author, "title": title, "year": year}
    return aliases, normalized


def _strip_tex_comments_preserve_offsets(text: str) -> str:
    chars = list(text)
    line_start = 0
    while line_start < len(chars):
        line_end = text.find("\n", line_start)
        if line_end < 0:
            line_end = len(chars)
        for index in range(line_start, line_end):
            if chars[index] != "%":
                continue
            backslashes = 0
            cursor = index - 1
            while cursor >= line_start and chars[cursor] == "\\":
                backslashes += 1
                cursor -= 1
            if backslashes % 2 == 0:
                for replace in range(index, line_end):
                    chars[replace] = " "
                break
        line_start = line_end + 1
    return "".join(chars)


CITATION_RE = re.compile(
    r"\\(?P<command>(?:[A-Za-z@]*cite[A-Za-z@]*|nocite))\*?"
    r"(?:\s*\[[^\]\r\n]*\])*\s*\{(?P<keys>[^{}]*)\}",
    flags=re.IGNORECASE,
)


def extract_citations(member_path: str, text: str) -> list[dict[str, Any]]:
    scanned = _strip_tex_comments_preserve_offsets(text) if member_path.endswith(".tex") else text
    rows: list[dict[str, Any]] = []
    for match in CITATION_RE.finditer(scanned):
        keys = [key.strip() for key in match.group("keys").split(",") if key.strip()]
        if not keys:
            continue
        rows.append(
            {
                "char_offset": match.start(),
                "command": match.group("command"),
                "keys": keys,
                "line": scanned.count("\n", 0, match.start()) + 1,
                "member_path": member_path,
            }
        )
    return rows


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        lroot, rroot = self.find(left), self.find(right)
        if lroot == rroot:
            return
        if lroot < rroot:
            self.parent[rroot] = lroot
        else:
            self.parent[lroot] = rroot


def derive_components(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda row: _utf8_key(str(row["node_id"])))
    union = _UnionFind(len(ordered))
    by_alias: dict[str, list[int]] = {}
    for index, entry in enumerate(ordered):
        for alias in entry["aliases"]:
            if alias["component_edge"]:
                by_alias.setdefault(str(alias["value"]), []).append(index)
    for alias in sorted(by_alias, key=_utf8_key):
        indexes = by_alias[alias]
        for index in indexes[1:]:
            union.union(indexes[0], index)

    groups: dict[int, list[dict[str, Any]]] = {}
    for index, entry in enumerate(ordered):
        groups.setdefault(union.find(index), []).append(entry)
    fallback_components: dict[str, set[int]] = {}
    for root, members in groups.items():
        for entry in members:
            for alias in entry["aliases"]:
                if alias["kind"] == "fallback_identity_sha256":
                    fallback_components.setdefault(str(alias["value"]), set()).add(root)
    ambiguous_roots = {
        root
        for roots in fallback_components.values()
        if len(roots) > 1
        for root in roots
    }

    components: list[dict[str, Any]] = []
    for root, members in groups.items():
        members.sort(key=lambda row: _utf8_key(str(row["node_id"])))
        alias_values = sorted(
            {str(alias["value"]) for entry in members for alias in entry["aliases"]},
            key=_utf8_key,
        )
        doi_values = {value for value in alias_values if value.startswith("doi:")}
        arxiv_values = {value for value in alias_values if value.startswith("arxiv:")}
        conflict = len(doi_values) > 1 or len(arxiv_values) > 1
        if conflict:
            disposition = "IDENTITY_CONFLICT__PERMANENTLY_SELECTION_INELIGIBLE"
        elif root in ambiguous_roots:
            disposition = "FALLBACK_IDENTITY_AMBIGUOUS__PERMANENTLY_SELECTION_INELIGIBLE"
        else:
            disposition = "PREEXISTING_AUTHOR_EXPOSURE__PINNED_SURVEY_BIBLIOGRAPHY__PERMANENTLY_SELECTION_INELIGIBLE"
        identity = canonical_digest(
            [entry["node_id"] for entry in members],
            domain="rtdl.goal5793.x1.survey_exposure.component",
            version=1,
            projection="sorted_member_node_ids",
        )["sha256"]
        components.append(
            {
                "aliases": alias_values,
                "component_id": f"survey_component_sha256:{identity}",
                "fallback_identity_ambiguous": root in ambiguous_roots,
                "identity_conflict": conflict,
                "member_citation_keys": sorted(
                    [str(entry["citation_key"]) for entry in members], key=_utf8_key
                ),
                "member_node_ids": [str(entry["node_id"]) for entry in members],
                "selection_disposition": disposition,
                "selection_eligible": False,
            }
        )
    components.sort(key=lambda row: _utf8_key(str(row["component_id"])))
    return components


def _load_goal5753_crosslinks(path: Path) -> tuple[dict[str, list[str]], dict[str, Any]]:
    if not path.is_file() or file_sha256(path) != GOAL5753_UNIVERSE_SHA256:
        raise RegistryInputError("GOAL5753_UNIVERSE_IDENTITY_MISMATCH")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("source_rows")
    if not isinstance(rows, list) or len(rows) != 35:
        raise RegistryInputError("GOAL5753_UNIVERSE_ROW_COUNT_MISMATCH")
    mapping: dict[str, list[str]] = {}
    for row in rows:
        mapping.setdefault(str(row["citation_key"]), []).append(str(row["candidate_id"]))
    for values in mapping.values():
        values.sort(key=_utf8_key)
    return mapping, {
        "bytes": path.stat().st_size,
        "file_sha256": file_sha256(path),
        "historical_row_count": len(rows),
        "path": DEFAULT_GOAL5753_UNIVERSE.as_posix(),
        "path_role": "canonical_repository_role__caller_filesystem_spelling_not_hashed",
        "unique_citation_key_count": len(mapping),
    }


def build_registry(archive_path: Path, goal5753_universe_path: Path) -> dict[str, Any]:
    tar_data = read_safe_tar(archive_path)
    contents: dict[str, bytes] = tar_data.pop("contents")
    if "sample.bib" not in contents:
        raise RegistryInputError("SAMPLE_BIB_MEMBER_MISSING")
    if sha256_bytes(contents["sample.bib"]) != SAMPLE_BIB_SHA256:
        raise RegistryInputError("SAMPLE_BIB_SHA256_MISMATCH")
    try:
        bib_text = contents["sample.bib"].decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RegistryInputError("SAMPLE_BIB_NOT_STRICT_UTF8") from exc
    parsed = parse_bibtex(bib_text)
    if len(parsed) != 186:
        raise RegistryInputError("PINNED_BIBLIOGRAPHY_ENTRY_COUNT_MISMATCH")

    crosslinks, goal5753_source = _load_goal5753_crosslinks(goal5753_universe_path)
    bibliography_keys = {str(entry["citation_key"]) for entry in parsed}
    missing_old_keys = sorted(set(crosslinks) - bibliography_keys, key=_utf8_key)
    if missing_old_keys:
        raise RegistryInputError("GOAL5753_CITATION_KEY_MISSING_FROM_PINNED_BIB")

    citation_occurrences: list[dict[str, Any]] = []
    text_member_rows: list[dict[str, Any]] = []
    coverage_gaps: list[dict[str, Any]] = []
    for path in sorted(contents, key=_utf8_key):
        payload = contents[path]
        suffix = PurePosixPath(path).suffix.lower()
        if suffix not in TEXT_SUFFIXES:
            coverage_gaps.append(
                {
                    "member_path": path,
                    "reason": "UNSCANNED_BINARY_MEMBER__NO_FROZEN_IDENTIFIER_PARSER_IN_SURVEY_COMPONENT",
                    "selection_or_unseen_effect": "NO_ELIGIBILITY__NO_UNSEEN_OR_BLIND_CLAIM",
                }
            )
            continue
        try:
            text = payload.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            coverage_gaps.append(
                {
                    "member_path": path,
                    "reason": "DECLARED_TEXT_MEMBER_NOT_STRICT_UTF8",
                    "selection_or_unseen_effect": "NO_ELIGIBILITY__NO_UNSEEN_OR_BLIND_CLAIM",
                }
            )
            continue
        citations = extract_citations(path, text)
        citation_occurrences.extend(citations)
        text_member_rows.append(
            {
                "citation_occurrence_count": len(citations),
                "member_path": path,
                "strict_utf8": True,
            }
        )
    citation_occurrences.sort(
        key=lambda row: (_utf8_key(str(row["member_path"])), int(row["char_offset"]))
    )
    citation_surface_rows: list[dict[str, Any]] = []
    for member_path in sorted(
        {str(row["member_path"]) for row in citation_occurrences}, key=_utf8_key
    ):
        member_occurrences = [
            row for row in citation_occurrences if row["member_path"] == member_path
        ]
        if member_path == "main.tex":
            surface_kind = "PAPER_BODY_MAIN_TEX"
        elif member_path.endswith(".csv"):
            surface_kind = "SURVEY_DATA_TABLE__NOT_PAPER_BODY_CITATION"
        else:
            surface_kind = "OTHER_STRICT_UTF8_SOURCE__NOT_ASSUMED_PAPER_BODY"
        citation_surface_rows.append(
            {
                "citation_key_occurrences": sum(
                    len(row["keys"]) for row in member_occurrences
                ),
                "citation_macro_occurrences": len(member_occurrences),
                "member_path": member_path,
                "surface_kind": surface_kind,
                "unique_citation_keys": len(
                    {
                        key
                        for row in member_occurrences
                        for key in row["keys"]
                        if key != "*"
                    }
                ),
            }
        )
    cited_keys = {
        key
        for occurrence in citation_occurrences
        for key in occurrence["keys"]
        if key != "*"
    }
    unresolved_citations = sorted(cited_keys - bibliography_keys, key=_utf8_key)
    if unresolved_citations:
        coverage_gaps.append(
            {
                "citation_keys": unresolved_citations,
                "reason": "SOURCE_CITATION_KEY_ABSENT_FROM_SAMPLE_BIB",
                "selection_or_unseen_effect": "NO_ELIGIBILITY__NO_UNSEEN_OR_BLIND_CLAIM",
            }
        )

    entries: list[dict[str, Any]] = []
    missing_strong_identifier_count = 0
    missing_fallback_count = 0
    for entry in parsed:
        aliases, normalized = _entry_aliases(entry)
        strong_aliases = [alias for alias in aliases if alias["component_edge"]]
        fallback_aliases = [alias for alias in aliases if alias["kind"] == "fallback_identity_sha256"]
        if not strong_aliases:
            missing_strong_identifier_count += 1
        if not fallback_aliases:
            missing_fallback_count += 1
        key = str(entry["citation_key"])
        fields = dict(entry["fields"])
        node_id = canonical_digest(
            {
                "citation_key": key,
                "raw_bytes": entry["raw_bytes"],
                "raw_sha256": entry["raw_sha256"],
            },
            domain="rtdl.goal5793.x1.survey_exposure.node",
            version=1,
            projection="citation_key_and_exact_bibtex_entry_identity",
        )["sha256"]
        entry_row = {
            "aliases": aliases,
            "citation_key": key,
            "cited_in_scanned_source": key in cited_keys,
            "entry_type": entry["entry_type"],
            "field_names_sorted": sorted(fields, key=_utf8_key),
            "normalized_identity_projection": normalized,
            "node_id": f"survey_bib_node_sha256:{node_id}",
            "old_goal5753_candidate_ids": crosslinks.get(key, []),
            "raw_bytes": entry["raw_bytes"],
            "raw_sha256": entry["raw_sha256"],
            "selection_disposition": "PREEXISTING_AUTHOR_EXPOSURE__PINNED_SURVEY_BIBLIOGRAPHY__PERMANENTLY_SELECTION_INELIGIBLE",
            "selection_eligible": False,
            "source_member": "sample.bib",
            "strong_identifier_present": bool(strong_aliases),
            "title": fields.get("title"),
            "year": normalized["year"] or None,
        }
        entries.append(entry_row)
    entries.sort(key=lambda row: _utf8_key(str(row["node_id"])))
    components = derive_components(entries)

    entry_digest = canonical_digest(
        entries,
        domain="rtdl.goal5793.x1.survey_exposure.entries",
        version=1,
        projection="all_186_full_registry_rows_sorted_by_node_id_utf8",
    )
    component_digest = canonical_digest(
        components,
        domain="rtdl.goal5793.x1.survey_exposure.components",
        version=1,
        projection="strong_identifier_union_find_components_sorted_by_component_id_utf8",
    )
    member_digest = canonical_digest(
        tar_data["member_manifest"],
        domain="rtdl.goal5793.x1.survey_exposure.archive_members",
        version=1,
        projection="safe_member_manifest_sorted_by_path_utf8",
    )

    regular_members = [row for row in tar_data["member_manifest"] if row["type"] == "regular"]
    directory_members = [row for row in tar_data["member_manifest"] if row["type"] == "directory"]
    old_crosslinked_rows = sum(len(row["old_goal5753_candidate_ids"]) for row in entries)
    main_tex_surface = next(
        row for row in citation_surface_rows if row["member_path"] == "main.tex"
    )
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5793,
        "stage": "X1_SURVEY_EXPOSURE_REGISTRY_COMPONENT",
        "status": "CREATE_ONLY_OFFLINE_SURVEY_REGISTRY_FROZEN__ALL_186_ENTRIES_PERMANENTLY_SELECTION_INELIGIBLE__X1_COMPONENT_NOT_X1_CLOSURE",
        "canonicalization": {
            "name": CANONICALIZATION_NAME,
            "new_successor_artifacts_only": True,
        },
        "superseded_create_only_lineage": REJECTED_CREATE_ONLY_V1,
        "source_authorities": {
            "goal5753_universe": goal5753_source,
            "survey_archive": tar_data["archive"],
            "sample_bib": {
                "bytes": len(contents["sample.bib"]),
                "member_path": "sample.bib",
                "sha256": sha256_bytes(contents["sample.bib"]),
            },
        },
        "safe_archive_policy": {
            "filesystem_extraction_performed": False,
            "only_directories_and_regular_files_allowed": True,
            "links_special_absolute_parent_backslash_duplicate_or_aliased_paths_allowed": False,
            "max_archive_members": MAX_ARCHIVE_MEMBERS,
            "max_member_bytes": MAX_MEMBER_BYTES,
            "max_total_regular_bytes": MAX_TOTAL_REGULAR_BYTES,
        },
        "counts": {
            "bibliography_entries": len(entries),
            "bibliography_entries_cited_in_scanned_source": sum(
                1 for row in entries if row["cited_in_scanned_source"]
            ),
            "bibliography_entries_not_cited_in_scanned_source": sum(
                1 for row in entries if not row["cited_in_scanned_source"]
            ),
            "components": len(components),
            "coverage_gaps": len(coverage_gaps),
            "directory_members": len(directory_members),
            "missing_fallback_identity_entries": missing_fallback_count,
            "missing_strong_identifier_entries": missing_strong_identifier_count,
            "old_goal5753_crosslinked_candidate_rows": old_crosslinked_rows,
            "old_goal5753_unique_citation_keys": len(crosslinks),
            "regular_members": len(regular_members),
            "selection_eligible_entries": 0,
            "all_scanned_source_citation_key_occurrences": sum(
                len(row["keys"]) for row in citation_occurrences
            ),
            "all_scanned_source_citation_macro_occurrences": len(citation_occurrences),
            "all_scanned_source_unique_citation_keys": len(cited_keys),
            "main_tex_paper_body_citation_key_occurrences": main_tex_surface[
                "citation_key_occurrences"
            ],
            "main_tex_paper_body_citation_macro_occurrences": main_tex_surface[
                "citation_macro_occurrences"
            ],
            "main_tex_paper_body_unique_citation_keys": main_tex_surface[
                "unique_citation_keys"
            ],
            "strict_utf8_scanned_members": len(text_member_rows),
            "unresolved_source_citation_keys": len(unresolved_citations),
        },
        "bibliography_completeness": {
            "sample_bib_is_complete_for_all_entries_physically_present_in_pinned_archive": True,
            "all_strict_utf8_source_citation_keys_resolve_to_sample_bib": not unresolved_citations,
            "complete_published_reference_list_claimed": False,
            "complete_literature_universe_claimed": False,
            "complete_author_mental_exposure_claimed": False,
            "bibliography_only_entries_are_still_conservatively_registered": True,
            "old_35_or_source_cited_subset_only_used": False,
        },
        "alias_and_component_policy": {
            "normalized_aliases": [
                "lowercase DOI",
                "lowercase versionless arXiv id",
                "uppercase OpenAlex W id",
                "domain-separated normalized title plus first-author family plus year fallback digest",
                "citation key as noncontrolling alias",
            ],
            "component_edges": list(COMPONENT_EDGE_ALIAS_KINDS),
            "component_algorithm": "deterministic union-find over node ids sorted by UTF-8 bytes",
            "fallback_identity_is_component_edge": False,
            "fallback_collision_is_merged": False,
            "all_aliases_preserved": True,
            "all_registry_matches_permanently_selection_ineligible": True,
        },
        "member_manifest": tar_data["member_manifest"],
        "member_manifest_digest": member_digest,
        "strict_utf8_member_scan": text_member_rows,
        "citation_surface_summary": {
            "main_tex_is_the_only_surface_called_paper_body": True,
            "csv_citations_are_not_called_paper_body_citations": True,
            "rows": citation_surface_rows,
        },
        "citation_occurrences": citation_occurrences,
        "unresolved_source_citation_keys": unresolved_citations,
        "bibliography_entries": entries,
        "components": components,
        "coverage_gaps": coverage_gaps,
        "digests": {
            "bibliography_entries": entry_digest,
            "components": component_digest,
        },
        "selection_policy": {
            "all_186_bibliography_entries_permanently_selection_ineligible": True,
            "survey_registry_match_selection_eligible": False,
            "coverage_gap_allows_selection_eligibility": False,
            "coverage_gap_allows_unseen_blind_or_held_out_claim": False,
            "later_query_matches_retained_as_duplicate_crosslinks": True,
        },
        "scope_boundary": {
            "complete_for_exact_pinned_survey_bibliography": True,
            "complete_presearch_project_exposure_registry": False,
            "x1_generic_examiner_implemented_by_this_artifact": False,
            "x1_environment_or_shared_native_implemented_by_this_artifact": False,
            "x1_complete_or_externally_reviewed": False,
            "x2_search_implemented_or_authorized": False,
            "network_or_live_provider_call_count": 0,
            "entropy_anchor_or_draw_count": 0,
            "candidate_selection_count": 0,
            "candidate_implementation_or_execution_count": 0,
            "gpu_home_pod_or_ssh_count": 0,
            "registered_or_performance_timing_count": 0,
            "generalization_soundness_completeness_false_rejection_third_family_claimed": False,
            "unseen_blind_held_out_usability_production_publication_or_submission_claimed": False,
        },
    }
    result["registry_sha256"] = seal_document(
        result,
        seal_field="registry_sha256",
        domain="rtdl.goal5793.x1.survey_exposure.registry_document",
        version=1,
    )
    return result


def serialized_document(document: Mapping[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def write_create_only(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey-archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--goal5753-universe", type=Path, default=DEFAULT_GOAL5753_UNIVERSE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    document = build_registry(args.survey_archive, args.goal5753_universe)
    payload = serialized_document(document)
    write_create_only(args.output, payload)
    print(
        json.dumps(
            {
                "bibliography_entries": document["counts"]["bibliography_entries"],
                "bytes": len(payload),
                "file_sha256": sha256_bytes(payload),
                "output": args.output.as_posix(),
                "registry_sha256": document["registry_sha256"],
                "selection_eligible_entries": 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
