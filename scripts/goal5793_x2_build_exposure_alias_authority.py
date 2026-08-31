#!/usr/bin/env python3
"""Build the detailed, conservative X2 alias table from frozen survey bytes."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x1_build_exposure_registry as predecessor
from scripts.goal5793_x2_offline_core import fallback_sha256, normalize_author, normalize_text


ROOT = Path(__file__).resolve().parents[1]
SURVEY_ARCHIVE = ROOT / "tmp/goal5793_survey_source_extract/goal5753/SELECTION_SOURCE/survey_source.tar"
X1_REGISTRY = ROOT / "history/internal_docs/goal5793_x1_project_exposure_registry_v2_20260822.json"
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5793_x2_exposure_alias_authority_20260822.json"
SURVEY_ARCHIVE_SHA256 = "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857"
X1_REGISTRY_SHA256 = "9695545df7b2908f9845bc7b825fa9e226b0d05d506b7b3c74305560393af804"
PREDECESSOR_BUILDER_SHA256 = "b27edf38703a0971034543d6d043a82223fbdccf5d43b94c27fc49dc6e36ebe1"
SAMPLE_BIB_SHA256 = "9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a"


class AliasAuthorityError(ValueError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _identity(path: Path, expected: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink() or _sha256(path) != expected:
        raise AliasAuthorityError(f"IDENTITY_MISMATCH:{path.as_posix()}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": expected,
    }


def _venue(fields: dict[str, str]) -> dict[str, str]:
    names = ("journal", "booktitle", "publisher", "organization", "school", "institution")
    return {name: fields[name] for name in names if fields.get(name)}


def _protocol_aliases(title: str, authors: str, year: int | None) -> dict[str, Any]:
    title_normalized = normalize_text(title)
    tokens = title_normalized.split()
    author_parts = predecessor._split_bib_authors(authors)
    normalized_authors = [normalize_text(author) for author in author_parts]
    first_author = normalize_author(author_parts[0]) if author_parts else ""
    projection = {
        "title_normalized": title_normalized,
        "title_alnum_compact": "".join(tokens),
        "title_token_sequence_sha256": hashlib.sha256("\0".join(tokens).encode("utf-8")).hexdigest(),
        "title_token_set_sha256": hashlib.sha256("\0".join(sorted(set(tokens))).encode("utf-8")).hexdigest(),
        "title_token_count": len(tokens),
        "authors_normalized": normalized_authors,
        "first_author_family_normalized": first_author,
        "year": year,
        "fallback_sha256": fallback_sha256(title, first_author, year) if first_author and year is not None else None,
    }
    return projection


def build_authority() -> dict[str, Any]:
    survey_identity = _identity(SURVEY_ARCHIVE, SURVEY_ARCHIVE_SHA256)
    registry_identity = _identity(X1_REGISTRY, X1_REGISTRY_SHA256)
    predecessor_identity = _identity(ROOT / "scripts/goal5793_x1_build_exposure_registry.py", PREDECESSOR_BUILDER_SHA256)
    safe = predecessor.read_safe_tar(SURVEY_ARCHIVE)
    contents = safe.pop("contents")
    sample = contents.get("sample.bib")
    if not isinstance(sample, bytes) or hashlib.sha256(sample).hexdigest() != SAMPLE_BIB_SHA256:
        raise AliasAuthorityError("SAMPLE_BIB_IDENTITY_MISMATCH")
    parsed = predecessor.parse_bibtex(sample.decode("utf-8", errors="strict"))
    if len(parsed) != 186:
        raise AliasAuthorityError("BIBLIOGRAPHY_ROW_COUNT_MISMATCH")
    x1 = json.loads(X1_REGISTRY.read_text(encoding="utf-8", errors="strict"))
    x1_by_key = {row["citation_key"]: row for row in x1["bibliography_entries"]}
    rows: list[dict[str, Any]] = []
    for entry in parsed:
        citation_key = entry["citation_key"]
        fields = dict(entry["fields"])
        title = fields.get("title", "")
        authors = fields.get("author", "")
        year_text = fields.get("year", "")
        year_match = re.search(r"[0-9]{4}", year_text)
        year = int(year_match.group(0)) if year_match else None
        historical = x1_by_key.get(citation_key)
        if historical is None or historical["raw_sha256"] != entry["raw_sha256"]:
            raise AliasAuthorityError("X1_BIBLIOGRAPHY_CROSSLINK_MISMATCH")
        historical_aliases = [alias["value"] for alias in historical["aliases"]]
        strong = {
            kind: sorted(value.split(":", 1)[1] for value in historical_aliases if value.startswith(kind + ":"))
            for kind in ("doi", "arxiv", "openalex")
        }
        row = {
            "citation_key": citation_key,
            "entry_type": entry["entry_type"],
            "raw_entry_bytes": entry["raw_bytes"],
            "raw_entry_sha256": entry["raw_sha256"],
            "title_exact_bibtex": title,
            "authors_exact_bibtex": authors,
            "year_exact_bibtex": year_text or None,
            "year_normalized": year,
            "venue_exact_fields": _venue(fields),
            "all_field_names": sorted(fields),
            "all_fields_exact": {key: fields[key] for key in sorted(fields)},
            "historical_x1_aliases": sorted(historical_aliases),
            "strong_identifiers": strong,
            "strong_identifier_present": any(strong.values()),
            "protocol_aliases": _protocol_aliases(title, authors, year),
            "matching_disposition": "FROZEN_PREEXISTING_EXPOSURE__PERMANENTLY_SELECTION_INELIGIBLE",
            "matching_risk": (
                "STRONG_IDENTIFIER_PLUS_CONSERVATIVE_TEXT_ALIASES"
                if any(strong.values())
                else "NO_STRONG_IDENTIFIER__CONSERVATIVE_TITLE_AUTHOR_YEAR_MATCHING_REQUIRED__MISS_TERMINATES_EXPANSION_IF_LATER_DISCOVERED"
            ),
            "selection_eligible": False,
        }
        rows.append(row)
    rows.sort(key=lambda row: row["citation_key"].encode("utf-8"))
    if len({row["citation_key"] for row in rows}) != 186:
        raise AliasAuthorityError("BIBLIOGRAPHY_CITATION_KEY_DUPLICATE")
    document: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.exposure_alias_authority.v1",
        "date": "2026-08-22",
        "status": "OFFLINE_EXPOSURE_ALIAS_TABLE_FROZEN__ALL_186_PREEXPOSED_AND_SELECTION_INELIGIBLE__MATCHING_RISK_EXPLICIT",
        "predecessors": {
            "survey_archive": survey_identity,
            "x1_registry": registry_identity,
            "x1_registry_builder": predecessor_identity,
            "sample_bib": {
                "member_path": "sample.bib",
                "bytes": len(sample),
                "sha256": SAMPLE_BIB_SHA256,
            },
        },
        "sample_bib_base64": base64.b64encode(sample).decode("ascii"),
        "matching_policy": {
            "strong_id_edges": ["normalized DOI", "versionless arXiv", "canonical OpenAlex W id"],
            "fallback_equivalence_edge_allowed": False,
            "fallback_collision": "FALLBACK_IDENTITY_AMBIGUOUS__SELECTION_INELIGIBLE",
            "conservative_match_order": [
                "strong identifier intersection",
                "exact protocol fallback sha256",
                "exact normalized title plus year",
                "same first-author family plus year and token Jaccard >= 0.90",
                "same first-author family plus year and complete reference-title token containment with >=4 tokens",
            ],
            "conservative_text_match_effect": "SELECTION_INELIGIBLE__FALSE_POSITIVE_COSTS_POWER_BUT_CANNOT_CREATE_FALSE_GENERALIZATION_EVIDENCE",
            "manual_disambiguation_allowed": False,
            "later_discovered_preexisting_exposure": "TERMINATE_SINGLE_EXPANSION__NO_REPLACEMENT_OR_REUSE",
        },
        "counts": {
            "bibliography_rows": 186,
            "strong_identifier_rows": sum(row["strong_identifier_present"] for row in rows),
            "no_strong_identifier_rows": sum(not row["strong_identifier_present"] for row in rows),
            "selection_eligible_rows": 0,
            "network_or_live_lookup_count": 0,
        },
        "rows": rows,
        "scope": {
            "complete_for_exact_sample_bib_member": True,
            "complete_author_mental_exposure_claimed": False,
            "literature_complete_claimed": False,
            "unseen_blind_or_held_out_claimed": False,
            "live_lookup_performed": False,
            "generalization_or_usability_evidence_count": 0,
        },
        "authorization": {
            "live_search": False,
            "entropy": False,
            "selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "timing": False,
        },
        "authority_sha256": "",
    }
    document["authority_sha256"] = seal_document(
        document,
        seal_field="authority_sha256",
        domain="rtdl.goal5793.x2.exposure_alias_authority",
        version=1,
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    document = build_authority()
    payload = canonical_json_bytes(document) + b"\n"
    identity = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    if not args.write_create_only:
        print(json.dumps({"status": "DRY_RUN_NO_HISTORY_WRITE", **identity}))
        return 0
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(json.dumps({"path": args.output.as_posix(), **identity}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
