#include "Goal5800Types.h"

#include <cuda_runtime_api.h>
#include <owl/owl.h>

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using goal5800::Box;
using goal5800::Ray;
using goal5800::RelationGeomData;
using goal5800::RelationRayGenData;
using goal5800::RelationRow;
using goal5800::TriangleRayGenData;

extern "C" char deviceCode_ptx[];

namespace {

struct RelationObservation {
  std::vector<std::pair<uint32_t, uint32_t>> rows;
  uint32_t raw_count{};
  uint32_t overflow{};
  uint32_t status{};
};

struct TriangleObservation {
  std::vector<uint64_t> per_ray;
  uint64_t weighted_sum{};
  uint32_t status{};
};

Box box(float lx, float ly, float ux, float uy, uint32_t id) {
  return Box{owl3f{lx, ly, -0.01f}, owl3f{ux, uy, 0.01f}, id};
}

std::vector<Box> diagnostic_indexed() {
  return {box(0.f, 0.f, 4.f, 1.f, 10), box(0.f, 0.f, 1.f, 4.f, 20)};
}

std::vector<Box> diagnostic_queries() {
  return {box(2.f, .25f, 3.f, .75f, 100),
          box(.25f, 2.f, .75f, 3.f, 101)};
}

std::vector<Box> broad_indexed() {
  return {box(0.f, 0.f, 2.f, 2.f, 0), box(1.f, 1.f, 3.f, 3.f, 1),
          box(-2.f, -2.f, -1.f, -1.f, 2),
          box(10.f, 10.f, 11.f, 11.f, 3)};
}

std::vector<Box> broad_queries() {
  return {box(1.25f, 1.25f, 1.75f, 1.75f, 0),
          box(0.f, 0.f, 2.f, 2.f, 1),
          box(.5f, .5f, 2.5f, 2.5f, 2),
          box(-1.75f, -1.75f, -1.25f, -1.25f, 3),
          box(10.f, 10.f, 11.f, 11.f, 4)};
}

RelationObservation run_relation(const char *intersect_program,
                                 const char *raygen_program,
                                 const std::vector<Box> &indexed,
                                 const std::vector<Box> &queries,
                                 uint32_t capacity) {
  OWLContext context = owlContextCreate(nullptr, 1);
  owlContextSetNumAttributeValues(context, 1);
  owlContextSetNumPayloadValues(context, 2);
  OWLModule module = owlModuleCreate(context, deviceCode_ptx);

  OWLVarDecl geom_vars[] = {
      {"boxes", OWL_BUFPTR, OWL_OFFSETOF(RelationGeomData, boxes)},
      {/* sentinel */}};
  OWLGeomType geom_type =
      owlGeomTypeCreate(context, OWL_GEOMETRY_USER, sizeof(RelationGeomData),
                        geom_vars, -1);
  owlGeomTypeSetIntersectProg(geom_type, 0, module, intersect_program);
  owlGeomTypeSetBoundsProg(geom_type, module, "RelationBounds");
  owlGeomTypeSetAnyHit(geom_type, 0, module, "RelationAnyHit");
  owlBuildPrograms(context);

  OWLBuffer indexed_buffer = owlDeviceBufferCreate(
      context, OWL_USER_TYPE(Box), indexed.size(), indexed.data());
  OWLGeom geom = owlGeomCreate(context, geom_type);
  owlGeomSetPrimCount(geom, indexed.size());
  owlGeomSetBuffer(geom, "boxes", indexed_buffer);
  OWLGroup gas = owlUserGeomGroupCreate(context, 1, &geom);
  owlGroupBuildAccel(gas);
  OWLGroup world = owlInstanceGroupCreate(context, 1, &gas);
  owlGroupBuildAccel(world);

  OWLVarDecl miss_vars[] = {{/* sentinel */}};
  owlMissProgCreate(context, module, "EmptyMiss", 0, miss_vars, -1);

  OWLVarDecl raygen_vars[] = {
      {"world", OWL_GROUP, OWL_OFFSETOF(RelationRayGenData, world)},
      {"queries", OWL_BUFPTR, OWL_OFFSETOF(RelationRayGenData, queries)},
      {"rows", OWL_BUFPTR, OWL_OFFSETOF(RelationRayGenData, rows)},
      {"row_count", OWL_BUFPTR,
       OWL_OFFSETOF(RelationRayGenData, row_count)},
      {"overflow", OWL_BUFPTR,
       OWL_OFFSETOF(RelationRayGenData, overflow)},
      {"status", OWL_BUFPTR, OWL_OFFSETOF(RelationRayGenData, status)},
      {"query_count", OWL_UINT,
       OWL_OFFSETOF(RelationRayGenData, query_count)},
      {"capacity", OWL_UINT, OWL_OFFSETOF(RelationRayGenData, capacity)},
      {"minimum_overlap", OWL_FLOAT,
       OWL_OFFSETOF(RelationRayGenData, minimum_overlap)},
      {/* sentinel */}};
  OWLRayGen raygen = owlRayGenCreate(context, module, raygen_program,
                                    sizeof(RelationRayGenData), raygen_vars,
                                    -1);

  OWLBuffer query_buffer = owlDeviceBufferCreate(
      context, OWL_USER_TYPE(Box), queries.size(), queries.data());
  const uint32_t storage_capacity = std::max(1u, capacity);
  OWLBuffer rows_buffer = owlHostPinnedBufferCreate(
      context, OWL_USER_TYPE(RelationRow), storage_capacity);
  OWLBuffer count_buffer = owlHostPinnedBufferCreate(context, OWL_UINT, 1);
  OWLBuffer overflow_buffer = owlHostPinnedBufferCreate(context, OWL_UINT, 1);
  OWLBuffer status_buffer = owlHostPinnedBufferCreate(context, OWL_UINT, 1);
  auto *host_rows = static_cast<RelationRow *>(const_cast<void *>(
      owlBufferGetPointer(rows_buffer, 0)));
  auto *host_count = static_cast<uint32_t *>(const_cast<void *>(
      owlBufferGetPointer(count_buffer, 0)));
  auto *host_overflow = static_cast<uint32_t *>(const_cast<void *>(
      owlBufferGetPointer(overflow_buffer, 0)));
  auto *host_status = static_cast<uint32_t *>(const_cast<void *>(
      owlBufferGetPointer(status_buffer, 0)));
  std::fill(host_rows, host_rows + storage_capacity, RelationRow{0, 0});
  *host_count = 0;
  *host_overflow = 0;
  *host_status = 0;

  owlRayGenSetGroup(raygen, "world", world);
  owlRayGenSetBuffer(raygen, "queries", query_buffer);
  owlRayGenSetBuffer(raygen, "rows", rows_buffer);
  owlRayGenSetBuffer(raygen, "row_count", count_buffer);
  owlRayGenSetBuffer(raygen, "overflow", overflow_buffer);
  owlRayGenSetBuffer(raygen, "status", status_buffer);
  owlRayGenSet1ui(raygen, "query_count", queries.size());
  owlRayGenSet1ui(raygen, "capacity", capacity);
  owlRayGenSet1f(raygen, "minimum_overlap", 0.f);

  owlBuildPrograms(context);
  owlBuildPipeline(context);
  owlBuildSBT(context);
  owlRayGenLaunch2D(raygen, queries.size(), 1);

  RelationObservation observation;
  observation.raw_count = *host_count;
  observation.overflow = *host_overflow;
  observation.status = *host_status;
  const uint32_t returned = std::min(observation.raw_count, capacity);
  for (uint32_t i = 0; i < returned; ++i) {
    observation.rows.emplace_back(host_rows[i].source_id, host_rows[i].item_id);
  }
  std::sort(observation.rows.begin(), observation.rows.end());
  observation.rows.erase(
      std::unique(observation.rows.begin(), observation.rows.end()),
      observation.rows.end());
  owlContextDestroy(context);
  return observation;
}

TriangleObservation run_triangle(const char *anyhit_program) {
  const std::vector<owl3f> vertices = {
      {-1.f, -1.f, 1.f}, {1.f, -1.f, 1.f}, {0.f, 1.f, 1.f},
      {-1.f, -1.f, 2.f}, {1.f, -1.f, 2.f}, {0.f, 1.f, 2.f},
      {-1.f, -1.f, 3.f}, {1.f, -1.f, 3.f}, {0.f, 1.f, 3.f},
      {2.f, -1.f, 1.f},  {4.f, -1.f, 1.f}, {3.f, 1.f, 1.f},
      {2.f, -1.f, 1.f},  {4.f, -1.f, 1.f}, {3.f, 1.f, 1.f}};
  const std::vector<owl3i> indices = {
      {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {9, 10, 11}, {12, 13, 14}};
  const std::vector<Ray> rays = {
      {{0.f, 0.f, 0.f}, {0.f, 0.f, 1.f}},
      {{3.f, 0.f, 0.f}, {0.f, 0.f, 1.f}},
      {{6.f, 0.f, 0.f}, {0.f, 0.f, 1.f}},
      {{0.f, 0.f, 2.5f}, {0.f, 0.f, 1.f}}};
  const std::vector<uint64_t> weights = {1, 3, 5, 7};

  OWLContext context = owlContextCreate(nullptr, 1);
  owlContextSetNumPayloadValues(context, 2);
  OWLModule module = owlModuleCreate(context, deviceCode_ptx);
  OWLVarDecl geom_vars[] = {{/* sentinel */}};
  OWLGeomType geom_type = owlGeomTypeCreate(
      context, OWL_TRIANGLES, 0, geom_vars, -1);
  owlGeomTypeSetAnyHit(geom_type, 0, module, anyhit_program);

  OWLBuffer vertex_buffer = owlDeviceBufferCreate(
      context, OWL_FLOAT3, vertices.size(), vertices.data());
  OWLBuffer index_buffer = owlDeviceBufferCreate(
      context, OWL_INT3, indices.size(), indices.data());
  OWLGeom geom = owlGeomCreate(context, geom_type);
  owlTrianglesSetVertices(geom, vertex_buffer, vertices.size(), sizeof(owl3f),
                          0);
  owlTrianglesSetIndices(geom, index_buffer, indices.size(), sizeof(owl3i), 0);
  OWLGroup gas = owlTrianglesGeomGroupCreate(context, 1, &geom);
  owlGroupBuildAccel(gas);
  OWLGroup world = owlInstanceGroupCreate(context, 1, &gas);
  owlGroupBuildAccel(world);

  OWLVarDecl miss_vars[] = {{/* sentinel */}};
  owlMissProgCreate(context, module, "EmptyMiss", 0, miss_vars, -1);
  OWLVarDecl raygen_vars[] = {
      {"world", OWL_GROUP, OWL_OFFSETOF(TriangleRayGenData, world)},
      {"rays", OWL_BUFPTR, OWL_OFFSETOF(TriangleRayGenData, rays)},
      {"weights", OWL_BUFPTR, OWL_OFFSETOF(TriangleRayGenData, weights)},
      {"per_ray", OWL_BUFPTR, OWL_OFFSETOF(TriangleRayGenData, per_ray)},
      {"weighted_sum", OWL_BUFPTR,
       OWL_OFFSETOF(TriangleRayGenData, weighted_sum)},
      {"status", OWL_BUFPTR, OWL_OFFSETOF(TriangleRayGenData, status)},
      {"ray_count", OWL_UINT, OWL_OFFSETOF(TriangleRayGenData, ray_count)},
      {"tmin", OWL_FLOAT, OWL_OFFSETOF(TriangleRayGenData, tmin)},
      {"tmax", OWL_FLOAT, OWL_OFFSETOF(TriangleRayGenData, tmax)},
      {/* sentinel */}};
  OWLRayGen raygen = owlRayGenCreate(context, module, "TriangleRayGen",
                                    sizeof(TriangleRayGenData), raygen_vars,
                                    -1);

  OWLBuffer ray_buffer = owlDeviceBufferCreate(
      context, OWL_USER_TYPE(Ray), rays.size(), rays.data());
  OWLBuffer weight_buffer = owlDeviceBufferCreate(
      context, OWL_ULONG, weights.size(), weights.data());
  OWLBuffer output_buffer =
      owlHostPinnedBufferCreate(context, OWL_ULONG, rays.size());
  OWLBuffer sum_buffer = owlHostPinnedBufferCreate(context, OWL_ULONG, 1);
  OWLBuffer status_buffer = owlHostPinnedBufferCreate(context, OWL_UINT, 1);
  auto *host_output = static_cast<uint64_t *>(const_cast<void *>(
      owlBufferGetPointer(output_buffer, 0)));
  auto *host_sum = static_cast<uint64_t *>(const_cast<void *>(
      owlBufferGetPointer(sum_buffer, 0)));
  auto *host_status = static_cast<uint32_t *>(const_cast<void *>(
      owlBufferGetPointer(status_buffer, 0)));
  std::fill(host_output, host_output + rays.size(), 0ull);
  *host_sum = 0;
  *host_status = 0;

  owlRayGenSetGroup(raygen, "world", world);
  owlRayGenSetBuffer(raygen, "rays", ray_buffer);
  owlRayGenSetBuffer(raygen, "weights", weight_buffer);
  owlRayGenSetBuffer(raygen, "per_ray", output_buffer);
  owlRayGenSetBuffer(raygen, "weighted_sum", sum_buffer);
  owlRayGenSetBuffer(raygen, "status", status_buffer);
  owlRayGenSet1ui(raygen, "ray_count", rays.size());
  owlRayGenSet1f(raygen, "tmin", 0.f);
  owlRayGenSet1f(raygen, "tmax", 10.f);

  owlBuildPrograms(context);
  owlBuildPipeline(context);
  owlBuildSBT(context);
  owlRayGenLaunch2D(raygen, rays.size(), 1);

  TriangleObservation observation;
  observation.per_ray.assign(host_output, host_output + rays.size());
  observation.weighted_sum = *host_sum;
  observation.status = *host_status;
  owlContextDestroy(context);
  return observation;
}

std::string rows_json(
    const std::vector<std::pair<uint32_t, uint32_t>> &rows) {
  std::ostringstream out;
  out << '[';
  for (size_t i = 0; i < rows.size(); ++i) {
    if (i) out << ',';
    out << '[' << rows[i].first << ',' << rows[i].second << ']';
  }
  out << ']';
  return out.str();
}

std::string u64_json(const std::vector<uint64_t> &values) {
  std::ostringstream out;
  out << '[';
  for (size_t i = 0; i < values.size(); ++i) {
    if (i) out << ',';
    out << values[i];
  }
  out << ']';
  return out.str();
}

void require(bool condition, const std::string &message) {
  if (!condition) throw std::runtime_error(message);
}

}  // namespace

int main(int argc, char **argv) {
  try {
    if (argc != 2) {
      throw std::runtime_error("usage: goal5800-owl-residual RESULT.json");
    }

    const auto valid_relation = run_relation(
        "RelationValid", "RelationRayGen", diagnostic_indexed(),
        diagnostic_queries(), 2);
    const auto wrong_abi = run_relation(
        "RelationWrongAbi", "RelationRayGen", diagnostic_indexed(),
        diagnostic_queries(), 2);
    const auto wrong_physical = run_relation(
        "RelationValid", "RelationSwappedRayGen", diagnostic_indexed(),
        diagnostic_queries(), 2);
    const auto overflow = run_relation(
        "RelationValid", "RelationRayGen", broad_indexed(), broad_queries(),
        7);
    const auto valid_triangle = run_triangle("TriangleCount");
    const auto wrong_effect = run_triangle("TriangleTerminate");
    const auto wrong_identity = run_triangle("TriangleDouble");

    const std::vector<std::pair<uint32_t, uint32_t>> expected_relation = {
        {100, 10}, {101, 20}};
    const std::vector<std::pair<uint32_t, uint32_t>> expected_abi = {
        {100, 0}, {101, 1}};
    const std::vector<std::pair<uint32_t, uint32_t>> expected_physical = {
        {100, 20}, {101, 10}};
    require(valid_relation.rows == expected_relation,
            "valid relation control is not exact");
    require(valid_relation.raw_count == 2 && valid_relation.overflow == 0 &&
                valid_relation.status == 0,
            "valid relation diagnostics are not clean");
    require(wrong_abi.rows == expected_abi && wrong_abi.overflow == 0 &&
                wrong_abi.status == 0,
            "payload/attribute wrong output did not reproduce exactly");
    require(wrong_physical.rows == expected_physical &&
                wrong_physical.overflow == 0 && wrong_physical.status == 0,
            "physical-binding wrong output did not reproduce exactly");
    require(overflow.raw_count == 8 && overflow.rows.size() == 7 &&
                overflow.overflow == 1 && overflow.status == 0,
            "partial-result status witness did not reproduce exactly");
    require(valid_triangle.per_ray == std::vector<uint64_t>({3, 2, 0, 1}) &&
                valid_triangle.weighted_sum == 16 &&
                valid_triangle.status == 0,
            "valid triangle control is not exact");
    require(wrong_effect.per_ray ==
                    std::vector<uint64_t>({1, 1, 0, 1}) &&
                wrong_effect.weighted_sum == 11 && wrong_effect.status == 0,
            "role/effect wrong output did not reproduce exactly");
    require(wrong_identity.per_ray ==
                    std::vector<uint64_t>({6, 4, 0, 2}) &&
                wrong_identity.weighted_sum == 32 &&
                wrong_identity.status == 0,
            "executable-identity wrong output did not reproduce exactly");

    const cudaError_t cuda_error = cudaGetLastError();
    require(cuda_error == cudaSuccess, std::string("CUDA diagnostic: ") +
                                            cudaGetErrorString(cuda_error));

    std::ostringstream json;
    json << "{\n"
         << "  \"schema\": \"rtdl.goal5800.owl_executable_residual.raw.v1\",\n"
         << "  \"status\": \"PASS\",\n"
         << "  \"arm\": \"PINNED_NVIDIA_OWL_WITH_DIAGNOSTIC_ONLY_VALIDATION_OVERLAY\",\n"
         << "  \"nearby_valid\": {\"relation\": "
         << rows_json(valid_relation.rows)
         << ", \"triangle_per_ray\": " << u64_json(valid_triangle.per_ray)
         << ", \"triangle_weighted_sum\": "
         << valid_triangle.weighted_sum << "},\n"
         << "  \"behavioral_controls\": {\n"
         << "    \"role_effect_closure\": {\"owl_accepted_and_executed\": true, \"output_per_ray\": "
         << u64_json(wrong_effect.per_ray)
         << ", \"output_weighted_sum\": " << wrong_effect.weighted_sum
         << ", \"silent_wrong\": true},\n"
         << "    \"payload_attribute_abi_ownership\": {\"owl_accepted_and_executed\": true, \"output\": "
         << rows_json(wrong_abi.rows) << ", \"silent_wrong\": true},\n"
         << "    \"physical_geometry_binding\": {\"owl_accepted_and_executed\": true, \"output\": "
         << rows_json(wrong_physical.rows) << ", \"silent_wrong\": true},\n"
         << "    \"device_status_continuation\": {\"owl_accepted_and_executed\": true, \"device_overflow\": "
         << overflow.overflow << ", \"raw_event_count\": "
         << overflow.raw_count << ", \"partial_result_consumed\": true, \"returned_row_count\": "
         << overflow.rows.size() << ", \"protocol_invariant_violated\": true},\n"
         << "    \"checked_program_executable_identity\": {\"owl_accepted_and_executed\": true, \"output_per_ray\": "
         << u64_json(wrong_identity.per_ray)
         << ", \"output_weighted_sum\": " << wrong_identity.weighted_sum
         << ", \"task_a_expected_weighted_sum\": 16, \"silent_wrong\": true}\n"
         << "  },\n"
         << "  \"runtime_diagnostics\": {\"cuda_last_error\": \"SUCCESS\", \"optix_validation_mode_requested_by_source_overlay\": \"ALL\"},\n"
         << "  \"registered_performance_timing_count\": 0,\n"
         << "  \"performance_claimed\": false\n"
         << "}\n";

    std::ofstream result(argv[1], std::ios::binary | std::ios::trunc);
    require(result.good(), "could not open result path");
    result << json.str();
    result.close();
    require(result.good(), "could not write result path");
    std::cout << "GOAL5800_OWL_UNTIMED_FUNCTIONAL_PASS" << std::endl;
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "GOAL5800_OWL_FAILURE: " << error.what() << std::endl;
    return 1;
  }
}
