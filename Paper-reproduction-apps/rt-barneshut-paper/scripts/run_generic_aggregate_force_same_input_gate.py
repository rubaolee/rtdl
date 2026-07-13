from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


APP_DIR = Path(__file__).resolve().parents[1]
ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())


def default_run_dir() -> Path:
    return APP_DIR / "_runs" / "generic_aggregate_force_same_input_gate"


def run_gate(
    *,
    prepared_arrays: Path,
    expected_force: Path,
    run_dir: Path,
    python: str,
    rtol: float,
    atol: float,
    theta: float,
    softening: float,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    if not prepared_arrays.is_file():
        raise FileNotFoundError(f"prepared arrays not found: {prepared_arrays}")
    if not expected_force.is_file():
        raise FileNotFoundError(f"expected force output not found: {expected_force}")

    candidate_force = run_dir / "generic_aggregate_numba_forces.txt"
    summary = run_dir / "summary.json"
    cmd = [
        python,
        str(APP_DIR / "rt_barneshut_reproduction.py"),
        "--mode",
        "aggregate-numba-force-compare",
        "--prepared-arrays-json",
        str(prepared_arrays),
        "--expected-force-output",
        str(expected_force),
        "--force-output",
        str(candidate_force),
        "--output",
        str(summary),
        "--force-compare-rtol",
        str(rtol),
        "--force-compare-atol",
        str(atol),
        "--theta",
        str(theta),
        "--softening",
        str(softening),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    payload = json.loads(summary.read_text(encoding="utf-8"))
    payload["gate_runner"] = {
        "mode": "generic_aggregate_force_same_input_gate",
        "prepared_arrays": str(prepared_arrays),
        "expected_force": str(expected_force),
        "candidate_force": str(candidate_force),
        "summary": str(summary),
        "rtol": float(rtol),
        "atol": float(atol),
        "theta": float(theta),
        "softening": float(softening),
        "claim_boundary": (
            "app_owned_pod_or_local_same_input_scalar_force_gate",
            "prepared_arrays_and_expected_force_are_inputs",
            "not_full_paper_reproduction",
            "not_performance_claim",
        ),
    }
    summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the RT-BarnesHut generic aggregate same-input scalar force comparator gate."
    )
    parser.add_argument(
        "--prepared-arrays",
        type=Path,
        default=APP_DIR / "_runs" / "author_same_input" / "author_treelogy_prepared_arrays.json",
    )
    parser.add_argument(
        "--expected-force",
        type=Path,
        default=APP_DIR / "_runs" / "author_same_input" / "author_treelogy_forces.txt",
    )
    parser.add_argument("--run-dir", type=Path, default=default_run_dir())
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--rtol", type=float, default=1.0e-4)
    parser.add_argument("--atol", type=float, default=1.0e-4)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--softening", type=float, default=0.0)
    args = parser.parse_args()

    try:
        payload = run_gate(
            prepared_arrays=args.prepared_arrays.resolve(),
            expected_force=args.expected_force.resolve(),
            run_dir=args.run_dir.resolve(),
            python=args.python,
            rtol=args.rtol,
            atol=args.atol,
            theta=args.theta,
            softening=args.softening,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(args.run_dir.resolve() / "summary.json")
    return 0 if payload["force_comparison"]["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
