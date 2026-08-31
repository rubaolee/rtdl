"""Generic paged recovery helpers for bounded pair-column streams.

This module is intentionally independent of any application or geometry
domain. It describes caller-visible pages, fail-closed retry metadata, and
key-addition merging for grouped summaries produced from pair-column streams.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence


PAIR_COLUMN_PAGED_RECOVERY_SCHEMA = "rtdl.pair_column_paged_recovery.v1"
PAIR_COLUMN_PAGED_RECOVERY_OVERFLOW_POLICY = "fail_closed_explicit_retry"
PAIR_COLUMN_PAGED_RECOVERY_MERGE_RULE = "key_addition"


@dataclass(frozen=True)
class PairColumnPageRequest:
    page_index: int
    start: int
    stop: int
    initial_capacity: int

    def __post_init__(self) -> None:
        if int(self.page_index) < 0:
            raise ValueError("page_index must be non-negative")
        if int(self.start) < 0:
            raise ValueError("page start must be non-negative")
        if int(self.stop) < int(self.start):
            raise ValueError("page stop must be greater than or equal to start")
        if int(self.initial_capacity) < 0:
            raise ValueError("initial_capacity must be non-negative")

    @property
    def item_count(self) -> int:
        return int(self.stop) - int(self.start)

    def slice(self, values: Sequence[object]) -> Sequence[object]:
        return values[int(self.start) : int(self.stop)]

    def to_metadata(self) -> dict[str, object]:
        return {
            "page_index": int(self.page_index),
            "start": int(self.start),
            "stop": int(self.stop),
            "item_count": int(self.item_count),
            "initial_capacity": int(self.initial_capacity),
        }


@dataclass(frozen=True)
class PairColumnPagedRecoveryContract:
    page_size: int
    initial_capacity: int
    overflow_policy: str = PAIR_COLUMN_PAGED_RECOVERY_OVERFLOW_POLICY
    merge_rule: str = PAIR_COLUMN_PAGED_RECOVERY_MERGE_RULE
    windows_are_caller_visible: bool = True
    native_paged_stream_implemented: bool = False
    automatic_retry_authorized: bool = False
    hidden_dispatch_authorized: bool = False
    merge_requires_disjoint_keys: bool = False

    def __post_init__(self) -> None:
        if int(self.page_size) <= 0:
            raise ValueError("page_size must be positive")
        if int(self.initial_capacity) < 0:
            raise ValueError("initial_capacity must be non-negative")
        if self.overflow_policy != PAIR_COLUMN_PAGED_RECOVERY_OVERFLOW_POLICY:
            raise ValueError("paged recovery currently supports only fail-closed explicit retry")
        if self.merge_rule != PAIR_COLUMN_PAGED_RECOVERY_MERGE_RULE:
            raise ValueError("paged recovery currently supports only key-addition merge")
        if not bool(self.windows_are_caller_visible):
            raise ValueError("paged recovery pages must be caller visible")
        if bool(self.native_paged_stream_implemented):
            raise ValueError("this helper is not a native paged stream implementation")
        if bool(self.automatic_retry_authorized):
            raise ValueError("automatic retry is not authorized by this contract")
        if bool(self.hidden_dispatch_authorized):
            raise ValueError("hidden dispatch is not authorized by this contract")
        if bool(self.merge_requires_disjoint_keys):
            raise ValueError("paged recovery must not require disjoint group keys")

    def to_metadata(self) -> dict[str, object]:
        return {
            "schema": PAIR_COLUMN_PAGED_RECOVERY_SCHEMA,
            "page_size": int(self.page_size),
            "initial_capacity": int(self.initial_capacity),
            "overflow_policy": self.overflow_policy,
            "merge_rule": self.merge_rule,
            "windows_are_caller_visible": bool(self.windows_are_caller_visible),
            "native_paged_stream_implemented": bool(self.native_paged_stream_implemented),
            "automatic_retry_authorized": bool(self.automatic_retry_authorized),
            "hidden_dispatch_authorized": bool(self.hidden_dispatch_authorized),
            "merge_requires_disjoint_keys": bool(self.merge_requires_disjoint_keys),
        }


@dataclass(frozen=True)
class PairColumnPageRecoveryRecord:
    request: PairColumnPageRequest
    first_capacity_status: Mapping[str, object]
    retry_used: bool
    retry_capacity_hint: int | None
    recovered_capacity_status: Mapping[str, object]
    grouped_source_row_count: int
    grouped_row_count: int
    grouped_overflow: bool
    device_group_count: int
    host_exact_rows: int | None = None

    def __post_init__(self) -> None:
        if int(self.grouped_source_row_count) < 0:
            raise ValueError("grouped_source_row_count must be non-negative")
        if int(self.grouped_row_count) < 0:
            raise ValueError("grouped_row_count must be non-negative")
        if int(self.device_group_count) < 0:
            raise ValueError("device_group_count must be non-negative")
        if self.host_exact_rows is not None and int(self.host_exact_rows) < 0:
            raise ValueError("host_exact_rows must be non-negative")
        if bool(self.retry_used):
            if self.retry_capacity_hint is None or int(self.retry_capacity_hint) < 0:
                raise ValueError("retried pages must carry retry_capacity_hint")
            if not bool(self.first_capacity_status.get("overflowed")):
                raise ValueError("retried pages must start from an overflowed fail-closed status")
        elif self.retry_capacity_hint is not None:
            raise ValueError("non-retried pages must not carry retry_capacity_hint")
        if bool(self.recovered_capacity_status.get("overflowed")):
            raise ValueError("recovered page status must not overflow")
        if bool(self.grouped_overflow):
            raise ValueError("grouped page continuation must not overflow")

    def to_metadata(self) -> dict[str, object]:
        metadata = self.request.to_metadata()
        metadata.update(
            {
                "host_exact_rows": None if self.host_exact_rows is None else int(self.host_exact_rows),
                "first_capacity_status": dict(self.first_capacity_status),
                "retry_used": bool(self.retry_used),
                "retry_capacity_hint": None
                if self.retry_capacity_hint is None
                else int(self.retry_capacity_hint),
                "recovered_capacity_status": dict(self.recovered_capacity_status),
                "grouped_source_row_count": int(self.grouped_source_row_count),
                "grouped_row_count": int(self.grouped_row_count),
                "grouped_overflow": bool(self.grouped_overflow),
                "device_group_count": int(self.device_group_count),
            }
        )
        return metadata


def iter_pair_column_page_requests(
    *,
    total_count: int,
    page_size: int,
    initial_capacity: int,
) -> tuple[PairColumnPageRequest, ...]:
    if int(total_count) < 0:
        raise ValueError("total_count must be non-negative")
    contract = PairColumnPagedRecoveryContract(
        page_size=int(page_size),
        initial_capacity=int(initial_capacity),
    )
    requests: list[PairColumnPageRequest] = []
    for page_index, start in enumerate(range(0, int(total_count), int(page_size))):
        stop = min(int(total_count), start + int(page_size))
        requests.append(
            PairColumnPageRequest(
                page_index=page_index,
                start=start,
                stop=stop,
                initial_capacity=contract.initial_capacity,
            )
        )
    return tuple(requests)


def merge_grouped_count_maps(
    page_counts: Sequence[Mapping[int, int]],
) -> dict[int, int]:
    """Merge per-page group counts by key addition, not concatenation."""
    merged: Counter[int] = Counter()
    for counts in page_counts:
        for key, value in counts.items():
            int_value = int(value)
            if int_value < 0:
                raise ValueError("group counts must be non-negative")
            merged[int(key)] += int_value
    return {key: int(merged[key]) for key in sorted(merged)}


def summarize_page_recovery_records(
    records: Sequence[PairColumnPageRecoveryRecord],
) -> dict[str, object]:
    retry_page_count = sum(1 for record in records if record.retry_used)
    overflow_page_count = sum(
        1 for record in records if bool(record.first_capacity_status.get("overflowed"))
    )
    return {
        "schema": PAIR_COLUMN_PAGED_RECOVERY_SCHEMA,
        "page_count": len(records),
        "overflow_page_count": int(overflow_page_count),
        "retry_page_count": int(retry_page_count),
        "grouped_source_row_count": int(sum(record.grouped_source_row_count for record in records)),
        "grouped_row_count": int(sum(record.grouped_row_count for record in records)),
        "page_records": [record.to_metadata() for record in records],
        "merge_rule": PAIR_COLUMN_PAGED_RECOVERY_MERGE_RULE,
        "merge_requires_disjoint_keys": False,
    }
