#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr double kEpsilon = 1.0e-9;

struct Point {
    double x;
    double y;
};

struct Triangle {
    int triangle_id;
    int query_group_id;
    bool is_query;
    Point vertices[3];
};

using WitnessRow = std::tuple<int, int, int>;

double cross(const Point& origin, const Point& a, const Point& b) {
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x);
}

bool on_segment(const Point& a, const Point& b, const Point& p) {
    if (std::abs(cross(a, b, p)) > kEpsilon) {
        return false;
    }
    return std::min(a.x, b.x) - kEpsilon <= p.x && p.x <= std::max(a.x, b.x) + kEpsilon &&
           std::min(a.y, b.y) - kEpsilon <= p.y && p.y <= std::max(a.y, b.y) + kEpsilon;
}

bool segment_intersects(const Point& a, const Point& b, const Point& c, const Point& d) {
    const double ab_c = cross(a, b, c);
    const double ab_d = cross(a, b, d);
    const double cd_a = cross(c, d, a);
    const double cd_b = cross(c, d, b);
    if (((ab_c > kEpsilon && ab_d < -kEpsilon) || (ab_c < -kEpsilon && ab_d > kEpsilon)) &&
        ((cd_a > kEpsilon && cd_b < -kEpsilon) || (cd_a < -kEpsilon && cd_b > kEpsilon))) {
        return true;
    }
    return on_segment(a, b, c) || on_segment(a, b, d) || on_segment(c, d, a) || on_segment(c, d, b);
}

bool point_in_triangle(const Point& point, const Point vertices[3]) {
    const double c1 = cross(vertices[0], vertices[1], point);
    const double c2 = cross(vertices[1], vertices[2], point);
    const double c3 = cross(vertices[2], vertices[0], point);
    const bool has_negative = c1 < -kEpsilon || c2 < -kEpsilon || c3 < -kEpsilon;
    const bool has_positive = c1 > kEpsilon || c2 > kEpsilon || c3 > kEpsilon;
    return !(has_negative && has_positive);
}

bool triangles_intersect(const Triangle& left, const Triangle& right) {
    for (const Point& point : left.vertices) {
        if (point_in_triangle(point, right.vertices)) {
            return true;
        }
    }
    for (const Point& point : right.vertices) {
        if (point_in_triangle(point, left.vertices)) {
            return true;
        }
    }
    const int edges[3][2] = {{0, 1}, {1, 2}, {2, 0}};
    for (const auto& left_edge : edges) {
        for (const auto& right_edge : edges) {
            if (segment_intersects(
                    left.vertices[left_edge[0]],
                    left.vertices[left_edge[1]],
                    right.vertices[right_edge[0]],
                    right.vertices[right_edge[1]])) {
                return true;
            }
        }
    }
    return false;
}

Triangle make_triangle(int triangle_id, int query_group_id, bool is_query, Point a, Point b, Point c) {
    Triangle triangle{};
    triangle.triangle_id = triangle_id;
    triangle.query_group_id = query_group_id;
    triangle.is_query = is_query;
    triangle.vertices[0] = a;
    triangle.vertices[1] = b;
    triangle.vertices[2] = c;
    return triangle;
}

void build_tiny(std::vector<Triangle>& scene, std::vector<Triangle>& query) {
    scene.push_back(make_triangle(0, -1, false, {0.0, 0.0}, {1.0, 0.0}, {0.0, 1.0}));
    scene.push_back(make_triangle(1, -1, false, {3.0, 0.0}, {4.0, 0.0}, {3.0, 1.0}));
    scene.push_back(make_triangle(2, -1, false, {0.0, 3.0}, {1.0, 3.0}, {0.0, 4.0}));
    query.push_back(make_triangle(10, 0, true, {0.10, 0.10}, {0.80, 0.10}, {0.10, 0.80}));
    query.push_back(make_triangle(11, 0, true, {3.20, 0.20}, {3.70, 0.20}, {3.20, 0.70}));
    query.push_back(make_triangle(20, 1, true, {5.00, 5.00}, {6.00, 5.00}, {5.00, 6.00}));
    query.push_back(make_triangle(30, 2, true, {0.20, 3.20}, {0.70, 3.20}, {0.20, 3.70}));
}

void build_grid(int cell_count, std::vector<Triangle>& scene, std::vector<Triangle>& query) {
    if (cell_count <= 0) {
        throw std::runtime_error("grid-count must be positive");
    }
    for (int index = 0; index < cell_count; ++index) {
        const double x0 = static_cast<double>(index * 3);
        scene.push_back(make_triangle(10000 + index, -1, false, {x0, 0.0}, {x0 + 1.0, 0.0}, {x0, 1.0}));
        query.push_back(make_triangle(
            20000 + index,
            index,
            true,
            {x0 + 0.10, 0.10},
            {x0 + 0.80, 0.10},
            {x0 + 0.10, 0.80}));
    }
}

std::vector<WitnessRow> collect_rows(const std::vector<Triangle>& scene, const std::vector<Triangle>& query) {
    std::set<WitnessRow> unique_rows;
    for (const Triangle& query_triangle : query) {
        for (const Triangle& scene_triangle : scene) {
            if (triangles_intersect(query_triangle, scene_triangle)) {
                unique_rows.insert({query_triangle.query_group_id, query_triangle.triangle_id, scene_triangle.triangle_id});
            }
        }
    }
    return {unique_rows.begin(), unique_rows.end()};
}

int parse_int_arg(char** argv, int argc, const std::string& name, int default_value) {
    for (int index = 1; index + 1 < argc; ++index) {
        if (argv[index] == name) {
            return std::atoi(argv[index + 1]);
        }
    }
    return default_value;
}

std::string parse_string_arg(char** argv, int argc, const std::string& name, const std::string& default_value) {
    for (int index = 1; index + 1 < argc; ++index) {
        if (argv[index] == name) {
            return argv[index + 1];
        }
    }
    return default_value;
}

}  // namespace

int main(int argc, char** argv) {
    try {
        const std::string dataset = parse_string_arg(argv, argc, "--dataset", "tiny");
        const int grid_count = parse_int_arg(argv, argc, "--grid-count", 64);
        const int repeat_count = std::max(1, parse_int_arg(argv, argc, "--repeat-count", 5));

        std::vector<Triangle> scene;
        std::vector<Triangle> query;
        if (dataset == "tiny" || dataset == "overflow") {
            build_tiny(scene, query);
        } else if (dataset == "grid") {
            build_grid(grid_count, scene, query);
        } else {
            throw std::runtime_error("unknown dataset");
        }

        std::vector<WitnessRow> rows;
        double best_seconds = 1.0e100;
        for (int repeat = 0; repeat < repeat_count; ++repeat) {
            const auto started = std::chrono::steady_clock::now();
            rows = collect_rows(scene, query);
            const auto stopped = std::chrono::steady_clock::now();
            const std::chrono::duration<double> elapsed = stopped - started;
            best_seconds = std::min(best_seconds, elapsed.count());
        }

        std::cout << "{";
        std::cout << "\"baseline\":\"standalone_cpp_exact_triangle_pairs\",";
        std::cout << "\"dataset\":\"" << (dataset == "grid" ? "grid_" + std::to_string(grid_count) : "tiny") << "\",";
        std::cout << "\"scene_triangle_count\":" << scene.size() << ",";
        std::cout << "\"query_triangle_count\":" << query.size() << ",";
        std::cout << "\"repeat_count\":" << repeat_count << ",";
        std::cout << "\"valid_count\":" << rows.size() << ",";
        std::cout << "\"elapsed_sec\":" << best_seconds << ",";
        std::cout << "\"candidate_id_rows\":[";
        for (std::size_t index = 0; index < rows.size(); ++index) {
            if (index != 0) {
                std::cout << ",";
            }
            const auto [group_id, query_id, scene_id] = rows[index];
            std::cout << "[" << group_id << "," << query_id << "," << scene_id << "]";
        }
        std::cout << "],";
        std::cout << "\"claim_boundary\":\"Standalone C++ exact baseline; no RTDL engine calls and no RT-core claim.\"";
        std::cout << "}\n";
        return 0;
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 1;
    }
}
