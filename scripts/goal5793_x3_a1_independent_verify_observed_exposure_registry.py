#!/usr/bin/env python3
"""Independent identity recount for Goal5793 X3's observed-work registry.

This verifier deliberately does not import the registry builder or the X2
normalization implementation.  It reimplements the frozen S0 identity
projection from the protocol text.  It shares only the reviewed canonical
document-seal helper, avoiding another handwritten seal framing.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
JOURNAL = ROOT / "history/internal_docs/goal5793_x3_provider_search_journal_20260822.jsonl"
REGISTRY = ROOT / "history/internal_docs/goal5793_x3_a1_observed_work_exposure_registry_20260824.json"
OUTPUT = ROOT / "history/internal_docs/goal5793_x3_a1_observed_work_exposure_registry_independent_verification_20260824.json"
JOURNAL_SHA256 = "94ab0fc951c728569c0d57f649de918feeb547a8f4dac0ea48ec43f176b7e4c5"
BODY_SHA256 = "453fbab3bf25b84986fa593b80e6e12451619ed24b2c189dc717e643253d874d"
REGISTRY_DOMAIN = "rtdl.goal5793.x3.a1.observed_work_exposure_registry.v1"
VERIFY_DOMAIN = "rtdl.goal5793.x3.a1.observed_work_exposure_registry_independent_verification.v1"


class VerificationError(ValueError):
    """Stable fail-closed verification error."""


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _normalize_text(value: str) -> str:
    if not isinstance(value, str):
        raise VerificationError("TEXT_SCHEMA_INVALID")
    text = html.unescape(value)
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^\]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ").replace("&", " and ")
    text = unicodedata.normalize("NFKC", text).casefold()
    text = "".join(ch if ch.isalnum() else " " for ch in text)
    return " ".join(text.split())


def _normalize_author(value: str) -> str:
    text = _normalize_text(value)
    if not text:
        return ""
    if "," in value:
        family = _normalize_text(value.split(",", 1)[0])
        return family.split()[-1] if family else ""
    return text.split()[-1]


def _doi(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise VerificationError("DOI_SCHEMA_INVALID")
    text = re.sub(r"(?i)^doi:\s*", "", value.strip(), count=1)
    text = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", text, count=1).strip().lower()
    if not text or re.search(r"\s", text) or not text.startswith("10.") or "/" not in text:
        raise VerificationError("DOI_SCHEMA_INVALID")
    return text


def _arxiv(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise VerificationError("ARXIV_SCHEMA_INVALID")
    text = value.strip().lower()
    text = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", text)
    text = re.sub(r"(?i)^arxiv:\s*", "", text).removesuffix(".pdf")
    text = re.sub(r"v[0-9]+$", "", text)
    if re.fullmatch(r"(?:[a-z-]+(?:\.[a-z-]+)?/\d{7}|\d{4}\.\d{4,5})", text) is None:
        raise VerificationError("ARXIV_SCHEMA_INVALID")
    return text


def _openalex(value: Any) -> str:
    if not isinstance(value, str):
        raise VerificationError("OPENALEX_SCHEMA_INVALID")
    match = re.search(r"(?i)(?:^|/)(W[0-9]+)$", value.strip())
    if match is None:
        raise VerificationError("OPENALEX_SCHEMA_INVALID")
    return match.group(1).upper()


def _fallback(title: str, first_author: str, year: int) -> str:
    return _sha(_canonical({
        "first_author": _normalize_author(first_author),
        "title": _normalize_text(title),
        "year": year,
    }))


def _journal_body(journal_path: Path) -> tuple[bytes, Mapping[str, Any]]:
    payload = journal_path.read_bytes()
    if _sha(payload) != JOURNAL_SHA256:
        raise VerificationError("JOURNAL_SHA256_MISMATCH")
    lines = [json.loads(line) for line in payload.decode("utf-8", errors="strict").splitlines()]
    if [line.get("event") for line in lines] != ["TRANSACTION_START", "HTTP_ATTEMPT", "TRANSACTION_TERMINAL_FAILURE"]:
        raise VerificationError("JOURNAL_EVENTS_MISMATCH")
    body = base64.b64decode(lines[1]["attempt"]["body_base64"], validate=True)
    if _sha(body) != BODY_SHA256:
        raise VerificationError("BODY_SHA256_MISMATCH")
    decoded = json.loads(body)
    if len(decoded.get("results", [])) != 200:
        raise VerificationError("BODY_RESULT_COUNT_MISMATCH")
    return body, decoded


def _expected_row(work: Mapping[str, Any], ordinal: int) -> dict[str, Any]:
    ids = work.get("ids") if isinstance(work.get("ids"), Mapping) else {}
    doi = _doi(work.get("doi") or ids.get("doi"))
    arxiv = _arxiv(ids.get("arxiv"))
    openalex = _openalex(work.get("id") or ids.get("openalex"))
    authorships = work.get("authorships")
    if not isinstance(authorships, list) or not authorships:
        raise VerificationError("FIRST_AUTHOR_MISSING")
    first_author = authorships[0]["author"]["display_name"]
    year = work.get("publication_year")
    if type(year) is not int:
        raise VerificationError("YEAR_INVALID")
    title = work.get("title")
    if isinstance(title, str) and title:
        fallback = _fallback(title, first_author, year)
        title_normalized = _normalize_text(title)
        fallback_reason = None
    else:
        fallback = None
        title_normalized = None
        fallback_reason = "TITLE_MISSING_IN_OBSERVED_PROVIDER_BYTES__NO_SYNTHETIC_SUBSTITUTE"
    aliases = [
        {"kind": kind, "value": value}
        for kind, value in (("doi", doi), ("arxiv", arxiv), ("openalex", openalex), ("fallback_sha256", fallback))
        if value is not None
    ]
    canonical_identity = (
        f"doi:{doi}" if doi is not None else
        f"arxiv:{arxiv}" if arxiv is not None else
        f"openalex:{openalex}" if openalex is not None else
        f"fallback_sha256:{fallback}"
    )
    return {
        "ordinal": ordinal,
        "record_sha256": _sha(_canonical(work)),
        "canonical_work_identity": canonical_identity,
        "doi": doi,
        "arxiv": arxiv,
        "openalex": openalex,
        "fallback_sha256": fallback,
        "fallback_unavailable_reason": fallback_reason,
        "title_normalized": title_normalized,
        "first_author_family_normalized": _normalize_author(first_author),
        "year": year,
        "aliases": aliases,
        "observed_in_goal5793_x3_terminal_page": True,
        "selection_eligible": False,
        "exclusion_reason": "OBSERVED_BY_PROJECT_BEFORE_ANY_SUCCESSOR_SELECTION__PERMANENTLY_INELIGIBLE",
    }


def verify_registry_document(
    registry: Mapping[str, Any],
    *,
    journal_path: Path = JOURNAL,
) -> dict[str, Any]:
    required = {
        "schema", "date", "status", "source", "identity_protocol", "rows", "counts",
        "claim_boundary", "authorization", "rows_sha256", "registry_sha256",
    }
    if set(registry) != required:
        raise VerificationError("REGISTRY_TOP_LEVEL_SCHEMA_MISMATCH")
    if registry["schema"] != "rtdl.goal5793.x3.a1.observed_work_exposure_registry.v1":
        raise VerificationError("REGISTRY_SCHEMA_MISMATCH")
    _, decoded = _journal_body(journal_path)
    expected_rows = [_expected_row(work, ordinal) for ordinal, work in enumerate(decoded["results"])]
    if registry["rows"] != expected_rows:
        raise VerificationError("REGISTRY_ROWS_MISMATCH")
    if registry["rows_sha256"] != _sha(canonical_json_bytes(expected_rows)):
        raise VerificationError("REGISTRY_ROWS_SEAL_MISMATCH")
    expected_seal = seal_document(
        registry,
        seal_field="registry_sha256",
        domain=REGISTRY_DOMAIN,
        version=1,
    )
    if registry["registry_sha256"] != expected_seal:
        raise VerificationError("REGISTRY_DOCUMENT_SEAL_MISMATCH")
    counts = {
        "observed_rows": len(expected_rows),
        "unique_openalex_ids": len({row["openalex"] for row in expected_rows}),
        "unique_canonical_work_identities": len({row["canonical_work_identity"] for row in expected_rows}),
        "doi_rows": sum(row["doi"] is not None for row in expected_rows),
        "arxiv_rows": sum(row["arxiv"] is not None for row in expected_rows),
        "openalex_rows": sum(row["openalex"] is not None for row in expected_rows),
        "fallback_rows": sum(row["fallback_sha256"] is not None for row in expected_rows),
        "fallback_unavailable_rows": sum(row["fallback_sha256"] is None for row in expected_rows),
        "selection_eligible_rows": sum(row["selection_eligible"] is True for row in expected_rows),
    }
    if registry["counts"] != counts:
        raise VerificationError("REGISTRY_COUNTS_MISMATCH")
    if counts != {
        "observed_rows": 200,
        "unique_openalex_ids": 200,
        "unique_canonical_work_identities": 200,
        "doi_rows": 195,
        "arxiv_rows": 0,
        "openalex_rows": 200,
        "fallback_rows": 199,
        "fallback_unavailable_rows": 1,
        "selection_eligible_rows": 0,
    }:
        raise VerificationError("REGISTRY_FROZEN_COUNT_VECTOR_MISMATCH")
    return {
        "counts": counts,
        "rows_sha256": registry["rows_sha256"],
        "registry_sha256": registry["registry_sha256"],
    }


def build_verification(registry_path: Path = REGISTRY, journal_path: Path = JOURNAL) -> dict[str, Any]:
    registry_payload = registry_path.read_bytes()
    registry = json.loads(registry_payload)
    result = verify_registry_document(registry, journal_path=journal_path)
    verification: dict[str, Any] = {
        "schema": "rtdl.goal5793.x3.a1.observed_work_exposure_registry_independent_verification.v1",
        "date": "2026-08-24",
        "status": "PASS__INDEPENDENT_IDENTITY_RECOUNT_EXACT",
        "independence": {
            "imports_registry_builder": False,
            "imports_x2_normalization_implementation": False,
            "shares_reviewed_document_seal_helper_only": True,
            "network_call_count": 0,
        },
        "source": {
            "journal_sha256": JOURNAL_SHA256,
            "response_body_sha256": BODY_SHA256,
            "registry_file_sha256": _sha(registry_payload),
            "registry_file_bytes": len(registry_payload),
        },
        "result": result,
        "authorization": {
            "provider_rerun": False,
            "selection": False,
            "candidate_work": False,
            "goal5803_entry": False,
        },
        "verification_sha256": "",
    }
    verification["verification_sha256"] = seal_document(
        verification,
        seal_field="verification_sha256",
        domain=VERIFY_DOMAIN,
        version=1,
    )
    return verification


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", type=Path, default=JOURNAL)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    document = build_verification(args.registry, args.journal)
    payload = canonical_json_bytes(document) + b"\n"
    if args.write_create_only:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(payload)
        status = "CREATE_ONLY_WRITE_PASS"
    elif args.verify_stored:
        if not args.output.is_file() or args.output.is_symlink() or args.output.read_bytes() != payload:
            raise SystemExit("STORED_VERIFICATION_MISMATCH")
        status = "POSTWRITE_VERIFY_PASS"
    else:
        status = "DRY_RUN_PASS"
    print(json.dumps({"status": status, "bytes": len(payload), "sha256": _sha(payload)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
