#ifndef RTDL_RTDL_H_
#define RTDL_RTDL_H_

/*
 * RTDL V3 draft C ABI.
 *
 * This header is a design-stage embedding boundary. It intentionally exposes
 * C-only opaque handles, status codes, external runtime handles, and neutral
 * buffer views. It has a minimal lifecycle stub implementation, but it is not
 * a frozen or backend-capable shared-library contract.
 *
 * Current ownership and threading rules are documented in
 * docs/learn/v3_0_c_abi_ownership_threading_contract.md.
 */

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#if defined(RTDL_BUILD_SHARED)
#define RTDL_API __declspec(dllexport)
#elif defined(RTDL_USE_SHARED)
#define RTDL_API __declspec(dllimport)
#else
#define RTDL_API
#endif
#else
#if defined(RTDL_BUILD_SHARED)
#define RTDL_API __attribute__((visibility("default")))
#else
#define RTDL_API
#endif
#endif

#define RTDL_ABI_VERSION_MAJOR 0
#define RTDL_ABI_VERSION_MINOR 1
#define RTDL_ABI_VERSION_PATCH 3

typedef struct rtdl_context rtdl_context;
typedef struct rtdl_index rtdl_index;
typedef struct rtdl_query rtdl_query;
typedef struct rtdl_buffer rtdl_buffer;

typedef enum rtdl_status {
  RTDL_STATUS_OK = 0,
  RTDL_STATUS_ERROR_INVALID_ARGUMENT = 1,
  RTDL_STATUS_ERROR_UNSUPPORTED = 2,
  RTDL_STATUS_ERROR_OUT_OF_MEMORY = 3,
  RTDL_STATUS_ERROR_BACKEND = 4,
  RTDL_STATUS_ERROR_INTERNAL = 5
} rtdl_status;

typedef enum rtdl_backend {
  RTDL_BACKEND_AUTO = 0,
  RTDL_BACKEND_CPU = 1,
  RTDL_BACKEND_EMBREE = 2,
  RTDL_BACKEND_OPTIX = 3,
  RTDL_BACKEND_HIPRT = 4,
  RTDL_BACKEND_VULKAN = 5,
  RTDL_BACKEND_APPLE_RT = 6
} rtdl_backend;

typedef enum rtdl_device_type {
  RTDL_DEVICE_HOST = 0,
  RTDL_DEVICE_CUDA = 1,
  RTDL_DEVICE_HIP = 2,
  RTDL_DEVICE_METAL = 3,
  RTDL_DEVICE_VULKAN = 4
} rtdl_device_type;

typedef enum rtdl_dtype {
  RTDL_DTYPE_U8 = 1,
  RTDL_DTYPE_U32 = 2,
  RTDL_DTYPE_U64 = 3,
  RTDL_DTYPE_I32 = 4,
  RTDL_DTYPE_I64 = 5,
  RTDL_DTYPE_F32 = 6,
  RTDL_DTYPE_F64 = 7
} rtdl_dtype;

typedef enum rtdl_primitive_kind {
  RTDL_PRIMITIVE_AABB2 = 1,
  RTDL_PRIMITIVE_SEGMENT2 = 2,
  RTDL_PRIMITIVE_TRIANGLE3 = 3
} rtdl_primitive_kind;

typedef enum rtdl_query_kind {
  RTDL_QUERY_AABB_OVERLAP = 1,
  RTDL_QUERY_RAY_HIT = 2,
  RTDL_QUERY_NEAREST = 3
} rtdl_query_kind;

typedef struct rtdl_external_runtime {
  rtdl_device_type device_type;
  int32_t device_id;
  void* context;
  void* stream;
  void* user_data;
} rtdl_external_runtime;

typedef void (*rtdl_buffer_release_fn)(void* data, void* user_data);

/*
 * If release is NULL, RTDL does not release data when the buffer handle is
 * destroyed. If release is non-NULL, rtdl_buffer_destroy calls it exactly once
 * for that buffer handle. Release callbacks must not throw across the C ABI.
 */
typedef struct rtdl_buffer_view {
  void* data;
  uint64_t byte_count;
  rtdl_device_type device_type;
  int32_t device_id;
  rtdl_dtype dtype;
  uint32_t ndim;
  int64_t shape[8];
  int64_t strides[8];
  rtdl_buffer_release_fn release;
  void* user_data;
} rtdl_buffer_view;

typedef struct rtdl_context_desc {
  uint32_t abi_version_major;
  uint32_t abi_version_minor;
  rtdl_backend backend;
  rtdl_external_runtime external_runtime;
} rtdl_context_desc;

typedef struct rtdl_index_desc {
  uint32_t abi_version_major;
  uint32_t abi_version_minor;
  rtdl_primitive_kind primitive_kind;
  rtdl_buffer* primitives;
  uint64_t primitive_count;
} rtdl_index_desc;

typedef struct rtdl_query_desc {
  uint32_t abi_version_major;
  uint32_t abi_version_minor;
  rtdl_query_kind query_kind;
  rtdl_buffer* inputs;
  uint64_t input_count;
} rtdl_query_desc;

RTDL_API uint32_t rtdl_abi_version_major(void);
RTDL_API uint32_t rtdl_abi_version_minor(void);
RTDL_API uint32_t rtdl_abi_version_patch(void);
RTDL_API uint32_t rtdl_abi_is_compatible(
    uint32_t major,
    uint32_t minor,
    uint32_t patch);
RTDL_API uint32_t rtdl_backend_is_supported(rtdl_backend backend);
RTDL_API uint32_t rtdl_route_is_supported(
    rtdl_primitive_kind primitive_kind,
    rtdl_query_kind query_kind,
    rtdl_device_type device_type);

RTDL_API const char* rtdl_status_string(rtdl_status status);
RTDL_API const char* rtdl_context_last_error(const rtdl_context* context);

RTDL_API rtdl_status rtdl_context_create(const rtdl_context_desc* desc, rtdl_context** context_out);
RTDL_API void rtdl_context_destroy(rtdl_context* context);

/* Declared for the future embedding boundary; currently returns unsupported. */
RTDL_API rtdl_status rtdl_context_set_external_runtime(
    rtdl_context* context,
    const rtdl_external_runtime* runtime);

RTDL_API rtdl_status rtdl_buffer_import(
    rtdl_context* context,
    const rtdl_buffer_view* view,
    rtdl_buffer** buffer_out);

RTDL_API rtdl_status rtdl_buffer_export(
    const rtdl_buffer* buffer,
    rtdl_buffer_view* view_out);

RTDL_API rtdl_status rtdl_index_build(
    rtdl_context* context,
    const rtdl_index_desc* desc,
    rtdl_index** index_out);

RTDL_API rtdl_status rtdl_query_execute(
    rtdl_context* context,
    const rtdl_index* index,
    const rtdl_query_desc* desc,
    rtdl_buffer** result_out);

RTDL_API void rtdl_buffer_destroy(rtdl_buffer* buffer);
RTDL_API void rtdl_index_destroy(rtdl_index* index);
RTDL_API void rtdl_query_destroy(rtdl_query* query);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // RTDL_RTDL_H_
