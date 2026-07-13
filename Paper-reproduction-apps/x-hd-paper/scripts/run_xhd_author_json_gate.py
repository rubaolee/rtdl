from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Iterable

from xhd_input_loader import load_points
from xhd_input_loader import load_wkt_points
from xhd_input_loader import translate_points_to_min_bound


def squared_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return float(sum((x - y) * (x - y) for x, y in zip(a, b)))


def directed_hausdorff(source: list[tuple[float, ...]], target: list[tuple[float, ...]]) -> float:
    max_min_sq = 0.0
    for point in source:
        nearest_sq = min(squared_distance(point, other) for other in target)
        max_min_sq = max(max_min_sq, nearest_sq)
    return math.sqrt(max_min_sq)


def exact_hausdorff(points_a: list[tuple[float, ...]], points_b: list[tuple[float, ...]]) -> dict[str, float]:
    directed_ab = directed_hausdorff(points_a, points_b)
    directed_ba = directed_hausdorff(points_b, points_a)
    return {
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff": max(directed_ab, directed_ba),
    }


def run_author(
    *,
    author_bin: Path,
    input1: Path,
    input2: Path,
    n_dims: int,
    author_json: Path,
    execution: str,
    variant: str,
    input_type: str,
) -> dict[str, object]:
    author_json.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(author_bin),
        "-input1",
        str(input1),
        "-input2",
        str(input2),
        "-n_dims",
        str(n_dims),
        "-input_type",
        input_type,
        "-variant",
        variant,
        "-execution",
        execution,
        "-json",
        str(author_json),
        "-overwrite=true",
        "-check=false",
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return {
        "cmd": cmd,
        "returncode": int(completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def load_author_hd_result(path: Path) -> float:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "HDResult" not in payload:
        raise KeyError(f"{path} does not contain HDResult")
    return float(payload["HDResult"])


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    input1 = Path(args.input1)
    input2 = Path(args.input2)
    points_a = load_points(input1, n_dims=args.n_dims, input_type=args.input_type)
    points_b = load_points(input2, n_dims=args.n_dims, input_type=args.input_type)
    preprocessing: list[str] = []
    if args.translate_each_input_to_min_bound:
        points_a = translate_points_to_min_bound(points_a)
        points_b = translate_points_to_min_bound(points_b)
        preprocessing.append("translate_each_input_to_min_bound")
    exact = exact_hausdorff(points_a, points_b)

    author_run: dict[str, object] | None = None
    author_hd: float | None = None
    author_json = Path(args.author_json) if args.author_json else None

    if args.author_bin:
        if author_json is None:
            raise ValueError("--author-json is required when --author-bin is provided")
        author_run = run_author(
            author_bin=Path(args.author_bin),
            input1=input1,
            input2=input2,
            n_dims=args.n_dims,
            author_json=author_json,
            execution=args.execution,
            variant=args.variant,
            input_type=args.input_type,
        )
    if author_json is not None and author_json.exists():
        author_hd = load_author_hd_result(author_json)

    author_run_failed = bool(author_run is not None and author_run["returncode"] != 0)
    # The author's `hd_exec -variant=rt` reports the directed Hausdorff
    # distance from input1 to input2.  The symmetric max remains in the summary
    # for fixture diagnostics, but the author comparator uses input1 -> input2.
    author_reference_key = "directed_a_to_b"
    author_reference_value = float(exact[author_reference_key])
    diff = None if author_hd is None else abs(float(author_hd) - author_reference_value)
    matched = False if author_run_failed else (None if diff is None else bool(diff <= args.tolerance))

    return {
        "schema": "rtdl.paper_reproduction.xhd.author_json_gate.v1",
        "paper_app": "x-hd-paper",
        "input1": str(input1),
        "input2": str(input2),
        "n_dims": args.n_dims,
        "input_type": args.input_type,
        "variant": args.variant,
        "execution": args.execution,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "reference_preprocessing": preprocessing,
        "rtdl_reference": exact,
        "author_comparison_reference": author_reference_key,
        "author_comparison_reference_value": author_reference_value,
        "author_json": None if author_json is None else str(author_json),
        "author_hd_result": author_hd,
        "abs_diff": diff,
        "tolerance": args.tolerance,
        "matched": matched,
        "author_run": author_run,
        "author_run_failed": author_run_failed,
        "boundary": (
            "Tiny same-input author JSON gate. This compares author HDResult to "
            "a deterministic exact Hausdorff reference for bounded WKT or ASCII "
            "PLY fixtures. "
            "It is not exact paper input reproduction and not a performance claim."
        ),
        "paper_reproduction_claim_authorized": False,
        "performance_claim_authorized": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the X-HD tiny same-input author JSON gate.")
    parser.add_argument("--input1", required=True)
    parser.add_argument("--input2", required=True)
    parser.add_argument("--n-dims", type=int, default=2)
    parser.add_argument("--input-type", default="wkt", choices=("wkt", "ply"))
    parser.add_argument(
        "--translate-each-input-to-min-bound",
        action="store_true",
        help=(
            "Translate each input point set independently so its coordinate-wise "
            "minimum is zero before computing the RTDL/reference comparator. "
            "This models the author PLY loader's reported MBR convention."
        ),
    )
    parser.add_argument("--author-bin")
    parser.add_argument("--author-json")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--variant", default="rt")
    parser.add_argument("--execution", default="gpu")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_summary(args)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if summary["author_run_failed"]:
        return 2
    return 0 if summary["matched"] is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
