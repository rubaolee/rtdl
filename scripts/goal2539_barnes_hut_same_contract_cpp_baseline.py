from __future__ import annotations

import argparse
import json
from pathlib import Path
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
#include <limits>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <thread>
#include <vector>

struct Body {
    int id;
    double x;
    double y;
    double mass;
};

struct Node {
    int id;
    double cx;
    double cy;
    double half_size;
    double mass;
    std::vector<int> member_indices;
    std::vector<int> child_indices;
    int depth;
    int dfs_index;
    int resume_index;
    double cell_cx;
    double cell_cy;
    bool is_leaf;
};

struct Force {
    double x = 0.0;
    double y = 0.0;
    std::uint64_t visited = 0;
    std::uint64_t aggregate_count = 0;
    std::uint64_t exact_count = 0;
};

static std::uint64_t morton_code_2d(
    double x,
    double y,
    double min_x,
    double min_y,
    double span,
    int bits
) {
    if (bits < 1 || bits > 30) {
        throw std::runtime_error("bits must be between 1 and 30");
    }
    if (span <= 0.0) {
        throw std::runtime_error("span must be positive");
    }
    const int scale = (1 << bits) - 1;
    auto clamp_coord = [&](double value, double min_value) {
        long long rounded = std::llround(((value - min_value) / span) * static_cast<double>(scale));
        if (rounded < 0) {
            return 0;
        }
        if (rounded > scale) {
            return scale;
        }
        return static_cast<int>(rounded);
    };
    const int xi = clamp_coord(x, min_x);
    const int yi = clamp_coord(y, min_y);
    std::uint64_t code = 0;
    for (int bit = 0; bit < bits; ++bit) {
        code |= static_cast<std::uint64_t>((xi >> bit) & 1) << (2 * bit);
        code |= static_cast<std::uint64_t>((yi >> bit) & 1) << (2 * bit + 1);
    }
    return code;
}

static std::vector<Body> make_generated_bodies(int body_count) {
    if (body_count < 1) {
        throw std::runtime_error("body_count must be positive");
    }
    const int grid = static_cast<int>(std::ceil(std::sqrt(static_cast<double>(body_count))));
    std::vector<Body> bodies;
    bodies.reserve(static_cast<std::size_t>(body_count));
    for (int index = 0; index < body_count; ++index) {
        const int gx = index % grid;
        const int gy = index / grid;
        double x = (static_cast<double>(gx) / static_cast<double>(std::max(1, grid - 1))) * 4.0 - 2.0;
        double y = (static_cast<double>(gy) / static_cast<double>(std::max(1, grid - 1))) * 4.0 - 2.0;
        x += static_cast<double>(((index * 17) % 11) - 5) * 0.001;
        y += static_cast<double>(((index * 31) % 13) - 6) * 0.001;
        const double mass = 1.0 + static_cast<double>(index % 7) * 0.1;
        bodies.push_back(Body{index + 1, x, y, mass});
    }
    return bodies;
}

static int add_node(
    const std::vector<Body>& bodies,
    const std::vector<int>& members,
    std::vector<Node>& nodes,
    int bucket_size,
    int max_depth,
    double cell_cx,
    double cell_cy,
    double node_half_size,
    int depth
) {
    double mass = 0.0;
    for (int index : members) {
        mass += bodies[static_cast<std::size_t>(index)].mass;
    }
    double center_mass_x = 0.0;
    double center_mass_y = 0.0;
    if (mass == 0.0) {
        for (int index : members) {
            center_mass_x += bodies[static_cast<std::size_t>(index)].x;
            center_mass_y += bodies[static_cast<std::size_t>(index)].y;
        }
        center_mass_x /= static_cast<double>(members.size());
        center_mass_y /= static_cast<double>(members.size());
    } else {
        for (int index : members) {
            const Body& body = bodies[static_cast<std::size_t>(index)];
            center_mass_x += body.x * body.mass;
            center_mass_y += body.y * body.mass;
        }
        center_mass_x /= mass;
        center_mass_y /= mass;
    }

    const int node_index = static_cast<int>(nodes.size());
    const bool is_leaf = static_cast<int>(members.size()) <= bucket_size
        || depth >= max_depth
        || node_half_size == 0.0;
    nodes.push_back(Node{
        node_index + 1,
        center_mass_x,
        center_mass_y,
        node_half_size,
        mass,
        members,
        {},
        depth,
        node_index,
        -1,
        cell_cx,
        cell_cy,
        is_leaf,
    });

    if (!is_leaf) {
        std::vector<int> quadrants[4];
        for (int index : members) {
            const Body& body = bodies[static_cast<std::size_t>(index)];
            const bool east = body.x >= cell_cx;
            const bool north = body.y >= cell_cy;
            const int quadrant = (east ? 1 : 0) + (north ? 2 : 0);
            quadrants[quadrant].push_back(index);
        }
        const double child_half_size = node_half_size / 2.0;
        const double offsets[4][2] = {
            {-child_half_size, -child_half_size},
            {child_half_size, -child_half_size},
            {-child_half_size, child_half_size},
            {child_half_size, child_half_size},
        };
        for (int quadrant = 0; quadrant < 4; ++quadrant) {
            if (quadrants[quadrant].empty()) {
                continue;
            }
            const int child_index = add_node(
                bodies,
                quadrants[quadrant],
                nodes,
                bucket_size,
                max_depth,
                cell_cx + offsets[quadrant][0],
                cell_cy + offsets[quadrant][1],
                child_half_size,
                depth + 1
            );
            nodes[static_cast<std::size_t>(node_index)].child_indices.push_back(child_index);
        }
        nodes[static_cast<std::size_t>(node_index)].is_leaf =
            nodes[static_cast<std::size_t>(node_index)].child_indices.empty();
    }
    return node_index;
}

static int subtree_end_index(const std::vector<Node>& nodes, int index) {
    const Node& node = nodes[static_cast<std::size_t>(index)];
    if (node.child_indices.empty()) {
        return index + 1;
    }
    int end_index = index + 1;
    for (int child_index : node.child_indices) {
        end_index = std::max(end_index, subtree_end_index(nodes, child_index));
    }
    return end_index;
}

static std::vector<Node> build_bucketized_tree(
    const std::vector<Body>& bodies,
    int bucket_size,
    int max_depth,
    int morton_bits
) {
    double min_x = bodies.front().x;
    double max_x = bodies.front().x;
    double min_y = bodies.front().y;
    double max_y = bodies.front().y;
    for (const Body& body : bodies) {
        min_x = std::min(min_x, body.x);
        max_x = std::max(max_x, body.x);
        min_y = std::min(min_y, body.y);
        max_y = std::max(max_y, body.y);
    }
    double span = std::max(max_x - min_x, max_y - min_y);
    if (span == 0.0) {
        span = 1.0;
    }
    span += 2.0e-9;
    const double center_x = (min_x + max_x) / 2.0;
    const double center_y = (min_y + max_y) / 2.0;
    const double half_size = span / 2.0;
    const double square_min_x = center_x - half_size;
    const double square_min_y = center_y - half_size;

    std::vector<int> ordered_indices(bodies.size());
    std::iota(ordered_indices.begin(), ordered_indices.end(), 0);
    std::stable_sort(ordered_indices.begin(), ordered_indices.end(), [&](int left, int right) {
        const Body& a = bodies[static_cast<std::size_t>(left)];
        const Body& b = bodies[static_cast<std::size_t>(right)];
        const std::uint64_t code_a = morton_code_2d(a.x, a.y, square_min_x, square_min_y, span, morton_bits);
        const std::uint64_t code_b = morton_code_2d(b.x, b.y, square_min_x, square_min_y, span, morton_bits);
        if (code_a != code_b) {
            return code_a < code_b;
        }
        return a.id < b.id;
    });

    std::vector<Node> nodes;
    nodes.reserve(bodies.size() * 2);
    add_node(
        bodies,
        ordered_indices,
        nodes,
        bucket_size,
        max_depth,
        center_x,
        center_y,
        half_size,
        0
    );
    for (std::size_t index = 0; index < nodes.size(); ++index) {
        const int end_index = subtree_end_index(nodes, static_cast<int>(index));
        nodes[index].resume_index = end_index < static_cast<int>(nodes.size()) ? end_index : -1;
    }
    return nodes;
}

static bool node_contains_source(const Node& node, int source_index) {
    return std::find(node.member_indices.begin(), node.member_indices.end(), source_index) != node.member_indices.end();
}

static void add_force(Force& force, const Body& source, double target_x, double target_y, double target_mass, double softening) {
    const double dx = target_x - source.x;
    const double dy = target_y - source.y;
    const double dist_sq = dx * dx + dy * dy + softening * softening;
    if (dist_sq == 0.0) {
        return;
    }
    const double inv_dist = 1.0 / std::sqrt(dist_sq);
    const double scale = source.mass * target_mass * inv_dist * inv_dist * inv_dist;
    force.x += dx * scale;
    force.y += dy * scale;
}

static void visit_node(
    const std::vector<Body>& bodies,
    const std::vector<Node>& nodes,
    int source_index,
    int node_index,
    double theta,
    double softening,
    Force& force
) {
    const Body& source = bodies[static_cast<std::size_t>(source_index)];
    const Node& node = nodes[static_cast<std::size_t>(node_index)];
    force.visited += 1;
    const double dx = node.cx - source.x;
    const double dy = node.cy - source.y;
    const double distance = std::hypot(dx, dy);
    const double opening_ratio = distance == 0.0
        ? std::numeric_limits<double>::infinity()
        : (2.0 * node.half_size) / distance;
    if (!node_contains_source(node, source_index) && opening_ratio < theta) {
        add_force(force, source, node.cx, node.cy, node.mass, softening);
        force.aggregate_count += 1;
        return;
    }
    if (!node.child_indices.empty()) {
        for (int child_index : node.child_indices) {
            visit_node(bodies, nodes, source_index, child_index, theta, softening, force);
        }
        return;
    }
    for (int target_index : node.member_indices) {
        if (target_index == source_index) {
            continue;
        }
        const Body& target = bodies[static_cast<std::size_t>(target_index)];
        add_force(force, source, target.x, target.y, target.mass, softening);
        force.exact_count += 1;
    }
}

static std::vector<Force> compute_forces(
    const std::vector<Body>& bodies,
    const std::vector<Node>& nodes,
    double theta,
    double softening,
    int thread_count
) {
    if (thread_count < 1) {
        throw std::runtime_error("thread_count must be positive");
    }
    std::vector<Force> forces(bodies.size());
    const int body_count = static_cast<int>(bodies.size());
    const int active_threads = std::min(thread_count, body_count);
    std::vector<std::thread> threads;
    threads.reserve(static_cast<std::size_t>(active_threads));
    for (int thread_index = 0; thread_index < active_threads; ++thread_index) {
        const int begin = (body_count * thread_index) / active_threads;
        const int end = (body_count * (thread_index + 1)) / active_threads;
        threads.emplace_back([&, begin, end]() {
            for (int source_index = begin; source_index < end; ++source_index) {
                visit_node(bodies, nodes, source_index, 0, theta, softening, forces[static_cast<std::size_t>(source_index)]);
            }
        });
    }
    for (std::thread& thread : threads) {
        thread.join();
    }
    return forces;
}

static std::vector<int> parse_thread_counts(const std::string& value) {
    std::vector<int> counts;
    std::stringstream stream(value);
    std::string item;
    while (std::getline(stream, item, ',')) {
        if (!item.empty()) {
            counts.push_back(std::stoi(item));
        }
    }
    if (counts.empty()) {
        throw std::runtime_error("at least one thread count is required");
    }
    return counts;
}

int main(int argc, char** argv) {
    int body_count = 8192;
    int bucket_size = 32;
    int max_depth = 32;
    int morton_bits = 16;
    double theta = 0.75;
    double softening = 0.05;
    std::string thread_counts_text = "1,4,16";

    for (int index = 1; index < argc; ++index) {
        const std::string arg = argv[index];
        auto require_value = [&](const char* name) -> std::string {
            if (index + 1 >= argc) {
                throw std::runtime_error(std::string(name) + " requires a value");
            }
            return argv[++index];
        };
        if (arg == "--body-count") {
            body_count = std::stoi(require_value("--body-count"));
        } else if (arg == "--bucket-size") {
            bucket_size = std::stoi(require_value("--bucket-size"));
        } else if (arg == "--max-depth") {
            max_depth = std::stoi(require_value("--max-depth"));
        } else if (arg == "--morton-bits") {
            morton_bits = std::stoi(require_value("--morton-bits"));
        } else if (arg == "--theta") {
            theta = std::stod(require_value("--theta"));
        } else if (arg == "--softening") {
            softening = std::stod(require_value("--softening"));
        } else if (arg == "--thread-counts") {
            thread_counts_text = require_value("--thread-counts");
        } else {
            throw std::runtime_error("unknown argument: " + arg);
        }
    }

    const auto build_start = std::chrono::steady_clock::now();
    const std::vector<Body> bodies = make_generated_bodies(body_count);
    const std::vector<Node> nodes = build_bucketized_tree(bodies, bucket_size, max_depth, morton_bits);
    const auto build_end = std::chrono::steady_clock::now();
    const double build_ms = std::chrono::duration<double, std::milli>(build_end - build_start).count();

    std::cout << std::fixed << std::setprecision(12);
    std::cout << "{";
    std::cout << "\"baseline\":\"std_thread_same_contract_barnes_hut_2d\",";
    std::cout << "\"body_count\":" << body_count << ",";
    std::cout << "\"bucket_size\":" << bucket_size << ",";
    std::cout << "\"theta\":" << theta << ",";
    std::cout << "\"softening\":" << softening << ",";
    std::cout << "\"build_ms\":" << build_ms << ",";
    std::cout << "\"tree_summary\":{";
    std::cout << "\"source_count\":" << bodies.size() << ",";
    std::cout << "\"tree_node_count\":" << nodes.size() << ",";
    std::size_t leaf_count = 0;
    int max_tree_depth = 0;
    std::size_t max_leaf_member_count = 0;
    for (const Node& node : nodes) {
        max_tree_depth = std::max(max_tree_depth, node.depth);
        if (node.is_leaf) {
            leaf_count += 1;
            max_leaf_member_count = std::max(max_leaf_member_count, node.member_indices.size());
        }
    }
    std::cout << "\"leaf_node_count\":" << leaf_count << ",";
    std::cout << "\"max_depth\":" << max_tree_depth << ",";
    std::cout << "\"max_leaf_member_count\":" << max_leaf_member_count;
    std::cout << "},";
    std::cout << "\"metadata\":{";
    std::cout << "\"authors_code_comparison\":false,";
    std::cout << "\"paper_reproduction\":false,";
    std::cout << "\"public_speedup_claim_authorized\":false,";
    std::cout << "\"same_contract_as_rtdl_fused_reference\":true";
    std::cout << "},";
    std::cout << "\"runs\":[";

    const std::vector<int> thread_counts = parse_thread_counts(thread_counts_text);
    bool first = true;
    for (int thread_count : thread_counts) {
        const auto force_start = std::chrono::steady_clock::now();
        const std::vector<Force> forces = compute_forces(bodies, nodes, theta, softening, thread_count);
        const auto force_end = std::chrono::steady_clock::now();
        const double force_ms = std::chrono::duration<double, std::milli>(force_end - force_start).count();
        double checksum_x = 0.0;
        double checksum_y = 0.0;
        std::uint64_t visited_total = 0;
        std::uint64_t aggregate_total = 0;
        std::uint64_t exact_total = 0;
        for (const Force& force : forces) {
            checksum_x += force.x;
            checksum_y += force.y;
            visited_total += force.visited;
            aggregate_total += force.aggregate_count;
            exact_total += force.exact_count;
        }
        if (!first) {
            std::cout << ",";
        }
        first = false;
        std::cout << "{";
        std::cout << "\"threads\":" << thread_count << ",";
        std::cout << "\"force_ms\":" << force_ms << ",";
        std::cout << "\"checksum_force_x\":" << checksum_x << ",";
        std::cout << "\"checksum_force_y\":" << checksum_y << ",";
        std::cout << "\"visited_node_total\":" << visited_total << ",";
        std::cout << "\"aggregate_contribution_row_count\":" << aggregate_total << ",";
        std::cout << "\"exact_contribution_row_count\":" << exact_total << ",";
        std::cout << "\"contribution_row_count\":" << (aggregate_total + exact_total);
        std::cout << "}";
    }
    std::cout << "]}";
    return 0;
}
"""


def _compile(source_path: Path, binary_path: Path, compiler: str, cxx_flags: tuple[str, ...]) -> dict[str, object]:
    command = [compiler, *cxx_flags, "-std=c++17", "-O3", "-pthread", str(source_path), "-o", str(binary_path)]
    start = time.perf_counter()
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return {
        "command": command,
        "elapsed_ms": (time.perf_counter() - start) * 1000.0,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_baseline(
    *,
    body_count: int,
    thread_counts: str,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    compiler: str,
    cxx_flags: tuple[str, ...],
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="rtdl_bh_cpp_") as tmpdir:
        tmp = Path(tmpdir)
        source_path = tmp / "same_contract_barnes_hut.cpp"
        binary_path = tmp / "same_contract_barnes_hut"
        source_path.write_text(CPP_SOURCE)
        compile_result = _compile(source_path, binary_path, compiler, cxx_flags)
        if compile_result["returncode"] != 0:
            return {
                "baseline": "std_thread_same_contract_barnes_hut_2d",
                "body_count": body_count,
                "compile": compile_result,
                "metadata": {
                    "authors_code_comparison": False,
                    "paper_reproduction": False,
                    "public_speedup_claim_authorized": False,
                    "same_contract_as_rtdl_fused_reference": True,
                },
                "runs": [],
            }
        command = [
            str(binary_path),
            "--body-count",
            str(body_count),
            "--thread-counts",
            thread_counts,
            "--bucket-size",
            str(bucket_size),
            "--max-depth",
            str(max_depth),
            "--theta",
            str(theta),
            "--softening",
            str(softening),
        ]
        start = time.perf_counter()
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        payload = json.loads(completed.stdout)
        payload["compile"] = compile_result
        payload["run_command"] = command
        payload["run_elapsed_ms"] = (time.perf_counter() - start) * 1000.0
        return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="C++ same-contract Barnes-Hut fused vector-sum baseline.")
    parser.add_argument("--body-count", type=int, default=8192)
    parser.add_argument("--thread-counts", default="1,4,16")
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--theta", type=float, default=0.75)
    parser.add_argument("--softening", type=float, default=0.05)
    parser.add_argument("--compiler", default="g++")
    parser.add_argument("--cxx-flag", action="append", default=[])
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    payload = run_baseline(
        body_count=args.body_count,
        thread_counts=args.thread_counts,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
        theta=args.theta,
        softening=args.softening,
        compiler=args.compiler,
        cxx_flags=tuple(args.cxx_flag),
    )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n")
    print(text)
    return 0 if payload.get("compile", {}).get("returncode") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
