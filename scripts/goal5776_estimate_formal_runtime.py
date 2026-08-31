#!/usr/bin/env python3
"""Conservative pre-POD wall-time budget from the final Home functional paths."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from goal5776_real_scale_formal_contract import FORMAL_UNITS, UNITS, schedule


def _load_roots(roots: list[Path]) -> dict[tuple[str, str, str], float]:
    result: dict[tuple[str, str, str], float] = {}
    for root in roots:
        resolved = root.resolve()
        if resolved.is_file():
            document = json.loads(resolved.read_text(encoding="utf-8"))
            records = document.get("results")
            if not isinstance(records, list):
                raise RuntimeError(
                    f"Goal5776 Home budget file lacks results: {resolved}")
        elif resolved.is_dir():
            records = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(resolved.glob("[0-9][0-9][0-9].json"))
            ]
        else:
            raise FileNotFoundError(resolved)
        for row in records:
            key = (str(row["unit_id"]), str(row["lifecycle"]), str(row["method"]))
            if key in result:
                raise RuntimeError(f"duplicate Goal5776 Home budget row: {key}")
            seconds = sum(
                float(item["registered_complete_endpoint_seconds"])
                for item in row["rows"]
            )
            # RayJoin prepared execution registers six independent batch rows,
            # but one worker owns a longer complete six-batch session.  Budget
            # the actually observed worker wall, never the sum of only the
            # row-local statistical timers.
            session_wall = row.get(
                "prepared_session_complete_wall_seconds_reported_separately")
            if session_wall is not None:
                session_wall_seconds = float(session_wall)
                if not math.isfinite(session_wall_seconds) \
                        or session_wall_seconds <= 0.0:
                    raise RuntimeError(
                        f"invalid Goal5776 Home session wall: {key}")
                seconds = max(seconds, session_wall_seconds)
            if not math.isfinite(seconds) or seconds <= 0.0:
                raise RuntimeError(f"invalid Goal5776 Home budget seconds: {key}")
            result[key] = seconds
    return result


def estimate(
    roots: list[Path], *, process_overhead_seconds: float = 5.0,
    safety_factor: float = 1.25,
) -> dict[str, object]:
    if process_overhead_seconds < 0.0 or safety_factor < 1.0:
        raise ValueError("Goal5776 budget bounds are invalid")
    observed = _load_roots(roots)
    rows = schedule()
    required = {
        (str(row["unit_id"]), str(row["lifecycle"]), str(row["method"]))
        for row in rows
    }
    formal_ids = {unit.unit_id for unit in FORMAL_UNITS}
    functional_only_ids = {unit.unit_id for unit in UNITS} - formal_ids
    extra = set(observed) - required
    allowed_extra = {
        key for key in extra if key[0] in functional_only_ids
    }
    if not required.issubset(observed) or extra != allowed_extra:
        raise RuntimeError(
            f"Goal5776 Home budget coverage mismatch: "
            f"missing={sorted(required-set(observed))}, "
            f"extra={sorted(extra-allowed_extra)}")
    endpoint_seconds = sum(
        observed[(str(row["unit_id"]), str(row["lifecycle"]), str(row["method"]))]
        for row in rows
    )
    process_seconds = process_overhead_seconds * len(rows)
    conservative_seconds = (endpoint_seconds + process_seconds) * safety_factor
    by_app: dict[str, float] = {}
    from goal5776_real_scale_formal_contract import UNIT_BY_ID
    for row in rows:
        key = (str(row["unit_id"]), str(row["lifecycle"]), str(row["method"]))
        app = UNIT_BY_ID[key[0]].app
        by_app[app] = by_app.get(app, 0.0) + observed[key]
    return {
        "schema": "rtdl.goal5776.home_derived_formal_runtime_budget.v1",
        "not_a_performance_result": True,
        "home_gpu_times_used_only_as_conservative_cost_inputs": True,
        "worker_count": len(rows),
        "covered_method_lifecycle_units": len(observed),
        "formal_method_lifecycle_units": len(required),
        "functional_only_observations_excluded_from_budget": len(allowed_extra),
        "observed_endpoint_sum_seconds": endpoint_seconds,
        "assumed_process_overhead_seconds_per_worker": process_overhead_seconds,
        "process_overhead_sum_seconds": process_seconds,
        "safety_factor": safety_factor,
        "conservative_budget_seconds": conservative_seconds,
        "conservative_budget_hours": conservative_seconds / 3600.0,
        "observed_endpoint_seconds_by_app": dict(sorted(by_app.items())),
        "owner_must_confirm_budget_before_worker_zero": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--home-root", action="append", type=Path, required=True)
    parser.add_argument("--process-overhead-seconds", type=float, default=5.0)
    parser.add_argument("--safety-factor", type=float, default=1.25)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    result = estimate(
        args.home_root,
        process_overhead_seconds=args.process_overhead_seconds,
        safety_factor=args.safety_factor,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
