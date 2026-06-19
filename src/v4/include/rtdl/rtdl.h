#ifndef RTDL_V4_RTDL_H_
#define RTDL_V4_RTDL_H_

/*
 * RTDL V4 experimental C ABI.
 *
 * This is the active V4 development boundary. It is intentionally pre-1.0:
 * use it to validate embedding, descriptor evolution, capability discovery,
 * result allocation, and fail-closed validation before any stable SDK claim.
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
#define RTDL_ABI_VERSION_MINOR 2
#define RTDL_ABI_VERSION_PATCH 0
#define RTDL_MAX_RANK 8

typedef struct rtdl_context rtdl_context;
typedef struct rtdl_buffer rtdl_buffer;
typedef struct rtdl_index rtdl_index;
typedef struct rtdl_query_plan rtdl_query_plan;
typedef struct rtdl_result rtdl_result;
typedef struct rtdl_event rtdl_event;

typedef enum rtdl_status {
  RTDL_STATUS_OK = 0,
  RTDL_STATUS_INVALID_ARGUMENT = 1,
  RTDL_STATUS_UNSUPPORTED = 2,
  RTDL_STATUS_RESULT_TRUNCATED = 3,
  RTDL_STATUS_ABI_VERSION_MISMATCH = 4,
  RTDL_STATUS_OUT_OF_MEMORY = 5,
  RTDL_STATUS_BACKEND_FAILURE = 6,
  RTDL_STATUS_STREAM_RUNTIME_FAILURE = 7,
  RTDL_STATUS_SHAPE_LAYOUT_MISMATCH = 8,
  RTDL_STATUS_OWNERSHIP_LIFETIME_VIOLATION = 9,
  RTDL_STATUS_INTERNAL_ERROR = 10
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

typedef enum rtdl_ownership_mode {
  RTDL_OWNERSHIP_BORROWED = 1,
  RTDL_OWNERSHIP_RELEASE_CALLBACK = 2,
  RTDL_OWNERSHIP_RTDL_OWNED = 3,
  RTDL_OWNERSHIP_EXTERNAL_OBJECT = 4,
  RTDL_OWNERSHIP_EXPORTED_RTDL_VIEW = 5
} rtdl_ownership_mode;

typedef enum rtdl_stream_mode {
  RTDL_STREAM_SYNCHRONOUS_HOST = 1,
  RTDL_STREAM_CALLER_STREAM_ASYNC = 2,
  RTDL_STREAM_RTDL_STREAM_ASYNC = 3
} rtdl_stream_mode;

typedef enum rtdl_primitive_kind {
  RTDL_PRIMITIVE_AABB2 = 1,
  RTDL_PRIMITIVE_SEGMENT2 = 2,
  RTDL_PRIMITIVE_TRIANGLE3 = 3,
  RTDL_PRIMITIVE_POINT3 = 4
} rtdl_primitive_kind;

typedef enum rtdl_query_kind {
  RTDL_QUERY_AABB_OVERLAP = 1,
  RTDL_QUERY_RAY_HIT = 2,
  RTDL_QUERY_FIXED_RADIUS_NEIGHBORS = 3,
  RTDL_QUERY_NEAREST = 4
} rtdl_query_kind;

typedef enum rtdl_output_mode {
  RTDL_OUTPUT_RTDL_OWNED_RESULT = 1,
  RTDL_OUTPUT_CALLER_PROVIDED_BUFFER = 2
} rtdl_output_mode;

typedef enum rtdl_capability {
  RTDL_CAP_BACKEND_AVAILABLE = 1,
  RTDL_CAP_ROUTE_ACCEPTS_HOST_BUFFERS = 2,
  RTDL_CAP_ROUTE_ACCEPTS_DEVICE_BUFFERS = 3,
  RTDL_CAP_ROUTE_SUPPORTS_BORROWED_DEVICE_POINTERS = 4,
  RTDL_CAP_ROUTE_SUPPORTS_EXTERNAL_STREAM = 5,
  RTDL_CAP_ROUTE_DETERMINISTIC_ROW_ORDER = 6,
  RTDL_CAP_ROUTE_SUPPORTS_ASYNC = 7,
  RTDL_CAP_ROUTE_REQUIRES_RTDL_ALLOCATION = 8,
  RTDL_CAP_ROUTE_SUPPORTS_RTDL_OWNED_RESULT = 9,
  RTDL_CAP_ROUTE_SUPPORTS_CALLER_OUTPUT = 10
} rtdl_capability;

typedef void (*rtdl_buffer_release_fn)(void* data, void* user_data);

typedef struct rtdl_external_runtime_desc {
  size_t struct_size;
  rtdl_device_type device_type;
  int32_t device_id;
  void* context;
  void* stream;
  rtdl_stream_mode stream_mode;
  void* user_data;
} rtdl_external_runtime_desc;

typedef struct rtdl_context_desc {
  size_t struct_size;
  uint32_t requested_abi_major;
  uint32_t requested_abi_minor;
  uint32_t requested_abi_patch;
  rtdl_backend backend;
  rtdl_external_runtime_desc external_runtime;
  void* user_data;
} rtdl_context_desc;

typedef struct rtdl_route_desc {
  size_t struct_size;
  rtdl_primitive_kind primitive_kind;
  rtdl_query_kind query_kind;
  rtdl_backend backend;
  rtdl_device_type device_type;
  rtdl_dtype dtype;
} rtdl_route_desc;

/*
 * Borrowed device pointers are caller-asserted. RTDL can validate descriptor
 * shape and route support, but cannot generally prove device pointer liveness,
 * residency, aliasing safety, or producer-object lifetime.
 */
typedef struct rtdl_buffer_desc {
  size_t struct_size;
  void* data;
  uint64_t byte_count;
  rtdl_device_type device_type;
  int32_t device_id;
  rtdl_dtype dtype;
  uint32_t ndim;
  int64_t shape[RTDL_MAX_RANK];
  int64_t strides[RTDL_MAX_RANK];
  rtdl_ownership_mode ownership;
  rtdl_buffer_release_fn release;
  void* user_data;
  uint64_t flags;
  void* producer_object;
} rtdl_buffer_desc;

typedef struct rtdl_index_desc {
  size_t struct_size;
  rtdl_primitive_kind primitive_kind;
  rtdl_buffer* primitives;
  uint64_t primitive_count;
} rtdl_index_desc;

typedef struct rtdl_output_desc {
  size_t struct_size;
  rtdl_output_mode mode;
  rtdl_buffer_desc caller_buffer;
  uint64_t capacity_count;
  uint64_t* required_count_out;
  uint64_t* written_count_out;
} rtdl_output_desc;

typedef struct rtdl_query_desc {
  size_t struct_size;
  rtdl_query_kind query_kind;
  rtdl_buffer* inputs;
  uint64_t input_count;
  rtdl_output_desc output;
} rtdl_query_desc;

RTDL_API uint32_t rtdl_abi_version_major(void);
RTDL_API uint32_t rtdl_abi_version_minor(void);
RTDL_API uint32_t rtdl_abi_version_patch(void);
RTDL_API uint32_t rtdl_abi_is_compatible(uint32_t major, uint32_t minor, uint32_t patch);

RTDL_API const char* rtdl_status_string(rtdl_status status);
RTDL_API const char* rtdl_last_create_error(void);
RTDL_API const char* rtdl_context_last_error(const rtdl_context* context);

RTDL_API rtdl_status rtdl_context_create(const rtdl_context_desc* desc, rtdl_context** context_out);
RTDL_API void rtdl_context_destroy(rtdl_context* context);

RTDL_API rtdl_status rtdl_query_capability(
    const rtdl_context* context,
    const rtdl_route_desc* route,
    rtdl_capability cap,
    uint64_t* value_out);

RTDL_API rtdl_status rtdl_buffer_import(
    rtdl_context* context,
    const rtdl_buffer_desc* desc,
    rtdl_buffer** buffer_out);
RTDL_API rtdl_status rtdl_buffer_export(const rtdl_buffer* buffer, rtdl_buffer_desc* desc_out);
RTDL_API void rtdl_buffer_destroy(rtdl_buffer* buffer);

RTDL_API rtdl_status rtdl_index_build(
    rtdl_context* context,
    const rtdl_index_desc* desc,
    rtdl_index** index_out);
RTDL_API void rtdl_index_destroy(rtdl_index* index);

RTDL_API rtdl_status rtdl_query_plan_create(
    rtdl_context* context,
    const rtdl_route_desc* route,
    const rtdl_index* index,
    rtdl_query_plan** plan_out);
RTDL_API void rtdl_query_plan_destroy(rtdl_query_plan* plan);

RTDL_API rtdl_status rtdl_query_execute(
    rtdl_context* context,
    const rtdl_query_plan* plan,
    const rtdl_query_desc* desc,
    rtdl_result** result_out);

RTDL_API uint64_t rtdl_result_row_count(const rtdl_result* result);
RTDL_API rtdl_status rtdl_result_get_buffer(const rtdl_result* result, rtdl_buffer_desc* desc_out);
RTDL_API void rtdl_result_destroy(rtdl_result* result);

#ifdef __cplusplus
}  /* extern "C" */
#endif

#endif  /* RTDL_V4_RTDL_H_ */
