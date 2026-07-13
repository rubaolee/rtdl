from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path


# The app normally lives inside the repository, but POD runs may stage the
# runner separately.  Keep the import contract explicit instead of relying on
# the staging directory layout.
ROOT = next(
    (
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "src" / "rtdsl").is_dir()
    ),
    Path(os.environ.get("RTDL_REPO_ROOT", "/workspace/rtdl-goal5481")),
)
if not (ROOT / "src" / "rtdsl").is_dir():
    raise RuntimeError(f"RTDL repository root is not available: {ROOT}")
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt


NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?")
AUTHOR_RE = re.compile(
    r"Loaded polygons\s+(?P<polygons>\d+).*?"
    r"Loaded queries\s+(?P<queries>\d+).*?"
    r"Loading Time\s+(?P<loading_ms>[0-9.eE+-]+)\s+ms.*?"
    r"Query Time\s+(?P<query_ms>[0-9.eE+-]+)\s+ms.*?"
    r"Results\s+(?P<results>\d+)",
    re.DOTALL,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _numbers(text: str) -> tuple[float, ...]:
    return tuple(float(value) for value in NUMBER_RE.findall(text))


def _split_wkt_top_level(text: str) -> tuple[str, ...]:
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("unbalanced WKT parentheses")
        elif char == "," and depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1
    if depth != 0:
        raise ValueError("unbalanced WKT parentheses")
    parts.append(text[start:].strip())
    return tuple(part for part in parts if part)


def _strip_outer_parens(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("(") or not stripped.endswith(")"):
        return stripped
    return stripped[1:-1].strip()


def geometry_wkt_mbr(text: str) -> tuple[float, float, float, float]:
    values = _numbers(text)
    if len(values) < 2 or len(values) % 2:
        raise ValueError(f"2-D WKT has an invalid coordinate count: {text[:80]!r}")
    xs = values[0::2]
    ys = values[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def geometry_wkt_mbrs(text: str) -> tuple[tuple[float, float, float, float], ...]:
    stripped = text.strip()
    start = stripped.find("(")
    end = stripped.rfind(")")
    if start < 0 or end <= start:
        raise ValueError(f"invalid WKT geometry: {stripped[:80]!r}")
    geometry_type = stripped[:start].strip().split()[0].upper()
    body = stripped[start + 1 : end]
    if geometry_type == "MULTIPOLYGON":
        polygons = _split_wkt_top_level(body)
        if not polygons:
            raise ValueError("empty MULTIPOLYGON WKT")
        return tuple(geometry_wkt_mbr(_strip_outer_parens(polygon)) for polygon in polygons)
    if geometry_type in {"POLYGON", "LINESTRING", "POINT"}:
        return (geometry_wkt_mbr(body),)
    raise ValueError(f"unsupported geometry WKT type: {geometry_type}")


def point_wkt_xy(text: str) -> tuple[float, float]:
    if not text.lstrip().upper().startswith("POINT"):
        raise ValueError(f"point query row is not POINT WKT: {text[:80]!r}")
    values = _numbers(text)
    if len(values) != 2:
        raise ValueError(f"POINT WKT must have exactly two coordinates: {text[:80]!r}")
    return values[0], values[1]


def load_geometry_mbrs(path: Path) -> tuple[tuple[float, float, float, float], ...]:
    rows: list[tuple[float, float, float, float]] = []
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                rows.extend(geometry_wkt_mbrs(line))
    if not rows:
        raise ValueError(f"geometry WKT input is empty: {path}")
    return tuple(rows)


def load_geometry_mbr_columns(path: Path):
    """Load WKT MBRs into the generic column contract without row objects."""
    import numpy as np

    ids: list[int] = []
    min_x: list[float] = []
    min_y: list[float] = []
    max_x: list[float] = []
    max_y: list[float] = []
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            for row_min_x, row_min_y, row_max_x, row_max_y in geometry_wkt_mbrs(line):
                ids.append(len(ids))
                min_x.append(row_min_x)
                min_y.append(row_min_y)
                max_x.append(row_max_x)
                max_y.append(row_max_y)
    if not ids:
        raise ValueError(f"geometry WKT input is empty: {path}")
    return rt.Aabb2DColumns(
        ids=np.asarray(ids, dtype=np.uint32),
        min_x=np.asarray(min_x, dtype=np.float64),
        min_y=np.asarray(min_y, dtype=np.float64),
        max_x=np.asarray(max_x, dtype=np.float64),
        max_y=np.asarray(max_y, dtype=np.float64),
    )


def geometry_wkt_mbr_fast(text: str) -> tuple[float, float, float, float]:
    """Parse numeric WKT coordinates through NumPy without Python float loops."""
    import numpy as np

    values = np.fromstring(
        re.sub(r"[^0-9eE+.-]+", " ", text),
        sep=" ",
        dtype=np.float64,
    )
    if values.size < 2 or values.size % 2:
        raise ValueError(f"2-D WKT has an invalid coordinate count: {text[:80]!r}")
    xs = values[0::2]
    ys = values[1::2]
    return float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())


def geometry_wkt_mbrs_fast(text: str) -> tuple[tuple[float, float, float, float], ...]:
    stripped = text.strip()
    start = stripped.find("(")
    end = stripped.rfind(")")
    if start < 0 or end <= start:
        raise ValueError(f"invalid geometry WKT: {stripped[:80]!r}")
    geometry_type = stripped[:start].strip().split()[0].upper()
    body = stripped[start + 1 : end]
    if geometry_type == "MULTIPOLYGON":
        polygons = _split_wkt_top_level(body)
        if not polygons:
            raise ValueError("empty MULTIPOLYGON WKT")
        return tuple(geometry_wkt_mbr_fast(_strip_outer_parens(polygon)) for polygon in polygons)
    if geometry_type in {"POLYGON", "LINESTRING", "POINT"}:
        return (geometry_wkt_mbr_fast(body),)
    raise ValueError(f"unsupported geometry WKT type: {geometry_type}")


def load_geometry_mbr_columns_fast(path: Path):
    """App-owned numeric WKT loader for the generic AABB column contract."""
    import numpy as np

    ids: list[int] = []
    min_x: list[float] = []
    min_y: list[float] = []
    max_x: list[float] = []
    max_y: list[float] = []
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            for row_min_x, row_min_y, row_max_x, row_max_y in geometry_wkt_mbrs_fast(line):
                ids.append(len(ids))
                min_x.append(row_min_x)
                min_y.append(row_min_y)
                max_x.append(row_max_x)
                max_y.append(row_max_y)
    if not ids:
        raise ValueError(f"geometry WKT input is empty: {path}")
    return rt.Aabb2DColumns(
        ids=np.asarray(ids, dtype=np.uint32),
        min_x=np.asarray(min_x, dtype=np.float64),
        min_y=np.asarray(min_y, dtype=np.float64),
        max_x=np.asarray(max_x, dtype=np.float64),
        max_y=np.asarray(max_y, dtype=np.float64),
    )


def load_point_queries(path: Path) -> tuple[tuple[float, float], ...]:
    with path.open("r", encoding="utf-8") as source:
        rows = tuple(point_wkt_xy(line) for line in source if line.strip())
    if not rows:
        raise ValueError(f"point-query WKT input is empty: {path}")
    return rows


def parse_author_output(stdout: str) -> dict[str, object]:
    match = AUTHOR_RE.search(stdout)
    if match is None:
        raise ValueError("author query output lacks the expected timing/count fields")
    return {
        "geometry_count": int(match.group("polygons")),
        "query_count": int(match.group("queries")),
        "loading_ms_diagnostic": float(match.group("loading_ms")),
        "query_ms_internal": float(match.group("query_ms")),
        "result_count": int(match.group("results")),
    }


def validate_exact_input_evidence(
    *,
    archive_result: dict[str, object],
    extraction_result: dict[str, object],
    geometry_path: Path,
    query_path: Path,
) -> Path:
    if not archive_result.get("claim_boundary", {}).get("archive_verified", False):
        raise ValueError("exact point gate requires a size+MD5 verified archive")
    extraction_boundary = extraction_result.get("claim_boundary", {})
    full_extraction = extraction_boundary.get("archive_extracted", False)
    subset_extraction = extraction_boundary.get("archive_subset_extracted", False)
    if not full_extraction and not subset_extraction:
        raise ValueError("exact point gate requires safely extracted archive evidence")
    final_path = Path(extraction_result["extraction"]["final_path"]).resolve()
    for path in (geometry_path.resolve(), query_path.resolve()):
        if not path.is_relative_to(final_path):
            raise ValueError(f"input is outside the verified extraction root: {path}")
    if subset_extraction:
        selected = {
            str(item["relative_path"])
            for item in extraction_result["extraction"].get("selected_members", ())
        }
        requested = {
            path.resolve().relative_to(final_path).as_posix()
            for path in (geometry_path, query_path)
        }
        if not requested.issubset(selected):
            raise ValueError("exact point gate input is absent from subset extraction evidence")
    return final_path


def run_author(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry_path: Path,
    query_path: Path,
    serialize_dir: Path,
) -> tuple[dict[str, object], str, list[str]]:
    command = [
        str(author_binary),
        "-geom",
        str(geometry_path),
        "-query",
        str(query_path),
        "-serialize",
        str(serialize_dir),
        "-query_type",
        "point-contains",
        "-index_type",
        "rtspatial",
        "-load_factor",
        "0.0001",
    ]
    environment = os.environ.copy()
    deps_lib = str(ae_root / "deps" / "lib")
    environment["LD_LIBRARY_PATH"] = deps_lib + (
        ":" + environment["LD_LIBRARY_PATH"]
        if environment.get("LD_LIBRARY_PATH")
        else ""
    )
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"author point-contains failed with exit {completed.returncode}: "
            f"{completed.stderr[-2000:]}"
        )
    return parse_author_output(completed.stdout), completed.stdout, command


def run_gate(
    *,
    author_binary: Path,
    ae_root: Path,
    geometry_path: Path,
    query_path: Path,
    serialize_dir: Path,
    archive_result: dict[str, object],
    extraction_result: dict[str, object],
    row_capacity_margin: float = 1.20,
) -> dict[str, object]:
    extraction_root = validate_exact_input_evidence(
        archive_result=archive_result,
        extraction_result=extraction_result,
        geometry_path=geometry_path,
        query_path=query_path,
    )
    author, author_stdout, author_command = run_author(
        author_binary=author_binary,
        ae_root=ae_root,
        geometry_path=geometry_path,
        query_path=query_path,
        serialize_dir=serialize_dir,
    )
    load_start = time.perf_counter()
    boxes = load_geometry_mbrs(geometry_path)
    points = load_point_queries(query_path)
    rtdl_load_sec = time.perf_counter() - load_start
    if len(boxes) != author["geometry_count"] or len(points) != author["query_count"]:
        raise RuntimeError("author and RTDL WKT row counts differ before execution")
    row_capacity = max(
        int(author["result_count"]) + 1024,
        int(math.ceil(int(author["result_count"]) * row_capacity_margin)),
    )
    route_start = time.perf_counter()
    rtdl = rt.expanded_aabb_point_membership_rows_2d(
        boxes,
        points,
        backend="optix",
        row_capacity=row_capacity,
    )
    rtdl_route_sec = time.perf_counter() - route_start
    matched = int(rtdl["valid_count"]) == int(author["result_count"])
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_point_contains_count.v1",
        "status": (
            "exact_input_point_contains_count_matched"
            if matched
            else "exact_input_point_contains_count_mismatch"
        ),
        "matched": matched,
        "input_identity": {
            "verified_extraction_root": str(extraction_root),
            "same_files_passed_to_author_and_rtdl": True,
            "geometry_path": str(geometry_path),
            "geometry_sha256": _sha256(geometry_path),
            "query_path": str(query_path),
            "query_sha256": _sha256(query_path),
        },
        "author": {
            **author,
            "command": author_command,
            "stdout": author_stdout,
            "pair_rows_exposed": False,
        },
        "rtdl": {
            "public_api": "expanded_aabb_point_membership_rows_2d",
            "backend": rtdl["backend"],
            "result_count": int(rtdl["valid_count"]),
            "row_capacity": row_capacity,
            "complete_candidate_coverage": rtdl["complete_candidate_coverage"],
            "rt_core_accelerated": rtdl["rt_core_accelerated"],
            "native_engine_customization": rtdl["native_engine_customization"],
            "load_wkt_sec": rtdl_load_sec,
            "route_wall_sec": rtdl_route_sec,
            "primitive_query_sec": rtdl["run_phases"][
                "emit_expanded_aabb_point_membership_rows_2d_sec"
            ],
        },
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": matched,
            "pointwise_containment_equivalence_claimed": False,
            "relation_level_evidence_reference": "Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_same_input_pip.json",
            "author_pair_relation_agreement_claimed": False,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--serialize-dir", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--extraction-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.serialize_dir.mkdir(parents=True, exist_ok=True)
    payload = run_gate(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        geometry_path=args.geometry.resolve(),
        query_path=args.query.resolve(),
        serialize_dir=args.serialize_dir.resolve(),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
    )
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
