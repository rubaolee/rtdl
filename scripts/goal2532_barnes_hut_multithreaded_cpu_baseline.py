#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import time


CPP_SOURCE = r"""
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <thread>
#include <vector>

struct Body {
    double x;
    double y;
    double mass;
};

static std::vector<Body> make_bodies(std::size_t body_count) {
    if (body_count == 0) {
        throw std::runtime_error("body_count must be positive");
    }
    std::size_t grid = static_cast<std::size_t>(std::ceil(std::sqrt(static_cast<double>(body_count))));
    std::vector<Body> bodies;
    bodies.reserve(body_count);
    for (std::size_t index = 0; index < body_count; ++index) {
        std::size_t gx = index % grid;
        std::size_t gy = index / grid;
        double denom = std::max<std::size_t>(1, grid - 1);
        double x = (static_cast<double>(gx) / denom) * 4.0 - 2.0;
        double y = (static_cast<double>(gy) / denom) * 4.0 - 2.0;
        x += (static_cast<int>((index * 17) % 11) - 5) * 0.001;
        y += (static_cast<int>((index * 31) % 13) - 6) * 0.001;
        double mass = 1.0 + (index % 7) * 0.1;
        bodies.push_back({x, y, mass});
    }
    return bodies;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        std::cerr << "usage: baseline <body_count> <threads>\n";
        return 2;
    }
    std::size_t body_count = static_cast<std::size_t>(std::stoull(argv[1]));
    unsigned int thread_count = static_cast<unsigned int>(std::stoul(argv[2]));
    if (thread_count == 0) {
        thread_count = 1;
    }
    const double softening = 0.05;
    auto bodies = make_bodies(body_count);
    std::vector<double> force_x(body_count, 0.0);
    std::vector<double> force_y(body_count, 0.0);

    auto begin = std::chrono::steady_clock::now();
    std::vector<std::thread> workers;
    workers.reserve(thread_count);
    for (unsigned int worker = 0; worker < thread_count; ++worker) {
        std::size_t start = (body_count * worker) / thread_count;
        std::size_t end = (body_count * (worker + 1)) / thread_count;
        workers.emplace_back([&, start, end]() {
            for (std::size_t i = start; i < end; ++i) {
                double fx = 0.0;
                double fy = 0.0;
                const Body &source = bodies[i];
                for (std::size_t j = 0; j < body_count; ++j) {
                    if (i == j) {
                        continue;
                    }
                    const Body &target = bodies[j];
                    double dx = target.x - source.x;
                    double dy = target.y - source.y;
                    double dist_sq = dx * dx + dy * dy + softening * softening;
                    double inv_dist = 1.0 / std::sqrt(dist_sq);
                    double scale = source.mass * target.mass * inv_dist * inv_dist * inv_dist;
                    fx += dx * scale;
                    fy += dy * scale;
                }
                force_x[i] = fx;
                force_y[i] = fy;
            }
        });
    }
    for (std::thread &worker : workers) {
        worker.join();
    }
    auto finish = std::chrono::steady_clock::now();

    double checksum_x = 0.0;
    double checksum_y = 0.0;
    for (std::size_t i = 0; i < body_count; ++i) {
        checksum_x += force_x[i];
        checksum_y += force_y[i];
    }
    double elapsed_ms = std::chrono::duration<double, std::milli>(finish - begin).count();
    std::cout << std::fixed << std::setprecision(12)
              << "{"
              << "\"baseline\":\"std_thread_exact_pairwise_force_2d\","
              << "\"body_count\":" << body_count << ","
              << "\"threads\":" << thread_count << ","
              << "\"elapsed_ms\":" << elapsed_ms << ","
              << "\"checksum_force_x\":" << checksum_x << ","
              << "\"checksum_force_y\":" << checksum_y
              << "}\n";
    return 0;
}
"""


def _parse_thread_counts(value: str) -> list[int]:
    counts: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        count = int(item)
        if count < 1:
            raise ValueError("thread counts must be positive")
        if count not in counts:
            counts.append(count)
    if not counts:
        raise ValueError("at least one thread count is required")
    return counts


def _compiler() -> str:
    requested = os.environ.get("CXX")
    if requested:
        return requested
    for candidate in ("clang++", "g++", "c++"):
        path = shutil.which(candidate)
        if path:
            return path
    raise RuntimeError("no C++ compiler found")


def run_baseline(*, body_count: int, thread_counts: list[int], keep_build_dir: bool = False) -> dict[str, object]:
    compiler = _compiler()
    temp_context = tempfile.TemporaryDirectory(prefix="rtdl_bh_baseline_")
    build_dir = Path(temp_context.name)
    source_path = build_dir / "barnes_hut_exact_baseline.cpp"
    exe_path = build_dir / "barnes_hut_exact_baseline"
    source_path.write_text(textwrap.dedent(CPP_SOURCE).strip() + "\n")

    compile_cmd = [
        compiler,
        "-std=c++17",
        "-O3",
        "-pthread",
        str(source_path),
        "-o",
        str(exe_path),
    ]
    compile_begin = time.perf_counter()
    compile_result = subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
    compile_elapsed_ms = (time.perf_counter() - compile_begin) * 1000.0

    runs: list[dict[str, object]] = []
    for thread_count in thread_counts:
        completed = subprocess.run(
            [str(exe_path), str(body_count), str(thread_count)],
            check=True,
            capture_output=True,
            text=True,
        )
        runs.append(json.loads(completed.stdout))

    if not keep_build_dir:
        temp_context.cleanup()

    return {
        "benchmark": "barnes_hut_ppopp2025_style",
        "baseline": "std_thread_exact_pairwise_force_2d",
        "body_count": body_count,
        "thread_counts": thread_counts,
        "compiler": compiler,
        "compile_elapsed_ms": compile_elapsed_ms,
        "compile_stderr": compile_result.stderr,
        "runs": runs,
        "metadata": {
            "paper_reproduction": False,
            "authors_code_comparison": False,
            "public_speedup_claim_authorized": False,
            "same_contract_as_paper_code": False,
            "claim_boundary": (
                "Local exact O(N^2) std::thread CPU baseline only. It is useful "
                "for sanity/performance pressure, but it is not RT-BarnesHut "
                "paper-code timing and not a whole-app RTDL speedup claim."
            ),
        },
        "build_dir": str(build_dir) if keep_build_dir else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Local multithreaded CPU Barnes-Hut exact-force baseline.")
    parser.add_argument("--body-count", type=int, default=2048)
    parser.add_argument("--thread-counts", default="1,4")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--keep-build-dir", action="store_true")
    args = parser.parse_args()

    payload = run_baseline(
        body_count=args.body_count,
        thread_counts=_parse_thread_counts(args.thread_counts),
        keep_build_dir=args.keep_build_dir,
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
