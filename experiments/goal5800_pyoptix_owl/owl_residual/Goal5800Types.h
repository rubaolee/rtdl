#pragma once

#include <owl/owl.h>

namespace goal5800 {

struct Box {
  owl3f lower;
  owl3f upper;
  uint32_t item_id;
};

struct RelationRow {
  uint32_t source_id;
  uint32_t item_id;
};

struct RelationGeomData {
  Box *boxes;
};

struct RelationPRD {
  Box query;
  RelationRow *rows;
  uint32_t *row_count;
  uint32_t *overflow;
  uint32_t *status;
  uint32_t capacity;
  float minimum_overlap;
};

struct RelationRayGenData {
  OptixTraversableHandle world;
  Box *queries;
  RelationRow *rows;
  uint32_t *row_count;
  uint32_t *overflow;
  uint32_t *status;
  uint32_t query_count;
  uint32_t capacity;
  float minimum_overlap;
};

struct Ray {
  owl3f origin;
  owl3f direction;
};

struct TriangleRayGenData {
  OptixTraversableHandle world;
  Ray *rays;
  uint64_t *weights;
  uint64_t *per_ray;
  uint64_t *weighted_sum;
  uint32_t *status;
  uint32_t ray_count;
  float tmin;
  float tmax;
};

struct EmptyMissData {};

}  // namespace goal5800
