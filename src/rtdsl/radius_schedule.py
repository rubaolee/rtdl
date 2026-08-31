from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RadiusGrowthMode = Literal["adaptive", "double", "add"]
RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION = "rtdl.radius_growth_schedule.v1"
RADIUS_GROWTH_MODES = ("adaptive", "double", "add")


@dataclass(frozen=True)
class RadiusGrowthStep:
    """One generic radius-growth update.

    The contract is intentionally app-neutral: it describes how a bounded search
    radius evolves from one iteration to the next after observing how many items
    remain unresolved.  Paper apps may map this to a specific source, but RTDL
    core does not encode paper identity here.
    """

    previous_radius: float
    next_radius: float
    hd_upper_bound: float
    cell_diagonal: float
    last_input_count: int
    next_input_count: int
    reduced_factor: float | None
    mode: RadiusGrowthMode
    expanded_by: float
    update_applied: bool
    clamp_applied: bool
    contract: str = RADIUS_GROWTH_SCHEDULE_CONTRACT_VERSION
    app_semantics: str = "none"

    def to_dict(self) -> dict[str, object]:
        return {
            "previous_radius": self.previous_radius,
            "next_radius": self.next_radius,
            "hd_upper_bound": self.hd_upper_bound,
            "cell_diagonal": self.cell_diagonal,
            "last_input_count": self.last_input_count,
            "next_input_count": self.next_input_count,
            "reduced_factor": self.reduced_factor,
            "mode": self.mode,
            "expanded_by": self.expanded_by,
            "update_applied": self.update_applied,
            "clamp_applied": self.clamp_applied,
            "contract": self.contract,
            "app_semantics": self.app_semantics,
        }


def _validate_radius_inputs(
    *,
    radius: float,
    hd_upper_bound: float,
    cell_diagonal: float,
    last_input_count: int,
    next_input_count: int,
    mode: str,
) -> RadiusGrowthMode:
    if mode not in RADIUS_GROWTH_MODES:
        raise ValueError("radius growth mode must be adaptive, double, or add")
    if radius < 0.0:
        raise ValueError("radius must be non-negative")
    if hd_upper_bound < 0.0:
        raise ValueError("hd_upper_bound must be non-negative")
    if cell_diagonal < 0.0:
        raise ValueError("cell_diagonal must be non-negative")
    if last_input_count <= 0:
        raise ValueError("last_input_count must be positive")
    if next_input_count < 0:
        raise ValueError("next_input_count must be non-negative")
    if next_input_count > last_input_count:
        raise ValueError("next_input_count must not exceed last_input_count")
    return mode  # type: ignore[return-value]


def radius_growth_step(
    *,
    radius: float,
    hd_upper_bound: float,
    cell_diagonal: float,
    last_input_count: int,
    next_input_count: int,
    mode: RadiusGrowthMode,
) -> RadiusGrowthStep:
    """Return the next bounded-search radius using a generic growth schedule.

    The update is applied only when unresolved input remains and the current
    radius is still below the upper bound.  Paper apps may map their own
    algorithm-specific schedule to these modes without putting paper identity
    into RTDL core.
    """

    checked_mode = _validate_radius_inputs(
        radius=radius,
        hd_upper_bound=hd_upper_bound,
        cell_diagonal=cell_diagonal,
        last_input_count=last_input_count,
        next_input_count=next_input_count,
        mode=mode,
    )
    previous = float(radius)
    upper = float(hd_upper_bound)
    diagonal = float(cell_diagonal)
    if next_input_count == 0 or previous >= upper:
        return RadiusGrowthStep(
            previous_radius=previous,
            next_radius=previous,
            hd_upper_bound=upper,
            cell_diagonal=diagonal,
            last_input_count=int(last_input_count),
            next_input_count=int(next_input_count),
            reduced_factor=None,
            mode=checked_mode,
            expanded_by=0.0,
            update_applied=False,
            clamp_applied=False,
        )

    reduced_factor = float(last_input_count - next_input_count) / float(last_input_count)
    if checked_mode == "adaptive":
        expanded_by = 0.0
        for expand_factor in (8.0, 4.0, 2.0, 1.0):
            # Matches the pinned author source: strict less-than.
            if reduced_factor < 1.0 / expand_factor:
                expanded_by = expand_factor * diagonal
                break
    elif checked_mode == "double":
        expanded_by = previous
    elif checked_mode == "add":
        expanded_by = diagonal
    else:  # pragma: no cover - guarded above
        raise AssertionError(f"unreachable radius growth mode: {checked_mode}")

    unclamped = previous + expanded_by
    next_radius = min(unclamped, upper)
    return RadiusGrowthStep(
        previous_radius=previous,
        next_radius=next_radius,
        hd_upper_bound=upper,
        cell_diagonal=diagonal,
        last_input_count=int(last_input_count),
        next_input_count=int(next_input_count),
        reduced_factor=reduced_factor,
        mode=checked_mode,
        expanded_by=float(expanded_by),
        update_applied=True,
        clamp_applied=unclamped > upper,
    )


def radius_growth_trace(
    *,
    initial_radius: float,
    hd_upper_bound: float,
    cell_diagonal: float,
    input_counts: list[int] | tuple[int, ...],
    mode: RadiusGrowthMode,
) -> list[RadiusGrowthStep]:
    """Return a trace over consecutive input-count observations."""

    if len(input_counts) < 2:
        raise ValueError("input_counts must contain at least two observations")
    radius = float(initial_radius)
    steps: list[RadiusGrowthStep] = []
    for last_count, next_count in zip(input_counts, input_counts[1:]):
        step = radius_growth_step(
            radius=radius,
            hd_upper_bound=hd_upper_bound,
            cell_diagonal=cell_diagonal,
            last_input_count=int(last_count),
            next_input_count=int(next_count),
            mode=mode,
        )
        steps.append(step)
        radius = step.next_radius
    return steps
