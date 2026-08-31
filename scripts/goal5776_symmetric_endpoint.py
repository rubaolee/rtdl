"""Shared symmetric endpoint timer for Goal5776 measurement front doors.

Application-specific adapters supply the physical prepare/execute and canonical
output projection.  This module owns the lifecycle boundary so an adapter
cannot accidentally time V2 physical rows against a V4 verified output again.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import time
from typing import Callable, Mapping, TypeVar

from goal5776_real_scale_formal_contract import COLD, LIFECYCLES, PREPARED


Owner = TypeVar("Owner")
Loaded = TypeVar("Loaded")
Raw = TypeVar("Raw")
Canonical = TypeVar("Canonical")


def validate_behavioral_true_optix(receipt: Mapping[str, object]) -> None:
    try:
        snapshot = dict(receipt["native_snapshot"])  # type: ignore[arg-type]
        successful = int(snapshot["successful_launch_count"])
        complete = int(snapshot["complete_context_launch_count"])
        # Current audit ABI proves binding by successful==complete.  Older
        # receipts may additionally expose an explicit unbound counter; when
        # present it must also be zero.
        unbound = int(snapshot.get(
            "unbound_launch_count", successful - complete
        ))
        invalid = (
            receipt["physical_executor_classification"]
            != "optix_traversal_observed"
            or successful <= 0
            or complete != successful
            or unbound != 0
            or any(int(snapshot[name]) != 0 for name in (
                "failed_launch_count",
                "incomplete_context_launch_count",
                "pending_context_at_finish",
                "session_error",
            ))
            or not snapshot["first_traversable"]
            or not snapshot["last_traversable"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("malformed behavioral OptiX receipt") from exc
    if invalid:
        raise RuntimeError("endpoint did not prove complete bound OptiX traversal")


@dataclass(frozen=True)
class EndpointObservation:
    lifecycle: str
    registered_complete_endpoint_seconds: float
    loading_seconds_reported_separately: float | None
    preparation_seconds_reported_separately: float | None
    canonical_output: object
    traversal_receipt: Mapping[str, object]
    matched: bool
    comparator_inside_registered_timer: bool = False
    preparation_is_free: bool = False
    close_inside_registered_timer: bool = False

    def __post_init__(self) -> None:
        if self.lifecycle not in LIFECYCLES:
            raise ValueError("unknown Goal5776 lifecycle")
        if not math.isfinite(self.registered_complete_endpoint_seconds) \
                or self.registered_complete_endpoint_seconds <= 0.0:
            raise ValueError("registered endpoint seconds must be finite and positive")
        if self.lifecycle == PREPARED:
            for name, value in (
                ("loading", self.loading_seconds_reported_separately),
                ("preparation", self.preparation_seconds_reported_separately),
            ):
                if value is None or not math.isfinite(value) or value < 0.0:
                    raise ValueError(
                        f"prepared lifecycle must report finite {name}"
                    )
        elif self.loading_seconds_reported_separately is not None \
                or self.preparation_seconds_reported_separately is not None:
            raise ValueError(
                "cold lifecycle reports loading and preparation only inside endpoint"
            )


def measure_symmetric_endpoint(
    *,
    lifecycle: str,
    load: Callable[[], Loaded],
    prepare: Callable[[Loaded], Owner],
    execute: Callable[[Owner], Raw],
    canonicalize_and_bind_output: Callable[[Raw], Canonical],
    finish_traversal_receipt: Callable[[Owner, Raw, Canonical], Mapping[str, object]],
    compare_outside_timer: Callable[[Canonical], bool],
    close: Callable[[Owner], None],
    clock: Callable[[], float] = time.perf_counter,
) -> EndpointObservation:
    """Measure one complete, method-independent application endpoint.

    For ``cold`` the timer starts before immutable application input loading
    and covers loading, prepare, execute, canonical output binding, receipt
    completion and owner teardown.  For ``prepared`` loading and preparation
    are both outside the registered execution timer and their directly
    observed seconds are retained separately; teardown is outside the per-call
    boundary.  Correctness comparison always occurs after the registered
    timer.  This API shape prevents an application adapter from silently
    charging file loading to only one method.
    """

    if lifecycle not in LIFECYCLES:
        raise ValueError(f"unknown lifecycle: {lifecycle}")
    owner: Owner | None = None
    closed = False
    loading_seconds: float | None = None
    prepare_seconds: float | None = None
    try:
        if lifecycle == PREPARED:
            loading_start = clock()
            loaded = load()
            loading_seconds = clock() - loading_start
            prepare_start = clock()
            owner = prepare(loaded)
            prepare_seconds = clock() - prepare_start
            endpoint_start = clock()
        else:
            endpoint_start = clock()
            loaded = load()
            owner = prepare(loaded)
        raw = execute(owner)
        canonical = canonicalize_and_bind_output(raw)
        receipt = finish_traversal_receipt(owner, raw, canonical)
        validate_behavioral_true_optix(receipt)
        if lifecycle == COLD:
            close(owner)
            closed = True
        endpoint_seconds = clock() - endpoint_start
        matched = bool(compare_outside_timer(canonical))
        if not matched:
            raise RuntimeError("canonical application output mismatch")
        return EndpointObservation(
            lifecycle=lifecycle,
            registered_complete_endpoint_seconds=endpoint_seconds,
            loading_seconds_reported_separately=loading_seconds,
            preparation_seconds_reported_separately=prepare_seconds,
            canonical_output=canonical,
            traversal_receipt=receipt,
            matched=True,
            close_inside_registered_timer=lifecycle == COLD,
        )
    finally:
        if owner is not None and not closed:
            close(owner)


__all__ = [
    "EndpointObservation",
    "measure_symmetric_endpoint",
    "validate_behavioral_true_optix",
]
