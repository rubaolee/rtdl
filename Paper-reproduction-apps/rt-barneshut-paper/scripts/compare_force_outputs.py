from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_force_file(path: Path) -> dict[int, float]:
    values: dict[int, float] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"{path}:{line_number}: expected '<id> <force>', got {line!r}")
        body_id = int(parts[0])
        force = float(parts[1])
        if body_id in values:
            raise ValueError(f"{path}:{line_number}: duplicate body id {body_id}")
        values[body_id] = force
    return values


def compare_force_outputs(
    left: Path,
    right: Path,
    *,
    rtol: float,
    atol: float,
) -> dict[str, object]:
    left_values = read_force_file(left)
    right_values = read_force_file(right)
    left_ids = set(left_values)
    right_ids = set(right_values)
    common_ids = sorted(left_ids & right_ids)
    missing_in_right = sorted(left_ids - right_ids)
    extra_in_right = sorted(right_ids - left_ids)
    max_abs_error = 0.0
    max_rel_error = 0.0
    max_error_id: int | None = None
    mismatch_count = 0

    for body_id in common_ids:
        lhs = left_values[body_id]
        rhs = right_values[body_id]
        abs_error = abs(lhs - rhs)
        denom = max(abs(lhs), abs(rhs), 1.0)
        rel_error = abs_error / denom
        if abs_error > max_abs_error or rel_error > max_rel_error:
            max_abs_error = max(max_abs_error, abs_error)
            max_rel_error = max(max_rel_error, rel_error)
            max_error_id = body_id
        if abs_error > atol + rtol * denom:
            mismatch_count += 1

    matched = (
        not missing_in_right
        and not extra_in_right
        and mismatch_count == 0
        and len(left_values) == len(right_values)
    )
    return {
        "left": str(left),
        "right": str(right),
        "left_count": len(left_values),
        "right_count": len(right_values),
        "common_count": len(common_ids),
        "missing_in_right_count": len(missing_in_right),
        "extra_in_right_count": len(extra_in_right),
        "mismatch_count": mismatch_count,
        "max_abs_error": max_abs_error,
        "max_rel_error": max_rel_error,
        "max_error_id": max_error_id,
        "rtol": rtol,
        "atol": atol,
        "matched": matched,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare RT-BarnesHut per-body force output files.")
    parser.add_argument("--left", type=Path, required=True)
    parser.add_argument("--right", type=Path, required=True)
    parser.add_argument("--rtol", type=float, default=1.0e-5)
    parser.add_argument("--atol", type=float, default=1.0e-5)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    payload = compare_force_outputs(args.left, args.right, rtol=args.rtol, atol=args.atol)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
