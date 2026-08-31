#!/usr/bin/env python3
"""Build the append-only registry for the 200 works observed by Goal5793 X3.

The X3 provider transaction is terminal and remains unchanged.  This script
performs no network access and does not reuse the partial page as a candidate
population.  It only records every work identity already present in the
sealed journal as permanently exposed and selection-ineligible.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core


ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl"
OUTPUT = ROOT / "history/internal_docs/goal5793_x3_a1_observed_work_exposure_registry_20260824.json"

JOURNAL_BYTES = 9_326_661
JOURNAL_SHA256 = "94ab0fc951c728569c0d57f649de918feeb547a8f4dac0ea48ec43f176b7e4c5"
BODY_BYTES = 6_991_761
BODY_SHA256 = "453fbab3bf25b84986fa593b80e6e12451619ed24b2c189dc717e643253d874d"
EXPECTED_RESULT_COUNT = 200
SCHEMA = "rtdl.goal5793.x3.a1.observed_work_exposure_registry.v1"
DOMAIN = "rtdl.goal5793.x3.a1.observed_work_exposure_registry.v1"


class RegistryError(ValueError):
    """Stable fail-closed registry error."""


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _identity(path: Path) -> dict[str, Any]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": _sha256(payload),
    }


def load_observed_body(journal_path: Path = JOURNAL) -> tuple[bytes, Mapping[str, Any]]:
    journal_payload = journal_path.read_bytes()
    if len(journal_payload) != JOURNAL_BYTES or _sha256(journal_payload) != JOURNAL_SHA256:
        raise RegistryError("JOURNAL_IDENTITY_MISMATCH")
    try:
        lines = [json.loads(line) for line in journal_payload.decode("utf-8", errors="strict").splitlines()]
    except Exception as exc:  # noqa: BLE001
        raise RegistryError("JOURNAL_JSON_INVALID") from exc
    if [row.get("event") for row in lines] != [
        "TRANSACTION_START",
        "HTTP_ATTEMPT",
        "TRANSACTION_TERMINAL_FAILURE",
    ]:
        raise RegistryError("JOURNAL_EVENT_SEQUENCE_MISMATCH")
    attempt_event = lines[1]
    attempt = attempt_event.get("attempt")
    if not isinstance(attempt, Mapping):
        raise RegistryError("JOURNAL_ATTEMPT_MISSING")
    if (
        attempt_event.get("provider") != "OpenAlex Works API"
        or attempt_event.get("request_sequence") != 0
        or attempt.get("attempt") != 1
        or attempt.get("status") != 200
        or attempt.get("error") is not None
    ):
        raise RegistryError("JOURNAL_ATTEMPT_IDENTITY_MISMATCH")
    try:
        body = base64.b64decode(attempt["body_base64"], validate=True)
    except Exception as exc:  # noqa: BLE001
        raise RegistryError("JOURNAL_BODY_BASE64_INVALID") from exc
    if len(body) != BODY_BYTES or _sha256(body) != BODY_SHA256:
        raise RegistryError("OBSERVED_BODY_IDENTITY_MISMATCH")
    try:
        decoded = json.loads(body)
    except Exception as exc:  # noqa: BLE001
        raise RegistryError("OBSERVED_BODY_JSON_INVALID") from exc
    if not isinstance(decoded, Mapping) or not isinstance(decoded.get("results"), list):
        raise RegistryError("OBSERVED_BODY_SCHEMA_INVALID")
    if len(decoded["results"]) != EXPECTED_RESULT_COUNT:
        raise RegistryError("OBSERVED_RESULT_COUNT_MISMATCH")
    if not isinstance(decoded.get("meta"), Mapping) or not decoded["meta"].get("next_cursor"):
        raise RegistryError("OBSERVED_BODY_CURSOR_MISSING")
    return body, decoded


def _first_author(work: Mapping[str, Any]) -> str:
    authorships = work.get("authorships")
    if not isinstance(authorships, list) or not authorships or not isinstance(authorships[0], Mapping):
        raise RegistryError("OBSERVED_FIRST_AUTHOR_MISSING")
    author = authorships[0].get("author")
    if not isinstance(author, Mapping) or not isinstance(author.get("display_name"), str) or not author["display_name"]:
        raise RegistryError("OBSERVED_FIRST_AUTHOR_MISSING")
    return str(author["display_name"])


def _work_row(work: Mapping[str, Any], ordinal: int) -> dict[str, Any]:
    ids = work.get("ids") if isinstance(work.get("ids"), Mapping) else {}
    try:
        doi = core.normalize_doi(work.get("doi") or ids.get("doi"))
        arxiv = core.normalize_arxiv(ids.get("arxiv"))
        openalex = core.normalize_openalex(work.get("id") or ids.get("openalex"))
    except core.X2Error as exc:
        raise RegistryError(f"OBSERVED_STRONG_ID_INVALID:{ordinal}:{exc.reason_id}") from exc
    if openalex is None:
        raise RegistryError(f"OBSERVED_OPENALEX_ID_MISSING:{ordinal}")
    first_author_raw = _first_author(work)
    year = work.get("publication_year")
    if type(year) is not int or not 1000 <= year <= 9999:
        raise RegistryError(f"OBSERVED_YEAR_INVALID:{ordinal}")
    title_raw = work.get("title")
    if title_raw is not None and not isinstance(title_raw, str):
        raise RegistryError(f"OBSERVED_TITLE_SCHEMA_INVALID:{ordinal}")
    if isinstance(title_raw, str) and title_raw:
        title_normalized: str | None = core.normalize_text(title_raw)
        fallback = core.fallback_sha256(title_raw, first_author_raw, year)
        fallback_unavailable_reason = None
    else:
        title_normalized = None
        fallback = None
        fallback_unavailable_reason = "TITLE_MISSING_IN_OBSERVED_PROVIDER_BYTES__NO_SYNTHETIC_SUBSTITUTE"
    aliases: list[dict[str, str]] = []
    for kind, value in (
        ("doi", doi),
        ("arxiv", arxiv),
        ("openalex", openalex),
        ("fallback_sha256", fallback),
    ):
        if value is not None:
            aliases.append({"kind": kind, "value": str(value)})
    if doi is not None:
        canonical_identity = f"doi:{doi}"
    elif arxiv is not None:
        canonical_identity = f"arxiv:{arxiv}"
    elif openalex is not None:
        canonical_identity = f"openalex:{openalex}"
    elif fallback is not None:  # pragma: no cover - OpenAlex id is mandatory above.
        canonical_identity = f"fallback_sha256:{fallback}"
    else:  # pragma: no cover
        raise RegistryError(f"OBSERVED_IDENTITY_EMPTY:{ordinal}")
    return {
        "ordinal": ordinal,
        "record_sha256": _sha256(core.canonical_bytes(work)),
        "canonical_work_identity": canonical_identity,
        "doi": doi,
        "arxiv": arxiv,
        "openalex": openalex,
        "fallback_sha256": fallback,
        "fallback_unavailable_reason": fallback_unavailable_reason,
        "title_normalized": title_normalized,
        "first_author_family_normalized": core.normalize_author(first_author_raw),
        "year": year,
        "aliases": aliases,
        "observed_in_goal5793_x3_terminal_page": True,
        "selection_eligible": False,
        "exclusion_reason": "OBSERVED_BY_PROJECT_BEFORE_ANY_SUCCESSOR_SELECTION__PERMANENTLY_INELIGIBLE",
    }


def build_registry(journal_path: Path = JOURNAL) -> dict[str, Any]:
    body, decoded = load_observed_body(journal_path)
    rows = [_work_row(work, ordinal) for ordinal, work in enumerate(decoded["results"])]
    openalex_ids = [row["openalex"] for row in rows]
    canonical_ids = [row["canonical_work_identity"] for row in rows]
    if len(set(openalex_ids)) != EXPECTED_RESULT_COUNT:
        raise RegistryError("OBSERVED_OPENALEX_ID_DUPLICATE")
    if len(set(canonical_ids)) != EXPECTED_RESULT_COUNT:
        raise RegistryError("OBSERVED_CANONICAL_ID_DUPLICATE")
    registry: dict[str, Any] = {
        "schema": SCHEMA,
        "date": "2026-08-24",
        "status": "PASS__EXACTLY_200_OBSERVED_WORKS_PERMANENTLY_SELECTION_INELIGIBLE",
        "source": {
            "journal": _identity(journal_path),
            "response_body_bytes": len(body),
            "response_body_sha256": _sha256(body),
            "journal_event": "HTTP_ATTEMPT",
            "request_sequence": 0,
            "provider": "OpenAlex Works API",
            "partial_page_is_candidate_population": False,
        },
        "identity_protocol": {
            "controlling_source": "GOAL5793_S0_CANONICAL_WORK_IDENTITY_RULES",
            "priority": ["doi", "arxiv", "openalex", "fallback_sha256"],
            "doi": "normalize_doi from the frozen X2 offline core",
            "arxiv": "versionless normalize_arxiv from the frozen X2 offline core",
            "openalex": "uppercase W identifier from the frozen X2 offline core",
            "fallback": "sha256(canonical JSON {first_author,title,year}) using the frozen X2/S0 normalization",
            "missing_title_policy": "preserve null fallback with an explicit reason; never synthesize title bytes",
        },
        "rows": rows,
        "counts": {
            "observed_rows": len(rows),
            "unique_openalex_ids": len(set(openalex_ids)),
            "unique_canonical_work_identities": len(set(canonical_ids)),
            "doi_rows": sum(row["doi"] is not None for row in rows),
            "arxiv_rows": sum(row["arxiv"] is not None for row in rows),
            "openalex_rows": sum(row["openalex"] is not None for row in rows),
            "fallback_rows": sum(row["fallback_sha256"] is not None for row in rows),
            "fallback_unavailable_rows": sum(row["fallback_sha256"] is None for row in rows),
            "selection_eligible_rows": sum(row["selection_eligible"] is True for row in rows),
        },
        "claim_boundary": {
            "registers_project_exposure": True,
            "reopens_goal5793": False,
            "constructs_complete_candidate_population": False,
            "supports_generalization_or_unseen_claim": False,
            "generalization_exam_count_added": 0,
            "usability_study_count_added": 0,
        },
        "authorization": {
            "network": False,
            "provider_rerun": False,
            "partial_page_science_use": False,
            "successor_selection": False,
            "candidate_work": False,
            "gpu_ssh_pod": False,
            "registered_or_performance_timing": False,
            "goal5803_entry_before_external_review": False,
        },
        "rows_sha256": _sha256(canonical_json_bytes(rows)),
        "registry_sha256": "",
    }
    expected_counts = {
        "observed_rows": 200,
        "unique_openalex_ids": 200,
        "unique_canonical_work_identities": 200,
        "doi_rows": 195,
        "arxiv_rows": 0,
        "openalex_rows": 200,
        "fallback_rows": 199,
        "fallback_unavailable_rows": 1,
        "selection_eligible_rows": 0,
    }
    if registry["counts"] != expected_counts:
        raise RegistryError(f"OBSERVED_IDENTITY_COUNTS_MISMATCH:{registry['counts']!r}")
    registry["registry_sha256"] = seal_document(
        registry,
        seal_field="registry_sha256",
        domain=DOMAIN,
        version=1,
    )
    return registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", type=Path, default=JOURNAL)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    registry = build_registry(args.journal)
    payload = canonical_json_bytes(registry) + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
        status = "CREATE_ONLY_WRITE_PASS"
    elif args.verify_stored:
        if not args.output.is_file() or args.output.is_symlink() or args.output.read_bytes() != payload:
            raise SystemExit("STORED_REGISTRY_MISMATCH")
        status = "POSTWRITE_VERIFY_PASS"
    else:
        status = "DRY_RUN_PASS"
    print(json.dumps({"status": status, "bytes": len(payload), "sha256": _sha256(payload)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
