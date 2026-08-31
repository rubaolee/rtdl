#!/usr/bin/env python3
"""Frozen PDF identity extractor used by the offline X2 source resolver."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import re
from typing import Any, Mapping

import pypdf

try:
    from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
    from scripts.goal5793_x2_offline_core import X2Error, normalize_arxiv, normalize_doi, normalize_https_url, normalize_text
except ModuleNotFoundError:
    from goal5793_x1_canonical import canonical_json_bytes, seal_document  # type: ignore
    from goal5793_x2_offline_core import X2Error, normalize_arxiv, normalize_doi, normalize_https_url, normalize_text  # type: ignore


PYPDF_VERSION = "6.14.2"
PYPDF_FILE_COUNT = 56
PYPDF_TOTAL_BYTES = 1_486_221
PYPDF_ROWS_SHA256 = "3df52f80b93fbcb44dd793e0ba27ee2438ad7cf06de7ab355e1755c0078a9bd1"
MAX_PDF_BYTES = 50_000_000
MAX_PAGES = 5000
MAX_EXTRACTED_UTF8_BYTES = 50_000_000


def _package_rows() -> list[dict[str, Any]]:
    root = Path(pypdf.__file__).resolve().parent
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix().encode("utf-8")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        data = path.read_bytes()
        rows.append({"path": path.relative_to(root).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return rows


def parser_authority() -> dict[str, Any]:
    rows = _package_rows()
    version = pypdf.__version__
    summary = {
        "version": version,
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "rows_sha256": hashlib.sha256(canonical_json_bytes(rows)).hexdigest(),
    }
    if summary != {
        "version": PYPDF_VERSION,
        "file_count": PYPDF_FILE_COUNT,
        "total_bytes": PYPDF_TOTAL_BYTES,
        "rows_sha256": PYPDF_ROWS_SHA256,
    }:
        raise X2Error("PDF_PARSER_AUTHORITY_IDENTITY_MISMATCH")
    return {"package": "pypdf", **summary, "rows": rows, "network_calls": 0}


def _annotation_urls(reader: pypdf.PdfReader) -> list[str]:
    rows: list[str] = []
    seen: set[str] = set()
    for page in reader.pages:
        annotations = page.get("/Annots") or []
        for reference in annotations:
            try:
                annotation = reference.get_object()
                action = annotation.get("/A")
                value = action.get("/URI") if action is not None else None
            except Exception:
                continue
            if not isinstance(value, str):
                continue
            try:
                url = normalize_https_url(value)
            except X2Error:
                continue
            if url not in seen:
                rows.append(url)
                seen.add(url)
    return rows


def _strong_ids(text: str) -> tuple[list[str], list[str]]:
    dois: set[str] = set()
    for match in re.findall(r"(?i)\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text):
        candidate = match.rstrip(".,;:)]}")
        try:
            normalized = normalize_doi(candidate)
        except X2Error:
            continue
        if normalized is not None:
            dois.add(normalized)
    arxivs: set[str] = set()
    for match in re.findall(r"(?i)(?:arxiv\s*:\s*|arxiv\.org/(?:abs|pdf)/)([a-z-]+(?:\.[a-z-]+)?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?", text):
        try:
            normalized = normalize_arxiv(match)
        except X2Error:
            continue
        if normalized is not None:
            arxivs.add(normalized)
    return sorted(dois), sorted(arxivs)


def extract_pdf_identity(pdf_bytes: bytes, component: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(pdf_bytes, bytes) or not pdf_bytes.startswith(b"%PDF-") or len(pdf_bytes) > MAX_PDF_BYTES:
        raise X2Error("PDF_BYTES_INVALID_OR_LIMIT_EXCEEDED")
    parser = parser_authority()
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes), strict=True)
    except Exception as exc:
        raise X2Error("PDF_PARSE_FAILED") from exc
    if reader.is_encrypted:
        raise X2Error("PDF_ENCRYPTED_UNSUPPORTED__SOURCE_GAP")
    if not 1 <= len(reader.pages) <= MAX_PAGES:
        raise X2Error("PDF_PAGE_COUNT_INVALID_OR_LIMIT_EXCEEDED")
    metadata = reader.metadata or {}
    text_parts = [str(metadata.get(key) or "") for key in ("/Title", "/Author", "/Subject", "/Keywords")]
    try:
        text_parts.extend(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise X2Error("PDF_TEXT_EXTRACTION_FAILED") from exc
    extracted_text = "\n".join(text_parts)
    text_bytes = extracted_text.encode("utf-8")
    if len(text_bytes) > MAX_EXTRACTED_UTF8_BYTES:
        raise X2Error("PDF_EXTRACTED_TEXT_LIMIT_EXCEEDED")
    normalized = normalize_text(extracted_text)
    observed_dois, observed_arxivs = _strong_ids(extracted_text)
    expected_dois = set(component.get("doi") or [])
    expected_arxivs = set(component.get("arxiv") or [])
    strong_match = bool(expected_dois & set(observed_dois) or expected_arxivs & set(observed_arxivs))
    titles = [value for value in component.get("title", []) if isinstance(value, str) and value]
    authors = [value for value in component.get("first_author", []) if isinstance(value, str) and value]
    years = [value for value in component.get("year", []) if type(value) is int]
    title_match = any(normalize_text(title) in normalized for title in titles)
    author_match = any(normalize_text(author) in normalized.split() for author in authors)
    year_match = any(str(year) in normalized.split() for year in years)
    fallback_match = bool(title_match and author_match and year_match)
    matched = bool(strong_match or fallback_match)
    receipt: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.pdf_identity_receipt.v1",
        "status": "PDF_IDENTITY_MATCH" if matched else "PDF_IDENTITY_MISMATCH__SOURCE_GAP__NO_MANUAL_SUBSTITUTION",
        "pdf": {"bytes": len(pdf_bytes), "sha256": hashlib.sha256(pdf_bytes).hexdigest(), "pages": len(reader.pages)},
        "parser_authority": {key: parser[key] for key in ("package", "version", "file_count", "total_bytes", "rows_sha256")},
        "extraction": {
            "utf8_bytes": len(text_bytes), "text_sha256": hashlib.sha256(text_bytes).hexdigest(),
            "observed_doi": observed_dois, "observed_arxiv": observed_arxivs,
            "annotation_urls_in_object_order": _annotation_urls(reader),
        },
        "identity_checks": {
            "strong_identifier_match": strong_match, "normalized_title_match": title_match,
            "first_author_family_match": author_match, "publication_year_match": year_match,
            "fallback_title_author_year_match": fallback_match, "matched": matched,
        },
        "manual_version_or_paper_choice_allowed": False,
        "network_calls": 0,
        "receipt_sha256": "",
    }
    receipt["receipt_sha256"] = seal_document(
        receipt, seal_field="receipt_sha256", domain="rtdl.goal5793.x2.pdf_identity_receipt", version=1
    )
    return receipt
