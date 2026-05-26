from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


SEGMENTED_ROW_STREAM_CONTRACT_VERSION = "rtdl.segmented_row_stream.v1"
SEGMENTED_ROW_STREAM_PRIMITIVE = "SEGMENTED_ROW_STREAM"
CHUNKED_ROW_CONTINUATION_ALIAS = "CHUNKED_ROW_CONTINUATION"
SEGMENTED_ROW_STREAM_FAILURE_MODE = "fail_closed_overflow"
SEGMENTED_ROW_STREAM_DEFAULT_ID = "rtdl_segmented_row_stream"

SEGMENTED_ROW_STREAM_CONTRACT = {
    "primitive": SEGMENTED_ROW_STREAM_PRIMITIVE,
    "alias": CHUNKED_ROW_CONTINUATION_ALIAS,
    "version": SEGMENTED_ROW_STREAM_CONTRACT_VERSION,
    "layer": "continuation",
    "status": "internal_substrate",
    "behavior": (
        "page a generic row stream into deterministic chunks with opaque "
        "continuation tokens and no silent truncation"
    ),
    "inputs": ("row_schema", "rows", "page_capacity", "continuation_token"),
    "outputs": ("row_pages", "next_token", "complete_candidate_coverage"),
    "overflow_policy": "fail_closed_no_partial_result",
    "failure_mode": SEGMENTED_ROW_STREAM_FAILURE_MODE,
    "app_boundary": (
        "Rows carry typed fields and ids only; domain interpretation, scoring, "
        "and solver semantics remain app or partner code."
    ),
}


class SegmentedRowStreamOverflowError(RuntimeError):
    """Raised when exact segmented output would exceed an explicit capacity."""


@dataclass(frozen=True)
class SegmentedRowPage:
    """One deterministic page of a generic row stream."""

    stream_id: str
    page_index: int
    row_offset: int
    row_schema: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]
    page_capacity: int
    next_token: str | None
    complete_candidate_coverage: bool
    overflowed: bool = False
    failure_mode: str | None = None
    contract_version: str = SEGMENTED_ROW_STREAM_CONTRACT_VERSION
    primitive: str = SEGMENTED_ROW_STREAM_PRIMITIVE

    @property
    def valid_count(self) -> int:
        return len(self.rows)

    @property
    def end_offset(self) -> int:
        return self.row_offset + self.valid_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "primitive": self.primitive,
            "contract_version": self.contract_version,
            "stream_id": self.stream_id,
            "page_index": self.page_index,
            "row_offset": self.row_offset,
            "end_offset": self.end_offset,
            "row_schema": self.row_schema,
            "rows": self.rows,
            "valid_count": self.valid_count,
            "page_capacity": self.page_capacity,
            "next_token": self.next_token,
            "complete_candidate_coverage": self.complete_candidate_coverage,
            "overflowed": self.overflowed,
            "failure_mode": self.failure_mode,
        }


@dataclass(frozen=True)
class SegmentedRowStream:
    """A complete or explicitly windowed sequence of row pages."""

    stream_id: str
    row_schema: tuple[str, ...]
    page_capacity: int
    pages: tuple[SegmentedRowPage, ...]
    complete_candidate_coverage: bool
    overflowed: bool = False
    failure_mode: str | None = None
    contract_version: str = SEGMENTED_ROW_STREAM_CONTRACT_VERSION
    primitive: str = SEGMENTED_ROW_STREAM_PRIMITIVE

    @property
    def total_rows(self) -> int:
        return sum(page.valid_count for page in self.pages)

    @property
    def next_token(self) -> str | None:
        if not self.pages:
            return None
        return self.pages[-1].next_token

    def to_dict(self) -> dict[str, Any]:
        return {
            "primitive": self.primitive,
            "contract_version": self.contract_version,
            "stream_id": self.stream_id,
            "row_schema": self.row_schema,
            "page_capacity": self.page_capacity,
            "pages": tuple(page.to_dict() for page in self.pages),
            "total_rows": self.total_rows,
            "page_count": len(self.pages),
            "next_token": self.next_token,
            "complete_candidate_coverage": self.complete_candidate_coverage,
            "overflowed": self.overflowed,
            "failure_mode": self.failure_mode,
        }


def segmented_row_stream_contract() -> dict[str, Any]:
    """Return serializable metadata for the generic segmented row stream."""

    return dict(SEGMENTED_ROW_STREAM_CONTRACT)


def make_segmented_row_token(stream_id: str, row_offset: int) -> str:
    """Create an opaque, deterministic continuation token."""

    normalized_stream_id = _normalize_stream_id(stream_id)
    normalized_offset = int(row_offset)
    if normalized_offset < 0:
        raise ValueError("row_offset must be non-negative")
    return f"{normalized_stream_id}:{normalized_offset}"


def parse_segmented_row_token(
    continuation_token: str | None,
    *,
    stream_id: str,
) -> int:
    """Parse a continuation token and return its row offset."""

    if continuation_token is None:
        return 0
    normalized_stream_id = _normalize_stream_id(stream_id)
    prefix = f"{normalized_stream_id}:"
    if not continuation_token.startswith(prefix):
        raise ValueError("continuation_token does not belong to this stream_id")
    offset_text = continuation_token[len(prefix) :]
    try:
        row_offset = int(offset_text)
    except ValueError as exc:
        raise ValueError("continuation_token row offset must be an integer") from exc
    if row_offset < 0:
        raise ValueError("continuation_token row offset must be non-negative")
    return row_offset


def emit_segmented_row_page(
    rows: Iterable[Iterable[Any]],
    *,
    row_schema: Iterable[str],
    page_capacity: int,
    continuation_token: str | None = None,
    stream_id: str = SEGMENTED_ROW_STREAM_DEFAULT_ID,
    total_row_capacity: int | None = None,
) -> SegmentedRowPage:
    """Emit one page of a generic row stream.

    This CPU/reference helper intentionally exposes the runtime contract before
    native backends adopt it. It never silently truncates exact output: if an
    explicit ``total_row_capacity`` is exceeded, it raises a fail-closed error
    before returning any page.
    """

    schema = _normalize_row_schema(row_schema)
    page_size = _normalize_page_capacity(page_capacity)
    row_tuple = _normalize_rows(rows, schema)
    _enforce_total_capacity(row_tuple, total_row_capacity)
    normalized_stream_id = _normalize_stream_id(stream_id)
    offset = parse_segmented_row_token(
        continuation_token,
        stream_id=normalized_stream_id,
    )
    if offset % page_size != 0:
        raise ValueError("continuation_token row offset must align with page_capacity")
    if offset > len(row_tuple):
        raise ValueError("continuation_token row offset exceeds row count")

    page_rows = row_tuple[offset : offset + page_size]
    next_offset = offset + len(page_rows)
    next_token = (
        make_segmented_row_token(normalized_stream_id, next_offset)
        if next_offset < len(row_tuple)
        else None
    )
    page_index = offset // page_size
    return SegmentedRowPage(
        stream_id=normalized_stream_id,
        page_index=page_index,
        row_offset=offset,
        row_schema=schema,
        rows=page_rows,
        page_capacity=page_size,
        next_token=next_token,
        complete_candidate_coverage=next_token is None,
    )


def emit_segmented_row_stream(
    rows: Iterable[Iterable[Any]],
    *,
    row_schema: Iterable[str],
    page_capacity: int,
    stream_id: str = SEGMENTED_ROW_STREAM_DEFAULT_ID,
    total_row_capacity: int | None = None,
    max_pages: int | None = None,
) -> SegmentedRowStream:
    """Emit row pages until the stream is complete or an explicit page limit is hit."""

    schema = _normalize_row_schema(row_schema)
    page_size = _normalize_page_capacity(page_capacity)
    if max_pages is not None and int(max_pages) < 1:
        raise ValueError("max_pages must be positive when provided")
    row_tuple = _normalize_rows(rows, schema)
    _enforce_total_capacity(row_tuple, total_row_capacity)
    normalized_stream_id = _normalize_stream_id(stream_id)

    pages: list[SegmentedRowPage] = []
    token: str | None = None
    while True:
        if max_pages is not None and len(pages) >= int(max_pages):
            break
        page = emit_segmented_row_page(
            row_tuple,
            row_schema=schema,
            page_capacity=page_size,
            continuation_token=token,
            stream_id=normalized_stream_id,
            total_row_capacity=total_row_capacity,
        )
        pages.append(page)
        token = page.next_token
        if token is None:
            break

    complete = bool(pages) and pages[-1].next_token is None
    return SegmentedRowStream(
        stream_id=normalized_stream_id,
        row_schema=schema,
        page_capacity=page_size,
        pages=tuple(pages),
        complete_candidate_coverage=complete,
    )


def reconstruct_segmented_row_stream(
    pages: Iterable[SegmentedRowPage | dict[str, Any]],
    *,
    require_complete: bool = True,
) -> tuple[tuple[Any, ...], ...]:
    """Validate pages and reconstruct rows in stream order."""

    page_tuple = tuple(_normalize_page(page) for page in pages)
    validation = validate_segmented_row_pages(page_tuple)
    if require_complete and not validation["complete_candidate_coverage"]:
        raise ValueError("segmented row stream is incomplete; continuation_token remains")

    reconstructed: list[tuple[Any, ...]] = []
    for page in page_tuple:
        reconstructed.extend(page.rows)
    return tuple(reconstructed)


def validate_segmented_row_pages(
    pages: Iterable[SegmentedRowPage | dict[str, Any]],
) -> dict[str, Any]:
    """Validate page contiguity, schema consistency, and completion metadata."""

    page_tuple = tuple(_normalize_page(page) for page in pages)
    if not page_tuple:
        raise ValueError("segmented row stream requires at least one page")

    stream_id = page_tuple[0].stream_id
    schema = page_tuple[0].row_schema
    page_capacity = page_tuple[0].page_capacity
    expected_offset = 0
    for expected_index, page in enumerate(page_tuple):
        if page.stream_id != stream_id:
            raise ValueError("segmented row pages mix stream_id values")
        if page.row_schema != schema:
            raise ValueError("segmented row pages mix row schemas")
        if page.page_capacity != page_capacity:
            raise ValueError("segmented row pages mix page capacities")
        if page.page_index != expected_index:
            raise ValueError("segmented row page_index values must be contiguous")
        if page.row_offset != expected_offset:
            raise ValueError("segmented row row_offset values must be contiguous")
        if page.valid_count > page.page_capacity:
            raise ValueError("segmented row page exceeds page_capacity")
        if page.next_token is not None:
            next_offset = parse_segmented_row_token(page.next_token, stream_id=stream_id)
            if next_offset != page.end_offset:
                raise ValueError("segmented row next_token must point to page end_offset")
        for row in page.rows:
            if len(row) != len(schema):
                raise ValueError("segmented row width does not match row_schema")
        expected_offset = page.end_offset

    complete = page_tuple[-1].next_token is None
    for page in page_tuple[:-1]:
        if page.next_token is None:
            raise ValueError("non-final segmented row page cannot terminate stream")
        if page.complete_candidate_coverage:
            raise ValueError("non-final segmented row page cannot claim complete coverage")
    if page_tuple[-1].complete_candidate_coverage != complete:
        raise ValueError("final segmented row page completion flag mismatch")

    return {
        "primitive": SEGMENTED_ROW_STREAM_PRIMITIVE,
        "contract_version": SEGMENTED_ROW_STREAM_CONTRACT_VERSION,
        "valid": True,
        "stream_id": stream_id,
        "row_schema": schema,
        "page_capacity": page_capacity,
        "page_count": len(page_tuple),
        "total_rows": expected_offset,
        "complete_candidate_coverage": complete,
        "next_token": page_tuple[-1].next_token,
        "overflowed": any(page.overflowed for page in page_tuple),
        "failure_mode": (
            SEGMENTED_ROW_STREAM_FAILURE_MODE
            if any(page.overflowed for page in page_tuple)
            else None
        ),
    }


def _normalize_stream_id(stream_id: str) -> str:
    normalized = str(stream_id)
    if not normalized:
        raise ValueError("stream_id must be non-empty")
    if ":" in normalized:
        raise ValueError("stream_id must not contain ':'")
    return normalized


def _normalize_page_capacity(page_capacity: int) -> int:
    normalized = int(page_capacity)
    if normalized < 1:
        raise ValueError("page_capacity must be positive")
    return normalized


def _normalize_total_capacity(total_row_capacity: int | None) -> int | None:
    if total_row_capacity is None:
        return None
    normalized = int(total_row_capacity)
    if normalized < 0:
        raise ValueError("total_row_capacity must be non-negative")
    return normalized


def _normalize_row_schema(row_schema: Iterable[str]) -> tuple[str, ...]:
    schema = tuple(str(field) for field in row_schema)
    if not schema:
        raise ValueError("row_schema must be non-empty")
    if any(not field for field in schema):
        raise ValueError("row_schema field names must be non-empty")
    if len(set(schema)) != len(schema):
        raise ValueError("row_schema field names must be unique")
    return schema


def _normalize_rows(
    rows: Iterable[Iterable[Any]],
    row_schema: tuple[str, ...],
) -> tuple[tuple[Any, ...], ...]:
    normalized_rows: list[tuple[Any, ...]] = []
    for row in rows:
        normalized = tuple(row)
        if len(normalized) != len(row_schema):
            raise ValueError("row width must match row_schema")
        normalized_rows.append(normalized)
    return tuple(normalized_rows)


def _enforce_total_capacity(
    rows: tuple[tuple[Any, ...], ...],
    total_row_capacity: int | None,
) -> None:
    capacity = _normalize_total_capacity(total_row_capacity)
    if capacity is not None and len(rows) > capacity:
        raise SegmentedRowStreamOverflowError(
            "SEGMENTED_ROW_STREAM overflow: "
            f"row_count={len(rows)} total_row_capacity={capacity} "
            f"failure_mode={SEGMENTED_ROW_STREAM_FAILURE_MODE} "
            "partial_result_returned=False"
        )


def _normalize_page(page: SegmentedRowPage | dict[str, Any]) -> SegmentedRowPage:
    if isinstance(page, SegmentedRowPage):
        return page
    return SegmentedRowPage(
        stream_id=str(page["stream_id"]),
        page_index=int(page["page_index"]),
        row_offset=int(page["row_offset"]),
        row_schema=tuple(str(field) for field in page["row_schema"]),
        rows=tuple(tuple(row) for row in page["rows"]),
        page_capacity=int(page["page_capacity"]),
        next_token=page.get("next_token"),
        complete_candidate_coverage=bool(page["complete_candidate_coverage"]),
        overflowed=bool(page.get("overflowed", False)),
        failure_mode=page.get("failure_mode"),
        contract_version=str(
            page.get("contract_version", SEGMENTED_ROW_STREAM_CONTRACT_VERSION)
        ),
        primitive=str(page.get("primitive", SEGMENTED_ROW_STREAM_PRIMITIVE)),
    )


__all__ = [
    "CHUNKED_ROW_CONTINUATION_ALIAS",
    "SEGMENTED_ROW_STREAM_CONTRACT",
    "SEGMENTED_ROW_STREAM_CONTRACT_VERSION",
    "SEGMENTED_ROW_STREAM_DEFAULT_ID",
    "SEGMENTED_ROW_STREAM_FAILURE_MODE",
    "SEGMENTED_ROW_STREAM_PRIMITIVE",
    "SegmentedRowPage",
    "SegmentedRowStream",
    "SegmentedRowStreamOverflowError",
    "emit_segmented_row_page",
    "emit_segmented_row_stream",
    "make_segmented_row_token",
    "parse_segmented_row_token",
    "reconstruct_segmented_row_stream",
    "segmented_row_stream_contract",
    "validate_segmented_row_pages",
]
