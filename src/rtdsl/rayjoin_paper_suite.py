from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterable


RAYJOIN_PAPER_SUITE_VERSION = "rtdl.rayjoin_paper_suite.exact_reproduction.v1"
RAYJOIN_PREPROCESSED_SHARE_URL = (
    "https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA"
)

DEFAULT_GRID_SIZE = 15000
DEFAULT_XSECT_FACTOR = "0.1"
DEFAULT_ENLARGE = "3.5"
DEFAULT_SERIALIZE_PREFIX = "/dev/shm"
DEFAULT_WARMUP = 5
DEFAULT_REPEAT = 5
RTDL_RUNNABLE_STATUSES = frozenset({"implemented", "implemented_compute_optional_output"})


@dataclass(frozen=True)
class PaperDatasetStats:
    line_segments_label: str
    polygons_label: str
    description: str


@dataclass(frozen=True)
class RayjoinPaperPair:
    pair_id: str
    paper_label: str
    left_dataset: str
    right_dataset: str
    left_relative_path: str
    right_relative_path: str
    left_stats: PaperDatasetStats
    right_stats: PaperDatasetStats


@dataclass(frozen=True)
class RayjoinPaperProgram:
    program_id: str
    paper_executable: str
    paper_query: str | None
    paper_table: str
    input_contract: str
    rtdl_optix_route: str
    rtdl_embree_route: str
    output_contract: str
    rtdl_status: str
    gap_note: str


@dataclass(frozen=True)
class RayjoinPaperCase:
    case_id: str
    pair: RayjoinPaperPair
    program: RayjoinPaperProgram


@dataclass(frozen=True)
class CdbPathStatus:
    path: str
    exists: bool
    bytes: int | None


@dataclass(frozen=True)
class RayjoinCaseAvailability:
    case_id: str
    program: str
    pair_id: str
    paper_label: str
    left: CdbPathStatus
    right: CdbPathStatus
    exact_input_ready: bool
    rtdl_status: str
    blocker: str | None


@dataclass(frozen=True)
class RayjoinAuthorCommand:
    case_id: str
    backend: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class CdbFileStats:
    path: str
    bytes: int
    chains: int
    points: int
    segments: int
    nonzero_faces: int


@dataclass(frozen=True)
class RayjoinSameSourceArcgisTarget:
    target_id: str
    source_asset_id: str
    output_relative_path: str
    cdb_name: str
    feature_id_field: str
    topology_contract: str


PAPER_DATASET_STATS: dict[str, PaperDatasetStats] = {
    "County": PaperDatasetStats("1.0M", "3.1K", "Boundaries of the U.S. Counties"),
    "Zipcode": PaperDatasetStats("23.9M", "32.2K", "ZIP Code areas for the USPS"),
    "Block": PaperDatasetStats("29.3M", "239.2K", "Census block groups in the U.S."),
    "Water": PaperDatasetStats("25.6M", "463.6K", "Major water features in the U.S."),
    "LKAF": PaperDatasetStats("1.8M", "18.2K", "Water areas in Africa"),
    "PKAF": PaperDatasetStats("1.3M", "25.7K", "Parks or green areas in Africa"),
    "LKAS": PaperDatasetStats("10.3M", "151.6K", "Water areas in Asia"),
    "PKAS": PaperDatasetStats("11.9M", "172.6K", "Parks or green areas in Asia"),
    "LKAU": PaperDatasetStats("1.2M", "14.5K", "Water areas in Australia"),
    "PKAU": PaperDatasetStats("567.1K", "12.8K", "Parks or green areas in Australia"),
    "LKEU": PaperDatasetStats("27.9M", "654.8K", "Water areas in Europe"),
    "PKEU": PaperDatasetStats("65.9M", "1.9M", "Parks or green areas in Europe"),
    "LKNA": PaperDatasetStats("69.3M", "1.6M", "Water areas in North America"),
    "PKNA": PaperDatasetStats("26.9M", "303.0K", "Parks or green areas in North America"),
    "LKSA": PaperDatasetStats("2.4M", "32.6K", "Water areas in South America"),
    "PKSA": PaperDatasetStats("3.2M", "49.5K", "Parks or green areas in South America"),
}


RAYJOIN_SECTION57_TABLE4_SECONDS: dict[str, dict[str, tuple[float | None, float | None]]] = {
    # Values from RayJoin ICS'24 Table 4. Tuple is (processing_sec, preprocessing_sec).
    # A None processing value means the artifact was reported as OOM.
    "PostGIS": {
        "county_zipcode": (30.58, None),
        "block_water": (233.78, None),
        "lkaf_pkaf": (0.97, None),
        "lkas_pkas": (27.78, None),
        "lkau_pkau": (0.79, None),
        "lkeu_pkeu": (92.58, None),
        "lkna_pkna": (163.42, None),
        "lksa_pksa": (2.54, None),
    },
    "Kinetica": {
        "county_zipcode": (22.81, None),
        "block_water": (52.75, None),
        "lkaf_pkaf": (0.34, None),
        "lkas_pkas": (4.10, None),
        "lkau_pkau": (0.86, None),
        "lkeu_pkeu": (14.69, None),
        "lkna_pkna": (11.75, None),
        "lksa_pksa": (1.05, None),
    },
    "EPUG-Overlay": {
        "county_zipcode": (165.71, 52.64),
        "block_water": (250.21, 114.46),
        "lkaf_pkaf": (4.94, 5.26),
        "lkas_pkas": (37.41, 35.22),
        "lkau_pkau": (4.74, 3.54),
        "lkeu_pkeu": (177.61, 161.91),
        "lkna_pkna": (234.53, 166.83),
        "lksa_pksa": (8.30, 9.75),
    },
    "RasterIntervals": {
        "county_zipcode": (2.94, 580.40),
        "block_water": (10.54, 1114.52),
        "lkaf_pkaf": (0.14, 81.20),
        "lkas_pkas": (5.29, 82.03),
        "lkau_pkau": (0.12, 48.72),
        "lkeu_pkeu": (15.47, 511.82),
        "lkna_pkna": (21.52, 203.45),
        "lksa_pksa": (0.45, 272.04),
    },
    "Uniform Grid*": {
        "county_zipcode": (1.82, 0.08),
        "block_water": (1.29, 0.13),
        "lkaf_pkaf": (0.78, 0.05),
        "lkas_pkas": (3.54, 0.07),
        "lkau_pkau": (0.38, 0.03),
        "lkeu_pkeu": (9.40, 0.20),
        "lkna_pkna": (7.29, 0.20),
        "lksa_pksa": (0.81, 0.06),
    },
    "LBVH*": {
        "county_zipcode": (8.07, 0.11),
        "block_water": (54.82, 0.18),
        "lkaf_pkaf": (0.05, 0.02),
        "lkas_pkas": (2.46, 0.09),
        "lkau_pkau": (0.05, 0.01),
        "lkeu_pkeu": (None, None),
        "lkna_pkna": (58.40, 0.47),
        "lksa_pksa": (0.26, 0.03),
    },
    "RayJoin*": {
        "county_zipcode": (0.12, 0.07),
        "block_water": (0.23, 0.12),
        "lkaf_pkaf": (0.01, 0.01),
        "lkas_pkas": (0.04, 0.05),
        "lkau_pkau": (0.01, 0.01),
        "lkeu_pkeu": (0.20, 0.20),
        "lkna_pkna": (0.25, 0.21),
        "lksa_pksa": (0.02, 0.01),
    },
}


RAYJOIN_PAPER_PAIRS: tuple[RayjoinPaperPair, ...] = (
    RayjoinPaperPair(
        pair_id="county_zipcode",
        paper_label="County x Zipcode",
        left_dataset="County",
        right_dataset="Zipcode",
        left_relative_path="point_cdb/dtl_cnty/dtl_cnty_Point.cdb",
        right_relative_path="point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb",
        left_stats=PAPER_DATASET_STATS["County"],
        right_stats=PAPER_DATASET_STATS["Zipcode"],
    ),
    RayjoinPaperPair(
        pair_id="block_water",
        paper_label="Block x Water",
        left_dataset="Block",
        right_dataset="Water",
        left_relative_path=(
            "point_cdb/USACensusBlockGroupBoundaries/"
            "USACensusBlockGroupBoundaries_Point.cdb"
        ),
        right_relative_path=(
            "point_cdb/USADetailedWaterBodies/"
            "USADetailedWaterBodies_Point.cdb"
        ),
        left_stats=PAPER_DATASET_STATS["Block"],
        right_stats=PAPER_DATASET_STATS["Water"],
    ),
    RayjoinPaperPair(
        pair_id="lkaf_pkaf",
        paper_label="LKAF x PKAF",
        left_dataset="LKAF",
        right_dataset="PKAF",
        left_relative_path="point_cdb/lakes/Africa/lakes_Africa_Point.cdb",
        right_relative_path="point_cdb/parks/Africa/parks_Africa_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKAF"],
        right_stats=PAPER_DATASET_STATS["PKAF"],
    ),
    RayjoinPaperPair(
        pair_id="lkas_pkas",
        paper_label="LKAS x PKAS",
        left_dataset="LKAS",
        right_dataset="PKAS",
        left_relative_path="point_cdb/lakes/Asia/lakes_Asia_Point.cdb",
        right_relative_path="point_cdb/parks/Asia/parks_Asia_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKAS"],
        right_stats=PAPER_DATASET_STATS["PKAS"],
    ),
    RayjoinPaperPair(
        pair_id="lkau_pkau",
        paper_label="LKAU x PKAU",
        left_dataset="LKAU",
        right_dataset="PKAU",
        left_relative_path="point_cdb/lakes/Australia/lakes_Australia_Point.cdb",
        right_relative_path="point_cdb/parks/Australia/parks_Australia_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKAU"],
        right_stats=PAPER_DATASET_STATS["PKAU"],
    ),
    RayjoinPaperPair(
        pair_id="lkeu_pkeu",
        paper_label="LKEU x PKEU",
        left_dataset="LKEU",
        right_dataset="PKEU",
        left_relative_path="point_cdb/lakes/Europe/lakes_Europe_Point.cdb",
        right_relative_path="point_cdb/parks/Europe/parks_Europe_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKEU"],
        right_stats=PAPER_DATASET_STATS["PKEU"],
    ),
    RayjoinPaperPair(
        pair_id="lkna_pkna",
        paper_label="LKNA x PKNA",
        left_dataset="LKNA",
        right_dataset="PKNA",
        left_relative_path="point_cdb/lakes/North_America/lakes_North_America_Point.cdb",
        right_relative_path="point_cdb/parks/North_America/parks_North_America_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKNA"],
        right_stats=PAPER_DATASET_STATS["PKNA"],
    ),
    RayjoinPaperPair(
        pair_id="lksa_pksa",
        paper_label="LKSA x PKSA",
        left_dataset="LKSA",
        right_dataset="PKSA",
        left_relative_path="point_cdb/lakes/South_America/lakes_South_America_Point.cdb",
        right_relative_path="point_cdb/parks/South_America/parks_South_America_Point.cdb",
        left_stats=PAPER_DATASET_STATS["LKSA"],
        right_stats=PAPER_DATASET_STATS["PKSA"],
    ),
)


RAYJOIN_PAPER_PROGRAMS: tuple[RayjoinPaperProgram, ...] = (
    RayjoinPaperProgram(
        program_id="lsi",
        paper_executable="query_exec",
        paper_query="lsi",
        paper_table="Table 3 top",
        input_contract=(
            "Base map R is -poly1; query map S is -poly2; the query stream is all "
            "line segments/edges from S."
        ),
        rtdl_optix_route="prepared segment-pair intersection count",
        rtdl_embree_route="prepared segment-pair intersection count",
        output_contract="segment-segment intersection count/rows",
        rtdl_status="implemented",
        gap_note="Need exact paper input CDBs before full matrix timing.",
    ),
    RayjoinPaperProgram(
        program_id="pip",
        paper_executable="query_exec",
        paper_query="pip",
        paper_table="Table 3 bottom",
        input_contract=(
            "Base map R is -poly1; query map S is -poly2; the query point stream is "
            "every point returned by S.get_points(), not one representative point per chain."
        ),
        rtdl_optix_route="RayJoin CDB closest-hit face-id point-location",
        rtdl_embree_route="RayJoin CDB closest-hit face-id point-location",
        output_contract="point id, face id, segment id, hit t; scalar positive-face count in hot path",
        rtdl_status="implemented",
        gap_note="Need exact paper input CDBs before full matrix timing.",
    ),
    RayjoinPaperProgram(
        program_id="overlay",
        paper_executable="polyover_exec",
        paper_query=None,
        paper_table="Section 5.7 / Table 4",
        input_contract=(
            "Both CDB maps are loaded; overlay runs LSI once, locates vertices of each map "
            "in the other map, classifies midpoints between intersections, then writes output chains."
        ),
        rtdl_optix_route="LSI + PIP + full overlay polygon assembly",
        rtdl_embree_route="LSI + PIP + full overlay polygon assembly",
        output_contract=(
            "default compute path matches polyover_exec without -output; optional output-chain "
            "assembly writes RayJoin-compatible chain files for correctness audits"
        ),
        rtdl_status="implemented_compute_optional_output",
        gap_note=(
            "RTDL overlay_seed rows still do not count; use the exact overlay runner for "
            "LSI, bidirectional vertex PIP, midpoint classification, and optional chain output."
        ),
    ),
)


RAYJOIN_US_ARCGIS_CDB_TARGETS: tuple[RayjoinSameSourceArcgisTarget, ...] = (
    RayjoinSameSourceArcgisTarget(
        target_id="county",
        source_asset_id="uscounty_feature_layer",
        output_relative_path="point_cdb/dtl_cnty/dtl_cnty_Point.cdb",
        cdb_name="dtl_cnty",
        feature_id_field="OBJECTID",
        topology_contract=(
            "same_source_regenerated_cdb_from_arcgis_rings; not a recovered "
            "paper_preprocessed Polygon-To-Line neighbor CDB"
        ),
    ),
    RayjoinSameSourceArcgisTarget(
        target_id="zipcode",
        source_asset_id="zipcode_feature_layer",
        output_relative_path="point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb",
        cdb_name="USAZIPCodeArea",
        feature_id_field="OBJECTID",
        topology_contract=(
            "same_source_regenerated_cdb_from_arcgis_rings; not a recovered "
            "paper_preprocessed Polygon-To-Line neighbor CDB"
        ),
    ),
    RayjoinSameSourceArcgisTarget(
        target_id="blockgroup",
        source_asset_id="blockgroup_feature_layer",
        output_relative_path=(
            "point_cdb/USACensusBlockGroupBoundaries/"
            "USACensusBlockGroupBoundaries_Point.cdb"
        ),
        cdb_name="USACensusBlockGroupBoundaries",
        feature_id_field="OBJECTID",
        topology_contract=(
            "same_source_regenerated_cdb_from_arcgis_rings; not a recovered "
            "paper_preprocessed Polygon-To-Line neighbor CDB"
        ),
    ),
    RayjoinSameSourceArcgisTarget(
        target_id="waterbodies",
        source_asset_id="waterbodies_feature_layer",
        output_relative_path=(
            "point_cdb/USADetailedWaterBodies/"
            "USADetailedWaterBodies_Point.cdb"
        ),
        cdb_name="USADetailedWaterBodies",
        feature_id_field="OBJECTID",
        topology_contract=(
            "same_source_regenerated_cdb_from_arcgis_rings; not a recovered "
            "paper_preprocessed Polygon-To-Line neighbor CDB"
        ),
    ),
)


def paper_pairs(pair_ids: Iterable[str] | None = None) -> tuple[RayjoinPaperPair, ...]:
    if pair_ids is None:
        return RAYJOIN_PAPER_PAIRS
    selected = set(pair_ids)
    return tuple(pair for pair in RAYJOIN_PAPER_PAIRS if pair.pair_id in selected)


def paper_programs(program_ids: Iterable[str] | None = None) -> tuple[RayjoinPaperProgram, ...]:
    if program_ids is None:
        return RAYJOIN_PAPER_PROGRAMS
    selected = set(program_ids)
    return tuple(program for program in RAYJOIN_PAPER_PROGRAMS if program.program_id in selected)


def paper_cases(
    *,
    pair_ids: Iterable[str] | None = None,
    program_ids: Iterable[str] | None = None,
) -> tuple[RayjoinPaperCase, ...]:
    cases: list[RayjoinPaperCase] = []
    for pair in paper_pairs(pair_ids):
        for program in paper_programs(program_ids):
            cases.append(
                RayjoinPaperCase(
                    case_id=f"{program.program_id}_{pair.pair_id}",
                    pair=pair,
                    program=program,
                )
            )
    return tuple(cases)


def same_source_arcgis_targets(target_ids: Iterable[str] | None = None) -> tuple[RayjoinSameSourceArcgisTarget, ...]:
    if target_ids is None:
        return RAYJOIN_US_ARCGIS_CDB_TARGETS
    selected = set(target_ids)
    return tuple(target for target in RAYJOIN_US_ARCGIS_CDB_TARGETS if target.target_id in selected)


def dataset_file(dataset_root: str | Path, relative_path: str) -> Path:
    return Path(dataset_root) / relative_path


def path_argument_text(path: str | Path) -> str:
    text = str(path)
    if not re.match(r"^[A-Za-z]:[\\/]", text) and not text.startswith("\\\\"):
        if text.startswith("/") or text.startswith("\\"):
            return text.replace("\\", "/")
    return text


def dataset_path_text(dataset_root: str | Path, relative_path: str) -> str:
    root_text = path_argument_text(dataset_root)
    if root_text.startswith("/") and not re.match(r"^[A-Za-z]:[\\/]", root_text):
        return str(PurePosixPath(root_text) / PurePosixPath(relative_path))
    return str(Path(root_text) / relative_path)


def _path_status(path: Path, *, display_path: str | None = None) -> CdbPathStatus:
    shown_path = display_path if display_path is not None else str(path)
    if not path.exists():
        return CdbPathStatus(path=shown_path, exists=False, bytes=None)
    return CdbPathStatus(path=shown_path, exists=True, bytes=path.stat().st_size)


def availability_matrix(
    dataset_root: str | Path,
    *,
    pair_ids: Iterable[str] | None = None,
    program_ids: Iterable[str] | None = None,
) -> tuple[RayjoinCaseAvailability, ...]:
    rows: list[RayjoinCaseAvailability] = []
    for case in paper_cases(pair_ids=pair_ids, program_ids=program_ids):
        left = _path_status(
            dataset_file(dataset_root, case.pair.left_relative_path),
            display_path=dataset_path_text(dataset_root, case.pair.left_relative_path),
        )
        right = _path_status(
            dataset_file(dataset_root, case.pair.right_relative_path),
            display_path=dataset_path_text(dataset_root, case.pair.right_relative_path),
        )
        exact_ready = left.exists and right.exists
        blocker = None
        if not exact_ready:
            missing = []
            if not left.exists:
                missing.append(case.pair.left_relative_path)
            if not right.exists:
                missing.append(case.pair.right_relative_path)
            blocker = "missing exact CDB input(s): " + ", ".join(missing)
        elif case.program.rtdl_status not in RTDL_RUNNABLE_STATUSES:
            blocker = case.program.gap_note
        rows.append(
            RayjoinCaseAvailability(
                case_id=case.case_id,
                program=case.program.program_id,
                pair_id=case.pair.pair_id,
                paper_label=case.pair.paper_label,
                left=left,
                right=right,
                exact_input_ready=exact_ready,
                rtdl_status=case.program.rtdl_status,
                blocker=blocker,
            )
        )
    return tuple(rows)


def build_rayjoin_author_command(
    case: RayjoinPaperCase,
    *,
    dataset_root: str | Path,
    query_exec: str | Path,
    polyover_exec: str | Path,
    mode: str = "rt",
    serialize_prefix: str = DEFAULT_SERIALIZE_PREFIX,
    grid_size: int = DEFAULT_GRID_SIZE,
    xsect_factor: str = DEFAULT_XSECT_FACTOR,
    enlarge: str = DEFAULT_ENLARGE,
    warmup: int = DEFAULT_WARMUP,
    repeat: int = DEFAULT_REPEAT,
    check: bool = False,
    output_path: str | Path | None = None,
) -> RayjoinAuthorCommand:
    if mode not in {"grid", "lbvh", "rt"}:
        raise ValueError("RayJoin author mode must be one of: grid, lbvh, rt")
    left = dataset_path_text(dataset_root, case.pair.left_relative_path)
    right = dataset_path_text(dataset_root, case.pair.right_relative_path)
    executable = query_exec if case.program.paper_executable == "query_exec" else polyover_exec
    command = [
        path_argument_text(executable),
        "-poly1",
        left,
        "-poly2",
        right,
        f"-serialize={serialize_prefix}",
        f"-grid_size={grid_size}",
        f"-mode={mode}",
        "-v=1",
        "-fau",
        "-xsect_factor",
        str(xsect_factor),
        f"-enlarge={enlarge}",
        f"-check={'true' if check else 'false'}",
    ]
    if case.program.paper_query is not None:
        command.extend(
            [
                f"-warmup={int(warmup)}",
                f"-repeat={int(repeat)}",
                f"-query={case.program.paper_query}",
            ]
        )
    if output_path is not None:
        command.extend(["-output", path_argument_text(output_path)])
    return RayjoinAuthorCommand(case_id=case.case_id, backend=f"rayjoin_author_{mode}", command=tuple(command))


def parse_rayjoin_timing(log_text: str) -> dict[str, float]:
    timings: dict[str, float] = {}
    for name, value in re.findall(r" - ([^:]+):\s+([0-9.]+) ms", log_text):
        timings[name.strip()] = float(value)
    return timings


def run_rayjoin_author_command(command: RayjoinAuthorCommand) -> dict[str, object]:
    start = time.perf_counter()
    completed = subprocess.run(
        command.command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    elapsed = time.perf_counter() - start
    timings = parse_rayjoin_timing(completed.stdout)
    stdout_lines = completed.stdout.splitlines()
    return {
        "schema": "rtdl.rayjoin_paper_suite.author_run.v1",
        "case_id": command.case_id,
        "backend": command.backend,
        "command": list(command.command),
        "elapsed_sec": elapsed,
        "timing_ms": timings,
        "stdout_summary": {
            "line_count": len(stdout_lines),
            "char_count": len(completed.stdout),
            "head": stdout_lines[:80],
            "tail": stdout_lines[-80:] if len(stdout_lines) > 160 else [],
            "truncated": len(stdout_lines) > 160,
        },
    }


def scan_cdb_file(path: str | Path) -> CdbFileStats:
    path = Path(path)
    chains = 0
    points = 0
    segments = 0
    faces: set[int] = set()
    with path.open("r", encoding="utf-8") as handle:
        while True:
            header = handle.readline()
            if not header:
                break
            header = header.strip()
            if not header:
                continue
            fields = header.split()
            if len(fields) != 6:
                raise ValueError(f"invalid CDB header in {path}: {header}")
            point_count = int(fields[1])
            left_face = int(fields[4])
            right_face = int(fields[5])
            chains += 1
            points += point_count
            segments += max(0, point_count - 1)
            if left_face != 0:
                faces.add(left_face)
            if right_face != 0:
                faces.add(right_face)
            for _ in range(point_count):
                if not handle.readline():
                    raise ValueError(f"unexpected EOF in CDB file {path}")
    return CdbFileStats(
        path=str(path),
        bytes=path.stat().st_size,
        chains=chains,
        points=points,
        segments=segments,
        nonzero_faces=len(faces),
    )


def exact_suite_manifest(dataset_root: str | Path) -> dict[str, object]:
    return {
        "schema": RAYJOIN_PAPER_SUITE_VERSION,
        "definition": {
            "scope": "exact RayJoin ICS'24 paper reproduction for LSI, PIP, and polygon overlay",
            "preprocessed_share_url": RAYJOIN_PREPROCESSED_SHARE_URL,
            "default_grid_size": DEFAULT_GRID_SIZE,
            "default_xsect_factor": DEFAULT_XSECT_FACTOR,
            "default_enlarge": DEFAULT_ENLARGE,
            "default_serialize_prefix": DEFAULT_SERIALIZE_PREFIX,
            "default_warmup": DEFAULT_WARMUP,
            "default_repeat": DEFAULT_REPEAT,
            "paper_query_semantics_source": "RayJoin src/run_query.cu and src/run_overlay.cu",
            "section57_table4_source": "RayJoin ICS'24 Table 4; cells are Processing Time (Preprocessing Time) in seconds.",
            "analogue_inputs_count_as_exact": False,
            "overlay_seed_counts_as_overlay": False,
            "input_provenance_modes": {
                "paper_preprocessed_cdb": (
                    "Original/preprocessed CDB files matching the RayJoin paper script layout and "
                    "paper Table 2 statistics."
                ),
                "same_source_regenerated_cdb": (
                    "CDB files regenerated from the public source datasets named by the RayJoin README; "
                    "valid for RayJoin-author-code vs RTDL apples-to-apples execution, but not a claim "
                    "that the paper's exact preprocessed CDB artifact was recovered unless stats match."
                ),
                "fixture_or_synthetic": (
                    "Small fixtures or synthetic inputs for regression only; never counts as paper reproduction."
                ),
            },
        },
        "dataset_root": str(dataset_root),
        "pairs": [asdict(pair) for pair in RAYJOIN_PAPER_PAIRS],
        "programs": [asdict(program) for program in RAYJOIN_PAPER_PROGRAMS],
        "section57_table4_seconds": RAYJOIN_SECTION57_TABLE4_SECONDS,
        "availability": [asdict(row) for row in availability_matrix(dataset_root)],
    }


def write_exact_suite_manifest(dataset_root: str | Path, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(exact_suite_manifest(dataset_root), indent=2, sort_keys=True), encoding="utf-8")
    return output


def render_exact_suite_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# RayJoin Exact Paper Reproduction Suite",
        "",
        "This suite redefines the RayJoin benchmark app as exact reproduction of the ICS'24 RayJoin programs:",
        "",
        "- LSI via RayJoin `query_exec -query=lsi`",
        "- PIP via RayJoin `query_exec -query=pip`",
        "- polygon overlay via RayJoin `polyover_exec`",
        "",
        "Analogue inputs do not count as exact reproduction. Current RTDL overlay seed rows do not count as polygon overlay.",
        "",
        "## Dataset Pairs",
        "",
        "| Pair | Left CDB | Right CDB | Paper stats |",
        "|---|---|---|---|",
    ]
    for pair in payload["pairs"]:
        left = pair["left_stats"]
        right = pair["right_stats"]
        lines.append(
            f"| {pair['paper_label']} | `{pair['left_relative_path']}` | "
            f"`{pair['right_relative_path']}` | "
            f"{pair['left_dataset']} {left['line_segments_label']} segs/{left['polygons_label']} polys; "
            f"{pair['right_dataset']} {right['line_segments_label']} segs/{right['polygons_label']} polys |"
        )
    lines.extend(
        [
            "",
            "## RTDL Program Status",
            "",
            "| Program | RTDL OptiX route | RTDL Embree route | Status | Gap |",
            "|---|---|---|---|---|",
        ]
    )
    for program in payload["programs"]:
        lines.append(
            f"| {program['program_id']} | {program['rtdl_optix_route']} | "
            f"{program['rtdl_embree_route']} | `{program['rtdl_status']}` | {program['gap_note']} |"
        )
    lines.extend(
        [
            "",
            "## Current Availability",
            "",
            "| Case | Exact inputs | RTDL status | Blocker |",
            "|---|---:|---|---|",
        ]
    )
    for row in payload["availability"]:
        blocker = row["blocker"] or ""
        lines.append(
            f"| `{row['case_id']}` | {row['exact_input_ready']} | `{row['rtdl_status']}` | {blocker} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_exact_suite_markdown(dataset_root: str | Path, output_path: str | Path) -> Path:
    payload = exact_suite_manifest(dataset_root)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_exact_suite_markdown(payload), encoding="utf-8")
    return output
