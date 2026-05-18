from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff_app


CPP_CONTINUATION_SOURCE = r"""
#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

struct Row {
    int query_id;
    int neighbor_id;
    double distance;
};

struct Directed {
    double distance;
    int source_id;
    int target_id;
    int row_count;
};

static Directed read_directed(std::istream& in, const std::string& expected_label) {
    std::string label;
    int n = 0;
    if (!(in >> label >> n)) {
        throw std::runtime_error("missing directed section");
    }
    if (label != expected_label) {
        throw std::runtime_error("unexpected directed section label");
    }
    if (n <= 0) {
        throw std::runtime_error("directed Hausdorff section must be non-empty");
    }

    Directed best{-1.0, 0, 0, n};
    for (int i = 0; i < n; ++i) {
        Row row{};
        if (!(in >> row.query_id >> row.neighbor_id >> row.distance)) {
            throw std::runtime_error("malformed nearest-neighbor row");
        }
        if (
            row.distance > best.distance ||
            (row.distance == best.distance && row.query_id < best.source_id) ||
            (row.distance == best.distance && row.query_id == best.source_id && row.neighbor_id < best.target_id)
        ) {
            best.distance = row.distance;
            best.source_id = row.query_id;
            best.target_id = row.neighbor_id;
        }
    }
    return best;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: hausdorff_user_cpp_continuation ROW_FILE\n";
        return 2;
    }
    try {
        std::ifstream in(argv[1]);
        if (!in) {
            throw std::runtime_error("could not open row file");
        }
        Directed ab = read_directed(in, "AB");
        Directed ba = read_directed(in, "BA");
        const bool choose_ba = ba.distance >= ab.distance;
        const Directed& undirected = choose_ba ? ba : ab;
        std::cout << std::setprecision(17)
                  << "{\"directed_a_to_b\":{\"distance\":" << ab.distance
                  << ",\"source_id\":" << ab.source_id
                  << ",\"target_id\":" << ab.target_id
                  << ",\"row_count\":" << ab.row_count
                  << "},\"directed_b_to_a\":{\"distance\":" << ba.distance
                  << ",\"source_id\":" << ba.source_id
                  << ",\"target_id\":" << ba.target_id
                  << ",\"row_count\":" << ba.row_count
                  << "},\"hausdorff_distance\":" << undirected.distance
                  << ",\"witness_direction\":\"" << (choose_ba ? "b_to_a" : "a_to_b")
                  << "\"}\n";
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 1;
    }
}
"""


def _cache_dir() -> Path:
    root = Path(os.environ.get("RTDL_HAUSDORFF_USER_CPP_CACHE", ROOT / "build" / "hausdorff_user_cpp"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def _build_cpp_continuation() -> Path:
    cache = _cache_dir()
    digest = hashlib.sha256(CPP_CONTINUATION_SOURCE.encode("utf-8")).hexdigest()[:16]
    suffix = ".exe" if sys.platform.startswith("win") else ""
    exe = cache / f"rtdl_hausdorff_user_cpp_continuation_{digest}{suffix}"
    if exe.exists():
        return exe
    source = cache / f"rtdl_hausdorff_user_cpp_continuation_{digest}.cpp"
    source.write_text(CPP_CONTINUATION_SOURCE, encoding="utf-8")
    compiler = os.environ.get("CXX", "g++")
    completed = subprocess.run(
        [compiler, "-O3", "-std=c++17", str(source), "-o", str(exe)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "failed to build learner-owned Hausdorff C++ continuation with "
            f"{compiler}: {completed.stderr.strip()}"
        )
    return exe


def _write_rows_file(rows_ab: list[dict[str, object]], rows_ba: list[dict[str, object]]) -> Path:
    digest = hashlib.sha256(
        json.dumps({"ab": rows_ab, "ba": rows_ba}, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    path = _cache_dir() / f"hausdorff_rows_{digest}.txt"
    if path.exists():
        return path
    with path.open("w", encoding="utf-8") as fh:
        fh.write(f"AB {len(rows_ab)}\n")
        for row in rows_ab:
            fh.write(f"{int(row['query_id'])} {int(row['neighbor_id'])} {float(row['distance']):.17g}\n")
        fh.write(f"BA {len(rows_ba)}\n")
        for row in rows_ba:
            fh.write(f"{int(row['query_id'])} {int(row['neighbor_id'])} {float(row['distance']):.17g}\n")
    return path


def _cpp_reduce(rows_ab: list[dict[str, object]], rows_ba: list[dict[str, object]]) -> dict[str, object]:
    exe = _build_cpp_continuation()
    rows_file = _write_rows_file(rows_ab, rows_ba)
    start = time.perf_counter()
    completed = subprocess.run(
        [str(exe), str(rows_file)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    payload["continuation_wall_sec"] = time.perf_counter() - start
    return payload


def _python_reduce(rows_ab: list[dict[str, object]], rows_ba: list[dict[str, object]]) -> dict[str, object]:
    start = time.perf_counter()
    directed_ab = hausdorff_app._directed_from_rows(rows_ab, "a_to_b")
    directed_ba = hausdorff_app._directed_from_rows(rows_ba, "b_to_a")
    undirected = max(
        (("a_to_b", directed_ab), ("b_to_a", directed_ba)),
        key=lambda item: (float(item[1]["distance"]), item[0]),
    )
    return {
        "directed_a_to_b": directed_ab,
        "directed_b_to_a": directed_ba,
        "hausdorff_distance": float(undirected[1]["distance"]),
        "witness_direction": undirected[0],
        "continuation_wall_sec": time.perf_counter() - start,
    }


def run_app(
    backend: str = "cpu_python_reference",
    copies: int = 1,
    *,
    continuation: str = "python",
) -> dict[str, object]:
    case = hausdorff_app.make_authored_point_sets(copies=copies)
    points_a = case["points_a"]
    points_b = case["points_b"]

    rtdl_start = time.perf_counter()
    rows_ab = list(hausdorff_app._run_nearest(backend, points_a, points_b))
    rows_ba = list(hausdorff_app._run_nearest(backend, points_b, points_a))
    rtdl_wall = time.perf_counter() - rtdl_start

    if continuation == "cpp":
        continuation_result = _cpp_reduce(rows_ab, rows_ba)
        continuation_kind = "learner_owned_cpp"
    elif continuation == "python":
        continuation_result = _python_reduce(rows_ab, rows_ba)
        continuation_kind = "python_reference"
    else:
        raise ValueError("continuation must be 'python' or 'cpp'")

    oracle = hausdorff_app.brute_force_hausdorff(points_a, points_b)
    matches_oracle = math.isclose(
        float(continuation_result["hausdorff_distance"]),
        float(oracle["hausdorff_distance"]),
        rel_tol=1e-9,
        abs_tol=1e-9,
    ) and continuation_result["witness_direction"] == oracle["witness_direction"]
    return {
        "app": "hausdorff_user_cpp_continuation",
        "backend": backend,
        "copies": copies,
        "point_count_a": len(points_a),
        "point_count_b": len(points_b),
        "continuation": continuation_kind,
        "rtdl_role": "RTDL emits generic k=1 nearest-neighbor rows.",
        "user_code_role": "User-owned code reduces nearest rows into directed and undirected Hausdorff summaries.",
        "counts_as_v2_partner_speedup": False,
        "why_not_v2_partner_claim": (
            "The C++ continuation is learner-owned application code. RTDL interoperates with it "
            "through Python, but its performance is not an official Torch/CuPy v2 partner claim."
        ),
        "rows_a_to_b": len(rows_ab),
        "rows_b_to_a": len(rows_ba),
        "rtdl_wall_sec": rtdl_wall,
        "continuation_wall_sec": float(continuation_result["continuation_wall_sec"]),
        "hausdorff_distance": float(continuation_result["hausdorff_distance"]),
        "witness_direction": continuation_result["witness_direction"],
        "matches_oracle": matches_oracle,
        "oracle": oracle,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hausdorff app showing RTDL plus a learner-owned C++ continuation."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree", "optix", "vulkan"),
        default="cpu_python_reference",
    )
    parser.add_argument("--copies", type=int, default=1)
    parser.add_argument("--continuation", choices=("python", "cpp"), default="python")
    args = parser.parse_args(argv)
    print(json.dumps(run_app(args.backend, args.copies, continuation=args.continuation), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
