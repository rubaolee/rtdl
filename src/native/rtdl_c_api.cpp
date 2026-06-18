#include "rtdl/rtdl.h"

#include <cstring>
#include <new>

struct rtdl_context {
  rtdl_context_desc desc;
  char last_error[256];
};

struct rtdl_index {
  uint32_t reserved;
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
  if (desc != nullptr && desc->abi_version_major != RTDL_ABI_VERSION_MAJOR) {
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
  context->desc.external_runtime = *runtime;
  clear_error(context);
  return RTDL_STATUS_OK;
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

RTDL_API void rtdl_index_destroy(rtdl_index* index) {
  delete index;
}

RTDL_API void rtdl_query_destroy(rtdl_query* query) {
  delete query;
}

}  // extern "C"
