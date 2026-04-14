from __future__ import annotations
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union


@dataclass(frozen=True)
class CuNSearchBuildConfig:
    include_dir: str
    library_path: str
    nvcc_path: str
    precision_mode: str
    current_status: str
    notes: str


def resolve_cunsearch_build_config(
    *,
    source_root: Union[str, Path],
    build_root: Union[str, Path],
    nvcc_path: Union[str, Path] = "nvcc",
) -> CuNSearchBuildConfig:
    source_root = Path(source_root).expanduser().resolve()
    build_root = Path(build_root).expanduser().resolve()
    include_dir = source_root / "include"
    library_path = build_root / "libcuNSearch.a"
    precision_mode = _detect_cunsearch_precision_mode(build_root)
    if not include_dir.is_dir() or not library_path.is_file():
        return CuNSearchBuildConfig(
            include_dir=str(include_dir),
            library_path=str(library_path),
            nvcc_path=str(nvcc_path),
            precision_mode=precision_mode,
            current_status="planned",
            notes="cuNSearch headers or built library are missing for the live driver path.",
        )
    return CuNSearchBuildConfig(
        include_dir=str(include_dir),
        library_path=str(library_path),
        nvcc_path=str(nvcc_path),
        precision_mode=precision_mode,
        current_status="ready",
        notes=(
            "cuNSearch headers and built static library are available for live bounded runs "
            f"with {precision_mode} precision."
        ),
    )


def run_cunsearch_fixed_radius_request_live(
    request_path: Union[str, Path],
    response_path: Union[str, Path],
    *,
    source_root: Union[str, Path],
    build_root: Union[str, Path],
    nvcc_path: Union[str, Path] = "nvcc",
) -> Path:
    config = resolve_cunsearch_build_config(
        source_root=source_root,
        build_root=build_root,
        nvcc_path=nvcc_path,
    )
    if config.current_status != "ready":
        raise RuntimeError(config.notes)

    request_path = Path(request_path)
    response_path = Path(response_path)
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    if payload.get("adapter") != "cunsearch":
        raise ValueError("unsupported cuNSearch request adapter")
    if payload.get("workload") != "fixed_radius_neighbors":
        raise ValueError("unsupported cuNSearch request workload")

    with TemporaryDirectory(prefix="rtdl_cunsearch_live_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        source_file = tmpdir_path / "driver.cu"
        binary_file = tmpdir_path / "driver"
        response_tmp = tmpdir_path / "response.json"
        source_file.write_text(
            _render_cunsearch_driver_source(payload, response_tmp, precision_mode=config.precision_mode),
            encoding="utf-8",
        )
        compile_proc = subprocess.run(
            [
                str(config.nvcc_path),
                "-std=c++14",
                "-O2",
                *(_precision_compile_flags(config.precision_mode)),
                "-I",
                config.include_dir,
                str(source_file),
                config.library_path,
                "-o",
                str(binary_file),
            ],
            capture_output=True,
            text=True,
        )
        if compile_proc.returncode != 0:
            raise RuntimeError(
                "cuNSearch live driver compilation failed.\n"
                f"stdout:\n{compile_proc.stdout}\n"
                f"stderr:\n{compile_proc.stderr}"
            )
        run_proc = subprocess.run(
            [str(binary_file)],
            capture_output=True,
            text=True,
        )
        if run_proc.returncode != 0:
            raise RuntimeError(
                "cuNSearch live driver execution failed.\n"
                f"stdout:\n{run_proc.stdout}\n"
                f"stderr:\n{run_proc.stderr}"
            )
        response_path.parent.mkdir(parents=True, exist_ok=True)
        response_path.write_text(response_tmp.read_text(encoding="utf-8"), encoding="utf-8")
    return response_path


def compile_cunsearch_fixed_radius_request_driver(
    request_path: Union[str, Path],
    response_path: Union[str, Path],
    output_dir: Union[str, Path],
    *,
    source_root: Union[str, Path],
    build_root: Union[str, Path],
    nvcc_path: Union[str, Path] = "nvcc",
) -> Path:
    config = resolve_cunsearch_build_config(
        source_root=source_root,
        build_root=build_root,
        nvcc_path=nvcc_path,
    )
    if config.current_status != "ready":
        raise RuntimeError(config.notes)

    request_path = Path(request_path)
    response_path = Path(response_path)
    output_dir = Path(output_dir)
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    if payload.get("adapter") != "cunsearch":
        raise ValueError("unsupported cuNSearch request adapter")
    if payload.get("workload") != "fixed_radius_neighbors":
        raise ValueError("unsupported cuNSearch request workload")

    output_dir.mkdir(parents=True, exist_ok=True)
    source_file = output_dir / "driver.cu"
    binary_file = output_dir / "driver"
    source_file.write_text(
        _render_cunsearch_driver_source(payload, response_path, precision_mode=config.precision_mode),
        encoding="utf-8",
    )
    compile_proc = subprocess.run(
        [
            str(config.nvcc_path),
            "-std=c++14",
            "-O2",
            *(_precision_compile_flags(config.precision_mode)),
            "-I",
            config.include_dir,
            str(source_file),
            config.library_path,
            "-o",
            str(binary_file),
        ],
        capture_output=True,
        text=True,
    )
    if compile_proc.returncode != 0:
        raise RuntimeError(
            "cuNSearch live driver compilation failed.\n"
            f"stdout:\n{compile_proc.stdout}\n"
            f"stderr:\n{compile_proc.stderr}"
        )
    return binary_file


def execute_compiled_cunsearch_fixed_radius_driver(
    binary_path: Union[str, Path],
    *,
    response_path: Optional[Union[str, Path]] = None,
) -> float:
    binary_path = Path(binary_path)
    start = time.perf_counter()
    run_proc = subprocess.run(
        [str(binary_path)],
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if run_proc.returncode != 0:
        raise RuntimeError(
            "cuNSearch live driver execution failed.\n"
            f"stdout:\n{run_proc.stdout}\n"
            f"stderr:\n{run_proc.stderr}"
        )
    if response_path is not None and not Path(response_path).is_file():
        raise RuntimeError("cuNSearch live driver completed without producing the expected response file")
    return elapsed


def _render_cunsearch_driver_source(
    payload: dict[str, object],
    response_tmp: Path,
    *,
    precision_mode: str = "double",
) -> str:
    radius = float(payload["radius"])
    k_max = int(payload["k_max"])
    query_points = tuple(payload["query_points"])
    search_points = tuple(payload["search_points"])
    real_literal_suffix = "f" if precision_mode == "float" else ""

    def render_points(points) -> str:
        rows = []
        for point in points:
            rows.append(
                "        {{{x}{suffix}, {y}{suffix}, {z}{suffix}}}".format(
                    x=float(point["x"]),
                    y=float(point["y"]),
                    z=float(point["z"]),
                    suffix=real_literal_suffix,
                )
            )
        if not rows:
            return ""
        return ",\n".join(rows)

    def render_ids(points) -> str:
        return ", ".join(str(int(point["id"])) for point in points)

    return f"""#include "cuNSearch.h"
#include <array>
#include <cmath>
#include <algorithm>
#include <fstream>
#include <iomanip>
#include <stdexcept>
#include <tuple>
#include <vector>

using namespace cuNSearch;

using Real3 = std::array<Real, 3>;

int main() {{
    std::vector<Real3> query_points = {{
{render_points(query_points)}
    }};
    std::vector<Real3> search_points = {{
{render_points(search_points)}
    }};
    std::vector<unsigned int> query_ids = {{ {render_ids(query_points)} }};
    std::vector<unsigned int> search_ids = {{ {render_ids(search_points)} }};

    NeighborhoodSearch nsearch(static_cast<Real>({radius}{real_literal_suffix}));
    unsigned int query_set = nsearch.add_point_set(query_points.front().data(), query_points.size(), true, true, true, nullptr);
    unsigned int search_set = nsearch.add_point_set(search_points.front().data(), search_points.size(), false, true, true, nullptr);
    nsearch.set_active(query_set, query_set, false);
    nsearch.set_active(search_set, search_set, false);
    nsearch.set_active(search_set, query_set, false);
    nsearch.set_active(query_set, search_set, true);
    nsearch.find_neighbors();

    std::ofstream out("{response_tmp.as_posix()}");
    out << "{{\\n";
    out << "  \\"adapter\\": \\"cunsearch\\",\\n";
    out << "  \\"response_format\\": \\"json_rows_v1\\",\\n";
    out << "  \\"workload\\": \\"fixed_radius_neighbors\\",\\n";
    out << "  \\"rows\\": [\\n";
    out << std::setprecision({17 if precision_mode == "double" else 9});

    bool first = true;
    auto const& point_set = nsearch.point_set(query_set);
    for (unsigned int i = 0; i < point_set.n_points(); ++i) {{
        auto count = point_set.n_neighbors(search_set, i);
        auto q = query_points[i];
        std::vector<std::tuple<double, unsigned int, unsigned int>> neighbors;
        neighbors.reserve(count);
        for (unsigned int j = 0; j < count; ++j) {{
            unsigned int neighbor_index = point_set.neighbor(search_set, i, j);
            auto s = search_points[neighbor_index];
            double dx = static_cast<double>(q[0]) - static_cast<double>(s[0]);
            double dy = static_cast<double>(q[1]) - static_cast<double>(s[1]);
            double dz = static_cast<double>(q[2]) - static_cast<double>(s[2]);
            double distance = std::sqrt(dx * dx + dy * dy + dz * dz);
            neighbors.push_back(std::make_tuple(distance, search_ids[neighbor_index], neighbor_index));
        }}
        std::sort(neighbors.begin(), neighbors.end());
        auto keep_count = std::min<std::size_t>(neighbors.size(), static_cast<std::size_t>({k_max}));
        for (std::size_t j = 0; j < keep_count; ++j) {{
            double distance = std::get<0>(neighbors[j]);
            unsigned int neighbor_id = std::get<1>(neighbors[j]);
            if (!first) out << ",\\n";
            first = false;
            out << "    {{\\"query_id\\":" << query_ids[i]
                << ",\\"neighbor_id\\":" << neighbor_id
                << ",\\"distance\\":" << distance << "}}";
        }}
    }}
    out << "\\n  ]\\n";
    out << "}}\\n";
    return 0;
}}
"""


def _detect_cunsearch_precision_mode(build_root: Path) -> str:
    cache_path = build_root / "CMakeCache.txt"
    if not cache_path.is_file():
        return "double"
    cache_text = cache_path.read_text(encoding="utf-8", errors="replace")
    marker = "CUNSEARCH_USE_DOUBLE_PRECISION:BOOL="
    for line in cache_text.splitlines():
        if line.startswith(marker):
            return "double" if line[len(marker):].strip().upper() == "ON" else "float"
    return "double"


def _precision_compile_flags(precision_mode: str) -> tuple[str, ...]:
    if precision_mode == "double":
        return ("-DCUNSEARCH_USE_DOUBLE_PRECISION",)
    return ()
