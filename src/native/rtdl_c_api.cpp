#include "rtdl/rtdl.h"

#include <limits>
#include <cstring>
#include <new>
#include <vector>

struct rtdl_context {
  rtdl_context_desc desc;
  char last_error[256];
};

struct rtdl_index {
  rtdl_primitive_kind primitive_kind;
  uint64_t primitive_count;
  std::vector<float> aabb2;
};

struct rtdl_query {
  uint32_t reserved;
};

struct rtdl_buffer {
  rtdl_context* context;
  rtdl_buffer_view view;
};

namespace {

void clear_error(rtdl_context* context) {
  if (context != nullptr) {
    context->last_error[0] = '\0';
  }
}

void set_error(rtdl_context* context, const char* message) {
  if (context == nullptr) {
    return;
  }
  std::strncpy(context->last_error, message, sizeof(context->last_error) - 1);
  context->last_error[sizeof(context->last_error) - 1] = '\0';
}

bool host_f32_aabb2_view_is_valid(const rtdl_buffer_view& view, uint64_t count) {
  const uint64_t row_bytes = 4u * static_cast<uint64_t>(sizeof(float));
  if (count > std::numeric_limits<uint64_t>::max() / row_bytes) {
    return false;
  }
  return view.device_type == RTDL_DEVICE_HOST && view.dtype == RTDL_DTYPE_F32 &&
      view.ndim == 2u && view.shape[0] >= 0 && static_cast<uint64_t>(view.shape[0]) == count &&
      view.shape[1] == 4 && view.strides[0] == static_cast<int64_t>(row_bytes) &&
      view.strides[1] == static_cast<int64_t>(sizeof(float)) &&
      (view.data != nullptr || count == 0u) && view.byte_count >= count * row_bytes;
}

bool backend_is_supported_by_host_proof(rtdl_backend backend) {
  return backend == RTDL_BACKEND_AUTO || backend == RTDL_BACKEND_CPU;
}

bool abi_version_is_compatible(uint32_t major, uint32_t minor, uint32_t patch) {
  return major == RTDL_ABI_VERSION_MAJOR && minor == RTDL_ABI_VERSION_MINOR &&
      patch <= RTDL_ABI_VERSION_PATCH;
}

bool descriptor_abi_is_supported(uint32_t major, uint32_t minor) {
  return abi_version_is_compatible(major, minor, RTDL_ABI_VERSION_PATCH);
}

bool aabb2_overlaps(const float* lhs, const float* rhs) {
  return lhs[0] <= rhs[2] && lhs[2] >= rhs[0] && lhs[1] <= rhs[3] && lhs[3] >= rhs[1];
}

void release_owned_u64(void* data, void*) {
  delete[] static_cast<uint64_t*>(data);
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
  return abi_version_is_compatible(major, minor, patch) ? 1u : 0u;
}

RTDL_API const char* rtdl_status_string(rtdl_status status) {
  switch (status) {
    case RTDL_STATUS_OK:
      return "ok";
    case RTDL_STATUS_ERROR_INVALID_ARGUMENT:
      return "invalid argument";
    case RTDL_STATUS_ERROR_UNSUPPORTED:
      return "unsupported";
    case RTDL_STATUS_ERROR_OUT_OF_MEMORY:
      return "out of memory";
    case RTDL_STATUS_ERROR_BACKEND:
      return "backend error";
    case RTDL_STATUS_ERROR_INTERNAL:
      return "internal error";
  }
  return "unknown status";
}

RTDL_API const char* rtdl_context_last_error(const rtdl_context* context) {
  if (context == nullptr) {
    return "context is null";
  }
  return context->last_error;
}

RTDL_API rtdl_status rtdl_context_create(const rtdl_context_desc* desc, rtdl_context** context_out) {
  if (context_out == nullptr) {
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  *context_out = nullptr;
  if (desc != nullptr && !descriptor_abi_is_supported(desc->abi_version_major, desc->abi_version_minor)) {
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }
  if (desc != nullptr && !backend_is_supported_by_host_proof(desc->backend)) {
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }

  rtdl_context* context = new (std::nothrow) rtdl_context {};
  if (context == nullptr) {
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }
  if (desc != nullptr) {
    context->desc = *desc;
  } else {
    context->desc.abi_version_major = RTDL_ABI_VERSION_MAJOR;
    context->desc.abi_version_minor = RTDL_ABI_VERSION_MINOR;
    context->desc.backend = RTDL_BACKEND_AUTO;
  }
  clear_error(context);
  *context_out = context;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_context_destroy(rtdl_context* context) {
  delete context;
}

RTDL_API rtdl_status rtdl_context_set_external_runtime(
    rtdl_context* context,
    const rtdl_external_runtime* runtime) {
  if (context == nullptr || runtime == nullptr) {
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  set_error(context, "external runtime handles are not implemented by the C ABI proof");
  return RTDL_STATUS_ERROR_UNSUPPORTED;
}

RTDL_API rtdl_status rtdl_buffer_import(
    rtdl_context* context,
    const rtdl_buffer_view* view,
    rtdl_buffer** buffer_out) {
  if (context == nullptr || view == nullptr || buffer_out == nullptr) {
    set_error(context, "buffer import requires context, view, and output pointer");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  *buffer_out = nullptr;
  if (view->data == nullptr && view->byte_count != 0) {
    set_error(context, "non-empty buffer view requires data pointer");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  rtdl_buffer* buffer = new (std::nothrow) rtdl_buffer {};
  if (buffer == nullptr) {
    set_error(context, "could not allocate rtdl_buffer");
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }
  buffer->context = context;
  buffer->view = *view;
  clear_error(context);
  *buffer_out = buffer;
  return RTDL_STATUS_OK;
}

RTDL_API rtdl_status rtdl_buffer_export(
    const rtdl_buffer* buffer,
    rtdl_buffer_view* view_out) {
  if (buffer == nullptr || view_out == nullptr) {
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  *view_out = buffer->view;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_buffer_destroy(rtdl_buffer* buffer) {
  if (buffer == nullptr) {
    return;
  }
  if (buffer->view.release != nullptr) {
    buffer->view.release(buffer->view.data, buffer->view.user_data);
  }
  delete buffer;
}

RTDL_API rtdl_status rtdl_index_build(
    rtdl_context* context,
    const rtdl_index_desc* desc,
    rtdl_index** index_out) {
  if (context == nullptr || desc == nullptr || index_out == nullptr) {
    set_error(context, "index build requires context, descriptor, and output pointer");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  *index_out = nullptr;
  if (!descriptor_abi_is_supported(desc->abi_version_major, desc->abi_version_minor)) {
    set_error(context, "index descriptor ABI version is unsupported");
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }
  if (desc->primitive_kind != RTDL_PRIMITIVE_AABB2) {
    set_error(context, "only host F32 AABB2 index build is implemented by the C ABI proof");
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }
  if (desc->primitives == nullptr ||
      !host_f32_aabb2_view_is_valid(desc->primitives->view, desc->primitive_count)) {
    set_error(context, "AABB2 index build requires a host F32 buffer with four floats per primitive");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  rtdl_index* index = new (std::nothrow) rtdl_index {};
  if (index == nullptr) {
    set_error(context, "could not allocate rtdl_index");
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }
  const float* data = static_cast<const float*>(desc->primitives->view.data);
  try {
    index->primitive_kind = desc->primitive_kind;
    index->primitive_count = desc->primitive_count;
    if (desc->primitive_count != 0u) {
      index->aabb2.assign(data, data + desc->primitive_count * 4u);
    }
  } catch (...) {
    delete index;
    set_error(context, "could not copy AABB2 primitive buffer");
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }
  clear_error(context);
  *index_out = index;
  return RTDL_STATUS_OK;
}

RTDL_API rtdl_status rtdl_query_execute(
    rtdl_context* context,
    const rtdl_index* index,
    const rtdl_query_desc* desc,
    rtdl_buffer** result_out) {
  if (context == nullptr || index == nullptr || desc == nullptr || result_out == nullptr) {
    set_error(context, "query execute requires context, index, descriptor, and output pointer");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  *result_out = nullptr;
  if (!descriptor_abi_is_supported(desc->abi_version_major, desc->abi_version_minor)) {
    set_error(context, "query descriptor ABI version is unsupported");
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }
  if (index->primitive_kind != RTDL_PRIMITIVE_AABB2 || desc->query_kind != RTDL_QUERY_AABB_OVERLAP) {
    set_error(context, "only host F32 AABB2 overlap query is implemented by the C ABI proof");
    return RTDL_STATUS_ERROR_UNSUPPORTED;
  }
  if (desc->inputs == nullptr || !host_f32_aabb2_view_is_valid(desc->inputs->view, desc->input_count)) {
    set_error(context, "AABB2 overlap query requires a host F32 buffer with four floats per query");
    return RTDL_STATUS_ERROR_INVALID_ARGUMENT;
  }
  const float* queries = static_cast<const float*>(desc->inputs->view.data);
  std::vector<uint64_t> pairs;
  try {
    for (uint64_t query_id = 0; query_id < desc->input_count; ++query_id) {
      const float* query = queries + query_id * 4u;
      for (uint64_t primitive_id = 0; primitive_id < index->primitive_count; ++primitive_id) {
        const float* primitive = index->aabb2.data() + primitive_id * 4u;
        if (aabb2_overlaps(query, primitive)) {
          pairs.push_back(query_id);
          pairs.push_back(primitive_id);
        }
      }
    }
  } catch (...) {
    set_error(context, "could not collect AABB2 overlap pairs");
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }

  rtdl_buffer* result = new (std::nothrow) rtdl_buffer {};
  if (result == nullptr) {
    set_error(context, "could not allocate query result buffer");
    return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
  }
  uint64_t* rows = nullptr;
  if (!pairs.empty()) {
    rows = new (std::nothrow) uint64_t[pairs.size()];
    if (rows == nullptr) {
      delete result;
      set_error(context, "could not allocate query result rows");
      return RTDL_STATUS_ERROR_OUT_OF_MEMORY;
    }
    std::memcpy(rows, pairs.data(), pairs.size() * sizeof(uint64_t));
  }
  result->context = context;
  result->view.data = rows;
  result->view.byte_count = pairs.size() * sizeof(uint64_t);
  result->view.device_type = RTDL_DEVICE_HOST;
  result->view.device_id = 0;
  result->view.dtype = RTDL_DTYPE_U64;
  result->view.ndim = 2;
  result->view.shape[0] = static_cast<int64_t>(pairs.size() / 2u);
  result->view.shape[1] = 2;
  result->view.strides[0] = static_cast<int64_t>(2u * sizeof(uint64_t));
  result->view.strides[1] = static_cast<int64_t>(sizeof(uint64_t));
  result->view.release = rows == nullptr ? nullptr : release_owned_u64;
  result->view.user_data = nullptr;
  clear_error(context);
  *result_out = result;
  return RTDL_STATUS_OK;
}

RTDL_API void rtdl_index_destroy(rtdl_index* index) {
  delete index;
}

RTDL_API void rtdl_query_destroy(rtdl_query* query) {
  delete query;
}

}  // extern "C"
