#include "Goal5800Types.h"

#include <optix_device.h>

using namespace goal5800;
using owl::box3f;
using owl::vec3f;

OPTIX_BOUNDS_PROGRAM(RelationBounds)(const void *geom_data,
                                     box3f &bounds,
                                     const int primitive_index) {
  const RelationGeomData &self = *(const RelationGeomData *)geom_data;
  const Box value = self.boxes[primitive_index];
  bounds = box3f((const vec3f &)value.lower, (const vec3f &)value.upper);
}

static __forceinline__ __device__ void relation_intersection(bool wrong_abi) {
  const int primitive_index = optixGetPrimitiveIndex();
  const RelationGeomData &self = owl::getProgramData<RelationGeomData>();
  RelationPRD &prd = owl::getPRD<RelationPRD>();
  const Box item = self.boxes[primitive_index];
  const Box query = prd.query;
  const bool closed =
      item.lower.x <= query.upper.x && item.upper.x >= query.lower.x &&
      item.lower.y <= query.upper.y && item.upper.y >= query.lower.y;
  const float dx = fmaxf(0.0f, fminf(query.upper.x, item.upper.x) -
                                   fmaxf(query.lower.x, item.lower.x));
  const float dy = fmaxf(0.0f, fminf(query.upper.y, item.upper.y) -
                                   fmaxf(query.lower.y, item.lower.y));
  if (closed && dx * dy >= prd.minimum_overlap) {
    const uint32_t attribute =
        wrong_abi ? (uint32_t)primitive_index : item.item_id;
    optixReportIntersection(0.0f, 0u, attribute);
  }
}

OPTIX_INTERSECT_PROGRAM(RelationValid)() { relation_intersection(false); }
OPTIX_INTERSECT_PROGRAM(RelationWrongAbi)() { relation_intersection(true); }

OPTIX_ANY_HIT_PROGRAM(RelationAnyHit)() {
  RelationPRD &prd = owl::getPRD<RelationPRD>();
  const uint32_t slot = atomicAdd(prd.row_count, 1u);
  if (slot < prd.capacity) {
    prd.rows[slot] = RelationRow{
        prd.query.item_id, optixGetAttribute_0()};
  } else {
    atomicExch(prd.overflow, 1u);
  }
  optixIgnoreIntersection();
}

static __forceinline__ __device__ void relation_raygen(bool swap_xy) {
  const RelationRayGenData &self =
      owl::getProgramData<RelationRayGenData>();
  const uint32_t query_index = owl::getLaunchIndex().x;
  if (query_index >= self.query_count) return;
  Box query = self.queries[query_index];
  if (swap_xy) {
    const float lower_x = query.lower.x;
    const float upper_x = query.upper.x;
    query.lower.x = query.lower.y;
    query.lower.y = lower_x;
    query.upper.x = query.upper.y;
    query.upper.y = upper_x;
  }
  RelationPRD prd{query, self.rows, self.row_count, self.overflow,
                  self.status, self.capacity, self.minimum_overlap};
  owl::Ray ray;
  ray.origin = vec3f(query.upper.x, query.lower.y, 0.0f);
  ray.direction = vec3f(query.lower.x - query.upper.x,
                        query.upper.y - query.lower.y, 0.0f);
  ray.tmin = 0.0f;
  ray.tmax = 1.0f;
  owl::traceRay(self.world, ray, prd, OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT);
}

OPTIX_RAYGEN_PROGRAM(RelationRayGen)() { relation_raygen(false); }
OPTIX_RAYGEN_PROGRAM(RelationSwappedRayGen)() { relation_raygen(true); }

static __forceinline__ __device__ void triangle_raygen() {
  const TriangleRayGenData &self =
      owl::getProgramData<TriangleRayGenData>();
  const uint32_t index = owl::getLaunchIndex().x;
  if (index >= self.ray_count) return;
  const Ray input = self.rays[index];
  uint64_t count = 0;
  owl::Ray ray((const vec3f &)input.origin, (const vec3f &)input.direction,
               self.tmin, self.tmax);
  owl::traceRay(self.world, ray, count, OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT);
  self.per_ray[index] = count;
  const uint64_t weight = self.weights[index];
  if (weight != 0ull && count > (~0ull) / weight) {
    atomicExch(self.status, 2u);
    return;
  }
  const uint64_t term = count * weight;
  const uint64_t prior = atomicAdd(
      reinterpret_cast<unsigned long long *>(self.weighted_sum),
      static_cast<unsigned long long>(term));
  if (prior > (~0ull) - term) atomicExch(self.status, 3u);
}

OPTIX_RAYGEN_PROGRAM(TriangleRayGen)() { triangle_raygen(); }

OPTIX_ANY_HIT_PROGRAM(TriangleCount)() {
  uint64_t &count = owl::getPRD<uint64_t>();
  count += 1ull;
  optixIgnoreIntersection();
}

OPTIX_ANY_HIT_PROGRAM(TriangleTerminate)() {
  uint64_t &count = owl::getPRD<uint64_t>();
  count += 1ull;
  optixTerminateRay();
}

OPTIX_ANY_HIT_PROGRAM(TriangleDouble)() {
  uint64_t &count = owl::getPRD<uint64_t>();
  count += 2ull;
  optixIgnoreIntersection();
}

OPTIX_MISS_PROGRAM(EmptyMiss)() {}
