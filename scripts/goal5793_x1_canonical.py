"""Canonical JSON and domain-separated digest helpers for Goal5793 X1.

This helper applies only to new Goal5793 successor artifacts.  Historical
Goal5789-A1, Goal5789-A2, and Goal5793-S0 seals keep their original conventions.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable, Mapping


CANONICALIZATION_NAME = (
    "UTF8_SORTED_KEYS_COMPACT_ENSURE_ASCII_FALSE_ALLOW_NAN_FALSE_"
    "NO_TRAILING_NEWLINE_V1"
)


def canonical_json_bytes(value: Any) -> bytes:
    """Return the single X1 canonical JSON representation."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_digest(
    value: Any,
    *,
    domain: str,
    version: int,
    projection: str,
) -> dict[str, Any]:
    """Digest an explicitly named projection under an explicit domain.

    Domain metadata is part of the hashed body so two equal JSON projections
    used for different scientific purposes cannot silently share an identity.
    """

    if not isinstance(domain, str) or not domain:
        raise ValueError("domain must be a nonempty string")
    if type(version) is not int or version < 1:
        raise ValueError("version must be a positive plain integer")
    if not isinstance(projection, str) or not projection:
        raise ValueError("projection must be a nonempty string")
    body = {
        "canonicalization": CANONICALIZATION_NAME,
        "domain": domain,
        "projection": projection,
        "value": value,
        "version": version,
    }
    encoded = canonical_json_bytes(body)
    return {
        "algorithm": "sha256",
        "canonicalization": CANONICALIZATION_NAME,
        "canonical_bytes": len(encoded),
        "domain": domain,
        "projection": projection,
        "sha256": sha256_bytes(encoded),
        "version": version,
    }


def seal_document(
    document: Mapping[str, Any],
    *,
    seal_field: str,
    domain: str,
    version: int,
) -> str:
    """Seal a document after removing exactly one named self-seal field."""

    if not isinstance(seal_field, str) or not seal_field:
        raise ValueError("seal_field must be a nonempty string")
    body = dict(document)
    body.pop(seal_field, None)
    digest_record = canonical_digest(
        body,
        domain=domain,
        version=version,
        projection=f"document_without:{seal_field}",
    )
    return str(digest_record["sha256"])


def project_rows(
    rows: list[Mapping[str, Any]],
    projector: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Project rows without sorting or deduplication.

    Callers must define ordering and duplicate rules before hashing; this helper
    deliberately refuses to invent set semantics.
    """

    if not isinstance(rows, list):
        raise TypeError("rows must be a list")
    return [dict(projector(row)) for row in rows]

