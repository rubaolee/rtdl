from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RTSPATIAL_RESULT_RE = re.compile(
    r"RT,\s*load\s+(?P<load_ms>[0-9]*\.?[0-9]+)\s+ms,\s*query\s+"
    r"(?P<query_ms>[0-9]*\.?[0-9]+)\s+ms,\s*results:\s*(?P<results>[0-9]+)"
)


def parse_rtspatial_output(text: str) -> dict[str, Any]:
    match = RTSPATIAL_RESULT_RE.search(text)
    if not match:
        raise ValueError("RTSpatial output did not contain an 'RT, load ..., query ..., results: ...' line")
    loaded_boxes = _parse_optional_int(text, r"Loaded boxes\s+([0-9]+)")
    loaded_point_queries = _parse_optional_int(text, r"Loaded point queries\s+([0-9]+)")
    loaded_box_queries = _parse_optional_int(text, r"Loaded box queries\s+([0-9]+)")
    return {
        "load_ms": float(match.group("load_ms")),
        "query_ms": float(match.group("query_ms")),
        "results": int(match.group("results")),
        "loaded_boxes": loaded_boxes,
        "loaded_point_queries": loaded_point_queries,
        "loaded_box_queries": loaded_box_queries,
    }


def _parse_optional_int(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def build_rtspatial_commands(
    manifest: dict[str, Any],
    *,
    rtspatial_exec: str,
    load_factor: float,
    limit_box: int = -1,
    limit_query: int = -1,
) -> dict[str, list[str]]:
    files = manifest["files"]
    boxes = str(files["boxes"])
    point_queries = str(files["point_queries"])
    box_queries = str(files["box_queries"])
    common = [
        rtspatial_exec,
        f"--box={boxes}",
        f"--load_factor={load_factor}",
        f"--limit_box={limit_box}",
        f"--limit_query={limit_query}",
    ]
    return {
        "point_contains": [
            *common,
            f"--point_query={point_queries}",
        ],
        "range_contains": [
            *common,
            f"--box_query={box_queries}",
            "--predicate=contains",
        ],
        "range_intersects": [
            *common,
            f"--box_query={box_queries}",
            "--predicate=intersects",
        ],
    }


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Helpers for LibRTS authors-code runs.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    parse_parser = subparsers.add_parser("parse-output")
    parse_parser.add_argument("--input", type=Path, required=True)

    command_parser = subparsers.add_parser("commands")
    command_parser.add_argument("--manifest", type=Path, required=True)
    command_parser.add_argument("--rtspatial-exec", default="rtspatial_exec")
    command_parser.add_argument("--load-factor", type=float, default=1.0)
    command_parser.add_argument("--limit-box", type=int, default=-1)
    command_parser.add_argument("--limit-query", type=int, default=-1)

    args = parser.parse_args(argv)
    if args.mode == "parse-output":
        payload = parse_rtspatial_output(args.input.read_text(encoding="utf-8"))
    elif args.mode == "commands":
        payload = build_rtspatial_commands(
            load_manifest(args.manifest),
            rtspatial_exec=args.rtspatial_exec,
            load_factor=args.load_factor,
            limit_box=args.limit_box,
            limit_query=args.limit_query,
        )
    else:
        raise ValueError(f"unsupported mode: {args.mode}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
