#include "rtdl/rtdl.h"

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <limits>
#include <new>
#include <vector>

#define RTDL_FIELD_AVAILABLE(size, type, field) \
  ((size) >= (offsetof(type, field) + sizeof(((type*)0)->field)))

struct rtdl_context {
  rtdl_backend backend;
  rtdl_external_runtime_desc runtime;
  char last_error[256];
};

struct rtdl_buffer {
  rtdl_context* context;
  rtdl_buffer_desc desc;
};

struct rtdl_index {
  rtdl_primitive_kind primitive_kind;
  uint64_t primitive_count;
  std::vector<float> aabb2;
};

struct rtdl_query_plan {
  rtdl_route_desc route;
  const rtdl_index* index;
};

struct rtdl_result {
  std::vector<uint64_t> rows;
};

struct rtdl_event {
  uint32_t reserved;
};

namespace {

thread_local char g_last_create_error[256] = "";

void write_error(char* destination, const char* message) {
  if (destination == nullptr) {
    return;
  }
  std::strncpy(destination, message, 255);
  destination[255] = '\0';
}

void set_context_error(rtdl_context* context, const char* message) {
  if (context != nullptr) {
    write_error(context->last_error, message);
  }
}

void clear_context_error(rtdl_context* context) {
  if (context != nullptr) {
    context->last_error[0] = '\0';
  }
}

void set_create_error(const char* message) {
  write_error(g_last_create_error, message);
}

void clear_create_error() {
  g_last_create_error[0] = '\0';
}

bool abi_is_compatible(uint32_t major, uint32_t minor, uint32_t patch) {
  if (major != RTDL_ABI_VERSION_MAJOR) {
    return false;
  }
  if (minor > RTDL_ABI_VERSION_MINOR) {
    return false;
  }
  if (minor == RTDL_ABI_VERSION_MINOR && patch > RTDL_ABI_VERSION_PATCH) {
    return false;
  }
  return true;
}

bool backend_is_known(rtdl_backend backend) {
  switch (backend) {
    case RTDL_BACKEND_AUTO:
    case RTDL_BACKEND_CPU:
    case RTDL_BACKEND_EMBREE:
    case RTDL_BACKEND_OPTIX:
    case RTDL_BACKEND_HIPRT:
    case RTDL_BACKEND_VULKAN:
    case RTDL_BACKEND_APPLE_RT:
      return true;
  }
  return false;
}

bool backend_is_available(rtdl_backend backend) {
  return backend == RTDL_BACKEND_AUTO || backend == RTDL_BACKEND_CPU;
}

bool device_type_is_known(rtdl_device_type device_type) {
  switch (device_type) {
    case RTDL_DEVICE_HOST:
    case RTDL_DEVICE_CUDA:
    case RTDL_DEVICE_HIP:
    case RTDL_DEVICE_METAL:
    case RTDL_DEVICE_VULKAN:
      return true;
  }
  return false;
}

bool dtype_is_known(rtdl_dtype dtype) {
  switch (dtype) {
    case RTDL_DTYPE_U8:
    case RTDL_DTYPE_U32:
    case RTDL_DTYPE_U64:
    case RTDL_DTYPE_I32:
    case RTDL_DTYPE_I64:
    case RTDL_DTYPE_F32:
    case RTDL_DTYPE_F64:
      return true;
  }
  return false;
}

bool ownership_is_known(rtdl_ownership_mode ownership) {
  switch (ownership) {
    case RTDL_OWNERSHIP_BORROWED:
    case RTDL_OWNERSHIP_RELEASE_CALLBACK:
    case RTDL_OWNERSHIP_RTDL_OWNED:
    case RTDL_OWNERSHIP_EXTERNAL_OBJECT:
    case RTDL_OWNERSHIP_EXPORTED_RTDL_VIEW:
      return true;
  }
  return false;
}

bool route_is_available(const rtdl_route_desc& route) {
  const rtdl_backend backend = route.backend == RTDL_BACKEND_AUTO ? RTDL_BACKEND_CPU : route.backend;
  return route.primitive_kind == RTDL_PRIMITIVE_AABB2 &&
      route.query_kind == RTDL_QUERY_AABB_OVERLAP &&
      route.device_type == RTDL_DEVICE_HOST &&
      route.dtype == RTDL_DTYPE_F32 &&
      backend == RTDL_BACKEND_CPU;
}

bool external_runtime_is_supported(const rtdl_external_runtime_desc& runtime) {
  return runtime.device_type == RTDL_DEVICE_HOST &&
      (runtime.device_id == 0 || runtime.device_id == -1) &&
      runtime.context == nullptr &&
      runtime.stream == nullptr &&
      (runtime.stream_mode == RTDL_STREAM_SYNCHRONOUS_HOST || runtime.stream_mode == 0);
}

bool checked_multiply_u64(uint64_t a, uint64_t b, uint64_t* out) {
  if (out == nullptr) {
    return false;
  }
  if (a != 0 && b > std::numeric_limits<uint64_t>::max() / a) {
    return false;
  }
  *out = a * b;
  return true;
}

uint64_t dtype_size(rtdl_dtype dtype) {
  switch (dtype) {
    case RTDL_DTYPE_U8:
      return 1;
    case RTDL_DTYPE_U32:
    case RTDL_DTYPE_I32:
    case RTDL_DTYPE_F32:
      return 4;
    case RTDL_DTYPE_U64:
    case RTDL_DTYPE_I64:
    case RTDL_DTYPE_F64:
      return 8;
  }
  return 0;
}

rtdl_status validate_buffer_desc(const rtdl_buffer_desc* desc, const char** message) {
  if (desc == nullptr) {
    *message = "buffer descriptor is null";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->struct_size < offsetof(rtdl_buffer_desc, data) + sizeof(desc->data)) {
    *message = "buffer descriptor struct_size is too small";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (!RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_buffer_desc, strides)) {
    *message = "buffer descriptor must include shape and stride fields";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (!device_type_is_known(desc->device_type) || !dtype_is_known(desc->dtype)) {
    *message = "buffer descriptor has unknown device type or dtype";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->ndim > RTDL_MAX_RANK) {
    *message = "buffer descriptor ndim exceeds RTDL_MAX_RANK";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->data == nullptr && desc->byte_count != 0) {
    *message = "buffer descriptor has null data with nonzero byte_count";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  rtdl_ownership_mode ownership = RTDL_OWNERSHIP_BORROWED;
  if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_buffer_desc, ownership)) {
    ownership = desc->ownership;
    if (!ownership_is_known(ownership)) {
      *message = "buffer descriptor has unknown ownership mode";
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
  }
  if (ownership == RTDL_OWNERSHIP_RELEASE_CALLBACK &&
      (!RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_buffer_desc, release) || desc->release == nullptr)) {
    *message = "release-callback ownership requires a release callback";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  uint64_t dense_item_count = 1;
  for (uint32_t dim = 0; dim < desc->ndim; ++dim) {
    if (desc->shape[dim] < 0 || desc->strides[dim] < 0) {
      *message = "buffer descriptor has negative shape or stride";
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    uint64_t next = 0;
    if (!checked_multiply_u64(dense_item_count, static_cast<uint64_t>(desc->shape[dim]), &next)) {
      *message = "buffer descriptor shape product overflows";
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    dense_item_count = next;
  }
  uint64_t dense_bytes = 0;
  if (!checked_multiply_u64(dense_item_count, dtype_size(desc->dtype), &dense_bytes)) {
    *message = "buffer descriptor byte extent overflows";
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->ndim > 0 && dense_bytes > desc->byte_count) {
    *message = "buffer descriptor byte_count is smaller than dense shape extent";
    return RTDL_STATUS_SHAPE_LAYOUT_MISMATCH;
  }
  *message = "";
  return RTDL_STATUS_OK;
}

bool host_f32_aabb2_desc_is_valid(const rtdl_buffer_desc& desc, uint64_t count) {
  const uint64_t row_bytes = 4u * static_cast<uint64_t>(sizeof(float));
  uint64_t required_bytes = 0;
  if (!checked_multiply_u64(count, row_bytes, &required_bytes)) {
    return false;
  }
  return desc.device_type == RTDL_DEVICE_HOST &&
      desc.dtype == RTDL_DTYPE_F32 &&
      desc.ndim == 2u &&
      desc.shape[0] >= 0 &&
      static_cast<uint64_t>(desc.shape[0]) == count &&
      desc.shape[1] == 4 &&
      desc.strides[0] == static_cast<int64_t>(row_bytes) &&
      desc.strides[1] == static_cast<int64_t>(sizeof(float)) &&
      (desc.data != nullptr || count == 0u) &&
      desc.byte_count >= required_bytes;
}

bool host_u64_pair_output_desc_is_valid(const rtdl_buffer_desc& desc, uint64_t capacity_count) {
  const uint64_t row_bytes = 2u * static_cast<uint64_t>(sizeof(uint64_t));
  uint64_t required_bytes = 0;
  if (!checked_multiply_u64(capacity_count, row_bytes, &required_bytes)) {
    return false;
  }
  return desc.device_type == RTDL_DEVICE_HOST &&
      desc.dtype == RTDL_DTYPE_U64 &&
      desc.ndim == 2u &&
      desc.shape[0] >= 0 &&
      static_cast<uint64_t>(desc.shape[0]) >= capacity_count &&
      desc.shape[1] == 2 &&
      desc.strides[0] == static_cast<int64_t>(row_bytes) &&
      desc.strides[1] == static_cast<int64_t>(sizeof(uint64_t)) &&
      (desc.data != nullptr || capacity_count == 0u) &&
      desc.byte_count >= required_bytes;
}

bool aabb2_overlaps(const float* lhs, const float* rhs) {
  return lhs[0] <= rhs[2] && lhs[2] >= rhs[0] && lhs[1] <= rhs[3] && lhs[3] >= rhs[1];
}

void fill_buffer_result_desc(const uint64_t* rows, uint64_t row_count, rtdl_buffer_desc* out) {
  std::memset(out, 0, sizeof(*out));
  out->struct_size = sizeof(*out);
  out->data = const_cast<uint64_t*>(rows);
  out->byte_count = row_count * 2u * sizeof(uint64_t);
  out->device_type = RTDL_DEVICE_HOST;
  out->device_id = 0;
  out->dtype = RTDL_DTYPE_U64;
  out->ndim = 2;
  out->shape[0] = static_cast<int64_t>(row_count);
  out->shape[1] = 2;
  out->strides[0] = static_cast<int64_t>(2u * sizeof(uint64_t));
  out->strides[1] = static_cast<int64_t>(sizeof(uint64_t));
  out->ownership = RTDL_OWNERSHIP_EXPORTED_RTDL_VIEW;
}

}  // namespace

extern "C" {

RTDL_API uint32_t rtdl_abi_version_major(void) {
  return RTDL_ABI_VERSION_MAJOR;
}

RTDL_API uint32_t rtdl_abi_version_minor(void) {
  return RTDL_ABI_VERSION_MINOR;
}

RTDL_API uint32_t rtdl_abi_version_patch(void) {
  return RTDL_ABI_VERSION_PATCH;
}

RTDL_API uint32_t rtdl_abi_is_compatible(uint32_t major, uint32_t minor, uint32_t patch) {
  return abi_is_compatible(major, minor, patch) ? 1u : 0u;
}

RTDL_API const char* rtdl_status_string(rtdl_status status) {
  switch (status) {
    case RTDL_STATUS_OK:
      return "ok";
    case RTDL_STATUS_INVALID_ARGUMENT:
      return "invalid argument";
    case RTDL_STATUS_UNSUPPORTED:
      return "unsupported";
    case RTDL_STATUS_RESULT_TRUNCATED:
      return "result truncated";
    case RTDL_STATUS_ABI_VERSION_MISMATCH:
      return "ABI version mismatch";
    case RTDL_STATUS_OUT_OF_MEMORY:
      return "out of memory";
    case RTDL_STATUS_BACKEND_FAILURE:
      return "backend failure";
    case RTDL_STATUS_STREAM_RUNTIME_FAILURE:
      return "stream/runtime failure";
    case RTDL_STATUS_SHAPE_LAYOUT_MISMATCH:
      return "shape/layout mismatch";
    case RTDL_STATUS_OWNERSHIP_LIFETIME_VIOLATION:
      return "ownership/lifetime violation";
    case RTDL_STATUS_INTERNAL_ERROR:
      return "internal error";
  }
  return "unknown status";
}

RTDL_API const char* rtdl_last_create_error(void) {
  return g_last_create_error;
}

RTDL_API const char* rtdl_context_last_error(const rtdl_context* context) {
  if (context == nullptr) {
    return "context is null";
  }
  return context->last_error;
}

RTDL_API rtdl_status rtdl_context_create(const rtdl_context_desc* desc, rtdl_context** context_out) {
  if (context_out == nullptr) {
    set_create_error("context_out is null");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *context_out = nullptr;
  clear_create_error();

  uint32_t requested_major = RTDL_ABI_VERSION_MAJOR;
  uint32_t requested_minor = RTDL_ABI_VERSION_MINOR;
  uint32_t requested_patch = 0;
  rtdl_backend backend = RTDL_BACKEND_AUTO;
  rtdl_external_runtime_desc runtime {};
  runtime.struct_size = sizeof(runtime);
  runtime.device_type = RTDL_DEVICE_HOST;
  runtime.device_id = 0;
  runtime.stream_mode = RTDL_STREAM_SYNCHRONOUS_HOST;

  if (desc != nullptr) {
    if (desc->struct_size < sizeof(size_t)) {
      set_create_error("context descriptor struct_size is too small");
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_context_desc, requested_abi_major)) {
      requested_major = desc->requested_abi_major;
    }
    if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_context_desc, requested_abi_minor)) {
      requested_minor = desc->requested_abi_minor;
    }
    if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_context_desc, requested_abi_patch)) {
      requested_patch = desc->requested_abi_patch;
    }
    if (!abi_is_compatible(requested_major, requested_minor, requested_patch)) {
      set_create_error("requested ABI version is not compatible with this V4 library");
      return RTDL_STATUS_ABI_VERSION_MISMATCH;
    }
    if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_context_desc, backend)) {
      backend = desc->backend;
    }
    if (!backend_is_known(backend)) {
      set_create_error("unknown backend");
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    if (!backend_is_available(backend)) {
      set_create_error("requested backend is not available in the V4 control-plane proof");
      return RTDL_STATUS_UNSUPPORTED;
    }
    if (RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_context_desc, external_runtime) &&
        desc->external_runtime.struct_size != 0) {
      runtime = desc->external_runtime;
      if (!external_runtime_is_supported(runtime)) {
        set_create_error("only synchronous host external runtime metadata is supported in this slice");
        return runtime.device_type == RTDL_DEVICE_HOST ? RTDL_STATUS_INVALID_ARGUMENT : RTDL_STATUS_UNSUPPORTED;
      }
    }
  }

  rtdl_context* context = new (std::nothrow) rtdl_context {};
  if (context == nullptr) {
    set_create_error("could not allocate rtdl_context");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  context->backend = backend == RTDL_BACKEND_AUTO ? RTDL_BACKEND_CPU : backend;
  context->runtime = runtime;
  clear_context_error(context);
  *context_out = context;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_context_destroy(rtdl_context* context) {
  delete context;
}

RTDL_API rtdl_status rtdl_query_capability(
    const rtdl_context* context,
    const rtdl_route_desc* route,
    rtdl_capability cap,
    uint64_t* value_out) {
  if (value_out == nullptr) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *value_out = 0;
  if (context == nullptr) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (cap == RTDL_CAP_BACKEND_AVAILABLE) {
    rtdl_backend backend = context->backend;
    if (route != nullptr) {
      if (route->struct_size < sizeof(size_t)) {
        return RTDL_STATUS_INVALID_ARGUMENT;
      }
      if (RTDL_FIELD_AVAILABLE(route->struct_size, rtdl_route_desc, backend)) {
        backend = route->backend;
      }
    }
    *value_out = backend_is_available(backend) ? 1u : 0u;
    return RTDL_STATUS_OK;
  }
  if (route == nullptr || route->struct_size < sizeof(size_t)) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (!RTDL_FIELD_AVAILABLE(route->struct_size, rtdl_route_desc, dtype)) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  const bool supported = route_is_available(*route);
  switch (cap) {
    case RTDL_CAP_ROUTE_ACCEPTS_HOST_BUFFERS:
      *value_out = supported ? 1u : 0u;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_ACCEPTS_DEVICE_BUFFERS:
      *value_out = 0;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_SUPPORTS_BORROWED_DEVICE_POINTERS:
      *value_out = 0;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_SUPPORTS_EXTERNAL_STREAM:
      *value_out = 0;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_DETERMINISTIC_ROW_ORDER:
      *value_out = supported ? 1u : 0u;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_SUPPORTS_ASYNC:
      *value_out = 0;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_REQUIRES_RTDL_ALLOCATION:
      *value_out = 0;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_SUPPORTS_RTDL_OWNED_RESULT:
      *value_out = supported ? 1u : 0u;
      return RTDL_STATUS_OK;
    case RTDL_CAP_ROUTE_SUPPORTS_CALLER_OUTPUT:
      *value_out = supported ? 1u : 0u;
      return RTDL_STATUS_OK;
    case RTDL_CAP_BACKEND_AVAILABLE:
      return RTDL_STATUS_INTERNAL_ERROR;
  }
  return RTDL_STATUS_UNSUPPORTED;
}

RTDL_API rtdl_status rtdl_buffer_import(
    rtdl_context* context,
    const rtdl_buffer_desc* desc,
    rtdl_buffer** buffer_out) {
  if (context == nullptr || buffer_out == nullptr) {
    set_context_error(context, "buffer import requires context and output pointer");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *buffer_out = nullptr;
  const char* message = "";
  const rtdl_status validation = validate_buffer_desc(desc, &message);
  if (validation != RTDL_STATUS_OK) {
    set_context_error(context, message);
    return validation;
  }
  rtdl_buffer* buffer = new (std::nothrow) rtdl_buffer {};
  if (buffer == nullptr) {
    set_context_error(context, "could not allocate rtdl_buffer");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  buffer->context = context;
  buffer->desc = *desc;
  if (!RTDL_FIELD_AVAILABLE(buffer->desc.struct_size, rtdl_buffer_desc, ownership) ||
      buffer->desc.ownership == 0) {
    buffer->desc.ownership = RTDL_OWNERSHIP_BORROWED;
  }
  clear_context_error(context);
  *buffer_out = buffer;
  return RTDL_STATUS_OK;
}

RTDL_API rtdl_status rtdl_buffer_export(const rtdl_buffer* buffer, rtdl_buffer_desc* desc_out) {
  if (buffer == nullptr || desc_out == nullptr) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *desc_out = buffer->desc;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_buffer_destroy(rtdl_buffer* buffer) {
  if (buffer == nullptr) {
    return;
  }
  if (buffer->desc.ownership == RTDL_OWNERSHIP_RELEASE_CALLBACK && buffer->desc.release != nullptr) {
    buffer->desc.release(buffer->desc.data, buffer->desc.user_data);
  }
  delete buffer;
}

RTDL_API rtdl_status rtdl_index_build(
    rtdl_context* context,
    const rtdl_index_desc* desc,
    rtdl_index** index_out) {
  if (context == nullptr || desc == nullptr || index_out == nullptr) {
    set_context_error(context, "index build requires context, descriptor, and output pointer");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *index_out = nullptr;
  if (desc->struct_size < sizeof(size_t) ||
      !RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_index_desc, primitive_count)) {
    set_context_error(context, "index descriptor struct_size is too small");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->primitive_kind != RTDL_PRIMITIVE_AABB2 || desc->primitives == nullptr) {
    set_context_error(context, "this V4 slice only builds host F32 AABB2 indices");
    return RTDL_STATUS_UNSUPPORTED;
  }
  if (!host_f32_aabb2_desc_is_valid(desc->primitives->desc, desc->primitive_count)) {
    set_context_error(context, "AABB2 index requires host F32 [primitive_count, 4] input");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  rtdl_index* index = new (std::nothrow) rtdl_index {};
  if (index == nullptr) {
    set_context_error(context, "could not allocate rtdl_index");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  try {
    const float* primitives = static_cast<const float*>(desc->primitives->desc.data);
    index->primitive_kind = RTDL_PRIMITIVE_AABB2;
    index->primitive_count = desc->primitive_count;
    index->aabb2.assign(primitives, primitives + desc->primitive_count * 4u);
  } catch (...) {
    delete index;
    set_context_error(context, "could not copy AABB2 primitive buffer");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  clear_context_error(context);
  *index_out = index;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_index_destroy(rtdl_index* index) {
  delete index;
}

RTDL_API rtdl_status rtdl_query_plan_create(
    rtdl_context* context,
    const rtdl_route_desc* route,
    const rtdl_index* index,
    rtdl_query_plan** plan_out) {
  if (context == nullptr || route == nullptr || index == nullptr || plan_out == nullptr) {
    set_context_error(context, "query plan create requires context, route, index, and output pointer");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  *plan_out = nullptr;
  if (route->struct_size < sizeof(size_t) ||
      !RTDL_FIELD_AVAILABLE(route->struct_size, rtdl_route_desc, dtype)) {
    set_context_error(context, "route descriptor struct_size is too small");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (!route_is_available(*route) || index->primitive_kind != route->primitive_kind) {
    set_context_error(context, "requested route is unsupported by the V4 control-plane proof");
    return RTDL_STATUS_UNSUPPORTED;
  }
  rtdl_query_plan* plan = new (std::nothrow) rtdl_query_plan {};
  if (plan == nullptr) {
    set_context_error(context, "could not allocate rtdl_query_plan");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  plan->route = *route;
  plan->index = index;
  clear_context_error(context);
  *plan_out = plan;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_query_plan_destroy(rtdl_query_plan* plan) {
  delete plan;
}

RTDL_API rtdl_status rtdl_query_execute(
    rtdl_context* context,
    const rtdl_query_plan* plan,
    const rtdl_query_desc* desc,
    rtdl_result** result_out) {
  if (context == nullptr || plan == nullptr || desc == nullptr) {
    set_context_error(context, "query execute requires context, plan, and descriptor");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (result_out != nullptr) {
    *result_out = nullptr;
  }
  if (desc->struct_size < sizeof(size_t) ||
      !RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_query_desc, input_count)) {
    set_context_error(context, "query descriptor struct_size is too small");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (desc->query_kind != RTDL_QUERY_AABB_OVERLAP || desc->inputs == nullptr) {
    set_context_error(context, "this V4 slice only executes host F32 AABB2 overlap queries");
    return RTDL_STATUS_UNSUPPORTED;
  }
  if (!host_f32_aabb2_desc_is_valid(desc->inputs->desc, desc->input_count)) {
    set_context_error(context, "AABB2 query requires host F32 [input_count, 4] input");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }

  std::vector<uint64_t> rows;
  try {
    const float* queries = static_cast<const float*>(desc->inputs->desc.data);
    for (uint64_t query_id = 0; query_id < desc->input_count; ++query_id) {
      const float* query = queries + query_id * 4u;
      for (uint64_t primitive_id = 0; primitive_id < plan->index->primitive_count; ++primitive_id) {
        const float* primitive = plan->index->aabb2.data() + primitive_id * 4u;
        if (aabb2_overlaps(query, primitive)) {
          rows.push_back(query_id);
          rows.push_back(primitive_id);
        }
      }
    }
  } catch (...) {
    set_context_error(context, "could not collect AABB2 overlap rows");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }

  rtdl_output_mode mode = RTDL_OUTPUT_RTDL_OWNED_RESULT;
  const bool output_present = RTDL_FIELD_AVAILABLE(desc->struct_size, rtdl_query_desc, output) &&
      desc->output.struct_size >= sizeof(size_t);
  if (output_present && RTDL_FIELD_AVAILABLE(desc->output.struct_size, rtdl_output_desc, mode) &&
      desc->output.mode != 0) {
    mode = desc->output.mode;
  }

  const uint64_t required_count = rows.size() / 2u;
  if (output_present && RTDL_FIELD_AVAILABLE(desc->output.struct_size, rtdl_output_desc, required_count_out) &&
      desc->output.required_count_out != nullptr) {
    *desc->output.required_count_out = required_count;
  }

  if (mode == RTDL_OUTPUT_CALLER_PROVIDED_BUFFER) {
    if (!output_present ||
        !RTDL_FIELD_AVAILABLE(desc->output.struct_size, rtdl_output_desc, written_count_out) ||
        !RTDL_FIELD_AVAILABLE(desc->output.struct_size, rtdl_output_desc, caller_buffer)) {
      set_context_error(context, "caller-provided output requires full output descriptor");
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    uint64_t capacity_count = desc->output.capacity_count;
    if (capacity_count == 0 && desc->output.caller_buffer.shape[0] > 0) {
      capacity_count = static_cast<uint64_t>(desc->output.caller_buffer.shape[0]);
    }
    const char* message = "";
    const rtdl_status validation = validate_buffer_desc(&desc->output.caller_buffer, &message);
    if (validation != RTDL_STATUS_OK) {
      set_context_error(context, message);
      return validation;
    }
    if (!host_u64_pair_output_desc_is_valid(desc->output.caller_buffer, capacity_count)) {
      set_context_error(context, "caller output requires host U64 [capacity, 2] buffer");
      return RTDL_STATUS_INVALID_ARGUMENT;
    }
    const uint64_t written_count = required_count < capacity_count ? required_count : capacity_count;
    if (written_count != 0) {
      std::memcpy(desc->output.caller_buffer.data, rows.data(), written_count * 2u * sizeof(uint64_t));
    }
    if (desc->output.written_count_out != nullptr) {
      *desc->output.written_count_out = written_count;
    }
    clear_context_error(context);
    return written_count < required_count ? RTDL_STATUS_RESULT_TRUNCATED : RTDL_STATUS_OK;
  }

  if (mode != RTDL_OUTPUT_RTDL_OWNED_RESULT) {
    set_context_error(context, "unknown query output mode");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  if (result_out == nullptr) {
    set_context_error(context, "RTDL-owned result mode requires result_out");
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  rtdl_result* result = new (std::nothrow) rtdl_result {};
  if (result == nullptr) {
    set_context_error(context, "could not allocate rtdl_result");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  try {
    result->rows.swap(rows);
  } catch (...) {
    delete result;
    set_context_error(context, "could not store query result rows");
    return RTDL_STATUS_OUT_OF_MEMORY;
  }
  clear_context_error(context);
  *result_out = result;
  return RTDL_STATUS_OK;
}

RTDL_API uint64_t rtdl_result_row_count(const rtdl_result* result) {
  return result == nullptr ? 0u : static_cast<uint64_t>(result->rows.size() / 2u);
}

RTDL_API rtdl_status rtdl_result_get_buffer(const rtdl_result* result, rtdl_buffer_desc* desc_out) {
  if (result == nullptr || desc_out == nullptr) {
    return RTDL_STATUS_INVALID_ARGUMENT;
  }
  fill_buffer_result_desc(result->rows.empty() ? nullptr : result->rows.data(), rtdl_result_row_count(result), desc_out);
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_result_destroy(rtdl_result* result) {
  delete result;
}

}  // extern "C"
