"""Validate the owner's bounded off-repository exposure disclosure.

The declaration is an honest reasonable-recall statement, never a claim of
complete human memory or literature completeness.  Every listed work is
permanently selection-ineligible.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Mapping

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


SCHEMA = "rtdl.goal5793.x1.owner_off_repository_exposure_disclosure.v1"
STATUS_VALUES = {
    "NONE_KNOWN_AFTER_REASONABLE_RECALL",
    "ALL_KNOWN_ITEMS_LISTED_AFTER_REASONABLE_RECALL",
}
ROOT_KEYS = {
    "schema",
    "date",
    "owner_role",
    "statement",
    "declared_scope",
    "owner_attests_complete_for_declared_scope",
    "disclosures",
    "claim_boundary",
    "authorization",
    "disclosure_sha256",
}
ROW_KEYS = {
    "title",
    "author",
    "year",
    "doi",
    "arxiv_id",
    "url",
    "exposure_kind",
    "notes",
    "permanently_selection_ineligible",
}
EXPECTED_SCOPE = {
    "included": (
        "off-repository papers, code, artifacts, projects, or private materials "
        "remembered as used to design, implement, debug, tune, or evaluate the "
        "frozen checker/calculus before the X1 disclosure freeze"
    ),
    "repo_git_s0_and_survey_items_need_not_be_relisted": True,
    "reasonable_recall_not_omniscience": True,
    "forgotten_or_incidental_exposure_mathematically_excluded": False,
}
EXPECTED_BOUNDARY = {
    "complete_author_mental_exposure_claimed": False,
    "complete_literature_universe_claimed": False,
    "unseen_blind_or_held_out_claim_authorized": False,
    "absence_from_disclosure_proves_never_seen": False,
    "later_recalled_preexisting_exposure_terminates_single_expansion_without_replacement": True,
}
EXPECTED_AUTHORIZATION = {
    "x1_complete": False,
    "x2_search": False,
    "entropy": False,
    "selection": False,
    "candidate_implementation": False,
    "candidate_execution": False,
    "gpu_home_pod_ssh": False,
    "registered_or_performance_timing": False,
    "external_reviewer_contact": False,
    "public_release_publication_or_submission": False,
}


class DisclosureError(ValueError):
    pass


def _exact_mapping(value: object, keys: set[str], context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise DisclosureError(f"{context}_keyset_mismatch")
    return value


def _nullable_string(value: object, context: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise DisclosureError(f"{context}_invalid")
    return value.strip()


def validate(document: object) -> dict[str, Any]:
    root = _exact_mapping(document, ROOT_KEYS, "root")
    if root["schema"] != SCHEMA or root["date"] != "2026-08-22":
        raise DisclosureError("schema_or_date_mismatch")
    if root["owner_role"] != "RTDL_PROJECT_OWNER":
        raise DisclosureError("owner_role_mismatch")
    if root["statement"] not in STATUS_VALUES:
        raise DisclosureError("statement_invalid")
    if canonical_json_bytes(root["declared_scope"]) != canonical_json_bytes(EXPECTED_SCOPE):
        raise DisclosureError("declared_scope_mismatch")
    if root["owner_attests_complete_for_declared_scope"] is not True:
        raise DisclosureError("declared_scope_attestation_required")
    if canonical_json_bytes(root["claim_boundary"]) != canonical_json_bytes(EXPECTED_BOUNDARY):
        raise DisclosureError("claim_boundary_mismatch")
    if canonical_json_bytes(root["authorization"]) != canonical_json_bytes(EXPECTED_AUTHORIZATION):
        raise DisclosureError("authorization_mismatch")
    rows = root["disclosures"]
    if not isinstance(rows, list):
        raise DisclosureError("disclosures_not_list")
    if root["statement"] == "NONE_KNOWN_AFTER_REASONABLE_RECALL" and rows:
        raise DisclosureError("none_statement_has_rows")
    if root["statement"] == "ALL_KNOWN_ITEMS_LISTED_AFTER_REASONABLE_RECALL" and not rows:
        raise DisclosureError("listed_statement_has_no_rows")
    normalized: set[bytes] = set()
    for index, value in enumerate(rows):
        row = _exact_mapping(value, ROW_KEYS, f"row_{index}")
        title = _nullable_string(row["title"], f"row_{index}_title")
        author = _nullable_string(row["author"], f"row_{index}_author")
        year = _nullable_string(row["year"], f"row_{index}_year")
        doi = _nullable_string(row["doi"], f"row_{index}_doi")
        arxiv_id = _nullable_string(row["arxiv_id"], f"row_{index}_arxiv")
        url = _nullable_string(row["url"], f"row_{index}_url")
        _nullable_string(row["exposure_kind"], f"row_{index}_exposure_kind")
        if row["notes"] is not None and not isinstance(row["notes"], str):
            raise DisclosureError(f"row_{index}_notes_invalid")
        if row["permanently_selection_ineligible"] is not True:
            raise DisclosureError(f"row_{index}_eligibility_mismatch")
        if not (doi or arxiv_id or url or (title and author and year)):
            raise DisclosureError(f"row_{index}_identity_insufficient")
        if doi is not None and re.fullmatch(r"10\.\d{4,9}/\S+", doi, re.IGNORECASE) is None:
            raise DisclosureError(f"row_{index}_doi_invalid")
        identity = canonical_json_bytes(
            {"title": title, "author": author, "year": year, "doi": doi, "arxiv_id": arxiv_id, "url": url}
        )
        if identity in normalized:
            raise DisclosureError("duplicate_disclosure_identity")
        normalized.add(identity)
    expected_seal = seal_document(
        root,
        seal_field="disclosure_sha256",
        domain="rtdl.goal5793.x1.owner_off_repository_exposure_disclosure",
        version=1,
    )
    if root["disclosure_sha256"] != expected_seal:
        raise DisclosureError("disclosure_seal_mismatch")
    return dict(root)


def build_none_template() -> dict[str, Any]:
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "date": "2026-08-22",
        "owner_role": "RTDL_PROJECT_OWNER",
        "statement": "NONE_KNOWN_AFTER_REASONABLE_RECALL",
        "declared_scope": deepcopy(EXPECTED_SCOPE),
        "owner_attests_complete_for_declared_scope": True,
        "disclosures": [],
        "claim_boundary": deepcopy(EXPECTED_BOUNDARY),
        "authorization": deepcopy(EXPECTED_AUTHORIZATION),
        "disclosure_sha256": "",
    }
    document["disclosure_sha256"] = seal_document(
        document,
        seal_field="disclosure_sha256",
        domain="rtdl.goal5793.x1.owner_off_repository_exposure_disclosure",
        version=1,
    )
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path, nargs="?")
    parser.add_argument("--print-none-template", action="store_true")
    args = parser.parse_args()
    if args.print_none_template:
        if args.path is not None:
            parser.error("path is incompatible with --print-none-template")
        print(json.dumps(build_none_template(), sort_keys=True, indent=2, ensure_ascii=False))
        return 0
    if args.path is None:
        parser.error("path is required unless --print-none-template is used")
    document = json.loads(args.path.read_text(encoding="utf-8"))
    validated = validate(document)
    print(validated["statement"], validated["disclosure_sha256"], len(validated["disclosures"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
