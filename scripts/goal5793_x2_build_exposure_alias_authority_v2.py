#!/usr/bin/env python3
"""Append-only legibility successor for the reviewed X2 exposure authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_build_exposure_alias_authority as v1


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json"
DOMAIN = "rtdl.goal5793.x2.exposure_alias_authority.v2"


def build_authority() -> dict[str, Any]:
    predecessor = v1.build_authority()
    rows = predecessor["rows"]
    for row in rows:
        aliases = row.get("protocol_aliases")
        if not isinstance(aliases, dict) or set(aliases) != {
            "title_normalized", "title_alnum_compact", "title_token_sequence_sha256",
            "title_token_set_sha256", "title_token_count", "authors_normalized",
            "first_author_family_normalized", "year", "fallback_sha256",
        }:
            raise v1.AliasAuthorityError("PROTOCOL_ALIAS_PROJECTION_SCHEMA_MISMATCH")
    strong = [row for row in rows if row["strong_identifier_present"]]
    weak = [row for row in rows if not row["strong_identifier_present"]]
    weak_author_year = [
        row for row in weak
        if row["protocol_aliases"]["first_author_family_normalized"]
        and row["protocol_aliases"]["year"] is not None
        and row["protocol_aliases"]["fallback_sha256"] is not None
    ]
    weak_title_only = [row for row in weak if row not in weak_author_year]
    if (len(strong), len(weak_author_year), len(weak_title_only)) != (7, 176, 3):
        raise v1.AliasAuthorityError("ALIAS_PATH_COUNT_MISMATCH")
    document: dict[str, Any] = {
        **predecessor,
        "schema": "rtdl.goal5793.x2.exposure_alias_authority.v2",
        "status": "FULL_NESTED_ALIAS_PROJECTION_WITH_EXPLICIT_7_176_3_COUNTS__ALL_186_SELECTION_INELIGIBLE",
        "successor_of": {
            "path": "generated/goal5793_x2_exposure_alias_authority_20260822.json",
            "review_finding": "P2_4_ALIAS_PROJECTION_LEGIBILITY",
            "reviewed_bytes_edited": False,
        },
        "rows_projection": (
            "FULL__AUTHOR_YEAR_FALLBACK_FIELDS_ARE_PRESENT_UNDER_EACH_ROW_PROTOCOL_ALIASES__NOT_REDACTED"
        ),
        "legibility_correction": {
            "top_level_first_author_year_fallback_fields_present": False,
            "nested_protocol_alias_fields_present_for_all_186_rows": True,
            "published_v1_mechanism_inert": False,
            "review_near_miss_cause": "REVIEWER_LOOKED_FOR_TOP_LEVEL_FIELDS_WHILE_OPERATIVE_FIELDS_ARE_NESTED_UNDER_PROTOCOL_ALIASES",
        },
        "counts": {
            **predecessor["counts"],
            "strong_identifier_rows": 7,
            "weak_identifier_rows_with_author_year_fallback_path": 176,
            "weak_identifier_rows_exact_title_only": 3,
            "all_rows_with_author_year_fallback_path_including_strong": 183,
            "rows_with_nested_protocol_alias_projection": 186,
        },
        "authority_sha256": "",
    }
    document["authority_sha256"] = seal_document(document, seal_field="authority_sha256", domain=DOMAIN, version=2)
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    args = parser.parse_args()
    document = build_authority()
    payload = canonical_json_bytes(document) + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_ALREADY_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
    print(json.dumps({"status": "PASS", "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "authority_sha256": document["authority_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
